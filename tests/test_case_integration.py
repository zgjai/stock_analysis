"""
案例管理集成测试
"""
import os
import json
from io import BytesIO
from PIL import Image
import pytest
from models.case_study import CaseStudy
from services.case_service import CaseService


class TestCaseIntegration:
    """案例管理集成测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.service = CaseService()
    
    def create_test_image(self, format='PNG', size=(100, 100), color='red'):
        """创建测试图片"""
        img = Image.new('RGB', size, color=color)
        img_io = BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        return img_io
    
    def test_complete_case_workflow(self, client, app):
        """测试完整的案例管理工作流程"""
        # 1. 上传案例
        img_data = self.create_test_image()
        upload_data = {
            'file': (img_data, 'workflow_test.png', 'image/png'),
            'stock_code': '000001',
            'title': '工作流程测试案例',
            'tags': '["技术分析", "突破", "测试"]',
            'notes': '这是一个完整工作流程的测试案例'
        }
        
        upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        assert upload_response.status_code == 200
        
        case_data = upload_response.get_json()['data']
        case_id = case_data['id']
        image_path = case_data['image_path']
        
        # 验证文件存在
        assert os.path.exists(image_path)
        
        # 2. 获取案例详情
        detail_response = client.get(f'/api/cases/{case_id}')
        assert detail_response.status_code == 200
        
        detail_data = detail_response.get_json()['data']
        assert detail_data['stock_code'] == '000001'
        assert detail_data['title'] == '工作流程测试案例'
        assert len(detail_data['tags_list']) == 3
        
        # 3. 更新案例信息
        update_data = {
            'title': '更新后的标题',
            'tags': ['技术分析', '更新标签'],
            'notes': '更新后的备注'
        }
        update_response = client.put(f'/api/cases/{case_id}', json=update_data)
        assert update_response.status_code == 200
        
        updated_data = update_response.get_json()['data']
        assert updated_data['title'] == '更新后的标题'
        assert '更新标签' in updated_data['tags_list']
        
        # 4. 通过不同方式搜索案例
        # 按股票代码搜索
        stock_response = client.get('/api/cases/by-stock/000001')
        assert stock_response.status_code == 200
        stock_cases = stock_response.get_json()['data']
        assert len(stock_cases) >= 1
        
        # 按标签搜索
        tag_response = client.get('/api/cases/by-tag/技术分析')
        assert tag_response.status_code == 200
        tag_cases = tag_response.get_json()['data']
        assert len(tag_cases) >= 1
        
        # 关键词搜索
        search_data = {'keyword': '更新后'}
        search_response = client.post('/api/cases/search', json=search_data)
        assert search_response.status_code == 200
        search_result = search_response.get_json()['data']
        assert search_result['total'] >= 1
        
        # 5. 获取图片
        image_response = client.get(f'/api/cases/{case_id}/image')
        assert image_response.status_code == 200
        assert image_response.content_type.startswith('image/')
        
        # 6. 获取统计信息
        stats_response = client.get('/api/cases/statistics')
        assert stats_response.status_code == 200
        stats = stats_response.get_json()['data']
        assert stats['total_cases'] >= 1
        assert stats['cases_with_stock'] >= 1
        assert stats['cases_with_tags'] >= 1
        
        # 7. 获取所有标签
        tags_response = client.get('/api/cases/tags')
        assert tags_response.status_code == 200
        all_tags = tags_response.get_json()['data']
        tag_names = [tag['tag'] for tag in all_tags]
        assert '技术分析' in tag_names
        assert '更新标签' in tag_names
        
        # 8. 删除案例
        delete_response = client.delete(f'/api/cases/{case_id}')
        assert delete_response.status_code == 200
        
        # 验证文件被删除
        assert not os.path.exists(image_path)
        
        # 验证数据库记录被删除
        deleted_case_response = client.get(f'/api/cases/{case_id}')
        assert deleted_case_response.status_code == 404
    
    def test_batch_operations(self, client, app):
        """测试批量操作"""
        cases = []
        
        # 批量上传案例
        for i in range(3):
            img_data = self.create_test_image(color=['red', 'green', 'blue'][i])
            upload_data = {
                'file': (img_data, f'batch_test_{i}.png', 'image/png'),
                'stock_code': f'00000{i+1}',
                'title': f'批量测试案例{i+1}',
                'tags': f'["批量测试", "案例{i+1}"]',
                'notes': f'这是第{i+1}个批量测试案例'
            }
            
            response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
            assert response.status_code == 200
            cases.append(response.get_json()['data'])
        
        # 验证所有案例都被创建
        list_response = client.get('/api/cases?keyword=批量测试')
        assert list_response.status_code == 200
        case_list = list_response.get_json()['data']
        assert case_list['total'] >= 3
        
        # 按标签搜索
        tag_response = client.get('/api/cases/by-tag/批量测试')
        assert tag_response.status_code == 200
        tag_cases = tag_response.get_json()['data']
        assert len(tag_cases) == 3
        
        # 批量删除
        for case in cases:
            delete_response = client.delete(f'/api/cases/{case["id"]}')
            assert delete_response.status_code == 200
            
            # 验证文件被删除
            assert not os.path.exists(case['image_path'])
    
    def test_image_format_handling(self, client, app):
        """测试不同图片格式的处理"""
        formats_to_test = [
            ('JPEG', 'test.jpg', 'image/jpeg'),
            ('PNG', 'test.png', 'image/png'),
            ('BMP', 'test.bmp', 'image/bmp')
        ]
        
        uploaded_cases = []
        
        for format_name, filename, content_type in formats_to_test:
            img_data = self.create_test_image(format=format_name)
            upload_data = {
                'file': (img_data, filename, content_type),
                'title': f'{format_name}格式测试',
                'notes': f'测试{format_name}格式图片上传'
            }
            
            response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
            assert response.status_code == 200
            
            case_data = response.get_json()['data']
            uploaded_cases.append(case_data)
            
            # 验证所有格式都被转换为PNG
            assert case_data['image_path'].endswith('.png')
            assert os.path.exists(case_data['image_path'])
            
            # 验证转换后的图片是RGB模式
            with Image.open(case_data['image_path']) as img:
                assert img.mode == 'RGB'
        
        # 清理测试文件
        for case in uploaded_cases:
            client.delete(f'/api/cases/{case["id"]}')
    
    def test_large_image_handling(self, client, app):
        """测试大图片处理"""
        # 创建一个大尺寸图片
        large_img = self.create_test_image(size=(2500, 1800))
        upload_data = {
            'file': (large_img, 'large_image.png', 'image/png'),
            'title': '大图片测试',
            'notes': '测试大尺寸图片的自动调整'
        }
        
        response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        assert response.status_code == 200
        
        case_data = response.get_json()['data']
        
        # 验证图片尺寸被调整
        with Image.open(case_data['image_path']) as img:
            width, height = img.size
            assert width <= 1920
            assert height <= 1080
        
        # 清理测试文件
        client.delete(f'/api/cases/{case_data["id"]}')
    
    def test_tag_management_integration(self, client, app):
        """测试标签管理集成"""
        # 创建多个带有不同标签的案例
        test_cases = [
            (['技术分析', '突破'], '技术分析案例1'),
            (['技术分析', '回调'], '技术分析案例2'),
            (['基本面', '财报'], '基本面分析案例'),
            (['技术分析', '支撑位'], '技术分析案例3')
        ]
        
        uploaded_cases = []
        
        for tags, title in test_cases:
            img_data = self.create_test_image()
            upload_data = {
                'file': (img_data, f'{title}.png', 'image/png'),
                'title': title,
                'tags': json.dumps(tags),
                'notes': f'{title}的备注'
            }
            
            response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
            assert response.status_code == 200
            uploaded_cases.append(response.get_json()['data'])
        
        # 测试标签统计
        tags_response = client.get('/api/cases/tags')
        assert tags_response.status_code == 200
        all_tags = tags_response.get_json()['data']
        
        # 验证标签计数
        tag_counts = {tag['tag']: tag['count'] for tag in all_tags}
        assert tag_counts.get('技术分析', 0) == 3
        assert tag_counts.get('基本面', 0) == 1
        assert tag_counts.get('突破', 0) == 1
        assert tag_counts.get('回调', 0) == 1
        assert tag_counts.get('财报', 0) == 1
        assert tag_counts.get('支撑位', 0) == 1
        
        # 测试按标签搜索
        tech_analysis_response = client.get('/api/cases/by-tag/技术分析')
        assert tech_analysis_response.status_code == 200
        tech_cases = tech_analysis_response.get_json()['data']
        assert len(tech_cases) == 3
        
        fundamental_response = client.get('/api/cases/by-tag/基本面')
        assert fundamental_response.status_code == 200
        fundamental_cases = fundamental_response.get_json()['data']
        assert len(fundamental_cases) == 1
        
        # 测试多标签搜索
        multi_tag_search = {
            'tags': ['技术分析', '突破']
        }
        search_response = client.post('/api/cases/search', json=multi_tag_search)
        assert search_response.status_code == 200
        search_result = search_response.get_json()['data']
        assert search_result['total'] == 1  # 只有一个案例同时包含这两个标签
        
        # 清理测试文件
        for case in uploaded_cases:
            client.delete(f'/api/cases/{case["id"]}')
    
    def test_search_functionality_comprehensive(self, client, app):
        """测试综合搜索功能"""
        # 创建测试数据
        test_data = [
            {
                'stock_code': '000001',
                'title': '平安银行技术分析',
                'tags': ['技术分析', '银行股'],
                'notes': '平安银行的技术分析案例'
            },
            {
                'stock_code': '000002',
                'title': '万科A基本面分析',
                'tags': ['基本面', '房地产'],
                'notes': '万科A的基本面分析案例'
            },
            {
                'stock_code': '000001',
                'title': '平安银行突破形态',
                'tags': ['技术分析', '突破', '银行股'],
                'notes': '平安银行突破形态分析'
            }
        ]
        
        uploaded_cases = []
        
        for i, data in enumerate(test_data):
            img_data = self.create_test_image()
            upload_data = {
                'file': (img_data, f'search_test_{i}.png', 'image/png'),
                'stock_code': data['stock_code'],
                'title': data['title'],
                'tags': json.dumps(data['tags']),
                'notes': data['notes']
            }
            
            response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
            assert response.status_code == 200
            uploaded_cases.append(response.get_json()['data'])
        
        # 测试各种搜索方式
        
        # 1. 关键词搜索（标题）
        search_response = client.post('/api/cases/search', json={'keyword': '平安银行'})
        assert search_response.status_code == 200
        result = search_response.get_json()['data']
        assert result['total'] == 2
        
        # 2. 关键词搜索（备注）
        search_response = client.post('/api/cases/search', json={'keyword': '基本面分析'})
        assert search_response.status_code == 200
        result = search_response.get_json()['data']
        assert result['total'] == 1
        
        # 3. 股票代码搜索
        search_response = client.post('/api/cases/search', json={'stock_code': '000001'})
        assert search_response.status_code == 200
        result = search_response.get_json()['data']
        assert result['total'] == 2
        
        # 4. 单标签搜索
        search_response = client.post('/api/cases/search', json={'tags': ['技术分析']})
        assert search_response.status_code == 200
        result = search_response.get_json()['data']
        assert result['total'] == 2
        
        # 5. 多标签搜索（AND逻辑）
        search_response = client.post('/api/cases/search', json={'tags': ['技术分析', '银行股']})
        assert search_response.status_code == 200
        result = search_response.get_json()['data']
        assert result['total'] == 2
        
        # 6. 组合搜索
        search_response = client.post('/api/cases/search', json={
            'keyword': '分析',
            'stock_code': '000001'
        })
        assert search_response.status_code == 200
        result = search_response.get_json()['data']
        assert result['total'] == 2
        
        # 清理测试文件
        for case in uploaded_cases:
            client.delete(f'/api/cases/{case["id"]}')
    
    def test_error_handling_integration(self, client, app):
        """测试错误处理集成"""
        # 1. 测试上传无效文件
        invalid_data = BytesIO(b"This is not an image")
        upload_data = {
            'file': (invalid_data, 'invalid.txt', 'text/plain'),
            'title': '无效文件测试'
        }
        
        response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        assert response.status_code == 400
        assert "不支持的文件格式" in response.get_json()['error']['message']
        
        # 2. 测试获取不存在的案例
        response = client.get('/api/cases/99999')
        assert response.status_code == 404
        assert "案例不存在" in response.get_json()['error']['message']
        
        # 3. 测试更新不存在的案例
        response = client.put('/api/cases/99999', json={'title': '新标题'})
        assert response.status_code == 404
        assert "案例不存在" in response.get_json()['error']['message']
        
        # 4. 测试删除不存在的案例
        response = client.delete('/api/cases/99999')
        assert response.status_code == 404
        assert "案例不存在" in response.get_json()['error']['message']
        
        # 5. 测试获取不存在案例的图片
        response = client.get('/api/cases/99999/image')
        assert response.status_code == 404
        assert "案例不存在" in response.get_json()['error']['message']