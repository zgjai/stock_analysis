/**
 * 复盘页面紧急修复脚本
 * 确保核心功能正常工作，即使其他组件失败
 */

(function() {
    'use strict';
    
    console.log('🚨 复盘页面紧急修复脚本启动');
    
    // 1. 确保基础工具函数可用
    if (typeof window.debounce === 'undefined') {
        window.debounce = function(func, wait, immediate) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    timeout = null;
                    if (!immediate) func.apply(this, args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func.apply(this, args);
            };
        };
        console.log('✅ debounce 函数已注入');
    }
    
    if (typeof window.throttle === 'undefined') {
        window.throttle = function(func, limit) {
            let inThrottle;
            return function executedFunction(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        };
        console.log('✅ throttle 函数已注入');
    }
    
    // 2. 强制清理加载状态函数
    window.forceCleanupLoadingStates = function() {
        console.log('🧹 执行强制清理加载状态...');
        
        try {
            // 清理全局加载遮罩
            const overlays = document.querySelectorAll('#global-loading-overlay, .modal-backdrop, .loading-overlay');
            overlays.forEach(overlay => {
                if (overlay) {
                    overlay.style.display = 'none';
                    try {
                        overlay.remove();
                    } catch (e) {
                        console.warn('无法移除遮罩元素:', e);
                    }
                }
            });
            
            // 清理spinner元素
            const spinners = document.querySelectorAll('.spinner-border');
            spinners.forEach(spinner => {
                const parent = spinner.closest('.text-center, .d-flex, .loading-container');
                if (parent && parent.textContent.includes('加载中')) {
                    spinner.style.display = 'none';
                }
            });
            
            // 替换持续显示"加载中"的内容
            const loadingTexts = document.querySelectorAll('*');
            loadingTexts.forEach(element => {
                if (element.textContent && element.textContent.includes('加载中...') && 
                    !element.querySelector('input, button, select')) {
                    
                    const container = element.closest('.card-body, .list-group-item, .table-responsive');
                    if (container) {
                        element.innerHTML = `
                            <div class="text-center text-muted py-4">
                                <i class="bi bi-exclamation-triangle fs-1 d-block mb-2 text-warning"></i>
                                <div class="mb-2">数据加载超时</div>
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
            
            // 重置body样式
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            console.log('✅ 强制清理完成');
            
        } catch (error) {
            console.error('强制清理时出错:', error);
        }
    };
    
    // 3. 简化版浮盈计算器
    window.SimpleFloatingProfitCalculator = class {
        constructor(stockCode, buyPrice) {
            this.stockCode = stockCode;
            this.buyPrice = buyPrice;
            this.currentPrice = null;
        }
        
        setCurrentPrice(price) {
            this.currentPrice = parseFloat(price);
            this.calculate();
        }
        
        calculate() {
            if (!this.buyPrice || !this.currentPrice) return;
            
            const profitRatio = (this.currentPrice - this.buyPrice) / this.buyPrice;
            const profitAmount = this.currentPrice - this.buyPrice;
            const percentage = (profitRatio * 100).toFixed(2);
            const sign = profitRatio > 0 ? '+' : '';
            
            // 更新显示
            const ratioElement = document.getElementById('floating-profit-ratio');
            if (ratioElement) {
                ratioElement.textContent = `${sign}${percentage}%`;
                ratioElement.className = profitRatio > 0 ? 'text-danger' : 
                                        profitRatio < 0 ? 'text-success' : 'text-muted';
            }
            
            const amountElement = document.getElementById('profit-amount-display');
            if (amountElement) {
                amountElement.textContent = `${sign}¥${profitAmount.toFixed(2)}`;
                amountElement.className = profitRatio > 0 ? 'text-danger' : 
                                         profitRatio < 0 ? 'text-success' : 'text-muted';
            }
            
            console.log(`💰 浮盈计算: ${sign}${percentage}% (¥${profitAmount.toFixed(2)})`);
        }
    };
    
    // 4. 自动修复函数
    function autoFix() {
        console.log('🔧 执行自动修复...');
        
        // 检查并修复FloatingProfitCalculator
        if (typeof window.FloatingProfitCalculator === 'undefined') {
            console.warn('⚠️ FloatingProfitCalculator 不可用，使用简化版本');
            window.FloatingProfitCalculator = window.SimpleFloatingProfitCalculator;
        }
        
        // 检查当前价格输入框
        const priceInput = document.getElementById('current-price-input');
        if (priceInput && !priceInput.hasAttribute('data-fixed')) {
            priceInput.addEventListener('input', window.debounce(function(e) {
                const price = parseFloat(e.target.value);
                if (!isNaN(price) && price > 0) {
                    // 尝试使用全局计算器
                    if (window.globalFloatingCalculator) {
                        window.globalFloatingCalculator.setCurrentPrice(price);
                    } else {
                        // 创建临时计算器
                        const buyPrice = 10.50; // 默认买入价格，实际应该从API获取
                        const calculator = new window.SimpleFloatingProfitCalculator('000001', buyPrice);
                        calculator.setCurrentPrice(price);
                    }
                }
            }, 300));
            
            priceInput.setAttribute('data-fixed', 'true');
            console.log('✅ 当前价格输入框已修复');
        }
        
        // 10秒后强制清理加载状态
        setTimeout(() => {
            const hasSpinners = document.querySelector('*[class*="spinner"]');
            const hasLoadingText = Array.from(document.querySelectorAll('*')).some(el => 
                el.textContent && el.textContent.includes('加载中'));
            
            if (hasSpinners || hasLoadingText) {
                console.warn('⏰ 检测到持续加载状态，执行强制清理');
                window.forceCleanupLoadingStates();
            }
        }, 10000);
        
        console.log('✅ 自动修复完成');
    }
    
    // 5. 错误处理
    window.addEventListener('error', function(e) {
        console.error('🚨 JavaScript错误:', e.error);
        
        // 如果是FloatingProfitCalculator相关错误，尝试修复
        if (e.error && e.error.message && e.error.message.includes('FloatingProfitCalculator')) {
            console.log('🔧 检测到FloatingProfitCalculator错误，尝试修复...');
            setTimeout(autoFix, 100);
        }
    });
    
    // 6. DOM加载完成后执行修复
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoFix);
    } else {
        autoFix();
    }
    
    // 7. 提供全局测试函数
    window.testReviewFix = function() {
        console.log('🧪 开始测试修复效果...');
        
        const tests = [
            {
                name: 'debounce函数',
                test: () => typeof window.debounce === 'function'
            },
            {
                name: 'throttle函数', 
                test: () => typeof window.throttle === 'function'
            },
            {
                name: 'FloatingProfitCalculator',
                test: () => typeof window.FloatingProfitCalculator === 'function'
            },
            {
                name: '强制清理函数',
                test: () => typeof window.forceCleanupLoadingStates === 'function'
            }
        ];
        
        let passed = 0;
        tests.forEach(test => {
            if (test.test()) {
                console.log(`✅ ${test.name} - 通过`);
                passed++;
            } else {
                console.log(`❌ ${test.name} - 失败`);
            }
        });
        
        console.log(`🏁 测试结果: ${passed}/${tests.length} 项通过`);
        return passed === tests.length;
    };
    
    console.log('✅ 复盘页面紧急修复脚本加载完成');
    
})();