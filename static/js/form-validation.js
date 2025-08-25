// 表单验证和用户体验增强模块
class FormValidator {
    constructor(form, options = {}) {
        this.form = typeof form === 'string' ? document.querySelector(form) : form;
        this.options = {
            realTimeValidation: true,
            showSuccessState: true,
            scrollToError: true,
            highlightErrors: true,
            ...options
        };
        
        this.rules = {};
        this.customValidators = {};
        this.isSubmitting = false;
        
        this.init();
    }
    
    init() {
        if (!this.form) {
            console.error('Form not found');
            return;
        }
        
        this.setupEventListeners();
        this.setupBuiltInValidation();
    }
    
    setupEventListeners() {
        // 表单提交事件
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
        
        // 实时验证事件
        if (this.options.realTimeValidation) {
            this.form.addEventListener('input', (e) => {
                if (e.target.matches('input, select, textarea')) {
                    this.validateField(e.target);
                }
            });
            
            this.form.addEventListener('blur', (e) => {
                if (e.target.matches('input, select, textarea')) {
                    this.validateField(e.target);
                }
            }, true);
        }
        
        // 字符计数器
        this.form.querySelectorAll('[maxlength]').forEach(field => {
            this.setupCharCounter(field);
        });
    }
    
    setupBuiltInValidation() {
        // 设置HTML5验证属性对应的规则
        this.form.querySelectorAll('[required]').forEach(field => {
            // 特殊处理：holding_stock字段只在卖出模式下才需要验证
            if (field.name === 'holding_stock') {
                this.addRule(field.name, {
                    validator: (value) => {
                        const tradeType = document.getElementById('trade-type')?.value;
                        if (tradeType === 'buy') {
                            return true; // 买入模式下不需要验证持仓股票
                        }
                        return Validators.required(value);
                    },
                    message: '请选择要卖出的持仓股票'
                });
            } else {
                this.addRule(field.name, {
                    validator: Validators.required,
                    message: this.getRequiredMessage(field)
                });
            }
        });
        
        this.form.querySelectorAll('[type="email"]').forEach(field => {
            this.addRule(field.name, {
                validator: Validators.email,
                message: '请输入有效的邮箱地址'
            });
        });
        
        this.form.querySelectorAll('[pattern]').forEach(field => {
            const pattern = new RegExp(field.getAttribute('pattern'));
            this.addRule(field.name, {
                validator: (value) => !value || pattern.test(value),
                message: field.getAttribute('title') || '格式不正确'
            });
        });
        
        this.form.querySelectorAll('[min], [max]').forEach(field => {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            
            if (min) {
                this.addRule(field.name, {
                    validator: (value) => !value || parseFloat(value) >= parseFloat(min),
                    message: `值不能小于 ${min}`
                });
            }
            
            if (max) {
                this.addRule(field.name, {
                    validator: (value) => !value || parseFloat(value) <= parseFloat(max),
                    message: `值不能大于 ${max}`
                });
            }
        });
        
        this.form.querySelectorAll('[minlength]').forEach(field => {
            const minLength = parseInt(field.getAttribute('minlength'));
            this.addRule(field.name, {
                validator: (value) => !value || value.length >= minLength,
                message: `至少需要 ${minLength} 个字符`
            });
        });
        
        this.form.querySelectorAll('[maxlength]').forEach(field => {
            const maxLength = parseInt(field.getAttribute('maxlength'));
            this.addRule(field.name, {
                validator: (value) => !value || value.length <= maxLength,
                message: `不能超过 ${maxLength} 个字符`
            });
        });
    }
    
    getRequiredMessage(field) {
        const label = this.form.querySelector(`label[for="${field.id}"]`);
        const fieldName = label ? label.textContent.replace('*', '').trim() : field.name;
        
        switch (field.type) {
            case 'email':
                return '请输入邮箱地址';
            case 'password':
                return '请输入密码';
            case 'tel':
                return '请输入电话号码';
            case 'number':
                return `请输入${fieldName}`;
            case 'date':
            case 'datetime-local':
                return '请选择日期';
            case 'file':
                return '请选择文件';
            default:
                if (field.tagName === 'SELECT') {
                    return `请选择${fieldName}`;
                }
                return `请输入${fieldName}`;
        }
    }
    
    addRule(fieldName, rule) {
        if (!this.rules[fieldName]) {
            this.rules[fieldName] = [];
        }
        this.rules[fieldName].push(rule);
    }
    
    addCustomValidator(name, validator) {
        this.customValidators[name] = validator;
    }
    
    validateField(field) {
        // 如果传入的是字符串，尝试查找对应的字段
        if (typeof field === 'string') {
            const fieldElement = this.form.querySelector(`[name="${field}"]`);
            if (!fieldElement) {
                console.warn(`Field with name "${field}" not found`);
                return true; // 字段不存在时返回true，避免阻塞
            }
            return this.validateField(fieldElement);
        }
        
        if (!field || !field.name) {
            return true;
        }
        
        const fieldName = field.name;
        const value = field.value;
        const rules = this.rules[fieldName] || [];
        
        // 清除之前的验证状态
        this.clearFieldValidation(field);
        
        // 执行验证规则
        for (let rule of rules) {
            const isValid = rule.validator(value);
            if (!isValid) {
                this.showFieldError(field, rule.message);
                return false;
            }
        }
        
        // 显示成功状态
        if (this.options.showSuccessState && value) {
            this.showFieldSuccess(field);
        }
        
        return true;
    }
    
    validateForm() {
        let isValid = true;
        const errors = {};
        
        // 验证所有字段
        Object.keys(this.rules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const fieldValid = this.validateField(field);
                if (!fieldValid) {
                    isValid = false;
                    const errorMessage = field.parentNode.querySelector('.invalid-feedback')?.textContent;
                    if (errorMessage) {
                        errors[fieldName] = errorMessage;
                    }
                }
            }
        });
        
        // 滚动到第一个错误字段
        if (!isValid && this.options.scrollToError) {
            const firstErrorField = this.form.querySelector('.is-invalid');
            if (firstErrorField) {
                UXUtils.scrollToElement(firstErrorField, 100);
                firstErrorField.focus();
            }
        }
        
        return { isValid, errors };
    }
    
    showFieldError(field, message) {
        if (!field || !field.classList) {
            return;
        }
        
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        const container = this.getFieldFeedbackContainer(field);
        if (!container) {
            return;
        }
        
        // 移除现有的反馈
        const existingFeedback = container.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // 添加错误反馈
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        
        container.appendChild(feedback);
        
        // 高亮错误字段
        if (this.options.highlightErrors) {
            UXUtils.highlightElement(field, 1000);
        }
    }
    
    showFieldSuccess(field, message = '') {
        if (!field || !field.classList) {
            return;
        }
        
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
        
        const container = this.getFieldFeedbackContainer(field);
        if (!container) {
            return;
        }
        
        // 移除现有的反馈
        const existingFeedback = container.querySelector('.valid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // 添加成功反馈
        if (message) {
            const feedback = document.createElement('div');
            feedback.className = 'valid-feedback';
            feedback.textContent = message;
            
            container.appendChild(feedback);
        }
    }
    
    clearFieldValidation(field) {
        if (!field || !field.classList) {
            return;
        }
        
        field.classList.remove('is-invalid', 'is-valid');
        
        const container = this.getFieldFeedbackContainer(field);
        if (container && container.querySelectorAll) {
            container.querySelectorAll('.invalid-feedback, .valid-feedback').forEach(feedback => {
                feedback.remove();
            });
        }
    }
    
    getFieldFeedbackContainer(field) {
        // 检查字段是否存在且有父节点
        if (!field || !field.parentNode) {
            return null;
        }
        
        // 如果字段在input-group中，返回input-group的父容器
        if (field.parentNode.classList && field.parentNode.classList.contains('input-group')) {
            return field.parentNode.parentNode;
        }
        return field.parentNode;
    }
    
    setupCharCounter(field) {
        const maxLength = parseInt(field.getAttribute('maxlength'));
        if (!maxLength) return;
        
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        
        const updateCounter = () => {
            const currentLength = field.value.length;
            const remaining = maxLength - currentLength;
            
            counter.textContent = `${currentLength}/${maxLength}`;
            
            if (remaining < 10) {
                counter.className = 'char-counter error';
            } else if (remaining < 20) {
                counter.className = 'char-counter warning';
            } else {
                counter.className = 'char-counter';
            }
        };
        
        field.addEventListener('input', updateCounter);
        this.getFieldFeedbackContainer(field).appendChild(counter);
        updateCounter();
    }
    
    async handleSubmit() {
        if (this.isSubmitting) return;
        
        const validation = this.validateForm();
        if (!validation.isValid) {
            UXUtils.showError('请检查表单中的错误信息');
            return;
        }
        
        this.isSubmitting = true;
        const submitButton = this.form.querySelector('[type="submit"]');
        
        try {
            // 显示提交状态
            if (submitButton) {
                UXUtils.showLoading(submitButton, '提交中...');
            }
            
            // 禁用表单
            FormUtils.disable(this.form, true);
            
            // 获取表单数据
            const formData = FormUtils.serialize(this.form);
            
            // 触发自定义提交事件
            const submitEvent = new CustomEvent('formValidSubmit', {
                detail: { formData, validator: this }
            });
            this.form.dispatchEvent(submitEvent);
            
        } catch (error) {
            console.error('Form submission error:', error);
            UXUtils.showError('提交失败，请重试');
        } finally {
            this.isSubmitting = false;
            
            // 恢复提交按钮状态
            if (submitButton) {
                UXUtils.hideLoading(submitButton);
            }
            
            // 启用表单
            FormUtils.disable(this.form, false);
        }
    }
    
    reset() {
        this.form.reset();
        
        // 清除所有验证状态
        this.form.querySelectorAll('.is-invalid, .is-valid').forEach(field => {
            this.clearFieldValidation(field);
        });
        
        // 重置字符计数器
        this.form.querySelectorAll('.char-counter').forEach(counter => {
            const field = counter.parentNode.querySelector('[maxlength]');
            if (field) {
                const maxLength = parseInt(field.getAttribute('maxlength'));
                counter.textContent = `0/${maxLength}`;
                counter.className = 'char-counter';
            }
        });
    }
    
    setFieldValue(fieldName, value) {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.value = value;
            this.validateField(field);
        }
    }
    
    getFieldValue(fieldName) {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        return field ? field.value : null;
    }
    
    showValidationSummary(errors) {
        // 移除现有的验证摘要
        const existingSummary = this.form.querySelector('.form-validation-summary');
        if (existingSummary) {
            existingSummary.remove();
        }
        
        if (Object.keys(errors).length === 0) return;
        
        const summary = document.createElement('div');
        summary.className = 'form-validation-summary';
        summary.innerHTML = `
            <h6><i class="bi bi-exclamation-triangle me-2"></i>请修正以下错误：</h6>
            <ul>
                ${Object.entries(errors).map(([field, message]) => 
                    `<li>${message}</li>`
                ).join('')}
            </ul>
        `;
        
        this.form.insertBefore(summary, this.form.firstChild);
        UXUtils.scrollToElement(summary, 100);
    }
}

// 表单增强工具类
class FormEnhancer {
    static enhanceAllForms() {
        document.querySelectorAll('form[data-validate]').forEach(form => {
            new FormValidator(form);
        });
    }
    
    static addLoadingStates() {
        // 为所有提交按钮添加加载状态
        document.addEventListener('click', (e) => {
            if (e.target.matches('button[type="submit"], input[type="submit"]')) {
                const form = e.target.closest('form');
                if (form && !form.hasAttribute('novalidate')) {
                    setTimeout(() => {
                        if (form.checkValidity()) {
                            UXUtils.showLoading(e.target, '处理中...');
                        }
                    }, 100);
                }
            }
        });
    }
    
    static addConfirmDialogs() {
        // 为危险操作添加确认对话框
        document.addEventListener('click', async (e) => {
            if (e.target.matches('[data-confirm]')) {
                e.preventDefault();
                
                const message = e.target.getAttribute('data-confirm');
                const confirmed = await UXUtils.showConfirm(message);
                
                if (confirmed) {
                    // 如果是表单提交
                    if (e.target.type === 'submit') {
                        e.target.closest('form').submit();
                    }
                    // 如果是链接
                    else if (e.target.href) {
                        window.location.href = e.target.href;
                    }
                    // 如果有点击处理函数
                    else if (e.target.onclick) {
                        e.target.onclick();
                    }
                }
            }
        });
    }
    
    static addFileUploadEnhancements() {
        document.querySelectorAll('input[type="file"]').forEach(input => {
            FormEnhancer.enhanceFileInput(input);
        });
    }
    
    static enhanceFileInput(input) {
        const wrapper = document.createElement('div');
        wrapper.className = 'file-upload-wrapper';
        
        const dropArea = document.createElement('div');
        dropArea.className = 'file-upload-area';
        dropArea.innerHTML = `
            <div class="file-upload-icon">
                <i class="bi bi-cloud-upload"></i>
            </div>
            <div class="file-upload-text">
                点击选择文件或拖拽文件到此处
            </div>
            <div class="file-upload-hint">
                ${input.accept ? `支持格式：${input.accept}` : ''}
                ${input.multiple ? '可选择多个文件' : ''}
            </div>
        `;
        
        // 插入到原input之前
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(dropArea);
        wrapper.appendChild(input);
        
        // 隐藏原input
        input.style.display = 'none';
        
        // 点击事件
        dropArea.addEventListener('click', () => {
            input.click();
        });
        
        // 拖拽事件
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.add('dragover');
            });
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.remove('dragover');
            });
        });
        
        dropArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            input.files = files;
            
            // 触发change事件
            const changeEvent = new Event('change', { bubbles: true });
            input.dispatchEvent(changeEvent);
        });
        
        // 文件选择变化事件
        input.addEventListener('change', () => {
            const files = Array.from(input.files);
            if (files.length > 0) {
                const fileNames = files.map(file => file.name).join(', ');
                dropArea.querySelector('.file-upload-text').textContent = 
                    `已选择 ${files.length} 个文件：${fileNames}`;
            } else {
                dropArea.querySelector('.file-upload-text').textContent = 
                    '点击选择文件或拖拽文件到此处';
            }
        });
    }
    
    static addSearchEnhancements() {
        document.querySelectorAll('input[type="search"], .search-box input').forEach(input => {
            FormEnhancer.enhanceSearchInput(input);
        });
    }
    
    static enhanceSearchInput(input) {
        const wrapper = input.parentNode;
        if (!wrapper.classList.contains('search-box')) {
            const searchWrapper = document.createElement('div');
            searchWrapper.className = 'search-box';
            input.parentNode.insertBefore(searchWrapper, input);
            searchWrapper.appendChild(input);
        }
        
        // 添加搜索图标
        if (!wrapper.querySelector('.search-icon')) {
            const searchIcon = document.createElement('i');
            searchIcon.className = 'bi bi-search search-icon';
            wrapper.appendChild(searchIcon);
        }
        
        // 添加清除按钮
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.className = 'clear-search';
        clearButton.innerHTML = '<i class="bi bi-x"></i>';
        clearButton.style.display = 'none';
        wrapper.appendChild(clearButton);
        
        // 输入事件
        input.addEventListener('input', () => {
            if (input.value) {
                clearButton.style.display = 'block';
                wrapper.querySelector('.search-icon').style.display = 'none';
            } else {
                clearButton.style.display = 'none';
                wrapper.querySelector('.search-icon').style.display = 'block';
            }
        });
        
        // 清除按钮事件
        clearButton.addEventListener('click', () => {
            input.value = '';
            input.focus();
            clearButton.style.display = 'none';
            wrapper.querySelector('.search-icon').style.display = 'block';
            
            // 触发input事件
            const inputEvent = new Event('input', { bubbles: true });
            input.dispatchEvent(inputEvent);
        });
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    FormEnhancer.enhanceAllForms();
    FormEnhancer.addLoadingStates();
    FormEnhancer.addConfirmDialogs();
    FormEnhancer.addFileUploadEnhancements();
    FormEnhancer.addSearchEnhancements();
});

// 导出到全局
if (typeof window !== 'undefined') {
    window.FormValidator = FormValidator;
    window.FormEnhancer = FormEnhancer;
}