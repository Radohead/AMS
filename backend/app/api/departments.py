"""
部门管理API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.asset import Department
from app.models.user import User
from app.schemas.asset import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter()


@router.get("/", response_model=List[DepartmentResponse])
async def list_departments(
    parent_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取部门列表"""
    query = db.query(Department)

    if parent_id is not None:
        query = query.filter(Department.parent_id == parent_id)
    else:
        query = query.filter(Department.parent_id.is_(None))

    if is_active is not None:
        query = query.filter(Department.is_active == is_active)

    return query.order_by(Department.id).all()


@router.get("/tree")
async def get_department_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取部门树形结构"""
    departments = db.query(Department).filter(Department.is_active == True).order_by(Department.id).all()

    def build_tree(parent_id=None):
        result = []
        for dept in departments:
            if dept.parent_id == parent_id:
                node = {
                    "id": dept.id,
                    "name": dept.name,
                    "code": dept.code,
                    "manager_id": dept.manager_id,
                    "children": build_tree(dept.id)
                }
                result.append(node)
        return result

    return build_tree()


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取部门详情"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.post("/", response_model=DepartmentResponse)
async def create_department(
    dept_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建部门"""
    if db.query(Department).filter(Department.code == dept_data.code).first():
        raise HTTPException(status_code=400, detail="Department code already exists")

    department = Department(**dept_data.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)

    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    dept_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新部门"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    update_data = dept_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(department, key, value)

    db.commit()
    db.refresh(department)

    return department


@router.delete("/{department_id}")
async def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除部门"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if db.query(Department).filter(Department.parent_id == department_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete department with children")

    if department.employees:
        raise HTTPException(status_code=400, detail="Cannot delete department with employees")

    db.delete(department)
    db.commit()

    return {"message": "Department deleted successfully"}
