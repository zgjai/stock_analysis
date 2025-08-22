#!/usr/bin/env python3
"""
简单的复盘记录修复 - 只修复复盘页面，不影响其他功能
"""

import os

def fix_review_page_only():
    """只修复复盘页面的显示问题"""
    print("=== 修复复盘页面显示问题 ===")
    
    review_template_path = "templates/review.html"
    
    if os.path.exists(review_template_path):
        with open(review_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在页面末尾添加一个简单的修复脚本
        fix_script = '''
<script>
// 复盘记录显示修复脚本
document.addEventListener('DOMContentLoaded', function() {
    console.log('[FIX] 复盘页面加载完成，开始修复...');
    
    // 延迟执行，确保所有脚本加载完成
    setTimeout(function() {
        fixReviewsDisplay();
    }, 1000);
});

function fixReviewsDisplay() {
    console.log('[FIX] 开始修复复盘记录显示...');
    
    // 检查是否有loadReviews函数
    if (typeof loadReviews === 'function') {
        console.log('[FIX] loadReviews函数存在，直接调用');
        loadReviews();
        return;
    }
    
    // 如果没有loadReviews函数，创建一个简单的版本
    console.log('[FIX] loadReviews函数不存在，创建简单版本');
    
    window.loadReviews = async function() {
        console.log('[FIX] 简单版本loadReviews开始执行');
        
        const reviewsList = document.getElementById('reviews-list');
        if (!reviewsList) {
            console.log('[FIX] 找不到reviews-list元素');
            return;
        }
        
        // 显示加载状态
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
            console.log('[FIX] API响应状态:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('[FIX] API返回数据:', data);
            
            if (data.success && data.data && data.data.reviews) {
                const reviews = data.data.reviews;
                console.log('[FIX] 找到复盘记录:', reviews.length, '条');
                
                if (reviews.length > 0) {
                    displayReviewsSimple(reviews);
                } else {
                    reviewsList.innerHTML = `
                        <div class="text-center text-muted py-5">
                            <i class="fas fa-clipboard-list fa-3x mb-3"></i>
                            <h5>暂无复盘记录</h5>
                            <p>开始您的第一次复盘分析</p>
                        </div>
                    `;
                }
            } else {
                throw new Error(data.message || '获取数据失败');
            }
        } catch (error) {
            console.error('[FIX] 加载失败:', error);
            reviewsList.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <h6>加载复盘记录失败</h6>
                    <p>${error.message}</p>
                    <button class="btn btn-outline-primary btn-sm" onclick="loadReviews()">
                        <i class="fas fa-redo"></i> 重试
                    </button>
                </div>
            `;
        }
    };
    
    // 创建简单的显示函数
    window.displayReviewsSimple = function(reviews) {
        console.log('[FIX] 显示复盘记录:', reviews);
        
        const reviewsList = document.getElementById('reviews-list');
        if (!reviewsList) return;
        
        const html = reviews.map(review => {
            const profitDisplay = review.floating_profit_display || {};
            const profitColor = profitDisplay.color || 'text-muted';
            const profitText = profitDisplay.display || '无数据';
            
            return `
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <h6 class="mb-1"><strong>${review.stock_code}</strong></h6>
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
                                <button class="btn btn-outline-primary btn-sm" title="查看">
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
        
        reviewsList.innerHTML = html;
        console.log('[FIX] 复盘记录显示完成');
    };
    
    // 执行加载
    loadReviews();
}
</script>'''
        
        # 在</body>标签前插入修复脚本
        if '</body>' in content:
            content = content.replace('</body>', fix_script + '\n</body>')
            print("✓ 添加了复盘记录修复脚本")
        else:
            # 如果没有</body>标签，在文件末尾添加
            content += fix_script
            print("✓ 在文件末尾添加了修复脚本")
        
        # 保存修改
        with open(review_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ 复盘页面修复完成")

def main():
    """主函数"""
    print("开始简单修复复盘页面...")
    print("=" * 50)
    
    fix_review_page_only()
    
    print("\n" + "=" * 50)
    print("简单修复完成！")
    print("\n修复说明:")
    print("1. ✅ 只修复了复盘页面的显示问题")
    print("2. ✅ 不影响其他页面的功能")
    print("3. ✅ 添加了独立的复盘记录加载逻辑")
    print("4. ✅ 包含完整的错误处理和重试功能")
    print("\n现在请:")
    print("1. 刷新复盘页面 (http://localhost:5001/review)")
    print("2. 应该能看到000776的复盘记录")
    print("3. 如果还有问题，查看浏览器控制台的[FIX]日志")

if __name__ == "__main__":
    main()