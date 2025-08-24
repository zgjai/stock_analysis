# 设计文档

## 概述

本设计文档描述了复盘功能增强的技术实现方案，包括可编辑持仓天数、保存功能和当前价格浮盈计算三个核心功能。设计遵循现有系统架构，通过扩展现有API和前端组件来实现新功能。

## 架构

### 系统架构图

```
前端 (review.html)
    ↓ API调用
后端 API (review_routes.py)
    ↓ 服务层调用
业务服务 (review_service.py)
    ↓ 数据访问
数据模型 (review_record.py, trade_record.py)
    ↓ 持久化
数据库 (SQLite)
```

### 数据流

1. **持仓天数编辑流程**：
   - 用户点击编辑 → 前端显示编辑框 → 用户输入 → 前端验证 → API调用 → 后端验证 → 数据库更新 → 响应返回 → 前端更新显示

2. **复盘保存流程**：
   - 用户填写复盘数据 → 前端收集数据 → 数据验证 → API调用 → 后端处理 → 数据库保存 → 成功响应 → 前端确认

3. **浮盈计算流程**：
   - 用户输入当前价格 → 前端实时验证 → 获取成本价 → 计算浮盈比例 → 实时显示结果

## 组件和接口

### 前端组件

#### 1. 持仓天数编辑组件
```javascript
class HoldingDaysEditor {
    constructor(stockCode, currentDays) {
        this.stockCode = stockCode;
        this.currentDays = currentDays;
        this.isEditing = false;
    }
    
    // 进入编辑模式
    enterEditMode() { }
    
    // 保存更改
    async saveChanges(newDays) { }
    
    // 取消编辑
    cancelEdit() { }
    
    // 验证输入
    validateInput(days) { }
}
```

#### 2. 复盘保存管理器
```javascript
class ReviewSaveManager {
    constructor(reviewForm) {
        this.form = reviewForm;
        this.hasUnsavedChanges = false;
        this.autoSaveTimer = null;
    }
    
    // 检测表单变化
    detectChanges() { }
    
    // 保存复盘数据
    async saveReview() { }
    
    // 自动保存
    enableAutoSave() { }
    
    // 离开页面警告
    setupBeforeUnloadWarning() { }
}
```

#### 3. 浮盈计算器
```javascript
class FloatingProfitCalculator {
    constructor(buyPrice) {
        this.buyPrice = buyPrice;
        this.currentPrice = null;
        this.profitRatio = 0;
    }
    
    // 设置当前价格
    setCurrentPrice(price) { }
    
    // 计算浮盈比例
    calculateProfitRatio() { }
    
    // 格式化显示
    formatDisplay() { }
    
    // 更新UI颜色
    updateDisplayColor() { }
}
```

### 后端API接口

#### 1. 持仓天数更新API
```python
@api_bp.route('/holdings/<string:stock_code>/days', methods=['PUT'])
def update_holding_days(stock_code):
    """
    更新持仓天数
    
    请求体:
    {
        "holding_days": 15
    }
    
    响应:
    {
        "success": true,
        "data": {
            "stock_code": "000001",
            "holding_days": 15,
            "updated_at": "2025-01-19T10:30:00"
        },
        "message": "持仓天数更新成功"
    }
    """
```

#### 2. 复盘保存API (扩展现有)
```python
@api_bp.route('/reviews', methods=['POST'])
@api_bp.route('/reviews/<int:review_id>', methods=['PUT'])
def save_review(review_id=None):
    """
    创建或更新复盘记录
    
    请求体:
    {
        "stock_code": "000001",
        "review_date": "2025-01-19",
        "holding_days": 15,
        "current_price": 12.50,
        "floating_profit_ratio": 0.0833,
        "price_up_score": 1,
        "bbi_score": 1,
        "volume_score": 0,
        "trend_score": 1,
        "j_score": 1,
        "analysis": "技术面良好，继续持有",
        "decision": "hold",
        "reason": "符合持有条件"
    }
    """
```

#### 3. 浮盈计算API
```python
@api_bp.route('/reviews/calculate-floating-profit', methods=['POST'])
def calculate_floating_profit():
    """
    计算浮盈比例
    
    请求体:
    {
        "stock_code": "000001",
        "current_price": 12.50
    }
    
    响应:
    {
        "success": true,
        "data": {
            "stock_code": "000001",
            "buy_price": 11.50,
            "current_price": 12.50,
            "floating_profit_ratio": 0.0870,
            "floating_profit_amount": 1.00,
            "formatted_ratio": "+8.70%"
        }
    }
    """
```

## 数据模型

### 复盘记录模型扩展
```python
class ReviewRecord(BaseModel):
    # 现有字段...
    
    # 新增字段
    current_price = db.Column(db.Numeric(10, 2))  # 当前价格
    floating_profit_ratio = db.Column(db.Numeric(5, 4))  # 浮盈比例
    buy_price = db.Column(db.Numeric(10, 2))  # 成本价（冗余存储，便于计算）
    
    def calculate_floating_profit(self, current_price):
        """计算浮盈比例"""
        if not self.buy_price or not current_price:
            return None
        
        profit_ratio = (current_price - self.buy_price) / self.buy_price
        self.current_price = current_price
        self.floating_profit_ratio = profit_ratio
        return profit_ratio
```

### 持仓信息扩展
```python
class HoldingInfo:
    """持仓信息数据传输对象"""
    def __init__(self, stock_code, buy_price, current_price=None):
        self.stock_code = stock_code
        self.buy_price = buy_price
        self.current_price = current_price
        self.floating_profit_ratio = None
        
    def update_current_price(self, price):
        """更新当前价格并计算浮盈"""
        self.current_price = price
        if self.buy_price:
            self.floating_profit_ratio = (price - self.buy_price) / self.buy_price
```

## 错误处理

### 前端错误处理
```javascript
class ReviewErrorHandler {
    static handleSaveError(error) {
        const errorMap = {
            'VALIDATION_ERROR': '数据验证失败，请检查输入',
            'NETWORK_ERROR': '网络连接失败，请重试',
            'SERVER_ERROR': '服务器错误，请稍后重试'
        };
        
        const message = errorMap[error.code] || error.message;
        showMessage(message, 'error');
    }
    
    static handleCalculationError(error) {
        console.error('浮盈计算错误:', error);
        return {
            ratio: null,
            display: '计算失败',
            color: 'text-muted'
        };
    }
}
```

### 后端错误处理
```python
class ReviewValidationError(ValidationError):
    """复盘数据验证错误"""
    pass

class HoldingDaysUpdateError(DatabaseError):
    """持仓天数更新错误"""
    pass

def handle_review_errors(func):
    """复盘相关错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ReviewValidationError as e:
            return create_error_response(e.message, 'VALIDATION_ERROR', 400)
        except HoldingDaysUpdateError as e:
            return create_error_response(e.message, 'UPDATE_ERROR', 500)
    return wrapper
```

## 测试策略

### 单元测试
1. **持仓天数更新测试**
   - 有效输入测试
   - 无效输入验证
   - 数据库更新验证
   - 错误处理测试

2. **浮盈计算测试**
   - 正收益计算
   - 负收益计算
   - 边界值测试
   - 精度测试

3. **复盘保存测试**
   - 完整数据保存
   - 部分数据保存
   - 数据验证测试
   - 并发保存测试

### 集成测试
1. **前后端集成测试**
   - API调用测试
   - 数据传输测试
   - 错误响应测试

2. **用户界面测试**
   - 交互流程测试
   - 实时计算测试
   - 表单验证测试

### 性能测试
1. **响应时间测试**
   - API响应时间 < 500ms
   - 浮盈计算响应 < 100ms
   - 页面加载时间 < 2s

2. **并发测试**
   - 多用户同时编辑
   - 大量数据加载
   - 频繁计算操作

## 安全考虑

### 数据验证
- 前端输入验证
- 后端数据验证
- SQL注入防护
- XSS攻击防护

### 权限控制
- 用户身份验证
- 数据访问权限
- 操作日志记录

### 数据完整性
- 事务处理
- 数据备份
- 回滚机制

## 部署考虑

### 数据库迁移
```sql
-- 添加新字段到复盘记录表
ALTER TABLE review_records 
ADD COLUMN current_price DECIMAL(10,2),
ADD COLUMN floating_profit_ratio DECIMAL(5,4),
ADD COLUMN buy_price DECIMAL(10,2);

-- 创建索引
CREATE INDEX idx_review_current_price ON review_records(current_price);
```

### 配置更新
- API路由注册
- 前端资源更新
- 缓存策略调整

### 监控指标
- API调用成功率
- 响应时间监控
- 错误率统计
- 用户使用情况