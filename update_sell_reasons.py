#!/usr/bin/env python3
"""
更新卖出原因配置，添加"见顶信号"选项
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.configuration import Configuration

def update_sell_reasons():
    """更新卖出原因配置"""
    app = create_app()
    
    with app.app_context():
        try:
            # 获取当前的卖出原因
            current_reasons = Configuration.get_sell_reasons()
            print(f"当前卖出原因: {current_reasons}")
            
            # 添加"见顶信号"如果不存在
            new_reasons = ["部分止盈", "止损", "下等马/草泥马", "见顶信号", "不符合交易纪律"]
            
            # 更新配置
            Configuration.set_sell_reasons(new_reasons)
            
            # 验证更新
            updated_reasons = Configuration.get_sell_reasons()
            print(f"更新后卖出原因: {updated_reasons}")
            
            if "见顶信号" in updated_reasons:
                print("✓ 成功添加'见顶信号'到卖出原因选项")
            else:
                print("✗ 添加'见顶信号'失败")
                return False
                
            return True
            
        except Exception as e:
            print(f"✗ 更新卖出原因失败: {str(e)}")
            return False

if __name__ == "__main__":
    success = update_sell_reasons()
    if success:
        print("卖出原因配置更新成功！")
    else:
        print("卖出原因配置更新失败！")
        sys.exit(1)