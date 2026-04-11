"""
易耗品库存管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.asset import Asset, ConsumableRecord, AssetType
from app.models.user import User
from app.schemas.asset import (
    ConsumableRecordCreate,
    ConsumableRecordResponse,
    PageResponse
)

router = APIRouter()


@router.get("/stock", response_model=PageResponse)
async def list_consumable_stock(
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取易耗品库存列表"""
    query = db.query(Asset).filter(Asset.asset_type == AssetType.CONSUMABLE)

    if keyword:
        query = query.filter(Asset.name.contains(keyword))

    total = query.count()
    items = query.order_by(Asset.name).offset((page - 1) * page_size).limit(page_size).all()

    from app.schemas.asset import AssetResponse
    item_responses = [AssetResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)


@router.get("/stock/low")
async def get_low_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取库存预警列表"""
    consumables = db.query(Asset).filter(
        Asset.asset_type == AssetType.CONSUMABLE,
        Asset.min_stock.isnot(None),
        Asset.current_stock.isnot(None)
    ).all()

    low_stock = []
    for item in consumables:
        if item.current_stock <= item.min_stock:
            low_stock.append({
                "id": item.id,
                "asset_no": item.asset_no,
                "name": item.name,
                "current_stock": item.current_stock,
                "min_stock": item.min_stock,
                "unit": item.unit
            })

    return low_stock


@router.post("/consume")
async def consume_consumable(
    record_data: ConsumableRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """领用易耗品"""
    asset = db.query(Asset).filter(Asset.id == record_data.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Consumable not found")

    if asset.current_stock < record_data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # 扣减库存
    asset.current_stock -= record_data.quantity

    # 记录领用
    record = ConsumableRecord(
        asset_id=record_data.asset_id,
        employee_id=record_data.employee_id,
        quantity=record_data.quantity,
        purpose=record_data.purpose,
        department_id=record_data.department_id,
        operator_id=current_user.employee_id or 0
    )

    db.add(record)
    db.commit()

    return {
        "message": "Consumable consumed successfully",
        "remaining_stock": asset.current_stock,
        "record": ConsumableRecordResponse.model_validate(record)
    }


@router.post("/{asset_id}/restock")
async def restock_consumable(
    asset_id: int,
    quantity: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """补充易耗品库存"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Consumable not found")

    if asset.asset_type != AssetType.CONSUMABLE:
        raise HTTPException(status_code=400, detail="Asset is not a consumable")

    asset.current_stock = (asset.current_stock or 0) + quantity
    db.commit()

    return {
        "message": "Consumable restocked successfully",
        "current_stock": asset.current_stock
    }


@router.get("/records", response_model=PageResponse)
async def list_consumable_records(
    asset_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取领用记录"""
    query = db.query(ConsumableRecord)

    if asset_id:
        query = query.filter(ConsumableRecord.asset_id == asset_id)
    if employee_id:
        query = query.filter(ConsumableRecord.employee_id == employee_id)

    total = query.count()
    items = query.order_by(ConsumableRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    from app.schemas.asset import ConsumableRecordResponse
    item_responses = [ConsumableRecordResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)
