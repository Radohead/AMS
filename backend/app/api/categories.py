"""
分类管理API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.asset import Category
from app.models.user import User
from app.schemas.asset import CategoryCreate, CategoryUpdate, CategoryResponse, PageResponse

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    parent_id: Optional[int] = None,
    asset_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分类列表"""
    query = db.query(Category)

    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    else:
        query = query.filter(Category.parent_id.is_(None))

    if asset_type:
        query = query.filter(Category.asset_type == asset_type)

    if is_active is not None:
        query = query.filter(Category.is_active == is_active)

    return query.order_by(Category.sort_order, Category.id).all()


@router.get("/tree")
async def get_category_tree(
    asset_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分类树形结构"""
    query = db.query(Category)
    if asset_type:
        query = query.filter(Category.asset_type == asset_type)

    categories = query.filter(Category.is_active == True).order_by(Category.sort_order).all()

    def build_tree(parent_id=None):
        result = []
        for cat in categories:
            if cat.parent_id == parent_id:
                node = {
                    "id": cat.id,
                    "name": cat.name,
                    "code": cat.code,
                    "asset_type": cat.asset_type,
                    "icon": cat.icon,
                    "children": build_tree(cat.id)
                }
                result.append(node)
        return result

    return build_tree()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分类详情"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建分类"""
    # 检查编码唯一性
    if db.query(Category).filter(Category.code == category_data.code).first():
        raise HTTPException(status_code=400, detail="Category code already exists")

    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # 检查是否有子分类
    if db.query(Category).filter(Category.parent_id == category_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete category with children")

    # 检查是否有资产
    if category.assets:
        raise HTTPException(status_code=400, detail="Cannot delete category with assets")

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}
