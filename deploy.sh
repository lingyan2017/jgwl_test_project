#!/bin/bash
# JGWL 管理系统快速部署脚本
# 适用于 Ubuntu/CentOS

set -e

echo "======================================"
echo "  JGWL 管理系统部署脚本"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用 root 权限运行此脚本${NC}"
    exit 1
fi

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo -e "${RED}无法检测操作系统${NC}"
    exit 1
fi

echo -e "${GREEN}检测到操作系统: $OS $VER${NC}"
echo ""

# 询问用户配置
read -p "请输入服务器域名或IP (默认: localhost): " DOMAIN
DOMAIN=${DOMAIN:-localhost}

read -p "请输入后端端口 (默认: 8030): " BACKEND_PORT
BACKEND_PORT=${BACKEND_PORT:-8030}

read -p "请输入项目部署目录 (默认: /opt/jgwl_project): " DEPLOY_DIR
DEPLOY_DIR=${DEPLOY_DIR:-/opt/jgwl_project}

echo ""
echo -e "${YELLOW}开始部署...${NC}"
echo ""

# 1. 安装系统依赖
echo -e "${GREEN}[1/8] 安装系统依赖...${NC}"
if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
    apt update && apt upgrade -y
    apt install -y python3 python3-pip python3-venv nginx mysql-server nodejs npm git curl wget
elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]]; then
    yum update -y
    yum install -y epel-release
    yum install -y python3 python3-pip nginx mysql-server nodejs npm git curl wget
else
    echo -e "${RED}不支持的操作系统${NC}"
    exit 1
fi

# 2. 创建部署目录
echo -e "${GREEN}[2/8] 创建部署目录...${NC}"
mkdir -p $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/logs
mkdir -p /var/www/jgwl

# 3. 复制项目文件（假设脚本在项目根目录运行）
echo -e "${GREEN}[3/8] 复制项目文件...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp -r $SCRIPT_DIR/* $DEPLOY_DIR/

# 4. 设置后端环境
echo -e "${GREEN}[4/8] 设置后端环境...${NC}"
cd $DEPLOY_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt 2>/dev/null || pip install .

# 5. 构建前端
echo -e "${GREEN}[5/8] 构建前端...${NC}"
cd $DEPLOY_DIR/frontend
npm install
npm run build

# 复制构建文件到 Nginx 目录
cp -r dist/* /var/www/jgwl/
chown -R www-data:www-data /var/www/jgwl 2>/dev/null || chown -R nginx:nginx /var/www/jgwl

# 6. 配置 Nginx
echo -e "${GREEN}[6/8] 配置 Nginx...${NC}"
cd $DEPLOY_DIR
sed -i "s/your-domain.com/$DOMAIN/g" nginx/jgwl.conf
sed -i "s/8030/$BACKEND_PORT/g" nginx/jgwl.conf

cp nginx/jgwl.conf /etc/nginx/conf.d/jgwl.conf

# 测试 Nginx 配置
nginx -t

# 7. 配置 systemd 服务
echo -e "${GREEN}[7/8] 配置 systemd 服务...${NC}"
sed -i "s|/opt/jgwl_project|$DEPLOY_DIR|g" systemd/jgwl-backend.service
sed -i "s/8030/$BACKEND_PORT/g" systemd/jgwl-backend.service

cp systemd/jgwl-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable jgwl-backend

# 8. 初始化数据库
echo -e "${GREEN}[8/8] 初始化数据库...${NC}"
source $DEPLOY_DIR/venv/bin/activate
cd $DEPLOY_DIR
python init_db.py 2>/dev/null || echo -e "${YELLOW}数据库初始化跳过（请手动执行）${NC}"

# 启动服务
echo ""
echo -e "${GREEN}启动服务...${NC}"
systemctl start jgwl-backend
systemctl restart nginx

# 检查服务状态
echo ""
echo -e "${GREEN}检查服务状态...${NC}"
echo "后端服务:"
systemctl is-active jgwl-backend
echo "Nginx 服务:"
systemctl is-active nginx

# 完成
echo ""
echo "======================================"
echo -e "${GREEN}  部署完成！${NC}"
echo "======================================"
echo ""
echo "访问地址: http://$DOMAIN"
echo "API 文档: http://$DOMAIN/docs"
echo ""
echo "默认管理员账号:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo -e "${YELLOW}重要提示:${NC}"
echo "1. 请立即修改管理员密码"
echo "2. 生产环境请配置 HTTPS"
echo "3. 请修改 .env 文件中的 SECRET_KEY"
echo "4. 查看日志: journalctl -u jgwl-backend -f"
echo ""
echo "常用命令:"
echo "  查看后端日志: journalctl -u jgwl-backend -f"
echo "  查看 Nginx 日志: tail -f /var/log/nginx/jgwl-error.log"
echo "  重启后端: systemctl restart jgwl-backend"
echo "  重启 Nginx: systemctl restart nginx"
echo ""
