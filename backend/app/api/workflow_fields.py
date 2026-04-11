"""
工作流字段配置 API

配置分配/调拨/盘点/报修/报废等工作流的字段
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.models.custom_field import WorkflowFieldConfig, FieldType

router = APIRouter()

# 工作流类型
WORKFLOW_TYPES = ["assign", "transfer", "return", "check", "repair", "scrap"]


# ============ Schema ============

class WorkflowFieldCreate(BaseModel):
    """创建工作流字段"""
    field_name: str = Field(..., min_length=1, max_length=50, description="字段标识")
    field_label: str = Field(..., min_length=1, max_length=100, description="显示名称")
    field_type: str = Field(default="text", description="字段类型")
    options: Optional[List[str]] = Field(default=None, description="下拉选项")
    required: bool = Field(default=False, description="是否必填")
    show_in_form: bool = Field(default=True, description="是否在表单显示")
    show_in_history: bool = Field(default=True, description="是否在历史记录显示")
    editable_by_user: bool = Field(default=True, description="用户是否可编辑")
    default_value: Optional[str] = Field(default=None, max_length=255, description="默认值")
    sort_order: int = Field(default=0, description="排序顺序")


class WorkflowFieldUpdate(BaseModel):
    """更新工作流字段"""
    field_label: Optional[str] = Field(default=None, max_length=100, description="显示名称")
    field_type: Optional[str] = Field(default=None, description="字段类型")
    options: Optional[List[str]] = Field(default=None, description="下拉选项")
    required: Optional[bool] = Field(default=None, description="是否必填")
    show_in_form: Optional[bool] = Field(default=None, description="是否在表单显示")
    show_in_history: Optional[bool] = Field(default=None, description="是否在历史记录显示")
    editable_by_user: Optional[bool] = Field(default=None, description="用户是否可编辑")
    default_value: Optional[str] = Field(default=None, max_length=255, description="默认值")
    sort_order: Optional[int] = Field(default=None, description="排序顺序")
    is_active: Optional[bool] = Field(default=None, description="是否启用")


class WorkflowFieldResponse(BaseModel):
    """工作流字段响应"""
    id: int
    workflow_type: str
    field_name: str
    field_label: str
    field_type: str
    options: List[str] = []
    required: bool
    show_in_form: bool
    show_in_history: bool
    editable_by_user: bool
    default_value: Optional[str] = None
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


# ============ API ============

@router.get("/{workflow_type}", response_model=List[WorkflowFieldResponse])
async def get_workflow_fields(
    workflow_type: str,
    include_inactive: bool = Query(False, description="包含已禁用的字段"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定工作流的字段配置

    workflow_type 可选值:
    - assign: 资产分配
    - transfer: 资产调拨
    - return: 资产退库
    - check: 资产盘点
    - repair: 报修工单
    - scrap: 报废申请
    """
    if workflow_type not in WORKFLOW_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的工作流类型: {workflow_type}，可选: {', '.join(WORKFLOW_TYPES)}"
        )

    query = db.query(WorkflowFieldConfig).filter(
        WorkflowFieldConfig.workflow_type == workflow_type
    )

    if not include_inactive:
        query = query.filter(WorkflowFieldConfig.is_active == True)

    fields = query.order_by(WorkflowFieldConfig.sort_order).all()

    result = []
    for field in fields:
        field_dict = field.to_dict()
        field_dict["options"] = field.get_options_list()
        result.append(WorkflowFieldResponse(**field_dict))

    return result


@router.post("/{workflow_type}", response_model=WorkflowFieldResponse)
async def create_workflow_field(
    workflow_type: str,
    field_data: WorkflowFieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    为指定工作流创建字段

    需要资产更新权限
    """
    if workflow_type not in WORKFLOW_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的工作流类型: {workflow_type}"
        )

    # 验证字段类型
    try:
        field_type = FieldType(field_data.field_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"无效的字段类型: {field_data.field_type}，可选: text, number, date, select, multi_select, textarea, checkbox"
        )

    # 检查字段名是否已存在
    existing = db.query(WorkflowFieldConfig).filter(
        WorkflowFieldConfig.workflow_type == workflow_type,
        WorkflowFieldConfig.field_name == field_data.field_name
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

    import json
    field = WorkflowFieldConfig(
        workflow_type=workflow_type,
        field_name=field_data.field_name,
        field_label=field_data.field_label,
        field_type=field_type,
        options=json.dumps(field_data.options) if field_data.options else None,
        required=field_data.required,
        show_in_form=field_data.show_in_form,
        show_in_history=field_data.show_in_history,
        editable_by_user=field_data.editable_by_user,
        default_value=field_data.default_value,
        sort_order=field_data.sort_order,
    )

    db.add(field)
    db.commit()
    db.refresh(field)

    field_dict = field.to_dict()
    field_dict["options"] = field.get_options_list()
    return WorkflowFieldResponse(**field_dict)


@router.put("/{field_id}", response_model=WorkflowFieldResponse)
async def update_workflow_field(
    field_id: int,
    field_data: WorkflowFieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    更新工作流字段配置
    """
    field = db.query(WorkflowFieldConfig).filter(
        WorkflowFieldConfig.id == field_id
    ).first()

    if not field:
        raise HTTPException(status_code=404, detail="字段不存在")

    update_dict = field_data.model_dump(exclude_unset=True)

    if "options" in update_dict:
        import json
        update_dict["options"] = json.dumps(update_dict["options"]) if update_dict["options"] else None

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

    field_dict = field.to_dict()
    field_dict["options"] = field.get_options_list()
    return WorkflowFieldResponse(**field_dict)


@router.delete("/{field_id}")
async def delete_workflow_field(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    删除工作流字段配置
    """
    field = db.query(WorkflowFieldConfig).filter(
        WorkflowFieldConfig.id == field_id
    ).first()

    if not field:
        raise HTTPException(status_code=404, detail="字段不存在")

    db.delete(field)
    db.commit()

    return {"message": "字段已删除"}


@router.get("/")
async def list_all_workflow_fields(
    include_inactive: bool = Query(False, description="包含已禁用的字段"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有工作流的字段配置

    按工作流类型分组返回
    """
    result = {}
    for wf_type in WORKFLOW_TYPES:
        query = db.query(WorkflowFieldConfig).filter(
            WorkflowFieldConfig.workflow_type == wf_type
        )
        if not include_inactive:
            query = query.filter(WorkflowFieldConfig.is_active == True)

        fields = query.order_by(WorkflowFieldConfig.sort_order).all()
        result[wf_type] = []
        for field in fields:
            field_dict = field.to_dict()
            field_dict["options"] = field.get_options_list()
            result[wf_type].append(field_dict)

    return result


@router.post("/{workflow_type}/reset")
async def reset_workflow_fields(
    workflow_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    重置工作流字段配置为默认值

    删除所有自定义字段，恢复系统默认配置
    """
    if workflow_type not in WORKFLOW_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的工作流类型: {workflow_type}"
        )

    deleted_count = db.query(WorkflowFieldConfig).filter(
        WorkflowFieldConfig.workflow_type == workflow_type
    ).delete()

    db.commit()

    return {
        "message": f"已重置 {workflow_type} 工作流字段配置",
        "deleted_count": deleted_count
    }


@router.post("/{workflow_type}/batch")
async def batch_create_workflow_fields(
    workflow_type: str,
    fields_data: List[WorkflowFieldCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("asset", "update"))
):
    """
    批量创建工作流字段

    一次创建多个字段
    """
    if workflow_type not in WORKFLOW_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的工作流类型: {workflow_type}"
        )

    import json
    created_fields = []

    for field_data in fields_data:
        try:
            field_type = FieldType(field_data.field_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的字段类型: {field_data.field_type}"
            )

        existing = db.query(WorkflowFieldConfig).filter(
            WorkflowFieldConfig.workflow_type == workflow_type,
            WorkflowFieldConfig.field_name == field_data.field_name
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"字段名 {field_data.field_name} 已存在"
            )

        if field_type in (FieldType.SELECT, FieldType.MULTI_SELECT):
            if not field_data.options:
                raise HTTPException(
                    status_code=400,
                    detail=f"字段类型 {field_data.field_type} 需要提供 options"
                )

        field = WorkflowFieldConfig(
            workflow_type=workflow_type,
            field_name=field_data.field_name,
            field_label=field_data.field_label,
            field_type=field_type,
            options=json.dumps(field_data.options) if field_data.options else None,
            required=field_data.required,
            show_in_form=field_data.show_in_form,
            show_in_history=field_data.show_in_history,
            editable_by_user=field_data.editable_by_user,
            default_value=field_data.default_value,
            sort_order=field_data.sort_order,
        )

        db.add(field)
        created_fields.append(field)

    db.commit()

    result = []
    for field in created_fields:
        db.refresh(field)
        field_dict = field.to_dict()
        field_dict["options"] = field.get_options_list()
        result.append(WorkflowFieldResponse(**field_dict))

    return {"created": len(result), "fields": result}
