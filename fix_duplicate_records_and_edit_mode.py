#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复重复记录和编辑模式问题
1. 修复保存时出现重复记录的问题
2. 修复编辑时仍需选择买入/卖出的问题
"""

import os
import re
from datetime import datetime

def backup_file(file_path):
    """备份文件"""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已备份文件: {backup_path}")
        return backup_path
    return None

def fix_duplicate_submission_issue():
    """修复重复提交问题"""
    file_path = "templates/trading_records.html"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 备份文件
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 增强重复提交防护机制
    old_duplicate_protection = r'''        // 添加重复提交防护 - 简化版本
        let isSubmitting = false;

        // 重写saveTrade方法，添加防护
        const originalSaveTrade = tradingManager\.saveTrade\.bind\(tradingManager\);
        tradingManager\.saveTrade = async function \(\) \{
            if \(isSubmitting\) \{
                console\.log\('🛡️ 正在提交中，忽略重复请求'\);
                return;
            \}

            isSubmitting = true;
            const saveBtn = document\.getElementById\('save-trade-btn'\);
            
            try \{
                if \(saveBtn\) \{
                    saveBtn\.disabled = true;
                    saveBtn\.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中\.\.\.';
                \}'''
    
    new_duplicate_protection = '''        // 增强重复提交防护机制
        let isSubmitting = false;
        let submissionTimeout = null;

        // 自动重置提交状态的安全机制
        function resetSubmissionState() {
            isSubmitting = false;
            const saveBtn = document.getElementById('save-trade-btn');
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = '保存';
            }
            if (submissionTimeout) {
                clearTimeout(submissionTimeout);
                submissionTimeout = null;
            }
        }

        // 重写saveTrade方法，添加增强防护
        const originalSaveTrade = tradingManager.saveTrade.bind(tradingManager);
        tradingManager.saveTrade = async function () {
            if (isSubmitting) {
                console.log('🛡️ 正在提交中，忽略重复请求');
                return;
            }

            isSubmitting = true;
            const saveBtn = document.getElementById('save-trade-btn');
            
            // 设置10秒超时自动重置，防止永久卡住
            submissionTimeout = setTimeout(() => {
                console.warn('⚠️ 提交超时，自动重置状态');
                resetSubmissionState();
            }, 10000);
            
            try {
                if (saveBtn) {
                    saveBtn.disabled = true;
                    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中...';
                }'''
    
    # 2. 修复提交完成后的状态重置
    old_submission_end = r'''                \} else \{
                    showMessage\(response\.message \|\| '保存失败', 'error'\);
                \}
                

            \} catch \(error\) \{
                console\.error\('保存交易失败:', error\);
                showMessage\('保存失败，请重试', 'error'\);
            \} finally \{
                isSubmitting = false;
                if \(saveBtn\) \{
                    saveBtn\.disabled = false;
                    saveBtn\.innerHTML = '保存';
                \}
            \}
        \};'''
    
    new_submission_end = '''                } else {
                    showMessage(response.message || '保存失败', 'error');
                }

            } catch (error) {
                console.error('保存交易失败:', error);
                showMessage('保存失败，请重试', 'error');
            } finally {
                // 确保状态重置
                resetSubmissionState();
            }
        };'''
    
    # 应用修复
    content = re.sub(old_duplicate_protection, new_duplicate_protection, content, flags=re.DOTALL)
    content = re.sub(old_submission_end, new_submission_end, content, flags=re.DOTALL)
    
    # 3. 添加额外的防护机制
    additional_protection = '''
        // 额外防护：监听表单提交事件，防止重复提交
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('trade-form');
            if (form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    if (isSubmitting) {
                        console.log('🛡️ 表单提交被阻止：正在处理中');
                        return false;
                    }
                    return false;
                });
            }
        });

        // 页面卸载时重置状态
        window.addEventListener('beforeunload', function() {
            resetSubmissionState();
        });
'''
    
    # 在脚本结束前添加额外防护
    content = content.replace('</script>\n{% endblock %}', additional_protection + '</script>\n{% endblock %}')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 重复提交防护机制已增强")
    return True

def fix_edit_mode_issue():
    """修复编辑模式问题"""
    file_path = "templates/trading_records.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 修复模态框显示事件监听器
    old_modal_listener = r'''            // 模态框显示时初始化交易类型选择
            document\.getElementById\('addTradeModal'\)\.addEventListener\('show\.bs\.modal', \(\) => \{
                // 如果不是编辑模式，显示交易类型选择
                if \(!this\.editingTradeId\) \{
                    this\.showTradeTypeSelection\(\);
                \}
            \}\);'''
    
    new_modal_listener = '''            // 模态框显示时初始化交易类型选择
            document.getElementById('addTradeModal').addEventListener('show.bs.modal', () => {
                console.log('模态框显示事件触发，editingTradeId:', this.editingTradeId);
                
                // 如果不是编辑模式，显示交易类型选择
                if (!this.editingTradeId) {
                    console.log('新建模式：显示交易类型选择');
                    this.showTradeTypeSelection();
                } else {
                    console.log('编辑模式：跳过交易类型选择，直接显示表单');
                    // 编辑模式：直接显示表单，跳过交易类型选择
                    document.getElementById('trade-type-selection').style.display = 'none';
                    document.getElementById('trade-form-container').style.display = 'block';
                    document.getElementById('back-to-type-selection').style.display = 'none';
                    document.getElementById('save-trade-btn').style.display = 'inline-block';
                }
            });'''
    
    # 2. 修复editTrade方法中的界面显示逻辑
    old_edit_display = r'''                    // 编辑模式：直接显示表单，跳过交易类型选择
                    document\.getElementById\('trade-type-selection'\)\.style\.display = 'none';
                    document\.getElementById\('trade-form-container'\)\.style\.display = 'block';
                    document\.getElementById\('back-to-type-selection'\)\.style\.display = 'none';
                    document\.getElementById\('save-trade-btn'\)\.style\.display = 'inline-block';'''
    
    new_edit_display = '''                    // 编辑模式：确保界面状态正确
                    console.log('设置编辑模式界面状态...');
                    
                    // 强制隐藏交易类型选择界面
                    const typeSelection = document.getElementById('trade-type-selection');
                    const formContainer = document.getElementById('trade-form-container');
                    const backBtn = document.getElementById('back-to-type-selection');
                    const saveBtn = document.getElementById('save-trade-btn');
                    
                    if (typeSelection) typeSelection.style.display = 'none';
                    if (formContainer) formContainer.style.display = 'block';
                    if (backBtn) backBtn.style.display = 'none';
                    if (saveBtn) saveBtn.style.display = 'inline-block';
                    
                    console.log('编辑模式界面状态设置完成');'''
    
    # 3. 修复resetTradeForm方法，确保编辑状态正确重置
    old_reset_form = r'''            // 重置界面显示状态
            this\.showTradeTypeSelection\(\);

            // 最后重置编辑状态（在处理完日期之后）
            this\.editingTradeId = null;'''
    
    new_reset_form = '''            // 重置界面显示状态
            console.log('重置表单，当前编辑状态:', this.editingTradeId);
            
            // 只有在非编辑模式下才显示交易类型选择
            if (!this.editingTradeId) {
                this.showTradeTypeSelection();
            }

            // 最后重置编辑状态（在处理完日期之后）
            this.editingTradeId = null;
            console.log('表单重置完成，编辑状态已清除');'''
    
    # 应用修复
    content = re.sub(old_modal_listener, new_modal_listener, content, flags=re.DOTALL)
    content = re.sub(old_edit_display, new_edit_display, content, flags=re.DOTALL)
    content = re.sub(old_reset_form, new_reset_form, content, flags=re.DOTALL)
    
    # 4. 添加模态框隐藏时的清理逻辑
    modal_hide_cleanup = '''
        // 模态框隐藏时清理状态
        document.getElementById('addTradeModal').addEventListener('hidden.bs.modal', () => {
            console.log('模态框已隐藏，清理状态');
            
            // 重置提交状态
            if (typeof resetSubmissionState === 'function') {
                resetSubmissionState();
            }
            
            // 清理编辑状态
            if (tradingManager) {
                tradingManager.editingTradeId = null;
            }
            
            console.log('状态清理完成');
        });
'''
    
    # 在事件监听器设置后添加清理逻辑
    content = content.replace(
        '            // 返回类型选择按钮',
        modal_hide_cleanup + '            // 返回类型选择按钮'
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 编辑模式界面逻辑已修复")
    return True

def main():
    """主函数"""
    print("🔧 开始修复重复记录和编辑模式问题...")
    print("=" * 50)
    
    try:
        # 修复重复提交问题
        print("\n1. 修复重复提交问题...")
        if fix_duplicate_submission_issue():
            print("✅ 重复提交问题修复完成")
        else:
            print("❌ 重复提交问题修复失败")
            return
        
        # 修复编辑模式问题
        print("\n2. 修复编辑模式问题...")
        if fix_edit_mode_issue():
            print("✅ 编辑模式问题修复完成")
        else:
            print("❌ 编辑模式问题修复失败")
            return
        
        print("\n" + "=" * 50)
        print("🎉 所有问题修复完成！")
        print("\n修复内容:")
        print("1. ✅ 增强了重复提交防护机制")
        print("   - 添加了超时自动重置")
        print("   - 改进了状态管理")
        print("   - 增加了额外的防护层")
        print("\n2. ✅ 修复了编辑模式界面问题")
        print("   - 编辑时直接显示表单，不再需要选择交易类型")
        print("   - 改进了模态框事件处理")
        print("   - 增强了状态清理机制")
        
        print("\n🔍 测试建议:")
        print("1. 测试新建交易记录（应该显示交易类型选择）")
        print("2. 测试编辑交易记录（应该直接显示表单）")
        print("3. 测试快速多次点击保存按钮（应该不会产生重复记录）")
        print("4. 测试网络较慢时的保存操作")
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()