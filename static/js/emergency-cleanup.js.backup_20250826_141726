// 紧急清理脚本 - 专门解决加载状态卡住问题
(function() {
    'use strict';
    
    console.log('🚨 紧急清理脚本启动');
    
    // 强力清理函数
    function nuclearCleanup() {
        console.log('🧹 执行核心清理...');
        
        // 1. 清理所有可能的加载遮罩
        const selectors = [
            '#global-loading-overlay',
            '.loading-overlay', 
            '.modal-backdrop',
            '[id*="loading"]',
            '[class*="loading"]',
            '[id*="Loading"]',
            '[class*="Loading"]',
            '.spinner-border',
            '.spinner-grow'
        ];
        
        selectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    if (element) {
                        element.style.display = 'none';
                        element.style.visibility = 'hidden';
                        element.style.opacity = '0';
                        element.style.zIndex = '-9999';
                        
                        // 尝试移除
                        setTimeout(() => {
                            try {
                                if (element.parentNode) {
                                    element.parentNode.removeChild(element);
                                }
                            } catch (e) {
                                console.warn('移除元素失败:', e);
                            }
                        }, 100);
                    }
                });
            } catch (e) {
                console.warn(`清理选择器 ${selector} 失败:`, e);
            }
        });
        
        // 2. 重置body和html样式
        if (document.body) {
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            document.body.style.position = '';
        }
        
        if (document.documentElement) {
            document.documentElement.style.overflow = '';
            document.documentElement.style.paddingRight = '';
        }
        
        // 3. 清理可能的内联样式
        const allElements = document.querySelectorAll('*');
        allElements.forEach(element => {
            if (element.style && element.style.zIndex === '9999') {
                element.style.display = 'none';
            }
        });
        
        console.log('✅ 核心清理完成');
    }
    
    // 立即执行
    nuclearCleanup();
    
    // 页面加载完成后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', nuclearCleanup);
    } else {
        nuclearCleanup();
    }
    
    // 窗口加载完成后执行
    window.addEventListener('load', nuclearCleanup);
    
    // 定期清理 - 每500ms检查一次，持续30秒
    let cleanupCount = 0;
    const aggressiveCleanup = setInterval(() => {
        const overlay = document.getElementById('global-loading-overlay');
        if (overlay && (overlay.style.display !== 'none' || overlay.offsetParent !== null)) {
            console.log('🎯 检测到顽固加载状态，执行强制清理');
            nuclearCleanup();
        }
        
        cleanupCount++;
        if (cleanupCount >= 60) { // 30秒后停止
            clearInterval(aggressiveCleanup);
            console.log('🏁 定期清理结束');
        }
    }, 500);
    
    // 暴露全局清理函数
    window.EMERGENCY_CLEANUP = nuclearCleanup;
    window.FORCE_HIDE_LOADING = nuclearCleanup;
    
    // 监听键盘快捷键 Ctrl+Shift+C 进行紧急清理
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'C') {
            console.log('🔥 快捷键触发紧急清理');
            nuclearCleanup();
        }
    });
    
    console.log('🚨 紧急清理脚本就绪 - 使用 EMERGENCY_CLEANUP() 或 Ctrl+Shift+C');
})();