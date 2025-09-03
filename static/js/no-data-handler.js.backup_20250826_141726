// 无数据状态处理辅助函数
class NoDataHandler {
    static showEmptyState(containerId, message = '暂无数据', icon = 'fas fa-inbox') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="${icon} fa-2x mb-3"></i>
                    <p class="mb-2">${message}</p>
                    <small class="text-muted">
                        系统可能刚启动或暂无相关数据
                        <br>
                        <button class="btn btn-outline-primary btn-sm mt-2" onclick="location.reload()">
                            <i class="fas fa-refresh"></i> 重新加载
                        </button>
                    </small>
                </div>
            `;
        }
    }
    
    static showLoadingState(containerId, message = '加载中...') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    ${message}
                    <br>
                    <small class="text-muted mt-2 d-block">
                        如果长时间无响应，可能是系统刚启动，请稍后重试
                    </small>
                </div>
            `;
        }
    }
    
    static showErrorState(containerId, error = '加载失败') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3 text-warning"></i>
                    <p class="mb-2">${error}</p>
                    <small class="text-muted">
                        请检查网络连接或稍后重试
                        <br>
                        <button class="btn btn-outline-primary btn-sm mt-2" onclick="location.reload()">
                            <i class="fas fa-refresh"></i> 重新加载
                        </button>
                    </small>
                </div>
            `;
        }
    }
    
    static withTimeout(promise, timeoutMs = 3000, timeoutMessage = '请求超时') {
        return Promise.race([
            promise,
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error(timeoutMessage)), timeoutMs)
            )
        ]);
    }
}

// 全局可用
window.NoDataHandler = NoDataHandler;
