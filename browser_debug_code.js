
// === 在浏览器控制台中运行这段代码 ===

console.log("🔍 开始调试 Analytics 页面...");

// 1. 检查当前页面
console.log("📍 当前页面:", window.location.pathname);

// 2. 检查关键元素是否存在
const elements = [
    'total-return-rate',
    'success-rate', 
    'closed-profit',
    'holding-profit'
];

console.log("🔍 检查页面元素:");
elements.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
        console.log(`✅ ${id}: "${element.textContent}"`);
    } else {
        console.log(`❌ 未找到元素: ${id}`);
    }
});

// 3. 检查 API 客户端
console.log("🔍 检查 API 客户端:");
if (typeof window.apiClient !== 'undefined') {
    console.log("✅ apiClient 存在");
} else {
    console.log("❌ apiClient 不存在");
}

// 4. 检查 AnalyticsManager
console.log("🔍 检查 AnalyticsManager:");
if (typeof window.analyticsManager !== 'undefined') {
    console.log("✅ analyticsManager 存在");
} else {
    console.log("❌ analyticsManager 不存在");
}

// 5. 手动测试 API
console.log("🔍 手动测试 API...");
fetch('/api/analytics/overview')
    .then(response => response.json())
    .then(data => {
        console.log("📦 API 响应:", data);
        
        if (data.success && data.data) {
            const analytics = data.data;
            console.log("🔍 关键数据:");
            console.log(`  total_return_rate: ${analytics.total_return_rate} (${typeof analytics.total_return_rate})`);
            console.log(`  success_rate: ${analytics.success_rate} (${typeof analytics.success_rate})`);
            console.log(`  closed_profit: ${analytics.closed_profit} (${typeof analytics.closed_profit})`);
            console.log(`  holding_profit: ${analytics.holding_profit} (${typeof analytics.holding_profit})`);
            
            // 6. 手动更新显示
            console.log("🎨 手动更新显示...");
            
            const returnRateElement = document.getElementById('total-return-rate');
            const successRateElement = document.getElementById('success-rate');
            const closedProfitElement = document.getElementById('closed-profit');
            const holdingProfitElement = document.getElementById('holding-profit');
            
            if (returnRateElement) {
                const newValue = `${(analytics.total_return_rate * 100).toFixed(2)}%`;
                console.log(`📝 更新总收益率: ${returnRateElement.textContent} → ${newValue}`);
                returnRateElement.textContent = newValue;
            }
            
            if (successRateElement) {
                const newValue = `${(analytics.success_rate * 100).toFixed(1)}%`;
                console.log(`📝 更新成功率: ${successRateElement.textContent} → ${newValue}`);
                successRateElement.textContent = newValue;
            }
            
            if (closedProfitElement) {
                const newValue = `¥${analytics.closed_profit.toFixed(2)}`;
                console.log(`📝 更新已清仓收益: ${closedProfitElement.textContent} → ${newValue}`);
                closedProfitElement.textContent = newValue;
            }
            
            if (holdingProfitElement) {
                const newValue = `¥${analytics.holding_profit.toFixed(2)}`;
                console.log(`📝 更新持仓收益: ${holdingProfitElement.textContent} → ${newValue}`);
                holdingProfitElement.textContent = newValue;
            }
            
            console.log("✅ 手动更新完成！检查页面显示是否正确。");
        }
    })
    .catch(error => {
        console.error("❌ API 请求失败:", error);
    });

console.log("🔍 调试代码执行完成。请查看上面的输出结果。");
