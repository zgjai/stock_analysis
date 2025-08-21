// 工具函数库

// 性能优化工具 - 使用条件声明避免重复
if (typeof window.PerformanceUtils === 'undefined') {
    window.PerformanceUtils = {
    // 防抖函数
    debounce: (func, wait, immediate = false) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    },

    // 节流函数
    throttle: (func, limit) => {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // 批处理器
    batchProcessor: (batchSize = 10, delay = 100) => {
        let batch = [];
        let timer = null;

        return {
            add: (item) => {
                batch.push(item);

                if (batch.length >= batchSize) {
                    this.flush();
                } else if (!timer) {
                    timer = setTimeout(() => this.flush(), delay);
                }
            },

            flush: () => {
                if (batch.length > 0) {
                    const currentBatch = [...batch];
                    batch = [];
                    if (timer) {
                        clearTimeout(timer);
                        timer = null;
                    }
                    return currentBatch;
                }
                return [];
            }
        };
    }
    };
}

// 为了向后兼容，将函数导出到全局作用域 - 使用条件声明避免重复
if (typeof window.debounce === 'undefined') {
    window.debounce = window.PerformanceUtils.debounce;
}
if (typeof window.throttle === 'undefined') {
    window.throttle = window.PerformanceUtils.throttle;
}

// 数据验证工具
const Validators = {
    // 股票代码验证
    stockCode: (code) => {
        const pattern = /^[0-9]{6}$/;
        return pattern.test(code);
    },

    // 价格验证
    price: (price) => {
        const num = parseFloat(price);
        return !isNaN(num) && num > 0;
    },

    // 数量验证
    quantity: (quantity) => {
        const num = parseInt(quantity);
        return !isNaN(num) && num > 0 && num % 100 === 0; // 股票必须是100的倍数
    },

    // 百分比验证
    percentage: (value) => {
        const num = parseFloat(value);
        return !isNaN(num) && num >= -100 && num <= 100;
    },

    // 邮箱验证
    email: (email) => {
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return pattern.test(email);
    },

    // 手机号验证
    phone: (phone) => {
        const pattern = /^1[3-9]\d{9}$/;
        return pattern.test(phone);
    },

    // 必填字段验证
    required: (value) => {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    }
};

// 数据格式化工具
const Formatters = {
    // 格式化货币
    currency: (amount, currency = 'CNY') => {
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    },

    // 格式化百分比
    percentage: (value, decimals = 2) => {
        return new Intl.NumberFormat('zh-CN', {
            style: 'percent',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    },

    // 格式化数字
    number: (value, decimals = 2) => {
        return new Intl.NumberFormat('zh-CN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    },

    // 格式化日期
    date: (date, options = {}) => {
        const defaultOptions = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        };
        return new Intl.DateTimeFormat('zh-CN', { ...defaultOptions, ...options })
            .format(new Date(date));
    },

    // 格式化日期时间
    datetime: (date, options = {}) => {
        const defaultOptions = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        return new Intl.DateTimeFormat('zh-CN', { ...defaultOptions, ...options })
            .format(new Date(date));
    },

    // 格式化文件大小
    fileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // 格式化股票代码显示
    stockCode: (code, name) => {
        return name ? `${name}(${code})` : code;
    }
};

// DOM操作工具
const DOMUtils = {
    // 创建元素
    createElement: (tag, attributes = {}, content = '') => {
        const element = document.createElement(tag);

        Object.keys(attributes).forEach(key => {
            if (key === 'className') {
                element.className = attributes[key];
            } else if (key === 'innerHTML') {
                element.innerHTML = attributes[key];
            } else {
                element.setAttribute(key, attributes[key]);
            }
        });

        if (content) {
            element.textContent = content;
        }

        return element;
    },

    // 查找元素
    find: (selector, parent = document) => {
        return parent.querySelector(selector);
    },

    // 查找所有元素
    findAll: (selector, parent = document) => {
        return Array.from(parent.querySelectorAll(selector));
    },

    // 添加事件监听器
    on: (element, event, handler, options = {}) => {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.addEventListener(event, handler, options);
        }
    },

    // 移除事件监听器
    off: (element, event, handler) => {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.removeEventListener(event, handler);
        }
    },

    // 显示/隐藏元素
    show: (element) => {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.style.display = '';
        }
    },

    hide: (element) => {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.style.display = 'none';
        }
    },

    // 切换显示状态
    toggle: (element) => {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            const isHidden = element.style.display === 'none' ||
                getComputedStyle(element).display === 'none';
            element.style.display = isHidden ? '' : 'none';
        }
    }
};

// 数据处理工具
const DataUtils = {
    // 深拷贝
    deepClone: (obj) => {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => DataUtils.deepClone(item));
        if (typeof obj === 'object') {
            const cloned = {};
            Object.keys(obj).forEach(key => {
                cloned[key] = DataUtils.deepClone(obj[key]);
            });
            return cloned;
        }
    },

    // 对象合并
    merge: (target, ...sources) => {
        if (!sources.length) return target;
        const source = sources.shift();

        if (DataUtils.isObject(target) && DataUtils.isObject(source)) {
            for (const key in source) {
                if (DataUtils.isObject(source[key])) {
                    if (!target[key]) Object.assign(target, { [key]: {} });
                    DataUtils.merge(target[key], source[key]);
                } else {
                    Object.assign(target, { [key]: source[key] });
                }
            }
        }

        return DataUtils.merge(target, ...sources);
    },

    // 判断是否为对象
    isObject: (item) => {
        return item && typeof item === 'object' && !Array.isArray(item);
    },

    // 数组去重
    unique: (array, key = null) => {
        if (key) {
            const seen = new Set();
            return array.filter(item => {
                const value = item[key];
                if (seen.has(value)) {
                    return false;
                }
                seen.add(value);
                return true;
            });
        }
        return [...new Set(array)];
    },

    // 数组分组
    groupBy: (array, key) => {
        return array.reduce((groups, item) => {
            const group = item[key];
            if (!groups[group]) {
                groups[group] = [];
            }
            groups[group].push(item);
            return groups;
        }, {});
    },

    // 数组排序
    sortBy: (array, key, order = 'asc') => {
        return array.sort((a, b) => {
            const aVal = a[key];
            const bVal = b[key];

            if (order === 'desc') {
                return bVal > aVal ? 1 : bVal < aVal ? -1 : 0;
            }
            return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
        });
    }
};

// 本地存储工具
const StorageUtils = {
    // 设置本地存储
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('LocalStorage set error:', error);
            return false;
        }
    },

    // 获取本地存储
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('LocalStorage get error:', error);
            return defaultValue;
        }
    },

    // 删除本地存储
    remove: (key) => {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('LocalStorage remove error:', error);
            return false;
        }
    },

    // 清空本地存储
    clear: () => {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('LocalStorage clear error:', error);
            return false;
        }
    }
};

// URL工具
const URLUtils = {
    // 获取URL参数
    getParams: (url = window.location.href) => {
        const params = {};
        const urlObj = new URL(url);
        urlObj.searchParams.forEach((value, key) => {
            params[key] = value;
        });
        return params;
    },

    // 设置URL参数
    setParams: (params, url = window.location.href) => {
        const urlObj = new URL(url);
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                urlObj.searchParams.set(key, params[key]);
            } else {
                urlObj.searchParams.delete(key);
            }
        });
        return urlObj.toString();
    },

    // 构建查询字符串
    buildQuery: (params) => {
        const query = new URLSearchParams();
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                query.append(key, params[key]);
            }
        });
        return query.toString();
    }
};

// 时间工具
const TimeUtils = {
    // 获取今天的日期字符串
    today: () => {
        return new Date().toISOString().split('T')[0];
    },

    // 获取昨天的日期字符串
    yesterday: () => {
        const date = new Date();
        date.setDate(date.getDate() - 1);
        return date.toISOString().split('T')[0];
    },

    // 获取N天前的日期字符串
    daysAgo: (days) => {
        const date = new Date();
        date.setDate(date.getDate() - days);
        return date.toISOString().split('T')[0];
    },

    // 计算两个日期之间的天数差
    daysBetween: (date1, date2) => {
        const oneDay = 24 * 60 * 60 * 1000;
        const firstDate = new Date(date1);
        const secondDate = new Date(date2);
        return Math.round(Math.abs((firstDate - secondDate) / oneDay));
    },

    // 格式化相对时间
    timeAgo: (date) => {
        const now = new Date();
        const past = new Date(date);
        const diffInSeconds = Math.floor((now - past) / 1000);

        if (diffInSeconds < 60) return '刚刚';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}分钟前`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}小时前`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}天前`;
        if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)}个月前`;
        return `${Math.floor(diffInSeconds / 31536000)}年前`;
    }
};

// 表单工具
const FormUtils = {
    // 序列化表单数据
    serialize: (form) => {
        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                // 处理多选字段
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }

        return data;
    },

    // 填充表单数据
    populate: (form, data) => {
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox' || field.type === 'radio') {
                    field.checked = field.value === data[key];
                } else {
                    field.value = data[key];
                }
            }
        });
    },

    // 验证表单
    validate: (form, rules = {}) => {
        const errors = {};
        const data = FormUtils.serialize(form);

        Object.keys(rules).forEach(field => {
            const value = data[field];
            const fieldRules = rules[field];

            fieldRules.forEach(rule => {
                if (typeof rule === 'function') {
                    const result = rule(value);
                    if (result !== true) {
                        if (!errors[field]) errors[field] = [];
                        errors[field].push(result);
                    }
                } else if (typeof rule === 'object') {
                    const { validator, message } = rule;
                    if (!validator(value)) {
                        if (!errors[field]) errors[field] = [];
                        errors[field].push(message);
                    }
                }
            });
        });

        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },

    // 显示验证错误
    showErrors: (form, errors) => {
        // 清除之前的错误
        FormUtils.clearErrors(form);

        // 显示新的错误
        Object.keys(errors).forEach(field => {
            const fieldElement = form.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                FormUtils.showFieldError(fieldElement, errors[field][0]);
            }
        });
    },

    // 清除表单错误
    clearErrors: (form) => {
        form.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(feedback => {
            feedback.remove();
        });
        form.querySelectorAll('.valid-feedback').forEach(feedback => {
            feedback.remove();
        });
    },

    // 显示字段错误
    showFieldError: (field, message) => {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');

        // 移除现有的反馈
        const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;

        // 插入反馈元素
        if (field.parentNode.classList.contains('input-group')) {
            field.parentNode.parentNode.appendChild(feedback);
        } else {
            field.parentNode.appendChild(feedback);
        }
    },

    // 显示字段成功状态
    showFieldSuccess: (field, message = '') => {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');

        // 移除现有的反馈
        const existingFeedback = field.parentNode.querySelector('.valid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        if (message) {
            const feedback = document.createElement('div');
            feedback.className = 'valid-feedback';
            feedback.textContent = message;

            if (field.parentNode.classList.contains('input-group')) {
                field.parentNode.parentNode.appendChild(feedback);
            } else {
                field.parentNode.appendChild(feedback);
            }
        }
    },

    // 实时验证字段
    validateField: (field, rules) => {
        const value = field.value;

        for (let rule of rules) {
            if (typeof rule === 'function') {
                const result = rule(value);
                if (result !== true) {
                    FormUtils.showFieldError(field, result);
                    return false;
                }
            } else if (typeof rule === 'object') {
                const { validator, message } = rule;
                if (!validator(value)) {
                    FormUtils.showFieldError(field, message);
                    return false;
                }
            }
        }

        FormUtils.showFieldSuccess(field);
        return true;
    },

    // 设置实时验证
    setupRealTimeValidation: (form, rules) => {
        Object.keys(rules).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const fieldRules = rules[fieldName];

                // 添加实时验证事件
                const validateOnEvent = () => {
                    setTimeout(() => {
                        FormUtils.validateField(field, fieldRules);
                    }, 100);
                };

                field.addEventListener('blur', validateOnEvent);
                field.addEventListener('input', validateOnEvent);
            }
        });
    },

    // 重置表单
    reset: (form) => {
        form.reset();
        FormUtils.clearErrors(form);
    },

    // 禁用表单
    disable: (form, disabled = true) => {
        const elements = form.querySelectorAll('input, select, textarea, button');
        elements.forEach(element => {
            element.disabled = disabled;
        });
    },

    // 获取表单数据（包含验证）
    getValidatedData: (form, rules = {}) => {
        const validation = FormUtils.validate(form, rules);

        if (!validation.isValid) {
            FormUtils.showErrors(form, validation.errors);
            return null;
        }

        return FormUtils.serialize(form);
    }
};

// UX工具
const UXUtils = {
    // 显示加载状态
    showLoading: (element, text = '加载中...') => {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (element) {
            const originalContent = element.innerHTML;
            element.dataset.originalContent = originalContent;

            element.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                ${text}
            `;
            element.disabled = true;
        }
    },

    // 隐藏加载状态
    hideLoading: (element) => {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (element && element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            element.disabled = false;
            delete element.dataset.originalContent;
        }
    },

    // 显示进度条
    showProgress: (container, progress = 0, text = '') => {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }

        if (container) {
            container.innerHTML = `
                <div class="progress mb-2">
                    <div class="progress-bar" role="progressbar" 
                         style="width: ${progress}%" 
                         aria-valuenow="${progress}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        ${progress}%
                    </div>
                </div>
                ${text ? `<small class="text-muted">${text}</small>` : ''}
            `;
        }
    },

    // 更新进度条
    updateProgress: (container, progress, text = '') => {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }

        if (container) {
            const progressBar = container.querySelector('.progress-bar');
            const textElement = container.querySelector('.text-muted');

            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-valuenow', progress);
                progressBar.textContent = `${progress}%`;
            }

            if (textElement && text) {
                textElement.textContent = text;
            }
        }
    },

    // 全局加载状态管理
    showGlobalLoading: (text = '加载中...') => {
        let overlay = document.getElementById('global-loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'global-loading-overlay';
            overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
            overlay.style.cssText = 'background: rgba(0,0,0,0.5); z-index: 9999;';
            overlay.innerHTML = `
                <div class="bg-white rounded p-4 text-center">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                    <div class="loading-text">${text}</div>
                </div>
            `;
            document.body.appendChild(overlay);
        } else {
            const textElement = overlay.querySelector('.loading-text');
            if (textElement) {
                textElement.textContent = text;
            }
            overlay.style.display = 'flex';
        }

        // 记录显示时间，用于超时检测
        overlay.dataset.showTime = Date.now().toString();

        // 设置自动超时清理（15秒后自动隐藏）
        setTimeout(() => {
            const currentOverlay = document.getElementById('global-loading-overlay');
            if (currentOverlay && currentOverlay.dataset.showTime === overlay.dataset.showTime) {
                console.warn('Global loading timeout, auto hiding...');
                UXUtils.hideGlobalLoading();
            }
        }, 15000);
    },

    hideGlobalLoading: () => {
        const overlay = document.getElementById('global-loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    },

    // 强制隐藏所有加载状态的函数
    forceHideAllLoading: () => {
        console.log('Force hiding all loading states...');

        // 隐藏全局加载遮罩
        const globalOverlay = document.getElementById('global-loading-overlay');
        if (globalOverlay) {
            globalOverlay.style.display = 'none';
            try {
                globalOverlay.remove();
            } catch (e) {
                console.warn('Failed to remove global overlay:', e);
            }
        }

        // 清理所有可能的加载元素
        const loadingElements = document.querySelectorAll(
            '*[id*="loading"], *[class*="loading"], .modal-backdrop, .loading-overlay'
        );
        loadingElements.forEach(element => {
            if (element && element.style) {
                element.style.display = 'none';
                try {
                    element.remove();
                } catch (e) {
                    console.warn('Failed to remove loading element:', e);
                }
            }
        });

        // 重置body样式
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        document.documentElement.style.overflow = '';

        console.log('All loading states force hidden');
    },
    updateProgress: (container, progress, text = '') => {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }

        if (container) {
            const progressBar = container.querySelector('.progress-bar');
            const textElement = container.querySelector('small');

            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-valuenow', progress);
                progressBar.textContent = `${progress}%`;
            }

            if (textElement && text) {
                textElement.textContent = text;
            }
        }
    },

    // 显示成功消息
    showSuccess: (message, duration = 3000) => {
        UXUtils.showToast(message, 'success', duration);
    },

    // 显示错误消息
    showError: (message, duration = 5000) => {
        UXUtils.showToast(message, 'error', duration);
    },

    // 显示警告消息
    showWarning: (message, duration = 4000) => {
        UXUtils.showToast(message, 'warning', duration);
    },

    // 显示信息消息
    showInfo: (message, duration = 3000) => {
        UXUtils.showToast(message, 'info', duration);
    },

    // 显示Toast消息
    showToast: (message, type = 'info', duration = 3000) => {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const icons = {
            'success': 'check-circle-fill',
            'error': 'exclamation-triangle-fill',
            'warning': 'exclamation-triangle-fill',
            'info': 'info-circle-fill'
        };

        const titles = {
            'success': '成功',
            'error': '错误',
            'warning': '警告',
            'info': '提示'
        };

        const colors = {
            'success': 'text-success',
            'error': 'text-danger',
            'warning': 'text-warning',
            'info': 'text-info'
        };

        const toastHtml = `
            <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="bi bi-${icons[type]} me-2 ${colors[type]}"></i>
                    <strong class="me-auto">${titles[type]}</strong>
                    <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        toast.show();

        // 自动清理
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },

    // 显示确认对话框
    showConfirm: (message, title = '确认', options = {}) => {
        return new Promise((resolve) => {
            const modalId = 'confirm-modal-' + Date.now();
            const modalHtml = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>${message}</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    ${options.cancelText || '取消'}
                                </button>
                                <button type="button" class="btn btn-primary" id="${modalId}-confirm">
                                    ${options.confirmText || '确认'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modalElement = document.getElementById(modalId);
            const modal = new bootstrap.Modal(modalElement);

            // 确认按钮事件
            document.getElementById(`${modalId}-confirm`).addEventListener('click', () => {
                modal.hide();
                resolve(true);
            });

            // 模态框关闭事件
            modalElement.addEventListener('hidden.bs.modal', () => {
                modalElement.remove();
                resolve(false);
            });

            modal.show();
        });
    },

    // 显示输入对话框
    showPrompt: (message, title = '输入', defaultValue = '', options = {}) => {
        return new Promise((resolve) => {
            const modalId = 'prompt-modal-' + Date.now();
            const modalHtml = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>${message}</p>
                                <input type="text" class="form-control" id="${modalId}-input" 
                                       value="${defaultValue}" placeholder="${options.placeholder || ''}">
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    ${options.cancelText || '取消'}
                                </button>
                                <button type="button" class="btn btn-primary" id="${modalId}-confirm">
                                    ${options.confirmText || '确认'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modalElement = document.getElementById(modalId);
            const inputElement = document.getElementById(`${modalId}-input`);
            const modal = new bootstrap.Modal(modalElement);

            // 确认按钮事件
            document.getElementById(`${modalId}-confirm`).addEventListener('click', () => {
                const value = inputElement.value.trim();
                modal.hide();
                resolve(value || null);
            });

            // 回车键确认
            inputElement.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const value = inputElement.value.trim();
                    modal.hide();
                    resolve(value || null);
                }
            });

            // 模态框关闭事件
            modalElement.addEventListener('hidden.bs.modal', () => {
                modalElement.remove();
                resolve(null);
            });

            modal.show();
            inputElement.focus();
        });
    },

    // 显示加载遮罩
    showLoadingOverlay: (container, text = '加载中...') => {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }

        if (container) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status"></div>
                    <span class="ms-2">${text}</span>
                </div>
            `;

            container.style.position = 'relative';
            container.appendChild(overlay);
        }
    },

    // 隐藏加载遮罩
    hideLoadingOverlay: (container) => {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }

        if (container) {
            const overlay = container.querySelector('.loading-overlay');
            if (overlay) {
                overlay.remove();
            }
        }
    },

    // 平滑滚动到元素
    scrollToElement: (element, offset = 0) => {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (element) {
            const elementPosition = element.offsetTop - offset;
            window.scrollTo({
                top: elementPosition,
                behavior: 'smooth'
            });
        }
    },

    // 高亮元素
    highlightElement: (element, duration = 2000) => {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (element) {
            element.classList.add('highlight-animation');
            setTimeout(() => {
                element.classList.remove('highlight-animation');
            }, duration);
        }
    },

    // 复制到剪贴板
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            UXUtils.showSuccess('已复制到剪贴板');
            return true;
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            UXUtils.showError('复制失败');
            return false;
        }
    }
};

// 响应式工具
const ResponsiveUtils = {
    // 获取当前断点
    getCurrentBreakpoint: () => {
        const width = window.innerWidth;
        if (width < 576) return 'xs';
        if (width < 768) return 'sm';
        if (width < 992) return 'md';
        if (width < 1200) return 'lg';
        if (width < 1400) return 'xl';
        return 'xxl';
    },

    // 检查是否为移动设备
    isMobile: () => {
        return window.innerWidth < 768;
    },

    // 检查是否为平板设备
    isTablet: () => {
        const width = window.innerWidth;
        return width >= 768 && width < 992;
    },

    // 检查是否为桌面设备
    isDesktop: () => {
        return window.innerWidth >= 992;
    },

    // 监听断点变化
    onBreakpointChange: (callback) => {
        let currentBreakpoint = ResponsiveUtils.getCurrentBreakpoint();

        const handleResize = () => {
            const newBreakpoint = ResponsiveUtils.getCurrentBreakpoint();
            if (newBreakpoint !== currentBreakpoint) {
                callback(newBreakpoint, currentBreakpoint);
                currentBreakpoint = newBreakpoint;
            }
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }
};

// 导出工具对象
if (typeof window !== 'undefined') {
    window.Validators = Validators;
    window.Formatters = Formatters;
    window.DOMUtils = DOMUtils;
    window.DataUtils = DataUtils;
    window.StorageUtils = StorageUtils;
    window.URLUtils = URLUtils;
    window.TimeUtils = TimeUtils;
    window.FormUtils = FormUtils;
    window.UXUtils = UXUtils;
    window.ResponsiveUtils = ResponsiveUtils;
}