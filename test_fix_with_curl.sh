#!/bin/bash

echo "=========================================="
echo "交易记录页面修复验证"
echo "=========================================="

BASE_URL="http://localhost:8080"

echo "1. 测试页面加载..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/trading-records")
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✓ 页面加载成功 (HTTP $HTTP_CODE)"
else
    echo "   ✗ 页面加载失败 (HTTP $HTTP_CODE)"
fi

echo ""
echo "2. 测试API端点..."

# 测试交易记录API
echo "   测试获取交易记录..."
TRADES_RESPONSE=$(curl -s "$BASE_URL/api/trades")
if echo "$TRADES_RESPONSE" | grep -q '"success": true'; then
    TRADE_COUNT=$(echo "$TRADES_RESPONSE" | grep -o '"total": [0-9]*' | grep -o '[0-9]*')
    echo "   ✓ 获取交易记录成功 (总计: $TRADE_COUNT 条)"
else
    echo "   ✗ 获取交易记录失败"
    echo "     响应: $(echo "$TRADES_RESPONSE" | head -c 100)..."
fi

# 测试买入原因API
echo "   测试买入原因配置..."
BUY_REASONS_RESPONSE=$(curl -s "$BASE_URL/api/trades/config/buy-reasons")
if echo "$BUY_REASONS_RESPONSE" | grep -q '"success": true'; then
    echo "   ✓ 获取买入原因成功"
else
    echo "   ✗ 获取买入原因失败"
fi

# 测试卖出原因API
echo "   测试卖出原因配置..."
SELL_REASONS_RESPONSE=$(curl -s "$BASE_URL/api/trades/config/sell-reasons")
if echo "$SELL_REASONS_RESPONSE" | grep -q '"success": true'; then
    echo "   ✓ 获取卖出原因成功"
else
    echo "   ✗ 获取卖出原因失败"
fi

echo ""
echo "3. 测试JavaScript文件..."

JS_FILES=(
    "/static/js/api.js"
    "/static/js/utils.js"
    "/static/js/form-validation.js"
    "/static/js/main.js"
)

for js_file in "${JS_FILES[@]}"; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$js_file")
    if [ "$HTTP_CODE" = "200" ]; then
        FILE_SIZE=$(curl -s "$BASE_URL$js_file" | wc -c)
        echo "   ✓ $js_file: 可访问 ($FILE_SIZE 字节)"
    else
        echo "   ✗ $js_file: HTTP $HTTP_CODE"
    fi
done

echo ""
echo "4. 检查页面关键元素..."
PAGE_CONTENT=$(curl -s "$BASE_URL/trading-records")

ELEMENTS=(
    "trades-table-body:交易记录表格"
    "addTradeModal:添加交易模态框"
    "TradingRecordsManager:JavaScript管理器"
    "apiClient:API客户端"
)

for element in "${ELEMENTS[@]}"; do
    id="${element%%:*}"
    name="${element##*:}"
    if echo "$PAGE_CONTENT" | grep -q "$id"; then
        echo "   ✓ $name: 存在"
    else
        echo "   ✗ $name: 缺失"
    fi
done

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

echo ""
echo "建议下一步操作:"
echo "1. 在浏览器中访问 http://localhost:8080/trading-records"
echo "2. 打开浏览器开发者工具检查是否有JavaScript错误"
echo "3. 尝试添加一条新的交易记录"
echo "4. 测试筛选和排序功能"