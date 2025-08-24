// 工具函数库 - 完全重写版本，避免所有重复声明

(function() {
    'use strict';
    
    // 防止重复加载
    if (window.UtilsLoaded) {
        console.log('Utils already loaded, skipping...');
        return;
    }
    
    // 性能优化工具
    const PerformanceUtils = {
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
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        // 批量DOM操作优化
        batchDOMUpdates: (callback) => {
            requestAnimationFrame(() => {
                callback();
            });
        },

        // 延迟加载
        lazyLoad: (selector, callback) => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        callback(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            });

            document.querySelectorAll(selector).forEach(el => {
                observer.observe(el);
            });
        }
    };

    // 数据验证工具
    const Validators = {
        // 必填验证
        required: (value) => {
            if (value === null || value === undefined) return false;
            if (typeof value === 'string') return value.trim().length > 0;
            if (typeof value === 'number') return !isNaN(value);
            if (typeof value === 'boolean') return true;
            return !!value;
        },

        // 股票代码验证
        stockCode: (code) => {
            if (!code || typeof code !== 'string') return false;
            return /^[0-9]{6}$/.test(code.trim());
        },

        // 股票名称验证
        stockName: (name) => {
            if (!name || typeof name !== 'string') return false;
            return name.trim().length > 0 && name.trim().length <= 20;
        },

        // 价格验证
        price: (price) => {
            if (price === null || price === undefined || price === '') return false;
            const num = parseFloat(price);
            return !isNaN(num) && num > 0 && num < 10000;
        },

        // 数量验证
        quantity: (quantity) => {
            if (quantity === null || quantity === undefined || quantity === '') return false;
            const num = parseInt(quantity);
            return !isNaN(num) && num > 0 && num % 100 === 0;
        },

        // 日期验证
        date: (date) => {
            if (!date) return false;
            const dateObj = new Date(date);
            return dateObj instanceof Date && !isNaN(dateObj);
        },

        // 邮箱验证
        email: (email) => {
            if (!email || typeof email !== 'string') return false;
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        }
    };

    // 格式化工具
    const Formatters = {
        // 格式化价格
        price: (price, decimals = 2) => {
            if (price === null || price === undefined || isNaN(price)) return '--';
            return parseFloat(price).toFixed(decimals);
        },

        // 格式化百分比
        percentage: (value, decimals = 2) => {
            if (value === null || value === undefined || isNaN(value)) return '--';
            return (parseFloat(value) * 100).toFixed(decimals) + '%';
        },

        // 格式化数量
        quantity: (quantity) => {
            if (quantity === null || quantity === undefined || isNaN(quantity)) return '--';
            return parseInt(quantity).toLocaleString();
        },

        // 格式化日期
        date: (date, format = 'YYYY-MM-DD') => {
            if (!date) return '--';
            const d = new Date(date);
            if (isNaN(d)) return '--';
            
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            
            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day);
        },

        // 格式化金额
        currency: (amount, currency = '¥') => {
            if (amount === null || amount === undefined || isNaN(amount)) return '--';
            return currency + parseFloat(amount).toLocaleString('zh-CN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
    };

    // DOM操作工具
    const DOMUtils = {
        // 安全获取元素
        getElement: (selector) => {
            try {
                return document.querySelector(selector);
            } catch (e) {
                console.error('Invalid selector:', selector, e);
                return null;
            }
        },

        // 安全获取多个元素
        getElements: (selector) => {
            try {
                return document.querySelectorAll(selector);
            } catch (e) {
                console.error('Invalid selector:', selector, e);
                return [];
            }
        },

        // 显示元素
        show: (element) => {
            if (element) {
                element.style.display = '';
                element.classList.remove('d-none');
            }
        },

        // 隐藏元素
        hide: (element) => {
            if (element) {
                element.style.display = 'none';
                element.classList.add('d-none');
            }
        },

        // 切换显示状态
        toggle: (element) => {
            if (element) {
                if (element.style.display === 'none' || element.classList.contains('d-none')) {
                    DOMUtils.show(element);
                } else {
                    DOMUtils.hide(element);
                }
            }
        }
    };

    // 数据处理工具
    const DataUtils = {
        // 深拷贝
        deepClone: (obj) => {
            if (obj === null || typeof obj !== 'object') return obj;
            if (obj instanceof Date) return new Date(obj);
            if (obj instanceof Array) return obj.map(item => DataUtils.deepClone(item));
            if (typeof obj === 'object') {
                const cloned = {};
                Object.keys(obj).forEach(key => {
                    cloned[key] = DataUtils.deepClone(obj[key]);
                });
                return cloned;
            }
        },

        // 数组去重
        unique: (arr, key = null) => {
            if (!Array.isArray(arr)) return [];
            if (key) {
                const seen = new Set();
                return arr.filter(item => {
                    const val = item[key];
                    if (seen.has(val)) return false;
                    seen.add(val);
                    return true;
                });
            }
            return [...new Set(arr)];
        },

        // 数组分组
        groupBy: (arr, key) => {
            if (!Array.isArray(arr)) return {};
            return arr.reduce((groups, item) => {
                const group = item[key];
                groups[group] = groups[group] || [];
                groups[group].push(item);
                return groups;
            }, {});
        }
    };

    // 存储工具
    const StorageUtils = {
        // 本地存储
        set: (key, value) => {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (e) {
                console.error('Storage set error:', e);
                return false;
            }
        },

        get: (key, defaultValue = null) => {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.error('Storage get error:', e);
                return defaultValue;
            }
        },

        remove: (key) => {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (e) {
                console.error('Storage remove error:', e);
                return false;
            }
        }
    };

    // URL工具
    const URLUtils = {
        // 获取URL参数
        getParam: (name) => {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get(name);
        },

        // 设置URL参数
        setParam: (name, value) => {
            const url = new URL(window.location);
            url.searchParams.set(name, value);
            window.history.pushState({}, '', url);
        },

        // 移除URL参数
        removeParam: (name) => {
            const url = new URL(window.location);
            url.searchParams.delete(name);
            window.history.pushState({}, '', url);
        }
    };

    // 时间工具
    const TimeUtils = {
        // 格式化时间差
        formatTimeDiff: (date1, date2 = new Date()) => {
            const diff = Math.abs(date2 - date1);
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            
            if (days > 0) return `${days}天前`;
            if (hours > 0) return `${hours}小时前`;
            if (minutes > 0) return `${minutes}分钟前`;
            return '刚刚';
        },

        // 获取今天的日期字符串
        today: () => {
            return new Date().toISOString().split('T')[0];
        }
    };

    // 表单工具
    const FormUtils = {
        // 序列化表单
        serialize: (form) => {
            if (!form) return {};
            
            const formData = new FormData(form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                if (data[key]) {
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

        // 填充表单
        populate: (form, data) => {
            if (!form || !data) return;
            
            Object.keys(data).forEach(key => {
                const element = form.querySelector(`[name="${key}"]`);
                if (element) {
                    if (element.type === 'checkbox' || element.type === 'radio') {
                        element.checked = element.value === data[key];
                    } else {
                        element.value = data[key];
                    }
                }
            });
        },

        // 重置表单
        reset: (form) => {
            if (form && typeof form.reset === 'function') {
                form.reset();
            }
        },

        // 禁用/启用表单
        disable: (form, disabled = true) => {
            if (!form) return;
            
            // 禁用/启用所有表单控件
            const formElements = form.querySelectorAll('input, select, textarea, button');
            formElements.forEach(element => {
                element.disabled = disabled;
            });
            
            // 添加/移除视觉样式
            if (disabled) {
                form.classList.add('form-disabled');
                form.style.opacity = '0.6';
                form.style.pointerEvents = 'none';
            } else {
                form.classList.remove('form-disabled');
                form.style.opacity = '';
                form.style.pointerEvents = '';
            }
        }
    };

    // 用户体验工具
    const UXUtils = {
        // 显示加载状态
        showLoading: (element, text = '加载中...') => {
            if (!element) return;
            
            element.disabled = true;
            element.dataset.originalText = element.textContent;
            element.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
        },

        // 隐藏加载状态
        hideLoading: (element) => {
            if (!element) return;
            
            element.disabled = false;
            if (element.dataset.originalText) {
                element.textContent = element.dataset.originalText;
                delete element.dataset.originalText;
            }
        },

        // 显示成功消息
        showSuccess: (message, duration = 3000) => {
            UXUtils.showMessage(message, 'success', duration);
        },

        // 显示错误消息
        showError: (message, duration = 5000) => {
            UXUtils.showMessage(message, 'danger', duration);
        },

        // 显示警告消息
        showWarning: (message, duration = 4000) => {
            UXUtils.showMessage(message, 'warning', duration);
        },

        // 显示信息消息
        showInfo: (message, duration = 3000) => {
            UXUtils.showMessage(message, 'info', duration);
        },

        // 通用消息显示
        showMessage: (message, type = 'info', duration = 3000) => {
            // 移除现有消息
            const existingAlert = document.querySelector('.alert-toast');
            if (existingAlert) {
                existingAlert.remove();
            }

            // 创建新消息
            const alert = document.createElement('div');
            alert.className = `alert alert-${type} alert-toast position-fixed`;
            alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            alert.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="flex-grow-1">${message}</div>
                    <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
                </div>
            `;

            document.body.appendChild(alert);

            // 自动移除
            if (duration > 0) {
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, duration);
            }
        },

        // Toast消息显示（别名方法，兼容现有代码）
        showToast: (message, type = 'info', duration = 3000) => {
            return UXUtils.showMessage(message, type, duration);
        },

        // 滚动到元素
        scrollToElement: (element, offset = 0) => {
            if (!element) return;
            
            const elementPosition = element.offsetTop;
            const offsetPosition = elementPosition - offset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        },

        // 显示确认对话框
        showConfirm: (message, title = '确认', options = {}) => {
            return new Promise((resolve) => {
                const confirmed = confirm(`${title}\n\n${message}`);
                resolve(confirmed);
            });
        },

        // 显示输入对话框
        showPrompt: (message, title = '输入', defaultValue = '', options = {}) => {
            return new Promise((resolve) => {
                const result = prompt(`${title}\n\n${message}`, defaultValue);
                resolve(result);
            });
        },

        // 全局加载状态管理
        showGlobalLoading: (message = '加载中...') => {
            // 移除现有的全局加载
            UXUtils.hideGlobalLoading();
            
            // 创建全局加载遮罩
            const loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'global-loading-overlay';
            loadingOverlay.className = 'position-fixed w-100 h-100 d-flex align-items-center justify-content-center';
            loadingOverlay.style.cssText = `
                top: 0;
                left: 0;
                background: rgba(0, 0, 0, 0.5);
                z-index: 9999;
                backdrop-filter: blur(2px);
            `;
            
            loadingOverlay.innerHTML = `
                <div class="bg-white rounded p-4 text-center shadow">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div class="text-muted">${message}</div>
                </div>
            `;
            
            document.body.appendChild(loadingOverlay);
            
            // 记录显示时间戳，用于超时处理
            loadingOverlay.dataset.showTime = Date.now();
            
            // 15秒自动超时隐藏
            setTimeout(() => {
                const overlay = document.getElementById('global-loading-overlay');
                if (overlay && overlay.dataset.showTime === loadingOverlay.dataset.showTime) {
                    console.warn('Global loading timeout, auto hiding...');
                    UXUtils.hideGlobalLoading();
                }
            }, 15000);
        },

        // 隐藏全局加载状态
        hideGlobalLoading: () => {
            const overlay = document.getElementById('global-loading-overlay');
            if (overlay) {
                overlay.remove();
            }
        },

        // 强制隐藏所有加载状态
        forceHideAllLoading: () => {
            // 隐藏全局加载
            UXUtils.hideGlobalLoading();
            
            // 隐藏所有按钮加载状态
            document.querySelectorAll('[data-original-text]').forEach(btn => {
                UXUtils.hideLoading(btn);
            });
            
            // 隐藏所有spinner
            document.querySelectorAll('.spinner-border, .spinner-grow').forEach(spinner => {
                const parent = spinner.closest('.btn, .card, .modal');
                if (parent) {
                    spinner.remove();
                }
            });
            
            // 移除所有加载相关的类
            document.querySelectorAll('.loading, .is-loading').forEach(el => {
                el.classList.remove('loading', 'is-loading');
                if (el.tagName === 'BUTTON') {
                    el.disabled = false;
                }
            });
            
            console.log('All loading states forcefully cleared');
        }
    };

    // 响应式工具
    const ResponsiveUtils = {
        // 检查是否为移动设备
        isMobile: () => {
            return window.innerWidth <= 768;
        },

        // 检查是否为平板设备
        isTablet: () => {
            return window.innerWidth > 768 && window.innerWidth <= 1024;
        },

        // 检查是否为桌面设备
        isDesktop: () => {
            return window.innerWidth > 1024;
        },

        // 响应式监听
        onResize: (callback) => {
            const handleResize = () => {
                callback({
                    width: window.innerWidth,
                    height: window.innerHeight,
                    isMobile: ResponsiveUtils.isMobile(),
                    isTablet: ResponsiveUtils.isTablet(),
                    isDesktop: ResponsiveUtils.isDesktop()
                });
            };

            window.addEventListener('resize', handleResize);
            return () => window.removeEventListener('resize', handleResize);
        }
    };

    // 安全地导出到全局作用域
    if (typeof window !== 'undefined') {
        window.PerformanceUtils = PerformanceUtils;
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
        
        // 标记已加载
        window.UtilsLoaded = true;
        
        console.log('✅ Utils library loaded successfully');
    }

})();