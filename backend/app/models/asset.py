"""
数据库模型 - 资产相关模型
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AssetType(str, enum.Enum):
    """资产类型"""
    FIXED = "fixed"           # 固定资产
    CONSUMABLE = "consumable" # 易耗品


class AssetStatus(str, enum.Enum):
    """资产状态"""
    STOCK = "stock"           # 在库/空闲
    IN_USE = "in_use"         # 使用中
    REPAIR = "repair"          # 维修中
    SCRAPPED = "scrapped"     # 已报废
    LOST = "lost"             # 丢失


class Category(Base):
    """资产分类"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    code = Column(String(50), unique=True, nullable=False, comment="分类编码")
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True, comment="父分类ID")
    asset_type = Column(Enum(AssetType), nullable=False, comment="资产类型")
    description = Column(Text, nullable=True, comment="分类描述")
    icon = Column(String(100), nullable=True, comment="分类图标")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    custom_fields = Column(Text, nullable=True, comment="自定义字段JSON")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    parent = relationship("Category", remote_side=[id], backref="children")
    assets = relationship("Asset", back_populates="category")


class Department(Base):
    """部门"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="部门名称")
    code = Column(String(50), unique=True, nullable=False, comment="部门编码")
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="父部门ID")
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="部门负责人")
    description = Column(Text, nullable=True, comment="部门描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    parent = relationship("Department", remote_side=[id], backref="children")
    manager = relationship("Employee", foreign_keys=[manager_id], backref="managed_departments")
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    assets = relationship("Asset", back_populates="department")


class Employee(Base):
    """员工"""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_no = Column(String(50), unique=True, nullable=False, comment="员工工号")
    name = Column(String(100), nullable=False, comment="员工姓名")
    email = Column(String(100), nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="电话")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="所属部门")
    position = Column(String(100), nullable=True, comment="职位")
    status = Column(String(20), default="active", comment="状态: active/inactive/leave")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    assets = relationship("Asset", back_populates="user", foreign_keys="Asset.user_id")
    managed_assets = relationship("Asset", back_populates="keeper", foreign_keys="Asset.keeper_id")
    repair_orders = relationship("RepairOrder", foreign_keys="RepairOrder.reporter_id")
    handled_repairs = relationship("RepairOrder", foreign_keys="RepairOrder.handler_id")


class Asset(Base):
    """资产"""
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_no = Column(String(50), unique=True, nullable=False, comment="资产编码")
    name = Column(String(200), nullable=False, comment="资产名称")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, comment="资产分类")
    asset_type = Column(Enum(AssetType), nullable=False, comment="资产类型")
    status = Column(Enum(AssetStatus), default=AssetStatus.STOCK, comment="资产状态")

    # 基本属性
    brand = Column(String(100), nullable=True, comment="品牌")
    model = Column(String(100), nullable=True, comment="型号")
    serial_no = Column(String(100), nullable=True, comment="序列号")
    purchase_date = Column(DateTime, nullable=True, comment="购买日期")
    purchase_price = Column(Float, default=0, comment="购买价格")
    warranty_end = Column(DateTime, nullable=True, comment="保修结束日期")

    # 使用信息
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="使用部门")
    user_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="使用人")
    keeper_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="保管人")
    location = Column(String(200), nullable=True, comment="存放位置")

    # 易耗品专用
    quantity = Column(Integer, default=1, comment="数量")
    unit = Column(String(20), nullable=True, comment="单位")
    min_stock = Column(Integer, nullable=True, comment="最低库存预警")
    current_stock = Column(Integer, nullable=True, comment="当前库存")

    # 二维码
    qr_code = Column(String(500), nullable=True, comment="二维码数据")

    # 图片
    images = Column(Text, nullable=True, comment="图片URLs JSON数组")

    # 自定义属性
    custom_fields = Column(Text, nullable=True, comment="自定义字段JSON")

    # 描述
    description = Column(Text, nullable=True, comment="资产描述")
    remarks = Column(Text, nullable=True, comment="备注")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True, comment="创建人")

    # 关系
    category = relationship("Category", back_populates="assets")
    department = relationship("Department", back_populates="assets")
    user = relationship("Employee", back_populates="assets", foreign_keys=[user_id])
    keeper = relationship("Employee", back_populates="managed_assets", foreign_keys=[keeper_id])
    records = relationship("AssetRecord", back_populates="asset")
    repair_orders = relationship("RepairOrder", back_populates="asset")


class AssetRecord(Base):
    """资产变动记录"""
    __tablename__ = "asset_records"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, comment="资产ID")
    action_type = Column(String(50), nullable=False, comment="操作类型: create/update/assign/transfer/return/repair/scrap")
    before_data = Column(Text, nullable=True, comment="变动前数据JSON")
    after_data = Column(Text, nullable=True, comment="变动后数据JSON")
    description = Column(Text, nullable=True, comment="变动说明")
    operator_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="操作人")
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    asset = relationship("Asset", back_populates="records")
    operator = relationship("Employee")


class ConsumableRecord(Base):
    """易耗品领用记录"""
    __tablename__ = "consumable_records"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, comment="易耗品ID")
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="领用人")
    quantity = Column(Integer, nullable=False, comment="领用数量")
    purpose = Column(Text, nullable=True, comment="领用用途")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="领用部门")
    operator_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="操作人")
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    asset = relationship("Asset")
    employee = relationship("Employee", foreign_keys=[employee_id])
    department = relationship("Department")
    operator = relationship("Employee", foreign_keys=[operator_id])


class RepairOrder(Base):
    """报修工单"""
    __tablename__ = "repair_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False, comment="工单编号")
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, comment="资产ID")
    reporter_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="报修人")
    description = Column(Text, nullable=False, comment="故障描述")
    images = Column(Text, nullable=True, comment="故障图片")
    priority = Column(String(20), default="normal", comment="优先级: low/normal/high/urgent")
    status = Column(String(20), default="pending", comment="状态: pending/assigned/processing/completed/cancelled")

    # 维修信息
    handler_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="处理人")
    repair_result = Column(Text, nullable=True, comment="维修结果")
    repair_cost = Column(Float, default=0, comment="维修费用")
    parts_used = Column(Text, nullable=True, comment="使用的配件")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    asset = relationship("Asset", back_populates="repair_orders")
    reporter = relationship("Employee", foreign_keys=[reporter_id])
    handler = relationship("Employee", foreign_keys=[handler_id])


class ScrapOrder(Base):
    """报废申请"""
    __tablename__ = "scrap_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False, comment="申请编号")
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, comment="资产ID")
    applicant_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="申请人")
    reason = Column(Text, nullable=False, comment="报废原因")
    description = Column(Text, nullable=True, comment="详细说明")
    images = Column(Text, nullable=True, comment="现场图片")

    # 审批流程
    status = Column(String(20), default="pending", comment="状态: pending/approved/rejected")
    reviewer_id = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="审批人")
    review_comment = Column(Text, nullable=True, comment="审批意见")
    reviewed_at = Column(DateTime, nullable=True, comment="审批时间")

    # 处置信息
    disposal_method = Column(String(50), nullable=True, comment="处置方式: recycle/discard/sell")
    residual_value = Column(Float, default=0, comment="残值")
    disposal_date = Column(DateTime, nullable=True, comment="处置日期")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    asset = relationship("Asset")
    applicant = relationship("Employee", foreign_keys=[applicant_id])
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])


class InventoryCheck(Base):
    """盘点计划"""
    __tablename__ = "inventory_checks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="盘点名称")
    start_date = Column(DateTime, nullable=False, comment="开始日期")
    end_date = Column(DateTime, nullable=True, comment="结束日期")
    categories = Column(Text, nullable=True, comment="盘点的分类ID列表JSON")
    departments = Column(Text, nullable=True, comment="盘点的部门ID列表JSON")
    status = Column(String(20), default="planning", comment="状态: planning/in_progress/completed/cancelled")
    created_by = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="创建人")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    creator = relationship("Employee")
    items = relationship("InventoryCheckItem", back_populates="check_plan")


class InventoryCheckItem(Base):
    """盘点明细"""
    __tablename__ = "inventory_check_items"

    id = Column(Integer, primary_key=True, index=True)
    check_id = Column(Integer, ForeignKey("inventory_checks.id"), nullable=False, comment="盘点计划ID")
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, comment="资产ID")
    expected_status = Column(String(20), nullable=True, comment="账面状态")
    actual_status = Column(String(20), nullable=True, comment="实际状态")
    expected_location = Column(String(200), nullable=True, comment="账面位置")
    actual_location = Column(String(200), nullable=True, comment="实际位置")
    expected_user_id = Column(Integer, nullable=True, comment="账面使用人")
    actual_user_id = Column(Integer, nullable=True, comment="实际使用人")
    check_result = Column(String(20), nullable=True, comment="盘点结果: normal/discrepancy/missing/extra")
    remarks = Column(Text, nullable=True, comment="备注")
    checked_by = Column(Integer, ForeignKey("employees.id"), nullable=True, comment="盘点人")
    checked_at = Column(DateTime, nullable=True, comment="盘点时间")

    # 关系
    check_plan = relationship("InventoryCheck", back_populates="items")
    asset = relationship("Asset")
    checker = relationship("Employee", foreign_keys=[checked_by])
