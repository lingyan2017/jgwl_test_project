# JGWL 管理系统 - Nginx 部署文档

## 📋 目录
- [环境要求](#环境要求)
- [部署架构](#部署架构)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [Nginx 配置](#nginx-配置)
- [数据库配置](#数据库配置)
- [启动服务](#启动服务)
- [常见问题](#常见问题)

---

## 环境要求

### 服务器要求
- **操作系统**: Linux (CentOS 7+/Ubuntu 18.04+) 或 Windows Server
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 至少 10GB 可用空间
- **CPU**: 2核及以上

### 软件要求
- **Python**: 3.10+
- **Node.js**: 18+ (仅构建时需要)
- **MySQL**: 5.7+ 或 8.0+
- **Nginx**: 1.18+
- **Git**: 2.0+

---

## 部署架构

```
客户端浏览器
    ↓
Nginx (端口 80/443)
    ├── 静态文件 (前端页面)
    └── 反向代理 → FastAPI 后端 (端口 8030)
                        ↓
                    MySQL 数据库
```

**访问流程**：
1. 用户访问 `http://your-domain.com`
2. Nginx 返回前端静态文件
3. 前端请求 `/api/v1/*` 时，Nginx 反向代理到后端服务
4. 后端处理业务逻辑并访问数据库

---

## 后端部署

### 1. 准备项目代码

```bash
# 克隆或上传项目代码到服务器
cd /opt
git clone <your-repository-url> jgwl_project
cd jgwl_project

# 或者使用 FTP/SFTP 上传代码
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 如果使用 pyproject.toml
pip install .
```

### 4. 配置环境变量

创建 `.env` 文件（生产环境）：

```bash
# 数据库配置
DB_HOST=123.56.164.133
DB_PORT=3306
DB_USER=root
DB_PASSWORD=1qaz3edc
DB_NAME=jgwl_db

# JWT 配置（生产环境请修改为强密钥）
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AES 加密配置（如果有）
AES_KEY=your-aes-key-here
AES_IV=your-aes-iv-here
```

**⚠️ 重要**：生产环境必须修改 `SECRET_KEY` 为强随机字符串！

### 5. 初始化数据库

```bash
# 确保 MySQL 服务已启动
# 执行初始化脚本
python init_db.py

# 或者手动执行 SQL 文件
mysql -h 123.56.164.133 -u root -p jgwl_db < sql/init.sql
```

### 6. 测试后端服务

```bash
# 启动后端服务（测试用）
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8030

# 访问 http://服务器IP:8030/docs 验证 API 文档
```

### 7. 配置 systemd 服务（Linux 推荐）

创建服务文件 `/etc/systemd/system/jgwl-backend.service`：

```ini
[Unit]
Description=JGWL Backend Service
After=network.target mysql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/jgwl_project
Environment="PATH=/opt/jgwl_project/venv/bin"
ExecStart=/opt/jgwl_project/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8030 --workers 4
Restart=always
RestartSec=10

# 日志配置
StandardOutput=append:/opt/jgwl_project/logs/backend.log
StandardError=append:/opt/jgwl_project/logs/backend-error.log

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable jgwl-backend

# 启动服务
sudo systemctl start jgwl-backend

# 查看状态
sudo systemctl status jgwl-backend

# 查看日志
sudo journalctl -u jgwl-backend -f
```

---

## 前端部署

### 1. 安装依赖并构建

```bash
cd /opt/jgwl_project/frontend

# 安装依赖
npm install
# 或使用 pnpm
pnpm install

# 构建生产版本
npm run build
# 或
pnpm build
```

构建完成后，会在 `frontend/dist` 目录生成静态文件。

### 2. 配置生产环境 API 地址

如果需要修改 API 地址，可以在构建前设置环境变量：

创建 `frontend/.env.production`：

```env
VITE_API_BASE_URL=http://your-domain.com/api
```

修改 `frontend/src/utils/request.ts`，使用环境变量：

```typescript
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
})
```

然后重新构建：

```bash
npm run build
```

### 3. 复制静态文件到 Nginx 目录

```bash
# 创建 Nginx 网站目录
sudo mkdir -p /var/www/jgwl

# 复制构建文件
sudo cp -r dist/* /var/www/jgwl/

# 设置权限
sudo chown -R www-data:www-data /var/www/jgwl
sudo chmod -R 755 /var/www/jgwl
```

---

## Nginx 配置

### 1. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install epel-release
sudo yum install nginx

# 启动 Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. 创建 Nginx 配置文件

创建 `/etc/nginx/conf.d/jgwl.conf`：

```nginx
# JGWL 管理系统 Nginx 配置

# HTTP 服务器配置
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # 修改为你的域名
    
    # 字符集
    charset utf-8;
    
    # 访问日志和错误日志
    access_log /var/log/nginx/jgwl-access.log;
    error_log /var/log/nginx/jgwl-error.log;
    
    # 客户端最大上传大小
    client_max_body_size 50M;
    
    # 前端静态文件根目录
    root /var/www/jgwl;
    index index.html;
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;
    
    # 静态资源缓存配置
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # HTML 文件不缓存
    location ~* \.html$ {
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
    }
    
    # 前端路由支持（Vue Router history 模式）
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8030;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Swagger 文档代理
    location /docs {
        proxy_pass http://127.0.0.1:8030;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /openapi.json {
        proxy_pass http://127.0.0.1:8030;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# HTTPS 配置（可选，推荐使用 Let's Encrypt）
# server {
#     listen 443 ssl http2;
#     server_name your-domain.com www.your-domain.com;
#     
#     # SSL 证书配置
#     ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
#     ssl_trusted_certificate /etc/letsencrypt/live/your-domain.com/chain.pem;
#     
#     # SSL 优化配置
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#     ssl_prefer_server_ciphers on;
#     ssl_session_cache shared:SSL:10m;
#     ssl_session_timeout 10m;
#     
#     # HSTS
#     add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
#     
#     # 其他配置同上...
#     # ...
#     
#     # HTTP 重定向到 HTTPS
#     # 在上面的 HTTP server 块中添加：
#     # return 301 https://$server_name$request_uri;
# }
```

### 3. 测试并重启 Nginx

```bash
# 测试配置文件语法
sudo nginx -t

# 如果测试通过，重启 Nginx
sudo systemctl restart nginx

# 查看 Nginx 状态
sudo systemctl status nginx

# 查看错误日志（如果有问题）
sudo tail -f /var/log/nginx/jgwl-error.log
```

### 4. 配置防火墙

```bash
# Ubuntu (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 数据库配置

### 1. 确保 MySQL 可远程访问（如果需要）

```sql
-- 登录 MySQL
mysql -u root -p

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS jgwl_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建专用用户（推荐）
CREATE USER 'jgwl_user'@'localhost' IDENTIFIED BY 'strong-password';
GRANT ALL PRIVILEGES ON jgwl_db.* TO 'jgwl_user'@'localhost';
FLUSH PRIVILEGES;

-- 如果需要远程访问
CREATE USER 'jgwl_user'@'%' IDENTIFIED BY 'strong-password';
GRANT ALL PRIVILEGES ON jgwl_db.* TO 'jgwl_user'@'%';
FLUSH PRIVILEGES;
```

### 2. 修改 MySQL 配置（如果需要远程访问）

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`：

```ini
[mysqld]
bind-address = 0.0.0.0  # 允许所有 IP 连接（注意安全）
# 或
bind-address = 127.0.0.1  # 仅本地连接（更安全）
```

重启 MySQL：

```bash
sudo systemctl restart mysql
```

---

## 启动服务

### 完整启动顺序

```bash
# 1. 启动 MySQL（如果未启动）
sudo systemctl start mysql

# 2. 启动后端服务
sudo systemctl start jgwl-backend

# 3. 启动 Nginx
sudo systemctl start nginx

# 4. 检查所有服务状态
sudo systemctl status mysql
sudo systemctl status jgwl-backend
sudo systemctl status nginx
```

### 访问系统

打开浏览器访问：
- **HTTP**: `http://your-domain.com`
- **HTTPS**: `https://your-domain.com`（如果配置了 SSL）

默认管理员账号（参考 `sql/init.sql`）：
- 用户名: `admin`
- 密码: `admin123`

**⚠️ 首次登录后请立即修改密码！**

---

## 常见问题

### 1. 502 Bad Gateway

**原因**: 后端服务未启动或 Nginx 无法连接到后端

**解决**:
```bash
# 检查后端服务状态
sudo systemctl status jgwl-backend

# 查看后端日志
sudo journalctl -u jgwl-backend -f

# 检查后端是否在监听 8030 端口
sudo netstat -tlnp | grep 8030

# 重启后端服务
sudo systemctl restart jgwl-backend
```

### 2. 404 Not Found（前端路由）

**原因**: Nginx 未正确配置 Vue Router history 模式

**解决**: 确保 Nginx 配置中有：
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 3. CORS 错误

**原因**: 跨域请求被阻止

**解决**: 
- 确保 Nginx 正确代理 `/api/` 路径
- 检查后端 CORS 配置（`main.py`）

### 4. 静态文件 404

**原因**: 文件路径或权限问题

**解决**:
```bash
# 检查文件是否存在
ls -la /var/www/jgwl/

# 检查权限
sudo chown -R www-data:www-data /var/www/jgwl
sudo chmod -R 755 /var/www/jgwl

# 检查 Nginx 配置中的 root 路径
cat /etc/nginx/conf.d/jgwl.conf | grep root
```

### 5. 数据库连接失败

**原因**: 数据库配置错误或网络问题

**解决**:
```bash
# 测试数据库连接
mysql -h 123.56.164.133 -u root -p jgwl_db

# 检查后端日志
sudo journalctl -u jgwl-backend -f

# 验证 .env 文件配置
cat /opt/jgwl_project/.env
```

### 6. 后端服务自动停止

**原因**: 内存不足或其他错误

**解决**:
```bash
# 查看系统日志
dmesg | grep -i kill

# 增加 systemd 重启策略
# 编辑 /etc/systemd/system/jgwl-backend.service
Restart=always
RestartSec=10

# 监控资源使用
htop
```

### 7. Nginx 权限 denied

**解决**:
```bash
# 确保 Nginx 用户有读取权限
sudo chown -R www-data:www-data /var/www/jgwl
sudo chmod -R 755 /var/www/jgwl

# 检查 SELinux（CentOS）
sudo setenforce 0  # 临时禁用测试
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/jgwl(/.*)?"
sudo restorecon -R /var/www/jgwl
```

---

## 性能优化建议

### 1. Nginx 优化

```nginx
# 在 /etc/nginx/nginx.conf 的 http 块中添加
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 65535;
    use epoll;
    multi_accept on;
}

http {
    # 开启 sendfile
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    
    # 保持连接
    keepalive_timeout 65;
    keepalive_requests 1000;
    
    # 客户端 body 缓冲区
    client_body_buffer_size 10K;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
}
```

### 2. 后端优化

```python
# main.py - 使用多进程
uvicorn.run(
    app="main:app",
    host="0.0.0.0",
    port=8030,
    workers=4,  # CPU 核心数
    loop="uvloop",  # 更快的异步循环
)
```

### 3. 数据库优化

```sql
-- 添加索引
ALTER TABLE sys_menu ADD INDEX idx_parent_id (parent_id);
ALTER TABLE sys_user ADD INDEX idx_username (username);
ALTER TABLE sys_role_menu ADD INDEX idx_role_id (role_id);
```

---

## 监控和维护

### 1. 日志管理

```bash
# 查看后端日志
sudo journalctl -u jgwl-backend -f

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/jgwl-access.log

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/jgwl-error.log

# 日志轮转配置 /etc/logrotate.d/jgwl
/var/log/nginx/jgwl-*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### 2. 备份策略

```bash
#!/bin/bash
# backup.sh - 数据库备份脚本

BACKUP_DIR="/backup/jgwl_db"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -h 123.56.164.133 -u root -p'1qaz3edc' jgwl_db > $BACKUP_DIR/jgwl_db_$DATE.sql

# 压缩备份
gzip $BACKUP_DIR/jgwl_db_$DATE.sql

# 删除 30 天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: jgwl_db_$DATE.sql.gz"
```

设置定时任务：

```bash
# 每天凌晨 2 点备份
crontab -e
0 2 * * * /opt/jgwl_project/backup.sh >> /var/log/jgwl_backup.log 2>&1
```

### 3. 健康检查

```bash
#!/bin/bash
# health_check.sh

# 检查后端服务
if curl -s http://127.0.0.1:8030/ | grep -q "JGWL"; then
    echo "✓ Backend is running"
else
    echo "✗ Backend is down"
    sudo systemctl restart jgwl-backend
fi

# 检查 Nginx
if curl -s http://localhost/ | grep -q "index.html"; then
    echo "✓ Nginx is running"
else
    echo "✗ Nginx is down"
    sudo systemctl restart nginx
fi

# 检查数据库
if mysql -h 123.56.164.133 -u root -p'1qaz3edc' -e "SELECT 1" &>/dev/null; then
    echo "✓ Database is accessible"
else
    echo "✗ Database connection failed"
fi
```

---

## 安全建议

1. **修改默认密码**: 首次部署后立即修改管理员密码
2. **使用 HTTPS**: 生产环境必须使用 SSL 证书
3. **防火墙配置**: 只开放必要端口（80, 443）
4. **定期更新**: 及时更新系统和依赖包
5. **备份数据**: 定期备份数据库和配置文件
6. **监控日志**: 定期检查日志发现异常
7. **限制访问**: 使用 IP 白名单限制管理后台访问
8. **强密码策略**: 使用强密码和密钥

---

## 快速部署脚本

创建 `deploy.sh`：

```bash
#!/bin/bash
set -e

echo "=== JGWL 系统部署脚本 ==="

# 1. 更新系统
echo "更新系统..."
sudo apt update && sudo apt upgrade -y

# 2. 安装依赖
echo "安装依赖..."
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server nodejs npm

# 3. 部署后端
echo "部署后端..."
cd /opt/jgwl_project
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. 构建前端
echo "构建前端..."
cd frontend
npm install
npm run build
sudo cp -r dist/* /var/www/jgwl/
sudo chown -R www-data:www-data /var/www/jgwl

# 5. 配置 Nginx
echo "配置 Nginx..."
sudo cp ../nginx/jgwl.conf /etc/nginx/conf.d/
sudo nginx -t
sudo systemctl restart nginx

# 6. 配置后端服务
echo "配置后端服务..."
sudo cp ../systemd/jgwl-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jgwl-backend
sudo systemctl start jgwl-backend

# 7. 初始化数据库
echo "初始化数据库..."
python ../init_db.py

echo "=== 部署完成 ==="
echo "访问: http://$(hostname -I | awk '{print $1}')"
echo "默认账号: admin / admin123"
```

---

## 联系支持

如有问题，请查看：
- 项目 README
- 日志文件
- GitHub Issues

---

**最后更新**: 2026-04-16
**版本**: 1.0.0
