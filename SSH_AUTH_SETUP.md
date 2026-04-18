# SSH 密钥认证配置指南

## 问题
Jenkins 构建失败，提示 `sshpass 未安装`

## 解决方案

### 方案 1: 安装 sshpass（最简单）⭐ 推荐

在 **Jenkins 服务器**上执行：

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y sshpass

# CentOS/RHEL  
sudo yum install -y sshpass

# 验证安装
sshpass -V
```

然后重新触发 Jenkins 构建即可。

---

### 方案 2: 使用 SSH 密钥认证（更安全）

#### 步骤 1: 生成 SSH 密钥对

在 **Jenkins 服务器**上执行：

```bash
# 生成密钥对（如果已有可跳过）
ssh-keygen -t rsa -b 4096 -C "jenkins@123.56.164.133"

# 默认保存在 ~/.ssh/id_rsa 和 ~/.ssh/id_rsa.pub
# 可以按回车使用默认路径
```

#### 步骤 2: 将公钥复制到目标服务器

```bash
# 方法 1: 使用 ssh-copy-id（推荐）
ssh-copy-id -i ~/.ssh/id_rsa.pub root@123.56.164.133

# 方法 2: 手动复制
cat ~/.ssh/id_rsa.pub | ssh root@123.56.164.133 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# 设置权限
ssh root@123.56.164.133 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

#### 步骤 3: 测试 SSH 连接

```bash
# 测试能否无密码登录
ssh -o StrictHostKeyChecking=no root@123.56.164.133

# 应该能直接登录，无需输入密码
exit
```

#### 步骤 4: 在 Jenkins 中添加 SSH 凭证

1. 登录 Jenkins
2. 进入 **Manage Jenkins → Credentials → System → Global credentials**
3. 点击 **Add Credentials**
4. 选择 **SSH Username with private key**
5. 填写：
   - **ID**: `server-ssh-key`（重要！必须与 Jenkinsfile_SSH_KEY 中的一致）
   - **Username**: `root`
   - **Private Key**: 
     - 选择 **Enter directly**
     - 点击 **Add**
     - 粘贴 `~/.ssh/id_rsa` 的内容（私钥）
   - **Passphrase**: 如果生成密钥时设置了密码，在此填写；否则留空
   - **Description**: Server SSH Key for 123.56.164.133
6. 点击 **OK**

#### 步骤 5: 修改 Jenkins 任务使用 SSH Key 版本

有两种方式：

**方式 A: 替换 Jenkinsfile**
```bash
# 在项目根目录执行
mv Jenkinsfile_SSH_KEY Jenkinsfile
git add Jenkinsfile
git commit -m "Use SSH key authentication instead of sshpass"
git push
```

**方式 B: 在 Jenkins UI 中指定 Script Path**
1. 进入 Jenkins 任务配置
2. Pipeline → Script Path 改为: `Jenkinsfile_SSH_KEY`
3. Save

#### 步骤 6: 重新构建

点击 **Build Now** 测试部署。

---

## 两种方案对比

| 特性 | sshpass | SSH 密钥 |
|------|---------|----------|
| 安装难度 | ⭐ 简单 | ⭐⭐ 中等 |
| 安全性 | ⚠️ 较低（密码明文） | ✅ 高（非对称加密） |
| 维护成本 | 低 | 中（需管理密钥） |
| 适用场景 | 测试环境 | 生产环境 |
| 是否需要额外工具 | 是（sshpass） | 否（OpenSSH 自带） |

---

## 常见问题

### Q1: sshpass 安装后仍然报错？

**A**: 检查 Jenkins 用户是否有执行权限
```bash
# 切换到 jenkins 用户
sudo su - jenkins

# 测试 sshpass
sshpass -V

# 如果找不到，检查 PATH
which sshpass
```

### Q2: SSH 密钥认证失败？

**A**: 检查以下几点：
```bash
# 1. 确认私钥路径正确
ls -la ~/.ssh/id_rsa

# 2. 确认公钥已添加到目标服务器
ssh root@123.56.164.133 "cat ~/.ssh/authorized_keys"

# 3. 检查文件权限
ls -la ~/.ssh/
# id_rsa 应该是 600
# id_rsa.pub 应该是 644
# authorized_keys 应该是 600

# 4. 查看详细错误信息
ssh -v root@123.56.164.133
```

### Q3: Jenkins 找不到 SSH 凭证？

**A**: 确保证件 ID 正确
- 在 Jenkinsfile_SSH_KEY 中查找: `SSH_CREDENTIALS_ID = 'server-ssh-key'`
- 在 Jenkins 凭证管理中确认 ID 完全一致（区分大小写）

### Q4: 权限被拒绝？

**A**: 修复权限
```bash
# 在目标服务器上执行
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 644 ~/.ssh/authorized_keys.pub

# 确保 .ssh 目录所有者正确
chown -R root:root ~/.ssh
```

---

## 推荐配置

对于生产环境，建议使用 **SSH 密钥认证**：

✅ **优点**:
- 更安全（无需存储密码）
- 支持自动化
- 符合最佳实践

❌ **缺点**:
- 初次配置稍复杂
- 需要管理密钥

---

## 快速决策

- **测试/开发环境**: 使用 sshpass（快速简单）
- **生产环境**: 使用 SSH 密钥（安全可靠）

根据你的实际情况选择合适的方案！
