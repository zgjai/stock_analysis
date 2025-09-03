/**
 * 修复历史交易排序问题的脚本
 */

// 检查并修复排序功能
function fixSortingIssue() {
    console.log('=== 开始修复排序问题 ===');
    
    // 1. 检查API客户端
    if (typeof window.apiClient === 'undefined') {
        console.error('❌ apiClient 未定义');
        return false;
    } else {
        console.log('✅ apiClient 已加载');
    }
    
    // 2. 检查排序控件
    const sortBySelect = document.getElementById('sort-by');
    const sortOrderSelect = document.getElementById('sort-order');
    
    if (!sortBySelect) {
        console.error('❌ sort-by 元素未找到');
        return false;
    } else {
        console.log('✅ sort-by 元素存在');
    }
    
    if (!sortOrderSelect) {
        console.error('❌ sort-order 元素未找到');
        return false;
    } else {
        console.log('✅ sort-order 元素存在');
    }
    
    // 3. 检查历史交易管理器
    if (typeof window.historicalTradesManager === 'undefined') {
        console.error('❌ historicalTradesManager 未定义');
        return false;
    } else {
        console.log('✅ historicalTradesManager 已加载');
    }
    
    // 4. 重新绑定事件监听器
    console.log('🔧 重新绑定排序事件监听器...');
    
    // 移除现有的事件监听器
    sortBySelect.removeEventListener('change', handleSortChange);
    sortOrderSelect.removeEventListener('change', handleSortChange);
    
    // 添加新的事件监听器
    sortBySelect.addEventListener('change', handleSortChange);
    sortOrderSelect.addEventListener('change', handleSortChange);
    
    console.log('✅ 事件监听器已重新绑定');
    
    // 5. 测试排序功能
    console.log('🧪 测试排序功能...');
    testSortingFunction();
    
    console.log('=== 排序问题修复完成 ===');
    return true;
}

// 排序变化处理函数
function handleSortChange() {
    console.log('📊 排序参数发生变化');
    
    const sortBy = document.getElementById('sort-by').value;
    const sortOrder = document.getElementById('sort-order').value;
    
    console.log(`排序字段: ${sortBy}, 排序方向: ${sortOrder}`);
    
    // 调用历史交易管理器的排序方法
    if (window.historicalTradesManager && typeof window.historicalTradesManager.applyFilters === 'function') {
        window.historicalTradesManager.applyFilters();
    } else {
        console.error('❌ historicalTradesManager.applyFilters 方法不可用');
        // 备用方案：直接调用API
        fallbackSorting(sortBy, sortOrder);
    }
}

// 备用排序方案
async function fallbackSorting(sortBy, sortOrder) {
    console.log('🔄 使用备用排序方案...');
    
    try {
        const params = {
            sort_by: sortBy,
            sort_order: sortOrder,
            per_page: 20
        };
        
        const response = await window.apiClient.request('GET', '/historical-trades', { params });
        
        if (response && response.success) {
            console.log('✅ 备用排序请求成功');
            // 更新表格显示
            updateTradesTable(response.data.trades);
        } else {
            console.error('❌ 备用排序请求失败:', response);
        }
    } catch (error) {
        console.error('❌ 备用排序出错:', error);
    }
}

// 更新交易表格
function updateTradesTable(trades) {
    const tbody = document.getElementById('historical-trades-table-body');
    
    if (!tbody) {
        console.error('❌ 表格主体元素未找到');
        return;
    }
    
    if (!trades || trades.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-5">
                    <i class="bi bi-inbox fs-1 d-block mb-3 text-secondary"></i>
                    <h5 class="text-muted">暂无历史交易记录</h5>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = trades.map(trade => `
        <tr>
            <td>
                <div>
                    <strong>${trade.stock_code}</strong>
                    <br>
                    <small class="text-muted">${trade.stock_name}</small>
                </div>
            </td>
            <td>${formatDate(trade.buy_date)}</td>
            <td>${formatDate(trade.sell_date)}</td>
            <td>
                <span class="badge bg-primary">${trade.holding_days}天</span>
            </td>
            <td>
                <span class="text-primary fw-bold">¥${formatNumber(trade.total_investment)}</span>
            </td>
            <td>
                <span class="${trade.total_return >= 0 ? 'text-danger fw-bold' : 'text-success fw-bold'}">
                    ${trade.total_return >= 0 ? '+' : ''}¥${formatNumber(trade.total_return)}
                </span>
            </td>
            <td>
                <span class="${trade.return_rate >= 0 ? 'text-danger fw-bold' : 'text-success fw-bold'}">
                    ${trade.return_rate >= 0 ? '+' : ''}${(trade.return_rate * 100).toFixed(2)}%
                </span>
            </td>
            <td>
                ${trade.has_review ? 
                    `<button class="btn btn-sm btn-outline-primary" onclick="viewReview(${trade.id})" title="查看复盘">
                        <i class="bi bi-eye"></i> 查看
                    </button>` :
                    `<button class="btn btn-sm btn-primary" onclick="addReview(${trade.id})" title="添加复盘">
                        <i class="bi bi-plus"></i> 添加
                    </button>`
                }
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-info" onclick="viewTradeDetails(${trade.id})" title="查看详情">
                        <i class="bi bi-info-circle"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    console.log(`✅ 表格已更新，显示 ${trades.length} 条记录`);
}

// 格式化日期
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
}

// 格式化数字
function formatNumber(num) {
    if (num === null || num === undefined) return '0.00';
    return parseFloat(num).toFixed(2);
}

// 测试排序功能
async function testSortingFunction() {
    console.log('🧪 开始测试排序功能...');
    
    const testCases = [
        { sort_by: 'stock_code', sort_order: 'asc' },
        { sort_by: 'return_rate', sort_order: 'desc' }
    ];
    
    for (const testCase of testCases) {
        try {
            console.log(`测试: ${testCase.sort_by} ${testCase.sort_order}`);
            
            const response = await window.apiClient.request('GET', '/historical-trades', { 
                params: { ...testCase, per_page: 5 } 
            });
            
            if (response && response.success) {
                console.log(`✅ 测试通过: ${testCase.sort_by} ${testCase.sort_order}`);
            } else {
                console.error(`❌ 测试失败: ${testCase.sort_by} ${testCase.sort_order}`, response);
            }
        } catch (error) {
            console.error(`❌ 测试出错: ${testCase.sort_by} ${testCase.sort_order}`, error);
        }
    }
    
    console.log('🧪 排序功能测试完成');
}

// 页面加载完成后自动运行修复
document.addEventListener('DOMContentLoaded', function() {
    // 延迟执行，确保所有脚本都已加载
    setTimeout(() => {
        fixSortingIssue();
    }, 1000);
});

// 手动修复函数（可在控制台调用）
window.fixSorting = fixSortingIssue;