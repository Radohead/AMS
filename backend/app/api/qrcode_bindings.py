"""
二维码绑定管理 API
用于管理资产二维码与草料二维码平台的绑定关系
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


# 数据模型
class QrcodeBindingBase(BaseModel):
    asset_id: int
    cai_liao_link_id: Optional[str] = None
    cai_liao_url: Optional[str] = None
    qrcode_url: Optional[str] = None


class QrcodeBindingCreate(QrcodeBindingBase):
    pass


class QrcodeBindingUpdate(BaseModel):
    cai_liao_link_id: Optional[str] = None
    cai_liao_url: Optional[str] = None
    qrcode_url: Optional[str] = None
    is_active: Optional[bool] = None


class QrcodeBindingResponse(QrcodeBindingBase):
    id: int
    scan_count: int = 0
    last_scan_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaiLiaoSyncRequest(BaseModel):
    """草料同步请求"""
    asset_ids: List[int]


class CaiLiaoSyncResponse(BaseModel):
    """同步结果"""
    total: int
    success: int
    failed: int
    failed_items: List[dict]


# 模拟数据存储（实际应使用数据库）
_bindings = {}  # {asset_id: QrcodeBindingResponse}


@router.get("/bindings", response_model=List[QrcodeBindingResponse])
async def list_bindings(
    asset_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取二维码绑定列表"""
    # 实际应从数据库查询
    bindings = list(_bindings.values())

    if asset_id:
        bindings = [b for b in bindings if b.asset_id == asset_id]

    total = len(bindings)
    start = (page - 1) * page_size
    end = start + page_size

    return bindings[start:end]


@router.get("/bindings/{asset_id}", response_model=QrcodeBindingResponse)
async def get_binding(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产的二维码绑定"""
    if asset_id not in _bindings:
        raise HTTPException(status_code=404, detail="绑定不存在")

    return _bindings[asset_id]


@router.post("/bindings", response_model=QrcodeBindingResponse)
async def create_binding(
    binding_data: QrcodeBindingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建二维码绑定"""
    if binding_data.asset_id in _bindings:
        raise HTTPException(status_code=400, detail="该资产已存在绑定")

    now = datetime.utcnow()
    binding = QrcodeBindingResponse(
        id=len(_bindings) + 1,
        **binding_data.model_dump(),
        scan_count=0,
        last_scan_at=None,
        is_active=True,
        created_at=now,
        updated_at=now
    )

    _bindings[binding_data.asset_id] = binding
    return binding


@router.put("/bindings/{asset_id}", response_model=QrcodeBindingResponse)
async def update_binding(
    asset_id: int,
    update_data: QrcodeBindingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新二维码绑定"""
    if asset_id not in _bindings:
        raise HTTPException(status_code=404, detail="绑定不存在")

    binding = _bindings[asset_id]

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(binding, key, value)

    binding.updated_at = datetime.utcnow()
    _bindings[asset_id] = binding

    return binding


@router.delete("/bindings/{asset_id}")
async def delete_binding(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除二维码绑定"""
    if asset_id not in _bindings:
        raise HTTPException(status_code=404, detail="绑定不存在")

    del _bindings[asset_id]
    return {"message": "删除成功"}


@router.post("/bindings/{asset_id}/regenerate")
async def regenerate_qrcode(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """重新生成二维码"""
    # 重新生成二维码URL
    # 实际应调用草料API或使用本地生成

    return {
        "message": "二维码已重新生成",
        "qrcode_url": f"/api/qrcodes/{asset_id}/download"
    }


@router.post("/sync/cai_liao")
async def sync_cai_liao(
    sync_data: CaiLiaoSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    同步资产到草料二维码平台

    注意：需要在后台配置草料API的密钥
    """
    # 草料API配置
    # CAI_LIAO_API_KEY = settings.CAI_LIAO_API_KEY
    # CAI_LIAO_TEMPLATE_ID = settings.CAI_LIAO_TEMPLATE_ID

    total = len(sync_data.asset_ids)
    success = 0
    failed = 0
    failed_items = []

    for asset_id in sync_data.asset_ids:
        try:
            # 实际应调用草料API创建二维码
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         "https://v2.api.haulele.com Port/qrcode/add",
            #         headers={"Authorization": CAI_LIAO_API_KEY},
            #         json={
            #             "qrcode_id": f"asset_{asset_id}",
            #             "template_id": CAI_LIAO_TEMPLATE_ID,
            #             "data": {...}
            #         }
            #     )

            # 模拟成功
            success += 1
        except Exception as e:
            failed += 1
            failed_items.append({
                "asset_id": asset_id,
                "error": str(e)
            })

    return CaiLiaoSyncResponse(
        total=total,
        success=success,
        failed=failed,
        failed_items=failed_items
    )


@router.get("/stats")
async def get_qrcode_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取二维码统计信息"""
    total_bindings = len(_bindings)
    active_bindings = len([b for b in _bindings.values() if b.is_active])
    total_scans = sum(b.scan_count for b in _bindings.values())

    return {
        "total_bindings": total_bindings,
        "active_bindings": active_bindings,
        "total_scans": total_scans
    }
