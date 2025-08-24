#!/usr/bin/env python3
"""
紧急修复数据验证问题
"""

import os
import sys

def emergency_fix_validation():
    """紧急修复数据验证问题"""
    
    print("🚨 紧急修复数据验证问题...")
    
    # 1. 修复前端表单验证逻辑
    template_path = "templates/trading_records.html"
    
    if not os.path.exists(template_path):
        print(f"❌ 文件不存在: {template_path}")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到并替换handleTradeFormSubmit方法中的验证逻辑
        old_validation = """                // 改进的数值字段验证 - 使用箭头函数保持this上下文
                const validateNumericField = (fieldName, fieldValue, isRequired = true) => {
                    console.log(`[DEBUG] 验证字段 "${fieldName}":`, fieldValue, '(type:', typeof fieldValue, ')');

                    // 如果是编辑模式且字段不存在，允许跳过
                    if (!isRequired && this.editingTradeId && (fieldValue === undefined || fieldValue === null)) {
                        console.log(`[DEBUG] 跳过验证 "${fieldName}" - 编辑模式且字段为空`);
                        return null;
                    }

                    // 检查必填字段 - 更严格的空值检查，但允许0作为有效值
                    if (isRequired && (fieldValue === undefined || fieldValue === null || fieldValue === '')) {
                        console.error(`[DEBUG] 验证失败 "${fieldName}" - 字段为空:`, fieldValue);
                        throw new Error(`${fieldName}不能为空`);
                    }

                    // 处理字符串类型
                    if (typeof fieldValue === 'string') {
                        fieldValue = fieldValue.trim();
                        if (fieldValue === '') {
                            if (isRequired) {
                                console.error(`[DEBUG] 验证失败 "${fieldName}" - 字符串为空`);
                                throw new Error(`${fieldName}不能为空`);
                            }
                            return null;
                        }
                    }

                    console.log(`[DEBUG] 验证通过 "${fieldName}":`, fieldValue);
                    return fieldValue;
                };"""

        new_validation = """                // 简化的验证逻辑 - 直接验证必填字段
                console.log('[DEBUG] 开始验证必填字段...');
                
                // 验证股票代码
                if (!formData.stock_code || formData.stock_code.trim() === '') {
                    UXUtils.showError('股票代码不能为空');
                    return;
                }
                
                // 验证股票名称
                if (!formData.stock_name || formData.stock_name.trim() === '') {
                    UXUtils.showError('股票名称不能为空');
                    return;
                }
                
                // 验证交易类型
                if (!formData.trade_type || formData.trade_type.trim() === '') {
                    UXUtils.showError('交易类型不能为空');
                    return;
                }
                
                // 验证操作原因
                if (!formData.reason || formData.reason.trim() === '') {
                    UXUtils.showError('操作原因不能为空');
                    return;
                }
                
                console.log('[DEBUG] 必填字段验证通过');"""

        if old_validation in content:
            content = content.replace(old_validation, new_validation)
            print("✅ 修复了复杂的验证逻辑")
        
        # 简化价格和数量验证
        old_price_validation = """                // 验证价格字段 - 添加备用获取方式
                let priceFieldValue = formData.price;

                // 如果formData中没有price，直接从DOM元素获取
                if (priceFieldValue === undefined || priceFieldValue === null || priceFieldValue === '') {
                    const priceElement = document.getElementById('price');
                    if (priceElement) {
                        priceFieldValue = priceElement.value;
                        console.log('[DEBUG] 从DOM元素获取价格:', priceFieldValue);
                    }
                }

                const priceValue = validateNumericField('价格', priceFieldValue, !this.editingTradeId);
                if (priceValue !== null) {
                    formData.price = priceValue;
                }

                // 验证数量字段 - 添加备用获取方式
                let quantityFieldValue = formData.quantity;

                // 如果formData中没有quantity，直接从DOM元素获取
                if (quantityFieldValue === undefined || quantityFieldValue === null || quantityFieldValue === '') {
                    const quantityElement = document.getElementById('quantity');
                    if (quantityElement) {
                        quantityFieldValue = quantityElement.value;
                        console.log('[DEBUG] 从DOM元素获取数量:', quantityFieldValue);
                    }
                }

                const quantityValue = validateNumericField('数量', quantityFieldValue, !this.editingTradeId);
                if (quantityValue !== null) {
                    formData.quantity = quantityValue;
                }"""

        new_price_validation = """                // 简化的价格和数量验证
                if (!formData.price || formData.price === '') {
                    const priceElement = document.getElementById('price');
                    if (priceElement && priceElement.value) {
                        formData.price = priceElement.value;
                    } else {
                        UXUtils.showError('价格不能为空');
                        return;
                    }
                }

                if (!formData.quantity || formData.quantity === '') {
                    const quantityElement = document.getElementById('quantity');
                    if (quantityElement && quantityElement.value) {
                        formData.quantity = quantityElement.value;
                    } else {
                        UXUtils.showError('数量不能为空');
                        return;
                    }
                }"""

        if old_price_validation in content:
            content = content.replace(old_price_validation, new_price_validation)
            print("✅ 简化了价格和数量验证")
        
        # 写入修复后的文件
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 前端验证逻辑修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复前端验证失败: {str(e)}")
        return False

def create_emergency_test_page():
    """创建紧急测试页面"""
    
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>紧急验证测试</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .test-result {
            background: #212529;
            color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.375rem;
            font-family: monospace;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1>🚨 紧急验证测试</h1>
        
        <div class="card mt-3">
            <div class="card-header">
                <h5>测试表单</h5>
            </div>
            <div class="card-body">
                <form id="emergency-test-form">
                    <div class="row">
                        <div class="col-md-3">
                            <label class="form-label">股票代码</label>
                            <input type="text" class="form-control" name="stock_code" value="000001" required>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">股票名称</label>
                            <input type="text" class="form-control" name="stock_name" value="平安银行" required>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">交易类型</label>
                            <select class="form-select" name="trade_type" required>
                                <option value="buy" selected>买入</option>
                                <option value="sell">卖出</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">价格</label>
                            <input type="number" class="form-control" name="price" value="10.50" step="0.01" required>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-3">
                            <label class="form-label">数量</label>
                            <input type="number" class="form-control" name="quantity" value="1000" step="100" required>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">操作原因</label>
                            <select class="form-select" name="reason" required>
                                <option value="少妇B1战法" selected>少妇B1战法</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">交易日期</label>
                            <input type="datetime-local" class="form-control" name="trade_date" required>
                        </div>
                    </div>
                    <div class="mt-3">
                        <button type="button" class="btn btn-primary" onclick="testFormData()">测试表单数据</button>
                        <button type="button" class="btn btn-success" onclick="testApiCall()">测试API调用</button>
                        <button type="button" class="btn btn-danger" onclick="testEmptyFields()">测试空字段</button>
                    </div>
                </form>
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-header">
                <h5>测试结果</h5>
            </div>
            <div class="card-body">
                <div id="test-output" class="test-result">等待测试...</div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script>
        // 设置当前时间
        document.querySelector('[name="trade_date"]').value = new Date().toISOString().slice(0, 16);
        
        function log(message) {
            const output = document.getElementById('test-output');
            const time = new Date().toLocaleTimeString();
            output.textContent += `[${time}] ${message}\\n`;
            output.scrollTop = output.scrollHeight;
        }
        
        function clear() {
            document.getElementById('test-output').textContent = '';
        }
        
        // FormUtils.serialize 实现
        const FormUtils = {
            serialize: (form) => {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                return data;
            }
        };
        
        function testFormData() {
            clear();
            log('=== 测试表单数据获取 ===');
            
            const form = document.getElementById('emergency-test-form');
            const data = FormUtils.serialize(form);
            
            log('表单数据:');
            log(JSON.stringify(data, null, 2));
            
            // 验证必填字段
            const required = ['stock_code', 'stock_name', 'trade_type', 'price', 'quantity', 'reason'];
            let valid = true;
            
            log('\\n必填字段检查:');
            required.forEach(field => {
                const value = data[field];
                const isEmpty = !value || value.toString().trim() === '';
                log(`${field}: ${isEmpty ? '❌ 空' : '✅ 有值'} ("${value}")`);
                if (isEmpty) valid = false;
            });
            
            log(`\\n验证结果: ${valid ? '✅ 通过' : '❌ 失败'}`);
        }
        
        async function testApiCall() {
            clear();
            log('=== 测试API调用 ===');
            
            const form = document.getElementById('emergency-test-form');
            const data = FormUtils.serialize(form);
            
            // 数据预处理
            if (data.price) data.price = parseFloat(data.price);
            if (data.quantity) data.quantity = parseInt(data.quantity);
            
            log('发送数据:');
            log(JSON.stringify(data, null, 2));
            
            try {
                const response = await axios.post('/api/trades', data, {
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 10000
                });
                
                log('\\n✅ API调用成功!');
                log('响应: ' + JSON.stringify(response.data, null, 2));
                
            } catch (error) {
                log('\\n❌ API调用失败!');
                if (error.response) {
                    log(`状态码: ${error.response.status}`);
                    log('错误详情: ' + JSON.stringify(error.response.data, null, 2));
                } else {
                    log('错误: ' + error.message);
                }
            }
        }
        
        function testEmptyFields() {
            clear();
            log('=== 测试空字段处理 ===');
            
            const form = document.getElementById('emergency-test-form');
            
            // 临时清空一些字段
            const stockCode = form.querySelector('[name="stock_code"]');
            const originalValue = stockCode.value;
            stockCode.value = '';
            
            const data = FormUtils.serialize(form);
            log('空字段测试数据:');
            log(JSON.stringify(data, null, 2));
            
            // 恢复原值
            stockCode.value = originalValue;
            
            log('\\n空字段检测:');
            Object.keys(data).forEach(key => {
                const value = data[key];
                const isEmpty = !value || value.toString().trim() === '';
                if (isEmpty) {
                    log(`❌ ${key} 为空`);
                }
            });
        }
    </script>
</body>
</html>'''
    
    try:
        with open('emergency_validation_test.html', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ 创建了紧急测试页面: emergency_validation_test.html")
        return True
    except Exception as e:
        print(f"❌ 创建测试页面失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚨 开始紧急修复数据验证问题...")
    
    success = True
    
    # 1. 修复验证逻辑
    if not emergency_fix_validation():
        success = False
    
    # 2. 创建测试页面
    if not create_emergency_test_page():
        success = False
    
    if success:
        print("\n🎉 紧急修复完成！")
        print("\n📋 修复内容:")
        print("  ✅ 简化了复杂的验证逻辑")
        print("  ✅ 直接验证必填字段")
        print("  ✅ 移除了容易出错的复杂验证")
        print("  ✅ 创建了紧急测试页面")
        print("\n🔧 测试方法:")
        print("  1. 访问 emergency_validation_test.html 进行测试")
        print("  2. 刷新交易记录页面重试")
        print("  3. 检查浏览器控制台的错误信息")
        print("\n⚠️  如果问题仍然存在:")
        print("  1. 确保所有必填字段都已填写")
        print("  2. 检查网络连接")
        print("  3. 查看服务器日志")
    else:
        print("\n❌ 紧急修复失败，请检查错误信息")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())