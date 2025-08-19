# 分批止盈功能设计文档

## 概述

当前系统的止盈设置只支持单一止盈记录，包含止盈比例、卖出比例和预计收益率。本设计将扩展现有架构，支持多个止盈目标的设置和管理，实现分批止盈功能。

## 架构

### 数据库设计

#### 新增表：profit_taking_targets
```sql
CREATE TABLE profit_taking_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_record_id INTEGER NOT NULL,
    target_price DECIMAL(10, 2),
    profit_ratio DECIMAL(5, 4),
    sell_ratio DECIMAL(5, 4) NOT NULL,
    expected_profit_ratio DECIMAL(5, 4),
    sequence_order INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trade_record_id) REFERENCES trade_records(id) ON DELETE CASCADE,
    CHECK (sell_ratio > 0 AND sell_ratio <= 1),
    CHECK (profit_ratio >= 0),
    CHECK (sequence_order > 0)
);

CREATE INDEX idx_profit_targets_trade ON profit_taking_targets(trade_record_id);
CREATE INDEX idx_profit_targets_sequence ON profit_taking_targets(trade_record_id, sequence_order);
```

#### 修改现有表：trade_records
- 保留现有的 `take_profit_ratio`, `sell_ratio`, `expected_profit_ratio` 字段作为兼容性字段
- 添加 `use_batch_profit_taking` 布尔字段，标识是否使用分批止盈

## 组件和接口

### 1. 数据模型层

#### ProfitTakingTarget 模型
```python
class ProfitTakingTarget(BaseModel):
    __tablename__ = 'profit_taking_targets'
    
    trade_record_id = db.Column(db.Integer, db.ForeignKey('trade_records.id'), nullable=False)
    target_price = db.Column(db.Numeric(10, 2))
    profit_ratio = db.Column(db.Numeric(5, 4))
    sell_ratio = db.Column(db.Numeric(5, 4), nullable=False)
    expected_profit_ratio = db.Column(db.Numeric(5, 4))
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    
    # 关系
    trade_record = db.relationship('TradeRecord', backref='profit_targets')
```

#### TradeRecord 模型扩展
```python
class TradeRecord(BaseModel):
    # 新增字段
    use_batch_profit_taking = db.Column(db.Boolean, default=False)
    
    # 新增方法
    def calculate_total_expected_profit(self):
        """计算所有止盈目标的总预期收益率"""
        
    def validate_profit_targets(self):
        """验证止盈目标设置的合理性"""
```

### 2. 服务层

#### ProfitTakingService
```python
class ProfitTakingService:
    @classmethod
    def create_profit_targets(cls, trade_id: int, targets: List[Dict]) -> List[ProfitTakingTarget]
    
    @classmethod
    def update_profit_targets(cls, trade_id: int, targets: List[Dict]) -> List[ProfitTakingTarget]
    
    @classmethod
    def validate_targets_total_ratio(cls, targets: List[Dict]) -> bool
    
    @classmethod
    def calculate_targets_expected_profit(cls, buy_price: float, targets: List[Dict]) -> Dict
```

#### TradingService 扩展
```python
class TradingService:
    @classmethod
    def create_trade_with_batch_profit(cls, data: Dict) -> TradeRecord
    
    @classmethod
    def update_trade_profit_targets(cls, trade_id: int, targets: List[Dict]) -> TradeRecord
```

### 3. API层

#### 新增路由
```python
# 获取交易记录的止盈目标
@api_bp.route('/trades/<int:trade_id>/profit-targets', methods=['GET'])

# 设置/更新交易记录的止盈目标
@api_bp.route('/trades/<int:trade_id>/profit-targets', methods=['PUT'])

# 计算分批止盈预期收益
@api_bp.route('/trades/calculate-batch-profit', methods=['POST'])
```

### 4. 前端组件

#### ProfitTargetsManager 组件
- 动态添加/删除止盈目标行
- 实时计算总体预期收益率
- 验证止盈比例总和
- 支持拖拽排序

#### 前端数据结构
```javascript
const profitTargets = [
    {
        id: null, // 新增时为null
        targetPrice: 0,
        profitRatio: 0,
        sellRatio: 0,
        expectedProfitRatio: 0,
        sequenceOrder: 1
    }
];
```

## 数据模型

### 止盈目标数据模型
```json
{
    "id": 1,
    "trade_record_id": 123,
    "target_price": 21.50,
    "profit_ratio": 0.20,
    "sell_ratio": 0.30,
    "expected_profit_ratio": 0.06,
    "sequence_order": 1,
    "created_at": "2025-01-16T10:00:00Z",
    "updated_at": "2025-01-16T10:00:00Z"
}
```

### 交易记录扩展数据模型
```json
{
    "id": 123,
    "stock_code": "000001",
    "use_batch_profit_taking": true,
    "profit_targets": [
        {
            "target_price": 21.50,
            "profit_ratio": 0.20,
            "sell_ratio": 0.30,
            "expected_profit_ratio": 0.06,
            "sequence_order": 1
        },
        {
            "target_price": 22.00,
            "profit_ratio": 0.25,
            "sell_ratio": 0.40,
            "expected_profit_ratio": 0.10,
            "sequence_order": 2
        }
    ],
    "total_expected_profit_ratio": 0.16,
    "total_sell_ratio": 0.70
}
```

## 错误处理

### 验证规则
1. 所有止盈目标的卖出比例总和不能超过100%
2. 止盈价格必须大于买入价格
3. 卖出比例必须在0-100%之间
4. 止盈比例必须大于等于0
5. 至少需要设置一个止盈目标

### 错误响应格式
```json
{
    "success": false,
    "message": "止盈设置验证失败",
    "errors": {
        "profit_targets": [
            {
                "index": 0,
                "field": "sell_ratio",
                "message": "卖出比例必须在0-100%之间"
            }
        ],
        "total_sell_ratio": "所有止盈目标的卖出比例总和不能超过100%"
    }
}
```

## 测试策略

### 单元测试
1. ProfitTakingTarget 模型验证测试
2. ProfitTakingService 业务逻辑测试
3. 止盈目标计算算法测试
4. 数据验证规则测试

### 集成测试
1. API 端点功能测试
2. 数据库操作测试
3. 前后端数据交互测试

### 前端测试
1. 动态添加/删除止盈目标测试
2. 实时计算功能测试
3. 表单验证测试
4. 用户交互测试

### 兼容性测试
1. 现有单一止盈记录的兼容性测试
2. 数据迁移测试
3. 新旧功能切换测试

## 实现细节

### 数据迁移策略
1. 为现有交易记录设置 `use_batch_profit_taking = false`
2. 保留现有的止盈字段，确保向后兼容
3. 提供数据迁移工具，将单一止盈转换为分批止盈

### 前端UI设计
1. 在买入设置区域添加"分批止盈"开关
2. 开启分批止盈时，显示动态止盈目标列表
3. 每行包含：止盈价格、止盈比例、卖出比例、删除按钮
4. 底部显示"添加止盈目标"按钮和总体统计信息

### 性能考虑
1. 使用数据库事务确保止盈目标的原子性操作
2. 前端使用防抖技术减少实时计算频率
3. 合理使用数据库索引优化查询性能