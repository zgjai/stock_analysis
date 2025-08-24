/**
 * 浮盈计算器类
 * 处理当前价格输入和实时浮盈比例计算
 */
class FloatingProfitCalculator {
    constructor(stockCode, buyPrice = null) {
        this.stockCode = stockCode;
        this.buyPrice = buyPrice;
        this.currentPrice = null;
        this.profitRatio = 0;
        this.profitAmount = 0;
        this.isCalculating = false;
        this.calculationTimer = null;
        
        try {
            // 绑定方法上下文 - 使用try-catch防止错误
            if (typeof this.handlePriceInput === 'function') {
                this.handlePriceInput = this.handlePriceInput.bind(this);
            }
            if (typeof this.updateDisplay === 'function') {
                this.updateDisplay = this.updateDisplay.bind(this);
            }
            
            // 初始化UI元素
            this.initializeElements();
            this.bindEvents();
        } catch (error) {
            console.error('FloatingProfitCalculator constructor error:', error);
            // 继续执行，不抛出错误
        }
    }
    
    /**
     * 初始化UI元素
     */
    initializeElements() {
        // 获取或创建当前价格输入框
        this.priceInput = document.getElementById('current-price-input');
        if (!this.priceInput) {
            console.warn('Current price input element not found');
            return;
        }
        
        // 获取或创建浮盈显示元素
        this.profitDisplay = document.getElementById('floating-profit-display');
        if (!this.profitDisplay) {
            console.warn('Floating profit display element not found');
            return;
        }
        
        // 获取或创建浮盈比例显示元素
        this.ratioDisplay = document.getElementById('floating-profit-ratio');
        if (!this.ratioDisplay) {
            console.warn('Floating profit ratio display element not found');
            return;
        }
        
        // 获取或创建错误提示元素
        this.errorDisplay = document.getElementById('floating-profit-error');
        
        // 设置初始状态
        this.resetDisplay();
    }
    
    /**
     * 绑定事件监听器
     */
    bindEvents() {
        if (!this.priceInput) return;
        
        // 实时输入事件
        this.priceInput.addEventListener('input', this.handlePriceInput);
        this.priceInput.addEventListener('blur', this.handlePriceInput);
        
        // 键盘事件
        this.priceInput.addEventListener('keypress', (e) => {
            // 只允许数字、小数点和退格键
            const allowedKeys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab'];
            if (!allowedKeys.includes(e.key)) {
                e.preventDefault();
            }
            
            // 防止多个小数点
            if (e.key === '.' && this.priceInput.value.includes('.')) {
                e.preventDefault();
            }
        });
    }
    
    /**
     * 处理价格输入事件
     */
    handlePriceInput(event) {
        const value = event.target.value.trim();
        
        // 使用防抖优化输入处理
        if (!this.debouncedCalculation) {
            this.debouncedCalculation = debounce((inputValue) => {
                this.processInput(inputValue);
            }, 300);
        }
        
        this.debouncedCalculation(value);
    }
    
    /**
     * 处理输入值
     */
    processInput(value) {
        // 验证输入
        const validationResult = this.validateInput(value);
        if (!validationResult.isValid) {
            this.showError(validationResult.message);
            this.resetDisplay();
            return;
        }
        
        // 清除错误提示
        this.clearError();
        
        // 设置当前价格
        this.setCurrentPrice(parseFloat(value));
    }
    
    /**
     * 验证价格输入
     */
    validateInput(value) {
        if (!value) {
            return { isValid: true, message: '' }; // 空值是有效的，只是不计算
        }
        
        // 检查是否为有效数字
        const numValue = parseFloat(value);
        if (isNaN(numValue)) {
            return { isValid: false, message: '请输入有效的数字' };
        }
        
        // 检查是否为正数
        if (numValue <= 0) {
            return { isValid: false, message: '价格必须大于0' };
        }
        
        // 检查小数位数（最多2位）
        const decimalParts = value.split('.');
        if (decimalParts.length > 1 && decimalParts[1].length > 2) {
            return { isValid: false, message: '价格最多保留2位小数' };
        }
        
        // 检查价格范围（0.01 - 9999.99）
        if (numValue < 0.01 || numValue > 9999.99) {
            return { isValid: false, message: '价格范围应在0.01-9999.99之间' };
        }
        
        return { isValid: true, message: '' };
    }
    
    /**
     * 设置当前价格并触发计算
     */
    async setCurrentPrice(price) {
        if (!price || price <= 0) {
            this.resetDisplay();
            return;
        }
        
        this.currentPrice = price;
        
        // 如果有买入价格，直接计算；否则通过API获取
        if (this.buyPrice) {
            this.calculateLocalProfit();
        } else {
            await this.calculateRemoteProfit();
        }
    }
    
    /**
     * 本地计算浮盈（当已知买入价格时）
     */
    calculateLocalProfit() {
        if (!this.buyPrice || !this.currentPrice) {
            this.resetDisplay();
            return;
        }
        
        try {
            // 计算浮盈比例和金额
            this.profitRatio = (this.currentPrice - this.buyPrice) / this.buyPrice;
            this.profitAmount = this.currentPrice - this.buyPrice;
            
            // 更新显示
            this.updateDisplay();
        } catch (error) {
            console.error('本地浮盈计算错误:', error);
            this.showError('计算失败，请重试');
        }
    }
    
    /**
     * 远程计算浮盈（通过API获取买入价格）
     */
    async calculateRemoteProfit() {
        if (!this.stockCode || !this.currentPrice) {
            this.resetDisplay();
            return;
        }
        
        // 检查缓存
        const cacheKey = `floating_profit_${this.stockCode}_${this.currentPrice}`;
        if (typeof globalCache !== 'undefined') {
            const cached = globalCache.get(cacheKey);
            if (cached) {
                this.updateFromCachedData(cached);
                return;
            }
        }
        
        // 显示计算中状态
        this.showCalculating();
        
        try {
            // 检查API客户端是否可用
            if (typeof apiClient === 'undefined') {
                throw new Error('API客户端未初始化');
            }
            
            // 调用浮盈计算API
            const response = await apiClient.calculateFloatingProfit(this.stockCode, this.currentPrice);
            
            if (response && response.success) {
                const data = response.data;
                
                // 缓存结果
                if (typeof globalCache !== 'undefined') {
                    globalCache.set(cacheKey, data, 60000); // 缓存1分钟
                }
                
                // 更新数据
                this.buyPrice = data.buy_price;
                this.profitRatio = data.floating_profit_ratio;
                this.profitAmount = data.floating_profit_amount;
                
                // 更新显示
                this.updateDisplay(data);
            } else {
                throw new Error(response?.error?.message || '计算失败');
            }
        } catch (error) {
            console.error('远程浮盈计算错误:', error);
            this.handleCalculationError(error);
        } finally {
            this.hideCalculating();
        }
    }
    
    /**
     * 从缓存数据更新
     */
    updateFromCachedData(data) {
        this.buyPrice = data.buy_price;
        this.profitRatio = data.floating_profit_ratio;
        this.profitAmount = data.floating_profit_amount;
        this.updateDisplay(data);
    }
    
    /**
     * 更新显示
     */
    updateDisplay(apiData = null) {
        if (!this.profitDisplay || !this.ratioDisplay) {
            return;
        }
        
        // 使用API数据或本地计算数据
        const displayData = apiData || this.formatDisplayData();
        
        // 更新浮盈比例显示
        this.ratioDisplay.textContent = displayData.formatted_ratio || this.formatRatio();
        
        // 更新颜色
        this.updateDisplayColor(displayData);
        
        // 更新详细信息（如果有显示元素）
        this.updateDetailedDisplay(displayData);
    }
    
    /**
     * 格式化显示数据
     */
    formatDisplayData() {
        if (this.profitRatio === null || this.profitRatio === undefined) {
            return {
                formatted_ratio: '无法计算',
                color_class: 'text-muted',
                is_profit: false,
                is_loss: false
            };
        }
        
        const percentage = (this.profitRatio * 100).toFixed(2);
        const sign = this.profitRatio > 0 ? '+' : '';
        
        return {
            formatted_ratio: `${sign}${percentage}%`,
            color_class: this.getColorClass(),
            is_profit: this.profitRatio > 0,
            is_loss: this.profitRatio < 0,
            profit_amount: this.profitAmount
        };
    }
    
    /**
     * 格式化比例显示
     */
    formatRatio() {
        if (this.profitRatio === null || this.profitRatio === undefined) {
            return '无法计算';
        }
        
        const percentage = (this.profitRatio * 100).toFixed(2);
        const sign = this.profitRatio > 0 ? '+' : '';
        return `${sign}${percentage}%`;
    }
    
    /**
     * 获取颜色类名
     */
    getColorClass() {
        if (this.profitRatio === null || this.profitRatio === undefined) {
            return 'text-muted';
        }
        
        if (this.profitRatio > 0) {
            return 'text-success'; // 绿色 - 盈利
        } else if (this.profitRatio < 0) {
            return 'text-danger';  // 红色 - 亏损
        } else {
            return 'text-muted';   // 灰色 - 持平
        }
    }
    
    /**
     * 更新显示颜色
     */
    updateDisplayColor(displayData) {
        const colorClass = displayData.color_class || this.getColorClass();
        
        // 移除所有颜色类
        this.ratioDisplay.classList.remove('text-success', 'text-danger', 'text-muted', 'text-warning');
        
        // 添加新的颜色类
        this.ratioDisplay.classList.add(colorClass);
        
        // 如果有父容器，也更新其颜色
        const container = this.ratioDisplay.closest('.floating-profit-container');
        if (container) {
            container.classList.remove('profit', 'loss', 'neutral');
            
            if (displayData.is_profit) {
                container.classList.add('profit');
            } else if (displayData.is_loss) {
                container.classList.add('loss');
            } else {
                container.classList.add('neutral');
            }
        }
    }
    
    /**
     * 更新详细显示信息
     */
    updateDetailedDisplay(displayData) {
        // 更新买入价格显示
        const buyPriceEl = document.getElementById('buy-price-display');
        if (buyPriceEl && this.buyPrice) {
            buyPriceEl.textContent = `¥${this.buyPrice.toFixed(2)}`;
        }
        
        // 更新当前价格显示
        const currentPriceEl = document.getElementById('current-price-display');
        if (currentPriceEl && this.currentPrice) {
            currentPriceEl.textContent = `¥${this.currentPrice.toFixed(2)}`;
        }
        
        // 更新盈亏金额显示
        const profitAmountEl = document.getElementById('profit-amount-display');
        if (profitAmountEl && this.profitAmount !== null && this.profitAmount !== undefined) {
            const sign = this.profitAmount > 0 ? '+' : '';
            profitAmountEl.textContent = `${sign}¥${this.profitAmount.toFixed(2)}`;
            profitAmountEl.className = this.getColorClass();
        }
    }
    
    /**
     * 显示计算中状态
     */
    showCalculating() {
        this.isCalculating = true;
        
        if (this.ratioDisplay) {
            this.ratioDisplay.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 计算中...';
            this.ratioDisplay.className = 'text-muted';
        }
        
        // 禁用输入框
        if (this.priceInput) {
            this.priceInput.disabled = true;
        }
    }
    
    /**
     * 隐藏计算中状态
     */
    hideCalculating() {
        this.isCalculating = false;
        
        // 启用输入框
        if (this.priceInput) {
            this.priceInput.disabled = false;
        }
    }
    
    /**
     * 重置显示
     */
    resetDisplay() {
        this.profitRatio = null;
        this.profitAmount = null;
        
        if (this.ratioDisplay) {
            this.ratioDisplay.textContent = '--';
            this.ratioDisplay.className = 'text-muted';
        }
        
        // 重置详细显示
        const profitAmountEl = document.getElementById('profit-amount-display');
        if (profitAmountEl) {
            profitAmountEl.textContent = '--';
            profitAmountEl.className = 'text-muted';
        }
    }
    
    /**
     * 显示错误信息
     */
    showError(message) {
        if (this.errorDisplay) {
            this.errorDisplay.textContent = message;
            this.errorDisplay.style.display = 'block';
            this.errorDisplay.className = 'text-danger small mt-1';
        } else {
            // 如果没有专门的错误显示元素，在比例显示中显示错误
            if (this.ratioDisplay) {
                this.ratioDisplay.textContent = '错误';
                this.ratioDisplay.className = 'text-danger';
                this.ratioDisplay.title = message;
            }
        }
        
        // 自动清除错误提示
        setTimeout(() => {
            this.clearError();
        }, 5000);
    }
    
    /**
     * 清除错误信息
     */
    clearError() {
        if (this.errorDisplay) {
            this.errorDisplay.style.display = 'none';
            this.errorDisplay.textContent = '';
        }
        
        if (this.ratioDisplay) {
            this.ratioDisplay.removeAttribute('title');
        }
    }
    
    /**
     * 处理计算错误
     */
    handleCalculationError(error) {
        console.error('浮盈计算错误:', error);
        
        let message = '计算失败';
        
        if (error.code === 'NETWORK_ERROR') {
            message = '网络连接失败，请重试';
        } else if (error.code === 'VALIDATION_ERROR') {
            message = '数据验证失败';
        } else if (error.message) {
            message = error.message;
        }
        
        this.showError(message);
        this.resetDisplay();
    }
    
    /**
     * 设置买入价格
     */
    setBuyPrice(buyPrice) {
        this.buyPrice = buyPrice;
        
        // 如果已有当前价格，重新计算
        if (this.currentPrice) {
            this.calculateLocalProfit();
        }
    }
    
    /**
     * 获取当前计算结果
     */
    getCalculationResult() {
        return {
            stock_code: this.stockCode,
            buy_price: this.buyPrice,
            current_price: this.currentPrice,
            floating_profit_ratio: this.profitRatio,
            floating_profit_amount: this.profitAmount,
            formatted_ratio: this.formatRatio(),
            color_class: this.getColorClass(),
            is_profit: this.profitRatio > 0,
            is_loss: this.profitRatio < 0
        };
    }
    
    /**
     * 销毁计算器实例
     */
    destroy() {
        // 清除定时器
        if (this.calculationTimer) {
            clearTimeout(this.calculationTimer);
        }
        
        // 移除事件监听器
        if (this.priceInput) {
            this.priceInput.removeEventListener('input', this.handlePriceInput);
            this.priceInput.removeEventListener('blur', this.handlePriceInput);
        }
        
        // 清理引用
        this.priceInput = null;
        this.profitDisplay = null;
        this.ratioDisplay = null;
        this.errorDisplay = null;
    }
}

// 浮盈计算器管理器
class FloatingProfitManager {
    constructor() {
        this.calculators = new Map();
    }
    
    /**
     * 创建或获取计算器实例
     */
    getCalculator(stockCode, buyPrice = null) {
        if (!this.calculators.has(stockCode)) {
            const calculator = new FloatingProfitCalculator(stockCode, buyPrice);
            this.calculators.set(stockCode, calculator);
        }
        
        const calculator = this.calculators.get(stockCode);
        
        // 更新买入价格（如果提供）
        if (buyPrice !== null) {
            calculator.setBuyPrice(buyPrice);
        }
        
        return calculator;
    }
    
    /**
     * 移除计算器实例
     */
    removeCalculator(stockCode) {
        const calculator = this.calculators.get(stockCode);
        if (calculator) {
            calculator.destroy();
            this.calculators.delete(stockCode);
        }
    }
    
    /**
     * 清理所有计算器
     */
    clearAll() {
        this.calculators.forEach(calculator => calculator.destroy());
        this.calculators.clear();
    }
}

// 创建全局管理器实例
const floatingProfitManager = new FloatingProfitManager();

// 导出类和管理器
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FloatingProfitCalculator, FloatingProfitManager, floatingProfitManager };
}