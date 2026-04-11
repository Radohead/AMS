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
| 可扩展性增强 | Sprint 5 | 待开始 | Phase 5 |

## 当前项目状态

### 已完成 (~80%)
- Web端全部CRUD功能
- 基础认证与权限
- 资产流转（分配/调拨/退库）
- 报修/报废/盘点流程
- 资产照片上传/展示/删除
- 资产附件（PDF/文档）上传/展示/下载/删除
- 房地产资产管理（含12个专用字段）
- 测试体系（119个测试用例，覆盖11个模块）

### 待开发 (~20%)
- 自定义字段系统
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
| **合计** | **11个测试文件** | **119** | ✅ |

### 新模块开发 Checklist

每个新模块开发前，确认以下清单：

- [ ] 分析需求，更新 PLAN_DETAIL.md 用例
- [ ] 创建测试文件 `tests/test_<module>.py`
- [ ] 编写测试用例（参考现有文件格式）
- [ ] 实现后端 API 和数据模型
- [ ] 实现前端页面和组件
- [ ] `pytest tests/test_<module>.py -v` 全部通过
- [ ] `pytest tests/ -v` 完整套件全部通过
- [ ] 更新 PLAN.md 模块状态为 ✅
- [ ] `git add` + `git commit` + `git push`
