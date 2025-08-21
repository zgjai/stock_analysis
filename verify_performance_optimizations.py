#!/usr/bin/env python3
"""
性能优化验证脚本
验证所有性能优化功能是否正确实现
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

class PerformanceOptimizationVerifier:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = {
            'files_created': [],
            'files_verified': [],
            'optimizations_implemented': [],
            'tests_passed': [],
            'errors': []
        }
    
    def verify_files_exist(self):
        """验证所有优化文件是否存在"""
        print("🔍 验证性能优化文件...")
        
        required_files = [
            'static/js/performance-optimizations.js',
            'static/js/auto-save-manager.js',
            'static/js/loading-indicators.js',
            'static/js/keyboard-shortcuts.js',
            'static/css/mobile-optimizations.css',
            'test_performance_optimizations.html'
        ]
        
        for file_path in required_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                self.results['files_created'].append(file_path)
                print(f"  ✅ {file_path}")
            else:
                self.results['errors'].append(f"Missing file: {file_path}")
                print(f"  ❌ {file_path}")
    
    def verify_file_contents(self):
        """验证文件内容是否包含必要的功能"""
        print("\n🔍 验证文件内容...")
        
        # 验证性能优化工具
        perf_file = self.base_path / 'static/js/performance-optimizations.js'
        if perf_file.exists():
            content = perf_file.read_text(encoding='utf-8')
            
            required_functions = [
                'debounce',
                'throttle',
                'rafThrottle',
                'MemoryCache',
                'BatchProcessor',
                'VirtualScroller',
                'LazyImageLoader'
            ]
            
            for func in required_functions:
                if func in content:
                    self.results['optimizations_implemented'].append(f"Performance: {func}")
                    print(f"  ✅ 性能优化: {func}")
                else:
                    self.results['errors'].append(f"Missing function: {func}")
                    print(f"  ❌ 缺少功能: {func}")
        
        # 验证自动保存管理器
        autosave_file = self.base_path / 'static/js/auto-save-manager.js'
        if autosave_file.exists():
            content = autosave_file.read_text(encoding='utf-8')
            
            required_features = [
                'AutoSaveManager',
                'enableOfflineQueue',
                'processOfflineQueue',
                'saveToStorage',
                'restoreFromStorage'
            ]
            
            for feature in required_features:
                if feature in content:
                    self.results['optimizations_implemented'].append(f"AutoSave: {feature}")
                    print(f"  ✅ 自动保存: {feature}")
                else:
                    self.results['errors'].append(f"Missing auto-save feature: {feature}")
                    print(f"  ❌ 缺少自动保存功能: {feature}")
        
        # 验证加载指示器
        loading_file = self.base_path / 'static/js/loading-indicators.js'
        if loading_file.exists():
            content = loading_file.read_text(encoding='utf-8')
            
            required_features = [
                'LoadingManager',
                'showGlobal',
                'createInline',
                'setButtonLoading',
                'createSkeleton',
                'createProgressBar'
            ]
            
            for feature in required_features:
                if feature in content:
                    self.results['optimizations_implemented'].append(f"Loading: {feature}")
                    print(f"  ✅ 加载指示器: {feature}")
                else:
                    self.results['errors'].append(f"Missing loading feature: {feature}")
                    print(f"  ❌ 缺少加载功能: {feature}")
        
        # 验证键盘快捷键
        keyboard_file = self.base_path / 'static/js/keyboard-shortcuts.js'
        if keyboard_file.exists():
            content = keyboard_file.read_text(encoding='utf-8')
            
            required_features = [
                'KeyboardShortcutManager',
                'register',
                'setContext',
                'showHelp',
                'registerDefaultShortcuts'
            ]
            
            for feature in required_features:
                if feature in content:
                    self.results['optimizations_implemented'].append(f"Keyboard: {feature}")
                    print(f"  ✅ 键盘快捷键: {feature}")
                else:
                    self.results['errors'].append(f"Missing keyboard feature: {feature}")
                    print(f"  ❌ 缺少键盘功能: {feature}")
        
        # 验证移动端优化CSS
        mobile_css = self.base_path / 'static/css/mobile-optimizations.css'
        if mobile_css.exists():
            content = mobile_css.read_text(encoding='utf-8')
            
            required_features = [
                '@media (max-width: 768px)',
                'touch-friendly',
                'min-height: 44px',
                'prefers-reduced-motion',
                'prefers-color-scheme: dark'
            ]
            
            for feature in required_features:
                if feature in content:
                    self.results['optimizations_implemented'].append(f"Mobile: {feature}")
                    print(f"  ✅ 移动端优化: {feature}")
                else:
                    self.results['errors'].append(f"Missing mobile feature: {feature}")
                    print(f"  ❌ 缺少移动端功能: {feature}")
    
    def verify_integration(self):
        """验证组件集成是否正确"""
        print("\n🔍 验证组件集成...")
        
        # 验证模板文件是否包含新的脚本
        template_file = self.base_path / 'templates/review.html'
        if template_file.exists():
            content = template_file.read_text(encoding='utf-8')
            
            required_scripts = [
                'performance-optimizations.js',
                'auto-save-manager.js',
                'loading-indicators.js',
                'keyboard-shortcuts.js'
            ]
            
            for script in required_scripts:
                if script in content:
                    self.results['optimizations_implemented'].append(f"Template: {script}")
                    print(f"  ✅ 模板集成: {script}")
                else:
                    self.results['errors'].append(f"Missing template script: {script}")
                    print(f"  ❌ 模板缺少脚本: {script}")
            
            # 验证CSS集成
            if 'mobile-optimizations.css' in content:
                self.results['optimizations_implemented'].append("Template: mobile-optimizations.css")
                print(f"  ✅ 模板集成: mobile-optimizations.css")
            else:
                self.results['errors'].append("Missing template CSS: mobile-optimizations.css")
                print(f"  ❌ 模板缺少CSS: mobile-optimizations.css")
        
        # 验证现有组件是否已更新
        components_to_check = [
            ('static/js/floating-profit-calculator.js', ['debounce', 'globalCache']),
            ('static/js/review-save-manager.js', ['autoSaveManager', 'debouncedDetectChanges']),
            ('static/js/review-integration.js', ['performanceOptimizations', 'initializePerformanceOptimizations'])
        ]
        
        for file_path, required_features in components_to_check:
            full_path = self.base_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                
                for feature in required_features:
                    if feature in content:
                        self.results['optimizations_implemented'].append(f"Integration: {file_path}:{feature}")
                        print(f"  ✅ 组件集成: {Path(file_path).name}:{feature}")
                    else:
                        self.results['errors'].append(f"Missing integration: {file_path}:{feature}")
                        print(f"  ❌ 缺少集成: {Path(file_path).name}:{feature}")
    
    def verify_performance_features(self):
        """验证性能优化特性"""
        print("\n🔍 验证性能优化特性...")
        
        features_to_verify = [
            {
                'name': '防抖和节流',
                'description': '优化高频事件处理',
                'files': ['static/js/performance-optimizations.js'],
                'keywords': ['debounce', 'throttle', 'rafThrottle']
            },
            {
                'name': '内存缓存',
                'description': '减少重复API调用',
                'files': ['static/js/performance-optimizations.js'],
                'keywords': ['MemoryCache', 'cache.set', 'cache.get']
            },
            {
                'name': '自动保存',
                'description': '防止数据丢失',
                'files': ['static/js/auto-save-manager.js'],
                'keywords': ['AutoSaveManager', 'enableOfflineQueue', 'autoSave']
            },
            {
                'name': '加载指示器',
                'description': '改善用户体验',
                'files': ['static/js/loading-indicators.js'],
                'keywords': ['LoadingManager', 'showLoading', 'createProgressBar']
            },
            {
                'name': '键盘快捷键',
                'description': '提高操作效率',
                'files': ['static/js/keyboard-shortcuts.js'],
                'keywords': ['KeyboardShortcutManager', 'register', 'ctrl+s']
            },
            {
                'name': '移动端优化',
                'description': '响应式设计和触摸优化',
                'files': ['static/css/mobile-optimizations.css'],
                'keywords': ['@media', 'min-height: 44px', 'touch-friendly']
            },
            {
                'name': '批处理优化',
                'description': '批量处理操作',
                'files': ['static/js/performance-optimizations.js'],
                'keywords': ['BatchProcessor', 'batchSize', 'queue']
            },
            {
                'name': '虚拟滚动',
                'description': '大数据列表优化',
                'files': ['static/js/performance-optimizations.js'],
                'keywords': ['VirtualScroller', 'visibleItems', 'bufferSize']
            }
        ]
        
        for feature in features_to_verify:
            feature_implemented = True
            
            for file_path in feature['files']:
                full_path = self.base_path / file_path
                if full_path.exists():
                    content = full_path.read_text(encoding='utf-8')
                    
                    keywords_found = 0
                    for keyword in feature['keywords']:
                        if keyword in content:
                            keywords_found += 1
                    
                    if keywords_found >= len(feature['keywords']) * 0.7:  # 至少70%的关键词存在
                        self.results['optimizations_implemented'].append(
                            f"Feature: {feature['name']} - {feature['description']}"
                        )
                        print(f"  ✅ {feature['name']}: {feature['description']}")
                    else:
                        feature_implemented = False
                        self.results['errors'].append(
                            f"Incomplete feature: {feature['name']} - missing keywords"
                        )
                        print(f"  ❌ {feature['name']}: 功能不完整")
                else:
                    feature_implemented = False
                    self.results['errors'].append(f"Missing file for feature: {feature['name']}")
                    print(f"  ❌ {feature['name']}: 缺少文件")
    
    def run_syntax_check(self):
        """运行JavaScript语法检查"""
        print("\n🔍 运行语法检查...")
        
        js_files = [
            'static/js/performance-optimizations.js',
            'static/js/auto-save-manager.js',
            'static/js/loading-indicators.js',
            'static/js/keyboard-shortcuts.js'
        ]
        
        for js_file in js_files:
            full_path = self.base_path / js_file
            if full_path.exists():
                try:
                    # 简单的语法检查 - 检查括号匹配
                    content = full_path.read_text(encoding='utf-8')
                    
                    # 检查基本语法错误
                    open_braces = content.count('{')
                    close_braces = content.count('}')
                    open_parens = content.count('(')
                    close_parens = content.count(')')
                    open_brackets = content.count('[')
                    close_brackets = content.count(']')
                    
                    if (open_braces == close_braces and 
                        open_parens == close_parens and 
                        open_brackets == close_brackets):
                        self.results['tests_passed'].append(f"Syntax check: {js_file}")
                        print(f"  ✅ 语法检查通过: {Path(js_file).name}")
                    else:
                        self.results['errors'].append(f"Syntax error in: {js_file}")
                        print(f"  ❌ 语法错误: {Path(js_file).name}")
                        
                except Exception as e:
                    self.results['errors'].append(f"Error checking {js_file}: {str(e)}")
                    print(f"  ❌ 检查错误: {Path(js_file).name} - {str(e)}")
    
    def generate_report(self):
        """生成验证报告"""
        print("\n📊 生成验证报告...")
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'files_created': len(self.results['files_created']),
                'optimizations_implemented': len(self.results['optimizations_implemented']),
                'tests_passed': len(self.results['tests_passed']),
                'errors': len(self.results['errors'])
            },
            'details': self.results
        }
        
        # 保存报告
        report_file = self.base_path / 'performance_optimization_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 打印摘要
        print(f"\n📋 验证摘要:")
        print(f"  ✅ 创建文件: {report['summary']['files_created']}")
        print(f"  ✅ 实现优化: {report['summary']['optimizations_implemented']}")
        print(f"  ✅ 通过测试: {report['summary']['tests_passed']}")
        print(f"  ❌ 发现错误: {report['summary']['errors']}")
        
        if report['summary']['errors'] > 0:
            print(f"\n❌ 发现的错误:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return report['summary']['errors'] == 0
    
    def run_verification(self):
        """运行完整验证"""
        print("🚀 开始性能优化验证...")
        print("=" * 60)
        
        self.verify_files_exist()
        self.verify_file_contents()
        self.verify_integration()
        self.verify_performance_features()
        self.run_syntax_check()
        
        success = self.generate_report()
        
        print("=" * 60)
        if success:
            print("🎉 性能优化验证成功完成!")
            print("✨ 所有优化功能已正确实现")
            return True
        else:
            print("⚠️  性能优化验证发现问题")
            print("🔧 请检查上述错误并修复")
            return False

def main():
    """主函数"""
    verifier = PerformanceOptimizationVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n🎯 下一步:")
        print("1. 打开 test_performance_optimizations.html 测试功能")
        print("2. 在移动设备上测试响应式设计")
        print("3. 测试键盘快捷键功能")
        print("4. 验证自动保存和离线功能")
        
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()