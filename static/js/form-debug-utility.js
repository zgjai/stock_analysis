/**
 * 表单数据调试工具
 * 用于诊断和修复表单数据传递问题
 */

class FormDataDebugger {
    constructor() {
        this.debugMode = true;
        this.logPrefix = '[FormDebug]';
    }
    
    /**
     * 调试表单序列化
     */
    debugFormSerialization(form) {
        if (!this.debugMode) return;
        
        console.group(`${this.logPrefix} 表单序列化调试`);
        
        // 1. 检查表单元素
        console.log('表单元素:', form);
        console.log('表单ID:', form.id);
        console.log('表单name:', form.name);
        
        // 2. 检查所有输入字段
        const inputs = form.querySelectorAll('input, select, textarea');
        console.log(`找到 ${inputs.length} 个输入字段:`);
        
        inputs.forEach((input, index) => {
            console.log(`  ${index + 1}. ${input.tagName} [name="${input.name}"] = "${input.value}" (type: ${input.type || 'text'})`);
        });
        
        // 3. 使用FormData测试
        const formData = new FormData(form);
        console.log('FormData 条目:');
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}: "${value}" (${typeof value})`);
        }
        
        // 4. 使用FormUtils.serialize测试
        if (typeof FormUtils !== 'undefined' && FormUtils.serialize) {
            const serialized = FormUtils.serialize(form);
            console.log('FormUtils.serialize 结果:', serialized);
        } else {
            console.warn('FormUtils.serialize 不可用');
        }
        
        // 5. 检查必填字段
        const requiredFields = form.querySelectorAll('[required]');
        console.log(`必填字段检查 (${requiredFields.length} 个):`);
        requiredFields.forEach(field => {
            const isEmpty = !field.value || field.value.trim() === '';
            console.log(`  ${field.name}: ${isEmpty ? '❌ 空值' : '✅ 有值'} ("${field.value}")`);
        });
        
        console.groupEnd();
    }
    
    /**
     * 调试API请求数据
     */
    debugApiRequestData(data, endpoint) {
        if (!this.debugMode) return;
        
        console.group(`${this.logPrefix} API请求数据调试`);
        console.log('请求端点:', endpoint);
        console.log('请求数据:', data);
        
        // 检查关键字段
        const criticalFields = ['stock_code', 'stock_name', 'trade_type', 'price', 'quantity', 'reason'];
        console.log('关键字段检查:');
        criticalFields.forEach(field => {
            const value = data[field];
            const isEmpty = value === undefined || value === null || value === '';
            console.log(`  ${field}: ${isEmpty ? '❌ 缺失/空值' : '✅ 有值'} (${JSON.stringify(value)})`);
        });
        
        console.groupEnd();
    }
    
    /**
     * 实时监控表单变化
     */
    monitorFormChanges(form) {
        if (!this.debugMode) return;
        
        console.log(`${this.logPrefix} 开始监控表单变化:`, form.id);
        
        form.addEventListener('input', (e) => {
            console.log(`${this.logPrefix} 字段变化: ${e.target.name} = "${e.target.value}"`);
        });
        
        form.addEventListener('change', (e) => {
            console.log(`${this.logPrefix} 字段确认变化: ${e.target.name} = "${e.target.value}"`);
        });
    }
    
    /**
     * 验证表单完整性
     */
    validateFormIntegrity(form) {
        const issues = [];
        
        // 检查表单是否存在
        if (!form) {
            issues.push('表单元素不存在');
            return issues;
        }
        
        // 检查必填字段
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value || field.value.trim() === '') {
                issues.push(`必填字段 "${field.name}" 为空`);
            }
        });
        
        // 检查name属性
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (!input.name) {
                issues.push(`输入字段缺少name属性: ${input.id || input.tagName}`);
            }
        });
        
        if (issues.length > 0) {
            console.warn(`${this.logPrefix} 表单完整性问题:`, issues);
        } else {
            console.log(`${this.logPrefix} 表单完整性检查通过`);
        }
        
        return issues;
    }
    
    /**
     * 创建表单数据快照
     */
    createFormSnapshot(form) {
        const snapshot = {
            timestamp: new Date().toISOString(),
            formId: form.id,
            data: {}
        };
        
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            snapshot.data[input.name] = {
                value: input.value,
                type: input.type || input.tagName.toLowerCase(),
                required: input.required,
                valid: input.checkValidity()
            };
        });
        
        return snapshot;
    }
}

// 创建全局调试器实例
window.formDebugger = new FormDataDebugger();

// 添加全局调试函数
window.debugTradeForm = function() {
    const form = document.getElementById('trade-form');
    if (form) {
        window.formDebugger.debugFormSerialization(form);
        return window.formDebugger.createFormSnapshot(form);
    } else {
        console.error('交易表单未找到');
        return null;
    }
};

// 自动监控交易表单（如果存在）
document.addEventListener('DOMContentLoaded', () => {
    const tradeForm = document.getElementById('trade-form');
    if (tradeForm) {
        window.formDebugger.monitorFormChanges(tradeForm);
        console.log('表单调试工具已激活，可以使用 debugTradeForm() 进行调试');
    }
});
