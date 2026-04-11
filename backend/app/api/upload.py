"""
文件上传API
"""
import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"}


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传图片"""
    if not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")

    # 检查文件大小
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # 生成唯一文件名
    ext = get_file_extension(file.filename)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, "images", filename)

    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # 保存文件
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return {
        "filename": filename,
        "url": f"/api/upload/images/{filename}",
        "size": len(content)
    }


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传通用文件"""
    if not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    ext = get_file_extension(file.filename)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, "files", filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return {
        "filename": filename,
        "original_name": file.filename,
        "url": f"/api/upload/files/{filename}",
        "size": len(content)
    }


@router.get("/images/{filename}")
async def get_image(filename: str):
    """获取图片"""
    filepath = os.path.join(settings.UPLOAD_DIR, "images", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath)


@router.get("/files/{filename}")
async def get_file(filename: str):
    """获取文件"""
    filepath = os.path.join(settings.UPLOAD_DIR, "files", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)


@router.delete("/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """删除文件"""
    # 尝试删除图片
    filepath = os.path.join(settings.UPLOAD_DIR, "images", filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(settings.UPLOAD_DIR, "files", filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(filepath)
    return {"message": "File deleted successfully"}
