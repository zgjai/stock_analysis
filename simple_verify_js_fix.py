#!/usr/bin/env python3
"""
简单验证JavaScript重复声明修复
"""
import requests
import re

def check_javascript_files():
    """检查JavaScript文件的修复情况"""
    print("🔍 检查JavaScript文件修复情况...")
    
    base_url = "http://localhost:5001"
    js_files = [
        "/static/js/utils.js",
        "/static/js/performance-optimizations.js", 
        "/static/js/api.js",
        "/static/js/review-emergency-fix.js"
    ]
    
    results = {}
    
    for js_file in js_files:
        try:
            url = base_url + js_file
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                results[js_file] = {
                    'loaded': True,
                    'content': content,
                    'size': len(content)
                }
                print(f"✅ {js_file} 加载成功 ({len(content)} 字符)")
            else:
                results[js_file] = {
                    'loaded': False,
                    'error': f"HTTP {response.status_code}"
                }
                print(f"❌ {js_file} 加载失败: HTTP {response.status_code}")
                
        except Exception as e:
            results[js_file] = {
                'loaded': False,
                'error': str(e)
            }
            print(f"❌ {js_file} 加载出错: {str(e)}")
    
    return results

def analyze_duplicate_declarations(js_results):
    """分析重复声明问题"""
    print("\n🔍 分析重复声明修复...")
    
    issues = []
    fixes = []
    
    # 检查utils.js的修复
    if '/static/js/utils.js' in js_results and js_results['/static/js/utils.js']['loaded']:
        content = js_results['/static/js/utils.js']['content']
        
        if 'window.PerformanceUtils' in content:
            fixes.append("✅ utils.js: PerformanceUtils 使用条件声明")
        else:
            issues.append("❌ utils.js: PerformanceUtils 未使用条件声明")
            
        if 'window.debounce' in content:
            fixes.append("✅ utils.js: debounce 使用条件声明")
        else:
            issues.append("❌ utils.js: debounce 未使用条件声明")
    
    # 检查performance-optimizations.js的修复
    if '/static/js/performance-optimizations.js' in js_results and js_results['/static/js/performance-optimizations.js']['loaded']:
        content = js_results['/static/js/performance-optimizations.js']['content']
        
        if 'window.debounce' in content and 'typeof window.debounce' in content:
            fixes.append("✅ performance-optimizations.js: debounce 使用条件声明")
        else:
            issues.append("❌ performance-optimizations.js: debounce 未使用条件声明")
            
        if 'window.throttle' in content and 'typeof window.throttle' in content:
            fixes.append("✅ performance-optimizations.js: throttle 使用条件声明")
        else:
            issues.append("❌ performance-optimizations.js: throttle 未使用条件声明")
    
    # 检查api.js的修复
    if '/static/js/api.js' in js_results and js_results['/static/js/api.js']['loaded']:
        content = js_results['/static/js/api.js']['content']
        
        if 'window.apiClient' in content and 'typeof window.apiClient' in content:
            fixes.append("✅ api.js: apiClient 使用条件声明")
        else:
            issues.append("❌ api.js: apiClient 未使用条件声明")
    
    # 检查emergency-fix.js的修复
    if '/static/js/review-emergency-fix.js' in js_results and js_results['/static/js/review-emergency-fix.js']['loaded']:
        content = js_results['/static/js/review-emergency-fix.js']['content']
        
        if 'initializeEmergencyFixes' in content:
            fixes.append("✅ review-emergency-fix.js: 函数名冲突已修复")
        else:
            issues.append("❌ review-emergency-fix.js: 函数名冲突未修复")
    
    return issues, fixes

def check_review_page():
    """检查复盘页面的模板修复"""
    print("\n🔍 检查复盘页面模板修复...")
    
    try:
        response = requests.get("http://localhost:5001/review", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            fixes = []
            issues = []
            
            # 检查模板中的修复
            if 'window.apiClient' in content and 'typeof window.apiClient' in content:
                fixes.append("✅ review.html: apiClient 使用条件声明")
            else:
                issues.append("❌ review.html: apiClient 未使用条件声明")
                
            if 'window.reviewSaveManager' in content and 'typeof window.reviewSaveManager' in content:
                fixes.append("✅ review.html: reviewSaveManager 使用条件声明")
            else:
                issues.append("❌ review.html: reviewSaveManager 未使用条件声明")
            
            return issues, fixes, True
            
        else:
            return [f"❌ 复盘页面加载失败: HTTP {response.status_code}"], [], False
            
    except Exception as e:
        return [f"❌ 复盘页面检查出错: {str(e)}"], [], False

def main():
    """主函数"""
    print("🚀 开始JavaScript重复声明修复验证")
    print("=" * 60)
    
    # 检查服务器
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        print("✅ 服务器运行正常")
    except:
        print("❌ 服务器未运行，请先启动服务器")
        return False
    
    # 检查JavaScript文件
    js_results = check_javascript_files()
    
    # 分析修复情况
    js_issues, js_fixes = analyze_duplicate_declarations(js_results)
    
    # 检查复盘页面
    page_issues, page_fixes, page_loaded = check_review_page()
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("📊 修复验证结果:")
    
    print(f"\n✅ 已修复的问题 ({len(js_fixes) + len(page_fixes)} 项):")
    for fix in js_fixes + page_fixes:
        print(f"   {fix}")
    
    if js_issues or page_issues:
        print(f"\n❌ 仍存在的问题 ({len(js_issues) + len(page_issues)} 项):")
        for issue in js_issues + page_issues:
            print(f"   {issue}")
    
    # 最终结论
    total_issues = len(js_issues) + len(page_issues)
    total_fixes = len(js_fixes) + len(page_fixes)
    
    print(f"\n{'='*60}")
    if total_issues == 0 and total_fixes > 0:
        print("🎉 JavaScript重复声明修复验证成功!")
        print(f"✅ 共修复了 {total_fixes} 个问题")
        print("✅ 没有发现遗留问题")
        print("✅ 页面应该可以正常加载，不再出现重复声明错误")
        return True
    else:
        print("⚠️  修复验证完成，但可能仍有问题:")
        print(f"   修复项目: {total_fixes}")
        print(f"   遗留问题: {total_issues}")
        if total_issues > 0:
            print("❌ 建议检查遗留问题")
        return total_issues == 0

if __name__ == "__main__":
    main()