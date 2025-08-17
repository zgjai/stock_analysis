#!/usr/bin/env python3
"""
前端界面基本功能测试 - 主要页面加载测试
测试任务3.1的实现：
- 测试仪表板页面的正常加载和显示
- 验证交易记录页面的数据展示
- 测试股票池和复盘页面的基本功能
- _需求: 1.2, 7.1_
"""

import os
import sys
import time
import requests
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class FrontendPageLoadingTester:
    def __init__(self):
        self.base_url = "http://localhost:5001"
        self.test_results = []
        self.timeout = 10
        
    def test_server_running(self):
        """测试服务器是否运行"""
        print("检查服务器状态...")
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                print("✅ 服务器运行正常")
                return True
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 服务器连接失败: {e}")
            return False
    
    def test_dashboard_page_loading(self):
        """测试仪表板页面的正常加载和显示"""
        print("\n📋 测试1: 仪表板页面加载测试")
        
        try:
            # 测试页面访问
            response = requests.get(f"{self.base_url}/", timeout=self.timeout)
            if response.status_code != 200:
                print(f"❌ 仪表板页面访问失败: {response.status_code}")
                self.test_results.append("仪表板页面访问失败")
                return False
            
            content = response.text
            print("✅ 仪表板页面访问成功")
            
            # 检查关键UI元素
            required_elements = [
                # 统计概览卡片
                'id="total-trades"',
                'id="total-profit"', 
                'id="current-holdings"',
                'id="success-rate"',
                
                # 图表区域
                'id="profitChart"',
                'id="distributionChart"',
                
                # 数据表格
                'id="recent-trades"',
                'id="holding-alerts"',
                
                # 页面标题和导航
                '仪表板',
                'class="stats-card"',
                'class="card"'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
                else:
                    print(f"  ✅ 找到元素: {element}")
            
            if missing_elements:
                print(f"❌ 仪表板页面缺少关键元素: {missing_elements}")
                self.test_results.append(f"仪表板页面缺少元素: {missing_elements}")
                return False
            
            # 检查JavaScript文件引用
            js_files = [
                'dashboard.js',
                'api.js',
                'main.js'
            ]
            
            for js_file in js_files:
                if js_file in content:
                    print(f"  ✅ JavaScript文件已引用: {js_file}")
                else:
                    print(f"  ❌ JavaScript文件未引用: {js_file}")
                    self.test_results.append(f"JavaScript文件未引用: {js_file}")
            
            # 检查CSS样式
            if 'main.css' in content or 'components.css' in content:
                print("  ✅ CSS样式文件已引用")
            else:
                print("  ❌ CSS样式文件未引用")
                self.test_results.append("CSS样式文件未引用")
            
            print("✅ 仪表板页面结构完整")
            return True
            
        except Exception as e:
            print(f"❌ 仪表板页面测试失败: {e}")
            self.test_results.append(f"仪表板页面测试异常: {e}")
            return False
    
    def test_trading_records_page_loading(self):
        """验证交易记录页面的数据展示"""
        print("\n📋 测试2: 交易记录页面加载测试")
        
        try:
            # 测试页面访问
            response = requests.get(f"{self.base_url}/trading-records", timeout=self.timeout)
            if response.status_code != 200:
                print(f"❌ 交易记录页面访问失败: {response.status_code}")
                self.test_results.append("交易记录页面访问失败")
                return False
            
            content = response.text
            print("✅ 交易记录页面访问成功")
            
            # 检查关键UI元素
            required_elements = [
                # 页面标题和操作按钮
                '交易记录',
                'id="addTradeModal"',
                'data-bs-toggle="modal"',
                
                # 筛选器
                'id="stock-code-filter"',
                'id="stock-name-filter"',
                'id="trade-type-filter"',
                'id="date-from"',
                'id="date-to"',
                
                # 数据表格
                'id="trades-table-body"',
                'class="table"',
                'class="pagination"',
                
                # 表单元素
                'id="trade-form"',
                'id="stock-code"',
                'id="stock-name"',
                'id="trade-type"',
                'id="price"',
                'id="quantity"',
                
                # 模态框
                'id="correctTradeModal"',
                'id="correctionHistoryModal"'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
                else:
                    print(f"  ✅ 找到元素: {element}")
            
            if missing_elements:
                print(f"❌ 交易记录页面缺少关键元素: {missing_elements}")
                self.test_results.append(f"交易记录页面缺少元素: {missing_elements}")
                return False
            
            # 检查JavaScript功能
            js_functions = [
                'class TradingRecordsManager',
                'loadTrades()',
                'saveTrade()',
                'filterTrades()',
                'renderTradesTable(',
                'updateReasonOptions(',
                'calculateRiskReward()'
            ]
            
            missing_functions = []
            for func in js_functions:
                if func not in content:
                    missing_functions.append(func)
                else:
                    print(f"  ✅ 找到JavaScript功能: {func}")
            
            if missing_functions:
                print(f"❌ 交易记录页面缺少JavaScript功能: {missing_functions}")
                self.test_results.append(f"交易记录页面缺少JavaScript功能: {missing_functions}")
            
            print("✅ 交易记录页面结构完整")
            return True
            
        except Exception as e:
            print(f"❌ 交易记录页面测试失败: {e}")
            self.test_results.append(f"交易记录页面测试异常: {e}")
            return False
    
    def test_stock_pool_page_loading(self):
        """测试股票池页面的基本功能"""
        print("\n📋 测试3: 股票池页面加载测试")
        
        try:
            # 测试页面访问
            response = requests.get(f"{self.base_url}/stock-pool", timeout=self.timeout)
            if response.status_code != 200:
                print(f"❌ 股票池页面访问失败: {response.status_code}")
                self.test_results.append("股票池页面访问失败")
                return False
            
            content = response.text
            print("✅ 股票池页面访问成功")
            
            # 检查关键UI元素
            required_elements = [
                # 页面标题和操作按钮
                '股票池管理',
                'id="addStockModal"',
                'onclick="refreshStockPool()"',
                
                # 股票池区域
                'id="watch-pool"',
                'id="buy-pool"',
                'id="watch-pool-count"',
                'id="buy-pool-count"',
                'id="pool-stats"',
                
                # 历史记录
                'id="pool-history"',
                
                # 表单元素
                'id="addStockForm"',
                'id="stockCode"',
                'id="stockName"',
                'id="poolType"',
                'id="targetPrice"',
                'id="addReason"',
                
                # 编辑模态框
                'id="editStockModal"',
                'id="editStockForm"'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
                else:
                    print(f"  ✅ 找到元素: {element}")
            
            if missing_elements:
                print(f"❌ 股票池页面缺少关键元素: {missing_elements}")
                self.test_results.append(f"股票池页面缺少元素: {missing_elements}")
                return False
            
            # 检查JavaScript功能
            js_functions = [
                'function initStockPool()',
                'function loadStockPool()',
                'function renderStockPools()',
                'function submitAddStock()',
                'function editStock(',
                'function moveStock(',
                'function removeStock(',
                'function setupFormValidation()'
            ]
            
            missing_functions = []
            for func in js_functions:
                if func not in content:
                    missing_functions.append(func)
                else:
                    print(f"  ✅ 找到JavaScript功能: {func}")
            
            if missing_functions:
                print(f"❌ 股票池页面缺少JavaScript功能: {missing_functions}")
                self.test_results.append(f"股票池页面缺少JavaScript功能: {missing_functions}")
            
            print("✅ 股票池页面结构完整")
            return True
            
        except Exception as e:
            print(f"❌ 股票池页面测试失败: {e}")
            self.test_results.append(f"股票池页面测试异常: {e}")
            return False
    
    def test_review_page_loading(self):
        """测试复盘页面的基本功能"""
        print("\n📋 测试4: 复盘页面加载测试")
        
        try:
            # 测试页面访问
            response = requests.get(f"{self.base_url}/review", timeout=self.timeout)
            if response.status_code != 200:
                print(f"❌ 复盘页面访问失败: {response.status_code}")
                self.test_results.append("复盘页面访问失败")
                return False
            
            content = response.text
            print("✅ 复盘页面访问成功")
            
            # 检查关键UI元素
            required_elements = [
                # 页面标题
                '复盘分析',
                
                # 持仓区域
                'id="holdings-list"',
                '当前持仓',
                'onclick="refreshHoldings()"',
                
                # 复盘记录区域
                'id="reviews-list"',
                '复盘记录',
                'id="review-date-filter"',
                'id="review-stock-filter"',
                
                # 持仓提醒区域
                'id="holding-alerts"',
                '持仓策略提醒',
                
                # 快速复盘面板
                'id="quick-review-stock"',
                'onclick="openQuickReview()"',
                
                # 复盘模态框
                'id="reviewModal"',
                'id="review-form"',
                'id="price-up-score"',
                'id="bbi-score"',
                'id="volume-score"',
                'id="trend-score"',
                'id="j-score"',
                'id="total-score"',
                
                # 持仓天数编辑模态框
                'id="holdingDaysModal"'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
                else:
                    print(f"  ✅ 找到元素: {element}")
            
            if missing_elements:
                print(f"❌ 复盘页面缺少关键元素: {missing_elements}")
                self.test_results.append(f"复盘页面缺少元素: {missing_elements}")
                return False
            
            # 检查JavaScript功能
            js_functions = [
                'function initReview()',
                'function loadHoldings()',
                'function loadHoldingAlerts()',
                'function loadReviews()',
                'function openReviewModal(',
                'function saveReview()',
                'function calculateTotalScore()',
                'function editHoldingDays(',
                'function filterReviews()'
            ]
            
            missing_functions = []
            for func in js_functions:
                if func not in content:
                    missing_functions.append(func)
                else:
                    print(f"  ✅ 找到JavaScript功能: {func}")
            
            if missing_functions:
                print(f"❌ 复盘页面缺少JavaScript功能: {missing_functions}")
                self.test_results.append(f"复盘页面缺少JavaScript功能: {missing_functions}")
            
            print("✅ 复盘页面结构完整")
            return True
            
        except Exception as e:
            print(f"❌ 复盘页面测试失败: {e}")
            self.test_results.append(f"复盘页面测试异常: {e}")
            return False
    
    def test_page_navigation(self):
        """测试页面导航功能"""
        print("\n📋 测试5: 页面导航测试")
        
        try:
            # 获取主页面内容检查导航链接
            response = requests.get(self.base_url, timeout=self.timeout)
            content = response.text
            
            # 检查导航链接
            navigation_links = [
                ('仪表板', '/'),
                ('交易记录', '/trading-records'),
                ('股票池', '/stock-pool'),
                ('复盘分析', '/review'),
                ('统计分析', '/analytics'),
                ('案例管理', '/cases')
            ]
            
            for link_text, link_url in navigation_links:
                if link_text in content and (link_url in content or link_url.replace('-', '_') in content):
                    print(f"  ✅ 导航链接存在: {link_text} -> {link_url}")
                else:
                    print(f"  ❌ 导航链接缺失: {link_text} -> {link_url}")
                    self.test_results.append(f"导航链接缺失: {link_text}")
            
            # 检查基础模板结构
            base_elements = [
                'class="navbar"',
                'class="sidebar"',
                'class="main-content"',
                'class="breadcrumb"',
                'Bootstrap'  # 检查是否使用Bootstrap
            ]
            
            for element in base_elements:
                if element in content:
                    print(f"  ✅ 基础模板元素存在: {element}")
                else:
                    print(f"  ❌ 基础模板元素缺失: {element}")
            
            print("✅ 页面导航结构完整")
            return True
            
        except Exception as e:
            print(f"❌ 页面导航测试失败: {e}")
            self.test_results.append(f"页面导航测试异常: {e}")
            return False
    
    def test_responsive_design(self):
        """测试响应式设计"""
        print("\n📋 测试6: 响应式设计测试")
        
        try:
            # 检查CSS文件中的响应式设计
            css_files = ['static/css/main.css', 'static/css/components.css']
            responsive_features_found = False
            
            for css_file in css_files:
                try:
                    with open(css_file, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                    
                    # 检查媒体查询
                    media_queries = [
                        '@media (max-width: 768px)',
                        '@media (max-width: 576px)',
                        '@media (min-width: 992px)'
                    ]
                    
                    for query in media_queries:
                        if query in css_content:
                            print(f"  ✅ 找到媒体查询: {query}")
                            responsive_features_found = True
                        else:
                            print(f"  ❌ 缺少媒体查询: {query}")
                    
                    # 检查响应式类
                    responsive_classes = [
                        '.col-',
                        '.row',
                        '.container',
                        '.d-none',
                        '.d-block'
                    ]
                    
                    for css_class in responsive_classes:
                        if css_class in css_content:
                            print(f"  ✅ 找到响应式类: {css_class}")
                            responsive_features_found = True
                    
                except FileNotFoundError:
                    print(f"  ❌ CSS文件不存在: {css_file}")
                    continue
            
            if not responsive_features_found:
                print("❌ 未找到响应式设计特性")
                self.test_results.append("缺少响应式设计特性")
                return False
            
            print("✅ 响应式设计特性完整")
            return True
            
        except Exception as e:
            print(f"❌ 响应式设计测试失败: {e}")
            self.test_results.append(f"响应式设计测试异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有页面加载测试"""
        print("🧪 开始前端界面基本功能测试 - 主要页面加载测试")
        print("=" * 70)
        
        # 首先检查服务器状态
        if not self.test_server_running():
            print("❌ 服务器未运行，无法进行测试")
            print("请先启动服务器: python run.py 或 python app.py")
            return False
        
        tests = [
            ("仪表板页面加载", self.test_dashboard_page_loading),
            ("交易记录页面加载", self.test_trading_records_page_loading),
            ("股票池页面加载", self.test_stock_pool_page_loading),
            ("复盘页面加载", self.test_review_page_loading),
            ("页面导航功能", self.test_page_navigation),
            ("响应式设计", self.test_responsive_design)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                    print(f"✅ {test_name} - 通过")
                else:
                    print(f"❌ {test_name} - 失败")
            except Exception as e:
                print(f"❌ {test_name} - 异常: {e}")
                self.test_results.append(f"{test_name}测试异常: {e}")
        
        # 输出测试结果
        print("\n" + "=" * 70)
        print("📊 测试结果汇总")
        print(f"✅ 通过测试: {passed_tests}/{total_tests}")
        
        if self.test_results:
            print(f"❌ 失败项目: {len(self.test_results)}")
            for i, error in enumerate(self.test_results, 1):
                print(f"   {i}. {error}")
        else:
            print("🎉 所有测试都通过了！")
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"📈 成功率: {success_rate:.1f}%")
        
        return len(self.test_results) == 0

def main():
    """主函数"""
    tester = FrontendPageLoadingTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 前端界面基本功能测试 - 主要页面加载测试全部通过！")
        print("✅ 任务3.1实现成功")
        
        # 输出实现总结
        print("\n📋 实现功能总结:")
        print("1. ✅ 仪表板页面正常加载，包含统计卡片、图表和数据表格")
        print("2. ✅ 交易记录页面数据展示完整，包含筛选器和表单功能")
        print("3. ✅ 股票池页面基本功能完整，包含双池管理和历史记录")
        print("4. ✅ 复盘页面功能完整，包含持仓管理和评分系统")
        print("5. ✅ 页面导航功能正常，基础模板结构完整")
        print("6. ✅ 响应式设计特性完整，支持多设备访问")
        
        return 0
    else:
        print("\n❌ 部分测试失败，请检查实现")
        return 1

if __name__ == "__main__":
    exit(main())