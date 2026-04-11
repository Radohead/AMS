"""
员工管理API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.asset import Employee
from app.models.user import User
from app.schemas.asset import EmployeeCreate, EmployeeUpdate, EmployeeResponse, PageResponse

router = APIRouter()


@router.get("/", response_model=PageResponse)
async def list_employees(
    keyword: Optional[str] = None,
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取员工列表"""
    query = db.query(Employee)

    if keyword:
        query = query.filter(
            or_(
                Employee.name.contains(keyword),
                Employee.employee_no.contains(keyword),
                Employee.email.contains(keyword),
                Employee.phone.contains(keyword)
            )
        )

    if department_id:
        query = query.filter(Employee.department_id == department_id)

    if status:
        query = query.filter(Employee.status == status)

    total = query.count()
    items = query.order_by(Employee.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    item_responses = [EmployeeResponse.model_validate(item) for item in items]
    return PageResponse(total=total, page=page, page_size=page_size, items=item_responses)


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取员工详情"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    emp_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建员工"""
    if db.query(Employee).filter(Employee.employee_no == emp_data.employee_no).first():
        raise HTTPException(status_code=400, detail="Employee number already exists")

    employee = Employee(**emp_data.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    emp_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新员工"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = emp_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    return employee


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除员工"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 检查是否有资产
    if employee.assets:
        raise HTTPException(status_code=400, detail="Cannot delete employee with assigned assets")

    employee.is_active = False
    employee.status = "leave"
    db.commit()

    return {"message": "Employee deactivated successfully"}
