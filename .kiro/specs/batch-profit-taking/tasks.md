# 分批止盈功能实现计划

- [x] 1. 创建数据库模型和迁移
  - 创建 ProfitTakingTarget 数据模型类
  - 实现模型验证方法和关系定义
  - 创建数据库迁移脚本，添加 profit_taking_targets 表
  - 为 trade_records 表添加 use_batch_profit_taking 字段
  - _需求: 1.1, 1.2, 2.1_

- [x] 2. 扩展 TradeRecord 模型功能
  - 在 TradeRecord 模型中添加 use_batch_profit_taking 字段
  - 实现 calculate_total_expected_profit 方法
  - 实现 validate_profit_targets 方法
  - 添加与 ProfitTakingTarget 的关系定义
  - _需求: 1.3, 2.1, 4.4_

- [x] 3. 实现 ProfitTakingService 服务类
  - 创建 ProfitTakingService 类，实现止盈目标的 CRUD 操作
  - 实现 create_profit_targets 方法
  - 实现 update_profit_targets 方法
  - 实现 validate_targets_total_ratio 验证方法
  - 实现 calculate_targets_expected_profit 计算方法
  - _需求: 1.1, 1.4, 2.2, 4.1, 4.2, 4.3_

- [x] 4. 扩展 TradingService 支持分批止盈
  - 修改 create_trade 方法支持分批止盈数据
  - 实现 create_trade_with_batch_profit 方法
  - 实现 update_trade_profit_targets 方法
  - 修改 calculate_risk_reward 方法支持多个止盈目标
  - _需求: 1.1, 1.2, 2.2_

- [x] 5. 创建分批止盈相关 API 路由
  - 实现 GET /trades/<id>/profit-targets 获取止盈目标接口
  - 实现 PUT /trades/<id>/profit-targets 设置止盈目标接口
  - 实现 POST /trades/calculate-batch-profit 计算分批止盈接口
  - 修改现有交易记录 API 支持分批止盈数据
  - _需求: 1.1, 1.2, 2.1, 2.2_

- [x] 6. 实现前端分批止盈组件
  - 创建 ProfitTargetsManager JavaScript 组件
  - 实现动态添加/删除止盈目标行功能
  - 实现实时计算总体预期收益率功能
  - 实现止盈比例总和验证功能
  - _需求: 1.1, 1.2, 2.2, 4.3_

- [x] 7. 修改交易记录表单界面
  - 在买入设置区域添加"分批止盈"开关
  - 集成 ProfitTargetsManager 组件到交易表单
  - 实现单一止盈和分批止盈模式切换
  - 更新表单验证逻辑支持分批止盈
  - _需求: 1.1, 3.1, 3.2, 4.4_

- [x] 8. 实现前端数据交互逻辑
  - 修改交易记录保存逻辑支持分批止盈数据
  - 实现止盈目标数据的前后端同步
  - 添加分批止盈相关的错误处理和用户提示
  - 实现编辑模式下的止盈目标数据回填
  - _需求: 1.4, 2.2, 3.2, 4.4_

- [x] 9. 实现数据验证和错误处理
  - 在后端实现完整的止盈目标数据验证
  - 实现前端实时验证和错误提示
  - 添加止盈比例总和超过100%的警告处理
  - 实现止盈价格和买入价格的关系验证
  - _需求: 4.1, 4.2, 4.3, 4.4_

- [x] 10. 编写单元测试
  - 为 ProfitTakingTarget 模型编写单元测试
  - 为 ProfitTakingService 编写业务逻辑测试
  - 为分批止盈 API 接口编写测试
  - 为止盈计算算法编写测试用例
  - _需求: 1.1, 1.2, 2.1, 2.2_

- [x] 11. 实现数据兼容性处理
  - 为现有交易记录设置默认的 use_batch_profit_taking = false
  - 实现单一止盈和分批止盈数据的兼容性处理
  - 确保现有功能不受影响
  - 提供数据迁移工具（可选）
  - _需求: 3.1, 3.2_

- [x] 12. 集成测试和功能验证
  - 测试完整的分批止盈创建流程
  - 测试分批止盈编辑和更新流程
  - 验证止盈目标计算的准确性
  - 测试错误处理和用户体验
  - _需求: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3.1, 3.2_