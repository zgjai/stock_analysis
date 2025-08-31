// 调试保存问题的脚本
// 在浏览器控制台中运行此脚本来调试保存问题

console.log('🔍 开始调试保存问题...');

// 检查isSubmitting状态
console.log('当前isSubmitting状态:', window.isSubmitting || 'undefined');

// 重置isSubmitting状态
if (typeof window.isSubmitting !== 'undefined') {
    window.isSubmitting = false;
    console.log('✅ 已重置isSubmitting为false');
}

// 检查tradingManager
if (window.tradingManager) {
    console.log('✅ tradingManager存在');
    
    // 检查saveTrade方法
    if (typeof window.tradingManager.saveTrade === 'function') {
        console.log('✅ saveTrade方法存在');
    } else {
        console.log('❌ saveTrade方法不存在');
    }
    
    // 检查handleTradeFormSubmit方法
    if (typeof window.tradingManager.handleTradeFormSubmit === 'function') {
        console.log('✅ handleTradeFormSubmit方法存在');
    } else {
        console.log('❌ handleTradeFormSubmit方法不存在');
    }
} else {
    console.log('❌ tradingManager不存在');
}

// 检查表单元素
const form = document.getElementById('trade-form');
if (form) {
    console.log('✅ 表单存在');
    
    // 检查表单数据
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    console.log('📝 当前表单数据:', data);
} else {
    console.log('❌ 表单不存在');
}

// 检查保存按钮
const saveBtn = document.getElementById('save-trade-btn');
if (saveBtn) {
    console.log('✅ 保存按钮存在');
    console.log('按钮状态 - disabled:', saveBtn.disabled);
    console.log('按钮文本:', saveBtn.innerHTML);
} else {
    console.log('❌ 保存按钮不存在');
}

// 提供手动重置功能
window.resetSubmitState = function() {
    if (typeof window.isSubmitting !== 'undefined') {
        window.isSubmitting = false;
    }
    
    // 查找所有可能的isSubmitting变量
    const scripts = document.querySelectorAll('script');
    scripts.forEach(script => {
        if (script.textContent.includes('isSubmitting')) {
            console.log('发现包含isSubmitting的脚本');
        }
    });
    
    const saveBtn = document.getElementById('save-trade-btn');
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '保存';
    }
    
    console.log('✅ 已重置提交状态');
};

console.log('🔧 调试完成。如需重置提交状态，请运行: resetSubmitState()');