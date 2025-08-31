
// 彻底禁用前端校验的脚本
// 这个脚本会在页面加载时运行，确保所有校验都被禁用

(function() {
    'use strict';
    
    console.log('🚫 开始禁用所有前端校验...');
    
    // 1. 禁用HTML5表单校验
    function disableHTML5Validation(silent = false) {
        // 给所有form添加novalidate属性
        document.querySelectorAll('form').forEach(form => {
            form.setAttribute('novalidate', 'true');
            form.noValidate = true;
        });
        
        // 移除所有required属性
        document.querySelectorAll('[required]').forEach(element => {
            element.removeAttribute('required');
        });
        
        // 移除所有pattern属性
        document.querySelectorAll('[pattern]').forEach(element => {
            element.removeAttribute('pattern');
        });
        
        // 移除min/max属性
        document.querySelectorAll('[min]').forEach(element => {
            element.removeAttribute('min');
        });
        
        document.querySelectorAll('[max]').forEach(element => {
            element.removeAttribute('max');
        });
        
        if (!silent) {
            console.log('✅ HTML5校验已禁用');
        }
    }
    
    // 2. 重写所有可能的校验器
    function disableJSValidation() {
        // 重写SimpleFormValidator
        if (window.SimpleFormValidator) {
            const originalPrototype = window.SimpleFormValidator.prototype;
            originalPrototype.validateField = function() { return true; };
            originalPrototype.validateForm = function() { 
                this.errors = {}; 
                return true; 
            };
            originalPrototype.showFieldError = function() {};
            originalPrototype.showFieldSuccess = function() {};
            originalPrototype.clearFieldError = function() {};
            originalPrototype.clearAllValidation = function() {};
        }
        
        // 重写FormValidator
        if (window.FormValidator) {
            const originalPrototype = window.FormValidator.prototype;
            originalPrototype.validateField = function() { return true; };
            originalPrototype.validateForm = function() { 
                return { isValid: true, errors: {} }; 
            };
            originalPrototype.showFieldError = function() {};
            originalPrototype.showFieldSuccess = function() {};
            originalPrototype.clearFieldValidation = function() {};
        }
        
        // 重写Validators对象
        if (window.Validators) {
            Object.keys(window.Validators).forEach(key => {
                window.Validators[key] = function() { return true; };
            });
        }
        
        console.log('✅ JavaScript校验已禁用');
    }
    
    // 3. 清除所有校验状态
    function clearValidationStates(silent = false) {
        // 移除所有is-invalid和is-valid类
        document.querySelectorAll('.is-invalid, .is-valid').forEach(element => {
            element.classList.remove('is-invalid', 'is-valid');
        });
        
        // 隐藏所有错误消息
        document.querySelectorAll('.invalid-feedback, .valid-feedback').forEach(element => {
            element.style.display = 'none';
        });
        
        if (!silent) {
            console.log('✅ 校验状态已清除');
        }
    }
    
    // 4. 阻止校验事件
    function blockValidationEvents() {
        // 阻止表单的invalid事件
        document.addEventListener('invalid', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }, true);
        
        // 阻止input事件中的校验
        document.addEventListener('input', function(e) {
            if (e.target.matches('input, select, textarea')) {
                // 清除可能的校验状态
                e.target.classList.remove('is-invalid', 'is-valid');
            }
        }, true);
        
        // 阻止blur事件中的校验
        document.addEventListener('blur', function(e) {
            if (e.target.matches('input, select, textarea')) {
                // 清除可能的校验状态
                e.target.classList.remove('is-invalid', 'is-valid');
            }
        }, true);
        
        console.log('✅ 校验事件已阻止');
    }
    
    // 5. 重写表单提交处理
    function overrideFormSubmission() {
        document.addEventListener('submit', function(e) {
            // 确保表单可以正常提交，不被校验阻止
            const form = e.target;
            if (form.tagName === 'FORM') {
                form.noValidate = true;
                // 清除所有校验状态
                form.querySelectorAll('.is-invalid, .is-valid').forEach(element => {
                    element.classList.remove('is-invalid', 'is-valid');
                });
            }
        }, true);
        
        console.log('✅ 表单提交已优化');
    }
    
    // 执行所有禁用操作
    function executeAll() {
        disableHTML5Validation();
        disableJSValidation();
        clearValidationStates();
        blockValidationEvents();
        overrideFormSubmission();
        
        console.log('🎉 所有前端校验已成功禁用！');
    }
    
    // 立即执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', executeAll);
    } else {
        executeAll();
    }
    
    // 监听DOM变化，只在需要时清理
    const observer = new MutationObserver(function(mutations) {
        let needsCleanup = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                needsCleanup = true;
            }
        });
        
        if (needsCleanup) {
            setTimeout(function() {
                clearValidationStates(true);
                disableHTML5Validation(true);
            }, 100);
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
})();
