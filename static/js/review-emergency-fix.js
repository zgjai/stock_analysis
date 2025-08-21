/**
 * 复盘页面紧急修复脚本
 * 解决加载和API调用问题
 */

// 全局错误处理
window.addEventListener('error', function (e) {
    console.error('JavaScript错误:', e.error);
});

// 全局未处理的Promise拒绝处理
window.addEventListener('unhandledrejection', function (e) {
    console.error('未处理的Promise拒绝:', e.reason);
    e.preventDefault();
});

// API调用增强错误处理
const originalFetch = window.fetch;
window.fetch = function (...args) {
    return originalFetch.apply(this, args)
        .then(response => {
            if (!response.ok) {
                console.error(`API请求失败: ${response.status} ${response.statusText}`, args[0]);
            }
            return response;
        })
        .catch(error => {
            console.error('网络请求错误:', error, args[0]);
            throw error;
        });
};

// 确保DOM加载完成后再执行初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEmergencyFixes);
} else {
    initializeEmergencyFixes();
}

function initializeEmergencyFixes() {
    console.log('复盘页面紧急修复脚本已加载');

    // 添加加载状态管理
    window.showLoading = function (message = '加载中...') {
        const existingLoader = document.querySelector('.loading-overlay');
        if (existingLoader) return;

        const loader = document.createElement('div');
        loader.className = 'loading-overlay';
        loader.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <div class="loading-text">${message}</div>
            </div>
        `;
        document.body.appendChild(loader);
    };

    window.hideLoading = function () {
        const loader = document.querySelector('.loading-overlay');
        if (loader) {
            loader.remove();
        }
    };

    // 添加错误显示功能
    window.showError = function (message, details = '') {
        console.error('显示错误:', message, details);

        // 移除现有的错误提示
        const existingError = document.querySelector('.error-alert');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger error-alert';
        errorDiv.innerHTML = `
            <strong>错误:</strong> ${message}
            ${details ? `<br><small>${details}</small>` : ''}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;

        const container = document.querySelector('.container-fluid') || document.body;
        container.insertBefore(errorDiv, container.firstChild);

        // 5秒后自动移除
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    };
}