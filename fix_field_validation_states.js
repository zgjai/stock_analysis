// 修复字段验证状态不一致的问题
// 这个脚本会强制清除交易日期和数量字段的无效状态

function fixFieldValidationStates() {
    console.log('🔧 开始修复字段验证状态...');
    
    // 需要修复的字段
    const fieldsToFix = ['trade-date', 'quantity'];
    
    fieldsToFix.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            console.log(`修复字段: ${fieldId}`);
            
            // 强制移除无效状态
            field// .classList.remove(["']is-invalid["']);
            
            // 如果字段有值，添加有效状态
            if (field.value && field.value.trim() !== '') {
                field// .classList.add(["']is-valid["']);
                console.log(`✅ ${fieldId} 设置为有效状态`);
            }
            
            // 移除错误反馈消息
            const container = getFieldContainer(field);
            if (container) {
                const invalidFeedback = container.querySelector('.invalid-feedback');
                if (invalidFeedback) {
                    invalidFeedback.remove();
                    console.log(`🗑️ 移除 ${fieldId} 的错误反馈`);
                }
            }
        } else {
            console.warn(`⚠️ 找不到字段: ${fieldId}`);
        }
    });
    
    console.log('✅ 字段验证状态修复完成');
}

function getFieldContainer(field) {
    if (!field || !field.parentNode) {
        return null;
    }
    
    // 如果字段在input-group中，返回input-group的父容器
    if (field.parentNode.classList && field.parentNode.classList.contains('input-group')) {
        return field.parentNode.parentNode;
    }
    return field.parentNode;
}

// 在表单验证后调用修复函数
function enhanceFormValidation() {
    const form = document.getElementById('trade-form');
    if (!form) return;
    
    // 监听表单验证事件
    form.addEventListener('input', function(e) {
        if (e.target.id === 'trade-date' || e.target.id === 'quantity') {
            setTimeout(() => {
                fixFieldValidationStates();
            }, 100);
        }
    });
    
    // 监听表单提交前
    form.addEventListener('submit', function(e) {
        setTimeout(() => {
            fixFieldValidationStates();
        }, 50);
    });
    
    // 立即修复一次
    fixFieldValidationStates();
}

// 页面加载完成后执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceFormValidation);
} else {
    enhanceFormValidation();
}

// 导出函数供外部调用
window.fixFieldValidationStates = fixFieldValidationStates;