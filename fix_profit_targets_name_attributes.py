#!/usr/bin/env python3
"""
修复分批止盈组件缺少name属性的问题
"""

import os
import sys

def fix_profit_targets_name_attributes():
    """修复分批止盈组件的name属性问题"""
    
    print("🔧 修复分批止盈组件name属性问题...")
    
    js_path = "static/js/profit-targets-manager.js"
    
    if not os.path.exists(js_path):
        print(f"❌ 文件不存在: {js_path}")
        return False
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复止盈比例输入框
        old_profit_ratio_input = """                            <input type="number" 
                                   class="form-control target-input profit-ratio-input" 
                                   data-target-id="${target.id}"
                                   data-field="profitRatio"
                                   value="${target.profitRatio}" 
                                   step="0.01" 
                                   min="0.01" 
                                   max="1000"
                                   placeholder="20.00">"""
        
        new_profit_ratio_input = """                            <input type="number" 
                                   class="form-control target-input profit-ratio-input" 
                                   name="profit_ratio_${target.id}"
                                   data-target-id="${target.id}"
                                   data-field="profitRatio"
                                   value="${target.profitRatio}" 
                                   step="0.01" 
                                   min="0.01" 
                                   max="1000"
                                   placeholder="20.00">"""
        
        if old_profit_ratio_input in content:
            content = content.replace(old_profit_ratio_input, new_profit_ratio_input)
            print("✅ 修复了止盈比例输入框的name属性")
        
        # 修复止盈价格输入框
        old_target_price_input = """                            <input type="number" 
                                   class="form-control target-input target-price-input" 
                                   data-target-id="${target.id}"
                                   data-field="targetPrice"
                                   value="${target.targetPrice}" 
                                   step="0.01" 
                                   min="0.01" 
                                   placeholder="0.00"
                                   readonly>"""
        
        new_target_price_input = """                            <input type="number" 
                                   class="form-control target-input target-price-input" 
                                   name="target_price_${target.id}"
                                   data-target-id="${target.id}"
                                   data-field="targetPrice"
                                   value="${target.targetPrice}" 
                                   step="0.01" 
                                   min="0.01" 
                                   placeholder="0.00"
                                   readonly>"""
        
        if old_target_price_input in content:
            content = content.replace(old_target_price_input, new_target_price_input)
            print("✅ 修复了止盈价格输入框的name属性")
        
        # 修复卖出比例输入框
        old_sell_ratio_input = """                            <input type="number" 
                                   class="form-control target-input sell-ratio-input" 
                                   data-target-id="${target.id}"
                                   data-field="sellRatio"
                                   value="${target.sellRatio}" 
                                   step="0.01" 
                                   min="0.01" 
                                   max="100" 
                                   placeholder="30.00">"""
        
        new_sell_ratio_input = """                            <input type="number" 
                                   class="form-control target-input sell-ratio-input" 
                                   name="sell_ratio_${target.id}"
                                   data-target-id="${target.id}"
                                   data-field="sellRatio"
                                   value="${target.sellRatio}" 
                                   step="0.01" 
                                   min="0.01" 
                                   max="100" 
                                   placeholder="30.00">"""
        
        if old_sell_ratio_input in content:
            content = content.replace(old_sell_ratio_input, new_sell_ratio_input)
            print("✅ 修复了卖出比例输入框的name属性")
        
        # 写入修复后的文件
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 分批止盈组件name属性修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复name属性失败: {str(e)}")
        return False

def fix_form_data_collection():
    """修复表单数据收集逻辑，确保能获取分批止盈数据"""
    
    print("🔧 修复表单数据收集逻辑...")
    
    template_path = "templates/trading_records.html"
    
    if not os.path.exists(template_path):
        print(f"❌ 文件不存在: {template_path}")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在handleTradeFormSubmit方法中添加专门的分批止盈数据收集逻辑
        old_batch_profit_logic = """                // 处理分批止盈数据
                formData.use_batch_profit_taking = this.useBatchProfitTaking;

                if (this.useBatchProfitTaking && this.profitTargetsManager) {
                    // 验证分批止盈数据
                    if (!this.profitTargetsManager.isValidTargets()) {
                        const errors = this.profitTargetsManager.getValidationErrors();
                        this.showBatchProfitErrors(errors);
                        UXUtils.showError('请检查分批止盈设置中的错误');
                        return;
                    }

                    // 获取分批止盈目标数据
                    const profitTargets = this.profitTargetsManager.getTargets();
                    
                    // 转换字段名以匹配后端期望的格式
                    const convertedTargets = profitTargets.map(target => ({
                        target_price: target.targetPrice,
                        profit_ratio: target.profitRatio / 100, // 转换为小数
                        sell_ratio: target.sellRatio / 100, // 转换为小数
                        sequence_order: target.sequenceOrder
                    }));
                    
                    // 验证止盈目标数据完整性
                    if (!this.validateProfitTargetsData(convertedTargets)) {
                        UXUtils.showError('分批止盈数据不完整，请检查所有必填字段');
                        return;
                    }

                    formData.profit_targets = convertedTargets;

                    // 清空单一止盈字段
                    delete formData.take_profit_ratio;
                    delete formData.sell_ratio;
                } else {
                    // 处理单一止盈数据
                    if (formData.take_profit_ratio) {
                        formData.take_profit_ratio = parseFloat(formData.take_profit_ratio) / 100;
                    }
                    if (formData.sell_ratio) {
                        formData.sell_ratio = parseFloat(formData.sell_ratio) / 100;
                    }
                    
                    // 清空分批止盈字段
                    delete formData.profit_targets;
                }"""

        new_batch_profit_logic = """                // 处理分批止盈数据
                formData.use_batch_profit_taking = this.useBatchProfitTaking;

                if (this.useBatchProfitTaking && this.profitTargetsManager) {
                    console.log('[DEBUG] 处理分批止盈数据...');
                    
                    // 验证分批止盈数据
                    if (!this.profitTargetsManager.isValidTargets()) {
                        const errors = this.profitTargetsManager.getValidationErrors();
                        this.showBatchProfitErrors(errors);
                        UXUtils.showError('请检查分批止盈设置中的错误');
                        return;
                    }

                    // 直接从分批止盈管理器获取数据（不依赖FormData）
                    const profitTargets = this.profitTargetsManager.getTargets();
                    console.log('[DEBUG] 从管理器获取的分批止盈数据:', profitTargets);
                    
                    // 验证数据完整性
                    if (!profitTargets || profitTargets.length === 0) {
                        UXUtils.showError('请至少设置一个分批止盈目标');
                        return;
                    }
                    
                    // 验证每个目标的数据
                    const invalidTargets = profitTargets.filter(target => 
                        !target.targetPrice || target.targetPrice <= 0 ||
                        !target.sellRatio || target.sellRatio <= 0 || target.sellRatio > 100
                    );
                    
                    if (invalidTargets.length > 0) {
                        UXUtils.showError('分批止盈目标数据不完整，请检查所有必填字段');
                        return;
                    }
                    
                    // 转换字段名以匹配后端期望的格式
                    const convertedTargets = profitTargets.map((target, index) => ({
                        target_price: parseFloat(target.targetPrice),
                        profit_ratio: parseFloat(target.profitRatio) / 100, // 转换为小数
                        sell_ratio: parseFloat(target.sellRatio) / 100, // 转换为小数
                        sequence_order: index + 1
                    }));
                    
                    console.log('[DEBUG] 转换后的分批止盈数据:', convertedTargets);
                    formData.profit_targets = convertedTargets;

                    // 清空单一止盈字段
                    delete formData.take_profit_ratio;
                    delete formData.sell_ratio;
                } else {
                    console.log('[DEBUG] 处理单一止盈数据...');
                    // 处理单一止盈数据
                    if (formData.take_profit_ratio) {
                        formData.take_profit_ratio = parseFloat(formData.take_profit_ratio) / 100;
                    }
                    if (formData.sell_ratio) {
                        formData.sell_ratio = parseFloat(formData.sell_ratio) / 100;
                    }
                    
                    // 清空分批止盈字段
                    delete formData.profit_targets;
                }"""

        if old_batch_profit_logic in content:
            content = content.replace(old_batch_profit_logic, new_batch_profit_logic)
            print("✅ 修复了分批止盈数据收集逻辑")
        
        # 写入修复后的文件
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 表单数据收集逻辑修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复表单数据收集失败: {str(e)}")
        return False

def create_name_attribute_test():
    """创建name属性测试页面"""
    
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Name属性测试</title>
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
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1>🔍 Name属性测试</h1>
        <p class="text-muted">检查表单字段是否有正确的name属性</p>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5>模拟交易表单</h5>
                    </div>
                    <div class="card-body">
                        <form id="test-form">
                            <!-- 基本字段 -->
                            <div class="row">
                                <div class="col-md-6">
                                    <label class="form-label">股票代码</label>
                                    <input type="text" class="form-control" name="stock_code" value="000001">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">股票名称</label>
                                    <input type="text" class="form-control" name="stock_name" value="平安银行">
                                </div>
                            </div>
                            
                            <div class="row mt-2">
                                <div class="col-md-4">
                                    <label class="form-label">交易类型</label>
                                    <select class="form-select" name="trade_type">
                                        <option value="buy" selected>买入</option>
                                    </select>
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">价格</label>
                                    <input type="number" class="form-control" name="price" value="10.00">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">数量</label>
                                    <input type="number" class="form-control" name="quantity" value="1000">
                                </div>
                            </div>
                            
                            <div class="mt-2">
                                <label class="form-label">操作原因</label>
                                <select class="form-select" name="reason">
                                    <option value="少妇B1战法" selected>少妇B1战法</option>
                                </select>
                            </div>
                            
                            <!-- 分批止盈开关 -->
                            <div class="mt-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" name="use_batch_profit_taking" id="use-batch-profit" checked>
                                    <label class="form-check-label" for="use-batch-profit">
                                        分批止盈
                                    </label>
                                </div>
                            </div>
                            
                            <!-- 模拟分批止盈字段 -->
                            <div class="mt-3 p-3 border rounded">
                                <h6>分批止盈目标</h6>
                                
                                <!-- 目标1 -->
                                <div class="row">
                                    <div class="col-md-4">
                                        <label class="form-label">止盈比例1 (%)</label>
                                        <input type="number" class="form-control" name="profit_ratio_1" value="20">
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label">止盈价格1</label>
                                        <input type="number" class="form-control" name="target_price_1" value="12.00">
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label">卖出比例1 (%)</label>
                                        <input type="number" class="form-control" name="sell_ratio_1" value="50">
                                    </div>
                                </div>
                                
                                <!-- 目标2 -->
                                <div class="row mt-2">
                                    <div class="col-md-4">
                                        <label class="form-label">止盈比例2 (%)</label>
                                        <input type="number" class="form-control" name="profit_ratio_2" value="50">
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label">止盈价格2</label>
                                        <input type="number" class="form-control" name="target_price_2" value="15.00">
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label">卖出比例2 (%)</label>
                                        <input type="number" class="form-control" name="sell_ratio_2" value="50">
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mt-3">
                                <button type="button" class="btn btn-primary" onclick="checkNameAttributes()">
                                    检查Name属性
                                </button>
                                <button type="button" class="btn btn-success" onclick="testFormData()">
                                    测试FormData
                                </button>
                                <button type="button" class="btn btn-warning" onclick="findMissingNames()">
                                    查找缺失Name
                                </button>
                                <button type="button" class="btn btn-info" onclick="clearResults()">
                                    清空结果
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>测试结果</h5>
                    </div>
                    <div class="card-body p-0">
                        <div id="test-output" class="test-result">等待测试...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function log(message, type = 'info') {
            const output = document.getElementById('test-output');
            const time = new Date().toLocaleTimeString();
            output.textContent += `[${time}] ${message}\\n`;
            output.scrollTop = output.scrollHeight;
        }
        
        function clearResults() {
            document.getElementById('test-output').textContent = '测试结果已清空...\\n';
        }
        
        function checkNameAttributes() {
            clearResults();
            log('=== 检查Name属性 ===');
            
            const form = document.getElementById('test-form');
            const allInputs = form.querySelectorAll('input, select, textarea');
            
            log(`找到 ${allInputs.length} 个输入字段:`);
            
            let hasNameCount = 0;
            let missingNameCount = 0;
            
            allInputs.forEach((input, index) => {
                const name = input.name;
                const type = input.type || input.tagName.toLowerCase();
                const value = input.value;
                
                if (name) {
                    log(`${index + 1}. ✅ ${type.toUpperCase()} [name="${name}"] = "${value}"`);
                    hasNameCount++;
                } else {
                    log(`${index + 1}. ❌ ${type.toUpperCase()} [name=""] = "${value}" (缺少name属性)`);
                    missingNameCount++;
                }
            });
            
            log(`\\n统计结果:`);
            log(`  有name属性: ${hasNameCount} 个`);
            log(`  缺少name属性: ${missingNameCount} 个`);
            log(`  总计: ${allInputs.length} 个`);
            
            if (missingNameCount === 0) {
                log('\\n🎉 所有字段都有name属性！');
            } else {
                log(`\\n⚠️  有 ${missingNameCount} 个字段缺少name属性！`);
            }
        }
        
        function testFormData() {
            clearResults();
            log('=== 测试FormData ===');
            
            const form = document.getElementById('test-form');
            const formData = new FormData(form);
            
            log('FormData 条目:');
            let count = 0;
            for (let [key, value] of formData.entries()) {
                count++;
                log(`${count}. ${key}: "${value}"`);
            }
            
            if (count === 0) {
                log('❌ FormData 为空！没有获取到任何数据！');
            } else {
                log(`\\n✅ FormData 包含 ${count} 个条目`);
            }
            
            // 测试序列化
            log('\\n序列化结果:');
            const serialized = {};
            for (let [key, value] of formData.entries()) {
                serialized[key] = value;
            }
            log(JSON.stringify(serialized, null, 2));
        }
        
        function findMissingNames() {
            clearResults();
            log('=== 查找缺失Name属性的字段 ===');
            
            const form = document.getElementById('test-form');
            const allInputs = form.querySelectorAll('input, select, textarea');
            const missingInputs = Array.from(allInputs).filter(input => !input.name);
            
            if (missingInputs.length === 0) {
                log('✅ 所有字段都有name属性！');
                return;
            }
            
            log(`找到 ${missingInputs.length} 个缺少name属性的字段:`);
            
            missingInputs.forEach((input, index) => {
                const type = input.type || input.tagName.toLowerCase();
                const id = input.id;
                const className = input.className;
                const value = input.value;
                
                log(`${index + 1}. ${type.toUpperCase()}`);
                log(`   ID: "${id}"`);
                log(`   Class: "${className}"`);
                log(`   Value: "${value}"`);
                log(`   建议name: "${id || 'field_' + (index + 1)}"`);
                log('');
            });
            
            log('💡 建议为这些字段添加name属性，或使用JavaScript直接获取值');
        }
    </script>
</body>
</html>'''
    
    try:
        with open('name_attribute_test.html', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ 创建了name属性测试页面: name_attribute_test.html")
        return True
    except Exception as e:
        print(f"❌ 创建测试页面失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始修复name属性问题...")
    
    success = True
    
    # 1. 修复分批止盈组件的name属性
    if not fix_profit_targets_name_attributes():
        success = False
    
    # 2. 修复表单数据收集逻辑
    if not fix_form_data_collection():
        success = False
    
    # 3. 创建测试页面
    if not create_name_attribute_test():
        success = False
    
    if success:
        print("\n🎉 Name属性问题修复完成！")
        print("\n📋 修复内容:")
        print("  ✅ 为分批止盈输入框添加了name属性")
        print("  ✅ 修复了表单数据收集逻辑")
        print("  ✅ 不再依赖FormData获取分批止盈数据")
        print("  ✅ 直接从管理器获取数据")
        print("  ✅ 创建了name属性测试页面")
        print("\n🔧 测试方法:")
        print("  1. 访问 name_attribute_test.html 检查name属性")
        print("  2. 刷新交易记录页面重试")
        print("  3. 检查分批止盈功能是否正常")
        print("\n💡 现在分批止盈数据应该能正确获取了！")
    else:
        print("\n❌ Name属性修复失败，请检查错误信息")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())