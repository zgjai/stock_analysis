#!/usr/bin/env python3
"""
简单的演示服务器，用于测试加载状态修复效果
"""
from flask import Flask, render_template_string, jsonify
import time
import random

app = Flask(__name__)

# 模拟API延迟
SIMULATE_DELAY = True
DELAY_SECONDS = 2  # 模拟2秒延迟

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加载状态修复演示</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>加载状态修复演示</h1>
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            这个演示展示了修复后的加载状态处理。API请求有2秒延迟，但页面会立即显示默认状态。
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>仪表板数据</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <div class="text-center">
                                    <h4 id="total-trades" class="text-primary">0</h4>
                                    <small>总交易次数</small>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="text-center">
                                    <h4 id="total-profit" class="text-success">0.00%</h4>
                                    <small>总收益率</small>
                                </div>
                            </div>
                        </div>
                        <button class="btn btn-primary mt-3" onclick="loadData()">加载数据</button>
                        <button class="btn btn-warning mt-3" onclick="testTimeout()">测试超时</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>状态演示</h5>
                    </div>
                    <div class="card-body">
                        <div id="status-demo" style="min-height: 100px;">
                            <div class="text-center text-muted">
                                <i class="fas fa-play-circle fa-2x mb-2"></i>
                                <p>点击按钮测试不同状态</p>
                            </div>
                        </div>
                        <button class="btn btn-info btn-sm" onclick="showLoading()">加载状态</button>
                        <button class="btn btn-secondary btn-sm" onclick="showEmpty()">空状态</button>
                        <button class="btn btn-danger btn-sm" onclick="showError()">错误状态</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 模拟NoDataHandler
        class NoDataHandler {
            static showLoadingState(containerId, message = '加载中...') {
                const container = document.getElementById(containerId);
                if (container) {
                    container.innerHTML = `
                        <div class="text-center text-muted py-4">
                            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                            ${message}
                        </div>
                    `;
                }
            }
            
            static showEmptyState(containerId, message = '暂无数据') {
                const container = document.getElementById(containerId);
                if (container) {
                    container.innerHTML = `
                        <div class="text-center text-muted py-4">
                            <i class="fas fa-inbox fa-2x mb-3"></i>
                            <p>${message}</p>
                            <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                                <i class="fas fa-refresh"></i> 重新加载
                            </button>
                        </div>
                    `;
                }
            }
            
            static showErrorState(containerId, error = '加载失败') {
                const container = document.getElementById(containerId);
                if (container) {
                    container.innerHTML = `
                        <div class="text-center text-muted py-4">
                            <i class="fas fa-exclamation-triangle fa-2x mb-3 text-warning"></i>
                            <p>${error}</p>
                            <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                                <i class="fas fa-refresh"></i> 重新加载
                            </button>
                        </div>
                    `;
                }
            }
            
            static withTimeout(promise, timeoutMs = 3000) {
                return Promise.race([
                    promise,
                    new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('请求超时')), timeoutMs)
                    )
                ]);
            }
        }
        
        async function loadData() {
            // 立即显示默认数据
            document.getElementById('total-trades').textContent = '0';
            document.getElementById('total-profit').textContent = '0.00%';
            
            try {
                // 模拟API请求
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                
                // 更新数据
                document.getElementById('total-trades').textContent = data.total_trades;
                document.getElementById('total-profit').textContent = data.total_profit + '%';
                
                alert('数据加载成功！');
            } catch (error) {
                alert('加载失败: ' + error.message);
            }
        }
        
        async function testTimeout() {
            try {
                // 测试超时机制
                await NoDataHandler.withTimeout(
                    fetch('/api/slow'),  // 这个接口会延迟5秒
                    3000  // 3秒超时
                );
                alert('请求成功');
            } catch (error) {
                alert('超时测试: ' + error.message);
            }
        }
        
        function showLoading() {
            NoDataHandler.showLoadingState('status-demo', '正在加载数据...');
        }
        
        function showEmpty() {
            NoDataHandler.showEmptyState('status-demo', '暂无数据');
        }
        
        function showError() {
            NoDataHandler.showErrorState('status-demo', '网络连接失败');
        }
    </script>
</body>
</html>
    """)

@app.route('/api/dashboard')
def api_dashboard():
    if SIMULATE_DELAY:
        time.sleep(DELAY_SECONDS)
    
    return jsonify({
        'total_trades': random.randint(10, 100),
        'total_profit': round(random.uniform(-5, 15), 2)
    })

@app.route('/api/slow')
def api_slow():
    time.sleep(5)  # 5秒延迟，用于测试超时
    return jsonify({'message': 'slow response'})

if __name__ == '__main__':
    print("启动演示服务器...")
    print("访问 http://localhost:5001 查看效果")
    app.run(debug=True, port=5001)
