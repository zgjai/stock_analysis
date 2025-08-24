#!/usr/bin/env python3
"""
最终JavaScript测试和修复验证
"""

import subprocess
import os
import time

def start_test_server():
    """启动测试服务器"""
    try:
        # 检查是否已有服务器在运行
        result = subprocess.run(['lsof', '-i', ':5001'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 检测到服务器已在端口5001运行")
            return True
        
        print("🚀 启动测试服务器...")
        # 启动Flask应用
        process = subprocess.Popen(['python', 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查服务器是否成功启动
        result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:5001'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip() == '200':
            print("✅ 测试服务器启动成功")
            return True
        else:
            print(f"❌ 服务器启动失败，HTTP状态码: {result.stdout.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ 启动服务器时出错: {e}")
        return False

def test_javascript_loading():
    """测试JavaScript文件加载"""
    js_files = [
        '/static/js/emergency-syntax-fix.js',
        '/static/js/utils.js',
        '/static/js/review-emergency-fix.js'
    ]
    
    print("🔍 测试JavaScript文件加载...")
    
    for js_file in js_files:
        try:
            result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
                                   f'http://localhost:5001{js_file}'], 
                                  capture_output=True, text=True)
            
            status_code = result.stdout.strip()
            if status_code == '200':
                print(f"  ✅ {js_file} 加载成功")
            else:
                print(f"  ❌ {js_file} 加载失败 (HTTP {status_code})")
                return False
        except Exception as e:
            print(f"  ❌ {js_file} 测试异常: {e}")
            return False
    
    return True

def test_review_page():
    """测试复盘页面"""
    print("🔍 测试复盘页面...")
    
    try:
        result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
                               'http://localhost:5001/review'], 
                              capture_output=True, text=True)
        
        status_code = result.stdout.strip()
        if status_code == '200':
            print("  ✅ 复盘页面加载成功")
            return True
        else:
            print(f"  ❌ 复盘页面加载失败 (HTTP {status_code})")
            return False
    except Exception as e:
        print(f"  ❌ 复盘页面测试异常: {e}")
        return False

def create_browser_test_script():
    """创建浏览器测试脚本"""
    test_script = '''
// 浏览器控制台测试脚本
// 复制粘贴到浏览器控制台中运行

console.log("🔍 开始JavaScript修复验证测试...");

// 测试1: 检查全局变量是否正确加载
const globalVars = ['Validators', 'Formatters', 'DOMUtils', 'DataUtils'];
let passedTests = 0;
let totalTests = 0;

globalVars.forEach(varName => {
    totalTests++;
    if (typeof window[varName] !== 'undefined') {
        console.log(`✅ ${varName} 加载成功`);
        passedTests++;
    } else {
        console.error(`❌ ${varName} 未加载`);
    }
});

// 测试2: 检查紧急修复脚本
totalTests++;
if (typeof window.fixAsyncSyntax === 'function') {
    console.log("✅ 紧急修复脚本加载成功");
    passedTests++;
} else {
    console.error("❌ 紧急修复脚本未加载");
}

// 测试3: 测试股票代码验证功能
if (window.Validators && window.Validators.stockCode) {
    totalTests++;
    try {
        const test1 = window.Validators.stockCode('000001');
        const test2 = window.Validators.stockCode('invalid');
        
        if (test1 === true && test2 === false) {
            console.log("✅ 股票代码验证功能正常");
            passedTests++;
        } else {
            console.error("❌ 股票代码验证功能异常");
        }
    } catch (e) {
        console.error("❌ 股票代码验证测试异常:", e);
    }
}

// 测试4: 检查是否还有语法错误
totalTests++;
let hasErrors = false;
const originalError = console.error;
console.error = function(...args) {
    const message = args.join(' ');
    if (message.includes('SyntaxError') || message.includes('already been declared')) {
        hasErrors = true;
    }
    originalError.apply(console, args);
};

setTimeout(() => {
    if (!hasErrors) {
        console.log("✅ 未检测到语法错误");
        passedTests++;
    } else {
        console.error("❌ 仍有语法错误");
    }
    
    // 显示最终结果
    console.log(`\\n📊 测试结果: ${passedTests}/${totalTests} 项通过`);
    
    if (passedTests === totalTests) {
        console.log("🎉 所有测试通过！JavaScript修复成功！");
    } else {
        console.log("⚠️ 部分测试失败，可能需要进一步检查");
    }
}, 2000);

console.log("\\n请等待2秒查看完整测试结果...");
'''
    
    with open('browser_test_script.js', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("📝 浏览器测试脚本已创建: browser_test_script.js")
    return True

def main():
    """主测试流程"""
    print("🧪 开始最终JavaScript修复验证...\n")
    
    # 创建浏览器测试脚本
    create_browser_test_script()
    
    # 检查服务器状态
    if not start_test_server():
        print("❌ 无法启动测试服务器，跳过网络测试")
        print("\n📋 手动测试步骤:")
        print("1. 启动Flask应用: python app.py")
        print("2. 访问: http://localhost:5000/review")
        print("3. 打开浏览器开发者工具")
        print("4. 复制browser_test_script.js内容到控制台运行")
        return False
    
    # 测试JavaScript文件加载
    if not test_javascript_loading():
        print("❌ JavaScript文件加载测试失败")
        return False
    
    # 测试复盘页面
    if not test_review_page():
        print("❌ 复盘页面测试失败")
        return False
    
    print("\n🎉 服务器端测试全部通过！")
    print("\n📋 接下来请进行浏览器测试:")
    print("1. 访问: http://localhost:5001/review")
    print("2. 打开浏览器开发者工具 (F12)")
    print("3. 切换到Console标签")
    print("4. 复制browser_test_script.js的内容到控制台运行")
    print("5. 查看测试结果")
    print("\n如果浏览器测试通过，说明JavaScript修复完全成功！")
    
    return True

if __name__ == '__main__':
    main()