"""
Pydantic schemas - 资产相关
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    FIXED = "fixed"
    CONSUMABLE = "consumable"
    REAL_ESTATE = "real_estate"


class AssetStatus(str, Enum):
    STOCK = "stock"
    IN_USE = "in_use"
    REPAIR = "repair"
    SCRAPPED = "scrapped"
    LOST = "lost"


# ========== 分类 Schema ==========
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    parent_id: Optional[int] = None
    asset_type: AssetType
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    custom_fields: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    custom_fields: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 部门 Schema ==========
class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 员工 Schema ==========
class EmployeeBase(BaseModel):
    employee_no: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    department_id: Optional[int] = None
    position: Optional[str] = Field(None, max_length=100)
    status: str = "active"
    avatar: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    department_id: Optional[int] = None
    position: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None
    avatar: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 资产 Schema ==========
class AssetBase(BaseModel):
    name: str = Field(..., max_length=200)
    category_id: int
    asset_type: AssetType
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_no: Optional[str] = Field(None, max_length=100)
    purchase_date: Optional[datetime] = None
    purchase_price: float = 0
    warranty_end: Optional[datetime] = None
    department_id: Optional[int] = None
    user_id: Optional[int] = None
    keeper_id: Optional[int] = None
    location: Optional[str] = Field(None, max_length=200)
    quantity: int = 1
    unit: Optional[str] = Field(None, max_length=20)
    min_stock: Optional[int] = None
    current_stock: Optional[int] = None
    description: Optional[str] = None
    remarks: Optional[str] = None
    # 房地产专用字段
    address: Optional[str] = Field(None, max_length=500)
    area: Optional[float] = Field(None, description="建筑面积(平方米)")
    land_area: Optional[float] = Field(None, description="占地面积(平方米)")
    property_type: Optional[str] = Field(None, max_length=50, description="产权类型")
    property_no: Optional[str] = Field(None, max_length=100, description="产权证号")
    land_no: Optional[str] = Field(None, max_length=100, description="土地证号")
    building_no: Optional[str] = Field(None, max_length=50, description="楼栋号")
    floor: Optional[str] = Field(None, max_length=20, description="楼层")
    room_no: Optional[str] = Field(None, max_length=50, description="房间号")
    usage: Optional[str] = Field(None, max_length=50, description="用途")
    build_year: Optional[int] = Field(None, description="建成年份")
    structure: Optional[str] = Field(None, max_length=50, description="建筑结构")


class AssetCreate(AssetBase):
    images: Optional[List[str]] = None
    custom_fields: Optional[str] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    category_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_no: Optional[str] = Field(None, max_length=100)
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    warranty_end: Optional[datetime] = None
    department_id: Optional[int] = None
    user_id: Optional[int] = None
    keeper_id: Optional[int] = None
    location: Optional[str] = Field(None, max_length=200)
    quantity: Optional[int] = None
    unit: Optional[str] = Field(None, max_length=20)
    min_stock: Optional[int] = None
    current_stock: Optional[int] = None
    description: Optional[str] = None
    remarks: Optional[str] = None
    custom_fields: Optional[str] = None
    images: Optional[List[str]] = None  # 资产照片URL列表
    # 注意：attachments 通过专门的 API 管理，不在 AssetUpdate 中


class AssetResponse(AssetBase):
    id: int
    asset_no: str
    status: AssetStatus
    qr_code: Optional[str] = None
    images: Optional[str] = None
    attachments: Optional[str] = None
    custom_fields: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


# ========== 附件 Schema ==========
class AttachmentInfo(BaseModel):
    """附件信息"""
    name: str           # 文件名
    url: str            # 访问路径
    type: str           # 文件类型
    size: int          # 文件大小(bytes)
    uploaded_at: str    # 上传时间


class AssetAssign(BaseModel):
    user_id: int
    keeper_id: Optional[int] = None
    department_id: Optional[int] = None
    location: Optional[str] = Field(None, max_length=200)
    remarks: Optional[str] = None


class AssetTransfer(BaseModel):
    target_department_id: Optional[int] = None
    target_user_id: Optional[int] = None
    target_keeper_id: Optional[int] = None
    target_location: Optional[str] = Field(None, max_length=200)
    remarks: Optional[str] = None


# ========== 资产变动记录 Schema ==========
class AssetRecordResponse(BaseModel):
    id: int
    asset_id: int
    action_type: str
    before_data: Optional[str] = None
    after_data: Optional[str] = None
    description: Optional[str] = None
    operator_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 易耗品领用 Schema ==========
class ConsumableRecordCreate(BaseModel):
    asset_id: int
    employee_id: int
    quantity: int = Field(..., gt=0)
    purpose: Optional[str] = None
    department_id: Optional[int] = None


class ConsumableRecordResponse(BaseModel):
    id: int
    asset_id: int
    employee_id: int
    quantity: int
    purpose: Optional[str] = None
    department_id: Optional[int] = None
    operator_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 报修工单 Schema ==========
class RepairOrderCreate(BaseModel):
    asset_id: int
    description: str
    images: Optional[List[str]] = None
    priority: str = "normal"


class RepairOrderUpdate(BaseModel):
    handler_id: Optional[int] = None
    status: Optional[str] = None
    repair_result: Optional[str] = None
    repair_cost: Optional[float] = None
    parts_used: Optional[str] = None


class RepairOrderResponse(BaseModel):
    id: int
    order_no: str
    asset_id: int
    reporter_id: int
    description: str
    images: Optional[str] = None
    priority: str
    status: str
    handler_id: Optional[int] = None
    repair_result: Optional[str] = None
    repair_cost: Optional[float] = None
    parts_used: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 报废申请 Schema ==========
class ScrapOrderCreate(BaseModel):
    asset_id: int
    reason: str
    description: Optional[str] = None
    images: Optional[List[str]] = None


class ScrapOrderReview(BaseModel):
    status: str  # approved/rejected
    review_comment: Optional[str] = None
    disposal_method: Optional[str] = None
    residual_value: Optional[float] = None


class ScrapOrderResponse(BaseModel):
    id: int
    order_no: str
    asset_id: int
    applicant_id: int
    reason: str
    description: Optional[str] = None
    images: Optional[str] = None
    status: str
    reviewer_id: Optional[int] = None
    review_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    disposal_method: Optional[str] = None
    residual_value: Optional[float] = None
    disposal_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 盘点 Schema ==========
class InventoryCheckCreate(BaseModel):
    name: str = Field(..., max_length=200)
    start_date: datetime
    end_date: Optional[datetime] = None
    categories: Optional[List[int]] = None
    departments: Optional[List[int]] = None


class InventoryCheckUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    end_date: Optional[datetime] = None
    status: Optional[str] = None


class InventoryCheckItemUpdate(BaseModel):
    actual_status: Optional[str] = None
    actual_location: Optional[str] = None
    actual_user_id: Optional[int] = None
    check_result: Optional[str] = None
    remarks: Optional[str] = None


class InventoryCheckResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    categories: Optional[str] = None
    departments: Optional[str] = None
    status: str
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryCheckItemResponse(BaseModel):
    id: int
    check_id: int
    asset_id: int
    expected_status: Optional[str] = None
    actual_status: Optional[str] = None
    expected_location: Optional[str] = None
    actual_location: Optional[str] = None
    expected_user_id: Optional[int] = None
    actual_user_id: Optional[int] = None
    check_result: Optional[str] = None
    remarks: Optional[str] = None
    checked_by: Optional[int] = None
    checked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 通用 Schema ==========
class PageResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List


class BatchImportResult(BaseModel):
    success: int
    failed: int
    errors: List[str]
