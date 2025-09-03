# 历史交易记录 API 文档

## 概述

历史交易记录 API 提供了完整的历史交易数据管理和复盘功能接口。本文档详细描述了所有可用的 API 端点、请求格式、响应格式和错误处理。

## 基础信息

- **Base URL**: `/api`
- **Content-Type**: `application/json`
- **Authentication**: 基于 Session 的身份验证
- **API Version**: v1.0

## 通用响应格式

### 成功响应
```json
{
    "success": true,
    "data": {},
    "message": "操作成功"
}
```

### 错误响应
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": {}
    }
}
```

### HTTP 状态码
- `200` - 请求成功
- `201` - 资源创建成功
- `400` - 请求参数错误
- `401` - 未授权访问
- `404` - 资源不存在
- `500` - 服务器内部错误

## 历史交易 API

### 1. 获取历史交易列表

获取分页的历史交易记录列表，支持多种筛选条件。

**请求**
```http
GET /api/historical-trades
```

**查询参数**
| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| per_page | integer | 否 | 20 | 每页记录数 |
| stock_code | string | 否 | - | 股票代码筛选 |
| stock_name | string | 否 | - | 股票名称筛选 |
| start_date | string | 否 | - | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | - | 结束日期 (YYYY-MM-DD) |
| min_return_rate | float | 否 | - | 最小收益率 |
| max_return_rate | float | 否 | - | 最大收益率 |
| min_holding_days | integer | 否 | - | 最小持仓天数 |
| max_holding_days | integer | 否 | - | 最大持仓天数 |
| sort_by | string | 否 | completion_date | 排序字段 |
| sort_order | string | 否 | desc | 排序方向 (asc/desc) |

**响应示例**
```json
{
    "success": true,
    "data": {
        "trades": [
            {
                "id": 1,
                "stock_code": "000001",
                "stock_name": "平安银行",
                "buy_date": "2024-01-15T09:30:00",
                "sell_date": "2024-01-25T14:30:00",
                "holding_days": 10,
                "total_investment": 10000.00,
                "total_return": 2000.00,
                "return_rate": 0.20,
                "completion_date": "2024-01-25T14:30:00",
                "has_review": true,
                "created_at": "2024-01-25T15:00:00",
                "updated_at": "2024-01-25T15:00:00"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 150,
            "pages": 8,
            "has_prev": false,
            "has_next": true
        }
    }
}
```

### 2. 获取单个历史交易详情

获取指定历史交易的详细信息，包括关联的买入卖出记录。

**请求**
```http
GET /api/historical-trades/{id}
```

**路径参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| id | integer | 是 | 历史交易记录ID |

**响应示例**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "stock_code": "000001",
        "stock_name": "平安银行",
        "buy_date": "2024-01-15T09:30:00",
        "sell_date": "2024-01-25T14:30:00",
        "holding_days": 10,
        "total_investment": 10000.00,
        "total_return": 2000.00,
        "return_rate": 0.20,
        "buy_records": [
            {
                "id": 101,
                "price": 10.00,
                "quantity": 1000,
                "trade_date": "2024-01-15T09:30:00",
                "reason": "技术突破买入"
            }
        ],
        "sell_records": [
            {
                "id": 102,
                "price": 12.00,
                "quantity": 1000,
                "trade_date": "2024-01-25T14:30:00",
                "reason": "止盈卖出"
            }
        ],
        "review": {
            "id": 1,
            "review_title": "平安银行交易复盘",
            "overall_score": 5
        }
    }
}
```

### 3. 同步生成历史交易记录

从现有交易记录中识别已完成的交易并生成历史记录。

**请求**
```http
POST /api/historical-trades/sync
```

**请求体**
```json
{
    "force_update": false,
    "date_range": {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
}
```

**请求参数**
| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| force_update | boolean | 否 | false | 是否强制更新已存在的记录 |
| date_range | object | 否 | - | 同步的日期范围 |

**响应示例**
```json
{
    "success": true,
    "data": {
        "synced_count": 25,
        "updated_count": 3,
        "skipped_count": 2,
        "total_processed": 30
    },
    "message": "历史交易记录同步完成"
}
```

### 4. 删除历史交易记录

删除指定的历史交易记录（谨慎操作）。

**请求**
```http
DELETE /api/historical-trades/{id}
```

**路径参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| id | integer | 是 | 历史交易记录ID |

**响应示例**
```json
{
    "success": true,
    "message": "历史交易记录已删除"
}
```

## 交易复盘 API

### 1. 获取交易复盘

获取指定历史交易的复盘记录。

**请求**
```http
GET /api/trade-reviews/{historical_trade_id}
```

**路径参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| historical_trade_id | integer | 是 | 历史交易记录ID |

**响应示例**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "historical_trade_id": 1,
        "review_title": "平安银行交易复盘",
        "review_content": "这是一次成功的交易...",
        "review_type": "success",
        "strategy_score": 5,
        "timing_score": 4,
        "risk_control_score": 5,
        "overall_score": 5,
        "key_learnings": "严格执行止盈计划很重要",
        "improvement_areas": "可以在更好的时机买入",
        "images": [
            {
                "id": 1,
                "filename": "chart_analysis.png",
                "original_filename": "图表分析.png",
                "description": "技术分析图表",
                "file_url": "/uploads/reviews/chart_analysis.png"
            }
        ],
        "created_at": "2024-01-25T16:00:00",
        "updated_at": "2024-01-25T16:00:00"
    }
}
```

### 2. 创建交易复盘

为指定的历史交易创建复盘记录。

**请求**
```http
POST /api/trade-reviews
```

**请求体**
```json
{
    "historical_trade_id": 1,
    "review_title": "平安银行交易复盘",
    "review_content": "这是一次成功的交易，严格按照计划执行。",
    "review_type": "success",
    "strategy_score": 5,
    "timing_score": 4,
    "risk_control_score": 5,
    "overall_score": 5,
    "key_learnings": "严格执行止盈计划很重要",
    "improvement_areas": "可以在更好的时机买入"
}
```

**请求参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| historical_trade_id | integer | 是 | 历史交易记录ID |
| review_title | string | 否 | 复盘标题 |
| review_content | string | 否 | 复盘内容 |
| review_type | string | 否 | 复盘类型 (general/success/failure/lesson) |
| strategy_score | integer | 否 | 策略执行评分 (1-5) |
| timing_score | integer | 否 | 时机把握评分 (1-5) |
| risk_control_score | integer | 否 | 风险控制评分 (1-5) |
| overall_score | integer | 否 | 总体评分 (1-5) |
| key_learnings | string | 否 | 关键学习点 |
| improvement_areas | string | 否 | 改进领域 |

**响应示例**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "historical_trade_id": 1,
        "review_title": "平安银行交易复盘",
        "overall_score": 5,
        "created_at": "2024-01-25T16:00:00"
    },
    "message": "复盘记录创建成功"
}
```

### 3. 更新交易复盘

更新已存在的复盘记录。

**请求**
```http
PUT /api/trade-reviews/{id}
```

**路径参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| id | integer | 是 | 复盘记录ID |

**请求体**
```json
{
    "review_title": "更新后的复盘标题",
    "review_content": "更新后的复盘内容",
    "overall_score": 4
}
```

**响应示例**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "review_title": "更新后的复盘标题",
        "overall_score": 4,
        "updated_at": "2024-01-25T17:00:00"
    },
    "message": "复盘记录更新成功"
}
```

### 4. 删除交易复盘

删除指定的复盘记录。

**请求**
```http
DELETE /api/trade-reviews/{id}
```

**路径参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| id | integer | 是 | 复盘记录ID |

**响应示例**
```json
{
    "success": true,
    "message": "复盘记录已删除"
}
```

## 复盘图片 API

### 1. 上传复盘图片

为指定的复盘记录上传图片。

**请求**
```http
POST /api/trade-reviews/{review_id}/images
```

**路径参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| review_id | integer | 是 | 复盘记录ID |

**请求体** (multipart/form-data)
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| file | file | 是 | 图片文件 |
| description | string | 否 | 图片描述 |
| display_order | integer | 否 | 显示顺序 |

**文件要求**
- 支持格式：PNG, JPEG, GIF
- 最大文件大小：5MB
- 每个复盘最多10张图片

**响应示例**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "trade_review_id": 1,
        "filename": "20240125_160000_chart.png",
        "original_filename": "图表分析.png",
        "file_url": "/uploads/reviews/20240125_160000_chart.png",
        "file_size": 1024000,
        "mime_type": "image/png",
        "description": "技术分析图表",
        "display_order": 1,
        "created_at": "2024-01-25T16:00:00"
    },
    "message": "图片上传成功"
}
```

### 2. 获取复盘图片列表

获取指定复盘记录的所有图片。

**请求**
```http
GET /api/trade-reviews/{review_id}/images
```

**路径参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| review_id | integer | 是 | 复盘记录ID |

**响应示例**
```json
{
    "success": true,
    "data": {
        "images": [
            {
                "id": 1,
                "filename": "20240125_160000_chart.png",
                "original_filename": "图表分析.png",
                "file_url": "/uploads/reviews/20240125_160000_chart.png",
                "description": "技术分析图表",
                "display_order": 1,
                "created_at": "2024-01-25T16:00:00"
            }
        ],
        "total": 1
    }
}
```

### 3. 更新图片信息

更新图片的描述和显示顺序。

**请求**
```http
PUT /api/trade-reviews/images/{image_id}
```

**路径参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| image_id | integer | 是 | 图片ID |

**请求体**
```json
{
    "description": "更新后的图片描述",
    "display_order": 2
}
```

**响应示例**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "description": "更新后的图片描述",
        "display_order": 2,
        "updated_at": "2024-01-25T17:00:00"
    },
    "message": "图片信息更新成功"
}
```

### 4. 删除复盘图片

删除指定的复盘图片。

**请求**
```http
DELETE /api/trade-reviews/images/{image_id}
```

**路径参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| image_id | integer | 是 | 图片ID |

**响应示例**
```json
{
    "success": true,
    "message": "图片已删除"
}
```

## 统计分析 API

### 1. 获取交易统计

获取历史交易的统计信息。

**请求**
```http
GET /api/historical-trades/statistics
```

**查询参数**
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| start_date | string | 否 | 统计开始日期 |
| end_date | string | 否 | 统计结束日期 |
| group_by | string | 否 | 分组方式 (month/quarter/year) |

**响应示例**
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_trades": 150,
            "profitable_trades": 120,
            "loss_trades": 30,
            "success_rate": 0.80,
            "total_investment": 1500000.00,
            "total_return": 300000.00,
            "average_return_rate": 0.20,
            "average_holding_days": 15
        },
        "monthly_stats": [
            {
                "month": "2024-01",
                "trades_count": 25,
                "total_return": 50000.00,
                "success_rate": 0.84
            }
        ]
    }
}
```

## 错误代码

### 通用错误代码
| 代码 | 描述 |
|------|------|
| INVALID_REQUEST | 请求格式错误 |
| MISSING_PARAMETER | 缺少必需参数 |
| INVALID_PARAMETER | 参数值无效 |
| UNAUTHORIZED | 未授权访问 |
| FORBIDDEN | 禁止访问 |
| NOT_FOUND | 资源不存在 |
| INTERNAL_ERROR | 服务器内部错误 |

### 业务错误代码
| 代码 | 描述 |
|------|------|
| TRADE_NOT_COMPLETED | 交易未完成 |
| REVIEW_ALREADY_EXISTS | 复盘记录已存在 |
| INVALID_SCORE_RANGE | 评分超出有效范围 |
| FILE_TOO_LARGE | 文件大小超出限制 |
| UNSUPPORTED_FILE_TYPE | 不支持的文件类型 |
| UPLOAD_LIMIT_EXCEEDED | 上传数量超出限制 |

## 使用示例

### JavaScript 示例

```javascript
// 获取历史交易列表
async function getHistoricalTrades(page = 1, filters = {}) {
    const params = new URLSearchParams({
        page: page,
        per_page: 20,
        ...filters
    });
    
    const response = await fetch(`/api/historical-trades?${params}`);
    const data = await response.json();
    
    if (data.success) {
        return data.data;
    } else {
        throw new Error(data.error.message);
    }
}

// 创建复盘记录
async function createReview(historicalTradeId, reviewData) {
    const response = await fetch('/api/trade-reviews', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            historical_trade_id: historicalTradeId,
            ...reviewData
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        return data.data;
    } else {
        throw new Error(data.error.message);
    }
}

// 上传复盘图片
async function uploadReviewImage(reviewId, file, description) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', description);
    
    const response = await fetch(`/api/trade-reviews/${reviewId}/images`, {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    
    if (data.success) {
        return data.data;
    } else {
        throw new Error(data.error.message);
    }
}
```

### Python 示例

```python
import requests
import json

class HistoricalTradingAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_historical_trades(self, page=1, **filters):
        """获取历史交易列表"""
        params = {'page': page, 'per_page': 20, **filters}
        response = self.session.get(f'{self.base_url}/api/historical-trades', params=params)
        return response.json()
    
    def create_review(self, historical_trade_id, review_data):
        """创建复盘记录"""
        data = {'historical_trade_id': historical_trade_id, **review_data}
        response = self.session.post(
            f'{self.base_url}/api/trade-reviews',
            json=data
        )
        return response.json()
    
    def upload_image(self, review_id, file_path, description=''):
        """上传复盘图片"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'description': description}
            response = self.session.post(
                f'{self.base_url}/api/trade-reviews/{review_id}/images',
                files=files,
                data=data
            )
        return response.json()

# 使用示例
api = HistoricalTradingAPI('http://localhost:5000')

# 获取历史交易
trades = api.get_historical_trades(page=1, stock_code='000001')

# 创建复盘
review = api.create_review(1, {
    'review_title': '测试复盘',
    'review_content': '复盘内容',
    'overall_score': 4
})

# 上传图片
image = api.upload_image(1, 'chart.png', '技术分析图表')
```

## 版本更新

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础的历史交易和复盘 API

### 计划更新
- 批量操作 API
- 更多统计分析接口
- WebSocket 实时更新
- API 限流和缓存优化