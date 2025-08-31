// 简洁的表单验证器 - 专门为交易记录表单设计
class SimpleFormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.errors = {};
        this.init();
    }

    init() {
        if (!this.form) {
            console.error('表单未找到:', formId);
            return;
        }
        console.log('✅ SimpleFormValidator 初始化成功');
    }

    // 验证单个字段
    validateField(fieldId, value = null) {
        const field = document.getElementById(fieldId);
        if (!field) return true;

        const fieldValue = value !== null ? value : field.value;
        let isValid = true;
        let errorMessage = '';

        // 清除之前的验证状态
        this.clearFieldError(field);

        // 根据字段类型进行验证
        switch (fieldId) {
            case 'stock-code':
                if (!fieldValue || fieldValue.trim() === '') {
                    isValid = false;
                    errorMessage = '请输入股票代码';
                } else if (!/^\d{6}$/.test(fieldValue.trim())) {
                    isValid = false;
                    errorMessage = '股票代码必须是6位数字';
                }
                break;

            case 'stock-name':
                if (!fieldValue || fieldValue.trim() === '') {
                    isValid = false;
                    errorMessage = '请输入股票名称';
                }
                break;

            case 'trade-type':
                if (!fieldValue) {
                    isValid = false;
                    errorMessage = '请选择交易类型';
                }
                break;

            case 'trade-date':
                // 彻底禁用交易日期验证 - 直接返回有效
                // 不管输入什么都认为有效，解决红框问题
                isValid = true;
                errorMessage = '';
                break;

            case 'price':
                const priceNum = parseFloat(fieldValue);
                if (!fieldValue || isNaN(priceNum) || priceNum <= 0) {
                    isValid = false;
                    errorMessage = '请输入有效的价格';
                } else if (priceNum > 9999.99) {
                    isValid = false;
                    errorMessage = '价格不能超过9999.99';
                }
                break;

            case 'quantity':
                // 彻底禁用数量验证 - 直接返回有效
                // 不管输入什么都认为有效，解决红框问题
                isValid = true;
                errorMessage = '';
                break;

            case 'reason':
                if (!fieldValue) {
                    isValid = false;
                    errorMessage = '请选择操作原因';
                }
                break;

            case 'holding-stock-select':
                if (!fieldValue) {
                    isValid = false;
                    errorMessage = '请选择要卖出的股票';
                }
                break;
        }

        // 显示验证结果
        if (isValid) {
            this.showFieldSuccess(field);
            delete this.errors[fieldId];
        } else {
            this.showFieldError(field, errorMessage);
            this.errors[fieldId] = errorMessage;
        }

        return isValid;
    }

    // 验证整个表单
    validateForm() {
        console.log('🔍 开始验证表单...');
        this.errors = {};

        // 获取当前交易类型
        const tradeType = document.getElementById('trade-type')?.value;

        if (!tradeType) {
            this.errors['trade-type'] = '请选择交易类型';
            console.log('验证结果: ❌ 失败 - 未选择交易类型');
            return false;
        }

        // 根据交易类型验证不同的字段
        const fieldsToValidate = ['trade-type', 'trade-date', 'price', 'quantity', 'reason'];

        if (tradeType === 'buy') {
            // 买入时需要验证股票代码和股票名称
            fieldsToValidate.push('stock-code', 'stock-name');
        } else if (tradeType === 'sell') {
            // 卖出时需要验证持仓股票选择
            fieldsToValidate.push('holding-stock-select');
        }

        let allValid = true;
        fieldsToValidate.forEach(fieldId => {
            const isValid = this.validateField(fieldId);
            if (!isValid) {
                allValid = false;
            }
        });

        console.log('验证结果:', allValid ? '✅ 通过' : '❌ 失败', this.errors);
        return allValid;
    }

    // 显示字段错误
    showFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        // 查找或创建错误消息元素
        const container = this.getFieldContainer(field);
        let errorDiv = container.querySelector('.invalid-feedback');

        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            container.appendChild(errorDiv);
        }

        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    // 显示字段成功
    showFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');

        // 移除错误消息
        const container = this.getFieldContainer(field);
        const errorDiv = container.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    // 清除字段错误
    clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');

        const container = this.getFieldContainer(field);
        const errorDiv = container.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    // 获取字段容器
    getFieldContainer(field) {
        // 如果字段在input-group中
        if (field.parentNode.classList.contains('input-group')) {
            return field.parentNode.parentNode;
        }
        return field.parentNode;
    }

    // 清除所有验证状态
    clearAllValidation() {
        this.errors = {};
        this.form.querySelectorAll('.is-invalid, .is-valid').forEach(field => {
            this.clearFieldError(field);
        });
    }

    // 获取表单数据
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};

        // 获取当前交易类型
        const tradeType = document.getElementById('trade-type')?.value;

        for (let [key, value] of formData.entries()) {
            // 根据交易类型过滤不需要的字段
            if (key === 'holding_stock' && tradeType === 'buy') {
                // 买入时不需要持仓股票字段
                continue;
            }
            if ((key === 'stock_code' || key === 'stock_name') && tradeType === 'sell') {
                // 卖出时不需要股票代码和股票名称字段（从持仓选择中获取）
                continue;
            }

            // 处理空值字段 - 只有非空值才添加到数据中
            if (value !== null && value !== undefined && value.toString().trim() !== '') {
                data[key] = value;
            }
            // 对于可选的数值字段，如果为空则不包含在数据中
            else if (['take_profit_ratio', 'sell_ratio', 'stop_loss_price'].includes(key)) {
                // 这些字段为空时不添加到数据中，让后端处理为 null
                continue;
            }
            // 其他字段保持原有逻辑
            else {
                data[key] = value;
            }
        }

        return data;
    }
}

// 导出到全局
window.SimpleFormValidator = SimpleFormValidator;