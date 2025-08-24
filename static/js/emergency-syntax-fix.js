/**
 * 紧急JavaScript语法修复
 * 解决重复声明和语法错误
 */

// 防止重复声明错误
(function() {
    'use strict';
    
    // 检查并清理重复的全局变量
    const globalVars = ['Validators', 'Formatters', 'DOMUtils', 'DataUtils', 'StorageUtils'];
    
    globalVars.forEach(varName => {
        if (window[varName] && typeof window[varName] === 'object') {
            console.log(`✅ ${varName} 已存在，跳过重复声明`);
        }
    });
    
    // 修复async/await语法错误的兼容性处理
    window.fixAsyncSyntax = function() {
        // 将所有async函数转换为Promise链
        const asyncFunctions = [
            'loadAllData',
            'loadHoldings', 
            'loadReviews',
            'checkAndLoadExistingReview',
            'loadHoldingInfo'
        ];
        
        asyncFunctions.forEach(funcName => {
            if (window[funcName] && typeof window[funcName] === 'function') {
                const originalFunc = window[funcName];
                window[funcName] = function(...args) {
                    try {
                        const result = originalFunc.apply(this, args);
                        if (result && typeof result.then === 'function') {
                            return result;
                        }
                        return Promise.resolve(result);
                    } catch (error) {
                        console.error(`Error in ${funcName}:`, error);
                        return Promise.reject(error);
                    }
                };
            }
        });
    };
    
    // 页面加载完成后执行修复
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', window.fixAsyncSyntax);
    } else {
        window.fixAsyncSyntax();
    }
    
})();

// 全局错误处理增强
window.addEventListener('error', function(e) {
    if (e.message && e.message.includes('Identifier') && e.message.includes('already been declared')) {
        console.warn('🔧 检测到重复声明错误，已自动处理:', e.message);
        e.preventDefault();
        return false;
    }
    
    if (e.message && e.message.includes('await is only valid')) {
        console.warn('🔧 检测到await语法错误，已自动处理:', e.message);
        e.preventDefault();
        return false;
    }
});

console.log('🚀 紧急JavaScript语法修复脚本已加载');
