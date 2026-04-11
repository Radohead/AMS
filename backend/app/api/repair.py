"""
报修管理API
"""
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.asset import RepairOrder, Asset, AssetStatus
from app.models.user import User
from app.schemas.asset import (
    RepairOrderCreate,
    RepairOrderUpdate,
    RepairOrderResponse,
    PageResponse
)

router = APIRouter()


def generate_order_no() -> str:
    """生成工单编号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    import random
    return f"RP{timestamp}{random.randint(100, 999)}"


@router.get("/", response_model=PageResponse)
async def list_repair_orders(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    handler_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取报修工单列表"""
    query = db.query(RepairOrder)

    if status:
        query = query.filter(RepairOrder.status == status)
    if priority:
        query = query.filter(RepairOrder.priority == priority)
    if handler_id:
        query = query.filter(RepairOrder.handler_id == handler_id)

    total = query.count()
    items = query.order_by(RepairOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    item_responses = [RepairOrderResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)


@router.get("/{order_id}", response_model=RepairOrderResponse)
async def get_repair_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取报修工单详情"""
    order = db.query(RepairOrder).filter(RepairOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Repair order not found")
    return order


@router.post("/", response_model=RepairOrderResponse)
async def create_repair_order(
    order_data: RepairOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建报修工单"""
    # 检查资产是否存在
    asset = db.query(Asset).filter(Asset.id == order_data.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 更新资产状态
    asset.status = AssetStatus.REPAIR

    # 创建工单
    order = RepairOrder(
        order_no=generate_order_no(),
        asset_id=order_data.asset_id,
        reporter_id=current_user.employee_id or 0,
        description=order_data.description,
        images=json.dumps(order_data.images) if order_data.images else None,
        priority=order_data.priority,
        status="pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


@router.put("/{order_id}", response_model=RepairOrderResponse)
async def update_repair_order(
    order_id: int,
    order_data: RepairOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新报修工单"""
    order = db.query(RepairOrder).filter(RepairOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Repair order not found")

    update_data = order_data.model_dump(exclude_unset=True)

    # 如果工单完成，更新资产状态
    if update_data.get("status") == "completed":
        order.completed_at = datetime.now()
        asset = db.query(Asset).filter(Asset.id == order.asset_id).first()
        if asset:
            asset.status = AssetStatus.IN_USE

    for key, value in update_data.items():
        setattr(order, key, value)

    db.commit()
    db.refresh(order)

    return order


@router.post("/{order_id}/assign")
async def assign_repair_order(
    order_id: int,
    handler_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """指派维修人员"""
    order = db.query(RepairOrder).filter(RepairOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Repair order not found")

    order.handler_id = handler_id
    order.status = "assigned"
    db.commit()

    return {"message": "Repair order assigned successfully"}


@router.post("/{order_id}/complete")
async def complete_repair_order(
    order_id: int,
    repair_result: str,
    repair_cost: float = 0,
    parts_used: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """完成维修"""
    order = db.query(RepairOrder).filter(RepairOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Repair order not found")

    order.status = "completed"
    order.repair_result = repair_result
    order.repair_cost = repair_cost
    order.parts_used = parts_used
    order.completed_at = datetime.now()

    # 恢复资产状态
    asset = db.query(Asset).filter(Asset.id == order.asset_id).first()
    if asset:
        asset.status = AssetStatus.IN_USE

    db.commit()

    return {"message": "Repair order completed successfully"}
