/**
 * 期望对比管理器
 * 
 * 负责期望对比功能的前端逻辑，包括：
 * - 数据加载和API调用
 * - 时间范围筛选
 * - 错误处理和加载状态管理
 * - 图表渲染和数据可视化
 * 
 * Requirements: 1.1, 1.2, 6.2, 6.3, 8.1
 */

class ExpectationComparisonManager {
    constructor() {
        this.currentTimeRange = 'all';
        this.baseCapital = 3200000; // 320万基准本金
        this.charts = {};
        this.isLoading = false;
        this.currentData = null;
        
        // 时间范围配置
        this.timeRangeConfig = {
            '30d': { label: '最近30天', days: 30 },
            '90d': { label: '最近90天', days: 90 },
            '1y': { label: '最近1年', days: 365 },
            'all': { label: '全部时间', days: null }
        };
        
        // 期望模型配置
        this.expectationModel = {
            scenarios: [
                { probability: 0.10, return_rate: 0.20, max_holding_days: 30 },
                { probability: 0.10, return_rate: 0.15, max_holding_days: 20 },
                { probability: 0.15, return_rate: 0.10, max_holding_days: 15 },
                { probability: 0.15, return_rate: 0.05, max_holding_days: 10 },
                { probability: 0.10, return_rate: 0.02, max_holding_days: 5 },
                { probability: 0.20, return_rate: -0.03, max_holding_days: 5 },
                { probability: 0.15, return_rate: -0.05, max_holding_days: 5 },
                { probability: 0.05, return_rate: -0.10, max_holding_days: 5 }
            ]
        };
        
        // 性能优化相关
        this.lastCacheKey = null;
        this.currentRequest = null;
        this.debounceTimer = null;
        this.chartAnimationEnabled = true;
        this.performanceMetrics = {
            loadTime: 0,
            renderTime: 0,
            apiResponseTime: 0
        };
        
        this.init();
    }
    
    /**
     * 初始化期望对比管理器
     */
    init() {
        console.log('初始化期望对比管理器...');
        
        // 注册Chart.js插件
        this.registerChartPlugins();
        
        // 设置响应式设计
        this.setupResponsiveDesign();
        
        this.bindEvents();
        this.initializeUI();
        
        // 启动性能监控
        this.startPerformanceMonitoring();
        
        // 记录初始化时间
        this.performanceMetrics.loadTime = performance.now();
        
        // 延迟加载数据，避免阻塞页面渲染
        setTimeout(() => {
            this.loadComparisonData();
            this.loadMonthlyExpectations();
        }, 100);
        
        // 页面卸载时清理资源
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }
    
    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 时间范围选择器事件
        const timeRangeSelect = document.getElementById('time-range-select');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (e) => {
                this.updateTimeRange(e.target.value);
            });
        }
        
        // 刷新按钮事件
        const refreshBtn = document.getElementById('refresh-expectation-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadComparisonData();
            });
        }
        
        // 月度期望收益刷新按钮事件
        const refreshMonthlyBtn = document.getElementById('refresh-monthly-expectation-btn');
        if (refreshMonthlyBtn) {
            refreshMonthlyBtn.addEventListener('click', () => {
                this.loadMonthlyExpectations();
            });
        }
    }
    
    /**
     * 更新时间范围（防抖优化版本）
     * @param {string} timeRange - 时间范围 ('30d', '90d', '1y', 'all')
     */
    updateTimeRange(timeRange) {
        if (!this.timeRangeConfig[timeRange]) {
            console.error(`无效的时间范围: ${timeRange}`);
            this.showErrorMessage('无效的时间范围');
            return;
        }
        
        if (this.currentTimeRange === timeRange) {
            console.log('时间范围未变更，跳过更新');
            return;
        }
        
        this.currentTimeRange = timeRange;
        console.log(`时间范围更新为: ${this.timeRangeConfig[timeRange].label}`);
        
        // 防抖处理，避免快速切换时的多次请求
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        this.debounceTimer = setTimeout(() => {
            this.loadComparisonData();
        }, 300);
    }
    
    /**
     * 加载期望对比数据（优化版本）
     * @param {boolean} forceRefresh - 是否强制刷新
     */
    async loadComparisonData(forceRefresh = false) {
        // 防止重复请求
        if (this.isLoading && !forceRefresh) {
            console.log('数据正在加载中，跳过重复请求');
            return;
        }
        
        // 缓存检查 - 如果有缓存数据且不是强制刷新，直接使用缓存
        const cacheKey = `expectation_${this.currentTimeRange}_${this.baseCapital}`;
        if (!forceRefresh && this.currentData && this.lastCacheKey === cacheKey) {
            console.log('使用缓存数据');
            this.renderComparison(this.currentData);
            return;
        }
        
        this.setLoadingState(true);
        
        try {
            console.log(`加载期望对比数据，时间范围: ${this.currentTimeRange}`);
            
            // 使用AbortController支持请求取消
            if (this.currentRequest) {
                this.currentRequest.abort();
            }
            this.currentRequest = new AbortController();
            
            const url = `/api/analytics/expectation-comparison?time_range=${this.currentTimeRange}&base_capital=${this.baseCapital}`;
            const response = await fetch(url, {
                signal: this.currentRequest.signal,
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.message || '获取数据失败');
            }
            
            this.currentData = result.data;
            this.lastCacheKey = cacheKey;
            this.renderComparison(this.currentData);
            
            console.log('期望对比数据加载成功');
            this.showSuccessMessage('数据加载成功');
            
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('请求已取消');
                return;
            }
            console.error('加载期望对比数据失败:', error);
            this.handleError(error, '加载期望对比数据失败');
        } finally {
            this.setLoadingState(false);
            this.currentRequest = null;
        }
    }
    
    /**
     * 渲染期望对比数据
     * @param {Object} data - 期望对比数据
     */
    renderComparison(data) {
        if (!data) {
            console.error('渲染数据为空');
            return;
        }
        
        try {
            // 更新对比卡片
            this.updateComparisonCards(data);
            
            // 渲染图表
            this.renderCharts(data);
            
            // 更新差异分析
            this.updateAnalysisSummary(data);
            
            console.log('期望对比数据渲染完成');
            
        } catch (error) {
            console.error('渲染期望对比数据失败:', error);
            this.showErrorState('数据渲染失败');
        }
    }
    
    /**
     * 设置加载状态
     * @param {boolean} loading - 是否加载中
     */
    setLoadingState(loading) {
        this.isLoading = loading;
        
        const refreshBtn = document.getElementById('refresh-expectation-btn');
        const timeRangeSelect = document.getElementById('time-range-select');
        
        if (loading) {
            // 显示加载状态
            if (refreshBtn) {
                refreshBtn.disabled = true;
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>加载中...';
            }
            
            if (timeRangeSelect) {
                timeRangeSelect.disabled = true;
            }
            
            // 显示全局加载提示
            this.showLoadingMessage();
            
        } else {
            // 恢复正常状态
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i>刷新';
            }
            
            if (timeRangeSelect) {
                timeRangeSelect.disabled = false;
            }
            
            // 隐藏加载提示
            this.hideLoadingMessage();
        }
    }
    
    /**
     * 显示加载消息
     */
    showLoadingMessage() {
        const analysisSummary = document.getElementById('analysis-summary');
        if (analysisSummary) {
            analysisSummary.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                    <h5 class="text-primary">正在加载期望对比数据</h5>
                    <p class="text-muted">请稍候，正在计算您的交易表现与期望目标的对比...</p>
                </div>
            `;
        }
    }
    
    /**
     * 隐藏加载消息
     */
    hideLoadingMessage() {
        // 加载消息会在渲染数据时被替换，这里不需要特别处理
    }
    
    /**
     * 处理错误
     * @param {Error} error - 错误对象
     * @param {string} context - 错误上下文
     */
    handleError(error, context = '操作') {
        console.error(`${context}失败:`, error);
        
        let errorMessage = '未知错误';
        let suggestions = [];
        
        // 根据错误类型提供具体的错误信息和建议
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorMessage = '网络连接失败';
            suggestions = [
                '请检查网络连接是否正常',
                '确认服务器是否正在运行',
                '稍后重试或联系管理员'
            ];
        } else if (error.message.includes('HTTP 404')) {
            errorMessage = 'API接口不存在';
            suggestions = [
                '请确认系统版本是否最新',
                '联系技术支持检查接口配置'
            ];
        } else if (error.message.includes('HTTP 500')) {
            errorMessage = '服务器内部错误';
            suggestions = [
                '服务器遇到问题，请稍后重试',
                '如果问题持续存在，请联系管理员'
            ];
        } else if (error.message.includes('暂无数据') || error.message.includes('no data')) {
            errorMessage = '暂无交易数据';
            suggestions = [
                '请先添加一些交易记录',
                '尝试选择不同的时间范围',
                '确认交易记录是否已正确保存'
            ];
        } else {
            errorMessage = error.message || '操作失败';
            suggestions = [
                '请刷新页面重试',
                '检查输入参数是否正确',
                '如果问题持续存在，请联系技术支持'
            ];
        }
        
        this.showErrorState(errorMessage, suggestions);
    }
    
    /**
     * 显示错误状态
     * @param {string} message - 错误消息
     * @param {Array} suggestions - 建议列表
     */
    showErrorState(message, suggestions = []) {
        const analysisSummary = document.getElementById('analysis-summary');
        if (analysisSummary) {
            let suggestionsHtml = '';
            if (suggestions.length > 0) {
                suggestionsHtml = `
                    <div class="mt-3">
                        <h6 class="text-muted">解决建议：</h6>
                        <ul class="list-unstyled">
                            ${suggestions.map(suggestion => `
                                <li class="mb-1">
                                    <i class="fas fa-lightbulb text-warning me-2"></i>
                                    ${suggestion}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            }
            
            analysisSummary.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <h5 class="text-danger">加载失败</h5>
                    <p class="text-muted mb-3">${message}</p>
                    ${suggestionsHtml}
                    <div class="mt-4">
                        <button class="btn btn-primary me-2" onclick="expectationManager.loadComparisonData(true)">
                            <i class="fas fa-redo me-1"></i>重新加载
                        </button>
                        <button class="btn btn-outline-secondary" onclick="expectationManager.showInitialState()">
                            <i class="fas fa-home me-1"></i>返回初始状态
                        </button>
                    </div>
                </div>
            `;
        }
        
        // 显示顶部错误提示
        this.showErrorMessage(message);
    }
    
    /**
     * 显示成功消息
     * @param {string} message - 成功消息
     */
    showSuccessMessage(message) {
        this.showToast(message, 'success');
    }
    
    /**
     * 显示错误消息
     * @param {string} message - 错误消息
     */
    showErrorMessage(message) {
        this.showToast(message, 'error');
    }
    
    /**
     * 显示警告消息
     * @param {string} message - 警告消息
     */
    showWarningMessage(message) {
        this.showToast(message, 'warning');
    }
    
    /**
     * 显示信息消息
     * @param {string} message - 信息消息
     */
    showInfoMessage(message) {
        this.showToast(message, 'info');
    }
    
    /**
     * 显示Toast消息
     * @param {string} message - 消息内容
     * @param {string} type - 消息类型 ('success', 'error', 'warning', 'info')
     */
    showToast(message, type = 'info') {
        // 检查是否有全局的showMessage函数
        if (typeof window.showMessage === 'function') {
            window.showMessage(message, type);
            return;
        }
        
        // 备用方案：创建简单的toast
        const toast = document.createElement('div');
        toast.className = `alert alert-${this.getBootstrapClass(type)} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${this.getIconForType(type)}
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // 自动移除
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }
    
    /**
     * 获取Bootstrap类名
     * @param {string} type - 消息类型
     * @returns {string} Bootstrap类名
     */
    getBootstrapClass(type) {
        const classMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return classMap[type] || 'info';
    }
    
    /**
     * 获取消息类型对应的图标
     * @param {string} type - 消息类型
     * @returns {string} 图标HTML
     */
    getIconForType(type) {
        const iconMap = {
            'success': '<i class="fas fa-check-circle me-2"></i>',
            'error': '<i class="fas fa-exclamation-circle me-2"></i>',
            'warning': '<i class="fas fa-exclamation-triangle me-2"></i>',
            'info': '<i class="fas fa-info-circle me-2"></i>'
        };
        return iconMap[type] || iconMap['info'];
    }
    
    /**
     * 自动错误恢复机制
     * @param {Error} error - 错误对象
     * @param {number} retryCount - 重试次数
     */
    async autoRecovery(error, retryCount = 0) {
        const maxRetries = 3;
        const retryDelay = Math.pow(2, retryCount) * 1000; // 指数退避
        
        if (retryCount < maxRetries) {
            console.log(`自动恢复尝试 ${retryCount + 1}/${maxRetries}，${retryDelay}ms后重试...`);
            
            setTimeout(async () => {
                try {
                    await this.loadComparisonData(true);
                    this.showSuccessMessage('数据恢复成功');
                } catch (retryError) {
                    await this.autoRecovery(retryError, retryCount + 1);
                }
            }, retryDelay);
        } else {
            console.error('自动恢复失败，已达到最大重试次数');
            this.showErrorMessage('自动恢复失败，请手动刷新页面');
        }
    }
    
    /**
     * 健康检查
     * @returns {Object} 健康状态
     */
    healthCheck() {
        const health = {
            status: 'healthy',
            issues: [],
            recommendations: []
        };
        
        // 检查必要的DOM元素
        const requiredElements = [
            'time-range-select',
            'refresh-expectation-btn',
            'analysis-summary',
            'expected-return-rate',
            'actual-return-rate'
        ];
        
        requiredElements.forEach(id => {
            if (!document.getElementById(id)) {
                health.issues.push(`缺少必要元素: ${id}`);
                health.status = 'unhealthy';
            }
        });
        
        // 检查Chart.js是否可用
        if (typeof Chart === 'undefined') {
            health.issues.push('Chart.js未加载');
            health.status = 'unhealthy';
            health.recommendations.push('请检查Chart.js库是否正确加载');
        }
        
        // 检查性能指标
        if (this.performanceMetrics.loadTime > 5000) {
            health.issues.push('页面加载时间过长');
            health.recommendations.push('考虑优化资源加载');
        }
        
        if (this.performanceMetrics.apiResponseTime > 3000) {
            health.issues.push('API响应时间过长');
            health.recommendations.push('检查网络连接或服务器性能');
        }
        
        // 检查内存使用
        if (performance.memory && performance.memory.usedJSHeapSize > 50 * 1024 * 1024) {
            health.issues.push('内存使用过高');
            health.recommendations.push('考虑清理不必要的数据或重新加载页面');
        }
        
        return health;
    }
    
    /**
     * 性能监控
     */
    startPerformanceMonitoring() {
        // 监控API响应时间
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = performance.now();
            try {
                const response = await originalFetch(...args);
                const endTime = performance.now();
                this.performanceMetrics.apiResponseTime = endTime - startTime;
                return response;
            } catch (error) {
                const endTime = performance.now();
                this.performanceMetrics.apiResponseTime = endTime - startTime;
                throw error;
            }
        };
        
        // 定期健康检查
        setInterval(() => {
            const health = this.healthCheck();
            if (health.status === 'unhealthy') {
                console.warn('健康检查发现问题:', health.issues);
                if (health.recommendations.length > 0) {
                    console.info('建议:', health.recommendations);
                }
            }
        }, 30000); // 每30秒检查一次
    }
    
    /**
     * 清理资源
     */
    cleanup() {
        // 清理图表
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
        
        // 取消正在进行的请求
        if (this.currentRequest) {
            this.currentRequest.abort();
            this.currentRequest = null;
        }
        
        // 清理定时器
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = null;
        }
        
        // 清理事件监听器
        window.removeEventListener('resize', this.handleResize);
        
        console.log('期望对比管理器资源已清理');
    }
    
    /**
     * 获取调试信息
     * @returns {Object} 调试信息
     */
    getDebugInfo() {
        return {
            currentTimeRange: this.currentTimeRange,
            baseCapital: this.baseCapital,
            isLoading: this.isLoading,
            hasCurrentData: !!this.currentData,
            chartCount: Object.keys(this.charts).length,
            performanceMetrics: this.performanceMetrics,
            isMobile: this.isMobile,
            isTablet: this.isTablet,
            chartAnimationEnabled: this.chartAnimationEnabled,
            lastCacheKey: this.lastCacheKey,
            healthStatus: this.healthCheck()
        };
    }
    
    /**
     * 注册Chart.js插件
     */
    registerChartPlugins() {
        try {
            // 安全注册datalabels插件
            if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
                // 检查是否已经注册，避免重复注册
                if (!Chart.registry.plugins.has('datalabels')) {
                    Chart.register(ChartDataLabels);
                    console.log('Chart.js datalabels插件已注册');
                } else {
                    console.log('Chart.js datalabels插件已存在');
                }
            } else {
                console.warn('Chart.js或datalabels插件未找到，数据标签功能将被禁用');
            }
        } catch (error) {
            console.error('注册Chart.js插件时发生错误:', error);
        }
    }
    
    /**
     * 安全创建图表
     * @param {HTMLElement} ctx - Canvas元素
     * @param {Object} config - 图表配置
     * @returns {Chart|null} 图表实例或null
     */
    createSafeChart(ctx, config) {
        try {
            // 使用全局的安全图表创建函数
            if (typeof window.createSafeChart === 'function') {
                return window.createSafeChart(ctx, config);
            }
            
            // 备用方案：本地安全创建
            if (!ctx || !ctx.getContext) {
                console.error('无效的canvas元素');
                return null;
            }
            
            if (!config || !config.type) {
                console.error('无效的图表配置');
                return null;
            }
            
            // 使用全局安全的datalabels配置
            if (config.options && config.options.plugins && config.options.plugins.datalabels) {
                if (typeof window.getSafeDataLabelsConfig === 'function') {
                    config.options.plugins.datalabels = window.getSafeDataLabelsConfig();
                } else {
                    // 禁用 datalabels 以避免错误
                    config.options.plugins.datalabels = { display: false };
                }
            }
            
            // 添加错误处理
            config.options = config.options || {};
            config.options.onError = function(error) {
                console.warn('Chart.js错误已处理:', error);
            };
            
            return new Chart(ctx, config);
            
        } catch (error) {
            console.error('创建图表时发生错误:', error);
            return null;
        }
    }

    /**
     * 设置响应式设计
     */
    setupResponsiveDesign() {
        // 检测设备类型
        this.isMobile = window.innerWidth <= 768;
        this.isTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
        
        // 根据设备类型调整图表动画
        this.chartAnimationEnabled = !this.isMobile; // 移动设备禁用动画以提升性能
        
        // 监听窗口大小变化
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
        
        console.log(`设备类型检测: 移动设备=${this.isMobile}, 平板=${this.isTablet}`);
    }
    
    /**
     * 处理窗口大小变化
     */
    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        this.isTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
        
        // 如果设备类型发生变化，重新渲染图表
        if (wasMobile !== this.isMobile) {
            this.chartAnimationEnabled = !this.isMobile;
            if (this.currentData) {
                this.renderCharts(this.currentData);
            }
        }
    }
    
    /**
     * 防抖函数
     * @param {Function} func - 要防抖的函数
     * @param {number} wait - 等待时间（毫秒）
     * @returns {Function} 防抖后的函数
     */
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
    
    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 时间范围选择器事件
        const timeRangeSelect = document.getElementById('time-range-select');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (e) => {
                this.handleTimeRangeChange(e.target.value);
            });
        }
        
        // 刷新按钮事件
        const refreshBtn = document.getElementById('refresh-expectation-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }
        
        // Tab切换事件 - 当切换到期望对比tab时加载数据
        const expectationTab = document.getElementById('expectation-tab');
        if (expectationTab) {
            expectationTab.addEventListener('shown.bs.tab', () => {
                this.onTabActivated();
            });
        }
    }
    
    /**
     * 初始化UI状态
     */
    initializeUI() {
        // 设置默认时间范围
        const timeRangeSelect = document.getElementById('time-range-select');
        if (timeRangeSelect) {
            timeRangeSelect.value = this.currentTimeRange;
        }
        
        // 显示初始状态
        this.showInitialState();
    }
    
    /**
     * 显示初始状态
     */
    showInitialState() {
        const analysisSummary = document.getElementById('analysis-summary');
        if (analysisSummary) {
            analysisSummary.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-chart-line fa-3x mb-3 text-primary"></i>
                    <h5>期望对比分析</h5>
                    <p class="mb-3">将您的实际交易表现与基于概率模型的期望目标进行对比分析</p>
                    <div class="alert alert-info d-inline-block">
                        <i class="fas fa-info-circle me-2"></i>
                        请选择时间范围开始分析，或点击刷新按钮加载数据
                    </div>
                </div>
            `;
        }
        
        // 重置所有数据显示
        this.resetDataDisplay();
    }
    
    /**
     * 重置数据显示
     */
    resetDataDisplay() {
        // 重置对比卡片
        const cardElements = [
            'expected-return-rate', 'actual-return-rate', 'return-rate-diff-badge',
            'expected-return-amount', 'actual-return-amount', 'return-amount-diff-badge',
            'expected-holding-days', 'actual-holding-days', 'holding-days-diff-badge',
            'expected-success-rate', 'actual-success-rate', 'success-rate-diff-badge'
        ];
        
        cardElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                if (id.includes('diff-badge')) {
                    element.className = 'badge bg-secondary';
                    element.textContent = '待计算';
                } else {
                    element.textContent = '-';
                }
            }
        });
        
        // 清空图表
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
    
    /**
     * 当tab被激活时的处理
     */
    onTabActivated() {
        console.log('期望对比tab已激活');
        if (!this.currentData) {
            this.loadComparisonData();
        }
    }
    
    /**
     * 处理时间范围变更
     * @param {string} timeRange - 新的时间范围
     */
    handleTimeRangeChange(timeRange) {
        if (this.currentTimeRange === timeRange) {
            return;
        }
        
        console.log(`时间范围变更: ${this.currentTimeRange} -> ${timeRange}`);
        this.currentTimeRange = timeRange;
        this.loadComparisonData();
    }
    
    /**
     * 刷新数据
     */
    refreshData() {
        console.log('刷新期望对比数据...');
        this.loadComparisonData(true);
    }
    
    /**
     * 加载期望对比数据
     * @param {boolean} forceRefresh - 是否强制刷新
     */
    async loadComparisonData(forceRefresh = false) {
        if (this.isLoading && !forceRefresh) {
            console.log('数据正在加载中，跳过重复请求');
            return;
        }
        
        try {
            this.setLoadingState(true);
            
            console.log(`加载期望对比数据 - 时间范围: ${this.currentTimeRange}`);
            
            // 调用API获取数据
            const response = await this.fetchComparisonData();
            
            if (response && response.success) {
                this.currentData = response.data;
                this.renderComparisonData(response.data);
                this.showSuccessMessage('期望对比数据加载成功');
            } else {
                throw new Error(response?.message || '获取期望对比数据失败');
            }
            
        } catch (error) {
            console.error('加载期望对比数据失败:', error);
            this.handleError(error, '加载期望对比数据失败');
        } finally {
            this.setLoadingState(false);
        }
    }
    
    /**
     * 调用API获取期望对比数据
     * @returns {Promise<Object>} API响应数据
     */
    async fetchComparisonData() {
        const params = {
            time_range: this.currentTimeRange,
            base_capital: this.baseCapital
        };
        
        // 使用全局API客户端
        if (typeof window.apiClient !== 'undefined' && typeof window.apiClient.getExpectationComparison === 'function') {
            return await window.apiClient.getExpectationComparison(params);
        } else if (typeof window.apiClient !== 'undefined') {
            return await window.apiClient.request('GET', '/analytics/expectation-comparison', params);
        } else {
            // 备用方案：直接使用fetch
            const queryString = new URLSearchParams(params).toString();
            const response = await fetch(`/api/analytics/expectation-comparison?${queryString}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        }
    }
    
    /**
     * 渲染期望对比数据
     * @param {Object} data - 期望对比数据
     */
    renderComparisonData(data) {
        console.log('渲染期望对比数据:', data);
        
        try {
            // 渲染对比卡片
            this.renderComparisonCards(data);
            
            // 渲染图表
            this.renderCharts(data);
            
            // 渲染差异分析
            this.renderAnalysisSummary(data);
            
        } catch (error) {
            console.error('渲染期望对比数据失败:', error);
            this.handleError(error, '渲染数据失败');
        }
    }
    
    /**
     * 渲染对比卡片
     * @param {Object} data - 期望对比数据
     */
    renderComparisonCards(data) {
        const { expectation, actual, comparison } = data;
        
        // 收益率对比
        this.updateCardValue('expected-return-rate', this.formatPercentage(expectation.return_rate));
        this.updateCardValue('actual-return-rate', this.formatPercentage(actual.return_rate));
        this.updateDiffBadge('return-rate-diff-badge', comparison.return_rate_diff, true);
        
        // 收益金额对比
        this.updateCardValue('expected-return-amount', this.formatCurrency(expectation.return_amount));
        this.updateCardValue('actual-return-amount', this.formatCurrency(actual.return_amount));
        this.updateDiffBadge('return-amount-diff-badge', comparison.return_amount_diff, false);
        
        // 持仓天数对比
        this.updateCardValue('expected-holding-days', this.formatDays(expectation.holding_days));
        this.updateCardValue('actual-holding-days', this.formatDays(actual.holding_days));
        this.updateDiffBadge('holding-days-diff-badge', comparison.holding_days_diff, false);
        
        // 胜率对比
        this.updateCardValue('expected-success-rate', this.formatPercentage(expectation.success_rate));
        this.updateCardValue('actual-success-rate', this.formatPercentage(actual.success_rate));
        this.updateDiffBadge('success-rate-diff-badge', comparison.success_rate_diff, true);
    }
    
    /**
     * 更新卡片数值
     * @param {string} elementId - 元素ID
     * @param {string} value - 显示值
     */
    updateCardValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }
    
    /**
     * 更新差异徽章
     * @param {string} elementId - 元素ID
     * @param {number} diff - 差异值
     * @param {boolean} isPercentage - 是否为百分比
     */
    updateDiffBadge(elementId, diff, isPercentage = false) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        // 根据需求5.1-5.6实现差异分析和提示功能
        const absDiff = Math.abs(diff);
        let threshold, badgeClass, text, icon;
        
        // 根据不同指标设置阈值
        if (isPercentage) {
            // 收益率和胜率：±5%范围内为接近期望 (需求5.6)
            threshold = 0.05;
        } else if (elementId.includes('amount')) {
            // 收益金额：±1万元范围内为接近期望
            threshold = 10000;
        } else {
            // 持仓天数：±1天范围内为接近期望
            threshold = 1;
        }
        
        // 根据需求5.4-5.6设置颜色和文本
        if (absDiff <= threshold) {
            // 需求5.6：差异在±5%范围内使用黄色显示并标注"接近期望"
            badgeClass = 'bg-warning text-dark';
            text = '接近期望';
            icon = '≈';
        } else if (diff > 0) {
            // 需求5.4：差异为正值使用绿色显示并标注"超出期望"
            badgeClass = 'bg-success text-white';
            text = '超出期望';
            icon = '↑';
        } else {
            // 需求5.5：差异为负值使用红色显示并标注"低于期望"
            badgeClass = 'bg-danger text-white';
            text = '低于期望';
            icon = '↓';
        }
        
        // 格式化显示值
        let displayValue;
        if (isPercentage) {
            displayValue = this.formatPercentage(diff);
        } else if (elementId.includes('amount')) {
            displayValue = this.formatCurrency(diff);
        } else {
            displayValue = diff.toFixed(1);
        }
        
        // 更新徽章样式和内容
        element.className = `badge ${badgeClass}`;
        element.innerHTML = `${icon} ${displayValue} (${text})`;
        
        // 添加工具提示以提供更详细的差异分析
        element.title = this.generateDifferenceTooltip(elementId, diff, isPercentage);
    }
    
    /**
     * 生成差异分析工具提示
     * @param {string} elementId - 元素ID
     * @param {number} diff - 差异值
     * @param {boolean} isPercentage - 是否为百分比
     * @returns {string} 工具提示文本
     */
    generateDifferenceTooltip(elementId, diff, isPercentage) {
        const absDiff = Math.abs(diff);
        let metricName, unit, analysis;
        
        // 确定指标名称和单位
        if (elementId.includes('return-rate')) {
            metricName = '收益率';
            unit = '%';
        } else if (elementId.includes('return-amount')) {
            metricName = '收益金额';
            unit = '元';
        } else if (elementId.includes('holding-days')) {
            metricName = '持仓天数';
            unit = '天';
        } else if (elementId.includes('success-rate')) {
            metricName = '胜率';
            unit = '%';
        } else {
            metricName = '指标';
            unit = '';
        }
        
        // 生成分析文本
        if (diff > 0) {
            analysis = `实际${metricName}超出期望${absDiff.toFixed(2)}${unit}，表现优于预期`;
        } else if (diff < 0) {
            analysis = `实际${metricName}低于期望${absDiff.toFixed(2)}${unit}，有改进空间`;
        } else {
            analysis = `实际${metricName}与期望值完全一致`;
        }
        
        return analysis;
    }
    
    /**
     * 渲染图表
     * @param {Object} data - 期望对比数据
     */
    renderCharts(data) {
        try {
            // 使用requestAnimationFrame优化渲染性能
            requestAnimationFrame(() => {
                this.renderReturnComparisonChart(data);
            });
            
            requestAnimationFrame(() => {
                this.renderHoldingDaysChart(data);
            });
            
            requestAnimationFrame(() => {
                this.renderSuccessRateChart(data);
            });
            
            requestAnimationFrame(() => {
                this.renderPerformanceComparisonChart(data);
            });
            
            // 如果有专用的收益金额图表，也渲染它
            if (document.getElementById('revenue-amount-chart')) {
                requestAnimationFrame(() => {
                    this.renderRevenueAmountChart(data);
                });
            }
        } catch (error) {
            console.error('渲染图表失败:', error);
            this.showErrorMessage('图表渲染失败，请刷新页面重试');
        }
    }
    
    /**
     * 获取响应式图表配置
     * @param {string} chartType - 图表类型
     * @returns {Object} 响应式配置
     */
    getResponsiveConfig(chartType = 'default') {
        const baseConfig = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'nearest',
                intersect: false,
            },
            animation: {
                duration: this.chartAnimationEnabled ? 800 : 0,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    display: true,
                    position: this.isMobile ? 'bottom' : 'top',
                    labels: {
                        font: {
                            size: this.isMobile ? 10 : 12
                        },
                        padding: this.isMobile ? 10 : 20,
                        usePointStyle: true
                    }
                },
                title: {
                    display: true,
                    font: {
                        size: this.isMobile ? 12 : 16,
                        weight: 'bold'
                    },
                    padding: this.isMobile ? 10 : 20
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 6,
                    displayColors: true,
                    titleFont: {
                        size: this.isMobile ? 11 : 13
                    },
                    bodyFont: {
                        size: this.isMobile ? 10 : 12
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        lineWidth: 1
                    },
                    ticks: {
                        font: {
                            size: this.isMobile ? 9 : 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        lineWidth: 1
                    },
                    ticks: {
                        font: {
                            size: this.isMobile ? 9 : 11
                        }
                    }
                }
            }
        };
        
        // 根据图表类型调整配置
        switch (chartType) {
            case 'radar':
                baseConfig.scales = {
                    r: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        pointLabels: {
                            font: {
                                size: this.isMobile ? 9 : 11
                            }
                        },
                        ticks: {
                            font: {
                                size: this.isMobile ? 8 : 10
                            }
                        }
                    }
                };
                break;
            case 'doughnut':
            case 'pie':
                delete baseConfig.scales;
                baseConfig.plugins.legend.position = this.isMobile ? 'bottom' : 'right';
                break;
        }
        
        return baseConfig;
    }
    
    /**
     * 获取优化的颜色方案
     * @param {string} type - 颜色类型 ('expectation', 'actual', 'positive', 'negative', 'neutral')
     * @returns {Object} 颜色配置
     */
    getColorScheme(type) {
        const colors = {
            expectation: {
                background: 'rgba(54, 162, 235, 0.8)',
                border: 'rgba(54, 162, 235, 1)',
                hover: 'rgba(54, 162, 235, 0.9)'
            },
            actual: {
                background: 'rgba(255, 99, 132, 0.8)',
                border: 'rgba(255, 99, 132, 1)',
                hover: 'rgba(255, 99, 132, 0.9)'
            },
            positive: {
                background: 'rgba(75, 192, 192, 0.8)',
                border: 'rgba(75, 192, 192, 1)',
                hover: 'rgba(75, 192, 192, 0.9)'
            },
            negative: {
                background: 'rgba(255, 159, 64, 0.8)',
                border: 'rgba(255, 159, 64, 1)',
                hover: 'rgba(255, 159, 64, 0.9)'
            },
            neutral: {
                background: 'rgba(201, 203, 207, 0.8)',
                border: 'rgba(201, 203, 207, 1)',
                hover: 'rgba(201, 203, 207, 0.9)'
            }
        };
        
        return colors[type] || colors.neutral;
    }
    
    /**
     * 渲染收益金额专用对比图表（基于320万本金）
     * @param {Object} data - 期望对比数据
     */
    renderRevenueAmountChart(data) {
        // 检查是否有专用的收益金额图表容器
        const ctx = document.getElementById('revenue-amount-chart');
        if (!ctx) {
            // 如果没有专用容器，跳过此图表
            return;
        }
        
        // 销毁现有图表
        if (this.charts.revenueAmount) {
            this.charts.revenueAmount.destroy();
        }
        
        const { expectation, actual, comparison } = data;
        
        // 计算收益金额数据（转换为万元）
        const expectedAmount = expectation.return_amount / 10000;
        const actualAmount = actual.return_amount / 10000;
        const diffAmount = comparison.return_amount_diff / 10000;
        
        // 获取响应式配置
        const responsiveConfig = this.getResponsiveConfig('revenue');
        
        this.charts.revenueAmount = this.createSafeChart(ctx, {
            type: 'bar',
            data: {
                labels: ['期望收益', '实际收益', '收益差异'],
                datasets: [{
                    label: '收益金额 (万元)',
                    data: [expectedAmount, actualAmount, diffAmount],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',   // 期望 - 蓝色
                        'rgba(255, 99, 132, 0.8)',   // 实际 - 红色
                        diffAmount >= 0 ? 'rgba(75, 192, 192, 0.8)' : 'rgba(255, 159, 64, 0.8)' // 差异 - 绿色/橙色
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        diffAmount >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 6,
                    borderSkipped: false,
                }]
            },
            options: {
                ...responsiveConfig,
                indexAxis: 'y', // 水平柱状图
                interaction: {
                    mode: 'nearest',
                    intersect: false,
                },
                plugins: {
                    ...responsiveConfig.plugins,
                    title: {
                        ...responsiveConfig.plugins?.title,
                        display: true,
                        text: '收益金额对比分析 (基于320万本金)',
                        font: {
                            size: responsiveConfig.plugins?.title?.font?.size || 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        display: false // 隐藏图例，因为颜色已经很明确
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 6,
                        displayColors: true,
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                            label: function(context) {
                                const value = context.parsed.x;
                                return `${value.toFixed(2)}万元`;
                            },
                            afterBody: function(context) {
                                const label = context[0].label;
                                if (label === '收益差异') {
                                    const value = context[0].parsed.x;
                                    if (Math.abs(value) < 1) {
                                        return '表现接近期望';
                                    } else if (value > 0) {
                                        return '超出期望表现';
                                    } else {
                                        return '低于期望表现';
                                    }
                                }
                                return '';
                            }
                        }
                    },
                    datalabels: {
                        display: true,
                        anchor: 'end',
                        align: 'right',
                        formatter: function(value, context) {
                            return value.toFixed(1) + '万';
                        },
                        font: {
                            weight: 'bold',
                            size: 12
                        },
                        color: function(context) {
                            return context.dataset.borderColor[context.dataIndex];
                        },
                        padding: 4
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            lineWidth: 1
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            callback: function(value, index, values) {
                                return value.toFixed(1) + '万';
                            }
                        },
                        title: {
                            display: true,
                            text: '收益金额 (万元)',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: responsiveConfig.plugins?.legend?.labels?.font?.size || 12
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                onHover: (event, activeElements) => {
                    event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
                },
                onClick: (event, activeElements) => {
                    if (activeElements.length > 0) {
                        const element = activeElements[0];
                        const label = this.charts.revenueAmount.data.labels[element.index];
                        const value = this.charts.revenueAmount.data.datasets[0].data[element.index];
                        console.log(`点击了: ${label} - ${value.toFixed(2)}万元`);
                    }
                }
            }
        });
        
        // 添加交互功能
        this.addChartInteractions(this.charts.revenueAmount, '收益金额对比');
    }
    
    /**
     * 渲染收益对比图表
     * @param {Object} data - 期望对比数据
     */
    renderReturnComparisonChart(data) {
        const ctx = document.getElementById('return-comparison-chart');
        if (!ctx) return;
        
        // 销毁现有图表
        if (this.charts.returnComparison) {
            this.charts.returnComparison.destroy();
        }
        
        const { expectation, actual } = data;
        
        // 计算收益率和收益金额的数据
        const returnRateData = {
            expected: expectation.return_rate * 100,
            actual: actual.return_rate * 100
        };
        
        const returnAmountData = {
            expected: expectation.return_amount / 10000,
            actual: actual.return_amount / 10000
        };
        
        // 获取响应式配置
        const responsiveConfig = this.getResponsiveConfig('return');
        
        const expectationColors = this.getColorScheme('expectation');
        const actualColors = this.getColorScheme('actual');
        
        this.charts.returnComparison = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['收益率 (%)', '收益金额 (万元)'],
                datasets: [{
                    label: '期望值',
                    data: [returnRateData.expected, returnAmountData.expected],
                    backgroundColor: [
                        expectationColors.background,
                        expectationColors.background
                    ],
                    borderColor: [
                        expectationColors.border,
                        expectationColors.border
                    ],
                    borderWidth: 2,
                    borderRadius: this.isMobile ? 2 : 6,
                    borderSkipped: false,
                    hoverBackgroundColor: [
                        expectationColors.hover,
                        expectationColors.hover
                    ]
                }, {
                    label: '实际值',
                    data: [returnRateData.actual, returnAmountData.actual],
                    backgroundColor: [
                        actualColors.background,
                        actualColors.background
                    ],
                    borderColor: [
                        actualColors.border,
                        actualColors.border
                    ],
                    borderWidth: 2,
                    borderRadius: this.isMobile ? 2 : 6,
                    borderSkipped: false,
                    hoverBackgroundColor: [
                        actualColors.hover,
                        actualColors.hover
                    ]
                }]
            },
            options: {
                ...responsiveConfig,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    ...responsiveConfig.plugins,
                    title: {
                        ...responsiveConfig.plugins?.title,
                        display: true,
                        text: '收益率与收益金额对比 (基于320万本金)',
                        font: {
                            size: responsiveConfig.plugins?.title?.font?.size || 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        ...responsiveConfig.plugins?.legend,
                        labels: {
                            ...responsiveConfig.plugins?.legend?.labels,
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 6,
                        displayColors: true,
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                            label: function(context) {
                                const label = context.dataset.label;
                                const value = context.parsed.y;
                                const metric = context.label;
                                
                                if (metric.includes('收益率')) {
                                    return `${label}: ${value.toFixed(2)}%`;
                                } else {
                                    return `${label}: ${value.toFixed(2)}万元`;
                                }
                            },
                            afterBody: function(context) {
                                if (context.length === 2) {
                                    const expected = context[0].parsed.y;
                                    const actual = context[1].parsed.y;
                                    const diff = actual - expected;
                                    const metric = context[0].label;
                                    
                                    if (metric.includes('收益率')) {
                                        return `差异: ${diff > 0 ? '+' : ''}${diff.toFixed(2)}%`;
                                    } else {
                                        return `差异: ${diff > 0 ? '+' : ''}${diff.toFixed(2)}万元`;
                                    }
                                }
                                return '';
                            }
                        }
                    },
                    datalabels: {
                        display: true,
                        anchor: 'end',
                        align: 'top',
                        formatter: function(value, context) {
                            const metric = context.chart.data.labels[context.dataIndex];
                            if (metric.includes('收益率')) {
                                return value.toFixed(2) + '%';
                            } else {
                                return value.toFixed(1) + '万';
                            }
                        },
                        font: {
                            weight: 'bold',
                            size: 11
                        },
                        color: function(context) {
                            return context.dataset.borderColor[context.dataIndex];
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            lineWidth: 1
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            callback: function(value, index, values) {
                                // 动态格式化Y轴标签
                                if (value >= 1000) {
                                    return (value / 1000).toFixed(1) + 'K';
                                }
                                return value.toFixed(1);
                            }
                        },
                        title: {
                            display: true,
                            text: '数值',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                onHover: (event, activeElements) => {
                    event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
                },
                onClick: (event, activeElements) => {
                    if (activeElements.length > 0) {
                        const element = activeElements[0];
                        const datasetLabel = element.dataset.label;
                        const label = this.charts.returnComparison.data.labels[element.index];
                        console.log(`点击了: ${datasetLabel} - ${label}`);
                    }
                }
            }
        });
        
        // 添加交互功能
        this.addChartInteractions(this.charts.returnComparison, '收益对比');
    }
    
    /**
     * 渲染持仓天数对比柱状图
     * @param {Object} data - 期望对比数据
     */
    renderHoldingDaysChart(data) {
        const ctx = document.getElementById('holding-days-chart');
        if (!ctx) return;
        
        // 销毁现有图表
        if (this.charts.holdingDays) {
            this.charts.holdingDays.destroy();
        }
        
        const { expectation, actual, comparison } = data;
        
        // 获取响应式配置
        const responsiveConfig = this.getResponsiveConfig('holdingDays');
        
        this.charts.holdingDays = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['期望持仓天数', '实际持仓天数'],
                datasets: [{
                    label: '持仓天数 (天)',
                    data: [expectation.holding_days, actual.holding_days],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',   // 期望 - 蓝色
                        'rgba(255, 99, 132, 0.8)'    // 实际 - 红色
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 6,
                    borderSkipped: false,
                }]
            },
            options: {
                ...responsiveConfig,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    ...responsiveConfig.plugins,
                    title: {
                        ...responsiveConfig.plugins?.title,
                        display: true,
                        text: '持仓天数对比分析',
                        font: {
                            size: responsiveConfig.plugins?.title?.font?.size || 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        display: false // 隐藏图例，因为颜色已经很明确
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 6,
                        displayColors: true,
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                            label: function(context) {
                                const value = context.parsed.y;
                                return `${value.toFixed(1)}天`;
                            },
                            afterBody: function(context) {
                                if (context.length === 1) {
                                    const label = context[0].label;
                                    if (label.includes('实际')) {
                                        const diff = comparison.holding_days_diff;
                                        let performance = '';
                                        if (Math.abs(diff) <= 1) {
                                            performance = '接近期望';
                                        } else if (diff < 0) {
                                            performance = '优于期望 (持仓时间更短)';
                                        } else {
                                            performance = '低于期望 (持仓时间过长)';
                                        }
                                        return `差异: ${diff > 0 ? '+' : ''}${diff.toFixed(1)}天 (${performance})`;
                                    }
                                }
                                return '';
                            }
                        }
                    },
                    datalabels: {
                        display: true,
                        anchor: 'end',
                        align: 'top',
                        formatter: function(value, context) {
                            return value.toFixed(1) + '天';
                        },
                        font: {
                            weight: 'bold',
                            size: 12
                        },
                        color: function(context) {
                            return context.dataset.borderColor[context.dataIndex];
                        },
                        padding: 4
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            lineWidth: 1
                        },
                        ticks: {
                            font: {
                                size: 11
                            },
                            callback: function(value, index, values) {
                                return value.toFixed(1) + '天';
                            }
                        },
                        title: {
                            display: true,
                            text: '持仓天数 (天)',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                onHover: (event, activeElements) => {
                    event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
                },
                onClick: (event, activeElements) => {
                    if (activeElements.length > 0) {
                        const element = activeElements[0];
                        const label = this.charts.holdingDays.data.labels[element.index];
                        const value = this.charts.holdingDays.data.datasets[0].data[element.index];
                        console.log(`点击了: ${label} - ${value.toFixed(1)}天`);
                    }
                }
            }
        });
        
        // 添加交互功能
        this.addChartInteractions(this.charts.holdingDays, '持仓天数对比');
    }
    
    /**
     * 渲染胜率对比环形图
     * @param {Object} data - 期望对比数据
     */
    renderSuccessRateChart(data) {
        const ctx = document.getElementById('success-rate-chart');
        if (!ctx) return;
        
        // 销毁现有图表
        if (this.charts.successRate) {
            this.charts.successRate.destroy();
        }
        
        const { expectation, actual, comparison } = data;
        
        // 转换为百分比
        const expectedRate = expectation.success_rate * 100;
        const actualRate = actual.success_rate * 100;
        
        // 获取响应式配置
        const responsiveConfig = this.getResponsiveConfig('successRate');
        
        this.charts.successRate = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['期望胜率', '实际胜率'],
                datasets: [{
                    label: '胜率对比',
                    data: [expectedRate, actualRate],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',   // 期望 - 蓝色
                        'rgba(255, 99, 132, 0.8)'    // 实际 - 红色
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 3,
                    hoverBackgroundColor: [
                        'rgba(54, 162, 235, 0.9)',
                        'rgba(255, 99, 132, 0.9)'
                    ],
                    hoverBorderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    hoverBorderWidth: 4
                }]
            },
            options: {
                ...responsiveConfig,
                cutout: '50%', // 环形图的内圆大小
                interaction: {
                    mode: 'point',
                    intersect: true,
                },
                plugins: {
                    ...responsiveConfig.plugins,
                    title: {
                        ...responsiveConfig.plugins?.title,
                        display: true,
                        text: '胜率对比分析',
                        font: {
                            size: responsiveConfig.plugins?.title?.font?.size || 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        ...responsiveConfig.plugins?.legend,
                        position: 'bottom',
                        labels: {
                            ...responsiveConfig.plugins?.legend?.labels,
                            usePointStyle: true,
                            padding: 20,
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        return {
                                            text: `${label}: ${value.toFixed(1)}%`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].borderColor[i],
                                            lineWidth: data.datasets[0].borderWidth,
                                            pointStyle: 'circle',
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 6,
                        displayColors: true,
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                            label: function(context) {
                                const value = context.parsed;
                                return `胜率: ${value.toFixed(2)}%`;
                            },
                            afterBody: function(context) {
                                if (context.length === 1) {
                                    const label = context[0].label;
                                    if (label.includes('实际')) {
                                        const diff = comparison.success_rate_diff * 100;
                                        let performance = '';
                                        if (Math.abs(diff) <= 5) {
                                            performance = '接近期望';
                                        } else if (diff > 0) {
                                            performance = '超出期望';
                                        } else {
                                            performance = '低于期望';
                                        }
                                        return `差异: ${diff > 0 ? '+' : ''}${diff.toFixed(2)}% (${performance})`;
                                    }
                                }
                                return '';
                            }
                        }
                    },
                    datalabels: {
                        display: true,
                        backgroundColor: function(context) {
                            return context.dataset.borderColor[context.dataIndex];
                        },
                        borderColor: '#fff',
                        borderRadius: 4,
                        borderWidth: 2,
                        color: '#fff',
                        font: {
                            weight: 'bold',
                            size: 12
                        },
                        padding: 6,
                        formatter: function(value, context) {
                            return value.toFixed(1) + '%';
                        }
                    }
                },
                animation: {
                    duration: 1200,
                    easing: 'easeInOutQuart'
                },
                onHover: (event, activeElements) => {
                    event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
                },
                onClick: (event, activeElements) => {
                    if (activeElements.length > 0) {
                        const element = activeElements[0];
                        const label = this.charts.successRate.data.labels[element.index];
                        const value = this.charts.successRate.data.datasets[0].data[element.index];
                        console.log(`点击了: ${label} - ${value.toFixed(1)}%`);
                    }
                }
            }
        });
        
        // 添加交互功能
        this.addChartInteractions(this.charts.successRate, '胜率对比');
    }

    /**
     * 渲染表现对比图表
     * @param {Object} data - 期望对比数据
     */
    renderPerformanceComparisonChart(data) {
        const ctx = document.getElementById('performance-comparison-chart');
        if (!ctx) return;
        
        // 销毁现有图表
        if (this.charts.performanceComparison) {
            this.charts.performanceComparison.destroy();
        }
        
        const { expectation, actual } = data;
        
        // 准备雷达图数据
        const performanceMetrics = [
            {
                label: '持仓天数',
                expected: expectation.holding_days,
                actual: actual.holding_days,
                unit: '天',
                reverse: true // 持仓天数越少越好
            },
            {
                label: '胜率',
                expected: expectation.success_rate * 100,
                actual: actual.success_rate * 100,
                unit: '%',
                reverse: false // 胜率越高越好
            }
        ];
        
        // 获取响应式配置
        const responsiveConfig = this.getResponsiveConfig('performance');
        
        this.charts.performanceComparison = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: performanceMetrics.map(m => m.label),
                datasets: [{
                    label: '期望值',
                    data: performanceMetrics.map(m => m.expected),
                    backgroundColor: 'rgba(54, 162, 235, 0.15)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 3,
                    fill: true
                }, {
                    label: '实际值',
                    data: performanceMetrics.map(m => m.actual),
                    backgroundColor: 'rgba(255, 99, 132, 0.15)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 3,
                    fill: true
                }]
            },
            options: {
                ...responsiveConfig,
                interaction: {
                    mode: 'point',
                    intersect: true,
                },
                plugins: {
                    ...responsiveConfig.plugins,
                    title: {
                        ...responsiveConfig.plugins?.title,
                        display: true,
                        text: '持仓天数与胜率对比',
                        font: {
                            size: responsiveConfig.plugins?.title?.font?.size || 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        ...responsiveConfig.plugins?.legend,
                        labels: {
                            ...responsiveConfig.plugins?.legend?.labels,
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        cornerRadius: 6,
                        displayColors: true,
                        callbacks: {
                            title: function(context) {
                                const index = context[0].dataIndex;
                                return performanceMetrics[index].label;
                            },
                            label: function(context) {
                                const label = context.dataset.label;
                                const value = context.parsed.r;
                                const index = context.dataIndex;
                                const unit = performanceMetrics[index].unit;
                                
                                if (unit === '%') {
                                    return `${label}: ${value.toFixed(2)}%`;
                                } else {
                                    return `${label}: ${value.toFixed(1)}${unit}`;
                                }
                            },
                            afterBody: function(context) {
                                if (context.length === 2) {
                                    const expected = context[0].parsed.r;
                                    const actual = context[1].parsed.r;
                                    const diff = actual - expected;
                                    const index = context[0].dataIndex;
                                    const unit = performanceMetrics[index].unit;
                                    const isReverse = performanceMetrics[index].reverse;
                                    
                                    let diffText = '';
                                    if (unit === '%') {
                                        diffText = `差异: ${diff > 0 ? '+' : ''}${diff.toFixed(2)}%`;
                                    } else {
                                        diffText = `差异: ${diff > 0 ? '+' : ''}${diff.toFixed(1)}${unit}`;
                                    }
                                    
                                    // 添加表现评价
                                    let performance = '';
                                    if (Math.abs(diff) < (unit === '%' ? 5 : 1)) {
                                        performance = ' (接近期望)';
                                    } else if ((diff > 0 && !isReverse) || (diff < 0 && isReverse)) {
                                        performance = ' (优于期望)';
                                    } else {
                                        performance = ' (低于期望)';
                                    }
                                    
                                    return diffText + performance;
                                }
                                return '';
                            }
                        }
                    },
                    datalabels: {
                        display: true,
                        backgroundColor: function(context) {
                            return context.dataset.borderColor;
                        },
                        borderColor: '#fff',
                        borderRadius: 4,
                        borderWidth: 1,
                        color: '#fff',
                        font: {
                            weight: 'bold',
                            size: 10
                        },
                        padding: 4,
                        formatter: function(value, context) {
                            const index = context.dataIndex;
                            const unit = performanceMetrics[index].unit;
                            
                            if (unit === '%') {
                                return value.toFixed(1) + '%';
                            } else {
                                return value.toFixed(1) + unit;
                            }
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            lineWidth: 1
                        },
                        angleLines: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            lineWidth: 1
                        },
                        pointLabels: {
                            font: {
                                size: responsiveConfig.plugins?.legend?.labels?.font?.size || 12,
                                weight: 'bold'
                            },
                            color: '#333'
                        },
                        ticks: {
                            font: {
                                size: 10
                            },
                            color: '#666',
                            backdropColor: 'rgba(255, 255, 255, 0.8)',
                            backdropPadding: 2,
                            callback: function(value, index, values) {
                                // 动态格式化刻度标签
                                if (value >= 100) {
                                    return value.toFixed(0);
                                } else if (value >= 10) {
                                    return value.toFixed(1);
                                } else {
                                    return value.toFixed(2);
                                }
                            }
                        },
                        suggestedMin: 0,
                        suggestedMax: function() {
                            // 动态计算最大值
                            const maxHoldingDays = Math.max(expectation.holding_days, actual.holding_days);
                            const maxSuccessRate = Math.max(expectation.success_rate * 100, actual.success_rate * 100);
                            return Math.max(maxHoldingDays * 1.2, maxSuccessRate * 1.2);
                        }()
                    }
                },
                animation: {
                    duration: 1200,
                    easing: 'easeInOutQuart'
                },
                onHover: (event, activeElements) => {
                    event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
                },
                onClick: (event, activeElements) => {
                    if (activeElements.length > 0) {
                        const element = activeElements[0];
                        const datasetLabel = element.dataset.label;
                        const metricIndex = element.index;
                        const metric = performanceMetrics[metricIndex];
                        console.log(`点击了: ${datasetLabel} - ${metric.label}`);
                    }
                }
            }
        });
        
        // 添加交互功能
        this.addChartInteractions(this.charts.performanceComparison, '表现对比');
    }
    
    /**
     * 渲染差异分析摘要
     * @param {Object} data - 期望对比数据
     */
    renderAnalysisSummary(data) {
        const analysisSummary = document.getElementById('analysis-summary');
        if (!analysisSummary) return;
        
        const { expectation, actual, comparison, time_range } = data;
        const timeRangeLabel = this.timeRangeConfig[time_range]?.label || '选定时间范围';
        
        // 生成详细的差异分析报告
        const detailedAnalysis = this.generateDetailedDifferenceAnalysis(expectation, actual, comparison);
        
        const summaryHtml = `
            <div class="row">
                <div class="col-12 mb-3">
                    <h6 class="text-primary">
                        <i class="fas fa-chart-area me-2"></i>
                        ${timeRangeLabel}内的差异分析报告
                    </h6>
                </div>
            </div>
            
            <!-- 差异概览卡片 -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card border-primary">
                        <div class="card-header bg-primary text-white">
                            <h6 class="card-title mb-0">
                                <i class="fas fa-balance-scale me-2"></i>
                                核心指标差异概览
                            </h6>
                        </div>
                        <div class="card-body">
                            ${detailedAnalysis.overview}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card border-0 bg-light">
                        <div class="card-body">
                            <h6 class="card-title text-success">
                                <i class="fas fa-arrow-up me-1"></i>优势表现
                            </h6>
                            ${this.generatePositiveAnalysis(comparison)}
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card border-0 bg-light">
                        <div class="card-body">
                            <h6 class="card-title text-warning">
                                <i class="fas fa-exclamation-triangle me-1"></i>改进空间
                            </h6>
                            ${this.generateImprovementAnalysis(comparison)}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 详细差异分析 -->
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="card-title mb-0">
                                <i class="fas fa-microscope me-2"></i>
                                详细差异分析
                            </h6>
                        </div>
                        <div class="card-body">
                            ${detailedAnalysis.detailed}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>分析说明：</strong>
                        基于320万本金的标准化对比分析（自2025年8月1日起计算），期望值来源于概率模型计算。
                        ${detailedAnalysis.recommendation}
                    </div>
                    
                    ${time_range.base_capital_start_note ? `
                    <div class="alert alert-warning">
                        <i class="fas fa-calendar-alt me-2"></i>
                        <strong>重要说明：</strong>
                        ${time_range.base_capital_start_note}，只有此日期及之后的交易记录参与期望对比计算。
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        analysisSummary.innerHTML = summaryHtml;
    }
    
    /**
     * 生成详细的差异分析报告
     * @param {Object} expectation - 期望数据
     * @param {Object} actual - 实际数据
     * @param {Object} comparison - 对比数据
     * @returns {Object} 详细分析结果
     */
    generateDetailedDifferenceAnalysis(expectation, actual, comparison) {
        // 计算各项差异的百分比和绝对值
        const returnRateDiff = comparison.return_rate_diff;
        const returnAmountDiff = comparison.return_amount_diff;
        const holdingDaysDiff = comparison.holding_days_diff;
        const successRateDiff = comparison.success_rate_diff;
        
        // 生成概览分析
        const overviewItems = [];
        
        // 收益率差异分析 (需求5.1)
        const returnRatePercent = (returnRateDiff / expectation.return_rate * 100);
        overviewItems.push({
            metric: '收益率',
            expected: this.formatPercentage(expectation.return_rate),
            actual: this.formatPercentage(actual.return_rate),
            diff: this.formatPercentage(returnRateDiff),
            status: this.getDifferenceStatus(returnRateDiff, 0.05, true),
            impact: returnRatePercent.toFixed(1) + '%'
        });
        
        // 收益金额差异分析 (需求5.2)
        const amountPercent = (returnAmountDiff / expectation.return_amount * 100);
        overviewItems.push({
            metric: '收益金额',
            expected: this.formatCurrency(expectation.return_amount),
            actual: this.formatCurrency(actual.return_amount),
            diff: this.formatCurrency(returnAmountDiff),
            status: this.getDifferenceStatus(returnAmountDiff, 10000, false),
            impact: amountPercent.toFixed(1) + '%'
        });
        
        // 持仓天数差异分析 (需求5.3)
        const holdingPercent = (holdingDaysDiff / expectation.holding_days * 100);
        overviewItems.push({
            metric: '持仓天数',
            expected: this.formatDays(expectation.holding_days),
            actual: this.formatDays(actual.holding_days),
            diff: (holdingDaysDiff > 0 ? '+' : '') + holdingDaysDiff.toFixed(1) + '天',
            status: this.getDifferenceStatus(holdingDaysDiff, 1, false),
            impact: holdingPercent.toFixed(1) + '%'
        });
        
        // 胜率差异分析
        const successPercent = (successRateDiff / expectation.success_rate * 100);
        overviewItems.push({
            metric: '胜率',
            expected: this.formatPercentage(expectation.success_rate),
            actual: this.formatPercentage(actual.success_rate),
            diff: this.formatPercentage(successRateDiff),
            status: this.getDifferenceStatus(successRateDiff, 0.05, true),
            impact: successPercent.toFixed(1) + '%'
        });
        
        // 生成概览HTML
        const overviewHtml = `
            <div class="table-responsive">
                <table class="table table-sm table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>指标</th>
                            <th>期望值</th>
                            <th>实际值</th>
                            <th>差异</th>
                            <th>状态</th>
                            <th>影响程度</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${overviewItems.map(item => `
                            <tr>
                                <td><strong>${item.metric}</strong></td>
                                <td>${item.expected}</td>
                                <td>${item.actual}</td>
                                <td>${item.diff}</td>
                                <td>${item.status.html}</td>
                                <td>${item.impact}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        // 生成详细分析
        const detailedHtml = this.generateDetailedAnalysisText(overviewItems);
        
        // 生成建议
        const recommendation = this.generateRecommendation(overviewItems);
        
        return {
            overview: overviewHtml,
            detailed: detailedHtml,
            recommendation: recommendation
        };
    }
    
    /**
     * 获取差异状态
     * @param {number} diff - 差异值
     * @param {number} threshold - 阈值
     * @param {boolean} isPercentage - 是否为百分比
     * @returns {Object} 状态信息
     */
    getDifferenceStatus(diff, threshold, isPercentage) {
        const absDiff = Math.abs(diff);
        
        if (absDiff <= threshold) {
            return {
                class: 'warning',
                text: '接近期望',
                icon: '≈',
                html: '<span class="badge bg-warning text-dark">≈ 接近期望</span>'
            };
        } else if (diff > 0) {
            return {
                class: 'success',
                text: '超出期望',
                icon: '↑',
                html: '<span class="badge bg-success">↑ 超出期望</span>'
            };
        } else {
            return {
                class: 'danger',
                text: '低于期望',
                icon: '↓',
                html: '<span class="badge bg-danger">↓ 低于期望</span>'
            };
        }
    }
    
    /**
     * 生成详细分析文本
     * @param {Array} items - 分析项目
     * @returns {string} 详细分析HTML
     */
    generateDetailedAnalysisText(items) {
        const analyses = items.map(item => {
            let analysis = '';
            const impact = parseFloat(item.impact);
            
            if (item.status.class === 'success') {
                analysis = `<div class="alert alert-success alert-sm">
                    <strong>${item.metric}表现优异：</strong>
                    实际值${item.actual}超出期望值${item.expected}，
                    差异为${item.diff}，相对提升${Math.abs(impact).toFixed(1)}%。
                </div>`;
            } else if (item.status.class === 'danger') {
                analysis = `<div class="alert alert-danger alert-sm">
                    <strong>${item.metric}需要改进：</strong>
                    实际值${item.actual}低于期望值${item.expected}，
                    差异为${item.diff}，相对下降${Math.abs(impact).toFixed(1)}%。
                </div>`;
            } else {
                analysis = `<div class="alert alert-warning alert-sm">
                    <strong>${item.metric}表现稳定：</strong>
                    实际值${item.actual}接近期望值${item.expected}，
                    差异为${item.diff}，波动幅度${Math.abs(impact).toFixed(1)}%。
                </div>`;
            }
            
            return analysis;
        });
        
        return analyses.join('');
    }
    
    /**
     * 生成建议
     * @param {Array} items - 分析项目
     * @returns {string} 建议文本
     */
    generateRecommendation(items) {
        const improvements = items.filter(item => item.status.class === 'danger');
        const strengths = items.filter(item => item.status.class === 'success');
        
        if (improvements.length === 0) {
            return '当前交易表现整体符合或超出期望，建议保持现有策略并继续优化。';
        } else if (improvements.length >= 3) {
            return `发现${improvements.length}项指标低于期望，建议重新评估交易策略，重点关注${improvements[0].metric}和${improvements[1].metric}的改进。`;
        } else {
            const improvementMetrics = improvements.map(item => item.metric).join('和');
            return `建议重点改进${improvementMetrics}，同时保持${strengths.length > 0 ? strengths[0].metric : '其他指标'}的优势表现。`;
        }
    }
    
    /**
     * 生成正面分析内容
     * @param {Object} comparison - 对比数据
     * @returns {string} HTML内容
     */
    generatePositiveAnalysis(comparison) {
        const positives = [];
        
        // 收益率分析 - 需求5.1和5.4
        if (comparison.return_rate_diff > 0.01) {
            const improvement = (comparison.return_rate_diff * 100).toFixed(2);
            positives.push({
                text: `收益率超出期望 ${this.formatPercentage(comparison.return_rate_diff)}`,
                detail: `相对提升${improvement}个百分点`,
                icon: 'fas fa-chart-line text-success'
            });
        }
        
        // 收益金额分析 - 需求5.2和5.4
        if (comparison.return_amount_diff > 10000) {
            const amount = this.formatCurrency(comparison.return_amount_diff);
            positives.push({
                text: `收益金额超出期望 ${amount}`,
                detail: `基于320万本金的额外收益`,
                icon: 'fas fa-coins text-success'
            });
        }
        
        // 胜率分析 - 需求5.4
        if (comparison.success_rate_diff > 0.05) {
            const improvement = (comparison.success_rate_diff * 100).toFixed(2);
            positives.push({
                text: `胜率超出期望 ${this.formatPercentage(comparison.success_rate_diff)}`,
                detail: `成功率提升${improvement}个百分点`,
                icon: 'fas fa-trophy text-success'
            });
        }
        
        // 持仓天数分析 - 需求5.3和5.4（持仓天数少是优势）
        if (comparison.holding_days_diff < -1) {
            const days = Math.abs(comparison.holding_days_diff).toFixed(1);
            positives.push({
                text: `持仓天数比期望少 ${days}天`,
                detail: `资金周转效率更高`,
                icon: 'fas fa-clock text-success'
            });
        }
        
        if (positives.length === 0) {
            return `
                <div class="text-center text-muted">
                    <i class="fas fa-info-circle fa-2x mb-2"></i>
                    <p class="mb-0">暂无明显优势表现</p>
                    <small>继续努力，争取超越期望目标</small>
                </div>
            `;
        }
        
        const positivesHtml = positives.map(p => `
            <div class="d-flex align-items-start mb-2">
                <i class="${p.icon} me-2 mt-1"></i>
                <div>
                    <div class="fw-bold">${p.text}</div>
                    <small class="text-muted">${p.detail}</small>
                </div>
            </div>
        `).join('');
        
        return `
            <div class="mb-2">
                ${positivesHtml}
            </div>
            <div class="alert alert-success alert-sm mb-0">
                <i class="fas fa-thumbs-up me-1"></i>
                <small>发现 ${positives.length} 项优势表现，继续保持！</small>
            </div>
        `;
    }
    
    /**
     * 生成改进分析内容
     * @param {Object} comparison - 对比数据
     * @returns {string} HTML内容
     */
    generateImprovementAnalysis(comparison) {
        const improvements = [];
        
        // 收益率改进分析 - 需求5.1和5.5
        if (comparison.return_rate_diff < -0.01) {
            const gap = Math.abs(comparison.return_rate_diff * 100).toFixed(2);
            improvements.push({
                text: `收益率低于期望 ${this.formatPercentage(Math.abs(comparison.return_rate_diff))}`,
                detail: `需要提升${gap}个百分点`,
                priority: 'high',
                icon: 'fas fa-chart-line text-danger'
            });
        }
        
        // 收益金额改进分析 - 需求5.2和5.5
        if (comparison.return_amount_diff < -10000) {
            const amount = this.formatCurrency(Math.abs(comparison.return_amount_diff));
            improvements.push({
                text: `收益金额低于期望 ${amount}`,
                detail: `基于320万本金的收益缺口`,
                priority: 'high',
                icon: 'fas fa-coins text-danger'
            });
        }
        
        // 胜率改进分析 - 需求5.5
        if (comparison.success_rate_diff < -0.05) {
            const gap = Math.abs(comparison.success_rate_diff * 100).toFixed(2);
            improvements.push({
                text: `胜率低于期望 ${this.formatPercentage(Math.abs(comparison.success_rate_diff))}`,
                detail: `成功率需提升${gap}个百分点`,
                priority: 'medium',
                icon: 'fas fa-target text-warning'
            });
        }
        
        // 持仓天数改进分析 - 需求5.3和5.5（持仓天数长需要改进）
        if (comparison.holding_days_diff > 1) {
            const days = comparison.holding_days_diff.toFixed(1);
            improvements.push({
                text: `持仓天数超出期望 ${days}天`,
                detail: `资金周转效率需要提升`,
                priority: 'medium',
                icon: 'fas fa-clock text-warning'
            });
        }
        
        if (improvements.length === 0) {
            return `
                <div class="text-center text-muted">
                    <i class="fas fa-check-circle fa-2x mb-2 text-success"></i>
                    <p class="mb-0">表现接近期望目标</p>
                    <small>各项指标均在合理范围内</small>
                </div>
            `;
        }
        
        // 按优先级排序
        improvements.sort((a, b) => {
            const priorityOrder = { high: 3, medium: 2, low: 1 };
            return priorityOrder[b.priority] - priorityOrder[a.priority];
        });
        
        const improvementsHtml = improvements.map(imp => `
            <div class="d-flex align-items-start mb-2">
                <i class="${imp.icon} me-2 mt-1"></i>
                <div>
                    <div class="fw-bold">${imp.text}</div>
                    <small class="text-muted">${imp.detail}</small>
                    ${imp.priority === 'high' ? '<span class="badge bg-danger badge-sm ms-2">高优先级</span>' : ''}
                </div>
            </div>
        `).join('');
        
        const highPriorityCount = improvements.filter(imp => imp.priority === 'high').length;
        const alertClass = highPriorityCount > 0 ? 'alert-danger' : 'alert-warning';
        const alertIcon = highPriorityCount > 0 ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
        
        return `
            <div class="mb-2">
                ${improvementsHtml}
            </div>
            <div class="alert ${alertClass} alert-sm mb-0">
                <i class="${alertIcon} me-1"></i>
                <small>发现 ${improvements.length} 项改进机会${highPriorityCount > 0 ? `，其中 ${highPriorityCount} 项为高优先级` : ''}</small>
            </div>
        `;
    }
    
    /**
     * 设置加载状态
     * @param {boolean} loading - 是否加载中
     */
    setLoadingState(loading) {
        this.isLoading = loading;
        
        const refreshBtn = document.getElementById('refresh-expectation-btn');
        const timeRangeSelect = document.getElementById('time-range-select');
        
        if (refreshBtn) {
            refreshBtn.disabled = loading;
            const icon = refreshBtn.querySelector('i');
            if (icon) {
                icon.className = loading ? 'fas fa-spinner fa-spin me-1' : 'fas fa-sync-alt me-1';
            }
        }
        
        if (timeRangeSelect) {
            timeRangeSelect.disabled = loading;
        }
        
        if (loading) {
            this.showLoadingState();
        }
    }
    
    /**
     * 显示加载状态
     */
    showLoadingState() {
        const analysisSummary = document.getElementById('analysis-summary');
        if (analysisSummary) {
            analysisSummary.innerHTML = `
                <div class="text-center text-muted">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    <span>正在加载期望对比数据...</span>
                </div>
            `;
        }
        
        // 重置数据显示
        this.resetDataDisplay();
    }
    
    /**
     * 重置数据显示
     */
    resetDataDisplay() {
        const dataElements = [
            'expected-return-rate', 'actual-return-rate', 'return-rate-diff-badge',
            'expected-return-amount', 'actual-return-amount', 'return-amount-diff-badge',
            'expected-holding-days', 'actual-holding-days', 'holding-days-diff-badge',
            'expected-success-rate', 'actual-success-rate', 'success-rate-diff-badge'
        ];
        
        dataElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = '-';
                element.className = element.className.replace(/bg-\w+/g, '');
            }
        });
    }
    
    /**
     * 处理错误
     * @param {Error} error - 错误对象
     * @param {string} context - 错误上下文
     */
    handleError(error, context = '操作') {
        console.error(`${context}:`, error);
        
        const errorMessage = this.getErrorMessage(error);
        this.showErrorMessage(errorMessage);
        
        // 显示错误状态
        const analysisSummary = document.getElementById('analysis-summary');
        if (analysisSummary) {
            analysisSummary.innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>${errorMessage}</p>
                    <button class="btn btn-outline-primary btn-sm" onclick="expectationComparisonManager.refreshData()">
                        <i class="fas fa-retry me-1"></i>重试
                    </button>
                </div>
            `;
        }
    }
    
    /**
     * 获取错误消息
     * @param {Error} error - 错误对象
     * @returns {string} 错误消息
     */
    getErrorMessage(error) {
        if (error.code === 'VALIDATION_ERROR') {
            return '请求参数错误，请检查时间范围设置';
        } else if (error.code === 'NETWORK_ERROR') {
            return '网络连接失败，请检查网络设置';
        } else if (error.message) {
            return error.message;
        } else {
            return '加载期望对比数据失败，请稍后重试';
        }
    }
    
    /**
     * 显示成功消息
     * @param {string} message - 消息内容
     */
    showSuccessMessage(message) {
        if (typeof showMessage === 'function') {
            showMessage(message, 'success');
        } else {
            console.log('Success:', message);
        }
    }
    
    /**
     * 显示错误消息
     * @param {string} message - 消息内容
     */
    showErrorMessage(message) {
        if (typeof showMessage === 'function') {
            showMessage(message, 'error');
        } else {
            console.error('Error:', message);
        }
    }
    
    /**
     * 格式化百分比
     * @param {number} value - 数值
     * @returns {string} 格式化后的百分比
     */
    formatPercentage(value) {
        if (value === null || value === undefined || isNaN(value)) {
            return '0.00%';
        }
        return `${(value * 100).toFixed(2)}%`;
    }
    
    /**
     * 格式化货币
     * @param {number} value - 数值
     * @returns {string} 格式化后的货币
     */
    formatCurrency(value) {
        if (value === null || value === undefined || isNaN(value)) {
            return '¥0.00';
        }
        return `¥${value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    
    /**
     * 格式化天数
     * @param {number} value - 数值
     * @returns {string} 格式化后的天数
     */
    formatDays(value) {
        if (value === null || value === undefined || isNaN(value)) {
            return '0天';
        }
        return `${value.toFixed(1)}天`;
    }
    
    /**
     * 处理窗口大小变化的响应式设计
     */
    handleResize() {
        // 重新调整所有图表大小
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }
    
    /**
     * 设置响应式行为
     */
    setupResponsiveDesign() {
        // 监听窗口大小变化
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
        
        // 监听设备方向变化
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleResize();
            }, 500);
        });
    }
    
    /**
     * 获取响应式图表配置
     * @param {string} chartType - 图表类型
     * @returns {Object} 响应式配置
     */
    getResponsiveConfig(chartType) {
        const baseConfig = {
            responsive: true,
            maintainAspectRatio: false,
        };
        
        // 根据屏幕大小调整配置
        const screenWidth = window.innerWidth;
        
        if (screenWidth < 576) {
            // 小屏幕配置
            return {
                ...baseConfig,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            font: {
                                size: 10
                            }
                        }
                    },
                    title: {
                        font: {
                            size: 14
                        }
                    }
                }
            };
        } else if (screenWidth < 768) {
            // 中等屏幕配置
            return {
                ...baseConfig,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            boxWidth: 14,
                            font: {
                                size: 11
                            }
                        }
                    },
                    title: {
                        font: {
                            size: 15
                        }
                    }
                }
            };
        } else {
            // 大屏幕配置
            return {
                ...baseConfig,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            boxWidth: 16,
                            font: {
                                size: 12
                            }
                        }
                    },
                    title: {
                        font: {
                            size: 16
                        }
                    }
                }
            };
        }
    }
    
    /**
     * 添加图表交互功能
     * @param {Chart} chart - Chart.js实例
     * @param {string} chartType - 图表类型
     */
    addChartInteractions(chart, chartType) {
        // 添加双击重置功能
        chart.canvas.addEventListener('dblclick', () => {
            chart.resetZoom();
            console.log(`${chartType}图表已重置缩放`);
        });
        
        // 添加键盘导航支持
        chart.canvas.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                chart.resetZoom();
            }
        });
        
        // 设置canvas为可聚焦
        chart.canvas.setAttribute('tabindex', '0');
        chart.canvas.setAttribute('role', 'img');
        chart.canvas.setAttribute('aria-label', `${chartType}对比图表`);
    }
    
    /**
     * 加载月度期望收益数据
     */
    async loadMonthlyExpectations() {
        try {
            console.log('加载月度期望收益数据...');
            
            const response = await fetch('/api/analytics/monthly-expectations');
            const result = await response.json();
            
            if (result.success) {
                this.monthlyExpectations = result.data;
                this.renderMonthlyExpectationsList();
                console.log('月度期望收益数据加载成功');
            } else {
                throw new Error(result.message || '获取月度期望数据失败');
            }
        } catch (error) {
            console.error('加载月度期望数据失败:', error);
            this.showMonthlyExpectationError('加载月度数据失败: ' + error.message);
        }
    }
    
    /**
     * 渲染月度期望收益列表
     */
    renderMonthlyExpectationsList() {
        const listContainer = document.getElementById('monthly-expectation-list');
        
        if (!this.monthlyExpectations || this.monthlyExpectations.length === 0) {
            listContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-triangle fa-2x text-warning mb-2"></i>
                    <p class="text-muted">暂无月度数据</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        this.monthlyExpectations.forEach((item, index) => {
            const isActive = this.selectedMonthIndex === index;
            html += `
                <div class="list-group-item list-group-item-action ${isActive ? 'active' : ''}" 
                     onclick="expectationComparisonManager.selectMonth(${index})" 
                     style="cursor: pointer;">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${item.month}</h6>
                            <small class="text-muted">期望收益: ${this.formatCurrency(item.expected_amount)}</small>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">收益率: ${item.expected_rate}%</small><br>
                            <small class="text-muted">本金: ${this.formatCurrency(item.start_capital)}</small>
                        </div>
                    </div>
                </div>
            `;
        });
        
        listContainer.innerHTML = html;
    }
    
    /**
     * 选择月份
     */
    async selectMonth(index) {
        this.selectedMonthIndex = index;
        this.renderMonthlyExpectationsList(); // 重新渲染以更新选中状态
        
        const selectedMonth = this.monthlyExpectations[index];
        
        // 解析年月
        const match = selectedMonth.month.match(/(\d{4})年(\d{2})月/);
        if (!match) {
            this.showMonthlyComparisonError('月份格式错误');
            return;
        }
        
        const year = parseInt(match[1]);
        const month = parseInt(match[2]);
        
        await this.loadMonthlyComparison(year, month);
    }
    
    /**
     * 加载月度对比数据
     */
    async loadMonthlyComparison(year, month) {
        try {
            const response = await fetch(`/api/analytics/monthly-comparison?year=${year}&month=${month}`);
            const result = await response.json();
            
            if (result.success) {
                this.renderMonthlyComparisonDetail(result.data);
            } else {
                throw new Error(result.message || '获取对比数据失败');
            }
        } catch (error) {
            console.error('加载月度对比数据失败:', error);
            this.showMonthlyComparisonError('加载对比数据失败: ' + error.message);
        }
    }
    
    /**
     * 渲染月度对比详情
     */
    renderMonthlyComparisonDetail(data) {
        const detailContainer = document.getElementById('monthly-comparison-detail');
        
        const expected = data.expected;
        const actual = data.actual;
        const comparison = data.comparison;
        
        detailContainer.innerHTML = `
            <div class="card border-0">
                <div class="card-header bg-light">
                    <h6 class="mb-0">
                        <i class="fas fa-chart-bar me-2"></i>${data.month_str} 期望与实际对比
                    </h6>
                </div>
                <div class="card-body">
                    <!-- 概览卡片 -->
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <div class="card border-primary">
                                <div class="card-body text-center py-3">
                                    <h6 class="card-title text-primary mb-2">
                                        <i class="fas fa-target me-1"></i>期望收益
                                    </h6>
                                    <h4 class="text-primary mb-1">${this.formatCurrency(expected.expected_amount)}</h4>
                                    <p class="text-muted mb-0 small">收益率: ${expected.expected_rate}%</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card border-success">
                                <div class="card-body text-center py-3">
                                    <h6 class="card-title text-success mb-2">
                                        <i class="fas fa-chart-line me-1"></i>实际收益
                                    </h6>
                                    <h4 class="${actual.total_profit >= 0 ? 'text-success' : 'text-danger'} mb-1">
                                        ${this.formatCurrency(actual.total_profit)}
                                    </h4>
                                    <p class="text-muted mb-0 small">收益率: ${(actual.return_rate * 100).toFixed(2)}%</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 详细对比表格 -->
                    <div class="table-responsive">
                        <table class="table table-sm table-striped">
                            <thead class="table-light">
                                <tr>
                                    <th>指标</th>
                                    <th>期望值</th>
                                    <th>实际值</th>
                                    <th>差异</th>
                                    <th>表现</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><i class="fas fa-coins me-1"></i>收益金额</td>
                                    <td>${this.formatCurrency(expected.expected_amount)}</td>
                                    <td class="${actual.total_profit >= 0 ? 'text-success' : 'text-danger'}">
                                        ${this.formatCurrency(actual.total_profit)}
                                    </td>
                                    <td class="${comparison.amount_diff >= 0 ? 'text-success' : 'text-danger'}">
                                        ${this.formatCurrency(comparison.amount_diff)}
                                        <br><small>(${comparison.amount_diff_pct.toFixed(1)}%)</small>
                                    </td>
                                    <td>
                                        <span class="badge bg-${comparison.amount_status.color}">
                                            ${comparison.amount_status.message}
                                        </span>
                                    </td>
                                </tr>
                                <tr>
                                    <td><i class="fas fa-percentage me-1"></i>收益率</td>
                                    <td>${expected.expected_rate}%</td>
                                    <td class="${actual.return_rate >= 0 ? 'text-success' : 'text-danger'}">
                                        ${(actual.return_rate * 100).toFixed(2)}%
                                    </td>
                                    <td class="${comparison.rate_diff >= 0 ? 'text-success' : 'text-danger'}">
                                        ${(comparison.rate_diff * 100).toFixed(2)}%
                                        <br><small>(${comparison.rate_diff_pct.toFixed(1)}%)</small>
                                    </td>
                                    <td>
                                        <span class="badge bg-${comparison.rate_status.color}">
                                            ${comparison.rate_status.message}
                                        </span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- 交易统计 -->
                    <div class="row mt-3">
                        <div class="col-12">
                            <h6 class="mb-2"><i class="fas fa-chart-pie me-2"></i>交易统计</h6>
                            <div class="row text-center">
                                <div class="col-3">
                                    <div class="border rounded p-2">
                                        <h6 class="text-primary mb-0">${actual.total_trades}</h6>
                                        <small class="text-muted">交易次数</small>
                                    </div>
                                </div>
                                <div class="col-3">
                                    <div class="border rounded p-2">
                                        <h6 class="text-info mb-0">${this.formatCurrency(actual.buy_amount)}</h6>
                                        <small class="text-muted">买入金额</small>
                                    </div>
                                </div>
                                <div class="col-3">
                                    <div class="border rounded p-2">
                                        <h6 class="text-warning mb-0">${this.formatCurrency(actual.sell_amount)}</h6>
                                        <small class="text-muted">卖出金额</small>
                                    </div>
                                </div>
                                <div class="col-3">
                                    <div class="border rounded p-2">
                                        <h6 class="text-success mb-0">${this.formatCurrency(expected.start_capital)}</h6>
                                        <small class="text-muted">期望本金</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * 格式化货币显示
     */
    formatCurrency(amount) {
        if (amount === 0) return '¥0';
        
        const absAmount = Math.abs(amount);
        let formatted;
        
        if (absAmount >= 100000000) { // 1亿以上
            formatted = (absAmount / 100000000).toFixed(2) + '亿';
        } else if (absAmount >= 10000) { // 1万以上
            formatted = (absAmount / 10000).toFixed(1) + '万';
        } else {
            formatted = absAmount.toLocaleString();
        }
        
        return (amount < 0 ? '-¥' : '¥') + formatted;
    }
    
    /**
     * 显示月度期望数据错误
     */
    showMonthlyExpectationError(message) {
        const listContainer = document.getElementById('monthly-expectation-list');
        listContainer.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle fa-2x text-danger mb-2"></i>
                <p class="text-danger">${message}</p>
                <button class="btn btn-outline-primary btn-sm" onclick="expectationComparisonManager.loadMonthlyExpectations()">
                    <i class="fas fa-redo me-1"></i>重新加载
                </button>
            </div>
        `;
    }
    
    /**
     * 显示月度对比错误
     */
    showMonthlyComparisonError(message) {
        const detailContainer = document.getElementById('monthly-comparison-detail');
        detailContainer.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                <h6 class="text-danger">${message}</h6>
                <p class="text-muted">请重新选择月份或刷新数据</p>
            </div>
        `;
    }

    /**
     * 销毁管理器
     */
    destroy() {
        // 移除事件监听器
        window.removeEventListener('resize', this.handleResize);
        window.removeEventListener('orientationchange', this.handleResize);
        
        // 销毁图表
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.currentData = null;
        
        console.log('期望对比管理器已销毁');
    }
}

// 创建全局实例
if (typeof window !== 'undefined') {
    // 确保在DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            try {
                window.expectationComparisonManager = new ExpectationComparisonManager();
                console.log('期望对比管理器初始化成功');
            } catch (error) {
                console.error('期望对比管理器初始化失败:', error);
            }
        });
    } else {
        try {
            window.expectationComparisonManager = new ExpectationComparisonManager();
            console.log('期望对比管理器初始化成功');
        } catch (error) {
            console.error('期望对比管理器初始化失败:', error);
        }
    }
}

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExpectationComparisonManager;
}