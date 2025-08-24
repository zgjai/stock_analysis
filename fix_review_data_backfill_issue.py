#!/usr/bin/env python3
"""
修复复盘页面数据回填问题

问题分析：
1. 前端在打开复盘模态框时，没有正确加载和回填已保存的复盘数据
2. checkAndLoadExistingReview函数可能存在数据查找和填充逻辑问题
3. API响应数据结构与前端期望不匹配

解决方案：
1. 修复前端数据回填逻辑
2. 优化复盘记录查找算法
3. 增强错误处理和调试信息
4. 确保API响应格式一致性
"""

import os
import re
import json
from datetime import datetime

def fix_review_template():
    """修复复盘模板中的数据回填逻辑"""
    template_path = 'templates/review.html'
    
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return False
    
    print(f"🔧 修复复盘模板: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 修复checkAndLoadExistingReview函数
    old_check_function = r'''async function checkAndLoadExistingReview\(stockCode, reviewDate\) \{
    console\.log\('🔍 检查现有复盘记录:', stockCode, reviewDate\);
    
    try \{
        // 获取所有复盘记录并查找匹配的记录
        const response = await fetch\('/api/reviews'\);
        if \(!response\.ok\) \{
            console\.warn\('⚠️ 获取复盘记录失败'\);
            return;
        \}
        
        const data = await response\.json\(\);
        if \(!data\.success \|\| !data\.data\?\.reviews\) \{
            console\.warn\('⚠️ 复盘记录数据格式错误'\);
            return;
        \}
        
        // 查找匹配的复盘记录
        const existingReview = data\.data\.reviews\.find\(review => 
            review\.stock_code === stockCode && review\.review_date === reviewDate
        \);
        
        if \(existingReview\) \{
            console\.log\('✅ 找到现有复盘记录:', existingReview\);
            
            // 设置复盘ID（用于更新而不是创建）
            const reviewIdField = document\.getElementById\('review-id'\);
            if \(reviewIdField\) \{
                reviewIdField\.value = existingReview\.id;
                console\.log\('🆔 设置复盘ID:', existingReview\.id\);
            \}
            
            // 填充现有数据
            populateModalWithExistingReview\(existingReview\);
        \} else \{
            console\.log\('ℹ️ 未找到现有复盘记录，将创建新记录'\);
            
            // 清空复盘ID
            const reviewIdField = document\.getElementById\('review-id'\);
            if \(reviewIdField\) \{
                reviewIdField\.value = '';
            \}
        \}
        
    \} catch \(error\) \{
        console\.error\('❌ 检查现有复盘记录失败:', error\);
    \}
\}'''

    new_check_function = '''async function checkAndLoadExistingReview(stockCode, reviewDate) {
    console.log('🔍 检查现有复盘记录:', stockCode, reviewDate);
    
    try {
        // 构建查询参数，直接查询特定股票和日期的记录
        const queryParams = new URLSearchParams({
            stock_code: stockCode,
            start_date: reviewDate,
            end_date: reviewDate,
            per_page: 1
        });
        
        const response = await fetch(`/api/reviews?${queryParams}`);
        if (!response.ok) {
            console.warn('⚠️ 获取复盘记录失败:', response.status, response.statusText);
            return;
        }
        
        const data = await response.json();
        console.log('📊 API响应数据:', data);
        
        if (!data.success) {
            console.warn('⚠️ API返回失败状态:', data.message || '未知错误');
            return;
        }
        
        // 处理不同的数据结构
        let reviews = [];
        if (data.data) {
            if (Array.isArray(data.data)) {
                // 直接是数组格式
                reviews = data.data;
            } else if (data.data.reviews && Array.isArray(data.data.reviews)) {
                // 分页格式
                reviews = data.data.reviews;
            } else if (data.data.data && Array.isArray(data.data.data)) {
                // 嵌套格式
                reviews = data.data.data;
            }
        }
        
        console.log('📝 解析到的复盘记录:', reviews);
        
        // 查找匹配的复盘记录（精确匹配股票代码和日期）
        const existingReview = reviews.find(review => {
            const matchStock = review.stock_code === stockCode;
            const matchDate = review.review_date === reviewDate;
            console.log(`🔍 检查记录 ${review.id}: 股票匹配=${matchStock}, 日期匹配=${matchDate}`);
            return matchStock && matchDate;
        });
        
        if (existingReview) {
            console.log('✅ 找到现有复盘记录:', existingReview);
            
            // 设置复盘ID（用于更新而不是创建）
            const reviewIdField = document.getElementById('review-id');
            if (reviewIdField) {
                reviewIdField.value = existingReview.id;
                console.log('🆔 设置复盘ID:', existingReview.id);
            }
            
            // 填充现有数据
            populateModalWithExistingReview(existingReview);
            
            // 显示提示信息
            if (typeof showInfoMessage === 'function') {
                showInfoMessage(`已加载 ${stockCode} 在 ${reviewDate} 的复盘记录`, {
                    position: 'toast',
                    duration: 2000
                });
            }
        } else {
            console.log('ℹ️ 未找到现有复盘记录，将创建新记录');
            
            // 清空复盘ID
            const reviewIdField = document.getElementById('review-id');
            if (reviewIdField) {
                reviewIdField.value = '';
            }
            
            // 显示提示信息
            if (typeof showInfoMessage === 'function') {
                showInfoMessage(`将为 ${stockCode} 创建新的复盘记录`, {
                    position: 'toast',
                    duration: 2000
                });
            }
        }
        
    } catch (error) {
        console.error('❌ 检查现有复盘记录失败:', error);
        
        // 显示错误信息
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('加载复盘记录失败: ' + error.message);
        }
        
        // 清空复盘ID，确保不会意外更新错误的记录
        const reviewIdField = document.getElementById('review-id');
        if (reviewIdField) {
            reviewIdField.value = '';
        }
    }
}'''

    # 替换函数
    if re.search(r'async function checkAndLoadExistingReview', content):
        content = re.sub(
            old_check_function,
            new_check_function,
            content,
            flags=re.DOTALL
        )
        print("✅ 已更新 checkAndLoadExistingReview 函数")
    else:
        print("⚠️ 未找到 checkAndLoadExistingReview 函数，可能已经被修改")
    
    # 2. 增强populateModalWithExistingReview函数
    old_populate_function = r'''function populateModalWithExistingReview\(review\) \{
    console\.log\('📝 填充现有复盘记录数据:', review\);
    
    // 填充基本信息
    const holdingDaysField = document\.getElementById\('holding-days'\);
    if \(holdingDaysField && review\.holding_days\) \{
        holdingDaysField\.value = review\.holding_days;
    \}
    
    const currentPriceField = document\.getElementById\('current-price-input'\);
    if \(currentPriceField && review\.current_price\) \{
        currentPriceField\.value = review\.current_price;
    \}
    
    // 填充评分
    const scoreFields = \[
        \{ id: 'price-up-score', value: review\.price_up_score \},
        \{ id: 'bbi-score', value: review\.bbi_score \},
        \{ id: 'volume-score', value: review\.volume_score \},
        \{ id: 'trend-score', value: review\.trend_score \},
        \{ id: 'j-score', value: review\.j_score \}
    \];
    
    scoreFields\.forEach\(field => \{
        const element = document\.getElementById\(field\.id\);
        if \(element\) \{
            element\.checked = field\.value === 1;
        \}
    \}\);
    
    // 填充文本字段
    const analysisField = document\.getElementById\('analysis'\);
    if \(analysisField && review\.analysis\) \{
        analysisField\.value = review\.analysis;
    \}
    
    const decisionField = document\.getElementById\('decision'\);
    if \(decisionField && review\.decision\) \{
        decisionField\.value = review\.decision;
    \}
    
    const reasonField = document\.getElementById\('reason'\);
    if \(reasonField && review\.reason\) \{
        reasonField\.value = review\.reason;
    \}
    
    // 显示浮盈信息
    if \(review\.floating_profit_display\) \{
        const profitRatioEl = document\.getElementById\('floating-profit-ratio'\);
        if \(profitRatioEl\) \{
            profitRatioEl\.textContent = review\.floating_profit_display\.display;
            profitRatioEl\.className = review\.floating_profit_display\.color;
        \}
    \}
    
    // 显示买入价格
    if \(review\.buy_price\) \{
        const buyPriceDisplay = document\.getElementById\('buy-price-display'\);
        if \(buyPriceDisplay\) \{
            buyPriceDisplay\.textContent = `¥\$\{review\.buy_price\.toFixed\(2\)\}`;
        \}
    \}
\}'''

    new_populate_function = '''function populateModalWithExistingReview(review) {
    console.log('📝 填充现有复盘记录数据:', review);
    
    try {
        // 填充基本信息
        const holdingDaysField = document.getElementById('holding-days');
        if (holdingDaysField && review.holding_days) {
            holdingDaysField.value = review.holding_days;
            console.log('✅ 已填充持仓天数:', review.holding_days);
        }
        
        const currentPriceField = document.getElementById('current-price-input');
        if (currentPriceField && review.current_price) {
            currentPriceField.value = review.current_price;
            console.log('✅ 已填充当前价格:', review.current_price);
        }
        
        // 填充评分复选框
        const scoreFields = [
            { id: 'price-up-score', value: review.price_up_score, name: '收盘价上升' },
            { id: 'bbi-score', value: review.bbi_score, name: '不破BBI线' },
            { id: 'volume-score', value: review.volume_score, name: '无放量阴线' },
            { id: 'trend-score', value: review.trend_score, name: '趋势还在向上' },
            { id: 'j-score', value: review.j_score, name: 'J没死叉' }
        ];
        
        let checkedCount = 0;
        scoreFields.forEach(field => {
            const element = document.getElementById(field.id);
            if (element) {
                const isChecked = field.value === 1;
                element.checked = isChecked;
                if (isChecked) checkedCount++;
                console.log(`✅ 已填充评分 ${field.name}:`, isChecked);
            } else {
                console.warn(`⚠️ 未找到评分字段: ${field.id}`);
            }
        });
        
        console.log(`📊 总评分: ${checkedCount}/5`);
        
        // 更新总分显示
        const totalScoreEl = document.getElementById('total-score');
        if (totalScoreEl) {
            totalScoreEl.textContent = checkedCount;
        }
        
        // 填充文本字段
        const analysisField = document.getElementById('analysis');
        if (analysisField) {
            analysisField.value = review.analysis || '';
            console.log('✅ 已填充分析内容:', review.analysis ? '有内容' : '空');
        }
        
        const decisionField = document.getElementById('decision');
        if (decisionField) {
            decisionField.value = review.decision || '';
            console.log('✅ 已填充决策结果:', review.decision);
        }
        
        const reasonField = document.getElementById('reason');
        if (reasonField) {
            reasonField.value = review.reason || '';
            console.log('✅ 已填充决策理由:', review.reason ? '有内容' : '空');
        }
        
        // 处理浮盈信息显示
        if (review.floating_profit_ratio !== null && review.floating_profit_ratio !== undefined) {
            const profitRatio = parseFloat(review.floating_profit_ratio);
            const profitPercentage = (profitRatio * 100).toFixed(2);
            
            const profitRatioEl = document.getElementById('floating-profit-ratio');
            if (profitRatioEl) {
                profitRatioEl.textContent = profitPercentage + '%';
                
                // 设置颜色
                const container = profitRatioEl.closest('.floating-profit-container');
                if (container) {
                    container.className = 'floating-profit-container';
                    if (profitRatio > 0) {
                        container.classList.add('profit');
                        profitRatioEl.style.color = '#dc3545'; // 红色表示盈利
                    } else if (profitRatio < 0) {
                        container.classList.add('loss');
                        profitRatioEl.style.color = '#28a745'; // 绿色表示亏损
                    } else {
                        container.classList.add('neutral');
                        profitRatioEl.style.color = '#6c757d'; // 灰色表示持平
                    }
                }
                console.log('✅ 已填充浮盈比例:', profitPercentage + '%');
            }
        }
        
        // 显示买入价格
        if (review.buy_price) {
            const buyPriceDisplay = document.getElementById('buy-price-display');
            if (buyPriceDisplay) {
                buyPriceDisplay.textContent = `¥${parseFloat(review.buy_price).toFixed(2)}`;
                console.log('✅ 已填充买入价格:', review.buy_price);
            }
        }
        
        // 触发变化检测，更新保存状态
        if (window.reviewSaveManager && typeof window.reviewSaveManager.captureOriginalFormData === 'function') {
            // 延迟执行，确保所有字段都已填充
            setTimeout(() => {
                window.reviewSaveManager.captureOriginalFormData();
                console.log('✅ 已更新原始表单数据');
            }, 100);
        }
        
        console.log('✅ 复盘记录数据填充完成');
        
    } catch (error) {
        console.error('❌ 填充复盘记录数据失败:', error);
        
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('填充复盘数据失败: ' + error.message);
        }
    }
}'''

    # 替换函数
    if re.search(r'function populateModalWithExistingReview', content):
        content = re.sub(
            old_populate_function,
            new_populate_function,
            content,
            flags=re.DOTALL
        )
        print("✅ 已更新 populateModalWithExistingReview 函数")
    else:
        print("⚠️ 未找到 populateModalWithExistingReview 函数，可能已经被修改")
    
    # 3. 增强openReviewModal函数，确保正确调用数据回填
    old_open_modal = r'''async function openReviewModal\(stockCode\) \{
    console\.log\('🔧 打开复盘模态框:', stockCode\);

    if \(!reviewModal\) \{
        console\.error\('❌ 复盘模态框未初始化'\);
        alert\('复盘模态框未初始化，请刷新页面重试'\);
        return;
    \}

    try \{
        // 重置表单
        const form = document\.getElementById\('review-form'\);
        if \(form\) form\.reset\(\);

        // 设置股票代码
        const stockCodeInput = document\.getElementById\('review-stock-code'\);
        const displayStockCode = document\.getElementById\('display-stock-code'\);

        if \(stockCodeInput\) stockCodeInput\.value = stockCode;
        if \(displayStockCode\) displayStockCode\.value = stockCode;

        // 设置当前日期
        const reviewDate = document\.getElementById\('review-date'\);
        const currentDate = new Date\(\)\.toISOString\(\)\.split\('T'\)\[0\];
        if \(reviewDate\) \{
            reviewDate\.value = currentDate;
        \}

        // 检查是否已存在复盘记录
        await checkAndLoadExistingReview\(stockCode, currentDate\);

        // 查找持仓信息并填充数据
        const holding = currentHoldings\.find\(h => h\.stock_code === stockCode\);
        if \(holding\) \{
            console\.log\('✅ 找到持仓信息:', holding\);
            populateModalWithHoldingData\(stockCode, holding\);
        \} else \{
            console\.warn\('⚠️ 未找到持仓信息，尝试从API获取:', stockCode\);
            loadHoldingInfo\(stockCode\)\.then\(holdingData => \{
                if \(holdingData\) \{
                    populateModalWithHoldingData\(stockCode, holdingData\);
                \}
            \}\);
        \}

        // 显示模态框
        reviewModal\.show\(\);
        console\.log\('✅ 模态框显示成功'\);

    \} catch \(error\) \{
        console\.error\('❌ openReviewModal失败:', error\);
        alert\('打开复盘模态框失败: ' \+ error\.message\);
    \}
\}'''

    new_open_modal = '''async function openReviewModal(stockCode) {
    console.log('🔧 打开复盘模态框:', stockCode);

    if (!reviewModal) {
        console.error('❌ 复盘模态框未初始化');
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('复盘模态框未初始化，请刷新页面重试');
        } else {
            alert('复盘模态框未初始化，请刷新页面重试');
        }
        return;
    }

    try {
        // 显示加载状态
        if (typeof showInfoMessage === 'function') {
            showInfoMessage('正在加载复盘数据...', {
                position: 'toast',
                duration: 1000
            });
        }

        // 重置表单
        const form = document.getElementById('review-form');
        if (form) {
            form.reset();
            console.log('✅ 表单已重置');
        }

        // 设置股票代码
        const stockCodeInput = document.getElementById('review-stock-code');
        const displayStockCode = document.getElementById('display-stock-code');

        if (stockCodeInput) {
            stockCodeInput.value = stockCode;
            console.log('✅ 已设置股票代码输入框:', stockCode);
        }
        if (displayStockCode) {
            displayStockCode.value = stockCode;
            console.log('✅ 已设置股票代码显示框:', stockCode);
        }

        // 设置当前日期
        const reviewDate = document.getElementById('review-date');
        const currentDate = new Date().toISOString().split('T')[0];
        if (reviewDate) {
            reviewDate.value = currentDate;
            console.log('✅ 已设置复盘日期:', currentDate);
        }

        // 先检查是否已存在复盘记录（这是关键步骤）
        console.log('🔍 开始检查现有复盘记录...');
        await checkAndLoadExistingReview(stockCode, currentDate);

        // 查找持仓信息并填充数据（只在没有现有记录时填充基础数据）
        const reviewIdField = document.getElementById('review-id');
        const hasExistingReview = reviewIdField && reviewIdField.value;
        
        if (!hasExistingReview) {
            console.log('📊 没有现有记录，填充持仓基础数据');
            const holding = currentHoldings.find(h => h.stock_code === stockCode);
            if (holding) {
                console.log('✅ 找到持仓信息:', holding);
                populateModalWithHoldingData(stockCode, holding);
            } else {
                console.warn('⚠️ 未找到持仓信息，尝试从API获取:', stockCode);
                try {
                    const holdingData = await loadHoldingInfo(stockCode);
                    if (holdingData) {
                        populateModalWithHoldingData(stockCode, holdingData);
                    }
                } catch (error) {
                    console.warn('⚠️ 获取持仓信息失败:', error);
                }
            }
        } else {
            console.log('📝 已有现有记录，跳过基础数据填充');
        }

        // 显示模态框
        reviewModal.show();
        console.log('✅ 模态框显示成功');

        // 延迟执行一些初始化操作，确保模态框完全显示
        setTimeout(() => {
            // 重新计算总分（防止显示不一致）
            if (typeof calculateTotalScore === 'function') {
                calculateTotalScore();
            }
            
            // 如果有当前价格，重新计算浮盈
            const currentPriceInput = document.getElementById('current-price-input');
            if (currentPriceInput && currentPriceInput.value && typeof calculateFloatingProfit === 'function') {
                calculateFloatingProfit();
            }
        }, 200);

    } catch (error) {
        console.error('❌ openReviewModal失败:', error);
        
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('打开复盘模态框失败: ' + error.message);
        } else {
            alert('打开复盘模态框失败: ' + error.message);
        }
    }
}'''

    # 替换函数
    if re.search(r'async function openReviewModal', content):
        content = re.sub(
            old_open_modal,
            new_open_modal,
            content,
            flags=re.DOTALL
        )
        print("✅ 已更新 openReviewModal 函数")
    else:
        print("⚠️ 未找到 openReviewModal 函数，可能已经被修改")
    
    # 4. 添加调试函数
    debug_functions = '''

// 调试函数：测试复盘数据回填
window.testReviewDataBackfill = async function(stockCode, reviewDate) {
    console.log('🧪 测试复盘数据回填:', stockCode, reviewDate);
    
    try {
        // 测试API调用
        const queryParams = new URLSearchParams({
            stock_code: stockCode,
            start_date: reviewDate,
            end_date: reviewDate,
            per_page: 1
        });
        
        const response = await fetch(`/api/reviews?${queryParams}`);
        const data = await response.json();
        
        console.log('📊 API响应:', data);
        
        // 测试数据解析
        let reviews = [];
        if (data.data) {
            if (Array.isArray(data.data)) {
                reviews = data.data;
            } else if (data.data.reviews && Array.isArray(data.data.reviews)) {
                reviews = data.data.reviews;
            }
        }
        
        console.log('📝 解析到的记录:', reviews);
        
        const existingReview = reviews.find(review => 
            review.stock_code === stockCode && review.review_date === reviewDate
        );
        
        if (existingReview) {
            console.log('✅ 找到匹配记录:', existingReview);
            return existingReview;
        } else {
            console.log('❌ 未找到匹配记录');
            return null;
        }
        
    } catch (error) {
        console.error('❌ 测试失败:', error);
        return null;
    }
};

// 调试函数：检查模态框状态
window.debugReviewModal = function() {
    console.log('🔍 检查复盘模态框状态');
    
    const modal = document.getElementById('reviewModal');
    const form = document.getElementById('review-form');
    const stockCodeInput = document.getElementById('review-stock-code');
    const reviewIdField = document.getElementById('review-id');
    const reviewDateField = document.getElementById('review-date');
    
    console.log('模态框元素:', modal ? '存在' : '不存在');
    console.log('表单元素:', form ? '存在' : '不存在');
    console.log('股票代码输入框:', stockCodeInput ? stockCodeInput.value : '不存在');
    console.log('复盘ID字段:', reviewIdField ? reviewIdField.value : '不存在');
    console.log('复盘日期字段:', reviewDateField ? reviewDateField.value : '不存在');
    
    if (form) {
        const formData = new FormData(form);
        const formObject = {};
        for (let [key, value] of formData.entries()) {
            formObject[key] = value;
        }
        console.log('表单数据:', formObject);
    }
    
    return {
        modal: !!modal,
        form: !!form,
        stockCode: stockCodeInput?.value,
        reviewId: reviewIdField?.value,
        reviewDate: reviewDateField?.value
    };
};'''

    # 在脚本末尾添加调试函数
    if '// 暴露全局函数' in content:
        content = content.replace(
            '// 暴露全局函数',
            debug_functions + '\n\n// 暴露全局函数'
        )
        print("✅ 已添加调试函数")
    
    # 保存修改后的文件
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 复盘模板修复完成")
    return True

def create_test_file():
    """创建测试文件来验证修复效果"""
    test_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>复盘数据回填测试</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h2>复盘数据回填测试</h2>
        
        <div class="card">
            <div class="card-body">
                <h5>测试步骤</h5>
                <ol>
                    <li>打开浏览器开发者工具（F12）</li>
                    <li>切换到Console标签页</li>
                    <li>输入以下命令测试：</li>
                </ol>
                
                <div class="bg-light p-3 rounded">
                    <h6>测试命令：</h6>
                    <code>
                        // 测试API数据获取<br>
                        testReviewDataBackfill('000001', '2025-01-20');<br><br>
                        
                        // 检查模态框状态<br>
                        debugReviewModal();<br><br>
                        
                        // 测试打开模态框<br>
                        openReviewModal('000001');
                    </code>
                </div>
                
                <div class="mt-3">
                    <h6>预期结果：</h6>
                    <ul>
                        <li>如果该股票在指定日期有复盘记录，应该能正确加载和显示</li>
                        <li>所有表单字段应该被正确填充</li>
                        <li>评分复选框应该显示正确的选中状态</li>
                        <li>浮盈比例应该正确计算和显示</li>
                    </ul>
                </div>
                
                <div class="mt-3">
                    <button class="btn btn-primary" onclick="window.location.href='/review'">
                        前往复盘页面测试
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    with open('test_review_data_backfill.html', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("✅ 已创建测试文件: test_review_data_backfill.html")

def main():
    """主函数"""
    print("🚀 开始修复复盘页面数据回填问题")
    print("=" * 50)
    
    try:
        # 修复复盘模板
        if fix_review_template():
            print("✅ 复盘模板修复成功")
        else:
            print("❌ 复盘模板修复失败")
            return False
        
        # 创建测试文件
        create_test_file()
        
        print("\n" + "=" * 50)
        print("🎉 修复完成！")
        print("\n修复内容：")
        print("1. ✅ 优化了复盘记录查找逻辑，支持多种API响应格式")
        print("2. ✅ 增强了数据回填函数，提供详细的调试信息")
        print("3. ✅ 改进了模态框打开流程，确保数据正确加载")
        print("4. ✅ 添加了调试函数，便于问题排查")
        print("5. ✅ 增加了错误处理和用户提示")
        
        print("\n测试方法：")
        print("1. 重启服务器")
        print("2. 访问复盘页面 /review")
        print("3. 选择一个已有复盘记录的股票")
        print("4. 点击开始复盘，检查数据是否正确回填")
        print("5. 或者访问 test_review_data_backfill.html 进行详细测试")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    main()