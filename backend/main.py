"""
AMS - Asset Management System 后端服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine
from app.api import (
    auth,
    assets,
    categories,
    employees,
    departments,
    inventory,
    repair,
    scrap,
    inventory_check,
    permissions,
    upload
)
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    yield
    # 关闭时


app = FastAPI(
    title="AMS 资产管理系统",
    description="公司内部资产管理解决方案",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(assets.router, prefix="/api/assets", tags=["资产管理"])
app.include_router(categories.router, prefix="/api/categories", tags=["资产分类"])
app.include_router(employees.router, prefix="/api/employees", tags=["员工管理"])
app.include_router(departments.router, prefix="/api/departments", tags=["部门管理"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["库存管理"])
app.include_router(repair.router, prefix="/api/repair", tags=["报修管理"])
app.include_router(scrap.router, prefix="/api/scrap", tags=["报废管理"])
app.include_router(inventory_check.router, prefix="/api/inventory-check", tags=["盘点管理"])
app.include_router(permissions.router, prefix="/api/permissions", tags=["权限管理"])
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])

# 静态文件服务（上传文件访问）
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
async def root():
    return {"message": "AMS 资产管理系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
