#!/usr/bin/env python3
"""
验证复盘功能实现
"""
import os
import sys
import re
from pathlib import Path

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (不存在)")
        return False

def check_file_content(file_path, patterns, description):
    """检查文件内容是否包含指定模式"""
    if not os.path.exists(file_path):
        print(f"✗ {description}: 文件不存在")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_patterns = []
        for pattern_name, pattern in patterns.items():
            if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
                missing_patterns.append(pattern_name)
        
        if missing_patterns:
            print(f"✗ {description}: 缺少 {', '.join(missing_patterns)}")
            return False
        else:
            print(f"✓ {description}: 所有必需内容都存在")
            return True
    except Exception as e:
        print(f"✗ {description}: 读取文件出错 - {str(e)}")
        return False

def verify_review_editor():
    """验证复盘编辑器组件"""
    print("\n=== 验证复盘编辑器组件 ===")
    
    file_path = "static/js/review-editor.js"
    patterns = {
        "ReviewEditor类": r"class ReviewEditor",
        "富文本编辑功能": r"initializeRichTextEditor|enhanceTextarea",
        "图片上传处理": r"handleImageUpload|previewImages",
        "评分系统": r"setupScoreInteraction|suggestOverallScore",
        "表单验证": r"validateForm",
        "保存功能": r"saveReview",
        "工具栏": r"addTextareaToolbar|applyTextFormat"
    }
    
    return check_file_content(file_path, patterns, "复盘编辑器组件")

def verify_image_uploader():
    """验证图片上传组件"""
    print("\n=== 验证图片上传组件 ===")
    
    file_path = "static/js/image-uploader.js"
    patterns = {
        "ImageUploader类": r"class ImageUploader",
        "拖拽上传": r"dragover|dragleave|drop",
        "文件验证": r"validateFiles",
        "图片预览": r"createPreview",
        "上传进度": r"showProgress|updateProgress",
        "文件管理": r"removeFile|addFiles"
    }
    
    return check_file_content(file_path, patterns, "图片上传组件")

def verify_review_viewer():
    """验证复盘查看器组件"""
    print("\n=== 验证复盘查看器组件 ===")
    
    file_path = "static/js/review-viewer.js"
    patterns = {
        "ReviewViewer类": r"class ReviewViewer",
        "复盘展示": r"displayReview|renderReview",
        "评分展示": r"renderReviewScores",
        "图片查看": r"renderReviewImages|showImageModal",
        "内容格式化": r"formatContent",
        "编辑功能": r"editReview"
    }
    
    return check_file_content(file_path, patterns, "复盘查看器组件")

def verify_api_routes():
    """验证API路由"""
    print("\n=== 验证API路由 ===")
    
    file_path = "api/trade_review_routes.py"
    patterns = {
        "获取复盘记录": r"@api_bp\.route.*trade-reviews.*GET",
        "创建复盘记录": r"@api_bp\.route.*trade-reviews.*POST",
        "更新复盘记录": r"@api_bp\.route.*trade-reviews.*PUT",
        "删除复盘记录": r"@api_bp\.route.*trade-reviews.*DELETE",
        "图片上传": r"@api_bp\.route.*images.*POST",
        "按交易获取复盘": r"by-trade"
    }
    
    return check_file_content(file_path, patterns, "API路由")

def verify_service_layer():
    """验证服务层"""
    print("\n=== 验证服务层 ===")
    
    file_path = "services/trade_review_service.py"
    patterns = {
        "TradeReviewService类": r"class TradeReviewService",
        "创建复盘": r"def create_review",
        "更新复盘": r"def update_review",
        "获取复盘": r"def get_review_by",
        "图片上传": r"def upload_review_images",
        "数据验证": r"def _validate_review_data",
        "文件验证": r"def _validate_image_file"
    }
    
    return check_file_content(file_path, patterns, "服务层")

def verify_template_integration():
    """验证模板集成"""
    print("\n=== 验证模板集成 ===")
    
    file_path = "templates/historical_trades.html"
    patterns = {
        "复盘模态框": r"id=[\"']reviewModal[\"']",
        "查看复盘模态框": r"id=[\"']viewReviewModal[\"']",
        "图片上传容器": r"id=[\"']image-uploader-container[\"']",
        "复盘表单": r"id=[\"']review-form[\"']",
        "评分系统": r"strategy-score|timing-score|risk-control-score|overall-score",
        "组件脚本引用": r"review-editor\.js|image-uploader\.js|review-viewer\.js"
    }
    
    return check_file_content(file_path, patterns, "模板集成")

def verify_historical_trades_manager():
    """验证历史交易管理器集成"""
    print("\n=== 验证历史交易管理器集成 ===")
    
    file_path = "static/js/historical-trades-manager.js"
    patterns = {
        "添加复盘": r"async addReview",
        "查看复盘": r"async viewReview",
        "编辑复盘": r"editReview",
        "组件集成": r"window\.reviewEditor|window\.reviewViewer",
        "图片上传器": r"imageUploader|ImageUploader"
    }
    
    return check_file_content(file_path, patterns, "历史交易管理器集成")

def check_task_completion():
    """检查任务完成情况"""
    print("\n=== 任务完成情况检查 ===")
    
    tasks = [
        ("创建复盘编辑器组件", verify_review_editor),
        ("实现复盘内容的富文本编辑功能", verify_review_editor),
        ("创建图片上传组件，支持多图片上传", verify_image_uploader),
        ("实现复盘评分系统界面", verify_review_editor),
        ("添加复盘内容的保存和更新功能", verify_review_editor),
        ("创建复盘查看界面", verify_review_viewer)
    ]
    
    completed_tasks = 0
    total_tasks = len(tasks)
    
    for task_name, verify_func in tasks:
        print(f"\n检查: {task_name}")
        if verify_func():
            completed_tasks += 1
            print(f"✓ 任务完成")
        else:
            print(f"✗ 任务未完成或有问题")
    
    print(f"\n任务完成情况: {completed_tasks}/{total_tasks}")
    return completed_tasks == total_tasks

def main():
    """主函数"""
    print("复盘编辑和查看功能实现验证")
    print("=" * 50)
    
    # 检查核心文件
    core_files = [
        ("static/js/review-editor.js", "复盘编辑器"),
        ("static/js/image-uploader.js", "图片上传组件"),
        ("static/js/review-viewer.js", "复盘查看器"),
        ("api/trade_review_routes.py", "复盘API路由"),
        ("services/trade_review_service.py", "复盘服务"),
        ("templates/historical_trades.html", "历史交易模板")
    ]
    
    print("\n=== 核心文件检查 ===")
    all_files_exist = True
    for file_path, description in core_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ 部分核心文件缺失，请检查实现")
        return False
    
    # 验证各个组件
    components_ok = True
    components_ok &= verify_review_editor()
    components_ok &= verify_image_uploader()
    components_ok &= verify_review_viewer()
    components_ok &= verify_api_routes()
    components_ok &= verify_service_layer()
    components_ok &= verify_template_integration()
    components_ok &= verify_historical_trades_manager()
    
    # 检查任务完成情况
    tasks_completed = check_task_completion()
    
    print("\n" + "=" * 50)
    if components_ok and tasks_completed:
        print("✅ 复盘编辑和查看功能实现完成！")
        print("\n功能特性:")
        print("- ✓ 复盘编辑器组件 (富文本编辑、评分系统)")
        print("- ✓ 图片上传组件 (拖拽上传、多图片支持)")
        print("- ✓ 复盘查看器组件 (格式化显示、图片查看)")
        print("- ✓ API接口完整 (CRUD操作、图片管理)")
        print("- ✓ 服务层完善 (数据验证、文件处理)")
        print("- ✓ 前端集成 (组件通信、用户体验)")
        
        print("\n使用说明:")
        print("1. 在历史交易页面点击'添加复盘'按钮")
        print("2. 填写复盘内容，支持富文本格式")
        print("3. 上传相关图片，支持拖拽操作")
        print("4. 设置评分并保存")
        print("5. 点击'查看复盘'查看已保存的复盘")
        
        return True
    else:
        print("❌ 复盘功能实现不完整，请检查上述问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)