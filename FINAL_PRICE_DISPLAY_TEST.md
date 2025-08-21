# 成本价和当前价显示修复验证

## 问题回顾
用户反馈：复盘页面的持仓中无法展示出当前价和买入价（成本价）

## 修复内容

### 1. 后端数据修复 (services/review_service.py)
- ✅ 修复平均买入价计算：从简单平均改为加权平均
- ✅ 添加当前价格获取逻辑，集成AKShare价格服务
- ✅ 完善持仓数据结构，包含所有必要字段

### 2. 前端显示修复 (templates/review.html)
- ✅ 修复字段名错误：`holding.buy_price` → `holding.avg_buy_price`
- ✅ 添加浮盈比例计算函数
- ✅ 完善价格显示逻辑

### 3. JavaScript修复 (static/js/review-emergency-fix.js)
- ✅ 统一字段名使用
- ✅ 添加当前价格显示列
- ✅ 修复持仓量字段引用

## 修复验证

### API数据结构验证
```
API返回的持仓数据字段:
  avg_buy_price: 19.45 (float)     ✅ 成本价字段正确
  avg_price: 19.45 (float)         ✅ 兼容字段正确
  current_price: 21.01 (float)     ✅ 当前价字段正确
  current_quantity: 31100 (int)    ✅ 持仓量字段正确
  stock_code: 000776 (str)         ✅ 股票代码正确
  stock_name: 广发证券 (str)        ✅ 股票名称正确
```

### 价格显示逻辑验证
```
前端显示逻辑测试:
  成本价: ¥19.45      ✅ 正确显示
  当前价: ¥21.01      ✅ 正确显示
  浮盈比例: 8.02%     ✅ 正确计算
```

### AKShare价格服务验证
```
测试股票: 000776
  ✅ 刷新成功: 21.01 (广发证券)
```

## 修复后的显示效果

### 持仓列表显示
```
┌─────────────────────────────────────────────────────────────┐
│ 000776                                                      │
│ 广发证券                                                    │
├─────────────┬─────────────┬─────────────┬─────────────┬─────┤
│   成本价    │   当前价    │   持仓量    │   浮盈比例  │操作 │
│  ¥19.45     │  ¥21.01     │   31100     │   +8.02%    │复盘 │
└─────────────┴─────────────┴─────────────┴─────────────┴─────┘
```

### 复盘模态框
- ✅ 自动填入当前价格：¥21.01
- ✅ 显示成本价：¥19.45
- ✅ 实时计算浮盈比例：8.02%

## 技术实现要点

### 1. 加权平均成本价计算
```python
# 修复前：简单平均（错误）
func.avg(TradeRecord.price)

# 修复后：加权平均（正确）
(func.sum(TradeRecord.price * TradeRecord.quantity) / func.sum(TradeRecord.quantity))
```

### 2. AKShare价格集成
```python
def _get_current_price(cls, stock_code: str) -> Optional[float]:
    """获取股票当前价格"""
    price_service = PriceService()
    
    # 优先使用缓存
    price_data = price_service.get_latest_price(stock_code)
    if price_data:
        return float(price_data['current_price'])
    
    # 缓存失效时从AKShare获取
    result = price_service.refresh_stock_price(stock_code)
    if result.get('success'):
        return float(result['data'].get('current_price', 0))
    
    return None
```

### 3. 前端字段统一
```javascript
// 成本价显示逻辑
¥${holding.avg_buy_price ? holding.avg_buy_price.toFixed(2) : 
   (holding.avg_price ? holding.avg_price.toFixed(2) : '--')}

// 当前价显示逻辑  
¥${holding.current_price ? holding.current_price.toFixed(2) : '--'}

// 浮盈比例计算
function calculateProfitRatio(holding) {
    if (!holding.avg_buy_price || !holding.current_price) return '--';
    const ratio = ((holding.current_price - holding.avg_buy_price) / holding.avg_buy_price * 100).toFixed(2);
    return ratio + '%';
}
```

## 用户体验改进

### 修复前
- ❌ 成本价显示"¥--"
- ❌ 当前价显示"¥--"  
- ❌ 无法看到浮盈情况
- ❌ 复盘时需手动输入价格

### 修复后
- ✅ 成本价正确显示"¥19.45"
- ✅ 当前价正确显示"¥21.01"
- ✅ 浮盈比例显示"+8.02%"
- ✅ 复盘时自动填入当前价格
- ✅ 支持实时价格刷新

## 测试文件
1. `test_price_service_integration.py` - 后端集成测试
2. `debug_price_display.html` - 前端调试页面
3. `test_cost_price_display.html` - 成本价显示测试

## 总结
通过本次修复，成功解决了复盘页面持仓中成本价和当前价无法显示的问题：

1. **数据层面**：修复了加权平均成本价计算，集成AKShare获取实时价格
2. **API层面**：完善了持仓数据结构，包含所有必要的价格字段
3. **前端层面**：修复了字段名错误，统一了显示逻辑
4. **用户体验**：现在可以直观看到每只股票的成本价、当前价和浮盈情况

用户现在可以在复盘页面看到完整的价格信息，包括：
- ✅ 买入价（成本价）：通过交易记录计算的加权平均价格
- ✅ 当前价：通过AKShare接口获取的实时价格
- ✅ 浮盈比例：自动计算的盈亏百分比

问题已完全解决！🎉