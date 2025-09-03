/**
 * 复盘编辑器组件
 * 负责复盘内容的编辑功能
 */
class ReviewEditor {
    constructor() {
        this.currentReviewId = null;
        this.currentTradeId = null;
        this.uploadedImages = [];
        this.isEditing = false;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeRichTextEditor();
    }

    setupEventListeners() {
        // 保存复盘按钮
        const saveBtn = document.getElementById('save-review-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveReview());
        }

        // 图片上传
        const imageInput = document.getElementById('review-images');
        if (imageInput) {
            imageInput.addEventListener('change', (e) => this.handleImageUpload(e));
        }

        // 表单验证
        const form = document.getElementById('review-form');
        if (form) {
            form.addEventListener('input', this.debounce(() => this.validateForm(), 300));
            form.addEventListener('change', () => this.validateForm());
        }

        // 实时字符计数
        this.setupCharacterCounters();

        // 评分联动
        this.setupScoreInteraction();
    }

    initializeRichTextEditor() {
        // 为复盘内容添加富文本编辑功能
        const contentTextarea = document.getElementById('review-content');
        if (contentTextarea) {
            this.enhanceTextarea(contentTextarea);
        }

        const learningsTextarea = document.getElementById('key-learnings');
        if (learningsTextarea) {
            this.enhanceTextarea(learningsTextarea);
        }

        const improvementTextarea = document.getElementById('improvement-areas');
        if (improvementTextarea) {
            this.enhanceTextarea(improvementTextarea);
        }
    }

    enhanceTextarea(textarea) {
        // 添加自动调整高度
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });

        // 添加快捷键支持
        textarea.addEventListener('keydown', (e) => {
            // Ctrl+B 加粗
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                this.insertTextAtCursor(textarea, '**', '**');
            }
            // Ctrl+I 斜体
            if (e.ctrlKey && e.key === 'i') {
                e.preventDefault();
                this.insertTextAtCursor(textarea, '*', '*');
            }
            // Tab 缩进
            if (e.key === 'Tab') {
                e.preventDefault();
                this.insertTextAtCursor(textarea, '    ');
            }
        });

        // 添加工具栏
        this.addTextareaToolbar(textarea);
    }

    addTextareaToolbar(textarea) {
        const toolbar = document.createElement('div');
        toolbar.className = 'textarea-toolbar mb-2';
        toolbar.innerHTML = `
            <div class="btn-group btn-group-sm" role="group">
                <button type="button" class="btn btn-outline-secondary" title="加粗 (Ctrl+B)" data-action="bold">
                    <i class="bi bi-type-bold"></i>
                </button>
                <button type="button" class="btn btn-outline-secondary" title="斜体 (Ctrl+I)" data-action="italic">
                    <i class="bi bi-type-italic"></i>
                </button>
                <button type="button" class="btn btn-outline-secondary" title="列表" data-action="list">
                    <i class="bi bi-list-ul"></i>
                </button>
                <button type="button" class="btn btn-outline-secondary" title="编号列表" data-action="numbered-list">
                    <i class="bi bi-list-ol"></i>
                </button>
                <button type="button" class="btn btn-outline-secondary" title="引用" data-action="quote">
                    <i class="bi bi-quote"></i>
                </button>
            </div>
        `;

        textarea.parentNode.insertBefore(toolbar, textarea);

        // 工具栏事件
        toolbar.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (!button) return;

            const action = button.dataset.action;
            this.applyTextFormat(textarea, action);
        });
    }

    insertTextAtCursor(textarea, startText, endText = '') {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        
        const newText = startText + selectedText + endText;
        textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
        
        // 设置光标位置
        const newCursorPos = start + startText.length + selectedText.length;
        textarea.setSelectionRange(newCursorPos, newCursorPos);
        textarea.focus();
    }

    applyTextFormat(textarea, action) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);

        let newText = '';
        let cursorOffset = 0;

        switch (action) {
            case 'bold':
                newText = `**${selectedText}**`;
                cursorOffset = selectedText ? 0 : 2;
                break;
            case 'italic':
                newText = `*${selectedText}*`;
                cursorOffset = selectedText ? 0 : 1;
                break;
            case 'list':
                newText = selectedText.split('\n').map(line => 
                    line.trim() ? `- ${line}` : line
                ).join('\n');
                break;
            case 'numbered-list':
                newText = selectedText.split('\n').map((line, index) => 
                    line.trim() ? `${index + 1}. ${line}` : line
                ).join('\n');
                break;
            case 'quote':
                newText = selectedText.split('\n').map(line => 
                    line.trim() ? `> ${line}` : line
                ).join('\n');
                break;
        }

        textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
        
        const newCursorPos = start + newText.length - cursorOffset;
        textarea.setSelectionRange(newCursorPos, newCursorPos);
        textarea.focus();
    }

    setupScoreInteraction() {
        const scoreSelects = ['strategy-score', 'timing-score', 'risk-control-score', 'overall-score'];
        
        scoreSelects.forEach(id => {
            const select = document.getElementById(id);
            if (select) {
                select.addEventListener('change', () => {
                    this.updateScoreDisplay();
                    this.suggestOverallScore();
                });
            }
        });
    }

    updateScoreDisplay() {
        const scoreSelects = ['strategy-score', 'timing-score', 'risk-control-score', 'overall-score'];
        
        scoreSelects.forEach(id => {
            const select = document.getElementById(id);
            const value = parseInt(select.value);
            
            // 更新选择框样式
            select.className = 'form-select';
            if (value) {
                if (value >= 4) {
                    select.classList.add('border-success');
                } else if (value <= 2) {
                    select.classList.add('border-danger');
                } else {
                    select.classList.add('border-warning');
                }
            }
        });
    }

    suggestOverallScore() {
        const strategyScore = parseInt(document.getElementById('strategy-score').value) || 0;
        const timingScore = parseInt(document.getElementById('timing-score').value) || 0;
        const riskScore = parseInt(document.getElementById('risk-control-score').value) || 0;
        
        if (strategyScore && timingScore && riskScore) {
            const avgScore = Math.round((strategyScore + timingScore + riskScore) / 3);
            const overallSelect = document.getElementById('overall-score');
            
            if (!overallSelect.value) {
                overallSelect.value = avgScore;
                this.updateScoreDisplay();
            }
        }
    }

    handleImageUpload(event) {
        const files = Array.from(event.target.files);
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        
        const validFiles = [];
        const errors = [];

        files.forEach(file => {
            if (!allowedTypes.includes(file.type)) {
                errors.push(`${file.name}: 不支持的文件格式`);
                return;
            }
            
            if (file.size > maxSize) {
                errors.push(`${file.name}: 文件大小超过5MB限制`);
                return;
            }
            
            validFiles.push(file);
        });

        if (errors.length > 0) {
            this.showMessage(errors.join('\n'), 'warning');
        }

        if (validFiles.length > 0) {
            this.previewImages(validFiles);
        }
    }

    previewImages(files) {
        const preview = document.getElementById('image-preview');
        
        files.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const imageContainer = this.createImagePreview(e.target.result, file.name, index);
                preview.appendChild(imageContainer);
            };
            reader.readAsDataURL(file);
        });
    }

    createImagePreview(src, filename, index) {
        const container = document.createElement('div');
        container.className = 'image-preview-item position-relative d-inline-block me-2 mb-2';
        container.dataset.index = index;
        
        container.innerHTML = `
            <div class="card" style="width: 150px;">
                <img src="${src}" class="card-img-top" style="height: 100px; object-fit: cover;" alt="${filename}">
                <div class="card-body p-2">
                    <input type="text" class="form-control form-control-sm" placeholder="图片描述..." 
                           name="image_descriptions[]" maxlength="100">
                    <small class="text-muted">${filename}</small>
                </div>
                <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0" 
                        onclick="this.closest('.image-preview-item').remove()" 
                        style="transform: translate(50%, -50%);">
                    <i class="bi bi-x"></i>
                </button>
            </div>
        `;
        
        return container;
    }

    validateForm() {
        const form = document.getElementById('review-form');
        const saveBtn = document.getElementById('save-review-btn');
        
        // 收集所有验证错误
        const errors = [];
        
        // 基本验证
        const title = document.getElementById('review-title').value.trim();
        const content = document.getElementById('review-content').value.trim();
        
        if (!title && !content) {
            errors.push('请至少填写复盘标题或内容');
        }
        
        // 标题长度验证
        if (title && title.length > 200) {
            errors.push('复盘标题不能超过200个字符');
        }
        
        // 内容长度验证
        if (content && content.length > 5000) {
            errors.push('复盘内容不能超过5000个字符');
        }
        
        // 评分验证
        const scores = ['strategy-score', 'timing-score', 'risk-control-score', 'overall-score'];
        scores.forEach(scoreId => {
            const scoreValue = document.getElementById(scoreId).value;
            if (scoreValue && (scoreValue < 1 || scoreValue > 5)) {
                errors.push('评分必须在1-5之间');
            }
        });
        
        // 学习点验证
        const learnings = document.getElementById('key-learnings').value.trim();
        if (learnings && learnings.length > 2000) {
            errors.push('关键学习点不能超过2000个字符');
        }
        
        const improvements = document.getElementById('improvement-areas').value.trim();
        if (improvements && improvements.length > 2000) {
            errors.push('改进领域不能超过2000个字符');
        }
        
        // 图片验证
        if (this.imageUploader) {
            const fileCount = this.imageUploader.getFileCount();
            if (fileCount > 10) {
                errors.push('最多只能上传10张图片');
            }
        }
        
        const isValid = errors.length === 0;
        
        // 更新保存按钮状态
        if (saveBtn) {
            saveBtn.disabled = !isValid;
        }
        
        // 显示验证错误
        this.displayValidationErrors(errors);
        
        return isValid;
    }

    displayValidationErrors(errors) {
        // 清除之前的错误显示
        this.clearValidationErrors();
        
        if (errors.length > 0) {
            const errorContainer = this.getOrCreateErrorContainer();
            errorContainer.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show">
                    <strong>表单验证失败：</strong>
                    <ul class="mb-0 mt-2">
                        ${errors.map(error => `<li>${error}</li>`).join('')}
                    </ul>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    }

    clearValidationErrors() {
        const errorContainer = document.getElementById('validation-errors');
        if (errorContainer) {
            errorContainer.innerHTML = '';
        }
    }

    getOrCreateErrorContainer() {
        let container = document.getElementById('validation-errors');
        if (!container) {
            container = document.createElement('div');
            container.id = 'validation-errors';
            
            // 插入到表单顶部
            const form = document.getElementById('review-form');
            if (form) {
                form.insertBefore(container, form.firstChild);
            }
        }
        return container;
    }

    async saveReview() {
        if (!this.validateForm()) {
            this.showMessage('请至少填写复盘标题或内容', 'warning');
            return;
        }

        const saveBtn = document.getElementById('save-review-btn');
        const spinner = saveBtn.querySelector('.spinner-border');
        
        try {
            saveBtn.disabled = true;
            spinner.style.display = 'inline-block';

            // 收集表单数据
            const formData = this.collectFormData();
            
            let response;
            if (this.isEditing && this.currentReviewId) {
                response = await this.updateReview(formData);
            } else {
                response = await this.createReview(formData);
            }

            if (response.success) {
                this.showMessage('复盘保存成功', 'success');
                
                // 如果有图片，上传图片
                if (this.imageUploader && this.imageUploader.getFileCount() > 0) {
                    await this.imageUploader.uploadFiles(response.data.id);
                } else {
                    // 兼容旧的图片上传方式
                    const imageFiles = document.getElementById('review-images').files;
                    if (imageFiles.length > 0) {
                        await this.uploadImages(response.data.id, imageFiles);
                    }
                }
                
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('reviewModal'));
                if (modal) {
                    modal.hide();
                }
                
                // 触发刷新事件
                document.dispatchEvent(new CustomEvent('reviewSaved', {
                    detail: { reviewId: response.data.id, tradeId: this.currentTradeId }
                }));
            } else {
                throw new Error(response.message || '保存失败');
            }
        } catch (error) {
            console.error('Save review error:', error);
            this.showMessage('保存复盘失败: ' + error.message, 'error');
        } finally {
            saveBtn.disabled = false;
            spinner.style.display = 'none';
        }
    }

    collectFormData() {
        const form = document.getElementById('review-form');
        const formData = new FormData(form);
        
        // 转换为JSON对象
        const data = {};
        for (let [key, value] of formData.entries()) {
            if (key.endsWith('[]')) {
                // 处理数组字段
                const arrayKey = key.slice(0, -2);
                if (!data[arrayKey]) data[arrayKey] = [];
                data[arrayKey].push(value);
            } else {
                data[key] = value;
            }
        }
        
        // 处理评分字段
        ['strategy_score', 'timing_score', 'risk_control_score', 'overall_score'].forEach(field => {
            if (data[field]) {
                data[field] = parseInt(data[field]);
            }
        });
        
        return data;
    }

    async createReview(data) {
        return await apiClient.request('POST', '/trade-reviews', data);
    }

    async updateReview(data) {
        return await apiClient.request('PUT', `/trade-reviews/${this.currentReviewId}`, data);
    }

    async uploadImages(reviewId, files) {
        const formData = new FormData();
        
        // 添加图片文件
        Array.from(files).forEach(file => {
            formData.append('images', file);
        });
        
        // 添加图片描述
        const descriptions = document.querySelectorAll('input[name="image_descriptions[]"]');
        descriptions.forEach(input => {
            formData.append('descriptions', input.value || '');
        });
        
        return await apiClient.request('POST', `/trade-reviews/${reviewId}/images`, formData);
    }

    loadReview(tradeData, reviewData = null) {
        this.currentTradeId = tradeData.id;
        this.isEditing = !!reviewData;
        this.currentReviewId = reviewData ? reviewData.id : null;
        
        // 填充交易信息
        this.displayTradeInfo(tradeData);
        
        // 填充复盘数据
        if (reviewData) {
            this.populateForm(reviewData);
        } else {
            this.resetForm();
        }
        
        // 初始化图片上传器
        this.initializeImageUploader();
        
        // 更新模态框标题
        const modalTitle = document.getElementById('review-modal-title');
        modalTitle.textContent = this.isEditing ? '编辑复盘' : '添加复盘';
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

    displayTradeInfo(tradeData) {
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
    }

    populateForm(reviewData) {
        document.getElementById('review-title').value = reviewData.review_title || '';
        document.getElementById('review-type').value = reviewData.review_type || 'general';
        document.getElementById('review-content').value = reviewData.review_content || '';
        document.getElementById('strategy-score').value = reviewData.strategy_score || '';
        document.getElementById('timing-score').value = reviewData.timing_score || '';
        document.getElementById('risk-control-score').value = reviewData.risk_control_score || '';
        document.getElementById('overall-score').value = reviewData.overall_score || '';
        document.getElementById('key-learnings').value = reviewData.key_learnings || '';
        document.getElementById('improvement-areas').value = reviewData.improvement_areas || '';
        
        this.updateScoreDisplay();
    }

    resetForm() {
        const form = document.getElementById('review-form');
        form.reset();
        
        document.getElementById('image-preview').innerHTML = '';
        this.currentReviewId = null;
        this.isEditing = false;
        
        // 清空图片上传器
        if (this.imageUploader) {
            this.imageUploader.clear();
        }
        
        // 重置评分样式
        const scoreSelects = ['strategy-score', 'timing-score', 'risk-control-score', 'overall-score'];
        scoreSelects.forEach(id => {
            const select = document.getElementById(id);
            select.className = 'form-select';
        });
    }

    formatNumber(num) {
        return new Intl.NumberFormat('zh-CN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(num);
    }

    // 字符计数器设置
    setupCharacterCounters() {
        const fields = [
            { id: 'review-title', max: 200 },
            { id: 'review-content', max: 5000 },
            { id: 'key-learnings', max: 2000 },
            { id: 'improvement-areas', max: 2000 }
        ];

        fields.forEach(field => {
            const element = document.getElementById(field.id);
            if (element) {
                this.addCharacterCounter(element, field.max);
            }
        });
    }

    addCharacterCounter(element, maxLength) {
        // 创建计数器元素
        const counter = document.createElement('small');
        counter.className = 'text-muted character-counter';
        counter.style.float = 'right';
        
        // 插入计数器
        element.parentNode.appendChild(counter);
        
        // 更新计数器
        const updateCounter = () => {
            const length = element.value.length;
            counter.textContent = `${length}/${maxLength}`;
            
            // 根据长度改变颜色
            if (length > maxLength * 0.9) {
                counter.className = 'text-danger character-counter';
            } else if (length > maxLength * 0.7) {
                counter.className = 'text-warning character-counter';
            } else {
                counter.className = 'text-muted character-counter';
            }
        };
        
        // 初始更新
        updateCounter();
        
        // 绑定事件
        element.addEventListener('input', updateCounter);
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

    // 增强的错误处理
    handleSaveError(error) {
        console.error('Save review error:', error);
        
        let message = '保存复盘失败';
        
        if (error.response) {
            const status = error.response.status;
            const data = error.response.data;
            
            switch (status) {
                case 400:
                    message = data.message || '请求数据格式错误';
                    break;
                case 413:
                    message = '上传的文件过大';
                    break;
                case 422:
                    message = '数据验证失败';
                    if (data.errors) {
                        message += '：' + Object.values(data.errors).flat().join('，');
                    }
                    break;
                case 500:
                    message = '服务器内部错误，请稍后重试';
                    break;
                default:
                    message = data.message || `保存失败 (${status})`;
            }
        } else if (error.request) {
            message = '网络连接失败，请检查网络连接';
        } else {
            message = error.message || '未知错误';
        }
        
        this.showMessage(message, 'error');
        return message;
    }

    // 自动保存功能
    enableAutoSave() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
        }
        
        this.autoSaveTimer = setInterval(() => {
            if (this.hasUnsavedChanges()) {
                this.autoSave();
            }
        }, 30000); // 30秒自动保存
    }

    disableAutoSave() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
    }

    hasUnsavedChanges() {
        // 检查表单是否有未保存的更改
        const form = document.getElementById('review-form');
        if (!form) return false;
        
        const formData = new FormData(form);
        const currentData = Object.fromEntries(formData.entries());
        
        // 与初始数据比较
        return JSON.stringify(currentData) !== JSON.stringify(this.initialFormData || {});
    }

    async autoSave() {
        if (!this.validateForm()) return;
        
        try {
            const formData = this.collectFormData();
            
            if (this.isEditing && this.currentReviewId) {
                await this.updateReview(formData);
                this.showMessage('已自动保存', 'info');
            }
        } catch (error) {
            console.warn('Auto save failed:', error);
        }
    }

    // 保存初始表单数据用于比较
    saveInitialFormData() {
        const form = document.getElementById('review-form');
        if (form) {
            const formData = new FormData(form);
            this.initialFormData = Object.fromEntries(formData.entries());
        }
    }

    // 键盘快捷键支持
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // 只在复盘编辑模态框打开时处理
            const modal = document.getElementById('reviewModal');
            if (!modal || !modal.classList.contains('show')) return;
            
            // Ctrl+S 保存
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveReview();
            }
            
            // Ctrl+Enter 保存并关闭
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.saveReview();
            }
            
            // Escape 取消编辑
            if (e.key === 'Escape') {
                if (this.hasUnsavedChanges()) {
                    if (confirm('有未保存的更改，确定要关闭吗？')) {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        modalInstance.hide();
                    }
                } else {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    modalInstance.hide();
                }
            }
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
window.ReviewEditor = ReviewEditor;