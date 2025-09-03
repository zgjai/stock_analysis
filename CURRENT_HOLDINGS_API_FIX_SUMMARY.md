# 当前持仓API路径修复总结

## 问题描述
在点击"添加卖出记录"时，无法加载当前持仓数据，控制台出现404错误：
```
GET http://localhost:5001/api/api/trades/current-holdings 404 (NOT FOUND)
```

## 问题原因
API客户端的baseURL设置为`/api`，但在调用时又传入了`/api/trades/current-holdings`，导致最终URL变成了`/api/api/trades/current-holdings`（重复了`/api`）。

## 修复方案
修改`templates/trading_records.html`中的`loadCurrentHoldings`函数，将API调用路径从：
```javascript
const response = await apiClient.request('GET', '/api/trades/current-holdings');
```

修改为：
```javascript
const response = await apiClient.request('GET', '/trades/current-holdings');
```

## 修复详情
- **文件**: `templates/trading_records.html`
- **函数**: `loadCurrentHoldings()`
- **行数**: 约2951行
- **修改**: 去掉API路径前的`/api`前缀

## 验证方法
1. 启动服务器
2. 访问交易记录页面
3. 点击"添加卖出记录"按钮
4. 检查是否能正常加载当前持仓数据
5. 确认控制台不再出现404错误

## 相关API端点
- **路由**: `GET /api/trades/current-holdings`
- **文件**: `api/trading_routes.py`
- **功能**: 获取当前持仓列表，用于卖出操作的股票选择

## 测试文件
创建了`test_current_holdings_fix.html`用于独立测试API修复效果。

## 状态
✅ 已修复 - API路径重复问题已解决