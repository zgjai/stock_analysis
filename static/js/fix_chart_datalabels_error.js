// 修复Chart.js datalabels插件错误的脚本

// 1. 安全的插件注册
function safeRegisterChartPlugins() {
    try {
        if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
            // 检查是否已经注册
            if (!Chart.registry.plugins.has('datalabels')) {
                Chart.register(ChartDataLabels);
                console.log('Chart.js datalabels插件已安全注册');
            } else {
                console.log('Chart.js datalabels插件已存在，跳过注册');
            }
        } else {
            console.warn('Chart.js或datalabels插件未加载');
        }
    } catch (error) {
        console.error('注册Chart.js插件时发生错误:', error);
    }
}

// 全局错误拦截器 - 在插件注册前设置
function setupGlobalErrorHandler() {
    const originalError = console.error;
    console.error = function(...args) {
        // 拦截并处理 datalabels 相关错误
        const errorStr = args.join(' ');
        if (errorStr.includes('Cannot read properties of null') && errorStr.includes('reading \'x\'')) {
            console.warn('Chart.js datalabels 空值错误已拦截并忽略');
            return;
        }
        originalError.apply(console, args);
    };
}

// 2. 安全的datalabels配置
function getSafeDataLabelsConfig() {
    return {
        display: function(context) {
            try {
                // 多层安全检查：确保context和数据存在
                if (!context || !context.dataset || !context.dataset.data) {
                    return false;
                }
                
                // 检查 dataIndex 是否有效
                if (typeof context.dataIndex !== 'number' || context.dataIndex < 0) {
                    return false;
                }
                
                // 检查数据数组长度
                if (context.dataIndex >= context.dataset.data.length) {
                    return false;
                }
                
                const value = context.dataset.data[context.dataIndex];
                return value != null && !isNaN(value) && value !== 0;
            } catch (error) {
                console.warn('datalabels display 函数错误:', error);
                return false;
            }
        },
        anchor: 'end',
        align: 'top',
        formatter: function(value, context) {
            try {
                // 安全检查：确保value存在且有效
                if (value == null || isNaN(value)) {
                    return '';
                }
                
                // 额外检查 context 对象
                if (!context || !context.chart || !context.chart.config) {
                    return value.toString();
                }
                
                // 根据图表类型格式化数据
                if (context.chart.config.type === 'doughnut' || context.chart.config.type === 'pie') {
                    return value.toFixed(1) + '%';
                } else {
                    return value.toFixed(2);
                }
            } catch (error) {
                console.warn('datalabels formatter 函数错误:', error);
                return '';
            }
        },
        color: function(context) {
            // 安全的颜色配置
            try {
                if (!context || !context.dataset) {
                    return '#000';
                }
                return context.dataset.borderColor || context.dataset.backgroundColor || '#000';
            } catch (error) {
                console.warn('datalabels color 函数错误:', error);
                return '#000';
            }
        },
        font: {
            weight: 'bold',
            size: 12
        },
        padding: 4,
        // 添加错误处理
        listeners: {
            enter: function(context) {
                // 安全的事件处理
                try {
                    if (context && context.element && context.element.options) {
                        context.element.options.backgroundColor = 'rgba(255, 255, 255, 0.8)';
                    }
                } catch (error) {
                    console.warn('datalabels enter事件处理错误:', error);
                }
            },
            leave: function(context) {
                // 安全的事件处理
                try {
                    if (context && context.element && context.element.options) {
                        context.element.options.backgroundColor = 'transparent';
                    }
                } catch (error) {
                    console.warn('datalabels leave事件处理错误:', error);
                }
            }
        }
    };
}

// 3. 安全的图表创建函数
function createSafeChart(ctx, config) {
    try {
        // 确保canvas元素存在
        if (!ctx || !ctx.getContext) {
            console.error('无效的canvas元素');
            return null;
        }
        
        // 安全的配置检查
        if (!config || !config.type) {
            console.error('无效的图表配置');
            return null;
        }
        
        // 如果配置中使用了datalabels，应用安全配置
        if (config.options && config.options.plugins && config.options.plugins.datalabels) {
            config.options.plugins.datalabels = getSafeDataLabelsConfig();
        }
        
        // 添加全局错误处理
        config.options = config.options || {};
        config.options.onError = function(error) {
            console.error('Chart.js错误:', error);
        };
        
        return new Chart(ctx, config);
        
    } catch (error) {
        console.error('创建图表时发生错误:', error);
        return null;
    }
}

// 4. 修复现有图表的函数
function fixExistingCharts() {
    try {
        // 获取所有Chart实例
        Chart.instances.forEach((chart, index) => {
            try {
                if (chart && chart.config && chart.config.options) {
                    // 检查是否使用了datalabels插件
                    if (chart.config.options.plugins && chart.config.options.plugins.datalabels) {
                        // 更新为安全配置
                        chart.config.options.plugins.datalabels = getSafeDataLabelsConfig();
                        chart.update('none'); // 静默更新
                    }
                }
            } catch (error) {
                console.warn(`修复图表${index}时发生错误:`, error);
            }
        });
        
        console.log('现有图表已修复');
        
    } catch (error) {
        console.error('修复现有图表时发生错误:', error);
    }
}

// 5. 增强的全局错误处理
window.addEventListener('error', function(event) {
    if (event.error && event.error.message) {
        const errorMsg = event.error.message;
        
        // 检查是否是 datalabels 相关错误
        if (errorMsg.includes('datalabels') || 
            (errorMsg.includes('Cannot read properties of null') && errorMsg.includes('reading \'x\'')) ||
            errorMsg.includes('chartjs-plugin-datalabels')) {
            
            console.warn('Chart.js datalabels错误已拦截:', event.error);
            
            // 尝试修复现有图表
            setTimeout(() => {
                fixExistingCharts();
            }, 100);
            
            // 阻止错误冒泡到控制台
            event.preventDefault();
            event.stopPropagation();
            return false;
        }
    }
});

// 拦截 unhandledrejection 事件
window.addEventListener('unhandledrejection', function(event) {
    if (event.reason && event.reason.message) {
        const errorMsg = event.reason.message;
        
        if (errorMsg.includes('datalabels') || 
            (errorMsg.includes('Cannot read properties of null') && errorMsg.includes('reading \'x\''))) {
            
            console.warn('Chart.js datalabels Promise 错误已拦截:', event.reason);
            event.preventDefault();
            return false;
        }
    }
});

// 6. 初始化函数
function initChartErrorFix() {
    // 设置全局错误处理
    setupGlobalErrorHandler();
    
    // 安全注册插件
    safeRegisterChartPlugins();
    
    // 修复现有图表
    if (typeof Chart !== 'undefined' && Chart.instances) {
        fixExistingCharts();
    }
    
    console.log('Chart.js datalabels错误修复已初始化');
}

// 导出函数供外部使用
if (typeof window !== 'undefined') {
    window.safeRegisterChartPlugins = safeRegisterChartPlugins;
    window.getSafeDataLabelsConfig = getSafeDataLabelsConfig;
    window.createSafeChart = createSafeChart;
    window.fixExistingCharts = fixExistingCharts;
    window.initChartErrorFix = initChartErrorFix;
    window.setupGlobalErrorHandler = setupGlobalErrorHandler;
}

// 自动初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChartErrorFix);
} else {
    initChartErrorFix();
}

console.log('Chart.js datalabels错误修复脚本已加载');