#!/usr/bin/env python3
"""
修复卖出比例字段映射问题
"""

import os
import sys

def fix_profit_targets_field_mapping():
    """修复分批止盈字段映射问题"""
    
    print("🔧 修复分批止盈字段映射问题...")
    
    # 1. 修复后端验证逻辑，支持多种字段名
    service_path = "services/profit_taking_service.py"
    
    if not os.path.exists(service_path):
        print(f"❌ 文件不存在: {service_path}")
        return False
    
    try:
        with open(service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复validate_targets_total_ratio方法中的字段获取逻辑
        old_sell_ratio_check = """            # 验证必需字段
            if 'sell_ratio' not in target or target['sell_ratio'] is None:
                target_errors['sell_ratio'] = "卖出比例不能为空"
            else:
                try:
                    sell_ratio = Decimal(str(target['sell_ratio']))"""
        
        new_sell_ratio_check = """            # 验证必需字段 - 支持多种字段名
            sell_ratio_value = target.get('sell_ratio') or target.get('sellRatio')
            if sell_ratio_value is None or sell_ratio_value == '':
                target_errors['sell_ratio'] = "卖出比例不能为空"
            else:
                try:
                    sell_ratio = Decimal(str(sell_ratio_value))"""
        
        if old_sell_ratio_check in content:
            content = content.replace(old_sell_ratio_check, new_sell_ratio_check)
            print("✅ 修复了sell_ratio字段获取逻辑")
        
        # 修复其他字段的获取逻辑
        old_target_price_check = """            # 验证止盈价格（如果提供）
            if 'target_price' in target and target['target_price'] is not None:
                try:
                    target_price = Decimal(str(target['target_price']))"""
        
        new_target_price_check = """            # 验证止盈价格（如果提供）
            target_price_value = target.get('target_price') or target.get('targetPrice')
            if target_price_value is not None and target_price_value != '':
                try:
                    target_price = Decimal(str(target_price_value))"""
        
        if old_target_price_check in content:
            content = content.replace(old_target_price_check, new_target_price_check)
            print("✅ 修复了target_price字段获取逻辑")
        
        # 修复profit_ratio字段获取逻辑
        old_profit_ratio_check = """            # 验证止盈比例（如果提供）
            if 'profit_ratio' in target and target['profit_ratio'] is not None:
                try:
                    profit_ratio = Decimal(str(target['profit_ratio']))"""
        
        new_profit_ratio_check = """            # 验证止盈比例（如果提供）
            profit_ratio_value = target.get('profit_ratio') or target.get('profitRatio')
            if profit_ratio_value is not None and profit_ratio_value != '':
                try:
                    profit_ratio = Decimal(str(profit_ratio_value))"""
        
        if old_profit_ratio_check in content:
            content = content.replace(old_profit_ratio_check, new_profit_ratio_check)
            print("✅ 修复了profit_ratio字段获取逻辑")
        
        # 修复sequence_order字段获取逻辑
        old_sequence_check = """            # 验证序列顺序（如果提供）
            if 'sequence_order' in target and target['sequence_order'] is not None:
                try:
                    sequence_order = int(target['sequence_order'])"""
        
        new_sequence_check = """            # 验证序列顺序（如果提供）
            sequence_order_value = target.get('sequence_order') or target.get('sequenceOrder')
            if sequence_order_value is not None and sequence_order_value != '':
                try:
                    sequence_order = int(sequence_order_value)"""
        
        if old_sequence_check in content:
            content = content.replace(old_sequence_check, new_sequence_check)
            print("✅ 修复了sequence_order字段获取逻辑")
        
        # 修复validate_targets_against_buy_price方法中的字段获取
        old_buy_price_validation = """            # 验证止盈价格必须大于买入价格
            if 'target_price' in target and target['target_price'] is not None:
                try:
                    target_price = Decimal(str(target['target_price']))"""
        
        new_buy_price_validation = """            # 验证止盈价格必须大于买入价格
            target_price_value = target.get('target_price') or target.get('targetPrice')
            if target_price_value is not None and target_price_value != '':
                try:
                    target_price = Decimal(str(target_price_value))"""
        
        if old_buy_price_validation in content:
            content = content.replace(old_buy_price_validation, new_buy_price_validation)
            print("✅ 修复了买入价格验证中的字段获取逻辑")
        
        # 修复calculate_targets_expected_profit方法中的字段获取
        old_calc_logic = """        for i, target in enumerate(targets):
            try:
                sell_ratio = Decimal(str(target.get('sell_ratio', 0)))
                
                # 计算止盈比例
                profit_ratio = Decimal('0')
                if 'target_price' in target and target['target_price']:
                    try:
                        target_price = Decimal(str(target['target_price']))"""
        
        new_calc_logic = """        for i, target in enumerate(targets):
            try:
                # 支持多种字段名
                sell_ratio_value = target.get('sell_ratio') or target.get('sellRatio', 0)
                sell_ratio = Decimal(str(sell_ratio_value))
                
                # 计算止盈比例
                profit_ratio = Decimal('0')
                target_price_value = target.get('target_price') or target.get('targetPrice')
                if target_price_value:
                    try:
                        target_price = Decimal(str(target_price_value))"""
        
        if old_calc_logic in content:
            content = content.replace(old_calc_logic, new_calc_logic)
            print("✅ 修复了计算方法中的字段获取逻辑")
        
        # 写入修复后的文件
        with open(service_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 后端字段映射修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复后端字段映射失败: {str(e)}")
        return False

def fix_frontend_data_conversion():
    """修复前端数据转换逻辑"""
    
    print("🔧 修复前端数据转换逻辑...")
    
    template_path = "templates/trading_records.html"
    
    if not os.path.exists(template_path):
        print(f"❌ 文件不存在: {template_path}")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并修复分批止盈数据处理逻辑
        old_profit_targets_logic = """                    // 获取分批止盈目标数据
                    const profitTargets = this.profitTargetsManager.getTargets();
                    
                    // 验证止盈目标数据完整性
                    if (!this.validateProfitTargetsData(profitTargets)) {
                        UXUtils.showError('分批止盈数据不完整，请检查所有必填字段');
                        return;
                    }

                    formData.profit_targets = profitTargets;"""
        
        new_profit_targets_logic = """                    // 获取分批止盈目标数据
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

                    formData.profit_targets = convertedTargets;"""
        
        if old_profit_targets_logic in content:
            content = content.replace(old_profit_targets_logic, new_profit_targets_logic)
            print("✅ 修复了前端分批止盈数据转换逻辑")
        
        # 修复validateProfitTargetsData方法
        old_validation_method = """        validateProfitTargetsData(profitTargets) {
            if (!profitTargets || profitTargets.length === 0) {
                return false;
            }

            return profitTargets.every(target => {
                return target.targetPrice > 0 && 
                       target.sellRatio > 0 && 
                       target.sellRatio <= 100;
            });
        }"""
        
        new_validation_method = """        validateProfitTargetsData(profitTargets) {
            if (!profitTargets || profitTargets.length === 0) {
                return false;
            }

            return profitTargets.every(target => {
                // 支持两种字段名格式
                const targetPrice = target.target_price || target.targetPrice;
                const sellRatio = target.sell_ratio || target.sellRatio;
                
                return targetPrice > 0 && 
                       sellRatio > 0 && 
                       sellRatio <= (target.sell_ratio ? 1 : 100); // 小数格式为1，百分比格式为100
            });
        }"""
        
        if old_validation_method in content:
            content = content.replace(old_validation_method, new_validation_method)
            print("✅ 修复了前端数据验证方法")
        
        # 写入修复后的文件
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 前端数据转换修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复前端数据转换失败: {str(e)}")
        return False

def create_field_mapping_test():
    """创建字段映射测试页面"""
    
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>字段映射测试</title>
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
        <h1>🔧 字段映射测试</h1>
        <p class="text-muted">测试分批止盈字段映射是否正确</p>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5>测试数据</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">买入价格</label>
                            <input type="number" class="form-control" id="buy-price" value="10.00" step="0.01">
                        </div>
                        
                        <h6>分批止盈目标</h6>
                        <div class="row">
                            <div class="col-md-4">
                                <label class="form-label">目标价格1</label>
                                <input type="number" class="form-control" id="target-price-1" value="12.00" step="0.01">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">止盈比例1 (%)</label>
                                <input type="number" class="form-control" id="profit-ratio-1" value="20" step="0.01">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">卖出比例1 (%)</label>
                                <input type="number" class="form-control" id="sell-ratio-1" value="50" step="0.01">
                            </div>
                        </div>
                        
                        <div class="row mt-2">
                            <div class="col-md-4">
                                <label class="form-label">目标价格2</label>
                                <input type="number" class="form-control" id="target-price-2" value="15.00" step="0.01">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">止盈比例2 (%)</label>
                                <input type="number" class="form-control" id="profit-ratio-2" value="50" step="0.01">
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">卖出比例2 (%)</label>
                                <input type="number" class="form-control" id="sell-ratio-2" value="50" step="0.01">
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <button type="button" class="btn btn-primary" onclick="testFrontendFormat()">
                                测试前端格式
                            </button>
                            <button type="button" class="btn btn-success" onclick="testBackendFormat()">
                                测试后端格式
                            </button>
                            <button type="button" class="btn btn-warning" onclick="testApiCall()">
                                测试API调用
                            </button>
                            <button type="button" class="btn btn-info" onclick="clearResults()">
                                清空结果
                            </button>
                        </div>
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

    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
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
        
        function getTestData() {
            return {
                buyPrice: parseFloat(document.getElementById('buy-price').value),
                targets: [
                    {
                        targetPrice: parseFloat(document.getElementById('target-price-1').value),
                        profitRatio: parseFloat(document.getElementById('profit-ratio-1').value),
                        sellRatio: parseFloat(document.getElementById('sell-ratio-1').value),
                        sequenceOrder: 1
                    },
                    {
                        targetPrice: parseFloat(document.getElementById('target-price-2').value),
                        profitRatio: parseFloat(document.getElementById('profit-ratio-2').value),
                        sellRatio: parseFloat(document.getElementById('sell-ratio-2').value),
                        sequenceOrder: 2
                    }
                ]
            };
        }
        
        function testFrontendFormat() {
            clearResults();
            log('=== 测试前端格式 ===');
            
            const data = getTestData();
            log('前端格式数据:');
            log(JSON.stringify(data, null, 2));
            
            // 验证数据完整性
            log('\\n数据验证:');
            data.targets.forEach((target, index) => {
                log(`目标${index + 1}:`);
                log(`  targetPrice: ${target.targetPrice} (${typeof target.targetPrice})`);
                log(`  profitRatio: ${target.profitRatio}% (${typeof target.profitRatio})`);
                log(`  sellRatio: ${target.sellRatio}% (${typeof target.sellRatio})`);
                
                const isValid = target.targetPrice > 0 && target.sellRatio > 0 && target.sellRatio <= 100;
                log(`  有效性: ${isValid ? '✅ 有效' : '❌ 无效'}`);
            });
        }
        
        function testBackendFormat() {
            clearResults();
            log('=== 测试后端格式 ===');
            
            const data = getTestData();
            
            // 转换为后端格式
            const backendData = {
                buy_price: data.buyPrice,
                profit_targets: data.targets.map(target => ({
                    target_price: target.targetPrice,
                    profit_ratio: target.profitRatio / 100, // 转换为小数
                    sell_ratio: target.sellRatio / 100, // 转换为小数
                    sequence_order: target.sequenceOrder
                }))
            };
            
            log('后端格式数据:');
            log(JSON.stringify(backendData, null, 2));
            
            // 验证转换结果
            log('\\n转换验证:');
            backendData.profit_targets.forEach((target, index) => {
                log(`目标${index + 1}:`);
                log(`  target_price: ${target.target_price} (${typeof target.target_price})`);
                log(`  profit_ratio: ${target.profit_ratio} (${typeof target.profit_ratio})`);
                log(`  sell_ratio: ${target.sell_ratio} (${typeof target.sell_ratio})`);
                
                const isValid = target.target_price > 0 && target.sell_ratio > 0 && target.sell_ratio <= 1;
                log(`  有效性: ${isValid ? '✅ 有效' : '❌ 无效'}`);
            });
        }
        
        async function testApiCall() {
            clearResults();
            log('=== 测试API调用 ===');
            
            const data = getTestData();
            
            // 转换为后端格式
            const apiData = {
                buy_price: data.buyPrice,
                profit_targets: data.targets.map(target => ({
                    target_price: target.targetPrice,
                    profit_ratio: target.profitRatio / 100,
                    sell_ratio: target.sellRatio / 100,
                    sequence_order: target.sequenceOrder
                }))
            };
            
            log('发送API数据:');
            log(JSON.stringify(apiData, null, 2));
            
            try {
                const response = await axios.post('/api/trades/validate-profit-targets', apiData, {
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 10000
                });
                
                log('\\n✅ API调用成功!');
                log(`状态码: ${response.status}`);
                log('响应数据:');
                log(JSON.stringify(response.data, null, 2));
                
            } catch (error) {
                log('\\n❌ API调用失败!');
                
                if (error.response) {
                    log(`HTTP错误: ${error.response.status}`);
                    try {
                        const errorData = error.response.data;
                        log('错误详情:');
                        log(JSON.stringify(errorData, null, 2));
                    } catch (e) {
                        log('无法解析错误响应');
                    }
                } else if (error.request) {
                    log('网络错误: 无法连接到服务器');
                } else {
                    log(`请求错误: ${error.message}`);
                }
            }
        }
    </script>
</body>
</html>'''
    
    try:
        with open('field_mapping_test.html', 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ 创建了字段映射测试页面: field_mapping_test.html")
        return True
    except Exception as e:
        print(f"❌ 创建测试页面失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始修复字段映射问题...")
    
    success = True
    
    # 1. 修复后端字段映射
    if not fix_profit_targets_field_mapping():
        success = False
    
    # 2. 修复前端数据转换
    if not fix_frontend_data_conversion():
        success = False
    
    # 3. 创建测试页面
    if not create_field_mapping_test():
        success = False
    
    if success:
        print("\n🎉 字段映射修复完成！")
        print("\n📋 修复内容:")
        print("  ✅ 后端支持多种字段名格式 (sellRatio/sell_ratio)")
        print("  ✅ 前端数据转换为后端期望格式")
        print("  ✅ 修复了数据验证逻辑")
        print("  ✅ 创建了字段映射测试页面")
        print("\n🔧 测试方法:")
        print("  1. 访问 field_mapping_test.html 进行测试")
        print("  2. 刷新交易记录页面重试")
        print("  3. 检查分批止盈功能是否正常")
        print("\n💡 现在应该能正常保存分批止盈的交易记录了！")
    else:
        print("\n❌ 字段映射修复失败，请检查错误信息")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())