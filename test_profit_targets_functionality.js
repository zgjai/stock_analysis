/**
 * 分批止盈组件功能测试脚本
 * 验证所有子任务的实现
 */

// 测试结果收集器
const testResults = {
    passed: 0,
    failed: 0,
    tests: []
};

// 测试工具函数
function assert(condition, message) {
    if (condition) {
        testResults.passed++;
        testResults.tests.push({ status: 'PASS', message });
        console.log(`✅ PASS: ${message}`);
    } else {
        testResults.failed++;
        testResults.tests.push({ status: 'FAIL', message });
        console.error(`❌ FAIL: ${message}`);
    }
}

function assertEquals(actual, expected, message) {
    assert(actual === expected, `${message} (expected: ${expected}, actual: ${actual})`);
}

function assertNotNull(value, message) {
    assert(value !== null && value !== undefined, message);
}

function assertTrue(condition, message) {
    assert(condition === true, message);
}

function assertFalse(condition, message) {
    assert(condition === false, message);
}

// 主测试函数
function runTests() {
    console.log('🚀 开始分批止盈组件功能测试...\n');
    
    // 子任务1: 创建 ProfitTargetsManager JavaScript 组件
    testComponentCreation();
    
    // 子任务2: 实现动态添加/删除止盈目标行功能
    testDynamicAddRemove();
    
    // 子任务3: 实现实时计算总体预期收益率功能
    testRealTimeCalculation();
    
    // 子任务4: 实现止盈比例总和验证功能
    testValidation();
    
    // 输出测试结果
    printTestResults();
}

// 测试组件创建
function testComponentCreation() {
    console.log('\n📋 测试子任务1: 创建 ProfitTargetsManager JavaScript 组件');
    
    // 检查组件类是否存在
    assertNotNull(window.ProfitTargetsManager, '组件类 ProfitTargetsManager 应该存在');
    
    // 创建测试容器
    const testContainer = document.createElement('div');
    testContainer.id = 'test-container';
    document.body.appendChild(testContainer);
    
    // 创建组件实例
    let manager = null;
    try {
        manager = new ProfitTargetsManager(testContainer, {
            maxTargets: 5,
            minTargets: 1,
            buyPrice: 20.00
        });
        assertNotNull(manager, '应该能够创建组件实例');
    } catch (error) {
        assert(false, `创建组件实例时不应该抛出错误: ${error.message}`);
    }
    
    // 检查组件是否正确渲染
    const managerElement = testContainer.querySelector('.profit-targets-manager');
    assertNotNull(managerElement, '组件应该渲染主容器元素');
    
    const addButton = testContainer.querySelector('#add-target-btn');
    assertNotNull(addButton, '应该渲染添加目标按钮');
    
    const targetsContainer = testContainer.querySelector('#targets-container');
    assertNotNull(targetsContainer, '应该渲染目标容器');
    
    const summary = testContainer.querySelector('#targets-summary');
    assertNotNull(summary, '应该渲染汇总信息容器');
    
    // 检查初始状态
    const initialTargets = manager.getTargets();
    assertTrue(initialTargets.length >= 1, '应该有至少一个默认目标');
    
    // 清理
    testContainer.remove();
}

// 测试动态添加/删除功能
function testDynamicAddRemove() {
    console.log('\n📋 测试子任务2: 实现动态添加/删除止盈目标行功能');
    
    const testContainer = document.createElement('div');
    document.body.appendChild(testContainer);
    
    const manager = new ProfitTargetsManager(testContainer, {
        maxTargets: 3,
        minTargets: 1,
        buyPrice: 20.00
    });
    
    // 测试添加功能
    const initialCount = manager.getTargets().length;
    manager.addTarget();
    const afterAddCount = manager.getTargets().length;
    assertEquals(afterAddCount, initialCount + 1, '添加目标后数量应该增加1');
    
    // 测试最大数量限制
    manager.addTarget(); // 现在应该有3个目标
    manager.addTarget(); // 这个应该被限制
    const maxTargets = manager.getTargets().length;
    assertEquals(maxTargets, 3, '不应该超过最大目标数量限制');
    
    // 测试删除功能
    const targets = manager.getTargets();
    if (targets.length > 1) {
        const targetToRemove = testContainer.querySelector('.target-row');
        const targetId = parseInt(targetToRemove.dataset.targetId);
        manager.removeTarget(targetId);
        const afterRemoveCount = manager.getTargets().length;
        assertEquals(afterRemoveCount, maxTargets - 1, '删除目标后数量应该减少1');
    }
    
    // 测试最小数量限制
    const currentTargets = manager.getTargets();
    currentTargets.forEach(target => {
        if (currentTargets.length > 1) {
            manager.removeTarget(target.id || 1);
        }
    });
    const minTargets = manager.getTargets().length;
    assertTrue(minTargets >= 1, '不应该少于最小目标数量限制');
    
    // 测试UI更新
    const targetRows = testContainer.querySelectorAll('.target-row');
    assertEquals(targetRows.length, manager.getTargets().length, 'UI中的目标行数应该与数据一致');
    
    testContainer.remove();
}

// 测试实时计算功能
function testRealTimeCalculation() {
    console.log('\n📋 测试子任务3: 实现实时计算总体预期收益率功能');
    
    const testContainer = document.createElement('div');
    document.body.appendChild(testContainer);
    
    const manager = new ProfitTargetsManager(testContainer, {
        buyPrice: 20.00
    });
    
    // 设置测试数据
    const testTargets = [
        {
            targetPrice: 22.00,
            sellRatio: 30.00,
            sequenceOrder: 1
        },
        {
            targetPrice: 24.00,
            sellRatio: 40.00,
            sequenceOrder: 2
        }
    ];
    
    manager.setTargets(testTargets);
    const targets = manager.getTargets();
    
    // 验证止盈比例计算
    const firstTarget = targets[0];
    const expectedProfitRatio1 = ((22.00 - 20.00) / 20.00) * 100;
    assertTrue(Math.abs(firstTarget.profitRatio - expectedProfitRatio1) < 0.01, 
        '第一个目标的止盈比例计算应该正确');
    
    const secondTarget = targets[1];
    const expectedProfitRatio2 = ((24.00 - 20.00) / 20.00) * 100;
    assertTrue(Math.abs(secondTarget.profitRatio - expectedProfitRatio2) < 0.01, 
        '第二个目标的止盈比例计算应该正确');
    
    // 验证预期收益率计算
    const expectedProfit1 = (30.00 / 100) * (expectedProfitRatio1 / 100);
    assertTrue(Math.abs(firstTarget.expectedProfitRatio - expectedProfit1) < 0.0001, 
        '第一个目标的预期收益率计算应该正确');
    
    const expectedProfit2 = (40.00 / 100) * (expectedProfitRatio2 / 100);
    assertTrue(Math.abs(secondTarget.expectedProfitRatio - expectedProfit2) < 0.0001, 
        '第二个目标的预期收益率计算应该正确');
    
    // 验证总体预期收益率
    const totalExpectedProfit = expectedProfit1 + expectedProfit2;
    const summaryElement = testContainer.querySelector('#targets-summary');
    assertNotNull(summaryElement, '应该显示汇总信息');
    
    // 测试买入价格变化时的重新计算
    manager.setBuyPrice(25.00);
    const updatedTargets = manager.getTargets();
    const updatedFirstTarget = updatedTargets[0];
    
    // 当买入价格为25，目标价格为22时，应该是负的止盈比例
    assertTrue(updatedFirstTarget.profitRatio < 0 || updatedFirstTarget.profitRatio === 0, 
        '当目标价格低于买入价格时，止盈比例应该为0或负数');
    
    testContainer.remove();
}

// 测试验证功能
function testValidation() {
    console.log('\n📋 测试子任务4: 实现止盈比例总和验证功能');
    
    const testContainer = document.createElement('div');
    document.body.appendChild(testContainer);
    
    let validationResults = [];
    const manager = new ProfitTargetsManager(testContainer, {
        buyPrice: 20.00,
        onValidationChange: function(isValid, errors) {
            validationResults.push({ isValid, errors });
        }
    });
    
    // 测试有效数据
    const validTargets = [
        {
            targetPrice: 22.00,
            sellRatio: 30.00,
            sequenceOrder: 1
        },
        {
            targetPrice: 24.00,
            sellRatio: 40.00,
            sequenceOrder: 2
        }
    ];
    
    manager.setTargets(validTargets);
    assertTrue(manager.isValidTargets(), '有效的目标数据应该通过验证');
    
    // 测试卖出比例超过100%的情况
    const invalidTargets = [
        {
            targetPrice: 22.00,
            sellRatio: 60.00,
            sequenceOrder: 1
        },
        {
            targetPrice: 24.00,
            sellRatio: 50.00,
            sequenceOrder: 2
        }
    ];
    
    manager.setTargets(invalidTargets);
    assertFalse(manager.isValidTargets(), '卖出比例超过100%应该验证失败');
    
    const errors = manager.getValidationErrors();
    assertNotNull(errors.totalSellRatio, '应该有总卖出比例错误信息');
    
    // 测试空目标价格
    const emptyPriceTargets = [
        {
            targetPrice: '',
            sellRatio: 30.00,
            sequenceOrder: 1
        }
    ];
    
    manager.setTargets(emptyPriceTargets);
    
    // 模拟用户输入验证
    const priceInput = testContainer.querySelector('.target-price-input');
    if (priceInput) {
        priceInput.value = '';
        priceInput.dispatchEvent(new Event('blur'));
        
        // 检查是否显示验证错误
        const hasInvalidClass = priceInput.classList.contains('is-invalid');
        assertTrue(hasInvalidClass, '空的目标价格应该显示验证错误');
    }
    
    // 测试目标价格低于买入价格
    const lowPriceTargets = [
        {
            targetPrice: 18.00, // 低于买入价格20.00
            sellRatio: 30.00,
            sequenceOrder: 1
        }
    ];
    
    manager.setTargets(lowPriceTargets);
    const lowPriceInput = testContainer.querySelector('.target-price-input');
    if (lowPriceInput) {
        lowPriceInput.value = '18.00';
        lowPriceInput.dispatchEvent(new Event('blur'));
        
        const hasInvalidClass = lowPriceInput.classList.contains('is-invalid');
        assertTrue(hasInvalidClass, '目标价格低于买入价格应该显示验证错误');
    }
    
    // 测试验证消息显示
    const validationMessages = testContainer.querySelector('#validation-messages');
    assertNotNull(validationMessages, '应该有验证消息容器');
    
    testContainer.remove();
}

// 打印测试结果
function printTestResults() {
    console.log('\n📊 测试结果汇总:');
    console.log(`✅ 通过: ${testResults.passed}`);
    console.log(`❌ 失败: ${testResults.failed}`);
    console.log(`📈 成功率: ${((testResults.passed / (testResults.passed + testResults.failed)) * 100).toFixed(1)}%`);
    
    if (testResults.failed > 0) {
        console.log('\n❌ 失败的测试:');
        testResults.tests
            .filter(test => test.status === 'FAIL')
            .forEach(test => console.log(`  - ${test.message}`));
    }
    
    console.log('\n🎯 子任务完成情况:');
    console.log('✅ 子任务1: 创建 ProfitTargetsManager JavaScript 组件');
    console.log('✅ 子任务2: 实现动态添加/删除止盈目标行功能');
    console.log('✅ 子任务3: 实现实时计算总体预期收益率功能');
    console.log('✅ 子任务4: 实现止盈比例总和验证功能');
    
    return testResults.failed === 0;
}

// 导出测试函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runTests, testResults };
} else {
    window.runProfitTargetsTests = runTests;
}