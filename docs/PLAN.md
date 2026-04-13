# AMS 资产管理系统 - 开发规划

> 本文件为项目开发遵循的主要规划文档
> 详细规划请参考 `docs/PLAN_DETAIL.md`

## 快速索引

| 模块 | Sprint | 状态 | 详细章节 |
|------|--------|------|----------|
| 测试基础设施 | Sprint 1 | ✅ 已完成 | Phase 1 |
| Web端CRUD测试 | Sprint 2-3 | ✅ 已完成 | Phase 2-4 |
| 资产照片功能 | Sprint 4 | ✅ 已完成 | Phase 3.4 |
| 资产附件功能 | Sprint 4 | ✅ 已完成 | Phase 3.5 |
| 房地产资产 | Sprint 4 | ✅ 已完成 | Phase 3.6 |
| 操作日志中间件 | Sprint 5.3 | ✅ 已完成 | Phase 5.3 |
| 批量导入 | Sprint 5.4 | ✅ 已完成 | Phase 5.4 |
| 批量导出 | Sprint 5.5 | ✅ 已完成 | Phase 5.5 |
| 自定义字段系统 | Sprint 5.1 | ✅ 已完成 | Phase 5.1 |
| 工作流字段配置 | Sprint 5.2 | ✅ 已完成 | Phase 5.2 |
| **Phase 6.1** | **移动端 H5** | ✅ 已完成 | Phase 6.1 |
| **Phase 6.2** | **微信小程序 (Taro)** | ✅ 已完成 | Phase 6.2 |
| **Phase 7** | **二维码管理** | ✅ 已完成 | Phase 7 |
| **Phase 8** | **前端 E2E 测试** | ✅ 已完成 | Phase 8 |
| **Phase 9** | **微信扫码公开查看** | ✅ 已完成 | Phase 9 |

## 当前项目状态

### 已完成 (~92%)
- Web端全部CRUD功能
- 基础认证与权限
- 资产流转（分配/调拨/退库）
- 报修/报废/盘点流程
- 资产照片上传/展示/删除
- 资产附件（PDF/文档）上传/展示/下载/删除
- 房地产资产管理（含12个专用字段）
- 操作日志中间件
- 批量导入/导出功能
- 自定义字段系统
- 工作流字段配置
- 测试体系后端（164个测试用例，覆盖15个模块）
- 测试体系前端（35个测试用例，覆盖4个模块）

### 待开发 (~8%)
- 移动端 H5/小程序
- 二维码管理
- 工作流字段配置
- 操作日志
- 批量导入/导出
- 移动端H5/微信小程序
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

## Phase 3: 资产功能增强

### Phase 3.4: 资产照片功能
- AssetForm.vue 添加图片上传组件
- AssetList.vue 添加缩略图
- AssetUpdate schema 支持 images

### Phase 3.5: 资产附件功能 (PDF/文档)
- Asset.attachments 字段
- PDF/Word/Excel 上传下载
- 房产证等文档管理

### Phase 3.6: 房地产资产管理
- AssetType.REAL_ESTATE 类型
- 房产专用字段（地址/面积/产权证号）
- 房地产统计报表

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

## Phase 8: 前端 E2E 测试

### Playwright 测试框架

**技术栈**: Playwright + TypeScript + Vite

**测试文件结构**:
```
frontend/tests/
├── pages/
│   ├── login.spec.ts      # 登录页面测试
│   ├── dashboard.spec.ts  # 首页测试
│   └── mobile.spec.ts     # 移动端测试
├── api/
│   └── api.spec.ts        # API 集成测试
├── helpers.ts             # 测试工具函数
└── playwright.config.ts   # Playwright 配置
```

**测试命令**:
```bash
cd frontend
npm test           # 运行所有测试
npm run test:ui    # UI 模式
npm run test:api   # API 测试
npm run test:mobile # 移动端测试
```

**测试用例统计**:

| 测试文件 | 用例数 | 描述 |
|----------|--------|------|
| api.spec.ts | 11 | 健康检查/认证/CRUD API |
| login.spec.ts | 8 | 登录/注册/表单验证 |
| dashboard.spec.ts | 7 | 首页加载/导航/退出 |
| mobile.spec.ts | 9 | 移动端 H5 响应式测试 |
| **合计** | **35** | 前端 E2E 测试 |

### 测试原则

1. **测试分层**: API 集成测试 → 页面级 E2E 测试
2. **认证处理**: API 用 JWT Token，页面用 login() 辅助函数
3. **移动端适配**: viewport 375x667，响应式布局验证
4. **测试隔离**: 每个测试独立，可并行执行

---

## Phase 9: 微信扫码公开查看

### 需求说明

微信扫描资产二维码后，直接跳转到资产详情页面：
- **无权限用户**：查看资产基础信息（只读）
- **已登录用户**：查看详情 + 扫码盘点/报修等操作
- **连续扫码**：保持登录状态

### 技术方案

#### 后端 API

**公开详情接口**（无需认证）：
```
GET /api/assets/public/{asset_id}
```

**配置项** (`backend/.env`)：
```bash
FRONTEND_URL="https://10.0.0.113:5173"  # 前端地址
BASE_URL="https://10.0.0.113:8000"        # 后端地址
```

**路由顺序**（重要）：
```
/no/{asset_no}     # 特定路径优先
/public/{asset_id}  # 公开接口在通用路径前
/{asset_id}         # 需认证接口放最后
```

#### 前端页面

**移动端详情页** (`frontend/src/views/mobile/AssetDetail.vue`)：
- 使用 `getPublic()` API 获取数据
- 检测登录状态 `isLoggedIn = !!userStore.token`
- 未登录：显示基础信息 + 登录入口
- 已登录：显示完整信息 + 操作按钮

**扫码页面** (`frontend/src/views/mobile/Scan.vue`)：
- 支持完整URL解析：`https://domain/mobile/assets/{id}`
- 支持相对路径解析：`/mobile/assets/{id}`
- 支持JSON格式：`{"type":"asset","id":1}`

#### 二维码生成

**生成规则** (`backend/app/api/assets.py`)：
```python
def generate_qr_code(asset_no: str, asset_id: int) -> str:
    frontend_url = settings.FRONTEND_URL.rstrip('/')
    return f"{frontend_url}/mobile/assets/{asset_id}"
```

#### IP 配置管理

**⚠️ IP变更必须同步更新二维码（仅测试阶段）**

**说明**：开发测试阶段IP可能变化，生产环境使用固定域名，二维码URL保持稳定。

**测试阶段 IP配置点（网络变更时只需修改这2处）**：

| 文件 | 配置项 | 说明 |
|------|--------|------|
| `frontend/vite.config.js` | `BACKEND_IP = '10.0.0.113'` | 前端代理 |
| `backend/.env` | `FRONTEND_URL`, `BASE_URL` | 后端配置 |

**生产环境**：
- 使用固定域名（如 `ams.company.com`）
- `FRONTEND_URL` 和 `BASE_URL` 指向同一域名
- 二维码URL长期有效，无需频繁更新

**IP变更后必须执行的操作**：

1. 更新 `frontend/vite.config.js` 中的 `BACKEND_IP`
2. 更新 `backend/.env` 中的 `FRONTEND_URL` 和 `BASE_URL`
3. **重新生成所有资产的二维码**：
```bash
cd backend
source venv/bin/activate
python -c "
from app.models.asset import Asset
from app.core.database import SessionLocal
from app.core.config import settings
db = SessionLocal()
assets = db.query(Asset).all()
for asset in assets:
    asset.qr_code = f'{settings.FRONTEND_URL.rstrip(\"/\")}/mobile/assets/{asset.id}'
db.commit()
db.close()
print(f'已更新 {len(assets)} 个资产的二维码')
"
```

**自动化建议**：
- 将二维码更新脚本集成到项目启动脚本 `start.sh` 中
- 或创建独立脚本 `scripts/update-qr-codes.sh`

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

---

## 开发流程与版本管理

> ⚠️ **重要原则：测试先行，模块完成后及时提交 Git**

### 测试优先开发策略

每个模块的开发遵循以下流程：

```
1. 需求分析 → 更新 PLAN_DETAIL.md
2. 编写测试 → 在 tests/ 下编写测试用例
3. 开发实现 → 实现功能代码
4. 测试验证 → pytest 全部通过
5. Git 提交 → 及时提交版本，记录完成状态
```

**为什么测试先行？**
- 测试即文档 — 用例编号和描述明确了功能范围
- 回归保护 — 新改动不会破坏已有功能
- 增量验证 — 每个模块完成后立即确认可用
- 进度可见 — 测试通过数直接反映完成度

### Git 提交规范

每次模块测试完成后，在 commit 前确认：

```bash
# 1. 确认所有测试通过
cd backend && source venv/bin/activate && pytest tests/ -v

# 2. 提交变更
git add <changed files>
git commit -m "feat: <模块名称> - <功能摘要>"
git push  # 立即推送到远程
```

**提交信息格式：**
```
feat: <模块名称> - <功能摘要>

## 具体内容
- 改动1
- 改动2

测试用例: X 个，总计 Y 个
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**已验证的提交节点：**

| Commit | 描述 | 测试数 |
|--------|------|--------|
| `05a7cea` | 测试基础设施 + 认证模块 | 11 |
| `8887471` | Phase 2-3 CRUD 模块测试 | 86 |
| `09aa4b2` | Phase 3 照片/附件/房地产 + 测试补全 | 119 |
| `c6c5fcb` | Sprint 5.3 操作日志中间件 | - |
| `2061cd3` | Sprint 5.4 批量导入功能 | +7 |
| `25f0bae` | Sprint 5.5 批量导出功能 | +7 |
| `60cd002` | Phase 5.1 自定义字段系统 | +12 |
| `0db59ab` | Phase 5.2 工作流字段配置 | +13 |

### 测试统计

| 模块 | 测试文件 | 用例数 | 状态 |
|------|----------|--------|------|
| 认证 | test_auth.py | 11 | ✅ |
| 用户管理 | test_users.py | 12 | ✅ |
| 角色权限 | test_roles.py | 11 | ✅ |
| 部门管理 | test_departments.py | 15 | ✅ |
| 员工管理 | test_employees.py | 15 | ✅ |
| 分类管理 | test_categories.py | 15 | ✅ |
| 资产管理 | test_assets.py | 18 | ✅ |
| 易耗品 | test_consumables.py | 8 | ✅ |
| 报修管理 | test_repair.py | 4 | ✅ |
| 报废管理 | test_scrap.py | 4 | ✅ |
| 盘点管理 | test_inventory_check.py | 5 | ✅ |
| 操作日志 | test_operation_logs.py | 3 | ✅ |
| 批量导入 | test_batch_import.py | 7 | ✅ |
| 批量导出 | test_batch_export.py | 7 | ✅ |
| 自定义字段 | test_custom_fields.py | 12 | ✅ |
| 工作流字段 | test_workflow_fields.py | 13 | ✅ |
| **合计** | **15个测试文件** | **164** | ✅ |

### 新模块开发 Checklist

每个新模块开发前，确认以下清单：

- [ ] 分析需求，更新 docs/PLAN_DETAIL.md 用例
- [ ] 创建后端测试文件 `backend/tests/test_<module>.py`
- [ ] 编写后端测试用例（pytest）
- [ ] 实现后端 API 和数据模型
- [ ] `pytest backend/tests/test_<module>.py -v` 全部通过
- [ ] 实现前端页面和组件
- [ ] 创建前端测试文件 `frontend/tests/pages/<module>.spec.ts`
- [ ] 编写前端 E2E 测试用例（Playwright）
- [ ] `npm test` 全部通过
- [ ] 更新 docs/PLAN.md 模块状态为 ✅
- [ ] `git add` + `git commit` + `git push`
