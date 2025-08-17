"""
案例管理服务测试
"""
import os
import json
import tempfile
import pytest
from PIL import Image
from io import BytesIO
from werkzeug.datastructures import FileStorage
from services.case_service import CaseService
from models.case_study import CaseStudy
from error_handlers import ValidationError, FileOperationError


class TestCaseService:
    """案例管理服务测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.service = CaseService()
    
    def create_test_image(self, format='PNG', size=(100, 100)):
        """创建测试图片"""
        img = Image.new('RGB', size, color='red')
        img_io = BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        return img_io
    
    def create_file_storage(self, filename, content=None, format='PNG'):
        """创建FileStorage对象"""
        if content is None:
            content = self.create_test_image(format=format)
        
        return FileStorage(
            stream=content,
            filename=filename,
            content_type=f'image/{format.lower()}'
        )
    
    def test_upload_image_success(self, app):
        """测试成功上传图片"""
        with app.app_context():
            file = self.create_file_storage('test.png')
            
            result = self.service.upload_image(
                file=file,
                stock_code='000001',
                title='测试案例',
                tags=['技术分析', '突破'],
                notes='这是一个测试案例'
            )
            
            assert result['stock_code'] == '000001'
            assert result['title'] == '测试案例'
            assert result['tags_list'] == ['技术分析', '突破']
            assert result['notes'] == '这是一个测试案例'
            assert 'image_path' in result
            assert os.path.exists(result['image_path'])
            
            # 清理测试文件
            if os.path.exists(result['image_path']):
                os.remove(result['image_path'])
    
    def test_upload_image_without_file(self, app):
        """测试上传空文件"""
        with app.app_context():
            with pytest.raises(ValidationError) as exc_info:
                self.service.upload_image(file=None)
            
            assert "请选择要上传的文件" in str(exc_info.value)
    
    def test_upload_image_invalid_format(self, app):
        """测试上传不支持的文件格式"""
        with app.app_context():
            # 创建一个文本文件
            text_content = BytesIO(b"This is not an image")
            file = FileStorage(
                stream=text_content,
                filename='test.txt',
                content_type='text/plain'
            )
            
            with pytest.raises(ValidationError) as exc_info:
                self.service.upload_image(file=file)
            
            assert "不支持的文件格式" in str(exc_info.value)
    
    def test_upload_large_image(self, app):
        """测试上传大尺寸图片（应该被自动调整）"""
        # 创建一个大尺寸图片
        large_img = self.create_test_image(size=(3000, 2000))
        file = self.create_file_storage('large.png', large_img)
        
        result = self.service.upload_image(
            file=file,
            title='大图片测试'
        )
        
        # 验证图片被调整了尺寸
        with Image.open(result['image_path']) as img:
            width, height = img.size
            assert width <= 1920
            assert height <= 1080
        
        # 清理测试文件
        if os.path.exists(result['image_path']):
            os.remove(result['image_path'])
    
    def test_convert_image_format(self, app):
        """测试图片格式转换"""
        # 创建JPEG图片
        jpeg_img = self.create_test_image(format='JPEG')
        file = self.create_file_storage('test.jpg', jpeg_img, 'JPEG')
        
        result = self.service.upload_image(file=file, title='格式转换测试')
        
        # 验证转换为PNG格式
        assert result['image_path'].endswith('.png')
        assert os.path.exists(result['image_path'])
        
        # 清理测试文件
        if os.path.exists(result['image_path']):
            os.remove(result['image_path'])
    
    def test_update_case(self, app):
        """测试更新案例"""
        # 先创建一个案例
        file = self.create_file_storage('test.png')
        case = self.service.upload_image(file=file, title='原标题')
        
        # 更新案例
        updated = self.service.update_case(
            case['id'],
            title='新标题',
            tags=['新标签'],
            notes='新备注'
        )
        
        assert updated['title'] == '新标题'
        assert updated['tags_list'] == ['新标签']
        assert updated['notes'] == '新备注'
        
        # 清理测试文件
        if os.path.exists(case['image_path']):
            os.remove(case['image_path'])
    
    def test_delete_case(self, app):
        """测试删除案例"""
        # 先创建一个案例
        file = self.create_file_storage('test.png')
        case = self.service.upload_image(file=file, title='待删除案例')
        image_path = case['image_path']
        
        # 验证文件存在
        assert os.path.exists(image_path)
        
        # 删除案例
        result = self.service.delete_case(case['id'])
        assert result is True
        
        # 验证文件被删除
        assert not os.path.exists(image_path)
        
        # 验证数据库记录被删除
        deleted_case = self.service.get_by_id(case['id'])
        assert deleted_case is None
    
    def test_get_cases_by_stock_code(self, app):
        """测试根据股票代码获取案例"""
        # 创建测试案例
        file1 = self.create_file_storage('test1.png')
        file2 = self.create_file_storage('test2.png')
        
        case1 = self.service.upload_image(file=file1, stock_code='000001', title='案例1')
        case2 = self.service.upload_image(file=file2, stock_code='000001', title='案例2')
        case3 = self.service.upload_image(file=self.create_file_storage('test3.png'), 
                                        stock_code='000002', title='案例3')
        
        # 获取000001的案例
        cases = self.service.get_cases_by_stock_code('000001')
        assert len(cases) == 2
        
        # 清理测试文件
        for case in [case1, case2, case3]:
            if os.path.exists(case['image_path']):
                os.remove(case['image_path'])
    
    def test_get_cases_by_tag(self, app):
        """测试根据标签获取案例"""
        # 创建测试案例
        file1 = self.create_file_storage('test1.png')
        file2 = self.create_file_storage('test2.png')
        
        case1 = self.service.upload_image(file=file1, tags=['技术分析'], title='案例1')
        case2 = self.service.upload_image(file=file2, tags=['技术分析', '突破'], title='案例2')
        case3 = self.service.upload_image(file=self.create_file_storage('test3.png'), 
                                        tags=['基本面'], title='案例3')
        
        # 获取技术分析标签的案例
        cases = self.service.get_cases_by_tag('技术分析')
        assert len(cases) == 2
        
        # 清理测试文件
        for case in [case1, case2, case3]:
            if os.path.exists(case['image_path']):
                os.remove(case['image_path'])
    
    def test_search_cases(self, app):
        """测试搜索案例"""
        # 创建测试案例
        file1 = self.create_file_storage('test1.png')
        file2 = self.create_file_storage('test2.png')
        
        case1 = self.service.upload_image(
            file=file1, 
            stock_code='000001',
            title='技术分析案例',
            tags=['技术分析'],
            notes='这是技术分析的案例'
        )
        case2 = self.service.upload_image(
            file=file2,
            stock_code='000002', 
            title='基本面分析',
            tags=['基本面'],
            notes='这是基本面分析的案例'
        )
        
        # 关键词搜索
        result = self.service.search_cases(keyword='技术分析')
        assert result['total'] >= 1
        
        # 股票代码搜索
        result = self.service.search_cases(stock_code='000001')
        assert result['total'] >= 1
        
        # 标签搜索
        result = self.service.search_cases(tags=['技术分析'])
        assert result['total'] >= 1
        
        # 清理测试文件
        for case in [case1, case2]:
            if os.path.exists(case['image_path']):
                os.remove(case['image_path'])
    
    def test_get_all_tags(self, app):
        """测试获取所有标签"""
        # 创建测试案例
        file1 = self.create_file_storage('test1.png')
        file2 = self.create_file_storage('test2.png')
        
        case1 = self.service.upload_image(file=file1, tags=['技术分析', '突破'], title='案例1')
        case2 = self.service.upload_image(file=file2, tags=['技术分析', '回调'], title='案例2')
        
        # 获取所有标签
        tags = self.service.get_all_tags()
        
        # 验证标签存在且有计数
        tag_names = [tag['tag'] for tag in tags]
        assert '技术分析' in tag_names
        assert '突破' in tag_names
        assert '回调' in tag_names
        
        # 验证技术分析标签的计数为2
        tech_analysis_tag = next(tag for tag in tags if tag['tag'] == '技术分析')
        assert tech_analysis_tag['count'] == 2
        
        # 清理测试文件
        for case in [case1, case2]:
            if os.path.exists(case['image_path']):
                os.remove(case['image_path'])
    
    def test_get_statistics(self, app):
        """测试获取统计信息"""
        # 创建测试案例
        file1 = self.create_file_storage('test1.png')
        file2 = self.create_file_storage('test2.png')
        
        case1 = self.service.upload_image(file=file1, stock_code='000001', tags=['技术分析'], title='案例1')
        case2 = self.service.upload_image(file=file2, tags=['基本面'], title='案例2')
        
        # 获取统计信息
        stats = self.service.get_statistics()
        
        assert stats['total_cases'] >= 2
        assert stats['cases_with_stock'] >= 1
        assert stats['cases_with_tags'] >= 2
        assert stats['total_tags'] >= 2
        
        # 清理测试文件
        for case in [case1, case2]:
            if os.path.exists(case['image_path']):
                os.remove(case['image_path'])
    
    def test_file_size_limit(self, app):
        """测试文件大小限制"""
        # 创建一个超大的图片数据（模拟）
        large_data = BytesIO(b'x' * (11 * 1024 * 1024))  # 11MB
        file = FileStorage(
            stream=large_data,
            filename='large.png',
            content_type='image/png'
        )
        
        with pytest.raises(ValidationError) as exc_info:
            self.service.upload_image(file=file)
        
        assert "文件大小超过限制" in str(exc_info.value)
    
    def test_image_format_conversion_rgba(self, app):
        """测试RGBA格式图片转换"""
        # 创建RGBA格式图片
        img = Image.new('RGBA', (100, 100), (255, 0, 0, 128))  # 半透明红色
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        file = FileStorage(
            stream=img_io,
            filename='rgba.png',
            content_type='image/png'
        )
        
        result = self.service.upload_image(file=file, title='RGBA测试')
        
        # 验证转换成功
        with Image.open(result['image_path']) as converted_img:
            assert converted_img.mode == 'RGB'
        
        # 清理测试文件
        if os.path.exists(result['image_path']):
            os.remove(result['image_path'])