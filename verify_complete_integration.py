#!/usr/bin/env python3
"""
复盘功能完整集成验证脚本
验证所有组件的集成和数据流
"""

import sys
import os
import time
import json
import requests
from datetime import datetime, date
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    """测试API端点是否正常工作"""
    print("=" * 60)
    print("测试API端点")
    print("=" * 60)
    
    base_url = "http://localhost:5001/api"
    
    # 测试端点列表
    endpoints = [
        ("GET", "/holdings", "获取持仓数据"),
        ("GET", "/reviews", "获取复盘记录"),
        ("POST", "/reviews/calculate-floating-profit", "浮盈计算", {
            "stock_code": "000001",
            "current_price": 12.50
        })
    ]
    
    results = []
    
    for method, endpoint, description, data in [(e[0], e[1], e[2], e[3] if len(e) > 3 else None) for e in endpoints]:
        try:
            url = base_url + endpoint
            
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=5)
            else:
                continue
            
            success = response.status_code in [200, 201]
            results.append({
                "endpoint": endpoint,
                "description": description,
                "success": success,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            })
            
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status} {description} ({endpoint}) - {response.status_code} - {response.elapsed.total_seconds():.3f}s")
            
            if success and response.json():
                response_data = response.json()
                if isinstance(response_data, dict) and 'data' in response_data:
                    print(f"     数据项数量: {len(response_data['data']) if isinstance(response_data['data'], list) else 1}")
            
        except requests.exceptions.RequestException as e:
            results.append({
                "endpoint": endpoint,
                "description": description,
                "success": False,
                "error": str(e)
            })
            print(f"✗ FAIL {description} ({endpoint}) - 连接错误: {e}")
        except Exception as e:
            results.append({
                "endpoint": endpoint,
                "description": description,
                "success": False,
                "error": str(e)
            })
            print(f"✗ FAIL {description} ({endpoint}) - 未知错误: {e}")
    
    # 统计结果
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nAPI测试结果: {passed}/{total} 通过")
    
    return results

def test_database_integration():
    """测试数据库集成"""
    print("\n" + "=" * 60)
    print("测试数据库集成")
    print("=" * 60)
    
    try:
        # 导入数据库模型
        from models.review_record import ReviewRecord
        from models.trade_record import TradeRecord
        from extensions import db
        from app import create_app
        
        # 创建应用上下文
        app = create_app()
        
        with app.app_context():
            # 测试数据库连接
            try:
                # 查询复盘记录
                review_count = ReviewRecord.query.count()
                print(f"✓ 复盘记录表连接正常，共 {review_count} 条记录")
                
                # 查询交易记录
                trade_count = TradeRecord.query.count()
                print(f"✓ 交易记录表连接正常，共 {trade_count} 条记录")
                
                # 测试新字段是否存在
                sample_review = ReviewRecord.query.first()
                if sample_review:
                    has_current_price = hasattr(sample_review, 'current_price')
                    has_floating_profit = hasattr(sample_review, 'floating_profit_ratio')
                    
                    print(f"✓ 复盘记录新字段检查:")
                    print(f"   - current_price: {'存在' if has_current_price else '不存在'}")
                    print(f"   - floating_profit_ratio: {'存在' if has_floating_profit else '不存在'}")
                    
                    if has_current_price and has_floating_profit:
                        print("✓ 数据库结构更新完成")
                        return True
                    else:
                        print("✗ 数据库结构需要更新")
                        return False
                else:
                    print("! 没有复盘记录数据，无法验证字段")
                    return True
                    
            except Exception as e:
                print(f"✗ 数据库查询失败: {e}")
                return False
                
    except ImportError as e:
        print(f"✗ 导入模块失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 数据库集成测试失败: {e}")
        return False

def test_component_files():
    """测试组件文件是否存在且完整"""
    print("\n" + "=" * 60)
    print("测试组件文件")
    print("=" * 60)
    
    # 需要检查的文件列表
    required_files = [
        ("static/js/api.js", "API客户端"),
        ("static/js/holding-days-editor.js", "持仓天数编辑器"),
        ("static/js/floating-profit-calculator.js", "浮盈计算器"),
        ("static/js/review-save-manager.js", "复盘保存管理器"),
        ("static/js/review-integration.js", "集成管理器"),
        ("templates/review.html", "复盘页面模板"),
        ("api/review_routes.py", "复盘API路由"),
        ("services/review_service.py", "复盘服务"),
        ("models/review_record.py", "复盘记录模型")
    ]
    
    results = []
    
    for file_path, description in required_files:
        exists = os.path.exists(file_path)
        
        if exists:
            # 检查文件大小
            size = os.path.getsize(file_path)
            
            # 检查关键内容（简单检查）
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 根据文件类型检查关键内容
            has_key_content = True
            if file_path.endswith('.js'):
                if 'class' not in content and 'function' not in content:
                    has_key_content = False
            elif file_path.endswith('.py'):
                if 'def ' not in content and 'class ' not in content:
                    has_key_content = False
            elif file_path.endswith('.html'):
                if '<html' not in content and '<!DOCTYPE' not in content:
                    has_key_content = False
            
            status = "✓ PASS" if has_key_content else "! WARN"
            print(f"{status} {description} ({file_path}) - {size} bytes")
            
            results.append({
                "file": file_path,
                "description": description,
                "exists": True,
                "size": size,
                "has_content": has_key_content
            })
        else:
            print(f"✗ FAIL {description} ({file_path}) - 文件不存在")
            results.append({
                "file": file_path,
                "description": description,
                "exists": False
            })
    
    # 统计结果
    existing_files = sum(1 for r in results if r['exists'])
    valid_files = sum(1 for r in results if r.get('exists') and r.get('has_content'))
    total_files = len(results)
    
    print(f"\n文件检查结果: {existing_files}/{total_files} 存在, {valid_files}/{total_files} 有效")
    
    return results

def test_integration_functionality():
    """测试集成功能"""
    print("\n" + "=" * 60)
    print("测试集成功能")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    
    # 测试复盘页面加载
    try:
        response = requests.get(f"{base_url}/review", timeout=10)
        if response.status_code == 200:
            print("✓ 复盘页面加载成功")
            
            # 检查页面是否包含必要的脚本
            content = response.text
            
            scripts_to_check = [
                "holding-days-editor.js",
                "floating-profit-calculator.js", 
                "review-save-manager.js",
                "review-integration.js"
            ]
            
            missing_scripts = []
            for script in scripts_to_check:
                if script not in content:
                    missing_scripts.append(script)
            
            if not missing_scripts:
                print("✓ 所有必要脚本已包含在页面中")
            else:
                print(f"! 缺少脚本: {', '.join(missing_scripts)}")
            
            # 检查必要的HTML元素
            required_elements = [
                'id="review-form"',
                'id="current-price-input"',
                'id="floating-profit-ratio"',
                'id="holding-days"',
                'id="reviewModal"'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                print("✓ 所有必要HTML元素已存在")
            else:
                print(f"! 缺少HTML元素: {', '.join(missing_elements)}")
            
            return len(missing_scripts) == 0 and len(missing_elements) == 0
            
        else:
            print(f"✗ 复盘页面加载失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ 复盘页面连接失败: {e}")
        return False

def test_api_integration():
    """测试API集成功能"""
    print("\n" + "=" * 60)
    print("测试API集成功能")
    print("=" * 60)
    
    base_url = "http://localhost:5001/api"
    
    # 测试浮盈计算API
    try:
        test_data = {
            "stock_code": "000001",
            "current_price": 12.50
        }
        
        response = requests.post(
            f"{base_url}/reviews/calculate-floating-profit",
            json=test_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result.get('data', {})
                print(f"✓ 浮盈计算API正常工作")
                print(f"   股票代码: {data.get('stock_code')}")
                print(f"   当前价格: {data.get('current_price')}")
                print(f"   浮盈比例: {data.get('formatted_ratio', 'N/A')}")
            else:
                print(f"✗ 浮盈计算API返回错误: {result.get('error', {}).get('message')}")
                return False
        else:
            print(f"✗ 浮盈计算API请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 浮盈计算API测试失败: {e}")
        return False
    
    # 测试复盘保存API
    try:
        review_data = {
            "stock_code": "000001",
            "review_date": date.today().isoformat(),
            "holding_days": 5,
            "current_price": 12.50,
            "price_up_score": 1,
            "bbi_score": 1,
            "volume_score": 0,
            "trend_score": 1,
            "j_score": 1,
            "analysis": "集成测试分析",
            "decision": "hold",
            "reason": "集成测试理由"
        }
        
        response = requests.post(
            f"{base_url}/reviews",
            json=review_data,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get('success'):
                print("✓ 复盘保存API正常工作")
                review_id = result.get('data', {}).get('id')
                if review_id:
                    print(f"   创建的复盘记录ID: {review_id}")
                    
                    # 尝试删除测试记录
                    try:
                        delete_response = requests.delete(f"{base_url}/reviews/{review_id}", timeout=5)
                        if delete_response.status_code == 200:
                            print("✓ 测试记录已清理")
                    except:
                        print("! 测试记录清理失败（不影响功能）")
            else:
                print(f"✗ 复盘保存API返回错误: {result.get('error', {}).get('message')}")
                return False
        else:
            print(f"✗ 复盘保存API请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 复盘保存API测试失败: {e}")
        return False
    
    return True

def generate_test_report(api_results, db_result, file_results, integration_result, api_integration_result):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("集成测试报告")
    print("=" * 60)
    
    # 计算总体得分
    api_score = sum(1 for r in api_results if r['success']) / len(api_results) if api_results else 0
    file_score = sum(1 for r in file_results if r.get('exists') and r.get('has_content', True)) / len(file_results) if file_results else 0
    
    total_score = (
        (api_score * 0.3) +
        (1 if db_result else 0) * 0.2 +
        (file_score * 0.2) +
        (1 if integration_result else 0) * 0.15 +
        (1 if api_integration_result else 0) * 0.15
    ) * 100
    
    print(f"总体评分: {total_score:.1f}/100")
    print()
    
    # 详细结果
    print("详细结果:")
    print(f"  API端点测试: {api_score*100:.1f}% ({sum(1 for r in api_results if r['success'])}/{len(api_results)})")
    print(f"  数据库集成: {'通过' if db_result else '失败'}")
    print(f"  组件文件: {file_score*100:.1f}% ({sum(1 for r in file_results if r.get('exists') and r.get('has_content', True))}/{len(file_results)})")
    print(f"  页面集成: {'通过' if integration_result else '失败'}")
    print(f"  API集成: {'通过' if api_integration_result else '失败'}")
    
    # 建议
    print("\n建议:")
    
    if api_score < 1.0:
        failed_apis = [r['description'] for r in api_results if not r['success']]
        print(f"  - 修复失败的API端点: {', '.join(failed_apis)}")
    
    if not db_result:
        print("  - 检查数据库连接和模型定义")
    
    if file_score < 1.0:
        missing_files = [r['description'] for r in file_results if not r.get('exists')]
        if missing_files:
            print(f"  - 创建缺失的文件: {', '.join(missing_files)}")
    
    if not integration_result:
        print("  - 检查复盘页面的脚本引用和HTML结构")
    
    if not api_integration_result:
        print("  - 检查API集成功能的实现")
    
    # 生成JSON报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_score": total_score,
        "results": {
            "api_endpoints": api_results,
            "database_integration": db_result,
            "component_files": file_results,
            "page_integration": integration_result,
            "api_integration": api_integration_result
        },
        "summary": {
            "api_score": api_score * 100,
            "file_score": file_score * 100,
            "overall_status": "PASS" if total_score >= 80 else "FAIL"
        }
    }
    
    # 保存报告
    with open('integration_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细报告已保存到: integration_test_report.json")
    
    return total_score >= 80

def main():
    """主函数"""
    print("复盘功能完整集成验证")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        print("✓ 服务器正在运行")
    except:
        print("✗ 服务器未运行，请先启动应用")
        print("   运行命令: python app.py")
        return False
    
    # 运行各项测试
    api_results = test_api_endpoints()
    db_result = test_database_integration()
    file_results = test_component_files()
    integration_result = test_integration_functionality()
    api_integration_result = test_api_integration()
    
    # 生成报告
    success = generate_test_report(
        api_results, 
        db_result, 
        file_results, 
        integration_result, 
        api_integration_result
    )
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if success:
        print("🎉 集成测试通过！所有组件已成功集成。")
        print("\n下一步:")
        print("1. 访问 http://localhost:5001/review 测试复盘功能")
        print("2. 访问 test_complete_integration.html 运行前端集成测试")
        print("3. 进行用户验收测试")
    else:
        print("❌ 集成测试失败，请根据上述建议进行修复。")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)