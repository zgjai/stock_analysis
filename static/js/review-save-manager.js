/**
 * 复盘保存管理器
 * 管理复盘表单的保存逻辑、变化检测和用户反馈
 */
class ReviewSaveManager {
    constructor(formSelector = '#review-form') {
        this.form = document.querySelector(formSelector);
        this.hasUnsavedChanges = false;
        this.autoSaveTimer = null;
        this.autoSaveInterval = 30000; // 30秒自动保存
        this.isAutoSaveEnabled = false;
        this.isSaving = false;
        this.originalFormData = {};
        this.saveButton = null;
        this.saveStatusIndicator = null;
        this.saveProgressContainer = null;
        this.lastSaveAttempt = 0; // 防抖机制
        this.performanceMetrics = {
            saveAttempts: 0,
            successfulSaves: 0,
            averageSaveTime: 0,
            totalSaveTime: 0
        };
        
        if (!this.form) {
            console.error('ReviewSaveManager: 未找到复盘表单');
            return;
        }
        
        this.init();
    }

    /**
     * 初始化保存管理器
     */
    init() {
        this.setupFormElements();
        this.setupEventListeners();
        this.setupBeforeUnloadWarning();
        this.createSaveStatusIndicator();
        this.captureOriginalFormData();
        this.setupAutoSave();
        this.setupPerformanceOptimizations();
        
        console.log('ReviewSaveManager 初始化完成');
    }
    
    /**
     * 设置自动保存
     */
    setupAutoSave() {
        if (typeof autoSaveManager !== 'undefined') {
            autoSaveManager.enable(
                () => this.saveReview(),
                () => this.hasUnsavedChanges,
                'review'
            );
        }
    }
    
    /**
     * 设置性能优化 - 增强版本，包含多种优化策略
     */
    setupPerformanceOptimizations() {
        console.log('⚡ 设置性能优化');
        
        // 1. 防抖优化 - 变化检测
        this.debouncedDetectChanges = debounce(() => {
            this.detectChanges();
        }, 300);
        
        // 2. 节流优化 - 状态更新
        this.throttledUpdateStatus = throttle(() => {
            this.updateSaveButtonState();
            this.updateSaveStatusIndicator();
        }, 100);

        // 3. 防抖优化 - 保存操作（防止重复提交）
        this.debouncedSave = debounce(() => {
            this.saveReview();
        }, 500);

        // 4. 批量处理优化 - 表单验证
        this.batchValidator = this.createBatchValidator();

        // 5. 内存缓存优化 - 表单数据
        this.formDataCache = new Map();
        this.cacheCleanupInterval = setInterval(() => {
            this.cleanupFormDataCache();
        }, 60000); // 每分钟清理一次

        // 6. 懒加载优化 - 非关键功能
        this.setupLazyFeatures();

        // 7. 预加载优化 - 常用数据
        this.preloadCommonData();

        // 8. 网络优化 - 请求合并和缓存
        this.setupNetworkOptimizations();

        // 9. DOM操作优化 - 批量更新
        this.setupDOMOptimizations();

        // 10. 内存监控 - 防止内存泄漏
        this.setupMemoryMonitoring();

        console.log('✅ 性能优化设置完成');
    }

    /**
     * 创建批量验证器
     */
    createBatchValidator() {
        const validationQueue = [];
        let validationTimer = null;

        return {
            add: (field, rules) => {
                validationQueue.push({ field, rules });
                
                if (validationTimer) {
                    clearTimeout(validationTimer);
                }
                
                validationTimer = setTimeout(() => {
                    this.processBatchValidation(validationQueue.splice(0));
                }, 200);
            }
        };
    }

    /**
     * 处理批量验证
     */
    processBatchValidation(validations) {
        const results = [];
        
        validations.forEach(({ field, rules }) => {
            const result = this.validateField(field, rules);
            results.push({ field, result });
        });

        // 批量更新UI
        this.updateValidationUI(results);
    }

    /**
     * 更新验证UI
     */
    updateValidationUI(results) {
        // 使用 requestAnimationFrame 优化DOM更新
        requestAnimationFrame(() => {
            results.forEach(({ field, result }) => {
                if (result.isValid) {
                    field// .classList.remove(["']is-invalid["']);
                    field// .classList.add(["']is-valid["']);
                } else {
                    field// .classList.remove(["']is-valid["']);
                    field// .classList.add(["']is-invalid["']);
                }
            });
        });
    }

    /**
     * 设置懒加载功能
     */
    setupLazyFeatures() {
        // 懒加载自动保存功能
        this.lazyAutoSave = () => {
            if (!this.autoSaveInitialized) {
                this.initializeAutoSave();
                this.autoSaveInitialized = true;
            }
        };

        // 懒加载高级验证功能
        this.lazyAdvancedValidation = () => {
            if (!this.advancedValidationInitialized) {
                this.initializeAdvancedValidation();
                this.advancedValidationInitialized = true;
            }
        };
    }

    /**
     * 预加载常用数据
     */
    preloadCommonData() {
        // 预加载股票代码列表（如果需要）
        if (typeof apiClient !== 'undefined' && apiClient.getStockCodes) {
            setTimeout(() => {
                apiClient.getStockCodes().then(codes => {
                    this.formDataCache.set('stockCodes', codes);
                }).catch(error => {
                    console.warn('⚠️ 预加载股票代码失败:', error);
                });
            }, 1000);
        }
    }

    /**
     * 设置网络优化
     */
    setupNetworkOptimizations() {
        // 请求去重
        this.pendingRequests = new Map();
        
        // 请求缓存
        this.requestCache = new Map();
        
        // 网络状态监控
        if ('connection' in navigator) {
            this.networkInfo = navigator.connection;
            this.adaptToNetworkConditions();
            
            navigator.connection.addEventListener('change', () => {
                this.adaptToNetworkConditions();
            });
        }
    }

    /**
     * 根据网络条件调整行为
     */
    adaptToNetworkConditions() {
        if (!this.networkInfo) return;

        const effectiveType = this.networkInfo.effectiveType;
        
        if (effectiveType === 'slow-2g' || effectiveType === '2g') {
            // 慢网络：增加防抖时间，减少请求频率
            this.debouncedDetectChanges = debounce(() => {
                this.detectChanges();
            }, 800);
            
            this.autoSaveInterval = 60000; // 1分钟
            console.log('🐌 检测到慢网络，已调整性能参数');
        } else if (effectiveType === '4g') {
            // 快网络：减少防抖时间，提高响应性
            this.debouncedDetectChanges = debounce(() => {
                this.detectChanges();
            }, 200);
            
            this.autoSaveInterval = 15000; // 15秒
            console.log('🚀 检测到快网络，已优化响应性');
        }
    }

    /**
     * 设置DOM操作优化
     */
    setupDOMOptimizations() {
        // DOM更新批处理
        this.domUpdateQueue = [];
        this.domUpdateScheduled = false;

        this.batchDOMUpdate = (updateFn) => {
            this.domUpdateQueue.push(updateFn);
            
            if (!this.domUpdateScheduled) {
                this.domUpdateScheduled = true;
                requestAnimationFrame(() => {
                    this.processDOMUpdates();
                });
            }
        };
    }

    /**
     * 处理DOM更新队列
     */
    processDOMUpdates() {
        const updates = this.domUpdateQueue.splice(0);
        
        updates.forEach(updateFn => {
            try {
                updateFn();
            } catch (error) {
                console.error('DOM更新错误:', error);
            }
        });
        
        this.domUpdateScheduled = false;
    }

    /**
     * 设置内存监控
     */
    setupMemoryMonitoring() {
        // 定期检查内存使用情况
        this.memoryCheckInterval = setInterval(() => {
            if ('memory' in performance) {
                const memInfo = performance.memory;
                const usedMB = (memInfo.usedJSHeapSize / 1024 / 1024).toFixed(2);
                const limitMB = (memInfo.jsHeapSizeLimit / 1024 / 1024).toFixed(2);
                
                console.log(`💾 内存使用: ${usedMB}MB / ${limitMB}MB`);
                
                // 如果内存使用超过80%，触发清理
                if (memInfo.usedJSHeapSize / memInfo.jsHeapSizeLimit > 0.8) {
                    console.warn('⚠️ 内存使用过高，执行清理');
                    this.performMemoryCleanup();
                }
            }
        }, 30000); // 每30秒检查一次
    }

    /**
     * 执行内存清理
     */
    performMemoryCleanup() {
        // 清理表单数据缓存
        this.cleanupFormDataCache();
        
        // 清理请求缓存
        this.requestCache.clear();
        
        // 清理分析数据（只保留最近的）
        try {
            ['save_success', 'save_error'].forEach(category => {
                const storageKey = `review_analytics_${category}`;
                const data = JSON.parse(localStorage.getItem(storageKey) || '[]');
                if (data.length > 50) {
                    const recentData = data.slice(-50);
                    localStorage.setItem(storageKey, JSON.stringify(recentData));
                }
            });
        } catch (error) {
            console.warn('清理分析数据失败:', error);
        }
        
        console.log('🧹 内存清理完成');
    }

    /**
     * 清理表单数据缓存
     */
    cleanupFormDataCache() {
        const now = Date.now();
        const maxAge = 5 * 60 * 1000; // 5分钟
        
        for (const [key, data] of this.formDataCache.entries()) {
            if (data.timestamp && (now - data.timestamp) > maxAge) {
                this.formDataCache.delete(key);
            }
        }
    }

    /**
     * 设置表单元素引用
     */
    setupFormElements() {
        // 查找保存按钮
        this.saveButton = document.querySelector('#reviewModal .btn-primary[onclick*="saveReview"]') ||
                         document.querySelector('#reviewModal .modal-footer .btn-primary');
        
        if (this.saveButton) {
            // 移除原有的onclick事件，使用我们的保存方法
            this.saveButton.removeAttribute('onclick');
            this.saveButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.saveReview();
            });
        }
    }

    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        if (!this.form) return;

        // 监听表单变化
        const formElements = this.form.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            // 根据元素类型选择合适的事件
            const events = this.getElementEvents(element);
            events.forEach(event => {
                element.addEventListener(event, () => {
                    if (this.debouncedDetectChanges) {
                        this.debouncedDetectChanges();
                    } else {
                        this.detectChanges();
                    }
                });
            });
        });

        // 监听复选框变化（评分项）
        const checkboxes = this.form.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.detectChanges();
            });
        });

        // 监听模态框显示事件，重置状态
        const modal = document.getElementById('reviewModal');
        if (modal) {
            modal.addEventListener('shown.bs.modal', () => {
                this.resetSaveState();
                this.captureOriginalFormData();
            });
        }
    }

    /**
     * 获取元素应该监听的事件类型
     */
    getElementEvents(element) {
        const tagName = element.tagName.toLowerCase();
        const type = element.type?.toLowerCase();

        if (tagName === 'select') {
            return ['change'];
        } else if (type === 'checkbox' || type === 'radio') {
            return ['change'];
        } else if (tagName === 'textarea' || type === 'text' || type === 'number' || type === 'date') {
            return ['input', 'change'];
        }
        
        return ['change'];
    }

    /**
     * 检测表单变化
     */
    detectChanges() {
        if (this.isSaving) return; // 保存过程中不检测变化

        const currentFormData = this.getCurrentFormData();
        const hasChanges = this.compareFormData(this.originalFormData, currentFormData);
        
        if (hasChanges !== this.hasUnsavedChanges) {
            this.hasUnsavedChanges = hasChanges;
            this.updateSaveButtonState();
            this.updateSaveStatusIndicator();
            
            // 如果启用了自动保存且有变化，重置自动保存计时器
            if (this.isAutoSaveEnabled && hasChanges) {
                this.resetAutoSaveTimer();
            }
        }
    }

    /**
     * 获取当前表单数据
     */
    getCurrentFormData() {
        const formData = {};
        
        if (!this.form) return formData;

        // 获取所有表单字段
        const elements = this.form.querySelectorAll('input, select, textarea');
        elements.forEach(element => {
            const name = element.name || element.id;
            if (!name) return;

            if (element.type === 'checkbox') {
                formData[name] = element.checked;
            } else if (element.type === 'radio') {
                if (element.checked) {
                    formData[name] = element.value;
                }
            } else {
                formData[name] = element.value;
            }
        });

        return formData;
    }

    /**
     * 比较表单数据是否有变化
     */
    compareFormData(original, current) {
        const originalKeys = Object.keys(original);
        const currentKeys = Object.keys(current);
        
        // 检查键的数量是否相同
        if (originalKeys.length !== currentKeys.length) {
            return true;
        }
        
        // 检查每个键的值是否相同
        for (const key of originalKeys) {
            if (original[key] !== current[key]) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * 捕获原始表单数据
     */
    captureOriginalFormData() {
        this.originalFormData = this.getCurrentFormData();
        this.hasUnsavedChanges = false;
        this.updateSaveButtonState();
        this.updateSaveStatusIndicator();
    }

    /**
     * 更新保存按钮状态
     */
    updateSaveButtonState() {
        if (!this.saveButton) return;

        if (this.isSaving) {
            this.saveButton.disabled = true;
            this.saveButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中...';
        } else if (this.hasUnsavedChanges) {
            this.saveButton.disabled = false;
            this.saveButton.innerHTML = '保存复盘';
            this.saveButton.classList.remove('btn-outline-primary');
            this.saveButton.classList.add('btn-primary');
        } else {
            this.saveButton.disabled = true;
            this.saveButton.innerHTML = '已保存';
            this.saveButton.classList.remove('btn-primary');
            this.saveButton.classList.add('btn-outline-primary');
        }
    }

    /**
     * 创建保存状态指示器
     */
    createSaveStatusIndicator() {
        // 在模态框标题旁边添加状态指示器
        const modalHeader = document.querySelector('#reviewModal .modal-header');
        if (!modalHeader) return;

        // 检查是否已存在指示器
        let indicator = modalHeader.querySelector('.save-status-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'save-status-indicator ms-auto me-2';
            indicator.innerHTML = '<small class="text-muted">已保存</small>';
            
            // 插入到关闭按钮之前
            const closeButton = modalHeader.querySelector('.btn-close');
            if (closeButton) {
                modalHeader.insertBefore(indicator, closeButton);
            } else {
                modalHeader.appendChild(indicator);
            }
        }
        
        this.saveStatusIndicator = indicator;
    }

    /**
     * 更新保存状态指示器
     */
    updateSaveStatusIndicator() {
        if (!this.saveStatusIndicator) return;

        if (this.isSaving) {
            this.saveStatusIndicator.innerHTML = `
                <small class="text-primary">
                    <span class="spinner-border spinner-border-sm me-1" style="width: 12px; height: 12px;"></span>
                    保存中...
                </small>
            `;
        } else if (this.hasUnsavedChanges) {
            this.saveStatusIndicator.innerHTML = '<small class="text-warning">有未保存的更改</small>';
        } else {
            this.saveStatusIndicator.innerHTML = '<small class="text-success">已保存</small>';
        }
    }

    /**
     * 保存复盘数据 - 增强版本，包含防抖机制和性能优化
     */
    async saveReview() {
        // 防抖机制：如果正在保存或没有未保存的更改，直接返回
        if (this.isSaving || !this.hasUnsavedChanges) {
            console.log('🚫 保存被跳过:', this.isSaving ? '正在保存中' : '没有未保存的更改');
            return;
        }

        // 防止重复提交的防抖检查
        const now = Date.now();
        if (this.lastSaveAttempt && (now - this.lastSaveAttempt) < 1000) {
            console.log('🚫 保存被防抖机制阻止，距离上次尝试时间过短');
            return;
        }
        this.lastSaveAttempt = now;

        console.log('💾 开始保存复盘数据');
        const saveStartTime = performance.now();
        
        this.isSaving = true;
        this.updateSaveButtonState();
        this.updateSaveStatusIndicator();

        // 显示保存进度
        this.showSaveProgress(0, '准备保存数据...');

        try {
            // 步骤1: 收集表单数据 (20%)
            this.showSaveProgress(20, '收集表单数据...');
            const reviewData = this.collectReviewData();
            
            // 步骤2: 验证数据 (40%)
            this.showSaveProgress(40, '验证数据...');
            const validation = this.validateReviewData(reviewData);
            if (!validation.isValid) {
                throw new Error(validation.message);
            }

            // 步骤3: 准备API请求 (60%)
            this.showSaveProgress(60, '准备发送请求...');
            const reviewId = document.getElementById('review-id')?.value || null;

            // 步骤4: 发送API请求 (80%)
            this.showSaveProgress(80, '保存到服务器...');
            const response = await apiClient.saveReview(reviewData, reviewId);

            if (response.success) {
                // 步骤5: 处理成功响应 (100%)
                this.showSaveProgress(100, '保存成功！');
                this.handleSaveSuccess(response);
            } else {
                throw new Error(response.error?.message || '保存失败');
            }

        } catch (error) {
            console.error('保存复盘失败:', error);
            this.hideSaveProgress();
            this.handleSaveError(error);
        } finally {
            const saveEndTime = performance.now();
            const saveDuration = (saveEndTime - saveStartTime).toFixed(2);
            console.log(`💾 保存操作完成，耗时: ${saveDuration}ms`);
            
            this.isSaving = false;
            this.updateSaveButtonState();
            this.updateSaveStatusIndicator();
            
            // 延迟隐藏进度条，让用户看到完成状态
            setTimeout(() => {
                this.hideSaveProgress();
            }, 1000);
        }
    }

    /**
     * 收集复盘数据
     */
    collectReviewData() {
        const data = {
            stock_code: document.getElementById('review-stock-code')?.value || '',
            review_date: document.getElementById('review-date')?.value || '',
            holding_days: parseInt(document.getElementById('holding-days')?.value) || 0,
            current_price: parseFloat(document.getElementById('current-price-input')?.value) || null,
            floating_profit_ratio: null, // 将在后端计算
            buy_price: null, // 将从交易记录获取
            price_up_score: document.getElementById('price-up-score')?.checked ? 1 : 0,
            bbi_score: document.getElementById('bbi-score')?.checked ? 1 : 0,
            volume_score: document.getElementById('volume-score')?.checked ? 1 : 0,
            trend_score: document.getElementById('trend-score')?.checked ? 1 : 0,
            j_score: document.getElementById('j-score')?.checked ? 1 : 0,
            analysis: document.getElementById('analysis')?.value || '',
            decision: document.getElementById('decision')?.value || '',
            reason: document.getElementById('reason')?.value || ''
        };

        // 计算总分
        data.total_score = data.price_up_score + data.bbi_score + data.volume_score + 
                          data.trend_score + data.j_score;

        return data;
    }

    /**
     * 验证复盘数据
     */
    validateReviewData(data) {
        const errors = [];

        if (!data.stock_code) {
            errors.push('股票代码不能为空');
        }

        if (!data.review_date) {
            errors.push('复盘日期不能为空');
        }

        if (!data.holding_days || data.holding_days < 1) {
            errors.push('持仓天数必须大于0');
        }

        if (!data.decision) {
            errors.push('请选择决策结果');
        }

        if (!data.reason.trim()) {
            errors.push('决策理由不能为空');
        }

        if (data.current_price !== null && (data.current_price <= 0 || data.current_price > 9999.99)) {
            errors.push('当前价格必须在0.01-9999.99之间');
        }

        return {
            isValid: errors.length === 0,
            message: errors.join('；'),
            errors: errors
        };
    }

    /**
     * 处理保存成功 - 增强版本，包含性能指标和用户体验优化
     */
    handleSaveSuccess(response) {
        console.log('✅ 保存成功处理开始');
        
        // 更新性能指标
        this.performanceMetrics.successfulSaves++;
        const saveTime = performance.now() - this.lastSaveAttempt;
        this.performanceMetrics.totalSaveTime += saveTime;
        this.performanceMetrics.averageSaveTime = this.performanceMetrics.totalSaveTime / this.performanceMetrics.successfulSaves;
        
        console.log('📊 保存性能指标:', {
            saveTime: `${saveTime.toFixed(2)}ms`,
            averageTime: `${this.performanceMetrics.averageSaveTime.toFixed(2)}ms`,
            successRate: `${((this.performanceMetrics.successfulSaves / this.performanceMetrics.saveAttempts) * 100).toFixed(1)}%`
        });

        // 更新原始数据，标记为已保存
        this.captureOriginalFormData();
        
        // 显示成功消息，根据保存时间选择不同的消息
        let successMessage = '复盘保存成功';
        if (saveTime < 1000) {
            successMessage += ' ⚡';
        } else if (saveTime > 3000) {
            successMessage += ' (网络较慢)';
        }
        
        this.showSaveMessage(successMessage, 'success', {
            position: 'toast',
            duration: 2000
        });
        
        // 如果有复盘ID，更新隐藏字段
        if (response.data?.id) {
            const reviewIdField = document.getElementById('review-id');
            if (reviewIdField) {
                reviewIdField.value = response.data.id;
                console.log('🆔 更新复盘ID:', response.data.id);
            }
        }

        // 触发自定义事件，通知其他组件
        document.dispatchEvent(new CustomEvent('reviewSaved', {
            detail: { 
                reviewData: response.data,
                isNew: !document.getElementById('review-id')?.value,
                saveTime: saveTime,
                performanceMetrics: { ...this.performanceMetrics }
            }
        }));

        // 优化的列表刷新 - 使用防抖避免频繁刷新
        if (typeof loadReviews === 'function') {
            if (!this.debouncedLoadReviews) {
                this.debouncedLoadReviews = debounce(() => {
                    console.log('🔄 刷新复盘列表');
                    loadReviews();
                }, 300);
            }
            this.debouncedLoadReviews();
        }

        // 记录成功保存的用户行为分析
        this.trackSaveSuccess(response, saveTime);
        
        console.log('✅ 保存成功处理完成');
    }

    /**
     * 处理保存错误 - 增强版本，包含智能错误恢复和用户指导
     */
    handleSaveError(error) {
        console.error('❌ 保存错误处理开始:', error);
        
        // 更新性能指标
        this.performanceMetrics.saveAttempts++;
        const failureRate = ((this.performanceMetrics.saveAttempts - this.performanceMetrics.successfulSaves) / this.performanceMetrics.saveAttempts * 100).toFixed(1);
        
        console.log('📊 错误统计:', {
            totalAttempts: this.performanceMetrics.saveAttempts,
            failures: this.performanceMetrics.saveAttempts - this.performanceMetrics.successfulSaves,
            failureRate: `${failureRate}%`
        });

        // 智能错误分析和消息生成
        const errorAnalysis = this.analyzeError(error);
        let message = errorAnalysis.userMessage;
        let recoveryAction = errorAnalysis.recoveryAction;

        // 显示错误消息
        this.showSaveMessage(message, 'error', {
            position: 'toast',
            duration: 6000,
            dismissible: true
        });

        // 如果有恢复建议，显示内联提示
        if (recoveryAction) {
            setTimeout(() => {
                this.showSaveMessage(recoveryAction, 'warning', {
                    position: 'inline',
                    duration: 8000
                });
            }, 1000);
        }

        // 自动重试机制（仅对网络错误）
        if (errorAnalysis.canRetry && !this.autoRetryAttempted) {
            this.scheduleAutoRetry(errorAnalysis.retryDelay);
        }

        // 触发自定义事件
        document.dispatchEvent(new CustomEvent('reviewSaveError', {
            detail: { 
                error: error,
                errorAnalysis: errorAnalysis,
                performanceMetrics: { ...this.performanceMetrics }
            }
        }));

        // 记录错误用于分析
        this.trackSaveError(error, errorAnalysis);
        
        console.error('❌ 保存错误处理完成');
    }

    /**
     * 分析错误类型并生成用户友好的消息和恢复建议
     */
    analyzeError(error) {
        const analysis = {
            type: 'unknown',
            userMessage: '保存失败，请重试',
            recoveryAction: null,
            canRetry: false,
            retryDelay: 2000
        };

        const errorMessage = error.message || error.toString() || '';
        const errorLower = errorMessage.toLowerCase();

        // 网络错误
        if (errorLower.includes('network') || errorLower.includes('fetch') || 
            errorLower.includes('timeout') || error.name === 'NetworkError') {
            analysis.type = 'network';
            analysis.userMessage = '网络连接异常，保存失败';
            analysis.recoveryAction = '请检查网络连接，系统将自动重试';
            analysis.canRetry = true;
            analysis.retryDelay = 3000;
        }
        // 验证错误
        else if (errorLower.includes('validation') || errorLower.includes('invalid') || 
                 errorLower.includes('required') || errorLower.includes('格式')) {
            analysis.type = 'validation';
            analysis.userMessage = '数据验证失败: ' + errorMessage;
            analysis.recoveryAction = '请检查表单中标红的字段并修正';
            analysis.canRetry = false;
        }
        // 权限错误
        else if (errorLower.includes('unauthorized') || errorLower.includes('forbidden') || 
                 errorLower.includes('权限') || error.status === 401 || error.status === 403) {
            analysis.type = 'permission';
            analysis.userMessage = '权限不足，无法保存';
            analysis.recoveryAction = '请刷新页面重新登录';
            analysis.canRetry = false;
        }
        // 服务器错误
        else if (errorLower.includes('server') || errorLower.includes('internal') || 
                 (error.status && error.status >= 500)) {
            analysis.type = 'server';
            analysis.userMessage = '服务器暂时无法处理请求';
            analysis.recoveryAction = '请稍后重试，或联系技术支持';
            analysis.canRetry = true;
            analysis.retryDelay = 5000;
        }
        // 数据冲突
        else if (errorLower.includes('conflict') || errorLower.includes('duplicate') || 
                 errorLower.includes('已存在')) {
            analysis.type = 'conflict';
            analysis.userMessage = '数据冲突: ' + errorMessage;
            analysis.recoveryAction = '请刷新页面获取最新数据';
            analysis.canRetry = false;
        }
        // 超时错误
        else if (errorLower.includes('timeout') || errorLower.includes('超时')) {
            analysis.type = 'timeout';
            analysis.userMessage = '请求超时，保存失败';
            analysis.recoveryAction = '网络较慢，请稍后重试';
            analysis.canRetry = true;
            analysis.retryDelay = 4000;
        }

        return analysis;
    }

    /**
     * 安排自动重试
     */
    scheduleAutoRetry(delay = 2000) {
        console.log(`🔄 安排自动重试，延迟 ${delay}ms`);
        
        this.autoRetryAttempted = true;
        
        // 显示重试倒计时
        let countdown = Math.ceil(delay / 1000);
        const countdownInterval = setInterval(() => {
            this.showSaveMessage(`自动重试中... ${countdown}s`, 'info', {
                position: 'inline',
                duration: 0,
                dismissible: false
            });
            countdown--;
            
            if (countdown <= 0) {
                clearInterval(countdownInterval);
            }
        }, 1000);

        setTimeout(() => {
            clearInterval(countdownInterval);
            console.log('🔄 执行自动重试');
            
            // 重置重试标志
            this.autoRetryAttempted = false;
            
            // 执行重试
            this.saveReview();
        }, delay);
    }

    /**
     * 记录保存成功的用户行为分析
     */
    trackSaveSuccess(response, saveTime) {
        const trackingData = {
            event: 'review_save_success',
            timestamp: new Date().toISOString(),
            saveTime: saveTime,
            dataSize: JSON.stringify(response.data || {}).length,
            formFields: this.getFormFieldsCount(),
            userAgent: navigator.userAgent,
            performanceMetrics: { ...this.performanceMetrics }
        };

        // 存储到本地用于分析
        this.storeAnalyticsData('save_success', trackingData);
        
        console.log('📈 保存成功分析数据已记录');
    }

    /**
     * 记录保存错误的用户行为分析
     */
    trackSaveError(error, errorAnalysis) {
        const trackingData = {
            event: 'review_save_error',
            timestamp: new Date().toISOString(),
            errorType: errorAnalysis.type,
            errorMessage: error.message || error.toString(),
            canRetry: errorAnalysis.canRetry,
            formFields: this.getFormFieldsCount(),
            userAgent: navigator.userAgent,
            performanceMetrics: { ...this.performanceMetrics }
        };

        // 存储到本地用于分析
        this.storeAnalyticsData('save_error', trackingData);
        
        console.log('📈 保存错误分析数据已记录');
    }

    /**
     * 获取表单字段数量
     */
    getFormFieldsCount() {
        if (!this.form) return 0;
        
        const fields = this.form.querySelectorAll('input, select, textarea');
        const filledFields = Array.from(fields).filter(field => {
            if (field.type === 'checkbox' || field.type === 'radio') {
                return field.checked;
            }
            return field.value && field.value.trim() !== '';
        });

        return {
            total: fields.length,
            filled: filledFields.length,
            fillRate: ((filledFields.length / fields.length) * 100).toFixed(1) + '%'
        };
    }

    /**
     * 存储分析数据到本地存储
     */
    storeAnalyticsData(category, data) {
        try {
            const storageKey = `review_analytics_${category}`;
            const existingData = JSON.parse(localStorage.getItem(storageKey) || '[]');
            
            existingData.push(data);
            
            // 只保留最近100条记录
            if (existingData.length > 100) {
                existingData.splice(0, existingData.length - 100);
            }
            
            localStorage.setItem(storageKey, JSON.stringify(existingData));
        } catch (error) {
            console.warn('⚠️ 无法存储分析数据:', error);
        }
    }

    /**
     * 显示保存进度
     */
    showSaveProgress(progress, message = '') {
        if (!this.saveProgressContainer) {
            this.createSaveProgressContainer();
        }

        const progressBar = this.saveProgressContainer.querySelector('.progress-bar');
        const progressText = this.saveProgressContainer.querySelector('.progress-text');
        const progressPercentage = this.saveProgressContainer.querySelector('.progress-percentage');

        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }

        if (progressText && message) {
            progressText.textContent = message;
        }

        if (progressPercentage) {
            progressPercentage.textContent = `${progress}%`;
        }

        // 显示进度容器
        this.saveProgressContainer.style.display = 'block';
        
        // 添加动画效果
        if (progress === 100) {
            progressBar.classList.add('bg-success');
            setTimeout(() => {
                progressBar.classList.remove('bg-success');
            }, 1000);
        }
    }

    /**
     * 隐藏保存进度
     */
    hideSaveProgress() {
        if (this.saveProgressContainer) {
            this.saveProgressContainer.style.display = 'none';
        }
    }

    /**
     * 创建保存进度容器
     */
    createSaveProgressContainer() {
        // 查找模态框footer
        const modalFooter = document.querySelector('#reviewModal .modal-footer');
        if (!modalFooter) return;

        // 创建进度容器
        this.saveProgressContainer = document.createElement('div');
        this.saveProgressContainer.className = 'save-progress-container mb-2';
        this.saveProgressContainer.style.display = 'none';
        this.saveProgressContainer.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-1">
                <small class="progress-text text-muted">准备保存...</small>
                <small class="progress-percentage text-muted">0%</small>
            </div>
            <div class="progress" style="height: 4px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" 
                     style="width: 0%" 
                     aria-valuenow="0" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                </div>
            </div>
        `;

        // 插入到footer的开头
        modalFooter.insertBefore(this.saveProgressContainer, modalFooter.firstChild);
    }

    /**
     * 显示保存消息 - 增强版本，支持不同位置和动画
     */
    showSaveMessage(message, type = 'info', options = {}) {
        const defaultOptions = {
            position: 'toast', // 'toast' | 'modal' | 'inline'
            duration: type === 'error' ? 5000 : 3000,
            dismissible: true,
            animation: true
        };
        
        const config = { ...defaultOptions, ...options };

        // 使用统一消息系统（如果存在）
        if (typeof showMessage === 'function') {
            showMessage(message, type, config);
            return;
        }

        // 根据位置选择不同的显示方式
        switch (config.position) {
            case 'modal':
                this.showModalMessage(message, type, config);
                break;
            case 'inline':
                this.showInlineMessage(message, type, config);
                break;
            default:
                this.showToastMessage(message, type, config);
        }
    }

    /**
     * 显示Toast消息
     */
    showToastMessage(message, type, config) {
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'error' ? 'alert-danger' : 
                          type === 'warning' ? 'alert-warning' : 'alert-info';
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-triangle' : 
                    type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${alertClass} alert-dismissible position-fixed ${config.animation ? 'fade show' : ''}`;
        alertDiv.style.cssText = `
            top: 20px; 
            right: 20px; 
            z-index: 9999; 
            min-width: 300px;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: none;
        `;
        
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${icon} me-2"></i>
                <div class="flex-grow-1">${message}</div>
                ${config.dismissible ? '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' : ''}
            </div>
        `;
        
        document.body.appendChild(alertDiv);
        
        // 自动移除
        if (config.duration > 0) {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    if (config.animation) {
                        alertDiv.classList.remove('show');
                        setTimeout(() => {
                            if (alertDiv.parentNode) {
                                alertDiv.parentNode.removeChild(alertDiv);
                            }
                        }, 150);
                    } else {
                        alertDiv.parentNode.removeChild(alertDiv);
                    }
                }
            }, config.duration);
        }
    }

    /**
     * 显示模态框内消息
     */
    showModalMessage(message, type, config) {
        const modalBody = document.querySelector('#reviewModal .modal-body');
        if (!modalBody) return;

        // 移除现有的消息
        const existingAlert = modalBody.querySelector('.save-message-alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'error' ? 'alert-danger' : 
                          type === 'warning' ? 'alert-warning' : 'alert-info';

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${alertClass} save-message-alert ${config.animation ? 'fade show' : ''}`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
            ${config.dismissible ? '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' : ''}
        `;

        modalBody.insertBefore(alertDiv, modalBody.firstChild);

        // 自动移除
        if (config.duration > 0) {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, config.duration);
        }
    }

    /**
     * 显示内联消息
     */
    showInlineMessage(message, type, config) {
        if (!this.saveStatusIndicator) return;

        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-triangle' : 'info-circle';
        
        const colorClass = type === 'success' ? 'text-success' : 
                          type === 'error' ? 'text-danger' : 
                          type === 'warning' ? 'text-warning' : 'text-info';

        this.saveStatusIndicator.innerHTML = `
            <small class="${colorClass}">
                <i class="fas fa-${icon} me-1"></i>
                ${message}
            </small>
        `;

        // 自动恢复状态
        if (config.duration > 0) {
            setTimeout(() => {
                this.updateSaveStatusIndicator();
            }, config.duration);
        }
    }

    /**
     * 启用自动保存
     */
    enableAutoSave() {
        this.isAutoSaveEnabled = true;
        this.resetAutoSaveTimer();
        console.log('自动保存已启用');
    }

    /**
     * 禁用自动保存
     */
    disableAutoSave() {
        this.isAutoSaveEnabled = false;
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
        console.log('自动保存已禁用');
    }

    /**
     * 重置自动保存计时器
     */
    resetAutoSaveTimer() {
        if (!this.isAutoSaveEnabled) return;

        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }

        this.autoSaveTimer = setTimeout(() => {
            if (this.hasUnsavedChanges && !this.isSaving) {
                console.log('执行自动保存...');
                this.saveReview();
            }
        }, this.autoSaveInterval);
    }

    /**
     * 设置离开页面警告
     */
    setupBeforeUnloadWarning() {
        console.log('🔧 设置离开页面警告机制');
        
        // 保存beforeunload处理器的引用，以便后续移除
        this.beforeUnloadHandler = (e) => {
            if (this.hasUnsavedChanges) {
                const message = '您有未保存的复盘数据，确定要离开吗？';
                console.log('⚠️ 检测到未保存更改，显示离开页面警告');
                
                // 现代浏览器的标准做法
                e.preventDefault();
                e.returnValue = message;
                return message;
            }
        };
        
        // 绑定beforeunload事件
        window.addEventListener('beforeunload', this.beforeUnloadHandler);
        console.log('✅ beforeunload警告事件已绑定');

        // 监听模态框关闭事件 - 增强版本
        this.setupModalCloseWarning();
        
        // 监听其他可能的页面离开事件
        this.setupAdditionalWarnings();
    }

    /**
     * 设置模态框关闭警告
     */
    setupModalCloseWarning() {
        const modal = document.getElementById('reviewModal');
        if (!modal) {
            console.warn('⚠️ 复盘模态框未找到，无法设置关闭警告');
            return;
        }

        // 保存模态框关闭处理器的引用
        this.modalCloseHandler = (e) => {
            if (this.hasUnsavedChanges) {
                console.log('⚠️ 检测到未保存更改，显示模态框关闭确认');
                
                // 创建更友好的确认对话框
                const confirmed = this.showModalCloseConfirmation();
                if (!confirmed) {
                    console.log('🚫 用户取消关闭模态框');
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                } else {
                    console.log('✅ 用户确认关闭模态框');
                    // 用户确认关闭，清理未保存状态
                    this.resetSaveState();
                }
            }
        };

        // 绑定模态框关闭事件
        modal.addEventListener('hide.bs.modal', this.modalCloseHandler);
        console.log('✅ 模态框关闭警告事件已绑定');

        // 监听模态框显示事件，重置状态
        modal.addEventListener('shown.bs.modal', () => {
            console.log('📋 模态框已显示，重置保存状态');
            this.resetSaveState();
            this.captureOriginalFormData();
        });
    }

    /**
     * 显示模态框关闭确认对话框
     */
    showModalCloseConfirmation() {
        // 获取未保存的字段信息
        const unsavedFields = this.getUnsavedFieldsInfo();
        
        let message = '您有未保存的复盘数据，确定要关闭吗？';
        if (unsavedFields.length > 0) {
            message += '\n\n未保存的更改包括：\n' + unsavedFields.join('\n');
        }
        
        // 使用自定义确认对话框（如果可用）或标准confirm
        if (typeof this.showCustomConfirmDialog === 'function') {
            return this.showCustomConfirmDialog(message, '未保存的更改');
        } else {
            return confirm(message);
        }
    }

    /**
     * 获取未保存字段的信息
     */
    getUnsavedFieldsInfo() {
        const unsavedFields = [];
        const currentData = this.getCurrentFormData();
        
        // 比较当前数据和原始数据，找出变化的字段
        for (const [key, value] of Object.entries(currentData)) {
            if (this.originalFormData[key] !== value) {
                const fieldElement = document.querySelector(`[name="${key}"], [id="${key}"]`);
                if (fieldElement) {
                    const label = this.getFieldLabel(fieldElement);
                    unsavedFields.push(`• ${label || key}: ${this.formatFieldValue(value)}`);
                }
            }
        }
        
        return unsavedFields;
    }

    /**
     * 获取字段标签
     */
    getFieldLabel(element) {
        // 尝试通过label标签获取
        const labelElement = document.querySelector(`label[for="${element.id}"]`);
        if (labelElement) {
            return labelElement.textContent.trim();
        }
        
        // 尝试通过前面的label获取
        const prevLabel = element.previousElementSibling;
        if (prevLabel && prevLabel.tagName === 'LABEL') {
            return prevLabel.textContent.trim();
        }
        
        // 尝试通过父元素中的label获取
        const parentLabel = element.closest('.form-group, .mb-3')?.querySelector('label');
        if (parentLabel) {
            return parentLabel.textContent.trim();
        }
        
        // 使用placeholder或name作为fallback
        return element.placeholder || element.name || element.id;
    }

    /**
     * 格式化字段值用于显示
     */
    formatFieldValue(value) {
        if (typeof value === 'string') {
            return value.length > 20 ? value.substring(0, 20) + '...' : value;
        } else if (typeof value === 'boolean') {
            return value ? '已选中' : '未选中';
        } else {
            return String(value);
        }
    }

    /**
     * 设置额外的警告机制
     */
    setupAdditionalWarnings() {
        // 监听浏览器后退按钮
        window.addEventListener('popstate', (e) => {
            if (this.hasUnsavedChanges) {
                console.log('⚠️ 检测到浏览器后退，有未保存更改');
                // 注意：现代浏览器限制了对popstate的阻止，这里主要用于日志记录
            }
        });

        // 监听页面可见性变化（用户切换标签页）
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.hasUnsavedChanges) {
                console.log('⚠️ 页面变为不可见，有未保存更改');
                // 可以在这里触发自动保存或其他操作
                if (this.isAutoSaveEnabled) {
                    console.log('🔄 触发自动保存');
                    this.saveReview();
                }
            }
        });

        console.log('✅ 额外警告机制已设置');
    }

    /**
     * 验证警告机制是否正常工作
     */
    verifyWarningMechanisms() {
        console.log('🔍 验证警告机制');
        
        const results = {
            beforeUnloadBound: false,
            modalCloseBound: false,
            hasUnsavedChangesDetection: false,
            warningMessageAccuracy: false
        };

        // 检查beforeunload事件是否绑定
        try {
            const listeners = getEventListeners ? getEventListeners(window) : null;
            results.beforeUnloadBound = listeners && listeners.beforeunload && listeners.beforeunload.length > 0;
        } catch (e) {
            // 在生产环境中getEventListeners可能不可用
            results.beforeUnloadBound = typeof this.beforeUnloadHandler === 'function';
        }

        // 检查模态框关闭事件是否绑定
        const modal = document.getElementById('reviewModal');
        if (modal) {
            try {
                const listeners = getEventListeners ? getEventListeners(modal) : null;
                results.modalCloseBound = listeners && listeners['hide.bs.modal'] && listeners['hide.bs.modal'].length > 0;
            } catch (e) {
                results.modalCloseBound = typeof this.modalCloseHandler === 'function';
            }
        }

        // 检查未保存更改检测
        results.hasUnsavedChangesDetection = typeof this.hasUnsavedChanges === 'boolean';

        // 检查警告消息准确性
        results.warningMessageAccuracy = typeof this.getUnsavedFieldsInfo === 'function';

        console.log('📊 警告机制验证结果:', results);
        return results;
    }

    /**
     * 测试警告机制
     */
    testWarningMechanisms() {
        console.log('🧪 测试警告机制');
        
        // 模拟表单变化
        const testField = document.getElementById('reason') || document.getElementById('analysis');
        if (testField) {
            const originalValue = testField.value;
            testField.value = '测试未保存更改 - ' + Date.now();
            testField.dispatchEvent(new Event('input'));
            
            setTimeout(() => {
                console.log('📋 测试结果:');
                console.log('- 有未保存更改:', this.hasUnsavedChanges);
                console.log('- 未保存字段信息:', this.getUnsavedFieldsInfo());
                
                // 恢复原值
                testField.value = originalValue;
                testField.dispatchEvent(new Event('input'));
            }, 500);
        } else {
            console.warn('⚠️ 未找到测试字段');
        }
    }

    /**
     * 重置保存状态
     */
    resetSaveState() {
        this.hasUnsavedChanges = false;
        this.isSaving = false;
        this.originalFormData = {};
        
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
        
        this.updateSaveButtonState();
        this.updateSaveStatusIndicator();
    }

    /**
     * 手动标记为已保存（用于外部调用）
     */
    markAsSaved() {
        this.captureOriginalFormData();
    }

    /**
     * 检查是否有未保存的更改
     */
    hasUnsavedData() {
        return this.hasUnsavedChanges;
    }

    /**
     * 强制保存（忽略验证）
     */
    async forceSave() {
        if (this.isSaving) return;
        
        const originalValidation = this.validateReviewData;
        this.validateReviewData = () => ({ isValid: true, message: '', errors: [] });
        
        try {
            await this.saveReview();
        } finally {
            this.validateReviewData = originalValidation;
        }
    }

    /**
     * 销毁管理器 - 增强版本，清理所有性能优化相关资源
     */
    destroy() {
        console.log('🧹 销毁ReviewSaveManager');
        
        // 清理定时器
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }

        if (this.cacheCleanupInterval) {
            clearInterval(this.cacheCleanupInterval);
            this.cacheCleanupInterval = null;
        }

        if (this.memoryCheckInterval) {
            clearInterval(this.memoryCheckInterval);
            this.memoryCheckInterval = null;
        }
        
        // 移除事件监听器
        if (this.beforeUnloadHandler) {
            window.removeEventListener('beforeunload', this.beforeUnloadHandler);
            this.beforeUnloadHandler = null;
        }
        
        if (this.modalCloseHandler) {
            const modal = document.getElementById('reviewModal');
            if (modal) {
                modal.removeEventListener('hide.bs.modal', this.modalCloseHandler);
            }
            this.modalCloseHandler = null;
        }

        // 清理网络监听器
        if (this.networkInfo && 'connection' in navigator) {
            try {
                navigator.connection.removeEventListener('change', this.adaptToNetworkConditions);
            } catch (error) {
                console.warn('清理网络监听器失败:', error);
            }
        }
        
        // 清理缓存和队列
        if (this.formDataCache) {
            this.formDataCache.clear();
            this.formDataCache = null;
        }

        if (this.requestCache) {
            this.requestCache.clear();
            this.requestCache = null;
        }

        if (this.pendingRequests) {
            this.pendingRequests.clear();
            this.pendingRequests = null;
        }

        if (this.domUpdateQueue) {
            this.domUpdateQueue.length = 0;
            this.domUpdateQueue = null;
        }

        // 清理进度容器
        if (this.saveProgressContainer && this.saveProgressContainer.parentNode) {
            this.saveProgressContainer.parentNode.removeChild(this.saveProgressContainer);
            this.saveProgressContainer = null;
        }
        
        // 清理其他引用
        this.form = null;
        this.saveButton = null;
        this.saveStatusIndicator = null;
        this.originalFormData = {};
        this.debouncedDetectChanges = null;
        this.throttledUpdateStatus = null;
        this.debouncedSave = null;
        this.debouncedLoadReviews = null;
        this.batchValidator = null;
        
        // 重置性能指标
        this.performanceMetrics = {
            saveAttempts: 0,
            successfulSaves: 0,
            averageSaveTime: 0,
            totalSaveTime: 0
        };
        
        console.log('✅ ReviewSaveManager 已完全销毁');
    }

    /**
     * 获取性能报告
     */
    getPerformanceReport() {
        const report = {
            metrics: { ...this.performanceMetrics },
            cacheStats: {
                formDataCacheSize: this.formDataCache ? this.formDataCache.size : 0,
                requestCacheSize: this.requestCache ? this.requestCache.size : 0
            },
            networkInfo: this.networkInfo ? {
                effectiveType: this.networkInfo.effectiveType,
                downlink: this.networkInfo.downlink,
                rtt: this.networkInfo.rtt
            } : null,
            memoryInfo: 'memory' in performance ? {
                used: (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(2) + 'MB',
                total: (performance.memory.totalJSHeapSize / 1024 / 1024).toFixed(2) + 'MB',
                limit: (performance.memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2) + 'MB'
            } : null
        };

        console.table(report.metrics);
        return report;
    }

    /**
     * 导出性能数据
     */
    exportPerformanceData() {
        const data = {
            timestamp: new Date().toISOString(),
            performanceReport: this.getPerformanceReport(),
            analyticsData: {
                saveSuccess: JSON.parse(localStorage.getItem('review_analytics_save_success') || '[]'),
                saveError: JSON.parse(localStorage.getItem('review_analytics_save_error') || '[]')
            }
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `review-save-performance-${new Date().toISOString().slice(0, 19)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('📊 性能数据已导出');
    }
}

// 全局实例
let reviewSaveManager = null;

// 初始化函数
function initializeReviewSaveManager() {
    if (reviewSaveManager) {
        reviewSaveManager.destroy();
    }
    
    reviewSaveManager = new ReviewSaveManager();
    
    // 监听模态框显示事件，确保管理器正确初始化
    const modal = document.getElementById('reviewModal');
    if (modal) {
        modal.addEventListener('shown.bs.modal', () => {
            if (!reviewSaveManager || !reviewSaveManager.form) {
                reviewSaveManager = new ReviewSaveManager();
            }
        });
    }
    
    return reviewSaveManager;
}

// DOM加载完成后自动初始化
document.addEventListener('DOMContentLoaded', () => {
    // 延迟初始化，确保其他脚本已加载
    setTimeout(() => {
        initializeReviewSaveManager();
    }, 100);
});

// 导出类和实例
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ReviewSaveManager, reviewSaveManager };
}