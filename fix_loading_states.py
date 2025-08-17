#!/usr/bin/env python3
"""
修复加载状态问题的脚本
解决没有数据时一直显示加载中的问题
"""

import os
import re

def fix_trading_records_loading():
    """修复交易记录页面的加载状态问题"""
    
    template_path = "templates/trading_records.html"
    
    if not os.path.exists(template_path):
        print(f"文件不存在: {template_path}")
        return False
    
    # 读取原文件
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: 确保初始化时立即隐藏加载状态
    init_fix = '''// 立即隐藏加载状态，防止卡住
(function() {
    const loadingModal = document.getElementById('loadingModal');
    if (loadingModal) {
        loadingModal.classList.remove('show');
        loadingModal.style.display = 'none';
        document.body.classList.remove('modal-open');
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) backdrop.remove();
    }
    
    // 立即显示空状态，避免一直显示加载中
    const tbody = document.getElementById('trades-table-body');
    if (tbody && tbody.innerHTML.includes('加载中')) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                    正在加载数据...
                </td>
            </tr>
        `;
    }
})();'''
    
    # 查找并替换现有的初始化代码
    pattern = r'// 立即隐藏加载状态，防止卡住\s*\(function\(\) \{[^}]+\}\)\(\);'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, init_fix, content, flags=re.DOTALL)
    else:
        # 如果没有找到，在script标签开始处添加
        script_start = content.find('<script>')
        if script_start != -1:
            insert_pos = script_start + len('<script>')
            content = content[:insert_pos] + '\n' + init_fix + '\n' + content[insert_pos:]
    
    # 修复2: 改进loadTrades方法的错误处理
    load_trades_fix = '''    async loadTrades() {
        const tbody = document.getElementById('trades-table-body');
        
        try {
            // 显示加载状态
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-4">
                        <div class="spinner-border spinner-border-sm me-2" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        正在加载交易记录...
                    </td>
                </tr>
            `;
            
            const params = {
                page: this.currentPage,
                per_page: this.perPage,
                sort_by: document.getElementById('sort-by').value,
                sort_order: document.getElementById('sort-order').value,
                ...this.currentFilters
            };
            
            // 设置5秒超时
            const timeout = 5000;
            const response = await Promise.race([
                apiClient.getTrades(params),
                new Promise((_, reject) => setTimeout(() => reject(new Error('请求超时')), timeout))
            ]);
            
            if (response && response.success) {
                this.renderTradesTable(response.data.trades || []);
                this.renderPagination({
                    total: response.data.total || 0,
                    pages: response.data.pages || 1,
                    current_page: response.data.current_page || 1,
                    per_page: response.data.per_page || 20,
                    has_next: response.data.has_next || false,
                    has_prev: response.data.has_prev || false
                });
            } else {
                throw new Error(response?.message || '获取交易记录失败');
            }
        } catch (error) {
            console.error('Failed to load trades:', error);
            
            // 显示错误状态
            let errorMessage = '加载失败，请重试';
            if (error.message === '请求超时') {
                errorMessage = '加载超时，请检查网络连接或稍后重试';
            } else if (error.message.includes('网络')) {
                errorMessage = '网络连接失败，请检查网络设置';
            }
            
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-4">
                        <i class="bi bi-exclamation-triangle fs-1 d-block mb-2 text-warning"></i>
                        <div class="mb-2">${errorMessage}</div>
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="tradingManager.loadTrades()">
                            <i class="bi bi-arrow-clockwise"></i> 重新加载
                        </button>
                    </td>
                </tr>
            `;
            
            // 重置分页
            this.renderPagination({ pages: 0, current_page: 1 });
            
            // 显示用户友好的错误消息
            if (error.message === '请求超时') {
                showMessage('加载超时，可能是系统刚启动或网络较慢，请稍后重试', 'warning');
            } else {
                showMessage('加载交易记录失败，请重试', 'error');
            }
        }
    }'''
    
    # 替换loadTrades方法
    pattern = r'async loadTrades\(\) \{[^}]+\}(?:\s*\})*'
    content = re.sub(pattern, load_trades_fix, content, flags=re.DOTALL)
    
    # 修复3: 改进renderTradesTable方法
    render_table_fix = '''    renderTradesTable(trades) {
        const tbody = document.getElementById('trades-table-body');
        
        if (!trades || trades.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-4">
                        <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                        <div class="mb-2">暂无交易记录</div>
                        <button type="button" class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#addTradeModal">
                            <i class="bi bi-plus-circle"></i> 添加第一条记录
                        </button>
                    </td>
                </tr>
            `;
            return;
        }
        
        try {
            tbody.innerHTML = trades.map(trade => `
                <tr ${trade.is_corrected ? 'class="table-warning"' : ''}>
                    <td>${formatDate(trade.trade_date)}</td>
                    <td>
                        <div class="fw-bold">${trade.stock_code}</div>
                        <small class="text-muted">${trade.stock_name}</small>
                    </td>
                    <td>
                        <span class="badge ${trade.trade_type === 'buy' ? 'bg-success' : 'bg-danger'}">
                            ${trade.trade_type === 'buy' ? '买入' : '卖出'}
                        </span>
                    </td>
                    <td class="fw-bold">¥${trade.price.toFixed(2)}</td>
                    <td>${trade.quantity.toLocaleString()}</td>
                    <td class="fw-bold">¥${(trade.price * trade.quantity).toLocaleString()}</td>
                    <td>
                        <span class="badge bg-secondary">${trade.reason}</span>
                    </td>
                    <td>
                        ${trade.is_corrected ? 
                            '<span class="badge bg-warning">已订正</span>' : 
                            '<span class="badge bg-success">正常</span>'
                        }
                        ${trade.original_record_id ? 
                            '<br><small class="text-muted">订正记录</small>' : ''
                        }
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm" role="group">
                            <button type="button" class="btn btn-outline-primary" 
                                    onclick="tradingManager.editTrade(${trade.id})" title="编辑">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button type="button" class="btn btn-outline-warning" 
                                    onclick="tradingManager.correctTrade(${trade.id})" title="订正">
                                <i class="bi bi-arrow-clockwise"></i>
                            </button>
                            <button type="button" class="btn btn-outline-info" 
                                    onclick="tradingManager.viewCorrectionHistory(${trade.id})" title="历史">
                                <i class="bi bi-clock-history"></i>
                            </button>
                            <button type="button" class="btn btn-outline-danger" 
                                    onclick="tradingManager.deleteTrade(${trade.id})" title="删除">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error rendering trades table:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-4">
                        <i class="bi bi-exclamation-triangle fs-1 d-block mb-2 text-danger"></i>
                        数据渲染失败，请刷新页面重试
                    </td>
                </tr>
            `;
        }
    }'''
    
    # 替换renderTradesTable方法
    pattern = r'renderTradesTable\(trades\) \{[^}]+\}(?:\s*\})*'
    content = re.sub(pattern, render_table_fix, content, flags=re.DOTALL)
    
    # 修复4: 添加页面加载完成后的初始化检查
    page_ready_fix = '''
// 页面加载完成后的额外检查
document.addEventListener('DOMContentLoaded', function() {
    // 延迟检查，确保所有脚本都已加载
    setTimeout(() => {
        const tbody = document.getElementById('trades-table-body');
        if (tbody && tbody.innerHTML.includes('加载中')) {
            console.log('检测到页面仍在加载状态，尝试修复...');
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-4">
                        <i class="bi bi-exclamation-triangle fs-1 d-block mb-2 text-warning"></i>
                        <div class="mb-2">页面加载异常</div>
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                            <i class="bi bi-arrow-clockwise"></i> 刷新页面
                        </button>
                    </td>
                </tr>
            `;
        }
    }, 3000);
});'''
    
    # 在script标签结束前添加页面就绪检查
    script_end = content.rfind('</script>')
    if script_end != -1:
        content = content[:script_end] + page_ready_fix + '\n' + content[script_end:]
    
    # 写入修复后的文件
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 交易记录页面加载状态修复完成")
    return True

def fix_other_pages_loading():
    """修复其他页面的类似问题"""
    
    pages_to_fix = [
        "templates/dashboard.html",
        "templates/stock_pool.html", 
        "templates/case_analysis.html"
    ]
    
    for page_path in pages_to_fix:
        if not os.path.exists(page_path):
            continue
            
        try:
            with open(page_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找并修复加载状态
            if '加载中...' in content and 'spinner-border' in content:
                # 添加超时处理
                timeout_fix = '''
// 防止加载状态卡住
setTimeout(() => {
    const loadingElements = document.querySelectorAll('.spinner-border');
    loadingElements.forEach(el => {
        const parent = el.closest('tr, .card-body, .loading-container');
        if (parent && parent.innerHTML.includes('加载中')) {
            console.log('检测到长时间加载，尝试修复...');
            if (parent.tagName === 'TR') {
                parent.innerHTML = `
                    <td colspan="9" class="text-center text-muted py-4">
                        <i class="bi bi-exclamation-triangle fs-1 d-block mb-2 text-warning"></i>
                        <div class="mb-2">加载超时</div>
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                            <i class="bi bi-arrow-clockwise"></i> 刷新页面
                        </button>
                    </td>
                `;
            }
        }
    });
}, 10000); // 10秒超时'''
                
                # 在script标签中添加超时处理
                script_start = content.find('<script>')
                if script_start != -1:
                    insert_pos = script_start + len('<script>')
                    content = content[:insert_pos] + timeout_fix + content[insert_pos:]
                    
                    with open(page_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ 修复了 {page_path} 的加载状态")
        
        except Exception as e:
            print(f"❌ 修复 {page_path} 时出错: {e}")

def main():
    """主函数"""
    print("🔧 开始修复加载状态问题...")
    
    # 修复交易记录页面
    if fix_trading_records_loading():
        print("✅ 交易记录页面修复成功")
    else:
        print("❌ 交易记录页面修复失败")
    
    # 修复其他页面
    fix_other_pages_loading()
    
    print("\n🎉 加载状态修复完成！")
    print("\n修复内容:")
    print("1. 添加了页面初始化时的加载状态检查")
    print("2. 改进了API请求的错误处理和超时机制")
    print("3. 优化了空数据状态的显示")
    print("4. 添加了重新加载按钮")
    print("5. 增加了页面加载异常的自动检测和修复")
    
    print("\n请刷新浏览器页面查看效果。")

if __name__ == "__main__":
    main()