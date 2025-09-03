/**
 * 非交易日配置页面JavaScript
 */

class NonTradingDaysManager {
    constructor() {
        this.currentYear = new Date().getFullYear();
        this.holidays = [];
        this.init();
    }

    init() {
        this.initEventListeners();
        this.initYearSelectors();
        this.loadHolidays();
    }

    initEventListeners() {
        // 检查交易日
        document.getElementById('checkTradingDayBtn').addEventListener('click', () => {
            this.checkTradingDay();
        });

        // 计算持仓天数
        document.getElementById('calculateHoldingDaysBtn').addEventListener('click', () => {
            this.calculateHoldingDays();
        });

        // 获取统计信息
        document.getElementById('getStatsBtn').addEventListener('click', () => {
            this.getStatistics();
        });

        // 保存节假日
        document.getElementById('saveHolidayBtn').addEventListener('click', () => {
            this.saveHoliday();
        });

        // 更新节假日
        document.getElementById('updateHolidayBtn').addEventListener('click', () => {
            this.updateHoliday();
        });

        // 刷新列表
        document.getElementById('refreshListBtn').addEventListener('click', () => {
            this.loadHolidays();
        });

        // 年份筛选
        document.getElementById('yearFilter').addEventListener('change', (e) => {
            this.filterByYear(e.target.value);
        });

        // 查看交易日历
        document.getElementById('viewCalendarBtn').addEventListener('click', () => {
            this.showCalendar();
        });

        // 批量导入
        document.getElementById('bulkImportBtn').addEventListener('click', () => {
            this.bulkImport();
        });

        // 日历年份选择
        document.getElementById('calendarYear').addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadCalendar(parseInt(e.target.value));
            }
        });
    }

    initYearSelectors() {
        const currentYear = new Date().getFullYear();
        const years = [];
        
        // 生成年份选项（当前年份前后5年）
        for (let year = currentYear - 5; year <= currentYear + 5; year++) {
            years.push(year);
        }

        // 填充年份选择器
        const selectors = ['statsYear', 'yearFilter', 'calendarYear'];
        selectors.forEach(selectorId => {
            const selector = document.getElementById(selectorId);
            years.forEach(year => {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year + '年';
                if (year === currentYear && selectorId !== 'yearFilter') {
                    option.selected = true;
                }
                selector.appendChild(option);
            });
        });

        // 设置默认日期
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('checkDate').value = today;
        document.getElementById('buyDate').value = today;
    }

    async checkTradingDay() {
        const date = document.getElementById('checkDate').value;
        if (!date) {
            this.showMessage('请选择日期', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/trading-days/check/${date}`);
            const result = await response.json();

            const resultDiv = document.getElementById('checkResult');
            if (result.success) {
                const isTrading = result.data.is_trading_day;
                resultDiv.innerHTML = `
                    <div class="alert alert-${isTrading ? 'success' : 'info'} mb-0">
                        <i class="bi bi-${isTrading ? 'check-circle' : 'x-circle'}"></i>
                        ${result.message}
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger mb-0">
                        <i class="bi bi-exclamation-triangle"></i>
                        ${result.message}
                    </div>
                `;
            }
        } catch (error) {
            console.error('检查交易日失败:', error);
            this.showMessage('检查交易日失败', 'error');
        }
    }

    async calculateHoldingDays() {
        const buyDate = document.getElementById('buyDate').value;
        const sellDate = document.getElementById('sellDate').value;

        if (!buyDate) {
            this.showMessage('请选择买入日期', 'warning');
            return;
        }

        try {
            let url = `/api/trading-days/holding-days?buy_date=${buyDate}`;
            if (sellDate) {
                url += `&sell_date=${sellDate}`;
            }

            const response = await fetch(url);
            const result = await response.json();

            const resultDiv = document.getElementById('holdingResult');
            if (result.success) {
                resultDiv.innerHTML = `
                    <div class="alert alert-success mb-0">
                        <i class="bi bi-calendar-check"></i>
                        <strong>${result.data.holding_days}</strong> 个交易日
                        <br><small class="text-muted">${result.message}</small>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger mb-0">
                        <i class="bi bi-exclamation-triangle"></i>
                        ${result.message}
                    </div>
                `;
            }
        } catch (error) {
            console.error('计算持仓天数失败:', error);
            this.showMessage('计算持仓天数失败', 'error');
        }
    }

    async getStatistics() {
        const year = document.getElementById('statsYear').value;
        if (!year) {
            this.showMessage('请选择年份', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/trading-calendar/${year}`);
            const result = await response.json();

            const resultDiv = document.getElementById('statsResult');
            if (result.success) {
                const data = result.data;
                resultDiv.innerHTML = `
                    <div class="alert alert-info mb-0">
                        <h6><i class="bi bi-bar-chart"></i> ${year}年统计</h6>
                        <p class="mb-1"><strong>总交易日:</strong> ${data.total_trading_days} 天</p>
                        <p class="mb-1"><strong>非交易日:</strong> ${data.total_non_trading_days} 天</p>
                        <small class="text-muted">点击"查看交易日历"查看详细信息</small>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger mb-0">
                        <i class="bi bi-exclamation-triangle"></i>
                        ${result.message}
                    </div>
                `;
            }
        } catch (error) {
            console.error('获取统计信息失败:', error);
            this.showMessage('获取统计信息失败', 'error');
        }
    }

    async loadHolidays() {
        try {
            const response = await fetch('/api/non-trading-days');
            const result = await response.json();

            if (result.success) {
                this.holidays = result.data;
                this.renderHolidaysTable();
                this.updateYearFilter();
            } else {
                this.showMessage('加载节假日列表失败', 'error');
            }
        } catch (error) {
            console.error('加载节假日列表失败:', error);
            this.showMessage('加载节假日列表失败', 'error');
        }
    }

    renderHolidaysTable(filteredHolidays = null) {
        const holidays = filteredHolidays || this.holidays;
        const tbody = document.getElementById('holidaysTableBody');
        const noDataMessage = document.getElementById('noDataMessage');

        if (holidays.length === 0) {
            tbody.innerHTML = '';
            noDataMessage.style.display = 'block';
            return;
        }

        noDataMessage.style.display = 'none';
        
        tbody.innerHTML = holidays.map(holiday => {
            const date = new Date(holiday.date);
            const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
            const weekday = weekdays[date.getDay()];
            
            return `
                <tr>
                    <td>${holiday.date}</td>
                    <td>${holiday.name}</td>
                    <td>
                        <span class="badge bg-secondary">${holiday.type === 'holiday' ? '节假日' : '其他'}</span>
                    </td>
                    <td>${holiday.description || '-'}</td>
                    <td>星期${weekday}</td>
                    <td>
                        <button type="button" class="btn btn-sm btn-outline-primary me-1" 
                                onclick="nonTradingDaysManager.editHoliday(${holiday.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="nonTradingDaysManager.deleteHoliday(${holiday.id}, '${holiday.date}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    updateYearFilter() {
        const years = [...new Set(this.holidays.map(h => new Date(h.date).getFullYear()))].sort((a, b) => b - a);
        const yearFilter = document.getElementById('yearFilter');
        
        // 清除现有选项（保留"所有年份"）
        while (yearFilter.children.length > 1) {
            yearFilter.removeChild(yearFilter.lastChild);
        }
        
        // 添加年份选项
        years.forEach(year => {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year + '年';
            yearFilter.appendChild(option);
        });
    }

    filterByYear(year) {
        if (!year) {
            this.renderHolidaysTable();
            return;
        }

        const filteredHolidays = this.holidays.filter(holiday => {
            return new Date(holiday.date).getFullYear() == year;
        });
        
        this.renderHolidaysTable(filteredHolidays);
    }

    async saveHoliday() {
        const form = document.getElementById('addHolidayForm');
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        const data = {
            date: document.getElementById('holidayDate').value,
            name: document.getElementById('holidayName').value,
            description: document.getElementById('holidayDescription').value
        };

        try {
            const response = await fetch('/api/non-trading-days', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.showMessage('节假日添加成功', 'success');
                this.closeModal('addHolidayModal');
                this.resetForm('addHolidayForm');
                this.loadHolidays();
            } else {
                this.showMessage(result.message, 'error');
            }
        } catch (error) {
            console.error('添加节假日失败:', error);
            this.showMessage('添加节假日失败', 'error');
        }
    }

    async editHoliday(id) {
        const holiday = this.holidays.find(h => h.id === id);
        if (!holiday) return;

        document.getElementById('editHolidayId').value = holiday.id;
        document.getElementById('editHolidayDate').value = holiday.date;
        document.getElementById('editHolidayName').value = holiday.name;
        document.getElementById('editHolidayDescription').value = holiday.description || '';

        const modal = new bootstrap.Modal(document.getElementById('editHolidayModal'));
        modal.show();
    }

    async updateHoliday() {
        const form = document.getElementById('editHolidayForm');
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        const id = document.getElementById('editHolidayId').value;
        const data = {
            name: document.getElementById('editHolidayName').value,
            description: document.getElementById('editHolidayDescription').value
        };

        try {
            const response = await fetch(`/api/non-trading-days/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.showMessage('节假日更新成功', 'success');
                this.closeModal('editHolidayModal');
                this.loadHolidays();
            } else {
                this.showMessage(result.message, 'error');
            }
        } catch (error) {
            console.error('更新节假日失败:', error);
            this.showMessage('更新节假日失败', 'error');
        }
    }

    async deleteHoliday(id, date) {
        if (!confirm(`确定要删除 ${date} 的节假日配置吗？`)) {
            return;
        }

        try {
            const response = await fetch(`/api/non-trading-days/${id}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showMessage('节假日删除成功', 'success');
                this.loadHolidays();
            } else {
                this.showMessage(result.message, 'error');
            }
        } catch (error) {
            console.error('删除节假日失败:', error);
            this.showMessage('删除节假日失败', 'error');
        }
    }

    async showCalendar() {
        const modal = new bootstrap.Modal(document.getElementById('calendarModal'));
        modal.show();
    }

    async loadCalendar(year) {
        try {
            const response = await fetch(`/api/trading-calendar/${year}`);
            const result = await response.json();

            const content = document.getElementById('calendarContent');
            if (result.success) {
                const data = result.data;
                content.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6>年度统计</h6>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>总交易日</span>
                                    <strong class="text-success">${data.total_trading_days} 天</strong>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>非交易日</span>
                                    <strong class="text-danger">${data.total_non_trading_days} 天</strong>
                                </li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6>月度交易日分布</h6>
                            <div class="row">
                                ${Object.entries(data.monthly_trading_days).map(([month, days]) => `
                                    <div class="col-4 mb-2">
                                        <small class="text-muted">${month}月</small>
                                        <div class="fw-bold">${days}天</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                    ${data.non_trading_days.length > 0 ? `
                        <div class="mt-4">
                            <h6>节假日列表</h6>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>日期</th>
                                            <th>名称</th>
                                            <th>描述</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${data.non_trading_days.map(holiday => `
                                            <tr>
                                                <td>${holiday.date}</td>
                                                <td>${holiday.name}</td>
                                                <td>${holiday.description || '-'}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ` : ''}
                `;
            } else {
                content.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i>
                        ${result.message}
                    </div>
                `;
            }
        } catch (error) {
            console.error('加载交易日历失败:', error);
            document.getElementById('calendarContent').innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    加载交易日历失败
                </div>
            `;
        }
    }

    async bulkImport() {
        const data = document.getElementById('bulkImportData').value.trim();
        if (!data) {
            this.showMessage('请输入导入数据', 'warning');
            return;
        }

        try {
            const holidays = JSON.parse(data);
            if (!Array.isArray(holidays)) {
                throw new Error('数据格式错误，应为数组');
            }

            const response = await fetch('/api/non-trading-days/bulk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ holidays })
            });

            const result = await response.json();

            if (result.success) {
                this.showMessage(`成功导入 ${result.data.length} 个节假日`, 'success');
                this.closeModal('bulkImportModal');
                document.getElementById('bulkImportData').value = '';
                this.loadHolidays();
            } else {
                this.showMessage(result.message, 'error');
            }
        } catch (error) {
            console.error('批量导入失败:', error);
            this.showMessage('数据格式错误或导入失败', 'error');
        }
    }

    closeModal(modalId) {
        const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
        if (modal) {
            modal.hide();
        }
    }

    resetForm(formId) {
        const form = document.getElementById(formId);
        form.reset();
        form.classList.remove('was-validated');
    }

    showMessage(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';

        const icon = {
            'success': 'check-circle',
            'error': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        }[type] || 'info-circle';

        // 使用现有的消息显示系统
        if (typeof showMessage === 'function') {
            showMessage(message, type);
        } else {
            // 备用消息显示
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert ${alertClass} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                <i class="bi bi-${icon}"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            const container = document.getElementById('message-container');
            if (container) {
                container.appendChild(alertDiv);
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.parentNode.removeChild(alertDiv);
                    }
                }, 5000);
            }
        }
    }
}

// 初始化管理器
let nonTradingDaysManager;

document.addEventListener('DOMContentLoaded', function() {
    nonTradingDaysManager = new NonTradingDaysManager();
});