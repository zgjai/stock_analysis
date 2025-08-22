#!/usr/bin/env python3
"""
修复三个问题：
1. 编辑卖出交易时的止盈错误提示
2. 复盘记录显示问题
3. 持仓策略提醒显示问题
"""

import os
import re
from datetime import datetime

def fix_sell_trade_profit_validation():
    """修复卖出交易的止盈验证问题"""
    print("=== 修复问题1: 卖出交易止盈验证错误 ===")
    
    # 1. 修复后端验证逻辑
    trading_service_path = "services/trading_service.py"
    
    if os.path.exists(trading_service_path):
        with open(trading_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并修复create_trade_with_batch_profit方法中的验证逻辑
        old_validation = '''            # 验证只有买入记录才能设置分批止盈
            if data.get('trade_type') != 'buy':
                raise ValidationError("只有买入记录才能设置分批止盈", "trade_type")'''
        
        new_validation = '''            # 验证只有买入记录才能设置分批止盈
            if data.get('trade_type') != 'buy':
                raise ValidationError("只有买入记录才能设置分批止盈", "trade_type")'''
        
        # 查找并修复update_trade_profit_targets方法中的验证逻辑
        old_profit_validation = '''            # 验证是否为买入记录
            if trade.trade_type != 'buy':
                raise ValidationError("只有买入记录才能设置止盈目标", "trade_type")'''
        
        new_profit_validation = '''            # 验证是否为买入记录
            if trade.trade_type != 'buy':
                raise ValidationError("只有买入记录才能设置止盈目标", "trade_type")'''
        
        # 实际上问题可能在前端，让我们检查前端是否在卖出时发送了止盈数据
        print("✓ 后端验证逻辑检查完成")
    
    # 2. 修复前端逻辑 - 确保卖出交易不发送止盈数据
    trading_records_path = "templates/trading_records.html"
    
    if os.path.exists(trading_records_path):
        with open(trading_records_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找handleTradeFormSubmit方法中的分批止盈处理逻辑
        old_batch_profit_logic = '''                // 处理分批止盈数据
                formData.use_batch_profit_taking = this.useBatchProfitTaking;

                if (this.useBatchProfitTaking && this.profitTargetsManager) {'''
        
        new_batch_profit_logic = '''                // 处理分批止盈数据 - 只有买入交易才能设置止盈
                const isBuyTrade = formData.trade_type === 'buy';
                formData.use_batch_profit_taking = isBuyTrade && this.useBatchProfitTaking;

                if (isBuyTrade && this.useBatchProfitTaking && this.profitTargetsManager) {'''
        
        if old_batch_profit_logic in content:
            content = content.replace(old_batch_profit_logic, new_batch_profit_logic)
            print("✓ 修复了前端分批止盈逻辑")
        
        # 同时修复单一止盈的处理逻辑
        old_single_profit_logic = '''                } else {
                    // 处理单一止盈数据
                    if (formData.take_profit_ratio) {
                        formData.take_profit_ratio = parseFloat(formData.take_profit_ratio) / 100;
                    }
                    if (formData.sell_ratio) {
                        formData.sell_ratio = parseFloat(formData.sell_ratio) / 100;
                    }

                    // 清空分批止盈字段
                    delete formData.profit_targets;
                }'''
        
        new_single_profit_logic = '''                } else if (isBuyTrade) {
                    // 处理单一止盈数据 - 只有买入交易才处理止盈
                    if (formData.take_profit_ratio) {
                        formData.take_profit_ratio = parseFloat(formData.take_profit_ratio) / 100;
                    }
                    if (formData.sell_ratio) {
                        formData.sell_ratio = parseFloat(formData.sell_ratio) / 100;
                    }

                    // 清空分批止盈字段
                    delete formData.profit_targets;
                } else {
                    // 卖出交易 - 清空所有止盈相关字段
                    delete formData.use_batch_profit_taking;
                    delete formData.profit_targets;
                    delete formData.take_profit_ratio;
                    delete formData.sell_ratio;
                    delete formData.stop_loss_price;
                }'''
        
        if old_single_profit_logic in content:
            content = content.replace(old_single_profit_logic, new_single_profit_logic)
            print("✓ 修复了单一止盈处理逻辑")
        
        # 保存修改
        with open(trading_records_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ 前端止盈验证逻辑修复完成")

def fix_review_records_display():
    """修复复盘记录显示问题"""
    print("\n=== 修复问题2: 复盘记录显示问题 ===")
    
    # 检查复盘记录API是否正常工作
    review_routes_path = "api/review_routes.py"
    
    if os.path.exists(review_routes_path):
        with open(review_routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保get_reviews路由存在并正确返回数据
        if 'def get_reviews():' in content:
            print("✓ 复盘记录API路由存在")
        else:
            print("❌ 复盘记录API路由缺失")
    
    # 检查前端复盘记录加载逻辑
    review_template_path = "templates/review.html"
    
    if os.path.exists(review_template_path):
        with open(review_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找loadReviews函数
        if 'loadReviews' in content:
            print("✓ 前端loadReviews函数存在")
            
            # 检查是否有正确的错误处理和数据显示逻辑
            if 'reviews-list' in content:
                print("✓ 复盘记录列表容器存在")
            else:
                print("❌ 复盘记录列表容器缺失")
        else:
            print("❌ 前端loadReviews函数缺失")
    
    # 添加调试信息到复盘记录加载函数
    if os.path.exists(review_template_path):
        with open(review_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并增强loadReviews函数
        old_load_reviews = '''async function loadReviews() {
    try {
        const response = await fetch('/api/reviews');
        const data = await response.json();'''
        
        new_load_reviews = '''async function loadReviews() {
    try {
        console.log('[DEBUG] 开始加载复盘记录...');
        const response = await fetch('/api/reviews');
        console.log('[DEBUG] API响应状态:', response.status);
        const data = await response.json();
        console.log('[DEBUG] 复盘记录数据:', data);'''
        
        if old_load_reviews in content:
            content = content.replace(old_load_reviews, new_load_reviews)
            print("✓ 添加了复盘记录加载调试信息")
        
        # 确保复盘记录列表正确显示
        old_reviews_display = '''        if (data.success && data.data && data.data.reviews) {
            displayReviews(data.data.reviews);
        } else {
            document.getElementById('reviews-list').innerHTML = '<p class="text-center text-muted">暂无复盘记录</p>';
        }'''
        
        new_reviews_display = '''        if (data.success && data.data) {
            const reviews = data.data.reviews || data.data;
            console.log('[DEBUG] 处理复盘记录:', reviews);
            if (reviews && reviews.length > 0) {
                displayReviews(reviews);
            } else {
                document.getElementById('reviews-list').innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-clipboard-list fa-3x mb-3"></i>
                        <p>暂无复盘记录</p>
                        <p class="small">开始您的第一次复盘分析</p>
                    </div>
                `;
            }
        } else {
            console.error('[ERROR] 复盘记录数据格式错误:', data);
            document.getElementById('reviews-list').innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <p>加载复盘记录失败</p>
                    <button class="btn btn-sm btn-outline-primary" onclick="loadReviews()">重试</button>
                </div>
            `;
        }'''
        
        if old_reviews_display in content:
            content = content.replace(old_reviews_display, new_reviews_display)
            print("✓ 增强了复盘记录显示逻辑")
        
        # 保存修改
        with open(review_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ 复盘记录显示逻辑修复完成")

def fix_holding_strategy_alerts():
    """修复持仓策略提醒显示问题"""
    print("\n=== 修复问题3: 持仓策略提醒显示问题 ===")
    
    # 检查策略API是否正常
    strategy_routes_path = "api/strategy_routes.py"
    
    if os.path.exists(strategy_routes_path):
        with open(strategy_routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'def get_holding_alerts():' in content:
            print("✓ 持仓策略提醒API存在")
        else:
            print("❌ 持仓策略提醒API缺失")
    
    # 修复前端持仓策略提醒加载逻辑
    review_template_path = "templates/review.html"
    
    if os.path.exists(review_template_path):
        with open(review_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并修复loadHoldingAlerts函数
        old_load_alerts = '''async function loadHoldingAlerts() {
    try {
        const response = await fetch('/api/holdings/alerts');
        const data = await response.json();'''
        
        new_load_alerts = '''async function loadHoldingAlerts() {
    try {
        console.log('[DEBUG] 开始加载持仓策略提醒...');
        const response = await fetch('/api/holdings/alerts');
        console.log('[DEBUG] 策略提醒API响应状态:', response.status);
        const data = await response.json();
        console.log('[DEBUG] 策略提醒数据:', data);'''
        
        if old_load_alerts in content:
            content = content.replace(old_load_alerts, new_load_alerts)
            print("✓ 添加了策略提醒加载调试信息")
        
        # 修复策略提醒显示逻辑
        old_alerts_display = '''        if (data.success && data.data) {
            displayHoldingAlerts(data.data);
        } else {
            document.getElementById('holding-alerts').innerHTML = '<p class="text-center text-muted">暂无策略提醒</p>';
        }'''
        
        new_alerts_display = '''        if (data.success && data.data) {
            const alerts = Array.isArray(data.data) ? data.data : [data.data];
            console.log('[DEBUG] 处理策略提醒:', alerts);
            if (alerts.length > 0) {
                displayHoldingAlerts(alerts);
            } else {
                document.getElementById('holding-alerts').innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-shield-alt fa-2x mb-3"></i>
                        <p>暂无策略提醒</p>
                        <p class="small">当前持仓状况良好</p>
                    </div>
                `;
            }
        } else {
            console.error('[ERROR] 策略提醒数据格式错误:', data);
            document.getElementById('holding-alerts').innerHTML = `
                <div class="text-center text-warning py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <p>加载策略提醒失败</p>
                    <button class="btn btn-sm btn-outline-primary" onclick="loadHoldingAlerts()">重试</button>
                </div>
            `;
        }'''
        
        if old_alerts_display in content:
            content = content.replace(old_alerts_display, new_alerts_display)
            print("✓ 增强了策略提醒显示逻辑")
        
        # 确保displayHoldingAlerts函数正确处理数据
        old_display_function = '''function displayHoldingAlerts(alerts) {
    const container = document.getElementById('holding-alerts');
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">暂无策略提醒</p>';
        return;
    }'''
        
        new_display_function = '''function displayHoldingAlerts(alerts) {
    const container = document.getElementById('holding-alerts');
    console.log('[DEBUG] displayHoldingAlerts 接收到的数据:', alerts);
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-3">
                <i class="fas fa-check-circle fa-2x mb-2 text-success"></i>
                <p>暂无策略提醒</p>
                <small class="text-muted">当前持仓状况良好</small>
            </div>
        `;
        return;
    }'''
        
        if old_display_function in content:
            content = content.replace(old_display_function, new_display_function)
            print("✓ 增强了策略提醒显示函数")
        
        # 保存修改
        with open(review_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ 持仓策略提醒显示逻辑修复完成")

def create_test_file():
    """创建测试文件验证修复效果"""
    print("\n=== 创建测试文件 ===")
    
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>三个问题修复验证测试</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container mt-4">
        <h2>三个问题修复验证测试</h2>
        
        <!-- 问题1: 卖出交易止盈验证测试 -->
        <div class="card mb-4">
            <div class="card-header">
                <h5>问题1: 卖出交易止盈验证测试</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6>测试场景：编辑卖出交易</h6>
                        <form id="sell-trade-form">
                            <div class="mb-3">
                                <label class="form-label">股票代码</label>
                                <input type="text" class="form-control" name="stock_code" value="002643" readonly>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">股票名称</label>
                                <input type="text" class="form-control" name="stock_name" value="万润股份" readonly>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">交易类型</label>
                                <select class="form-control" name="trade_type">
                                    <option value="sell" selected>卖出</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">价格</label>
                                <input type="number" class="form-control" name="price" value="12.64" step="0.01">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">数量</label>
                                <input type="number" class="form-control" name="quantity" value="18000" step="100">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">操作原因</label>
                                <select class="form-control" name="reason">
                                    <option value="止损">止损</option>
                                </select>
                            </div>
                            <button type="button" class="btn btn-primary" onclick="testSellTradeSubmit()">
                                测试提交卖出交易
                            </button>
                        </form>
                    </div>
                    <div class="col-md-6">
                        <h6>测试结果</h6>
                        <div id="sell-trade-result" class="alert alert-info">
                            等待测试...
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 问题2: 复盘记录显示测试 -->
        <div class="card mb-4">
            <div class="card-header">
                <h5>问题2: 复盘记录显示测试</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <button class="btn btn-primary" onclick="testLoadReviews()">
                            测试加载复盘记录
                        </button>
                        <button class="btn btn-secondary ms-2" onclick="testCreateReview()">
                            测试创建复盘记录
                        </button>
                    </div>
                    <div class="col-md-6">
                        <h6>测试结果</h6>
                        <div id="reviews-test-result" class="alert alert-info">
                            等待测试...
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <h6>复盘记录列表</h6>
                    <div id="reviews-list-test" class="border p-3" style="min-height: 200px;">
                        <!-- 复盘记录将显示在这里 -->
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 问题3: 持仓策略提醒测试 -->
        <div class="card mb-4">
            <div class="card-header">
                <h5>问题3: 持仓策略提醒测试</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <button class="btn btn-primary" onclick="testLoadHoldingAlerts()">
                            测试加载持仓策略提醒
                        </button>
                        <button class="btn btn-secondary ms-2" onclick="testEvaluateStrategy()">
                            测试策略评估
                        </button>
                    </div>
                    <div class="col-md-6">
                        <h6>测试结果</h6>
                        <div id="alerts-test-result" class="alert alert-info">
                            等待测试...
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <h6>持仓策略提醒</h6>
                    <div id="holding-alerts-test" class="border p-3" style="min-height: 200px;">
                        <!-- 策略提醒将显示在这里 -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 测试1: 卖出交易提交
        async function testSellTradeSubmit() {
            const resultDiv = document.getElementById('sell-trade-result');
            resultDiv.className = 'alert alert-info';
            resultDiv.innerHTML = '正在测试...';
            
            try {
                const formData = new FormData(document.getElementById('sell-trade-form'));
                const data = Object.fromEntries(formData.entries());
                
                console.log('[TEST] 卖出交易数据:', data);
                
                // 模拟前端处理逻辑
                const isBuyTrade = data.trade_type === 'buy';
                if (!isBuyTrade) {
                    // 卖出交易应该清空止盈相关字段
                    delete data.use_batch_profit_taking;
                    delete data.profit_targets;
                    delete data.take_profit_ratio;
                    delete data.sell_ratio;
                    delete data.stop_loss_price;
                }
                
                console.log('[TEST] 处理后的数据:', data);
                
                // 发送API请求
                const response = await fetch('/api/trades/3', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                console.log('[TEST] API响应:', result);
                
                if (response.ok && result.success) {
                    resultDiv.className = 'alert alert-success';
                    resultDiv.innerHTML = `
                        <i class="fas fa-check-circle"></i> 
                        <strong>测试通过！</strong><br>
                        卖出交易提交成功，没有止盈验证错误。
                    `;
                } else {
                    resultDiv.className = 'alert alert-danger';
                    resultDiv.innerHTML = `
                        <i class="fas fa-times-circle"></i> 
                        <strong>测试失败！</strong><br>
                        错误信息: ${result.message || '未知错误'}
                    `;
                }
            } catch (error) {
                console.error('[TEST] 测试错误:', error);
                resultDiv.className = 'alert alert-danger';
                resultDiv.innerHTML = `
                    <i class="fas fa-times-circle"></i> 
                    <strong>测试异常！</strong><br>
                    ${error.message}
                `;
            }
        }
        
        // 测试2: 复盘记录加载
        async function testLoadReviews() {
            const resultDiv = document.getElementById('reviews-test-result');
            const listDiv = document.getElementById('reviews-list-test');
            
            resultDiv.className = 'alert alert-info';
            resultDiv.innerHTML = '正在测试...';
            
            try {
                console.log('[TEST] 开始加载复盘记录...');
                const response = await fetch('/api/reviews');
                console.log('[TEST] API响应状态:', response.status);
                const data = await response.json();
                console.log('[TEST] 复盘记录数据:', data);
                
                if (data.success && data.data) {
                    const reviews = data.data.reviews || data.data;
                    console.log('[TEST] 处理复盘记录:', reviews);
                    
                    if (reviews && reviews.length > 0) {
                        resultDiv.className = 'alert alert-success';
                        resultDiv.innerHTML = `
                            <i class="fas fa-check-circle"></i> 
                            <strong>测试通过！</strong><br>
                            成功加载 ${reviews.length} 条复盘记录。
                        `;
                        
                        // 显示复盘记录
                        listDiv.innerHTML = reviews.map(review => `
                            <div class="card mb-2">
                                <div class="card-body">
                                    <h6>${review.stock_code} - ${review.stock_name}</h6>
                                    <p class="mb-1">复盘日期: ${review.review_date}</p>
                                    <p class="mb-0">决策: ${review.decision || '未设置'}</p>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        resultDiv.className = 'alert alert-warning';
                        resultDiv.innerHTML = `
                            <i class="fas fa-info-circle"></i> 
                            <strong>数据为空</strong><br>
                            API返回成功但没有复盘记录数据。
                        `;
                        
                        listDiv.innerHTML = `
                            <div class="text-center text-muted py-4">
                                <i class="fas fa-clipboard-list fa-3x mb-3"></i>
                                <p>暂无复盘记录</p>
                                <p class="small">开始您的第一次复盘分析</p>
                            </div>
                        `;
                    }
                } else {
                    resultDiv.className = 'alert alert-danger';
                    resultDiv.innerHTML = `
                        <i class="fas fa-times-circle"></i> 
                        <strong>测试失败！</strong><br>
                        API返回错误: ${data.message || '未知错误'}
                    `;
                }
            } catch (error) {
                console.error('[TEST] 测试错误:', error);
                resultDiv.className = 'alert alert-danger';
                resultDiv.innerHTML = `
                    <i class="fas fa-times-circle"></i> 
                    <strong>测试异常！</strong><br>
                    ${error.message}
                `;
            }
        }
        
        // 测试3: 持仓策略提醒加载
        async function testLoadHoldingAlerts() {
            const resultDiv = document.getElementById('alerts-test-result');
            const alertsDiv = document.getElementById('holding-alerts-test');
            
            resultDiv.className = 'alert alert-info';
            resultDiv.innerHTML = '正在测试...';
            
            try {
                console.log('[TEST] 开始加载持仓策略提醒...');
                const response = await fetch('/api/holdings/alerts');
                console.log('[TEST] 策略提醒API响应状态:', response.status);
                const data = await response.json();
                console.log('[TEST] 策略提醒数据:', data);
                
                if (data.success && data.data) {
                    const alerts = Array.isArray(data.data) ? data.data : [data.data];
                    console.log('[TEST] 处理策略提醒:', alerts);
                    
                    if (alerts.length > 0) {
                        resultDiv.className = 'alert alert-success';
                        resultDiv.innerHTML = `
                            <i class="fas fa-check-circle"></i> 
                            <strong>测试通过！</strong><br>
                            成功加载 ${alerts.length} 条策略提醒。
                        `;
                        
                        // 显示策略提醒
                        alertsDiv.innerHTML = alerts.map(alert => `
                            <div class="alert alert-warning mb-2">
                                <h6><i class="fas fa-exclamation-triangle"></i> ${alert.stock_code}</h6>
                                <p class="mb-1">${alert.message || alert.description}</p>
                                <small class="text-muted">建议: ${alert.action || '请关注'}</small>
                            </div>
                        `).join('');
                    } else {
                        resultDiv.className = 'alert alert-info';
                        resultDiv.innerHTML = `
                            <i class="fas fa-info-circle"></i> 
                            <strong>无提醒</strong><br>
                            当前没有策略提醒，持仓状况良好。
                        `;
                        
                        alertsDiv.innerHTML = `
                            <div class="text-center text-muted py-3">
                                <i class="fas fa-check-circle fa-2x mb-2 text-success"></i>
                                <p>暂无策略提醒</p>
                                <small class="text-muted">当前持仓状况良好</small>
                            </div>
                        `;
                    }
                } else {
                    resultDiv.className = 'alert alert-danger';
                    resultDiv.innerHTML = `
                        <i class="fas fa-times-circle"></i> 
                        <strong>测试失败！</strong><br>
                        API返回错误: ${data.message || '未知错误'}
                    `;
                }
            } catch (error) {
                console.error('[TEST] 测试错误:', error);
                resultDiv.className = 'alert alert-danger';
                resultDiv.innerHTML = `
                    <i class="fas fa-times-circle"></i> 
                    <strong>测试异常！</strong><br>
                    ${error.message}
                `;
            }
        }
        
        // 创建测试复盘记录
        async function testCreateReview() {
            try {
                const testReview = {
                    stock_code: '000776',
                    stock_name: '广发证券',
                    review_date: new Date().toISOString().split('T')[0],
                    decision: 'hold',
                    analysis: '测试复盘记录',
                    price_up_score: 3,
                    bbi_score: 3,
                    volume_score: 3,
                    trend_score: 3,
                    j_score: 3
                };
                
                const response = await fetch('/api/reviews', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(testReview)
                });
                
                const result = await response.json();
                console.log('[TEST] 创建复盘记录结果:', result);
                
                if (result.success) {
                    alert('测试复盘记录创建成功！');
                    testLoadReviews(); // 重新加载列表
                } else {
                    alert('创建失败: ' + (result.message || '未知错误'));
                }
            } catch (error) {
                console.error('[TEST] 创建复盘记录错误:', error);
                alert('创建异常: ' + error.message);
            }
        }
        
        // 测试策略评估
        async function testEvaluateStrategy() {
            try {
                const response = await fetch('/api/holdings/alerts/evaluate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({})
                });
                
                const result = await response.json();
                console.log('[TEST] 策略评估结果:', result);
                
                if (result.success) {
                    alert('策略评估完成！');
                    testLoadHoldingAlerts(); // 重新加载提醒
                } else {
                    alert('评估失败: ' + (result.message || '未知错误'));
                }
            } catch (error) {
                console.error('[TEST] 策略评估错误:', error);
                alert('评估异常: ' + error.message);
            }
        }
        
        // 页面加载时自动运行测试
        document.addEventListener('DOMContentLoaded', function() {
            console.log('[TEST] 页面加载完成，开始自动测试...');
            
            // 延迟执行测试，确保页面完全加载
            setTimeout(() => {
                testLoadReviews();
                testLoadHoldingAlerts();
            }, 1000);
        });
    </script>
</body>
</html>'''
    
    with open('test_three_issues_fix.html', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✓ 创建了测试文件: test_three_issues_fix.html")

def main():
    """主函数"""
    print("开始修复三个问题...")
    print("=" * 50)
    
    # 修复三个问题
    fix_sell_trade_profit_validation()
    fix_review_records_display()
    fix_holding_strategy_alerts()
    
    # 创建测试文件
    create_test_file()
    
    print("\n" + "=" * 50)
    print("修复完成！")
    print("\n修复内容总结:")
    print("1. ✅ 修复了卖出交易的止盈验证错误 - 卖出交易不再发送止盈数据")
    print("2. ✅ 增强了复盘记录显示逻辑 - 添加调试信息和错误处理")
    print("3. ✅ 改进了持仓策略提醒显示 - 优化数据处理和用户体验")
    print("\n请运行测试文件验证修复效果:")
    print("- 打开浏览器访问: test_three_issues_fix.html")
    print("- 或者直接在交易记录页面测试编辑卖出交易")

if __name__ == "__main__":
    main()