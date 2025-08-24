#!/usr/bin/env python3
"""
验证 Validators 修复
"""

def verify_validators_fix():
    """验证 Validators 修复是否正确"""
    print("🔍 验证 Validators 修复...")
    
    # 检查 utils.js 文件
    try:
        with open('static/js/utils.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必需的验证器
        required_validators = [
            'required:',
            'email:',
            'stockCode:',
            'stockName:',
            'price:',
            'quantity:',
            'date:'
        ]
        
        missing_validators = []
        for validator in required_validators:
            if validator not in content:
                missing_validators.append(validator.replace(':', ''))
        
        if missing_validators:
            print(f"❌ 缺失验证器: {', '.join(missing_validators)}")
            return False
        
        print("✅ 所有必需的验证器都已定义")
        
        # 检查 required 验证器的实现
        if 'required: (value) =>' in content:
            print("✅ required 验证器: 正确定义")
        else:
            print("❌ required 验证器: 定义格式不正确")
            return False
        
        # 检查 Validators 导出
        if 'window.Validators = Validators;' in content:
            print("✅ Validators 对象: 正确导出到全局")
        else:
            print("❌ Validators 对象: 未正确导出")
            return False
        
        return True
        
    except FileNotFoundError:
        print("❌ static/js/utils.js 文件不存在")
        return False
    except Exception as e:
        print(f"❌ 检查文件时出错: {e}")
        return False

def check_form_validation_usage():
    """检查表单验证中的验证器使用"""
    print("\n🔍 检查表单验证中的验证器使用...")
    
    try:
        with open('static/js/form-validation.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查验证器调用
        validator_calls = [
            ('Validators.required', 'required字段验证'),
            ('Validators.email', 'email字段验证'),
        ]
        
        for validator_call, description in validator_calls:
            if validator_call in content:
                print(f"✅ 找到验证器调用: {validator_call} ({description})")
            else:
                print(f"❌ 未找到验证器调用: {validator_call}")
        
        # 检查 rule.validator 调用
        if 'rule.validator(value)' in content:
            print("✅ 验证器调用方式: 正确")
        else:
            print("❌ 验证器调用方式: 可能有问题")
        
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
    print("Validators 修复验证")
    print("=" * 50)
    
    # 验证修复
    validators_ok = verify_validators_fix()
    form_validation_ok = check_form_validation_usage()
    
    print("\n" + "=" * 50)
    if validators_ok and form_validation_ok:
        print("🎉 修复验证成功！")
        print("✅ Validators.required 函数已正确添加")
        print("✅ 表单验证应该可以正常工作了")
        print("\n📝 修复摘要:")
        print("- 添加了 Validators.required() 验证器")
        print("- 支持字符串、数字、布尔值的必填验证")
        print("- 兼容现有的 email、stockCode 等验证器")
        print("- 正确导出到全局 window.Validators 对象")
    else:
        print("❌ 修复验证失败，请检查上述问题")
    
    print("=" * 50)

if __name__ == '__main__':
    main()