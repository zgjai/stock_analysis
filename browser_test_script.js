
// 浏览器控制台测试脚本
// 复制粘贴到浏览器控制台中运行

console.log("🔍 开始JavaScript修复验证测试...");

// 测试1: 检查全局变量是否正确加载
const globalVars = ['Validators', 'Formatters', 'DOMUtils', 'DataUtils'];
let passedTests = 0;
let totalTests = 0;

globalVars.forEach(varName => {
    totalTests++;
    if (typeof window[varName] !== 'undefined') {
        console.log(`✅ ${varName} 加载成功`);
        passedTests++;
    } else {
        console.error(`❌ ${varName} 未加载`);
    }
});

// 测试2: 检查紧急修复脚本
totalTests++;
if (typeof window.fixAsyncSyntax === 'function') {
    console.log("✅ 紧急修复脚本加载成功");
    passedTests++;
} else {
    console.error("❌ 紧急修复脚本未加载");
}

// 测试3: 测试股票代码验证功能
if (window.Validators && window.Validators.stockCode) {
    totalTests++;
    try {
        const test1 = window.Validators.stockCode('000001');
        const test2 = window.Validators.stockCode('invalid');
        
        if (test1 === true && test2 === false) {
            console.log("✅ 股票代码验证功能正常");
            passedTests++;
        } else {
            console.error("❌ 股票代码验证功能异常");
        }
    } catch (e) {
        console.error("❌ 股票代码验证测试异常:", e);
    }
}

// 测试4: 检查是否还有语法错误
totalTests++;
let hasErrors = false;
const originalError = console.error;
console.error = function(...args) {
    const message = args.join(' ');
    if (message.includes('SyntaxError') || message.includes('already been declared')) {
        hasErrors = true;
    }
    originalError.apply(console, args);
};

setTimeout(() => {
    if (!hasErrors) {
        console.log("✅ 未检测到语法错误");
        passedTests++;
    } else {
        console.error("❌ 仍有语法错误");
    }
    
    // 显示最终结果
    console.log(`\n📊 测试结果: ${passedTests}/${totalTests} 项通过`);
    
    if (passedTests === totalTests) {
        console.log("🎉 所有测试通过！JavaScript修复成功！");
    } else {
        console.log("⚠️ 部分测试失败，可能需要进一步检查");
    }
}, 2000);

console.log("\n请等待2秒查看完整测试结果...");
