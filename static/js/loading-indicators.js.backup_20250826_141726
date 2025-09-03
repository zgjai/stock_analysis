/**
 * 加载指示器和进度条组件
 * 提供各种加载状态的视觉反馈
 */

/**
 * 全局加载管理器
 */
class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
        this.globalOverlay = null;
        this.loadingStates = new Map();
        
        this.init();
    }
    
    /**
     * 初始化加载管理器
     */
    init() {
        this.createGlobalOverlay();
        this.injectStyles();
    }
    
    /**
     * 创建全局遮罩层
     */
    createGlobalOverlay() {
        this.globalOverlay = document.createElement('div');
        this.globalOverlay.className = 'global-loading-overlay';
        this.globalOverlay.innerHTML = `
            <div class="loading-spinner-container">
                <div class="loading-spinner">
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                </div>
                <div class="loading-text">加载中...</div>
            </div>
        `;
        
        document.body.appendChild(this.globalOverlay);
    }
    
    /**
     * 注入样式
     */
    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .global-loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(2px);
                z-index: 9999;
                display: none;
                align-items: center;
                justify-content: center;
                transition: opacity 0.3s ease;
            }
            
            .global-loading-overlay.show {
                display: flex;
            }
            
            .loading-spinner-container {
                text-align: center;
            }
            
            .loading-spinner {
                position: relative;
                width: 60px;
                height: 60px;
                margin: 0 auto 20px;
            }
            
            .spinner-ring {
                position: absolute;
                width: 100%;
                height: 100%;
                border: 3px solid transparent;
                border-top: 3px solid #007bff;
                border-radius: 50%;
                animation: spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
            }
            
            .spinner-ring:nth-child(1) { animation-delay: -0.45s; }
            .spinner-ring:nth-child(2) { animation-delay: -0.3s; }
            .spinner-ring:nth-child(3) { animation-delay: -0.15s; }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .loading-text {
                color: #6c757d;
                font-size: 14px;
                font-weight: 500;
            }
            
            .inline-loading {
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            
            .inline-spinner {
                width: 16px;
                height: 16px;
                border: 2px solid #f3f3f3;
                border-top: 2px solid #007bff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            .button-loading {
                position: relative;
                pointer-events: none;
            }
            
            .button-loading::after {
                content: '';
                position: absolute;
                width: 16px;
                height: 16px;
                margin: auto;
                border: 2px solid transparent;
                border-top-color: currentColor;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                top: 0;
                left: 0;
                bottom: 0;
                right: 0;
            }
            
            .skeleton-loader {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: skeleton-loading 1.5s infinite;
            }
            
            @keyframes skeleton-loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
            
            .progress-bar-container {
                width: 100%;
                height: 4px;
                background-color: #e9ecef;
                border-radius: 2px;
                overflow: hidden;
                position: relative;
            }
            
            .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #007bff, #0056b3);
                border-radius: 2px;
                transition: width 0.3s ease;
                position: relative;
            }
            
            .progress-bar.indeterminate {
                width: 30% !important;
                animation: indeterminate-progress 2s infinite;
            }
            
            @keyframes indeterminate-progress {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(400%); }
            }
            
            .pulse-loader {
                animation: pulse 1.5s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .dots-loader {
                display: inline-flex;
                gap: 4px;
            }
            
            .dots-loader .dot {
                width: 6px;
                height: 6px;
                background-color: #007bff;
                border-radius: 50%;
                animation: dots-bounce 1.4s ease-in-out infinite both;
            }
            
            .dots-loader .dot:nth-child(1) { animation-delay: -0.32s; }
            .dots-loader .dot:nth-child(2) { animation-delay: -0.16s; }
            
            @keyframes dots-bounce {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1); }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    /**
     * 显示全局加载
     * @param {string} text - 加载文本
     * @param {string} id - 加载ID
     */
    showGlobal(text = '加载中...', id = 'default') {
        this.activeLoaders.add(id);
        
        const textElement = this.globalOverlay.querySelector('.loading-text');
        if (textElement) {
            textElement.textContent = text;
        }
        
        this.globalOverlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * 隐藏全局加载
     * @param {string} id - 加载ID
     */
    hideGlobal(id = 'default') {
        this.activeLoaders.delete(id);
        
        if (this.activeLoaders.size === 0) {
            this.globalOverlay.classList.remove('show');
            document.body.style.overflow = '';
        }
    }
    
    /**
     * 创建内联加载指示器
     * @param {string} text - 加载文本
     * @param {string} size - 大小 (small, medium, large)
     * @returns {HTMLElement} 加载元素
     */
    createInline(text = '加载中...', size = 'medium') {
        const container = document.createElement('div');
        container.className = 'inline-loading';
        
        const spinner = document.createElement('div');
        spinner.className = `inline-spinner ${size}`;
        
        const textElement = document.createElement('span');
        textElement.textContent = text;
        textElement.className = 'loading-text';
        
        container.appendChild(spinner);
        container.appendChild(textElement);
        
        return container;
    }
    
    /**
     * 为按钮添加加载状态
     * @param {HTMLElement} button - 按钮元素
     * @param {boolean} loading - 是否加载中
     * @param {string} loadingText - 加载时的文本
     */
    setButtonLoading(button, loading, loadingText = null) {
        if (!button) return;
        
        if (loading) {
            button.dataset.originalText = button.textContent;
            button.classList.add('button-loading');
            button.disabled = true;
            
            if (loadingText) {
                button.textContent = loadingText;
            }
        } else {
            button.classList.remove('button-loading');
            button.disabled = false;
            
            if (button.dataset.originalText) {
                button.textContent = button.dataset.originalText;
                delete button.dataset.originalText;
            }
        }
    }
    
    /**
     * 创建骨架屏加载器
     * @param {Object} config - 配置对象
     * @returns {HTMLElement} 骨架屏元素
     */
    createSkeleton(config = {}) {
        const {
            width = '100%',
            height = '20px',
            borderRadius = '4px',
            count = 1,
            gap = '10px'
        } = config;
        
        const container = document.createElement('div');
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = gap;
        
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-loader';
            skeleton.style.width = Array.isArray(width) ? width[i] || width[0] : width;
            skeleton.style.height = Array.isArray(height) ? height[i] || height[0] : height;
            skeleton.style.borderRadius = borderRadius;
            
            container.appendChild(skeleton);
        }
        
        return container;
    }
    
    /**
     * 创建进度条
     * @param {Object} options - 选项
     * @returns {Object} 进度条控制对象
     */
    createProgressBar(options = {}) {
        const {
            container,
            height = '4px',
            color = '#007bff',
            backgroundColor = '#e9ecef',
            animated = true
        } = options;
        
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress-bar-container';
        progressContainer.style.height = height;
        progressContainer.style.backgroundColor = backgroundColor;
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.style.background = color;
        progressBar.style.width = '0%';
        
        if (animated) {
            progressBar.style.transition = 'width 0.3s ease';
        }
        
        progressContainer.appendChild(progressBar);
        
        if (container) {
            container.appendChild(progressContainer);
        }
        
        return {
            element: progressContainer,
            setProgress: (percent) => {
                progressBar.style.width = `${Math.max(0, Math.min(100, percent))}%`;
            },
            setIndeterminate: (indeterminate) => {
                if (indeterminate) {
                    progressBar.classList.add('indeterminate');
                } else {
                    progressBar.classList.remove('indeterminate');
                }
            },
            destroy: () => {
                if (progressContainer.parentNode) {
                    progressContainer.parentNode.removeChild(progressContainer);
                }
            }
        };
    }
    
    /**
     * 创建点状加载器
     * @param {HTMLElement} container - 容器元素
     * @returns {HTMLElement} 点状加载器元素
     */
    createDotsLoader(container = null) {
        const loader = document.createElement('div');
        loader.className = 'dots-loader';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'dot';
            loader.appendChild(dot);
        }
        
        if (container) {
            container.appendChild(loader);
        }
        
        return loader;
    }
    
    /**
     * 为元素添加脉冲加载效果
     * @param {HTMLElement} element - 目标元素
     * @param {boolean} loading - 是否加载中
     */
    setPulseLoading(element, loading) {
        if (!element) return;
        
        if (loading) {
            element.classList.add('pulse-loader');
        } else {
            element.classList.remove('pulse-loader');
        }
    }
    
    /**
     * 显示加载状态
     * @param {string} key - 状态键
     * @param {Object} options - 选项
     */
    showLoading(key, options = {}) {
        const {
            type = 'global',
            text = '加载中...',
            container = null,
            timeout = 0
        } = options;
        
        this.loadingStates.set(key, {
            type,
            startTime: Date.now(),
            timeout: timeout > 0 ? setTimeout(() => {
                this.hideLoading(key);
            }, timeout) : null
        });
        
        switch (type) {
            case 'global':
                this.showGlobal(text, key);
                break;
            case 'inline':
                if (container) {
                    const loader = this.createInline(text);
                    loader.dataset.loadingKey = key;
                    container.appendChild(loader);
                }
                break;
            case 'button':
                if (container) {
                    this.setButtonLoading(container, true, text);
                }
                break;
            case 'pulse':
                if (container) {
                    this.setPulseLoading(container, true);
                }
                break;
        }
    }
    
    /**
     * 隐藏加载状态
     * @param {string} key - 状态键
     */
    hideLoading(key) {
        const state = this.loadingStates.get(key);
        if (!state) return;
        
        // 清除超时定时器
        if (state.timeout) {
            clearTimeout(state.timeout);
        }
        
        switch (state.type) {
            case 'global':
                this.hideGlobal(key);
                break;
            case 'inline':
                const inlineLoader = document.querySelector(`[data-loading-key="${key}"]`);
                if (inlineLoader && inlineLoader.parentNode) {
                    inlineLoader.parentNode.removeChild(inlineLoader);
                }
                break;
            case 'button':
                // 按钮加载状态需要外部传入元素引用
                break;
            case 'pulse':
                // 脉冲加载状态需要外部传入元素引用
                break;
        }
        
        this.loadingStates.delete(key);
    }
    
    /**
     * 检查是否正在加载
     * @param {string} key - 状态键
     * @returns {boolean} 是否正在加载
     */
    isLoading(key) {
        return this.loadingStates.has(key);
    }
    
    /**
     * 获取加载持续时间
     * @param {string} key - 状态键
     * @returns {number} 持续时间（毫秒）
     */
    getLoadingDuration(key) {
        const state = this.loadingStates.get(key);
        return state ? Date.now() - state.startTime : 0;
    }
    
    /**
     * 清除所有加载状态
     */
    clearAll() {
        for (const key of this.loadingStates.keys()) {
            this.hideLoading(key);
        }
    }
    
    /**
     * 销毁加载管理器
     */
    destroy() {
        this.clearAll();
        
        if (this.globalOverlay && this.globalOverlay.parentNode) {
            this.globalOverlay.parentNode.removeChild(this.globalOverlay);
        }
        
        document.body.style.overflow = '';
    }
}

/**
 * 智能加载装饰器
 * 自动为异步函数添加加载状态
 */
function withLoading(options = {}) {
    const {
        key = 'default',
        type = 'global',
        text = '加载中...',
        minDuration = 500,
        container = null
    } = options;
    
    return function decorator(target, propertyKey, descriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = async function(...args) {
            const startTime = Date.now();
            
            // 显示加载状态
            loadingManager.showLoading(key, { type, text, container });
            
            try {
                const result = await originalMethod.apply(this, args);
                
                // 确保最小加载时间
                const elapsed = Date.now() - startTime;
                if (elapsed < minDuration) {
                    await new Promise(resolve => setTimeout(resolve, minDuration - elapsed));
                }
                
                return result;
            } finally {
                // 隐藏加载状态
                loadingManager.hideLoading(key);
            }
        };
        
        return descriptor;
    };
}

// 创建全局加载管理器实例
const loadingManager = new LoadingManager();

// 导出类和实例
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LoadingManager, loadingManager, withLoading };
}