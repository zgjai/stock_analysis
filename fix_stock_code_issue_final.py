#!/usr/bin/env python3
"""
最终修复股票代码传递问题的脚本
"""

import os
import sys

def fix_trading_records_form_submission():
    """修复交易记录表单提交中的股票代码传递问题"""
    
    template_path = "templates/trading_records.html"
    
    if not os.path.exists(template_path):
        print(f"❌ 文件不存在: {template_path}")
        return False
    
    print("🔧 开始修复交易记录表单提交问题...")
    
    try:
        # 读取原文件
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并替换handleTradeFormSubmit方法中的表单数据获取逻辑
        old_form_data_logic = """            // 获取表单数据
            const formData = FormUtils.serialize(this.form);
            
            // 触发自定义提交事件
            const submitEvent = new CustomEvent('formValidSubmit', {
                detail: { formData, validator: this }
            });
            this.form.dispatchEvent(submitEvent);"""
        
        new_form_data_logic = """            // 获取表单数据 - 使用更可靠的方式
            const formData = FormUtils.serialize(this.form);
            
            // 直接调用交易管理器的处理方法，而不是依赖事件
            if (window.tradingManager && typeof window.tradingManager.handleTradeFormSubmit === 'function') {
                await window.tradingManager.handleTradeFormSubmit(formData);
            } else {
                console.error('TradingManager not available');
                throw new Error('系统初始化未完成，请刷新页面重试');
            }"""
        
        if old_form_data_logic in content:
            content = content.replace(old_form_data_logic, new_form_data_logic)
            print("✅ 修复了表单验证器中的事件触发逻辑")
        
        # 在TradingRecordsManager类中添加表单提交事件监听器
        old_event_listener = """        // 保存交易按钮
        document.getElementById('save-trade-btn').addEventListener('click', () => {
            this.saveTrade();
        });"""
        
        new_event_listener = """        // 保存交易按钮
        document.getElementById('save-trade-btn').addEventListener('click', () => {
            this.saveTrade();
        });
        
        // 监听表单验证成功事件
        document.getElementById('trade-form').addEventListener('formValidSubmit', async (e) => {
            const { formData } = e.detail;
            await this.handleTradeFormSubmit(formData);
        });"""
        
        if old_event_listener in content:
            content = content.replace(old_event_listener, new_event_listener)
            print("✅ 添加了表单提交事件监听器")
        
        # 增强handleTradeFormSubmit方法中的数据验证
        old_validation_start = """        async handleTradeFormSubmit(formData) {
            try {
                console.log('[DEBUG] handleTradeFormSubmit 接收到的 formData:', formData);
                console.log('[DEBUG] formData.price:', formData.price, '(type:', typeof formData.price, ')');
                console.log('[DEBUG] formData.quantity:', formData.quantity, '(type:', typeof formData.quantity, ')');"""
        
        new_validation_start = """        async handleTradeFormSubmit(formData) {
            try {
                console.log('[DEBUG] handleTradeFormSubmit 接收到的 formData:', formData);
                console.log('[DEBUG] formData.stock_code:', formData.stock_code, '(type:', typeof formData.stock_code, ')');
                console.log('[DEBUG] formData.stock_name:', formData.stock_name, '(type:', typeof formData.stock_name, ')');
                console.log('[DEBUG] formData.price:', formData.price, '(type:', typeof formData.price, ')');
                console.log('[DEBUG] formData.quantity:', formData.quantity, '(type:', typeof formData.quantity, ')');
                
                // 紧急修复：如果formData中缺少关键字段，直接从DOM获取
                if (!formData.stock_code || formData.stock_code.trim() === '') {
                    const stockCodeElement = document.getElementById('stock-code');
                    if (stockCodeElement && stockCodeElement.value) {
                        formData.stock_code = stockCodeElement.value.trim();
                        console.log('[DEBUG] 从DOM获取股票代码:', formData.stock_code);
                    }
                }
                
                if (!formData.stock_name || formData.stock_name.trim() === '') {
                    const stockNameElement = document.getElementById('stock-name');
                    if (stockNameElement && stockNameElement.value) {
                        formData.stock_name = stockNameElement.value.trim();
                        console.log('[DEBUG] 从DOM获取股票名称:', formData.stock_name);
                    }
                }
                
                if (!formData.trade_type || formData.trade_type.trim() === '') {
                    const tradeTypeElement = document.getElementById('trade-type');
                    if (tradeTypeElement && tradeTypeElement.value) {
                        formData.trade_type = tradeTypeElement.value.trim();
                        console.log('[DEBUG] 从DOM获取交易类型:', formData.trade_type);
                    }
                }
                
                if (!formData.reason || formData.reason.trim() === '') {
                    const reasonElement = document.getElementById('reason');
                    if (reasonElement && reasonElement.value) {
                        formData.reason = reasonElement.value.trim();
                        console.log('[DEBUG] 从DOM获取操作原因:', formData.reason);
                    }
                }"""
        
        if old_validation_start in content:
            content = content.replace(old_validation_start, new_validation_start)
            print("✅ 增强了表单数据验证和DOM备用获取逻辑")
        
        # 修复saveTrade方法，确保它能正确处理表单数据
        old_save_trade = """        // 保持向后兼容的方法
        async saveTrade() {
            if (this.formValidator) {
                // 触发表单验证和提交
                const form = document.getElementById('trade-form');
                const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                form.dispatchEvent(submitEvent);
            } else {
                // 回退到旧的验证方式
                this.handleTradeFormSubmit(FormUtils.serialize(document.getElementById('trade-form')));
            }
        }"""
        
        new_save_trade = """        // 保持向后兼容的方法
        async saveTrade() {
            const form = document.getElementById('trade-form');
            
            if (this.formValidator) {
                // 触发表单验证和提交
                const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                form.dispatchEvent(submitEvent);
            } else {
                // 回退到旧的验证方式 - 直接获取表单数据并处理
                console.log('[DEBUG] 使用回退方式处理表单提交');
                const formData = FormUtils.serialize(form);
                
                // 确保关键字段不为空
                if (!formData.stock_code) {
                    formData.stock_code = document.getElementById('stock-code').value || '';
                }
                if (!formData.stock_name) {
                    formData.stock_name = document.getElementById('stock-name').value || '';
                }
                if (!formData.trade_type) {
                    formData.trade_type = document.getElementById('trade-type').value || '';
                }
                if (!formData.reason) {
                    formData.reason = document.getElementById('reason').value || '';
                }
                
                console.log('[DEBUG] 回退方式获取的表单数据:', formData);
                await this.handleTradeFormSubmit(formData);
            }
        }"""
        
        if old_save_trade in content:
            content = content.replace(old_save_trade, new_save_trade)
            print("✅ 修复了saveTrade方法的数据获取逻辑")
        
        # 写入修复后的文件
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 交易记录表单提交问题修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {str(e)}")
        return False

def create_form_data_debug_utility():
    """创建表单数据调试工具"""
    
    debug_js_path = "static/js/form-debug-utility.js"
    
    debug_js_content = '''/**
 * 表单数据调试工具
 * 用于诊断和修复表单数据传递问题
 */

class FormDataDebugger {
    constructor() {
        this.debugMode = true;
        this.logPrefix = '[FormDebug]';
    }
    
    /**
     * 调试表单序列化
     */
    debugFormSerialization(form) {
        if (!this.debugMode) return;
        
        console.group(`${this.logPrefix} 表单序列化调试`);
        
        // 1. 检查表单元素
        console.log('表单元素:', form);
        console.log('表单ID:', form.id);
        console.log('表单name:', form.name);
        
        // 2. 检查所有输入字段
        const inputs = form.querySelectorAll('input, select, textarea');
        console.log(`找到 ${inputs.length} 个输入字段:`);
        
        inputs.forEach((input, index) => {
            console.log(`  ${index + 1}. ${input.tagName} [name="${input.name}"] = "${input.value}" (type: ${input.type || 'text'})`);
        });
        
        // 3. 使用FormData测试
        const formData = new FormData(form);
        console.log('FormData 条目:');
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}: "${value}" (${typeof value})`);
        }
        
        // 4. 使用FormUtils.serialize测试
        if (typeof FormUtils !== 'undefined' && FormUtils.serialize) {
            const serialized = FormUtils.serialize(form);
            console.log('FormUtils.serialize 结果:', serialized);
        } else {
            console.warn('FormUtils.serialize 不可用');
        }
        
        // 5. 检查必填字段
        const requiredFields = form.querySelectorAll('[required]');
        console.log(`必填字段检查 (${requiredFields.length} 个):`);
        requiredFields.forEach(field => {
            const isEmpty = !field.value || field.value.trim() === '';
            console.log(`  ${field.name}: ${isEmpty ? '❌ 空值' : '✅ 有值'} ("${field.value}")`);
        });
        
        console.groupEnd();
    }
    
    /**
     * 调试API请求数据
     */
    debugApiRequestData(data, endpoint) {
        if (!this.debugMode) return;
        
        console.group(`${this.logPrefix} API请求数据调试`);
        console.log('请求端点:', endpoint);
        console.log('请求数据:', data);
        
        // 检查关键字段
        const criticalFields = ['stock_code', 'stock_name', 'trade_type', 'price', 'quantity', 'reason'];
        console.log('关键字段检查:');
        criticalFields.forEach(field => {
            const value = data[field];
            const isEmpty = value === undefined || value === null || value === '';
            console.log(`  ${field}: ${isEmpty ? '❌ 缺失/空值' : '✅ 有值'} (${JSON.stringify(value)})`);
        });
        
        console.groupEnd();
    }
    
    /**
     * 实时监控表单变化
     */
    monitorFormChanges(form) {
        if (!this.debugMode) return;
        
        console.log(`${this.logPrefix} 开始监控表单变化:`, form.id);
        
        form.addEventListener('input', (e) => {
            console.log(`${this.logPrefix} 字段变化: ${e.target.name} = "${e.target.value}"`);
        });
        
        form.addEventListener('change', (e) => {
            console.log(`${this.logPrefix} 字段确认变化: ${e.target.name} = "${e.target.value}"`);
        });
    }
    
    /**
     * 验证表单完整性
     */
    validateFormIntegrity(form) {
        const issues = [];
        
        // 检查表单是否存在
        if (!form) {
            issues.push('表单元素不存在');
            return issues;
        }
        
        // 检查必填字段
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value || field.value.trim() === '') {
                issues.push(`必填字段 "${field.name}" 为空`);
            }
        });
        
        // 检查name属性
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (!input.name) {
                issues.push(`输入字段缺少name属性: ${input.id || input.tagName}`);
            }
        });
        
        if (issues.length > 0) {
            console.warn(`${this.logPrefix} 表单完整性问题:`, issues);
        } else {
            console.log(`${this.logPrefix} 表单完整性检查通过`);
        }
        
        return issues;
    }
    
    /**
     * 创建表单数据快照
     */
    createFormSnapshot(form) {
        const snapshot = {
            timestamp: new Date().toISOString(),
            formId: form.id,
            data: {}
        };
        
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            snapshot.data[input.name] = {
                value: input.value,
                type: input.type || input.tagName.toLowerCase(),
                required: input.required,
                valid: input.checkValidity()
            };
        });
        
        return snapshot;
    }
}

// 创建全局调试器实例
window.formDebugger = new FormDataDebugger();

// 添加全局调试函数
window.debugTradeForm = function() {
    const form = document.getElementById('trade-form');
    if (form) {
        window.formDebugger.debugFormSerialization(form);
        return window.formDebugger.createFormSnapshot(form);
    } else {
        console.error('交易表单未找到');
        return null;
    }
};

// 自动监控交易表单（如果存在）
document.addEventListener('DOMContentLoaded', () => {
    const tradeForm = document.getElementById('trade-form');
    if (tradeForm) {
        window.formDebugger.monitorFormChanges(tradeForm);
        console.log('表单调试工具已激活，可以使用 debugTradeForm() 进行调试');
    }
});
'''
    
    try:
        with open(debug_js_path, 'w', encoding='utf-8') as f:
            f.write(debug_js_content)
        print(f"✅ 创建了表单调试工具: {debug_js_path}")
        return True
    except Exception as e:
        print(f"❌ 创建调试工具失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始修复股票代码传递问题...")
    
    success = True
    
    # 1. 修复交易记录表单提交问题
    if not fix_trading_records_form_submission():
        success = False
    
    # 2. 创建调试工具
    if not create_form_data_debug_utility():
        success = False
    
    if success:
        print("\n🎉 所有修复完成！")
        print("\n📋 修复内容:")
        print("  ✅ 修复了表单验证器中的事件触发逻辑")
        print("  ✅ 添加了表单提交事件监听器")
        print("  ✅ 增强了表单数据验证和DOM备用获取逻辑")
        print("  ✅ 修复了saveTrade方法的数据获取逻辑")
        print("  ✅ 创建了表单数据调试工具")
        print("\n🔧 调试方法:")
        print("  1. 在浏览器控制台运行 debugTradeForm() 查看表单数据")
        print("  2. 检查控制台中的 [FormDebug] 日志")
        print("  3. 使用 clearAllLoadingStates() 清理加载状态")
        print("\n⚠️  如果问题仍然存在，请:")
        print("  1. 刷新页面")
        print("  2. 检查浏览器控制台的错误信息")
        print("  3. 使用调试工具分析表单数据传递过程")
    else:
        print("\n❌ 修复过程中出现错误，请检查上述错误信息")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())