#!/usr/bin/env python3
"""
调试前端API调用问题
"""

import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/api/reviews', methods=['POST'])
def debug_reviews():
    """调试复盘API请求"""
    logger.info("收到POST请求到 /api/reviews")
    
    # 记录请求头
    logger.info("请求头:")
    for header, value in request.headers:
        logger.info(f"  {header}: {value}")
    
    # 记录原始数据
    raw_data = request.get_data()
    logger.info(f"原始数据长度: {len(raw_data)}")
    logger.info(f"原始数据: {raw_data}")
    
    # 尝试解析JSON
    try:
        json_data = request.get_json()
        logger.info("解析的JSON数据:")
        logger.info(json.dumps(json_data, indent=2, ensure_ascii=False))
        
        # 检查必填字段
        required_fields = ['stock_code', 'review_date']
        missing_fields = []
        for field in required_fields:
            if field not in json_data or json_data[field] is None or json_data[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"缺少必填字段: {missing_fields}")
            return jsonify({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"缺少必填字段: {', '.join(missing_fields)}"
                }
            }), 400
        
        # 检查数据类型
        type_errors = []
        
        if 'holding_days' in json_data:
            try:
                holding_days = int(json_data['holding_days'])
                if holding_days < 1:
                    type_errors.append("持仓天数必须大于0")
            except (ValueError, TypeError):
                type_errors.append("持仓天数必须是整数")
        
        if 'current_price' in json_data and json_data['current_price'] is not None:
            try:
                current_price = float(json_data['current_price'])
                if current_price <= 0:
                    type_errors.append("当前价格必须大于0")
            except (ValueError, TypeError):
                type_errors.append("当前价格必须是数字")
        
        if type_errors:
            logger.error(f"数据类型错误: {type_errors}")
            return jsonify({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"数据验证失败: {'; '.join(type_errors)}"
                }
            }), 400
        
        # 模拟成功响应
        logger.info("数据验证通过，返回成功响应")
        return jsonify({
            "success": True,
            "data": {
                "id": 999,
                "message": "调试模式 - 数据验证通过"
            },
            "message": "复盘记录创建成功"
        }), 201
        
    except Exception as e:
        logger.error(f"JSON解析失败: {e}")
        return jsonify({
            "success": False,
            "error": {
                "code": "PARSE_ERROR",
                "message": f"请求数据格式错误: {str(e)}"
            }
        }), 400

if __name__ == '__main__':
    print("启动调试服务器...")
    print("访问地址: http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True)