from flask import Blueprint, render_template, request, jsonify, current_app
import os

# 创建前端路由蓝图
frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    """首页重定向到仪表板"""
    return render_template('dashboard.html')

@frontend_bp.route('/dashboard')
def dashboard():
    """仪表板页面"""
    return render_template('dashboard.html')

@frontend_bp.route('/trading-records')
def trading_records():
    """交易记录页面"""
    return render_template('trading_records.html')

@frontend_bp.route('/review')
def review():
    """复盘分析页面"""
    return render_template('review.html')

@frontend_bp.route('/stock-pool')
def stock_pool():
    """股票池管理页面"""
    return render_template('stock_pool.html')

@frontend_bp.route('/sector-analysis')
def sector_analysis():
    """板块分析页面"""
    return render_template('sector_analysis.html')

@frontend_bp.route('/cases')
def cases():
    """案例管理页面"""
    return render_template('cases.html')

@frontend_bp.route('/analytics')
def analytics():
    """统计分析页面"""
    return render_template('analytics.html')

@frontend_bp.route('/non-trading-days')
def non_trading_days():
    """非交易日配置页面"""
    return render_template('non_trading_days.html')

@frontend_bp.route('/profit-distribution-config')
def profit_distribution_config():
    """收益分布配置页面"""
    return render_template('profit_distribution_config.html')

@frontend_bp.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': '系统运行正常'
    })

@frontend_bp.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return render_template('404.html'), 404

@frontend_bp.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return render_template('500.html'), 500

# 临时调试路由

from flask import render_template_string

@frontend_bp.route('/debug-analytics')
def debug_analytics():
    """调试Analytics页面"""
    return render_template_string("""<!DOCTYPE html>
<html>
<head>
    <title>Analytics 详细调试</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .result { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .error { background: #ffebee; color: #c62828; }
        .success { background: #e8f5e9; color: #2e7d32; }
        .warning { background: #fff3e0; color: #f57c00; }
        pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
        .card { border: 1px solid #ddd; padding: 15px; margin: 10px; display: inline-block; min-width: 200px; }
    </style>
</head>
<body>
    <h1>Analytics 页面详细调试</h1>
    
    <div class="section">
        <h2>1. API 测试</h2>
        <button onclick="testDirectAPI()">直接测试 API</button>
        <button onclick="testWithApiClient()">使用 ApiClient 测试</button>
        <div id="api-results"></div>
    </div>
    
    <div class="section">
        <h2>2. 模拟前端渲染</h2>
        <button onclick="simulateRender()">模拟 renderOverview</button>
        <div id="render-results"></div>
        
        <!-- 模拟的显示卡片 -->
        <div class="card">
            <h6>总收益率</h6>
            <h4 id="test-total-return-rate">-</h4>
        </div>
        <div class="card">
            <h6>成功率</h6>
            <h4 id="test-success-rate">-</h4>
        </div>
        <div class="card">
            <h6>已清仓收益</h6>
            <h4 id="test-closed-profit">-</h4>
        </div>
        <div class="card">
            <h6>持仓收益</h6>
            <h4 id="test-holding-profit">-</h4>
        </div>
    </div>
    
    <div class="section">
        <h2>3. 检查实际页面元素</h2>
        <button onclick="checkPageElements()">检查页面元素</button>
        <div id="element-results"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/axios@1.4.0/dist/axios.min.js"></script>
    <script>
        let lastApiData = null;
        
        async function testDirectAPI() {
            const resultsDiv = document.getElementById('api-results');
            resultsDiv.innerHTML = '';
            
            try {
                addResult('api-results', '🔄 直接请求 /api/analytics/overview...', 'result');
                
                const response = await fetch('/api/analytics/overview');
                const data = await response.json();
                
                addResult('api-results', `📡 响应状态: ${response.status}`, response.ok ? 'success' : 'error');
                addResult('api-results', '📦 完整响应:', 'result');
                addResult('api-results', JSON.stringify(data, null, 2), 'result');
                
                if (data.success && data.data) {
                    lastApiData = data.data;
                    
                    addResult('api-results', '🔍 关键数据分析:', 'success');
                    addResult('api-results', `total_return_rate: ${data.data.total_return_rate} (${typeof data.data.total_return_rate})`, 'result');
                    addResult('api-results', `success_rate: ${data.data.success_rate} (${typeof data.data.success_rate})`, 'result');
                    addResult('api-results', `closed_profit: ${data.data.closed_profit} (${typeof data.data.closed_profit})`, 'result');
                    addResult('api-results', `holding_profit: ${data.data.holding_profit} (${typeof data.data.holding_profit})`, 'result');
                }
                
            } catch (error) {
                addResult('api-results', `❌ 请求失败: ${error.message}`, 'error');
            }
        }
        
        async function testWithApiClient() {
            const resultsDiv = document.getElementById('api-results');
            
            try {
                // 检查 apiClient 是否存在
                if (typeof window.apiClient === 'undefined') {
                    addResult('api-results', '⚠️ window.apiClient 不存在，尝试创建...', 'warning');
                    
                    // 尝试加载 API 客户端
                    const script = document.createElement('script');
                    script.src = '/static/js/api.js';
                    document.head.appendChild(script);
                    
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
                
                if (typeof window.apiClient !== 'undefined') {
                    addResult('api-results', '🔄 使用 ApiClient 请求...', 'result');
                    
                    const response = await window.apiClient.getAnalyticsOverview();
                    
                    addResult('api-results', '📦 ApiClient 响应:', 'result');
                    addResult('api-results', JSON.stringify(response, null, 2), 'result');
                    
                    if (response.success && response.data) {
                        lastApiData = response.data;
                    }
                } else {
                    addResult('api-results', '❌ 无法加载 ApiClient', 'error');
                }
                
            } catch (error) {
                addResult('api-results', `❌ ApiClient 请求失败: ${error.message}`, 'error');
            }
        }
        
        function simulateRender() {
            const resultsDiv = document.getElementById('render-results');
            resultsDiv.innerHTML = '';
            
            if (!lastApiData) {
                addResult('render-results', '⚠️ 请先运行 API 测试获取数据', 'warning');
                return;
            }
            
            addResult('render-results', '🎨 模拟 renderOverview 函数...', 'result');
            
            // 模拟 analytics.html 中的 renderOverview 函数
            const data = lastApiData;
            
            // 总收益率
            const returnRateText = data.total_return_rate ? 
                `${(data.total_return_rate * 100).toFixed(2)}%` : '0.00%';
            document.getElementById('test-total-return-rate').textContent = returnRateText;
            addResult('render-results', `总收益率计算: ${data.total_return_rate} * 100 = ${returnRateText}`, 'success');
            
            // 成功率
            const successRateText = data.success_rate ? 
                `${(data.success_rate * 100).toFixed(1)}%` : '0.0%';
            document.getElementById('test-success-rate').textContent = successRateText;
            addResult('render-results', `成功率计算: ${data.success_rate} * 100 = ${successRateText}`, 'success');
            
            // 已清仓收益
            const closedProfitText = data.closed_profit ? 
                `¥${data.closed_profit.toFixed(2)}` : '¥0.00';
            document.getElementById('test-closed-profit').textContent = closedProfitText;
            addResult('render-results', `已清仓收益: ${closedProfitText}`, 'success');
            
            // 持仓收益
            const holdingProfitText = data.holding_profit ? 
                `¥${data.holding_profit.toFixed(2)}` : '¥0.00';
            document.getElementById('test-holding-profit').textContent = holdingProfitText;
            addResult('render-results', `持仓收益: ${holdingProfitText}`, 'success');
            
            addResult('render-results', '✅ 渲染完成，检查上方的卡片显示', 'success');
        }
        
        function checkPageElements() {
            const resultsDiv = document.getElementById('element-results');
            resultsDiv.innerHTML = '';
            
            addResult('element-results', '🔍 检查实际页面元素...', 'result');
            
            // 检查是否在 analytics 页面
            const isAnalyticsPage = window.location.pathname.includes('analytics');
            addResult('element-results', `当前页面: ${window.location.pathname}`, isAnalyticsPage ? 'success' : 'warning');
            
            if (!isAnalyticsPage) {
                addResult('element-results', '⚠️ 不在 analytics 页面，无法检查元素', 'warning');
                return;
            }
            
            // 检查关键元素
            const elements = [
                'total-return-rate',
                'success-rate', 
                'closed-profit',
                'holding-profit'
            ];
            
            elements.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    const currentValue = element.textContent;
                    addResult('element-results', `✅ ${id}: "${currentValue}"`, 'success');
                } else {
                    addResult('element-results', `❌ 未找到元素: ${id}`, 'error');
                }
            });
            
            // 检查是否有 AnalyticsManager
            if (typeof window.analyticsManager !== 'undefined') {
                addResult('element-results', '✅ AnalyticsManager 存在', 'success');
            } else {
                addResult('element-results', '❌ AnalyticsManager 不存在', 'error');
            }
        }
        
        function addResult(containerId, message, className) {
            const container = document.getElementById(containerId);
            const div = document.createElement('div');
            div.className = `result ${className}`;
            div.textContent = message;
            container.appendChild(div);
        }
        
        // 页面加载时自动运行基本测试
        window.addEventListener('load', () => {
            setTimeout(() => {
                testDirectAPI();
            }, 1000);
        });
    </script>
</body>
</html>""")
