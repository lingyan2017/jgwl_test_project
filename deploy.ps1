# JGWL Test Project 部署脚本 (PowerShell)
# 使用方法: .\deploy.ps1 [-DeployType frontend|backend|all]

param(
    [ValidateSet("frontend", "backend", "all")]
    [string]$DeployType = "all"
)

# 配置变量
$REMOTE_HOST = "123.56.164.133"
$REMOTE_USER = "root"
$REMOTE_PORT = "22"
$REMOTE_PASSWORD = $env:REMOTE_PASSWORD ?? "your_password"

$FRONTEND_REMOTE_DIR = "/usr/local/nginx"
$BACKEND_REMOTE_DIR = "/home/app/services/py_project/jgwl_test"
$PROJECT_NAME = "jgwl_test_project"
$BACKEND_PORT = "8030"

# 颜色输出函数
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 检查依赖
function Test-Dependencies {
    Write-Info "检查依赖..."
    
    # 检查 SSH 客户端
    if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
        Write-Error-Custom "SSH 客户端未安装，请安装 OpenSSH"
        exit 1
    }
    
    # 检查 SCP
    if (-not (Get-Command scp -ErrorAction SilentlyContinue)) {
        Write-Error-Custom "SCP 客户端未安装，请安装 OpenSSH"
        exit 1
    }
    
    Write-Info "✅ 依赖检查通过"
}

# 构建前端
function Build-Frontend {
    Write-Info "构建前端..."
    
    Set-Location frontend
    
    # 安装依赖
    if (Get-Command pnpm -ErrorAction SilentlyContinue) {
        Write-Info "使用 pnpm 安装依赖..."
        & pnpm install
    } elseif (Get-Command npm -ErrorAction SilentlyContinue) {
        Write-Info "使用 npm 安装依赖..."
        & npm install
    } else {
        Write-Error-Custom "未找到 pnpm 或 npm"
        exit 1
    }
    
    # 构建
    Write-Info "构建前端项目..."
    if (Get-Command pnpm -ErrorAction SilentlyContinue) {
        & pnpm build
    } else {
        & npm run build
    }
    
    # 检查构建结果
    if (-not (Test-Path "dist")) {
        Write-Error-Custom "前端构建失败，dist 目录不存在"
        exit 1
    }
    
    Write-Info "✅ 前端构建成功"
    Set-Location ..
}

# 打包文件
function Compress-Archive-Custom {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )
    
    Write-Info "压缩文件: $SourcePath -> $DestinationPath"
    
    # 使用 tar 命令（Windows 10+ 支持）
    $tarCmd = "tar -czf `"$DestinationPath`" -C `"$SourcePath`" ."
    Invoke-Expression $tarCmd
}

# 上传文件到服务器
function Upload-To-Server {
    param(
        [string]$LocalFile,
        [string]$RemotePath
    )
    
    Write-Info "上传文件: $LocalFile -> $REMOTE_USER@$REMOTE_HOST:$RemotePath"
    
    # 使用 plink/pscp 或 scp
    $env:SSHPASS = $REMOTE_PASSWORD
    $scpCmd = "sshpass -p `"$REMOTE_PASSWORD`" scp -P $REMOTE_PORT `"$LocalFile`" ${REMOTE_USER}@${REMOTE_HOST}:$RemotePath"
    Invoke-Expression $scpCmd
}

# 在服务器上执行命令
function Invoke-RemoteCommand {
    param([string]$Command)
    
    Write-Info "执行远程命令..."
    
    $sshCmd = "sshpass -p `"$REMOTE_PASSWORD`" ssh -p $REMOTE_PORT ${REMOTE_USER}@${REMOTE_HOST} `"$Command`""
    Invoke-Expression $sshCmd
}

# 部署前端
function Deploy-Frontend {
    Write-Info "部署前端到服务器..."
    
    $BuildDir = ".\build"
    New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
    
    # 创建 tar 包
    Compress-Archive-Custom -SourcePath "frontend\dist" -DestinationPath "$BuildDir\frontend-dist.tar.gz"
    
    # 上传到服务器
    Upload-To-Server -LocalFile "$BuildDir\frontend-dist.tar.gz" -RemotePath "/tmp/"
    
    # 在服务器上部署
    $remoteScript = @"
echo '部署前端文件...'

# 备份旧版本
if [ -d '/usr/local/nginx/html' ]; then
    mv /usr/local/nginx/html /usr/local/nginx/html.backup.\$(date +%Y%m%d%H%M%S)
fi

# 创建目录
mkdir -p /usr/local/nginx/html

# 解压新文件
tar -xzf /tmp/frontend-dist.tar.gz -C /usr/local/nginx/html/

# 清理临时文件
rm -f /tmp/frontend-dist.tar.gz

# 设置权限
chown -R nginx:nginx /usr/local/nginx/html 2>/dev/null || true
chmod -R 755 /usr/local/nginx/html

echo '✅ 前端部署完成'
ls -lh /usr/local/nginx/html/
"@
    
    Invoke-RemoteCommand -Command $remoteScript
    
    Write-Info "✅ 前端部署成功"
}

# 部署后端
function Deploy-Backend {
    Write-Info "部署后端到服务器..."
    
    $BuildDir = ".\build"
    $ProjectDir = "$BuildDir\$PROJECT_NAME"
    New-Item -ItemType Directory -Force -Path $ProjectDir | Out-Null
    
    # 复制后端代码（排除不必要的文件）
    Write-Info "打包后端代码..."
    
    $excludeItems = @('node_modules', 'frontend', '.git', '__pycache__', '*.pyc', '.pytest_cache', 'logs', '.env', 'build')
    
    Get-ChildItem -Path "." -Exclude $excludeItems | Copy-Item -Destination $ProjectDir -Recurse -Force
    
    # 创建 tar 包
    Set-Location $BuildDir
    Compress-Archive-Custom -SourcePath $PROJECT_NAME -DestinationPath "$PROJECT_NAME.tar.gz"
    Set-Location ..
    
    # 上传到服务器
    Upload-To-Server -LocalFile "$BuildDir\$PROJECT_NAME.tar.gz" -RemotePath "/tmp/"
    
    # 在服务器上部署
    $remoteScript = @"
echo '部署后端代码...'

# 备份旧版本
if [ -d '$BACKEND_REMOTE_DIR' ]; then
    mv $BACKEND_REMOTE_DIR $BACKEND_REMOTE_DIR.backup.\$(date +%Y%m%d%H%M%S)
fi

# 创建目录
mkdir -p $BACKEND_REMOTE_DIR

# 解压新代码
tar -xzf /tmp/$PROJECT_NAME.tar.gz -C /tmp/
mv /tmp/$PROJECT_NAME/* $BACKEND_REMOTE_DIR/

# 清理临时文件
rm -rf /tmp/$PROJECT_NAME
rm -f /tmp/$PROJECT_NAME.tar.gz

# 设置权限
chown -R app:app $BACKEND_REMOTE_DIR 2>/dev/null || true
chmod -R 755 $BACKEND_REMOTE_DIR

echo '✅ 后端代码部署完成'
ls -lh $BACKEND_REMOTE_DIR/
"@
    
    Invoke-RemoteCommand -Command $remoteScript
    
    Write-Info "✅ 后端部署成功"
}

# 重启后端服务
function Restart-BackendService {
    Write-Info "重启后端服务..."
    
    $remoteScript = @"
echo '重启后端服务...'

cd $BACKEND_REMOTE_DIR

# 停止旧服务
PID=\$(ps aux | grep 'uv run main.py' | grep -v grep | awk '{print \$2}')
if [ ! -z "\$PID" ]; then
    echo "停止旧进程: \$PID"
    kill \$PID
    sleep 3
    
    # 强制杀死
    if ps -p \$PID > /dev/null; then
        kill -9 \$PID
    fi
fi

# 使用 uv 启动服务
if [ -f 'pyproject.toml' ]; then
    echo '使用 uv 启动服务...'
    
    # 同步依赖
    uv sync
    
    # 确保日志目录存在
    mkdir -p logs
    
    # 后台启动服务
    nohup uv run main.py > logs/app.log 2>&1 &
    
    # 等待服务启动
    sleep 5
    
    # 检查服务是否启动
    if ps aux | grep 'uv run main.py' | grep -v grep > /dev/null; then
        echo '✅ 后端服务启动成功'
    else
        echo '❌ 后端服务启动失败'
        echo '查看日志:'
        tail -n 50 logs/app.log
        exit 1
    fi
else
    echo '❌ pyproject.toml 不存在'
    exit 1
fi

echo '服务状态:'
ps aux | grep 'uv run main.py' | grep -v grep
"@
    
    Invoke-RemoteCommand -Command $remoteScript
    
    Write-Info "✅ 后端服务重启成功"
}

# 重载 Nginx
function Reload-Nginx {
    Write-Info "重载 Nginx..."
    
    $remoteScript = @"
echo '检查 Nginx 配置...'

# 测试 Nginx 配置
nginx -t

if [ `$? -eq 0 ]; then
    echo 'Nginx 配置正确，重载服务...'
    systemctl reload nginx || nginx -s reload
    echo '✅ Nginx 重载成功'
else
    echo '❌ Nginx 配置错误'
    exit 1
fi
"@
    
    Invoke-RemoteCommand -Command $remoteScript
    
    Write-Info "✅ Nginx 重载成功"
}

# 健康检查
function Test-HealthCheck {
    Write-Info "执行健康检查..."
    
    # 等待服务完全启动
    Start-Sleep -Seconds 10
    
    # 检查后端 API
    $maxRetries = 5
    $retryCount = 0
    
    while ($retryCount -lt $maxRetries) {
        try {
            $response = Invoke-WebRequest -Uri "http://${REMOTE_HOST}:${BACKEND_PORT}/api/v1/auth/login" -Method GET -TimeoutSec 5 -UseBasicParsing
            $httpCode = $response.StatusCode
        } catch {
            $httpCode = $_.Exception.Response.StatusCode.value__
            if (-not $httpCode) { $httpCode = "000" }
        }
        
        if ($httpCode -eq 200 -or $httpCode -eq 422) {
            Write-Info "✅ 后端服务健康检查通过 (HTTP $httpCode)"
            break
        } else {
            $retryCount++
            Write-Warn "⏳ 等待服务启动... ($retryCount/$maxRetries) HTTP Code: $httpCode"
            Start-Sleep -Seconds 5
        }
    }
    
    if ($retryCount -eq $maxRetries) {
        Write-Error-Custom "❌ 后端服务健康检查失败"
        exit 1
    }
    
    # 检查前端
    try {
        $response = Invoke-WebRequest -Uri "http://${REMOTE_HOST}/" -Method GET -TimeoutSec 5 -UseBasicParsing
        $httpCode = $response.StatusCode
        
        if ($httpCode -eq 200) {
            Write-Info "✅ 前端服务健康检查通过 (HTTP $httpCode)"
        } else {
            Write-Warn "⚠️  前端服务返回 HTTP $httpCode"
        }
    } catch {
        Write-Warn "⚠️  前端服务检查失败"
    }
}

# 清理构建文件
function Clear-BuildFiles {
    Write-Info "清理构建文件..."
    if (Test-Path ".\build") {
        Remove-Item -Path ".\build" -Recurse -Force
    }
    Write-Info "✅ 清理完成"
}

# 主函数
function Main {
    Write-Info "=========================================="
    Write-Info "开始部署 JGWL Test Project"
    Write-Info "部署类型: $DeployType"
    Write-Info "服务器: $REMOTE_HOST"
    Write-Info "=========================================="
    
    # 检查依赖
    Test-Dependencies
    
    switch ($DeployType) {
        "frontend" {
            Build-Frontend
            Deploy-Frontend
            Reload-Nginx
        }
        "backend" {
            Deploy-Backend
            Restart-BackendService
            Test-HealthCheck
        }
        "all" {
            Build-Frontend
            Deploy-Frontend
            Deploy-Backend
            Restart-BackendService
            Reload-Nginx
            Test-HealthCheck
        }
        default {
            Write-Error-Custom "未知的部署类型: $DeployType"
            Write-Host "用法: .\deploy.ps1 [-DeployType frontend|backend|all]"
            exit 1
        }
    }
    
    # 清理
    Clear-BuildFiles
    
    Write-Info "=========================================="
    Write-Info "✅ 部署完成！"
    Write-Info "=========================================="
}

# 执行主函数
Main
