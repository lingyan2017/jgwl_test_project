# Jenkins 部署配置指南

## 📋 目录
- [前置要求](#前置要求)
- [Jenkins 插件安装](#jenkins-插件安装)
- [凭证配置](#凭证配置)
- [创建 Pipeline 任务](#创建-pipeline-任务)
- [环境变量配置](#环境变量配置)
- [使用说明](#使用说明)
- [故障排查](#故障排查)

---

## 前置要求

### 服务器端要求

1. **安装必要软件**
```bash
# 安装 Python 3.10+
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3.10-dev

# 安装 uv（Python 包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 pnpm
npm install -g pnpm

# 安装 Nginx
sudo apt-get install nginx

# 安装 sshpass（用于密码认证）
sudo apt-get install sshpass
```

2. **创建应用目录**
```bash
# 创建后端目录
sudo mkdir -p /home/app/services/py_project/jgwl_test
sudo chown -R app:app /home/app/services/py_project

# 创建前端目录
sudo mkdir -p /usr/local/nginx/html
sudo chown -R nginx:nginx /usr/local/nginx/html
```

3. **配置 Nginx**
```bash
sudo nano /etc/nginx/conf.d/jgwl.conf
```

参考 `nginx/jgwl.conf` 配置文件。

### Jenkins 服务器要求

1. **安装 Jenkins**
```bash
# Ubuntu/Debian
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins
```

2. **安装必要工具**
```bash
# 在 Jenkins 服务器上安装
sudo apt-get install git sshpass rsync
```

---

## Jenkins 插件安装

登录 Jenkins，进入 **Manage Jenkins → Manage Plugins → Available**，安装以下插件：

1. **Pipeline** - 流水线支持
2. **Git Plugin** - Git 集成
3. **SSH Agent Plugin** - SSH 支持（可选，如果使用密钥认证）
4. **Build Timeout Plugin** - 构建超时控制
5. **Workspace Cleanup Plugin** - 工作空间清理
6. **DingTalk Plugin** - 钉钉通知（可选）

---

## 凭证配置

### 方法 1: Gitee 凭证（推荐）

1. 进入 **Manage Jenkins → Credentials → System → Global credentials**
2. 点击 **Add Credentials**
3. 选择 **Username with password**
4. 填写：
   - **ID**: `gitee-credentials`
   - **Username**: 你的 Gitee 用户名
   - **Password**: 你的 Gitee 密码或访问令牌
   - **Description**: Gitee 仓库凭证

### 方法 2: SSH 密钥（更安全）

1. 生成 SSH 密钥对
```bash
ssh-keygen -t rsa -b 4096 -C "jenkins@gitee"
```

2. 将公钥添加到 Gitee
   - 复制 `~/.ssh/id_rsa.pub` 内容
   - 在 Gitee → 设置 → SSH 公钥中添加

3. 在 Jenkins 中添加凭证
   - **Kind**: SSH Username with private key
   - **ID**: `gitee-ssh-key`
   - **Username**: git
   - **Private Key**: Enter directly，粘贴私钥内容

---

## 创建 Pipeline 任务

### 步骤 1: 新建任务

1. 登录 Jenkins
2. 点击 **New Item**
3. 输入任务名称：`jgwl-test-project`
4. 选择 **Pipeline**
5. 点击 **OK**

### 步骤 2: 配置 General

1. **描述**: JGWL Test Project 自动部署
2. **勾选**: Discard old builds
   - Max # of builds to keep: 10
3. **勾选**: Do not allow concurrent builds

### 步骤 3: 配置 Build Triggers（触发器）

选择以下任一方式：

#### 方式 A: 定时构建
- 勾选 **Build periodically**
- 日程表：`H 2 * * *` （每天凌晨 2 点）

#### 方式 B: Gitee Webhook（推荐）
1. 勾选 **Gitee webhook trigger**
2. 点击 **Advanced**
3. 复制 **Secret token**
4. 在 Gitee 仓库中：
   - 进入 **管理 → WebHooks**
   - 添加 WebHook
   - URL: `http://your-jenkins-server/gitee-webhook/`
   - 密码：粘贴 Secret token
   - 勾选推送事件

#### 方式 C: 轮询 SCM
- 勾选 **Poll SCM**
- 日程表：`H/5 * * * *` （每 5 分钟检查一次）

### 步骤 4: 配置 Pipeline

1. **Definition**: Pipeline script from SCM
2. **SCM**: Git
3. **Repository URL**: `https://gitee.com/lingyan2020/jgwl_test_project.git`
4. **Credentials**: 选择之前配置的 `gitee-credentials`
5. **Branch Specifier**: `*/main` (或你的分支名)
6. **Script Path**: `Jenkinsfile`

### 步骤 5: 配置环境变量

进入 **Manage Jenkins → Configure System → Global properties**，添加：

| 名称 | 值 | 说明 |
|------|-----|------|
| REMOTE_PASSWORD | your_password | 服务器 SSH 密码 |
| REMOTE_USER | root | 服务器用户名 |
| REMOTE_HOST | 123.56.164.133 | 服务器地址 |

或者在 Jenkinsfile 中直接配置（不推荐，不安全）。

### 步骤 6: 保存并构建

1. 点击 **Save**
2. 点击 **Build Now** 测试部署

---

## 环境变量配置

### 在 Jenkinsfile 中配置（不推荐）

```groovy
environment {
    REMOTE_PASSWORD = 'your_server_password'
}
```

⚠️ **警告**: 这种方式不安全，密码会明文存储在代码中。

### 使用 Jenkins 凭证存储（推荐）

1. 在 Jenkinsfile 中使用：
```groovy
withCredentials([string(credentialsId: 'server-password', variable: 'REMOTE_PASSWORD')]) {
    // 使用 ${env.REMOTE_PASSWORD}
}
```

2. 或在 Jenkins UI 中配置全局环境变量

---

## 使用说明

### 手动触发部署

1. 进入 Jenkins 任务页面
2. 点击 **Build Now**
3. 查看构建进度和日志

### 查看构建日志

1. 点击构建编号（如 #1）
2. 点击 **Console Output**
3. 查看详细日志

### 部署特定部分

修改 Jenkinsfile 中的参数：
```groovy
// 只部署前端
environment {
    DEPLOY_TYPE = 'frontend'
}

// 只部署后端
environment {
    DEPLOY_TYPE = 'backend'
}

// 部署全部（默认）
environment {
    DEPLOY_TYPE = 'all'
}
```

### 回滚版本

1. 找到之前的成功构建
2. 点击 **Rebuild**
3. 或使用备份目录恢复：
```bash
# 前端回滚
mv /usr/local/nginx/html /usr/local/nginx/html.failed
mv /usr/local/nginx/html.backup.20240101120000 /usr/local/nginx/html

# 后端回滚
mv /home/app/services/py_project/jgwl_test /home/app/services/py_project/jgwl_test.failed
mv /home/app/services/py_project/jgwl_test.backup.20240101120000 /home/app/services/py_project/jgwl_test
```

---

## 故障排查

### 问题 1: Git 克隆失败

**错误信息**: `Failed to connect to gitee.com`

**解决方案**:
```bash
# 检查网络连接
ping gitee.com

# 检查凭证
ssh -T git@gitee.com

# 在 Jenkins 服务器上测试
git clone https://gitee.com/lingyan2020/jgwl_test_project.git
```

### 问题 2: SSH 连接失败

**错误信息**: `Permission denied (publickey,password)`

**解决方案**:
```bash
# 测试 SSH 连接
sshpass -p 'your_password' ssh -p 22 root@123.56.164.133

# 检查防火墙
sudo ufw status

# 检查 SSH 服务
sudo systemctl status sshd
```

### 问题 3: 前端构建失败

**错误信息**: `pnpm: command not found`

**解决方案**:
```bash
# 安装 pnpm
npm install -g pnpm

# 或在 Jenkins 中使用 npm
# 修改 Jenkinsfile 中的构建命令
```

### 问题 4: 后端服务启动失败

**错误信息**: `uv: command not found`

**解决方案**:
```bash
# 在服务器上安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 检查 uv 路径
which uv

# 可能需要添加到 PATH
export PATH="$HOME/.local/bin:$PATH"
```

### 问题 5: 权限问题

**错误信息**: `Permission denied`

**解决方案**:
```bash
# 检查目录权限
ls -lh /usr/local/nginx/
ls -lh /home/app/services/py_project/

# 修正权限
sudo chown -R nginx:nginx /usr/local/nginx/html
sudo chown -R app:app /home/app/services/py_project/jgwl_test
```

### 问题 6: 端口被占用

**错误信息**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
sudo lsof -i :8030

# 杀死进程
sudo kill -9 <PID>

# 或在 Jenkinsfile 中增加等待时间
sleep 10
```

---

## 安全建议

1. **使用 SSH 密钥而非密码**
   - 更安全
   - 无需在 Jenkins 中存储密码

2. **限制 Jenkins 用户权限**
   - 不要使用 root 运行 Jenkins
   - 创建专用的 jenkins 用户

3. **启用 HTTPS**
   - 为 Jenkins 配置 SSL 证书
   - 使用反向代理（Nginx）

4. **定期更新**
   - 更新 Jenkins 和插件
   - 更新服务器软件包

5. **备份配置**
   - 定期备份 Jenkins 配置
   - 备份服务器数据

---

## 监控和告警

### 添加钉钉通知

1. 安装 DingTalk Plugin
2. 配置钉钉机器人
3. 在 Jenkinsfile 中添加：

```groovy
post {
    success {
        dingtalk(
            robot: 'your-robot-id',
            type: 'MARKDOWN',
            title: 'JGWL 部署成功',
            text: [
                '### ✅ JGWL Test Project 部署成功',
                "- 构建号: #${env.BUILD_NUMBER}",
                "- 构建人: ${env.BUILD_USER}",
                "- 时间: ${new Date()}",
                "[查看详情](${env.BUILD_URL})"
            ]
        )
    }
    failure {
        dingtalk(
            robot: 'your-robot-id',
            type: 'MARKDOWN',
            title: 'JGWL 部署失败',
            text: [
                '### ❌ JGWL Test Project 部署失败',
                "- 构建号: #${env.BUILD_NUMBER}",
                "- 构建人: ${env.BUILD_USER}",
                "- 时间: ${new Date()}",
                "[查看日志](${env.BUILD_URL}console)"
            ]
        )
    }
}
```

---

## 性能优化

1. **使用缓存**
```groovy
stage('Cache Dependencies') {
    steps {
        // 缓存 node_modules
        cache(paths: ['frontend/node_modules'], key: 'npm-${checksum("frontend/package-lock.json")}')
        
        // 缓存 Python 依赖
        cache(paths: ['.venv'], key: 'uv-${checksum("uv.lock")}')
    }
}
```

2. **并行构建**
```groovy
stage('Build') {
    parallel {
        stage('Frontend') {
            steps {
                // 构建前端
            }
        }
        stage('Backend') {
            steps {
                // 打包后端
            }
        }
    }
}
```

3. **增量部署**
   - 只上传变更的文件
   - 使用 rsync 替代 scp

---

## 相关文档

- [Jenkins 官方文档](https://www.jenkins.io/doc/)
- [Jenkins Pipeline 语法](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [uv 文档](https://github.com/astral-sh/uv)
- [Nginx 配置指南](https://nginx.org/en/docs/)

---

## 联系支持

如有问题，请联系：
- 项目负责人: [你的名字]
- 邮箱: [你的邮箱]
- 电话: [你的电话]
