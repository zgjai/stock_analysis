/**
 * 收益分布配置管理
 */
class ProfitDistributionConfig {
    constructor() {
        this.configs = [];
        this.analysisData = null;
        this.sortable = null;
        this.init();
    }

    async init() {
        await this.loadConfigs();
        await this.loadAnalysis();
        this.initSortable();
        this.bindEvents();
    }

    /**
     * 加载配置列表
     */
    async loadConfigs() {
        try {
            const response = await fetch('/api/profit-distribution/configs');
            const result = await response.json();
            
            if (result.success) {
                this.configs = result.data;
                this.renderConfigs();
            } else {
                this.showToast('加载配置失败: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('加载配置失败:', error);
            this.showToast('加载配置失败: ' + error.message, 'error');
        }
    }

    /**
     * 加载分析数据
     */
    async loadAnalysis() {
        try {
            const useTradePairs = document.getElementById('useTradePairs').checked;
            const response = await fetch(`/api/profit-distribution/analysis?use_trade_pairs=${useTradePairs}`);
            const result = await response.json();
            
            if (result.success) {
                this.analysisData = result.data;
                this.renderAnalysis();
                this.renderChart();
            } else {
                this.showToast('加载分析数据失败: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('加载分析数据失败:', error);
            this.showToast('加载分析数据失败: ' + error.message, 'error');
        }
    }

    /**
     * 渲染配置列表
     */
    renderConfigs() {
        const container = document.getElementById('configsList');
        
        if (this.configs.length === 0) {
            container.innerHTML = '<div class="text-center text-muted">暂无配置</div>';
            return;
        }

        container.innerHTML = this.configs.map(config => `
            <div class="config-item ${!config.is_active ? 'inactive' : ''}" data-id="${config.id}">
                <div class="d-flex align-items-center">
                    <div class="drag-handle me-3">
                        <i class="fas fa-grip-vertical"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="range-display">${config.range_name}</div>
                        <small class="text-muted">
                            ${this.formatRange(config.min_profit_rate, config.max_profit_rate)}
                        </small>
                    </div>
                    <div class="ms-3">
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="profitConfig.editConfig(${config.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="profitConfig.deleteConfig(${config.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * 渲染分析结果
     */
    renderAnalysis() {
        if (!this.analysisData) return;

        const summary = this.analysisData.summary || {};
        
        document.getElementById('totalTrades').textContent = this.analysisData.total_trades || 0;
        document.getElementById('totalProfit').textContent = this.formatCurrency(summary.total_profit || 0);
        document.getElementById('avgProfitRate').textContent = this.formatPercentage(summary.average_profit_rate || 0);
        document.getElementById('winRate').textContent = this.formatPercentage(summary.win_rate || 0);
    }

    /**
     * 渲染分布图表
     */
    renderChart() {
        if (!this.analysisData || !this.analysisData.distribution) return;

        const container = document.getElementById('distributionChart');
        const distribution = this.analysisData.distribution;
        const maxCount = Math.max(...distribution.map(d => d.count));

        container.innerHTML = distribution.map(item => {
            const percentage = maxCount > 0 ? (item.count / maxCount) * 100 : 0;
            return `
                <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span class="fw-bold">${item.range_name}</span>
                        <span class="text-muted">${item.count}笔 (${item.percentage.toFixed(1)}%)</span>
                    </div>
                    <div class="chart-bar" style="width: ${percentage}%">
                        <div class="chart-label">${item.range_name}</div>
                        <div class="chart-value">${item.count}</div>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * 初始化拖拽排序
     */
    initSortable() {
        const container = document.getElementById('configsList');
        this.sortable = Sortable.create(container, {
            handle: '.drag-handle',
            animation: 150,
            onEnd: (evt) => {
                this.updateSortOrder();
            }
        });
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 切换分析模式
        document.getElementById('useTradePairs').addEventListener('change', () => {
            this.loadAnalysis();
        });
    }

    /**
     * 更新排序顺序
     */
    async updateSortOrder() {
        try {
            const items = document.querySelectorAll('.config-item');
            const configs = Array.from(items).map((item, index) => ({
                id: parseInt(item.dataset.id),
                sort_order: index
            }));

            const response = await fetch('/api/profit-distribution/configs/batch-update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ configs })
            });

            const result = await response.json();
            if (result.success) {
                this.showToast('排序更新成功', 'success');
                await this.loadConfigs();
            } else {
                this.showToast('排序更新失败: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('更新排序失败:', error);
            this.showToast('更新排序失败: ' + error.message, 'error');
        }
    }

    /**
     * 显示添加配置模态框
     */
    showAddConfigModal() {
        document.getElementById('configModalTitle').textContent = '添加收益区间';
        document.getElementById('configForm').reset();
        document.getElementById('configId').value = '';
        document.getElementById('isActive').checked = true;
        
        const modal = new bootstrap.Modal(document.getElementById('configModal'));
        modal.show();
    }

    /**
     * 编辑配置
     */
    editConfig(configId) {
        const config = this.configs.find(c => c.id === configId);
        if (!config) return;

        document.getElementById('configModalTitle').textContent = '编辑收益区间';
        document.getElementById('configId').value = config.id;
        document.getElementById('rangeName').value = config.range_name;
        document.getElementById('minProfitRate').value = config.min_profit_rate ? (config.min_profit_rate * 100) : '';
        document.getElementById('maxProfitRate').value = config.max_profit_rate ? (config.max_profit_rate * 100) : '';
        document.getElementById('sortOrder').value = config.sort_order;
        document.getElementById('isActive').checked = config.is_active;

        const modal = new bootstrap.Modal(document.getElementById('configModal'));
        modal.show();
    }

    /**
     * 保存配置
     */
    async saveConfig() {
        try {
            const configId = document.getElementById('configId').value;
            const isEdit = !!configId;

            const data = {
                range_name: document.getElementById('rangeName').value,
                min_profit_rate: this.parsePercentage(document.getElementById('minProfitRate').value),
                max_profit_rate: this.parsePercentage(document.getElementById('maxProfitRate').value),
                sort_order: parseInt(document.getElementById('sortOrder').value) || 0,
                is_active: document.getElementById('isActive').checked
            };

            const url = isEdit 
                ? `/api/profit-distribution/configs/${configId}`
                : '/api/profit-distribution/configs';
            
            const method = isEdit ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                this.showToast(isEdit ? '配置更新成功' : '配置创建成功', 'success');
                bootstrap.Modal.getInstance(document.getElementById('configModal')).hide();
                await this.loadConfigs();
                await this.loadAnalysis();
            } else {
                this.showToast((isEdit ? '配置更新失败: ' : '配置创建失败: ') + result.message, 'error');
            }
        } catch (error) {
            console.error('保存配置失败:', error);
            this.showToast('保存配置失败: ' + error.message, 'error');
        }
    }

    /**
     * 删除配置
     */
    async deleteConfig(configId) {
        if (!confirm('确定要删除这个配置吗？')) return;

        try {
            const response = await fetch(`/api/profit-distribution/configs/${configId}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            if (result.success) {
                this.showToast('配置删除成功', 'success');
                await this.loadConfigs();
                await this.loadAnalysis();
            } else {
                this.showToast('配置删除失败: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('删除配置失败:', error);
            this.showToast('删除配置失败: ' + error.message, 'error');
        }
    }

    /**
     * 重置为默认配置
     */
    async resetToDefault() {
        if (!confirm('确定要重置为默认配置吗？这将删除所有自定义配置。')) return;

        try {
            const response = await fetch('/api/profit-distribution/configs/reset-default', {
                method: 'POST'
            });

            const result = await response.json();
            if (result.success) {
                this.showToast('已重置为默认配置', 'success');
                await this.loadConfigs();
                await this.loadAnalysis();
            } else {
                this.showToast('重置失败: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('重置失败:', error);
            this.showToast('重置失败: ' + error.message, 'error');
        }
    }

    /**
     * 刷新分析
     */
    async refreshAnalysis() {
        await this.loadAnalysis();
        this.showToast('分析数据已刷新', 'success');
    }

    /**
     * 格式化收益率区间
     */
    formatRange(minRate, maxRate) {
        const min = minRate !== null ? this.formatPercentage(minRate) : '无下限';
        const max = maxRate !== null ? this.formatPercentage(maxRate) : '无上限';
        return `${min} ~ ${max}`;
    }

    /**
     * 格式化百分比
     */
    formatPercentage(value) {
        if (value === null || value === undefined) return '-';
        return (value * 100).toFixed(2) + '%';
    }

    /**
     * 格式化货币
     */
    formatCurrency(value) {
        if (value === null || value === undefined) return '-';
        return '¥' + value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    /**
     * 解析百分比输入
     */
    parsePercentage(value) {
        if (!value || value === '') return null;
        return parseFloat(value) / 100;
    }

    /**
     * 显示Toast通知
     */
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastBody = document.getElementById('toastBody');
        
        toastBody.textContent = message;
        
        // 设置样式
        toast.className = `toast ${type === 'error' ? 'bg-danger text-white' : type === 'success' ? 'bg-success text-white' : 'bg-info text-white'}`;
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
}

// 全局变量和函数
let profitConfig;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    profitConfig = new ProfitDistributionConfig();
});

// 全局函数供HTML调用
function showAddConfigModal() {
    profitConfig.showAddConfigModal();
}

function saveConfig() {
    profitConfig.saveConfig();
}

function resetToDefault() {
    profitConfig.resetToDefault();
}

function refreshAnalysis() {
    profitConfig.refreshAnalysis();
}