#!/usr/bin/env python3
"""
临时添加调试路由到主应用
"""

# 读取调试HTML内容
with open('debug_analytics_detailed.html', 'r', encoding='utf-8') as f:
    debug_html = f.read()

# 创建临时路由文件
route_code = f'''
from flask import render_template_string

@frontend_bp.route('/debug-analytics')
def debug_analytics():
    """调试Analytics页面"""
    return render_template_string("""{debug_html}""")
'''

# 将路由添加到routes.py
with open('routes.py', 'r', encoding='utf-8') as f:
    routes_content = f.read()

# 检查是否已经添加了调试路由
if 'debug-analytics' not in routes_content:
    # 在文件末尾添加调试路由
    with open('routes.py', 'a', encoding='utf-8') as f:
        f.write('\n\n# 临时调试路由\n')
        f.write(route_code)
    
    print("✅ 调试路由已添加到 routes.py")
    print("📍 访问: http://localhost:5001/debug-analytics")
    print("⚠️  请重启服务器以使路由生效")
else:
    print("ℹ️  调试路由已存在")
    print("📍 访问: http://localhost:5001/debug-analytics")