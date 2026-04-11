"""
自定义字段模型

支持分类级自定义字段定义，实现资产信息的可扩展性
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class FieldType(str, enum.Enum):
    """字段类型"""
    TEXT = "text"              # 文本输入
    NUMBER = "number"          # 数字输入
    DATE = "date"             # 日期选择
    SELECT = "select"          # 下拉单选
    MULTI_SELECT = "multi_select"  # 下拉多选
    TEXTAREA = "textarea"      # 多行文本
    CHECKBOX = "checkbox"      # 复选框


class CustomFieldDefinition(Base):
    """
    自定义字段定义

    按资产分类定义字段，存储在 custom_fields JSON 字段中
    """
    __tablename__ = "custom_field_definitions"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, comment="所属分类ID")

    # 字段基本信息
    field_name = Column(String(50), nullable=False, comment="字段标识(snake_case)")
    field_label = Column(String(100), nullable=False, comment="显示名称")
    field_type = Column(Enum(FieldType), default=FieldType.TEXT, comment="字段类型")

    # 下拉选项（用于 select/multi_select 类型）
    options = Column(Text, nullable=True, comment="选项JSON数组")

    # 字段属性
    placeholder = Column(String(200), nullable=True, comment="占位提示文字")
    default_value = Column(String(255), nullable=True, comment="默认值")
    required = Column(Boolean, default=False, comment="是否必填")
    editable = Column(Boolean, default=True, comment="是否可编辑")
    visible = Column(Boolean, default=True, comment="是否可见")
    show_in_list = Column(Boolean, default=False, comment="是否在列表显示")

    # 布局配置
    sort_order = Column(Integer, default=0, comment="排序顺序")
    width = Column(String(20), default="full", comment="宽度: half/full")

    # 验证规则
    min_length = Column(Integer, nullable=True, comment="最小长度")
    max_length = Column(Integer, nullable=True, comment="最大长度")
    min_value = Column(String(50), nullable=True, comment="最小值")
    max_value = Column(String(50), nullable=True, comment="最大值")
    pattern = Column(String(200), nullable=True, comment="正则表达式")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    category = relationship("Category", backref="custom_field_definitions")

    def get_options_list(self) -> list:
        """获取选项列表"""
        if not self.options:
            return []
        import json
        try:
            return json.loads(self.options)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_options_list(self, options: list):
        """设置选项列表"""
        import json
        self.options = json.dumps(options)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "category_id": self.category_id,
            "field_name": self.field_name,
            "field_label": self.field_label,
            "field_type": self.field_type.value,
            "options": self.get_options_list(),
            "placeholder": self.placeholder,
            "default_value": self.default_value,
            "required": self.required,
            "editable": self.editable,
            "visible": self.visible,
            "show_in_list": self.show_in_list,
            "sort_order": self.sort_order,
            "width": self.width,
            "is_active": self.is_active,
        }


class WorkflowFieldConfig(Base):
    """
    工作流字段配置

    配置分配/调拨/盘点/报修/报废等工作流的字段
    """
    __tablename__ = "workflow_field_configs"

    id = Column(Integer, primary_key=True, index=True)

    # 工作流类型
    workflow_type = Column(String(50), nullable=False, comment="工作流类型")
    """
    可选值:
    - assign: 资产分配
    - transfer: 资产调拨
    - return: 资产退库
    - check: 资产盘点
    - repair: 报修工单
    - scrap: 报废申请
    """

    # 字段信息
    field_name = Column(String(50), nullable=False, comment="字段标识")
    field_label = Column(String(100), nullable=False, comment="显示名称")
    field_type = Column(Enum(FieldType), default=FieldType.TEXT, comment="字段类型")

    # 下拉选项
    options = Column(Text, nullable=True, comment="选项JSON数组")

    # 配置
    required = Column(Boolean, default=False, comment="是否必填")
    show_in_form = Column(Boolean, default=True, comment="是否在表单显示")
    show_in_history = Column(Boolean, default=True, comment="是否在历史记录显示")
    editable_by_user = Column(Boolean, default=True, comment="用户是否可编辑")
    default_value = Column(String(255), nullable=True, comment="默认值")

    # 排序
    sort_order = Column(Integer, default=0, comment="排序顺序")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def get_options_list(self) -> list:
        """获取选项列表"""
        if not self.options:
            return []
        import json
        try:
            return json.loads(self.options)
        except (json.JSONDecodeError, TypeError):
            return []

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "workflow_type": self.workflow_type,
            "field_name": self.field_name,
            "field_label": self.field_label,
            "field_type": self.field_type.value,
            "options": self.get_options_list(),
            "required": self.required,
            "show_in_form": self.show_in_form,
            "show_in_history": self.show_in_history,
            "editable_by_user": self.editable_by_user,
            "default_value": self.default_value,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
        }


class FieldTemplate(Base):
    """
    字段模板

    预定义的字段模板，可快速应用到分类
    """
    __tablename__ = "field_templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")

    # 适用范围
    applicable_asset_types = Column(Text, nullable=True, comment="适用的资产类型(JSON数组)")
    """如: ["fixed", "consumable", "real_estate"]"""

    # 字段定义
    fields = Column(Text, nullable=False, comment="字段定义JSON")
    """
    格式: [
        {"field_name": "color", "field_label": "颜色", "field_type": "select", "options": ["红色","蓝色","绿色"]},
        {"field_name": "size", "field_label": "尺寸", "field_type": "text"}
    ]
    """

    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_system = Column(Boolean, default=False, comment="是否系统模板")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def get_fields_list(self) -> list:
        """获取字段列表"""
        if not self.fields:
            return []
        import json
        try:
            return json.loads(self.fields)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_applicable_types(self) -> list:
        """获取适用资产类型"""
        if not self.applicable_asset_types:
            return []
        import json
        try:
            return json.loads(self.applicable_asset_types)
        except (json.JSONDecodeError, TypeError):
            return []
