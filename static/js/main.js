// 主应用逻辑
class App {
    constructor() {
        this.currentPage = null;
        this.apiClient = new ApiClient('/api');
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupNavigation();
        this.setupSidebar();
        this.loadCurrentPage();
    }

    setupEventListeners() {
        // 侧边栏切换
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', this.toggleSidebar.bind(this));
        }

        // 导航链接点击事件
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-link[data-page]')) {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.navigateTo(page);
            }
        });

        // 表单提交事件
        document.addEventListener('submit', (e) => {
            if (e.target.matches('form[data-api]')) {
                e.preventDefault();
                this.handleFormSubmit(e.target);
            }
        });

        // 全局错误处理
        window.addEventListener('error', (e) => {
            // 检查是否是 Chart.js datalabels 相关错误
            if (e.error && e.error.message) {
                const errorMsg = e.error.message;
                if (errorMsg.includes('datalabels') || 
                    (errorMsg.includes('Cannot read properties of null') && errorMsg.includes('reading \'x\''))) {
                    console.warn('Chart.js datalabels错误已被拦截:', e.error);
                    return; // 不显示用户提示
                }
            }
            
            console.error('Global error:', e.error);
            this.showMessage('系统发生错误，请刷新页面重试', 'error');
        });

        // API错误处理
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.showMessage('网络请求失败，请检查网络连接', 'error');
        });
    }

    setupNavigation() {
        // 设置当前页面的导航状态
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link[data-page]');
        
        navLinks.forEach(link => {
            const page = link.getAttribute('data-page');
            const href = link.getAttribute('href');
            
            if (currentPath === href || currentPath.includes(page)) {
                link.classList.add('active');
                this.currentPage = page;
            } else {
                link.classList.remove('active');
            }
        });
    }

    setupSidebar() {
        // 移动端侧边栏处理
        const sidebar = document.getElementById('sidebar');
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay d-lg-none';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 999;
            display: none;
        `;
        document.body.appendChild(overlay);

        // 点击遮罩关闭侧边栏
        overlay.addEventListener('click', () => {
            this.closeSidebar();
        });
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar.classList.contains('show')) {
            this.closeSidebar();
        } else {
            sidebar.classList.add('show');
            overlay.style.display = 'block';
        }
    }

    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        sidebar.classList.remove('show');
        overlay.style.display = 'none';
    }

    navigateTo(page) {
        // 简单的客户端路由
        const routes = {
            'dashboard': '/',
            'trading': '/trading-records',
            'review': '/review',
            'historical-trades': '/historical-trades',
            'stock-pool': '/stock-pool',
            'sector': '/sector-analysis',
            'cases': '/cases',
            'analytics': '/analytics',
            'non-trading-days': '/non-trading-days'
        };

        const url = routes[page];
        if (url) {
            window.location.href = url;
        }
    }

    loadCurrentPage() {
        // 根据当前页面加载相应的数据和功能
        if (this.currentPage) {
            this.initPageFeatures(this.currentPage);
        }
    }

    initPageFeatures(page) {
        // 初始化页面特定功能
        switch (page) {
            case 'dashboard':
                if (typeof initDashboard === 'function') {
                    initDashboard();
                }
                break;
            case 'trading':
                if (typeof initTradingRecords === 'function') {
                    initTradingRecords();
                }
                break;
            case 'review':
                if (typeof initReview === 'function') {
                    initReview();
                }
                break;
            case 'historical-trades':
                if (typeof HistoricalTradesManager !== 'undefined') {
                    console.log('历史交易页面已加载');
                }
                break;
            case 'stock-pool':
                if (typeof initStockPool === 'function') {
                    initStockPool();
                }
                break;
            case 'sector':
                if (typeof initSectorAnalysis === 'function') {
                    initSectorAnalysis();
                }
                break;
            case 'cases':
                if (typeof initCases === 'function') {
                    initCases();
                }
                break;
            case 'analytics':
                if (typeof initAnalytics === 'function') {
                    initAnalytics();
                }
                break;
            case 'non-trading-days':
                if (typeof NonTradingDaysManager !== 'undefined') {
                    // 非交易日页面已经有自己的初始化逻辑
                    console.log('非交易日配置页面已加载');
                }
                break;
        }
    }

    async handleFormSubmit(form) {
        const apiEndpoint = form.getAttribute('data-api');
        const method = form.getAttribute('data-method') || 'POST';
        
        // 如果表单有验证器，使用验证器处理
        if (form.formValidator) {
            return; // 让FormValidator处理提交
        }
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            this.showLoading(true);
            const response = await this.apiClient.request(method, apiEndpoint, data);
            
            if (response.success) {
                UXUtils.showSuccess('操作成功');
                // 触发自定义事件
                form.dispatchEvent(new CustomEvent('formSuccess', { detail: response }));
            } else {
                UXUtils.showError(response.message || '操作失败');
                
                // 如果有字段级错误，显示它们
                if (response.errors) {
                    this.showFormErrors(form, response.errors);
                }
            }
        } catch (error) {
            console.error('Form submission error:', error);
            
            // 处理验证错误
            if (error.response && error.response.status === 422) {
                const errors = error.response.data.errors || {};
                this.showFormErrors(form, errors);
                UXUtils.showError('请检查表单中的错误信息');
            } else {
                UXUtils.showError('提交失败，请重试');
            }
        } finally {
            this.showLoading(false);
        }
    }
    
    showFormErrors(form, errors) {
        // 清除之前的错误
        FormUtils.clearErrors(form);
        
        // 显示字段错误
        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const errorMessage = Array.isArray(errors[fieldName]) 
                    ? errors[fieldName][0] 
                    : errors[fieldName];
                FormUtils.showFieldError(field, errorMessage);
            }
        });
        
        // 滚动到第一个错误字段
        const firstErrorField = form.querySelector('.is-invalid');
        if (firstErrorField) {
            UXUtils.scrollToElement(firstErrorField, 100);
            firstErrorField.focus();
        }
    }

    showLoading(show = true) {
        const loadingModal = document.getElementById('loadingModal');
        if (loadingModal) {
            try {
                // 获取或创建模态框实例
                let modal = bootstrap.Modal.getInstance(loadingModal);
                if (!modal) {
                    modal = new bootstrap.Modal(loadingModal, {
                        backdrop: 'static',
                        keyboard: false
                    });
                }
                
                if (show) {
                    modal.show();
                } else {
                    modal.hide();
                }
            } catch (error) {
                console.error('Error controlling loading modal:', error);
                // 备用方案：直接操作DOM
                if (show) {
                    loadingModal.classList.add('show');
                    loadingModal.style.display = 'block';
                    // 添加背景遮罩
                    if (!document.querySelector('.modal-backdrop')) {
                        const backdrop = document.createElement('div');
                        backdrop.className = 'modal-backdrop fade show';
                        document.body.appendChild(backdrop);
                    }
                } else {
                    loadingModal.classList.remove('show');
                    loadingModal.style.display = 'none';
                    // 移除背景遮罩
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                }
            }
        }
    }

    showMessage(message, type = 'info', duration = 5000) {
        UXUtils.showToast(message, type, duration);
    }

    // 工具方法
    formatCurrency(amount) {
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: 'CNY'
        }).format(amount);
    }

    formatPercent(value) {
        return new Intl.NumberFormat('zh-CN', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }

    formatDate(date) {
        return new Intl.DateTimeFormat('zh-CN').format(new Date(date));
    }

    formatDateTime(date) {
        return new Intl.DateTimeFormat('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    }
}

// 全局应用实例
let app;

// DOM加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    // 清除任何可能残留的加载状态
    setTimeout(() => {
        const loadingModal = document.getElementById('loadingModal');
        if (loadingModal) {
            loadingModal.classList.remove('show');
            loadingModal.style.display = 'none';
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
        }
    }, 50);
    
    app = new App();
});

// 全局工具函数
function showMessage(message, type = 'info', config = {}) {
    // 如果config是数字，说明是旧的duration参数，转换为配置对象
    if (typeof config === 'number') {
        config = { duration: config };
    }
    
    const duration = config.duration || 5000;
    UXUtils.showToast(message, type, duration);
}

function showLoading(show = true) {
    if (app) {
        app.showLoading(show);
    } else {
        // 如果app还没初始化，直接操作DOM
        const loadingModal = document.getElementById('loadingModal');
        if (loadingModal) {
            try {
                let modal = bootstrap.Modal.getInstance(loadingModal);
                if (!modal) {
                    modal = new bootstrap.Modal(loadingModal, {
                        backdrop: 'static',
                        keyboard: false
                    });
                }
                
                if (show) {
                    modal.show();
                } else {
                    modal.hide();
                }
            } catch (error) {
                console.error('Error controlling loading modal (global):', error);
                // 最后的备用方案
                if (show) {
                    loadingModal.classList.add('show');
                    loadingModal.style.display = 'block';
                } else {
                    loadingModal.classList.remove('show');
                    loadingModal.style.display = 'none';
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) backdrop.remove();
                }
            }
        }
    }
}

function showSuccess(message, duration = 3000) {
    UXUtils.showSuccess(message, duration);
}

function showError(message, duration = 5000) {
    UXUtils.showError(message, duration);
}

function showWarning(message, duration = 4000) {
    UXUtils.showWarning(message, duration);
}

function showInfo(message, duration = 3000) {
    UXUtils.showInfo(message, duration);
}

function showConfirm(message, title = '确认', options = {}) {
    return UXUtils.showConfirm(message, title, options);
}

function showPrompt(message, title = '输入', defaultValue = '', options = {}) {
    return UXUtils.showPrompt(message, title, defaultValue, options);
}

function formatCurrency(amount) {
    return app ? app.formatCurrency(amount) : amount;
}

function formatPercent(value) {
    return app ? app.formatPercent(value) : value;
}

function formatDate(date) {
    return app ? app.formatDate(date) : date;
}

function formatDateTime(date) {
    return app ? app.formatDateTime(date) : date;
}