"""
自定义字段 API

提供分类级自定义字段的 CRUD 操作
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.models.custom_field import CustomFieldDefinition, WorkflowFieldConfig, FieldTemplate, FieldType

router = APIRouter()


# ============ Schema ============

class CustomFieldCreate(BaseModel):
    """创建自定义字段"""
    field_name: str = Field(..., min_length=1, max_length=50, description="字段标识")
    field_label: str = Field(..., min_length=1, max_length=100, description="显示名称")
    field_type: str = Field(default="text", description="字段类型")
    options: Optional[List[str]] = Field(default=None, description="下拉选项")
    placeholder: Optional[str] = Field(default=None, max_length=200, description="占位提示")
    default_value: Optional[str] = Field(default=None, max_length=255, description="默认值")
    required: bool = Field(default=False, description="是否必填")
    editable: bool = Field(default=True, description="是否可编辑")
    visible: bool = Field(default=True, description="是否可见")
    show_in_list: bool = Field(default=False, description="是否在列表显示")
    sort_order: int = Field(default=0, description="排序顺序")
    width: str = Field(default="full", description="宽度: half/full")
    min_length: Optional[int] = Field(default=None, description="最小长度")
    max_length: Optional[int] = Field(default=None, description="最大长度")
    min_value: Optional[str] = Field(default=None, description="最小值")
    max_value: Optional[str] = Field(default=None, description="最大值")
    pattern: Optional[str] = Field(default=None, description="正则表达式")


class CustomFieldUpdate(BaseModel):
    """更新自定义字段"""
    field_label: Optional[str] = Field(default=None, max_length=100, description="显示名称")
    field_type: Optional[str] = Field(default=None, description="字段类型")
    options: Optional[List[str]] = Field(default=None, description="下拉选项")
    placeholder: Optional[str] = Field(default=None, max_length=200, description="占位提示")
    default_value: Optional[str] = Field(default=None, max_length=255, description="默认值")
    required: Optional[bool] = Field(default=None, description="是否必填")
    editable: Optional[bool] = Field(default=None, description="是否可编辑")
    visible: Optional[bool] = Field(default=None, description="是否可见")
    show_in_list: Optional[bool] = Field(default=None, description="是否在列表显示")
    sort_order: Optional[int] = Field(default=None, description="排序顺序")
    width: Optional[str] = Field(default=None, description="宽度: half/full")
    min_length: Optional[int] = Field(default=None, description="最小长度")
    max_length: Optional[int] = Field(default=None, description="最大长度")
    min_value: Optional[str] = Field(default=None, description="最小值")
    max_value: Optional[str] = Field(default=None, description="最大值")
    pattern: Optional[str] = Field(default=None, description="正则表达式")
    is_active: Optional[bool] = Field(default=None, description="是否启用")


class CustomFieldResponse(BaseModel):
    """自定义字段响应"""
    id: int
    category_id: int
    field_name: str
    field_label: str
    field_type: str
    options: List[str] = []
    placeholder: Optional[str] = None
    default_value: Optional[str] = None
    required: bool
    editable: bool
    visible: bool
    show_in_list: bool
    sort_order: int
    width: str
    is_active: bool

    class Config:
        from_attributes = True


# ============ API ============

@router.get("/category/{category_id}", response_model=List[CustomFieldResponse])
async def get_category_fields(
    category_id: int,
    include_inactive: bool = Query(False, description="包含已禁用的字段"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取分类的自定义字段定义

    返回该分类下所有启用的自定义字段，按 sort_order 排序
    """
    query = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.category_id == category_id
    )

    if not include_inactive:
        query = query.filter(CustomFieldDefinition.is_active == True)

    fields = query.order_by(CustomFieldDefinition.sort_order).all()

    # 转换 options JSON 为列表
    result = []
    for field in fields:
        field_dict = field.to_dict()
        field_dict["options"] = field.get_options_list()
        result.append(CustomFieldResponse(**field_dict))

    return result


@router.post("/category/{category_id}", response_model=CustomFieldResponse)
async def create_category_field(
    category_id: int,
    field_data: CustomFieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    为分类创建自定义字段

    需要资产更新权限
    """
    # 验证字段类型
    try:
        field_type = FieldType(field_data.field_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"无效的字段类型: {field_data.field_type}，可选: text, number, date, select, multi_select, textarea, checkbox"
        )

    # 检查字段名是否已存在
    existing = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.category_id == category_id,
        CustomFieldDefinition.field_name == field_data.field_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"字段名 {field_data.field_name} 已存在"
        )

    # 验证选项（select/multi_select 类型需要选项）
    if field_type in (FieldType.SELECT, FieldType.MULTI_SELECT):
        if not field_data.options:
            raise HTTPException(
                status_code=400,
                detail=f"字段类型 {field_data.field_type} 需要提供 options"
            )

    # 创建字段
    import json
    field = CustomFieldDefinition(
        category_id=category_id,
        field_name=field_data.field_name,
        field_label=field_data.field_label,
        field_type=field_type,
        options=json.dumps(field_data.options) if field_data.options else None,
        placeholder=field_data.placeholder,
        default_value=field_data.default_value,
        required=field_data.required,
        editable=field_data.editable,
        visible=field_data.visible,
        show_in_list=field_data.show_in_list,
        sort_order=field_data.sort_order,
        width=field_data.width,
        min_length=field_data.min_length,
        max_length=field_data.max_length,
        min_value=field_data.min_value,
        max_value=field_data.max_value,
        pattern=field_data.pattern,
    )

    db.add(field)
    db.commit()
    db.refresh(field)

    # 转换并返回
    field_dict = field.to_dict()
    field_dict["options"] = field.get_options_list()
    return CustomFieldResponse(**field_dict)


@router.put("/{field_id}", response_model=CustomFieldResponse)
async def update_field(
    field_id: int,
    field_data: CustomFieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    更新自定义字段定义
    """
    field = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.id == field_id
    ).first()

    if not field:
        raise HTTPException(status_code=404, detail="字段不存在")

    # 更新字段
    update_dict = field_data.model_dump(exclude_unset=True)

    # 处理 options
    if "options" in update_dict:
        import json
        update_dict["options"] = json.dumps(update_dict["options"]) if update_dict["options"] else None

    # 处理 field_type
    if "field_type" in update_dict and update_dict["field_type"]:
        try:
            update_dict["field_type"] = FieldType(update_dict["field_type"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的字段类型: {update_dict['field_type']}"
            )

    for key, value in update_dict.items():
        setattr(field, key, value)

    db.commit()
    db.refresh(field)

    # 转换并返回
    field_dict = field.to_dict()
    field_dict["options"] = field.get_options_list()
    return CustomFieldResponse(**field_dict)


@router.delete("/{field_id}")
async def delete_field(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    删除自定义字段定义
    """
    field = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.id == field_id
    ).first()

    if not field:
        raise HTTPException(status_code=404, detail="字段不存在")

    db.delete(field)
    db.commit()

    return {"message": "字段已删除"}


@router.post("/category/{category_id}/batch")
async def batch_create_fields(
    category_id: int,
    fields_data: List[CustomFieldCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    批量创建自定义字段

    一次创建多个字段
    """
    import json
    created_fields = []

    for field_data in fields_data:
        # 验证字段类型
        try:
            field_type = FieldType(field_data.field_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的字段类型: {field_data.field_type}"
            )

        # 检查重复
        existing = db.query(CustomFieldDefinition).filter(
            CustomFieldDefinition.category_id == category_id,
            CustomFieldDefinition.field_name == field_data.field_name
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"字段名 {field_data.field_name} 已存在"
            )

        # 验证选项
        if field_type in (FieldType.SELECT, FieldType.MULTI_SELECT):
            if not field_data.options:
                raise HTTPException(
                    status_code=400,
                    detail=f"字段类型 {field_data.field_type} 需要提供 options"
                )

        field = CustomFieldDefinition(
            category_id=category_id,
            field_name=field_data.field_name,
            field_label=field_data.field_label,
            field_type=field_type,
            options=json.dumps(field_data.options) if field_data.options else None,
            placeholder=field_data.placeholder,
            default_value=field_data.default_value,
            required=field_data.required,
            editable=field_data.editable,
            visible=field_data.visible,
            show_in_list=field_data.show_in_list,
            sort_order=field_data.sort_order,
            width=field_data.width,
        )

        db.add(field)
        created_fields.append(field)

    db.commit()

    # 返回创建成功的字段
    result = []
    for field in created_fields:
        db.refresh(field)
        field_dict = field.to_dict()
        field_dict["options"] = field.get_options_list()
        result.append(CustomFieldResponse(**field_dict))

    return {"created": len(result), "fields": result}


@router.get("/templates")
async def get_field_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取预定义的字段模板
    """
    templates = db.query(FieldTemplate).filter(
        FieldTemplate.is_active == True
    ).all()

    result = []
    for template in templates:
        result.append({
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "applicable_asset_types": template.get_applicable_types(),
            "fields": template.get_fields_list(),
        })

    return result


@router.post("/category/{category_id}/apply-template/{template_id}")
async def apply_template_to_category(
    category_id: int,
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    将字段模板应用到分类

    根据模板创建自定义字段
    """
    template = db.query(FieldTemplate).filter(
        FieldTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    fields = template.get_fields_list()
    if not fields:
        raise HTTPException(status_code=400, detail="模板无字段定义")

    import json
    created_fields = []

    # 获取当前最大排序值
    max_order = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.category_id == category_id
    ).count()

    for idx, field_def in enumerate(fields):
        field_name = field_def.get("field_name")
        if not field_name:
            continue

        # 检查是否已存在
        existing = db.query(CustomFieldDefinition).filter(
            CustomFieldDefinition.category_id == category_id,
            CustomFieldDefinition.field_name == field_name
        ).first()

        if existing:
            continue

        try:
            field_type = FieldType(field_def.get("field_type", "text"))
        except ValueError:
            field_type = FieldType.TEXT

        field = CustomFieldDefinition(
            category_id=category_id,
            field_name=field_name,
            field_label=field_def.get("field_label", field_name),
            field_type=field_type,
            options=json.dumps(field_def.get("options")) if field_def.get("options") else None,
            placeholder=field_def.get("placeholder"),
            default_value=field_def.get("default_value"),
            required=field_def.get("required", False),
            sort_order=max_order + idx,
            width=field_def.get("width", "full"),
        )

        db.add(field)
        created_fields.append(field)

    db.commit()

    return {
        "message": f"成功创建 {len(created_fields)} 个字段",
        "created_count": len(created_fields),
    }
