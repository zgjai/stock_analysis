#!/usr/bin/env python3
"""
股票交易记录系统 - 测试环境准备验证脚本

此脚本用于快速验证测试环境是否准备就绪，包括：
1. 验证系统能够正常启动和运行
2. 检查数据库连接和基本配置  
3. 确保所有API端点可访问

需求覆盖: 1.1, 6.1

使用方法:
    python test_environment_ready.py
    
返回值:
    0 - 环境准备就绪
    1 - 环境存在问题
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from config import TestingConfig
    from extensions import db
    from sqlalchemy import text, inspect
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在项目根目录运行此脚本，并且已安装所有依赖")
    sys.exit(1)


class EnvironmentReadinessTest:
    """环境准备就绪测试类"""
    
    def __init__(self):
        self.app = None
        self.client = None
        self.test_results = []
        self.error_count = 0
        self.warning_count = 0
    
    def log_success(self, message):
        """记录成功信息"""
        print(f"✅ {message}")
        self.test_results.append(('SUCCESS', message))
    
    def log_warning(self, message):
        """记录警告信息"""
        print(f"⚠️  {message}")
        self.test_results.append(('WARNING', message))
        self.warning_count += 1
    
    def log_error(self, message):
        """记录错误信息"""
        print(f"❌ {message}")
        self.test_results.append(('ERROR', message))
        self.error_count += 1
    
    def run_readiness_test(self):
        """运行环境准备就绪测试"""
        print("🚀 股票交易记录系统 - 测试环境准备验证")
        print("=" * 60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # 1. 系统启动验证
            self.test_system_startup()
            
            # 2. 数据库连接验证
            self.test_database_connection()
            
            # 3. 基本配置验证
            self.test_basic_configuration()
            
            # 4. 核心API端点验证
            self.test_core_api_endpoints()
            
            # 生成最终报告
            return self.generate_final_report()
            
        except Exception as e:
            self.log_error(f"测试过程中发生严重错误: {str(e)}")
            if os.getenv('DEBUG'):
                traceback.print_exc()
            return False
    
    def test_system_startup(self):
        """测试系统启动"""
        print("📋 1. 系统启动验证")
        print("-" * 30)
        
        try:
            # 创建Flask应用
            self.app = create_app(TestingConfig)
            self.log_success("Flask应用创建成功")
            
            # 验证测试配置
            if self.app.config.get('TESTING'):
                self.log_success("测试配置已启用")
            else:
                self.log_warning("测试配置未启用")
            
            # 检查蓝图注册
            blueprints = list(self.app.blueprints.keys())
            expected_blueprints = ['api', 'sector', 'case', 'frontend']
            
            for bp in expected_blueprints:
                if bp in blueprints:
                    self.log_success(f"蓝图 '{bp}' 已注册")
                else:
                    self.log_warning(f"蓝图 '{bp}' 未注册")
            
            # 创建测试客户端
            self.client = self.app.test_client()
            self.log_success("测试客户端创建成功")
            
        except Exception as e:
            self.log_error(f"系统启动失败: {str(e)}")
            raise
    
    def test_database_connection(self):
        """测试数据库连接"""
        print("\n💾 2. 数据库连接验证")
        print("-" * 30)
        
        try:
            with self.app.app_context():
                # 创建数据库表
                db.create_all()
                self.log_success("数据库表结构创建成功")
                
                # 测试基本查询
                result = db.session.execute(text('SELECT 1')).fetchone()
                if result and result[0] == 1:
                    self.log_success("数据库基本查询测试通过")
                else:
                    self.log_error("数据库基本查询失败")
                
                # 检查表结构
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                if len(tables) >= 8:  # 期望至少8个表
                    self.log_success(f"数据库表结构完整 ({len(tables)} 个表)")
                else:
                    self.log_warning(f"数据库表数量不足 ({len(tables)} 个表)")
                
                # 验证关键表
                key_tables = ['trade_records', 'review_records', 'stock_pool']
                for table in key_tables:
                    if table in tables:
                        self.log_success(f"关键表 '{table}' 存在")
                    else:
                        self.log_error(f"关键表 '{table}' 缺失")
                
        except Exception as e:
            self.log_error(f"数据库连接测试失败: {str(e)}")
    
    def test_basic_configuration(self):
        """测试基本配置"""
        print("\n⚙️  3. 基本配置验证")
        print("-" * 30)
        
        try:
            # 检查必要目录
            required_dirs = ['data', 'uploads']
            for dir_name in required_dirs:
                dir_path = Path(dir_name)
                if dir_path.exists():
                    self.log_success(f"目录 '{dir_name}' 存在")
                else:
                    # 尝试创建目录
                    try:
                        dir_path.mkdir(exist_ok=True)
                        self.log_success(f"目录 '{dir_name}' 已创建")
                    except Exception as e:
                        self.log_error(f"无法创建目录 '{dir_name}': {e}")
            
            # 检查关键配置项
            with self.app.app_context():
                config_checks = [
                    ('SECRET_KEY', '密钥配置'),
                    ('SQLALCHEMY_DATABASE_URI', '数据库连接'),
                    ('UPLOAD_FOLDER', '上传目录'),
                    ('MAX_CONTENT_LENGTH', '文件大小限制')
                ]
                
                for key, desc in config_checks:
                    if self.app.config.get(key):
                        self.log_success(f"{desc}已配置")
                    else:
                        self.log_error(f"{desc}未配置")
            
            # 测试文件写入权限
            try:
                test_file = Path('data/test_write.tmp')
                test_file.write_text('test')
                test_file.unlink()
                self.log_success("数据目录写入权限正常")
            except Exception as e:
                self.log_error(f"数据目录写入权限异常: {e}")
                
        except Exception as e:
            self.log_error(f"配置验证失败: {str(e)}")
    
    def test_core_api_endpoints(self):
        """测试核心API端点"""
        print("\n🌐 4. 核心API端点验证")
        print("-" * 30)
        
        try:
            # 定义核心API端点
            core_endpoints = [
                ('/api/health', '健康检查'),
                ('/api/', 'API信息'),
                ('/api/trades', '交易记录'),
                ('/api/stock-pool', '股票池'),
                ('/api/strategies', '交易策略'),
                ('/api/cases', '案例管理')
            ]
            
            successful_endpoints = 0
            
            for endpoint, description in core_endpoints:
                try:
                    response = self.client.get(endpoint)
                    
                    # 200和404都算成功（404说明端点存在但可能没有数据）
                    if response.status_code in [200, 404]:
                        self.log_success(f"{description} ({endpoint}): {response.status_code}")
                        successful_endpoints += 1
                    else:
                        self.log_error(f"{description} ({endpoint}): {response.status_code}")
                        
                except Exception as e:
                    self.log_error(f"{description} ({endpoint}): 连接错误 - {str(e)}")
            
            # 计算成功率
            success_rate = (successful_endpoints / len(core_endpoints)) * 100
            
            if success_rate >= 90:
                self.log_success(f"API端点测试通过 ({success_rate:.1f}%)")
            elif success_rate >= 70:
                self.log_warning(f"API端点部分可用 ({success_rate:.1f}%)")
            else:
                self.log_error(f"API端点测试失败 ({success_rate:.1f}%)")
                
        except Exception as e:
            self.log_error(f"API端点测试失败: {str(e)}")
    
    def generate_final_report(self):
        """生成最终报告"""
        print("\n" + "=" * 60)
        print("📊 测试环境准备验证报告")
        print("=" * 60)
        
        # 统计结果
        success_count = sum(1 for result in self.test_results if result[0] == 'SUCCESS')
        total_tests = len(self.test_results)
        
        print(f"总测试项目: {total_tests}")
        print(f"成功: {success_count} ✅")
        print(f"警告: {self.warning_count} ⚠️")
        print(f"错误: {self.error_count} ❌")
        
        # 计算成功率
        if total_tests > 0:
            success_rate = (success_count / total_tests) * 100
            print(f"成功率: {success_rate:.1f}%")
        else:
            success_rate = 0
        
        print("\n" + "-" * 60)
        
        # 判断整体状态
        if self.error_count == 0 and success_rate >= 90:
            print("🎉 测试环境准备就绪！系统可以正常使用。")
            overall_success = True
        elif self.error_count == 0 and success_rate >= 70:
            print("⚠️  测试环境基本就绪，但存在一些警告项目。")
            overall_success = True
        else:
            print("❌ 测试环境存在问题，请解决错误项目后重试。")
            overall_success = False
        
        # 显示错误和警告汇总
        if self.error_count > 0:
            print(f"\n❌ 需要解决的错误 ({self.error_count}):")
            for result_type, message in self.test_results:
                if result_type == 'ERROR':
                    print(f"   • {message}")
        
        if self.warning_count > 0:
            print(f"\n⚠️  需要注意的警告 ({self.warning_count}):")
            for result_type, message in self.test_results:
                if result_type == 'WARNING':
                    print(f"   • {message}")
        
        print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return overall_success


def main():
    """主函数"""
    tester = EnvironmentReadinessTest()
    success = tester.run_readiness_test()
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()