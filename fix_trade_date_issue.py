#!/usr/bin/env python3
"""
修复交易日期编辑后保存不生效的问题

问题分析：
1. 前端表单序列化可能没有正确处理datetime-local字段
2. 日期格式转换和时区处理可能有问题
3. 后端更新逻辑可能过滤掉了交易日期字段

修复方案：
1. 改进前端的表单数据收集，确保交易日期被正确包含
2. 修复后端的日期处理逻辑
3. 添加调试日志来跟踪问题
"""

import os
import sys

def fix_frontend_form_serialization():
    """修复前端表单序列化问题"""
    
    # 读取trading_records.html文件
    template_path = 'templates/trading_records.html'
    
    if not os.path.exists(template_path):
        print(f"❌ 文件不存在: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找saveTrade函数中的表单数据收集部分
    # 在handleTradeFormSubmit函数中添加交易日期的特殊处理
    
    old_code = '''                if (!formData.reason || formData.reason.trim() === '') {
                    const reasonElement = document.getElementById('reason');
                    if (reasonElement && reasonElement.value) {
                        formData.reason = reasonElement.value.trim();
                        console.log('[DEBUG] 从DOM获取操作原因:', formData.reason);
                    }
                }'''
    
    new_code = '''                if (!formData.reason || formData.reason.trim() === '') {
                    const reasonElement = document.getElementById('reason');
                    if (reasonElement && reasonElement.value) {
                        formData.reason = reasonElement.value.trim();
                        console.log('[DEBUG] 从DOM获取操作原因:', formData.reason);
                    }
                }

                // 特殊处理交易日期 - 确保交易日期被正确收集
                if (!formData.trade_date || formData.trade_date.trim() === '') {
                    const tradeDateElement = document.getElementById('trade-date');
                    if (tradeDateElement && tradeDateElement.value) {
                        formData.trade_date = tradeDateElement.value.trim();
                        console.log('[DEBUG] 从DOM获取交易日期:', formData.trade_date);
                    }
                } else {
                    console.log('[DEBUG] 表单中已有交易日期:', formData.trade_date);
                }'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✅ 已添加交易日期的特殊处理逻辑")
    else:
        print("⚠️ 未找到预期的代码位置，尝试其他方式...")
        
        # 尝试在handleTradeFormSubmit函数的开始部分添加日期处理
        search_pattern = '''console.log('[DEBUG] handleTradeFormSubmit 接收到的 formData:', formData);'''
        
        if search_pattern in content:
            insert_code = '''
                // 确保交易日期被正确收集
                const tradeDateElement = document.getElementById('trade-date');
                if (tradeDateElement && tradeDateElement.value) {
                    formData.trade_date = tradeDateElement.value.trim();
                    console.log('[DEBUG] 强制从DOM获取交易日期:', formData.trade_date);
                }
                
                console.log('[DEBUG] handleTradeFormSubmit 接收到的 formData:', formData);'''
            
            content = content.replace(search_pattern, insert_code)
            print("✅ 已在函数开始处添加交易日期处理")
        else:
            print("❌ 无法找到合适的插入位置")
            return False
    
    # 保存修改后的文件
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_backend_date_handling():
    """修复后端日期处理问题"""
    
    # 修复trading_routes.py中的日期处理
    routes_path = 'api/trading_routes.py'
    
    if not os.path.exists(routes_path):
        print(f"❌ 文件不存在: {routes_path}")
        return False
    
    with open(routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并修复日期处理逻辑
    old_date_handling = '''        # 处理交易日期
        if 'trade_date' in data and isinstance(data['trade_date'], str):
            try:
                data['trade_date'] = datetime.fromisoformat(data['trade_date'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("交易日期格式不正确")'''
    
    new_date_handling = '''        # 处理交易日期
        if 'trade_date' in data and data['trade_date'] is not None:
            if isinstance(data['trade_date'], str):
                try:
                    # 处理多种日期格式
                    trade_date_str = data['trade_date'].strip()
                    if trade_date_str:
                        # 处理datetime-local格式 (YYYY-MM-DDTHH:MM)
                        if 'T' in trade_date_str and len(trade_date_str) == 16:
                            data['trade_date'] = datetime.fromisoformat(trade_date_str)
                        # 处理ISO格式
                        elif 'T' in trade_date_str:
                            data['trade_date'] = datetime.fromisoformat(trade_date_str.replace('Z', '+00:00'))
                        else:
                            # 尝试其他格式
                            data['trade_date'] = datetime.fromisoformat(trade_date_str)
                        
                        app.logger.info(f"交易日期处理成功: {trade_date_str} -> {data['trade_date']}")
                    else:
                        raise ValidationError("交易日期不能为空")
                except ValueError as e:
                    app.logger.error(f"交易日期格式错误: {data['trade_date']}, 错误: {str(e)}")
                    raise ValidationError(f"交易日期格式不正确: {data['trade_date']}")
            else:
                app.logger.info(f"交易日期已是datetime对象: {data['trade_date']}")'''
    
    if old_date_handling in content:
        content = content.replace(old_date_handling, new_date_handling)
        print("✅ 已修复后端日期处理逻辑")
    else:
        print("⚠️ 未找到预期的日期处理代码")
        return False
    
    # 保存修改后的文件
    with open(routes_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def fix_trading_service_update():
    """修复TradingService的更新逻辑"""
    
    service_path = 'services/trading_service.py'
    
    if not os.path.exists(service_path):
        print(f"❌ 文件不存在: {service_path}")
        return False
    
    with open(service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并修复过滤逻辑，确保交易日期不被过滤掉
    old_filter_logic = '''            # 过滤掉None值和空字符串，避免覆盖必填字段
            filtered_data = {}
            for key, value in data.items():
                if value is not None and value != '':
                    filtered_data[key] = value'''
    
    new_filter_logic = '''            # 过滤掉None值和空字符串，避免覆盖必填字段
            # 但保留交易日期字段，即使它可能是空字符串
            filtered_data = {}
            for key, value in data.items():
                if key == 'trade_date':
                    # 交易日期字段特殊处理，允许更新
                    if value is not None:
                        filtered_data[key] = value
                elif value is not None and value != '':
                    filtered_data[key] = value'''
    
    if old_filter_logic in content:
        content = content.replace(old_filter_logic, new_filter_logic)
        print("✅ 已修复TradingService的过滤逻辑")
    else:
        print("⚠️ 未找到预期的过滤逻辑代码")
        return False
    
    # 保存修改后的文件
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def create_debug_test_file():
    """创建调试测试文件"""
    
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交易日期编辑测试</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h2>交易日期编辑测试</h2>
        
        <div class="card">
            <div class="card-body">
                <h5>测试步骤</h5>
                <ol>
                    <li>打开交易记录页面</li>
                    <li>点击编辑某条交易记录</li>
                    <li>修改交易日期</li>
                    <li>保存记录</li>
                    <li>重新打开该记录，检查日期是否已更新</li>
                </ol>
                
                <h5 class="mt-4">调试信息</h5>
                <div id="debug-info" class="border p-3 bg-light">
                    <p>请打开浏览器开发者工具的控制台，查看以下调试信息：</p>
                    <ul>
                        <li><code>[DEBUG] 从DOM获取交易日期: ...</code></li>
                        <li><code>[DEBUG] 表单中已有交易日期: ...</code></li>
                        <li><code>[DEBUG] handleTradeFormSubmit 接收到的 formData: ...</code></li>
                    </ul>
                </div>
                
                <h5 class="mt-4">常见问题</h5>
                <div class="alert alert-info">
                    <h6>如果交易日期仍然不能保存，请检查：</h6>
                    <ul class="mb-0">
                        <li>浏览器控制台是否有JavaScript错误</li>
                        <li>网络请求是否成功发送</li>
                        <li>服务器日志中是否有错误信息</li>
                        <li>数据库中的记录是否实际更新</li>
                    </ul>
                </div>
                
                <button class="btn btn-primary" onclick="testFormSerialization()">测试表单序列化</button>
                <button class="btn btn-secondary" onclick="testDateHandling()">测试日期处理</button>
            </div>
        </div>
    </div>

    <script>
        function testFormSerialization() {
            console.log('=== 测试表单序列化 ===');
            
            // 创建测试表单
            const form = document.createElement('form');
            form.innerHTML = `
                <input name="stock_code" value="000001">
                <input name="stock_name" value="平安银行">
                <input name="trade_type" value="buy">
                <input name="trade_date" type="datetime-local" value="2025-01-20T14:30">
                <input name="price" value="12.50">
                <input name="quantity" value="1000">
                <input name="reason" value="测试原因">
            `;
            
            // 测试FormData
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            console.log('FormData结果:', data);
            console.log('交易日期值:', data.trade_date);
            console.log('交易日期类型:', typeof data.trade_date);
        }
        
        function testDateHandling() {
            console.log('=== 测试日期处理 ===');
            
            const testDates = [
                '2025-01-20T14:30',
                '2025-01-20T14:30:00',
                '2025-01-20T14:30:00.000Z',
                '2025-01-20 14:30:00'
            ];
            
            testDates.forEach(dateStr => {
                try {
                    const date = new Date(dateStr);
                    console.log(`${dateStr} -> ${date.toISOString()}`);
                } catch (e) {
                    console.error(`${dateStr} -> 解析失败:`, e.message);
                }
            });
        }
    </script>
</body>
</html>'''
    
    with open('test_trade_date_fix.html', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ 已创建调试测试文件: test_trade_date_fix.html")

def main():
    """主函数"""
    print("🔧 开始修复交易日期编辑问题...")
    
    success_count = 0
    total_fixes = 3
    
    # 1. 修复前端表单序列化
    print("\n1. 修复前端表单序列化...")
    if fix_frontend_form_serialization():
        success_count += 1
    
    # 2. 修复后端日期处理
    print("\n2. 修复后端日期处理...")
    if fix_backend_date_handling():
        success_count += 1
    
    # 3. 修复TradingService更新逻辑
    print("\n3. 修复TradingService更新逻辑...")
    if fix_trading_service_update():
        success_count += 1
    
    # 4. 创建调试测试文件
    print("\n4. 创建调试测试文件...")
    create_debug_test_file()
    
    print(f"\n🎯 修复完成！成功修复 {success_count}/{total_fixes} 个问题")
    
    if success_count == total_fixes:
        print("\n✅ 所有修复都已完成，请重启服务器并测试交易日期编辑功能")
        print("\n📋 测试步骤：")
        print("1. 重启Flask服务器")
        print("2. 打开交易记录页面")
        print("3. 编辑一条交易记录的日期")
        print("4. 保存并重新打开，检查日期是否已更新")
        print("5. 查看浏览器控制台的调试信息")
    else:
        print("\n⚠️ 部分修复失败，请手动检查相关文件")
    
    print("\n🔍 如果问题仍然存在，请：")
    print("1. 检查浏览器控制台的错误信息")
    print("2. 查看服务器日志")
    print("3. 使用test_trade_date_fix.html进行调试")

if __name__ == "__main__":
    main()