# AMS - Asset Management System 资产管理系统

公司内部资产管理解决方案，支持资产全生命周期管理。

## 项目结构

```
AMS/
├── backend/              # 后端服务 (Python FastAPI)
├── frontend/            # PC端管理后台 (Vue 3)
├── mobile/              # 移动端小程序
└── docs/                # 项目文档
```

## 功能模块

### 1. 资产管理
- [x] 资产分类管理（固定资产/易耗品）
- [x] 资产登记与入库
- [x] 资产照片上传
- [x] 二维码生成与打印
- [x] 资产详情查看

### 2. 资产流转
- [x] 员工信息库管理
- [x] 资产领用与分配
- [x] 资产调拨
- [x] 资产退库

### 3. 盘点管理
- [x] 扫码盘点
- [x] 盘点报告生成
- [x] 盘盈盘亏统计

### 4. 维修与报废
- [x] 报修工单管理
- [x] 报废审批流程

### 5. 系统功能
- [x] 用户权限管理 (RBAC)
- [x] 操作日志审计
- [x] 数据导入导出

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + Pydantic
- **前端**: Vue 3 + Element Plus + Vite
- **数据库**: SQLite (开发) / MySQL (生产)
- **二维码**: qrcode + 草料二维码API
