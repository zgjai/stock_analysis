/**
 * 性能优化工具类
 * 提供防抖、节流、缓存等性能优化功能
 */

/**
 * 防抖函数 - 延迟执行，在指定时间内多次调用只执行最后一次
 * @param {Function} func - 要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @param {boolean} immediate - 是否立即执行第一次
 * @returns {Function} 防抖后的函数
 */
if (typeof window.debounce === 'undefined') {
    window.debounce = function(func, delay, immediate = false) {
    let timeoutId;
    let lastCallTime = 0;
    
    return function debounced(...args) {
        const context = this;
        const now = Date.now();
        
        const callNow = immediate && !timeoutId;
        
        clearTimeout(timeoutId);
        
        timeoutId = setTimeout(() => {
            timeoutId = null;
            if (!immediate) {
                lastCallTime = Date.now();
                func.apply(context, args);
            }
        }, delay);
        
        if (callNow) {
            lastCallTime = now;
            func.apply(context, args);
        }
    };
    };
}

/**
 * 节流函数 - 限制函数执行频率
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 时间间隔（毫秒）
 * @returns {Function} 节流后的函数
 */
if (typeof window.throttle === 'undefined') {
    window.throttle = function(func, limit) {
    let inThrottle;
    let lastFunc;
    let lastRan;
    
    return function throttled(...args) {
        const context = this;
        
        if (!inThrottle) {
            func.apply(context, args);
            lastRan = Date.now();
            inThrottle = true;
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(() => {
                if ((Date.now() - lastRan) >= limit) {
                    func.apply(context, args);
                    lastRan = Date.now();
                }
            }, limit - (Date.now() - lastRan));
        }
    };
    };
}

/**
 * 请求动画帧节流 - 使用 requestAnimationFrame 优化高频更新
 * @param {Function} func - 要优化的函数
 * @returns {Function} 优化后的函数
 */
function rafThrottle(func) {
    let rafId = null;
    let lastArgs = null;
    
    return function rafThrottled(...args) {
        const context = this;
        lastArgs = args;
        
        if (rafId === null) {
            rafId = requestAnimationFrame(() => {
                func.apply(context, lastArgs);
                rafId = null;
            });
        }
    };
}

/**
 * 内存缓存类
 */
class MemoryCache {
    constructor(maxSize = 100, ttl = 300000) { // 默认5分钟TTL
        this.cache = new Map();
        this.maxSize = maxSize;
        this.ttl = ttl;
        this.timers = new Map();
    }
    
    /**
     * 设置缓存
     * @param {string} key - 缓存键
     * @param {*} value - 缓存值
     * @param {number} customTtl - 自定义TTL
     */
    set(key, value, customTtl = null) {
        // 如果缓存已满，删除最旧的项
        if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
            const firstKey = this.cache.keys().next().value;
            this.delete(firstKey);
        }
        
        // 清除旧的定时器
        if (this.timers.has(key)) {
            clearTimeout(this.timers.get(key));
        }
        
        // 设置新值
        this.cache.set(key, {
            value: value,
            timestamp: Date.now()
        });
        
        // 设置过期定时器
        const ttl = customTtl || this.ttl;
        if (ttl > 0) {
            const timer = setTimeout(() => {
                this.delete(key);
            }, ttl);
            this.timers.set(key, timer);
        }
    }
    
    /**
     * 获取缓存
     * @param {string} key - 缓存键
     * @returns {*} 缓存值或null
     */
    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        // 检查是否过期
        if (this.ttl > 0 && Date.now() - item.timestamp > this.ttl) {
            this.delete(key);
            return null;
        }
        
        return item.value;
    }
    
    /**
     * 删除缓存
     * @param {string} key - 缓存键
     */
    delete(key) {
        this.cache.delete(key);
        if (this.timers.has(key)) {
            clearTimeout(this.timers.get(key));
            this.timers.delete(key);
        }
    }
    
    /**
     * 清空缓存
     */
    clear() {
        this.cache.clear();
        this.timers.forEach(timer => clearTimeout(timer));
        this.timers.clear();
    }
    
    /**
     * 获取缓存大小
     */
    size() {
        return this.cache.size;
    }
    
    /**
     * 检查是否存在
     * @param {string} key - 缓存键
     */
    has(key) {
        return this.cache.has(key) && this.get(key) !== null;
    }
}

/**
 * API请求缓存装饰器
 * @param {number} ttl - 缓存时间（毫秒）
 * @param {Function} keyGenerator - 缓存键生成函数
 */
function apiCache(ttl = 60000, keyGenerator = null) {
    const cache = new MemoryCache(50, ttl);
    
    return function decorator(target, propertyKey, descriptor) {
        const originalMethod = descriptor.value;
        
        descriptor.value = async function(...args) {
            // 生成缓存键
            const key = keyGenerator ? 
                keyGenerator.apply(this, args) : 
                `${propertyKey}_${JSON.stringify(args)}`;
            
            // 检查缓存
            const cached = cache.get(key);
            if (cached) {
                return cached;
            }
            
            // 执行原方法
            try {
                const result = await originalMethod.apply(this, args);
                
                // 只缓存成功的结果
                if (result && result.success) {
                    cache.set(key, result, ttl);
                }
                
                return result;
            } catch (error) {
                // 不缓存错误结果
                throw error;
            }
        };
        
        return descriptor;
    };
}

/**
 * 批量操作优化器
 */
class BatchProcessor {
    constructor(batchSize = 10, delay = 100) {
        this.batchSize = batchSize;
        this.delay = delay;
        this.queue = [];
        this.timer = null;
        this.processing = false;
    }
    
    /**
     * 添加任务到批处理队列
     * @param {Function} task - 任务函数
     * @param {*} data - 任务数据
     * @returns {Promise} 任务结果Promise
     */
    add(task, data) {
        return new Promise((resolve, reject) => {
            this.queue.push({
                task,
                data,
                resolve,
                reject
            });
            
            this.scheduleProcess();
        });
    }
    
    /**
     * 调度批处理
     */
    scheduleProcess() {
        if (this.timer) {
            clearTimeout(this.timer);
        }
        
        this.timer = setTimeout(() => {
            this.process();
        }, this.delay);
    }
    
    /**
     * 执行批处理
     */
    async process() {
        if (this.processing || this.queue.length === 0) {
            return;
        }
        
        this.processing = true;
        
        try {
            const batch = this.queue.splice(0, this.batchSize);
            
            // 并行执行批次中的任务
            const promises = batch.map(async (item) => {
                try {
                    const result = await item.task(item.data);
                    item.resolve(result);
                } catch (error) {
                    item.reject(error);
                }
            });
            
            await Promise.allSettled(promises);
            
            // 如果还有任务，继续处理
            if (this.queue.length > 0) {
                this.scheduleProcess();
            }
        } finally {
            this.processing = false;
        }
    }
    
    /**
     * 清空队列
     */
    clear() {
        this.queue.forEach(item => {
            item.reject(new Error('Batch processor cleared'));
        });
        this.queue = [];
        
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
    }
}

/**
 * 虚拟滚动优化器
 */
class VirtualScroller {
    constructor(container, itemHeight, renderItem, bufferSize = 5) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.renderItem = renderItem;
        this.bufferSize = bufferSize;
        this.data = [];
        this.visibleItems = [];
        this.scrollTop = 0;
        this.containerHeight = 0;
        
        this.init();
    }
    
    init() {
        this.containerHeight = this.container.clientHeight;
        this.container.style.overflow = 'auto';
        
        // 创建滚动容器
        this.scrollContainer = document.createElement('div');
        this.scrollContainer.style.position = 'relative';
        this.container.appendChild(this.scrollContainer);
        
        // 绑定滚动事件
        this.container.addEventListener('scroll', throttle(() => {
            this.handleScroll();
        }, 16)); // 60fps
        
        // 监听容器大小变化
        if (window.ResizeObserver) {
            this.resizeObserver = new ResizeObserver(() => {
                this.containerHeight = this.container.clientHeight;
                this.render();
            });
            this.resizeObserver.observe(this.container);
        }
    }
    
    /**
     * 设置数据
     * @param {Array} data - 数据数组
     */
    setData(data) {
        this.data = data;
        this.render();
    }
    
    /**
     * 处理滚动事件
     */
    handleScroll() {
        this.scrollTop = this.container.scrollTop;
        this.render();
    }
    
    /**
     * 渲染可见项
     */
    render() {
        const totalHeight = this.data.length * this.itemHeight;
        const visibleCount = Math.ceil(this.containerHeight / this.itemHeight);
        const startIndex = Math.floor(this.scrollTop / this.itemHeight);
        const endIndex = Math.min(startIndex + visibleCount + this.bufferSize * 2, this.data.length);
        const actualStartIndex = Math.max(0, startIndex - this.bufferSize);
        
        // 设置总高度
        this.scrollContainer.style.height = `${totalHeight}px`;
        
        // 清空现有项
        this.scrollContainer.innerHTML = '';
        
        // 渲染可见项
        for (let i = actualStartIndex; i < endIndex; i++) {
            const item = this.data[i];
            const element = this.renderItem(item, i);
            
            element.style.position = 'absolute';
            element.style.top = `${i * this.itemHeight}px`;
            element.style.height = `${this.itemHeight}px`;
            element.style.width = '100%';
            
            this.scrollContainer.appendChild(element);
        }
    }
    
    /**
     * 销毁虚拟滚动器
     */
    destroy() {
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
        
        this.container.innerHTML = '';
    }
}

/**
 * 图片懒加载优化器
 */
class LazyImageLoader {
    constructor(options = {}) {
        this.options = {
            rootMargin: '50px',
            threshold: 0.1,
            placeholder: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB2aWV3Qm94PSIwIDAgMSAxIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiNGNUY1RjUiLz48L3N2Zz4=',
            ...options
        };
        
        this.observer = null;
        this.images = new Set();
        
        this.init();
    }
    
    init() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver(
                this.handleIntersection.bind(this),
                {
                    rootMargin: this.options.rootMargin,
                    threshold: this.options.threshold
                }
            );
        }
    }
    
    /**
     * 观察图片元素
     * @param {HTMLImageElement} img - 图片元素
     */
    observe(img) {
        if (!img || this.images.has(img)) return;
        
        this.images.add(img);
        
        // 设置占位符
        if (!img.src && this.options.placeholder) {
            img.src = this.options.placeholder;
        }
        
        if (this.observer) {
            this.observer.observe(img);
        } else {
            // 降级处理
            this.loadImage(img);
        }
    }
    
    /**
     * 处理交叉观察
     * @param {Array} entries - 观察条目
     */
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadImage(entry.target);
                this.observer.unobserve(entry.target);
            }
        });
    }
    
    /**
     * 加载图片
     * @param {HTMLImageElement} img - 图片元素
     */
    loadImage(img) {
        const dataSrc = img.dataset.src;
        if (dataSrc) {
            img.src = dataSrc;
            img.removeAttribute('data-src');
        }
        
        this.images.delete(img);
    }
    
    /**
     * 销毁懒加载器
     */
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        this.images.clear();
    }
}

// 创建全局实例
const globalCache = new MemoryCache();
const batchProcessor = new BatchProcessor();
const lazyImageLoader = new LazyImageLoader();

// 导出工具函数和类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        debounce,
        throttle,
        rafThrottle,
        MemoryCache,
        apiCache,
        BatchProcessor,
        VirtualScroller,
        LazyImageLoader,
        globalCache,
        batchProcessor,
        lazyImageLoader
    };
}