#!/usr/bin/env python3
"""
简单的测试服务器
用于浏览器兼容性测试
"""

from flask import Flask, render_template_string

app = Flask(__name__)

# 简单的HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票交易记录系统 - 测试页面</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">股票交易记录系统</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">仪表板</a>
                <a class="nav-link" href="/trading_records">交易记录</a>
                <a class="nav-link" href="/stock_pool">股票池</a>
                <a class="nav-link" href="/analytics">统计分析</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>{{ page_title }}</h1>
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">测试内容</h5>
                        <p class="card-text">这是一个用于浏览器兼容性测试的页面。</p>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#testModal">
                            测试模态框
                        </button>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <canvas id="testChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>股票代码</th>
                            <th>股票名称</th>
                            <th>价格</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>000001</td>
                            <td>平安银行</td>
                            <td>12.50</td>
                        </tr>
                        <tr>
                            <td>000002</td>
                            <td>万科A</td>
                            <td>18.30</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- 模态框 -->
    <div class="modal fade" id="testModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">测试模态框</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form>
                        <div class="mb-3">
                            <label for="testInput" class="form-label">测试输入</label>
                            <input type="text" class="form-control" id="testInput" name="test_input">
                        </div>
                        <div class="mb-3">
                            <label for="testSelect" class="form-label">测试选择</label>
                            <select class="form-select" id="testSelect" name="test_select">
                                <option value="">请选择</option>
                                <option value="1">选项1</option>
                                <option value="2">选项2</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    <button type="button" class="btn btn-primary">保存</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 测试Chart.js
        const ctx = document.getElementById('testChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['1月', '2月', '3月', '4月', '5月'],
                datasets: [{
                    label: '收益率',
                    data: [12, 19, 3, 5, 2],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // 测试jQuery
        $(document).ready(function() {
            console.log('jQuery loaded successfully');
        });
        
        // 测试Fetch API
        if (typeof fetch !== 'undefined') {
            console.log('Fetch API is supported');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, page_title="仪表板")

@app.route('/trading_records')
def trading_records():
    return render_template_string(HTML_TEMPLATE, page_title="交易记录")

@app.route('/stock_pool')
def stock_pool():
    return render_template_string(HTML_TEMPLATE, page_title="股票池")

@app.route('/analytics')
def analytics():
    return render_template_string(HTML_TEMPLATE, page_title="统计分析")

@app.route('/review')
def review():
    return render_template_string(HTML_TEMPLATE, page_title="复盘记录")

@app.route('/cases')
def cases():
    return render_template_string(HTML_TEMPLATE, page_title="案例管理")

@app.route('/sector_analysis')
def sector_analysis():
    return render_template_string(HTML_TEMPLATE, page_title="板块分析")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=False)