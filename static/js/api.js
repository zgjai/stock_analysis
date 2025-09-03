// API客户端封装
// API客户端类 - 使用条件声明避免重复
if (typeof window.ApiClient === 'undefined') {
    class ApiClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.retryConfig = {
            maxRetries: 2,
            retryDelay: 1000,
            retryCondition: (error) => {
                // 只对网络错误和5xx服务器错误进行重试
                return error.code === 'NETWORK_ERROR' || 
                       (error.code && error.code.startsWith('HTTP_5'));
            }
        };
        this.setupAxios();
    }

    setupAxios() {
        // 设置默认配置 - 缩短超时时间
        axios.defaults.timeout = 10000; // 10秒超时
        axios.defaults.headers.common['Content-Type'] = 'application/json';

        // 请求拦截器
        axios.interceptors.request.use(
            (config) => {
                // 添加请求时间戳
                config.metadata = { startTime: new Date() };
                console.log(`API请求开始: ${config.method?.toUpperCase()} ${config.url}`);
                return config;
            },
            (error) => {
                console.error('请求拦截器错误:', error);
                return Promise.reject(error);
            }
        );

        // 响应拦截器
        axios.interceptors.response.use(
            (response) => {
                // 计算请求耗时
                const endTime = new Date();
                const duration = endTime - response.config.metadata.startTime;
                console.log(`API请求成功: ${duration}ms - ${response.config.url}`);
                
                return response;
            },
            (error) => {
                console.error('API请求失败:', error.config?.url, error.message);
                
                // 不在拦截器中显示错误消息，让调用方处理
                // this.handleError(error);
                return Promise.reject(error);
            }
        );
    }

    async request(method, url, data = null, config = {}) {
        try {
            const fullUrl = url.startsWith('http') ? url : `${this.baseURL}${url}`;
            
            const requestConfig = {
                method: method.toLowerCase(),
                url: fullUrl,
                ...config
            };

            if (data) {
                if (method.toLowerCase() === 'get') {
                    requestConfig.params = data;
                } else {
                    requestConfig.data = data;
                }
            }

            const response = await axios(requestConfig);
            return response.data;
        } catch (error) {
            throw this.processError(error);
        }
    }

    // 交易记录相关API
    async getTrades(params = {}) {
        return this.request('GET', '/trades', params);
    }

    async createTrade(data) {
        return this.request('POST', '/trades', data);
    }

    async updateTrade(id, data) {
        return this.request('PUT', `/trades/${id}`, data);
    }

    async deleteTrade(id) {
        return this.request('DELETE', `/trades/${id}`);
    }

    async calculateRiskReward(data) {
        return this.request('POST', '/trades/calculate-risk-reward', data);
    }

    async correctTrade(id, correctedData, reason) {
        return this.request('POST', `/trades/${id}/correct`, {
            corrected_data: correctedData,
            reason: reason
        });
    }

    async getCorrectionHistory(id) {
        return this.request('GET', `/trades/${id}/history`);
    }

    async getTradeConfig() {
        return this.request('GET', '/trades/config');
    }

    async getBuyReasons() {
        return this.request('GET', '/trades/config/buy-reasons');
    }

    async getSellReasons() {
        return this.request('GET', '/trades/config/sell-reasons');
    }

    async setBuyReasons(reasons) {
        return this.request('PUT', '/trades/config/buy-reasons', { buy_reasons: reasons });
    }

    async setSellReasons(reasons) {
        return this.request('PUT', '/trades/config/sell-reasons', { sell_reasons: reasons });
    }

    // 分批止盈相关API
    async getProfitTargets(tradeId) {
        return this.request('GET', `/trades/${tradeId}/profit-targets`);
    }

    async setProfitTargets(tradeId, profitTargets) {
        return this.request('PUT', `/trades/${tradeId}/profit-targets`, { profit_targets: profitTargets });
    }

    async calculateBatchProfit(buyPrice, profitTargets) {
        return this.request('POST', '/trades/calculate-batch-profit', {
            buy_price: buyPrice,
            profit_targets: profitTargets
        });
    }

    async getTradeWithProfitTargets(tradeId) {
        return this.request('GET', `/trades/${tradeId}`);
    }

    // 复盘记录相关API
    async getReviews(params = {}) {
        return this.request('GET', '/reviews', params);
    }

    async createReview(data) {
        return this.request('POST', '/reviews', data);
    }

    async updateReview(id, data) {
        return this.request('PUT', `/reviews/${id}`, data);
    }

    async getHoldings() {
        return this.request('GET', '/holdings');
    }

    // Removed getHoldingAlerts method as holding alerts module has been removed

    // 持仓天数更新API - 需求1
    async updateHoldingDays(stockCode, holdingDays) {
        return this.requestWithRetry(
            'PUT', 
            `/holdings/${stockCode}/days`, 
            { holding_days: holdingDays },
            '持仓天数更新'
        );
    }

    // 浮盈计算API - 需求3
    async calculateFloatingProfit(stockCode, currentPrice) {
        return this.requestWithRetry(
            'POST', 
            '/reviews/calculate-floating-profit', 
            { stock_code: stockCode, current_price: currentPrice },
            '浮盈计算'
        );
    }

    // 扩展复盘保存方法以支持新字段 - 需求2
    async saveReview(reviewData, reviewId = null) {
        // 构建包含新字段的完整数据对象
        const completeData = {
            stock_code: reviewData.stock_code,
            review_date: reviewData.review_date,
            holding_days: reviewData.holding_days,
            current_price: reviewData.current_price,
            floating_profit_ratio: reviewData.floating_profit_ratio,
            buy_price: reviewData.buy_price,
            price_up_score: reviewData.price_up_score,
            bbi_score: reviewData.bbi_score,
            volume_score: reviewData.volume_score,
            trend_score: reviewData.trend_score,
            j_score: reviewData.j_score,
            analysis: reviewData.analysis,
            decision: reviewData.decision,
            reason: reviewData.reason,
            ...reviewData // 包含任何额外字段
        };

        const method = reviewId ? 'PUT' : 'POST';
        const url = reviewId ? `/reviews/${reviewId}` : '/reviews';
        
        return this.requestWithRetry(method, url, completeData, '复盘保存');
    }

    // 带重试机制的请求方法
    async requestWithRetry(method, url, data, operation = '操作') {
        let lastError = null;
        
        for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
            try {
                const response = await this.request(method, url, data);
                return response;
            } catch (error) {
                lastError = error;
                
                // 检查是否应该重试
                if (attempt < this.retryConfig.maxRetries && 
                    this.retryConfig.retryCondition(error)) {
                    
                    console.log(`${operation}失败，第${attempt + 1}次重试...`);
                    await this.delay(this.retryConfig.retryDelay * (attempt + 1));
                    continue;
                }
                
                // 不重试或已达到最大重试次数
                break;
            }
        }
        
        // 处理最终错误
        return this.handleReviewError(lastError, operation);
    }

    // 股票池相关API
    async getStockPool(params = {}) {
        return this.request('GET', '/stock-pool', params);
    }

    async addToStockPool(data) {
        return this.request('POST', '/stock-pool', data);
    }

    async updateStockPool(id, data) {
        return this.request('PUT', `/stock-pool/${id}`, data);
    }

    async removeFromStockPool(id) {
        return this.request('DELETE', `/stock-pool/${id}`);
    }

    // 案例管理相关API
    async getCases(params = {}) {
        return this.request('GET', '/cases', params);
    }

    async createCase(data) {
        // 处理文件上传
        if (data instanceof FormData) {
            return this.request('POST', '/cases', data, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
        }
        return this.request('POST', '/cases', data);
    }

    async updateCase(id, data) {
        return this.request('PUT', `/cases/${id}`, data);
    }

    async deleteCase(id) {
        return this.request('DELETE', `/cases/${id}`);
    }

    async getCaseById(id) {
        return this.request('GET', `/cases/${id}`);
    }

    async getCasesByStock(stockCode) {
        return this.request('GET', `/cases/by-stock/${stockCode}`);
    }

    async getCasesByTag(tag) {
        return this.request('GET', `/cases/by-tag/${tag}`);
    }

    async getAllTags() {
        return this.request('GET', '/cases/tags');
    }

    async getCaseStatistics() {
        return this.request('GET', '/cases/statistics');
    }

    async searchCases(searchData) {
        return this.request('POST', '/cases/search', searchData);
    }

    // 统计分析相关API
    async getAnalyticsOverview() {
        return this.request('GET', '/analytics/overview');
    }

    async getMonthlyAnalytics() {
        return this.request('GET', '/analytics/monthly');
    }

    async getProfitDistribution() {
        return this.request('GET', '/analytics/profit-distribution');
    }

    async exportAnalytics() {
        return this.request('GET', '/analytics/export');
    }

    async getExpectationComparison(params = {}) {
        return this.request('GET', '/analytics/expectation-comparison', params);
    }

    // 股票价格相关API
    async refreshPrices() {
        return this.request('POST', '/prices/refresh');
    }

    async getStockPrice(stockCode) {
        return this.request('GET', `/prices/${stockCode}`);
    }

    // 板块分析相关API
    async getSectorRanking(params = {}) {
        return this.request('GET', '/sectors/ranking', params);
    }

    async refreshSectorData() {
        return this.request('POST', '/sectors/refresh');
    }

    async getSectorHistory(params = {}) {
        return this.request('GET', '/sectors/history', params);
    }

    async getTopPerformingSectors(days, topK) {
        return this.request('GET', '/sectors/top-performers', { days, top_k: topK });
    }

    // 策略相关API
    async getStrategies() {
        return this.request('GET', '/strategies');
    }

    async createStrategy(data) {
        return this.request('POST', '/strategies', data);
    }

    async updateStrategy(id, data) {
        return this.request('PUT', `/strategies/${id}`, data);
    }

    async deleteStrategy(id) {
        return this.request('DELETE', `/strategies/${id}`);
    }

    async evaluateStrategies() {
        return this.request('POST', '/strategies/evaluate');
    }

    // 工具方法
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // 错误处理
    handleError(error) {
        let message = '请求失败';
        
        if (error.response) {
            // 服务器返回错误状态码
            const { status, data } = error.response;
            
            switch (status) {
                case 400:
                    message = data.error?.message || '请求参数错误';
                    break;
                case 401:
                    message = '未授权访问';
                    break;
                case 403:
                    message = '访问被拒绝';
                    break;
                case 404:
                    message = '请求的资源不存在';
                    break;
                case 422:
                    message = data.error?.message || '数据验证失败';
                    break;
                case 500:
                    message = '服务器内部错误';
                    break;
                default:
                    message = data.error?.message || `请求失败 (${status})`;
            }
        } else if (error.request) {
            // 网络错误
            message = '网络连接失败，请检查网络设置';
        } else {
            // 其他错误
            message = error.message || '未知错误';
        }

        // 显示错误消息
        if (typeof showMessage === 'function') {
            showMessage(message, 'error');
        } else {
            console.error('API Error:', message);
        }
    }

    processError(error) {
        // 处理并返回标准化的错误对象
        const processedError = {
            message: '请求失败',
            code: 'UNKNOWN_ERROR',
            details: null
        };

        if (error.response) {
            const { status, data } = error.response;
            processedError.code = `HTTP_${status}`;
            
            // 针对复盘相关API的特定错误处理
            if (status === 400 && data.error?.code === 'VALIDATION_ERROR') {
                processedError.code = 'VALIDATION_ERROR';
                processedError.message = data.error?.message || '数据验证失败，请检查输入';
            } else if (status === 404 && error.config?.url?.includes('/holdings/')) {
                processedError.code = 'HOLDING_NOT_FOUND';
                processedError.message = '未找到对应的持仓记录';
            } else if (status === 422 && error.config?.url?.includes('/reviews/')) {
                processedError.code = 'REVIEW_VALIDATION_ERROR';
                processedError.message = data.error?.message || '复盘数据验证失败';
            } else {
                processedError.message = data.error?.message || `HTTP错误 ${status}`;
            }
            
            processedError.details = data.error?.details || null;
        } else if (error.request) {
            processedError.code = 'NETWORK_ERROR';
            processedError.message = '网络连接失败';
        } else {
            processedError.message = error.message || '未知错误';
        }

        return processedError;
    }

    // 复盘相关错误处理辅助方法
    handleReviewError(error, operation = '操作') {
        const errorMap = {
            'VALIDATION_ERROR': '数据验证失败，请检查输入格式',
            'REVIEW_VALIDATION_ERROR': '复盘数据验证失败，请检查必填字段',
            'HOLDING_NOT_FOUND': '未找到对应的持仓记录',
            'NETWORK_ERROR': '网络连接失败，请重试',
            'HTTP_500': '服务器错误，请稍后重试',
            'HTTP_403': '没有权限执行此操作',
            'HTTP_401': '请先登录'
        };
        
        const message = errorMap[error.code] || error.message || `${operation}失败`;
        
        // 显示错误消息
        if (typeof showMessage === 'function') {
            showMessage(message, 'error');
        } else {
            console.error(`Review API Error [${operation}]:`, message);
        }
        
        return {
            success: false,
            error: {
                code: error.code,
                message: message,
                details: error.details
            }
        };
    }

    // 批量请求
    async batchRequest(requests) {
        try {
            const promises = requests.map(req => 
                this.request(req.method, req.url, req.data, req.config)
            );
            
            const results = await Promise.allSettled(promises);
            
            return results.map((result, index) => ({
                request: requests[index],
                success: result.status === 'fulfilled',
                data: result.status === 'fulfilled' ? result.value : null,
                error: result.status === 'rejected' ? result.reason : null
            }));
        } catch (error) {
            throw this.processError(error);
        }
    }

    // 文件上传
    async uploadFile(file, endpoint, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        // 添加额外数据
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        return this.request('POST', endpoint, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total
                );
                // 触发上传进度事件
                document.dispatchEvent(new CustomEvent('uploadProgress', {
                    detail: { percent: percentCompleted, file: file.name }
                }));
            }
        });
    }

    // 下载文件
    async downloadFile(url, filename) {
        try {
            const response = await this.request('GET', url, null, {
                responseType: 'blob'
            });

            // 创建下载链接
            const downloadUrl = window.URL.createObjectURL(new Blob([response]));
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(downloadUrl);

            return { success: true };
        } catch (error) {
            throw this.processError(error);
        }
    }
}

// 创建全局API客户端实例 - 使用条件声明避免重复
if (typeof window.apiClient === 'undefined') {
    window.apiClient = new ApiClient();
}

// 导出API客户端类和实例
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiClient, apiClient };
}
    window.ApiClient = ApiClient;
}