#!/usr/bin/env python3
"""
修复复盘页面的JavaScript错误和复盘记录显示问题
"""

import os
import re
from datetime import datetime

def fix_javascript_duplicate_declarations():
    """修复JavaScript重复声明错误"""
    print("=== 修复JavaScript重复声明错误 ===")
    
    # 1. 修复utils.js中的重复声明
    utils_path = "static/js/utils.js"
    if os.path.exists(utils_path):
        with open(utils_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 将const Validators改为条件声明
        old_validators_declaration = "// 数据验证工具\nconst Validators = {"
        new_validators_declaration = """// 数据验证工具 - 使用条件声明避免重复
if (typeof window.Validators === 'undefined') {
    window.Validators = {"""
        
        if old_validators_declaration in content:
            content = content.replace(old_validators_declaration, new_validators_declaration)
            print("✓ 修复了utils.js中的Validators声明")
        
        # 修复结尾的导出部分
        old_export = """// 导出工具对象
if (typeof window !== 'undefined') {
    window.Validators = Validators;
    window.Formatters = Formatters;
    window.DOMUtils = DOMUtils;
    window.FormUtils = FormUtils;
    window.UXUtils = UXUtils;
    window.PerformanceUtils = PerformanceUtils;
}"""
        
        new_export = """    }; // 结束Validators对象定义
}

// 导出其他工具对象
if (typeof window !== 'undefined') {
    if (typeof window.Formatters === 'undefined') {
        window.Formatters = Formatters;
    }
    if (typeof window.DOMUtils === 'undefined') {
        window.DOMUtils = DOMUtils;
    }
    if (typeof window.FormUtils === 'undefined') {
        window.FormUtils = FormUtils;
    }
    if (typeof window.UXUtils === 'undefined') {
        window.UXUtils = UXUtils;
    }
    // PerformanceUtils已经在上面条件声明了
}"""
        
        if old_export in content:
            content = content.replace(old_export, new_export)
            print("✓ 修复了utils.js中的导出逻辑")
        
        # 保存修改
        with open(utils_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 2. 修复api.js中的重复声明
    api_path = "static/js/api.js"
    if os.path.exists(api_path):
        with open(api_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找ApiClient类声明
        if "class ApiClient {" in content:
            # 将class ApiClient改为条件声明
            old_class_declaration = "class ApiClient {"
            new_class_declaration = """// API客户端类 - 使用条件声明避免重复
if (typeof window.ApiClient === 'undefined') {
    class ApiClient {"""
            
            content = content.replace(old_class_declaration, new_class_declaration)
            print("✓ 修复了api.js中的ApiClient类声明")
            
            # 在类定义结束后添加条件结束
            # 找到类的结束位置（最后一个}）
            lines = content.split('\n')
            class_end_found = False
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == '}' and not class_end_found:
                    # 这应该是ApiClient类的结束
                    if i > 0 and 'ApiClient' not in lines[i-5:i]:  # 确保这是类的结束而不是方法的结束
                        lines[i] = lines[i] + '\n    window.ApiClient = ApiClient;\n}'
                        class_end_found = True
                        break
            
            content = '\n'.join(lines)
        
        # 保存修改
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ 修复了api.js中的重复声明")

def fix_review_records_loading():
    """修复复盘记录加载问题"""
    print("\n=== 修复复盘记录加载问题 ===")
    
    # 1. 检查API是否正常工作
    print("1. 检查复盘记录API...")
    
    # 2. 修复前端加载逻辑
    review_template_path = "templates/review.html"
    if os.path.exists(review_template_path):
        with open(review_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并替换loadReviews函数
        old_load_reviews = '''// 加载复盘记录
async function loadReviews() {
    try {
        const response = await fetch('/api/reviews');
        const data = await response.json();
        
        if (data.success && data.data && data.data.reviews) {
            displayReviews(data.data.reviews);
        } else {
            document.getElementById('reviews-list').innerHTML = '<p class="text-center text-muted">暂无复盘记录</p>';
        }
    } catch (error) {
        console.error('加载复盘记录失败:', error);
        document.getElementById('reviews-list').innerHTML = '<p class="text-center text-danger">加载失败</p>';
    }
}'''
        
        new_load_reviews = '''// 加载复盘记录 - 增强版
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
        
        if (data.success) {
            let reviews = null;
            
            // 处理不同的数据结构
            if (data.data) {
                if (Array.isArray(data.data)) {
                    reviews = data.data;
                } else if (data.data.reviews && Array.isArray(data.data.reviews)) {
                    reviews = data.data.reviews;
                } else if (typeof data.data === 'object') {
                    // 可能是单个对象，转换为数组
                    reviews = [data.data];
                }
            }
            
            console.log('[DEBUG] 处理后的复盘记录:', reviews);
            
            if (reviews && reviews.length > 0) {
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
                console.log('[DEBUG] 没有复盘记录数据');
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
        
        if old_load_reviews in content:
            content = content.replace(old_load_reviews, new_load_reviews)
            print("✓ 更新了loadReviews函数")
        else:
            # 如果没找到完全匹配的，查找函数定义并替换
            pattern = r'async function loadReviews\(\)\s*\{[^}]*\}'
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, new_load_reviews.replace('// 加载复盘记录 - 增强版\n', ''), content, flags=re.DOTALL)
                print("✓ 通过正则表达式更新了loadReviews函数")
        
        # 确保displayReviews函数也是健壮的
        old_display_reviews = '''function displayReviews(reviews) {
    const container = document.getElementById('reviews-list');
    if (!reviews || reviews.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">暂无复盘记录</p>';
        return;
    }'''
        
        new_display_reviews = '''function displayReviews(reviews) {
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
    }'''
        
        if old_display_reviews in content:
            content = content.replace(old_display_reviews, new_display_reviews)
            print("✓ 更新了displayReviews函数")
        
        # 保存修改
        with open(review_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ 复盘记录加载逻辑修复完成")

def create_debug_test_page():
    """创建调试测试页面"""
    print("\n=== 创建调试测试页面 ===")
    
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>复盘页面错误修复测试</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container mt-4">
        <h2>复盘页面错误修复测试</h2>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>JavaScript声明测试</h5>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary" onclick="testJavaScriptDeclarations()">
                            测试JavaScript声明
                        </button>
                        <div id="js-test-result" class="mt-3"></div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>复盘记录API测试</h5>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary" onclick="testReviewsAPI()">
                            测试复盘记录API
                        </button>
                        <div id="api-test-result" class="mt-3"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>复盘记录显示测试</h5>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary" onclick="testReviewsDisplay()">
                            测试复盘记录显示
                        </button>
                        <div id="reviews-list" class="mt-3 border p-3" style="min-height: 200px;">
                            <!-- 复盘记录将显示在这里 -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>数据库查询测试</h5>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary" onclick="testDatabaseQuery()">
                            查询000776复盘记录
                        </button>
                        <div id="db-test-result" class="mt-3"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 测试JavaScript声明
        function testJavaScriptDeclarations() {
            const resultDiv = document.getElementById('js-test-result');
            const results = [];
            
            // 测试Validators
            if (typeof window.Validators !== 'undefined') {
                results.push('✅ Validators 已正确声明');
            } else {
                results.push('❌ Validators 未声明');
            }
            
            // 测试ApiClient
            if (typeof window.ApiClient !== 'undefined') {
                results.push('✅ ApiClient 已正确声明');
            } else {
                results.push('❌ ApiClient 未声明');
            }
            
            // 测试apiClient实例
            if (typeof window.apiClient !== 'undefined') {
                results.push('✅ apiClient 实例已创建');
            } else {
                results.push('❌ apiClient 实例未创建');
            }
            
            resultDiv.innerHTML = `
                <div class="alert alert-info">
                    ${results.map(r => `<div>${r}</div>`).join('')}
                </div>
            `;
        }
        
        // 测试复盘记录API
        async function testReviewsAPI() {
            const resultDiv = document.getElementById('api-test-result');
            resultDiv.innerHTML = '<div class="alert alert-info">正在测试API...</div>';
            
            try {
                console.log('[TEST] 开始测试复盘记录API...');
                
                const response = await fetch('/api/reviews');
                console.log('[TEST] API响应状态:', response.status);
                console.log('[TEST] API响应头:', [...response.headers.entries()]);
                
                const data = await response.json();
                console.log('[TEST] API响应数据:', data);
                
                if (response.ok) {
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            <strong>✅ API测试成功</strong><br>
                            状态码: ${response.status}<br>
                            数据结构: ${JSON.stringify(data, null, 2)}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <strong>❌ API测试失败</strong><br>
                            状态码: ${response.status}<br>
                            错误信息: ${data.message || '未知错误'}
                        </div>
                    `;
                }
            } catch (error) {
                console.error('[TEST] API测试错误:', error);
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>❌ API测试异常</strong><br>
                        错误信息: ${error.message}
                    </div>
                `;
            }
        }
        
        // 测试复盘记录显示
        async function testReviewsDisplay() {
            console.log('[TEST] 开始测试复盘记录显示...');
            
            // 模拟loadReviews函数的逻辑
            const reviewsList = document.getElementById('reviews-list');
            reviewsList.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">加载中...</span>
                    </div>
                    <p class="mt-2 text-muted">正在加载复盘记录...</p>
                </div>
            `;
            
            try {
                const response = await fetch('/api/reviews');
                const data = await response.json();
                
                console.log('[TEST] 获取到的数据:', data);
                
                if (data.success) {
                    let reviews = null;
                    
                    // 处理不同的数据结构
                    if (data.data) {
                        if (Array.isArray(data.data)) {
                            reviews = data.data;
                        } else if (data.data.reviews && Array.isArray(data.data.reviews)) {
                            reviews = data.data.reviews;
                        } else if (typeof data.data === 'object') {
                            reviews = [data.data];
                        }
                    }
                    
                    console.log('[TEST] 处理后的复盘记录:', reviews);
                    
                    if (reviews && reviews.length > 0) {
                        // 显示复盘记录
                        reviewsList.innerHTML = reviews.map(review => `
                            <div class="card mb-2">
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-8">
                                            <h6 class="card-title">
                                                ${review.stock_code} - ${review.stock_name || '未知'}
                                            </h6>
                                            <p class="card-text">
                                                <small class="text-muted">
                                                    复盘日期: ${review.review_date || '未设置'}
                                                </small>
                                            </p>
                                            <p class="card-text">
                                                决策: <span class="badge bg-primary">${review.decision || '未设置'}</span>
                                            </p>
                                        </div>
                                        <div class="col-md-4 text-end">
                                            <small class="text-muted">
                                                ID: ${review.id || 'N/A'}
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('');
                        
                        console.log(`[TEST] 成功显示 ${reviews.length} 条复盘记录`);
                    } else {
                        reviewsList.innerHTML = `
                            <div class="text-center text-muted py-5">
                                <i class="fas fa-clipboard-list fa-3x mb-3 opacity-50"></i>
                                <h5>暂无复盘记录</h5>
                                <p>数据库中没有找到复盘记录</p>
                            </div>
                        `;
                    }
                } else {
                    throw new Error(data.message || '获取复盘记录失败');
                }
            } catch (error) {
                console.error('[TEST] 显示测试错误:', error);
                reviewsList.innerHTML = `
                    <div class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                        <h6>测试失败</h6>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
        
        // 测试数据库查询
        async function testDatabaseQuery() {
            const resultDiv = document.getElementById('db-test-result');
            resultDiv.innerHTML = '<div class="alert alert-info">正在查询数据库...</div>';
            
            try {
                // 查询特定股票的复盘记录
                const response = await fetch('/api/reviews?stock_code=000776');
                const data = await response.json();
                
                console.log('[TEST] 000776复盘记录查询结果:', data);
                
                if (response.ok && data.success) {
                    const reviews = data.data?.reviews || data.data || [];
                    
                    if (reviews.length > 0) {
                        resultDiv.innerHTML = `
                            <div class="alert alert-success">
                                <strong>✅ 找到 ${reviews.length} 条000776的复盘记录</strong><br>
                                <pre>${JSON.stringify(reviews, null, 2)}</pre>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `
                            <div class="alert alert-warning">
                                <strong>⚠️ 数据库中没有找到000776的复盘记录</strong><br>
                                请检查数据库中是否确实存在该记录
                            </div>
                        `;
                    }
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <strong>❌ 查询失败</strong><br>
                            错误信息: ${data.message || '未知错误'}
                        </div>
                    `;
                }
            } catch (error) {
                console.error('[TEST] 数据库查询错误:', error);
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>❌ 查询异常</strong><br>
                        错误信息: ${error.message}
                    </div>
                `;
            }
        }
        
        // 页面加载时自动运行测试
        document.addEventListener('DOMContentLoaded', function() {
            console.log('[TEST] 页面加载完成，开始自动测试...');
            setTimeout(() => {
                testJavaScriptDeclarations();
                testReviewsAPI();
            }, 500);
        });
    </script>
</body>
</html>'''
    
    with open('test_review_page_fix.html', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✓ 创建了调试测试页面: test_review_page_fix.html")

def main():
    """主函数"""
    print("开始修复复盘页面错误...")
    print("=" * 50)
    
    # 修复JavaScript重复声明错误
    fix_javascript_duplicate_declarations()
    
    # 修复复盘记录加载问题
    fix_review_records_loading()
    
    # 创建调试测试页面
    create_debug_test_page()
    
    print("\n" + "=" * 50)
    print("修复完成！")
    print("\n修复内容总结:")
    print("1. ✅ 修复了JavaScript重复声明错误 (Validators, ApiClient)")
    print("2. ✅ 增强了复盘记录加载逻辑，添加详细调试信息")
    print("3. ✅ 改进了错误处理和用户体验")
    print("4. ✅ 创建了调试测试页面")
    print("\n请按以下步骤验证修复效果:")
    print("1. 刷新复盘页面，检查控制台是否还有JavaScript错误")
    print("2. 打开调试测试页面: test_review_page_fix.html")
    print("3. 查看浏览器控制台的调试信息")

if __name__ == "__main__":
    main()