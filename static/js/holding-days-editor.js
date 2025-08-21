/**
 * 持仓天数编辑器组件
 * 实现需求1：支持后端API的可编辑持仓天数
 */
class HoldingDaysEditor {
    constructor(stockCode, currentDays, options = {}) {
        this.stockCode = stockCode;
        this.currentDays = currentDays;
        this.originalDays = currentDays;
        this.isEditing = false;
        this.isLoading = false;
        
        // 配置选项
        this.options = {
            minDays: 1,
            maxDays: 9999,
            autoSave: true,
            showLoadingState: true,
            validateOnInput: true,
            ...options
        };
        
        // DOM元素引用
        this.containerElement = null;
        this.displayElement = null;
        this.inputElement = null;
        this.saveButton = null;
        this.cancelButton = null;
        this.errorElement = null;
        
        // 事件处理器绑定
        this.handleInputKeydown = this.handleInputKeydown.bind(this);
        this.handleInputBlur = this.handleInputBlur.bind(this);
        this.handleInputInput = this.handleInputInput.bind(this);
        this.handleSaveClick = this.handleSaveClick.bind(this);
        this.handleCancelClick = this.handleCancelClick.bind(this);
        this.handleDisplayClick = this.handleDisplayClick.bind(this);
    }
    
    /**
     * 初始化编辑器并绑定到DOM元素
     * @param {HTMLElement|string} container - 容器元素或选择器
     */
    init(container) {
        if (typeof container === 'string') {
            this.containerElement = document.querySelector(container);
        } else {
            this.containerElement = container;
        }
        
        if (!this.containerElement) {
            console.error('HoldingDaysEditor: Container element not found');
            return false;
        }
        
        this.render();
        this.bindEvents();
        return true;
    }
    
    /**
     * 渲染编辑器HTML结构
     */
    render() {
        const html = `
            <div class="holding-days-editor" data-stock-code="${this.stockCode}">
                <div class="display-mode">
                    <span class="days-display fw-bold" title="点击编辑持仓天数">${this.currentDays}</span>
                    <small class="text-muted d-block">天数</small>
                </div>
                <div class="edit-mode d-none">
                    <div class="input-group input-group-sm">
                        <input type="number" 
                               class="form-control days-input" 
                               value="${this.currentDays}"
                               min="${this.options.minDays}"
                               max="${this.options.maxDays}"
                               placeholder="天数">
                        <button class="btn btn-success btn-sm save-btn" type="button" title="保存">
                            <i class="bi bi-check"></i>
                        </button>
                        <button class="btn btn-secondary btn-sm cancel-btn" type="button" title="取消">
                            <i class="bi bi-x"></i>
                        </button>
                    </div>
                    <div class="error-message text-danger small mt-1 d-none"></div>
                    <div class="loading-indicator text-muted small mt-1 d-none">
                        <span class="spinner-border spinner-border-sm me-1"></span>
                        保存中...
                    </div>
                </div>
            </div>
        `;
        
        this.containerElement.innerHTML = html;
        this.cacheElements();
    }
    
    /**
     * 缓存DOM元素引用
     */
    cacheElements() {
        const container = this.containerElement.querySelector('.holding-days-editor');
        this.displayElement = container.querySelector('.days-display');
        this.inputElement = container.querySelector('.days-input');
        this.saveButton = container.querySelector('.save-btn');
        this.cancelButton = container.querySelector('.cancel-btn');
        this.errorElement = container.querySelector('.error-message');
        this.loadingElement = container.querySelector('.loading-indicator');
        this.displayMode = container.querySelector('.display-mode');
        this.editMode = container.querySelector('.edit-mode');
    }
    
    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 显示模式点击事件
        this.displayElement.addEventListener('click', this.handleDisplayClick);
        
        // 输入框事件
        this.inputElement.addEventListener('keydown', this.handleInputKeydown);
        this.inputElement.addEventListener('blur', this.handleInputBlur);
        
        if (this.options.validateOnInput) {
            this.inputElement.addEventListener('input', this.handleInputInput);
        }
        
        // 按钮事件
        this.saveButton.addEventListener('click', this.handleSaveClick);
        this.cancelButton.addEventListener('click', this.handleCancelClick);
    }
    
    /**
     * 进入编辑模式
     */
    enterEditMode() {
        if (this.isEditing || this.isLoading) return;
        
        this.isEditing = true;
        this.originalDays = this.currentDays;
        
        // 切换显示模式
        this.displayMode.classList.add('d-none');
        this.editMode.classList.remove('d-none');
        
        // 聚焦输入框并选中文本
        this.inputElement.focus();
        this.inputElement.select();
        
        // 清除之前的错误
        this.clearError();
        
        // 触发事件
        this.triggerEvent('editStart', {
            stockCode: this.stockCode,
            originalDays: this.originalDays
        });
    }
    
    /**
     * 退出编辑模式
     */
    exitEditMode() {
        if (!this.isEditing) return;
        
        this.isEditing = false;
        
        // 切换显示模式
        this.editMode.classList.add('d-none');
        this.displayMode.classList.remove('d-none');
        
        // 清除错误和加载状态
        this.clearError();
        this.hideLoading();
        
        // 触发事件
        this.triggerEvent('editEnd', {
            stockCode: this.stockCode,
            currentDays: this.currentDays
        });
    }
    
    /**
     * 保存更改
     */
    async saveChanges(newDays = null) {
        if (this.isLoading) return false;
        
        const daysToSave = newDays !== null ? newDays : parseInt(this.inputElement.value);
        
        // 验证输入
        const validation = this.validateInput(daysToSave);
        if (!validation.isValid) {
            this.showError(validation.message);
            return false;
        }
        
        // 检查是否有变化
        if (daysToSave === this.originalDays) {
            this.exitEditMode();
            return true;
        }
        
        try {
            this.showLoading();
            
            // 调用API更新持仓天数
            const response = await apiClient.updateHoldingDays(this.stockCode, daysToSave);
            
            if (response && response.success) {
                // 更新成功
                this.currentDays = daysToSave;
                this.updateDisplay(daysToSave);
                this.exitEditMode();
                
                // 显示成功消息
                if (typeof showMessage === 'function') {
                    showMessage(`${this.stockCode} 持仓天数已更新为 ${daysToSave} 天`, 'success');
                }
                
                // 触发保存成功事件
                this.triggerEvent('saveSuccess', {
                    stockCode: this.stockCode,
                    oldDays: this.originalDays,
                    newDays: daysToSave,
                    response: response
                });
                
                return true;
            } else {
                throw new Error(response?.error?.message || '保存失败');
            }
        } catch (error) {
            console.error('Save holding days error:', error);
            
            let errorMessage = '保存失败';
            if (error.code === 'VALIDATION_ERROR') {
                errorMessage = '数据验证失败，请检查输入';
            } else if (error.code === 'HOLDING_NOT_FOUND') {
                errorMessage = '未找到对应的持仓记录';
            } else if (error.code === 'NETWORK_ERROR') {
                errorMessage = '网络连接失败，请重试';
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            this.showError(errorMessage);
            
            // 触发保存失败事件
            this.triggerEvent('saveError', {
                stockCode: this.stockCode,
                error: error,
                message: errorMessage
            });
            
            return false;
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * 取消编辑
     */
    cancelEdit() {
        if (this.isLoading) return;
        
        // 恢复原始值
        this.inputElement.value = this.originalDays;
        this.exitEditMode();
        
        // 触发取消事件
        this.triggerEvent('editCancel', {
            stockCode: this.stockCode,
            originalDays: this.originalDays
        });
    }
    
    /**
     * 验证输入值
     * @param {number} days - 要验证的天数
     * @returns {Object} 验证结果
     */
    validateInput(days) {
        // 检查是否为数字
        if (isNaN(days) || days === null || days === undefined) {
            return {
                isValid: false,
                message: '请输入有效的数字'
            };
        }
        
        // 检查是否为整数
        if (!Number.isInteger(days)) {
            return {
                isValid: false,
                message: '持仓天数必须是整数'
            };
        }
        
        // 检查范围
        if (days < this.options.minDays) {
            return {
                isValid: false,
                message: `持仓天数不能小于 ${this.options.minDays} 天`
            };
        }
        
        if (days > this.options.maxDays) {
            return {
                isValid: false,
                message: `持仓天数不能大于 ${this.options.maxDays} 天`
            };
        }
        
        return {
            isValid: true,
            message: ''
        };
    }
    
    /**
     * 更新显示值
     * @param {number} days - 新的天数值
     */
    updateDisplay(days) {
        this.displayElement.textContent = days;
        this.inputElement.value = days;
    }
    
    /**
     * 显示错误消息
     * @param {string} message - 错误消息
     */
    showError(message) {
        this.errorElement.textContent = message;
        this.errorElement.classList.remove('d-none');
        this.inputElement.classList.add('is-invalid');
    }
    
    /**
     * 清除错误消息
     */
    clearError() {
        this.errorElement.classList.add('d-none');
        this.inputElement.classList.remove('is-invalid');
    }
    
    /**
     * 显示加载状态
     */
    showLoading() {
        if (!this.options.showLoadingState) return;
        
        this.isLoading = true;
        this.loadingElement.classList.remove('d-none');
        this.saveButton.disabled = true;
        this.cancelButton.disabled = true;
        this.inputElement.disabled = true;
    }
    
    /**
     * 隐藏加载状态
     */
    hideLoading() {
        this.isLoading = false;
        this.loadingElement.classList.add('d-none');
        this.saveButton.disabled = false;
        this.cancelButton.disabled = false;
        this.inputElement.disabled = false;
    }
    
    /**
     * 事件处理器：显示元素点击
     */
    handleDisplayClick(event) {
        event.preventDefault();
        event.stopPropagation();
        this.enterEditMode();
    }
    
    /**
     * 事件处理器：输入框键盘事件
     */
    handleInputKeydown(event) {
        switch (event.key) {
            case 'Enter':
                event.preventDefault();
                this.saveChanges();
                break;
            case 'Escape':
                event.preventDefault();
                this.cancelEdit();
                break;
        }
    }
    
    /**
     * 事件处理器：输入框失焦
     */
    handleInputBlur(event) {
        // 延迟处理，避免与按钮点击冲突
        setTimeout(() => {
            if (this.isEditing && !this.isLoading) {
                if (this.options.autoSave) {
                    this.saveChanges();
                } else {
                    this.cancelEdit();
                }
            }
        }, 150);
    }
    
    /**
     * 事件处理器：输入框输入事件
     */
    handleInputInput(event) {
        if (this.options.validateOnInput) {
            const value = parseInt(event.target.value);
            const validation = this.validateInput(value);
            
            if (!validation.isValid && event.target.value !== '') {
                this.showError(validation.message);
            } else {
                this.clearError();
            }
        }
    }
    
    /**
     * 事件处理器：保存按钮点击
     */
    handleSaveClick(event) {
        event.preventDefault();
        event.stopPropagation();
        this.saveChanges();
    }
    
    /**
     * 事件处理器：取消按钮点击
     */
    handleCancelClick(event) {
        event.preventDefault();
        event.stopPropagation();
        this.cancelEdit();
    }
    
    /**
     * 触发自定义事件
     * @param {string} eventName - 事件名称
     * @param {Object} detail - 事件详情
     */
    triggerEvent(eventName, detail) {
        const event = new CustomEvent(`holdingDaysEditor:${eventName}`, {
            detail: detail,
            bubbles: true
        });
        
        if (this.containerElement) {
            this.containerElement.dispatchEvent(event);
        }
    }
    
    /**
     * 销毁编辑器
     */
    destroy() {
        // 移除事件监听器
        if (this.displayElement) {
            this.displayElement.removeEventListener('click', this.handleDisplayClick);
        }
        
        if (this.inputElement) {
            this.inputElement.removeEventListener('keydown', this.handleInputKeydown);
            this.inputElement.removeEventListener('blur', this.handleInputBlur);
            this.inputElement.removeEventListener('input', this.handleInputInput);
        }
        
        if (this.saveButton) {
            this.saveButton.removeEventListener('click', this.handleSaveClick);
        }
        
        if (this.cancelButton) {
            this.cancelButton.removeEventListener('click', this.handleCancelClick);
        }
        
        // 清空容器
        if (this.containerElement) {
            this.containerElement.innerHTML = '';
        }
        
        // 清空引用
        this.containerElement = null;
        this.displayElement = null;
        this.inputElement = null;
        this.saveButton = null;
        this.cancelButton = null;
        this.errorElement = null;
        this.loadingElement = null;
        this.displayMode = null;
        this.editMode = null;
    }
    
    /**
     * 获取当前状态
     * @returns {Object} 当前状态信息
     */
    getState() {
        return {
            stockCode: this.stockCode,
            currentDays: this.currentDays,
            originalDays: this.originalDays,
            isEditing: this.isEditing,
            isLoading: this.isLoading
        };
    }
    
    /**
     * 设置新的天数值（不触发保存）
     * @param {number} days - 新的天数值
     */
    setValue(days) {
        const validation = this.validateInput(days);
        if (validation.isValid) {
            this.currentDays = days;
            this.updateDisplay(days);
            return true;
        }
        return false;
    }
    
    /**
     * 获取当前天数值
     * @returns {number} 当前天数
     */
    getValue() {
        return this.currentDays;
    }
    
    /**
     * 启用/禁用编辑器
     * @param {boolean} enabled - 是否启用
     */
    setEnabled(enabled) {
        if (enabled) {
            this.displayElement.style.pointerEvents = '';
            this.displayElement.style.opacity = '';
        } else {
            this.displayElement.style.pointerEvents = 'none';
            this.displayElement.style.opacity = '0.6';
            
            if (this.isEditing) {
                this.cancelEdit();
            }
        }
    }
}

/**
 * 持仓天数编辑器管理器
 * 用于管理页面中的多个编辑器实例
 */
class HoldingDaysEditorManager {
    constructor() {
        this.editors = new Map();
        this.globalOptions = {
            minDays: 1,
            maxDays: 9999,
            autoSave: true,
            showLoadingState: true,
            validateOnInput: true
        };
    }
    
    /**
     * 创建编辑器实例
     * @param {string} stockCode - 股票代码
     * @param {number} currentDays - 当前天数
     * @param {HTMLElement|string} container - 容器元素
     * @param {Object} options - 选项
     * @returns {HoldingDaysEditor} 编辑器实例
     */
    createEditor(stockCode, currentDays, container, options = {}) {
        const editorOptions = { ...this.globalOptions, ...options };
        const editor = new HoldingDaysEditor(stockCode, currentDays, editorOptions);
        
        if (editor.init(container)) {
            this.editors.set(stockCode, editor);
            
            // 监听编辑器事件
            this.bindEditorEvents(editor);
            
            return editor;
        }
        
        return null;
    }
    
    /**
     * 获取编辑器实例
     * @param {string} stockCode - 股票代码
     * @returns {HoldingDaysEditor|null} 编辑器实例
     */
    getEditor(stockCode) {
        return this.editors.get(stockCode) || null;
    }
    
    /**
     * 销毁编辑器实例
     * @param {string} stockCode - 股票代码
     */
    destroyEditor(stockCode) {
        const editor = this.editors.get(stockCode);
        if (editor) {
            editor.destroy();
            this.editors.delete(stockCode);
        }
    }
    
    /**
     * 销毁所有编辑器实例
     */
    destroyAll() {
        this.editors.forEach((editor, stockCode) => {
            editor.destroy();
        });
        this.editors.clear();
    }
    
    /**
     * 绑定编辑器事件
     * @param {HoldingDaysEditor} editor - 编辑器实例
     */
    bindEditorEvents(editor) {
        if (!editor.containerElement) return;
        
        // 监听保存成功事件
        editor.containerElement.addEventListener('holdingDaysEditor:saveSuccess', (event) => {
            console.log('Holding days updated:', event.detail);
            
            // 触发全局事件，通知其他组件更新
            document.dispatchEvent(new CustomEvent('holdingDaysUpdated', {
                detail: event.detail
            }));
        });
        
        // 监听保存失败事件
        editor.containerElement.addEventListener('holdingDaysEditor:saveError', (event) => {
            console.error('Holding days update failed:', event.detail);
        });
    }
    
    /**
     * 设置全局选项
     * @param {Object} options - 全局选项
     */
    setGlobalOptions(options) {
        this.globalOptions = { ...this.globalOptions, ...options };
    }
    
    /**
     * 批量更新持仓天数
     * @param {Array} updates - 更新数据数组 [{stockCode, days}, ...]
     * @returns {Promise<Array>} 更新结果数组
     */
    async batchUpdate(updates) {
        const results = [];
        
        for (const update of updates) {
            const editor = this.getEditor(update.stockCode);
            if (editor) {
                try {
                    const success = await editor.saveChanges(update.days);
                    results.push({
                        stockCode: update.stockCode,
                        success: success,
                        days: update.days
                    });
                } catch (error) {
                    results.push({
                        stockCode: update.stockCode,
                        success: false,
                        error: error.message
                    });
                }
            }
        }
        
        return results;
    }
}

// 创建全局管理器实例
const holdingDaysEditorManager = new HoldingDaysEditorManager();

// 导出类和实例
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        HoldingDaysEditor, 
        HoldingDaysEditorManager, 
        holdingDaysEditorManager 
    };
}