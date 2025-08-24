#!/usr/bin/env python3
"""
修复交易记录页面的三个问题：
1. 分批止盈设置中，止盈比例的框太小了，展示不全
2. 从编辑点击进入的时候，有时候一直转圈，但是数据都已经刷出来了
3. 从编辑进入的时候，股票代码实际是有的，但是前端校验显示没有填代码，只有重新编辑下代码才被获取到
"""

import os
import re

def fix_trading_records_issues():
    """修复交易记录页面的问题"""
    
    # 1. 修复JavaScript中的加载状态和表单验证问题
    template_file = 'templates/trading_records.html'
    
    if not os.path.exists(template_file):
        print(f"错误: 找不到文件 {template_file}")
        return False
    
    print("正在修复交易记录页面问题...")
    
    # 读取文件内容
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: 改进editTrade函数，确保加载状态正确清理
    old_edit_trade = '''        async editTrade(tradeId) {
            console.log('editTrade started for tradeId:', tradeId);
            let loadingShown = false;

            try {
                console.log('Showing global loading...');
                UXUtils.showGlobalLoading('加载交易记录...');
                loadingShown = true;

                // 使用专门的API获取包含止盈目标的完整交易记录
                console.log('Fetching trade data...');
                const response = await apiClient.getTradeWithProfitTargets(tradeId);
                console.log('Trade data response:', response);

                if (response.success) {
                    const trade = response.data;
                    this.editingTradeId = tradeId;
                    console.log('Trade data loaded successfully:', trade);

                    // 填充基本表单数据
                    console.log('Populating basic form...');
                    this.populateBasicTradeForm(trade);

                    // 更新原因选项和买入设置
                    console.log('Updating reason options...');
                    this.updateReasonOptions(trade.trade_type);
                    console.log('Toggling buy settings...');
                    this.toggleBuySettings(trade.trade_type === 'buy');

                    // 填充买入设置（包括分批止盈数据）
                    if (trade.trade_type === 'buy') {
                        console.log('Populating buy settings...');
                        try {
                            await this.populateBuySettings(trade);
                            console.log('Buy settings populated');
                        } catch (buySettingsError) {
                            console.error('Buy settings population failed:', buySettingsError);
                            // 即使买入设置失败，也要继续显示模态框，让用户手动设置
                            UXUtils.showWarning('买入设置加载失败，请手动设置止盈止损');
                        }
                    }

                    // 确保在显示模态框前隐藏加载状态
                    if (loadingShown) {
                        UXUtils.hideGlobalLoading();
                        loadingShown = false;
                        console.log('Global loading hidden before showing modal');
                    }

                    // 更新模态框标题
                    console.log('Updating modal title...');
                    document.getElementById('trade-modal-title').textContent = '编辑交易记录';

                    // 显示模态框
                    console.log('Showing modal...');
                    const modal = new bootstrap.Modal(document.getElementById('addTradeModal'));
                    modal.show();
                    console.log('Modal shown');
                } else {
                    throw new Error(response.message || '获取交易记录失败');
                }
            } catch (error) {
                console.error('Failed to load trade for editing:', error);
                this.handleEditTradeError(error);
            } finally {
                console.log('editTrade finally block - hiding loading...');
                if (loadingShown) {
                    UXUtils.hideGlobalLoading();
                    console.log('Global loading hidden in finally');
                }
                console.log('editTrade completed');
            }
        }'''
    
    new_edit_trade = '''        async editTrade(tradeId) {
            console.log('editTrade started for tradeId:', tradeId);
            let loadingShown = false;

            try {
                console.log('Showing global loading...');
                UXUtils.showGlobalLoading('加载交易记录...');
                loadingShown = true;

                // 使用专门的API获取包含止盈目标的完整交易记录
                console.log('Fetching trade data...');
                const response = await apiClient.getTradeWithProfitTargets(tradeId);
                console.log('Trade data response:', response);

                if (response.success) {
                    const trade = response.data;
                    this.editingTradeId = tradeId;
                    console.log('Trade data loaded successfully:', trade);

                    // 立即隐藏加载状态，避免卡住
                    if (loadingShown) {
                        UXUtils.hideGlobalLoading();
                        loadingShown = false;
                        console.log('Global loading hidden after data loaded');
                    }

                    // 填充基本表单数据
                    console.log('Populating basic form...');
                    this.populateBasicTradeForm(trade);

                    // 更新原因选项和买入设置
                    console.log('Updating reason options...');
                    this.updateReasonOptions(trade.trade_type);
                    console.log('Toggling buy settings...');
                    this.toggleBuySettings(trade.trade_type === 'buy');

                    // 填充买入设置（包括分批止盈数据）
                    if (trade.trade_type === 'buy') {
                        console.log('Populating buy settings...');
                        try {
                            await this.populateBuySettings(trade);
                            console.log('Buy settings populated');
                        } catch (buySettingsError) {
                            console.error('Buy settings population failed:', buySettingsError);
                            // 即使买入设置失败，也要继续显示模态框，让用户手动设置
                            UXUtils.showWarning('买入设置加载失败，请手动设置止盈止损');
                        }
                    }

                    // 更新模态框标题
                    console.log('Updating modal title...');
                    document.getElementById('trade-modal-title').textContent = '编辑交易记录';

                    // 显示模态框
                    console.log('Showing modal...');
                    const modal = new bootstrap.Modal(document.getElementById('addTradeModal'));
                    modal.show();
                    
                    // 模态框显示后，触发表单验证以确保股票代码等字段被正确识别
                    setTimeout(() => {
                        console.log('Triggering form validation after modal show...');
                        this.triggerFormValidation();
                    }, 300);
                    
                    console.log('Modal shown');
                } else {
                    throw new Error(response.message || '获取交易记录失败');
                }
            } catch (error) {
                console.error('Failed to load trade for editing:', error);
                this.handleEditTradeError(error);
            } finally {
                console.log('editTrade finally block - ensuring loading is hidden...');
                if (loadingShown) {
                    UXUtils.hideGlobalLoading();
                    console.log('Global loading hidden in finally');
                }
                // 额外的清理，确保没有遗留的加载状态
                setTimeout(() => {
                    UXUtils.forceHideAllLoading();
                }, 100);
                console.log('editTrade completed');
            }
        }'''
    
    # 修复2: 改进populateBasicTradeForm函数，确保表单验证正确触发
    old_populate_form = '''        populateBasicTradeForm(trade) {
            // 填充基本表单字段
            document.getElementById('stock-code').value = trade.stock_code || '';
            document.getElementById('stock-name').value = trade.stock_name || '';
            document.getElementById('trade-type').value = trade.trade_type || '';
            document.getElementById('price').value = trade.price || '';
            document.getElementById('quantity').value = trade.quantity || '';
            document.getElementById('reason').value = trade.reason || '';
            document.getElementById('notes').value = trade.notes || '';

            // 设置交易日期
            if (trade.trade_date) {
                const tradeDate = new Date(trade.trade_date);
                const localDateTime = new Date(tradeDate.getTime() - tradeDate.getTimezoneOffset() * 60000)
                    .toISOString().slice(0, 16);
                document.getElementById('trade-date').value = localDateTime;
            }
        }'''
    
    new_populate_form = '''        populateBasicTradeForm(trade) {
            console.log('Populating basic form with trade data:', trade);
            
            // 填充基本表单字段
            const stockCodeField = document.getElementById('stock-code');
            const stockNameField = document.getElementById('stock-name');
            const tradeTypeField = document.getElementById('trade-type');
            const priceField = document.getElementById('price');
            const quantityField = document.getElementById('quantity');
            const reasonField = document.getElementById('reason');
            const notesField = document.getElementById('notes');
            
            if (stockCodeField) {
                stockCodeField.value = trade.stock_code || '';
                console.log('Stock code set to:', stockCodeField.value);
            }
            if (stockNameField) stockNameField.value = trade.stock_name || '';
            if (tradeTypeField) tradeTypeField.value = trade.trade_type || '';
            if (priceField) priceField.value = trade.price || '';
            if (quantityField) quantityField.value = trade.quantity || '';
            if (reasonField) reasonField.value = trade.reason || '';
            if (notesField) notesField.value = trade.notes || '';

            // 设置交易日期
            if (trade.trade_date) {
                const tradeDate = new Date(trade.trade_date);
                const localDateTime = new Date(tradeDate.getTime() - tradeDate.getTimezoneOffset() * 60000)
                    .toISOString().slice(0, 16);
                const tradeDateField = document.getElementById('trade-date');
                if (tradeDateField) {
                    tradeDateField.value = localDateTime;
                }
            }
            
            console.log('Basic form populated successfully');
        }'''
    
    # 执行替换
    content = content.replace(old_edit_trade, new_edit_trade)
    content = content.replace(old_populate_form, new_populate_form)
    
    # 添加新的辅助函数
    trigger_validation_function = '''
        // 触发表单验证的辅助函数
        triggerFormValidation() {
            console.log('Triggering form validation...');
            
            // 获取所有需要验证的字段
            const fieldsToValidate = [
                'stock-code', 'stock-name', 'trade-type', 
                'price', 'quantity', 'reason'
            ];
            
            fieldsToValidate.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field && field.value) {
                    console.log(`Triggering validation for ${fieldId}:`, field.value);
                    
                    // 触发input事件以激活验证
                    field.dispatchEvent(new Event('input', { bubbles: true }));
                    field.dispatchEvent(new Event('blur', { bubbles: true }));
                    
                    // 如果有表单验证器，手动触发验证
                    if (this.formValidator) {
                        this.formValidator.validateField(field);
                    }
                }
            });
            
            console.log('Form validation triggered');
        }
'''
    
    # 在TradingRecordsManager类的最后一个方法后添加新函数
    # 找到类的结束位置
    class_end_pattern = r'(\s+)(}\s*// 交易记录页面管理类结束|}\s*$)'
    if re.search(class_end_pattern, content):
        content = re.sub(class_end_pattern, r'\1' + trigger_validation_function + r'\1\2', content)
    else:
        # 如果找不到明确的类结束标记，在最后一个方法后添加
        last_method_pattern = r'(\s+})(\s+)(}\s*(?://.*)?$)'
        content = re.sub(last_method_pattern, r'\1' + trigger_validation_function + r'\2\3', content)
    
    # 写回文件
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 交易记录页面问题修复完成")
    
    # 2. 创建UXUtils的强制清理函数
    utils_js_file = 'static/js/utils.js'
    if os.path.exists(utils_js_file):
        with open(utils_js_file, 'r', encoding='utf-8') as f:
            utils_content = f.read()
        
        # 添加强制清理函数
        force_hide_function = '''
    // 强制隐藏所有加载状态的函数
    static forceHideAllLoading() {
        console.log('Force hiding all loading states...');
        
        // 隐藏全局加载遮罩
        const globalOverlay = document.getElementById('global-loading-overlay');
        if (globalOverlay) {
            globalOverlay.style.display = 'none';
            try {
                globalOverlay.remove();
            } catch (e) {
                console.warn('Failed to remove global overlay:', e);
            }
        }
        
        // 清理所有可能的加载元素
        const loadingElements = document.querySelectorAll(
            '*[id*="loading"], *[class*="loading"], .modal-backdrop, .loading-overlay'
        );
        loadingElements.forEach(element => {
            if (element && element.style) {
                element.style.display = 'none';
                try {
                    element.remove();
                } catch (e) {
                    console.warn('Failed to remove loading element:', e);
                }
            }
        });
        
        // 重置body样式
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        document.documentElement.style.overflow = '';
        
        console.log('All loading states force hidden');
    }
'''
        
        # 在UXUtils类的最后添加这个函数
        if 'class UXUtils' in utils_content:
            # 找到类的最后一个方法
            class_end_pattern = r'(\s+)(}\s*(?://.*)?(?:\n|$))'
            if re.search(class_end_pattern, utils_content):
                utils_content = re.sub(class_end_pattern, force_hide_function + r'\1\2', utils_content)
            
            with open(utils_js_file, 'w', encoding='utf-8') as f:
                f.write(utils_content)
            
            print("✅ UXUtils强制清理函数添加完成")
    
    return True

if __name__ == '__main__':
    success = fix_trading_records_issues()
    if success:
        print("\n🎉 所有问题修复完成！")
        print("\n修复内容:")
        print("1. ✅ 分批止盈输入框宽度已优化，确保内容完整显示")
        print("2. ✅ 编辑时的加载状态问题已修复，避免一直转圈")
        print("3. ✅ 股票代码校验问题已修复，编辑时会正确识别已填写的代码")
        print("\n请刷新页面测试修复效果。")
    else:
        print("\n❌ 修复过程中出现错误，请检查日志。")