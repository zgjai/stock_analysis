#!/usr/bin/env python3
"""
修复编辑交易记录时"价格不能为空"的问题

问题分析：
1. 前端可能发送空字符串或None值
2. 后端验证逻辑过于严格
3. 数据类型转换问题

解决方案：
1. 改进后端验证逻辑
2. 增强前端数据处理
3. 添加调试日志
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from extensions import db
from models.trade_record import TradeRecord

def analyze_existing_trades():
    """分析现有交易记录的价格字段"""
    print("=== 分析现有交易记录 ===")
    
    trades = TradeRecord.query.all()
    print(f"总交易记录数: {len(trades)}")
    
    price_issues = []
    for trade in trades:
        if trade.price is None:
            price_issues.append(f"ID {trade.id}: 价格为None")
        elif trade.price == 0:
            price_issues.append(f"ID {trade.id}: 价格为0")
        elif trade.price < 0:
            price_issues.append(f"ID {trade.id}: 价格为负数 ({trade.price})")
    
    if price_issues:
        print("发现价格问题:")
        for issue in price_issues:
            print(f"  - {issue}")
    else:
        print("✅ 所有交易记录的价格字段都正常")
    
    return price_issues

def create_improved_validation():
    """创建改进的验证逻辑"""
    
    validation_code = '''
# 改进的价格验证逻辑
def validate_price_field(data, field_name='price'):
    """
    改进的价格字段验证
    
    Args:
        data: 请求数据字典
        field_name: 字段名称
    
    Returns:
        float: 验证后的价格值
    
    Raises:
        ValidationError: 验证失败时抛出
    """
    if field_name not in data:
        return None  # 字段不存在，允许（更新时可能不传某些字段）
    
    value = data[field_name]
    
    # 处理None值
    if value is None:
        raise ValidationError(f"{field_name}不能为空")
    
    # 处理空字符串
    if isinstance(value, str):
        value = value.strip()
        if value == '':
            raise ValidationError(f"{field_name}不能为空")
        
        # 尝试转换为数字
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}格式无效，必须是数字")
    
    # 处理数字类型
    if isinstance(value, (int, float)):
        if value <= 0:
            raise ValidationError(f"{field_name}必须大于0")
        return float(value)
    
    # 其他类型
    raise ValidationError(f"{field_name}类型无效")

def validate_quantity_field(data, field_name='quantity'):
    """
    改进的数量字段验证
    """
    if field_name not in data:
        return None
    
    value = data[field_name]
    
    if value is None:
        raise ValidationError(f"{field_name}不能为空")
    
    if isinstance(value, str):
        value = value.strip()
        if value == '':
            raise ValidationError(f"{field_name}不能为空")
        
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}格式无效，必须是整数")
    
    if isinstance(value, (int, float)):
        value = int(value)
        if value <= 0:
            raise ValidationError(f"{field_name}必须大于0")
        if value % 100 != 0:
            raise ValidationError(f"{field_name}必须是100的倍数")
        return value
    
    raise ValidationError(f"{field_name}类型无效")
'''
    
    return validation_code

def create_improved_api_route():
    """创建改进的API路由代码"""
    
    route_code = '''
@api_bp.route('/trades/<int:trade_id>', methods=['PUT'])
def update_trade(trade_id):
    """更新交易记录 - 改进版本"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("请求数据不能为空")
        
        # 记录原始数据用于调试
        app.logger.info(f"更新交易记录 {trade_id}，原始数据: {data}")
        
        # 改进的字段验证
        validated_data = {}
        
        # 验证价格字段（如果提供）
        if 'price' in data:
            try:
                validated_price = validate_price_field(data, 'price')
                if validated_price is not None:
                    validated_data['price'] = validated_price
                    app.logger.info(f"价格验证通过: {validated_price}")
            except ValidationError as e:
                app.logger.error(f"价格验证失败: {e.message}")
                raise e
        
        # 验证数量字段（如果提供）
        if 'quantity' in data:
            try:
                validated_quantity = validate_quantity_field(data, 'quantity')
                if validated_quantity is not None:
                    validated_data['quantity'] = validated_quantity
                    app.logger.info(f"数量验证通过: {validated_quantity}")
            except ValidationError as e:
                app.logger.error(f"数量验证失败: {e.message}")
                raise e
        
        # 复制其他字段
        for key, value in data.items():
            if key not in ['price', 'quantity'] and value is not None:
                validated_data[key] = value
        
        # 处理交易日期
        if 'trade_date' in validated_data and isinstance(validated_data['trade_date'], str):
            try:
                validated_data['trade_date'] = datetime.fromisoformat(
                    validated_data['trade_date'].replace('Z', '+00:00')
                )
            except ValueError:
                raise ValidationError("交易日期格式不正确")
        
        app.logger.info(f"验证后的数据: {validated_data}")
        
        # 更新交易记录
        trade = TradingService.update_trade(trade_id, validated_data)
        
        # 如果使用分批止盈，返回包含止盈目标的详细信息
        if trade.use_batch_profit_taking:
            trade_data = TradingService.get_trade_with_profit_targets(trade.id)
        else:
            trade_data = trade.to_dict()
        
        return create_success_response(
            data=trade_data,
            message='交易记录更新成功'
        )
    
    except Exception as e:
        app.logger.error(f"更新交易记录失败: {str(e)}")
        raise e
'''
    
    return route_code

def create_frontend_fix():
    """创建前端修复代码"""
    
    frontend_code = '''
// 改进的表单数据处理函数
function processTradeFormData(formData) {
    const processedData = {};
    
    // 处理所有字段
    for (const [key, value] of Object.entries(formData)) {
        // 跳过空值
        if (value === null || value === undefined) {
            continue;
        }
        
        // 处理字符串值
        if (typeof value === 'string') {
            const trimmedValue = value.trim();
            if (trimmedValue === '') {
                continue; // 跳过空字符串
            }
            processedData[key] = trimmedValue;
        } else {
            processedData[key] = value;
        }
    }
    
    // 特殊处理数值字段
    if ('price' in processedData) {
        const price = parseFloat(processedData.price);
        if (isNaN(price) || price <= 0) {
            throw new Error('价格必须是大于0的数字');
        }
        processedData.price = price;
    }
    
    if ('quantity' in processedData) {
        const quantity = parseInt(processedData.quantity);
        if (isNaN(quantity) || quantity <= 0) {
            throw new Error('数量必须是大于0的整数');
        }
        if (quantity % 100 !== 0) {
            throw new Error('数量必须是100的倍数');
        }
        processedData.quantity = quantity;
    }
    
    return processedData;
}

// 改进的表单提交处理
async function handleTradeFormSubmit(formData) {
    try {
        console.log('原始表单数据:', formData);
        
        // 处理表单数据
        const processedData = processTradeFormData(formData);
        console.log('处理后的数据:', processedData);
        
        // 验证必填字段（仅在创建时）
        if (!this.editingTradeId) {
            const requiredFields = ['stock_code', 'stock_name', 'trade_type', 'price', 'quantity', 'reason'];
            for (const field of requiredFields) {
                if (!(field in processedData)) {
                    throw new Error(`${field}不能为空`);
                }
            }
        }
        
        let response;
        if (this.editingTradeId) {
            // 更新交易记录
            console.log(`更新交易记录 ${this.editingTradeId}:`, processedData);
            response = await apiClient.updateTrade(this.editingTradeId, processedData);
        } else {
            // 创建新交易记录
            console.log('创建新交易记录:', processedData);
            response = await apiClient.createTrade(processedData);
        }
        
        if (response.success) {
            UXUtils.showSuccess(this.editingTradeId ? '交易记录更新成功' : '交易记录创建成功');
            
            // 关闭模态框并刷新列表
            const modal = bootstrap.Modal.getInstance(document.getElementById('addTradeModal'));
            modal.hide();
            await this.loadTrades();
        } else {
            throw new Error(response.message || '保存失败');
        }
        
    } catch (error) {
        console.error('表单提交错误:', error);
        UXUtils.showError(error.message || '保存失败，请重试');
    }
}
'''
    
    return frontend_code

def main():
    """主函数"""
    print("=== 修复编辑交易记录价格验证问题 ===")
    
    # 创建Flask应用上下文
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading_records.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # 分析现有数据
        price_issues = analyze_existing_trades()
        
        # 生成修复代码
        print("\n=== 生成修复代码 ===")
        
        validation_code = create_improved_validation()
        route_code = create_improved_api_route()
        frontend_code = create_frontend_fix()
        
        # 保存修复代码到文件
        with open('improved_validation.py', 'w', encoding='utf-8') as f:
            f.write(validation_code)
        print("✅ 已生成改进的验证逻辑: improved_validation.py")
        
        with open('improved_api_route.py', 'w', encoding='utf-8') as f:
            f.write(route_code)
        print("✅ 已生成改进的API路由: improved_api_route.py")
        
        with open('improved_frontend.js', 'w', encoding='utf-8') as f:
            f.write(frontend_code)
        print("✅ 已生成改进的前端代码: improved_frontend.js")
        
        print("\n=== 修复建议 ===")
        print("1. 在 api/trading_routes.py 中应用改进的验证逻辑")
        print("2. 在前端表单处理中应用改进的数据处理")
        print("3. 添加更详细的日志记录用于调试")
        print("4. 测试各种边界情况")
        
        if price_issues:
            print(f"\n⚠️  发现 {len(price_issues)} 个价格数据问题，建议先修复这些数据")

if __name__ == '__main__':
    main()