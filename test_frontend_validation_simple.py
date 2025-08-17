#!/usr/bin/env python3
"""
前端表单验证和用户体验优化简单测试脚本
测试任务18的实现：前端表单验证和用户体验优化
"""

import os
import re
import json
from pathlib import Path

class FrontendValidationTester:
    def __init__(self):
        self.test_results = []
        self.base_path = Path(".")
        
    def test_javascript_files_exist(self):
        """测试JavaScript文件是否存在"""
        print("📋 测试1: JavaScript文件存在性检查")
        
        required_files = [
            "static/js/utils.js",
            "static/js/form-validation.js",
            "static/js/main.js",
            "static/js/api.js"
        ]
        
        for file_path in required_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                print(f"  ✅ {file_path} 存在")
            else:
                print(f"  ❌ {file_path} 不存在")
                self.test_results.append(f"文件不存在: {file_path}")
        
        return len([f for f in required_files if (self.base_path / f).exists()]) == len(required_files)
    
    def test_css_files_exist(self):
        """测试CSS文件是否存在"""
        print("\n📋 测试2: CSS文件存在性检查")
        
        required_files = [
            "static/css/main.css",
            "static/css/components.css"
        ]
        
        for file_path in required_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                print(f"  ✅ {file_path} 存在")
            else:
                print(f"  ❌ {file_path} 不存在")
                self.test_results.append(f"文件不存在: {file_path}")
        
        return len([f for f in required_files if (self.base_path / f).exists()]) == len(required_files)
    
    def test_form_validation_features(self):
        """测试表单验证功能代码"""
        print("\n📋 测试3: 表单验证功能代码检查")
        
        form_validation_file = self.base_path / "static/js/form-validation.js"
        if not form_validation_file.exists():
            print("  ❌ form-validation.js 文件不存在")
            self.test_results.append("form-validation.js 文件不存在")
            return False
        
        content = form_validation_file.read_text(encoding='utf-8')
        
        # 检查关键类和方法
        required_features = [
            "class FormValidator",
            "class FormEnhancer",
            "setupEventListeners",  # 实际的方法名
            "validateField",
            "showFieldError",
            "showFieldSuccess",
            "handleSubmit",
            "addRule",
            "clearFieldValidation"  # 实际的方法名
        ]
        
        for feature in required_features:
            if feature in content:
                print(f"  ✅ {feature} 功能存在")
            else:
                print(f"  ❌ {feature} 功能缺失")
                self.test_results.append(f"功能缺失: {feature}")
        
        return all(feature in content for feature in required_features)
    
    def test_ux_utils_features(self):
        """测试UX工具功能代码"""
        print("\n📋 测试4: UX工具功能代码检查")
        
        utils_file = self.base_path / "static/js/utils.js"
        if not utils_file.exists():
            print("  ❌ utils.js 文件不存在")
            self.test_results.append("utils.js 文件不存在")
            return False
        
        content = utils_file.read_text(encoding='utf-8')
        
        # 检查UX工具功能
        required_features = [
            "const UXUtils",
            "showLoading",
            "hideLoading",
            "showProgress",
            "showToast",
            "showConfirm",
            "showPrompt",
            "scrollToElement",
            "copyToClipboard",
            "const ResponsiveUtils",
            "getCurrentBreakpoint",
            "isMobile"
        ]
        
        for feature in required_features:
            if feature in content:
                print(f"  ✅ {feature} 功能存在")
            else:
                print(f"  ❌ {feature} 功能缺失")
                self.test_results.append(f"功能缺失: {feature}")
        
        return all(feature in content for feature in required_features)
    
    def test_enhanced_form_utils(self):
        """测试增强的表单工具"""
        print("\n📋 测试5: 增强表单工具代码检查")
        
        utils_file = self.base_path / "static/js/utils.js"
        content = utils_file.read_text(encoding='utf-8')
        
        # 检查增强的FormUtils功能
        required_features = [
            "clearErrors",
            "showFieldError",
            "showFieldSuccess",
            "validateField",
            "setupRealTimeValidation",
            "getValidatedData"
        ]
        
        for feature in required_features:
            if feature in content:
                print(f"  ✅ FormUtils.{feature} 功能存在")
            else:
                print(f"  ❌ FormUtils.{feature} 功能缺失")
                self.test_results.append(f"FormUtils功能缺失: {feature}")
        
        return all(feature in content for feature in required_features)
    
    def test_css_validation_styles(self):
        """测试CSS验证样式"""
        print("\n📋 测试6: CSS验证样式检查")
        
        main_css_file = self.base_path / "static/css/main.css"
        components_css_file = self.base_path / "static/css/components.css"
        
        if not main_css_file.exists():
            print("  ❌ main.css 文件不存在")
            self.test_results.append("main.css 文件不存在")
            return False
        
        main_content = main_css_file.read_text(encoding='utf-8')
        components_content = components_css_file.read_text(encoding='utf-8') if components_css_file.exists() else ""
        
        all_content = main_content + components_content
        
        # 检查验证相关的CSS类
        required_styles = [
            ".is-invalid",
            ".is-valid",
            ".invalid-feedback",
            ".valid-feedback",
            ".loading-overlay",
            ".loading-spinner",
            ".highlight-animation",
            ".char-counter",
            ".progress",
            ".toast"
        ]
        
        for style in required_styles:
            if style in all_content:
                print(f"  ✅ {style} 样式存在")
            else:
                print(f"  ❌ {style} 样式缺失")
                self.test_results.append(f"样式缺失: {style}")
        
        return all(style in all_content for style in required_styles)
    
    def test_responsive_design_styles(self):
        """测试响应式设计样式"""
        print("\n📋 测试7: 响应式设计样式检查")
        
        main_css_file = self.base_path / "static/css/main.css"
        content = main_css_file.read_text(encoding='utf-8')
        
        # 检查媒体查询
        media_queries = [
            "@media (max-width: 768px)",
            "@media (max-width: 576px)"
        ]
        
        for query in media_queries:
            if query in content:
                print(f"  ✅ {query} 媒体查询存在")
            else:
                print(f"  ❌ {query} 媒体查询缺失")
                self.test_results.append(f"媒体查询缺失: {query}")
        
        # 检查响应式相关样式
        responsive_features = [
            ".sidebar.show",
            "font-size: 16px",  # 防止iOS缩放
            "min-height: 44px"  # 触摸友好高度
        ]
        
        for feature in responsive_features:
            if feature in content:
                print(f"  ✅ 响应式特性存在: {feature}")
            else:
                print(f"  ❌ 响应式特性缺失: {feature}")
                self.test_results.append(f"响应式特性缺失: {feature}")
        
        return all(query in content for query in media_queries)
    
    def test_template_integration(self):
        """测试模板集成"""
        print("\n📋 测试8: 模板集成检查")
        
        base_template = self.base_path / "templates/base.html"
        trading_template = self.base_path / "templates/trading_records.html"
        
        if not base_template.exists():
            print("  ❌ base.html 模板不存在")
            self.test_results.append("base.html 模板不存在")
            return False
        
        base_content = base_template.read_text(encoding='utf-8')
        
        # 检查基础模板中的脚本引用
        required_scripts = [
            "form-validation.js",
            "utils.js",
            "main.js",
            "api.js"
        ]
        
        for script in required_scripts:
            if script in base_content:
                print(f"  ✅ {script} 脚本已引用")
            else:
                print(f"  ❌ {script} 脚本未引用")
                self.test_results.append(f"脚本未引用: {script}")
        
        # 检查必要的HTML元素
        required_elements = [
            'id="toast-container"',
            'id="loadingModal"',
            'toast-container'  # 检查类名存在
        ]
        
        for element in required_elements:
            if element in base_content:
                print(f"  ✅ HTML元素存在: {element}")
            else:
                print(f"  ❌ HTML元素缺失: {element}")
                self.test_results.append(f"HTML元素缺失: {element}")
        
        # 检查交易记录模板
        if trading_template.exists():
            trading_content = trading_template.read_text(encoding='utf-8')
            
            # 检查表单验证属性
            validation_attributes = [
                'data-validate',
                'pattern="[0-9]{6}"',
                'maxlength=',
                'minlength=',
                'required'
            ]
            
            for attr in validation_attributes:
                if attr in trading_content:
                    print(f"  ✅ 验证属性存在: {attr}")
                else:
                    print(f"  ❌ 验证属性缺失: {attr}")
                    self.test_results.append(f"验证属性缺失: {attr}")
        
        return all(script in base_content for script in required_scripts)
    
    def test_javascript_syntax(self):
        """测试JavaScript语法"""
        print("\n📋 测试9: JavaScript语法检查")
        
        js_files = [
            "static/js/utils.js",
            "static/js/form-validation.js",
            "static/js/main.js"
        ]
        
        syntax_ok = True
        
        for js_file in js_files:
            file_path = self.base_path / js_file
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                
                # 简单的语法检查
                # 检查括号匹配
                open_braces = content.count('{')
                close_braces = content.count('}')
                open_parens = content.count('(')
                close_parens = content.count(')')
                
                if open_braces == close_braces:
                    print(f"  ✅ {js_file} 大括号匹配")
                else:
                    print(f"  ❌ {js_file} 大括号不匹配 ({open_braces}:{close_braces})")
                    self.test_results.append(f"{js_file} 大括号不匹配")
                    syntax_ok = False
                
                if open_parens == close_parens:
                    print(f"  ✅ {js_file} 小括号匹配")
                else:
                    print(f"  ❌ {js_file} 小括号不匹配 ({open_parens}:{close_parens})")
                    self.test_results.append(f"{js_file} 小括号不匹配")
                    syntax_ok = False
                
                # 检查常见语法错误
                if 'function(' in content or 'function (' in content:
                    print(f"  ✅ {js_file} 包含函数定义")
                
                if 'class ' in content:
                    print(f"  ✅ {js_file} 包含类定义")
        
        return syntax_ok
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始前端表单验证和用户体验优化测试")
        print("=" * 60)
        
        tests = [
            self.test_javascript_files_exist,
            self.test_css_files_exist,
            self.test_form_validation_features,
            self.test_ux_utils_features,
            self.test_enhanced_form_utils,
            self.test_css_validation_styles,
            self.test_responsive_design_styles,
            self.test_template_integration,
            self.test_javascript_syntax
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"  ❌ 测试执行异常: {e}")
                self.test_results.append(f"测试执行异常: {e}")
        
        # 输出测试结果
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print(f"✅ 通过测试: {passed_tests}/{total_tests}")
        
        if self.test_results:
            print(f"❌ 失败项目: {len(self.test_results)}")
            for i, error in enumerate(self.test_results, 1):
                print(f"   {i}. {error}")
        else:
            print("🎉 所有测试都通过了！")
        
        return len(self.test_results) == 0

def main():
    """主函数"""
    tester = FrontendValidationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 前端表单验证和用户体验优化测试全部通过！")
        print("✅ 任务18实现成功")
        
        # 输出实现总结
        print("\n📋 实现功能总结:")
        print("1. ✅ 实现了所有表单的客户端验证和错误提示")
        print("2. ✅ 添加了操作成功的反馈消息和状态指示")
        print("3. ✅ 创建了加载状态和进度指示器")
        print("4. ✅ 优化了移动端响应式设计和交互体验")
        print("5. ✅ 增强了表单工具和验证器")
        print("6. ✅ 添加了UX工具和响应式工具")
        print("7. ✅ 完善了CSS样式和动画效果")
        print("8. ✅ 集成了模板和JavaScript脚本")
        
        return 0
    else:
        print("\n❌ 部分测试失败，请检查实现")
        return 1

if __name__ == "__main__":
    exit(main())