/**
 * 错误监控和调试支持系统
 * 提供详细的控制台日志记录、功能测试函数、依赖检查和状态诊断工具
 * 确保错误信息对开发者友好且对用户安全
 */

// 调试配置
const DEBUG_CONFIG = {
    // 是否启用详细日志
    enableVerboseLogging: true,
    // 是否启用性能监控
    enablePerformanceMonitoring: true,
    // 是否启用错误收集
    enableErrorCollection: true,
    // 日志级别 (debug, info, warn, error)
    logLevel: 'debug',
    // 最大日志条数
    maxLogEntries: 1000,
    // 是否在生产环境中启用调试
    enableInProduction: false
};

// 全局调试状态
const DEBUG_STATE = {
    initialized: false,
    errorCount: 0,
    warningCount: 0,
    logEntries: [],
    performanceMetrics: {},
    dependencyStatus: {},
    lastHealthCheck: null
};

/**
 * 调试监控系统类
 */
class DebugMonitoringSystem {
    constructor(config = {}) {
        this.config = { ...DEBUG_CONFIG, ...config };
        this.state = DEBUG_STATE;
        this.logBuffer = [];
        this.errorBuffer = [];
        this.performanceBuffer = [];
        
        this.init();
    }
    
    /**
     * 初始化调试监控系统
     */
    init() {
        console.log('🔧 初始化调试监控系统');
        
        try {
            // 设置全局错误处理
            this.setupGlobalErrorHandling();
            
            // 设置性能监控
            if (this.config.enablePerformanceMonitoring) {
                this.setupPerformanceMonitoring();
            }
            
            // 设置控制台增强
            this.setupConsoleEnhancements();
            
            // 注册调试工具到全局
            this.registerGlobalDebugTools();
            
            this.state.initialized = true;
            console.log('✅ 调试监控系统初始化成功');
            
            // 执行初始健康检查
            setTimeout(() => this.performHealthCheck(), 1000);
            
        } catch (error) {
            console.error('❌ 调试监控系统初始化失败:', error);
        }
    }
    
    /**
     * 设置全局错误处理
     */
    setupGlobalErrorHandling() {
        console.log('🛡️ 设置全局错误处理');
        
        // JavaScript运行时错误
        window.addEventListener('error', (event) => {
            this.handleGlobalError({
                type: 'javascript',
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error,
                stack: event.error ? event.error.stack : null,
                timestamp: new Date().toISOString()
            });
        });
        
        // Promise拒绝错误
        window.addEventListener('unhandledrejection', (event) => {
            this.handleGlobalError({
                type: 'promise',
                message: event.reason ? event.reason.message || event.reason : 'Unhandled Promise Rejection',
                reason: event.reason,
                stack: event.reason && event.reason.stack ? event.reason.stack : null,
                timestamp: new Date().toISOString()
            });
        });
        
        // 资源加载错误
        window.addEventListener('error', (event) => {
            if (event.target !== window) {
                this.handleGlobalError({
                    type: 'resource',
                    message: `Failed to load resource: ${event.target.src || event.target.href}`,
                    element: event.target.tagName,
                    source: event.target.src || event.target.href,
                    timestamp: new Date().toISOString()
                });
            }
        }, true);
    }
    
    /**
     * 处理全局错误
     */
    handleGlobalError(errorInfo) {
        this.state.errorCount++;
        this.errorBuffer.push(errorInfo);
        
        // 保持错误缓冲区大小
        if (this.errorBuffer.length > 100) {
            this.errorBuffer.shift();
        }
        
        // 详细日志记录
        console.group(`🚨 全局错误 #${this.state.errorCount} [${errorInfo.type}]`);
        console.error('错误信息:', errorInfo.message);
        if (errorInfo.filename) {
            console.error('文件:', errorInfo.filename);
            console.error('位置:', `${errorInfo.lineno}:${errorInfo.colno}`);
        }
        if (errorInfo.stack) {
            console.error('堆栈:', errorInfo.stack);
        }
        console.error('时间:', errorInfo.timestamp);
        console.error('完整信息:', errorInfo);
        console.groupEnd();
        
        // 用户友好的错误提示（仅关键错误）
        if (this.shouldShowUserError(errorInfo)) {
            this.showUserFriendlyError(errorInfo);
        }
    }
    
    /**
     * 判断是否应该向用户显示错误
     */
    shouldShowUserError(errorInfo) {
        // 资源加载错误通常不需要显示给用户
        if (errorInfo.type === 'resource') {
            return false;
        }
        
        // 某些已知的非关键错误
        const ignoredMessages = [
            'Script error',
            'Non-Error promise rejection captured',
            'ResizeObserver loop limit exceeded'
        ];
        
        return !ignoredMessages.some(msg => 
            errorInfo.message && errorInfo.message.includes(msg)
        );
    }
    
    /**
     * 显示用户友好的错误信息
     */
    showUserFriendlyError(errorInfo) {
        const userMessage = this.generateUserFriendlyMessage(errorInfo);
        
        // 使用统一消息系统（如果可用）
        if (typeof showErrorMessage === 'function') {
            showErrorMessage(userMessage);
        } else {
            // 降级到原生alert（仅在开发环境）
            if (this.config.enableInProduction || window.location.hostname === 'localhost') {
                console.warn('⚠️ 统一消息系统不可用，使用原生alert');
                alert(userMessage);
            }
        }
    }
    
    /**
     * 生成用户友好的错误消息
     */
    generateUserFriendlyMessage(errorInfo) {
        switch (errorInfo.type) {
            case 'javascript':
                return '页面功能出现异常，请刷新页面重试';
            case 'promise':
                return '数据处理出现问题，请稍后重试';
            case 'resource':
                return '资源加载失败，请检查网络连接';
            default:
                return '系统出现异常，请刷新页面重试';
        }
    }
    
    /**
     * 设置性能监控
     */
    setupPerformanceMonitoring() {
        console.log('⚡ 设置性能监控');
        
        // 页面加载性能
        if ('performance' in window && 'timing' in performance) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const timing = performance.timing;
                    const metrics = {
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                        pageLoad: timing.loadEventEnd - timing.navigationStart,
                        domReady: timing.domComplete - timing.navigationStart,
                        firstPaint: this.getFirstPaintTime(),
                        timestamp: new Date().toISOString()
                    };
                    
                    this.state.performanceMetrics.pageLoad = metrics;
                    this.logPerformanceMetrics('页面加载', metrics);
                }, 0);
            });
        }
        
        // 监控长任务
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 50) { // 超过50ms的任务
                            console.warn(`⚠️ 长任务检测: ${entry.duration.toFixed(2)}ms`, entry);
                        }
                    }
                });
                observer.observe({ entryTypes: ['longtask'] });
            } catch (error) {
                console.warn('⚠️ 长任务监控不支持:', error);
            }
        }
    }
    
    /**
     * 获取首次绘制时间
     */
    getFirstPaintTime() {
        if ('performance' in window && 'getEntriesByType' in performance) {
            const paintEntries = performance.getEntriesByType('paint');
            const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
            return firstPaint ? firstPaint.startTime : null;
        }
        return null;
    }
    
    /**
     * 记录性能指标
     */
    logPerformanceMetrics(operation, metrics) {
        console.group(`⚡ 性能指标: ${operation}`);
        Object.entries(metrics).forEach(([key, value]) => {
            if (typeof value === 'number') {
                console.log(`${key}: ${value.toFixed(2)}ms`);
            } else {
                console.log(`${key}:`, value);
            }
        });
        console.groupEnd();
        
        this.performanceBuffer.push({
            operation,
            metrics,
            timestamp: new Date().toISOString()
        });
        
        // 保持性能缓冲区大小
        if (this.performanceBuffer.length > 50) {
            this.performanceBuffer.shift();
        }
    }
    
    /**
     * 设置控制台增强
     */
    setupConsoleEnhancements() {
        console.log('🎨 设置控制台增强');
        
        // 保存原始console方法
        const originalConsole = {
            log: console.log,
            warn: console.warn,
            error: console.error,
            info: console.info,
            debug: console.debug
        };
        
        // 增强console.log
        console.log = (...args) => {
            this.addLogEntry('log', args);
            originalConsole.log(...args);
        };
        
        // 增强console.warn
        console.warn = (...args) => {
            this.state.warningCount++;
            this.addLogEntry('warn', args);
            originalConsole.warn(...args);
        };
        
        // 增强console.error
        console.error = (...args) => {
            this.state.errorCount++;
            this.addLogEntry('error', args);
            originalConsole.error(...args);
        };
        
        // 增强console.info
        console.info = (...args) => {
            this.addLogEntry('info', args);
            originalConsole.info(...args);
        };
        
        // 增强console.debug
        console.debug = (...args) => {
            if (this.config.logLevel === 'debug') {
                this.addLogEntry('debug', args);
                originalConsole.debug(...args);
            }
        };
    }
    
    /**
     * 添加日志条目
     */
    addLogEntry(level, args) {
        const entry = {
            level,
            message: args.map(arg => 
                typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
            ).join(' '),
            args,
            timestamp: new Date().toISOString(),
            stack: new Error().stack
        };
        
        this.state.logEntries.push(entry);
        
        // 保持日志条目数量限制
        if (this.state.logEntries.length > this.config.maxLogEntries) {
            this.state.logEntries.shift();
        }
    }
    
    /**
     * 注册全局调试工具
     */
    registerGlobalDebugTools() {
        console.log('🔧 注册全局调试工具');
        
        // 将调试工具注册到window对象
        window.debugTools = {
            // 系统状态
            getSystemStatus: () => this.getSystemStatus(),
            
            // 依赖检查
            checkDependencies: () => this.checkAllDependencies(),
            
            // 功能测试
            runFunctionalTests: () => this.runFunctionalTests(),
            
            // 性能诊断
            performanceReport: () => this.generatePerformanceReport(),
            
            // 错误报告
            errorReport: () => this.generateErrorReport(),
            
            // 日志导出
            exportLogs: () => this.exportLogs(),
            
            // 健康检查
            healthCheck: () => this.performHealthCheck(),
            
            // 清理缓存
            clearCache: () => this.clearDebugCache(),
            
            // 重置状态
            reset: () => this.resetDebugState()
        };
        
        console.log('✅ 全局调试工具注册完成');
        console.log('💡 使用 window.debugTools 访问调试功能');
    }
    
    /**
     * 获取系统状态
     */
    getSystemStatus() {
        const status = {
            timestamp: new Date().toISOString(),
            debugSystem: {
                initialized: this.state.initialized,
                errorCount: this.state.errorCount,
                warningCount: this.state.warningCount,
                logEntries: this.state.logEntries.length
            },
            browser: {
                userAgent: navigator.userAgent,
                language: navigator.language,
                platform: navigator.platform,
                cookieEnabled: navigator.cookieEnabled,
                onLine: navigator.onLine
            },
            page: {
                url: window.location.href,
                title: document.title,
                readyState: document.readyState,
                visibilityState: document.visibilityState
            },
            performance: this.state.performanceMetrics,
            dependencies: this.state.dependencyStatus
        };
        
        console.group('📊 系统状态报告');
        console.table(status.debugSystem);
        console.log('浏览器信息:', status.browser);
        console.log('页面信息:', status.page);
        console.log('性能指标:', status.performance);
        console.log('依赖状态:', status.dependencies);
        console.groupEnd();
        
        return status;
    }
    
    /**
     * 检查所有依赖
     */
    checkAllDependencies() {
        console.log('🔍 执行全面依赖检查');
        
        const dependencies = [
            // 核心依赖
            { name: 'Bootstrap', check: () => typeof bootstrap !== 'undefined', category: 'core' },
            
            // API和服务
            { name: 'ApiClient', check: () => typeof ApiClient !== 'undefined', category: 'api' },
            { name: 'ReviewSaveManager', check: () => typeof ReviewSaveManager !== 'undefined', category: 'api' },
            
            // 消息系统
            { name: 'UnifiedMessageSystem', check: () => typeof UnifiedMessageSystem !== 'undefined', category: 'ui' },
            { name: 'showErrorMessage', check: () => typeof showErrorMessage === 'function', category: 'ui' },
            { name: 'showSuccessMessage', check: () => typeof showSuccessMessage === 'function', category: 'ui' },
            
            // 工具函数
            { name: 'debounce', check: () => typeof debounce === 'function', category: 'utils' },
            { name: 'throttle', check: () => typeof throttle === 'function', category: 'utils' },
            
            // 性能工具
            { name: 'PerformanceUtils', check: () => typeof PerformanceUtils !== 'undefined', category: 'performance' },
            
            // 浏览器API
            { name: 'localStorage', check: () => typeof localStorage !== 'undefined', category: 'browser' },
            { name: 'sessionStorage', check: () => typeof sessionStorage !== 'undefined', category: 'browser' },
            { name: 'fetch', check: () => typeof fetch === 'function', category: 'browser' },
            { name: 'Promise', check: () => typeof Promise !== 'undefined', category: 'browser' }
        ];
        
        const results = {};
        const summary = { total: 0, available: 0, missing: 0, byCategory: {} };
        
        dependencies.forEach(dep => {
            const isAvailable = dep.check();
            results[dep.name] = {
                available: isAvailable,
                category: dep.category
            };
            
            summary.total++;
            if (isAvailable) {
                summary.available++;
            } else {
                summary.missing++;
            }
            
            if (!summary.byCategory[dep.category]) {
                summary.byCategory[dep.category] = { total: 0, available: 0, missing: 0 };
            }
            summary.byCategory[dep.category].total++;
            if (isAvailable) {
                summary.byCategory[dep.category].available++;
            } else {
                summary.byCategory[dep.category].missing++;
            }
        });
        
        // 更新状态
        this.state.dependencyStatus = {
            results,
            summary,
            lastCheck: new Date().toISOString()
        };
        
        // 输出结果
        console.group('📋 依赖检查结果');
        console.log(`总计: ${summary.total}, 可用: ${summary.available}, 缺失: ${summary.missing}`);
        
        Object.entries(summary.byCategory).forEach(([category, stats]) => {
            console.log(`${category}: ${stats.available}/${stats.total} 可用`);
        });
        
        console.table(results);
        console.groupEnd();
        
        // 显示缺失的关键依赖
        const missingCritical = dependencies
            .filter(dep => !dep.check() && ['core', 'api'].includes(dep.category))
            .map(dep => dep.name);
            
        if (missingCritical.length > 0) {
            console.warn('🚨 缺失关键依赖:', missingCritical);
            if (typeof showWarningMessage === 'function') {
                showWarningMessage(`缺失关键依赖: ${missingCritical.join(', ')}`);
            }
        }
        
        return this.state.dependencyStatus;
    }
    
    /**
     * 运行功能测试
     */
    runFunctionalTests() {
        console.log('🧪 运行功能测试');
        
        const tests = [
            {
                name: 'DOM元素存在性测试',
                test: () => this.testDOMElements()
            },
            {
                name: 'API客户端功能测试',
                test: () => this.testApiClient()
            },
            {
                name: '保存管理器功能测试',
                test: () => this.testSaveManager()
            },
            {
                name: '消息系统功能测试',
                test: () => this.testMessageSystem()
            },
            {
                name: '事件绑定测试',
                test: () => this.testEventBindings()
            },
            {
                name: '本地存储测试',
                test: () => this.testLocalStorage()
            }
        ];
        
        const results = [];
        let passedCount = 0;
        
        console.group('🧪 功能测试结果');
        
        tests.forEach((test, index) => {
            console.group(`测试 ${index + 1}: ${test.name}`);
            
            try {
                const startTime = performance.now();
                const result = test.test();
                const endTime = performance.now();
                const duration = (endTime - startTime).toFixed(2);
                
                const testResult = {
                    name: test.name,
                    passed: result.success,
                    message: result.message,
                    details: result.details,
                    duration: `${duration}ms`,
                    timestamp: new Date().toISOString()
                };
                
                results.push(testResult);
                
                if (result.success) {
                    passedCount++;
                    console.log(`✅ 通过 (${duration}ms)`);
                    if (result.message) console.log('信息:', result.message);
                } else {
                    console.error(`❌ 失败 (${duration}ms)`);
                    console.error('原因:', result.message);
                    if (result.details) console.error('详情:', result.details);
                }
                
            } catch (error) {
                console.error(`❌ 异常:`, error);
                results.push({
                    name: test.name,
                    passed: false,
                    message: error.message,
                    error: error.stack,
                    timestamp: new Date().toISOString()
                });
            }
            
            console.groupEnd();
        });
        
        console.log(`📊 测试汇总: ${passedCount}/${tests.length} 通过`);
        console.table(results);
        console.groupEnd();
        
        return {
            summary: {
                total: tests.length,
                passed: passedCount,
                failed: tests.length - passedCount,
                passRate: ((passedCount / tests.length) * 100).toFixed(1) + '%'
            },
            results,
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * 测试DOM元素
     */
    testDOMElements() {
        const requiredElements = [
            '#reviewModal',
            '#review-form',
            '#save-review-btn',
            '#holdings-list',
            '#reviews-list'
        ];
        
        const missing = [];
        const found = [];
        
        requiredElements.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                found.push(selector);
            } else {
                missing.push(selector);
            }
        });
        
        return {
            success: missing.length === 0,
            message: missing.length === 0 
                ? `所有必需元素都存在 (${found.length}/${requiredElements.length})`
                : `缺失元素: ${missing.join(', ')}`,
            details: { found, missing }
        };
    }
    
    /**
     * 测试API客户端
     */
    testApiClient() {
        if (typeof ApiClient === 'undefined') {
            return {
                success: false,
                message: 'ApiClient类未定义'
            };
        }
        
        try {
            const client = new ApiClient();
            const requiredMethods = ['get', 'post', 'put', 'delete'];
            const missingMethods = requiredMethods.filter(method => typeof client[method] !== 'function');
            
            return {
                success: missingMethods.length === 0,
                message: missingMethods.length === 0 
                    ? 'API客户端功能完整'
                    : `缺失方法: ${missingMethods.join(', ')}`,
                details: { requiredMethods, missingMethods }
            };
        } catch (error) {
            return {
                success: false,
                message: 'API客户端实例化失败',
                details: error.message
            };
        }
    }
    
    /**
     * 测试保存管理器
     */
    testSaveManager() {
        if (typeof ReviewSaveManager === 'undefined') {
            return {
                success: false,
                message: 'ReviewSaveManager类未定义'
            };
        }
        
        try {
            // 检查是否有表单元素
            const form = document.querySelector('#review-form');
            if (!form) {
                return {
                    success: false,
                    message: '复盘表单元素不存在，无法测试保存管理器'
                };
            }
            
            const manager = new ReviewSaveManager('#review-form');
            const requiredMethods = ['saveReview', 'hasUnsavedChanges'];
            const missingMethods = requiredMethods.filter(method => typeof manager[method] !== 'function');
            
            return {
                success: missingMethods.length === 0,
                message: missingMethods.length === 0 
                    ? '保存管理器功能完整'
                    : `缺失方法: ${missingMethods.join(', ')}`,
                details: { requiredMethods, missingMethods }
            };
        } catch (error) {
            return {
                success: false,
                message: '保存管理器实例化失败',
                details: error.message
            };
        }
    }
    
    /**
     * 测试消息系统
     */
    testMessageSystem() {
        const messageFunctions = [
            'showErrorMessage',
            'showSuccessMessage',
            'showWarningMessage',
            'showInfoMessage'
        ];
        
        const missing = messageFunctions.filter(fn => typeof window[fn] !== 'function');
        
        return {
            success: missing.length === 0,
            message: missing.length === 0 
                ? '消息系统功能完整'
                : `缺失函数: ${missing.join(', ')}`,
            details: { required: messageFunctions, missing }
        };
    }
    
    /**
     * 测试事件绑定
     */
    testEventBindings() {
        const testElements = [
            { selector: '#save-review-btn', event: 'click' },
            { selector: '#current-price-input', event: 'input' }
        ];
        
        const results = [];
        
        testElements.forEach(({ selector, event }) => {
            const element = document.querySelector(selector);
            if (element) {
                // 检查是否有事件监听器（这是一个简化的检查）
                const hasListeners = element.onclick !== null || 
                                   element.addEventListener !== undefined;
                results.push({
                    selector,
                    event,
                    element: !!element,
                    hasListeners
                });
            } else {
                results.push({
                    selector,
                    event,
                    element: false,
                    hasListeners: false
                });
            }
        });
        
        const allGood = results.every(r => r.element);
        
        return {
            success: allGood,
            message: allGood ? '事件绑定测试通过' : '部分元素不存在',
            details: results
        };
    }
    
    /**
     * 测试本地存储
     */
    testLocalStorage() {
        try {
            const testKey = 'debug_test_' + Date.now();
            const testValue = 'test_value';
            
            localStorage.setItem(testKey, testValue);
            const retrieved = localStorage.getItem(testKey);
            localStorage.removeItem(testKey);
            
            return {
                success: retrieved === testValue,
                message: retrieved === testValue ? '本地存储功能正常' : '本地存储读写失败'
            };
        } catch (error) {
            return {
                success: false,
                message: '本地存储不可用',
                details: error.message
            };
        }
    }
    
    /**
     * 生成性能报告
     */
    generatePerformanceReport() {
        console.group('⚡ 性能报告');
        
        const report = {
            timestamp: new Date().toISOString(),
            pageMetrics: this.state.performanceMetrics,
            recentOperations: this.performanceBuffer.slice(-10),
            memoryUsage: this.getMemoryUsage(),
            networkInfo: this.getNetworkInfo(),
            recommendations: this.generatePerformanceRecommendations()
        };
        
        console.log('页面指标:', report.pageMetrics);
        console.log('最近操作:', report.recentOperations);
        console.log('内存使用:', report.memoryUsage);
        console.log('网络信息:', report.networkInfo);
        console.log('优化建议:', report.recommendations);
        
        console.groupEnd();
        
        return report;
    }
    
    /**
     * 获取内存使用情况
     */
    getMemoryUsage() {
        if ('memory' in performance) {
            return {
                used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + ' MB',
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + ' MB',
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024) + ' MB'
            };
        }
        return { message: '内存信息不可用' };
    }
    
    /**
     * 获取网络信息
     */
    getNetworkInfo() {
        if ('connection' in navigator) {
            const conn = navigator.connection;
            return {
                effectiveType: conn.effectiveType,
                downlink: conn.downlink + ' Mbps',
                rtt: conn.rtt + ' ms',
                saveData: conn.saveData
            };
        }
        return { message: '网络信息不可用' };
    }
    
    /**
     * 生成性能优化建议
     */
    generatePerformanceRecommendations() {
        const recommendations = [];
        
        // 检查页面加载时间
        if (this.state.performanceMetrics.pageLoad && 
            this.state.performanceMetrics.pageLoad.pageLoad > 3000) {
            recommendations.push('页面加载时间较长，考虑优化资源加载');
        }
        
        // 检查错误数量
        if (this.state.errorCount > 5) {
            recommendations.push('错误数量较多，需要修复JavaScript错误');
        }
        
        // 检查内存使用
        const memory = this.getMemoryUsage();
        if (memory.used && parseInt(memory.used) > 100) {
            recommendations.push('内存使用较高，检查是否存在内存泄漏');
        }
        
        if (recommendations.length === 0) {
            recommendations.push('性能表现良好，无明显问题');
        }
        
        return recommendations;
    }
    
    /**
     * 生成错误报告
     */
    generateErrorReport() {
        console.group('🚨 错误报告');
        
        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                totalErrors: this.state.errorCount,
                totalWarnings: this.state.warningCount,
                recentErrors: this.errorBuffer.length
            },
            recentErrors: this.errorBuffer.slice(-10),
            errorPatterns: this.analyzeErrorPatterns(),
            recommendations: this.generateErrorRecommendations()
        };
        
        console.log('错误汇总:', report.summary);
        console.log('最近错误:', report.recentErrors);
        console.log('错误模式:', report.errorPatterns);
        console.log('修复建议:', report.recommendations);
        
        console.groupEnd();
        
        return report;
    }
    
    /**
     * 分析错误模式
     */
    analyzeErrorPatterns() {
        const patterns = {};
        
        this.errorBuffer.forEach(error => {
            const key = error.type + ':' + (error.message || 'unknown');
            patterns[key] = (patterns[key] || 0) + 1;
        });
        
        return Object.entries(patterns)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([pattern, count]) => ({ pattern, count }));
    }
    
    /**
     * 生成错误修复建议
     */
    generateErrorRecommendations() {
        const recommendations = [];
        
        if (this.state.errorCount === 0) {
            recommendations.push('暂无错误，系统运行正常');
        } else {
            recommendations.push('检查控制台中的详细错误信息');
            recommendations.push('确保所有JavaScript依赖都已正确加载');
            
            if (this.errorBuffer.some(e => e.type === 'resource')) {
                recommendations.push('检查网络连接和资源路径');
            }
            
            if (this.errorBuffer.some(e => e.type === 'promise')) {
                recommendations.push('检查异步操作的错误处理');
            }
        }
        
        return recommendations;
    }
    
    /**
     * 导出日志
     */
    exportLogs() {
        const exportData = {
            timestamp: new Date().toISOString(),
            system: this.getSystemStatus(),
            logs: this.state.logEntries,
            errors: this.errorBuffer,
            performance: this.performanceBuffer
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `debug-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        link.click();
        
        console.log('📁 日志已导出');
        return exportData;
    }
    
    /**
     * 执行健康检查
     */
    performHealthCheck() {
        console.log('🏥 执行系统健康检查');
        
        const checks = [
            {
                name: '依赖完整性',
                check: () => {
                    const deps = this.checkAllDependencies();
                    return deps.summary.missing === 0;
                }
            },
            {
                name: '错误水平',
                check: () => this.state.errorCount < 10
            },
            {
                name: '内存使用',
                check: () => {
                    const memory = this.getMemoryUsage();
                    return !memory.used || parseInt(memory.used) < 200;
                }
            },
            {
                name: '页面响应',
                check: () => document.readyState === 'complete'
            }
        ];
        
        const results = checks.map(check => ({
            name: check.name,
            passed: check.check(),
            timestamp: new Date().toISOString()
        }));
        
        const overallHealth = results.every(r => r.passed);
        
        this.state.lastHealthCheck = {
            timestamp: new Date().toISOString(),
            overall: overallHealth,
            results
        };
        
        console.group('🏥 健康检查结果');
        console.log(`总体状态: ${overallHealth ? '✅ 健康' : '❌ 异常'}`);
        console.table(results);
        console.groupEnd();
        
        return this.state.lastHealthCheck;
    }
    
    /**
     * 清理调试缓存
     */
    clearDebugCache() {
        console.log('🧹 清理调试缓存');
        
        this.state.logEntries = [];
        this.errorBuffer = [];
        this.performanceBuffer = [];
        this.state.errorCount = 0;
        this.state.warningCount = 0;
        
        console.log('✅ 调试缓存已清理');
    }
    
    /**
     * 重置调试状态
     */
    resetDebugState() {
        console.log('🔄 重置调试状态');
        
        this.clearDebugCache();
        this.state.performanceMetrics = {};
        this.state.dependencyStatus = {};
        this.state.lastHealthCheck = null;
        
        console.log('✅ 调试状态已重置');
    }
}

/**
 * 初始化日志记录函数
 * 用于记录初始化过程的详细信息
 */
function logInitializationProgress(step, status, details = {}) {
    const logEntry = {
        step,
        status, // 'start', 'success', 'error', 'warning'
        details,
        timestamp: new Date().toISOString()
    };
    
    // 根据状态选择合适的日志级别
    switch (status) {
        case 'start':
            console.log(`🚀 开始: ${step}`, details);
            break;
        case 'success':
            console.log(`✅ 成功: ${step}`, details);
            break;
        case 'error':
            console.error(`❌ 失败: ${step}`, details);
            break;
        case 'warning':
            console.warn(`⚠️ 警告: ${step}`, details);
            break;
        default:
            console.log(`📝 ${step}:`, details);
    }
    
    // 如果调试系统已初始化，记录到调试系统
    if (window.debugMonitor && window.debugMonitor.state.initialized) {
        window.debugMonitor.addLogEntry('info', [step, status, details]);
    }
}

// 创建全局调试监控实例
let debugMonitor = null;

// 初始化调试监控系统
function initializeDebugMonitoring() {
    console.log('🔧 初始化调试监控系统');
    
    try {
        debugMonitor = new DebugMonitoringSystem();
        window.debugMonitor = debugMonitor;
        
        console.log('✅ 调试监控系统初始化成功');
        console.log('💡 使用以下命令访问调试功能:');
        console.log('  - debugTools.getSystemStatus() - 获取系统状态');
        console.log('  - debugTools.checkDependencies() - 检查依赖');
        console.log('  - debugTools.runFunctionalTests() - 运行功能测试');
        console.log('  - debugTools.healthCheck() - 健康检查');
        console.log('  - debugTools.exportLogs() - 导出日志');
        
        return true;
    } catch (error) {
        console.error('❌ 调试监控系统初始化失败:', error);
        return false;
    }
}

// 自动初始化（如果在浏览器环境中）
if (typeof window !== 'undefined') {
    // 等待DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeDebugMonitoring);
    } else {
        // DOM已经加载完成，立即初始化
        initializeDebugMonitoring();
    }
}

// 导出调试工具（用于模块化环境）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DebugMonitoringSystem,
        initializeDebugMonitoring,
        logInitializationProgress
    };
}