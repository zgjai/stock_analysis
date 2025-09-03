/**
 * 响应式工具类
 * 处理不同设备尺寸下的界面适配
 */
class ResponsiveUtils {
    constructor() {
        this.breakpoints = {
            xs: 0,
            sm: 576,
            md: 768,
            lg: 992,
            xl: 1200,
            xxl: 1400
        };
        
        this.currentBreakpoint = this.getCurrentBreakpoint();
        this.resizeHandlers = new Set();
        
        this.init();
    }

    init() {
        this.setupResizeListener();
        this.setupOrientationListener();
        this.detectTouchDevice();
        this.setupViewportMeta();
    }

    setupResizeListener() {
        let resizeTimer;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const newBreakpoint = this.getCurrentBreakpoint();
                
                if (newBreakpoint !== this.currentBreakpoint) {
                    const oldBreakpoint = this.currentBreakpoint;
                    this.currentBreakpoint = newBreakpoint;
                    
                    this.handleBreakpointChange(oldBreakpoint, newBreakpoint);
                }
                
                this.handleResize();
            }, 100);
        });
    }

    setupOrientationListener() {
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });
    }

    detectTouchDevice() {
        const isTouchDevice = 'ontouchstart' in window || 
                             navigator.maxTouchPoints > 0 || 
                             navigator.msMaxTouchPoints > 0;
        
        if (isTouchDevice) {
            document.body.classList.add('touch-device');
        } else {
            document.body.classList.add('no-touch');
        }
    }

    setupViewportMeta() {
        let viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            viewport = document.createElement('meta');
            viewport.name = 'viewport';
            viewport.content = 'width=device-width, initial-scale=1, shrink-to-fit=no';
            document.head.appendChild(viewport);
        }
    }

    getCurrentBreakpoint() {
        const width = window.innerWidth;
        
        if (width >= this.breakpoints.xxl) return 'xxl';
        if (width >= this.breakpoints.xl) return 'xl';
        if (width >= this.breakpoints.lg) return 'lg';
        if (width >= this.breakpoints.md) return 'md';
        if (width >= this.breakpoints.sm) return 'sm';
        return 'xs';
    }

    isMobile() {
        return this.currentBreakpoint === 'xs' || this.currentBreakpoint === 'sm';
    }

    isTablet() {
        return this.currentBreakpoint === 'md';
    }

    isDesktop() {
        return this.currentBreakpoint === 'lg' || 
               this.currentBreakpoint === 'xl' || 
               this.currentBreakpoint === 'xxl';
    }

    handleBreakpointChange(oldBreakpoint, newBreakpoint) {
        console.log(`Breakpoint changed: ${oldBreakpoint} -> ${newBreakpoint}`);
        
        // 更新body类
        document.body.classList.remove(`breakpoint-${oldBreakpoint}`);
        document.body.classList.add(`breakpoint-${newBreakpoint}`);
        
        // 触发自定义事件
        const event = new CustomEvent('breakpointChange', {
            detail: { oldBreakpoint, newBreakpoint }
        });
        document.dispatchEvent(event);
        
        // 调用特定的处理方法
        this.adaptHistoricalTradesTable();
        this.adaptModals();
        this.adaptFilters();
    }

    handleResize() {
        this.resizeHandlers.forEach(handler => {
            try {
                handler();
            } catch (error) {
                console.error('Resize handler error:', error);
            }
        });
    }

    handleOrientationChange() {
        console.log('Orientation changed');
        
        // 重新计算断点
        setTimeout(() => {
            const newBreakpoint = this.getCurrentBreakpoint();
            if (newBreakpoint !== this.currentBreakpoint) {
                this.handleBreakpointChange(this.currentBreakpoint, newBreakpoint);
            }
        }, 200);
    }

    // 历史交易表格适配
    adaptHistoricalTradesTable() {
        const table = document.getElementById('historical-trades-table');
        if (!table) return;

        if (this.isMobile()) {
            this.makeTableResponsive(table);
            this.hideNonEssentialColumns(table);
        } else {
            this.restoreTableColumns(table);
        }
    }

    makeTableResponsive(table) {
        // 添加响应式包装器
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }

        // 添加移动端样式
        table.classList.add('table-sm');
    }

    hideNonEssentialColumns(table) {
        const columnsToHide = ['holding-days', 'actions'];
        
        columnsToHide.forEach(columnClass => {
            const elements = table.querySelectorAll(`[data-column="${columnClass}"]`);
            elements.forEach(el => {
                el.style.display = 'none';
            });
        });

        // 合并股票信息列
        this.mergeStockInfoColumns(table);
    }

    mergeStockInfoColumns(table) {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const stockCodeCell = row.querySelector('[data-column="stock-code"]');
            const stockNameCell = row.querySelector('[data-column="stock-name"]');
            
            if (stockCodeCell && stockNameCell) {
                stockCodeCell.innerHTML = `
                    <div class="d-flex flex-column">
                        <strong>${stockCodeCell.textContent}</strong>
                        <small class="text-muted">${stockNameCell.textContent}</small>
                    </div>
                `;
                stockNameCell.style.display = 'none';
            }
        });
    }

    restoreTableColumns(table) {
        // 显示所有列
        const hiddenElements = table.querySelectorAll('[style*="display: none"]');
        hiddenElements.forEach(el => {
            el.style.display = '';
        });

        // 移除移动端样式
        table.classList.remove('table-sm');
    }

    // 模态框适配
    adaptModals() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(modal => {
            if (this.isMobile()) {
                modal.classList.add('modal-fullscreen-sm-down');
            } else {
                modal.classList.remove('modal-fullscreen-sm-down');
            }
        });
    }

    // 筛选器适配
    adaptFilters() {
        const filterContainer = document.querySelector('.filters-container');
        if (!filterContainer) return;

        if (this.isMobile()) {
            this.makeFiltersCollapsible(filterContainer);
        } else {
            this.restoreFiltersLayout(filterContainer);
        }
    }

    makeFiltersCollapsible(container) {
        // 创建折叠按钮
        let toggleBtn = container.querySelector('.filter-toggle-btn');
        if (!toggleBtn) {
            toggleBtn = document.createElement('button');
            toggleBtn.className = 'btn btn-outline-secondary filter-toggle-btn mb-2';
            toggleBtn.innerHTML = '<i class="bi bi-funnel"></i> 筛选条件';
            toggleBtn.type = 'button';
            toggleBtn.setAttribute('data-bs-toggle', 'collapse');
            toggleBtn.setAttribute('data-bs-target', '#filter-content');
            
            container.insertBefore(toggleBtn, container.firstChild);
        }

        // 包装筛选内容
        const filterContent = container.querySelector('.filter-content');
        if (filterContent && !filterContent.classList.contains('collapse')) {
            filterContent.classList.add('collapse');
            filterContent.id = 'filter-content';
        }
    }

    restoreFiltersLayout(container) {
        const toggleBtn = container.querySelector('.filter-toggle-btn');
        if (toggleBtn) {
            toggleBtn.remove();
        }

        const filterContent = container.querySelector('.filter-content');
        if (filterContent) {
            filterContent.classList.remove('collapse');
            filterContent.classList.add('show');
        }
    }

    // 图片上传器适配
    adaptImageUploader() {
        const uploaders = document.querySelectorAll('.image-uploader');
        
        uploaders.forEach(uploader => {
            if (this.isMobile()) {
                this.makeMobileImageUploader(uploader);
            } else {
                this.restoreDesktopImageUploader(uploader);
            }
        });
    }

    makeMobileImageUploader(uploader) {
        // 调整预览图片大小
        const previews = uploader.querySelectorAll('.image-preview-card');
        previews.forEach(preview => {
            preview.style.width = '100%';
            preview.style.marginBottom = '10px';
        });

        // 简化上传区域
        const uploadArea = uploader.querySelector('.upload-area');
        if (uploadArea) {
            uploadArea.style.padding = '20px 10px';
        }
    }

    restoreDesktopImageUploader(uploader) {
        const previews = uploader.querySelectorAll('.image-preview-card');
        previews.forEach(preview => {
            preview.style.width = '';
            preview.style.marginBottom = '';
        });

        const uploadArea = uploader.querySelector('.upload-area');
        if (uploadArea) {
            uploadArea.style.padding = '';
        }
    }

    // 注册resize处理器
    addResizeHandler(handler) {
        this.resizeHandlers.add(handler);
    }

    removeResizeHandler(handler) {
        this.resizeHandlers.delete(handler);
    }

    // 工具方法
    getViewportSize() {
        return {
            width: window.innerWidth,
            height: window.innerHeight
        };
    }

    getScrollbarWidth() {
        const outer = document.createElement('div');
        outer.style.visibility = 'hidden';
        outer.style.overflow = 'scroll';
        outer.style.msOverflowStyle = 'scrollbar';
        document.body.appendChild(outer);

        const inner = document.createElement('div');
        outer.appendChild(inner);

        const scrollbarWidth = outer.offsetWidth - inner.offsetWidth;
        outer.parentNode.removeChild(outer);

        return scrollbarWidth;
    }

    // 检测设备特性
    getDeviceInfo() {
        return {
            isMobile: this.isMobile(),
            isTablet: this.isTablet(),
            isDesktop: this.isDesktop(),
            breakpoint: this.currentBreakpoint,
            viewport: this.getViewportSize(),
            pixelRatio: window.devicePixelRatio || 1,
            isRetina: window.devicePixelRatio > 1,
            isTouch: document.body.classList.contains('touch-device')
        };
    }

    // CSS媒体查询检测
    matchMedia(query) {
        return window.matchMedia(query).matches;
    }

    // 预设媒体查询
    isLandscape() {
        return this.matchMedia('(orientation: landscape)');
    }

    isPortrait() {
        return this.matchMedia('(orientation: portrait)');
    }

    isPrintMode() {
        return this.matchMedia('print');
    }

    prefersReducedMotion() {
        return this.matchMedia('(prefers-reduced-motion: reduce)');
    }

    prefersDarkMode() {
        return this.matchMedia('(prefers-color-scheme: dark)');
    }
}

// 创建全局实例
window.responsiveUtils = new ResponsiveUtils();

// 导出类
window.ResponsiveUtils = ResponsiveUtils;