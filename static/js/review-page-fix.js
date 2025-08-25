
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
                const container = parent.closest('.card-body, #holdings-list, #reviews-list');
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
        
        // Removed loadHoldingAlerts function as holding alerts module has been removed
        
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
        
        // Removed displayHoldingAlerts function as holding alerts module has been removed
            
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
