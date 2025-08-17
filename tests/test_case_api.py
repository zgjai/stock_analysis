"""
案例管理API测试
"""
import os
import json
import tempfile
from io import BytesIO
from PIL import Image
import pytest
from werkzeug.datastructures import FileStorage


class TestCaseAPI:
    """案例管理API测试类"""
    
    def create_test_image(self, format='PNG', size=(100, 100)):
        """创建测试图片"""
        img = Image.new('RGB', size, color='blue')
        img_io = BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        return img_io
    
    def test_upload_case_success(self, client, app):
        """测试成功上传案例"""
        img_data = self.create_test_image()
        
        data = {
            'file': (img_data, 'test.png', 'image/png'),
            'stock_code': '000001',
            'title': '测试案例',
            'tags': '["技术分析", "突破"]',
            'notes': '这是一个测试案例'
        }
        
        response = client.post('/api/cases', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['stock_code'] == '000001'
        assert result['data']['title'] == '测试案例'
        assert result['data']['tags_list'] == ['技术分析', '突破']
        
        # 清理测试文件
        if 'image_path' in result['data'] and os.path.exists(result['data']['image_path']):
            os.remove(result['data']['image_path'])
    
    def test_upload_case_without_file(self, client, app):
        """测试上传案例时没有文件"""
        data = {
            'title': '测试案例',
            'notes': '没有文件的案例'
        }
        
        response = client.post('/api/cases', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] is False
        assert "请选择要上传的文件" in result['error']['message']
    
    def test_upload_case_invalid_format(self, client, app):
        """测试上传不支持的文件格式"""
        text_data = BytesIO(b"This is not an image")
        
        data = {
            'file': (text_data, 'test.txt', 'text/plain'),
            'title': '测试案例'
        }
        
        response = client.post('/api/cases', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] is False
        assert "不支持的文件格式" in result['error']['message']
    
    def test_get_cases_list(self, client, app):
        """测试获取案例列表"""
        # 先上传一个案例
        img_data = self.create_test_image()
        upload_data = {
            'file': (img_data, 'test.png', 'image/png'),
            'title': '列表测试案例'
        }
        upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        uploaded_case = upload_response.get_json()['data']
        
        # 获取案例列表
        response = client.get('/api/cases')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert 'cases' in result['data']
        assert result['data']['total'] >= 1
        
        # 清理测试文件
        if os.path.exists(uploaded_case['image_path']):
            os.remove(uploaded_case['image_path'])
    
    def test_get_case_detail(self, client, app):
        """测试获取案例详情"""
        # 先上传一个案例
        img_data = self.create_test_image()
        upload_data = {
            'file': (img_data, 'test.png', 'image/png'),
            'title': '详情测试案例',
            'notes': '这是详情测试'
        }
        upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        uploaded_case = upload_response.get_json()['data']
        
        # 获取案例详情
        response = client.get(f'/api/cases/{uploaded_case["id"]}')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['title'] == '详情测试案例'
        assert result['data']['notes'] == '这是详情测试'
        
        # 清理测试文件
        if os.path.exists(uploaded_case['image_path']):
            os.remove(uploaded_case['image_path'])
    
    def test_update_case(self, client, app):
        """测试更新案例"""
        # 先上传一个案例
        img_data = self.create_test_image()
        upload_data = {
            'file': (img_data, 'test.png', 'image/png'),
            'title': '原标题'
        }
        upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        uploaded_case = upload_response.get_json()['data']
        
        # 更新案例
        update_data = {
            'title': '新标题',
            'tags': ['新标签'],
            'notes': '新备注'
        }
        response = client.put(f'/api/cases/{uploaded_case["id"]}', 
                            json=update_data,
                            content_type='application/json')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['title'] == '新标题'
        assert result['data']['tags_list'] == ['新标签']
        assert result['data']['notes'] == '新备注'
        
        # 清理测试文件
        if os.path.exists(uploaded_case['image_path']):
            os.remove(uploaded_case['image_path'])
    
    def test_delete_case(self, client, app):
        """测试删除案例"""
        # 先上传一个案例
        img_data = self.create_test_image()
        upload_data = {
            'file': (img_data, 'test.png', 'image/png'),
            'title': '待删除案例'
        }
        upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        uploaded_case = upload_response.get_json()['data']
        image_path = uploaded_case['image_path']
        
        # 验证文件存在
        assert os.path.exists(image_path)
        
        # 删除案例
        response = client.delete(f'/api/cases/{uploaded_case["id"]}')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert "案例删除成功" in result['message']
        
        # 验证文件被删除
        assert not os.path.exists(image_path)
    
    def test_get_case_image(self, client, app):
        """测试获取案例图片"""
        # 先上传一个案例
        img_data = self.create_test_image()
        upload_data = {
            'file': (img_data, 'test.png', 'image/png'),
            'title': '图片测试案例'
        }
        upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        uploaded_case = upload_response.get_json()['data']
        
        # 获取案例图片
        response = client.get(f'/api/cases/{uploaded_case["id"]}/image')
        

        assert response.status_code == 200
        assert response.content_type.startswith('image/')
        
        # 清理测试文件
        if os.path.exists(uploaded_case['image_path']):
            os.remove(uploaded_case['image_path'])
    
    def test_get_cases_by_stock_code(self, client, app):
        """测试根据股票代码获取案例"""
        # 上传两个相同股票代码的案例
        img_data1 = self.create_test_image()
        img_data2 = self.create_test_image()
        
        upload_data1 = {
            'file': (img_data1, 'test1.png', 'image/png'),
            'stock_code': '000001',
            'title': '案例1'
        }
        upload_data2 = {
            'file': (img_data2, 'test2.png', 'image/png'),
            'stock_code': '000001',
            'title': '案例2'
        }
        
        upload_response1 = client.post('/api/cases', data=upload_data1, content_type='multipart/form-data')
        upload_response2 = client.post('/api/cases', data=upload_data2, content_type='multipart/form-data')
        
        case1 = upload_response1.get_json()['data']
        case2 = upload_response2.get_json()['data']
        
        # 根据股票代码获取案例
        response = client.get('/api/cases/by-stock/000001')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert len(result['data']) == 2
        
        # 清理测试文件
        for case in [case1, case2]:
            if os.path.exists(case['image_path']):
                os.remove(case['image_path'])
    
    def test_get_cases_by_tag(self, client, app):
        """测试根据标签获取案例"""
        # 上传带有相同标签的案例
        img_data1 = self.create_test_image()
        img_data2 = self.create_test_image()
        
        upload_data1 = {
            'file': (img_data1, 'test1.png', 'image/png'),
            'title': '案例1',
            'tags': '["技术分析"]'
        }
        upload_data2 = {
            'file': (img_data2, 'test2.png', 'image/png'),
            'title': '案例2',
            'tags': '["技术分析", "突破"]'
        }
        
        upload_response1 = client.post('/api/cases', data=upload_data1, content_type='multipart/form-data')
        upload_response2 = client.post('/api/cases', data=upload_data2, content_type='multipart/form-data')
        
        case1 = upload_response1.get_json()['data']
        case2 = upload_response2.get_json()['data']
        
        # 根据标签获取案例
        response = client.get('/api/cases/by-tag/技术分析')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert len(result['data']) == 2
        
        # 清理测试文件
        for case in [case1, case2]:
            if os.path.exists(case['image_path']):
                os.remove(case['image_path'])
    
    def test_get_all_tags(self, client, app):
        """测试获取所有标签"""
        # 上传带有标签的案例
        img_data = self.create_test_image()
        upload_data = {
            'file': (img_data, 'test.png', 'image/png'),
            'title': '标签测试案例',
            'tags': '["技术分析", "突破", "回调"]'
        }
        
        upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        uploaded_case = upload_response.get_json()['data']
        
        # 获取所有标签
        response = client.get('/api/cases/tags')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert len(result['data']) >= 3
        
        # 验证标签格式
        for tag_info in result['data']:
            assert 'tag' in tag_info
            assert 'count' in tag_info
            assert isinstance(tag_info['count'], int)
        
        # 清理测试文件
        if os.path.exists(uploaded_case['image_path']):
            os.remove(uploaded_case['image_path'])
    
    def test_get_statistics(self, client, app):
        """测试获取统计信息"""
        # 上传一个案例
        img_data = self.create_test_image()
        upload_data = {
            'file': (img_data, 'test.png', 'image/png'),
            'stock_code': '000001',
            'title': '统计测试案例',
            'tags': '["技术分析"]'
        }
        
        upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        uploaded_case = upload_response.get_json()['data']
        
        # 获取统计信息
        response = client.get('/api/cases/statistics')
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        
        stats = result['data']
        assert 'total_cases' in stats
        assert 'cases_with_stock' in stats
        assert 'cases_with_tags' in stats
        assert 'recent_cases' in stats
        assert 'total_tags' in stats
        
        assert stats['total_cases'] >= 1
        assert stats['cases_with_stock'] >= 1
        assert stats['cases_with_tags'] >= 1
        
        # 清理测试文件
        if os.path.exists(uploaded_case['image_path']):
            os.remove(uploaded_case['image_path'])
    
    def test_search_cases(self, client, app):
        """测试高级搜索案例"""
        # 上传测试案例
        img_data = self.create_test_image()
        upload_data = {
            'file': (img_data, 'test.png', 'image/png'),
            'stock_code': '000001',
            'title': '搜索测试案例',
            'tags': '["技术分析"]',
            'notes': '这是搜索测试的备注'
        }
        
        upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
        uploaded_case = upload_response.get_json()['data']
        
        # 关键词搜索
        search_data = {'keyword': '搜索测试'}
        response = client.post('/api/cases/search', json=search_data)
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['total'] >= 1
        
        # 股票代码搜索
        search_data = {'stock_code': '000001'}
        response = client.post('/api/cases/search', json=search_data)
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['total'] >= 1
        
        # 标签搜索
        search_data = {'tags': ['技术分析']}
        response = client.post('/api/cases/search', json=search_data)
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert result['data']['total'] >= 1
        
        # 清理测试文件
        if os.path.exists(uploaded_case['image_path']):
            os.remove(uploaded_case['image_path'])
    
    def test_search_cases_with_pagination(self, client, app):
        """测试搜索案例的分页功能"""
        # 上传多个案例
        cases = []
        for i in range(5):
            img_data = self.create_test_image()
            upload_data = {
                'file': (img_data, f'test{i}.png', 'image/png'),
                'title': f'分页测试案例{i}'
            }
            upload_response = client.post('/api/cases', data=upload_data, content_type='multipart/form-data')
            cases.append(upload_response.get_json()['data'])
        
        # 测试分页
        search_data = {
            'keyword': '分页测试',
            'page': 1,
            'per_page': 2
        }
        response = client.post('/api/cases/search', json=search_data)
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] is True
        assert len(result['data']['cases']) <= 2
        assert result['data']['current_page'] == 1
        assert result['data']['per_page'] == 2
        
        # 清理测试文件
        for case in cases:
            if os.path.exists(case['image_path']):
                os.remove(case['image_path'])
    
    def test_get_nonexistent_case(self, client, app):
        """测试获取不存在的案例"""
        response = client.get('/api/cases/99999')
        
        assert response.status_code == 404
        result = response.get_json()
        assert result['success'] is False
        assert "案例不存在" in result['error']['message']
    
    def test_update_nonexistent_case(self, client, app):
        """测试更新不存在的案例"""
        update_data = {'title': '新标题'}
        response = client.put('/api/cases/99999', json=update_data)
        
        assert response.status_code == 404
        result = response.get_json()
        assert result['success'] is False
        assert "案例不存在" in result['error']['message']
    
    def test_delete_nonexistent_case(self, client, app):
        """测试删除不存在的案例"""
        response = client.delete('/api/cases/99999')
        
        assert response.status_code == 404
        result = response.get_json()
        assert result['success'] is False
        assert "案例不存在" in result['error']['message']