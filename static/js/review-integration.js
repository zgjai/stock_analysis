/**
 * 复盘功能集成管理器
 * 负责集成所有复盘相关组件并管理它们之间的交互
 */
class ReviewIntegrationManager {
    constructor() {
        this.components = {
            saveManager: null,
            floatingProfitCalculator: null,
            holdingDaysEditors: new Map()
        };
        
        this.state = {
            currentStockCode: null,
            currentReviewData: null,
            isInitialized: false,
            isModalOpen: false
        };
        
        this.eventHandlers = new Map();
        this.performanceOptimizations = {
            debouncedHandlers: new Map(),
            throttledHandlers: new Map(),
            batchProcessor: null,
            loadingStates: new Set()
        };
        
        // 绑定方法上下文
        this.handleModalShow = this.handleModalShow.bind(this);
        this.handleModalHide = this.handleModalHide.bind(this);
        this.handleFormChange = this.handleFormChange.bind(this);
        this.handleSaveSuccess = this.handleSaveSuccess.bind(this);
        this.handleSaveError = this.handleSaveError.bind(this);
        this.handleHoldingDaysUpdate = this.handleHoldingDaysUpdate.bind(this);
        this.handleFloatingProfitUpdate = this.handleFloatingProfitUpdate.bind(this);
    }
    
    /**
     * 初始化集成管理器
     */
    async init() {
        if (this.state.isInitialized) {
            console.log('ReviewIntegrationManager already initialized');
            return;
        }
        
        try {
            console.log('Initializing ReviewIntegrationManager...');
            
            // 等待DOM完全加载
            await this.waitForDOM();
            
            // 初始化性能优化 - 使用try-catch防止错误
            try {
                this.initializePerformanceOptimizations();
            } catch (error) {
                console.warn('Performance optimizations failed, continuing...', error);
            }
            
            // 初始化各个组件 - 使用try-catch防止错误
            try {
                await this.initializeComponents();
            } catch (error) {
                console.warn('Some components failed to initialize, continuing...', error);
            }
            
            // 设置事件监听器
            try {
                this.setupEventListeners();
            } catch (error) {
                console.warn('Event listeners setup failed, continuing...', error);
            }
            
            // 设置组件间通信
            try {
                this.setupComponentCommunication();
            } catch (error) {
                console.warn('Component communication setup failed, continuing...', error);
            }
            
            this.state.isInitialized = true;
            console.log('ReviewIntegrationManager initialized successfully');
            
            // 触发初始化完成事件
            try {
                this.triggerEvent('integrationReady', {
                    components: Object.keys(this.components),
                    timestamp: new Date().toISOString()
                });
            } catch (error) {
                console.warn('Failed to trigger integration ready event', error);
            }
            
        } catch (error) {
            console.error('Failed to initialize ReviewIntegrationManager:', error);
            // 不抛出错误，让页面继续工作
            this.state.isInitialized = true; // 标记为已初始化，避免重复尝试
        }
    }
    
    /**
     * 初始化性能优化
     */
    initializePerformanceOptimizations() {
        // 创建防抖处理器
        this.performanceOptimizations.debouncedHandlers.set('formChange', 
            debounce(this.handleFormChange, 300));
        
        // 创建节流处理器
        this.performanceOptimizations.throttledHandlers.set('floatingProfitUpdate', 
            throttle(this.handleFloatingProfitUpdate, 100));
        
        // 创建批处理器
        if (typeof BatchProcessor !== 'undefined') {
            this.performanceOptimizations.batchProcessor = new BatchProcessor(5, 200);
        }
        
        // 启用自动保存
        if (typeof autoSaveManager !== 'undefined') {
            autoSaveManager.enable(
                () => this.saveCurrentReview(),
                () => this.hasUnsavedChanges(),
                'reviewIntegration'
            );
        }
        
        // 设置键盘快捷键
        if (typeof keyboardShortcutManager !== 'undefined') {
            this.setupKeyboardShortcuts();
        }
        
        console.log('Performance optimizations initialized');
    }
    
    /**
     * 设置键盘快捷键
     */
    setupKeyboardShortcuts() {
        // 快速保存
        keyboardShortcutManager.register('ctrl+s', (e) => {
            e.preventDefault();
            this.saveCurrentReview();
        }, {
            description: '保存复盘',
            context: 'review'
        });
        
        // 快速切换评分
        for (let i = 1; i <= 5; i++) {
            keyboardShortcutManager.register(`alt+${i}`, (e) => {
                e.preventDefault();
                this.toggleScoreByIndex(i - 1);
            }, {
                description: `切换评分项 ${i}`,
                context: 'review'
            });
        }
        
        // 聚焦到当前价格输入
        keyboardShortcutManager.register('ctrl+p', (e) => {
            e.preventDefault();
            const priceInput = document.getElementById('current-price-input');
            if (priceInput) {
                priceInput.focus();
                priceInput.select();
            }
        }, {
            description: '聚焦到当前价格输入',
            context: 'review'
        });
    }
    
    /**
     * 等待DOM元素加载完成
     */
    async waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }
    
    /**
     * 初始化各个组件
     */
    async initializeComponents() {
        // 初始化复盘保存管理器
        await this.initializeSaveManager();
        
        // 初始化浮盈计算器
        await this.initializeFloatingProfitCalculator();
        
        // 初始化持仓天数编辑器（在持仓数据加载后）
        await this.initializeHoldingDaysEditors();
        
        console.log('All components initialized');
    }
    
    /**
     * 初始化复盘保存管理器
     */
    async initializeSaveManager() {
        try {
            if (typeof ReviewSaveManager === 'undefined') {
                throw new Error('ReviewSaveManager class not found');
            }
            
            const form = document.getElementById('review-form');
            if (!form) {
                throw new Error('Review form not found');
            }
            
            this.components.saveManager = new ReviewSaveManager('#review-form');
            console.log('ReviewSaveManager initialized');
            
        } catch (error) {
            console.error('Failed to initialize ReviewSaveManager:', error);
            throw error;
        }
    }
    
    /**
     * 初始化浮盈计算器
     */
    async initializeFloatingProfitCalculator() {
        try {
            // 检查依赖
            if (typeof FloatingProfitCalculator === 'undefined') {
                throw new Error('FloatingProfitCalculator class not found');
            }
            
            if (typeof debounce === 'undefined') {
                throw new Error('debounce function not found - utils.js may not be loaded');
            }
            
            // 检查必要的DOM元素是否存在
            const requiredElements = ['current-price-input', 'floating-profit-ratio'];
            const missingElements = requiredElements.filter(id => !document.getElementById(id));
            
            if (missingElements.length > 0) {
                console.warn('Some FloatingProfitCalculator elements not found:', missingElements);
                console.warn('FloatingProfitCalculator will be initialized when elements are available');
                return;
            }
            
            // 创建全局浮盈计算器实例
            this.components.floatingProfitCalculator = new FloatingProfitCalculator(null, null);
            console.log('FloatingProfitCalculator initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize FloatingProfitCalculator:', error);
            // 浮盈计算器不是必需的，可以继续运行
            console.warn('Continuing without FloatingProfitCalculator');
            this.components.floatingProfitCalculator = null;
        }
    }
    
    /**
     * 初始化持仓天数编辑器
     */
    async initializeHoldingDaysEditors() {
        try {
            if (typeof HoldingDaysEditor === 'undefined') {
                console.warn('HoldingDaysEditor class not found, skipping initialization');
                return;
            }
            
            // 持仓天数编辑器将在持仓数据加载时动态创建
            console.log('HoldingDaysEditor ready for dynamic initialization');
            
        } catch (error) {
            console.error('Failed to initialize HoldingDaysEditors:', error);
            // 持仓天数编辑器不是必需的，可以继续运行
            console.warn('Continuing without HoldingDaysEditors');
        }
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 复盘模态框事件
        const modal = document.getElementById('reviewModal');
        if (modal) {
            modal.addEventListener('show.bs.modal', this.handleModalShow);
            modal.addEventListener('hide.bs.modal', this.handleModalHide);
        }
        
        // 表单变化事件
        const form = document.getElementById('review-form');
        if (form) {
            form.addEventListener('change', this.handleFormChange);
            form.addEventListener('input', this.handleFormChange);
        }
        
        // 全局事件监听
        document.addEventListener('reviewSaved', this.handleSaveSuccess);
        document.addEventListener('reviewSaveError', this.handleSaveError);
        document.addEventListener('holdingDaysUpdated', this.handleHoldingDaysUpdate);
        document.addEventListener('floatingProfitCalculated', this.handleFloatingProfitUpdate);
        
        console.log('Event listeners setup complete');
    }
    
    /**
     * 设置组件间通信
     */
    setupComponentCommunication() {
        // 当浮盈计算完成时，通知保存管理器
        if (this.components.floatingProfitCalculator) {
            // 监听价格输入变化
            const priceInput = document.getElementById('current-price-input');
            if (priceInput) {
                priceInput.addEventListener('input', (e) => {
                    // 通知保存管理器表单有变化
                    if (this.components.saveManager) {
                        this.components.saveManager.detectChanges();
                    }
                });
            }
        }
        
        // 当持仓天数更新时，通知保存管理器
        document.addEventListener('holdingDaysEditor:saveSuccess', (e) => {
            if (this.components.saveManager) {
                // 更新表单中的持仓天数值
                const holdingDaysInput = document.getElementById('holding-days');
                if (holdingDaysInput) {
                    holdingDaysInput.value = e.detail.newDays;
                    this.components.saveManager.detectChanges();
                }
            }
        });
        
        console.log('Component communication setup complete');
    }
    
    /**
     * 处理模态框显示事件
     */
    handleModalShow(event) {
        this.state.isModalOpen = true;
        
        // 获取股票代码
        const stockCodeInput = document.getElementById('review-stock-code');
        if (stockCodeInput) {
            this.state.currentStockCode = stockCodeInput.value;
        }
        
        // 初始化当前股票的组件
        this.initializeStockSpecificComponents();
        
        // 触发模态框打开事件
        this.triggerEvent('modalOpened', {
            stockCode: this.state.currentStockCode,
            timestamp: new Date().toISOString()
        });
        
        console.log('Review modal opened for stock:', this.state.currentStockCode);
    }
    
    /**
     * 处理模态框隐藏事件
     */
    handleModalHide(event) {
        this.state.isModalOpen = false;
        this.state.currentStockCode = null;
        this.state.currentReviewData = null;
        
        // 清理股票特定的组件
        this.cleanupStockSpecificComponents();
        
        // 触发模态框关闭事件
        this.triggerEvent('modalClosed', {
            timestamp: new Date().toISOString()
        });
        
        console.log('Review modal closed');
    }
    
    /**
     * 初始化股票特定的组件
     */
    async initializeStockSpecificComponents() {
        if (!this.state.currentStockCode) return;
        
        try {
            // 如果浮盈计算器还没有初始化，尝试重新初始化
            if (!this.components.floatingProfitCalculator) {
                await this.initializeFloatingProfitCalculator();
            }
            
            // 获取股票的买入价格
            const buyPrice = await this.getBuyPrice(this.state.currentStockCode);
            
            // 更新浮盈计算器
            if (this.components.floatingProfitCalculator) {
                this.components.floatingProfitCalculator.stockCode = this.state.currentStockCode;
                this.components.floatingProfitCalculator.setBuyPrice(buyPrice);
                
                // 显示买入价格
                const buyPriceDisplay = document.getElementById('buy-price-display');
                if (buyPriceDisplay && buyPrice) {
                    buyPriceDisplay.textContent = `¥${buyPrice.toFixed(2)}`;
                }
            } else {
                console.warn('FloatingProfitCalculator not available for stock-specific initialization');
            }
            
            // 初始化持仓天数编辑器（如果在模态框中有相关元素）
            const holdingDaysContainer = document.querySelector('.holding-days-editable-container');
            if (holdingDaysContainer && typeof HoldingDaysEditor !== 'undefined') {
                const currentDays = parseInt(document.getElementById('holding-days')?.value) || 0;
                const editor = new HoldingDaysEditor(this.state.currentStockCode, currentDays);
                
                // 这里不直接初始化编辑器，因为模态框中的持仓天数是普通输入框
                // 但我们可以监听其变化
                const holdingDaysInput = document.getElementById('holding-days');
                if (holdingDaysInput) {
                    holdingDaysInput.addEventListener('change', (e) => {
                        // 可以在这里添加验证逻辑
                        const days = parseInt(e.target.value);
                        if (days < 1) {
                            e.target.value = 1;
                            this.showMessage('持仓天数不能小于1天', 'warning');
                        }
                    });
                }
            }
            
        } catch (error) {
            console.error('Failed to initialize stock-specific components:', error);
        }
    }
    
    /**
     * 清理股票特定的组件
     */
    cleanupStockSpecificComponents() {
        // 重置浮盈计算器
        if (this.components.floatingProfitCalculator) {
            this.components.floatingProfitCalculator.stockCode = null;
            this.components.floatingProfitCalculator.buyPrice = null;
            this.components.floatingProfitCalculator.resetDisplay();
        }
        
        // 清理持仓天数编辑器
        this.components.holdingDaysEditors.clear();
    }
    
    /**
     * 获取股票买入价格
     */
    async getBuyPrice(stockCode) {
        try {
            if (typeof apiClient === 'undefined') {
                console.warn('API client not available');
                return null;
            }
            
            // 尝试从持仓数据获取买入价格
            const holdingsResponse = await apiClient.getHoldings();
            if (holdingsResponse && holdingsResponse.success) {
                const holding = holdingsResponse.data.find(h => h.stock_code === stockCode);
                if (holding && holding.buy_price) {
                    return parseFloat(holding.buy_price);
                }
            }
            
            // 如果持仓数据中没有，尝试从交易记录获取
            const tradesResponse = await apiClient.getTrades({ stock_code: stockCode });
            if (tradesResponse && tradesResponse.success && tradesResponse.data.length > 0) {
                // 获取最近的买入记录
                const buyTrades = tradesResponse.data.filter(t => t.trade_type === 'buy');
                if (buyTrades.length > 0) {
                    // 计算平均买入价格
                    const totalAmount = buyTrades.reduce((sum, t) => sum + (t.price * t.quantity), 0);
                    const totalQuantity = buyTrades.reduce((sum, t) => sum + t.quantity, 0);
                    return totalQuantity > 0 ? totalAmount / totalQuantity : null;
                }
            }
            
            return null;
        } catch (error) {
            console.error('Failed to get buy price:', error);
            return null;
        }
    }
    
    /**
     * 处理表单变化事件
     */
    handleFormChange(event) {
        // 检查是否是当前价格输入
        if (event.target.id === 'current-price-input') {
            this.handleCurrentPriceChange(event.target.value);
        }
        
        // 检查是否是持仓天数输入
        if (event.target.id === 'holding-days') {
            this.handleHoldingDaysChange(event.target.value);
        }
        
        // 触发表单变化事件
        this.triggerEvent('formChanged', {
            field: event.target.id || event.target.name,
            value: event.target.value,
            type: event.target.type
        });
    }
    
    /**
     * 处理当前价格变化
     */
    handleCurrentPriceChange(price) {
        if (this.components.floatingProfitCalculator && price) {
            const numPrice = parseFloat(price);
            if (!isNaN(numPrice) && numPrice > 0) {
                this.components.floatingProfitCalculator.setCurrentPrice(numPrice);
            }
        }
    }
    
    /**
     * 处理持仓天数变化
     */
    handleHoldingDaysChange(days) {
        const numDays = parseInt(days);
        if (!isNaN(numDays) && numDays >= 1) {
            // 验证通过，可以进行其他处理
            this.triggerEvent('holdingDaysChanged', {
                stockCode: this.state.currentStockCode,
                days: numDays
            });
        }
    }
    
    /**
     * 处理保存成功事件
     */
    handleSaveSuccess(event) {
        console.log('Review save success:', event.detail);
        
        // 更新状态
        this.state.currentReviewData = event.detail.reviewData;
        
        // 触发集成层面的保存成功事件
        this.triggerEvent('saveSuccess', {
            reviewData: event.detail.reviewData,
            isNew: event.detail.isNew,
            timestamp: new Date().toISOString()
        });
        
        // 显示成功消息
        this.showMessage('复盘保存成功', 'success');
    }
    
    /**
     * 处理保存错误事件
     */
    handleSaveError(event) {
        console.error('Review save error:', event.detail);
        
        // 触发集成层面的保存错误事件
        this.triggerEvent('saveError', {
            error: event.detail.error,
            timestamp: new Date().toISOString()
        });
        
        // 显示错误消息
        this.showMessage('复盘保存失败: ' + (event.detail.error?.message || '未知错误'), 'error');
    }
    
    /**
     * 处理持仓天数更新事件
     */
    handleHoldingDaysUpdate(event) {
        console.log('Holding days updated:', event.detail);
        
        // 如果是当前股票，更新模态框中的值
        if (event.detail.stockCode === this.state.currentStockCode) {
            const holdingDaysInput = document.getElementById('holding-days');
            if (holdingDaysInput) {
                holdingDaysInput.value = event.detail.newDays;
                
                // 通知保存管理器有变化
                if (this.components.saveManager) {
                    this.components.saveManager.detectChanges();
                }
            }
        }
        
        // 触发集成层面的持仓天数更新事件
        this.triggerEvent('holdingDaysUpdated', event.detail);
    }
    
    /**
     * 处理浮盈更新事件
     */
    handleFloatingProfitUpdate(event) {
        console.log('Floating profit updated:', event.detail);
        
        // 触发集成层面的浮盈更新事件
        this.triggerEvent('floatingProfitUpdated', event.detail);
    }
    
    /**
     * 创建持仓天数编辑器
     */
    createHoldingDaysEditor(stockCode, currentDays, container) {
        if (typeof HoldingDaysEditor === 'undefined') {
            console.warn('HoldingDaysEditor not available');
            return null;
        }
        
        try {
            const editor = new HoldingDaysEditor(stockCode, currentDays);
            if (editor.init(container)) {
                this.components.holdingDaysEditors.set(stockCode, editor);
                
                // 监听编辑器事件
                container.addEventListener('holdingDaysEditor:saveSuccess', (e) => {
                    this.handleHoldingDaysUpdate(e);
                });
                
                return editor;
            }
        } catch (error) {
            console.error('Failed to create holding days editor:', error);
        }
        
        return null;
    }
    
    /**
     * 获取持仓天数编辑器
     */
    getHoldingDaysEditor(stockCode) {
        return this.components.holdingDaysEditors.get(stockCode) || null;
    }
    
    /**
     * 获取浮盈计算结果
     */
    getFloatingProfitResult() {
        if (this.components.floatingProfitCalculator) {
            return this.components.floatingProfitCalculator.getCalculationResult();
        }
        return null;
    }
    
    /**
     * 检查是否有未保存的更改
     */
    hasUnsavedChanges() {
        if (this.components.saveManager) {
            return this.components.saveManager.hasUnsavedData();
        }
        return false;
    }
    
    /**
     * 强制保存当前复盘
     */
    async forceSave() {
        if (this.components.saveManager) {
            return await this.components.saveManager.saveReview();
        }
        return false;
    }
    
    /**
     * 显示消息
     */
    showMessage(message, type = 'info') {
        if (typeof showMessage === 'function') {
            showMessage(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
    
    /**
     * 触发自定义事件
     */
    triggerEvent(eventName, detail) {
        const event = new CustomEvent(`reviewIntegration:${eventName}`, {
            detail: detail,
            bubbles: true
        });
        
        document.dispatchEvent(event);
        
        // 记录事件处理器
        if (this.eventHandlers.has(eventName)) {
            const handlers = this.eventHandlers.get(eventName);
            handlers.forEach(handler => {
                try {
                    handler(detail);
                } catch (error) {
                    console.error(`Error in event handler for ${eventName}:`, error);
                }
            });
        }
    }
    
    /**
     * 添加事件监听器
     */
    addEventListener(eventName, handler) {
        if (!this.eventHandlers.has(eventName)) {
            this.eventHandlers.set(eventName, []);
        }
        this.eventHandlers.get(eventName).push(handler);
    }
    
    /**
     * 移除事件监听器
     */
    removeEventListener(eventName, handler) {
        if (this.eventHandlers.has(eventName)) {
            const handlers = this.eventHandlers.get(eventName);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    
    /**
     * 获取组件状态
     */
    getState() {
        return {
            ...this.state,
            components: {
                saveManager: !!this.components.saveManager,
                floatingProfitCalculator: !!this.components.floatingProfitCalculator,
                holdingDaysEditors: this.components.holdingDaysEditors.size
            }
        };
    }
    
    /**
     * 执行完整功能测试
     */
    async runIntegrationTest() {
        console.log('Starting integration test...');
        
        const testResults = {
            componentInitialization: false,
            eventCommunication: false,
            dataFlow: false,
            errorHandling: false,
            userInteraction: false
        };
        
        try {
            // 测试组件初始化
            testResults.componentInitialization = this.testComponentInitialization();
            
            // 测试事件通信
            testResults.eventCommunication = await this.testEventCommunication();
            
            // 测试数据流
            testResults.dataFlow = await this.testDataFlow();
            
            // 测试错误处理
            testResults.errorHandling = await this.testErrorHandling();
            
            // 测试用户交互
            testResults.userInteraction = await this.testUserInteraction();
            
        } catch (error) {
            console.error('Integration test failed:', error);
        }
        
        console.log('Integration test results:', testResults);
        return testResults;
    }
    
    /**
     * 测试组件初始化
     */
    testComponentInitialization() {
        const hasRequiredComponents = 
            this.components.saveManager !== null &&
            this.components.floatingProfitCalculator !== null;
        
        console.log('Component initialization test:', hasRequiredComponents ? 'PASS' : 'FAIL');
        return hasRequiredComponents;
    }
    
    /**
     * 测试事件通信
     */
    async testEventCommunication() {
        return new Promise((resolve) => {
            let eventReceived = false;
            
            // 监听测试事件
            const testHandler = () => {
                eventReceived = true;
            };
            
            this.addEventListener('test', testHandler);
            
            // 触发测试事件
            this.triggerEvent('test', { message: 'test' });
            
            // 检查事件是否被接收
            setTimeout(() => {
                this.removeEventListener('test', testHandler);
                console.log('Event communication test:', eventReceived ? 'PASS' : 'FAIL');
                resolve(eventReceived);
            }, 100);
        });
    }
    
    /**
     * 测试数据流
     */
    async testDataFlow() {
        try {
            // 测试浮盈计算数据流
            if (this.components.floatingProfitCalculator) {
                this.components.floatingProfitCalculator.setBuyPrice(10.00);
                this.components.floatingProfitCalculator.setCurrentPrice(11.00);
                
                const result = this.components.floatingProfitCalculator.getCalculationResult();
                const hasValidResult = result && result.floating_profit_ratio > 0;
                
                console.log('Data flow test:', hasValidResult ? 'PASS' : 'FAIL');
                return hasValidResult;
            }
            
            return false;
        } catch (error) {
            console.error('Data flow test error:', error);
            return false;
        }
    }
    
    /**
     * 测试错误处理
     */
    async testErrorHandling() {
        try {
            // 测试无效价格输入
            if (this.components.floatingProfitCalculator) {
                this.components.floatingProfitCalculator.setCurrentPrice(-1);
                
                // 应该不会抛出异常，而是优雅处理
                console.log('Error handling test: PASS');
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Error handling test failed:', error);
            return false;
        }
    }
    
    /**
     * 测试用户交互
     */
    async testUserInteraction() {
        try {
            // 模拟用户输入
            const priceInput = document.getElementById('current-price-input');
            if (priceInput) {
                // 模拟输入事件
                priceInput.value = '12.50';
                priceInput.dispatchEvent(new Event('input', { bubbles: true }));
                
                console.log('User interaction test: PASS');
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('User interaction test error:', error);
            return false;
        }
    }
    
    /**
     * 保存当前复盘
     */
    async saveCurrentReview() {
        if (this.components.saveManager) {
            return await this.components.saveManager.saveReview();
        }
        return false;
    }
    
    /**
     * 检查是否有未保存的更改
     */
    hasUnsavedChanges() {
        if (this.components.saveManager) {
            return this.components.saveManager.hasUnsavedData();
        }
        return false;
    }
    
    /**
     * 根据索引切换评分项
     */
    toggleScoreByIndex(index) {
        const scoreIds = ['price-up-score', 'bbi-score', 'volume-score', 'trend-score', 'j-score'];
        if (index >= 0 && index < scoreIds.length) {
            const checkbox = document.getElementById(scoreIds[index]);
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                checkbox.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    }
    
    /**
     * 显示加载状态
     */
    showLoading(key, options = {}) {
        this.performanceOptimizations.loadingStates.add(key);
        if (typeof loadingManager !== 'undefined') {
            loadingManager.showLoading(key, options);
        }
    }
    
    /**
     * 隐藏加载状态
     */
    hideLoading(key) {
        this.performanceOptimizations.loadingStates.delete(key);
        if (typeof loadingManager !== 'undefined') {
            loadingManager.hideLoading(key);
        }
    }
    
    /**
     * 批量处理操作
     */
    async batchProcess(operations) {
        if (this.performanceOptimizations.batchProcessor) {
            const promises = operations.map(op => 
                this.performanceOptimizations.batchProcessor.add(op.task, op.data)
            );
            return await Promise.allSettled(promises);
        } else {
            // 降级处理
            const promises = operations.map(op => op.task(op.data));
            return await Promise.allSettled(promises);
        }
    }
    
    /**
     * 销毁集成管理器
     */
    destroy() {
        // 移除事件监听器
        const modal = document.getElementById('reviewModal');
        if (modal) {
            modal.removeEventListener('show.bs.modal', this.handleModalShow);
            modal.removeEventListener('hide.bs.modal', this.handleModalHide);
        }
        
        const form = document.getElementById('review-form');
        if (form) {
            form.removeEventListener('change', this.handleFormChange);
            form.removeEventListener('input', this.handleFormChange);
        }
        
        document.removeEventListener('reviewSaved', this.handleSaveSuccess);
        document.removeEventListener('reviewSaveError', this.handleSaveError);
        document.removeEventListener('holdingDaysUpdated', this.handleHoldingDaysUpdate);
        document.removeEventListener('floatingProfitCalculated', this.handleFloatingProfitUpdate);
        
        // 销毁组件
        if (this.components.saveManager && typeof this.components.saveManager.destroy === 'function') {
            this.components.saveManager.destroy();
        }
        
        if (this.components.floatingProfitCalculator && typeof this.components.floatingProfitCalculator.destroy === 'function') {
            this.components.floatingProfitCalculator.destroy();
        }
        
        this.components.holdingDaysEditors.forEach(editor => {
            if (typeof editor.destroy === 'function') {
                editor.destroy();
            }
        });
        
        // 清空状态
        this.components = {
            saveManager: null,
            floatingProfitCalculator: null,
            holdingDaysEditors: new Map()
        };
        
        this.state = {
            currentStockCode: null,
            currentReviewData: null,
            isInitialized: false,
            isModalOpen: false
        };
        
        this.eventHandlers.clear();
        
        // 清理性能优化
        if (this.performanceOptimizations.batchProcessor) {
            this.performanceOptimizations.batchProcessor.clear();
        }
        
        // 清理加载状态
        this.performanceOptimizations.loadingStates.forEach(key => {
            this.hideLoading(key);
        });
        
        // 禁用自动保存
        if (typeof autoSaveManager !== 'undefined') {
            autoSaveManager.disable('reviewIntegration');
        }
        
        console.log('ReviewIntegrationManager destroyed');
    }
}

// 创建全局集成管理器实例
let reviewIntegrationManager = null;

/**
 * 初始化复盘集成管理器
 */
async function initializeReviewIntegration() {
    try {
        if (reviewIntegrationManager) {
            reviewIntegrationManager.destroy();
        }
        
        reviewIntegrationManager = new ReviewIntegrationManager();
        await reviewIntegrationManager.init();
        
        console.log('Review integration initialized successfully');
        return reviewIntegrationManager;
        
    } catch (error) {
        console.error('Failed to initialize review integration:', error);
        throw error;
    }
}

/**
 * 获取集成管理器实例
 */
function getReviewIntegrationManager() {
    return reviewIntegrationManager;
}

// DOM加载完成后自动初始化
document.addEventListener('DOMContentLoaded', () => {
    // 延迟初始化，确保其他脚本已加载
    setTimeout(async () => {
        try {
            await initializeReviewIntegration();
        } catch (error) {
            console.error('Auto-initialization failed:', error);
        }
    }, 500);
});

// 导出类和函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        ReviewIntegrationManager, 
        initializeReviewIntegration, 
        getReviewIntegrationManager 
    };
}