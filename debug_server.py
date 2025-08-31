#!/usr/bin/env python3
"""
简单的调试服务器，用于测试前端问题
"""

from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

# 读取调试HTML文件内容
with open('debug_analytics_detailed.html', 'r', encoding='utf-8') as f:
    DEBUG_HTML = f.read()

@app.route('/debug')
def debug_page():
    """调试页面"""
    return DEBUG_HTML

@app.route('/test-api')
def test_api():
    """测试主服务器的API"""
    try:
        response = requests.get('http://localhost:5001/api/analytics/overview', timeout=10)
        return jsonify({
            'status_code': response.status_code,
            'data': response.json() if response.status_code == 200 else response.text
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 启动调试服务器...")
    print("📍 调试页面: http://localhost:5002/debug")
    print("📍 API测试: http://localhost:5002/test-api")
    print("⚠️  请确保主服务器运行在 localhost:5001")
    
    app.run(host='localhost', port=5002, debug=True)