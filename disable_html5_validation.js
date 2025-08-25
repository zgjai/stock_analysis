// 禁用HTML5原生验证，解决表单验证冲突
(function() {
    'use strict';
    
    console.log('🔧 禁用HTML5验证脚本已加载');
    
    function disableHTML5Validation() {
        // 禁用表单的HTML5验证
        const form = document.getElementById('trade-form');
        if (form) {
            form.noValidate = true;
            console.log('✅ 已禁用表单HTML5验证');
        }
        
        // 移除所有输入框的验证属性
        const inputs = document.querySelectorAll('#trade-form input, #trade-form select');
        inputs.forEach(input => {
            // 移除pattern属性（可能导致验证失败）
            if (input.hasAttribute('pattern')) {
                input.removeAttribute('pattern');
                console.log(`✅ 移除 ${input.id} 的pattern属性`);
            }
            
            // 移除maxlength限制（可能导致输入被截断）
            if (input.hasAttribute('maxlength')) {
                input.removeAttribute('maxlength');
                console.log(`✅ 移除 ${input.id} 的maxlength属性`);
            }
            
            // 清除任何现有的验证状态
            input.classList.remove('is-invalid', 'is-valid');
        });
        
        console.log('✅ HTML5验证已完全禁用');
    }
    
    // 页面加载后立即执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', disableHTML5Validation);
    } else {
        disableHTML5Validation();
    }
    
    // 模态框显示时也执行一次
    document.addEventListener('show.bs.modal', function(e) {
        if (e.target.id === 'addTradeModal') {
            setTimeout(disableHTML5Validation, 100);
        }
    });
    
    // 全局暴露函数
    window.disableHTML5Validation = disableHTML5Validation;
    
    console.log('💡 如果还有问题，在控制台执行: disableHTML5Validation()');
    
})();