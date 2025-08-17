# 数据库系统文档

## 概述

股票交易记录和复盘系统的数据库采用SQLite作为存储引擎，使用SQLAlchemy ORM进行数据访问。系统包含完整的表结构、索引优化、数据迁移机制和测试验证功能。

## 数据库表结构

### 核心业务表

#### 1. 交易记录表 (trade_records)
存储所有买入和卖出交易记录，包含止损止盈设置和自动计算字段。

**主要字段：**
- `stock_code`: 股票代码
- `stock_name`: 股票名称  
- `trade_type`: 交易类型 ('buy', 'sell')
- `price`: 交易价格
- `quantity`: 交易数量
- `trade_date`: 交易日期
- `reason`: 操作原因
- `stop_loss_price`: 止损价格
- `take_profit_ratio`: 止盈比例
- `expected_loss_ratio`: 预期亏损比例（自动计算）
- `expected_profit_ratio`: 预期收益比例（自动计算）

**订正功能字段：**
- `is_corrected`: 是否被订正
- `original_record_id`: 原始记录ID
- `correction_reason`: 订正原因

#### 2. 交易记录订正表 (trade_corrections)
记录交易记录的订正历史和变更详情。

#### 3. 复盘记录表 (review_records)
存储持仓股票的每日复盘评分和分析。

**评分字段（每项0-1分）：**
- `price_up_score`: 收盘价上升
- `bbi_score`: 不破BBI线
- `volume_score`: 无放量阴线
- `trend_score`: 趋势还在向上
- `j_score`: J没死叉
- `total_score`: 总分（自动计算）

#### 4. 股票池表 (stock_pool)
管理待观测池和待买入池的股票。

**池类型：**
- `watch`: 待观测池
- `buy_ready`: 待买入池

**状态：**
- `active`: 活跃
- `moved`: 已移动
- `removed`: 已移除

#### 5. 案例研究表 (case_studies)
存储股票走势截图案例和分析标签。

#### 6. 配置表 (configurations)
存储系统配置，如买入卖出原因选项。

#### 7. 股票价格表 (stock_prices)
缓存股票价格数据，支持日期去重。

#### 8. 板块数据表 (sector_data)
存储板块涨跌幅数据和排名信息。

#### 9. 板块排名表 (sector_rankings)
存储完整的板块排名历史数据（JSON格式）。

#### 10. 交易策略表 (trading_strategies)
存储持仓策略规则配置。

## 索引优化

系统创建了多个索引以优化查询性能：

### 单列索引
- 股票代码索引：`stock_code`
- 日期索引：`trade_date`, `review_date`, `record_date`

### 复合索引
- 交易记录复合索引：`(stock_code, trade_type, trade_date DESC)`
- 复盘评分索引：`(total_score DESC, review_date DESC)`
- 板块性能索引：`(change_percent DESC, record_date DESC)`

### 唯一约束
- 复盘记录：`(stock_code, review_date)` - 防止同一股票同一天重复复盘
- 股票价格：`(stock_code, record_date)` - 防止同一股票同一天重复价格记录
- 板块数据：`(sector_name, record_date)` - 防止同一板块同一天重复记录

## 数据库初始化

### 使用方法

```bash
# 初始化数据库（首次运行）
python init_db.py

# 强制重建数据库（会先备份）
python init_db.py --force

# 仅验证数据库结构
python init_db.py --verify

# 备份数据库
python init_db.py --backup
```

### 初始化流程

1. **连接测试**: 验证数据库连接
2. **表创建**: 创建所有业务表
3. **索引创建**: 创建性能优化索引
4. **初始数据**: 插入默认配置和策略
5. **结构验证**: 验证表结构和数据完整性

### 默认初始数据

**买入原因选项：**
- 少妇B1战法
- 少妇SB1战法
- 少妇B2战法
- 单针二十战法

**卖出原因选项：**
- 部分止盈
- 止损
- 下等马/草泥马

**默认交易策略：**
基于持仓天数的动态止损止盈策略，包含多个时间段的风险控制规则。

## 数据库迁移系统

### 迁移命令

```bash
# 查看迁移状态
python db_migration.py status

# 应用所有待处理迁移
python db_migration.py migrate

# 创建新迁移
python db_migration.py create --description "添加新字段"

# 回滚指定迁移
python db_migration.py rollback --version "20241216_000001_initial_schema"

# 重置迁移状态（危险操作）
python db_migration.py reset
```

### 迁移文件结构

迁移文件位于 `migrations/` 目录，命名格式：`YYYYMMDD_HHMMSS_description.py`

每个迁移文件包含：
- `upgrade()`: 应用迁移的SQL语句
- `downgrade()`: 回滚迁移的SQL语句

### 迁移记录

系统自动维护 `schema_migrations` 表记录已应用的迁移：
- `version`: 迁移版本号
- `description`: 迁移描述
- `applied_at`: 应用时间

## 数据库测试

### 运行测试

```bash
# 运行完整的数据库测试套件
python test_database.py
```

### 测试覆盖

1. **连接测试**: 验证数据库连接正常
2. **表结构测试**: 验证所有表已正确创建
3. **模型操作测试**: 测试所有模型的CRUD操作
4. **索引测试**: 验证索引创建和性能
5. **约束测试**: 验证数据完整性约束
6. **数据清理**: 自动清理测试数据

### 测试特性

- **自动计算验证**: 测试止损止盈比例自动计算
- **关系验证**: 测试模型间的外键关系
- **约束验证**: 测试数据类型和值约束
- **唯一性验证**: 测试唯一约束和重复处理
- **JSON字段验证**: 测试JSON字段的序列化和反序列化

## 模型使用示例

### 交易记录操作

```python
# 创建买入记录
trade = TradeRecord(
    stock_code='000001',
    stock_name='平安银行',
    trade_type='buy',
    price=12.50,
    quantity=1000,
    trade_date=datetime.now(),
    reason='少妇B1战法',
    stop_loss_price=11.00,
    take_profit_ratio=0.20,
    sell_ratio=0.50
)
trade.save()

# 查询交易记录
trades = TradeRecord.get_by_stock_code('000001')
recent_trades = TradeRecord.get_by_date_range(start_date, end_date)
```

### 复盘记录操作

```python
# 创建复盘记录
review = ReviewRecord(
    stock_code='000001',
    review_date=date.today(),
    price_up_score=1,
    bbi_score=1,
    volume_score=0,
    trend_score=1,
    j_score=1,
    holding_days=5
)
review.save()  # total_score 自动计算为4

# 更新评分
review.update_scores(volume_score=1)  # total_score 自动更新为5
```

### 股票池操作

```python
# 添加到观察池
stock = StockPool(
    stock_code='000002',
    stock_name='万科A',
    pool_type='watch',
    target_price=25.00,
    add_reason='技术面良好'
)
stock.save()

# 移动到买入池
moved_stock = stock.move_to_pool('buy_ready', '达到买入条件')
```

### 配置管理

```python
# 获取配置
buy_reasons = Configuration.get_buy_reasons()
sell_reasons = Configuration.get_sell_reasons()

# 设置配置
Configuration.set_buy_reasons(['新战法1', '新战法2'])
```

## 性能优化建议

### 查询优化

1. **使用索引**: 查询时尽量使用已建立索引的字段
2. **分页查询**: 大量数据查询时使用分页
3. **选择性查询**: 只查询需要的字段，避免SELECT *
4. **批量操作**: 大量数据插入时使用批量操作

### 索引维护

1. **定期分析**: 分析查询模式，添加必要索引
2. **清理无用索引**: 删除不再使用的索引
3. **复合索引优化**: 根据WHERE条件优化复合索引顺序

### 数据维护

1. **定期备份**: 使用 `init_db.py --backup` 定期备份
2. **数据清理**: 定期清理过期的缓存数据
3. **完整性检查**: 定期运行 `test_database.py` 验证数据完整性

## 故障排除

### 常见问题

1. **表不存在**: 运行 `python init_db.py` 重新初始化
2. **索引错误**: 运行 `python init_db.py --force` 强制重建
3. **数据损坏**: 从备份文件恢复数据库
4. **迁移失败**: 检查迁移文件语法，必要时回滚

### 调试方法

1. **连接测试**: `python init_db.py --verify`
2. **完整测试**: `python test_database.py`
3. **迁移状态**: `python db_migration.py status`
4. **日志分析**: 查看应用日志中的数据库错误信息

## 数据备份与恢复

### 自动备份

系统在强制重建数据库时会自动创建备份文件，格式：
`trading_journal_backup_YYYYMMDD_HHMMSS.db`

### 手动备份

```bash
# 创建备份
python init_db.py --backup

# 或直接复制数据库文件
cp data/trading_journal.db data/backup_$(date +%Y%m%d_%H%M%S).db
```

### 数据恢复

```bash
# 从备份恢复
cp data/trading_journal_backup_20241216_162138.db data/trading_journal.db

# 验证恢复的数据库
python init_db.py --verify
```

## 扩展和定制

### 添加新表

1. 在 `models/` 目录创建新的模型文件
2. 在 `models/__init__.py` 中导入新模型
3. 创建迁移文件添加新表
4. 更新测试脚本验证新表

### 修改现有表

1. 创建迁移文件描述变更
2. 在迁移文件中编写ALTER TABLE语句
3. 更新对应的模型类
4. 运行迁移应用变更
5. 更新测试验证变更

### 性能监控

可以通过以下方式监控数据库性能：

1. **查询日志**: 启用SQLAlchemy查询日志
2. **执行计划**: 分析慢查询的执行计划
3. **索引使用**: 监控索引的使用情况
4. **数据库大小**: 定期检查数据库文件大小

这个数据库系统为股票交易记录和复盘系统提供了完整、可靠、高性能的数据存储解决方案。