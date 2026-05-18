# 商品管理系统

基于 Python FastAPI + Vue 3 + Element Plus + MySQL 的全栈商品管理系统。

## How to Run

### 环境要求

- Docker & Docker Compose

### 一键启动

```bash
# 1. 复制环境变量模板并按需修改（生产环境务必修改密码和 JWT_SECRET）
cp .env.example .env

# 2. 启动服务
docker-compose up --build -d
```

启动完成后访问：

- 管理后台：http://localhost:8081
- 后端 API：http://localhost:9999/docs

### 停止服务

```bash
docker-compose down
```

### 清除数据重建

```bash
docker-compose down -v
docker-compose up --build -d
```

## Services

| 服务 | 容器名 | 端口映射 | 说明 |
|------|--------|---------|------|
| MySQL 8.0 | product-mgmt-db | 3307:3306 | 数据库，utf8mb4 编码 |
| FastAPI Backend | product-mgmt-backend | 9999:9999 | Python 后端 API |
| Vue3 Frontend | product-mgmt-frontend | 8081:80 | 管理后台前端 |

## 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 超级管理员 |

## 测试

后端包含 64 个自动化测试（使用 SQLite 内存数据库，无需 MySQL），覆盖认证、分类、商品、图片上传、操作日志、健康检查、API 限流等模块，包含大量边界用例。

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 运行全部测试
cd backend
python -m pytest tests/ -v
```

## 题目内容

请帮我用python语言做一个商品管理系统

## 功能模块

- 用户登录/登出（JWT 认证，密码前端 SHA-256 + 后端 BCrypt 加盐加密）
- 商品管理（增删改查、分页、按分类/状态筛选）
- 分类管理（增删改查、排序、关联商品保护删除）
- 操作日志（自动记录商品/分类/用户/认证模块的增删改操作，按模块筛选）
- API 限流（全局 120 次/分钟，登录接口 5 次/分钟）
- 响应式布局（适配移动端，侧边栏可收起、表格自适应）
- 商品图片自动生成（Docker 启动时生成 29 张带商品名称和分类颜色标识的图片）

## 技术栈

- 后端：Python 3.11 + FastAPI + SQLAlchemy + PyMySQL + Pillow
- 前端：Vue 3 + Vite + Element Plus + Pinia + Axios
- 数据库：MySQL 8.0 (utf8mb4)
- 部署：Docker + Docker Compose + Nginx

## 项目结构

```
├── backend/                        # Python FastAPI 后端
│   ├── app/
│   │   ├── core/                   # 安全、依赖注入、异常处理、日志工具、限流
│   │   │   ├── deps.py
│   │   │   ├── exceptions.py
│   │   │   ├── log_utils.py
│   │   │   ├── rate_limit.py
│   │   │   └── security.py
│   │   ├── models/                 # SQLAlchemy ORM 模型
│   │   │   ├── category.py
│   │   │   ├── log.py
│   │   │   ├── product.py
│   │   │   └── user.py
│   │   ├── routers/                # API 路由
│   │   │   ├── auth.py
│   │   │   ├── categories.py
│   │   │   ├── logs.py
│   │   │   ├── products.py
│   │   │   └── users.py
│   │   ├── schemas/                # Pydantic 数据模型
│   │   │   ├── auth.py
│   │   │   ├── category.py
│   │   │   ├── common.py
│   │   │   ├── log.py
│   │   │   ├── product.py
│   │   │   └── user.py
│   │   ├── services/               # 业务逻辑层
│   │   │   ├── category_service.py
│   │   │   ├── product_service.py
│   │   │   └── user_service.py
│   │   ├── config.py               # 应用配置
│   │   ├── database.py             # 数据库连接
│   │   └── main.py                 # FastAPI 入口
│   ├── tests/                      # 自动化测试（pytest + SQLite）
│   │   ├── conftest.py
│   │   ├── test_helpers.py
│   │   ├── test_auth.py
│   │   ├── test_categories.py
│   │   ├── test_products.py
│   │   ├── test_upload.py
│   │   └── test_edge_cases.py
│   ├── schema.sql                  # 数据库初始化脚本（含测试数据）
│   ├── generate_images.py          # 商品图片自动生成脚本
│   ├── requirements.txt
│   ├── Dockerfile
│   └── start.sh
├── frontend-admin/                 # Vue 3 管理后台
│   ├── src/
│   │   ├── api/                    # Axios 请求封装
│   │   ├── router/                 # Vue Router 路由
│   │   ├── stores/                 # Pinia 状态管理
│   │   ├── styles/                 # 全局样式
│   │   ├── views/                  # 页面组件
│   │   ├── App.vue
│   │   └── main.js
│   ├── nginx.conf
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── docs/
│   └── project_design.md           # 设计文档
├── docker-compose.yml
├── .gitignore
└── README.md
```
