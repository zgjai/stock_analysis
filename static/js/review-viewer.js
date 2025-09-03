/**
 * 复盘查看器组件
 * 负责复盘内容的展示和查看功能
 */
class ReviewViewer {
    constructor() {
        this.currentReview = null;
        this.currentTrade = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // 编辑复盘按钮
        const editBtn = document.getElementById('edit-review-btn');
        if (editBtn) {
            editBtn.addEventListener('click', () => this.editReview());
        }

        // 图片查看器
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('review-image')) {
                this.showImageModal(e.target);
            }
        });
    }

    async loadReview(tradeId) {
        try {
            const response = await apiClient.request('GET', `/trade-reviews/${tradeId}`);
            
            if (response.success && response.data) {
                this.currentReview = response.data;
                this.displayReview(response.data);
                return response.data;
            } else {
                throw new Error('该交易暂无复盘记录');
            }
        } catch (error) {
            console.error('Load review error:', error);
            this.showMessage('获取复盘内容失败: ' + error.message, 'error');
            return null;
        }
    }

    displayReview(reviewData) {
        const content = document.getElementById('view-review-content');
        
        content.innerHTML = `
            ${this.renderReviewHeader(reviewData)}
            ${this.renderReviewContent(reviewData)}
            ${this.renderReviewScores(reviewData)}
            ${this.renderReviewLearnings(reviewData)}
            ${this.renderReviewImages(reviewData.images || [])}
            ${this.renderReviewMeta(reviewData)}
        `;

        // 设置编辑按钮数据
        const editBtn = document.getElementById('edit-review-btn');
        if (editBtn) {
            editBtn.setAttribute('data-review-id', reviewData.id);
        }
    }

    renderReviewHeader(reviewData) {
        const typeText = this.getReviewTypeText(reviewData.review_type);
        const typeBadgeClass = this.getReviewTypeBadgeClass(reviewData.review_type);
        
        return `
            <div class="row mb-4">
                <div class="col-md-8">
                    <h4 class="mb-2">${reviewData.review_title || '交易复盘'}</h4>
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge ${typeBadgeClass}">${typeText}</span>
                        ${reviewData.overall_score ? 
                            `<span class="badge bg-secondary">总评: ${reviewData.overall_score}/5</span>` : 
                            ''
                        }
                    </div>
                </div>
                <div class="col-md-4 text-end">
                    <small class="text-muted">
                        <i class="bi bi-calendar"></i> 
                        创建时间: ${this.formatDateTime(reviewData.created_at)}
                    </small>
                    ${reviewData.updated_at !== reviewData.created_at ? 
                        `<br><small class="text-muted">
                            <i class="bi bi-pencil"></i> 
                            更新时间: ${this.formatDateTime(reviewData.updated_at)}
                        </small>` : 
                        ''
                    }
                </div>
            </div>
        `;
    }

    renderReviewContent(reviewData) {
        if (!reviewData.review_content) {
            return '';
        }

        return `
            <div class="row mb-4">
                <div class="col-md-12">
                    <h6 class="border-bottom pb-2 mb-3">
                        <i class="bi bi-journal-text"></i> 复盘内容
                    </h6>
                    <div class="review-content bg-light rounded p-3">
                        ${this.formatContent(reviewData.review_content)}
                    </div>
                </div>
            </div>
        `;
    }

    renderReviewScores(reviewData) {
        const scores = [
            { key: 'strategy_score', label: '策略执行', icon: 'bi-bullseye' },
            { key: 'timing_score', label: '时机把握', icon: 'bi-clock' },
            { key: 'risk_control_score', label: '风险控制', icon: 'bi-shield-check' },
            { key: 'overall_score', label: '总体评分', icon: 'bi-star-fill' }
        ];

        const hasScores = scores.some(score => reviewData[score.key]);
        
        if (!hasScores) {
            return '';
        }

        return `
            <div class="row mb-4">
                <div class="col-md-12">
                    <h6 class="border-bottom pb-2 mb-3">
                        <i class="bi bi-graph-up"></i> 评分详情
                    </h6>
                    <div class="row">
                        ${scores.map(score => {
                            const value = reviewData[score.key];
                            if (!value) return '';
                            
                            return `
                                <div class="col-md-3 col-sm-6 mb-3">
                                    <div class="text-center p-3 bg-light rounded">
                                        <i class="${score.icon} fs-4 ${this.getScoreColor(value)} mb-2"></i>
                                        <div class="fs-2 fw-bold ${this.getScoreColor(value)}">${value}</div>
                                        <div class="text-muted small">/ 5</div>
                                        <div class="fw-medium">${score.label}</div>
                                        <div class="small text-muted">${this.getScoreText(value)}</div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderReviewLearnings(reviewData) {
        const hasLearnings = reviewData.key_learnings || reviewData.improvement_areas;
        
        if (!hasLearnings) {
            return '';
        }

        return `
            <div class="row mb-4">
                <div class="col-md-12">
                    <h6 class="border-bottom pb-2 mb-3">
                        <i class="bi bi-lightbulb"></i> 学习总结
                    </h6>
                </div>
                ${reviewData.key_learnings ? `
                    <div class="col-md-6 mb-3">
                        <div class="card h-100">
                            <div class="card-header bg-success text-white">
                                <i class="bi bi-check-circle"></i> 关键学习点
                            </div>
                            <div class="card-body">
                                ${this.formatContent(reviewData.key_learnings)}
                            </div>
                        </div>
                    </div>
                ` : ''}
                ${reviewData.improvement_areas ? `
                    <div class="col-md-6 mb-3">
                        <div class="card h-100">
                            <div class="card-header bg-warning text-dark">
                                <i class="bi bi-arrow-up-circle"></i> 改进领域
                            </div>
                            <div class="card-body">
                                ${this.formatContent(reviewData.improvement_areas)}
                            </div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderReviewImages(images) {
        if (!images || images.length === 0) {
            return '';
        }

        return `
            <div class="row mb-4">
                <div class="col-md-12">
                    <h6 class="border-bottom pb-2 mb-3">
                        <i class="bi bi-images"></i> 复盘图片 (${images.length})
                    </h6>
                    <div class="row">
                        ${images.map((image, index) => `
                            <div class="col-md-3 col-sm-4 col-6 mb-3">
                                <div class="card">
                                    <img src="${image.file_path}" 
                                         class="card-img-top review-image" 
                                         style="height: 150px; object-fit: cover; cursor: pointer;" 
                                         alt="${image.description || '复盘图片'}"
                                         data-bs-toggle="modal" 
                                         data-bs-target="#imageModal"
                                         data-image-src="${image.file_path}"
                                         data-image-title="${image.description || '复盘图片'}"
                                         data-image-index="${index}">
                                    ${image.description ? `
                                        <div class="card-body p-2">
                                            <small class="text-muted">${image.description}</small>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderReviewMeta(reviewData) {
        return `
            <div class="row">
                <div class="col-md-12">
                    <div class="border-top pt-3">
                        <div class="row text-muted small">
                            <div class="col-md-6">
                                <i class="bi bi-person"></i> 复盘ID: ${reviewData.id}
                            </div>
                            <div class="col-md-6 text-end">
                                <i class="bi bi-clock"></i> 
                                创建于 ${this.formatDateTime(reviewData.created_at)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    formatContent(content) {
        if (!content) return '';
        
        // 处理换行
        let formatted = content.replace(/\n/g, '<br>');
        
        // 处理简单的Markdown格式
        formatted = formatted
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // 粗体
            .replace(/\*(.*?)\*/g, '<em>$1</em>') // 斜体
            .replace(/^- (.+)$/gm, '<li>$1</li>') // 列表项
            .replace(/^(\d+)\. (.+)$/gm, '<li>$1. $2</li>') // 编号列表
            .replace(/^> (.+)$/gm, '<blockquote class="blockquote-sm">$1</blockquote>'); // 引用
        
        // 包装列表项
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul class="mb-0">$1</ul>');
        
        return formatted;
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

    getReviewTypeBadgeClass(type) {
        const classes = {
            'general': 'bg-secondary',
            'success': 'bg-success',
            'failure': 'bg-danger',
            'lesson': 'bg-info'
        };
        return classes[type] || 'bg-secondary';
    }

    getScoreColor(score) {
        if (score >= 4) return 'text-success';
        if (score <= 2) return 'text-danger';
        return 'text-warning';
    }

    getScoreText(score) {
        const texts = {
            1: '很差',
            2: '较差',
            3: '一般',
            4: '良好',
            5: '优秀'
        };
        return texts[score] || '';
    }

    showImageModal(imgElement) {
        // 创建图片查看模态框
        let imageModal = document.getElementById('imageModal');
        
        if (!imageModal) {
            imageModal = this.createImageModal();
            document.body.appendChild(imageModal);
        }

        const modalImg = imageModal.querySelector('.modal-image');
        const modalTitle = imageModal.querySelector('.modal-title');
        
        modalImg.src = imgElement.dataset.imageSrc || imgElement.src;
        modalTitle.textContent = imgElement.dataset.imageTitle || '复盘图片';
        
        const modal = new bootstrap.Modal(imageModal);
        modal.show();
    }

    createImageModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'imageModal';
        modal.tabIndex = -1;
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">复盘图片</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="" class="modal-image img-fluid" alt="复盘图片">
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }

    async editReview() {
        const reviewId = document.getElementById('edit-review-btn').getAttribute('data-review-id');
        
        if (!reviewId || !this.currentReview) {
            this.showMessage('无法编辑复盘', 'error');
            return;
        }

        try {
            // 关闭查看模态框
            const viewModal = bootstrap.Modal.getInstance(document.getElementById('viewReviewModal'));
            if (viewModal) {
                viewModal.hide();
            }

            // 触发编辑事件
            document.dispatchEvent(new CustomEvent('editReview', {
                detail: { 
                    reviewId: reviewId,
                    reviewData: this.currentReview 
                }
            }));
        } catch (error) {
            console.error('Edit review error:', error);
            this.showMessage('编辑复盘失败', 'error');
        }
    }

    formatDateTime(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showMessage(message, type = 'info') {
        // 使用全局消息系统
        if (window.showMessage) {
            window.showMessage(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// 导出类
window.ReviewViewer = ReviewViewer;