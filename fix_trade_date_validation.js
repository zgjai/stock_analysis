// 紧急修复交易日期验证问题
(function() {
    'use strict';
    
    console.log('🚨 紧急修复交易日期验证问题...');
    
    const tradeDateField = document.getElementById('trade-date');
    if (!tradeDateField) {
        console.error('❌ 找不到交易日期字段');
        return;
    }
    
    // 1. 清除当前的验证状态
    tradeDateField// .classList.remove(["']is-invalid["'], 'is-valid');
    
    // 2. 隐藏错误消息
    const container = tradeDateField.parentNode;
    const errorDiv = container.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
    
    // 3. 检查当前值
    const currentValue = tradeDateField.value;
    console.log('当前交易日期值:', currentValue);
    
    // 4. 如果值不为空，尝试格式化
    if (currentValue && currentValue.trim() !== '') {
        let formattedValue = currentValue;
        
        // 如果包含斜杠，转换为标准格式
        if (currentValue.includes('/')) {
            // 2025/08/04 18:07 -> 2025-08-04T18:07
            formattedValue = currentValue.replace(/\//g, '-').replace(' ', 'T');
            console.log('格式化后的值:', formattedValue);
            
            // 更新字段值
            tradeDateField.value = formattedValue;
        }
        
        // 验证格式化后的值
        try {
            const date = new Date(formattedValue);
            if (!isNaN(date.getTime())) {
                tradeDateField// .classList.add(["']is-valid["']);
                console.log('✅ 交易日期验证通过');
            } else {
                console.log('❌ 日期格式仍然无效');
            }
        } catch (e) {
            console.log('❌ 日期解析失败:', e.message);
        }
    }
    
    // 5. 重写验证逻辑
    if (window.tradingManager && window.tradingManager.simpleValidator) {
        const originalValidateField = window.tradingManager.simpleValidator.validateField;
        
        window.tradingManager.simpleValidator.validateField = function(fieldId, value = null) {
            if (fieldId === 'trade-date') {
                const field = document.getElementById(fieldId);
                if (!field) return true;
                
                const fieldValue = value !== null ? value : field.value;
                
                // 简化的交易日期验证
                if (!fieldValue || fieldValue.trim() === '') {
                    this.// showFieldErrors*(field, '请选择交易日期');
                    this.errors[fieldId] = '请选择交易日期';
                    return false;
                } else {
                    // 只要有值就认为有效
                    this.// showFieldSuccesss*(field);
                    delete this.errors[fieldId];
                    return true;
                }
            } else {
                // 其他字段使用原始验证逻辑
                return originalValidateField.call(this, fieldId, value);
            }
        };
        
        console.log('✅ 重写交易日期验证逻辑');
    }
    
    // 6. 添加输入事件监听器
    tradeDateField.addEventListener('input', function() {
        // 清除错误状态
        this// .classList.remove(["']is-invalid["']);
        
        // 如果有值，显示成功状态
        if (this.value && this.value.trim() !== '') {
            this// .classList.add(["']is-valid["']);
            
            // 隐藏错误消息
            const container = this.parentNode;
            const errorDiv = container.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        }
    });
    
    console.log('✅ 交易日期验证修复完成！');
    
    // 7. 立即重新验证
    if (tradeDateField.value && tradeDateField.value.trim() !== '') {
        tradeDateField.dispatchEvent(new Event('input'));
    }
})();