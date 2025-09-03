/**
 * 分批止盈目标管理组件
 * 用于管理交易记录中的多个止盈目标
 */
class ProfitTargetsManager {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.querySelector(container) : container;
        this.options = {
            maxTargets: 10,
            minTargets: 1,
            buyPrice: 0,
            onTargetsChange: null,
            onValidationChange: null,
            ...options
        };

        this.targets = [];
        this.nextId = 1;
        this.isValid = true;
        this.validationErrors = {};

        this.init();
    }

    init() {
        if (!this.container) {
            console.error('ProfitTargetsManager: Container not found');
            return;
        }

        this.render();
        this.setupEventListeners();

        // 添加默认的第一个止盈目标，但不触发通知
        if (this.targets.length === 0) {
            this.addTarget(null, false); // 第二个参数表示不触发通知
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="profit-targets-manager" style="max-width: 800px;">
                <!-- 标题区域 -->
                <div class="d-flex justify-content-between align-items-center mb-4 p-3 bg-gradient rounded-3 shadow-sm" 
                     style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-bullseye text-white fs-4 me-3"></i>
                        <h5 class="mb-0 text-white fw-bold">止盈目标设置</h5>
                    </div>
                    <button type="button" class="btn btn-light btn-lg shadow-sm" id="add-target-btn">
                        <i class="bi bi-plus-circle me-2"></i>
                        <span class="fw-semibold">添加止盈目标</span>
                    </button>
                </div>
                
                <!-- 目标列表容器 -->
                <div class="targets-container mb-4" id="targets-container">
                    <!-- 止盈目标列表将在这里渲染 -->
                </div>
                
                <!-- 汇总信息 -->
                <div class="targets-summary mb-3" id="targets-summary">
                    <!-- 汇总信息将在这里显示 -->
                </div>
                
                <!-- 验证消息 -->
                <div class="validation-messages" id="validation-messages">
                    <!-- 验证错误信息将在这里显示 -->
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        // 添加止盈目标按钮
        const addBtn = this.container.querySelector('#add-target-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addTarget());
        }

        // 使用事件委托处理动态添加的元素
        this.container.addEventListener('click', (e) => {
            if (e.target.matches('.remove-target-btn')) {
                const targetId = parseInt(e.target.dataset.targetId);
                this.removeTarget(targetId);
            }
        });

        this.container.addEventListener('input', (e) => {
            if (e.target.matches('.target-input')) {
                this.handleTargetInputChange(e.target);
            }
        });

        this.container.addEventListener('blur', (e) => {
            if (e.target.matches('.target-input')) {
                this.validateTarget(e.target);
            }
        });
    }

    addTarget(data = null, notify = true) {
        if (this.targets.length >= this.options.maxTargets) {
            UXUtils.showWarning(`最多只能添加${this.options.maxTargets}个止盈目标`);
            return;
        }

        const target = {
            id: this.nextId++,
            targetPrice: data?.targetPrice || '',
            profitRatio: data?.profitRatio || '',
            sellRatio: data?.sellRatio || '',
            expectedProfitRatio: data?.expectedProfitRatio || 0,
            sequenceOrder: this.targets.length + 1
        };

        this.targets.push(target);
        this.renderTargets();
        this.updateSummary();
        this.validateAllTargets();

        if (notify) {
            this.notifyChange();
        }

        // 聚焦到新添加的止盈比例输入框
        setTimeout(() => {
            const newTargetInput = this.container.querySelector(`[data-target-id="${target.id}"] .profit-ratio-input`);
            if (newTargetInput) {
                newTargetInput.focus();
            }
        }, 100);
    }

    removeTarget(targetId) {
        if (this.targets.length <= this.options.minTargets) {
            UXUtils.showWarning(`至少需要保留${this.options.minTargets}个止盈目标`);
            return;
        }

        this.targets = this.targets.filter(target => target.id !== targetId);

        // 重新排序
        this.targets.forEach((target, index) => {
            target.sequenceOrder = index + 1;
        });

        this.renderTargets();
        this.updateSummary();
        this.validateAllTargets();
        this.notifyChange();
    }

    renderTargets() {
        const container = this.container.querySelector('#targets-container');
        if (!container) return;

        container.innerHTML = this.targets.map(target => this.renderTarget(target)).join('');

        // 更新添加按钮状态
        const addBtn = this.container.querySelector('#add-target-btn');
        if (addBtn) {
            addBtn.disabled = this.targets.length >= this.options.maxTargets;
        }
    }

    renderTarget(target) {
        const canRemove = this.targets.length > this.options.minTargets;

        return `
            <div class="target-row mb-4 p-4 border rounded-3 shadow-sm bg-white position-relative" 
                 data-target-id="${target.id}" 
                 style="border: 2px solid #e9ecef !important; transition: all 0.3s ease;">
                
                <!-- 目标序号标识 -->
                <div class="position-absolute top-0 start-0 translate-middle">
                    <span class="badge bg-primary rounded-pill px-3 py-2 fs-6 shadow-sm">
                        #${target.sequenceOrder}
                    </span>
                </div>
                
                <!-- 删除按钮 -->
                ${canRemove ? `
                    <div class="position-absolute top-0 end-0 translate-middle">
                        <button type="button" 
                                class="btn btn-danger btn-sm rounded-circle remove-target-btn shadow-sm" 
                                data-target-id="${target.id}"
                                title="删除此止盈目标"
                                style="width: 32px; height: 32px; padding: 0;">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    </div>
                ` : ''}
                
                <!-- 平衡宽度的单行布局 -->
                <div class="d-flex align-items-end gap-2" style="flex-wrap: wrap;">
                    <!-- 止盈比例 -->
                    <div style="width: 150px; flex-shrink: 0;">
                        <label class="form-label text-primary mb-1" style="font-size: 0.75rem; font-weight: 600;">
                            止盈比例 <span class="text-danger">*</span>
                        </label>
                        <div class="input-group input-group-sm">
                            <input type="number" 
                                   class="form-control target-input profit-ratio-input" 
                                   name="profit_ratio_${target.id}"
                                   data-target-id="${target.id}"
                                   data-field="profitRatio"
                                   value="${target.profitRatio}" 
                                   step="0.01" 
                                   min="0.01" 
                                   max="1000"
                                   placeholder="20.00"
                                   style="font-weight: 600; font-size: 0.85rem;">
                            <span class="input-group-text bg-primary text-white fw-bold" style="font-size: 0.75rem;">%</span>
                        </div>
                    </div>
                    
                    <!-- 止盈价格 -->
                    <div style="width: 150px; flex-shrink: 0;">
                        <label class="form-label text-success mb-1" style="font-size: 0.75rem; font-weight: 600;">
                            止盈价格
                        </label>
                        <div class="input-group input-group-sm">
                            <span class="input-group-text bg-success text-white fw-bold" style="font-size: 0.75rem;">¥</span>
                            <input type="number" 
                                   class="form-control target-input target-price-input" 
                                   name="target_price_${target.id}"
                                   data-target-id="${target.id}"
                                   data-field="targetPrice"
                                   value="${target.targetPrice}" 
                                   step="0.01" 
                                   min="0.01" 
                                   placeholder="0.00"
                                   readonly
                                   style="font-weight: 600; background-color: #f8f9fa; font-size: 0.85rem;">
                        </div>
                    </div>
                    
                    <!-- 卖出比例 -->
                    <div style="width: 150px; flex-shrink: 0;">
                        <label class="form-label text-warning mb-1" style="font-size: 0.75rem; font-weight: 600;">
                            卖出比例 <span class="text-danger">*</span>
                        </label>
                        <div class="input-group input-group-sm">
                            <input type="number" 
                                   class="form-control target-input sell-ratio-input" 
                                   name="sell_ratio_${target.id}"
                                   data-target-id="${target.id}"
                                   data-field="sellRatio"
                                   value="${target.sellRatio}" 
                                   step="0.01" 
                                   min="0.01" 
                                   max="1000" 
                                   placeholder="30.00"
                                   style="font-weight: 600; font-size: 0.85rem;">
                            <span class="input-group-text bg-warning text-dark fw-bold" style="font-size: 0.75rem;">%</span>
                        </div>
                    </div>
                    
                    <!-- 预期收益率 -->
                    <div style="width: 160px; flex-shrink: 0;">
                        <label class="form-label text-info mb-1" style="font-size: 0.75rem; font-weight: 600;">
                            预期收益率
                        </label>
                        <div class="bg-light rounded text-center align-items-center justify-content-center border" style="height: 40px; width: 100px; border-color: #17a2b8 !important;display: flex;align-items: center;justify-content: center;">
                            <span class="expected-profit-ratio fw-bold ${target.expectedProfitRatio > 0 ? 'text-success' : 'text-muted'}" 
                                  data-target-id="${target.id}"
                                  style="font-size: 0.8rem;">
                                ${this.formatPercent(target.expectedProfitRatio)}
                            </span>
                        </div>
                    </div>
                </div>
                
                <div class="target-validation-messages mt-3" data-target-id="${target.id}">
                    <!-- 目标验证错误信息 -->
                </div>
            </div>
        `;
    }

    handleTargetInputChange(input) {
        const targetId = parseInt(input.dataset.targetId);
        const field = input.dataset.field;
        const value = input.value;

        const target = this.targets.find(t => t.id === targetId);
        if (!target) return;

        target[field] = value;

        // 如果是止盈比例变化，自动计算止盈价格
        if (field === 'profitRatio' && value && this.options.buyPrice > 0) {
            const profitRatio = parseFloat(value);
            const buyPrice = this.options.buyPrice;

            if (profitRatio > 0) {
                target.targetPrice = (buyPrice * (1 + profitRatio / 100)).toFixed(2);

                // 更新界面上的止盈价格显示
                const targetPriceInput = this.container.querySelector(`[data-target-id="${targetId}"][data-field="targetPrice"]`);
                if (targetPriceInput) {
                    targetPriceInput.value = target.targetPrice;
                }
            }
        }

        // 实时计算预期收益率
        this.calculateExpectedProfit(target);
        this.updateTargetDisplay(target);
        this.updateSummary();
        this.validateTarget(input);
        this.notifyChange();
    }

    calculateExpectedProfit(target) {
        const sellRatio = parseFloat(target.sellRatio) || 0;
        const profitRatio = parseFloat(target.profitRatio) || 0;

        // 预期收益率 = 卖出比例 × 止盈比例
        target.expectedProfitRatio = (sellRatio / 100) * (profitRatio / 100);
    }

    updateTargetDisplay(target) {
        const expectedProfitElement = this.container.querySelector(`[data-target-id="${target.id}"].expected-profit-ratio`);
        if (expectedProfitElement) {
            expectedProfitElement.textContent = this.formatPercent(target.expectedProfitRatio);
            expectedProfitElement.className = `expected-profit-ratio fw-bold ${target.expectedProfitRatio > 0 ? 'text-success' : ''}`;
        }
    }

    updateSummary() {
        const summaryContainer = this.container.querySelector('#targets-summary');
        if (!summaryContainer) return;

        const totalSellRatio = this.targets.reduce((sum, target) => {
            return sum + (parseFloat(target.sellRatio) || 0);
        }, 0);

        const totalExpectedProfit = this.targets.reduce((sum, target) => {
            return sum + (target.expectedProfitRatio || 0);
        }, 0);

        const isOverSold = totalSellRatio > 200;  // 调整过度卖出的阈值
        const sellRatioClass = isOverSold ? 'text-danger' : totalSellRatio > 0 ? 'text-primary' : 'text-muted';
        const profitClass = totalExpectedProfit > 0 ? 'text-success' : 'text-muted';

        // 计算进度条宽度，以200%为基准
        const sellRatioProgress = Math.min(totalSellRatio / 2, 100);  // 200%对应100%进度条
        const progressBarClass = isOverSold ? 'bg-danger' : totalSellRatio > 160 ? 'bg-warning' : 'bg-primary';

        summaryContainer.innerHTML = `
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-light border-0 py-3">
                    <h6 class="mb-0 fw-bold text-dark">
                        <i class="bi bi-bar-chart-line me-2"></i>
                        汇总统计
                    </h6>
                </div>
                <div class="card-body p-4">
                    <div class="row g-4">
                        <!-- 目标数量 -->
                        <div class="col-lg-4">
                            <div class="text-center p-3 bg-light rounded-3">
                                <div class="mb-2">
                                    <i class="bi bi-bullseye fs-2 text-info"></i>
                                </div>
                                <div class="fs-3 fw-bold text-dark">${this.targets.length}</div>
                                <div class="small text-muted">止盈目标数量</div>
                            </div>
                        </div>
                        
                        <!-- 总卖出比例 -->
                        <div class="col-lg-4">
                            <div class="text-center p-3 bg-light rounded-3">
                                <div class="mb-2">
                                    <i class="bi bi-pie-chart fs-2 ${sellRatioClass}"></i>
                                </div>
                                <div class="fs-3 fw-bold ${sellRatioClass}">
                                    ${totalSellRatio.toFixed(1)}%
                                    ${isOverSold ? '<i class="bi bi-exclamation-triangle text-danger ms-1" title="卖出比例超过100%"></i>' : ''}
                                </div>
                                <div class="small text-muted mb-2">总卖出比例</div>
                                <div class="progress" style="height: 8px;">
                                    <div class="progress-bar ${progressBarClass}" 
                                         role="progressbar" 
                                         style="width: ${sellRatioProgress}%" 
                                         aria-valuenow="${sellRatioProgress}" 
                                         aria-valuemin="0" 
                                         aria-valuemax="100">
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 总预期收益率 -->
                        <div class="col-lg-4">
                            <div class="text-center p-3 bg-light rounded-3">
                                <div class="mb-2">
                                    <i class="bi bi-graph-up-arrow fs-2 ${profitClass}"></i>
                                </div>
                                <div class="fs-3 fw-bold ${profitClass}">
                                    ${this.formatPercent(totalExpectedProfit)}
                                </div>
                                <div class="small text-muted">总预期收益率</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 状态提示 -->
                    <div class="mt-3 text-center">
                        ${totalSellRatio === 100 ?
                '<span class="badge bg-success fs-6 px-3 py-2"><i class="bi bi-check-circle me-1"></i>标准配置</span>' :
                totalSellRatio > 200 ?
                    '<span class="badge bg-danger fs-6 px-3 py-2"><i class="bi bi-exclamation-triangle me-1"></i>比例过高</span>' :
                    totalSellRatio > 160 ?
                        '<span class="badge bg-warning fs-6 px-3 py-2"><i class="bi bi-info-circle me-1"></i>比例较高</span>' :
                        '<span class="badge bg-secondary fs-6 px-3 py-2"><i class="bi bi-clock me-1"></i>配置合理</span>'
            }
                    </div>
                </div>
            </div>
        `;
    }

    validateTarget(input) {
        const targetId = parseInt(input.dataset.targetId);
        const field = input.dataset.field;
        const value = input.value;

        const target = this.targets.find(t => t.id === targetId);
        if (!target) return;

        let isValid = true;
        let errorMessage = '';

        // 清除之前的验证状态
        input// .classList.remove(["']is-invalid["'], 'is-valid');

        // 验证规则
        switch (field) {
            case 'profitRatio':
                if (!value || value === '') {
                    isValid = false;
                    errorMessage = '止盈比例不能为空';
                } else {
                    const ratio = parseFloat(value);
                    if (isNaN(ratio) || ratio <= 0) {
                        isValid = false;
                        errorMessage = '止盈比例必须大于0';
                    } else if (ratio > 1000) {  // 允许大于10%的止盈比例
                        isValid = false;
                        errorMessage = '止盈比例不能超过1000%';
                    }
                }
                break;

            case 'targetPrice':
                // 止盈价格现在是自动计算的，不需要验证用户输入
                if (value && value !== '') {
                    const price = parseFloat(value);
                    if (isNaN(price) || price <= 0) {
                        isValid = false;
                        errorMessage = '止盈价格计算错误';
                    } else if (price > 9999.99) {
                        isValid = false;
                        errorMessage = '止盈价格超出范围';
                    }
                }
                break;

            case 'sellRatio':
                if (!value || value === '') {
                    isValid = false;
                    errorMessage = '卖出比例不能为空';
                } else {
                    const ratio = parseFloat(value);
                    if (isNaN(ratio)) {
                        isValid = false;
                        errorMessage = '卖出比例格式无效';
                    } else if (ratio <= 0) {
                        isValid = false;
                        errorMessage = '卖出比例必须大于0';
                    } else if (ratio > 1000) {  // 允许大于100%的卖出比例
                        isValid = false;
                        errorMessage = '单个卖出比例不能超过1000%';
                    }
                }
                break;
        }

        // 更新验证状态
        if (isValid) {
            input// .classList.add(["']is-valid["']);
            this.clearTargetError(targetId, field);
        } else {
            input// .classList.add(["']is-invalid["']);
            this.showTargetError(targetId, field, errorMessage);
        }

        // 更新目标的验证状态
        if (!this.validationErrors[targetId]) {
            this.validationErrors[targetId] = {};
        }

        if (isValid) {
            delete this.validationErrors[targetId][field];
            if (Object.keys(this.validationErrors[targetId]).length === 0) {
                delete this.validationErrors[targetId];
            }
        } else {
            this.validationErrors[targetId][field] = errorMessage;
        }

        this.updateValidationState();
    }

    validateAllTargets() {
        this.validationErrors = {};

        // 验证每个目标
        this.targets.forEach(target => {
            const targetRow = this.container.querySelector(`[data-target-id="${target.id}"]`);
            if (targetRow) {
                const inputs = targetRow.querySelectorAll('.target-input');
                inputs.forEach(input => this.validateTarget(input));
            }
        });

        // 验证总卖出比例
        this.validateTotalSellRatio();

        this.updateValidationState();
    }

    validateTotalSellRatio() {
        const totalSellRatio = this.targets.reduce((sum, target) => {
            return sum + (parseFloat(target.sellRatio) || 0);
        }, 0);

        // 清除之前的总比例错误
        delete this.validationErrors.totalSellRatio;
        delete this.validationErrors.totalSellRatioWarning;

        if (totalSellRatio > 1000) {  // 允许大于100%的总卖出比例，但设置合理上限
            this.validationErrors.totalSellRatio = `所有止盈目标的卖出比例总和不能超过1000%，当前为${totalSellRatio.toFixed(2)}%`;
        } else if (totalSellRatio > 200) {
            // 超过200%给出警告
            this.validationErrors.totalSellRatioWarning = `卖出比例总和较高(${totalSellRatio.toFixed(2)}%)，请确认是否合理`;
        } else if (totalSellRatio < 50 && totalSellRatio > 0) {
            // 小于50%给出提示
            this.validationErrors.totalSellRatioWarning = `卖出比例总和较低(${totalSellRatio.toFixed(2)}%)，可能未充分利用止盈机会`;
        }
    }

    showTargetError(targetId, field, message) {
        const targetRow = this.container.querySelector(`[data-target-id="${targetId}"]`);
        if (!targetRow) return;

        const messagesContainer = targetRow.querySelector('.target-validation-messages');
        if (!messagesContainer) return;

        // 移除现有的错误信息
        const existingError = messagesContainer.querySelector(`[data-field="${field}"]`);
        if (existingError) {
            existingError.remove();
        }

        // 添加新的错误信息
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block small';
        errorDiv.dataset.field = field;
        errorDiv.textContent = message;
        messagesContainer.appendChild(errorDiv);
    }

    clearTargetError(targetId, field) {
        const targetRow = this.container.querySelector(`[data-target-id="${targetId}"]`);
        if (!targetRow) return;

        const messagesContainer = targetRow.querySelector('.target-validation-messages');
        if (!messagesContainer) return;

        const errorDiv = messagesContainer.querySelector(`[data-field="${field}"]`);
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    updateValidationState() {
        // 区分错误和警告
        const errorKeys = Object.keys(this.validationErrors).filter(key =>
            key !== 'totalSellRatioWarning' && !key.endsWith('Warning')
        );
        const hasErrors = errorKeys.length > 0;
        const wasValid = this.isValid;
        this.isValid = !hasErrors;

        // 显示全局验证消息
        this.showValidationMessages();

        // 如果验证状态发生变化，通知外部
        if (wasValid !== this.isValid && this.options.onValidationChange) {
            this.options.onValidationChange(this.isValid, this.validationErrors);
        }
    }

    showValidationMessages() {
        const messagesContainer = this.container.querySelector('#validation-messages');
        if (!messagesContainer) return;

        messagesContainer.innerHTML = '';

        // 显示严重错误（阻止保存）
        if (this.validationErrors.totalSellRatio) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger alert-sm';
            errorDiv.innerHTML = `
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                <strong>错误：</strong>${this.validationErrors.totalSellRatio}
            `;
            messagesContainer.appendChild(errorDiv);
        }

        // 显示警告信息（不阻止保存）
        if (this.validationErrors.totalSellRatioWarning) {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'alert alert-warning alert-sm';
            warningDiv.innerHTML = `
                <i class="bi bi-exclamation-triangle me-2"></i>
                <strong>提示：</strong>${this.validationErrors.totalSellRatioWarning}
            `;
            messagesContainer.appendChild(warningDiv);
        }

        // 显示一般性提示
        const targetCount = this.targets.length;
        const validTargets = this.targets.filter(t => t.targetPrice && t.sellRatio).length;

        if (targetCount > 0 && validTargets < targetCount) {
            const infoDiv = document.createElement('div');
            infoDiv.className = 'alert alert-info alert-sm';
            infoDiv.innerHTML = `
                <i class="bi bi-info-circle me-2"></i>
                还有${targetCount - validTargets}个止盈目标需要完善信息
            `;
            messagesContainer.appendChild(infoDiv);
        }
    }

    // 公共方法
    getTargets() {
        return this.targets.map(target => {
            // 前端统一使用百分比格式，直接发送给后端
            // 后端会负责转换为小数格式存储
            return {
                targetPrice: parseFloat(target.targetPrice) || 0,
                profitRatio: parseFloat(target.profitRatio) || 0,  // 百分比格式（如20表示20%）
                sellRatio: parseFloat(target.sellRatio) || 0,      // 百分比格式（如30表示30%）
                expectedProfitRatio: target.expectedProfitRatio || 0,
                sequenceOrder: target.sequenceOrder
            };
        });
    }

    setTargets(targets) {
        this.targets = [];
        this.nextId = 1;

        if (targets && targets.length > 0) {
            targets.forEach((targetData, index) => {
                // 处理从后端获取的数据格式转换
                let sellRatio = targetData.sellRatio || targetData.sell_ratio || '';
                let profitRatio = targetData.profitRatio || targetData.profit_ratio || '';

                // 后端存储的是小数格式，转换为百分比格式供前端显示
                if (sellRatio && parseFloat(sellRatio) <= 1) {
                    sellRatio = (parseFloat(sellRatio) * 100).toFixed(2);
                }
                if (profitRatio && parseFloat(profitRatio) <= 1) {
                    profitRatio = (parseFloat(profitRatio) * 100).toFixed(2);
                }

                const target = {
                    id: this.nextId++,
                    targetPrice: targetData.targetPrice || targetData.target_price || '',
                    profitRatio: profitRatio,
                    sellRatio: sellRatio,
                    expectedProfitRatio: targetData.expectedProfitRatio || targetData.expected_profit_ratio || 0,
                    sequenceOrder: targetData.sequenceOrder || targetData.sequence_order || (index + 1)
                };
                this.targets.push(target);
            });
        } else {
            // 如果没有数据，添加一个默认目标
            this.addTarget();
            return;
        }

        this.renderTargets();
        this.updateSummary();
        this.validateAllTargets();
    }

    setBuyPrice(buyPrice) {
        this.options.buyPrice = parseFloat(buyPrice) || 0;

        // 重新计算所有目标的止盈价格
        this.targets.forEach(target => {
            if (target.profitRatio && this.options.buyPrice > 0) {
                const profitRatio = parseFloat(target.profitRatio);
                const buyPrice = this.options.buyPrice;

                if (profitRatio > 0) {
                    target.targetPrice = (buyPrice * (1 + profitRatio / 100)).toFixed(2);
                }
            }
            this.calculateExpectedProfit(target);
        });

        this.renderTargets();
        this.updateSummary();
        this.validateAllTargets();
    }

    isValidTargets() {
        return this.isValid;
    }

    // 执行完整验证（包括后端验证）
    async performFullValidation() {
        // 先执行前端验证
        this.validateAllTargets();

        if (!this.isValid) {
            return {
                isValid: false,
                errors: this.validationErrors,
                source: 'frontend'
            };
        }

        // 如果前端验证通过，执行后端验证
        const backendResult = await this.validateWithBackend();

        if (!backendResult.isValid) {
            this.showBackendValidationErrors(backendResult.errors);
            return {
                isValid: false,
                errors: backendResult.errors,
                source: 'backend'
            };
        }

        return {
            isValid: true,
            validationResult: backendResult.validationResult,
            source: 'both'
        };
    }

    getValidationErrors() {
        return this.validationErrors;
    }

    clear() {
        this.targets = [];
        this.nextId = 1;
        this.validationErrors = {};
        this.isValid = true;

        this.renderTargets();
        this.updateSummary();
        this.showValidationMessages();

        // 添加默认目标
        this.addTarget();
    }

    // 后端验证方法
    async validateWithBackend() {
        if (!this.options.buyPrice || this.options.buyPrice <= 0) {
            return {
                isValid: false,
                errors: { buyPrice: '买入价格无效，无法进行后端验证' }
            };
        }

        const targets = this.getTargets().map(target => ({
            target_price: target.targetPrice,
            profit_ratio: target.profitRatio, // 发送百分比格式，后端会处理转换
            sell_ratio: target.sellRatio,     // 发送百分比格式，后端会处理转换
            sequence_order: target.sequenceOrder
        }));

        try {
            const response = await fetch('/api/trades/validate-profit-targets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    buy_price: this.options.buyPrice,
                    profit_targets: targets
                })
            });

            const result = await response.json();

            if (result.success) {
                return {
                    isValid: result.data.is_valid,
                    errors: result.data.validation_errors || {},
                    validationResult: result.data.validation_result || null
                };
            } else {
                return {
                    isValid: false,
                    errors: { general: result.error?.message || '后端验证失败' }
                };
            }
        } catch (error) {
            console.error('Backend validation error:', error);
            return {
                isValid: false,
                errors: { general: '网络错误，无法进行后端验证' }
            };
        }
    }

    // 显示后端验证错误
    showBackendValidationErrors(errors) {
        // 清除现有的后端验证错误
        this.container.querySelectorAll('.backend-validation-error').forEach(el => el.remove());

        if (errors.general) {
            const messagesContainer = this.container.querySelector('#validation-messages');
            if (messagesContainer) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger alert-sm backend-validation-error';
                errorDiv.innerHTML = `
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <strong>后端验证错误：</strong>${errors.general}
                `;
                messagesContainer.appendChild(errorDiv);
            }
        }

        // 显示具体字段的后端验证错误
        Object.keys(errors).forEach(key => {
            if (key.startsWith('targets[')) {
                const match = key.match(/targets\[(\d+)\]/);
                if (match) {
                    const targetIndex = parseInt(match[1]);
                    const target = this.targets[targetIndex];
                    if (target) {
                        const targetErrors = errors[key];
                        Object.keys(targetErrors).forEach(field => {
                            this.showTargetError(target.id, `backend_${field}`, targetErrors[field]);
                        });
                    }
                }
            }
        });
    }

    // 工具方法
    formatPercent(value) {
        if (!value || value === 0) return '0.00%';
        return (value * 100).toFixed(2) + '%';
    }

    notifyChange() {
        if (this.options.onTargetsChange) {
            this.options.onTargetsChange(this.getTargets(), this.isValid);
        }
    }

    // 销毁组件
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.targets = [];
        this.validationErrors = {};
    }
}

// 导出到全局作用域
if (typeof window !== 'undefined') {
    window.ProfitTargetsManager = ProfitTargetsManager;
}
window.ProfitTargetsManager = ProfitTargetsManager;