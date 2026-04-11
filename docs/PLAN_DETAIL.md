# AMS 资产管理系统 - 开发整体进度规划

> 本文件为项目详细开发规划，请配合 `docs/PLAN.md` 快速索引使用

## Context

AMS（资产管理系统）是一款面向公司内部的资产全生命周期管理软件，采用 FastAPI + Vue 3 前后端分离架构。

**需求变更冗余设计**：
1. **资产信息条目可扩展** - 支持分类级自定义字段定义，无需修改代码即可增减字段
2. **功能节点可配置** - 分配/调拨/盘点/预警等功能的具体信息条目可配置
3. **网络部署灵活性** - 支持本地/局域网/云端多环境部署，非标准端口避免阻断

**功能范围**：
1. **Web 端** - 完整资产管理后台
2. **移动端微信小程序** - 扫码/查询/更新/盘点
3. **移动端 H5** - 浏览器访问（简化版）
4. **二维码管理** - 批量生成/排版打印/草料API集成

---

## 一、数据模型设计（可扩展性）

### 1.1 当前固定字段 vs 自定义字段

```
┌─────────────────────────────────────────────────────────────┐
│                        Asset 资产表                          │
├─────────────────────────────────────────────────────────────┤
│  固定字段 (系统内置)        │  自定义字段 (分类定义)          │
├─────────────────────────────────────────────────────────────┤
│  id, asset_no, name         │  custom_fields JSON            │
│  category_id, asset_type    │  按 CategoryCustomField 定义    │
│  status, brand, model       │  动态渲染表单和详情            │
│  serial_no, location        │                               │
│  department_id, user_id     │                               │
│  purchase_date, price       │                               │
│  warranty_end, ...          │                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 自定义字段模型设计

```python
# app/models/custom_field.py (新增)
class CustomFieldDefinition(Base):
    """自定义字段定义"""
    __tablename__ = "custom_field_definitions"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    field_name = Column(String(50))      # 字段标识
    field_label = Column(String(100))     # 显示名称
    field_type = Column(String(20))       # text/number/date/select/multi_select
    options = Column(Text)                # 下拉选项JSON ["option1","option2"]
    required = Column(Boolean, default=False)
    default_value = Column(String(255))
    sort_order = Column(Integer, default=0)

class FieldTemplate(Base):
    """字段模板（可选：预定义模板）"""
    __tablename__ = "field_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))           # 模板名称
    field_type = Column(String(20))      # 适用资产类型
    fields = Column(Text)                # JSON: [{field_definitions}]
```

### 1.3 各功能节点可配置字段

```python
# app/models/workflow_field.py (新增)
class WorkflowFieldConfig(Base):
    """工作流字段配置"""
    __tablename__ = "workflow_field_configs"

    id = Column(Integer, primary_key=True)
    workflow_type = Column(String(50))   # assign/transfer/check/repair/scrap
    field_name = Column(String(50))
    field_label = Column(String(100))
    field_type = Column(String(20))
    required = Column(Boolean)
    show_in_list = Column(Boolean)        # 是否在列表显示
    editable_by_user = Column(Boolean)    # 用户是否可编辑

# workflow_type 可选值:
# - assign: 分配时填写
# - transfer: 调拨时填写
# - check: 盘点时填写
# - repair: 报修时填写
# - scrap: 报废时填写
# - alert: 预警规则配置
```

---

## 二、模块划分与优先级

### Phase 1: 基础层 (Web端 - 已实现，补充测试)

| 模块 | 文件位置 | 功能清单 | 状态 |
|------|----------|----------|------|
| 1.1 用户认证与权限 | `app/api/auth.py` | 登录/注册/密码修改/权限获取 | 已实现 |
| 1.2 用户管理 | `app/api/permissions.py` | CRUD/角色分配/禁用 | 已实现 |
| 1.3 角色权限 | `app/api/permissions.py` | 角色CRUD/权限绑定 | 已实现 |

### Phase 2: 组织架构层

| 模块 | 文件位置 | 功能清单 | 状态 |
|------|----------|----------|------|
| 2.1 部门管理 | `app/api/departments.py` | 树形部门CRUD/删除检查 | 已实现 |
| 2.2 员工管理 | `app/api/employees.py` | 员工CRUD/软删除 | 已实现 |

### Phase 3: 资产基础层

| 模块 | 文件位置 | 功能清单 | 状态 |
|------|----------|----------|------|
| 3.1 分类管理 | `app/api/categories.py` | 多级分类CRUD | 已实现 |
| 3.2 资产登记 | `app/api/assets.py` | CRUD/二维码/照片上传 | 已实现 |
| 3.3 资产流转 | `app/api/assets.py` | 分配/调拨/退库 | 已实现 |

### Phase 4: 业务功能层

| 模块 | 文件位置 | 功能清单 | 状态 |
|------|----------|----------|------|
| 4.1 易耗品管理 | `app/api/inventory.py` | 库存/领用/补货/预警 | 已实现 |
| 4.2 报修管理 | `app/api/repair.py` | 工单/指派/完成 | 已实现 |
| 4.3 报废管理 | `app/api/scrap.py` | 申请/审批/处置 | 已实现 |
| 4.4 盘点管理 | `app/api/inventory_check.py` | 计划/扫码盘点/报告 | 已实现 |

### Phase 5: 可扩展性增强 (待实现)

| 模块 | 优先级 | 功能清单 |
|------|--------|----------|
| 5.1 自定义字段定义 | 高 | 分类级字段定义与表单渲染 |
| 5.2 工作流字段配置 | 中 | 分配/调拨/盘点等功能字段可配置 |
| 5.3 操作日志 | 高 | 拦截器自动记录CRUD操作 |
| 5.4 批量导入 | 高 | Excel批量创建资产/员工 |
| 5.5 数据导出 | 中 | CSV/Excel导出资产报表 |

### Phase 6: 移动端 - 微信小程序

| 模块 | 功能清单 | 技术方案 |
|------|----------|----------|
| 6.1 登录授权 | 微信一键登录、Token刷新 | 微信小程序 wx.login + 后端 JWT |
| 6.2 扫码查询 | 扫描资产二维码查询详情 | wx.scanCode |
| 6.3 扫码盘点 | 扫描资产确认盘点状态 | InventoryCheck API |
| 6.4 资产更新 | 更新使用人/位置/状态 | PATCH /api/assets/{id} |
| 6.5 我的待办 | 待盘点/待处理报修/待确认 | 个人任务列表 |
| 6.6 消息通知 | 盘点提醒/报修进度 | 微信消息订阅 |

### Phase 7: 移动端 - H5 浏览器版

| 模块 | 功能清单 | 技术方案 |
|------|----------|----------|
| 7.1 响应式页面 | 适配手机屏幕 | Vue 3 + Element Plus 响应式 |
| 7.2 扫码功能 | 调用浏览器扫码API | Web API /wx.miniProgram |
| 7.3 简化操作 | 移动端精简版功能 | 独立的 mobile 路由 |
| 7.4 离线缓存 | IndexedDB 本地缓存 | 盘点离线模式 |

### Phase 8: 二维码管理

| 模块 | 功能清单 | 技术方案 |
|------|----------|----------|
| 8.1 批量生成 | 按分类/部门批量生成二维码 | qrcode library |
| 8.2 排版打印 | A4纸排版、PDF导出 | 前端 canvas + jsPDF |
| 8.3 草料二维码 | API对接、批量创建、数据同步 | 草料二维码 API |
| 8.4 二维码管理 | 绑定/解绑/重新生成 | CRUD + 关联表 |

---

## 三、网络部署配置

### 3.1 多环境配置

```python
# app/core/config.py

class Settings(BaseSettings):
    # 环境标识
    ENVIRONMENT: str = "development"  # development / lan / production

    # 数据库
    DATABASE_URL: str = "sqlite:///./ams.db"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000                  # 可配置非标准端口

    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # API Base URL (二维码内容/邮件链接等)
    API_BASE_URL: str = "http://localhost:8000"

    # 二维码访问基础URL
    QRCODE_BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
```

### 3.2 部署场景配置

| 场景 | PORT | API_BASE_URL | CORS_ORIGINS |
|------|------|--------------|--------------|
| 本地开发 | 8000 | http://localhost:8000 | localhost:* |
| 局域网测试 | 8765 | http://192.168.x.x:8765 | * (或指定IP段) |
| 云服务器 | 80/443 | https://api.example.com | your-domain.com |

### 3.3 .env 文件模板

```bash
# .env.development (本地开发)
ENVIRONMENT=development
PORT=8000
DATABASE_URL=sqlite:///./ams.db
API_BASE_URL=http://localhost:8000
QRCODE_BASE_URL=http://localhost:8000
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# .env.lan (局域网测试)
ENVIRONMENT=lan
PORT=8765
DATABASE_URL=sqlite:///./ams.db
API_BASE_URL=http://192.168.1.100:8765
QRCODE_BASE_URL=http://192.168.1.100:8765
CORS_ORIGINS=["http://192.168.1.100:5173","*"]

# .env.production (云端部署)
ENVIRONMENT=production
PORT=8000
DATABASE_URL=mysql://user:pass@localhost:3306/ams
API_BASE_URL=https://api.yourdomain.com
QRCODE_BASE_URL=https://yourdomain.com
CORS_ORIGINS=["https://yourdomain.com"]
SECRET_KEY=<generate-secure-key>
```

### 3.4 启动脚本

```bash
#!/bin/bash
# start.sh

ENV=${1:-development}
source .env.${ENV}

echo "Starting AMS in ${ENV} mode..."
echo "API will be available at: ${API_BASE_URL}"
echo "CORS Origins: ${CORS_ORIGINS}"

cd backend
source venv/bin/activate
uvicorn main:app --host $HOST --port $PORT --reload
```

### 3.5 防火墙与端口

```
# 常用被封端口 (避免使用)
- 80, 443 (常被ISP阻断)
- 22 (SSH可能被限)
- 3306, 5432 (数据库端口)

# 推荐使用
- 8000-9000 (开发/测试)
- 8765 (局域网测试 - 非标准)
- 30000-40000 (企业内网)
```

---

## 四、每个模块的开发流程

### Step 1: 需求用例 (Requirements Test Cases)

```
用例编号: REQ-{模块}-{序号}
用例描述: [描述要实现的功能]
前置条件: [测试前需要准备的数据/状态]
测试步骤:
  1. [具体操作步骤]
  2. [具体操作步骤]
预期结果: [系统应该返回的响应/状态]
```

### Step 2: 设计用例 (Design Test Cases)

```
用例编号: DES-{模块}-{序号}
验证点: [要验证的设计细节]
检查方法: [如何检查设计是否正确]
标准: [符合/不符合标准的定义]
```

### Step 3: 测试用例 (Testing Test Cases)

```
用例编号: TEST-{模块}-{序号}
测试类型: [单元测试/集成测试/端到端测试]
测试数据: [准备什么测试数据]
测试方法: [调用API的方式]
断言条件: [assert 条件]
```

---

## 五、具体模块开发计划

### 模块 1: 测试基础设施搭建

#### 1.1 实现文件:
- `tests/__init__.py`
- `tests/conftest.py` - pytest fixtures
- `tests/test_auth.py` - 认证测试
- `tests/test_base.py` - 基础测试类

#### 1.2 测试用例
```python
# tests/test_auth.py
TEST-AUTH-001: test_login_success
TEST-AUTH-002: test_login_invalid_credentials
TEST-AUTH-003: test_get_current_user
TEST-AUTH-004: test_change_password
TEST-AUTH-005: test_unauthorized_access
```

---

### 模块 2-12: Web端CRUD模块

| 模块 | 测试文件 | 测试用例数 |
|------|----------|-----------|
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

### 模块 13: 自定义字段系统 (可扩展性)

#### 13.1 数据模型
```python
# app/models/custom_field.py
class CustomFieldDefinition(Base):
    """自定义字段定义"""
    id: int
    category_id: int
    field_name: str       # snake_case
    field_label: str       # 中文显示名
    field_type: str        # text/number/date/select/multi_select
    options: str           # JSON数组，下拉选项
    required: bool
    default_value: str
    sort_order: int

class WorkflowFieldConfig(Base):
    """工作流字段配置"""
    id: int
    workflow_type: str     # assign/transfer/check/repair/scrap/alert
    field_name: str
    field_label: str
    field_type: str
    required: bool
    show_in_list: bool
    editable_by_user: bool
```

#### 13.2 API 设计
```
GET  /api/custom-fields/category/{category_id}     # 获取分类字段定义
POST /api/custom-fields/category/{category_id}      # 创建字段定义
PUT  /api/custom-fields/{field_id}                  # 更新字段定义
DELETE /api/custom-fields/{field_id}                 # 删除字段定义

GET  /api/workflow-fields/{workflow_type}            # 获取工作流字段配置
PUT  /api/workflow-fields/{workflow_type}            # 更新工作流字段配置
```

#### 13.3 前端实现
```
frontend/src/
├── components/
│   ├── DynamicForm.vue           # 动态表单组件
│   ├── FieldRenderer.vue         # 根据field_type渲染字段
│   └── fields/
│       ├── TextField.vue
│       ├── NumberField.vue
│       ├── DateField.vue
│       └── SelectField.vue
```

#### 13.4 测试用例
```python
# tests/test_custom_fields.py
TEST-CF-001: test_create_field_definition
TEST-CF-002: test_get_fields_by_category
TEST-CF-003: test_dynamic_form_validation
TEST-CF-004: test_workflow_field_config
```

---

### 模块 14: 操作日志中间件

#### 14.1 实现
```python
# app/middleware/operation_logging.py
class OperationLoggingMiddleware:
    async def dispatch(request, call_next):
        # 记录 operation 到 OperationLog 表
        # 排除 GET 请求和 /logs 路径
        response = await call_next(request)
        return response
```

#### 14.2 测试用例
```python
# tests/test_operation_logs.py
TEST-LOG-001: test_asset_crud_logged
TEST-LOG-002: test_asset_assign_logged
TEST-LOG-003: test_query_operation_logs
```

---

### 模块 15: 微信小程序

#### 15.1 项目结构
```
wechat-miniapp/
├── src/
│   ├── pages/
│   │   ├── index/           # 首页/扫码入口
│   │   ├── scan/            # 扫码结果页
│   │   ├── asset/           # 资产详情
│   │   ├── check/           # 盘点页
│   │   ├── profile/         # 个人中心
│   │   └── login/           # 登录页
│   ├── api/
│   │   ├── auth.ts
│   │   ├── asset.ts
│   │   └── check.ts
│   └── utils/
│       └── request.ts       # 请求封装
├── project.config.json
└── package.json
```

#### 15.2 核心流程
```
1. 微信登录: wx.login() -> code -> /api/auth/wechat
2. 获取token: 后端验证code，返回JWT
3. 扫码: wx.scanCode() -> 解析asset_no -> /api/assets/no/{asset_no}
4. 盘点: PUT /api/inventory-check/{id}/items/{itemId}
```

#### 15.3 测试用例
```javascript
TEST-MINI-001: test_scan_and_view_asset
TEST-MINI-002: test_scan_check_asset
TEST-MINI-003: test_update_asset_info
```

---

### 模块 16: 移动端 H5

#### 16.1 路由设计
```
frontend/src/router/index.js
/mobile                # 移动端首页
/mobile/scan           # 扫码页
/mobile/asset/:id      # 资产详情
/mobile/check/:id      # 盘点页
/mobile/login          # 登录页
```

#### 16.2 扫码方案
```javascript
// 方案1: html5-qrcode (通用浏览器)
import { Html5Qrcode } from 'html5-qrcode'
const scanner = new Html5Qrcode('qr-reader')
await scanner.start({ facingMode: 'environment' }, onSuccess, onError)

// 方案2: 微信环境使用JSSDK
wx.scanQRCode({ needResult: 1, scanType: ['qrCode'] })
```

---

### 模块 17: 二维码批量生成与打印

#### 17.1 前端页面
```
frontend/src/views/qrcode/
├── QrcodeGenerator.vue     # 选择资产 + 设置样式
├── QrcodePreview.vue        # 预览 + 打印
└── components/
    └── QrcodeItem.vue       # 单个二维码
```

#### 17.2 功能清单
- 按分类/部门选择资产
- 设置二维码尺寸 (2cm/3cm/4cm)
- 设置每页数量 (6/9/12/16)
- 预览排版效果
- 导出 PDF / 打印

---

### 模块 18: 草料二维码 API 集成

#### 18.1 后端实现
```
backend/app/
├── utils/
│   └── cai_liao_client.py   # 草料API客户端
├── api/
│   ├── qrcode_bindings.py    # 绑定管理
│   └── cai_liao_sync.py      # 数据同步
└── models/
    └── qrcode.py             # QrcodeBinding model
```

#### 18.2 数据模型
```python
class QrcodeBinding(Base):
    asset_id: int
    cai_liao_link_id: str
    cai_liao_url: str
    qrcode_url: str
    scan_count: int
    last_scan_at: datetime
```

---

## 六，开发迭代节奏

### Sprint 1: 测试基础设施
- pytest 框架搭建
- 认证模块测试

### Sprint 2-3: Web端CRUD测试
- Phase 2-4 所有模块测试
- 覆盖率目标 80%

### Sprint 4: 可扩展性增强
- 自定义字段系统
- 工作流字段配置
- 操作日志中间件

### Sprint 5: 移动端 H5
- mobile 路由
- 响应式布局
- 扫码功能

### Sprint 6: 微信小程序
- Taro 项目
- 登录授权
- 扫码/盘点

### Sprint 7: 二维码管理
- 批量生成
- PDF导出
- 草料API

---

## 七、关键文件清单

### 后端新增
| 文件 | 说明 |
|------|------|
| `app/models/custom_field.py` | 自定义字段模型 |
| `app/models/workflow_field.py` | 工作流字段配置 |
| `app/models/qrcode.py` | 二维码绑定模型 |
| `app/api/custom_fields.py` | 自定义字段API |
| `app/api/workflow_fields.py` | 工作流字段API |
| `app/api/qrcode_bindings.py` | 二维码绑定API |
| `app/api/cai_liao.py` | 草料API |
| `app/utils/cai_liao_client.py` | 草料客户端 |
| `app/middleware/logging.py` | 操作日志中间件 |

### 前端新增
| 文件 | 说明 |
|------|------|
| `src/views/mobile/*` | 移动端页面 |
| `src/views/qrcode/*` | 二维码管理页面 |
| `src/components/DynamicForm.vue` | 动态表单组件 |
| `src/components/fields/*` | 各类字段组件 |

### 微信小程序
| 文件 | 说明 |
|------|------|
| `wechat-miniapp/` | Taro 项目目录 |

### 配置文件
| 文件 | 说明 |
|------|------|
| `.env.development` | 本地开发配置 |
| `.env.lan` | 局域网测试配置 |
| `.env.production` | 云端生产配置 |
| `start.sh` | 多环境启动脚本 |

---

## 八、验证方法

### 本地验证
```bash
# 启动本地开发
./start.sh development

# 启动局域网测试
./start.sh lan

# 运行测试
cd backend && source venv/bin/activate
pytest tests/ -v --cov=app

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

### 局域网测试验证
```bash
# 1. 获取本机IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# 2. 启动服务
./start.sh lan

# 3. 手机访问
http://<your-ip>:8765

# 4. 二维码扫码测试
# 确保二维码内容为 http://<your-ip>:8765/api/assets/scan/{asset_no}
```

### 云端部署验证
```bash
# 使用 Nginx 反向代理
# 确保 CORS 配置包含你的域名
```
