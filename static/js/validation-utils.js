/**
 * 验证工具类
 * 提供通用的表单验证功能
 */
class ValidationUtils {
    constructor() {
        this.rules = new Map();
        this.messages = new Map();
        this.setupDefaultRules();
    }

    setupDefaultRules() {
        // 股票代码验证
        this.addRule('stockCode', (value) => {
            if (!value) return true; // 可选字段
            return /^[0-9]{6}$/.test(value);
        }, '股票代码必须是6位数字');

        // 日期验证
        this.addRule('date', (value) => {
            if (!value) return true; // 可选字段
            const date = new Date(value);
            return date instanceof Date && !isNaN(date);
        }, '请输入有效的日期');

        // 必填验证
        this.addRule('required', (value) => {
            return value !== null && value !== undefined && value.toString().trim() !== '';
        }, '此字段为必填项');

        // 长度验证
        this.addRule('maxLength', (value, max) => {
            if (!value) return true;
            return value.toString().length <= max;
        }, '内容长度超出限制');

        this.addRule('minLength', (value, min) => {
            if (!value) return true;
            return value.toString().length >= min;
        }, '内容长度不足');

        // 数字验证
        this.addRule('number', (value) => {
            if (!value) return true;
            return !isNaN(parseFloat(value)) && isFinite(value);
        }, '请输入有效的数字');

        this.addRule('integer', (value) => {
            if (!value) return true;
            return Number.isInteger(parseFloat(value));
        }, '请输入整数');

        // 范围验证
        this.addRule('range', (value, min, max) => {
            if (!value) return true;
            const num = parseFloat(value);
            return num >= min && num <= max;
        }, '数值超出允许范围');

        // 评分验证
        this.addRule('score', (value) => {
            if (!value) return true;
            const score = parseInt(value);
            return score >= 1 && score <= 5;
        }, '评分必须在1-5之间');

        // 文件大小验证
        this.addRule('fileSize', (file, maxSize) => {
            if (!file) return true;
            return file.size <= maxSize;
        }, '文件大小超出限制');

        // 文件类型验证
        this.addRule('fileType', (file, allowedTypes) => {
            if (!file) return true;
            return allowedTypes.includes(file.type);
        }, '文件类型不支持');
    }

    addRule(name, validator, message) {
        this.rules.set(name, validator);
        this.messages.set(name, message);
    }

    validate(value, ruleName, ...params) {
        const rule = this.rules.get(ruleName);
        if (!rule) {
            console.warn(`Validation rule '${ruleName}' not found`);
            return { valid: true };
        }

        const valid = rule(value, ...params);
        const message = valid ? null : this.messages.get(ruleName);

        return { valid, message };
    }

    validateField(element, rules) {
        const errors = [];
        const value = this.getFieldValue(element);

        for (const rule of rules) {
            const { valid, message } = this.validate(value, rule.name, ...rule.params || []);
            if (!valid) {
                errors.push(message || `验证失败: ${rule.name}`);
            }
        }

        this.updateFieldUI(element, errors);
        return errors;
    }

    validateForm(formElement, validationConfig) {
        const allErrors = {};
        let hasErrors = false;

        for (const [fieldName, rules] of Object.entries(validationConfig)) {
            const field = formElement.querySelector(`[name="${fieldName}"]`) || 
                          formElement.querySelector(`#${fieldName}`);
            
            if (field) {
                const errors = this.validateField(field, rules);
                if (errors.length > 0) {
                    allErrors[fieldName] = errors;
                    hasErrors = true;
                }
            }
        }

        return { valid: !hasErrors, errors: allErrors };
    }

    getFieldValue(element) {
        if (element.type === 'checkbox') {
            return element.checked;
        } else if (element.type === 'radio') {
            const form = element.closest('form');
            const checked = form.querySelector(`input[name="${element.name}"]:checked`);
            return checked ? checked.value : null;
        } else if (element.type === 'file') {
            return element.files[0] || null;
        } else {
            return element.value;
        }
    }

    updateFieldUI(element, errors) {
        // 清除之前的状态
        element.classList.remove('is-valid', 'is-invalid');
        this.clearFieldFeedback(element);

        if (errors.length > 0) {
            element.classList.add('is-invalid');
            this.showFieldFeedback(element, errors[0], 'invalid');
        } else if (element.value.trim() !== '') {
            element.classList.add('is-valid');
        }
    }

    showFieldFeedback(element, message, type = 'invalid') {
        const feedbackClass = type === 'invalid' ? 'invalid-feedback' : 'valid-feedback';
        
        let feedback = element.parentNode.querySelector(`.${feedbackClass}`);
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = feedbackClass;
            element.parentNode.appendChild(feedback);
        }
        
        feedback.textContent = message;
    }

    clearFieldFeedback(element) {
        const feedbacks = element.parentNode.querySelectorAll('.invalid-feedback, .valid-feedback');
        feedbacks.forEach(feedback => feedback.remove());
    }

    // 实时验证设置
    setupRealTimeValidation(formElement, validationConfig, options = {}) {
        const { 
            debounceTime = 300,
            validateOnInput = true,
            validateOnBlur = true,
            validateOnChange = true
        } = options;

        for (const [fieldName, rules] of Object.entries(validationConfig)) {
            const field = formElement.querySelector(`[name="${fieldName}"]`) || 
                          formElement.querySelector(`#${fieldName}`);
            
            if (field) {
                if (validateOnInput) {
                    field.addEventListener('input', this.debounce(() => {
                        this.validateField(field, rules);
                    }, debounceTime));
                }

                if (validateOnBlur) {
                    field.addEventListener('blur', () => {
                        this.validateField(field, rules);
                    });
                }

                if (validateOnChange) {
                    field.addEventListener('change', () => {
                        this.validateField(field, rules);
                    });
                }
            }
        }
    }

    // 自定义验证规则
    createCustomRule(name, validator, message) {
        this.addRule(name, validator, message);
    }

    // 条件验证
    validateConditional(element, condition, rules) {
        if (condition()) {
            return this.validateField(element, rules);
        }
        return [];
    }

    // 跨字段验证
    validateCrossField(form, fieldName1, fieldName2, validator, message) {
        const field1 = form.querySelector(`[name="${fieldName1}"]`);
        const field2 = form.querySelector(`[name="${fieldName2}"]`);
        
        if (field1 && field2) {
            const value1 = this.getFieldValue(field1);
            const value2 = this.getFieldValue(field2);
            
            const valid = validator(value1, value2);
            
            if (!valid) {
                this.updateFieldUI(field2, [message]);
                return false;
            } else {
                this.updateFieldUI(field2, []);
                return true;
            }
        }
        
        return true;
    }

    // 异步验证
    async validateAsync(value, asyncValidator) {
        try {
            const result = await asyncValidator(value);
            return { valid: result.valid, message: result.message };
        } catch (error) {
            console.error('Async validation error:', error);
            return { valid: false, message: '验证过程中发生错误' };
        }
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

    // 预定义验证配置
    static getReviewFormValidation() {
        return {
            'review-title': [
                { name: 'maxLength', params: [200] }
            ],
            'review-content': [
                { name: 'maxLength', params: [5000] }
            ],
            'strategy-score': [
                { name: 'score' }
            ],
            'timing-score': [
                { name: 'score' }
            ],
            'risk-control-score': [
                { name: 'score' }
            ],
            'overall-score': [
                { name: 'score' }
            ],
            'key-learnings': [
                { name: 'maxLength', params: [2000] }
            ],
            'improvement-areas': [
                { name: 'maxLength', params: [2000] }
            ]
        };
    }

    static getFilterValidation() {
        return {
            'stock-code-filter': [
                { name: 'stockCode' }
            ],
            'date-from': [
                { name: 'date' }
            ],
            'date-to': [
                { name: 'date' }
            ]
        };
    }
}

// 创建全局实例
window.validationUtils = new ValidationUtils();

// 导出类
window.ValidationUtils = ValidationUtils;