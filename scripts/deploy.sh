#!/bin/bash

# 历史交易记录功能部署脚本
# 用于自动化部署流程

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令未找到，请先安装"
        exit 1
    fi
}

# 检查Python版本
check_python_version() {
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    local major_version=$(echo $python_version | cut -d'.' -f1)
    local minor_version=$(echo $python_version | cut -d'.' -f2)
    
    if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 8 ]); then
        log_error "需要Python 3.8或更高版本，当前版本: $python_version"
        exit 1
    fi
    
    log_success "Python版本检查通过: $python_version"
}

# 检查虚拟环境
check_virtual_env() {
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warning "未检测到虚拟环境，建议使用虚拟环境"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "虚拟环境检查通过: $VIRTUAL_ENV"
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    pip install -r requirements.txt
    log_success "依赖安装完成"
}

# 配置存储
setup_storage() {
    log_info "配置存储目录和权限..."
    python3 scripts/setup_storage.py --env ${ENVIRONMENT}
    log_success "存储配置完成"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    # 先进行干运行检查
    log_info "执行迁移干运行检查..."
    python3 scripts/deploy_migrations.py --env ${ENVIRONMENT} --dry-run
    
    # 询问是否继续
    read -p "迁移检查通过，是否继续执行实际迁移? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 scripts/deploy_migrations.py --env ${ENVIRONMENT}
        log_success "数据库迁移完成"
    else
        log_warning "跳过数据库迁移"
    fi
}

# 运行部署测试
run_deployment_tests() {
    log_info "运行部署测试..."
    python3 scripts/deployment_test.py --env ${ENVIRONMENT} --base-url ${BASE_URL}
    log_success "部署测试完成"
}

# 创建初始备份
create_initial_backup() {
    log_info "创建初始备份..."
    python3 scripts/backup_restore.py backup --type full --env ${ENVIRONMENT}
    log_success "初始备份创建完成"
}

# 配置系统服务
setup_system_services() {
    if [ "$SETUP_SERVICES" = "true" ]; then
        log_info "配置系统服务..."
        
        # 检查是否有sudo权限
        if sudo -n true 2>/dev/null; then
            # 配置Nginx
            if [ -f "deployment/nginx.conf" ]; then
                sudo cp deployment/nginx.conf /etc/nginx/sites-available/historical-trading
                sudo ln -sf /etc/nginx/sites-available/historical-trading /etc/nginx/sites-enabled/
                sudo nginx -t && sudo systemctl reload nginx
                log_success "Nginx配置完成"
            fi
            
            # 配置systemd服务
            if [ -f "deployment/historical-trading.service" ]; then
                sudo cp deployment/historical-trading.service /etc/systemd/system/
                sudo systemctl daemon-reload
                sudo systemctl enable historical-trading
                log_success "systemd服务配置完成"
            fi
        else
            log_warning "需要sudo权限配置系统服务，请手动配置"
        fi
    else
        log_info "跳过系统服务配置"
    fi
}

# 显示部署后信息
show_post_deployment_info() {
    log_success "部署完成！"
    echo
    echo "后续步骤:"
    echo "1. 检查服务状态: sudo systemctl status historical-trading"
    echo "2. 查看应用日志: tail -f logs/app.log"
    echo "3. 访问应用: ${BASE_URL}"
    echo "4. 查看部署测试报告: deployment_test_report.json"
    echo
    echo "备份管理:"
    echo "- 列出备份: python3 scripts/backup_restore.py list --env ${ENVIRONMENT}"
    echo "- 创建备份: python3 scripts/backup_restore.py backup --type full --env ${ENVIRONMENT}"
    echo
    echo "监控命令:"
    echo "- 查看服务日志: sudo journalctl -u historical-trading -f"
    echo "- 查看Nginx日志: sudo tail -f /var/log/nginx/access.log"
}

# 主函数
main() {
    # 默认参数
    ENVIRONMENT="production"
    BASE_URL="http://localhost:5001"
    SETUP_SERVICES="false"
    SKIP_TESTS="false"
    SKIP_BACKUP="false"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --base-url)
                BASE_URL="$2"
                shift 2
                ;;
            --setup-services)
                SETUP_SERVICES="true"
                shift
                ;;
            --skip-tests)
                SKIP_TESTS="true"
                shift
                ;;
            --skip-backup)
                SKIP_BACKUP="true"
                shift
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --env ENV              设置环境 (development|production, 默认: production)"
                echo "  --base-url URL         设置应用URL (默认: http://localhost:5001)"
                echo "  --setup-services       配置系统服务 (需要sudo权限)"
                echo "  --skip-tests           跳过部署测试"
                echo "  --skip-backup          跳过初始备份"
                echo "  --help                 显示帮助信息"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    log_info "开始部署历史交易记录功能..."
    log_info "环境: ${ENVIRONMENT}"
    log_info "应用URL: ${BASE_URL}"
    
    # 检查系统要求
    log_info "检查系统要求..."
    check_command python3
    check_command pip
    check_python_version
    check_virtual_env
    
    # 安装依赖
    install_dependencies
    
    # 配置存储
    setup_storage
    
    # 运行数据库迁移
    run_migrations
    
    # 配置系统服务
    setup_system_services
    
    # 运行部署测试
    if [ "$SKIP_TESTS" != "true" ]; then
        run_deployment_tests
    else
        log_info "跳过部署测试"
    fi
    
    # 创建初始备份
    if [ "$SKIP_BACKUP" != "true" ]; then
        create_initial_backup
    else
        log_info "跳过初始备份"
    fi
    
    # 显示部署后信息
    show_post_deployment_info
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"