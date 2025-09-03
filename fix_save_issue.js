// 修复保存问题的脚本
// 这个脚本将修复isSubmitting状态被卡住的问题

(function() {
    console.log('🔧 开始修复保存问题...');
    
    // 查找trading_records.html中的isSubmitting变量
    // 由于它是在闭包中定义的，我们需要通过重写方法来修复
    
    if (window.tradingManager) {
        // 保存原始方法的引用
        const originalSaveTrade = window.tradingManager.saveTrade;
        const originalHandleSubmit = window.tradingManager.handleTradeFormSubmit;
        
        // 创建一个全局的提交状态管理器
        window.submitStateManager = {
            isSubmitting: false,
            
            setSubmitting: function(state) {
                this.isSubmitting = state;
                console.log('📊 提交状态设置为:', state);
                
                // 更新按钮状态
                const saveBtn = document.getElementById('save-trade-btn');
                if (saveBtn) {
                    saveBtn.disabled = state;
                    saveBtn.innerHTML = state ? '<span class="spinner-border spinner-border-sm me-2"></span>保存中...' : '保存';
                }
            },
            
            reset: function() {
                this.setSubmitting(false);
                console.log('✅ 提交状态已重置');
            }
        };
        
        // 重写saveTrade方法
        window.tradingManager.saveTrade = async function() {
            console.log('🔍 开始保存交易...');
            
            if (window.submitStateManager.isSubmitting) {
                console.log('🛡️ 正在提交中，忽略重复请求');
                return;
            }
            
            window.submitStateManager.setSubmitting(true);
            
            try {
                // 使用简洁验证器验证表单
                if (!this.simpleValidator.validateForm()) {
                    console.log('❌ 表单验证失败:', this.simpleValidator.errors);
                    showMessage('请检查表单中的错误信息', 'error');
                    return;
                }
                
                console.log('✅ 表单验证通过');
                
                // 获取表单数据
                const formData = this.simpleValidator.getFormData();
                console.log('📝 表单数据:', formData);
                
                // 处理表单提交
                await this.handleTradeFormSubmit(formData);
                
            } catch (error) {
                console.error('保存交易时发生错误:', error);
                showMessage('保存失败: ' + error.message, 'error');
            } finally {
                window.submitStateManager.reset();
            }
        };
        
        // 重写handleTradeFormSubmit方法，确保所有return都不会导致状态卡住
        window.tradingManager.handleTradeFormSubmit = async function(formData) {
            try {
                console.log('[DEBUG] handleTradeFormSubmit 接收到的 formData:', formData);
                
                // 验证必填字段
                const requiredFields = ['stock_code', 'stock_name', 'trade_type', 'reason', 'price', 'quantity'];
                
                for (const field of requiredFields) {
                    if (!formData[field] || formData[field].toString().trim() === '') {
                        // 尝试从DOM获取
                        const element = document.getElementById(field.replace('_', '-'));
                        if (element && element.value && element.value.trim() !== '') {
                            formData[field] = element.value.trim();
                            console.log(`[DEBUG] 从DOM获取${field}:`, formData[field]);
                        } else {
                            const fieldNames = {
                                'stock_code': '股票代码',
                                'stock_name': '股票名称', 
                                'trade_type': '交易类型',
                                'reason': '操作原因',
                                'price': '价格',
                                'quantity': '数量'
                            };
                            throw new Error(`${fieldNames[field]}不能为空`);
                        }
                    }
                }
                
                // 处理数值字段
                if (formData.price) {
                    const price = parseFloat(formData.price);
                    if (isNaN(price) || price <= 0) {
                        throw new Error('价格必须是大于0的数字');
                    }
                    formData.price = price;
                }
                
                if (formData.quantity) {
                    const quantity = parseInt(formData.quantity);
                    if (isNaN(quantity) || quantity <= 0) {
                        throw new Error('数量必须是大于0的整数');
                    }
                    formData.quantity = quantity;
                }
                
                console.log('[DEBUG] 验证通过，准备提交到API...');
                
                // 调用API
                let response;
                if (this.editingTradeId) {
                    console.log('[DEBUG] 更新交易记录:', this.editingTradeId);
                    response = await apiClient.updateTrade(this.editingTradeId, formData);
                } else {
                    console.log('[DEBUG] 创建新交易记录');
                    response = await apiClient.createTrade(formData);
                }
                
                console.log('[DEBUG] API响应:', response);
                
                if (response.success) {
                    showMessage(this.editingTradeId ? '交易记录更新成功' : '交易记录创建成功', 'success');
                    
                    // 关闭模态框
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addTradeModal'));
                    if (modal) {
                        modal.hide();
                    }
                    
                    // 重新加载交易记录
                    await this.loadTrades();
                } else {
                    throw new Error(response.message || '保存失败');
                }
                
            } catch (error) {
                console.error('[DEBUG] handleTradeFormSubmit错误:', error);
                throw error; // 重新抛出错误，让上层处理
            }
        };
        
        console.log('✅ 保存方法已修复');
        
        // 提供手动重置功能
        window.resetSaveState = function() {
            window.submitStateManager.reset();
        };
        
        console.log('🔧 修复完成。如需手动重置状态，请运行: resetSaveState()');
        
    } else {
        console.log('❌ tradingManager不存在，无法修复');
    }
})();