"""
盘点管理API
"""
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.asset import (
    InventoryCheck,
    InventoryCheckItem,
    Asset,
    AssetType
)
from app.models.user import User
from app.schemas.asset import (
    InventoryCheckCreate,
    InventoryCheckUpdate,
    InventoryCheckResponse,
    InventoryCheckItemUpdate,
    InventoryCheckItemResponse,
    PageResponse
)

router = APIRouter()


@router.get("/", response_model=PageResponse)
async def list_inventory_checks(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取盘点计划列表"""
    query = db.query(InventoryCheck)

    if status:
        query = query.filter(InventoryCheck.status == status)

    total = query.count()
    items = query.order_by(InventoryCheck.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    item_responses = [InventoryCheckResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)


@router.get("/{check_id}", response_model=InventoryCheckResponse)
async def get_inventory_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取盘点计划详情"""
    check = db.query(InventoryCheck).filter(InventoryCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Inventory check not found")
    return check


@router.post("/", response_model=InventoryCheckResponse)
async def create_inventory_check(
    check_data: InventoryCheckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建盘点计划"""
    check = InventoryCheck(
        name=check_data.name,
        start_date=check_data.start_date,
        end_date=check_data.end_date,
        categories=json.dumps(check_data.categories) if check_data.categories else None,
        departments=json.dumps(check_data.departments) if check_data.departments else None,
        status="planning",
        created_by=current_user.employee_id or 0
    )

    db.add(check)
    db.commit()
    db.refresh(check)

    # 自动生成盘点明细
    await generate_check_items(check.id, check_data.categories, check_data.departments, db)

    return check


async def generate_check_items(check_id: int, category_ids: List[int], department_ids: List[int], db: Session):
    """生成盘点明细"""
    query = db.query(Asset)

    if category_ids:
        query = query.filter(Asset.category_id.in_(category_ids))
    if department_ids:
        query = query.filter(Asset.department_id.in_(department_ids))

    assets = query.all()

    for asset in assets:
        item = InventoryCheckItem(
            check_id=check_id,
            asset_id=asset.id,
            expected_status=asset.status,
            expected_location=asset.location,
            expected_user_id=asset.user_id
        )
        db.add(item)

    db.commit()


@router.put("/{check_id}", response_model=InventoryCheckResponse)
async def update_inventory_check(
    check_id: int,
    check_data: InventoryCheckUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新盘点计划"""
    check = db.query(InventoryCheck).filter(InventoryCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Inventory check not found")

    update_data = check_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(check, key, value)

    db.commit()
    db.refresh(check)

    return check


@router.post("/{check_id}/start")
async def start_inventory_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """开始盘点"""
    check = db.query(InventoryCheck).filter(InventoryCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Inventory check not found")

    if check.status != "planning":
        raise HTTPException(status_code=400, detail="Can only start planned check")

    check.status = "in_progress"
    db.commit()

    return {"message": "Inventory check started"}


@router.get("/{check_id}/items", response_model=PageResponse)
async def get_check_items(
    check_id: int,
    check_result: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取盘点明细"""
    query = db.query(InventoryCheckItem).filter(InventoryCheckItem.check_id == check_id)

    if check_result:
        query = query.filter(InventoryCheckItem.check_result == check_result)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    item_responses = [InventoryCheckItemResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)


@router.put("/{check_id}/items/{item_id}")
async def update_check_item(
    check_id: int,
    item_id: int,
    item_data: InventoryCheckItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新盘点明细（扫码盘点时使用）"""
    item = db.query(InventoryCheckItem).filter(
        and_(
            InventoryCheckItem.id == item_id,
            InventoryCheckItem.check_id == check_id
        )
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Inventory check item not found")

    update_data = item_data.model_dump(exclude_unset=True)

    # 自动判断盘点结果
    if update_data.get("actual_status") and not update_data.get("check_result"):
        if update_data["actual_status"] != item.expected_status:
            update_data["check_result"] = "discrepancy"

    if update_data.get("actual_location") and update_data["actual_location"] != item.expected_location:
        update_data["check_result"] = "discrepancy"

    if update_data.get("actual_user_id") and update_data["actual_user_id"] != item.expected_user_id:
        update_data["check_result"] = "discrepancy"

    for key, value in update_data.items():
        setattr(item, key, value)

    item.checked_by = current_user.employee_id or 0
    item.checked_at = datetime.now()

    db.commit()

    return {"message": "Check item updated", "item": item}


@router.post("/{check_id}/complete")
async def complete_inventory_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """完成盘点"""
    check = db.query(InventoryCheck).filter(InventoryCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Inventory check not found")

    check.status = "completed"
    check.end_date = datetime.now()
    db.commit()

    return {"message": "Inventory check completed"}


@router.get("/{check_id}/report")
async def get_check_report(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取盘点报告"""
    check = db.query(InventoryCheck).filter(InventoryCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Inventory check not found")

    items = db.query(InventoryCheckItem).filter(InventoryCheckItem.check_id == check_id).all()

    total = len(items)
    normal = len([i for i in items if i.check_result == "normal"])
    discrepancy = len([i for i in items if i.check_result == "discrepancy"])
    missing = len([i for i in items if i.check_result == "missing"])
    extra = len([i for i in items if i.check_result == "extra"])
    unchecked = len([i for i in items if i.check_result is None])

    return {
        "check": check,
        "summary": {
            "total": total,
            "normal": normal,
            "discrepancy": discrepancy,
            "missing": missing,
            "extra": extra,
            "unchecked": unchecked
        },
        "items": items
    }
