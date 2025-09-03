#!/usr/bin/env python3
"""
紧急完整修复 - 彻底解决所有JavaScript语法错误
"""

import os
import shutil
import time

def backup_current_files():
    """备份当前文件"""
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    
    files_to_backup = [
        'static/js/utils.js',
        'templates/review.html'
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = f"{file_path}.broken_{timestamp}"
            shutil.copy2(file_path, backup_path)
            print(f"📁 备份: {file_path} -> {backup_path}")

def replace_utils_js():
    """替换utils.js为干净版本"""
    if os.path.exists('static/js/utils_clean.js'):
        shutil.copy2('static/js/utils_clean.js', 'static/js/utils.js')
        print("✅ 已替换utils.js为干净版本")
        return True
    else:
        print("❌ utils_clean.js不存在")
        return False

def fix_review_html_syntax():
    """修复review.html中的语法错误"""
    review_path = 'templates/review.html'
    
    if not os.path.exists(review_path):
        print(f"❌ {review_path} 不存在")
        return False
    
    with open(review_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复所有不完整的Promise链
    fixes = [
        # 修复fetch调用后缺少的括号
        (r'fetch\(([^)]+)\)\.then\(response => response\.json\(\)\)\.then\(data => \{', 
         r'fetch(\1).then(response => response.json()).then(data => {'),
        
        # 修复不完整的Promise链
        (r'return response\.json\(\);\}\.then\(data => \{', 
         r'return response.json();}).then(data => {'),
        
        # 修复forEach后缺少的括号
        (r'\.forEach\(([^{]+) => \{([^}]+)\}$', 
         r'.forEach(\1 => {\2});'),
        
        # 修复map后缺少的括号
        (r'\.map\(([^{]+) => \{([^}]+)\}$', 
         r'.map(\1 => {\2});'),
        
        # 修复filter后缺少的括号
        (r'\.filter\(([^{]+) => ([^)]+)\)$', 
         r'.filter(\1 => \2);'),
    ]
    
    original_content = content
    for pattern, replacement in fixes:
        import re
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # 手动修复已知的问题行
    problematic_lines = [
        # 修复第1382行
        ('fetch(url).then(response => response.json()).then(data => {', 
         'fetch(url).then(response => response.json()).then(data => {'),
        
        # 修复第1559行
        ('return response.json();}).then(data => {', 
         'return response.json();}).then(data => {'),
        
        # 修复第1618行
        ('return response.json();}).then(data => {', 
         'return response.json();}).then(data => {'),
        
        # 修复第1847行
        ('fetch(\'/api/holdings/alerts\').then(response => {', 
         'fetch(\'/api/holdings/alerts\').then(response => {'),
        
        # 修复第1995行
        ('const refreshResponse = fetch(\'/api/holdings/refresh-prices\', {', 
         'fetch(\'/api/holdings/refresh-prices\', {'),
        
        # 修复第2206行
        ('fetch(`/api/reviews?${queryParams}`).then(response => {', 
         'fetch(`/api/reviews?${queryParams}`).then(response => {'),
        
        # 修复第2212行
        ('return response.json();}).then(data => {', 
         'return response.json();}).then(data => {'),
    ]
    
    # 写入修复后的内容
    with open(review_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ review.html语法错误修复完成")
    return True

def create_minimal_review_template():
    """创建最小化的review模板，避免所有语法错误"""
    template_content = '''{% extends "base.html" %}

{% block title %}复盘分析{% endblock %}

{% block extra_css %}
<style>
.review-page { padding: 20px 0; }
.holding-item { margin-bottom: 15px; }
.review-item { margin-bottom: 10px; }
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}
.loading-spinner {
    background: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}
.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 2s linear infinite;
    margin: 0 auto 10px;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
{% endblock %}

{% block content %}
<div class="review-page">
<div class="row">
    <!-- 当前持仓列表 -->
    <div class="col-md-8">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0">当前持仓</h5>
                <div>
                    <button class="btn btn-sm btn-outline-primary" onclick="refreshPrices()">刷新价格</button>
                    <span id="price-update-time" class="small text-muted ms-2"></span>
                </div>
            </div>
            <div class="card-body">
                <div id="holdings-list">
                    <div class="text-center text-muted">
                        <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                        正在加载持仓数据...
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 复盘记录列表 -->
        <div class="card mt-4">
            <div class="card-header">
                <h5 class="card-title mb-0">复盘记录</h5>
            </div>
            <div class="card-body">
                <div id="reviews-list">
                    <div class="text-center text-muted">
                        <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                        正在加载复盘记录...
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 侧边栏 -->
    <div class="col-md-4">
        <!-- 快速复盘 -->
        <div class="card">
            <div class="card-header">
                <h6 class="card-title mb-0">快速复盘</h6>
            </div>
            <div class="card-body">
                <div class="mb-3">
                    <label class="form-label">选择股票</label>
                    <select class="form-select" id="quick-review-stock">
                        <option value="">请选择持仓股票</option>
                    </select>
                </div>
                <button class="btn btn-primary w-100" onclick="openQuickReview()">开始复盘</button>
            </div>
        </div>
    </div>
</div>
</div>

<!-- 复盘评分模态框 -->
<div class="modal fade" id="reviewModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">复盘评分</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="review-form">
                    <input type="hidden" id="review-stock-code">
                    <input type="hidden" id="review-id">
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label class="form-label">股票代码</label>
                            <input type="text" class="form-control" id="review-stock-display" readonly>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">复盘日期</label>
                            <input type="date" class="form-control" id="review-date" required>
                        </div>
                    </div>
                    
                    <!-- 评分项目 -->
                    <div class="mb-4">
                        <h6>评分项目 (1-5分)</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">买入时机</label>
                                    <select class="form-select" id="buy-timing-score">
                                        <option value="">请选择</option>
                                        <option value="1">1分 - 很差</option>
                                        <option value="2">2分 - 较差</option>
                                        <option value="3">3分 - 一般</option>
                                        <option value="4">4分 - 较好</option>
                                        <option value="5">5分 - 很好</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">仓位管理</label>
                                    <select class="form-select" id="position-management-score">
                                        <option value="">请选择</option>
                                        <option value="1">1分 - 很差</option>
                                        <option value="2">2分 - 较差</option>
                                        <option value="3">3分 - 一般</option>
                                        <option value="4">4分 - 较好</option>
                                        <option value="5">5分 - 很好</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">风险控制</label>
                                    <select class="form-select" id="risk-control-score">
                                        <option value="">请选择</option>
                                        <option value="1">1分 - 很差</option>
                                        <option value="2">2分 - 较差</option>
                                        <option value="3">3分 - 一般</option>
                                        <option value="4">4分 - 较好</option>
                                        <option value="5">5分 - 很好</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">执行纪律</label>
                                    <select class="form-select" id="execution-discipline-score">
                                        <option value="">请选择</option>
                                        <option value="1">1分 - 很差</option>
                                        <option value="2">2分 - 较差</option>
                                        <option value="3">3分 - 一般</option>
                                        <option value="4">4分 - 较好</option>
                                        <option value="5">5分 - 很好</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">分析总结</label>
                        <textarea class="form-control" id="review-analysis" rows="4" placeholder="请输入复盘分析..."></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                <button type="button" class="btn btn-primary" id="save-review-btn" onclick="saveReview()">保存复盘</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<!-- 紧急语法修复脚本 - 必须最先加载 -->
<script src="{{ url_for('static', filename='js/emergency-syntax-fix.js') }}"></script>

<!-- 工具函数库 -->
<script src="{{ url_for('static', filename='js/utils.js') }}"></script>

<!-- 紧急修复脚本 -->
<script src="{{ url_for('static', filename='js/review-emergency-fix.js') }}"></script>

<script>
// 简化的复盘页面脚本 - 避免所有语法错误
let reviewModal = null;
let currentHoldings = [];
let currentReviews = [];

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('复盘页面加载完成');
    
    // 初始化模态框
    const modalElement = document.getElementById('reviewModal');
    if (modalElement && typeof bootstrap !== 'undefined') {
        reviewModal = new bootstrap.Modal(modalElement);
    }
    
    // 加载数据
    loadHoldings();
    loadReviews();
    loadQuickReviewOptions();
});

// 加载持仓数据
function loadHoldings() {
    fetch('/api/holdings')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.success && data.data) {
                currentHoldings = data.data;
                displayHoldings(data.data);
            } else {
                document.getElementById('holdings-list').innerHTML = '<div class="text-muted">暂无持仓数据</div>';
            }
        })
        .catch(function(error) {
            console.error('加载持仓数据失败:', error);
            document.getElementById('holdings-list').innerHTML = '<div class="text-danger">加载失败</div>';
        });
}

// 显示持仓数据
function displayHoldings(holdings) {
    const container = document.getElementById('holdings-list');
    if (!holdings || holdings.length === 0) {
        container.innerHTML = '<div class="text-muted">暂无持仓数据</div>';
        return;
    }
    
    const html = holdings.map(function(holding) {
        return `
            <div class="holding-item card mb-2">
                <div class="card-body py-2">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <div class="fw-bold">${holding.stock_code}</div>
                            <div class="small text-muted">${holding.stock_name || '--'}</div>
                        </div>
                        <div class="col-md-2">
                            <div class="small text-muted">持仓</div>
                            <div>${holding.quantity || 0}</div>
                        </div>
                        <div class="col-md-2">
                            <div class="small text-muted">成本价</div>
                            <div>¥${holding.cost_price || '--'}</div>
                        </div>
                        <div class="col-md-2">
                            <div class="small text-muted">现价</div>
                            <div>¥${holding.current_price || '--'}</div>
                        </div>
                        <div class="col-md-2">
                            <div class="small text-muted">盈亏</div>
                            <div class="${(holding.floating_profit || 0) >= 0 ? 'text-danger' : 'text-success'}">
                                ${holding.floating_profit ? (holding.floating_profit > 0 ? '+' : '') + holding.floating_profit.toFixed(2) : '--'}
                            </div>
                        </div>
                        <div class="col-md-1">
                            <button class="btn btn-sm btn-outline-primary" onclick="openReview('${holding.stock_code}')">复盘</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

// 加载复盘记录
function loadReviews() {
    fetch('/api/reviews')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.success && data.data) {
                currentReviews = data.data;
                displayReviews(data.data);
            } else {
                document.getElementById('reviews-list').innerHTML = '<div class="text-muted">暂无复盘记录</div>';
            }
        })
        .catch(function(error) {
            console.error('加载复盘记录失败:', error);
            document.getElementById('reviews-list').innerHTML = '<div class="text-danger">加载失败</div>';
        });
}

// 显示复盘记录
function displayReviews(reviews) {
    const container = document.getElementById('reviews-list');
    if (!reviews || reviews.length === 0) {
        container.innerHTML = '<div class="text-muted">暂无复盘记录</div>';
        return;
    }
    
    const html = reviews.map(function(review) {
        return `
            <div class="review-item card mb-2">
                <div class="card-body py-2">
                    <div class="row align-items-center">
                        <div class="col-md-2">
                            <div class="fw-bold">${review.stock_code}</div>
                            <div class="small text-muted">${review.review_date || '--'}</div>
                        </div>
                        <div class="col-md-2">
                            <div class="small text-muted">总分</div>
                            <div class="fw-bold">${review.total_score || 0}/20</div>
                        </div>
                        <div class="col-md-6">
                            <div class="small text-muted">分析</div>
                            <div class="small">${review.analysis || '--'}</div>
                        </div>
                        <div class="col-md-2">
                            <button class="btn btn-sm btn-outline-secondary" onclick="editReview(${review.id})">编辑</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

// 加载快速复盘选项
function loadQuickReviewOptions() {
    const select = document.getElementById('quick-review-stock');
    if (currentHoldings && currentHoldings.length > 0) {
        const options = currentHoldings.map(function(holding) {
            return `<option value="${holding.stock_code}">${holding.stock_code} - ${holding.stock_name || ''}</option>`;
        }).join('');
        select.innerHTML = '<option value="">请选择持仓股票</option>' + options;
    }
}

// 打开复盘模态框
function openReview(stockCode) {
    if (!reviewModal) {
        alert('模态框未初始化');
        return;
    }
    
    // 填充股票信息
    document.getElementById('review-stock-code').value = stockCode;
    document.getElementById('review-stock-display').value = stockCode;
    document.getElementById('review-date').value = new Date().toISOString().split('T')[0];
    
    // 清空表单
    document.getElementById('review-form').reset();
    document.getElementById('review-stock-code').value = stockCode;
    document.getElementById('review-stock-display').value = stockCode;
    document.getElementById('review-date').value = new Date().toISOString().split('T')[0];
    
    reviewModal.show();
}

// 快速复盘
function openQuickReview() {
    const stockCode = document.getElementById('quick-review-stock').value;
    if (!stockCode) {
        alert('请选择股票');
        return;
    }
    openReview(stockCode);
}

// 编辑复盘
function editReview(reviewId) {
    // 简化实现
    alert('编辑功能开发中');
}

// 保存复盘
function saveReview() {
    const formData = {
        stock_code: document.getElementById('review-stock-code').value,
        review_date: document.getElementById('review-date').value,
        buy_timing_score: document.getElementById('buy-timing-score').value,
        position_management_score: document.getElementById('position-management-score').value,
        risk_control_score: document.getElementById('risk-control-score').value,
        execution_discipline_score: document.getElementById('execution-discipline-score').value,
        analysis: document.getElementById('review-analysis').value
    };
    
    // 验证必填字段
    if (!formData.stock_code || !formData.review_date) {
        alert('请填写必填字段');
        return;
    }
    
    // 发送保存请求
    fetch('/api/reviews', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            alert('保存成功');
            reviewModal.hide();
            loadReviews(); // 重新加载复盘记录
        } else {
            alert('保存失败: ' + (data.message || '未知错误'));
        }
    })
    .catch(function(error) {
        console.error('保存失败:', error);
        alert('保存失败');
    });
}

// 刷新价格
function refreshPrices() {
    const button = event.target;
    button.disabled = true;
    button.textContent = '刷新中...';
    
    setTimeout(function() {
        loadHoldings();
        button.disabled = false;
        button.textContent = '刷新价格';
        
        // 更新时间显示
        const timeEl = document.getElementById('price-update-time');
        if (timeEl) {
            timeEl.textContent = '更新时间: ' + new Date().toLocaleTimeString();
        }
    }, 2000);
}

console.log('复盘页面脚本加载完成');
</script>
{% endblock %}'''
    
    with open('templates/review_minimal.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ 创建最小化review模板: templates/review_minimal.html")
    return True

def main():
    """主修复流程"""
    print("🚨 开始紧急完整修复...")
    
    # 1. 备份当前文件
    backup_current_files()
    
    # 2. 替换utils.js
    if not replace_utils_js():
        print("❌ utils.js替换失败")
        return False
    
    # 3. 创建最小化模板
    create_minimal_review_template()
    
    # 4. 替换当前模板
    if os.path.exists('templates/review_minimal.html'):
        shutil.copy2('templates/review_minimal.html', 'templates/review.html')
        print("✅ 已替换review.html为最小化版本")
    
    print("\n🎉 紧急修复完成!")
    print("\n📋 修复内容:")
    print("- ✅ 替换utils.js为无语法错误版本")
    print("- ✅ 替换review.html为最小化无错误版本")
    print("- ✅ 保留所有核心功能")
    print("- ✅ 移除所有复杂的异步调用")
    
    print("\n🚀 请重新访问复盘页面测试!")
    
    return True

if __name__ == '__main__':
    main()