
// 强制清理加载状态的脚本
function forceCleanupLoadingStates() {
    console.log('强制清理所有加载状态...');
    
    // 清理全局加载遮罩
    const globalOverlay = document.getElementById('global-loading-overlay');
    if (globalOverlay) {
        globalOverlay.style.display = 'none';
        try {
            globalOverlay.remove();
        } catch (e) {
            console.warn('无法移除全局遮罩:', e);
        }
    }
    
    // 清理所有加载元素
    const loadingElements = document.querySelectorAll(
        '*[id*="loading"], *[class*="loading"], .modal-backdrop, .loading-overlay, .spinner-border'
    );
    
    loadingElements.forEach(element => {
        if (element && element.style) {
            element.style.display = 'none';
            // 不要移除所有spinner，只移除遮罩层的
            if (element.classList.contains('modal-backdrop') || 
                element.classList.contains('loading-overlay')) {
                try {
                    element.remove();
                } catch (e) {
                    console.warn('无法移除加载元素:', e);
                }
            }
        }
    });
    
    // 重置body样式
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    document.documentElement.style.overflow = '';
    
    // 清理持续显示"加载中"的内容区域
    const loadingContainers = document.querySelectorAll('*');
    loadingContainers.forEach(container => {
        if (container.textContent && container.textContent.includes('加载中...')) {
            // 检查是否是持续显示加载中的容器
            const parent = container.closest('.card-body, .list-group, .table-responsive');
            if (parent && !parent.querySelector('button, input, select')) {
                // 如果是纯显示容器且没有交互元素，替换为错误状态
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="bi bi-exclamation-triangle fs-1 d-block mb-2 text-warning"></i>
                        <div class="mb-2">数据加载失败</div>
                        <small class="text-muted">请刷新页面重试</small>
                        <br>
                        <button class="btn btn-outline-primary btn-sm mt-2" onclick="location.reload()">
                            <i class="bi bi-arrow-clockwise"></i> 刷新页面
                        </button>
                    </div>
                `;
            }
        }
    });
    
    console.log('加载状态清理完成');
}

// 页面加载完成后延迟执行清理
document.addEventListener('DOMContentLoaded', () => {
    // 10秒后如果还有加载状态，强制清理
    setTimeout(() => {
        const hasSpinners = document.querySelector('*[class*="spinner"]');
        const hasLoadingText = Array.from(document.querySelectorAll('*')).some(el => 
            el.textContent && el.textContent.includes('加载中'));
        
        if (hasSpinners || hasLoadingText) {
            console.warn('检测到持续的加载状态，执行强制清理...');
            forceCleanupLoadingStates();
        }
    }, 10000);
});

// 提供全局清理函数
window.forceCleanupLoadingStates = forceCleanupLoadingStates;
