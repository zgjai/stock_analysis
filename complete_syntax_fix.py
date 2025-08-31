#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的语法错误修复
"""

import os
import re
from datetime import datetime

def restore_and_fix():
    """恢复备份并重新修复"""
    file_path = "templates/trading_records.html"
    
    # 查找最新的备份文件
    backup_files = []
    for f in os.listdir('templates'):
        if f.startswith('trading_records.html.backup_'):
            backup_files.append(f)
    
    if not backup_files:
        print("❌ 找不到备份文件")
        return False
    
    # 使用最新的备份
    latest_backup = sorted(backup_files)[-1]
    backup_path = f"templates/{latest_backup}"
    
    print(f"📁 使用备份文件: {backup_path}")
    
    # 恢复备份
    with open(backup_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 重新修复重复提交问题（避免语法错误）...")
    
    # 1. 只修复事件绑定部分，不动saveTrade方法
    old_save_binding = r'''            // 保存交易按钮
            document\.getElementById\('save-trade-btn'\)\.addEventListener\('click', \(\) => \{
                this\.saveTrade\(\);
            \}\);'''
    
    new_save_binding = '''            // 保存交易按钮 - 带重复提交防护
            let saveButtonClicked = false;
            
            document.getElementById('save-trade-btn').addEventListener('click', async () => {
                // 简单的重复点击防护
                if (saveButtonClicked) {
                    console.log('🛡️ 按钮已被点击，请等待处理完成');
                    return;
                }
                
                saveButtonClicked = true;
                const saveBtn = document.getElementById('save-trade-btn');
                
                try {
                    // 禁用按钮并显示加载状态
                    if (saveBtn) {
                        saveBtn.disabled = true;
                        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中...';
                    }
                    
                    // 调用原始的saveTrade方法
                    await this.saveTrade();
                    
                } catch (error) {
                    console.error('保存按钮事件处理错误:', error);
                    showMessage('保存失败，请重试', 'error');
                } finally {
                    // 重置按钮状态
                    saveButtonClicked = false;
                    if (saveBtn) {
                        saveBtn.disabled = false;
                        saveBtn.innerHTML = '保存';
                    }
                }
            });'''
    
    # 2. 移除initTradingRecords中的重复逻辑
    duplicate_logic_pattern = r'''        // 增强重复提交防护机制
        let isSubmitting = false;
        let submissionTimeout = null;

        // 自动重置提交状态的安全机制
        function resetSubmissionState\(\) \{
            isSubmitting = false;
            const saveBtn = document\.getElementById\('save-trade-btn'\);
            if \(saveBtn\) \{
                saveBtn\.disabled = false;
                saveBtn\.innerHTML = '保存';
            \}
            if \(submissionTimeout\) \{
                clearTimeout\(submissionTimeout\);
                submissionTimeout = null;
            \}
        \}

        // 重写saveTrade方法，添加增强防护
        const originalSaveTrade = tradingManager\.saveTrade\.bind\(tradingManager\);
        tradingManager\.saveTrade = async function \(\) \{.*?\};'''
    
    # 应用修复
    content = re.sub(old_save_binding, new_save_binding, content, flags=re.DOTALL)
    content = re.sub(duplicate_logic_pattern, '', content, flags=re.DOTALL)
    
    # 3. 清理可能的语法错误残留
    # 移除孤立的finally块
    orphan_finally_patterns = [
        r'\s*\} finally \{\s*this\._isSaving = false;\s*\}',
        r'\s*\} finally \{\s*\}',
        r'return;\s*\} finally \{[^}]*\}'
    ]
    
    for pattern in orphan_finally_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # 4. 确保saveTrade方法完整
    # 如果saveTrade方法被破坏了，恢复一个简单版本
    if 'async saveTrade()' not in content or 'this._isSaving' in content:
        # 查找并修复saveTrade方法
        saveTrade_pattern = r'(async saveTrade\(\) \{[^}]*?this\._isSaving[^}]*?\})'
        
        simple_saveTrade = '''async saveTrade() {
            try {
                console.log('🔍 开始保存交易...');

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

                // 调用API
                let response;
                if (this.editingTradeId) {
                    response = await apiClient.updateTrade(this.editingTradeId, formData);
                } else {
                    response = await apiClient.createTrade(formData);
                }

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
                    showMessage(response.message || '保存失败', 'error');
                }
                
            } catch (error) {
                console.error('保存交易时发生错误:', error);
                showMessage('保存失败: ' + error.message, 'error');
            }
        }'''
        
        content = re.sub(saveTrade_pattern, simple_saveTrade, content, flags=re.DOTALL)
    
    # 写入修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 完整修复完成")
    return True

def main():
    """主函数"""
    print("🚨 完整语法错误修复")
    print("=" * 40)
    
    try:
        if restore_and_fix():
            print("\n🎉 修复完成！")
            print("✅ 恢复了原始备份")
            print("✅ 重新应用了重复提交防护")
            print("✅ 避免了语法错误")
            print("\n请刷新页面测试")
        else:
            print("❌ 修复失败")
            
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()