"""
数据库连接和表结构测试脚本
"""
import sys
from datetime import datetime, date
from app import create_app
from extensions import db
from models import *


def test_database_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    try:
        app = create_app()
        with app.app_context():
            # 执行简单查询
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1 as test")).fetchone()
                if result and result[0] == 1:
                    print("✓ 数据库连接成功")
                    return True
                else:
                    print("✗ 数据库连接失败")
                    return False
    except Exception as e:
        print(f"✗ 数据库连接异常: {e}")
        return False


def test_table_creation():
    """测试表创建"""
    print("\n=== 测试表创建 ===")
    try:
        app = create_app()
        with app.app_context():
            # 获取所有表名
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = [
                'trade_records', 'trade_corrections', 'review_records', 'stock_pool',
                'case_studies', 'configurations', 'stock_prices', 'sector_data',
                'sector_rankings', 'trading_strategies'
            ]
            
            print(f"数据库中的表: {tables}")
            
            missing_tables = [table for table in expected_tables if table not in tables]
            if missing_tables:
                print(f"✗ 缺少表: {missing_tables}")
                return False
            
            print("✓ 所有必需的表都已创建")
            return True
    except Exception as e:
        print(f"✗ 表创建测试失败: {e}")
        return False


def test_model_operations():
    """测试模型基本操作"""
    print("\n=== 测试模型操作 ===")
    try:
        app = create_app()
        with app.app_context():
            # 测试配置模型
            print("测试配置模型...")
            config = Configuration.set_value('test_key', 'test_value', '测试配置')
            retrieved_value = Configuration.get_value('test_key')
            assert retrieved_value == 'test_value', "配置值不匹配"
            print("✓ 配置模型测试通过")
            
            # 测试交易记录模型
            print("测试交易记录模型...")
            trade = TradeRecord(
                stock_code='000001',
                stock_name='平安银行',
                trade_type='buy',
                price=12.50,
                quantity=1000,
                trade_date=datetime.now(),
                reason='测试买入',
                stop_loss_price=11.00,
                take_profit_ratio=0.20,
                sell_ratio=0.50
            )
            trade.save()
            
            # 验证自动计算字段
            assert trade.expected_loss_ratio is not None, "预期亏损比例未计算"
            assert trade.expected_profit_ratio is not None, "预期收益比例未计算"
            print("✓ 交易记录模型测试通过")
            
            # 测试复盘记录模型
            print("测试复盘记录模型...")
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
            review.save()
            
            # 验证总分计算
            assert review.total_score == 4, f"总分计算错误，期望4，实际{review.total_score}"
            print("✓ 复盘记录模型测试通过")
            
            # 测试股票池模型
            print("测试股票池模型...")
            stock_pool = StockPool(
                stock_code='000002',
                stock_name='万科A',
                pool_type='watch',
                target_price=25.00,
                add_reason='技术面良好'
            )
            stock_pool.save()
            
            # 测试池间移动
            moved_stock = stock_pool.move_to_pool('buy_ready', '达到买入条件')
            assert moved_stock.pool_type == 'buy_ready', "股票池移动失败"
            assert stock_pool.status == 'moved', "原记录状态未更新"
            print("✓ 股票池模型测试通过")
            
            # 测试案例研究模型
            print("测试案例研究模型...")
            case = CaseStudy(
                stock_code='000001',
                title='测试案例',
                image_path='/test/path.jpg',
                tags=['技术分析', '突破'],
                notes='测试案例说明'
            )
            case.save()
            
            # 验证标签处理
            assert len(case.tags_list) == 2, "标签列表长度不正确"
            assert '技术分析' in case.tags_list, "标签内容不正确"
            print("✓ 案例研究模型测试通过")
            
            # 测试股票价格模型
            print("测试股票价格模型...")
            price = StockPrice.update_or_create(
                stock_code='000001',
                stock_name='平安银行',
                current_price=12.80,
                change_percent=2.40,
                record_date=date.today()
            )
            
            # 测试重复日期更新
            updated_price = StockPrice.update_or_create(
                stock_code='000001',
                stock_name='平安银行',
                current_price=12.90,
                change_percent=3.20,
                record_date=date.today()
            )
            
            assert price.id == updated_price.id, "重复日期应该更新而不是创建新记录"
            assert float(updated_price.current_price) == 12.90, "价格更新失败"
            print("✓ 股票价格模型测试通过")
            
            # 测试板块数据模型
            print("测试板块数据模型...")
            sector = SectorData(
                sector_name='银行',
                change_percent=1.50,
                record_date=date.today(),
                rank_position=5
            )
            sector.save()
            
            # 测试重复检查
            duplicate_check = SectorData.has_data_for_date(date.today())
            assert duplicate_check == True, "重复日期检查失败"
            print("✓ 板块数据模型测试通过")
            
            # 测试交易策略模型
            print("测试交易策略模型...")
            strategy = TradingStrategy(
                strategy_name='测试策略',
                description='测试用策略'
            )
            test_rules = {
                "rules": [
                    {"day_range": [1, 5], "loss_threshold": -0.05, "action": "sell_all"}
                ]
            }
            strategy.rules_list = test_rules
            strategy.save()
            
            # 验证规则解析
            assert len(strategy.rules_list['rules']) == 1, "策略规则解析失败"
            print("✓ 交易策略模型测试通过")
            
            print("✓ 所有模型操作测试通过")
            return True
            
    except Exception as e:
        print(f"✗ 模型操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_indexes():
    """测试索引创建"""
    print("\n=== 测试索引 ===")
    try:
        app = create_app()
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            # 检查主要表的索引
            tables_to_check = ['trade_records', 'review_records', 'stock_pool', 'sector_data']
            
            for table in tables_to_check:
                try:
                    indexes = inspector.get_indexes(table)
                    print(f"{table} 表的索引: {[idx['name'] for idx in indexes]}")
                except Exception as e:
                    print(f"{table} 表索引检查失败: {e}")
            
            print("✓ 索引检查完成")
            return True
    except Exception as e:
        print(f"✗ 索引测试失败: {e}")
        return False


def test_constraints():
    """测试约束条件"""
    print("\n=== 测试约束条件 ===")
    try:
        app = create_app()
        with app.app_context():
            # 测试交易类型约束
            try:
                invalid_trade = TradeRecord(
                    stock_code='000001',
                    stock_name='测试',
                    trade_type='invalid',  # 无效的交易类型
                    price=10.00,
                    quantity=100,
                    trade_date=datetime.now(),
                    reason='测试'
                )
                invalid_trade.save()
                print("✗ 交易类型约束未生效")
                return False
            except Exception:
                print("✓ 交易类型约束正常")
            
            # 测试复盘评分约束
            try:
                invalid_review = ReviewRecord(
                    stock_code='000001',
                    review_date=date.today(),
                    price_up_score=2,  # 无效的评分（应该是0或1）
                    bbi_score=1,
                    volume_score=1,
                    trend_score=1,
                    j_score=1
                )
                invalid_review.save()
                print("✗ 复盘评分约束未生效")
                return False
            except Exception:
                print("✓ 复盘评分约束正常")
            
            print("✓ 约束条件测试通过")
            return True
    except Exception as e:
        print(f"✗ 约束条件测试失败: {e}")
        return False


def cleanup_test_data():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    try:
        app = create_app()
        with app.app_context():
            # 删除测试数据
            db.session.query(TradeRecord).filter_by(stock_code='000001').delete()
            db.session.query(ReviewRecord).filter_by(stock_code='000001').delete()
            db.session.query(StockPool).filter_by(stock_code='000002').delete()
            db.session.query(CaseStudy).filter_by(stock_code='000001').delete()
            db.session.query(StockPrice).filter_by(stock_code='000001').delete()
            db.session.query(SectorData).filter_by(sector_name='银行').delete()
            db.session.query(TradingStrategy).filter_by(strategy_name='测试策略').delete()
            db.session.query(Configuration).filter_by(config_key='test_key').delete()
            
            db.session.commit()
            print("✓ 测试数据清理完成")
            return True
    except Exception as e:
        print(f"✗ 测试数据清理失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始数据库测试...")
    
    tests = [
        test_database_connection,
        test_table_creation,
        test_model_operations,
        test_indexes,
        test_constraints,
        cleanup_test_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n测试失败，停止后续测试")
            break
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！")
        sys.exit(0)
    else:
        print("✗ 部分测试失败！")
        sys.exit(1)


if __name__ == '__main__':
    main()