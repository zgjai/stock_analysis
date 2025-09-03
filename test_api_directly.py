#!/usr/bin/env python3
"""
直接测试API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import json

def test_api():
    """测试API"""
    app = create_app()
    
    with app.test_client() as client:
        try:
            print("=== 直接测试期望对比API ===\n")
            
            # 测试期望对比API
            response = client.get('/api/analytics/expectation-comparison?time_range=all')
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.get_json()
                print("✅ API调用成功")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print("❌ API调用失败")
                print(f"响应内容: {response.get_data(as_text=True)}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_api()