#!/usr/bin/env python3
"""
检查复盘记录数据和API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.review_record import ReviewRecord
from datetime import datetime, date

def check_review_data():
    """检查复盘记录数据"""
    print("=== 检查复盘记录数据 ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 检查数据库连接
            print("1. 检查数据库连接...")
            total_reviews = ReviewRecord.query.count()
            print(f"✓ 数据库连接正常，总共有 {total_reviews} 条复盘记录")
            
            # 2. 查询000776的复盘记录
            print("\n2. 查询000776的复盘记录...")
            reviews_000776 = ReviewRecord.query.filter_by(stock_code='000776').all()
            
            if reviews_000776:
                print(f"✓ 找到 {len(reviews_000776)} 条000776的复盘记录:")
                for review in reviews_000776:
                    print(f"   - ID: {review.id}")
                    print(f"     股票: {review.stock_code} - {review.stock_name}")
                    print(f"     日期: {review.review_date}")
                    print(f"     决策: {review.decision}")
                    print(f"     创建时间: {review.created_at}")
                    print(f"     更新时间: {review.updated_at}")
                    print()
            else:
                print("❌ 没有找到000776的复盘记录")
            
            # 3. 查询所有复盘记录
            print("3. 查询所有复盘记录...")
            all_reviews = ReviewRecord.query.order_by(ReviewRecord.created_at.desc()).limit(10).all()
            
            if all_reviews:
                print(f"✓ 最近的 {len(all_reviews)} 条复盘记录:")
                for review in all_reviews:
                    print(f"   - {review.stock_code} ({review.stock_name}) - {review.review_date} - {review.decision}")
            else:
                print("❌ 数据库中没有任何复盘记录")
            
            # 4. 测试API响应格式
            print("\n4. 测试API响应格式...")
            from services.review_service import ReviewService
            
            try:
                # 获取复盘记录列表
                result = ReviewService.get_reviews()
                print("✓ ReviewService.get_reviews() 调用成功")
                print(f"   返回数据结构: {type(result)}")
                print(f"   数据内容: {result}")
                
                # 检查数据结构
                if isinstance(result, dict):
                    if 'reviews' in result:
                        print(f"   包含reviews字段，有 {len(result['reviews'])} 条记录")
                    else:
                        print(f"   数据字段: {list(result.keys())}")
                
            except Exception as e:
                print(f"❌ ReviewService调用失败: {e}")
            
            # 5. 创建测试复盘记录（如果没有000776的记录）
            if not reviews_000776:
                print("\n5. 创建测试复盘记录...")
                try:
                    test_review = ReviewRecord(
                        stock_code='000776',
                        stock_name='广发证券',
                        review_date=date.today(),
                        decision='hold',
                        analysis='测试复盘记录',
                        price_up_score=3,
                        bbi_score=3,
                        volume_score=3,
                        trend_score=3,
                        j_score=3,
                        total_score=15
                    )
                    
                    db.session.add(test_review)
                    db.session.commit()
                    
                    print(f"✓ 成功创建测试复盘记录，ID: {test_review.id}")
                    
                except Exception as e:
                    print(f"❌ 创建测试复盘记录失败: {e}")
                    db.session.rollback()
            
        except Exception as e:
            print(f"❌ 检查过程中出现错误: {e}")

def test_review_api():
    """测试复盘记录API"""
    print("\n=== 测试复盘记录API ===")
    
    app = create_app()
    
    with app.test_client() as client:
        try:
            # 测试GET /api/reviews
            print("1. 测试 GET /api/reviews...")
            response = client.get('/api/reviews')
            
            print(f"   状态码: {response.status_code}")
            print(f"   响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   响应数据: {data}")
                
                if data and data.get('success'):
                    print("✓ API调用成功")
                    
                    # 检查数据结构
                    api_data = data.get('data')
                    if api_data:
                        if isinstance(api_data, dict) and 'reviews' in api_data:
                            reviews = api_data['reviews']
                            print(f"   找到 {len(reviews)} 条复盘记录")
                        elif isinstance(api_data, list):
                            print(f"   找到 {len(api_data)} 条复盘记录")
                        else:
                            print(f"   数据类型: {type(api_data)}")
                    else:
                        print("   没有data字段")
                else:
                    print(f"❌ API返回失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API调用失败，状态码: {response.status_code}")
                print(f"   响应内容: {response.get_data(as_text=True)}")
            
            # 测试特定股票查询
            print("\n2. 测试 GET /api/reviews?stock_code=000776...")
            response = client.get('/api/reviews?stock_code=000776')
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   响应数据: {data}")
                
                if data and data.get('success'):
                    api_data = data.get('data')
                    if api_data:
                        if isinstance(api_data, dict) and 'reviews' in api_data:
                            reviews = api_data['reviews']
                            print(f"✓ 找到 {len(reviews)} 条000776的复盘记录")
                        elif isinstance(api_data, list):
                            print(f"✓ 找到 {len(api_data)} 条000776的复盘记录")
                        else:
                            print(f"   数据类型: {type(api_data)}")
                    else:
                        print("   没有找到000776的复盘记录")
                else:
                    print(f"❌ API返回失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ API调用失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ API测试过程中出现错误: {e}")

def main():
    """主函数"""
    print("开始检查复盘记录数据和API...")
    print("=" * 50)
    
    check_review_data()
    test_review_api()
    
    print("\n" + "=" * 50)
    print("检查完成！")
    print("\n建议:")
    print("1. 如果数据库中确实有复盘记录但前端不显示，问题在前端逻辑")
    print("2. 如果数据库中没有复盘记录，需要先创建一些测试数据")
    print("3. 如果API返回的数据结构不符合前端预期，需要调整前端解析逻辑")

if __name__ == "__main__":
    main()