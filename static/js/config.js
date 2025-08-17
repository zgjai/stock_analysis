// 前端配置文件
const Config = {
    // API配置
    API: {
        BASE_URL: '/api',
        TIMEOUT: 30000,
        RETRY_ATTEMPTS: 3
    },

    // 分页配置
    PAGINATION: {
        DEFAULT_PAGE_SIZE: 20,
        PAGE_SIZE_OPTIONS: [10, 20, 50, 100]
    },

    // 图表配置
    CHARTS: {
        DEFAULT_COLORS: [
            '#007bff', '#28a745', '#ffc107', '#dc3545',
            '#17a2b8', '#6f42c1', '#e83e8c', '#fd7e14'
        ],
        ANIMATION_DURATION: 1000
    },

    // 文件上传配置
    UPLOAD: {
        MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
        ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif'],
        ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.gif']
    },

    // 本地存储键名
    STORAGE_KEYS: {
        USER_PREFERENCES: 'stock_journal_preferences',
        FILTER_SETTINGS: 'stock_journal_filters',
        CHART_SETTINGS: 'stock_journal_charts'
    },

    // 消息配置
    MESSAGES: {
        DEFAULT_DURATION: 5000,
        SUCCESS_DURATION: 3000,
        ERROR_DURATION: 8000
    },

    // 表单验证配置
    VALIDATION: {
        STOCK_CODE_PATTERN: /^[0-9]{6}$/,
        PRICE_MIN: 0.01,
        PRICE_MAX: 9999.99,
        QUANTITY_MIN: 100,
        QUANTITY_STEP: 100
    },

    // 格式化配置
    FORMAT: {
        CURRENCY: 'CNY',
        LOCALE: 'zh-CN',
        DATE_FORMAT: 'YYYY-MM-DD',
        DATETIME_FORMAT: 'YYYY-MM-DD HH:mm:ss'
    },

    // 刷新间隔配置
    REFRESH: {
        DASHBOARD_INTERVAL: 5 * 60 * 1000, // 5分钟
        PRICE_INTERVAL: 30 * 1000, // 30秒
        ALERTS_INTERVAL: 60 * 1000 // 1分钟
    },

    // 调试配置
    DEBUG: {
        ENABLED: false,
        LOG_LEVEL: 'info',
        SHOW_API_LOGS: false
    }
};

// 根据环境调整配置
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    Config.DEBUG.ENABLED = true;
    Config.DEBUG.SHOW_API_LOGS = true;
}

// 导出配置
if (typeof window !== 'undefined') {
    window.Config = Config;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = Config;
}