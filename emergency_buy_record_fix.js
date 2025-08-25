// 紧急修复：绕过前端验证直接提交买入记录
(function() {
    'use strict';
    
    console.log('🚨 紧急买入记录修复脚本已加载');
    
    // 创建紧急提交函数
    window.emergencySubmitBuyRecord = async function() {
        console.log('🚨 开始紧急提交买入记录...');
        
        try {
            // 直接从表单获取数据
            const formData = {
                stock_code: document.getElementById('stock-code')?.value?.trim() || '',
                stock_name: document.getElementById('stock-name')?.value?.trim() || '',
                trade_type: 'buy',
                price: parseFloat(document.getElementById('price')?.value) || 0,
                quantity: parseInt(document.getElementById('quantity')?.value) || 0,
                trade_date: document.getElementById('trade-date')?.value || new Date().toISOString().slice(0, 16),
                reason: document.getElementById('reason')?.value?.trim() || ''
            };
            
            console.log('📋 收集的表单数据:', formData);
            
            // 基本验证
            const errors = [];
            if (!formData.stock_code) errors.push('股票代码不能为空');
            if (!formData.stock_name) errors.push('股票名称不能为空');
            if (formData.price <= 0) errors.push('价格必须大于0');
            if (formData.quantity <= 0) errors.push('数量必须大于0');
            if (!formData.reason) errors.push('操作原因不能为空');
            
            if (errors.length > 0) {
                alert('验证失败：\n' + errors.join('\n'));
                return;
            }
            
            console.log('✅ 基本验证通过，开始提交...');
            
            // 直接调用API
            const response = await fetch('/api/trades', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            console.log('📡 API响应状态:', response.status);
            
            const result = await response.json();
            console.log('📡 API响应数据:', result);
            
            if (response.ok) {
                alert('✅ 买入记录添加成功！\n' + 
                      '交易ID: ' + result.data.id + '\n' +
                      '股票: ' + result.data.stock_code + ' - ' + result.data.stock_name + '\n' +
                      '价格: ¥' + result.data.price + '\n' +
                      '数量: ' + result.data.quantity + ' 股');
                
                // 关闭模态框
                const modal = bootstrap.Modal.getInstance(document.getElementById('addTradeModal'));
                if (modal) modal.hide();
                
                // 刷新页面或重新加载交易记录
                if (typeof tradingManager !== 'undefined' && tradingManager.loadTrades) {
                    tradingManager.loadTrades();
                } else {
                    location.reload();
                }
            } else {
                alert('❌ 添加失败：\n' + (result.error?.message || '未知错误'));
            }
            
        } catch (error) {
            console.error('🚨 紧急提交失败:', error);
            alert('❌ 提交失败：\n' + error.message);
        }
    };
    
    // 创建紧急按钮
    function createEmergencyButton() {
        // 等待模态框加载
        const checkModal = () => {
            const modal = document.getElementById('addTradeModal');
            if (modal) {
                const modalFooter = modal.querySelector('.modal-footer');
                if (modalFooter && !modalFooter.querySelector('#emergency-submit-btn')) {
                    const emergencyBtn = document.createElement('button');
                    emergencyBtn.id = 'emergency-submit-btn';
                    emergencyBtn.type = 'button';
                    emergencyBtn.className = 'btn btn-warning';
                    emergencyBtn.innerHTML = '🚨 紧急提交';
                    emergencyBtn.title = '绕过前端验证直接提交';
                    emergencyBtn.onclick = window.emergencySubmitBuyRecord;
                    
                    modalFooter.insertBefore(emergencyBtn, modalFooter.firstChild);
                    console.log('🚨 紧急提交按钮已添加');
                }
            } else {
                setTimeout(checkModal, 500);
            }
        };
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', checkModal);
        } else {
            checkModal();
        }
    }
    
    // 添加控制台快捷方式
    console.log('🚨 紧急修复已就绪！');
    console.log('💡 使用方法：');
    console.log('   1. 在控制台输入: emergencySubmitBuyRecord()');
    console.log('   2. 或者点击模态框中的"🚨 紧急提交"按钮');
    console.log('   3. 确保表单已填写完整');
    
    // 创建紧急按钮
    createEmergencyButton();
    
    // 添加键盘快捷键 Ctrl+Shift+E
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'E') {
            e.preventDefault();
            console.log('🚨 快捷键触发紧急提交');
            window.emergencySubmitBuyRecord();
        }
    });
    
})();