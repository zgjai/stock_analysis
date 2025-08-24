#!/usr/bin/env python3
"""
修复复盘页面加载问题
解决浮盈计算器初始化错误和页面一直显示"加载中"的问题
"""

import os
import sys

def fix_review_loading_issue():
    """修复复盘页面加载问题"""
    
    print("开始修复复盘页面加载问题...")
    
    # 1. 检查并修复JavaScript文件的依赖问题
    print("\n1. 检查JavaScript依赖...")
    
    utils_js_path = "static/js/utils.js"
    if os.path.exists(utils_js_path):
        print("✓ utils.js 文件存在")
        
        # 检查是否包含debounce和throttle函数
        with open(utils_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'debounce' in content and 'throttle' in content:
            print("✓ debounce 和 throttle 函数已存在")
        else:
            print("❌ debounce 或 throttle 函数缺失")
            return False
    else:
        print("❌ utils.js 文件不存在")
        return False
    
    # 2. 检查浮盈计算器文件
    print("\n2. 检查浮盈计算器...")
    
    calculator_js_path = "static/js/floating-profit-calculator.js"
    if os.path.exists(calculator_js_path):
        print("✓ floating-profit-calculator.js 文件存在")
        
        # 检查是否有绑定错误的方法
        with open(calculator_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'this.calculateProfit.bind(this)' in content:
            print("❌ 发现错误的方法绑定")
            return False
        else:
            print("✓ 方法绑定已修复")
    else:
        print("❌ floating-profit-calculator.js 文件不存在")
        return False
    
    # 3. 检查复盘集成管理器
    print("\n3. 检查复盘集成管理器...")
    
    integration_js_path = "static/js/review-integration.js"
    if os.path.exists(integration_js_path):
        print("✓ review-integration.js 文件存在")
    else:
        print("❌ review-integration.js 文件不存在")
        return False
    
    # 4. 创建加载状态强制清理脚本
    print("\n4. 创建加载状态强制清理脚本...")
    
    cleanup_script = """
// 强制清理加载状态的脚本
function forceCleanupLoadingStates() {
    console.log('强制清理所有加载状态...');
    
    // 清理全局加载遮罩
    const globalOverlay = document.getElementById('global-loading-overlay');
    if (globalOverlay) {
        globalOverlay.style.display = 'none';
        try {
            globalOverlay.remove();
        } catch (e) {
            console.warn('无法移除全局遮罩:', e);
        }
    }
    
    // 清理所有加载元素
    const loadingElements = document.querySelectorAll(
        '*[id*="loading"], *[class*="loading"], .modal-backdrop, .loading-overlay, .spinner-border'
    );
    
    loadingElements.forEach(element => {
        if (element && element.style) {
            element.style.display = 'none';
            // 不要移除所有spinner，只移除遮罩层的
            if (element.classList.contains('modal-backdrop') || 
                element.classList.contains('loading-overlay')) {
                try {
                    element.remove();
                } catch (e) {
                    console.warn('无法移除加载元素:', e);
                }
            }
        }
    });
    
    // 重置body样式
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
    document.documentElement.style.overflow = '';
    
    // 清理持续显示"加载中"的内容区域
    const loadingContainers = document.querySelectorAll('*');
    loadingContainers.forEach(container => {
        if (container.textContent && container.textContent.includes('加载中...')) {
            // 检查是否是持续显示加载中的容器
            const parent = container.closest('.card-body, .list-group, .table-responsive');
            if (parent && !parent.querySelector('button, input, select')) {
                // 如果是纯显示容器且没有交互元素，替换为错误状态
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="bi bi-exclamation-triangle fs-1 d-block mb-2 text-warning"></i>
                        <div class="mb-2">数据加载失败</div>
                        <small class="text-muted">请刷新页面重试</small>
                        <br>
                        <button class="btn btn-outline-primary btn-sm mt-2" onclick="location.reload()">
                            <i class="bi bi-arrow-clockwise"></i> 刷新页面
                        </button>
                    </div>
                `;
            }
        }
    });
    
    console.log('加载状态清理完成');
}

// 页面加载完成后延迟执行清理
document.addEventListener('DOMContentLoaded', () => {
    // 10秒后如果还有加载状态，强制清理
    setTimeout(() => {
        const hasLoadingElements = document.querySelector('*[class*="spinner"], *:contains("加载中")');
        if (hasLoadingElements) {
            console.warn('检测到持续的加载状态，执行强制清理...');
            forceCleanupLoadingStates();
        }
    }, 10000);
});

// 提供全局清理函数
window.forceCleanupLoadingStates = forceCleanupLoadingStates;
"""
    
    cleanup_js_path = "static/js/loading-cleanup.js"
    with open(cleanup_js_path, 'w', encoding='utf-8') as f:
        f.write(cleanup_script)
    
    print(f"✓ 创建加载状态清理脚本: {cleanup_js_path}")
    
    # 5. 创建调试页面
    print("\n5. 创建调试页面...")
    
    debug_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>复盘页面调试</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h2>复盘页面调试工具</h2>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5>系统状态检查</h5>
                    </div>
                    <div class="card-body">
                        <div id="status-log" class="small" style="height: 400px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 4px;">
                            <div class="text-muted">等待检查...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>操作面板</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <button id="check-dependencies" class="btn btn-primary">检查依赖</button>
                            <button id="test-calculator" class="btn btn-success">测试计算器</button>
                            <button id="test-integration" class="btn btn-info">测试集成</button>
                            <button id="force-cleanup" class="btn btn-warning">强制清理加载</button>
                            <button id="clear-log" class="btn btn-secondary">清空日志</button>
                        </div>
                        
                        <hr>
                        
                        <div class="mb-3">
                            <label class="form-label">测试股票代码</label>
                            <input type="text" id="test-stock-code" class="form-control" value="000001" placeholder="6位股票代码">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">测试买入价格</label>
                            <input type="number" id="test-buy-price" class="form-control" value="10.50" step="0.01" min="0">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">测试当前价格</label>
                            <input type="number" id="test-current-price" class="form-control" value="11.20" step="0.01" min="0">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/utils.js"></script>
    <script src="/static/js/floating-profit-calculator.js"></script>
    <script src="/static/js/review-integration.js"></script>
    <script src="/static/js/loading-cleanup.js"></script>
    
    <script>
        function log(message, type = 'info') {
            const logContainer = document.getElementById('status-log');
            const timestamp = new Date().toLocaleTimeString();
            const colors = {
                'info': 'text-info',
                'success': 'text-success',
                'error': 'text-danger',
                'warning': 'text-warning'
            };
            
            const logEntry = document.createElement('div');
            logEntry.className = colors[type] || 'text-muted';
            logEntry.innerHTML = `[${timestamp}] ${message}`;
            
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        document.getElementById('clear-log').addEventListener('click', () => {
            document.getElementById('status-log').innerHTML = '<div class="text-muted">日志已清空</div>';
        });
        
        document.getElementById('check-dependencies').addEventListener('click', () => {
            log('开始检查依赖...', 'info');
            
            const dependencies = [
                { name: 'debounce', obj: window.debounce },
                { name: 'throttle', obj: window.throttle },
                { name: 'FloatingProfitCalculator', obj: window.FloatingProfitCalculator },
                { name: 'ReviewIntegrationManager', obj: window.ReviewIntegrationManager },
                { name: 'PerformanceUtils', obj: window.PerformanceUtils }
            ];
            
            dependencies.forEach(dep => {
                if (typeof dep.obj !== 'undefined') {
                    log(`✓ ${dep.name} 可用`, 'success');
                } else {
                    log(`❌ ${dep.name} 不可用`, 'error');
                }
            });
            
            log('依赖检查完成', 'info');
        });
        
        document.getElementById('test-calculator').addEventListener('click', () => {
            log('开始测试浮盈计算器...', 'info');
            
            try {
                const stockCode = document.getElementById('test-stock-code').value;
                const buyPrice = parseFloat(document.getElementById('test-buy-price').value);
                const currentPrice = parseFloat(document.getElementById('test-current-price').value);
                
                const calculator = new FloatingProfitCalculator(stockCode, buyPrice);
                log(`✓ 计算器创建成功 (${stockCode})`, 'success');
                
                calculator.setCurrentPrice(currentPrice);
                log(`✓ 设置当前价格: ${currentPrice}`, 'success');
                
                const result = calculator.getCalculationResult();
                if (result) {
                    log(`✓ 计算结果: ${result.formatted_ratio}`, 'success');
                    log(`  盈亏金额: ¥${result.floating_profit_amount?.toFixed(2) || 'N/A'}`, 'info');
                } else {
                    log('❌ 无法获取计算结果', 'error');
                }
                
            } catch (error) {
                log(`❌ 计算器测试失败: ${error.message}`, 'error');
                console.error('计算器测试失败:', error);
            }
        });
        
        document.getElementById('test-integration').addEventListener('click', async () => {
            log('开始测试集成管理器...', 'info');
            
            try {
                if (typeof ReviewIntegrationManager === 'undefined') {
                    throw new Error('ReviewIntegrationManager 不可用');
                }
                
                const manager = new ReviewIntegrationManager();
                log('✓ 集成管理器创建成功', 'success');
                
                await manager.init();
                log('✓ 集成管理器初始化成功', 'success');
                
                const state = manager.getState();
                log(`✓ 管理器状态: ${JSON.stringify(state, null, 2)}`, 'info');
                
            } catch (error) {
                log(`❌ 集成管理器测试失败: ${error.message}`, 'error');
                console.error('集成管理器测试失败:', error);
            }
        });
        
        document.getElementById('force-cleanup').addEventListener('click', () => {
            log('执行强制清理...', 'warning');
            
            if (typeof forceCleanupLoadingStates === 'function') {
                forceCleanupLoadingStates();
                log('✓ 强制清理完成', 'success');
            } else {
                log('❌ 清理函数不可用', 'error');
            }
        });
        
        // 页面加载完成后自动检查依赖
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                document.getElementById('check-dependencies').click();
            }, 500);
        });
    </script>
</body>
</html>"""
    
    debug_html_path = "debug_review_loading.html"
    with open(debug_html_path, 'w', encoding='utf-8') as f:
        f.write(debug_html)
    
    print(f"✓ 创建调试页面: {debug_html_path}")
    
    print("\n修复完成！")
    print("\n使用说明:")
    print("1. 访问 /debug_review_loading.html 进行系统诊断")
    print("2. 如果复盘页面仍然卡在加载中，可以在浏览器控制台执行:")
    print("   forceCleanupLoadingStates()")
    print("3. 检查浏览器控制台是否有JavaScript错误")
    
    return True

if __name__ == "__main__":
    success = fix_review_loading_issue()
    sys.exit(0 if success else 1)