# AMS 前后端匹配测试 - 问题跟踪表

## 测试执行记录

| 测试日期 | 测试模块 | 测试用例数 | 通过 | 失败 | 跳过 |
|----------|----------|------------|------|------|------|
| 2026-04-12 | 登录模块 | 7 | 7 | 0 | 0 |
| 2026-04-12 | Dashboard | 7 | 6 | 0 | 1 |
| 2026-04-12 | 移动端H5 | 8 | 8 | 0 | 0 |
| 2026-04-12 | API集成 | 10 | 10 | 0 | 0 |
| 2026-04-12 | 资产列表 | 10 | 10 | 0 | 0 |
| 2026-04-12 | 分类管理 | 9 | 9 | 0 | 0 |
| 2026-04-12 | 部门管理 | 9 | 9 | 0 | 0 |
| 2026-04-12 | 员工管理 | 9 | 9 | 0 | 0 |
| 2026-04-12 | 报修管理 | 9 | 9 | 0 | 0 |
| 2026-04-12 | 报废管理 | 9 | 9 | 0 | 0 |
| 2026-04-12 | 易耗品管理 | 8 | 8 | 0 | 0 |
| 2026-04-12 | 盘点管理 | 9 | 9 | 0 | 0 |
| 2026-04-12 | 用户管理 | 8 | 8 | 0 | 0 |
| 2026-04-12 | 角色管理 | 7 | 7 | 0 | 0 |
| 2026-04-12 | 日志管理 | 7 | 7 | 0 | 0 |
| 2026-04-12 | 二维码管理 | 7 | 7 | 0 | 0 |
| **总计** | **16个模块** | **140** | **139** | **0** | **1** |

---

## 2026-04-13 测试/Debug 记录

### 问题1: IP变更后二维码URL不一致

**问题描述**：IP变更后，二维码指向错误的地址

**原因**：
1. 后端 `generate_qr_code` 硬编码了 `https://ams.example.com`
2. 前端 `vite.config.js` 代理IP未同步更新
3. 多个文件存在旧IP硬编码

**修复**：
- 后端添加 `FRONTEND_URL` 配置项 (`backend/app/core/config.py`)
- 二维码生成使用 `settings.FRONTEND_URL` (`backend/app/api/assets.py`)
- 前端代理统一配置 (`frontend/vite.config.js`)
- 创建二维码更新脚本 (`backend/scripts/update_qr_codes.py`)

**配置文件**（IP变更时只需修改这2处）：
| 文件 | 配置项 |
|------|--------|
| `frontend/vite.config.js` | `BACKEND_IP` |
| `backend/.env` | `FRONTEND_URL`, `BASE_URL` |

---

### 问题2: 移动端资产详情照片/附件不显示

**问题描述**：移动端详情页无法显示照片和附件

**原因**：
1. Web端 `AssetResponse` schema 中 `images` 定义为 `str`，前端需要 `JSON.parse()`
2. 移动端直接使用相对路径，缺少完整URL处理
3. 移动端详情页缺少附件显示功能

**修复**：
- 后端 schema 添加 validator 自动解析 JSON 字段 (`backend/app/schemas/asset.py`)
- 移动端详情页引入 `getImageUrl()` 处理图片URL (`frontend/src/views/mobile/AssetDetail.vue`)
- 添加附件列表显示功能 (`frontend/src/views/mobile/AssetDetail.vue`)

---

### 问题3: 微信扫码跳转到登录页

**问题描述**：未登录用户扫码后被强制跳转到登录页，无法查看资产概要

**原因**：
1. 路由守卫强制所有移动端页面需要认证
2. `GET /{asset_id}/attachments` API 需要认证，导致 401

**修复**：
- 路由守卫添加公开页面白名单 (`frontend/src/router/index.js`)
- 附件列表API改为公开接口 (`backend/app/api/assets.py`)

**公开页面列表**：
- `/mobile/assets/:id` - 资产详情（无需登录）

---

### 问题4: Web端资产详情页加载失败

**问题描述**：Web端资产详情页显示"加载数据失败"

**原因**：代码对已解析的 `images` 字段再次 `JSON.parse()`

**修复**：
- 移除重复解析，直接使用数组 (`frontend/src/views/assets/AssetDetail.vue`)

---

### 问题5: 二维码管理页面资产列表为空

**问题描述**：二维码管理页面无法加载资产列表

**原因**：使用原生 `fetch` 而非封装 API，未携带认证 token

**修复**：
- 改用 `assetApi.list()` 替代原生 fetch

---

### 问题6: 二维码URL与资产详情不一致

**问题描述**：批量生成的二维码与资产详情页URL不一致

**原因**：二维码生成使用 `/mobile/scan?no=xxx`，应为 `/mobile/assets/{id}`

**修复**：
- 统一使用 `/mobile/assets/{id}` 格式

---

## 问题跟踪表

### P0: 资产模块 (Assets)

| 问题ID | 用例ID | 问题描述 | 类型 | 严重度 | 状态 | 修复建议 |
|--------|--------|----------|------|--------|------|----------|
| ASSET-BUG-001 | - | 资产新建表单验证正常工作 | - | - | 已通过 | - |
| ASSET-BUG-002 | - | 资产详情页面跳转正常 | - | - | 已通过 | - |
| ASSET-BUG-003 | - | 资产编辑页面加载正常 | - | - | 已通过 | - |
| ASSET-BUG-004 | - | images字段返回数组格式 | 后端 | 高 | ✅已修复 | - |
| ASSET-BUG-005 | - | 移动端照片/附件显示 | 前端 | 高 | ✅已修复 | - |
| ASSET-BUG-006 | - | 二维码URL统一格式 | 前端 | 中 | ✅已修复 | - |

### P1: 分类/部门/员工/报修/报废

| 模块 | 问题描述 | 状态 |
|------|----------|------|
| 分类管理 | 全部9个测试通过 | ✅ |
| 部门管理 | 全部9个测试通过 | ✅ |
| 员工管理 | 全部9个测试通过 | ✅ |
| 报修管理 | 全部9个测试通过 | ✅ |
| 报废管理 | 全部9个测试通过 | ✅ |

### P2: 其他模块

| 模块 | 问题描述 | 状态 |
|------|----------|------|
| 易耗品管理 | 全部8个测试通过 | ✅ |
| 盘点管理 | 全部9个测试通过 | ✅ |
| 用户管理 | 全部8个测试通过 | ✅ |
| 角色管理 | 全部7个测试通过 | ✅ |
| 日志管理 | 全部7个测试通过 | ✅ |
| 二维码管理 | 全部7个测试通过 | ✅ |

### P3: 移动端 (Mobile)

| 问题ID | 问题描述 | 状态 |
|--------|----------|------|
| MOBILE-001 | 微信扫码跳转登录页 | ✅已修复 |
| MOBILE-002 | 资产照片不显示 | ✅已修复 |
| MOBILE-003 | 附件列表不显示 | ✅已修复 |
| MOBILE-004 | 二维码URL不一致 | ✅已修复 |

---

## 已知问题汇总

### 高优先级 (影响核心功能)

1. ~~**categories/departments返回格式不一致**~~ ✅ 已解决
   - ~~前端正使用getTree() API，list()未被使用，功能正常~~

2. ~~**images/attachments字段需要JSON解析**~~ ✅ 已解决
   - ~~前端已有兼容处理（AssetDetail.vue第407行）~~

### 中优先级 (影响用户体验)

3. ~~**报修指派参数传递方式**~~ ✅ 已解决
   - ~~修复: 添加body参数支持，同时兼容query参数~~
   - ~~后端: repair.py - 添加 RepairOrderAssign schema~~
   - ~~前端: modules.js - 使用 { handler_id } body格式~~

4. ~~**盘点明细更新路径**~~ ✅ 已解决
   - ~~修复: 添加扁平化路径 PUT /inventory-check/items/{item_id}~~
   - ~~后端: inventory_check.py - 添加扁平路径~~
   - ~~前端: modules.js - 使用新路径~~

---

## 测试覆盖率

| 模块 | 测试文件 | 测试用例数 | 覆盖率 |
|------|----------|------------|--------|
| 登录 | login.spec.ts | 7 | 100% |
| Dashboard | dashboard.spec.ts | 7 | 85% |
| 资产 | assets.spec.ts | 10 | 70% |
| 移动端 | mobile.spec.ts | 8 | 100% |
| API集成 | api.spec.ts | 10 | 60% |
| 分类 | categories.spec.ts | 9 | 80% |
| 部门 | departments.spec.ts | 9 | 80% |
| 员工 | employees.spec.ts | 9 | 80% |
| 报修 | repair.spec.ts | 9 | 80% |
| 报废 | scrap.spec.ts | 9 | 80% |
| 易耗品 | consumables.spec.ts | 8 | 75% |
| 盘点 | inventory-check.spec.ts | 9 | 80% |
| 用户 | users.spec.ts | 8 | 80% |
| 角色 | roles.spec.ts | 7 | 70% |
| 日志 | logs.spec.ts | 7 | 70% |
| 二维码 | qrcode.spec.ts | 7 | 50% |

**总体覆盖率**: 约 78%
**总计测试用例**: 140个
**测试通过率**: 99.3% (139/140)

---

## ✅ 所有问题已解决

### 修复清单

1. **报修指派API** (`backend/app/api/repair.py`)
   - 添加 `RepairOrderAssign` schema
   - 支持 body 和 query 参数

2. **盘点明细更新API** (`backend/app/api/inventory_check.py`)
   - 添加扁平化路径 `PUT /inventory-check/items/{item_id}`

3. **前端API调用** (`frontend/src/api/modules.js`)
   - `repair.assign()` 使用 body 参数
   - `inventoryCheck.updateItem()` 使用扁平路径

4. **批量导入/导出功能** (`frontend/src/views/assets/AssetList.vue`)
   - 添加"下载模板"按钮 - 调用 `GET /api/assets/import/template`
   - 添加"导入"按钮 - 弹窗上传Excel文件
   - 添加"导出"按钮 - 调用 `GET /api/assets/export` 下载Excel
   - 后端导出API改为 GET 方法以支持URL直接下载

---

## 测试命令

```bash
# 运行所有测试
npm test

# 运行单个模块测试
npm test tests/pages/assets.spec.ts
npm test tests/pages/repair.spec.ts
npm test tests/pages/inventory-check.spec.ts

# UI模式调试
npm run test:ui

# 查看测试报告
npm run test:report
```
