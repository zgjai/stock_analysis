// 最终验证测试脚本
(function() {
    console.log('🧪 开始最终验证测试...');
    
    // 测试所有关键字段
    const testFields = [
        { id: 'trade-date', name: '交易日期', testValue: '' },
        { id: 'quantity', name: '数量', testValue: '' },
        { id: 'price', name: '价格', testValue: '' },
        { id: 'stock-code', name: '股票代码', testValue: '' },
        { id: 'stock-name', name: '股票名称', testValue: '' }
    ];
    
    let allTestsPassed = true;
    
    testFields.forEach(test => {
        const field = document.getElementById(test.id);
        if (field) {
            // 设置空值
            field.value = test.testValue;
            
            // 触发各种事件
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.dispatchEvent(new Event('blur', { bubbles: true }));
            field.dispatchEvent(new Event('change', { bubbles: true }));
            
            // 检查是否有红框
            const hasError = field.classList.contains('is-invalid');
            const hasRequired = field.hasAttribute('required');
            
            if (hasError) {
                console.log(`❌ ${test.name} 仍然显示红框`);
                allTestsPassed = false;
            } else {
                console.log(`✅ ${test.name} 无红框`);
            }
            
            if (hasRequired) {
                console.log(`❌ ${test.name} 仍然有required属性`);
                allTestsPassed = false;
            } else {
                console.log(`✅ ${test.name} 无required属性`);
            }
        } else {
            console.log(`⚠️ 字段 ${test.name} 未找到`);
        }
    });
    
    // 测试验证器
    if (window.tradingManager && window.tradingManager.simpleValidator) {
        const validator = window.tradingManager.simpleValidator;
        
        // 测试字段验证
        const fieldResult = validator.validateField('trade-date', '');
        if (fieldResult === true) {
            console.log('✅ 字段验证返回true');
        } else {
            console.log('❌ 字段验证仍然返回false');
            allTestsPassed = false;
        }
        
        // 测试表单验证
        const formResult = validator.validateForm();
        if (formResult === true) {
            console.log('✅ 表单验证返回true');
        } else {
            console.log('❌ 表单验证仍然返回false');
            allTestsPassed = false;
        }
    } else {
        console.log('⚠️ 验证器未找到');
    }
    
    // 最终结果
    if (allTestsPassed) {
        console.log('🎉 所有测试通过！验证已被彻底禁用！');
        if (typeof showMessage === 'function') {
            showMessage('🎉 验证修复成功！所有字段都不会再显示红框！', 'success');
        } else {
            alert('🎉 验证修复成功！');
        }
    } else {
        console.log('💀 部分测试失败，需要继续修复');
        if (typeof showMessage === 'function') {
            showMessage('⚠️ 部分验证仍需修复', 'warning');
        }
    }
    
    return allTestsPassed;
})();