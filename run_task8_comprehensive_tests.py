#!/usr/bin/env python3
"""
任务8 - 复盘保存功能综合测试运行器
运行所有相关测试：后端API测试、前端集成测试、性能测试等
"""

import sys
import os
import json
import time
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class ComprehensiveTestRunner:
    """综合测试运行器"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.test_results = {}
        self.overall_stats = {
            'total_test_suites': 0,
            'passed_test_suites': 0,
            'failed_test_suites': 0,
            'total_individual_tests': 0,
            'passed_individual_tests': 0,
            'failed_individual_tests': 0,
            'warning_individual_tests': 0
        }
        
        print("🚀 初始化复盘保存功能综合测试运行器")
        print(f"🌐 目标服务器: {self.base_url}")
        
        # 确保测试脚本存在
        self.test_scripts = {
            'backend_api': 'verify_task8_save_functionality.py',
            'integration': 'test_task8_integration_verification.py'
        }
        
        self.check_test_scripts()
    
    def check_test_scripts(self):
        """检查测试脚本是否存在"""
        print("\n🔍 检查测试脚本")
        
        missing_scripts = []
        for test_name, script_path in self.test_scripts.items():
            if not Path(script_path).exists():
                missing_scripts.append(script_path)
                print(f"❌ 缺少测试脚本: {script_path}")
            else:
                print(f"✅ 找到测试脚本: {script_path}")
        
        if missing_scripts:
            print(f"\n⚠️ 缺少 {len(missing_scripts)} 个测试脚本，某些测试将被跳过")
        else:
            print("\n✅ 所有测试脚本都已就绪")
    
    def check_server_status(self) -> bool:
        """检查服务器状态"""
        print("\n🔍 检查服务器状态")
        
        try:
            import requests
            response = requests.get(self.base_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ 服务器运行正常 (状态码: {response.status_code})")
                return True
            else:
                print(f"⚠️ 服务器响应异常 (状态码: {response.status_code})")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到服务器: {self.base_url}")
            print("请确保服务器正在运行")
            return False
        except Exception as e:
            print(f"❌ 服务器检查失败: {str(e)}")
            return False
    
    def run_backend_api_tests(self) -> Dict[str, Any]:
        """运行后端API测试"""
        print("\n" + "="*60)
        print("🔧 运行后端API测试")
        print("="*60)
        
        script_path = self.test_scripts['backend_api']
        
        if not Path(script_path).exists():
            return {
                'success': False,
                'error': f'测试脚本不存在: {script_path}',
                'stats': {},
                'execution_time': 0
            }
        
        try:
            start_time = time.time()
            
            # 运行后端API测试脚本
            result = subprocess.run([
                sys.executable, script_path,
                '--url', self.base_url,
                '--output', f'backend_api_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            ], capture_output=True, text=True, timeout=300)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 解析输出
            output_lines = result.stdout.split('\n')
            stats = self.parse_test_output(output_lines)
            
            success = result.returncode == 0
            
            print(f"后端API测试完成 (耗时: {execution_time:.2f}秒)")
            print(f"退出码: {result.returncode}")
            
            if result.stderr:
                print(f"错误输出: {result.stderr}")
            
            return {
                'success': success,
                'stats': stats,
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '后端API测试超时',
                'stats': {},
                'execution_time': 300
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'后端API测试执行异常: {str(e)}',
                'stats': {},
                'execution_time': 0
            }
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """运行集成测试"""
        print("\n" + "="*60)
        print("🔧 运行前端集成测试")
        print("="*60)
        
        script_path = self.test_scripts['integration']
        
        if not Path(script_path).exists():
            return {
                'success': False,
                'error': f'测试脚本不存在: {script_path}',
                'stats': {},
                'execution_time': 0
            }
        
        try:
            start_time = time.time()
            
            # 运行集成测试脚本
            result = subprocess.run([
                sys.executable, script_path,
                '--url', self.base_url,
                '--headless',
                '--output', f'integration_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            ], capture_output=True, text=True, timeout=600)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 解析输出
            output_lines = result.stdout.split('\n')
            stats = self.parse_test_output(output_lines)
            
            success = result.returncode == 0
            
            print(f"集成测试完成 (耗时: {execution_time:.2f}秒)")
            print(f"退出码: {result.returncode}")
            
            if result.stderr:
                print(f"错误输出: {result.stderr}")
            
            return {
                'success': success,
                'stats': stats,
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '集成测试超时',
                'stats': {},
                'execution_time': 600
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'集成测试执行异常: {str(e)}',
                'stats': {},
                'execution_time': 0
            }
    
    def run_manual_verification(self) -> Dict[str, Any]:
        """运行手动验证检查"""
        print("\n" + "="*60)
        print("🔧 运行手动验证检查")
        print("="*60)
        
        verification_items = [
            {
                'name': '复盘页面可访问性',
                'url': f'{self.base_url}/review',
                'expected_content': ['复盘', '持仓', '保存']
            },
            {
                'name': '静态资源可用性',
                'files': [
                    '/static/js/api.js',
                    '/static/js/review-save-manager.js',
                    '/static/js/unified-message-system.js'
                ]
            },
            {
                'name': 'API端点可用性',
                'endpoints': [
                    '/api/reviews',
                    '/api/holdings',
                    '/api/holdings/alerts'
                ]
            }
        ]
        
        results = []
        
        try:
            import requests
            session = requests.Session()
            session.timeout = 10
            
            for item in verification_items:
                item_result = {
                    'name': item['name'],
                    'success': True,
                    'details': []
                }
                
                if 'url' in item:
                    # 检查页面可访问性
                    try:
                        response = session.get(item['url'])
                        if response.status_code == 200:
                            content = response.text.lower()
                            for expected in item['expected_content']:
                                if expected.lower() in content:
                                    item_result['details'].append(f"✅ 找到内容: {expected}")
                                else:
                                    item_result['details'].append(f"❌ 未找到内容: {expected}")
                                    item_result['success'] = False
                        else:
                            item_result['success'] = False
                            item_result['details'].append(f"❌ HTTP状态码: {response.status_code}")
                    except Exception as e:
                        item_result['success'] = False
                        item_result['details'].append(f"❌ 请求失败: {str(e)}")
                
                elif 'files' in item:
                    # 检查静态文件可用性
                    for file_path in item['files']:
                        try:
                            url = f"{self.base_url}{file_path}"
                            response = session.get(url)
                            if response.status_code == 200:
                                item_result['details'].append(f"✅ 文件可用: {file_path}")
                            else:
                                item_result['details'].append(f"❌ 文件不可用: {file_path} (状态码: {response.status_code})")
                                item_result['success'] = False
                        except Exception as e:
                            item_result['details'].append(f"❌ 文件检查失败: {file_path} - {str(e)}")
                            item_result['success'] = False
                
                elif 'endpoints' in item:
                    # 检查API端点可用性
                    for endpoint in item['endpoints']:
                        try:
                            url = f"{self.base_url}{endpoint}"
                            response = session.get(url)
                            if response.status_code in [200, 400, 422]:  # 400/422表示端点存在但参数无效
                                item_result['details'].append(f"✅ 端点可用: {endpoint}")
                            else:
                                item_result['details'].append(f"❌ 端点不可用: {endpoint} (状态码: {response.status_code})")
                                item_result['success'] = False
                        except Exception as e:
                            item_result['details'].append(f"❌ 端点检查失败: {endpoint} - {str(e)}")
                            item_result['success'] = False
                
                results.append(item_result)
                
                # 打印结果
                status = "✅" if item_result['success'] else "❌"
                print(f"{status} {item['name']}")
                for detail in item_result['details']:
                    print(f"   {detail}")
            
            # 统计结果
            successful_items = sum(1 for r in results if r['success'])
            total_items = len(results)
            
            return {
                'success': successful_items == total_items,
                'stats': {
                    'total': total_items,
                    'passed': successful_items,
                    'failed': total_items - successful_items
                },
                'results': results,
                'execution_time': 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'手动验证异常: {str(e)}',
                'stats': {},
                'execution_time': 0
            }
    
    def parse_test_output(self, output_lines: List[str]) -> Dict[str, int]:
        """解析测试输出，提取统计信息"""
        stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
        
        for line in output_lines:
            line = line.strip()
            
            # 查找统计信息
            if '总测试数:' in line:
                try:
                    stats['total'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif '通过测试:' in line:
                try:
                    stats['passed'] = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
            elif '失败测试:' in line:
                try:
                    stats['failed'] = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
            elif '警告测试:' in line:
                try:
                    stats['warnings'] = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
        
        return stats
    
    def update_overall_stats(self, test_name: str, test_result: Dict[str, Any]):
        """更新总体统计信息"""
        self.overall_stats['total_test_suites'] += 1
        
        if test_result['success']:
            self.overall_stats['passed_test_suites'] += 1
        else:
            self.overall_stats['failed_test_suites'] += 1
        
        # 更新个别测试统计
        if 'stats' in test_result and test_result['stats']:
            stats = test_result['stats']
            self.overall_stats['total_individual_tests'] += stats.get('total', 0)
            self.overall_stats['passed_individual_tests'] += stats.get('passed', 0)
            self.overall_stats['failed_individual_tests'] += stats.get('failed', 0)
            self.overall_stats['warning_individual_tests'] += stats.get('warnings', 0)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 开始运行复盘保存功能综合测试套件")
        print("=" * 80)
        
        overall_start_time = time.time()
        
        # 检查服务器状态
        if not self.check_server_status():
            print("❌ 服务器不可用，终止测试")
            return {
                'success': False,
                'error': '服务器不可用',
                'test_results': {},
                'overall_stats': self.overall_stats,
                'total_time': 0
            }
        
        # 运行各项测试
        test_suite = [
            ('手动验证检查', self.run_manual_verification),
            ('后端API测试', self.run_backend_api_tests),
            ('前端集成测试', self.run_integration_tests)
        ]
        
        for test_name, test_method in test_suite:
            print(f"\n{'='*20} 开始 {test_name} {'='*20}")
            
            try:
                test_result = test_method()
                self.test_results[test_name] = test_result
                self.update_overall_stats(test_name, test_result)
                
                # 显示测试结果摘要
                if test_result['success']:
                    print(f"✅ {test_name} 完成")
                else:
                    print(f"❌ {test_name} 失败")
                    if 'error' in test_result:
                        print(f"   错误: {test_result['error']}")
                
                if 'stats' in test_result and test_result['stats']:
                    stats = test_result['stats']
                    print(f"   统计: 总计 {stats.get('total', 0)}, 通过 {stats.get('passed', 0)}, 失败 {stats.get('failed', 0)}")
                
            except Exception as e:
                print(f"❌ {test_name} 执行异常: {str(e)}")
                self.test_results[test_name] = {
                    'success': False,
                    'error': f'执行异常: {str(e)}',
                    'stats': {},
                    'execution_time': 0
                }
                self.update_overall_stats(test_name, self.test_results[test_name])
            
            time.sleep(2)  # 测试套件间隔
        
        overall_end_time = time.time()
        total_time = overall_end_time - overall_start_time
        
        # 生成综合报告
        return self.generate_comprehensive_report(total_time)
    
    def generate_comprehensive_report(self, total_time: float) -> Dict[str, Any]:
        """生成综合测试报告"""
        print("\n" + "="*80)
        print("📊 综合测试结果汇总")
        print("="*80)
        
        # 测试套件统计
        print(f"测试套件统计:")
        print(f"  总测试套件: {self.overall_stats['total_test_suites']}")
        print(f"  通过套件: {self.overall_stats['passed_test_suites']} ✅")
        print(f"  失败套件: {self.overall_stats['failed_test_suites']} ❌")
        
        if self.overall_stats['total_test_suites'] > 0:
            suite_success_rate = (self.overall_stats['passed_test_suites'] / self.overall_stats['total_test_suites']) * 100
            print(f"  套件成功率: {suite_success_rate:.1f}%")
        
        # 个别测试统计
        print(f"\n个别测试统计:")
        print(f"  总测试数: {self.overall_stats['total_individual_tests']}")
        print(f"  通过测试: {self.overall_stats['passed_individual_tests']} ✅")
        print(f"  失败测试: {self.overall_stats['failed_individual_tests']} ❌")
        print(f"  警告测试: {self.overall_stats['warning_individual_tests']} ⚠️")
        
        if self.overall_stats['total_individual_tests'] > 0:
            individual_success_rate = (self.overall_stats['passed_individual_tests'] / self.overall_stats['total_individual_tests']) * 100
            print(f"  个别测试成功率: {individual_success_rate:.1f}%")
        
        print(f"\n总耗时: {total_time:.2f}秒")
        
        # 详细结果
        print(f"\n详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {test_name}")
            if 'execution_time' in result:
                print(f"     耗时: {result['execution_time']:.2f}秒")
            if not result['success'] and 'error' in result:
                print(f"     错误: {result['error']}")
        
        # 生成报告数据
        report = {
            'test_type': 'comprehensive',
            'overall_stats': self.overall_stats,
            'test_results': self.test_results,
            'total_time': total_time,
            'success': self.overall_stats['failed_test_suites'] == 0,
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url
        }
        
        return report
    
    def save_comprehensive_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存综合测试报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task8_comprehensive_test_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 综合测试报告已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")
            return ""
    
    def generate_html_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """生成HTML格式的测试报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task8_comprehensive_test_report_{timestamp}.html"
        
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>任务8 - 复盘保存功能综合测试报告</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8f9fa; }}
        .test-success {{ color: #28a745; }}
        .test-failure {{ color: #dc3545; }}
        .test-warning {{ color: #ffc107; }}
        .card {{ margin-bottom: 1rem; }}
        .stat-card {{ text-align: center; padding: 1rem; }}
        .stat-number {{ font-size: 2rem; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">
                    <i class="fas fa-clipboard-check text-primary"></i>
                    任务8 - 复盘保存功能综合测试报告
                </h1>
                <p class="text-center text-muted">生成时间: {report['timestamp']}</p>
                <p class="text-center text-muted">目标服务器: {report['base_url']}</p>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-number text-primary">{report['overall_stats']['total_test_suites']}</div>
                    <div>测试套件总数</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-number test-success">{report['overall_stats']['passed_test_suites']}</div>
                    <div>通过套件</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-number test-failure">{report['overall_stats']['failed_test_suites']}</div>
                    <div>失败套件</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-number text-info">{report['total_time']:.2f}s</div>
                    <div>总耗时</div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-number text-primary">{report['overall_stats']['total_individual_tests']}</div>
                    <div>个别测试总数</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-number test-success">{report['overall_stats']['passed_individual_tests']}</div>
                    <div>通过测试</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-number test-failure">{report['overall_stats']['failed_individual_tests']}</div>
                    <div>失败测试</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-number test-warning">{report['overall_stats']['warning_individual_tests']}</div>
                    <div>警告测试</div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <h3>详细测试结果</h3>
            </div>
        </div>
"""
            
            # 添加每个测试套件的详细结果
            for test_name, result in report['test_results'].items():
                success_class = "test-success" if result['success'] else "test-failure"
                icon = "fas fa-check-circle" if result['success'] else "fas fa-times-circle"
                
                html_content += f"""
        <div class="row mb-3">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="{success_class}">
                            <i class="{icon}"></i>
                            {test_name}
                        </h5>
                    </div>
                    <div class="card-body">
"""
                
                if 'stats' in result and result['stats']:
                    stats = result['stats']
                    html_content += f"""
                        <div class="row mb-2">
                            <div class="col-md-3">总计: {stats.get('total', 0)}</div>
                            <div class="col-md-3 test-success">通过: {stats.get('passed', 0)}</div>
                            <div class="col-md-3 test-failure">失败: {stats.get('failed', 0)}</div>
                            <div class="col-md-3 test-warning">警告: {stats.get('warnings', 0)}</div>
                        </div>
"""
                
                if 'execution_time' in result:
                    html_content += f"<p><strong>执行时间:</strong> {result['execution_time']:.2f}秒</p>"
                
                if not result['success'] and 'error' in result:
                    html_content += f"<p class='test-failure'><strong>错误:</strong> {result['error']}</p>"
                
                html_content += """
                    </div>
                </div>
            </div>
        </div>
"""
            
            html_content += """
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📄 HTML测试报告已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 生成HTML报告失败: {str(e)}")
            return ""

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='复盘保存功能综合测试运行器')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='服务器URL (默认: http://localhost:5000)')
    parser.add_argument('--output', help='输出报告文件名前缀')
    parser.add_argument('--html', action='store_true', help='生成HTML报告')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = ComprehensiveTestRunner(args.url)
    
    try:
        # 运行所有测试
        report = runner.run_all_tests()
        
        # 保存JSON报告
        json_filename = None
        if args.output:
            json_filename = f"{args.output}.json"
        
        runner.save_comprehensive_report(report, json_filename)
        
        # 生成HTML报告
        if args.html:
            html_filename = None
            if args.output:
                html_filename = f"{args.output}.html"
            runner.generate_html_report(report, html_filename)
        
        # 根据测试结果设置退出码
        if report['success']:
            print("\n🎉 所有测试套件通过!")
            sys.exit(0)
        else:
            print(f"\n⚠️ 有 {report['overall_stats']['failed_test_suites']} 个测试套件失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()