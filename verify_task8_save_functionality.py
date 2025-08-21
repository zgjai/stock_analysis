#!/usr/bin/env python3
"""
任务8 - 复盘保存功能验证脚本
测试复盘数据的完整保存流程、列表刷新、错误处理和状态变化
"""

import sys
import json
import time
import requests
import traceback
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple

class SaveFunctionalityVerifier:
    """复盘保存功能验证器"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        self.test_results = []
        self.test_stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
        
        print("🚀 初始化复盘保存功能验证器")
        print(f"📡 API基础URL: {self.api_base}")
    
    def log_result(self, test_name: str, success: bool, message: str, details: Optional[str] = None) -> Dict:
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        self.test_stats['total'] += 1
        
        if success is True:
            self.test_stats['passed'] += 1
            status_icon = "✅"
        elif success is False:
            self.test_stats['failed'] += 1
            status_icon = "❌"
        else:
            self.test_stats['warnings'] += 1
            status_icon = "⚠️"
        
        print(f"{status_icon} {test_name}: {message}")
        if details:
            print(f"   详情: {details}")
        
        return result
    
    def test_server_connection(self) -> bool:
        """测试服务器连接"""
        print("\n🔍 测试服务器连接")
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                self.log_result("服务器连接", True, "服务器连接正常")
                return True
            else:
                self.log_result("服务器连接", False, f"服务器返回状态码: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_result("服务器连接", False, f"连接失败: {str(e)}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """测试API端点可用性"""
        print("\n🔍 测试API端点可用性")
        
        endpoints = [
            ('/reviews', 'GET', '复盘列表API'),
            ('/reviews', 'POST', '创建复盘API'),
            ('/holdings', 'GET', '持仓列表API'),
            ('/holdings/alerts', 'GET', '持仓提醒API')
        ]
        
        all_available = True
        
        for endpoint, method, description in endpoints:
            try:
                url = f"{self.api_base}{endpoint}"
                
                if method == 'GET':
                    response = self.session.get(url, timeout=10)
                elif method == 'POST':
                    # 发送空数据测试端点是否存在
                    response = self.session.post(url, json={}, timeout=10)
                
                if response.status_code in [200, 400, 422]:  # 400/422表示端点存在但数据无效
                    self.log_result(f"API端点-{description}", True, f"端点可用 (状态码: {response.status_code})")
                else:
                    self.log_result(f"API端点-{description}", False, f"端点不可用 (状态码: {response.status_code})")
                    all_available = False
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"API端点-{description}", False, f"请求失败: {str(e)}")
                all_available = False
        
        return all_available
    
    def test_review_data_validation(self) -> bool:
        """测试复盘数据验证"""
        print("\n🔍 测试复盘数据验证")
        
        # 测试有效数据
        valid_data = {
            'stock_code': '000001',
            'review_date': date.today().isoformat(),
            'holding_days': 5,
            'current_price': 10.50,
            'floating_profit_ratio': 5.0,
            'buy_price': 10.00,
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 0,
            'trend_score': 1,
            'j_score': 1,
            'analysis': '测试分析内容',
            'decision': 'hold',
            'reason': '测试决策理由'
        }
        
        try:
            response = self.session.post(f"{self.api_base}/reviews", json=valid_data, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    self.log_result("有效数据验证", True, "有效数据成功保存", f"复盘ID: {response_data.get('data', {}).get('id')}")
                    return True
                else:
                    self.log_result("有效数据验证", False, f"保存失败: {response_data.get('error', {}).get('message', '未知错误')}")
                    return False
            else:
                error_msg = "未知错误"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', error_msg)
                except:
                    pass
                self.log_result("有效数据验证", False, f"HTTP {response.status_code}: {error_msg}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("有效数据验证", False, f"请求异常: {str(e)}")
            return False
    
    def test_invalid_data_handling(self) -> bool:
        """测试无效数据处理"""
        print("\n🔍 测试无效数据处理")
        
        invalid_test_cases = [
            ({}, "空数据"),
            ({'stock_code': ''}, "空股票代码"),
            ({'stock_code': '000001', 'review_date': ''}, "空复盘日期"),
            ({'stock_code': '000001', 'review_date': date.today().isoformat(), 'holding_days': 0}, "无效持仓天数"),
            ({'stock_code': '000001', 'review_date': date.today().isoformat(), 'holding_days': 5, 'decision': ''}, "空决策结果"),
            ({'stock_code': '000001', 'review_date': date.today().isoformat(), 'holding_days': 5, 'decision': 'hold', 'reason': ''}, "空决策理由"),
            ({'stock_code': '000001', 'review_date': date.today().isoformat(), 'holding_days': 5, 'decision': 'hold', 'reason': '测试', 'current_price': -1}, "负数价格"),
            ({'stock_code': '000001', 'review_date': date.today().isoformat(), 'holding_days': 5, 'decision': 'hold', 'reason': '测试', 'current_price': 10000}, "超大价格")
        ]
        
        all_handled = True
        
        for invalid_data, test_name in invalid_test_cases:
            try:
                response = self.session.post(f"{self.api_base}/reviews", json=invalid_data, timeout=10)
                
                if response.status_code in [400, 422]:  # 期望的验证错误状态码
                    self.log_result(f"无效数据处理-{test_name}", True, "正确拒绝无效数据")
                elif response.status_code == 200:
                    response_data = response.json()
                    if not response_data.get('success'):
                        self.log_result(f"无效数据处理-{test_name}", True, "正确拒绝无效数据")
                    else:
                        self.log_result(f"无效数据处理-{test_name}", False, "错误接受了无效数据")
                        all_handled = False
                else:
                    self.log_result(f"无效数据处理-{test_name}", "warning", f"意外状态码: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"无效数据处理-{test_name}", False, f"请求异常: {str(e)}")
                all_handled = False
        
        return all_handled
    
    def test_review_crud_operations(self) -> bool:
        """测试复盘CRUD操作"""
        print("\n🔍 测试复盘CRUD操作")
        
        # 创建测试复盘
        create_data = {
            'stock_code': '000002',
            'review_date': date.today().isoformat(),
            'holding_days': 3,
            'current_price': 15.20,
            'price_up_score': 1,
            'bbi_score': 0,
            'volume_score': 1,
            'trend_score': 1,
            'j_score': 0,
            'analysis': 'CRUD测试分析',
            'decision': 'sell_partial',
            'reason': 'CRUD测试理由'
        }
        
        try:
            # 创建复盘
            create_response = self.session.post(f"{self.api_base}/reviews", json=create_data, timeout=10)
            
            if create_response.status_code != 200:
                self.log_result("CRUD-创建", False, f"创建失败: HTTP {create_response.status_code}")
                return False
            
            create_result = create_response.json()
            if not create_result.get('success'):
                self.log_result("CRUD-创建", False, f"创建失败: {create_result.get('error', {}).get('message')}")
                return False
            
            review_id = create_result.get('data', {}).get('id')
            if not review_id:
                self.log_result("CRUD-创建", False, "创建成功但未返回ID")
                return False
            
            self.log_result("CRUD-创建", True, f"成功创建复盘，ID: {review_id}")
            
            # 读取复盘列表
            list_response = self.session.get(f"{self.api_base}/reviews", timeout=10)
            if list_response.status_code == 200:
                list_result = list_response.json()
                if list_result.get('success') and list_result.get('data'):
                    self.log_result("CRUD-读取", True, f"成功读取复盘列表，共 {len(list_result['data'])} 条记录")
                else:
                    self.log_result("CRUD-读取", False, "读取复盘列表失败")
            else:
                self.log_result("CRUD-读取", False, f"读取失败: HTTP {list_response.status_code}")
            
            # 更新复盘
            update_data = create_data.copy()
            update_data['analysis'] = 'CRUD测试分析-已更新'
            update_data['reason'] = 'CRUD测试理由-已更新'
            
            update_response = self.session.put(f"{self.api_base}/reviews/{review_id}", json=update_data, timeout=10)
            if update_response.status_code == 200:
                update_result = update_response.json()
                if update_result.get('success'):
                    self.log_result("CRUD-更新", True, f"成功更新复盘 {review_id}")
                else:
                    self.log_result("CRUD-更新", False, f"更新失败: {update_result.get('error', {}).get('message')}")
            else:
                self.log_result("CRUD-更新", False, f"更新失败: HTTP {update_response.status_code}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result("CRUD操作", False, f"请求异常: {str(e)}")
            return False
    
    def test_error_scenarios(self) -> bool:
        """测试错误场景处理"""
        print("\n🔍 测试错误场景处理")
        
        # 测试不存在的复盘更新
        try:
            fake_id = 999999
            update_data = {
                'stock_code': '000001',
                'review_date': date.today().isoformat(),
                'holding_days': 1,
                'decision': 'hold',
                'reason': '测试不存在的复盘'
            }
            
            response = self.session.put(f"{self.api_base}/reviews/{fake_id}", json=update_data, timeout=10)
            
            if response.status_code == 404:
                self.log_result("错误处理-不存在的复盘", True, "正确返回404错误")
            elif response.status_code == 200:
                result = response.json()
                if not result.get('success'):
                    self.log_result("错误处理-不存在的复盘", True, "正确处理不存在的复盘")
                else:
                    self.log_result("错误处理-不存在的复盘", False, "错误地更新了不存在的复盘")
            else:
                self.log_result("错误处理-不存在的复盘", "warning", f"意外状态码: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("错误处理-不存在的复盘", False, f"请求异常: {str(e)}")
        
        # 测试格式错误的数据
        try:
            malformed_data = {
                'stock_code': '000001',
                'review_date': 'invalid-date',
                'holding_days': 'not-a-number',
                'decision': 'hold',
                'reason': '测试格式错误'
            }
            
            response = self.session.post(f"{self.api_base}/reviews", json=malformed_data, timeout=10)
            
            if response.status_code in [400, 422]:
                self.log_result("错误处理-格式错误", True, "正确拒绝格式错误的数据")
            elif response.status_code == 200:
                result = response.json()
                if not result.get('success'):
                    self.log_result("错误处理-格式错误", True, "正确处理格式错误")
                else:
                    self.log_result("错误处理-格式错误", False, "错误接受了格式错误的数据")
            else:
                self.log_result("错误处理-格式错误", "warning", f"意外状态码: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("错误处理-格式错误", False, f"请求异常: {str(e)}")
        
        return True
    
    def test_performance_metrics(self) -> bool:
        """测试性能指标"""
        print("\n🔍 测试性能指标")
        
        test_data = {
            'stock_code': '000003',
            'review_date': date.today().isoformat(),
            'holding_days': 7,
            'current_price': 8.90,
            'price_up_score': 1,
            'bbi_score': 1,
            'volume_score': 1,
            'trend_score': 0,
            'j_score': 1,
            'analysis': '性能测试分析内容',
            'decision': 'hold',
            'reason': '性能测试决策理由'
        }
        
        # 测试单次保存性能
        try:
            start_time = time.time()
            response = self.session.post(f"{self.api_base}/reviews", json=test_data, timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            if response.status_code == 200:
                if response_time < 1000:  # 1秒内
                    self.log_result("性能-单次保存", True, f"响应时间良好: {response_time:.2f}ms")
                elif response_time < 3000:  # 3秒内
                    self.log_result("性能-单次保存", "warning", f"响应时间较慢: {response_time:.2f}ms")
                else:
                    self.log_result("性能-单次保存", False, f"响应时间过慢: {response_time:.2f}ms")
            else:
                self.log_result("性能-单次保存", False, f"保存失败: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("性能-单次保存", False, f"请求异常: {str(e)}")
        
        # 测试列表查询性能
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_base}/reviews", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    record_count = len(result.get('data', []))
                    if response_time < 500:  # 500ms内
                        self.log_result("性能-列表查询", True, f"查询性能良好: {response_time:.2f}ms ({record_count}条记录)")
                    elif response_time < 2000:  # 2秒内
                        self.log_result("性能-列表查询", "warning", f"查询性能一般: {response_time:.2f}ms ({record_count}条记录)")
                    else:
                        self.log_result("性能-列表查询", False, f"查询性能较差: {response_time:.2f}ms ({record_count}条记录)")
                else:
                    self.log_result("性能-列表查询", False, "查询失败")
            else:
                self.log_result("性能-列表查询", False, f"查询失败: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("性能-列表查询", False, f"请求异常: {str(e)}")
        
        return True
    
    def test_data_consistency(self) -> bool:
        """测试数据一致性"""
        print("\n🔍 测试数据一致性")
        
        # 创建测试数据
        test_data = {
            'stock_code': '000004',
            'review_date': date.today().isoformat(),
            'holding_days': 10,
            'current_price': 12.34,
            'floating_profit_ratio': 23.4,
            'buy_price': 10.00,
            'price_up_score': 1,
            'bbi_score': 0,
            'volume_score': 1,
            'trend_score': 1,
            'j_score': 0,
            'analysis': '数据一致性测试分析',
            'decision': 'sell_all',
            'reason': '数据一致性测试理由'
        }
        
        try:
            # 创建复盘
            create_response = self.session.post(f"{self.api_base}/reviews", json=test_data, timeout=10)
            
            if create_response.status_code != 200:
                self.log_result("数据一致性", False, f"创建失败: HTTP {create_response.status_code}")
                return False
            
            create_result = create_response.json()
            if not create_result.get('success'):
                self.log_result("数据一致性", False, f"创建失败: {create_result.get('error', {}).get('message')}")
                return False
            
            created_data = create_result.get('data', {})
            review_id = created_data.get('id')
            
            # 验证返回的数据与输入数据一致
            consistency_checks = [
                ('stock_code', test_data['stock_code'], created_data.get('stock_code')),
                ('review_date', test_data['review_date'], created_data.get('review_date')),
                ('holding_days', test_data['holding_days'], created_data.get('holding_days')),
                ('current_price', test_data['current_price'], created_data.get('current_price')),
                ('decision', test_data['decision'], created_data.get('decision')),
                ('reason', test_data['reason'], created_data.get('reason'))
            ]
            
            all_consistent = True
            for field_name, expected, actual in consistency_checks:
                if expected == actual:
                    self.log_result(f"数据一致性-{field_name}", True, f"数据一致: {expected}")
                else:
                    self.log_result(f"数据一致性-{field_name}", False, f"数据不一致: 期望 {expected}, 实际 {actual}")
                    all_consistent = False
            
            # 验证计算字段
            total_score = (test_data['price_up_score'] + test_data['bbi_score'] + 
                          test_data['volume_score'] + test_data['trend_score'] + test_data['j_score'])
            
            if created_data.get('total_score') == total_score:
                self.log_result("数据一致性-总分计算", True, f"总分计算正确: {total_score}")
            else:
                self.log_result("数据一致性-总分计算", False, f"总分计算错误: 期望 {total_score}, 实际 {created_data.get('total_score')}")
                all_consistent = False
            
            return all_consistent
            
        except requests.exceptions.RequestException as e:
            self.log_result("数据一致性", False, f"请求异常: {str(e)}")
            return False
    
    def test_concurrent_operations(self) -> bool:
        """测试并发操作"""
        print("\n🔍 测试并发操作")
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def create_review(thread_id):
            """并发创建复盘的线程函数"""
            try:
                test_data = {
                    'stock_code': f'00000{thread_id}',
                    'review_date': date.today().isoformat(),
                    'holding_days': thread_id,
                    'current_price': 10.0 + thread_id,
                    'price_up_score': 1,
                    'bbi_score': 1,
                    'volume_score': 0,
                    'trend_score': 1,
                    'j_score': 0,
                    'analysis': f'并发测试分析-线程{thread_id}',
                    'decision': 'hold',
                    'reason': f'并发测试理由-线程{thread_id}'
                }
                
                start_time = time.time()
                response = self.session.post(f"{self.api_base}/reviews", json=test_data, timeout=15)
                end_time = time.time()
                
                results_queue.put({
                    'thread_id': thread_id,
                    'success': response.status_code == 200,
                    'response_time': (end_time - start_time) * 1000,
                    'status_code': response.status_code
                })
                
            except Exception as e:
                results_queue.put({
                    'thread_id': thread_id,
                    'success': False,
                    'error': str(e),
                    'response_time': 0,
                    'status_code': 0
                })
        
        # 启动5个并发线程
        threads = []
        thread_count = 5
        
        for i in range(1, thread_count + 1):
            thread = threading.Thread(target=create_review, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=20)
        
        # 收集结果
        successful_requests = 0
        failed_requests = 0
        total_response_time = 0
        
        while not results_queue.empty():
            result = results_queue.get()
            if result['success']:
                successful_requests += 1
                total_response_time += result['response_time']
            else:
                failed_requests += 1
        
        if successful_requests > 0:
            avg_response_time = total_response_time / successful_requests
            success_rate = (successful_requests / thread_count) * 100
            
            if success_rate >= 80:
                self.log_result("并发操作", True, 
                              f"并发测试通过: {successful_requests}/{thread_count} 成功, 平均响应时间: {avg_response_time:.2f}ms")
            else:
                self.log_result("并发操作", "warning", 
                              f"并发测试部分成功: {successful_requests}/{thread_count} 成功, 成功率: {success_rate:.1f}%")
        else:
            self.log_result("并发操作", False, "所有并发请求都失败了")
        
        return successful_requests > 0
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 开始运行复盘保存功能完整测试套件")
        print("=" * 60)
        
        start_time = time.time()
        
        # 测试序列
        test_methods = [
            ('服务器连接测试', self.test_server_connection),
            ('API端点测试', self.test_api_endpoints),
            ('数据验证测试', self.test_review_data_validation),
            ('无效数据处理测试', self.test_invalid_data_handling),
            ('CRUD操作测试', self.test_review_crud_operations),
            ('错误场景测试', self.test_error_scenarios),
            ('性能指标测试', self.test_performance_metrics),
            ('数据一致性测试', self.test_data_consistency),
            ('并发操作测试', self.test_concurrent_operations)
        ]
        
        for test_name, test_method in test_methods:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                test_method()
            except Exception as e:
                self.log_result(test_name, False, f"测试执行异常: {str(e)}")
                print(f"❌ {test_name} 执行异常:")
                traceback.print_exc()
            
            time.sleep(0.5)  # 测试间隔
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 生成测试报告
        print("\n" + "="*60)
        print("📊 测试结果汇总")
        print("="*60)
        
        print(f"总测试数: {self.test_stats['total']}")
        print(f"通过测试: {self.test_stats['passed']} ✅")
        print(f"失败测试: {self.test_stats['failed']} ❌")
        print(f"警告测试: {self.test_stats['warnings']} ⚠️")
        
        if self.test_stats['total'] > 0:
            success_rate = (self.test_stats['passed'] / self.test_stats['total']) * 100
            print(f"成功率: {success_rate:.1f}%")
        
        print(f"总耗时: {total_time:.2f}秒")
        
        # 生成详细报告
        report = {
            'summary': self.test_stats.copy(),
            'success_rate': success_rate if self.test_stats['total'] > 0 else 0,
            'total_time': total_time,
            'test_results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存测试报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task8_save_functionality_test_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 测试报告已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")
            return ""

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='复盘保存功能验证脚本')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='服务器URL (默认: http://localhost:5000)')
    parser.add_argument('--output', help='输出报告文件名')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 创建验证器
    verifier = SaveFunctionalityVerifier(args.url)
    
    try:
        # 运行所有测试
        report = verifier.run_all_tests()
        
        # 保存报告
        if args.output:
            verifier.save_report(report, args.output)
        else:
            verifier.save_report(report)
        
        # 根据测试结果设置退出码
        if report['summary']['failed'] == 0:
            print("\n🎉 所有测试通过!")
            sys.exit(0)
        else:
            print(f"\n⚠️ 有 {report['summary']['failed']} 个测试失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试执行异常: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()