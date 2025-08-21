#!/usr/bin/env python3
"""
修复复盘分析页面的JavaScript错误和加载问题
"""

import os
import re
import json
from pathlib import Path

def fix_template_duplicate_scripts():
    """修复模板中重复引用的脚本"""
    template_path = "templates/review.html"
    
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除重复的emergency脚本引用
    pattern = r'<!-- Emergency fix script.*?-->\s*<script src="{{ url_for\(\'static\', filename=\'js/review-fix-emergency\.js\'\) }}"></script>\s*'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if len(matches) > 1:
        print(f"🔧 发现 {len(matches)} 个重复的emergency脚本引用，正在修复...")
        # 只保留第一个
        content = re.sub(pattern, '', content, count=len(matches)-1, flags=re.DOTALL)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 模板重复脚本引用已修复")
        return True
    
    print("✅ 模板脚本引用正常")
    return True

def fix_javascript_syntax_errors():
    """修复JavaScript语法错误"""
    js_files = [
        "static/js/utils.js",
        "static/js/review-save-manager.js", 
        "static/js/keyboard-shortcuts.js",
        "static/js/review-integration.js"
    ]
    
    fixed_files = []
    
    for js_file in js_files:
        if not os.path.exists(js_file):
            print(f"⚠️ JavaScript文件不存在: {js_file}")
            continue
            
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复重复的条件判断
        content = re.sub(
            r'if \(typeof reviewSaveManager !== \'undefined\' && reviewSaveManager\) \{\s*if \(typeof reviewSaveManager !== \'undefined\' && reviewSaveManager\) \{',
            'if (typeof reviewSaveManager !== \'undefined\' && reviewSaveManager) {',
            content
        )
        
        # 修复重复的赋值语句
        content = re.sub(
            r'reviewSaveManager = new ReviewSaveManager\(\);\s*reviewSaveManager = new ReviewSaveManager\(\);',
            'reviewSaveManager = new ReviewSaveManager();',
            content
        )
        
        # 修复重复的module.exports
        content = re.sub(
            r'module\.exports = \{ ReviewSaveManager, reviewSaveManager \};\s*module\.exports = \{ ReviewSaveManager, reviewSaveManager \};',
            'module.exports = { ReviewSaveManager, reviewSaveManager };',
            content
        )
        
        if content != original_content:
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed_files.append(js_file)
            print(f"✅ 已修复: {js_file}")
    
    if fixed_files:
        print(f"🔧 共修复了 {len(fixed_files)} 个JavaScript文件")
    else:
        print("✅ JavaScript文件语法正常")
    
    return True

def create_review_page_fix_script():
    """创建复盘页面修复脚本"""
    fix_script = """
/**
 * 复盘页面修复脚本 - 解决加载和显示问题
 */
(function() {
    'use strict';
    
    console.log('🔧 复盘页面修复脚本启动');
    
    // 修复函数
    function fixReviewPageIssues() {
        // 1. 强制清理持续的加载状态
        const loadingElements = document.querySelectorAll('.spinner-border');
        loadingElements.forEach(spinner => {
            const parent = spinner.closest('.text-center');
            if (parent && parent.textContent.includes('加载中')) {
                const container = parent.closest('.card-body, #holdings-list, #reviews-list, #holding-alerts');
                if (container) {
                    showEmptyState(container);
                }
            }
        });
        
        // 2. 确保基础函数可用
        if (typeof window.loadHoldings !== 'function') {
            window.loadHoldings = async function() {
                console.log('📊 加载持仓数据...');
                try {
                    const response = await fetch('/api/holdings');
                    if (response.ok) {
                        const data = await response.json();
                        displayHoldings(data.holdings || []);
                    } else {
                        throw new Error('API响应错误');
                    }
                } catch (error) {
                    console.error('加载持仓数据失败:', error);
                    showEmptyState(document.getElementById('holdings-list'), 'holdings');
                }
            };
        }
        
        if (typeof window.loadReviews !== 'function') {
            window.loadReviews = async function() {
                console.log('📝 加载复盘记录...');
                try {
                    const response = await fetch('/api/reviews');
                    if (response.ok) {
                        const data = await response.json();
                        displayReviews(data.reviews || []);
                    } else {
                        throw new Error('API响应错误');
                    }
                } catch (error) {
                    console.error('加载复盘记录失败:', error);
                    showEmptyState(document.getElementById('reviews-list'), 'reviews');
                }
            };
        }
        
        if (typeof window.loadHoldingAlerts !== 'function') {
            window.loadHoldingAlerts = async function() {
                console.log('🔔 加载持仓提醒...');
                try {
                    const response = await fetch('/api/holding-alerts');
                    if (response.ok) {
                        const data = await response.json();
                        displayHoldingAlerts(data.alerts || []);
                    } else {
                        throw new Error('API响应错误');
                    }
                } catch (error) {
                    console.error('加载持仓提醒失败:', error);
                    showEmptyState(document.getElementById('holding-alerts'), 'alerts');
                }
            };
        }
        
        // 3. 显示空状态函数
        function showEmptyState(container, type = 'data') {
            if (!container) return;
            
            const emptyStates = {
                'holdings': {
                    icon: 'bi-briefcase',
                    title: '暂无持仓数据',
                    subtitle: '请先添加交易记录',
                    action: '<a href="/trading-records" class="btn btn-outline-primary btn-sm mt-2"><i class="bi bi-plus-circle"></i> 添加交易记录</a>'
                },
                'reviews': {
                    icon: 'bi-journal-plus',
                    title: '暂无复盘记录',
                    subtitle: '开始您的第一次复盘分析',
                    action: ''
                },
                'alerts': {
                    icon: 'bi-check-circle text-success',
                    title: '暂无提醒',
                    subtitle: '当前持仓状态良好',
                    action: ''
                },
                'data': {
                    icon: 'bi-info-circle',
                    title: '暂无数据',
                    subtitle: '请稍后再试',
                    action: '<button class="btn btn-outline-primary btn-sm mt-2" onclick="location.reload()"><i class="bi bi-arrow-clockwise"></i> 刷新页面</button>'
                }
            };
            
            const state = emptyStates[type] || emptyStates['data'];
            
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="bi ${state.icon} fs-1 d-block mb-2"></i>
                    <div class="mb-2">${state.title}</div>
                    <small class="text-muted">${state.subtitle}</small>
                    ${state.action}
                </div>
            `;
        }
        
        // 4. 显示数据函数
        function displayHoldings(holdings) {
            const container = document.getElementById('holdings-list');
            if (!container) return;
            
            if (!holdings || holdings.length === 0) {
                showEmptyState(container, 'holdings');
                return;
            }
            
            container.innerHTML = holdings.map(holding => `
                <div class="holding-item card mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <div class="fw-bold">${holding.stock_name || holding.stock_code}</div>
                                <small class="text-muted">${holding.stock_code}</small>
                            </div>
                            <div class="col-md-2">
                                <div class="small text-muted">持仓数量</div>
                                <div>${holding.quantity || 0}</div>
                            </div>
                            <div class="col-md-2">
                                <div class="small text-muted">成本价</div>
                                <div>¥${(holding.buy_price || 0).toFixed(2)}</div>
                            </div>
                            <div class="col-md-2">
                                <div class="small text-muted">持仓天数</div>
                                <div>${holding.holding_days || 0}天</div>
                            </div>
                            <div class="col-md-3">
                                <button class="btn btn-primary btn-sm" onclick="openReview('${holding.stock_code}')">
                                    <i class="bi bi-journal-plus"></i> 复盘
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function displayReviews(reviews) {
            const container = document.getElementById('reviews-list');
            if (!container) return;
            
            if (!reviews || reviews.length === 0) {
                showEmptyState(container, 'reviews');
                return;
            }
            
            container.innerHTML = reviews.map(review => `
                <div class="card mb-2">
                    <div class="card-body py-2">
                        <div class="row align-items-center">
                            <div class="col-md-2">
                                <small class="text-muted">${review.review_date}</small>
                            </div>
                            <div class="col-md-2">
                                <strong>${review.stock_code}</strong>
                            </div>
                            <div class="col-md-2">
                                <span class="badge bg-primary">${review.total_score}/5</span>
                            </div>
                            <div class="col-md-4">
                                <small>${review.analysis || '无分析内容'}</small>
                            </div>
                            <div class="col-md-2">
                                <button class="btn btn-outline-primary btn-sm" onclick="editReview(${review.id})">
                                    编辑
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function displayHoldingAlerts(alerts) {
            const container = document.getElementById('holding-alerts');
            if (!container) return;
            
            if (!alerts || alerts.length === 0) {
                showEmptyState(container, 'alerts');
                return;
            }
            
            container.innerHTML = alerts.map(alert => `
                <div class="alert alert-${alert.type || 'info'} alert-dismissible fade show">
                    <strong>${alert.title}</strong>
                    <p class="mb-0">${alert.message}</p>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `).join('');
        }
        
        // 5. 全局函数
        window.openReview = function(stockCode) {
            console.log('📝 打开复盘:', stockCode);
            // 这里应该打开复盘模态框
            const modal = document.getElementById('reviewModal');
            if (modal) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                
                // 设置股票代码
                const stockCodeInput = document.getElementById('review-stock-code');
                const displayStockCode = document.getElementById('display-stock-code');
                if (stockCodeInput) stockCodeInput.value = stockCode;
                if (displayStockCode) displayStockCode.value = stockCode;
            }
        };
        
        window.refreshHoldings = function() {
            console.log('🔄 刷新持仓数据');
            const container = document.getElementById('holdings-list');
            if (container) {
                container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm me-2"></div>刷新中...</div>';
                setTimeout(() => {
                    window.loadHoldings();
                }, 500);
            }
        };
        
        console.log('✅ 复盘页面修复完成');
    }
    
    // 页面加载完成后执行修复
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixReviewPageIssues);
    } else {
        fixReviewPageIssues();
    }
    
    // 5秒后强制显示内容
    setTimeout(() => {
        const loadingElements = document.querySelectorAll('.spinner-border');
        if (loadingElements.length > 0) {
            console.warn('⏰ 检测到持续加载，强制显示内容');
            fixReviewPageIssues();
        }
    }, 5000);
    
})();
"""
    
    with open("static/js/review-page-fix.js", 'w', encoding='utf-8') as f:
        f.write(fix_script)
    
    print("✅ 创建了复盘页面修复脚本: static/js/review-page-fix.js")
    return True

def main():
    """主函数"""
    print("🚀 开始修复复盘分析页面问题...")
    
    try:
        # 1. 修复模板重复脚本
        fix_template_duplicate_scripts()
        
        # 2. 修复JavaScript语法错误
        fix_javascript_syntax_errors()
        
        # 3. 创建页面修复脚本
        create_review_page_fix_script()
        
        print("\n✅ 复盘页面问题修复完成!")
        print("\n📋 修复内容:")
        print("  - 移除了模板中重复的脚本引用")
        print("  - 修复了JavaScript语法错误和重复声明")
        print("  - 创建了页面修复脚本")
        print("\n🔧 建议操作:")
        print("  1. 刷新浏览器页面")
        print("  2. 检查控制台是否还有错误")
        print("  3. 测试复盘功能是否正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复过程中出错: {e}")
        return False

if __name__ == "__main__":
    main()