"""
数据库初始化脚本
创建初始数据和超级管理员
"""
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.models.asset import Category, Department, Employee, Asset, AssetType
from app.models.user import User, Role, Permission
from app.core.security import get_password_hash
import json


def init_database():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")


def create_initial_data(db: Session):
    """创建初始数据"""

    # 创建权限
    permissions_data = [
        # 资产管理权限
        {"name": "查看资产", "code": "asset:read", "resource": "asset", "action": "read"},
        {"name": "创建资产", "code": "asset:create", "resource": "asset", "action": "create"},
        {"name": "编辑资产", "code": "asset:update", "resource": "asset", "action": "update"},
        {"name": "删除资产", "code": "asset:delete", "resource": "asset", "action": "delete"},

        # 分类权限
        {"name": "查看分类", "code": "category:read", "resource": "category", "action": "read"},
        {"name": "创建分类", "code": "category:create", "resource": "category", "action": "create"},
        {"name": "编辑分类", "code": "category:update", "resource": "category", "action": "update"},
        {"name": "删除分类", "code": "category:delete", "resource": "category", "action": "delete"},

        # 员工权限
        {"name": "查看员工", "code": "employee:read", "resource": "employee", "action": "read"},
        {"name": "创建员工", "code": "employee:create", "resource": "employee", "action": "create"},
        {"name": "编辑员工", "code": "employee:update", "resource": "employee", "action": "update"},
        {"name": "删除员工", "code": "employee:delete", "resource": "employee", "action": "delete"},

        # 部门权限
        {"name": "查看部门", "code": "department:read", "resource": "department", "action": "read"},
        {"name": "创建部门", "code": "department:create", "resource": "department", "action": "create"},
        {"name": "编辑部门", "code": "department:update", "resource": "department", "action": "update"},
        {"name": "删除部门", "code": "department:delete", "resource": "department", "action": "delete"},

        # 报修权限
        {"name": "查看报修", "code": "repair:read", "resource": "repair", "action": "read"},
        {"name": "创建报修", "code": "repair:create", "resource": "repair", "action": "create"},
        {"name": "处理报修", "code": "repair:update", "resource": "repair", "action": "update"},

        # 报废权限
        {"name": "查看报废", "code": "scrap:read", "resource": "scrap", "action": "read"},
        {"name": "创建报废", "code": "scrap:create", "resource": "scrap", "action": "create"},
        {"name": "审批报废", "code": "scrap:approve", "resource": "scrap", "action": "approve"},

        # 盘点权限
        {"name": "查看盘点", "code": "inventory_check:read", "resource": "inventory_check", "action": "read"},
        {"name": "创建盘点", "code": "inventory_check:create", "resource": "inventory_check", "action": "create"},
        {"name": "执行盘点", "code": "inventory_check:update", "resource": "inventory_check", "action": "update"},

        # 用户权限
        {"name": "查看用户", "code": "user:read", "resource": "user", "action": "read"},
        {"name": "创建用户", "code": "user:create", "resource": "user", "action": "create"},
        {"name": "编辑用户", "code": "user:update", "resource": "user", "action": "update"},
        {"name": "删除用户", "code": "user:delete", "resource": "user", "action": "delete"},

        # 角色权限
        {"name": "查看角色", "code": "role:read", "resource": "role", "action": "read"},
        {"name": "创建角色", "code": "role:create", "resource": "role", "action": "create"},
        {"name": "编辑角色", "code": "role:update", "resource": "role", "action": "update"},
    ]

    permissions = []
    for perm_data in permissions_data:
        perm = Permission(**perm_data)
        db.add(perm)
        permissions.append(perm)

    db.flush()

    # 创建角色
    # 超级管理员角色
    admin_role = Role(
        name="超级管理员",
        code="super_admin",
        description="系统超级管理员，拥有所有权限",
        is_system=True
    )
    admin_role.permissions = permissions
    db.add(admin_role)

    # 资产管理员角色
    asset_admin_role = Role(
        name="资产管理员",
        code="asset_admin",
        description="负责资产管理、盘点、维修等日常运营工作",
        is_system=False
    )
    asset_admin_role.permissions = [p for p in permissions if p.resource in ['asset', 'category', 'employee', 'department', 'repair', 'scrap', 'inventory_check']]
    db.add(asset_admin_role)

    # 普通员工角色
    normal_role = Role(
        name="普通员工",
        code="normal_user",
        description="普通员工，可查看资产、发起报修等",
        is_system=False
    )
    normal_role.permissions = [p for p in permissions if p.action == 'read' or p.code in ['repair:create', 'scrap:create']]
    db.add(normal_role)

    db.flush()

    # 创建超级管理员用户
    admin_user = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        real_name="系统管理员",
        email="admin@example.com",
        is_superuser=True,
        is_active=True
    )
    admin_user.roles = [admin_role]
    db.add(admin_user)

    # 创建资产管理员用户
    asset_user = User(
        username="asset_admin",
        password_hash=get_password_hash("asset123"),
        real_name="资产管理员",
        email="asset@example.com",
        is_superuser=False,
        is_active=True
    )
    asset_user.roles = [asset_admin_role]
    db.add(asset_user)

    # 创建初始分类
    categories = [
        # 固定资产
        {"name": "IT与办公设备", "code": "IT_DEVICE", "asset_type": AssetType.FIXED, "sort_order": 1},
        {"name": "台式电脑", "code": "DESKTOP", "asset_type": AssetType.FIXED, "sort_order": 11},
        {"name": "笔记本电脑", "code": "LAPTOP", "asset_type": AssetType.FIXED, "sort_order": 12},
        {"name": "服务器", "code": "SERVER", "asset_type": AssetType.FIXED, "sort_order": 13},
        {"name": "打印机", "code": "PRINTER", "asset_type": AssetType.FIXED, "sort_order": 14},
        {"name": "办公家具", "code": "FURNITURE", "asset_type": AssetType.FIXED, "sort_order": 2},
        {"name": "办公桌椅", "code": "DESK_CHAIR", "asset_type": AssetType.FIXED, "sort_order": 21},
        {"name": "文件柜", "code": "CABINET", "asset_type": AssetType.FIXED, "sort_order": 22},
        {"name": "会议设备", "code": "MEETING_DEVICE", "asset_type": AssetType.FIXED, "sort_order": 3},
        {"name": "投影仪", "code": "PROJECTOR", "asset_type": AssetType.FIXED, "sort_order": 31},
        {"name": "视频会议设备", "code": "VIDEO_DEVICE", "asset_type": AssetType.FIXED, "sort_order": 32},
        # 易耗品
        {"name": "办公用品", "code": "OFFICE_SUPPLY", "asset_type": AssetType.CONSUMABLE, "sort_order": 4},
        {"name": "纸张", "code": "PAPER", "asset_type": AssetType.CONSUMABLE, "sort_order": 41},
        {"name": "笔类", "code": "PEN", "asset_type": AssetType.CONSUMABLE, "sort_order": 42},
        {"name": "文件夹", "code": "FOLDER", "asset_type": AssetType.CONSUMABLE, "sort_order": 43},
        {"name": "IT耗材", "code": "IT_CONSUMABLE", "asset_type": AssetType.CONSUMABLE, "sort_order": 5},
        {"name": "墨盒", "code": "INK_CARTRIDGE", "asset_type": AssetType.CONSUMABLE, "sort_order": 51},
        {"name": "键盘鼠标", "code": "KEYBOARD_MOUSE", "asset_type": AssetType.CONSUMABLE, "sort_order": 52},
    ]

    created_categories = {}
    for cat_data in categories:
        cat = Category(**cat_data)
        db.add(cat)
        db.flush()
        created_categories[cat.code] = cat

    # 设置父子关系
    for cat_data in categories:
        code = cat_data["code"]
        if code == "IT_DEVICE":
            created_categories[code].parent_id = None
        elif code in ["DESKTOP", "LAPTOP", "SERVER", "PRINTER"]:
            created_categories[code].parent_id = created_categories["IT_DEVICE"].id
        elif code in ["DESK_CHAIR", "CABINET"]:
            created_categories[code].parent_id = created_categories["FURNITURE"].id
        elif code in ["PROJECTOR", "VIDEO_DEVICE"]:
            created_categories[code].parent_id = created_categories["MEETING_DEVICE"].id
        elif code in ["PAPER", "PEN", "FOLDER"]:
            created_categories[code].parent_id = created_categories["OFFICE_SUPPLY"].id
        elif code in ["INK_CARTRIDGE", "KEYBOARD_MOUSE"]:
            created_categories[code].parent_id = created_categories["IT_CONSUMABLE"].id

    # 创建初始部门
    departments = [
        {"name": "总经理办公室", "code": "CEO"},
        {"name": "技术部", "code": "TECH"},
        {"name": "市场部", "code": "MARKET"},
        {"name": "财务部", "code": "FINANCE"},
        {"name": "人力资源部", "code": "HR"},
        {"name": "行政部", "code": "ADMIN"},
    ]

    created_departments = {}
    for dept_data in departments:
        dept = Department(**dept_data)
        db.add(dept)
        db.flush()
        created_departments[dept.code] = dept

    # 创建初始员工
    employees = [
        {"employee_no": "E001", "name": "张三", "email": "zhangsan@example.com", "department_id": created_departments["CEO"].id, "position": "总经理"},
        {"employee_no": "E002", "name": "李四", "email": "lisi@example.com", "department_id": created_departments["TECH"].id, "position": "技术总监"},
        {"employee_no": "E003", "name": "王五", "email": "wangwu@example.com", "department_id": created_departments["TECH"].id, "position": "开发工程师"},
        {"employee_no": "E004", "name": "赵六", "email": "zhaoliu@example.com", "department_id": created_departments["MARKET"].id, "position": "市场经理"},
    ]

    for emp_data in employees:
        emp = Employee(**emp_data)
        db.add(emp)

    db.commit()
    print("初始数据创建完成")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        init_database()
        create_initial_data(db)
        print("数据库初始化完成！")
        print("\n初始账户：")
        print("  超级管理员: admin / admin123")
        print("  资产管理员: asset_admin / asset123")
    finally:
        db.close()
