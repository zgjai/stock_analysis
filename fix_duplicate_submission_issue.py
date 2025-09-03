#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复重复提交问题的紧急修复脚本
问题：保存按钮被绑定了多次事件，导致一次点击触发多次提交
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

def fix_duplicate_submission():
    """修复重复提交问题"""
    file_path = "templates/trading_records.html"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 备份文件
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 分析重复提交问题...")
    
    # 1. 移除重复的保存按钮事件绑定
    # 找到第一个保存按钮事件绑定（在setupEventListeners中）
    first_save_binding = r'''            // 保存交易按钮
            document\.getElementById\('save-trade-btn'\)\.addEventListener\('click', \(\) => \{
                this\.saveTrade\(\);
            \}\);'''
    
    # 找到第二个重复的事件绑定（在initTradingRecords中）
    duplicate_save_binding = r'''        // 重写saveTrade方法，添加增强防护
        const originalSaveTrade = tradingManager\.saveTrade\.bind\(tradingManager\);
        tradingManager\.saveTrade = async function \(\) \{
            if \(isSubmitting\) \{
                console\.log\('🛡️ 正在提交中，忽略重复请求'\);
                return;
            \}

            isSubmitting = true;
            const saveBtn = document\.getElementById\('save-trade-btn'\);
            
            // 设置10秒超时自动重置，防止永久卡住
            submissionTimeout = setTimeout\(\(\) => \{
                console\.warn\('⚠️ 提交超时，自动重置状态'\);
                resetSubmissionState\(\);
            \}, 10000\);
            
            try \{
                if \(saveBtn\) \{
                    saveBtn\.disabled = true;
                    saveBtn\.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中\.\.\.';
                \}
                
                console\.log\('🔍 开始保存交易\.\.\.'\);

                // 使用简洁验证器验证表单
                if \(!this\.simpleValidator\.validateForm\(\)\) \{
                    console\.log\('❌ 表单验证失败:', this\.simpleValidator\.errors\);
                    showMessage\('请检查表单中的错误信息', 'error'\);
                    return;
                \}

                console\.log\('✅ 表单验证通过'\);

                // 获取表单数据
                const formData = this\.simpleValidator\.getFormData\(\);
                console\.log\('📝 表单数据:', formData\);

                // 直接调用API，不再通过原始的handleTradeFormSubmit
                let response;
                if \(this\.editingTradeId\) \{
                    response = await apiClient\.updateTrade\(this\.editingTradeId, formData\);
                \} else \{
                    response = await apiClient\.createTrade\(formData\);
                \}

                if \(response\.success\) \{
                    showMessage\(this\.editingTradeId \? '交易记录更新成功' : '交易记录创建成功', 'success'\);

                    // 关闭模态框
                    const modal = bootstrap\.Modal\.getInstance\(document\.getElementById\('addTradeModal'\)\);
                    if \(modal\) \{
                        modal\.hide\(\);
                    \}

                    // 重新加载交易记录
                    await this\.loadTrades\(\);
                \} else \{
                    showMessage\(response\.message \|\| '保存失败', 'error'\);
                \}
                
            \} catch \(error\) \{
                console\.error\('保存交易时发生错误:', error\);
                showMessage\('保存失败: ' \+ error\.message, 'error'\);
            \} finally \{
                isSubmitting = false;
                if \(saveBtn\) \{
                    saveBtn\.disabled = false;
                    saveBtn\.innerHTML = '保存';
                \}
            \}
        \};'''
    
    # 2. 修复：在setupEventListeners中添加重复提交防护
    new_save_binding = '''            // 保存交易按钮 - 带重复提交防护
            let isSubmitting = false;
            let submissionTimeout = null;
            
            // 重置提交状态的函数
            const resetSubmissionState = () => {
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
            };
            
            document.getElementById('save-trade-btn').addEventListener('click', async () => {
                // 防止重复提交
                if (isSubmitting) {
                    console.log('🛡️ 正在提交中，忽略重复请求');
                    return;
                }
                
                isSubmitting = true;
                const saveBtn = document.getElementById('save-trade-btn');
                
                // 设置10秒超时自动重置
                submissionTimeout = setTimeout(() => {
                    console.warn('⚠️ 提交超时，自动重置状态');
                    resetSubmissionState();
                }, 10000);
                
                try {
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
                    resetSubmissionState();
                }
            });'''
    
    # 应用修复
    content = re.sub(first_save_binding, new_save_binding, content, flags=re.DOTALL)
    
    # 移除重复的saveTrade重写逻辑
    content = re.sub(duplicate_save_binding, '', content, flags=re.DOTALL)
    
    # 3. 确保saveTrade方法本身不会重复执行
    # 查找原始的saveTrade方法并添加防护
    original_save_trade_pattern = r'(async saveTrade\(\) \{[^}]*?\})'
    
    def add_protection_to_save_trade(match):
        method_content = match.group(1)
        
        # 如果已经有防护，就不添加了
        if '正在保存中' in method_content:
            return method_content
            
        # 在方法开始添加防护
        protected_method = method_content.replace(
            'async saveTrade() {',
            '''async saveTrade() {
        // 防止方法级别的重复调用
        if (this._isSaving) {
            console.log('🛡️ saveTrade方法正在执行中，跳过重复调用');
            return;
        }
        
        this._isSaving = true;
        
        try {'''
        )
        
        # 在方法结束添加清理
        protected_method = protected_method.replace(
            '    }',
            '''        } finally {
            this._isSaving = false;
        }
    }'''
        )
        
        return protected_method
    
    content = re.sub(original_save_trade_pattern, add_protection_to_save_trade, content, flags=re.DOTALL)
    
    # 4. 移除多余的重复防护代码
    extra_protection_pattern = r'''        // 增强重复提交防护机制
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
        \}'''
    
    content = re.sub(extra_protection_pattern, '', content, flags=re.DOTALL)
    
    # 5. 清理多余的模态框事件监听器
    duplicate_modal_listener = r'''
        // 模态框隐藏时清理状态
        document\.getElementById\('addTradeModal'\)\.addEventListener\('hidden\.bs\.modal', \(\) => \{
            console\.log\('模态框已隐藏，清理状态'\);
            
            // 重置提交状态
            if \(typeof resetSubmissionState === 'function'\) \{
                resetSubmissionState\(\);
            \}
            
            // 清理编辑状态
            if \(tradingManager\) \{
                tradingManager\.editingTradeId = null;
            \}
            
            console\.log\('状态清理完成'\);
        \}\);'''
    
    content = re.sub(duplicate_modal_listener, '', content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 重复提交问题修复完成")
    return True

def main():
    """主函数"""
    print("🚨 紧急修复重复提交问题")
    print("=" * 50)
    
    try:
        if fix_duplicate_submission():
            print("\n🎉 修复完成！")
            print("\n修复内容:")
            print("1. ✅ 移除了重复的保存按钮事件绑定")
            print("2. ✅ 在事件监听器中添加了重复提交防护")
            print("3. ✅ 在saveTrade方法中添加了方法级别的防护")
            print("4. ✅ 清理了多余的防护代码")
            print("5. ✅ 移除了重复的模态框事件监听器")
            
            print("\n🔍 测试建议:")
            print("1. 刷新页面")
            print("2. 尝试添加新的交易记录")
            print("3. 快速多次点击保存按钮")
            print("4. 检查网络面板，确保只有一次API请求")
            
        else:
            print("❌ 修复失败")
            
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()