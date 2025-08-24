/**
 * 统一消息提示系统
 * 为复盘页面提供一致的消息显示功能
 * 支持错误、成功、警告和信息消息
 */

class UnifiedMessageSystem {
    constructor() {
        this.messageContainer = null;
        this.toastContainer = null;
        this.init();
    }

    /**
     * 初始化消息系统
     */
    init() {
        // 确保消息容器存在
        this.ensureContainers();
        
        // 设置默认样式
        this.setupStyles();
        
        console.log('✅ 统一消息系统初始化完成');
    }

    /**
     * 确保消息容器存在
     */
    ensureContainers() {
        // 查找或创建主消息容器
        this.messageContainer = document.getElementById('message-container');
        if (!this.messageContainer) {
            this.messageContainer = document.createElement('div');
            this.messageContainer.id = 'message-container';
            this.messageContainer.className = 'message-container';
            
            // 插入到主内容区域的顶部
            const mainContent = document.querySelector('.main-content') || document.body;
            mainContent.insertBefore(this.messageContainer, mainContent.firstChild);
        }

        // 查找或创建Toast容器
        this.toastContainer = document.getElementById('toast-container');
        if (!this.toastContainer) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'toast-container';
            this.toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            this.toastContainer.style.zIndex = '9999';
            document.body.appendChild(this.toastContainer);
        }
    }

    /**
     * 设置默认样式
     */
    setupStyles() {
        // 如果样式还没有添加，则添加
        if (!document.getElementById('unified-message-styles')) {
            const style = document.createElement('style');
            style.id = 'unified-message-styles';
            style.textContent = `
                .message-container {
                    position: relative;
                    z-index: 1000;
                }
                
                .unified-alert {
                    margin-bottom: 1rem;
                    border-radius: 0.375rem;
                    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
                    animation: slideInDown 0.3s ease-out;
                }
                
                .unified-alert.fade-out {
                    animation: fadeOut 0.3s ease-out forwards;
                }
                
                .unified-toast {
                    min-width: 300px;
                    max-width: 400px;
                    animation: slideInRight 0.3s ease-out;
                }
                
                .unified-toast.fade-out {
                    animation: slideOutRight 0.3s ease-out forwards;
                }
                
                @keyframes slideInDown {
                    from {
                        transform: translateY(-20px);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
                
                @keyframes slideInRight {
                    from {
                        transform: translateX(20px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                
                @keyframes fadeOut {
                    from {
                        opacity: 1;
                    }
                    to {
                        opacity: 0;
                        transform: translateY(-10px);
                    }
                }
                
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(20px);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * 显示错误消息
     * @param {string} message - 错误消息内容
     * @param {Object} options - 配置选项
     */
    showErrorMessage(message, options = {}) {
        const config = {
            type: 'error',
            icon: 'fas fa-exclamation-triangle',
            title: '错误',
            duration: 5000,
            dismissible: true,
            position: 'alert', // 'alert' 或 'toast'
            ...options
        };

        console.error('错误消息:', message);
        
        if (config.position === 'toast') {
            this.showToast(message, config);
        } else {
            this.showAlert(message, config);
        }
    }

    /**
     * 显示成功消息
     * @param {string} message - 成功消息内容
     * @param {Object} options - 配置选项
     */
    showSuccessMessage(message, options = {}) {
        const config = {
            type: 'success',
            icon: 'fas fa-check-circle',
            title: '成功',
            duration: 3000,
            dismissible: true,
            position: 'alert', // 'alert' 或 'toast'
            ...options
        };

        console.log('成功消息:', message);
        
        if (config.position === 'toast') {
            this.showToast(message, config);
        } else {
            this.showAlert(message, config);
        }
    }

    /**
     * 显示警告消息
     * @param {string} message - 警告消息内容
     * @param {Object} options - 配置选项
     */
    showWarningMessage(message, options = {}) {
        const config = {
            type: 'warning',
            icon: 'fas fa-exclamation-circle',
            title: '警告',
            duration: 4000,
            dismissible: true,
            position: 'alert',
            ...options
        };

        console.warn('警告消息:', message);
        
        if (config.position === 'toast') {
            this.showToast(message, config);
        } else {
            this.showAlert(message, config);
        }
    }

    /**
     * 显示信息消息
     * @param {string} message - 信息消息内容
     * @param {Object} options - 配置选项
     */
    showInfoMessage(message, options = {}) {
        const config = {
            type: 'info',
            icon: 'fas fa-info-circle',
            title: '提示',
            duration: 3000,
            dismissible: true,
            position: 'alert',
            ...options
        };

        console.info('信息消息:', message);
        
        if (config.position === 'toast') {
            this.showToast(message, config);
        } else {
            this.showAlert(message, config);
        }
    }

    /**
     * 显示Alert样式的消息
     * @param {string} message - 消息内容
     * @param {Object} config - 配置对象
     */
    showAlert(message, config) {
        const alertId = 'alert-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        
        // 获取Bootstrap alert类型
        const alertClass = this.getBootstrapAlertClass(config.type);
        
        // 创建alert元素
        const alertDiv = document.createElement('div');
        alertDiv.id = alertId;
        alertDiv.className = `alert ${alertClass} unified-alert ${config.dismissible ? 'alert-dismissible' : ''} fade show`;
        alertDiv.setAttribute('role', 'alert');
        
        // 构建alert内容
        let alertContent = '';
        if (config.icon) {
            alertContent += `<i class="${config.icon} me-2"></i>`;
        }
        alertContent += message;
        
        if (config.dismissible) {
            alertContent += '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        }
        
        alertDiv.innerHTML = alertContent;
        
        // 添加到容器
        this.messageContainer.appendChild(alertDiv);
        
        // 设置自动消失
        if (config.duration > 0) {
            setTimeout(() => {
                this.removeAlert(alertId);
            }, config.duration);
        }
        
        return alertId;
    }

    /**
     * 显示Toast样式的消息
     * @param {string} message - 消息内容
     * @param {Object} config - 配置对象
     */
    showToast(message, config) {
        const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        
        // 创建toast元素
        const toastDiv = document.createElement('div');
        toastDiv.id = toastId;
        toastDiv.className = 'toast unified-toast';
        toastDiv.setAttribute('role', 'alert');
        toastDiv.setAttribute('aria-live', 'assertive');
        toastDiv.setAttribute('aria-atomic', 'true');
        
        // 获取颜色类
        const colorClass = this.getToastColorClass(config.type);
        
        // 构建toast内容
        const toastContent = `
            <div class="toast-header">
                <i class="${config.icon} me-2 ${colorClass}"></i>
                <strong class="me-auto">${config.title}</strong>
                <small class="text-muted">${this.getCurrentTime()}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        toastDiv.innerHTML = toastContent;
        
        // 添加到容器
        this.toastContainer.appendChild(toastDiv);
        
        // 初始化Bootstrap Toast
        let toast;
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            toast = new bootstrap.Toast(toastDiv, { 
                delay: config.duration,
                autohide: config.duration > 0
            });
            toast.show();
        } else {
            // 如果Bootstrap不可用，使用简单的显示/隐藏
            toastDiv.style.display = 'block';
            if (config.duration > 0) {
                setTimeout(() => {
                    this.removeToast(toastId);
                }, config.duration);
            }
        }
        
        // 监听隐藏事件，自动清理
        toastDiv.addEventListener('hidden.bs.toast', () => {
            this.removeToast(toastId);
        });
        
        return toastId;
    }

    /**
     * 移除Alert消息
     * @param {string} alertId - Alert ID
     */
    removeAlert(alertId) {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            alertElement.classList.add('fade-out');
            setTimeout(() => {
                if (alertElement.parentNode) {
                    alertElement.parentNode.removeChild(alertElement);
                }
            }, 300);
        }
    }

    /**
     * 移除Toast消息
     * @param {string} toastId - Toast ID
     */
    removeToast(toastId) {
        const toastElement = document.getElementById(toastId);
        if (toastElement) {
            toastElement.classList.add('fade-out');
            setTimeout(() => {
                if (toastElement.parentNode) {
                    toastElement.parentNode.removeChild(toastElement);
                }
            }, 300);
        }
    }

    /**
     * 清除所有消息
     */
    clearAllMessages() {
        // 清除所有alerts
        const alerts = this.messageContainer.querySelectorAll('.unified-alert');
        alerts.forEach(alert => {
            this.removeAlert(alert.id);
        });
        
        // 清除所有toasts
        const toasts = this.toastContainer.querySelectorAll('.unified-toast');
        toasts.forEach(toast => {
            this.removeToast(toast.id);
        });
    }

    /**
     * 获取Bootstrap Alert类型
     * @param {string} type - 消息类型
     * @returns {string} Bootstrap alert类
     */
    getBootstrapAlertClass(type) {
        const classMap = {
            'error': 'alert-danger',
            'success': 'alert-success',
            'warning': 'alert-warning',
            'info': 'alert-info'
        };
        return classMap[type] || 'alert-info';
    }

    /**
     * 获取Toast颜色类
     * @param {string} type - 消息类型
     * @returns {string} 颜色类
     */
    getToastColorClass(type) {
        const classMap = {
            'error': 'text-danger',
            'success': 'text-success',
            'warning': 'text-warning',
            'info': 'text-info'
        };
        return classMap[type] || 'text-info';
    }

    /**
     * 获取当前时间字符串
     * @returns {string} 格式化的时间字符串
     */
    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
    }

    /**
     * 批量显示消息
     * @param {Array} messages - 消息数组
     */
    showMessages(messages) {
        messages.forEach((msg, index) => {
            setTimeout(() => {
                const method = `show${msg.type.charAt(0).toUpperCase() + msg.type.slice(1)}Message`;
                if (typeof this[method] === 'function') {
                    this[method](msg.message, msg.options || {});
                }
            }, index * 200); // 错开显示时间
        });
    }

    /**
     * 显示加载消息
     * @param {string} message - 加载消息
     * @returns {string} 消息ID，用于后续移除
     */
    showLoadingMessage(message = '正在处理...') {
        const config = {
            type: 'info',
            icon: 'fas fa-spinner fa-spin',
            title: '处理中',
            duration: 0, // 不自动消失
            dismissible: false,
            position: 'alert'
        };
        
        return this.showAlert(message, config);
    }

    /**
     * 隐藏加载消息
     * @param {string} messageId - 消息ID
     */
    hideLoadingMessage(messageId) {
        this.removeAlert(messageId);
    }
}

// 创建全局实例
let unifiedMessageSystem = null;

// 初始化函数
function initializeUnifiedMessageSystem() {
    if (!unifiedMessageSystem) {
        unifiedMessageSystem = new UnifiedMessageSystem();
    }
    return unifiedMessageSystem;
}

// 便捷函数 - 与现有代码兼容
function showErrorMessage(message, options = {}) {
    if (!unifiedMessageSystem) {
        initializeUnifiedMessageSystem();
    }
    return unifiedMessageSystem.showErrorMessage(message, options);
}

function showSuccessMessage(message, options = {}) {
    if (!unifiedMessageSystem) {
        initializeUnifiedMessageSystem();
    }
    return unifiedMessageSystem.showSuccessMessage(message, options);
}

function showWarningMessage(message, options = {}) {
    if (!unifiedMessageSystem) {
        initializeUnifiedMessageSystem();
    }
    return unifiedMessageSystem.showWarningMessage(message, options);
}

function showInfoMessage(message, options = {}) {
    if (!unifiedMessageSystem) {
        initializeUnifiedMessageSystem();
    }
    return unifiedMessageSystem.showInfoMessage(message, options);
}

// DOM加载完成后自动初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeUnifiedMessageSystem();
});

// 导出到全局作用域（用于向后兼容）
window.UnifiedMessageSystem = UnifiedMessageSystem;
window.unifiedMessageSystem = unifiedMessageSystem;
window.showErrorMessage = showErrorMessage;
window.showSuccessMessage = showSuccessMessage;
window.showWarningMessage = showWarningMessage;
window.showInfoMessage = showInfoMessage;