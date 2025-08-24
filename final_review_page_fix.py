#!/usr/bin/env python3
"""
最终修复复盘页面问题
基于检查结果，数据和API都正常，问题在前端JavaScript
"""

import os
import re

def fix_review_template_completely():
    """完全修复复盘模板的JavaScript问题"""
    print("=== 完全修复复盘模板JavaScript ===")
    
    review_template_path = "templates/review.html"
    
    if os.path.exists(review_template_path):
        with open(review_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 确保loadReviews函数正确处理API返回的数据结构
        # 根据API测试结果，数据结构是 data.data.reviews
        new_load_reviews_function = '''
// 加载复盘记录 - 最终修复版
async function loadReviews() {
    console.log('[DEBUG] 开始加载复盘记录...');
    
    try {
        // 显示加载状态
        const reviewsList = document.getElementById('reviews-list');
        if (reviewsList) {
            reviewsList.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                    <p class="mt-2 text-muted">正在加载复盘记录...</p>
                </div>
            `;
        }
        
        const response = await fetch('/api/reviews');
        console.log('[DEBUG] API响应状态:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('[DEBUG] 复盘记录原始数据:', data);
        
        if (data.success && data.data && data.data.reviews) {
            const reviews = data.data.reviews;
            console.log('[DEBUG] 找到复盘记录:', reviews.length, '条');
            
            if (reviews.length > 0) {
                displayReviews(reviews);
                console.log(`[DEBUG] 成功显示 ${reviews.length} 条复盘记录`);
            } else {
                if (reviewsList) {
                    reviewsList.innerHTML = `
                        <div class="text-center text-muted py-5">
                            <i class="fas fa-clipboard-list fa-3x mb-3 opacity-50"></i>
                            <h5>暂无复盘记录</h5>
                            <p class="mb-3">开始您的第一次复盘分析</p>
                            <button class="btn btn-primary btn-sm" onclick="openReviewModal()">
                                <i class="fas fa-plus"></i> 创建复盘记录
                            </button>
                        </div>
                    `;
                }
                console.log('[DEBUG] 复盘记录数组为空');
            }
        } else {
            throw new Error(data.message || '获取复盘记录失败');
        }
    } catch (error) {
        console.error('[ERROR] 加载复盘记录失败:', error);
        
        const reviewsList = document.getElementById('reviews-list');
        if (reviewsList) {
            reviewsList.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <h6>加载复盘记录失败</h6>
                    <p class="mb-3">${error.message}</p>
                    <button class="btn btn-outline-primary btn-sm" onclick="loadReviews()">
                        <i class="fas fa-redo"></i> 重试
                    </button>
                </div>
            `;
        }
        
        // 显示错误提示
        if (typeof window.showError === 'function') {
            window.showError('加载复盘记录失败', error.message);
        }
    }
}'''
        
        # 2. 确保displayReviews函数能正确显示数据
        new_display_reviews_function = '''
function displayReviews(reviews) {
    console.log('[DEBUG] displayReviews 接收到的数据:', reviews);
    
    const container = document.getElementById('reviews-list');
    if (!container) {
        console.error('[ERROR] 找不到reviews-list容器');
        return;
    }
    
    if (!reviews || reviews.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-clipboard-list fa-2x mb-3 opacity-50"></i>
                <p>暂无复盘记录</p>
                <small class="text-muted">开始您的第一次复盘分析</small>
            </div>
        `;
        return;
    }
    
    // 生成复盘记录HTML
    const reviewsHtml = reviews.map(review => {
        const profitDisplay = review.floating_profit_display || {};
        const profitColor = profitDisplay.color || 'text-muted';
        const profitText = profitDisplay.display || '无数据';
        
        return `
            <div class="card mb-3 review-item" data-review-id="${review.id}">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <h6 class="card-title mb-1">
                                <strong>${review.stock_code}</strong>
                            </h6>
                            <small class="text-muted">${review.review_date}</small>
                        </div>
                        <div class="col-md-2">
                            <span class="badge bg-primary">${review.decision || '未设置'}</span>
                        </div>
                        <div class="col-md-2">
                            <small class="text-muted">持仓天数</small><br>
                            <strong>${review.holding_days || 0}天</strong>
                        </div>
                        <div class="col-md-2">
                            <small class="text-muted">浮盈</small><br>
                            <strong class="${profitColor}">${profitText}</strong>
                        </div>
                        <div class="col-md-2">
                            <small class="text-muted">总分</small><br>
                            <strong>${review.total_score || 0}/25</strong>
                        </div>
                        <div class="col-md-1">
                            <div class="btn-group-vertical btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm" onclick="editReview(${review.id})" title="编辑">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="deleteReview(${review.id})" title="删除">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    ${review.analysis ? `
                        <div class="row mt-2">
                            <div class="col-12">
                                <small class="text-muted">分析:</small>
                                <p class="mb-0 small">${review.analysis}</p>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = reviewsHtml;
    console.log('[DEBUG] 复盘记录HTML已生成并插入到页面');
}'''
        
        # 3. 查找并替换现有的函数
        # 使用正则表达式查找并替换loadReviews函数
        load_reviews_pattern = r'async function loadReviews\(\)\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}'
        if re.search(load_reviews_pattern, content, re.DOTALL):
            content = re.sub(load_reviews_pattern, new_load_reviews_function.strip(), content, flags=re.DOTALL)
            print("✓ 替换了loadReviews函数")
        else:
            # 如果没找到，在适当位置添加
            script_section = content.find('<script>')
            if script_section != -1:
                content = content[:script_section + 8] + new_load_reviews_function + content[script_section + 8:]
                print("✓ 添加了loadReviews函数")
        
        # 替换displayReviews函数
        display_reviews_pattern = r'function displayReviews\([^)]*\)\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}'
        if re.search(display_reviews_pattern, content, re.DOTALL):
            content = re.sub(display_reviews_pattern, new_display_reviews_function.strip(), content, flags=re.DOTALL)
            print("✓ 替换了displayReviews函数")
        else:
            # 如果没找到，在loadReviews函数后添加
            load_reviews_end = content.find(new_load_reviews_function) + len(new_load_reviews_function)
            if load_reviews_end > len(new_load_reviews_function):
                content = content[:load_reviews_end] + '\\n\\n' + new_display_reviews_function + content[load_reviews_end:]
                print("✓ 添加了displayReviews函数")
        
        # 4. 确保页面加载时调用loadReviews
        init_code = '''
// 页面初始化 - 确保在DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] 复盘页面DOM加载完成');
    
    // 延迟执行以确保所有脚本都已加载
    setTimeout(() => {
        console.log('[DEBUG] 开始初始化复盘页面...');
        
        // 加载复盘记录
        if (typeof loadReviews === 'function') {
            loadReviews();
        } else {
            console.error('[ERROR] loadReviews函数未定义');
        }
        
        // 加载持仓数据
        if (typeof loadHoldings === 'function') {
            loadHoldings();
        }
        
        // 加载持仓策略提醒
        if (typeof loadHoldingAlerts === 'function') {
            loadHoldingAlerts();
        }
        
    }, 500);
});'''
        
        # 查找现有的初始化代码并替换
        if 'DOMContentLoaded' in content:
            # 如果已有DOMContentLoaded监听器，替换它
            dom_pattern = r'document\.addEventListener\([\'"]DOMContentLoaded[\'"][^}]*\}\);'
            if re.search(dom_pattern, content, re.DOTALL):
                content = re.sub(dom_pattern, init_code.strip(), content, flags=re.DOTALL)
                print("✓ 替换了页面初始化代码")
        else:
            # 如果没有，在script标签末尾添加
            script_end = content.rfind('</script>')
            if script_end != -1:
                content = content[:script_end] + init_code + '\\n' + content[script_end:]
                print("✓ 添加了页面初始化代码")
        
        # 保存修改
        with open(review_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ 复盘模板JavaScript修复完成")

def create_simple_test_page():
    """创建简单的测试页面"""
    print("\\n=== 创建简单测试页面 ===")
    
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>复盘记录显示测试</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container mt-4">
        <h2>复盘记录显示测试</h2>
        
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">复盘记录</h5>
                <button class="btn btn-primary btn-sm" onclick="testLoadReviews()">
                    <i class="fas fa-sync"></i> 加载复盘记录
                </button>
            </div>
            <div class="card-body">
                <div id="reviews-list" style="min-height: 300px;">
                    <!-- 复盘记录将显示在这里 -->
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <h5>调试信息</h5>
            <div id="debug-info" class="bg-light p-3 rounded">
                <small class="text-muted">调试信息将显示在这里...</small>
            </div>
        </div>
    </div>

    <script>
        // 复制修复后的loadReviews函数
        async function loadReviews() {
            console.log('[DEBUG] 开始加载复盘记录...');
            
            const debugInfo = document.getElementById('debug-info');
            debugInfo.innerHTML = '<small class="text-info">正在加载复盘记录...</small>';
            
            try {
                // 显示加载状态
                const reviewsList = document.getElementById('reviews-list');
                if (reviewsList) {
                    reviewsList.innerHTML = `
                        <div class="text-center py-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">加载中...</span>
                            </div>
                            <p class="mt-2 text-muted">正在加载复盘记录...</p>
                        </div>
                    `;
                }
                
                const response = await fetch('/api/reviews');
                console.log('[DEBUG] API响应状态:', response.status);
                debugInfo.innerHTML += '<br><small class="text-info">API响应状态: ' + response.status + '</small>';
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                console.log('[DEBUG] 复盘记录原始数据:', data);
                debugInfo.innerHTML += '<br><small class="text-info">API返回数据结构: ' + JSON.stringify(data, null, 2) + '</small>';
                
                if (data.success && data.data && data.data.reviews) {
                    const reviews = data.data.reviews;
                    console.log('[DEBUG] 找到复盘记录:', reviews.length, '条');
                    debugInfo.innerHTML += '<br><small class="text-success">找到 ' + reviews.length + ' 条复盘记录</small>';
                    
                    if (reviews.length > 0) {
                        displayReviews(reviews);
                        console.log(`[DEBUG] 成功显示 ${reviews.length} 条复盘记录`);
                        debugInfo.innerHTML += '<br><small class="text-success">成功显示复盘记录</small>';
                    } else {
                        if (reviewsList) {
                            reviewsList.innerHTML = `
                                <div class="text-center text-muted py-5">
                                    <i class="fas fa-clipboard-list fa-3x mb-3 opacity-50"></i>
                                    <h5>暂无复盘记录</h5>
                                    <p class="mb-3">开始您的第一次复盘分析</p>
                                </div>
                            `;
                        }
                        console.log('[DEBUG] 复盘记录数组为空');
                        debugInfo.innerHTML += '<br><small class="text-warning">复盘记录数组为空</small>';
                    }
                } else {
                    throw new Error(data.message || '获取复盘记录失败');
                }
            } catch (error) {
                console.error('[ERROR] 加载复盘记录失败:', error);
                debugInfo.innerHTML += '<br><small class="text-danger">错误: ' + error.message + '</small>';
                
                const reviewsList = document.getElementById('reviews-list');
                if (reviewsList) {
                    reviewsList.innerHTML = `
                        <div class="text-center text-danger py-4">
                            <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                            <h6>加载复盘记录失败</h6>
                            <p class="mb-3">${error.message}</p>
                            <button class="btn btn-outline-primary btn-sm" onclick="loadReviews()">
                                <i class="fas fa-redo"></i> 重试
                            </button>
                        </div>
                    `;
                }
            }
        }
        
        function displayReviews(reviews) {
            console.log('[DEBUG] displayReviews 接收到的数据:', reviews);
            
            const container = document.getElementById('reviews-list');
            if (!container) {
                console.error('[ERROR] 找不到reviews-list容器');
                return;
            }
            
            if (!reviews || reviews.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-clipboard-list fa-2x mb-3 opacity-50"></i>
                        <p>暂无复盘记录</p>
                        <small class="text-muted">开始您的第一次复盘分析</small>
                    </div>
                `;
                return;
            }
            
            // 生成复盘记录HTML
            const reviewsHtml = reviews.map(review => {
                const profitDisplay = review.floating_profit_display || {};
                const profitColor = profitDisplay.color || 'text-muted';
                const profitText = profitDisplay.display || '无数据';
                
                return `
                    <div class="card mb-3 review-item" data-review-id="${review.id}">
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-3">
                                    <h6 class="card-title mb-1">
                                        <strong>${review.stock_code}</strong>
                                    </h6>
                                    <small class="text-muted">${review.review_date}</small>
                                </div>
                                <div class="col-md-2">
                                    <span class="badge bg-primary">${review.decision || '未设置'}</span>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">持仓天数</small><br>
                                    <strong>${review.holding_days || 0}天</strong>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">浮盈</small><br>
                                    <strong class="${profitColor}">${profitText}</strong>
                                </div>
                                <div class="col-md-2">
                                    <small class="text-muted">总分</small><br>
                                    <strong>${review.total_score || 0}/25</strong>
                                </div>
                                <div class="col-md-1">
                                    <button class="btn btn-outline-primary btn-sm" title="查看详情">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                </div>
                            </div>
                            ${review.analysis ? `
                                <div class="row mt-2">
                                    <div class="col-12">
                                        <small class="text-muted">分析:</small>
                                        <p class="mb-0 small">${review.analysis}</p>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            }).join('');
            
            container.innerHTML = reviewsHtml;
            console.log('[DEBUG] 复盘记录HTML已生成并插入到页面');
        }
        
        function testLoadReviews() {
            document.getElementById('debug-info').innerHTML = '<small class="text-muted">开始测试...</small>';
            loadReviews();
        }
        
        // 页面加载时自动执行
        document.addEventListener('DOMContentLoaded', function() {
            console.log('[DEBUG] 测试页面加载完成');
            setTimeout(() => {
                loadReviews();
            }, 500);
        });
    </script>
</body>
</html>'''
    
    with open('test_review_display_simple.html', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✓ 创建了简单测试页面: test_review_display_simple.html")

def main():
    """主函数"""
    print("开始最终修复复盘页面...")
    print("=" * 50)
    
    # 完全修复复盘模板
    fix_review_template_completely()
    
    # 创建简单测试页面
    create_simple_test_page()
    
    print("\\n" + "=" * 50)
    print("最终修复完成！")
    print("\\n修复内容:")
    print("1. ✅ 完全重写了loadReviews函数，确保正确处理API数据结构")
    print("2. ✅ 完全重写了displayReviews函数，确保正确显示复盘记录")
    print("3. ✅ 添加了详细的调试日志，便于问题排查")
    print("4. ✅ 确保页面初始化时自动加载复盘记录")
    print("5. ✅ 创建了简单的测试页面验证功能")
    print("\\n验证步骤:")
    print("1. 刷新复盘页面 (http://localhost:5001/review)")
    print("2. 打开浏览器控制台查看调试信息")
    print("3. 或者打开测试页面: test_review_display_simple.html")
    print("4. 应该能看到000776的复盘记录显示出来")

if __name__ == "__main__":
    main()