# AMS 资产管理系统 - 开发规划

> 本文件为项目开发遵循的主要规划文档
> 详细规划请参考 `docs/PLAN_DETAIL.md`

## 快速索引

| 模块 | Sprint | 状态 | 详细章节 |
|------|--------|------|----------|
| 测试基础设施 | Sprint 1 | 待开始 | Phase 1 |
| Web端CRUD测试 | Sprint 2-3 | 待开始 | Phase 2-4 |
| 可扩展性增强 | Sprint 4 | 待开始 | Phase 5 |
| 移动端H5 | Sprint 5 | 待开始 | Phase 6 |
| 微信小程序 | Sprint 6 | 待开始 | Phase 6 |
| 二维码管理 | Sprint 7 | 待开始 | Phase 7 |

## 当前项目状态

### 已完成 (~80%)
- Web端全部CRUD功能
- 基础认证与权限
- 资产流转（分配/调拨/退库）
- 报修/报废/盘点流程

### 待开发 (~20%)
- 测试体系
- 自定义字段系统
- 操作日志
- 移动端
- 二维码管理

---

## Phase 1: 测试基础设施

**目标**: 建立完整的测试框架

**文件清单**:
- `tests/__init__.py`
- `tests/conftest.py` - pytest fixtures
- `tests/test_auth.py` - 认证测试
- `tests/test_base.py` - 基础测试类

**测试用例** (5个):
- TEST-AUTH-001: test_login_success
- TEST-AUTH-002: test_login_invalid_credentials
- TEST-AUTH-003: test_get_current_user
- TEST-AUTH-004: test_change_password
- TEST-AUTH-005: test_unauthorized_access

---

## Phase 2-4: Web端CRUD模块测试

| 模块 | 测试文件 | 用例数 |
|------|----------|--------|
| 用户管理 | `tests/test_users.py` | 5 |
| 角色权限 | `tests/test_roles.py` | 4 |
| 部门管理 | `tests/test_departments.py` | 4 |
| 员工管理 | `tests/test_employees.py` | 4 |
| 分类管理 | `tests/test_categories.py` | 4 |
| 资产管理 | `tests/test_assets.py` | 7 |
| 易耗品 | `tests/test_consumables.py` | 5 |
| 报修管理 | `tests/test_repair.py` | 3 |
| 报废管理 | `tests/test_scrap.py` | 4 |
| 盘点管理 | `tests/test_inventory_check.py` | 5 |

---

## Phase 5: 可扩展性增强

### 模块13: 自定义字段系统

**数据模型** (`app/models/custom_field.py`):
```python
class CustomFieldDefinition(Base):
    category_id: int
    field_name: str       # 字段标识
    field_label: str      # 显示名称
    field_type: str       # text/number/date/select
    options: str          # 下拉选项JSON
    required: bool
    default_value: str
    sort_order: int
```

**API**:
```
GET  /api/custom-fields/category/{category_id}
POST /api/custom-fields/category/{category_id}
PUT  /api/custom-fields/{field_id}
DELETE /api/custom-fields/{field_id}
```

**前端组件**:
- `src/components/DynamicForm.vue`
- `src/components/fields/`

---

## Phase 6: 移动端

### 微信小程序
- Taro 框架
- 页面: 首页/扫码/资产详情/盘点/个人中心
- API: 认证/资产/盘点

### 移动端H5
- 路由: `/mobile/*`
- 组件: 扫码/资产/盘点
- 技术: html5-qrcode + IndexedDB离线

---

## Phase 7: 二维码管理

### 批量生成
- `src/views/qrcode/QrcodeGenerator.vue`
- `src/views/qrcode/QrcodePreview.vue`
- PDF导出 (jsPDF)

### 草料API集成
- `backend/app/utils/cai_liao_client.py`
- `backend/app/models/qrcode.py`

---

## 环境配置

### .env 文件
```bash
# 本地开发
PORT=8000

# 局域网测试 (防火墙友好)
PORT=8765

# 生产环境
PORT=8000
```

### 启动脚本
```bash
./start.sh development  # 本地
./start.sh lan         # 局域网
./start.sh production  # 云端
```
