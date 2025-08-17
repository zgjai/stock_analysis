#!/usr/bin/env python3
"""
最终修复验证脚本
"""
import subprocess
import time
import json

def test_api():
    """测试API是否正常"""
    print("1. 测试API响应...")
    try:
        result = subprocess.run([
            'curl', '-s', 'http://localhost:5001/api/trades'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if data.get('success') and 'data' in data and 'trades' in data['data']:
                    print(f"✓ API正常，返回{len(data['data']['trades'])}条交易记录")
                    return True
                else:
                    print("✗ API响应格式不正确")
                    return False
            except json.JSONDecodeError:
                print("✗ API返回的不是有效JSON")
                return False
        else:
            print("✗ API请求失败")
            return False
    except Exception as e:
        print(f"✗ API测试异常: {e}")
        return False

def check_page_content():
    """检查页面内容"""
    print("\n2. 检查页面内容...")
    try:
        result = subprocess.run([
            'curl', '-s', 'http://localhost:5001/trading-records'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            content = result.stdout
            
            # 检查是否包含必要的元素
            checks = [
                ('交易记录表格', 'trades-table-body' in content),
                ('立即隐藏脚本', '立即隐藏加载状态' in content),
                ('TradingRecordsManager', 'TradingRecordsManager' in content),
                ('API客户端', 'apiClient' in content),
                ('防重复初始化', 'tradingManagerInitialized' in content)
            ]
            
            all_good = True
            for name, check in checks:
                if check:
                    print(f"✓ {name}: 存在")
                else:
                    print(f"✗ {name}: 缺失")
                    all_good = False
            
            return all_good
        else:
            print("✗ 无法获取页面内容")
            return False
    except Exception as e:
        print(f"✗ 页面检查异常: {e}")
        return False

def main():
    """主函数"""
    print("交易记录页面最终修复验证")
    print("=" * 50)
    
    api_ok = test_api()
    page_ok = check_page_content()
    
    print("\n" + "=" * 50)
    print("验证结果:")
    print(f"API测试: {'✓ 通过' if api_ok else '✗ 失败'}")
    print(f"页面检查: {'✓ 通过' if page_ok else '✗ 失败'}")
    
    if api_ok and page_ok:
        print("\n🎉 修复验证通过！")
        print("\n修复内容总结:")
        print("1. ✓ 修正了前端数据结构映射 (data.items -> data.trades)")
        print("2. ✓ 修正了分页数据结构 (pagination -> 直接构造)")
        print("3. ✓ 添加了立即隐藏加载状态的代码")
        print("4. ✓ 添加了防重复初始化的保护")
        print("5. ✓ 改进了showLoading函数的调用")
        
        print("\n请刷新浏览器页面查看效果！")
        return True
    else:
        print("\n❌ 修复验证失败，需要进一步检查")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)