# Requirements Document

## Introduction

股票交易记录和复盘系统是一个个人投资管理工具，帮助用户记录每日交易操作、进行复盘分析、管理股票观察池，并提供收益统计分析。系统采用本地运行的网页形态，数据存储在本地文件中，支持通过Git进行数据同步，为后续扩展为多用户公开网站奠定基础。

## Requirements

### Requirement 1

**User Story:** 作为投资者，我希望能够记录每日的交易操作，以便跟踪我的买卖行为和决策过程。

#### Acceptance Criteria

1. WHEN 用户访问交易记录页面 THEN 系统 SHALL 显示当日交易记录表单
2. WHEN 用户添加买入操作 THEN 系统 SHALL 记录股票代码、股票名称、买入价格、买入数量、买入时间、操作原因、止损价格、止盈设置和备注信息
3. WHEN 用户添加卖出操作 THEN 系统 SHALL 记录股票代码、股票名称、卖出价格、卖出数量、卖出时间、操作原因和备注信息
4. WHEN 用户选择买入原因 THEN 系统 SHALL 提供可配置的原因选项（默认包括：少妇B1战法、少妇SB1战法、少妇B2战法、单针二十战法）
5. WHEN 用户选择卖出原因 THEN 系统 SHALL 提供可配置的原因选项（默认包括：部分止盈、止损、下等马/草泥马）
6. WHEN 用户设置买入止损止盈参数 THEN 系统 SHALL 自动计算预计亏损比例和预计收益率
7. WHEN 用户输入止损价格 THEN 系统 SHALL 基于买入价格自动计算预计亏损比例
8. WHEN 用户设置止盈比例和卖出比例 THEN 系统 SHALL 自动计算预计收益率
9. WHEN 用户发现交易记录错误 THEN 系统 SHALL 提供订正功能允许修改关键交易信息
10. WHEN 用户订正交易记录 THEN 系统 SHALL 保留原始记录并创建新的订正记录，同时记录订正原因
11. WHEN 用户查看交易记录 THEN 系统 SHALL 显示记录是否被订正过，并提供查看订正历史的功能
4. WHEN 用户提交交易记录 THEN 系统 SHALL 保存数据到本地存储文件
5. WHEN 用户查看历史交易记录 THEN 系统 SHALL 按日期倒序显示所有交易操作

### Requirement 2

**User Story:** 作为投资者，我希望能够对持仓股票进行复盘分析和决策记录，以便优化投资策略。

#### Acceptance Criteria

1. WHEN 用户访问复盘页面 THEN 系统 SHALL 显示当前所有持仓股票列表
2. WHEN 用户选择某只持仓股票 THEN 系统 SHALL 显示该股票的持仓成本、当前价格、盈亏情况和持仓天数
3. WHEN 用户进行每日持仓复盘 THEN 系统 SHALL 提供5项评分标准（收盘价上升、不破BBI线、无放量阴线、趋势还在向上、J没死叉），每项1分
4. WHEN 用户完成复盘评分 THEN 系统 SHALL 自动计算总分（满分5分）并记录评分详情
5. WHEN 用户进行复盘分析 THEN 系统 SHALL 允许记录分析内容、决策结果（继续持有/清仓/部分止盈）和理由
6. WHEN 用户保存复盘记录 THEN 系统 SHALL 将复盘数据关联到对应日期和股票
7. WHEN 用户查看持仓提醒 THEN 系统 SHALL 基于配置的策略规则和当前价格生成卖出建议
8. WHEN 系统评估持仓策略 THEN 系统 SHALL 根据持仓天数、盈亏比例和策略规则判断是否触发提醒
9. WHEN 策略规则触发 THEN 系统 SHALL 显示具体的操作建议（清仓/部分卖出）和卖出比例
5. WHEN 用户查看历史复盘 THEN 系统 SHALL 按时间顺序显示复盘记录和决策执行情况

### Requirement 3

**User Story:** 作为投资者，我希望能够管理股票观察池和待买入池，以便跟踪市场机会。

#### Acceptance Criteria

1. WHEN 用户访问股票池管理页面 THEN 系统 SHALL 显示待观测池和待买入池两个分类
2. WHEN 用户添加股票到观察池 THEN 系统 SHALL 记录股票代码、名称、添加原因、目标价位和添加时间
3. WHEN 用户将观察池股票移至待买入池 THEN 系统 SHALL 更新股票状态并记录移动时间和原因
4. WHEN 用户从股票池中移除股票 THEN 系统 SHALL 记录移除时间和原因
5. WHEN 用户查看股票池历史 THEN 系统 SHALL 显示股票在不同池中的流转记录

### Requirement 4

**User Story:** 作为投资者，我希望能够上传和管理股票走势截图，以便建立参考案例库。

#### Acceptance Criteria

1. WHEN 用户访问案例管理页面 THEN 系统 SHALL 提供图片上传功能
2. WHEN 用户上传股票截图 THEN 系统 SHALL 允许添加股票代码、分析标签、备注说明
3. WHEN 用户保存截图案例 THEN 系统 SHALL 将图片转换为通用格式（PNG/JPEG）并存储到本地目录，同时记录元数据
4. WHEN 用户浏览案例库 THEN 系统 SHALL 按时间或标签分类显示所有截图案例
5. WHEN 用户搜索案例 THEN 系统 SHALL 支持按股票代码、标签或时间范围筛选

### Requirement 5

**User Story:** 作为投资者，我希望能够查看整体投资统计分析，以便评估投资表现。

#### Acceptance Criteria

1. WHEN 用户访问统计分析页面 THEN 系统 SHALL 显示总体收益概览
2. WHEN 系统计算收益统计 THEN 系统 SHALL 显示已清仓收益、持仓浮盈浮亏、总收益率
3. WHEN 用户查看收益分布 THEN 系统 SHALL 按盈亏区间显示股票分布情况
4. WHEN 用户查看月度统计 THEN 系统 SHALL 显示每月交易次数、收益情况和成功率
5. WHEN 用户导出统计数据 THEN 系统 SHALL 支持导出Excel格式的统计报表

### Requirement 6

**User Story:** 作为开发者，我希望系统支持本地数据存储和Git同步，以便在不同设备间同步数据。

#### Acceptance Criteria

1. WHEN 系统启动 THEN 系统 SHALL 从本地SQLite数据库加载所有数据
2. WHEN 用户进行任何数据操作 THEN 系统 SHALL 实时保存数据到SQLite数据库
3. WHEN 用户提交代码到Git THEN 系统 SHALL 确保数据文件被包含在版本控制中
4. WHEN 用户在新设备克隆项目 THEN 系统 SHALL 能够从数据文件恢复完整的历史记录
5. IF 数据库不存在 THEN 系统 SHALL 创建初始化的数据库表结构
6. WHEN 用户手动触发价格刷新 THEN 系统 SHALL 通过AKShare库获取最新股票价格并更新数据库

### Requirement 7

**User Story:** 作为开发者，我希望系统采用合适的技术架构，以便实现稳定可靠的功能。

#### Acceptance Criteria

1. WHEN 系统架构设计 THEN 系统 SHALL 采用Python后端提供REST API接口
2. WHEN 数据存储设计 THEN 系统 SHALL 使用SQLite数据库存储所有业务数据
3. WHEN 配置管理设计 THEN 系统 SHALL 支持买入卖出原因选项的配置化管理
4. WHEN 股票价格获取 THEN 系统 SHALL 集成AKShare库实现股票实时价格查询
5. WHEN 图片处理 THEN 系统 SHALL 自动转换上传图片为PNG/JPEG通用格式确保跨平台兼容性

### Requirement 8

**User Story:** 作为投资者，我希望能够分析板块热点情况，以便识别市场机会和趋势。

#### Acceptance Criteria

1. WHEN 用户手动刷新板块数据 THEN 系统 SHALL 通过AKShare库获取最新板块涨跌幅数据并按日期存储
2. WHEN 用户查看板块排名 THEN 系统 SHALL 显示当日板块涨幅排名列表
3. WHEN 用户查询历史板块表现 THEN 系统 SHALL 支持按时间范围查看板块历史排名数据
4. WHEN 用户查看TOPK板块统计 THEN 系统 SHALL 显示最近N天上涨排名TOPK的板块及其进入榜单次数
5. WHEN 系统存储板块数据 THEN 系统 SHALL 确保同一板块同一日期不重复记录，避免数据覆盖
6. WHEN 用户分析板块趋势 THEN 系统 SHALL 提供板块表现的图表可视化展示

### Requirement 9

**User Story:** 作为投资者，我希望能够配置和管理交易策略，以便获得自动化的持仓操作提醒。

#### Acceptance Criteria

1. WHEN 用户创建交易策略 THEN 系统 SHALL 允许配置基于持仓天数的动态止损止盈规则
2. WHEN 用户配置策略规则 THEN 系统 SHALL 支持设置亏损阈值、盈利阈值、回撤阈值和对应操作
3. WHEN 用户启用策略 THEN 系统 SHALL 自动对所有持仓股票应用策略评估
4. WHEN 系统评估持仓 THEN 系统 SHALL 基于当前价格、持仓天数和策略规则生成操作建议
5. WHEN 策略触发提醒 THEN 系统 SHALL 显示具体的股票代码、触发条件、建议操作和卖出比例
6. WHEN 用户修改策略 THEN 系统 SHALL 实时更新所有相关的持仓提醒

### Requirement 10

**User Story:** 作为用户，我希望系统具有良好的用户界面和交互体验，以便高效使用。

#### Acceptance Criteria

1. WHEN 用户访问系统 THEN 系统 SHALL 提供清晰的导航菜单和页面布局
2. WHEN 用户在移动设备访问 THEN 系统 SHALL 提供响应式设计适配不同屏幕尺寸
3. WHEN 用户进行数据输入 THEN 系统 SHALL 提供表单验证和错误提示
4. WHEN 用户操作成功 THEN 系统 SHALL 显示确认消息和状态反馈
5. WHEN 系统加载数据 THEN 系统 SHALL 显示加载状态和进度指示