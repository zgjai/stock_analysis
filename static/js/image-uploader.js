/**
 * 图片上传组件
 * 负责处理复盘图片的上传、预览和管理
 */
class ImageUploader {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            maxFiles: 10,
            maxSize: 5 * 1024 * 1024, // 5MB
            allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            multiple: true,
            ...options
        };
        
        this.files = [];
        this.previews = [];
        
        this.init();
    }

    init() {
        this.createUploadInterface();
        this.setupEventListeners();
    }

    createUploadInterface() {
        this.container.innerHTML = `
            <div class="image-uploader">
                <div class="upload-area border-2 border-dashed rounded p-4 text-center" 
                     style="border-color: #dee2e6; transition: all 0.3s;">
                    <div class="upload-content">
                        <i class="bi bi-cloud-upload fs-1 text-muted mb-3"></i>
                        <h6 class="text-muted">拖拽图片到这里或点击选择</h6>
                        <p class="text-muted small mb-3">
                            支持 JPG、PNG、GIF、WebP 格式，单张图片不超过 ${this.formatFileSize(this.options.maxSize)}
                        </p>
                        <button type="button" class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-plus"></i> 选择图片
                        </button>
                    </div>
                    <input type="file" class="file-input d-none" 
                           ${this.options.multiple ? 'multiple' : ''} 
                           accept="${this.options.allowedTypes.join(',')}">
                </div>
                <div class="image-previews mt-3"></div>
                <div class="upload-progress mt-2" style="display: none;">
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                    </div>
                    <small class="text-muted">正在上传...</small>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        const uploadArea = this.container.querySelector('.upload-area');
        const fileInput = this.container.querySelector('.file-input');
        const selectButton = this.container.querySelector('.btn');

        // 点击选择文件
        selectButton.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('click', (e) => {
            if (e.target === uploadArea || e.target.closest('.upload-content')) {
                fileInput.click();
            }
        });

        // 文件选择
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files));

        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#007bff';
            uploadArea.style.backgroundColor = '#f8f9fa';
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#dee2e6';
            uploadArea.style.backgroundColor = 'transparent';
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#dee2e6';
            uploadArea.style.backgroundColor = 'transparent';
            
            const files = Array.from(e.dataTransfer.files);
            this.handleFileSelect(files);
        });
    }

    handleFileSelect(files) {
        const validFiles = this.validateFiles(Array.from(files));
        
        if (validFiles.length > 0) {
            this.addFiles(validFiles);
        }
    }

    validateFiles(files) {
        const validFiles = [];
        const errors = [];
        const warnings = [];

        files.forEach(file => {
            // 检查文件类型
            if (!this.options.allowedTypes.includes(file.type)) {
                errors.push(`${file.name}: 不支持的文件格式，仅支持 JPG、PNG、GIF、WebP`);
                return;
            }

            // 检查文件大小
            if (file.size > this.options.maxSize) {
                errors.push(`${file.name}: 文件大小 ${this.formatFileSize(file.size)} 超过 ${this.formatFileSize(this.options.maxSize)} 限制`);
                return;
            }

            // 检查文件数量
            if (this.files.length + validFiles.length >= this.options.maxFiles) {
                errors.push(`最多只能上传 ${this.options.maxFiles} 张图片`);
                return;
            }

            // 检查文件名长度
            if (file.name.length > 255) {
                warnings.push(`${file.name}: 文件名过长，将被截断`);
            }

            // 检查是否为重复文件
            const isDuplicate = this.files.some(existingFile => 
                existingFile.name === file.name && existingFile.size === file.size
            );
            
            if (isDuplicate) {
                warnings.push(`${file.name}: 文件已存在，将跳过`);
                return;
            }

            // 检查图片尺寸（异步，但先添加到有效文件列表）
            validFiles.push(file);
        });

        // 显示错误和警告
        if (errors.length > 0) {
            this.showMessage(errors.join('\n'), 'error');
        }
        
        if (warnings.length > 0) {
            this.showMessage(warnings.join('\n'), 'warning');
        }

        return validFiles;
    }

    // 异步验证图片尺寸
    async validateImageDimensions(file) {
        return new Promise((resolve) => {
            const img = new Image();
            const url = URL.createObjectURL(file);
            
            img.onload = () => {
                URL.revokeObjectURL(url);
                
                const warnings = [];
                
                // 检查图片尺寸
                if (img.width > 4000 || img.height > 4000) {
                    warnings.push(`${file.name}: 图片尺寸过大 (${img.width}x${img.height})，建议压缩后上传`);
                }
                
                if (img.width < 100 || img.height < 100) {
                    warnings.push(`${file.name}: 图片尺寸过小 (${img.width}x${img.height})，可能影响显示效果`);
                }
                
                resolve({ valid: true, warnings });
            };
            
            img.onerror = () => {
                URL.revokeObjectURL(url);
                resolve({ valid: false, warnings: [`${file.name}: 无法读取图片文件`] });
            };
            
            img.src = url;
        });
    }

    addFiles(files) {
        files.forEach(file => {
            const fileId = this.generateFileId();
            const fileData = {
                id: fileId,
                file: file,
                name: file.name,
                size: file.size,
                type: file.type,
                description: ''
            };

            this.files.push(fileData);
            this.createPreview(fileData);
        });

        this.updateUploadArea();
    }

    createPreview(fileData) {
        const previewContainer = this.container.querySelector('.image-previews');
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewElement = document.createElement('div');
            previewElement.className = 'image-preview-card d-inline-block me-2 mb-2';
            previewElement.dataset.fileId = fileData.id;
            
            previewElement.innerHTML = `
                <div class="card" style="width: 180px;">
                    <div class="position-relative">
                        <img src="${e.target.result}" class="card-img-top" 
                             style="height: 120px; object-fit: cover;" alt="${fileData.name}">
                        <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 remove-btn" 
                                style="transform: translate(50%, -50%);" title="删除图片">
                            <i class="bi bi-x"></i>
                        </button>
                    </div>
                    <div class="card-body p-2">
                        <input type="text" class="form-control form-control-sm mb-1 description-input" 
                               placeholder="图片描述..." maxlength="100" 
                               value="${fileData.description}">
                        <small class="text-muted d-block text-truncate" title="${fileData.name}">
                            ${fileData.name}
                        </small>
                        <small class="text-muted">${this.formatFileSize(fileData.size)}</small>
                    </div>
                </div>
            `;

            // 添加事件监听器
            const removeBtn = previewElement.querySelector('.remove-btn');
            removeBtn.addEventListener('click', () => this.removeFile(fileData.id));

            const descriptionInput = previewElement.querySelector('.description-input');
            descriptionInput.addEventListener('input', (e) => {
                fileData.description = e.target.value;
            });

            previewContainer.appendChild(previewElement);
            this.previews.push(previewElement);
        };

        reader.readAsDataURL(fileData.file);
    }

    removeFile(fileId) {
        // 从文件列表中移除
        this.files = this.files.filter(file => file.id !== fileId);
        
        // 移除预览元素
        const previewElement = this.container.querySelector(`[data-file-id="${fileId}"]`);
        if (previewElement) {
            previewElement.remove();
        }
        
        this.previews = this.previews.filter(preview => 
            preview.dataset.fileId !== fileId
        );

        this.updateUploadArea();
    }

    updateUploadArea() {
        const uploadArea = this.container.querySelector('.upload-area');
        const hasFiles = this.files.length > 0;
        const maxReached = this.files.length >= this.options.maxFiles;

        if (maxReached) {
            uploadArea.style.display = 'none';
        } else {
            uploadArea.style.display = 'block';
        }

        // 更新提示文本
        const uploadContent = uploadArea.querySelector('.upload-content h6');
        if (hasFiles) {
            uploadContent.textContent = `已选择 ${this.files.length} 张图片，${maxReached ? '已达上限' : '可继续添加'}`;
        } else {
            uploadContent.textContent = '拖拽图片到这里或点击选择';
        }
    }

    async uploadFiles(reviewId, onProgress = null) {
        if (this.files.length === 0) {
            return { success: true, data: [] };
        }

        const formData = new FormData();
        
        // 添加文件
        this.files.forEach(fileData => {
            formData.append('images', fileData.file);
        });
        
        // 添加描述
        this.files.forEach(fileData => {
            formData.append('descriptions', fileData.description || '');
        });

        try {
            this.showProgress(true);
            
            const response = await this.uploadWithRetry(
                reviewId, 
                formData, 
                onProgress,
                3 // 最多重试3次
            );

            this.showProgress(false);
            
            if (response.success) {
                this.showMessage('图片上传成功', 'success');
                this.clear(); // 清空已上传的文件
            }
            
            return response;
        } catch (error) {
            this.showProgress(false);
            this.handleUploadError(error);
            throw error;
        }
    }

    async uploadWithRetry(reviewId, formData, onProgress, maxRetries) {
        let lastError;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const response = await apiClient.request(
                    'POST', 
                    `/trade-reviews/${reviewId}/images`, 
                    formData,
                    {
                        timeout: 60000, // 60秒超时
                        onUploadProgress: (progressEvent) => {
                            const percentCompleted = Math.round(
                                (progressEvent.loaded * 100) / progressEvent.total
                            );
                            this.updateProgress(percentCompleted);
                            
                            if (onProgress) {
                                onProgress(percentCompleted);
                            }
                        }
                    }
                );

                return response;
            } catch (error) {
                lastError = error;
                
                // 如果不是网络错误或服务器错误，不重试
                if (!this.shouldRetry(error)) {
                    throw error;
                }
                
                if (attempt < maxRetries) {
                    this.showMessage(`上传失败，正在重试 (${attempt}/${maxRetries})...`, 'warning');
                    await this.delay(1000 * attempt); // 递增延迟
                }
            }
        }
        
        throw lastError;
    }

    shouldRetry(error) {
        // 网络错误或5xx服务器错误可以重试
        if (!error.response) return true; // 网络错误
        
        const status = error.response.status;
        return status >= 500 || status === 408 || status === 429; // 服务器错误、超时、限流
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    handleUploadError(error) {
        let message = '图片上传失败';
        
        if (error.response) {
            const status = error.response.status;
            const data = error.response.data;
            
            switch (status) {
                case 400:
                    message = '上传的文件格式不正确';
                    break;
                case 413:
                    message = '上传的文件过大';
                    break;
                case 422:
                    message = '文件验证失败';
                    if (data.errors) {
                        message += '：' + Object.values(data.errors).flat().join('，');
                    }
                    break;
                case 429:
                    message = '上传过于频繁，请稍后重试';
                    break;
                case 500:
                    message = '服务器错误，请稍后重试';
                    break;
                default:
                    message = data.message || `上传失败 (${status})`;
            }
        } else if (error.request) {
            message = '网络连接失败，请检查网络连接';
        } else {
            message = error.message || '未知错误';
        }
        
        this.showMessage(message, 'error');
    }

    showProgress(show) {
        const progressContainer = this.container.querySelector('.upload-progress');
        progressContainer.style.display = show ? 'block' : 'none';
        
        if (!show) {
            this.updateProgress(0);
        }
    }

    updateProgress(percent) {
        const progressBar = this.container.querySelector('.progress-bar');
        progressBar.style.width = `${percent}%`;
        progressBar.setAttribute('aria-valuenow', percent);
    }

    getFiles() {
        return this.files;
    }

    getFileCount() {
        return this.files.length;
    }

    clear() {
        this.files = [];
        this.previews = [];
        
        const previewContainer = this.container.querySelector('.image-previews');
        previewContainer.innerHTML = '';
        
        this.updateUploadArea();
    }

    generateFileId() {
        return 'file_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // 图片压缩功能
    async compressImage(file, maxWidth = 1920, maxHeight = 1080, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                // 计算新尺寸
                let { width, height } = this.calculateNewDimensions(
                    img.width, 
                    img.height, 
                    maxWidth, 
                    maxHeight
                );
                
                canvas.width = width;
                canvas.height = height;
                
                // 绘制压缩后的图片
                ctx.drawImage(img, 0, 0, width, height);
                
                // 转换为Blob
                canvas.toBlob((blob) => {
                    // 创建新的File对象
                    const compressedFile = new File([blob], file.name, {
                        type: file.type,
                        lastModified: Date.now()
                    });
                    
                    resolve(compressedFile);
                }, file.type, quality);
            };
            
            img.onerror = () => resolve(file); // 压缩失败时返回原文件
            img.src = URL.createObjectURL(file);
        });
    }

    calculateNewDimensions(originalWidth, originalHeight, maxWidth, maxHeight) {
        let width = originalWidth;
        let height = originalHeight;
        
        // 如果图片尺寸超过限制，按比例缩放
        if (width > maxWidth || height > maxHeight) {
            const ratio = Math.min(maxWidth / width, maxHeight / height);
            width = Math.round(width * ratio);
            height = Math.round(height * ratio);
        }
        
        return { width, height };
    }

    // 批量处理文件
    async processFiles(files) {
        const processedFiles = [];
        const totalFiles = files.length;
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            try {
                // 更新处理进度
                this.updateProcessingProgress(i + 1, totalFiles);
                
                // 验证图片尺寸
                const validation = await this.validateImageDimensions(file);
                
                if (!validation.valid) {
                    this.showMessage(validation.warnings.join('\n'), 'error');
                    continue;
                }
                
                // 如果文件过大，进行压缩
                let processedFile = file;
                if (file.size > 2 * 1024 * 1024) { // 2MB以上压缩
                    processedFile = await this.compressImage(file);
                    
                    if (processedFile.size < file.size) {
                        this.showMessage(
                            `${file.name} 已压缩：${this.formatFileSize(file.size)} → ${this.formatFileSize(processedFile.size)}`, 
                            'info'
                        );
                    }
                }
                
                processedFiles.push(processedFile);
                
                // 显示警告（如果有）
                if (validation.warnings.length > 0) {
                    this.showMessage(validation.warnings.join('\n'), 'warning');
                }
                
            } catch (error) {
                console.error('Process file error:', error);
                this.showMessage(`处理文件 ${file.name} 时出错`, 'error');
            }
        }
        
        this.hideProcessingProgress();
        return processedFiles;
    }

    updateProcessingProgress(current, total) {
        const percent = Math.round((current / total) * 100);
        
        // 显示处理进度
        let progressElement = this.container.querySelector('.processing-progress');
        if (!progressElement) {
            progressElement = document.createElement('div');
            progressElement.className = 'processing-progress mt-2';
            progressElement.innerHTML = `
                <div class="progress">
                    <div class="progress-bar bg-info" role="progressbar" style="width: 0%"></div>
                </div>
                <small class="text-muted">正在处理图片...</small>
            `;
            this.container.appendChild(progressElement);
        }
        
        const progressBar = progressElement.querySelector('.progress-bar');
        const progressText = progressElement.querySelector('small');
        
        progressBar.style.width = `${percent}%`;
        progressText.textContent = `正在处理图片 ${current}/${total}...`;
    }

    hideProcessingProgress() {
        const progressElement = this.container.querySelector('.processing-progress');
        if (progressElement) {
            progressElement.remove();
        }
    }

    // 拖拽排序功能
    enableDragSort() {
        const previewContainer = this.container.querySelector('.image-previews');
        if (!previewContainer) return;
        
        // 使用简单的拖拽排序
        let draggedElement = null;
        
        previewContainer.addEventListener('dragstart', (e) => {
            if (e.target.closest('.image-preview-card')) {
                draggedElement = e.target.closest('.image-preview-card');
                e.dataTransfer.effectAllowed = 'move';
            }
        });
        
        previewContainer.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        });
        
        previewContainer.addEventListener('drop', (e) => {
            e.preventDefault();
            
            if (draggedElement) {
                const dropTarget = e.target.closest('.image-preview-card');
                
                if (dropTarget && dropTarget !== draggedElement) {
                    const rect = dropTarget.getBoundingClientRect();
                    const midpoint = rect.left + rect.width / 2;
                    
                    if (e.clientX < midpoint) {
                        previewContainer.insertBefore(draggedElement, dropTarget);
                    } else {
                        previewContainer.insertBefore(draggedElement, dropTarget.nextSibling);
                    }
                    
                    // 更新文件顺序
                    this.updateFileOrder();
                }
                
                draggedElement = null;
            }
        });
    }

    updateFileOrder() {
        const previewCards = this.container.querySelectorAll('.image-preview-card');
        const newOrder = [];
        
        previewCards.forEach(card => {
            const fileId = card.dataset.fileId;
            const file = this.files.find(f => f.id === fileId);
            if (file) {
                newOrder.push(file);
            }
        });
        
        this.files = newOrder;
    }

    showMessage(message, type = 'info') {
        // 使用全局消息系统
        if (window.showMessage) {
            window.showMessage(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// 导出类
window.ImageUploader = ImageUploader;