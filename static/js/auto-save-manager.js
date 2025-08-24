/**
 * 自动保存管理器
 * 实现智能自动保存功能，防止数据丢失
 */
class AutoSaveManager {
    constructor(options = {}) {
        this.options = {
            interval: 30000,        // 自动保存间隔（毫秒）
            maxRetries: 3,          // 最大重试次数
            retryDelay: 5000,       // 重试延迟（毫秒）
            enableOfflineQueue: true, // 启用离线队列
            storageKey: 'autoSave_', // 本地存储键前缀
            ...options
        };
        
        this.isEnabled = false;
        this.timer = null;
        this.saveQueue = [];
        this.retryQueue = [];
        this.isOnline = navigator.onLine;
        this.lastSaveTime = 0;
        this.saveCallbacks = new Map();
        
        this.init();
    }
    
    /**
     * 初始化自动保存管理器
     */
    init() {
        // 监听网络状态变化
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.processOfflineQueue();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
        });
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // 页面隐藏时立即保存
                this.saveImmediately();
            } else {
                // 页面显示时恢复自动保存
                this.resume();
            }
        });
        
        // 监听页面卸载事件
        window.addEventListener('beforeunload', () => {
            this.saveImmediately();
        });
        
        // 从本地存储恢复未保存的数据
        this.restoreFromStorage();
    }
    
    /**
     * 启用自动保存
     * @param {Function} saveFunction - 保存函数
     * @param {Function} changeDetector - 变化检测函数
     * @param {string} dataKey - 数据键
     */
    enable(saveFunction, changeDetector, dataKey = 'default') {
        if (!saveFunction || typeof saveFunction !== 'function') {
            throw new Error('Save function is required');
        }
        
        this.saveCallbacks.set(dataKey, {
            save: saveFunction,
            detect: changeDetector || (() => true),
            lastData: null,
            hasChanges: false
        });
        
        this.isEnabled = true;
        this.startTimer();
        
        console.log(`AutoSave enabled for ${dataKey}`);
    }
    
    /**
     * 禁用自动保存
     * @param {string} dataKey - 数据键
     */
    disable(dataKey = null) {
        if (dataKey) {
            this.saveCallbacks.delete(dataKey);
            if (this.saveCallbacks.size === 0) {
                this.isEnabled = false;
                this.stopTimer();
            }
        } else {
            this.isEnabled = false;
            this.saveCallbacks.clear();
            this.stopTimer();
        }
        
        console.log(`AutoSave disabled${dataKey ? ` for ${dataKey}` : ''}`);
    }
    
    /**
     * 暂停自动保存
     */
    pause() {
        this.stopTimer();
    }
    
    /**
     * 恢复自动保存
     */
    resume() {
        if (this.isEnabled && this.saveCallbacks.size > 0) {
            this.startTimer();
        }
    }
    
    /**
     * 启动定时器
     */
    startTimer() {
        this.stopTimer();
        
        this.timer = setInterval(() => {
            this.checkAndSave();
        }, this.options.interval);
    }
    
    /**
     * 停止定时器
     */
    stopTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }
    
    /**
     * 检查并保存
     */
    async checkAndSave() {
        if (!this.isEnabled || this.saveCallbacks.size === 0) {
            return;
        }
        
        const savePromises = [];
        
        for (const [dataKey, callback] of this.saveCallbacks) {
            try {
                // 检测是否有变化
                const hasChanges = callback.detect ? callback.detect() : true;
                
                if (hasChanges) {
                    console.log(`Auto-saving ${dataKey}...`);
                    savePromises.push(this.performSave(dataKey, callback.save));
                }
            } catch (error) {
                console.error(`Error checking changes for ${dataKey}:`, error);
            }
        }
        
        if (savePromises.length > 0) {
            try {
                await Promise.allSettled(savePromises);
                this.lastSaveTime = Date.now();
            } catch (error) {
                console.error('Auto-save error:', error);
            }
        }
    }
    
    /**
     * 执行保存操作
     * @param {string} dataKey - 数据键
     * @param {Function} saveFunction - 保存函数
     * @param {number} retryCount - 重试次数
     */
    async performSave(dataKey, saveFunction, retryCount = 0) {
        try {
            // 如果离线且启用了离线队列，添加到队列
            if (!this.isOnline && this.options.enableOfflineQueue) {
                this.addToOfflineQueue(dataKey, saveFunction);
                return;
            }
            
            const result = await saveFunction();
            
            if (result && result.success) {
                // 保存成功，清除本地存储
                this.clearFromStorage(dataKey);
                
                // 触发保存成功事件
                this.triggerEvent('autoSaveSuccess', {
                    dataKey,
                    result,
                    timestamp: Date.now()
                });
                
                console.log(`Auto-save successful for ${dataKey}`);
            } else {
                throw new Error(result?.error?.message || 'Save failed');
            }
        } catch (error) {
            console.error(`Auto-save failed for ${dataKey}:`, error);
            
            // 如果还有重试次数，添加到重试队列
            if (retryCount < this.options.maxRetries) {
                this.addToRetryQueue(dataKey, saveFunction, retryCount + 1);
            } else {
                // 保存到本地存储作为备份
                this.saveToStorage(dataKey);
                
                // 触发保存失败事件
                this.triggerEvent('autoSaveError', {
                    dataKey,
                    error,
                    retryCount,
                    timestamp: Date.now()
                });
            }
        }
    }
    
    /**
     * 立即保存所有数据
     */
    async saveImmediately() {
        if (!this.isEnabled || this.saveCallbacks.size === 0) {
            return;
        }
        
        const savePromises = [];
        
        for (const [dataKey, callback] of this.saveCallbacks) {
            savePromises.push(this.performSave(dataKey, callback.save));
        }
        
        try {
            await Promise.allSettled(savePromises);
            console.log('Immediate save completed');
        } catch (error) {
            console.error('Immediate save error:', error);
        }
    }
    
    /**
     * 添加到离线队列
     * @param {string} dataKey - 数据键
     * @param {Function} saveFunction - 保存函数
     */
    addToOfflineQueue(dataKey, saveFunction) {
        // 避免重复添加
        const existing = this.saveQueue.find(item => item.dataKey === dataKey);
        if (existing) {
            existing.saveFunction = saveFunction;
            existing.timestamp = Date.now();
        } else {
            this.saveQueue.push({
                dataKey,
                saveFunction,
                timestamp: Date.now()
            });
        }
        
        // 保存到本地存储
        this.saveToStorage(dataKey);
        
        console.log(`Added ${dataKey} to offline queue`);
    }
    
    /**
     * 添加到重试队列
     * @param {string} dataKey - 数据键
     * @param {Function} saveFunction - 保存函数
     * @param {number} retryCount - 重试次数
     */
    addToRetryQueue(dataKey, saveFunction, retryCount) {
        setTimeout(() => {
            this.performSave(dataKey, saveFunction, retryCount);
        }, this.options.retryDelay * retryCount);
        
        console.log(`Scheduled retry ${retryCount} for ${dataKey}`);
    }
    
    /**
     * 处理离线队列
     */
    async processOfflineQueue() {
        if (this.saveQueue.length === 0) {
            return;
        }
        
        console.log(`Processing ${this.saveQueue.length} offline saves...`);
        
        const queue = [...this.saveQueue];
        this.saveQueue = [];
        
        for (const item of queue) {
            try {
                await this.performSave(item.dataKey, item.saveFunction);
            } catch (error) {
                console.error(`Failed to process offline save for ${item.dataKey}:`, error);
                // 重新添加到队列
                this.saveQueue.push(item);
            }
        }
    }
    
    /**
     * 保存到本地存储
     * @param {string} dataKey - 数据键
     */
    saveToStorage(dataKey) {
        if (!this.options.enableOfflineQueue) return;
        
        try {
            const callback = this.saveCallbacks.get(dataKey);
            if (callback && callback.detect) {
                // 获取当前数据
                const currentData = this.getCurrentData(dataKey);
                if (currentData) {
                    const storageKey = this.options.storageKey + dataKey;
                    localStorage.setItem(storageKey, JSON.stringify({
                        data: currentData,
                        timestamp: Date.now()
                    }));
                }
            }
        } catch (error) {
            console.error(`Failed to save ${dataKey} to storage:`, error);
        }
    }
    
    /**
     * 从本地存储清除
     * @param {string} dataKey - 数据键
     */
    clearFromStorage(dataKey) {
        try {
            const storageKey = this.options.storageKey + dataKey;
            localStorage.removeItem(storageKey);
        } catch (error) {
            console.error(`Failed to clear ${dataKey} from storage:`, error);
        }
    }
    
    /**
     * 从本地存储恢复数据
     */
    restoreFromStorage() {
        if (!this.options.enableOfflineQueue) return;
        
        try {
            const keys = Object.keys(localStorage);
            const autoSaveKeys = keys.filter(key => key.startsWith(this.options.storageKey));
            
            for (const storageKey of autoSaveKeys) {
                const dataKey = storageKey.replace(this.options.storageKey, '');
                const stored = localStorage.getItem(storageKey);
                
                if (stored) {
                    const { data, timestamp } = JSON.parse(stored);
                    
                    // 检查数据是否过期（24小时）
                    if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
                        this.triggerEvent('dataRestored', {
                            dataKey,
                            data,
                            timestamp
                        });
                    } else {
                        // 清除过期数据
                        localStorage.removeItem(storageKey);
                    }
                }
            }
        } catch (error) {
            console.error('Failed to restore from storage:', error);
        }
    }
    
    /**
     * 获取当前数据（需要子类实现或通过回调提供）
     * @param {string} dataKey - 数据键
     */
    getCurrentData(dataKey) {
        // 这个方法需要根据具体应用场景实现
        // 可以通过事件或回调来获取当前数据
        const event = new CustomEvent('autoSave:getCurrentData', {
            detail: { dataKey }
        });
        document.dispatchEvent(event);
        
        return event.detail.data || null;
    }
    
    /**
     * 触发自定义事件
     * @param {string} eventName - 事件名称
     * @param {Object} detail - 事件详情
     */
    triggerEvent(eventName, detail) {
        const event = new CustomEvent(`autoSave:${eventName}`, {
            detail,
            bubbles: true
        });
        document.dispatchEvent(event);
    }
    
    /**
     * 获取状态信息
     */
    getStatus() {
        return {
            isEnabled: this.isEnabled,
            isOnline: this.isOnline,
            lastSaveTime: this.lastSaveTime,
            queueSize: this.saveQueue.length,
            activeCallbacks: this.saveCallbacks.size,
            interval: this.options.interval
        };
    }
    
    /**
     * 设置保存间隔
     * @param {number} interval - 新的间隔时间（毫秒）
     */
    setInterval(interval) {
        this.options.interval = interval;
        
        if (this.isEnabled) {
            this.startTimer();
        }
    }
    
    /**
     * 销毁自动保存管理器
     */
    destroy() {
        this.disable();
        this.saveQueue = [];
        this.retryQueue = [];
        
        // 移除事件监听器
        window.removeEventListener('online', this.processOfflineQueue);
        window.removeEventListener('offline', () => {});
        document.removeEventListener('visibilitychange', () => {});
        window.removeEventListener('beforeunload', () => {});
        
        console.log('AutoSaveManager destroyed');
    }
}

// 创建全局自动保存管理器实例
const autoSaveManager = new AutoSaveManager();

// 导出类和实例
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AutoSaveManager, autoSaveManager };
}