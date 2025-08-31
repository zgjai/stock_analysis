/**
 * 优化的仪表板JavaScript
 * 实现增量数据更新和性能优化
 */

class OptimizedDashboard {
    constructor() {
        this.cache = new Map();
        this.updateTimers = new Map();
        this.isLoading = false;
        this.lastUpdateTime = null;
        this.updateInterval = 30000; // 30秒更新间隔
        this.retryCount = 0;
        this.maxRetries = 3;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startPeriodicUpdates();
        this.setupVisibilityChangeHandler();
    }
    
    setupEventListeners() {
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.resumeUpdates();
            } else {
                this.pauseUpdates();
            }
        });
        
        // 监听网络状态变化
        window.addEventListener('online', () => {
            this.resumeUpdates();
            this.showNetworkStatus('网络已连接', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.pauseUpdates();
            this.showNetworkStatus('网络已断开', 'warning');
        });
        
        // 监听数据刷新按钮
        const refreshBtn = document.getElementById('refresh-dashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.forceRefresh();
            });
        }
    }
    
    async loadInitialData() {
        this.showLoading(true);
        
        try {
            // 并行加载所有数据
            const [overallStats, monthlyStats, profitDistribution, holdings] = await Promise.all([
                this.loadOverallStatistics(),
                this.loadMonthlyStatistics(),
                this.loadProfitDistribution(),
                this.loadCurrentHoldings()
            ]);
            
            // 更新UI
            this.updateOverallStatistics(overallStats);
            this.updateMonthlyChart(monthlyStats);
            this.updateProfitDistribution(profitDistribution);
            this.updateHoldingsTable(holdings);
            
            this.lastUpdateTime = new Date();
            this.retryCount = 0;
            
        } catch (error) {
            console.error('加载初始数据失败:', error);
            this.handleLoadError(error);
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadOverallStatistics() {
        const cacheKey = 'overall_statistics';
        const cached = this.getFromCache(cacheKey);
        
        if (cached && this.isCacheValid(cached, 5 * 60 * 1000)) { // 5分钟缓存
            return cached.data;
        }
        
        try {
            const response = await fetch('/api/analytics/overall', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('加载总体统计失败:', error);
            // 如果有缓存数据，使用缓存数据
            if (cached) {
                return cached.data;
            }
            throw error;
        }
    }
    
    async loadMonthlyStatistics() {
        const cacheKey = 'monthly_statistics';
        const cached = this.getFromCache(cacheKey);
        
        if (cached && this.isCacheValid(cached, 10 * 60 * 1000)) { // 10分钟缓存
            return cached.data;
        }
        
        try {
            const currentYear = new Date().getFullYear();
            const response = await fetch(`/api/analytics/monthly?year=${currentYear}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('加载月度统计失败:', error);
            if (cached) {
                return cached.data;
            }
            throw error;
        }
    }
    
    async loadProfitDistribution() {
        const cacheKey = 'profit_distribution';
        const cached = this.getFromCache(cacheKey);
        
        if (cached && this.isCacheValid(cached, 15 * 60 * 1000)) { // 15分钟缓存
            return cached.data;
        }
        
        try {
            const response = await fetch('/api/analytics/profit-distribution?use_trade_pairs=true');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('加载收益分布失败:', error);
            if (cached) {
                return cached.data;
            }
            throw error;
        }
    }
    
    async loadCurrentHoldings() {
        const cacheKey = 'current_holdings';
        const cached = this.getFromCache(cacheKey);
        
        if (cached && this.isCacheValid(cached, 2 * 60 * 1000)) { // 2分钟缓存（价格变化较快）
            return cached.data;
        }
        
        try {
            const response = await fetch('/api/analytics/holdings');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('加载持仓数据失败:', error);
            if (cached) {
                return cached.data;
            }
            throw error;
        }
    }
    
    updateOverallStatistics(data) {
        if (!data) return;
        
        // 使用动画更新数值
        this.animateValue('total-investment', data.total_investment, '¥');
        this.animateValue('realized-profit', data.realized_profit, '¥');
        this.animateValue('current-holdings-profit', data.current_holdings_profit, '¥');
        this.animateValue('total-profit', data.total_profit, '¥');
        this.animateValuePercentage('total-return-rate', data.total_return_rate);
        this.animateValuePercentage('success-rate', data.success_rate);
        
        // 更新其他统计信息
        this.updateElement('current-holdings-count', data.current_holdings_count);
        this.updateElement('total-buy-count', data.total_buy_count);
        this.updateElement('total-sell-count', data.total_sell_count);
        
        // 更新颜色指示器
        this.updateProfitIndicator('realized-profit', data.realized_profit);
        this.updateProfitIndicator('current-holdings-profit', data.current_holdings_profit);
        this.updateProfitIndicator('total-profit', data.total_profit);
    }
    
    updateMonthlyChart(data) {
        if (!data || !data.monthly_data) return;
        
        try {
            // 准备图表数据
            const months = data.monthly_data.map(item => item.month_name);
            const profitRates = data.monthly_data.map(item => 
                item.profit_rate !== null ? (item.profit_rate * 100).toFixed(2) : null
            );
            
            // 更新或创建图表
            this.updateOrCreateChart('monthly-chart', {
                type: 'line',
                data: {
                    labels: months,
                    datasets: [{
                        label: '月度收益率 (%)',
                        data: profitRates,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1,
                        spanGaps: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.parsed.y;
                                    return value !== null ? `收益率: ${value}%` : '无数据';
                                }
                            }
                        }
                    }
                }
            });
            
        } catch (error) {
            console.error('更新月度图表失败:', error);
        }
    }
    
    updateProfitDistribution(data) {
        if (!data || !data.distribution) return;
        
        try {
            const labels = data.distribution.map(item => item.range_name);
            const counts = data.distribution.map(item => item.count);
            const percentages = data.distribution.map(item => item.percentage.toFixed(1));
            
            this.updateOrCreateChart('profit-distribution-chart', {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: counts,
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF',
                            '#FF9F40'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label;
                                    const count = context.parsed;
                                    const percentage = percentages[context.dataIndex];
                                    return `${label}: ${count}笔 (${percentage}%)`;
                                }
                            }
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
            
            // 更新汇总信息
            if (data.summary) {
                this.updateElement('total-trades', data.total_trades);
                this.updateElement('win-rate', data.summary.win_rate.toFixed(1) + '%');
                this.updateElement('average-profit-rate', (data.summary.average_profit_rate * 100).toFixed(2) + '%');
            }
            
        } catch (error) {
            console.error('更新收益分布图表失败:', error);
        }
    }
    
    updateHoldingsTable(data) {
        if (!data || !data.holdings) return;
        
        const tableBody = document.querySelector('#holdings-table tbody');
        if (!tableBody) return;
        
        // 清空现有内容
        tableBody.innerHTML = '';
        
        // 添加新数据
        Object.entries(data.holdings).forEach(([stockCode, holding]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${stockCode}</td>
                <td>${holding.stock_name}</td>
                <td>${holding.quantity}</td>
                <td>¥${holding.avg_cost.toFixed(2)}</td>
                <td>¥${holding.current_price.toFixed(2)}</td>
                <td>¥${holding.market_value.toFixed(2)}</td>
                <td class="${holding.profit_amount >= 0 ? 'text-danger' : 'text-success'}">
                    ¥${holding.profit_amount.toFixed(2)}
                </td>
                <td class="${holding.profit_rate >= 0 ? 'text-danger' : 'text-success'}">
                    ${(holding.profit_rate * 100).toFixed(2)}%
                </td>
            `;
            tableBody.appendChild(row);
        });
        
        // 更新持仓汇总
        if (data.summary) {
            this.updateElement('holdings-total-cost', '¥' + data.summary.total_cost.toFixed(2));
            this.updateElement('holdings-total-value', '¥' + data.summary.total_market_value.toFixed(2));
            this.updateElement('holdings-total-profit', '¥' + data.summary.total_profit.toFixed(2));
            this.updateElement('holdings-profit-rate', data.summary.total_profit_rate.toFixed(2) + '%');
        }
    }
    
    animateValue(elementId, targetValue, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseFloat(element.textContent.replace(/[^\d.-]/g, '')) || 0;
        const duration = 1000; // 1秒动画
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // 使用缓动函数
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (targetValue - startValue) * easeOutQuart;
            
            element.textContent = suffix + currentValue.toFixed(2);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    animateValuePercentage(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        // 从当前显示的百分比中提取数值
        const currentText = element.textContent.replace('%', '');
        const startValue = parseFloat(currentText) || 0;
        const targetPercentage = (targetValue || 0) * 100; // 转换为百分比
        const duration = 1000; // 1秒动画
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // 使用缓动函数
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (targetPercentage - startValue) * easeOutQuart;
            
            element.textContent = currentValue.toFixed(2) + '%';
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }
    
    updateProfitIndicator(elementId, value) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        element.classList.remove('text-success', 'text-danger', 'text-muted');
        
        if (value > 0) {
            element.classList.add('text-success');
        } else if (value < 0) {
            element.classList.add('text-danger');
        } else {
            element.classList.add('text-muted');
        }
    }
    
    updateOrCreateChart(canvasId, config) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        // 如果图表已存在，销毁它
        if (window.charts && window.charts[canvasId]) {
            window.charts[canvasId].destroy();
        }
        
        // 创建新图表
        if (!window.charts) {
            window.charts = {};
        }
        
        const ctx = canvas.getContext('2d');
        window.charts[canvasId] = new Chart(ctx, config);
    }
    
    startPeriodicUpdates() {
        // 清除现有定时器
        this.clearAllTimers();
        
        // 设置不同数据的更新频率
        this.updateTimers.set('overall', setInterval(() => {
            this.updateOverallStatisticsIncremental();
        }, 30000)); // 30秒
        
        this.updateTimers.set('holdings', setInterval(() => {
            this.updateHoldingsIncremental();
        }, 60000)); // 1分钟
        
        this.updateTimers.set('monthly', setInterval(() => {
            this.updateMonthlyStatisticsIncremental();
        }, 300000)); // 5分钟
    }
    
    async updateOverallStatisticsIncremental() {
        if (this.isLoading || document.visibilityState === 'hidden') return;
        
        try {
            const data = await this.loadOverallStatistics();
            this.updateOverallStatistics(data);
            this.updateLastUpdateTime();
        } catch (error) {
            console.error('增量更新总体统计失败:', error);
            this.handleUpdateError(error);
        }
    }
    
    async updateHoldingsIncremental() {
        if (this.isLoading || document.visibilityState === 'hidden') return;
        
        try {
            const data = await this.loadCurrentHoldings();
            this.updateHoldingsTable(data);
            this.updateLastUpdateTime();
        } catch (error) {
            console.error('增量更新持仓数据失败:', error);
            this.handleUpdateError(error);
        }
    }
    
    async updateMonthlyStatisticsIncremental() {
        if (this.isLoading || document.visibilityState === 'hidden') return;
        
        try {
            const data = await this.loadMonthlyStatistics();
            this.updateMonthlyChart(data);
            this.updateLastUpdateTime();
        } catch (error) {
            console.error('增量更新月度统计失败:', error);
            this.handleUpdateError(error);
        }
    }
    
    pauseUpdates() {
        this.clearAllTimers();
    }
    
    resumeUpdates() {
        this.startPeriodicUpdates();
        // 立即执行一次更新
        this.updateOverallStatisticsIncremental();
    }
    
    clearAllTimers() {
        this.updateTimers.forEach((timer) => {
            clearInterval(timer);
        });
        this.updateTimers.clear();
    }
    
    async forceRefresh() {
        // 清除所有缓存
        this.cache.clear();
        
        // 重新加载所有数据
        await this.loadInitialData();
        
        this.showMessage('数据已刷新', 'success');
    }
    
    showLoading(show) {
        this.isLoading = show;
        const loadingElement = document.getElementById('dashboard-loading');
        if (loadingElement) {
            loadingElement.style.display = show ? 'block' : 'none';
        }
        
        // 禁用/启用刷新按钮
        const refreshBtn = document.getElementById('refresh-dashboard');
        if (refreshBtn) {
            refreshBtn.disabled = show;
        }
    }
    
    handleLoadError(error) {
        this.retryCount++;
        
        if (this.retryCount <= this.maxRetries) {
            console.log(`重试加载数据 (${this.retryCount}/${this.maxRetries})`);
            setTimeout(() => {
                this.loadInitialData();
            }, 2000 * this.retryCount); // 递增延迟
        } else {
            this.showMessage('数据加载失败，请检查网络连接', 'error');
        }
    }
    
    handleUpdateError(error) {
        console.error('更新数据失败:', error);
        // 静默处理增量更新错误，不影响用户体验
    }
    
    showMessage(message, type = 'info') {
        // 创建消息提示
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        messageDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // 添加到页面顶部
        const container = document.querySelector('.container-fluid') || document.body;
        container.insertBefore(messageDiv, container.firstChild);
        
        // 自动消失
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }
    
    showNetworkStatus(message, type) {
        const statusElement = document.getElementById('network-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `alert alert-${type}`;
            statusElement.style.display = 'block';
            
            setTimeout(() => {
                statusElement.style.display = 'none';
            }, 3000);
        }
    }
    
    updateLastUpdateTime() {
        this.lastUpdateTime = new Date();
        const timeElement = document.getElementById('last-update-time');
        if (timeElement) {
            timeElement.textContent = `最后更新: ${this.lastUpdateTime.toLocaleTimeString()}`;
        }
    }
    
    setupVisibilityChangeHandler() {
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && this.lastUpdateTime) {
                const timeSinceUpdate = Date.now() - this.lastUpdateTime.getTime();
                // 如果页面隐藏超过5分钟，重新加载数据
                if (timeSinceUpdate > 5 * 60 * 1000) {
                    this.forceRefresh();
                }
            }
        });
    }
    
    // 缓存管理方法
    getFromCache(key) {
        return this.cache.get(key);
    }
    
    setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }
    
    isCacheValid(cached, maxAge) {
        return cached && (Date.now() - cached.timestamp) < maxAge;
    }
    
    // 清理过期缓存
    cleanupCache() {
        const now = Date.now();
        const maxAge = 30 * 60 * 1000; // 30分钟
        
        for (const [key, cached] of this.cache.entries()) {
            if (now - cached.timestamp > maxAge) {
                this.cache.delete(key);
            }
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    window.optimizedDashboard = new OptimizedDashboard();
    
    // 定期清理缓存
    setInterval(() => {
        window.optimizedDashboard.cleanupCache();
    }, 10 * 60 * 1000); // 每10分钟清理一次
});

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OptimizedDashboard;
}