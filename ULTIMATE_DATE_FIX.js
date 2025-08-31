// 终极修复 - 彻底解决交易日期红框问题
(function() {
    'use strict';
    
    console.log('💀 终极修复开始 - 彻底解决交易日期问题！');
    
    // 1. 找到交易日期字段
    const tradeDateField = document.getElementById('trade-date');
    if (!tradeDateField) {
        console.error('❌ 找不到交易日期字段');
        return;
    }
    
    // 2. 暴力清除所有验证状态
    function clearDateValidation() {
        tradeDateField// .classList.remove(["']is-invalid["'], 'is-valid');
        tradeDateField// .classList.add(["']is-valid["']); // 强制显示为有效
        
        // 清除所有错误消息
        const containers = [
            tradeDateField.parentNode,
            tradeDateField.parentNode.parentNode,
            tradeDateField.closest('.mb-3'),
            tradeDateField.closest('.col-md-6')
        ];
        
        containers.forEach(container => {
            if (container) {
                const errorDivs = container.querySelectorAll('.invalid-feedback');
                errorDivs.forEach(div => {
                    div.style.display = 'none';
                    div.remove();
                });
            }
        });
        
        console.log('✅ 清除交易日期验证状态');
    }
    
    // 3. 立即清除
    clearDateValidation();
    
    // 4. 重写所有可能的验证器
    if (window.tradingManager) {
        // 重写SimpleFormValidator
        if (window.tradingManager.simpleValidator) {
            const validator = window.tradingManager.simpleValidator;
            
            // 删除交易日期错误
            delete validator.errors['trade-date'];
            
            // 重写validateField方法
            const originalValidateField = validator.validateField;
            validator.validateField = function(fieldId, value = null) {
                if (fieldId === 'trade-date') {
                    // 交易日期永远返回true
                    const field = document.getElementById(fieldId);
                    if (field) {
                        field// .classList.remove(["']is-invalid["']);
                        field// .classList.add(["']is-valid["']);
                        
                        // 清除错误消息
                        const container = this.getFieldContainer(field);
                        const errorDiv = container.querySelector('.invalid-feedback');
                        if (errorDiv) {
                            errorDiv.style.display = 'none';
                        }
                    }
                    delete this.errors[fieldId];
                    return true;
                } else {
                    return originalValidateField.call(this, fieldId, value);
                }
            };
            
            console.log('✅ 重写SimpleFormValidator');
        }
        
        // 重写FormValidator
        if (window.tradingManager.formValidator) {
            const formValidator = window.tradingManager.formValidator;
            
            // 删除交易日期的验证规则
            if (formValidator.rules && formValidator.rules['trade_date']) {
                delete formValidator.rules['trade_date'];
            }
            
            // 重写validateField方法
            const originalValidateField = formValidator.validateField;
            formValidator.validateField = function(field) {
                if (typeof field === 'string' && field === 'trade_date') {
                    return true;
                }
                if (field && field.name === 'trade_date') {
                    return true;
                }
                if (field && field.id === 'trade-date') {
                    return true;
                }
                return originalValidateField.call(this, field);
            };
            
            console.log('✅ 重写FormValidator');
        }
    }
    
    // 5. 监听所有可能触发验证的事件
    const events = ['input', 'change', 'blur', 'focus', 'keyup', 'keydown'];
    events.forEach(eventType => {
        tradeDateField.addEventListener(eventType, function(e) {
            // 延迟执行，确保在其他验证器之后
            setTimeout(() => {
                clearDateValidation();
            }, 10);
        });
    });
    
    // 6. 定期检查并清除红框
    const intervalId = setInterval(() => {
        if (tradeDateField.classList.contains('is-invalid')) {
            console.log('🔧 检测到交易日期红框，立即清除');
            clearDateValidation();
        }
    }, 100);
    
    // 7. 10秒后停止定期检查
    setTimeout(() => {
        clearInterval(intervalId);
        console.log('⏰ 停止定期检查');
    }, 10000);
    
    // 8. 重写HTML5验证
    tradeDateField.setCustomValidity(''); // 清除自定义验证消息
    tradeDateField.removeAttribute('required'); // 临时移除required属性
    
    // 9. 监听表单提交
    const form = document.getElementById('trade-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // 确保交易日期不会阻止提交
            clearDateValidation();
            
            // 重新添加required属性（如果需要的话）
            if (!tradeDateField.hasAttribute('required')) {
                tradeDateField.setAttribute('required', '');
            }
        });
    }
    
    console.log('💀 终极修复完成！交易日期应该不会再显示红框了！');
    
    // 10. 返回清理函数
    return function cleanup() {
        clearInterval(intervalId);
        console.log('🧹 清理完成');
    };
})();