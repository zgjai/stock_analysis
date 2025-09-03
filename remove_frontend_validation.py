#!/usr/bin/env python3
"""
彻底移除前端页面校验逻辑的脚本
解决经常出现的校验问题
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """备份文件"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"✅ 已备份: {file_path} -> {backup_path}")
        return backup_path
    return None

def remove_html_validation_attributes(content):
    """移除HTML中的校验属性"""
    # 移除required属性
    content = re.sub(r'\s+required(?:\s*=\s*["\'][^"\']*["\'])?', '', content, flags=re.IGNORECASE)
    
    # 移除pattern属性
    content = re.sub(r'\s+pattern\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
    
    # 移除minlength属性
    content = re.sub(r'\s+minlength\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
    
    # 移除maxlength属性（保留一些合理的长度限制）
    # content = re.sub(r'\s+maxlength\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
    
    # 移除min和max属性（数字输入的范围限制）
    content = re.sub(r'\s+min\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\s+max\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
    
    # 移除data-validate属性
    content = re.sub(r'\s+data-validate(?:\s*=\s*["\'][^"\']*["\'])?', '', content, flags=re.IGNORECASE)
    
    # 移除novalidate属性（我们要添加这个）
    content = re.sub(r'\s+novalidate(?:\s*=\s*["\'][^"\']*["\'])?', '', content, flags=re.IGNORECASE)
    
    return content

def add_novalidate_to_forms(content):
    """给所有form标签添加novalidate属性"""
    # 匹配form标签并添加novalidate
    def replace_form_tag(match):
        form_tag = match.group(0)
        if 'novalidate' not in form_tag.lower():
            # 在form标签中添加novalidate属性
            if form_tag.endswith('>'):
                form_tag = form_tag[:-1] + ' novalidate>'
            else:
                form_tag = form_tag + ' novalidate'
        return form_tag
    
    content = re.sub(r'<form[^>]*>', replace_form_tag, content, flags=re.IGNORECASE)
    return content

def disable_js_validation(content):
    """禁用JavaScript中的校验逻辑"""
    
    # 替换validateField方法，让它总是返回true
    content = re.sub(
        r'validateField\s*\([^)]*\)\s*{[^}]*}',
        'validateField() { return true; }',
        content,
        flags=re.DOTALL
    )
    
    # 替换validateForm方法，让它总是返回true
    content = re.sub(
        r'validateForm\s*\([^)]*\)\s*{[^}]*}',
        'validateForm() { this.errors = {}; return true; }',
        content,
        flags=re.DOTALL
    )
    
    # 注释掉所有的验证相关代码
    validation_patterns = [
        r'\.classList\.add\(["\']is-invalid["\']',
        r'\.classList\.remove\(["\']is-valid["\']',
        r'\.classList\.add\(["\']is-valid["\']',
        r'\.classList\.remove\(["\']is-invalid["\']',
        r'showFieldError\s*\(',
        r'showFieldSuccess\s*\(',
        r'clearFieldError\s*\(',
        r'clearFieldValidation\s*\(',
    ]
    
    for pattern in validation_patterns:
        content = re.sub(pattern, '// ' + pattern.replace('\\', ''), content)
    
    return content

def process_html_files():
    """处理HTML模板文件"""
    html_files = []
    
    # 查找所有HTML文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                html_files.append(file_path)
    
    print(f"🔍 找到 {len(html_files)} 个HTML文件")
    
    for file_path in html_files:
        try:
            # 备份文件
            backup_file(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除校验属性
            original_content = content
            content = remove_html_validation_attributes(content)
            content = add_novalidate_to_forms(content)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已处理HTML文件: {file_path}")
            else:
                print(f"⏭️  跳过HTML文件（无需修改）: {file_path}")
                
        except Exception as e:
            print(f"❌ 处理HTML文件失败 {file_path}: {e}")

def process_js_files():
    """处理JavaScript文件"""
    js_files = []
    
    # 查找所有JavaScript文件
    for root, dirs, files in os.walk('.'):
        # 跳过一些目录
        if any(skip_dir in root for skip_dir in ['node_modules', '.git', '__pycache__', 'venv']):
            continue
            
        for file in files:
            if file.endswith('.js'):
                file_path = os.path.join(root, file)
                js_files.append(file_path)
    
    print(f"🔍 找到 {len(js_files)} 个JavaScript文件")
    
    for file_path in js_files:
        try:
            # 备份文件
            backup_file(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 禁用校验逻辑
            original_content = content
            content = disable_js_validation(content)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已处理JS文件: {file_path}")
            else:
                print(f"⏭️  跳过JS文件（无需修改）: {file_path}")
                
        except Exception as e:
            print(f"❌ 处理JS文件失败 {file_path}: {e}")

def create_validation_disabler():
    """创建一个彻底禁用校验的JavaScript文件"""
    
    js_content = '''
// 彻底禁用前端校验的脚本
// 这个脚本会在页面加载时运行，确保所有校验都被禁用

(function() {
    'use strict';
    
    console.log('🚫 开始禁用所有前端校验...');
    
    // 1. 禁用HTML5表单校验
    function disableHTML5Validation() {
        // 给所有form添加novalidate属性
        document.querySelectorAll('form').forEach(form => {
            form.setAttribute('novalidate', 'true');
            form.noValidate = true;
        });
        
        // 移除所有required属性
        document.querySelectorAll('[required]').forEach(element => {
            element.removeAttribute('required');
        });
        
        // 移除所有pattern属性
        document.querySelectorAll('[pattern]').forEach(element => {
            element.removeAttribute('pattern');
        });
        
        // 移除min/max属性
        document.querySelectorAll('[min]').forEach(element => {
            element.removeAttribute('min');
        });
        
        document.querySelectorAll('[max]').forEach(element => {
            element.removeAttribute('max');
        });
        
        console.log('✅ HTML5校验已禁用');
    }
    
    // 2. 重写所有可能的校验器
    function disableJSValidation() {
        // 重写SimpleFormValidator
        if (window.SimpleFormValidator) {
            const originalPrototype = window.SimpleFormValidator.prototype;
            originalPrototype.validateField = function() { return true; };
            originalPrototype.validateForm = function() { 
                this.errors = {}; 
                return true; 
            };
            originalPrototype.showFieldError = function() {};
            originalPrototype.showFieldSuccess = function() {};
            originalPrototype.clearFieldError = function() {};
            originalPrototype.clearAllValidation = function() {};
        }
        
        // 重写FormValidator
        if (window.FormValidator) {
            const originalPrototype = window.FormValidator.prototype;
            originalPrototype.validateField = function() { return true; };
            originalPrototype.validateForm = function() { 
                return { isValid: true, errors: {} }; 
            };
            originalPrototype.showFieldError = function() {};
            originalPrototype.showFieldSuccess = function() {};
            originalPrototype.clearFieldValidation = function() {};
        }
        
        // 重写Validators对象
        if (window.Validators) {
            Object.keys(window.Validators).forEach(key => {
                window.Validators[key] = function() { return true; };
            });
        }
        
        console.log('✅ JavaScript校验已禁用');
    }
    
    // 3. 清除所有校验状态
    function clearValidationStates() {
        // 移除所有is-invalid和is-valid类
        document.querySelectorAll('.is-invalid, .is-valid').forEach(element => {
            element.classList.remove('is-invalid', 'is-valid');
        });
        
        // 隐藏所有错误消息
        document.querySelectorAll('.invalid-feedback, .valid-feedback').forEach(element => {
            element.style.display = 'none';
        });
        
        console.log('✅ 校验状态已清除');
    }
    
    // 4. 阻止校验事件
    function blockValidationEvents() {
        // 阻止表单的invalid事件
        document.addEventListener('invalid', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }, true);
        
        // 阻止input事件中的校验
        document.addEventListener('input', function(e) {
            if (e.target.matches('input, select, textarea')) {
                // 清除可能的校验状态
                e.target.classList.remove('is-invalid', 'is-valid');
            }
        }, true);
        
        // 阻止blur事件中的校验
        document.addEventListener('blur', function(e) {
            if (e.target.matches('input, select, textarea')) {
                // 清除可能的校验状态
                e.target.classList.remove('is-invalid', 'is-valid');
            }
        }, true);
        
        console.log('✅ 校验事件已阻止');
    }
    
    // 5. 重写表单提交处理
    function overrideFormSubmission() {
        document.addEventListener('submit', function(e) {
            // 确保表单可以正常提交，不被校验阻止
            const form = e.target;
            if (form.tagName === 'FORM') {
                form.noValidate = true;
                // 清除所有校验状态
                form.querySelectorAll('.is-invalid, .is-valid').forEach(element => {
                    element.classList.remove('is-invalid', 'is-valid');
                });
            }
        }, true);
        
        console.log('✅ 表单提交已优化');
    }
    
    // 执行所有禁用操作
    function executeAll() {
        disableHTML5Validation();
        disableJSValidation();
        clearValidationStates();
        blockValidationEvents();
        overrideFormSubmission();
        
        console.log('🎉 所有前端校验已成功禁用！');
    }
    
    // 立即执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', executeAll);
    } else {
        executeAll();
    }
    
    // 定期清理（防止其他脚本重新启用校验）
    setInterval(function() {
        clearValidationStates();
        disableHTML5Validation();
    }, 1000);
    
})();
'''
    
    # 写入到静态文件目录
    output_path = 'static/js/disable-validation.js'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✅ 已创建校验禁用脚本: {output_path}")
    return output_path

def update_base_template():
    """更新基础模板，引入禁用校验的脚本"""
    base_template_path = 'templates/base.html'
    
    if not os.path.exists(base_template_path):
        print(f"⚠️  基础模板不存在: {base_template_path}")
        return
    
    # 备份文件
    backup_file(base_template_path)
    
    try:
        with open(base_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经包含了禁用校验的脚本
        if 'disable-validation.js' in content:
            print("⏭️  基础模板已包含禁用校验脚本")
            return
        
        # 在</body>标签前添加脚本引用
        script_tag = '    <script src="{{ url_for(\'static\', filename=\'js/disable-validation.js\') }}"></script>\n'
        
        if '</body>' in content:
            content = content.replace('</body>', script_tag + '</body>')
        else:
            # 如果没有</body>标签，添加到文件末尾
            content += '\n' + script_tag
        
        with open(base_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新基础模板: {base_template_path}")
        
    except Exception as e:
        print(f"❌ 更新基础模板失败: {e}")

def main():
    """主函数"""
    print("🚀 开始移除前端页面校验逻辑...")
    print("=" * 50)
    
    # 1. 处理HTML文件
    print("\n📄 处理HTML模板文件...")
    process_html_files()
    
    # 2. 处理JavaScript文件
    print("\n📜 处理JavaScript文件...")
    process_js_files()
    
    # 3. 创建校验禁用脚本
    print("\n🔧 创建校验禁用脚本...")
    disable_script_path = create_validation_disabler()
    
    # 4. 更新基础模板
    print("\n📋 更新基础模板...")
    update_base_template()
    
    print("\n" + "=" * 50)
    print("🎉 前端校验移除完成！")
    print("\n📝 完成的操作:")
    print("   ✅ 移除了HTML中的required、pattern、min、max等校验属性")
    print("   ✅ 给所有form标签添加了novalidate属性")
    print("   ✅ 禁用了JavaScript中的校验逻辑")
    print("   ✅ 创建了校验禁用脚本")
    print("   ✅ 更新了基础模板引用")
    print("\n⚠️  注意:")
    print("   - 所有原文件都已备份（.backup_时间戳）")
    print("   - 如需恢复，可以使用备份文件")
    print("   - 建议重启服务器以确保更改生效")

if __name__ == '__main__':
    main()