import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logger import setup_logging
from app.middleware.log_middleware import RequestLogMiddleware

# 启动时初始化日志（控制台 + 文件轮转）
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173",
                   "http://localhost:5174", "http://localhost:5175",
                   "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件（在 CORS 之后注册，确保能拿到真实路径）
app.add_middleware(RequestLogMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": f"{settings.PROJECT_NAME} v{settings.VERSION}", "docs": "/docs"}


if __name__ == "__main__":
    print(f"Swagger: http://127.0.0.1:8030/docs")
    uvicorn.run(app="main:app", host="0.0.0.0", port=8030, reload=True)
