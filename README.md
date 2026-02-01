# 轻量电商 API 示例（FastAPI + 内存数据库）

一个基于 FastAPI 的轻量级电商 API 示例，提供用户与产品的完整 CRUD 能力，支持内存字典数据库模拟存储，并保留 JSON 持久化示例。适合快速原型和教学演示。

## 功能概览

- ✅ **用户管理（User）**：创建 / 查询列表 / 查询详情 / 更新 / 删除
- ✅ **产品管理（Product）**：创建 / 查询列表 / 查询详情 / 更新 / 删除 / 获取可用产品
- ✅ **订单示例**：订单创建、订单查询（依赖内存产品/用户数据）
- ✅ **内存数据库**：`InMemoryDatabase` 使用 Python 字典存储 User 和 Product，自增 ID，支持更新/删除
- ✅ **JSON 数据库示例**：`Database` 类保留 JSON 持久化演示
- ✅ **自动文档**：Swagger UI / ReDoc

**架构说明**：用户与产品的主存储为 `InMemoryDatabase`（内存字典），创建/更新/删除时会同步到 `DataStore`（内存对象列表），供订单创建与查询使用；订单数据同时写入 JSON 数据库 `Database` 做持久化演示。

## 目录结构

```
├── src/
│   ├── main.py          # FastAPI 入口，User/Product CRUD API
│   ├── database.py      # JSON 数据库模拟 & 内存字典数据库 InMemoryDatabase
│   ├── models.py        # Pydantic 数据模型 + dataclass 原始模型
│   └── __init__.py
├── tests/
│   ├── test_main.py     # 示例单元测试
│   └── __init__.py
├── requirements.txt     # 依赖列表（FastAPI / Uvicorn / Pydantic 等）
├── setup.py
├── README.md
└── .gitignore
```

## 环境要求

- Python 3.8+
- 建议使用虚拟环境：`python -m venv venv && source venv/bin/activate`（Windows 使用 `venv\Scripts\activate`）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
# 开发模式运行（包含自动重载）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要 API（摘要）

### 通用
- `GET /` 根路由（欢迎信息与版本）
- `GET /health` 健康检查

### 用户 User（基于内存数据库）
- `POST /users` 创建用户
- `GET /users` 获取用户列表
- `GET /users/{user_id}` 获取用户详情
- `PUT /users/{user_id}` 更新用户
- `DELETE /users/{user_id}` 删除用户

### 产品 Product（基于内存数据库）
- `POST /products` 创建产品（名称唯一校验）
- `GET /products` 获取产品列表
- `GET /products/available` 获取可用产品
- `GET /products/{product_id}` 获取产品详情
- `PUT /products/{product_id}` 更新产品（支持库存/可用状态联动）
- `DELETE /products/{product_id}` 删除产品

### 订单示例
- `POST /orders` 创建订单（依赖当前内存用户与产品，用户/产品在创建时会同步到订单用 DataStore）
- `GET /orders` 获取订单列表

### 数据库信息
- `GET /database/info` 获取 JSON 数据库信息（表名、表结构、数据文件路径）

## 数据模型亮点

- Pydantic 模型：User / Product / Order 及扩展的 Category、Review、Inventory、Supplier、OrderDetail 等示例模型
- Email、长度、范围、必填/可选等多重校验
- dataclass 原始模型与 Pydantic 转换示例

## 测试

```bash
python -m pytest tests/
```

> 当前仅含基础示例测试；主应用通过 `uvicorn src.main:app` 启动，可按需使用 `fastapi.testclient.TestClient` 补充接口测试。

## 下一步可拓展方向

- 引入真实数据库（PostgreSQL/MySQL/SQLite）并替换内存存储
- 增加鉴权与用户登录态
- 为更多业务模型补充实际 API（Category / Review / Inventory / Supplier / OrderDetail）
- 编写更完善的单元测试与集成测试

## 许可证

MIT License