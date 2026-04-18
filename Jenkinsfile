// Jenkins Pipeline for JGWL Test Project
pipeline {
    agent any
    
    environment {
        // Git 仓库配置
        GIT_URL = 'https://gitee.com/lingyan2020/jgwl_test_project.git'
        GIT_CREDENTIALS_ID = 'gitee-credentials'  // 需要在 Jenkins 中配置凭证
        
        // 服务器配置
        REMOTE_HOST = '123.56.164.133'
        REMOTE_USER = 'root'  // 根据实际用户修改
        REMOTE_PORT = '22'
        
        // 远程目录配置
        FRONTEND_REMOTE_DIR = '/usr/local/nginx'
        BACKEND_REMOTE_DIR = '/home/app/services/py_project/jgwl_test'
        
        // 项目配置
        PROJECT_NAME = 'jgwl_test_project'
        BACKEND_PORT = '8030'
        
        // 构建目录
        WORKSPACE_DIR = "${env.WORKSPACE}"
        DIST_DIR = "${WORKSPACE_DIR}/frontend/dist"
        BUILD_DIR = "${WORKSPACE_DIR}/build"
    }
    
    options {
        // 保留最近的 10 次构建记录
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // 超时时间 30 分钟
        timeout(time: 30, unit: 'MINUTES')
        // 禁止并发构建
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                echo '📦 拉取代码...'
                checkout scm
                // 或者使用 git 命令
                // git branch: 'main', credentialsId: "${GIT_CREDENTIALS_ID}", url: "${GIT_URL}"
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo '⚙️ 设置构建环境...'
                sh '''
                    # 创建构建目录
                    mkdir -p ${BUILD_DIR}
                    
                    # 检查 Node.js 版本
                    node --version || echo "Node.js not installed"
                    
                    # 检查 Python 版本
                    python3 --version || echo "Python3 not installed"
                    
                    # 检查 uv 是否安装
                    uv --version || echo "uv not installed"
                '''
            }
        }
        
        stage('Install Frontend Dependencies') {
            steps {
                echo '📥 安装前端依赖...'
                dir('frontend') {
                    sh '''
                        # 使用 pnpm 安装依赖（如果没有 pnpm，使用 npm）
                        if command -v pnpm &> /dev/null; then
                            pnpm install
                        elif command -v npm &> /dev/null; then
                            npm install
                        else
                            echo "Error: Neither pnpm nor npm found"
                            exit 1
                        fi
                    '''
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                echo '🔨 构建前端...'
                dir('frontend') {
                    sh '''
                        # 构建前端项目
                        if command -v pnpm &> /dev/null; then
                            pnpm build
                        else
                            npm run build
                        fi
                        
                        # 检查构建结果
                        if [ ! -d "dist" ]; then
                            echo "Error: Build failed, dist directory not found"
                            exit 1
                        fi
                        
                        echo "✅ 前端构建成功"
                        ls -lh dist/
                    '''
                }
            }
        }
        
        stage('Package Backend') {
            steps {
                echo '📦 打包后端代码...'
                sh '''
                    # 创建后端打包目录
                    mkdir -p ${BUILD_DIR}/${PROJECT_NAME}
                    
                    # 复制后端代码（排除不必要的文件）
                    rsync -av \
                        --exclude='node_modules' \
                        --exclude='frontend' \
                        --exclude='.git' \
                        --exclude='__pycache__' \
                        --exclude='*.pyc' \
                        --exclude='.pytest_cache' \
                        --exclude='logs/*' \
                        --exclude='.env' \
                        --exclude='build' \
                        ${WORKSPACE_DIR}/ ${BUILD_DIR}/${PROJECT_NAME}/
                    
                    echo "✅ 后端代码打包完成"
                    du -sh ${BUILD_DIR}/${PROJECT_NAME}/
                '''
            }
        }
        
        stage('Deploy to Server') {
            steps {
                echo '🚀 部署到服务器...'
                
                script {
                    // 部署前端
                    deployFrontend()
                    
                    // 部署后端
                    deployBackend()
                }
            }
        }
        
        stage('Start Services') {
            steps {
                echo '🔄 启动服务...'
                
                script {
                    // 重启后端服务
                    restartBackendService()
                    
                    // 重载 Nginx 配置
                    reloadNginx()
                }
            }
        }
        
        stage('Health Check') {
            steps {
                echo '💓 健康检查...'
                script {
                    healthCheck()
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ 部署成功！'
            // 可以添加通知，如钉钉、企业微信等
            // dingtalk accessToken: 'your-token', message: 'JGWL 项目部署成功'
        }
        failure {
            echo '❌ 部署失败！'
            // 发送失败通知
            // dingtalk accessToken: 'your-token', message: 'JGWL 项目部署失败'
        }
        always {
            echo '🧹 清理工作空间...'
            cleanWs()
        }
    }
}

// 函数定义
def deployFrontend() {
    echo '📤 上传前端文件...'
    sh """
        # 创建临时 tar 包
        cd ${DIST_DIR}
        tar -czf ${BUILD_DIR}/frontend-dist.tar.gz .
        
        # 上传到服务器
        sshpass -p '${REMOTE_PASSWORD}' scp -P ${REMOTE_PORT} \
            ${BUILD_DIR}/frontend-dist.tar.gz \
            ${REMOTE_USER}@${REMOTE_HOST}:/tmp/
        
        # 在服务器上解压并部署
        sshpass -p '${REMOTE_PASSWORD}' ssh -p ${REMOTE_PORT} \
            ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
            echo "部署前端文件..."
            
            # 备份旧版本
            if [ -d "${FRONTEND_REMOTE_DIR}/html" ]; then
                mv ${FRONTEND_REMOTE_DIR}/html ${FRONTEND_REMOTE_DIR}/html.backup.\$(date +%Y%m%d%H%M%S)
            fi
            
            # 创建目录
            mkdir -p ${FRONTEND_REMOTE_DIR}/html
            
            # 解压新文件
            tar -xzf /tmp/frontend-dist.tar.gz -C ${FRONTEND_REMOTE_DIR}/html/
            
            # 清理临时文件
            rm -f /tmp/frontend-dist.tar.gz
            
            # 设置权限
            chown -R nginx:nginx ${FRONTEND_REMOTE_DIR}/html 2>/dev/null || true
            chmod -R 755 ${FRONTEND_REMOTE_DIR}/html
            
            echo "✅ 前端部署完成"
            ls -lh ${FRONTEND_REMOTE_DIR}/html/
EOF
    """
}

def deployBackend() {
    echo '📤 上传后端代码...'
    sh """
        # 创建 tar 包
        cd ${BUILD_DIR}
        tar -czf ${PROJECT_NAME}.tar.gz ${PROJECT_NAME}/
        
        # 上传到服务器
        sshpass -p '${REMOTE_PASSWORD}' scp -P ${REMOTE_PORT} \
            ${BUILD_DIR}/${PROJECT_NAME}.tar.gz \
            ${REMOTE_USER}@${REMOTE_HOST}:/tmp/
        
        # 在服务器上部署
        sshpass -p '${REMOTE_PASSWORD}' ssh -p ${REMOTE_PORT} \
            ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
            echo "部署后端代码..."
            
            # 备份旧版本
            if [ -d "${BACKEND_REMOTE_DIR}" ]; then
                mv ${BACKEND_REMOTE_DIR} ${BACKEND_REMOTE_DIR}.backup.\$(date +%Y%m%d%H%M%S)
            fi
            
            # 创建目录
            mkdir -p ${BACKEND_REMOTE_DIR}
            
            # 解压新代码
            tar -xzf /tmp/${PROJECT_NAME}.tar.gz -C /tmp/
            mv /tmp/${PROJECT_NAME}/* ${BACKEND_REMOTE_DIR}/
            
            # 清理临时文件
            rm -rf /tmp/${PROJECT_NAME}
            rm -f /tmp/${PROJECT_NAME}.tar.gz
            
            # 设置权限
            chown -R app:app ${BACKEND_REMOTE_DIR} 2>/dev/null || true
            chmod -R 755 ${BACKEND_REMOTE_DIR}
            
            echo "✅ 后端代码部署完成"
            ls -lh ${BACKEND_REMOTE_DIR}/
EOF
    """
}

def restartBackendService() {
    echo '🔄 重启后端服务...'
    sh """
        sshpass -p '${REMOTE_PASSWORD}' ssh -p ${REMOTE_PORT} \
            ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
            echo "重启后端服务..."
            
            cd ${BACKEND_REMOTE_DIR}
            
            # 停止旧服务
            if [ -f "main.py" ]; then
                # 查找并停止旧进程
                PID=\$(ps aux | grep "uv run main.py" | grep -v grep | awk '{print \$2}')
                if [ ! -z "\$PID" ]; then
                    echo "停止旧进程: \$PID"
                    kill \$PID
                    sleep 3
                    
                    # 强制杀死
                    if ps -p \$PID > /dev/null; then
                        kill -9 \$PID
                    fi
                fi
            fi
            
            # 使用 uv 创建/更新虚拟环境并启动服务
            if [ -f "pyproject.toml" ]; then
                echo "使用 uv 启动服务..."
                
                # 同步依赖
                uv sync
                
                # 后台启动服务
                nohup uv run main.py > logs/app.log 2>&1 &
                
                # 等待服务启动
                sleep 5
                
                # 检查服务是否启动
                if ps aux | grep "uv run main.py" | grep -v grep > /dev/null; then
                    echo "✅ 后端服务启动成功"
                else
                    echo "❌ 后端服务启动失败"
                    exit 1
                fi
            else
                echo "❌ pyproject.toml 不存在"
                exit 1
            fi
            
            echo "服务状态:"
            ps aux | grep "uv run main.py" | grep -v grep
EOF
    """
}

def reloadNginx() {
    echo '🔄 重载 Nginx...'
    sh """
        sshpass -p '${REMOTE_PASSWORD}' ssh -p ${REMOTE_PORT} \
            ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
            echo "检查 Nginx 配置..."
            
            # 测试 Nginx 配置
            nginx -t
            
            if [ \$? -eq 0 ]; then
                echo "Nginx 配置正确，重载服务..."
                systemctl reload nginx || nginx -s reload
                echo "✅ Nginx 重载成功"
            else
                echo "❌ Nginx 配置错误"
                exit 1
            fi
EOF
    """
}

def healthCheck() {
    echo '💓 执行健康检查...'
    sh """
        # 等待服务完全启动
        sleep 10
        
        # 检查后端 API
        MAX_RETRIES=5
        RETRY_COUNT=0
        
        while [ \$RETRY_COUNT -lt \$MAX_RETRIES ]; do
            HTTP_CODE=\$(curl -s -o /dev/null -w "%{http_code}" http://${REMOTE_HOST}:${BACKEND_PORT}/api/v1/auth/login || echo "000")
            
            if [ "\$HTTP_CODE" = "200" ] || [ "\$HTTP_CODE" = "422" ]; then
                echo "✅ 后端服务健康检查通过 (HTTP \$HTTP_CODE)"
                break
            else
                RETRY_COUNT=\$((RETRY_COUNT + 1))
                echo "⏳ 等待服务启动... (\$RETRY_COUNT/\$MAX_RETRIES) HTTP Code: \$HTTP_CODE"
                sleep 5
            fi
        done
        
        if [ \$RETRY_COUNT -eq \$MAX_RETRIES ]; then
            echo "❌ 后端服务健康检查失败"
            exit 1
        fi
        
        # 检查前端
        HTTP_CODE=\$(curl -s -o /dev/null -w "%{http_code}" http://${REMOTE_HOST}/ || echo "000")
        
        if [ "\$HTTP_CODE" = "200" ]; then
            echo "✅ 前端服务健康检查通过 (HTTP \$HTTP_CODE)"
        else
            echo "⚠️  前端服务返回 HTTP \$HTTP_CODE"
        fi
    """
}
