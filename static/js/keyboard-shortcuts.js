/**
 * 键盘快捷键管理器
 * 提供全局和局部键盘快捷键支持
 */
class KeyboardShortcutManager {
    constructor() {
        this.shortcuts = new Map();
        this.contexts = new Map();
        this.currentContext = 'global';
        this.isEnabled = true;
        this.modifierKeys = {
            ctrl: false,
            alt: false,
            shift: false,
            meta: false
        };
        
        this.init();
    }
    
    /**
     * 初始化快捷键管理器
     */
    init() {
        this.bindEvents();
        this.registerDefaultShortcuts();
        this.createHelpModal();
    }
    
    /**
     * 绑定事件监听器
     */
    bindEvents() {
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
        document.addEventListener('keyup', this.handleKeyUp.bind(this));
        
        // 监听焦点变化以切换上下文
        document.addEventListener('focusin', this.handleFocusChange.bind(this));
        document.addEventListener('focusout', this.handleFocusChange.bind(this));
        
        // 防止在输入框中触发快捷键
        document.addEventListener('keydown', (e) => {
            const target = e.target;
            const isInput = target.tagName === 'INPUT' || 
                           target.tagName === 'TEXTAREA' || 
                           target.contentEditable === 'true';
            
            if (isInput && !e.ctrlKey && !e.metaKey && !e.altKey) {
                return; // 在输入框中不处理普通按键
            }
        }, true);
    }
    
    /**
     * 处理按键按下事件
     * @param {KeyboardEvent} event - 键盘事件
     */
    handleKeyDown(event) {
        if (!this.isEnabled) return;
        
        // 更新修饰键状态
        this.updateModifierKeys(event);
        
        // 生成快捷键字符串
        const shortcutKey = this.generateShortcutKey(event);
        
        // 查找匹配的快捷键
        const shortcut = this.findShortcut(shortcutKey);
        
        if (shortcut) {
            // 检查上下文
            if (this.isShortcutAvailable(shortcut)) {
                event.preventDefault();
                event.stopPropagation();
                
                try {
                    shortcut.handler(event);
                    
                    // 触发快捷键执行事件
                    this.triggerEvent('shortcutExecuted', {
                        key: shortcutKey,
                        shortcut: shortcut,
                        event: event
                    });
                } catch (error) {
                    console.error('Shortcut handler error:', error);
                }
            }
        }
    }
    
    /**
     * 处理按键释放事件
     * @param {KeyboardEvent} event - 键盘事件
     */
    handleKeyUp(event) {
        this.updateModifierKeys(event);
    }
    
    /**
     * 处理焦点变化
     * @param {FocusEvent} event - 焦点事件
     */
    handleFocusChange(event) {
        const target = event.target;
        
        // 根据焦点元素确定上下文
        if (target.closest('#reviewModal')) {
            this.setContext('review');
        } else if (target.closest('.modal')) {
            this.setContext('modal');
        } else if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
            this.setContext('input');
        } else {
            this.setContext('global');
        }
    }
    
    /**
     * 更新修饰键状态
     * @param {KeyboardEvent} event - 键盘事件
     */
    updateModifierKeys(event) {
        this.modifierKeys.ctrl = event.ctrlKey;
        this.modifierKeys.alt = event.altKey;
        this.modifierKeys.shift = event.shiftKey;
        this.modifierKeys.meta = event.metaKey;
    }
    
    /**
     * 生成快捷键字符串
     * @param {KeyboardEvent} event - 键盘事件
     * @returns {string} 快捷键字符串
     */
    generateShortcutKey(event) {
        const parts = [];
        
        if (event.ctrlKey || event.metaKey) parts.push('ctrl');
        if (event.altKey) parts.push('alt');
        if (event.shiftKey) parts.push('shift');
        
        // 处理特殊键
        let key = event.key.toLowerCase();
        
        // 标准化一些键名
        const keyMap = {
            ' ': 'space',
            'arrowup': 'up',
            'arrowdown': 'down',
            'arrowleft': 'left',
            'arrowright': 'right',
            'escape': 'esc'
        };
        
        key = keyMap[key] || key;
        parts.push(key);
        
        return parts.join('+');
    }
    
    /**
     * 查找快捷键
     * @param {string} shortcutKey - 快捷键字符串
     * @returns {Object|null} 快捷键对象
     */
    findShortcut(shortcutKey) {
        // 首先在当前上下文中查找
        const contextShortcuts = this.contexts.get(this.currentContext);
        if (contextShortcuts && contextShortcuts.has(shortcutKey)) {
            return contextShortcuts.get(shortcutKey);
        }
        
        // 然后在全局快捷键中查找
        if (this.currentContext !== 'global') {
            const globalShortcuts = this.contexts.get('global');
            if (globalShortcuts && globalShortcuts.has(shortcutKey)) {
                return globalShortcuts.get(shortcutKey);
            }
        }
        
        return null;
    }
    
    /**
     * 检查快捷键是否可用
     * @param {Object} shortcut - 快捷键对象
     * @returns {boolean} 是否可用
     */
    isShortcutAvailable(shortcut) {
        // 检查启用状态
        if (!shortcut.enabled) return false;
        
        // 检查条件函数
        if (shortcut.condition && typeof shortcut.condition === 'function') {
            return shortcut.condition();
        }
        
        return true;
    }
    
    /**
     * 注册快捷键
     * @param {string} key - 快捷键字符串
     * @param {Function} handler - 处理函数
     * @param {Object} options - 选项
     */
    register(key, handler, options = {}) {
        const {
            context = 'global',
            description = '',
            enabled = true,
            condition = null,
            preventDefault = true
        } = options;
        
        const shortcut = {
            key,
            handler,
            description,
            enabled,
            condition,
            preventDefault,
            context
        };
        
        // 确保上下文存在
        if (!this.contexts.has(context)) {
            this.contexts.set(context, new Map());
        }
        
        // 注册快捷键
        this.contexts.get(context).set(key, shortcut);
        
        console.log(`Registered shortcut: ${key} in context: ${context}`);
    }
    
    /**
     * 注销快捷键
     * @param {string} key - 快捷键字符串
     * @param {string} context - 上下文
     */
    unregister(key, context = 'global') {
        const contextShortcuts = this.contexts.get(context);
        if (contextShortcuts) {
            contextShortcuts.delete(key);
        }
    }
    
    /**
     * 设置当前上下文
     * @param {string} context - 上下文名称
     */
    setContext(context) {
        if (this.currentContext !== context) {
            const oldContext = this.currentContext;
            this.currentContext = context;
            
            this.triggerEvent('contextChanged', {
                oldContext,
                newContext: context
            });
        }
    }
    
    /**
     * 启用/禁用快捷键
     * @param {boolean} enabled - 是否启用
     */
    setEnabled(enabled) {
        this.isEnabled = enabled;
    }
    
    /**
     * 启用/禁用特定快捷键
     * @param {string} key - 快捷键字符串
     * @param {boolean} enabled - 是否启用
     * @param {string} context - 上下文
     */
    setShortcutEnabled(key, enabled, context = 'global') {
        const contextShortcuts = this.contexts.get(context);
        if (contextShortcuts && contextShortcuts.has(key)) {
            contextShortcuts.get(key).enabled = enabled;
        }
    }
    
    /**
     * 注册默认快捷键
     */
    registerDefaultShortcuts() {
        // 全局快捷键
        this.register('ctrl+s', (e) => {
            // 保存当前页面数据
            if (typeof reviewSaveManager !== 'undefined' && reviewSaveManager) {
                reviewSaveManager.saveReview();
            }
        }, {
            description: '保存当前数据',
            context: 'global'
        });
        
        this.register('ctrl+shift+s', (e) => {
            // 强制保存
            if (typeof reviewSaveManager !== 'undefined' && reviewSaveManager) {
                reviewSaveManager.forceSave();
            }
        }, {
            description: '强制保存',
            context: 'global'
        });
        
        this.register('f1', (e) => {
            this.showHelp();
        }, {
            description: '显示帮助',
            context: 'global'
        });
        
        this.register('ctrl+/', (e) => {
            this.showHelp();
        }, {
            description: '显示快捷键帮助',
            context: 'global'
        });
        
        this.register('esc', (e) => {
            // 关闭模态框或取消当前操作
            const modal = document.querySelector('.modal.show');
            if (modal) {
                const closeBtn = modal.querySelector('.btn-close, [data-bs-dismiss="modal"]');
                if (closeBtn) {
                    closeBtn.click();
                }
            }
        }, {
            description: '关闭模态框/取消操作',
            context: 'global'
        });
        
        // 复盘页面快捷键
        this.register('ctrl+n', (e) => {
            // 新建复盘
            const newReviewBtn = document.querySelector('[onclick*="openReviewModal"]');
            if (newReviewBtn) {
                newReviewBtn.click();
            }
        }, {
            description: '新建复盘',
            context: 'global'
        });
        
        this.register('ctrl+r', (e) => {
            // 刷新数据
            if (typeof loadReviews === 'function') {
                loadReviews();
            }
        }, {
            description: '刷新复盘数据',
            context: 'global'
        });
        
        // 复盘模态框快捷键
        this.register('ctrl+enter', (e) => {
            // 快速保存并关闭
            if (typeof reviewSaveManager !== 'undefined' && reviewSaveManager) {
                reviewSaveManager.saveReview().then(() => {
                    const modal = document.getElementById('reviewModal');
                    if (modal) {
                        const closeBtn = modal.querySelector('.btn-close');
                        if (closeBtn) {
                            closeBtn.click();
                        }
                    }
                });
            }
        }, {
            description: '保存并关闭',
            context: 'review'
        });
        
        this.register('alt+1', (e) => {
            this.toggleScoreItem('price-up-score');
        }, {
            description: '切换价格上涨评分',
            context: 'review'
        });
        
        this.register('alt+2', (e) => {
            this.toggleScoreItem('bbi-score');
        }, {
            description: '切换BBI评分',
            context: 'review'
        });
        
        this.register('alt+3', (e) => {
            this.toggleScoreItem('volume-score');
        }, {
            description: '切换成交量评分',
            context: 'review'
        });
        
        this.register('alt+4', (e) => {
            this.toggleScoreItem('trend-score');
        }, {
            description: '切换趋势评分',
            context: 'review'
        });
        
        this.register('alt+5', (e) => {
            this.toggleScoreItem('j-score');
        }, {
            description: '切换J值评分',
            context: 'review'
        });
        
        this.register('tab', (e) => {
            // 在复盘模态框中优化Tab导航
            this.handleTabNavigation(e);
        }, {
            description: 'Tab导航',
            context: 'review',
            preventDefault: false
        });
        
        // 持仓天数编辑快捷键
        this.register('f2', (e) => {
            // 编辑当前选中的持仓天数
            const activeElement = document.activeElement;
            const holdingDaysContainer = activeElement.closest('.holding-days-editor');
            if (holdingDaysContainer) {
                const displayElement = holdingDaysContainer.querySelector('.days-display');
                if (displayElement) {
                    displayElement.click();
                }
            }
        }, {
            description: '编辑持仓天数',
            context: 'global'
        });
        
        // 导航快捷键
        this.register('ctrl+1', (e) => {
            this.navigateToPage('/dashboard');
        }, {
            description: '跳转到仪表板',
            context: 'global'
        });
        
        this.register('ctrl+2', (e) => {
            this.navigateToPage('/trading_records');
        }, {
            description: '跳转到交易记录',
            context: 'global'
        });
        
        this.register('ctrl+3', (e) => {
            this.navigateToPage('/review');
        }, {
            description: '跳转到复盘分析',
            context: 'global'
        });
        
        this.register('ctrl+4', (e) => {
            this.navigateToPage('/analytics');
        }, {
            description: '跳转到数据分析',
            context: 'global'
        });
    }
    
    /**
     * 切换评分项
     * @param {string} scoreId - 评分项ID
     */
    toggleScoreItem(scoreId) {
        const checkbox = document.getElementById(scoreId);
        if (checkbox) {
            checkbox.checked = !checkbox.checked;
            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
    
    /**
     * 处理Tab导航
     * @param {KeyboardEvent} event - 键盘事件
     */
    handleTabNavigation(event) {
        const modal = document.getElementById('reviewModal');
        if (!modal || !modal.classList.contains('show')) {
            return;
        }
        
        // 获取所有可聚焦元素
        const focusableElements = modal.querySelectorAll(
            'input:not([disabled]), select:not([disabled]), textarea:not([disabled]), ' +
            'button:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (event.shiftKey) {
            // Shift+Tab - 向前导航
            if (document.activeElement === firstElement) {
                event.preventDefault();
                lastElement.focus();
            }
        } else {
            // Tab - 向后导航
            if (document.activeElement === lastElement) {
                event.preventDefault();
                firstElement.focus();
            }
        }
    }
    
    /**
     * 导航到页面
     * @param {string} path - 页面路径
     */
    navigateToPage(path) {
        if (window.location.pathname !== path) {
            window.location.href = path;
        }
    }
    
    /**
     * 显示帮助模态框
     */
    showHelp() {
        const helpModal = document.getElementById('shortcutHelpModal');
        if (helpModal) {
            const modal = new bootstrap.Modal(helpModal);
            modal.show();
        }
    }
    
    /**
     * 创建帮助模态框
     */
    createHelpModal() {
        const existingModal = document.getElementById('shortcutHelpModal');
        if (existingModal) {
            return;
        }
        
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'shortcutHelpModal';
        modal.tabIndex = -1;
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">键盘快捷键</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div id="shortcutHelpContent"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 监听模态框显示事件，动态生成内容
        modal.addEventListener('show.bs.modal', () => {
            this.updateHelpContent();
        });
    }
    
    /**
     * 更新帮助内容
     */
    updateHelpContent() {
        const content = document.getElementById('shortcutHelpContent');
        if (!content) return;
        
        let html = '';
        
        // 按上下文分组显示快捷键
        for (const [contextName, shortcuts] of this.contexts) {
            if (shortcuts.size === 0) continue;
            
            const contextTitle = {
                'global': '全局快捷键',
                'review': '复盘页面',
                'modal': '模态框',
                'input': '输入框'
            }[contextName] || contextName;
            
            html += `<h6 class="mt-3 mb-2">${contextTitle}</h6>`;
            html += '<div class="row">';
            
            for (const [key, shortcut] of shortcuts) {
                if (shortcut.description) {
                    html += `
                        <div class="col-md-6 mb-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="text-muted">${shortcut.description}</span>
                                <kbd class="ms-2">${this.formatShortcutKey(key)}</kbd>
                            </div>
                        </div>
                    `;
                }
            }
            
            html += '</div>';
        }
        
        content.innerHTML = html;
    }
    
    /**
     * 格式化快捷键显示
     * @param {string} key - 快捷键字符串
     * @returns {string} 格式化后的字符串
     */
    formatShortcutKey(key) {
        return key
            .split('+')
            .map(part => {
                const keyMap = {
                    'ctrl': 'Ctrl',
                    'alt': 'Alt',
                    'shift': 'Shift',
                    'meta': 'Cmd',
                    'space': 'Space',
                    'esc': 'Esc',
                    'enter': 'Enter',
                    'tab': 'Tab'
                };
                return keyMap[part] || part.toUpperCase();
            })
            .join(' + ');
    }
    
    /**
     * 获取所有快捷键
     * @returns {Array} 快捷键列表
     */
    getAllShortcuts() {
        const allShortcuts = [];
        
        for (const [contextName, shortcuts] of this.contexts) {
            for (const [key, shortcut] of shortcuts) {
                allShortcuts.push({
                    ...shortcut,
                    context: contextName,
                    formattedKey: this.formatShortcutKey(key)
                });
            }
        }
        
        return allShortcuts;
    }
    
    /**
     * 触发自定义事件
     * @param {string} eventName - 事件名称
     * @param {Object} detail - 事件详情
     */
    triggerEvent(eventName, detail) {
        const event = new CustomEvent(`keyboardShortcut:${eventName}`, {
            detail,
            bubbles: true
        });
        document.dispatchEvent(event);
    }
    
    /**
     * 销毁快捷键管理器
     */
    destroy() {
        document.removeEventListener('keydown', this.handleKeyDown);
        document.removeEventListener('keyup', this.handleKeyUp);
        document.removeEventListener('focusin', this.handleFocusChange);
        document.removeEventListener('focusout', this.handleFocusChange);
        
        this.shortcuts.clear();
        this.contexts.clear();
        
        const helpModal = document.getElementById('shortcutHelpModal');
        if (helpModal && helpModal.parentNode) {
            helpModal.parentNode.removeChild(helpModal);
        }
    }
}

// 创建全局快捷键管理器实例
const keyboardShortcutManager = new KeyboardShortcutManager();

// 导出类和实例
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { KeyboardShortcutManager, keyboardShortcutManager };
}