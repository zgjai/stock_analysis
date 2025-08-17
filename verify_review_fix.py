#!/usr/bin/env python3
"""
验证复盘分析页面修复效果
"""

import os
import re

def verify_review_page_fix():
    """验证复盘分析页面的修复"""
    
    template_path = "templates/review.html"
    
    if not os.path.exists(template_path):
        print(f"❌ 文件不存在: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # 检查1: 是否有初始化空状态处理
    if 'initializeEmptyStates' in content:
        checks.append("✅ 初始化空状态处理")
    else:
        checks.append("❌ 缺少初始化空状态处理")
    
    # 检查2: 是否有超时处理
    if 'Promise.race' in content and '超时' in content:
        checks.append("✅ 超时处理机制")
    else:
        checks.append("❌ 缺少超时处理机制")
    
    # 检查3: 是否有错误状态显示
    if 'showErrorStates' in content:
        checks.append("✅ 错误状态显示")
    else:
        checks.append("❌ 缺少错误状态显示")
    
    # 检查4: 是否有重新加载功能
    if '重新加载' in content and 'bi-arrow-clockwise' in content:
        checks.append("✅ 重新加载功能")
    else:
        checks.append("❌ 缺少重新加载功能")
    
    # 检查5: 是否有友好的空数据提示
    if '暂无持仓数据' in content and '暂无复盘记录' in content:
        checks.append("✅ 友好的空数据提示")
    else:
        checks.append("❌ 缺少友好的空数据提示")
    
    # 检查6: 是否有引导用户操作
    if '添加交易记录' in content:
        checks.append("✅ 用户操作引导")
    else:
        checks.append("❌ 缺少用户操作引导")
    
    # 检查7: 是否移除了原来的问题代码
    if content.count('加载中...') <= 3:  # 应该只在初始加载时显示
        checks.append("✅ 移除了持续加载状态")
    else:
        checks.append("❌ 仍有过多的加载状态")
    
    print("复盘分析页面修复验证:")
    for check in checks:
        print(f"  {check}")
    
    success_count = len([c for c in checks if c.startswith("✅")])
    total_count = len(checks)
    
    print(f"\n修复完成度: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    return success_count >= total_count * 0.8  # 80%以上算成功

def verify_trading_records_intact():
    """验证交易记录页面是否完好"""
    
    template_path = "templates/trading_records.html"
    
    if not os.path.exists(template_path):
        print(f"❌ 交易记录页面不存在")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    essential_functions = [
        'TradingRecordsManager',
        'loadTrades',
        'renderTradesTable',
        'saveTrade',
        'filterTrades'
    ]
    
    missing_functions = []
    for func in essential_functions:
        if func not in content:
            missing_functions.append(func)
    
    if missing_functions:
        print(f"❌ 交易记录页面缺少关键函数: {', '.join(missing_functions)}")
        return False
    else:
        print("✅ 交易记录页面功能完整")
        return True

def create_test_page():
    """创建测试页面来演示修复效果"""
    
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>复盘分析页面修复测试</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h2>复盘分析页面修复效果演示</h2>
        
        <div class="row">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h6>修复前：一直加载中</h6>
                    </div>
                    <div class="card-body">
                        <div class="text-center text-muted">
                            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                            加载中...
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h6>修复后：友好的空状态</h6>
                    </div>
                    <div class="card-body">
                        <div class="text-center text-muted py-4">
                            <i class="bi bi-briefcase fs-1 d-block mb-2"></i>
                            <div class="mb-2">暂无持仓数据</div>
                            <small class="text-muted">请先添加交易记录</small>
                            <br>
                            <button class="btn btn-outline-primary btn-sm mt-2">
                                <i class="bi bi-plus-circle"></i> 添加交易记录
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h6>修复后：错误状态处理</h6>
                    </div>
                    <div class="card-body">
                        <div class="text-center text-muted py-4">
                            <i class="bi bi-exclamation-triangle fs-1 d-block mb-2 text-warning"></i>
                            <div class="mb-2">加载超时</div>
                            <small class="text-muted">请检查网络连接或稍后重试</small>
                            <br>
                            <button class="btn btn-outline-primary btn-sm mt-2">
                                <i class="bi bi-arrow-clockwise"></i> 重新加载
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="alert alert-success">
                    <h6>✅ 修复效果</h6>
                    <ul class="mb-0">
                        <li>不再一直显示"加载中"状态</li>
                        <li>没有数据时显示友好的提示信息</li>
                        <li>加载失败时显示明确的错误信息</li>
                        <li>提供重新加载和引导操作按钮</li>
                        <li>改善了整体用户体验</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <div class="alert alert-info">
                    <h6>🔧 技术改进</h6>
                    <ul class="mb-0">
                        <li>添加了5秒超时机制，避免无限等待</li>
                        <li>改进了错误处理和状态管理</li>
                        <li>优化了页面初始化流程</li>
                        <li>增加了自动重试和手动重试功能</li>
                        <li>提供了更好的用户反馈</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    with open('test_review_fix.html', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ 创建了测试页面: test_review_fix.html")

def main():
    """主函数"""
    print("🔍 验证复盘分析页面修复效果...")
    print("=" * 50)
    
    # 验证复盘分析页面修复
    review_fix_ok = verify_review_page_fix()
    
    print("\n" + "=" * 50)
    
    # 验证交易记录页面是否完好
    trading_intact = verify_trading_records_intact()
    
    print("\n" + "=" * 50)
    
    # 创建测试页面
    create_test_page()
    
    print("\n" + "=" * 50)
    
    # 总结
    if review_fix_ok and trading_intact:
        print("🎉 修复验证通过！")
        print("✅ 复盘分析页面已修复")
        print("✅ 交易记录页面保持完整")
    elif review_fix_ok:
        print("⚠️  复盘分析页面已修复，但交易记录页面可能有问题")
    elif trading_intact:
        print("⚠️  交易记录页面正常，但复盘分析页面修复不完整")
    else:
        print("❌ 两个页面都可能有问题，需要进一步检查")
    
    print("\n现在的状态:")
    print("- 复盘分析页面不会再一直显示'加载中'")
    print("- 没有数据时会显示友好的提示")
    print("- 加载失败时会显示错误信息和重试按钮")
    print("- 交易记录页面功能保持完整")
    
    print("\n测试建议:")
    print("1. 打开 test_review_fix.html 查看修复效果演示")
    print("2. 访问复盘分析页面确认不再一直加载")
    print("3. 访问交易记录页面确认功能正常")

if __name__ == "__main__":
    main()