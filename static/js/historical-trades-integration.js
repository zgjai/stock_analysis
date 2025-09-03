/**
 * 历史交易功能集成脚本
 * 负责协调各个模块之间的交互
 */
class HistoricalTradesIntegration {
    constructor() {
        this.manager = null;
        this.reviewEditor = null;
        this.reviewViewer = null;
        this.imageUploader = null;
        
        this.init();
    }

    async init() {
        try {
            // 等待DOM加载完成
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
            } else {
                this.initializeComponents();
            }
        } catch (error) {
            console.error('Historical trades integration init error:', error);
        }
    }

    initializeComponents() {
        // 检查是否在历史交易页面
        if (!this.isHistoricalTradesPage()) {
            return;
        }

        // 标记页面类型
        document.body.classList.add('historical-trades-page');

        // 初始化各个组件
        this.initializeManager();
        this.initializeReviewEditor();
        this.initializeReviewViewer();
        this.setupGlobalEventHandlers();
        this.setupErrorHandling();
        
        console.log('Historical trades integration initialized successfully');
    }

    isHistoricalTradesPage() {
        // 检查URL或页面标识
        return window.location.pathname.includes('/historical-trades') ||
               document.querySelector('#historical-trades-table') !== null ||
               document.body.classList.contains('historical-trades-page');
    }

    initializeManager() {
        if (typeof HistoricalTradesManager !== 'undefined') {
            this.manager = new HistoricalTradesManager();
            window.historicalTradesManager = this.manager;
        } else {
            console.warn('HistoricalTradesManager not available');
        }
    }

    initializeReviewEditor() {
        if (typeof ReviewEditor !== 'undefined') {
            this.reviewEditor = new ReviewEditor();
            window.reviewEditor = this.reviewEditor;
        } else {
            console.warn('ReviewEditor not available');
        }
    }

    initializeReviewViewer() {
        if (typeof ReviewViewer !== 'undefined') {
            this.reviewViewer = new ReviewViewer();
            window.reviewViewer = this.reviewViewer;
        } else {
            console.warn('ReviewViewer not available');
        }
    }

    setupGlobalEventHandlers() {
        // 复盘保存成功事件
        document.addEventListener('reviewSaved', (e) => {
            if (this.manager) {
                this.manager.loadHistoricalTrades();
            }
        });

        // 复盘编辑事件
        document.addEventListener('editReview', (e) => {
            if (this.manager) {
                this.manager.editReviewById(e.detail.reviewId, e.detail.reviewData);
            }
        });

        // 全局键盘快捷键
        document.addEventListener('keydown', (e) => {
            this.handleGlobalKeyboard(e);
        });

        // 网络状态监听
        window.addEventListener('online', () => {
            this.showMessage('网络连接已恢复', 'success');
        });

        window.addEventListener('offline', () => {
            this.showMessage('网络连接已断开', 'warning');
        });

        // 页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.manager) {
                // 页面重新可见时刷新数据
                this.manager.loadHistoricalTrades();
            }
        });
    }

    handleGlobalKeyboard(e) {
        // 只在历史交易页面处理
        if (!this.isHistoricalTradesPage()) return;

        // F5 刷新数据
        if (e.key === 'F5') {
            e.preventDefault();
            if (this.manager) {
                this.manager.loadHistoricalTrades();
            }
        }

        // Ctrl+F 聚焦搜索
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.getElementById('stock-code-filter');
            if (searchInput) {
                searchInput.focus();
            }
        }
    }

    setupErrorHandling() {
        // 全局错误处理
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            this.handleGlobalError(e.error);
        });

        // Promise 错误处理
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.handleGlobalError(e.reason);
        });
    }

    handleGlobalError(error) {
        // 只处理与历史交易相关的错误
        if (!this.isHistoricalTradesPage()) return;

        let message = '发生了未知错误';
        
        if (error.message) {
            if (error.message.includes('network') || error.message.includes('fetch')) {
                message = '网络连接错误，请检查网络连接';
            } else if (error.message.includes('timeout')) {
                message = '请求超时，请稍后重试';
            } else {
                message = error.message;
            }
        }

        this.showMessage(message, 'error');
    }

    // 工具方法
    showMessage(message, type = 'info') {
        if (window.showMessage) {
            window.showMessage(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    // 性能监控
    startPerformanceMonitoring() {
        if (!window.performance) return;

        // 监控页面加载性能
        window.addEventListener('load', () => {
            setTimeout(() => {
                const navigation = performance.getEntriesByType('navigation')[0];
                if (navigation) {
                    const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
                    console.log(`Page load time: ${loadTime}ms`);
                    
                    if (loadTime > 3000) {
                        console.warn('Page load time is slow');
                    }
                }
            }, 0);
        });

        // 监控API请求性能
        this.monitorApiPerformance();
    }

    monitorApiPerformance() {
        const originalFetch = window.fetch;
        
        window.fetch = async function(...args) {
            const startTime = performance.now();
            
            try {
                const response = await originalFetch.apply(this, args);
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                console.log(`API request: ${args[0]} - ${duration.toFixed(2)}ms`);
                
                if (duration > 5000) {
                    console.warn(`Slow API request: ${args[0]} - ${duration.toFixed(2)}ms`);
                }
                
                return response;
            } catch (error) {
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                console.error(`API request failed: ${args[0]} - ${duration.toFixed(2)}ms`, error);
                throw error;
            }
        };
    }

    // 数据预加载
    async preloadData() {
        if (!this.manager) return;

        try {
            // 预加载统计数据
            await this.manager.loadStatistics();
        } catch (error) {
            console.warn('Preload data failed:', error);
        }
    }

    // 清理资源
    cleanup() {
        // 清理事件监听器
        document.removeEventListener('reviewSaved', this.handleReviewSaved);
        document.removeEventListener('editReview', this.handleEditReview);
        
        // 清理组件
        if (this.reviewEditor && this.reviewEditor.disableAutoSave) {
            this.reviewEditor.disableAutoSave();
        }
        
        // 清理缓存
        if (this.manager && this.manager.clearCache) {
            this.manager.clearCache();
        }
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    window.historicalTradesIntegration = new HistoricalTradesIntegration();
});

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    if (window.historicalTradesIntegration) {
        window.historicalTradesIntegration.cleanup();
    }
});

// 导出类
window.HistoricalTradesIntegration = HistoricalTradesIntegration;