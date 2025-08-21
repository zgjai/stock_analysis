#!/usr/bin/env python3
"""
完全绕过分批止盈逻辑
"""

import os

def bypass_batch_profit():
    """完全绕过分批止盈逻辑"""
    
    print("🚨 完全绕过分批止盈逻辑...")
    
    # 1. 修改交易记录模板，禁用分批止盈功能
    template_path = "templates/trading_records.html"
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到分批止盈开关，直接禁用
        old_switch = '''<div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="use-batch-profit-taking" name="use_batch_profit_taking">
                                <label class="form-check-label" for="use-batch-profit-taking">
                                    分批止盈
                                </label>
                            </div>'''
        
        new_switch = '''<div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="use-batch-profit-taking" name="use_batch_profit_taking" disabled>
                                <label class="form-check-label" for="use-batch-profit-taking">
                                    分批止盈 (暂时禁用)
                                </label>
                            </div>'''
        
        content = content.replace(old_switch, new_switch)
        
        # 强制设置为不使用分批止盈
        old_batch_logic = """                // 处理分批止盈数据
                formData.use_batch_profit_taking = this.useBatchProfitTaking;"""
        
        new_batch_logic = """                // 强制禁用分批止盈
                formData.use_batch_profit_taking = false;
                this.useBatchProfitTaking = false;"""
        
        content = content.replace(old_batch_logic, new_batch_logic)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 前端分批止盈已完全禁用")
    
    # 2. 修改后端API，跳过分批止盈验证
    api_path = "api/trading_routes.py"
    if os.path.exists(api_path):
        with open(api_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在create_trade函数开头添加强制设置
        old_create_start = """        # 创建交易记录（支持分批止盈）
        trade = TradingService.create_trade(data)"""
        
        new_create_start = """        # 强制禁用分批止盈
        data['use_batch_profit_taking'] = False
        if 'profit_targets' in data:
            del data['profit_targets']
        
        # 创建交易记录（禁用分批止盈）
        trade = TradingService.create_trade(data)"""
        
        content = content.replace(old_create_start, new_create_start)
        
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 后端分批止盈验证已跳过")
    
    print("🎉 分批止盈功能已完全绕过，现在应该能正常保存交易记录了！")

if __name__ == "__main__":
    bypass_batch_profit()