# JGWL 管理系统 - 快速开始指南

## 🚀 5分钟快速部署

### 方法一：使用自动部署脚本（推荐）

```bash
# 1. 上传项目到服务器
scp -r jgwl_test_project user@server:/opt/

# 2. SSH 登录服务器
ssh user@server

# 3. 进入项目目录
cd /opt/jgwl_test_project

# 4. 赋予执行权限
chmod +x deploy.sh

# 5. 运行部署脚本（需要 root 权限）
sudo ./deploy.sh
```

脚本会自动完成：
- ✅ 安装所有依赖（Python, Node.js, Nginx, MySQL）
- ✅ 配置虚拟环境
- ✅ 构建前端
- ✅ 配置 Nginx
- ✅ 配置 systemd 服务
- ✅ 初始化数据库

---

### 方法二：手动部署

#### 步骤 1: 准备环境

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server nodejs npm

# CentOS/RHEL
sudo yum install -y epel-release
sudo yum install -y python3 python3-pip nginx mysql-server nodejs npm
```

#### 步骤 2: 部署后端

```bash
# 创建项目目录
sudo mkdir -p /opt/jgwl_project
cd /opt/jgwl_project

# 上传或克隆代码
git clone <your-repo> .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 初始化数据库
python init_db.py
```

#### 步骤 3: 构建前端

```bash
cd frontend
npm install
npm run build

# 复制到 Nginx 目录
sudo mkdir -p /var/www/jgwl
sudo cp -r dist/* /var/www/jgwl/
sudo chown -R www-data:www-data /var/www/jgwl
```

#### 步骤 4: 配置 Nginx

```bash
# 复制配置文件
sudo cp nginx/jgwl.conf /etc/nginx/conf.d/jgwl.conf

# 编辑配置，修改域名
sudo nano /etc/nginx/conf.d/jgwl.conf

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 步骤 5: 配置后端服务

```bash
# 复制 systemd 配置
sudo cp systemd/jgwl-backend.service /etc/systemd/system/

# 重新加载并启动
sudo systemctl daemon-reload
sudo systemctl enable jgwl-backend
sudo systemctl start jgwl-backend

# 检查状态
sudo systemctl status jgwl-backend
```

---

## 📝 配置文件说明

### 1. 后端配置 (.env)

```env
# 数据库配置
DB_HOST=123.56.164.133
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=jgwl_db

# JWT 配置（生产环境必须修改）
SECRET_KEY=change-this-to-a-random-string-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 2. Nginx 配置 (nginx/jgwl.conf)

主要修改项：
```nginx
server_name your-domain.com;  # 改为你的域名或IP
root /var/www/jgwl;           # 前端文件路径
proxy_pass http://127.0.0.1:8030;  # 后端地址
```

### 3. Systemd 配置 (systemd/jgwl-backend.service)

主要修改项：
```ini
WorkingDirectory=/opt/jgwl_project  # 项目路径
Environment="PATH=/opt/jgwl_project/venv/bin"
ExecStart=/opt/jgwl_project/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8030 --workers 4
```

---

## 🔧 常用运维命令

### 服务管理

```bash
# 后端服务
sudo systemctl start jgwl-backend      # 启动
sudo systemctl stop jgwl-backend       # 停止
sudo systemctl restart jgwl-backend    # 重启
sudo systemctl status jgwl-backend     # 状态
sudo systemctl enable jgwl-backend     # 开机自启

# Nginx
sudo systemctl restart nginx           # 重启
sudo systemctl reload nginx            # 重载配置
sudo nginx -t                          # 测试配置

# MySQL
sudo systemctl restart mysql           # 重启
```

### 日志查看

```bash
# 后端日志
sudo journalctl -u jgwl-backend -f
sudo tail -f /opt/jgwl_project/logs/backend.log

# Nginx 日志
sudo tail -f /var/log/nginx/jgwl-access.log
sudo tail -f /var/log/nginx/jgwl-error.log

# 系统日志
sudo dmesg | grep -i error
```

### 更新部署

```bash
# 1. 拉取最新代码
cd /opt/jgwl_project
git pull

# 2. 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 3. 重新构建前端
cd frontend
npm install
npm run build
sudo cp -r dist/* /var/www/jgwl/

# 4. 重启服务
sudo systemctl restart jgwl-backend
sudo systemctl reload nginx
```

---

## 🐳 Docker 部署（可选）

如果想使用 Docker，可以创建以下文件：

### docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: jgwl-mysql
    environment:
      MYSQL_ROOT_PASSWORD: 1qaz3edc
      MYSQL_DATABASE: jgwl_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - jgwl-network
    restart: always

  backend:
    build: .
    container_name: jgwl-backend
    ports:
      - "8030:8030"
    environment:
      DB_HOST: mysql
      DB_PORT: 3306
      DB_USER: root
      DB_PASSWORD: 1qaz3edc
      DB_NAME: jgwl_db
    depends_on:
      - mysql
    networks:
      - jgwl-network
    restart: always
    volumes:
      - ./logs:/app/logs

  nginx:
    image: nginx:alpine
    container_name: jgwl-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./nginx/jgwl.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
    networks:
      - jgwl-network
    restart: always

volumes:
  mysql_data:

networks:
  jgwl-network:
    driver: bridge
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8030

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8030", "--workers", "4"]
```

启动 Docker：

```bash
docker-compose up -d
```

---

## ⚠️ 注意事项

### 安全建议

1. **修改默认密码**
   ```sql
   UPDATE sys_user SET password = '新的加密密码' WHERE username = 'admin';
   ```

2. **配置防火墙**
   ```bash
   # 只开放必要端口
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **使用 HTTPS**
   ```bash
   # 使用 Let's Encrypt 免费证书
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

4. **定期备份**
   ```bash
   # 数据库备份
   mysqldump -u root -p jgwl_db > backup_$(date +%Y%m%d).sql
   
   # 文件备份
   tar -czf backup_$(date +%Y%m%d).tar.gz /opt/jgwl_project
   ```

### 性能优化

1. **增加后端工作进程**
   ```ini
   # systemd 配置中
   ExecStart=... --workers 4  # 根据 CPU 核心数调整
   ```

2. **启用 Gzip 压缩**
   - 已在 Nginx 配置中启用

3. **静态资源缓存**
   - 已在 Nginx 配置中设置 30 天缓存

4. **数据库索引优化**
   ```sql
   CREATE INDEX idx_username ON sys_user(username);
   CREATE INDEX idx_parent_id ON sys_menu(parent_id);
   ```

---

## 🆘 故障排查

### 问题 1: 502 Bad Gateway

```bash
# 检查后端是否运行
sudo systemctl status jgwl-backend

# 检查端口监听
sudo netstat -tlnp | grep 8030

# 查看后端日志
sudo journalctl -u jgwl-backend -n 50
```

### 问题 2: 页面空白

```bash
# 检查前端文件
ls -la /var/www/jgwl/

# 检查 Nginx 错误日志
sudo tail -f /var/log/nginx/jgwl-error.log

# 清除浏览器缓存
# Ctrl + Shift + R
```

### 问题 3: 数据库连接失败

```bash
# 测试连接
mysql -h 123.56.164.133 -u root -p

# 检查 MySQL 状态
sudo systemctl status mysql

# 检查防火墙
sudo ufw status
```

---

## 📞 获取帮助

- 查看完整文档: `DEPLOYMENT.md`
- 查看项目 README: `README.md`
- 提交 Issue: GitHub Issues

---

**祝你部署顺利！** 🎉
