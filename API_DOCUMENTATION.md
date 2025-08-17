# 股票交易记录和复盘系统 - API文档

## 目录
- [API概述](#api概述)
- [认证和错误处理](#认证和错误处理)
- [交易记录API](#交易记录api)
- [复盘记录API](#复盘记录api)
- [股票池API](#股票池api)
- [案例管理API](#案例管理api)
- [统计分析API](#统计分析api)
- [价格服务API](#价格服务api)
- [板块分析API](#板块分析api)
- [策略管理API](#策略管理api)
- [配置管理API](#配置管理api)

## API概述

### 基础信息
- **Base URL**: `http://localhost:5000/api`
- **数据格式**: JSON
- **字符编码**: UTF-8
- **HTTP方法**: GET, POST, PUT, DELETE

### 通用响应格式
```json
{
    "success": true,
    "data": {},
    "message": "操作成功",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### 错误响应格式
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": {}
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## 认证和错误处理

### 错误代码
- `VALIDATION_ERROR`: 数据验证错误
- `NOT_FOUND`: 资源不存在
- `DATABASE_ERROR`: 数据库操作错误
- `EXTERNAL_API_ERROR`: 外部API调用错误
- `FILE_OPERATION_ERROR`: 文件操作错误

### HTTP状态码
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 交易记录API

### 获取交易记录列表
```http
GET /api/trades
```

**查询参数**:
- `page` (int): 页码，默认1
- `per_page` (int): 每页数量，默认20
- `stock_code` (string): 股票代码筛选
- `trade_type` (string): 交易类型筛选 (buy/sell)
- `start_date` (string): 开始日期 (YYYY-MM-DD)
- `end_date` (string): 结束日期 (YYYY-MM-DD)

**响应示例**:
```json
{
    "success": true,
    "data": {
        "trades": [
            {
                "id": 1,
                "stock_code": "000001",
                "stock_name": "平安银行",
                "trade_type": "buy",
                "price": 12.50,
                "quantity": 1000,
                "trade_date": "2024-01-01T09:30:00Z",
                "reason": "少妇B1战法",
                "notes": "技术面突破",
                "stop_loss_price": 11.25,
                "take_profit_ratio": 0.20,
                "sell_ratio": 0.50,
                "expected_loss_ratio": 0.10,
                "expected_profit_ratio": 0.10,
                "is_corrected": false,
                "created_at": "2024-01-01T09:30:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 100,
            "pages": 5
        }
    }
}
```

### 创建交易记录
```http
POST /api/trades
```

**请求体**:
```json
{
    "stock_code": "000001",
    "stock_name": "平安银行",
    "trade_type": "buy",
    "price": 12.50,
    "quantity": 1000,
    "trade_date": "2024-01-01T09:30:00Z",
    "reason": "少妇B1战法",
    "notes": "技术面突破",
    "stop_loss_price": 11.25,
    "take_profit_ratio": 0.20,
    "sell_ratio": 0.50
}
```

### 更新交易记录
```http
PUT /api/trades/{id}
```

### 删除交易记录
```http
DELETE /api/trades/{id}
```

### 订正交易记录
```http
POST /api/trades/{id}/correct
```

**请求体**:
```json
{
    "corrected_data": {
        "price": 12.60,
        "quantity": 1200
    },
    "reason": "价格记录错误"
}
```

### 获取订正历史
```http
GET /api/trades/{id}/history
```

### 计算风险收益比
```http
POST /api/trades/calculate-risk-reward
```

**请求体**:
```json
{
    "buy_price": 12.50,
    "stop_loss_price": 11.25,
    "take_profit_ratio": 0.20,
    "sell_ratio": 0.50
}
```

## 复盘记录API

### 获取复盘记录
```http
GET /api/reviews
```

**查询参数**:
- `stock_code` (string): 股票代码
- `start_date` (string): 开始日期
- `end_date` (string): 结束日期

### 创建复盘记录
```http
POST /api/reviews
```

**请求体**:
```json
{
    "stock_code": "000001",
    "review_date": "2024-01-01",
    "price_up_score": 1,
    "bbi_score": 1,
    "volume_score": 0,
    "trend_score": 1,
    "j_score": 1,
    "analysis": "技术面良好",
    "decision": "hold",
    "reason": "继续观察",
    "holding_days": 5
}
```

### 获取当前持仓
```http
GET /api/holdings
```

### 获取持仓提醒
```http
GET /api/holdings/alerts
```

## 股票池API

### 获取股票池列表
```http
GET /api/stock-pool
```

**查询参数**:
- `pool_type` (string): 池类型 (watch/buy_ready)
- `status` (string): 状态 (active/moved/removed)

### 添加股票到池中
```http
POST /api/stock-pool
```

**请求体**:
```json
{
    "stock_code": "000001",
    "stock_name": "平安银行",
    "pool_type": "watch",
    "target_price": 13.00,
    "add_reason": "技术面突破"
}
```

### 更新股票池状态
```http
PUT /api/stock-pool/{id}
```

### 从池中移除股票
```http
DELETE /api/stock-pool/{id}
```

## 案例管理API

### 获取案例列表
```http
GET /api/cases
```

**查询参数**:
- `stock_code` (string): 股票代码
- `tags` (string): 标签筛选
- `page` (int): 页码
- `per_page` (int): 每页数量

### 上传案例
```http
POST /api/cases
```

**请求体** (multipart/form-data):
- `image`: 图片文件
- `stock_code`: 股票代码
- `title`: 案例标题
- `tags`: 标签 (JSON数组字符串)
- `notes`: 备注

### 更新案例信息
```http
PUT /api/cases/{id}
```

### 删除案例
```http
DELETE /api/cases/{id}
```

## 统计分析API

### 获取总体统计
```http
GET /api/analytics/overview
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "total_trades": 150,
        "total_profit": 25000.00,
        "realized_profit": 18000.00,
        "unrealized_profit": 7000.00,
        "success_rate": 0.65,
        "avg_holding_days": 8.5,
        "total_investment": 500000.00,
        "current_positions": 12
    }
}
```

### 获取月度统计
```http
GET /api/analytics/monthly
```

**查询参数**:
- `year` (int): 年份
- `months` (int): 月份数量

### 获取收益分布
```http
GET /api/analytics/profit-distribution
```

### 导出统计数据
```http
GET /api/analytics/export
```

**查询参数**:
- `format` (string): 导出格式 (excel/csv)
- `start_date` (string): 开始日期
- `end_date` (string): 结束日期

## 价格服务API

### 刷新股票价格
```http
POST /api/prices/refresh
```

**请求体**:
```json
{
    "stock_codes": ["000001", "000002"]
}
```

### 获取股票价格
```http
GET /api/prices/{stock_code}
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "stock_code": "000001",
        "stock_name": "平安银行",
        "current_price": 12.50,
        "change_percent": 2.45,
        "record_date": "2024-01-01",
        "updated_at": "2024-01-01T15:00:00Z"
    }
}
```

## 板块分析API

### 刷新板块数据
```http
POST /api/sectors/refresh
```

### 获取板块排名
```http
GET /api/sectors/ranking
```

**查询参数**:
- `date` (string): 日期 (YYYY-MM-DD)
- `limit` (int): 返回数量限制

### 获取历史板块表现
```http
GET /api/sectors/history
```

**查询参数**:
- `sector_name` (string): 板块名称
- `start_date` (string): 开始日期
- `end_date` (string): 结束日期

### 获取TOPK板块统计
```http
GET /api/sectors/top-performers
```

**查询参数**:
- `days` (int): 天数，默认7
- `top_k` (int): 前K名，默认10

**响应示例**:
```json
{
    "success": true,
    "data": [
        {
            "sector_name": "新能源汽车",
            "appearances": 5,
            "avg_rank": 3.2,
            "best_rank": 1,
            "latest_rank": 4,
            "trend": "up"
        }
    ]
}
```

## 策略管理API

### 获取策略列表
```http
GET /api/strategies
```

### 创建策略
```http
POST /api/strategies
```

**请求体**:
```json
{
    "strategy_name": "激进策略",
    "description": "适合短线操作",
    "rules": {
        "rules": [
            {
                "day_range": [1, 3],
                "loss_threshold": -0.05,
                "action": "sell_all",
                "condition": "loss_exceed"
            }
        ]
    },
    "is_active": true
}
```

### 更新策略
```http
PUT /api/strategies/{id}
```

### 删除策略
```http
DELETE /api/strategies/{id}
```

### 评估策略提醒
```http
POST /api/strategies/evaluate
```

**请求体**:
```json
{
    "stock_code": "000001",
    "holding_days": 5,
    "buy_price": 12.00,
    "current_price": 11.50
}
```

## 配置管理API

### 获取配置
```http
GET /api/config/{config_key}
```

### 更新配置
```http
PUT /api/config/{config_key}
```

**请求体**:
```json
{
    "config_value": ["新选项1", "新选项2"],
    "description": "配置描述"
}
```

### 获取所有配置
```http
GET /api/config
```

## 使用示例

### JavaScript示例
```javascript
// 创建API客户端
class TradingJournalAPI {
    constructor(baseURL = 'http://localhost:5000/api') {
        this.baseURL = baseURL;
    }
    
    async getTrades(params = {}) {
        const url = new URL(`${this.baseURL}/trades`);
        Object.keys(params).forEach(key => 
            url.searchParams.append(key, params[key])
        );
        
        const response = await fetch(url);
        return await response.json();
    }
    
    async createTrade(tradeData) {
        const response = await fetch(`${this.baseURL}/trades`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tradeData)
        });
        return await response.json();
    }
}

// 使用示例
const api = new TradingJournalAPI();

// 获取交易记录
api.getTrades({ stock_code: '000001', page: 1 })
    .then(data => console.log(data));

// 创建交易记录
api.createTrade({
    stock_code: '000001',
    stock_name: '平安银行',
    trade_type: 'buy',
    price: 12.50,
    quantity: 1000,
    reason: '少妇B1战法'
}).then(data => console.log(data));
```

### Python示例
```python
import requests
import json

class TradingJournalAPI:
    def __init__(self, base_url='http://localhost:5000/api'):
        self.base_url = base_url
    
    def get_trades(self, **params):
        response = requests.get(f'{self.base_url}/trades', params=params)
        return response.json()
    
    def create_trade(self, trade_data):
        response = requests.post(
            f'{self.base_url}/trades',
            json=trade_data,
            headers={'Content-Type': 'application/json'}
        )
        return response.json()

# 使用示例
api = TradingJournalAPI()

# 获取交易记录
trades = api.get_trades(stock_code='000001', page=1)
print(trades)

# 创建交易记录
new_trade = api.create_trade({
    'stock_code': '000001',
    'stock_name': '平安银行',
    'trade_type': 'buy',
    'price': 12.50,
    'quantity': 1000,
    'reason': '少妇B1战法'
})
print(new_trade)
```

## 注意事项

1. **数据格式**: 所有日期时间字段使用ISO 8601格式
2. **数值精度**: 价格字段保留2位小数，比例字段保留4位小数
3. **文件上传**: 图片文件大小限制为16MB
4. **缓存**: 股票价格数据有5分钟缓存
5. **并发**: API支持并发请求，但建议控制请求频率
6. **错误处理**: 始终检查响应中的success字段

---

**版本**: v1.0  
**更新日期**: 2024-01-01  
**联系方式**: 请通过GitHub Issues反馈API问题