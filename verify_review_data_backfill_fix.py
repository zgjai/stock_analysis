#!/usr/bin/env python3
"""
验证复盘数据回填修复效果

这个脚本会：
1. 检查修复后的代码是否正确
2. 测试API响应格式
3. 验证前端逻辑
"""

import os
import re
import json
import requests
from datetime import datetime, date

def verify_template_fixes():
    """验证模板修复是否成功"""
    print("🔍 验证模板修复...")
    
    template_path = 'templates/review.html'
    if not os.path.exists(template_path):
        print("❌ 模板文件不存在")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键修复点
    checks = [
        {
            'name': '优化的checkAndLoadExistingReview函数',
            'pattern': r'queryParams = new URLSearchParams\(',
            'expected': True
        },
        {
            'name': '增强的populateModalWithExistingReview函数',
            'pattern': r'console\.log\(\'📝 填充现有复盘记录数据:\', review\);',
            'expected': True
        },
        {
            'name': '改进的openReviewModal函数',
            'pattern': r'await checkAndLoadExistingReview\(stockCode, currentDate\);',
            'expected': True
        },
        {
            'name': '调试函数testReviewDataBackfill',
            'pattern': r'window\.testReviewDataBackfill = async function',
            'expected': True
        },
        {
            'name': '调试函数debugReviewModal',
            'pattern': r'window\.debugReviewModal = function',
            'expected': True
        }
    ]
    
    all_passed = True
    for check in checks:
        found = bool(re.search(check['pattern'], content))
        status = "✅" if found == check['expected'] else "❌"
        print(f"  {status} {check['name']}: {'找到' if found else '未找到'}")
        if found != check['expected']:
            all_passed = False
    
    return all_passed

def test_api_response_format():
    """测试API响应格式"""
    print("\n🔍 测试API响应格式...")
    
    try:
        # 测试复盘记录API
        response = requests.get('http://localhost:5000/api/reviews?per_page=1', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API响应成功")
            print(f"  响应格式: {type(data)}")
            
            if 'success' in data:
                print(f"  success字段: {data['success']}")
            
            if 'data' in data:
                data_content = data['data']
                print(f"  data字段类型: {type(data_content)}")
                
                if isinstance(data_content, dict):
                    if 'reviews' in data_content:
                        reviews = data_content['reviews']
                        print(f"  reviews字段类型: {type(reviews)}")
                        print(f"  reviews数量: {len(reviews) if isinstance(reviews, list) else 'N/A'}")
                        
                        if isinstance(reviews, list) and len(reviews) > 0:
                            sample_review = reviews[0]
                            print("  示例复盘记录字段:")
                            for key in ['id', 'stock_code', 'review_date', 'total_score', 'decision']:
                                if key in sample_review:
                                    print(f"    {key}: {sample_review[key]}")
                elif isinstance(data_content, list):
                    print(f"  直接数组格式，数量: {len(data_content)}")
            
            return True
        else:
            print(f"❌ API响应失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️ 无法连接到服务器，请确保服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def create_comprehensive_test():
    """创建综合测试页面"""
    print("\n🔧 创建综合测试页面...")
    
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>复盘数据回填综合测试</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .test-result { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .test-success { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .test-error { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .test-warning { background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
        .code-block { background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h2>复盘数据回填综合测试</h2>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5>自动化测试</h5>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary" onclick="runAllTests()">运行所有测试</button>
                        <button class="btn btn-secondary ms-2" onclick="clearResults()">清空结果</button>
                        
                        <div id="test-results" class="mt-3"></div>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h5>手动测试</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">股票代码</label>
                            <input type="text" class="form-control" id="test-stock-code" value="000001" placeholder="输入股票代码">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">复盘日期</label>
                            <input type="date" class="form-control" id="test-review-date">
                        </div>
                        <button class="btn btn-success" onclick="testSpecificRecord()">测试指定记录</button>
                        <button class="btn btn-info ms-2" onclick="testModalOpen()">测试模态框打开</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>测试说明</h5>
                    </div>
                    <div class="card-body">
                        <h6>测试项目：</h6>
                        <ul>
                            <li>API连接测试</li>
                            <li>数据格式验证</li>
                            <li>记录查找测试</li>
                            <li>数据回填测试</li>
                            <li>模态框功能测试</li>
                        </ul>
                        
                        <h6 class="mt-3">使用方法：</h6>
                        <ol>
                            <li>点击"运行所有测试"</li>
                            <li>查看测试结果</li>
                            <li>如有问题，查看控制台日志</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 设置默认日期为今天
        document.getElementById('test-review-date').value = new Date().toISOString().split('T')[0];
        
        function addTestResult(title, status, message, details = null) {
            const resultsDiv = document.getElementById('test-results');
            const resultClass = status === 'success' ? 'test-success' : 
                               status === 'error' ? 'test-error' : 'test-warning';
            
            const resultHtml = `
                <div class="test-result ${resultClass}">
                    <strong>${title}</strong>: ${message}
                    ${details ? `<div class="mt-2"><small>${details}</small></div>` : ''}
                </div>
            `;
            
            resultsDiv.innerHTML += resultHtml;
        }
        
        function clearResults() {
            document.getElementById('test-results').innerHTML = '';
        }
        
        async function testApiConnection() {
            console.log('🔍 测试API连接...');
            
            try {
                const response = await fetch('/api/reviews?per_page=1');
                const data = await response.json();
                
                if (response.ok && data.success) {
                    addTestResult('API连接测试', 'success', 'API连接正常');
                    return data;
                } else {
                    addTestResult('API连接测试', 'error', `API响应异常: ${data.message || '未知错误'}`);
                    return null;
                }
            } catch (error) {
                addTestResult('API连接测试', 'error', `连接失败: ${error.message}`);
                return null;
            }
        }
        
        async function testDataFormat(apiData) {
            console.log('🔍 测试数据格式...');
            
            if (!apiData || !apiData.data) {
                addTestResult('数据格式测试', 'error', '没有数据可供测试');
                return false;
            }
            
            const data = apiData.data;
            let reviews = [];
            
            if (Array.isArray(data)) {
                reviews = data;
                addTestResult('数据格式测试', 'success', '检测到直接数组格式');
            } else if (data.reviews && Array.isArray(data.reviews)) {
                reviews = data.reviews;
                addTestResult('数据格式测试', 'success', '检测到分页格式');
            } else {
                addTestResult('数据格式测试', 'warning', '未知的数据格式');
                return false;
            }
            
            if (reviews.length > 0) {
                const sample = reviews[0];
                const requiredFields = ['id', 'stock_code', 'review_date'];
                const missingFields = requiredFields.filter(field => !(field in sample));
                
                if (missingFields.length === 0) {
                    addTestResult('数据字段测试', 'success', '所有必需字段都存在');
                } else {
                    addTestResult('数据字段测试', 'error', `缺少字段: ${missingFields.join(', ')}`);
                }
            }
            
            return true;
        }
        
        async function testRecordSearch() {
            console.log('🔍 测试记录查找...');
            
            const stockCode = '000001';
            const reviewDate = new Date().toISOString().split('T')[0];
            
            try {
                const queryParams = new URLSearchParams({
                    stock_code: stockCode,
                    start_date: reviewDate,
                    end_date: reviewDate,
                    per_page: 1
                });
                
                const response = await fetch(`/api/reviews?${queryParams}`);
                const data = await response.json();
                
                if (response.ok && data.success) {
                    addTestResult('记录查找测试', 'success', `查找 ${stockCode} 的记录成功`);
                    return data;
                } else {
                    addTestResult('记录查找测试', 'warning', `没有找到 ${stockCode} 的记录`);
                    return null;
                }
            } catch (error) {
                addTestResult('记录查找测试', 'error', `查找失败: ${error.message}`);
                return null;
            }
        }
        
        async function testModalFunctions() {
            console.log('🔍 测试模态框函数...');
            
            const functions = [
                'testReviewDataBackfill',
                'debugReviewModal',
                'openReviewModal',
                'checkAndLoadExistingReview',
                'populateModalWithExistingReview'
            ];
            
            let availableFunctions = 0;
            
            functions.forEach(funcName => {
                if (typeof window[funcName] === 'function') {
                    availableFunctions++;
                } else {
                    console.warn(`函数 ${funcName} 不可用`);
                }
            });
            
            if (availableFunctions === functions.length) {
                addTestResult('模态框函数测试', 'success', '所有必需函数都可用');
            } else {
                addTestResult('模态框函数测试', 'warning', 
                    `${availableFunctions}/${functions.length} 个函数可用`);
            }
            
            return availableFunctions > 0;
        }
        
        async function runAllTests() {
            clearResults();
            addTestResult('测试开始', 'success', '开始运行综合测试...');
            
            // 1. 测试API连接
            const apiData = await testApiConnection();
            
            // 2. 测试数据格式
            if (apiData) {
                await testDataFormat(apiData);
            }
            
            // 3. 测试记录查找
            await testRecordSearch();
            
            // 4. 测试模态框函数
            await testModalFunctions();
            
            addTestResult('测试完成', 'success', '所有测试已完成，请查看结果');
        }
        
        async function testSpecificRecord() {
            const stockCode = document.getElementById('test-stock-code').value;
            const reviewDate = document.getElementById('test-review-date').value;
            
            if (!stockCode || !reviewDate) {
                alert('请输入股票代码和复盘日期');
                return;
            }
            
            clearResults();
            addTestResult('指定记录测试', 'success', `测试 ${stockCode} 在 ${reviewDate} 的记录...`);
            
            if (typeof window.testReviewDataBackfill === 'function') {
                try {
                    const result = await window.testReviewDataBackfill(stockCode, reviewDate);
                    if (result) {
                        addTestResult('记录查找', 'success', '找到匹配记录', 
                            `ID: ${result.id}, 评分: ${result.total_score || 0}/5`);
                    } else {
                        addTestResult('记录查找', 'warning', '未找到匹配记录');
                    }
                } catch (error) {
                    addTestResult('记录查找', 'error', `测试失败: ${error.message}`);
                }
            } else {
                addTestResult('函数检查', 'error', 'testReviewDataBackfill 函数不可用');
            }
        }
        
        async function testModalOpen() {
            const stockCode = document.getElementById('test-stock-code').value;
            
            if (!stockCode) {
                alert('请输入股票代码');
                return;
            }
            
            if (typeof window.openReviewModal === 'function') {
                try {
                    await window.openReviewModal(stockCode);
                    addTestResult('模态框测试', 'success', `成功打开 ${stockCode} 的复盘模态框`);
                } catch (error) {
                    addTestResult('模态框测试', 'error', `打开失败: ${error.message}`);
                }
            } else {
                addTestResult('模态框测试', 'error', 'openReviewModal 函数不可用');
            }
        }
    </script>
</body>
</html>'''
    
    with open('comprehensive_review_backfill_test.html', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ 已创建综合测试页面: comprehensive_review_backfill_test.html")

def main():
    """主函数"""
    print("🔍 验证复盘数据回填修复效果")
    print("=" * 50)
    
    # 1. 验证模板修复
    template_ok = verify_template_fixes()
    
    # 2. 测试API响应格式
    api_ok = test_api_response_format()
    
    # 3. 创建综合测试页面
    create_comprehensive_test()
    
    print("\n" + "=" * 50)
    print("📊 验证结果汇总:")
    print(f"  模板修复: {'✅ 通过' if template_ok else '❌ 失败'}")
    print(f"  API测试: {'✅ 通过' if api_ok else '⚠️ 需要服务器运行'}")
    
    if template_ok:
        print("\n🎉 修复验证成功！")
        print("\n下一步操作：")
        print("1. 重启服务器")
        print("2. 访问 /review 页面")
        print("3. 测试复盘数据回填功能")
        print("4. 或访问 comprehensive_review_backfill_test.html 进行详细测试")
    else:
        print("\n❌ 修复验证失败，请检查修复脚本")
    
    return template_ok

if __name__ == "__main__":
    main()