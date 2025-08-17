#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git数据同步脚本
Git Data Synchronization Script
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

class GitSyncManager:
    """Git同步管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_files = [
            'data/',
            'uploads/',
            'backups/'  # 可选，根据需要决定是否同步备份
        ]
    
    def run_command(self, command, description, capture_output=True):
        """执行命令并处理错误"""
        try:
            print(f"🔄 {description}...")
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                print(f"❌ {description} 失败:")
                if result.stderr:
                    print(result.stderr)
                return False, result.stderr
            else:
                print(f"✅ {description} 成功")
                if result.stdout and result.stdout.strip():
                    print(result.stdout.strip())
                return True, result.stdout
                
        except Exception as e:
            print(f"❌ {description} 出错: {str(e)}")
            return False, str(e)
    
    def check_git_repo(self):
        """检查是否为Git仓库"""
        if not (self.project_root / '.git').exists():
            print("❌ 当前目录不是Git仓库")
            print("请先运行: git init")
            return False
        return True
    
    def check_remote(self):
        """检查远程仓库配置"""
        success, output = self.run_command("git remote -v", "检查远程仓库")
        if not success or not output.strip():
            print("⚠️  未配置远程仓库")
            print("请先添加远程仓库: git remote add origin <repository-url>")
            return False
        return True
    
    def get_git_status(self):
        """获取Git状态"""
        success, output = self.run_command("git status --porcelain", "检查Git状态")
        if not success:
            return None
        return output.strip()
    
    def has_uncommitted_changes(self):
        """检查是否有未提交的更改"""
        status = self.get_git_status()
        return status is not None and len(status) > 0
    
    def pull_changes(self):
        """拉取远程更改"""
        success, output = self.run_command("git pull origin main", "拉取远程更改")
        
        if not success:
            # 检查是否是因为没有上游分支
            if "no tracking information" in output.lower():
                print("⚠️  没有设置上游分支，尝试设置...")
                success, _ = self.run_command(
                    "git push --set-upstream origin main", 
                    "设置上游分支"
                )
                if success:
                    return self.pull_changes()  # 重试拉取
            return False
        
        return True
    
    def add_data_files(self):
        """添加数据文件到Git"""
        files_added = []
        
        for file_pattern in self.data_files:
            file_path = self.project_root / file_pattern
            if file_path.exists():
                success, _ = self.run_command(f"git add {file_pattern}", f"添加 {file_pattern}")
                if success:
                    files_added.append(file_pattern)
        
        if not files_added:
            print("📝 没有数据文件需要添加")
            return True
        
        print(f"📁 已添加文件: {', '.join(files_added)}")
        return True
    
    def commit_changes(self, message=None):
        """提交更改"""
        # 检查是否有暂存的更改
        success, output = self.run_command("git diff --cached --quiet", "检查暂存更改")
        if success:  # 没有暂存的更改
            print("📝 没有新的更改需要提交")
            return True
        
        if message is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Auto sync: {timestamp}"
        
        success, _ = self.run_command(f'git commit -m "{message}"', "提交更改")
        return success
    
    def push_changes(self):
        """推送更改到远程仓库"""
        success, output = self.run_command("git push origin main", "推送到远程仓库")
        
        if not success:
            # 检查是否需要先设置上游分支
            if "no upstream branch" in output.lower():
                print("⚠️  设置上游分支...")
                success, _ = self.run_command(
                    "git push --set-upstream origin main", 
                    "设置上游分支并推送"
                )
        
        return success
    
    def create_backup_before_sync(self):
        """同步前创建备份"""
        try:
            from services.backup_service import BackupService
            backup_service = BackupService()
            
            print("💾 创建同步前备份...")
            result = backup_service.create_backup(f'pre_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            
            if result['success']:
                print(f"✅ 备份创建成功: {result['backup_name']}")
                return True
            else:
                print(f"⚠️  备份创建失败: {result['error']}")
                return False
                
        except ImportError:
            print("⚠️  备份服务不可用，跳过备份步骤")
            return True
        except Exception as e:
            print(f"⚠️  备份创建出错: {str(e)}")
            return False
    
    def sync(self, message=None, create_backup=True):
        """执行完整的同步流程"""
        print("🔄 开始Git数据同步...")
        print("=" * 50)
        
        # 检查Git仓库
        if not self.check_git_repo():
            return False
        
        # 检查远程仓库
        if not self.check_remote():
            return False
        
        # 创建备份（可选）
        if create_backup:
            if not self.create_backup_before_sync():
                response = input("备份失败，是否继续同步？(y/N): ")
                if response.lower() != 'y':
                    print("❌ 同步已取消")
                    return False
        
        # 拉取远程更改
        if not self.pull_changes():
            print("❌ 拉取远程更改失败，请检查网络连接和仓库配置")
            return False
        
        # 添加数据文件
        if not self.add_data_files():
            print("❌ 添加数据文件失败")
            return False
        
        # 提交更改
        if not self.commit_changes(message):
            print("❌ 提交更改失败")
            return False
        
        # 推送到远程
        if not self.push_changes():
            print("❌ 推送到远程仓库失败")
            return False
        
        print("=" * 50)
        print("🎉 数据同步完成!")
        
        # 显示最近的提交
        self.run_command("git log --oneline -3", "最近的提交记录")
        
        return True
    
    def status(self):
        """显示Git状态信息"""
        print("📊 Git仓库状态")
        print("=" * 30)
        
        # 检查仓库
        if not self.check_git_repo():
            return
        
        # 显示分支信息
        self.run_command("git branch -v", "当前分支")
        
        # 显示远程仓库
        self.run_command("git remote -v", "远程仓库")
        
        # 显示状态
        self.run_command("git status", "工作区状态", capture_output=False)
        
        # 显示最近提交
        self.run_command("git log --oneline -5", "最近提交")
    
    def init_repo(self, remote_url=None):
        """初始化Git仓库"""
        print("🚀 初始化Git仓库...")
        
        # 初始化仓库
        if not self.run_command("git init", "初始化Git仓库")[0]:
            return False
        
        # 添加所有文件
        if not self.run_command("git add .", "添加所有文件")[0]:
            return False
        
        # 初始提交
        if not self.run_command('git commit -m "Initial commit: Stock Trading Journal System"', "初始提交")[0]:
            return False
        
        # 添加远程仓库
        if remote_url:
            if not self.run_command(f"git remote add origin {remote_url}", "添加远程仓库")[0]:
                return False
            
            # 推送到远程
            if not self.run_command("git push -u origin main", "推送到远程仓库")[0]:
                return False
        
        print("✅ Git仓库初始化完成!")
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Git数据同步工具')
    parser.add_argument('command', nargs='?', default='sync', 
                       choices=['sync', 'status', 'init'],
                       help='执行的命令 (默认: sync)')
    parser.add_argument('-m', '--message', help='提交信息')
    parser.add_argument('--no-backup', action='store_true', help='跳过备份步骤')
    parser.add_argument('--remote', help='远程仓库URL (仅用于init命令)')
    
    args = parser.parse_args()
    
    sync_manager = GitSyncManager()
    
    try:
        if args.command == 'sync':
            success = sync_manager.sync(
                message=args.message, 
                create_backup=not args.no_backup
            )
            sys.exit(0 if success else 1)
            
        elif args.command == 'status':
            sync_manager.status()
            
        elif args.command == 'init':
            success = sync_manager.init_repo(args.remote)
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 操作失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()