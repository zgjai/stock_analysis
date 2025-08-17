// 仪表板页面逻辑
let profitChart = null;
let distributionChart = null;

function initDashboard() {
    console.log('Starting dashboard initialization...');
    
    // 立即清除加载状态
    const loadingModal = document.getElementById('loadingModal');
    if (loadingModal) {
        loadingModal.classList.remove('show');
        loadingModal.style.display = 'none';
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) backdrop.remove();
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
    }
    
    // 创建安全的showLoading函数
    if (typeof showLoading !== 'function') {
        window.showLoading = function(show) {
            console.log('Loading state:', show);
            // 不显示加载模态框，避免卡住
        };
    }
    
    console.log('Loading dashboard data...');
    
    // 直接加载数据，不使用加载状态
    loadDashboardData();
    initCharts();
    setupRefreshButton();
}

async function loadDashboardData() {
    console.log('Loading dashboard data...');
    
    // 先显示默认数据，避免页面空白
    updateStatsCards({
        total_trades: 0,
        total_return_rate: 0,
        current_holdings_count: 0,
        success_rate: 0
    });
    updateRecentTrades([]);
    updateHoldingAlerts([]);
    
    try {
        // 检查apiClient是否存在
        if (typeof apiClient === 'undefined') {
            console.error('apiClient not available');
            return;
        }
        
        // 设置较短的超时时间，避免长时间等待
        const timeout = 3000; // 3秒超时
        
        // 分步加载数据，每个请求都有独立的超时处理
        console.log('Loading overview data...');
        try {
            const overview = await Promise.race([
                apiClient.getAnalyticsOverview(),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), timeout))
            ]);
            if (overview && overview.data) {
                updateStatsCards(overview.data);
                console.log('Overview data updated');
            }
        } catch (error) {
            console.warn('Failed to load overview:', error.message);
            // 保持默认数据，不阻塞页面
        }
        
        console.log('Loading trades data...');
        try {
            const recentTrades = await Promise.race([
                apiClient.getTrades({ limit: 5, order: 'desc' }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), timeout))
            ]);
            if (recentTrades && recentTrades.data) {
                const tradesData = recentTrades.data;
                const tradesList = Array.isArray(tradesData) ? tradesData : (tradesData.trades || []);
                updateRecentTrades(tradesList);
                console.log('Trades data updated');
            }
        } catch (error) {
            console.warn('Failed to load trades:', error.message);
            // 保持空数组，显示"暂无数据"
        }
        
        console.log('Loading alerts data...');
        try {
            const holdingAlerts = await Promise.race([
                apiClient.getHoldingAlerts(),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), timeout))
            ]);
            if (holdingAlerts && holdingAlerts.data) {
                updateHoldingAlerts(holdingAlerts.data);
                console.log('Alerts data updated');
            }
        } catch (error) {
            console.warn('Failed to load alerts:', error.message);
            // 保持空数组，显示"暂无数据"
        }
        
        // 异步更新图表，不阻塞主要内容
        setTimeout(() => {
            updateCharts().catch(error => {
                console.warn('Failed to update charts:', error.message);
            });
        }, 100);
        
        console.log('Dashboard data loading completed');
        
    } catch (error) {
        console.error('Dashboard loading error:', error);
        // 确保即使出错也显示基本界面
        updateStatsCards({
            total_trades: 0,
            total_return_rate: 0,
            current_holdings_count: 0,
            success_rate: 0
        });
        updateRecentTrades([]);
        updateHoldingAlerts([]);
    }
}

function updateStatsCards(data) {
    // 更新总交易次数
    const totalTradesElement = document.getElementById('total-trades');
    if (totalTradesElement) {
        const totalTrades = (data.total_buy_count || 0) + (data.total_sell_count || 0);
        totalTradesElement.textContent = totalTrades;
    }

    // 更新总收益率
    const totalProfitElement = document.getElementById('total-profit');
    if (totalProfitElement) {
        const profit = (data.total_return_rate || 0) / 100; // 转换为小数
        totalProfitElement.textContent = Formatters.percentage(profit);
        // 移除之前的颜色类，根据盈亏情况添加新的颜色
        totalProfitElement.className = 'stats-value';
        if (profit > 0) {
            totalProfitElement.style.color = '#28a745'; // 绿色表示盈利
        } else if (profit < 0) {
            totalProfitElement.style.color = '#dc3545'; // 红色表示亏损
        } else {
            totalProfitElement.style.color = '#6c757d'; // 灰色表示持平
        }
    }

    // 更新当前持仓
    const currentHoldingsElement = document.getElementById('current-holdings');
    if (currentHoldingsElement) {
        currentHoldingsElement.textContent = data.current_holdings_count || 0;
    }

    // 更新成功率
    const successRateElement = document.getElementById('success-rate');
    if (successRateElement) {
        const rate = (data.success_rate || 0) / 100; // 转换为小数
        successRateElement.textContent = Formatters.percentage(rate);
    }
}

function updateRecentTrades(trades) {
    const tbody = document.getElementById('recent-trades');
    if (!tbody) return;

    if (!trades || trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">暂无交易记录</td></tr>';
        return;
    }

    tbody.innerHTML = trades.map(trade => `
        <tr>
            <td>${Formatters.date(trade.trade_date)}</td>
            <td>
                <span class="fw-bold">${trade.stock_name}</span>
                <small class="text-muted d-block">${trade.stock_code}</small>
            </td>
            <td>
                <span class="badge ${trade.trade_type === 'buy' ? 'bg-success' : 'bg-danger'}">
                    ${trade.trade_type === 'buy' ? '买入' : '卖出'}
                </span>
            </td>
            <td>${Formatters.currency(trade.price)}</td>
            <td>${Formatters.number(trade.quantity, 0)}</td>
        </tr>
    `).join('');
}

function updateHoldingAlerts(alerts) {
    const container = document.getElementById('holding-alerts');
    if (!container) return;

    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<div class="text-center text-muted">暂无持仓提醒</div>';
        return;
    }

    container.innerHTML = alerts.map(alert => `
        <div class="alert alert-${getAlertClass(alert.alert_type)} alert-dismissible fade show" role="alert">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="alert-heading mb-1">${alert.stock_name} (${alert.stock_code})</h6>
                    <p class="mb-1">${alert.alert_message}</p>
                    <small class="text-muted">
                        持仓天数: ${alert.holding_days}天 | 
                        盈亏: ${Formatters.percentage(alert.profit_loss_ratio)}
                    </small>
                </div>
                <div class="text-end">
                    ${alert.sell_ratio > 0 ? `
                        <span class="badge bg-warning">
                            建议卖出 ${Formatters.percentage(alert.sell_ratio)}
                        </span>
                    ` : ''}
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `).join('');
}

function getAlertClass(alertType) {
    const classes = {
        'sell_all': 'danger',
        'sell_partial': 'warning',
        'hold': 'info'
    };
    return classes[alertType] || 'info';
}

async function updateCharts() {
    try {
        const [monthlyData, distributionData] = await Promise.all([
            apiClient.getMonthlyAnalytics(),
            apiClient.getProfitDistribution()
        ]);

        updateProfitChart(monthlyData.data);
        updateDistributionChart(distributionData.data);
    } catch (error) {
        console.error('Failed to update charts:', error);
    }
}

function initCharts() {
    // 检查 Chart.js 是否可用
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }

    // 初始化收益趋势图
    const profitCtx = document.getElementById('profitChart');
    if (profitCtx) {
        profitChart = new Chart(profitCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '月度收益率',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
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
                                return Formatters.percentage(value);
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `收益率: ${Formatters.percentage(context.parsed.y)}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 初始化收益分布图
    const distributionCtx = document.getElementById('distributionChart');
    if (distributionCtx) {
        distributionChart = new Chart(distributionCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
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
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value}只 (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
}

function updateProfitChart(data) {
    if (!profitChart || !data) return;

    // 处理数据格式 - data 可能是数组或包含数组的对象
    const chartData = Array.isArray(data) ? data : (data.monthly_data || data.data || []);
    
    if (!Array.isArray(chartData) || chartData.length === 0) {
        console.warn('No valid chart data for profit chart');
        return;
    }

    const labels = chartData.map(item => item.month_name || item.month);
    const profits = chartData.map(item => item.profit_rate || 0);

    profitChart.data.labels = labels;
    profitChart.data.datasets[0].data = profits;
    profitChart.update();
}

function updateDistributionChart(data) {
    if (!distributionChart || !data) return;

    // 处理数据格式 - data 可能是数组或包含数组的对象
    const chartData = Array.isArray(data) ? data : (data.profit_ranges || data.data || []);
    
    if (!Array.isArray(chartData) || chartData.length === 0) {
        console.warn('No valid chart data for distribution chart');
        return;
    }

    // 过滤掉计数为0的区间，使图表更清晰
    const filteredData = chartData.filter(item => (item.count || 0) > 0);
    
    if (filteredData.length === 0) {
        console.warn('No data with counts > 0 for distribution chart');
        return;
    }

    const labels = filteredData.map(item => item.range);
    const counts = filteredData.map(item => item.count || 0);

    distributionChart.data.labels = labels;
    distributionChart.data.datasets[0].data = counts;
    distributionChart.update();
}

function setupRefreshButton() {
    const refreshBtn = document.querySelector('[onclick="refreshData()"]');
    if (refreshBtn) {
        refreshBtn.onclick = async () => {
            await refreshData();
        };
    }
}

async function refreshData() {
    try {
        showLoading(true);
        
        // 刷新股票价格
        await apiClient.refreshPrices();
        
        // 重新加载仪表板数据
        await loadDashboardData();
        
        showMessage('数据刷新成功', 'success');
    } catch (error) {
        console.error('Failed to refresh data:', error);
        showMessage('数据刷新失败', 'error');
    } finally {
        showLoading(false);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, current path:', window.location.pathname);
    
    // 立即清除任何可能的加载状态
    const loadingModal = document.getElementById('loadingModal');
    if (loadingModal) {
        loadingModal.classList.remove('show');
        loadingModal.style.display = 'none';
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) backdrop.remove();
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }
    
    if (window.location.pathname === '/' || window.location.pathname.includes('dashboard')) {
        console.log('Initializing dashboard...');
        
        // 简化初始化，直接开始
        setTimeout(() => {
            try {
                initDashboard();
            } catch (error) {
                console.error('Failed to initialize dashboard:', error);
                // 确保清除加载状态
                if (loadingModal) {
                    loadingModal.classList.remove('show');
                    loadingModal.style.display = 'none';
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) backdrop.remove();
                }
                // 显示基本内容，不阻塞页面
                updateStatsCards({
                    total_trades: 0,
                    total_return_rate: 0,
                    current_holdings_count: 0,
                    success_rate: 0
                });
                updateRecentTrades([]);
                updateHoldingAlerts([]);
            }
        }, 100);
    }
});

// 导出函数供全局使用
window.initDashboard = initDashboard;
window.refreshData = refreshData;