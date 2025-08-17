#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据备份管理工具
Data Backup Management Tool
"""

import sys
import argparse
from datetime import datetime
from services.backup_service import BackupService

def create_backup(args):
    """创建备份"""
    backup_service = BackupService()
    
    backup_name = args.name
    if backup_name is None and args.auto:
        backup_name = f'auto_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    print("正在创建备份...")
    result = backup_service.create_backup(backup_name)
    
    if result['success']:
        print(f"✓ 备份创建成功!")
        print(f"  备份文件: {result['backup_name']}")
        print(f"  文件大小: {result['size'] / (1024*1024):.2f} MB")
        print(f"  保存路径: {result['backup_path']}")
    else:
        print(f"✗ 备份创建失败: {result['error']}")
        sys.exit(1)

def restore_backup(args):
    """恢复备份"""
    backup_service = BackupService()
    
    if not args.confirm:
        print("警告: 恢复备份将覆盖当前数据!")
        print("请使用 --confirm 参数确认此操作")
        sys.exit(1)
    
    print(f"正在恢复备份: {args.file}")
    result = backup_service.restore_backup(args.file)
    
    if result['success']:
        print("✓ 备份恢复成功!")
        print(f"  {result['message']}")
        if 'uploads_restored' in result:
            print(f"  恢复文件数: {result['uploads_restored']}")
    else:
        print(f"✗ 备份恢复失败: {result['error']}")
        sys.exit(1)

def list_backups(args):
    """列出备份"""
    backup_service = BackupService()
    
    result = backup_service.list_backups()
    
    if result['success']:
        backups = result['backups']
        if not backups:
            print("没有找到备份文件")
            return
        
        print(f"找到 {result['total_count']} 个备份文件 (总大小: {result['total_size_mb']:.2f} MB)")
        print("-" * 80)
        print(f"{'文件名':<40} {'大小(MB)':<10} {'创建时间':<20}")
        print("-" * 80)
        
        for backup in backups:
            print(f"{backup['filename']:<40} {backup['size_mb']:<10.2f} {backup['created_at'][:19]}")
            
            if args.verbose and 'backup_name' in backup:
                print(f"  备份名称: {backup['backup_name']}")
                print(f"  数据库大小: {backup.get('database_size', 0) / 1024:.1f} KB")
                print(f"  上传文件数: {backup.get('uploads_count', 0)}")
                print()
    else:
        print(f"✗ 列出备份失败: {result['error']}")
        sys.exit(1)

def delete_backup(args):
    """删除备份"""
    backup_service = BackupService()
    
    if not args.confirm:
        print("请使用 --confirm 参数确认删除操作")
        sys.exit(1)
    
    result = backup_service.delete_backup(args.file)
    
    if result['success']:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ 删除失败: {result['error']}")
        sys.exit(1)

def cleanup_backups(args):
    """清理过期备份"""
    backup_service = BackupService()
    
    if not args.confirm:
        print(f"将删除 {args.days} 天前的备份文件")
        print("请使用 --confirm 参数确认此操作")
        sys.exit(1)
    
    result = backup_service.cleanup_old_backups(args.days)
    
    if result['success']:
        print(f"✓ 清理完成!")
        print(f"  删除文件数: {result['deleted_count']}")
        print(f"  释放空间: {result['deleted_size_mb']:.2f} MB")
        print(f"  保留天数: {result['retention_days']} 天")
    else:
        print(f"✗ 清理失败: {result['error']}")
        sys.exit(1)

def verify_backup(args):
    """验证备份"""
    backup_service = BackupService()
    
    result = backup_service.verify_backup(args.file)
    
    if result['success']:
        verification = result['verification']
        print(f"备份文件验证: {verification['filename']}")
        print("-" * 50)
        
        if verification['is_valid']:
            print("✓ 备份文件有效")
        else:
            print("✗ 备份文件无效")
        
        print(f"包含数据库: {'是' if verification['has_database'] else '否'}")
        print(f"包含元数据: {'是' if verification['has_metadata'] else '否'}")
        print(f"上传文件数: {verification['uploads_count']}")
        
        if 'database_tables' in verification:
            print(f"数据库表数: {verification['database_tables']}")
        
        if verification['errors']:
            print("\n发现的问题:")
            for error in verification['errors']:
                print(f"  - {error}")
        
        if 'metadata' in verification:
            metadata = verification['metadata']
            print(f"\n备份信息:")
            print(f"  备份名称: {metadata.get('backup_name', 'N/A')}")
            print(f"  创建时间: {metadata.get('created_at', 'N/A')}")
            print(f"  版本: {metadata.get('version', 'N/A')}")
    else:
        print(f"✗ 验证失败: {result['error']}")
        sys.exit(1)

def auto_backup_check(args):
    """检查自动备份"""
    backup_service = BackupService()
    
    result = backup_service.auto_backup_check()
    
    if result['success']:
        print("自动备份检查结果:")
        print(f"  需要备份: {'是' if result['needs_backup'] else '否'}")
        print(f"  原因: {result['reason']}")
        
        if result['latest_backup']:
            print(f"  最新备份: {result['latest_backup']}")
            print(f"  备份时间: {result['latest_backup_time'][:19]}")
        
        if result['needs_backup'] and args.auto_create:
            print("\n正在创建自动备份...")
            create_result = backup_service.create_backup()
            if create_result['success']:
                print(f"✓ 自动备份创建成功: {create_result['backup_name']}")
            else:
                print(f"✗ 自动备份创建失败: {create_result['error']}")
    else:
        print(f"✗ 检查失败: {result['error']}")
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='股票交易记录系统备份管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建备份
    create_parser = subparsers.add_parser('create', help='创建备份')
    create_parser.add_argument('--name', help='备份名称')
    create_parser.add_argument('--auto', action='store_true', help='自动生成备份名称')
    create_parser.set_defaults(func=create_backup)
    
    # 恢复备份
    restore_parser = subparsers.add_parser('restore', help='恢复备份')
    restore_parser.add_argument('file', help='备份文件名')
    restore_parser.add_argument('--confirm', action='store_true', help='确认恢复操作')
    restore_parser.set_defaults(func=restore_backup)
    
    # 列出备份
    list_parser = subparsers.add_parser('list', help='列出备份文件')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    list_parser.set_defaults(func=list_backups)
    
    # 删除备份
    delete_parser = subparsers.add_parser('delete', help='删除备份文件')
    delete_parser.add_argument('file', help='备份文件名')
    delete_parser.add_argument('--confirm', action='store_true', help='确认删除操作')
    delete_parser.set_defaults(func=delete_backup)
    
    # 清理过期备份
    cleanup_parser = subparsers.add_parser('cleanup', help='清理过期备份')
    cleanup_parser.add_argument('--days', type=int, default=30, help='保留天数 (默认30天)')
    cleanup_parser.add_argument('--confirm', action='store_true', help='确认清理操作')
    cleanup_parser.set_defaults(func=cleanup_backups)
    
    # 验证备份
    verify_parser = subparsers.add_parser('verify', help='验证备份文件')
    verify_parser.add_argument('file', help='备份文件名')
    verify_parser.set_defaults(func=verify_backup)
    
    # 自动备份检查
    auto_parser = subparsers.add_parser('auto-check', help='检查是否需要自动备份')
    auto_parser.add_argument('--auto-create', action='store_true', help='如果需要则自动创建备份')
    auto_parser.set_defaults(func=auto_backup_check)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 操作失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()