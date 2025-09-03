#!/usr/bin/env python3
"""
测试排序修复的脚本
"""
import webbrowser
import time

def main():
    print("=== 历史交易排序修复测试 ===\n")
    
    print("1. 请在浏览器中访问: http://localhost:5001/historical-trades")
    print("2. 打开浏览器开发者工具 (F12)")
    print("3. 切换到 Console 标签页")
    print("4. 尝试更改排序字段和排序方向")
    print("5. 观察控制台输出的调试信息")
    
    print("\n预期看到的调试信息:")
    print("- '排序字段变化: [字段名]'")
    print("- '排序方向变化: [方向]'")
    print("- '=== applyFilters 开始 ==='")
    print("- '应用筛选和排序: {...}'")
    print("- '=== loadHistoricalTrades 开始 ==='")
    print("- '请求参数: {...}'")
    print("- 'API响应: {...}'")
    
    print("\n如果看不到这些信息，说明:")
    print("- JavaScript文件可能没有正确加载")
    print("- 事件监听器可能没有正确绑定")
    print("- 可能存在JavaScript错误")
    
    print("\n故障排除步骤:")
    print("1. 检查Network标签页，确认所有JS文件都成功加载")
    print("2. 检查Console标签页，查看是否有JavaScript错误")
    print("3. 在Console中输入 'window.historicalTradesManager' 检查对象是否存在")
    print("4. 在Console中输入 'window.apiClient' 检查API客户端是否存在")
    
    # 尝试打开浏览器
    try:
        print("\n正在尝试打开浏览器...")
        webbrowser.open('http://localhost:5001/historical-trades')
        print("✅ 浏览器已打开")
    except Exception as e:
        print(f"❌ 无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:5001/historical-trades")
    
    print("\n测试完成后，请报告:")
    print("1. 排序功能是否正常工作")
    print("2. 控制台是否显示了预期的调试信息")
    print("3. 是否有任何JavaScript错误")

if __name__ == "__main__":
    main()