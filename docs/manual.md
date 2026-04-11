# AMS 资产管理系统

公司内部资产管理解决方案，支持资产全生命周期管理。

## 功能特性

### 资产管理
- [x] 资产分类管理（固定资产/易耗品，支持多级分类）
- [x] 资产登记与入库
- [x] 资产照片上传
- [x] 二维码生成与打印
- [x] 资产详情查看
- [x] 资产编辑与删除

### 资产流转
- [x] 员工信息库管理
- [x] 部门管理（树形结构）
- [x] 资产领用与分配
- [x] 资产调拨
- [x] 资产退库
- [x] 变动记录追踪

### 易耗品管理
- [x] 易耗品库存管理
- [x] 库存预警（低于最低库存提醒）
- [x] 易耗品领用
- [x] 库存补充

### 盘点管理
- [x] 创建盘点计划
- [x] 按分类/部门筛选资产
- [x] 扫码盘点
- [x] 盘点报告生成
- [x] 盘盈盘亏统计

### 维修与报废
- [x] 报修工单创建
- [x] 报修优先级设置
- [x] 维修人员指派
- [x] 维修完成记录
- [x] 报废申请
- [x] 报废审批流程
- [x] 处置方式记录

### 系统管理
- [x] 用户管理
- [x] 角色管理
- [x] 权限管理（RBAC）
- [x] 登录日志
- [x] 操作日志

## 技术架构

### 后端
- **框架**: Python FastAPI
- **ORM**: SQLAlchemy
- **数据验证**: Pydantic
- **认证**: JWT
- **数据库**: SQLite (开发) / MySQL (生产)

### 前端
- **框架**: Vue 3
- **UI库**: Element Plus
- **状态管理**: Pinia
- **构建工具**: Vite

### 部署
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx

## 快速开始

### 开发环境

#### 1. 克隆项目
```bash
git clone <repository-url>
cd AMS
```

#### 2. 启动后端
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -m app.init_db

# 启动服务
uvicorn main:app --reload --port 8000
```

#### 3. 启动前端
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 访问系统
打开浏览器访问 http://localhost:5173

#### 5. 初始账户
- 超级管理员: `admin` / `admin123`
- 资产管理员: `asset_admin` / `asset123`

### Docker部署

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 项目结构

```
AMS/
├── backend/                      # 后端服务
│   ├── app/
│   │   ├── api/                 # API路由
│   │   ├── core/                # 核心配置
│   │   ├── models/              # 数据模型
│   │   ├── schemas/             # Pydantic schemas
│   │   └── utils/               # 工具函数
│   ├── main.py                   # 应用入口
│   ├── requirements.txt          # Python依赖
│   └── Dockerfile
│
├── frontend/                     # 前端应用
│   ├── src/
│   │   ├── api/                 # API调用
│   │   ├── components/          # 公共组件
│   │   ├── router/              # 路由配置
│   │   ├── store/               # 状态管理
│   │   ├── views/               # 页面视图
│   │   ├── assets/              # 静态资源
│   │   └── main.js              # 入口文件
│   ├── package.json
│   └── Dockerfile
│
├── docs/                         # 项目文档
├── docker-compose.yml            # Docker编排
└── README.md                     # 项目说明
```

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 权限说明

系统内置三个角色：

| 角色 | 权限说明 |
|------|----------|
| 超级管理员 | 拥有所有权限，可管理系统所有功能 |
| 资产管理员 | 负责资产管理、盘点、维修等日常运营工作 |
| 普通员工 | 可查看资产、发起报修、报废申请 |

## 开发指南

### 添加新的API
1. 在 `app/models/` 中定义数据模型
2. 在 `app/schemas/` 中定义Pydantic Schema
3. 在 `app/api/` 中创建路由文件
4. 在 `main.py` 中注册路由

### 添加新的页面
1. 在 `src/views/` 中创建Vue组件
2. 在 `src/router/index.js` 中配置路由
3. 在 `src/api/modules.js` 中添加API调用函数

## 许可证

MIT License
