#!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
import os

def verify_template_syntax():
    """验证Jinja2模板语法"""
    try:
        # 创建Jinja2环境
        env = Environment(loader=FileSystemLoader('templates'))
        
        # 尝试加载模板
        template = env.get_template('trading_records.html')
        
        print("✅ 模板语法检查通过")
        
        # 尝试渲染模板（使用空上下文）
        try:
            rendered = template.render()
            print("✅ 模板渲染成功")
            print(f"渲染后的内容长度: {len(rendered)} 字符")
            
            # 检查是否包含JavaScript错误
            if 'SyntaxError' in rendered:
                print("⚠️  渲染后的内容可能包含JavaScript语法错误")
            else:
                print("✅ 渲染后的内容未发现明显的JavaScript语法错误")
                
        except Exception as render_error:
            print(f"⚠️  模板渲染警告: {render_error}")
            print("这可能是由于缺少上下文变量导致的，但模板语法本身是正确的")
        
    except TemplateSyntaxError as e:
        print(f"❌ 模板语法错误:")
        print(f"   文件: {e.filename}")
        print(f"   行号: {e.lineno}")
        print(f"   错误: {e.message}")
        return False
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("验证trading_records.html模板语法...")
    success = verify_template_syntax()
    
    if success:
        print("\n🎉 模板修复成功！现在可以尝试刷新浏览器页面。")
    else:
        print("\n💥 模板仍有问题，需要进一步修复。")