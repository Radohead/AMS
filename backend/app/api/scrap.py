"""
报废管理API
"""
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.asset import ScrapOrder, Asset, AssetStatus
from app.models.user import User
from app.schemas.asset import (
    ScrapOrderCreate,
    ScrapOrderReview,
    ScrapOrderResponse,
    PageResponse
)

router = APIRouter()


def generate_order_no() -> str:
    """生成报废申请编号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    import random
    return f"SC{timestamp}{random.randint(100, 999)}"


@router.get("/", response_model=PageResponse)
async def list_scrap_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取报废申请列表"""
    query = db.query(ScrapOrder)

    if status:
        query = query.filter(ScrapOrder.status == status)

    total = query.count()
    items = query.order_by(ScrapOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    item_responses = [ScrapOrderResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)


@router.get("/{order_id}", response_model=ScrapOrderResponse)
async def get_scrap_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取报废申请详情"""
    order = db.query(ScrapOrder).filter(ScrapOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Scrap order not found")
    return order


@router.post("/", response_model=ScrapOrderResponse)
async def create_scrap_order(
    order_data: ScrapOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建报废申请"""
    asset = db.query(Asset).filter(Asset.id == order_data.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    order = ScrapOrder(
        order_no=generate_order_no(),
        asset_id=order_data.asset_id,
        applicant_id=current_user.employee_id or 0,
        reason=order_data.reason,
        description=order_data.description,
        images=json.dumps(order_data.images) if order_data.images else None,
        status="pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


@router.post("/{order_id}/approve")
async def approve_scrap_order(
    order_id: int,
    review_data: ScrapOrderReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """审批报废申请"""
    order = db.query(ScrapOrder).filter(ScrapOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Scrap order not found")

    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order is not pending")

    order.status = review_data.status
    order.reviewer_id = current_user.employee_id or 0
    order.review_comment = review_data.review_comment
    order.reviewed_at = datetime.now()

    # 如果审批通过，更新资产状态
    if review_data.status == "approved":
        asset = db.query(Asset).filter(Asset.id == order.asset_id).first()
        if asset:
            asset.status = AssetStatus.SCRAPPED

        if review_data.disposal_method:
            order.disposal_method = review_data.disposal_method
        if review_data.residual_value is not None:
            order.residual_value = review_data.residual_value

    db.commit()

    return {"message": "Scrap order reviewed successfully"}


@router.post("/{order_id}/dispose")
async def dispose_asset(
    order_id: int,
    disposal_method: str,
    disposal_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """处置资产"""
    order = db.query(ScrapOrder).filter(ScrapOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Scrap order not found")

    if order.status != "approved":
        raise HTTPException(status_code=400, detail="Order must be approved first")

    order.disposal_method = disposal_method
    order.disposal_date = disposal_date or datetime.now()
    db.commit()

    return {"message": "Asset disposed successfully"}
