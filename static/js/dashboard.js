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
    // Removed recent trades and holding alerts functionality
    
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
        
        // Removed recent trades and holding alerts loading functionality
        
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
        // Removed recent trades and holding alerts functionality
    }
}

function updateStatsCards(data) {
    // 更新已清仓收益
    const realizedProfitElement = document.getElementById('realized-profit');
    if (realizedProfitElement) {
        const realizedProfit = data.realized_profit || 0;
        realizedProfitElement.textContent = Formatters.currency(realizedProfit);
        // 根据盈亏情况设置颜色
        realizedProfitElement.className = 'stats-value';
        if (realizedProfit > 0) {
            realizedProfitElement.style.color = '#28a745'; // 绿色表示盈利
        } else if (realizedProfit < 0) {
            realizedProfitElement.style.color = '#dc3545'; // 红色表示亏损
        } else {
            realizedProfitElement.style.color = '#6c757d'; // 灰色表示持平
        }
    }

    // 更新当前持仓收益
    const currentHoldingsProfitElement = document.getElementById('current-holdings-profit');
    if (currentHoldingsProfitElement) {
        const holdingsProfit = data.current_holdings_profit || 0;
        currentHoldingsProfitElement.textContent = Formatters.currency(holdingsProfit);
        // 根据盈亏情况设置颜色
        currentHoldingsProfitElement.className = 'stats-value';
        if (holdingsProfit > 0) {
            currentHoldingsProfitElement.style.color = '#28a745'; // 绿色表示盈利
        } else if (holdingsProfit < 0) {
            currentHoldingsProfitElement.style.color = '#dc3545'; // 红色表示亏损
        } else {
            currentHoldingsProfitElement.style.color = '#6c757d'; // 灰色表示持平
        }
    }

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

    // 更新当前持仓数量
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

    // 更新总投入资金
    const totalInvestmentElement = document.getElementById('total-investment');
    if (totalInvestmentElement) {
        const investment = data.total_investment || 0;
        totalInvestmentElement.textContent = Formatters.currency(investment);
    }

    // 更新最后更新时间
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        if (data.last_updated) {
            const updateTime = new Date(data.last_updated);
            lastUpdatedElement.textContent = updateTime.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit'
            });
        } else {
            lastUpdatedElement.textContent = '--';
        }
    }
}

// Removed updateRecentTrades, updateHoldingAlerts, and getAlertClass functions
// as these modules have been removed from the dashboard interface

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
    // 处理月度收益率数据：null值表示无数据，显示为0但在工具提示中标明
    const profits = chartData.map(item => {
        if (item.profit_rate === null || item.profit_rate === undefined) {
            return null; // Chart.js会跳过null值
        }
        return item.profit_rate;
    });

    profitChart.data.labels = labels;
    profitChart.data.datasets[0].data = profits;
    
    // 更新图表配置以处理null值
    profitChart.options.plugins.tooltip.callbacks.label = function(context) {
        const dataIndex = context.dataIndex;
        const monthData = chartData[dataIndex];
        
        if (monthData.profit_rate === null || !monthData.has_data) {
            return '无交易数据';
        }
        
        return `收益率: ${Formatters.percentage(context.parsed.y)}`;
    };
    
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
                // Removed recent trades and holding alerts functionality
            }
        }, 100);
    }
});

// 导出函数供全局使用
window.initDashboard = initDashboard;
window.refreshData = refreshData;