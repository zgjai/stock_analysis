// 模拟前端验证器
const Validators = {
    stockCode: (code) => {
        if (!code || typeof code !== 'string') return false;
        return /^[0-9]{6}$/.test(code.trim());
    },
    price: (price) => {
        if (price === null || price === undefined || price === '') return false;
        const num = parseFloat(price);
        return !isNaN(num) && num > 0 && num < 10000;
    },
    quantity: (quantity) => {
        if (quantity === null || quantity === undefined || quantity === '') return false;
        const num = parseInt(quantity);
        return !isNaN(num) && num > 0 && num % 100 === 0;
    }
};

// 测试你的数据
const testData = {
    stock_code: '000776',
    price: '19.453',
    quantity: '31100'
};

console.log('=== 验证器测试结果 ===');
console.log('股票代码验证:', Validators.stockCode(testData.stock_code));
console.log('价格验证:', Validators.price(testData.price));
console.log('数量验证:', Validators.quantity(testData.quantity));

// 详细检查数量
const num = parseInt(testData.quantity);
console.log('\n=== 数量详细检查 ===');
console.log('原始值:', testData.quantity);
console.log('转换后:', num);
console.log('是否为数字:', !isNaN(num));
console.log('是否大于0:', num > 0);
console.log('是否100的倍数:', num % 100 === 0);
console.log('31100 % 100 =', 31100 % 100);