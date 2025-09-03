/**
 * 历史交易记录管理器
 * 负责历史交易页面的所有交互功能
 */
class HistoricalTradesManager {
    constructor() {
        this.currentPage = 1;
        this.perPage = 20;
        this.totalPages = 1;
        this.currentFilters = {};
        this.editingReviewId = null;
        this.currentTradeId = null;

        this.init();
    }

    async init() {
        try {
            // 设置事件监听器
            this.setupEventListeners();

            // 加载统计信息
            await this.loadStatistics();

            // 加载历史交易记录
            await this.loadHistoricalTrades();

            console.log('Historical trades page initialized successfully');
        } catch (error) {
            console.error('Failed to initialize historical trades page:', error);
            this.showMessage('页面初始化失败，请刷新重试', 'error');
        }
    }

    setupEventListeners() {
        // 分页大小变化
        const perPageSelect = document.getElementById('per-page');
        if (perPageSelect) {
            perPageSelect.addEventListener('change', () => {
                this.perPage = parseInt(perPageSelect.value);
                this.currentPage = 1;
                this.loadHistoricalTrades();
            });
        }

        // 排序字段变化
        const sortBySelect = document.getElementById('sort-by');
        if (sortBySelect) {
            sortBySelect.addEventListener('change', () => {
                console.log('排序字段变化:', sortBySelect.value);
                this.applyFilters();
            });
        } else {
            console.error('sort-by 元素未找到');
        }

        // 排序方向变化
        const sortOrderSelect = document.getElementById('sort-order');
        if (sortOrderSelect) {
            sortOrderSelect.addEventListener('change', () => {
                console.log('排序方向变化:', sortOrderSelect.value);
                this.applyFilters();
            });
        } else {
            console.error('sort-order 元素未找到');
        }

        // 复盘模态框事件
        const reviewModal = document.getElementById('reviewModal');
        if (reviewModal) {
            reviewModal.addEventListener('hidden.bs.modal', () => {
                this.resetReviewForm();
            });
        }

        // 保存复盘按钮
        const saveReviewBtn = document.getElementById('save-review-btn');
        if (saveReviewBtn) {
            saveReviewBtn.addEventListener('click', () => {
                this.saveReview();
            });
        }

        // 编辑复盘按钮
        const editReviewBtn = document.getElementById('edit-review-btn');
        if (editReviewBtn) {
            editReviewBtn.addEventListener('click', () => {
                this.editCurrentReview();
            });
        }

        // 图片上传预览
        const reviewImages = document.getElementById('review-images');
        if (reviewImages) {
            reviewImages.addEventListener('change', (e) => {
                this.previewImages(e.target.files);
            });
        }

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            // 只在历史交易页面处理快捷键
            if (!document.body.classList.contains('historical-trades-page')) return;
            
            // Ctrl+Enter 应用筛选
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.applyFilters();
            }
            // Ctrl+R 刷新数据
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.loadHistoricalTrades();
            }
            // Escape 重置筛选
            if (e.key === 'Escape') {
                this.resetFilters();
            }
        });

        // 筛选输入框回车键支持
        const filterInputs = ['stock-code-filter', 'stock-name-filter', 'date-from', 'date-to'];
        filterInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.applyFilters();
                    }
                });
                
                // 添加输入验证
                input.addEventListener('input', (e) => {
                    this.validateFilterInput(e.target);
                });
            }
        });

        // 响应式处理
        this.setupResponsiveHandlers();

        // 自定义事件监听
        document.addEventListener('reviewSaved', (e) => {
            this.loadHistoricalTrades();
        });

        document.addEventListener('editReview', (e) => {
            this.editReviewById(e.detail.reviewId, e.detail.reviewData);
        });

        // 窗口大小变化处理
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }

    async loadStatistics() {
        try {
            const response = await apiClient.request('GET', '/historical-trades/statistics');
            
            if (response.success) {
                this.renderStatistics(response.data);
            }
        } catch (error) {
            console.error('Failed to load statistics:', error);
            // 不显示错误，统计信息是可选的
        }
    }

    renderStatistics(stats) {
        const statisticsCards = document.getElementById('statistics-cards');
        
        if (stats && stats.total_trades > 0) {
            document.getElementById('total-trades').textContent = stats.total_trades || 0;
            document.getElementById('profitable-trades').textContent = 
                `${stats.profitable_trades || 0} (${stats.win_rate || 0}%)`;
            document.getElementById('total-return').textContent = 
                `¥${this.formatNumber(stats.total_return || 0)}`;
            document.getElementById('average-return-rate').textContent = 
                `${(stats.avg_return_rate || 0).toFixed(2)}%`;
            
            statisticsCards.style.display = 'block';
        } else {
            statisticsCards.style.display = 'none';
        }
    }

    async loadHistoricalTrades() {
        try {
            console.log('=== loadHistoricalTrades 开始 ===');
            
            // 检查apiClient是否可用
            if (typeof apiClient === 'undefined') {
                console.error('apiClient 未定义');
                this.showError('API客户端未初始化，请刷新页面重试');
                return;
            }
            
            this.showLoading();

            const params = {
                page: this.currentPage,
                per_page: this.perPage,
                ...this.currentFilters
            };

            console.log('请求参数:', params);
            console.log('排序参数检查:', { 
                sort_by: params.sort_by, 
                sort_order: params.sort_order 
            });

            const response = await apiClient.request('GET', '/historical-trades', params);
            
            console.log('API响应:', response);

            if (response.success) {
                const trades = response.data.trades || [];
                console.log('数据加载成功，记录数:', trades.length);
                
                // 验证排序是否正确
                if (trades.length > 1 && params.sort_by) {
                    console.log('验证排序结果:');
                    console.log('前5条记录的排序字段值:');
                    for (let i = 0; i < Math.min(5, trades.length); i++) {
                        const sortValue = trades[i][params.sort_by];
                        console.log(`  ${i+1}. ${trades[i].stock_code} - ${params.sort_by}: ${sortValue}`);
                    }
                    
                    // 检查排序是否正确
                    let sortingCorrect = true;
                    for (let i = 0; i < trades.length - 1; i++) {
                        const current = trades[i][params.sort_by];
                        const next = trades[i + 1][params.sort_by];
                        
                        if (params.sort_order === 'desc') {
                            if (current < next) {
                                sortingCorrect = false;
                                break;
                            }
                        } else {
                            if (current > next) {
                                sortingCorrect = false;
                                break;
                            }
                        }
                    }
                    
                    console.log(`排序验证结果: ${sortingCorrect ? '✅ 正确' : '❌ 错误'}`);
                    
                    if (!sortingCorrect) {
                        console.warn('⚠️ 检测到排序错误！这可能是前端显示问题。');
                    }
                }
                
                this.renderHistoricalTrades(trades);
                this.updatePagination(response.data);
                this.updateRecordsCount(response.data);
            } else {
                throw new Error(response.message || '加载历史交易记录失败');
            }
            
            console.log('=== loadHistoricalTrades 完成 ===');
        } catch (error) {
            console.error('Failed to load historical trades:', error);
            this.showError('加载历史交易记录失败: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    updateRecordsCount(pagination) {
        const recordsCount = document.getElementById('records-count');
        if (pagination && pagination.total > 0) {
            const currentPage = pagination.current_page || pagination.page || 1;
            const perPage = pagination.per_page || 20;
            const start = (currentPage - 1) * perPage + 1;
            const end = Math.min(currentPage * perPage, pagination.total);
            recordsCount.textContent = `显示 ${start}-${end} 条，共 ${pagination.total} 条记录`;
        } else {
            recordsCount.textContent = '';
        }
    }

    renderHistoricalTrades(trades) {
        console.log('=== renderHistoricalTrades 开始 ===');
        console.log('接收到的交易数据:', trades?.length || 0, '条');
        
        const tbody = document.getElementById('historical-trades-table-body');
        
        if (!tbody) {
            console.error('❌ 表格主体元素未找到');
            return;
        }
        
        if (!trades || trades.length === 0) {
            const hasFilters = Object.keys(this.currentFilters).length > 0;
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-5">
                        <i class="bi bi-${hasFilters ? 'search' : 'inbox'} fs-1 d-block mb-3 text-secondary"></i>
                        <h5 class="text-muted">${hasFilters ? '未找到匹配的交易记录' : '暂无历史交易记录'}</h5>
                        <p class="mb-3">
                            ${hasFilters ? 
                                '请尝试调整筛选条件或清除筛选器' : 
                                '完成清仓的交易将自动出现在这里'
                            }
                        </p>
                        ${hasFilters ? 
                            `<button class="btn btn-outline-primary" onclick="historicalTradesManager.resetFilters()">
                                <i class="bi bi-arrow-clockwise"></i> 清除筛选
                            </button>` :
                            `<button class="btn btn-outline-primary" onclick="historicalTradesManager.syncHistoricalTrades()">
                                <i class="bi bi-arrow-clockwise"></i> 同步数据
                            </button>`
                        }
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = trades.map(trade => `
            <tr>
                <td>
                    <div>
                        <strong>${trade.stock_code}</strong>
                        <br>
                        <small class="text-muted">${trade.stock_name}</small>
                    </div>
                </td>
                <td>${this.formatDate(trade.buy_date)}</td>
                <td>${this.formatDate(trade.sell_date)}</td>
                <td>
                    <span class="badge ${this.getHoldingDaysBadgeClass(trade.holding_days)}">${trade.holding_days}天</span>
                </td>
                <td>
                    <span class="text-primary fw-bold">¥${this.formatNumber(trade.total_investment)}</span>
                </td>
                <td>
                    <span class="${trade.total_return >= 0 ? 'text-danger fw-bold' : 'text-success fw-bold'}">
                        ${trade.total_return >= 0 ? '+' : ''}¥${this.formatNumber(trade.total_return)}
                    </span>
                </td>
                <td>
                    <span class="${trade.return_rate >= 0 ? 'text-danger fw-bold' : 'text-success fw-bold'}">
                        ${trade.return_rate >= 0 ? '+' : ''}${(trade.return_rate * 100).toFixed(2)}%
                    </span>
                </td>
                <td>
                    ${trade.has_review ? 
                        `<button class="btn btn-sm btn-outline-primary" onclick="historicalTradesManager.viewReview(${trade.id})" title="查看复盘">
                            <i class="bi bi-eye"></i> 查看
                        </button>` :
                        `<button class="btn btn-sm btn-primary" onclick="historicalTradesManager.addReview(${trade.id})" title="添加复盘">
                            <i class="bi bi-plus"></i> 添加
                        </button>`
                    }
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-info" onclick="historicalTradesManager.viewTradeDetails(${trade.id})" title="查看详情">
                            <i class="bi bi-info-circle"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    updatePagination(pagination) {
        this.totalPages = pagination.pages || pagination.total_pages || 1;
        this.currentPage = pagination.current_page || pagination.page || 1;

        const paginationElement = document.getElementById('pagination');
        if (this.totalPages <= 1) {
            paginationElement.innerHTML = '';
            return;
        }

        let paginationHTML = '';

        // 上一页
        if (this.currentPage > 1) {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="historicalTradesManager.goToPage(${this.currentPage - 1})">上一页</a>
                </li>
            `;
        }

        // 页码
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(this.totalPages, this.currentPage + 2);

        if (startPage > 1) {
            paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="historicalTradesManager.goToPage(1)">1</a></li>`;
            if (startPage > 2) {
                paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="historicalTradesManager.goToPage(${i})">${i}</a>
                </li>
            `;
        }

        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) {
                paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            paginationHTML += `<li class="page-item"><a class="page-link" href="#" onclick="historicalTradesManager.goToPage(${this.totalPages})">${this.totalPages}</a></li>`;
        }

        // 下一页
        if (this.currentPage < this.totalPages) {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="historicalTradesManager.goToPage(${this.currentPage + 1})">下一页</a>
                </li>
            `;
        }

        paginationElement.innerHTML = paginationHTML;
    }

    goToPage(page) {
        if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
            this.currentPage = page;
            this.loadHistoricalTrades();
        }
    }

    applyFilters() {
        console.log('=== applyFilters 开始 ===');
        
        const filters = {};

        const stockCode = document.getElementById('stock-code-filter').value.trim();
        if (stockCode) filters.stock_code = stockCode;

        const stockName = document.getElementById('stock-name-filter').value.trim();
        if (stockName) filters.stock_name = stockName;

        const dateFrom = document.getElementById('date-from').value;
        if (dateFrom) filters.start_date = dateFrom;

        const dateTo = document.getElementById('date-to').value;
        if (dateTo) filters.end_date = dateTo;

        const returnRateFilter = document.getElementById('return-rate-filter').value;
        if (returnRateFilter === 'positive') {
            filters.is_profitable = true;
        } else if (returnRateFilter === 'negative') {
            filters.is_profitable = false;
        }

        // 排序参数
        const sortByElement = document.getElementById('sort-by');
        const sortOrderElement = document.getElementById('sort-order');
        
        if (!sortByElement) {
            console.error('sort-by 元素未找到');
            return;
        }
        
        if (!sortOrderElement) {
            console.error('sort-order 元素未找到');
            return;
        }
        
        const sortBy = sortByElement.value;
        const sortOrder = sortOrderElement.value;
        
        filters.sort_by = sortBy || 'completion_date';
        filters.sort_order = sortOrder || 'desc';

        console.log('应用筛选和排序:', filters);
        console.log('当前排序:', { sort_by: filters.sort_by, sort_order: filters.sort_order });

        this.currentFilters = filters;
        this.currentPage = 1;
        
        console.log('调用 loadHistoricalTrades...');
        this.loadHistoricalTrades();
        console.log('=== applyFilters 完成 ===');
    }

    resetFilters() {
        document.getElementById('stock-code-filter').value = '';
        document.getElementById('stock-name-filter').value = '';
        document.getElementById('date-from').value = '';
        document.getElementById('date-to').value = '';
        document.getElementById('return-rate-filter').value = '';
        document.getElementById('sort-by').value = 'completion_date';
        document.getElementById('sort-order').value = 'desc';

        this.currentFilters = {};
        this.currentPage = 1;
        this.loadHistoricalTrades();
    }

    async syncHistoricalTrades() {
        try {
            // 显示确认对话框
            if (!confirm('确定要同步历史交易数据吗？这可能需要一些时间。')) {
                return;
            }

            // 显示加载模态框
            const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
            loadingModal.show();

            this.showMessage('正在同步历史交易数据，请稍候...', 'info');

            const response = await apiClient.request('POST', '/historical-trades/sync');

            if (response.success) {
                const data = response.data;
                let message = '同步完成';
                
                if (data.processed_count !== undefined) {
                    message += `，共处理 ${data.processed_count} 条记录`;
                }
                if (data.created_count !== undefined) {
                    message += `，新增 ${data.created_count} 条历史交易`;
                }
                if (data.updated_count !== undefined) {
                    message += `，更新 ${data.updated_count} 条记录`;
                }

                this.showMessage(message, 'success');
                
                // 重新加载统计信息和交易记录
                await this.loadStatistics();
                await this.loadHistoricalTrades();
            } else {
                throw new Error(response.message || '同步失败');
            }
        } catch (error) {
            console.error('Failed to sync historical trades:', error);
            this.showMessage('同步历史交易数据失败: ' + (error.message || '未知错误'), 'error');
        } finally {
            // 隐藏加载模态框
            const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
            if (loadingModal) {
                loadingModal.hide();
            }
        }
    }

    async addReview(tradeId) {
        try {
            // 获取交易详情
            const response = await apiClient.request('GET', `/historical-trades/${tradeId}`);
            
            if (response.success) {
                this.currentTradeId = tradeId;
                this.editingReviewId = null;
                
                // 使用新的复盘编辑器
                if (window.reviewEditor) {
                    window.reviewEditor.loadReview(response.data, null);
                    this.showReviewModal();
                } else {
                    this.showReviewModal(response.data, null);
                }
            } else {
                throw new Error(response.message || '获取交易详情失败');
            }
        } catch (error) {
            console.error('Failed to load trade details:', error);
            this.showMessage('获取交易详情失败', 'error');
        }
    }

    async viewReview(tradeId) {
        try {
            const response = await apiClient.request('GET', `/trade-reviews/by-trade/${tradeId}`);
            
            if (response.success && response.data) {
                this.currentTradeId = tradeId;
                
                // 使用新的复盘查看器
                if (window.reviewViewer) {
                    window.reviewViewer.currentReview = response.data;
                    window.reviewViewer.currentTrade = { id: tradeId };
                    window.reviewViewer.displayReview(response.data);
                    this.showViewReviewModal();
                } else {
                    this.showViewReviewModal(response.data);
                }
            } else {
                throw new Error(response.message || '获取复盘内容失败');
            }
        } catch (error) {
            console.error('Failed to load review:', error);
            this.showMessage('获取复盘内容失败', 'error');
        }
    }

    showReviewModal(tradeData = null, reviewData = null) {
        // 如果没有传入数据，说明是通过新组件调用的
        if (!tradeData && !reviewData) {
            // 初始化图片上传器
            this.initializeImageUploader();
        } else {
            // 兼容旧的调用方式
            // 填充交易信息
            const tradeInfo = document.getElementById('trade-info');
            tradeInfo.innerHTML = `
                <div class="col-md-3">
                    <strong>股票:</strong> ${tradeData.stock_code} ${tradeData.stock_name}
                </div>
                <div class="col-md-3">
                    <strong>持仓天数:</strong> ${tradeData.holding_days}天
                </div>
                <div class="col-md-3">
                    <strong>投入本金:</strong> ¥${this.formatNumber(tradeData.total_investment)}
                </div>
                <div class="col-md-3">
                    <strong>实际收益:</strong> 
                    <span class="${tradeData.total_return >= 0 ? 'text-danger' : 'text-success'}">
                        ¥${this.formatNumber(tradeData.total_return)} (${(tradeData.return_rate * 100).toFixed(2)}%)
                    </span>
                </div>
            `;

            // 填充表单数据
            document.getElementById('historical-trade-id').value = tradeData.id;
            
            if (reviewData) {
                this.editingReviewId = reviewData.id;
                document.getElementById('review-title').value = reviewData.review_title || '';
                document.getElementById('review-type').value = reviewData.review_type || 'general';
                document.getElementById('review-content').value = reviewData.review_content || '';
                document.getElementById('strategy-score').value = reviewData.strategy_score || '';
                document.getElementById('timing-score').value = reviewData.timing_score || '';
                document.getElementById('risk-control-score').value = reviewData.risk_control_score || '';
                document.getElementById('overall-score').value = reviewData.overall_score || '';
                document.getElementById('key-learnings').value = reviewData.key_learnings || '';
                document.getElementById('improvement-areas').value = reviewData.improvement_areas || '';
            }

            // 更新模态框标题
            const modalTitle = document.getElementById('review-modal-title');
            modalTitle.textContent = reviewData ? '编辑复盘' : '添加复盘';
        }

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('reviewModal'));
        modal.show();
    }

    initializeImageUploader() {
        // 初始化图片上传组件
        if (window.ImageUploader && !this.imageUploader) {
            this.imageUploader = new ImageUploader('image-uploader-container', {
                maxFiles: 10,
                maxSize: 5 * 1024 * 1024,
                multiple: true
            });
        }
    }

    showViewReviewModal(reviewData = null) {
        // 如果没有传入数据，说明是通过新组件调用的
        if (!reviewData) {
            // 新组件已经处理了内容渲染
        } else {
            // 兼容旧的调用方式
            const content = document.getElementById('view-review-content');
            
            content.innerHTML = `
                <div class="row mb-3">
                    <div class="col-md-8">
                        <h5>${reviewData.review_title || '交易复盘'}</h5>
                        <span class="badge bg-secondary">${this.getReviewTypeText(reviewData.review_type)}</span>
                    </div>
                    <div class="col-md-4 text-end">
                        <small class="text-muted">创建时间: ${this.formatDateTime(reviewData.created_at)}</small>
                    </div>
                </div>

                <div class="row mb-3">
                    <div class="col-md-12">
                        <h6>复盘内容</h6>
                        <div class="border rounded p-3 bg-light">
                            ${reviewData.review_content ? reviewData.review_content.replace(/\n/g, '<br>') : '暂无内容'}
                        </div>
                    </div>
                </div>

                ${this.renderScores(reviewData)}

                <div class="row mb-3">
                    <div class="col-md-6">
                        <h6>关键学习点</h6>
                        <div class="border rounded p-3 bg-light">
                            ${reviewData.key_learnings ? reviewData.key_learnings.replace(/\n/g, '<br>') : '暂无内容'}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6>改进领域</h6>
                        <div class="border rounded p-3 bg-light">
                            ${reviewData.improvement_areas ? reviewData.improvement_areas.replace(/\n/g, '<br>') : '暂无内容'}
                        </div>
                    </div>
                </div>

                ${reviewData.images && reviewData.images.length > 0 ? this.renderReviewImages(reviewData.images) : ''}
            `;

            // 设置编辑按钮的数据
            const editBtn = document.getElementById('edit-review-btn');
            editBtn.setAttribute('data-review-id', reviewData.id);
        }

        const modal = new bootstrap.Modal(document.getElementById('viewReviewModal'));
        modal.show();
    }

    renderScores(reviewData) {
        const scores = [
            { label: '策略执行', value: reviewData.strategy_score },
            { label: '时机把握', value: reviewData.timing_score },
            { label: '风险控制', value: reviewData.risk_control_score },
            { label: '总体评分', value: reviewData.overall_score }
        ];

        const hasScores = scores.some(score => score.value);
        
        if (!hasScores) {
            return '';
        }

        return `
            <div class="row mb-3">
                <div class="col-md-12">
                    <h6>评分</h6>
                    <div class="row">
                        ${scores.map(score => `
                            <div class="col-md-3">
                                <div class="text-center">
                                    <div class="fs-4 ${this.getScoreColor(score.value)}">${score.value || '-'}/5</div>
                                    <small class="text-muted">${score.label}</small>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderReviewImages(images) {
        return `
            <div class="row mb-3">
                <div class="col-md-12">
                    <h6>复盘图片</h6>
                    <div class="row">
                        ${images.map(image => `
                            <div class="col-md-3 mb-2">
                                <img src="${image.file_path}" class="img-fluid rounded" alt="${image.description || '复盘图片'}" 
                                     style="cursor: pointer;" onclick="this.style.transform = this.style.transform ? '' : 'scale(2)'">
                                ${image.description ? `<small class="text-muted d-block mt-1">${image.description}</small>` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    async editCurrentReview() {
        const reviewId = document.getElementById('edit-review-btn').getAttribute('data-review-id');
        
        try {
            const response = await apiClient.request('GET', `/trade-reviews/${reviewId}`);
            
            if (response.success) {
                // 关闭查看模态框
                const viewModal = bootstrap.Modal.getInstance(document.getElementById('viewReviewModal'));
                viewModal.hide();

                // 获取交易数据
                const tradeResponse = await apiClient.request('GET', `/historical-trades/${this.currentTradeId}`);
                
                if (tradeResponse.success) {
                    // 显示编辑模态框
                    setTimeout(() => {
                        if (window.reviewEditor) {
                            window.reviewEditor.loadReview(tradeResponse.data, response.data);
                            this.showReviewModal();
                        } else {
                            this.showReviewModal(tradeResponse.data, response.data);
                        }
                    }, 300);
                }
            }
        } catch (error) {
            console.error('Failed to load review for editing:', error);
            this.showMessage('获取复盘数据失败', 'error');
        }
    }

    async editReviewById(reviewId, reviewData) {
        try {
            // 获取交易数据
            const tradeResponse = await apiClient.request('GET', `/historical-trades/${this.currentTradeId}`);
            
            if (tradeResponse.success) {
                if (window.reviewEditor) {
                    window.reviewEditor.loadReview(tradeResponse.data, reviewData);
                    this.showReviewModal();
                } else {
                    this.showReviewModal(tradeResponse.data, reviewData);
                }
            }
        } catch (error) {
            console.error('Failed to edit review:', error);
            this.showMessage('编辑复盘失败', 'error');
        }
    }

    async saveReview() {
        try {
            const form = document.getElementById('review-form');
            const formData = new FormData(form);

            // 添加图片文件
            const imageFiles = document.getElementById('review-images').files;
            for (let i = 0; i < imageFiles.length; i++) {
                formData.append('images', imageFiles[i]);
            }

            const saveBtn = document.getElementById('save-review-btn');
            const spinner = saveBtn.querySelector('.spinner-border');
            
            saveBtn.disabled = true;
            spinner.style.display = 'inline-block';

            let response;
            if (this.editingReviewId) {
                response = await apiClient.request('PUT', `/trade-reviews/${this.editingReviewId}`, formData);
            } else {
                response = await apiClient.request('POST', '/trade-reviews', formData);
            }

            if (response.success) {
                this.showMessage('复盘保存成功', 'success');
                
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('reviewModal'));
                modal.hide();

                // 刷新列表
                await this.loadHistoricalTrades();
            } else {
                throw new Error(response.message || '保存失败');
            }
        } catch (error) {
            console.error('Failed to save review:', error);
            this.showMessage('保存复盘失败', 'error');
        } finally {
            const saveBtn = document.getElementById('save-review-btn');
            const spinner = saveBtn.querySelector('.spinner-border');
            
            saveBtn.disabled = false;
            spinner.style.display = 'none';
        }
    }

    resetReviewForm() {
        const form = document.getElementById('review-form');
        form.reset();
        
        document.getElementById('image-preview').innerHTML = '';
        this.editingReviewId = null;
        this.currentTradeId = null;
    }

    previewImages(files) {
        const preview = document.getElementById('image-preview');
        preview.innerHTML = '';

        Array.from(files).forEach((file, index) => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const div = document.createElement('div');
                    div.className = 'position-relative d-inline-block me-2 mb-2';
                    div.innerHTML = `
                        <img src="${e.target.result}" class="img-thumbnail" style="width: 100px; height: 100px; object-fit: cover;">
                        <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0" 
                                onclick="this.parentElement.remove()" style="transform: translate(50%, -50%);">
                            <i class="bi bi-x"></i>
                        </button>
                    `;
                    preview.appendChild(div);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    async viewTradeDetails(tradeId) {
        try {
            const response = await apiClient.request('GET', `/historical-trades/${tradeId}`);
            
            if (response.success) {
                this.showTradeDetailsModal(response.data);
            }
        } catch (error) {
            console.error('Failed to load trade details:', error);
            this.showMessage('获取交易详情失败', 'error');
        }
    }

    showTradeDetailsModal(trade) {
        // 创建模态框内容
        const modalContent = `
            <div class="modal fade" id="tradeDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">交易详情 - ${trade.stock_code} ${trade.stock_name}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <h6>基本信息</h6>
                                    <table class="table table-sm">
                                        <tr><td>股票代码:</td><td><strong>${trade.stock_code}</strong></td></tr>
                                        <tr><td>股票名称:</td><td>${trade.stock_name}</td></tr>
                                        <tr><td>买入日期:</td><td>${this.formatDate(trade.buy_date)}</td></tr>
                                        <tr><td>卖出日期:</td><td>${this.formatDate(trade.sell_date)}</td></tr>
                                        <tr><td>持仓天数:</td><td><span class="badge ${this.getHoldingDaysBadgeClass(trade.holding_days)}">${trade.holding_days}天</span></td></tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6>财务数据</h6>
                                    <table class="table table-sm">
                                        <tr><td>投入本金:</td><td class="text-primary fw-bold">¥${this.formatNumber(trade.total_investment)}</td></tr>
                                        <tr><td>实际收益:</td><td class="${trade.total_return >= 0 ? 'text-danger' : 'text-success'} fw-bold">${trade.total_return >= 0 ? '+' : ''}¥${this.formatNumber(trade.total_return)}</td></tr>
                                        <tr><td>收益率:</td><td class="${trade.return_rate >= 0 ? 'text-danger' : 'text-success'} fw-bold">${trade.return_rate >= 0 ? '+' : ''}${(trade.return_rate * 100).toFixed(2)}%</td></tr>
                                        <tr><td>完成日期:</td><td>${this.formatDate(trade.completion_date)}</td></tr>
                                    </table>
                                </div>
                            </div>
                            
                            ${trade.buy_records && trade.buy_records.length > 0 ? `
                            <div class="mb-3">
                                <h6>买入记录 (${trade.buy_records.length}笔)</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped">
                                        <thead>
                                            <tr><th>日期</th><th>数量</th><th>价格</th><th>金额</th></tr>
                                        </thead>
                                        <tbody>
                                            ${trade.buy_records.map(record => `
                                                <tr>
                                                    <td>${this.formatDate(record.trade_date)}</td>
                                                    <td>${record.quantity}</td>
                                                    <td>¥${this.formatNumber(record.price)}</td>
                                                    <td>¥${this.formatNumber(record.total_amount)}</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            ` : ''}
                            
                            ${trade.sell_records && trade.sell_records.length > 0 ? `
                            <div class="mb-3">
                                <h6>卖出记录 (${trade.sell_records.length}笔)</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm table-striped">
                                        <thead>
                                            <tr><th>日期</th><th>数量</th><th>价格</th><th>金额</th></tr>
                                        </thead>
                                        <tbody>
                                            ${trade.sell_records.map(record => `
                                                <tr>
                                                    <td>${this.formatDate(record.trade_date)}</td>
                                                    <td>${record.quantity}</td>
                                                    <td>¥${this.formatNumber(record.price)}</td>
                                                    <td>¥${this.formatNumber(record.total_amount)}</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-primary" onclick="historicalTradesManager.addReview(${trade.id})">
                                <i class="bi bi-plus"></i> 添加复盘
                            </button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 移除已存在的模态框
        const existingModal = document.getElementById('tradeDetailsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // 添加新模态框到页面
        document.body.insertAdjacentHTML('beforeend', modalContent);

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('tradeDetailsModal'));
        modal.show();

        // 模态框关闭后清理
        document.getElementById('tradeDetailsModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    // 工具方法
    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    }

    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    }

    formatNumber(number) {
        if (number === null || number === undefined) return '0.00';
        const num = parseFloat(number);
        if (isNaN(num)) return '0.00';
        
        // 对于大数字，使用千分位分隔符
        return num.toLocaleString('zh-CN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    getReviewTypeText(type) {
        const types = {
            'general': '一般复盘',
            'success': '成功案例',
            'failure': '失败教训',
            'lesson': '重要学习'
        };
        return types[type] || '一般复盘';
    }

    getScoreColor(score) {
        if (!score) return 'text-muted';
        if (score >= 4) return 'text-success';
        if (score >= 3) return 'text-warning';
        return 'text-danger';
    }

    getHoldingDaysBadgeClass(days) {
        if (days <= 7) return 'bg-success';      // 短期持仓
        if (days <= 30) return 'bg-info';       // 中期持仓
        if (days <= 90) return 'bg-warning';    // 长期持仓
        return 'bg-secondary';                   // 超长期持仓
    }

    showLoading() {
        const tbody = document.getElementById('historical-trades-table-body');
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                    加载中...
                </td>
            </tr>
        `;
    }

    hideLoading() {
        // Loading will be replaced by actual content or empty state
    }

    showError(message) {
        const tbody = document.getElementById('historical-trades-table-body');
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-danger py-4">
                    <i class="bi bi-exclamation-triangle fs-1 d-block mb-2"></i>
                    ${message}
                    <br>
                    <button class="btn btn-outline-primary btn-sm mt-2" onclick="historicalTradesManager.loadHistoricalTrades()">
                        重试
                    </button>
                </td>
            </tr>
        `;
    }

    showMessage(message, type = 'info') {
        // 使用现有的消息系统
        if (typeof showMessage === 'function') {
            showMessage(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    // 输入验证方法
    validateFilterInput(input) {
        const value = input.value.trim();
        const id = input.id;
        
        // 清除之前的验证状态
        input.classList.remove('is-invalid', 'is-valid');
        
        switch (id) {
            case 'stock-code-filter':
                if (value && !/^[0-9]{6}$/.test(value)) {
                    input.classList.add('is-invalid');
                    this.setInputFeedback(input, '股票代码应为6位数字');
                } else if (value) {
                    input.classList.add('is-valid');
                    this.clearInputFeedback(input);
                }
                break;
                
            case 'date-from':
            case 'date-to':
                if (value && !this.isValidDate(value)) {
                    input.classList.add('is-invalid');
                    this.setInputFeedback(input, '请输入有效的日期');
                } else if (value) {
                    input.classList.add('is-valid');
                    this.clearInputFeedback(input);
                }
                break;
        }
    }

    isValidDate(dateString) {
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }

    setInputFeedback(input, message) {
        let feedback = input.parentNode.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            input.parentNode.appendChild(feedback);
        }
        feedback.textContent = message;
    }

    clearInputFeedback(input) {
        const feedback = input.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    }

    // 响应式处理方法
    setupResponsiveHandlers() {
        // 检测移动设备
        this.isMobile = window.innerWidth <= 768;
        
        // 调整表格显示
        this.adjustTableForMobile();
    }

    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        if (wasMobile !== this.isMobile) {
            this.adjustTableForMobile();
        }
    }

    adjustTableForMobile() {
        const table = document.getElementById('historical-trades-table');
        if (!table) return;
        
        if (this.isMobile) {
            table.classList.add('table-responsive-sm');
            // 隐藏一些不重要的列
            this.hideColumnsOnMobile(['holding-days', 'actions']);
        } else {
            table.classList.remove('table-responsive-sm');
            this.showAllColumns();
        }
    }

    hideColumnsOnMobile(columnIds) {
        columnIds.forEach(id => {
            const elements = document.querySelectorAll(`[data-column="${id}"]`);
            elements.forEach(el => el.style.display = 'none');
        });
    }

    showAllColumns() {
        const hiddenElements = document.querySelectorAll('[data-column]');
        hiddenElements.forEach(el => el.style.display = '');
    }

    // 防抖函数
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // 错误处理增强
    handleApiError(error) {
        console.error('API Error:', error);
        
        let message = '操作失败';
        
        if (error.response) {
            // 服务器响应错误
            const status = error.response.status;
            const data = error.response.data;
            
            switch (status) {
                case 400:
                    message = data.message || '请求参数错误';
                    break;
                case 401:
                    message = '未授权访问';
                    break;
                case 403:
                    message = '权限不足';
                    break;
                case 404:
                    message = '资源不存在';
                    break;
                case 500:
                    message = '服务器内部错误';
                    break;
                default:
                    message = data.message || `服务器错误 (${status})`;
            }
        } else if (error.request) {
            // 网络错误
            message = '网络连接失败，请检查网络连接';
        } else {
            // 其他错误
            message = error.message || '未知错误';
        }
        
        this.showMessage(message, 'error');
        return message;
    }

    // 数据验证方法
    validateTradeData(data) {
        const errors = [];
        
        if (!data.stock_code || !/^[0-9]{6}$/.test(data.stock_code)) {
            errors.push('股票代码格式不正确');
        }
        
        if (!data.buy_date || !this.isValidDate(data.buy_date)) {
            errors.push('买入日期无效');
        }
        
        if (!data.sell_date || !this.isValidDate(data.sell_date)) {
            errors.push('卖出日期无效');
        }
        
        if (data.buy_date && data.sell_date && new Date(data.buy_date) >= new Date(data.sell_date)) {
            errors.push('卖出日期必须晚于买入日期');
        }
        
        return errors;
    }

    // 性能优化方法
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }

    // 缓存管理
    getCachedData(key) {
        try {
            const cached = localStorage.getItem(`historical_trades_${key}`);
            if (cached) {
                const data = JSON.parse(cached);
                // 检查缓存是否过期（5分钟）
                if (Date.now() - data.timestamp < 5 * 60 * 1000) {
                    return data.value;
                }
            }
        } catch (error) {
            console.warn('Cache read error:', error);
        }
        return null;
    }

    setCachedData(key, value) {
        try {
            const data = {
                value: value,
                timestamp: Date.now()
            };
            localStorage.setItem(`historical_trades_${key}`, JSON.stringify(data));
        } catch (error) {
            console.warn('Cache write error:', error);
        }
    }

    clearCache() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith('historical_trades_')) {
                    localStorage.removeItem(key);
                }
            });
        } catch (error) {
            console.warn('Cache clear error:', error);
        }
    }
}