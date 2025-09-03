#!/usr/bin/env python3
"""
浏览器测试 selectMonth 修复
"""

import time
import subprocess
import webbrowser
from pathlib import Path

def start_server():
    """启动开发服务器"""
    print("🚀 启动开发服务器...")
    try:
        # 尝试启动Flask应用
        process = subprocess.Popen(['python', 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("   ✅ 服务器启动成功")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ 服务器启动失败: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"   ❌ 启动服务器时出错: {e}")
        return None

def open_test_pages():
    """打开测试页面"""
    print("\n🌐 打开测试页面...")
    
    base_url = "http://localhost:5000"
    test_urls = [
        f"{base_url}/analytics",
        f"{base_url}/static/../test_selectMonth_fix.html"
    ]
    
    for url in test_urls:
        try:
            print(f"   📖 打开: {url}")
            webbrowser.open(url)
            time.sleep(1)
        except Exception as e:
            print(f"   ❌ 无法打开 {url}: {e}")

def create_browser_test_instructions():
    """创建浏览器测试说明"""
    instructions = """
# 浏览器测试说明

## 测试步骤

### 1. Analytics 页面测试
1. 打开 http://localhost:5000/analytics
2. 滚动到"月度期望收益对比"部分
3. 点击任意月份项目
4. 检查是否出现错误

### 2. 控制台检查
1. 按 F12 打开开发者工具
2. 切换到 Console 标签
3. 查看是否有以下日志：
   - "期望对比管理器初始化成功"
   - 没有 "Cannot read properties of undefined" 错误

### 3. 功能测试
1. 点击月份列表中的项目
2. 检查右侧是否显示对比详情
3. 验证数据加载是否正常

### 4. 测试页面
1. 打开 test_selectMonth_fix.html
2. 点击各个测试按钮
3. 查看测试结果

## 预期结果

✅ 正常情况:
- 月份点击正常响应
- 控制台显示初始化成功日志
- 没有JavaScript错误
- 对比详情正常显示

❌ 异常情况:
- 点击月份无响应
- 控制台显示错误
- selectMonth 相关错误

## 故障排除

如果仍有问题:
1. 检查网络连接
2. 清除浏览器缓存
3. 重启服务器
4. 检查JavaScript文件是否正确加载
"""
    
    with open("BROWSER_TEST_INSTRUCTIONS.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("   ✅ 已创建浏览器测试说明: BROWSER_TEST_INSTRUCTIONS.md")

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 selectMonth 修复浏览器测试")
    print("=" * 60)
    
    # 创建测试说明
    create_browser_test_instructions()
    
    # 检查必要文件
    required_files = ["app.py", "templates/analytics.html", "static/js/expectation-comparison-manager.js"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ 缺少必要文件: {missing_files}")
        return
    
    print("\n📋 测试准备:")
    print("1. ✅ 修复文件已就位")
    print("2. ✅ 测试说明已创建")
    
    # 询问是否启动服务器
    response = input("\n🤔 是否启动开发服务器进行测试? (y/n): ").lower().strip()
    
    if response == 'y':
        server_process = start_server()
        
        if server_process:
            try:
                # 打开测试页面
                open_test_pages()
                
                print("\n" + "=" * 60)
                print("🎯 测试进行中...")
                print("📖 请在浏览器中按照说明进行测试")
                print("⌨️  按 Ctrl+C 停止服务器")
                print("=" * 60)
                
                # 等待用户停止
                server_process.wait()
                
            except KeyboardInterrupt:
                print("\n\n🛑 停止服务器...")
                server_process.terminate()
                server_process.wait()
                print("   ✅ 服务器已停止")
        
    else:
        print("\n📝 手动测试:")
        print("1. 启动你的开发服务器")
        print("2. 打开 http://localhost:5000/analytics")
        print("3. 按照 BROWSER_TEST_INSTRUCTIONS.md 中的说明进行测试")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()