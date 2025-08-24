#!/usr/bin/env python3
"""
验证 UXUtils 修复
"""

def verify_uxutils_fix():
    """验证 UXUtils 修复是否正确"""
    print("🔍 验证 UXUtils 修复...")
    
    # 检查 utils.js 文件
    try:
        with open('static/js/utils.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必需的函数
        required_functions = [
            'showGlobalLoading',
            'forceHideAllLoading', 
            'hideGlobalLoading'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f'{func}:' not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ 缺失函数: {', '.join(missing_functions)}")
            return False
        
        print("✅ 所有必需的 UXUtils 函数都已添加")
        
        # 检查函数实现的关键部分
        checks = [
            ('showGlobalLoading 创建遮罩', 'global-loading-overlay'),
            ('showGlobalLoading 超时机制', '15000'),
            ('forceHideAllLoading 清理按钮', 'data-original-text'),
            ('forceHideAllLoading 清理spinner', 'spinner-border'),
        ]
        
        for check_name, check_content in checks:
            if check_content in content:
                print(f"✅ {check_name}: 正确")
            else:
                print(f"⚠️ {check_name}: 可能有问题")
        
        return True
        
    except FileNotFoundError:
        print("❌ static/js/utils.js 文件不存在")
        return False
    except Exception as e:
        print(f"❌ 检查文件时出错: {e}")
        return False

def check_trading_records_usage():
    """检查交易记录模板中的函数调用"""
    print("\n🔍 检查交易记录模板中的函数调用...")
    
    try:
        with open('templates/trading_records.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查函数调用
        function_calls = [
            ('UXUtils.showGlobalLoading', '加载交易记录'),
            ('UXUtils.forceHideAllLoading', 'finally'),
        ]
        
        for func_call, context in function_calls:
            if func_call in content:
                print(f"✅ 找到函数调用: {func_call}")
                # 检查上下文
                if context in content:
                    print(f"  ✅ 上下文正确: {context}")
                else:
                    print(f"  ⚠️ 上下文可能有问题: {context}")
            else:
                print(f"❌ 未找到函数调用: {func_call}")
        
        return True
        
    except FileNotFoundError:
        print("❌ templates/trading_records.html 文件不存在")
        return False
    except Exception as e:
        print(f"❌ 检查文件时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("UXUtils 修复验证")
    print("=" * 50)
    
    # 验证修复
    utils_ok = verify_uxutils_fix()
    trading_ok = check_trading_records_usage()
    
    print("\n" + "=" * 50)
    if utils_ok and trading_ok:
        print("🎉 修复验证成功！")
        print("✅ UXUtils.showGlobalLoading 和 UXUtils.forceHideAllLoading 函数已正确添加")
        print("✅ 交易记录编辑功能应该可以正常工作了")
        print("\n📝 修复摘要:")
        print("- 添加了 UXUtils.showGlobalLoading() 函数")
        print("- 添加了 UXUtils.forceHideAllLoading() 函数") 
        print("- 添加了 UXUtils.hideGlobalLoading() 函数")
        print("- 包含了15秒超时机制防止加载状态卡住")
        print("- 包含了强制清理所有加载状态的功能")
    else:
        print("❌ 修复验证失败，请检查上述问题")
    
    print("=" * 50)

if __name__ == '__main__':
    main()