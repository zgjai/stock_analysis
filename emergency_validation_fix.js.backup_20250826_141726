// 紧急修复验证问题的脚本
(function() {
    'use strict';
    
    console.log('🚨 紧急修复验证问题...');
    
    // 修复数量字段的HTML5验证属性
    const quantityField = document.getElementById('quantity');
    if (quantityField) {
        quantityField.setAttribute('min', '1');
        quantityField.setAttribute('step', '1');
        console.log('✅ 修复数量字段验证属性');
    }
    
    // 修复价格字段的HTML5验证属性
    const priceField = document.getElementById('price');
    if (priceField) {
        priceField.setAttribute('step', '0.001');
        priceField.setAttribute('min', '0.001');
        priceField.setAttribute('max', '9999.999');
        console.log('✅ 修复价格字段验证属性');
    }
    
    // 清除所有字段的验证状态
    const form = document.getElementById('trade-form');
    if (form) {
        const invalidFields = form.querySelectorAll('.is-invalid');
        invalidFields.forEach(field => {
            field.classList.remove('is-invalid');
            console.log(`✅ 清除字段 ${field.id} 的错误状态`);
        });
        
        const errorMessages = form.querySelectorAll('.invalid-feedback');
        errorMessages.forEach(msg => {
            msg.style.display = 'none';
        });
        
        console.log('✅ 清除所有错误消息');
    }
    
    // 重新验证表单
    if (window.tradingManager && window.tradingManager.simpleValidator) {
        setTimeout(() => {
            console.log('🔄 重新验证表单...');
            const isValid = window.tradingManager.simpleValidator.validateForm();
            console.log(`验证结果: ${isValid ? '✅ 通过' : '❌ 失败'}`);
            
            if (!isValid) {
                console.log('错误详情:', window.tradingManager.simpleValidator.errors);
            }
        }, 500);
    }
    
    console.log('🎉 紧急修复完成！');
})();