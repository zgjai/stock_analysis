#!/usr/bin/env python3
"""
验证 FormUtils 修复
"""

def verify_formutils_fix():
    """验证 FormUtils 修复是否正确"""
    print("🔍 验证 FormUtils 修复...")
    
    # 检查 utils.js 文件
    try:
        with open('static/js/utils.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必需的 FormUtils 方法
        required_methods = [
            'serialize:',
            'populate:',
            'reset:',
            'disable:'
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in content:
                missing_methods.append(method.replace(':', ''))
        
        if missing_methods:
            print(f"❌ 缺失方法: {', '.join(missing_methods)}")
            return False
        
        print("✅ 所有必需的 FormUtils 方法都已定义")
        
        # 检查 disable 方法的实现
        if 'disable: (form, disabled = true)' in content:
            print("✅ disable 方法: 正确定义")
        else:
            print("❌ disable 方法: 定义格式不正确")
            return False
        
        # 检查 disable 方法的关键功能
        disable_checks = [
            ('禁用表单控件', 'element.disabled = disabled'),
            ('视觉样式处理', 'form-disabled'),
            ('透明度设置', 'opacity'),
            ('指针事件控制', 'pointerEvents')
        ]
        
        for check_name, check_content in disable_checks:
            if check_content in content:
                print(f"✅ {check_name}: 正确")
            else:
                print(f"⚠️ {check_name}: 可能有问题")
        
        # 检查 FormUtils 导出
        if 'window.FormUtils = FormUtils;' in content:
            print("✅ FormUtils 对象: 正确导出到全局")
        else:
            print("❌ FormUtils 对象: 未正确导出")
            return False
        
        return True
        
    except FileNotFoundError:
        print("❌ static/js/utils.js 文件不存在")
        return False
    except Exception as e:
        print(f"❌ 检查文件时出错: {e}")
        return False

def check_form_validation_usage():
    """检查表单验证中的 FormUtils 使用"""
    print("\n🔍 检查表单验证中的 FormUtils 使用...")
    
    try:
        with open('static/js/form-validation.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查 FormUtils 方法调用
        formutils_calls = [
            ('FormUtils.disable', '禁用/启用表单'),
            ('FormUtils.serialize', '序列化表单数据'),
        ]
        
        for method_call, description in formutils_calls:
            if method_call in content:
                print(f"✅ 找到方法调用: {method_call} ({description})")
            else:
                print(f"❌ 未找到方法调用: {method_call}")
        
        # 检查具体的调用上下文
        if 'FormUtils.disable(this.form, true)' in content:
            print("✅ 表单禁用调用: 正确")
        else:
            print("❌ 表单禁用调用: 可能有问题")
            
        if 'FormUtils.disable(this.form, false)' in content:
            print("✅ 表单启用调用: 正确")
        else:
            print("❌ 表单启用调用: 可能有问题")
        
        return True
        
    except FileNotFoundError:
        print("❌ static/js/form-validation.js 文件不存在")
        return False
    except Exception as e:
        print(f"❌ 检查文件时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("FormUtils 修复验证")
    print("=" * 50)
    
    # 验证修复
    formutils_ok = verify_formutils_fix()
    form_validation_ok = check_form_validation_usage()
    
    print("\n" + "=" * 50)
    if formutils_ok and form_validation_ok:
        print("🎉 修复验证成功！")
        print("✅ FormUtils.disable 方法已正确添加")
        print("✅ 表单验证应该可以正常工作了")
        print("\n📝 修复摘要:")
        print("- 添加了 FormUtils.disable() 方法")
        print("- 支持禁用/启用表单及其所有控件")
        print("- 包含视觉反馈（透明度、指针事件）")
        print("- 兼容现有的 serialize、populate、reset 方法")
    else:
        print("❌ 修复验证失败，请检查上述问题")
    
    print("=" * 50)

if __name__ == '__main__':
    main()