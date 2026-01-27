"""FastAPI主应用模块"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import uvicorn

# 导入项目模块
from models import User, Product, Order, DataStore
from database import Database, DatabaseManager, InMemoryDatabase


# 创建FastAPI应用实例
app = FastAPI(
    title="Python项目API",
    description="一个基于FastAPI的Python项目示例",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 全局数据存储
data_store = DataStore()
db_manager = DatabaseManager()
app_db = db_manager.get_database("app_db")
in_memory_db = InMemoryDatabase()


# Pydantic模型定义
class UserCreate(BaseModel):
    """用户创建模型"""
    username: str
    email: EmailStr
    is_active: bool = True


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: str


class ProductCreate(BaseModel):
    """产品创建模型"""
    name: str
    price: float
    description: Optional[str] = None
    stock: int = 0
    is_available: bool = True


class ProductUpdate(BaseModel):
    """产品更新模型"""
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    stock: Optional[int] = None
    is_available: Optional[bool] = None


class ProductResponse(BaseModel):
    """产品响应模型"""
    id: int
    name: str
    price: float
    description: Optional[str]
    stock: int
    is_available: bool


class OrderCreate(BaseModel):
    """订单创建模型"""
    user_id: int
    product_ids: List[int]


class OrderResponse(BaseModel):
    """订单响应模型"""
    id: int
    user_id: int
    products: List[ProductResponse]
    total_amount: float
    status: str
    created_at: str


# 根路由
@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "欢迎使用Python项目API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# 用户相关API（使用 InMemoryDatabase 实现 CRUD）
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """创建新用户"""
    # 检查用户名或邮箱是否已存在
    for u in in_memory_db.list_users():
        if u["username"] == user.username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
        if u["email"] == user.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已存在")
    
    created_at = datetime.now().isoformat()
    user_id = in_memory_db.create_user({
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": created_at
    })
    record = in_memory_db.get_user(user_id)
    return UserResponse(
        id=record["user_id"],
        username=record["username"],
        email=record["email"],
        is_active=record["is_active"],
        created_at=record["created_at"]
    )


@app.get("/users", response_model=List[UserResponse])
async def get_users():
    """获取所有用户"""
    users = []
    for u in in_memory_db.list_users():
        users.append(UserResponse(
            id=u["user_id"],
            username=u["username"],
            email=u["email"],
            is_active=u["is_active"],
            created_at=u["created_at"]
        ))
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """获取指定用户"""
    record = in_memory_db.get_user(user_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户未找到")
    return UserResponse(
        id=record["user_id"],
        username=record["username"],
        email=record["email"],
        is_active=record["is_active"],
        created_at=record["created_at"]
    )


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, payload: UserUpdate):
    """更新指定用户"""
    record = in_memory_db.get_user(user_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户未找到")
    
    updates = {}
    if payload.username is not None:
        updates["username"] = payload.username
    if payload.email is not None:
        updates["email"] = payload.email
    if payload.is_active is not None:
        updates["is_active"] = payload.is_active
    
    # 唯一性检查（用户名/邮箱）
    for u in in_memory_db.list_users():
        if u["user_id"] == user_id:
            continue
        if "username" in updates and u["username"] == updates["username"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
        if "email" in updates and u["email"] == updates["email"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已存在")
    
    ok = in_memory_db.update_user(user_id, updates)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="更新失败")
    
    updated = in_memory_db.get_user(user_id)
    return UserResponse(
        id=updated["user_id"],
        username=updated["username"],
        email=updated["email"],
        is_active=updated["is_active"],
        created_at=updated["created_at"]
    )


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """删除指定用户"""
    record = in_memory_db.get_user(user_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户未找到")
    in_memory_db.delete_user(user_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# 产品相关API（使用 InMemoryDatabase 实现 CRUD，并同步数据到 data_store 以兼容订单逻辑）
@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    """创建新产品"""
    # 名称唯一性检查
    for p in in_memory_db.list_products():
        if p["name"] == product.name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="产品名称已存在")
    
    created_at = datetime.now().isoformat()
    is_available = product.is_available if product.is_available is not None else product.stock > 0
    product_id = in_memory_db.create_product({
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "stock": product.stock,
        "is_available": is_available,
        "created_at": created_at
    })
    record = in_memory_db.get_product(product_id)
    
    # 同步到 data_store 供订单使用
    new_product = Product(
        id=product_id,
        name=record["name"],
        price=record["price"],
        description=record.get("description") or "",
        stock=record["stock"]
    )
    data_store.add_product(new_product)
    
    return ProductResponse(
        id=record["product_id"],
        name=record["name"],
        price=record["price"],
        description=record.get("description"),
        stock=record["stock"],
        is_available=record["is_available"]
    )


@app.get("/products", response_model=List[ProductResponse])
async def get_products():
    """获取所有产品"""
    products = []
    for p in in_memory_db.list_products():
        products.append(ProductResponse(
            id=p["product_id"],
            name=p["name"],
            price=p["price"],
            description=p.get("description"),
            stock=p["stock"],
            is_available=p["is_available"]
        ))
    return products


@app.get("/products/available", response_model=List[ProductResponse])
async def get_available_products():
    """获取可用的产品"""
    products = []
    for p in in_memory_db.list_products():
        if p.get("is_available", False):
            products.append(ProductResponse(
                id=p["product_id"],
                name=p["name"],
                price=p["price"],
                description=p.get("description"),
                stock=p["stock"],
                is_available=p["is_available"]
            ))
    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """获取指定产品"""
    record = in_memory_db.get_product(product_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品未找到")
    return ProductResponse(
        id=record["product_id"],
        name=record["name"],
        price=record["price"],
        description=record.get("description"),
        stock=record["stock"],
        is_available=record["is_available"]
    )


@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, payload: ProductUpdate):
    """更新指定产品"""
    record = in_memory_db.get_product(product_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品未找到")
    
    updates: Dict[str, Any] = {}
    if payload.name is not None:
        updates["name"] = payload.name
    if payload.price is not None:
        updates["price"] = payload.price
    if payload.description is not None:
        updates["description"] = payload.description
    if payload.stock is not None:
        updates["stock"] = payload.stock
        # 如果未显式提供 is_available，则根据库存推断
        if payload.is_available is None:
            updates["is_available"] = payload.stock > 0
    if payload.is_available is not None:
        updates["is_available"] = payload.is_available
    
    # 唯一性检查：名称
    for p in in_memory_db.list_products():
        if p["product_id"] == product_id:
            continue
        if "name" in updates and p["name"] == updates["name"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="产品名称已存在")
    
    ok = in_memory_db.update_product(product_id, updates)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="更新失败")
    
    updated = in_memory_db.get_product(product_id)
    
    # 同步到 data_store
    ds_product = data_store.get_product_by_id(product_id)
    if ds_product:
        if "name" in updates:
            ds_product.name = updates["name"]
        if "price" in updates:
            ds_product.price = updates["price"]
        if "description" in updates:
            ds_product.description = updates["description"] or ""
        if "stock" in updates:
            ds_product.stock = updates["stock"]
    
    return ProductResponse(
        id=updated["product_id"],
        name=updated["name"],
        price=updated["price"],
        description=updated.get("description"),
        stock=updated["stock"],
        is_available=updated["is_available"]
    )


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int):
    """删除指定产品"""
    record = in_memory_db.get_product(product_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品未找到")
    
    in_memory_db.delete_product(product_id)
    
    # 同步删除 data_store
    ds_product = data_store.get_product_by_id(product_id)
    if ds_product:
        data_store.products = [p for p in data_store.products if p.id != product_id]
    
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# 订单相关API
@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate):
    """创建新订单"""
    # 检查用户是否存在
    user = data_store.get_user_by_id(order.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    
    # 获取产品
    products = []
    total_amount = 0.0
    
    for product_id in order.product_ids:
        product = data_store.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"产品 {product_id} 未找到"
            )
        if not product.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"产品 {product.name} 库存不足"
            )
        products.append(product)
        total_amount += product.price
    
    # 创建订单
    new_order = Order(
        id=len(data_store.orders) + 1,
        user_id=order.user_id,
        products=products,
        total_amount=total_amount
    )
    data_store.add_order(new_order)
    
    # 保存到数据库
    order_data = {
        "user_id": new_order.user_id,
        "product_ids": [p.id for p in new_order.products],
        "total_amount": new_order.total_amount,
        "status": new_order.status,
        "created_at": new_order.created_at.isoformat()
    }
    app_db.insert("orders", order_data)
    
    return OrderResponse(
        id=new_order.id,
        user_id=new_order.user_id,
        products=[ProductResponse(
            id=p.id,
            name=p.name,
            price=p.price,
            description=p.description,
            stock=p.stock,
            is_available=p.is_available
        ) for p in new_order.products],
        total_amount=new_order.total_amount,
        status=new_order.status,
        created_at=new_order.created_at.isoformat()
    )


@app.get("/orders", response_model=List[OrderResponse])
async def get_orders():
    """获取所有订单"""
    orders = []
    for order in data_store.orders:
        orders.append(OrderResponse(
            id=order.id,
            user_id=order.user_id,
            products=[ProductResponse(
                id=p.id,
                name=p.name,
                price=p.price,
                description=p.description,
                stock=p.stock,
                is_available=p.is_available
            ) for p in order.products],
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at.isoformat()
        ))
    return orders


# 数据库信息API
@app.get("/database/info")
async def get_database_info():
    """获取数据库信息"""
    tables_info = {}
    for table_name in app_db.get_all_tables():
        tables_info[table_name] = app_db.get_table_info(table_name)
    
    return {
        "database_name": app_db.db_name,
        "tables": tables_info,
        "data_file": app_db.data_file
    }


# 错误处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404错误处理"""
    return JSONResponse(
        status_code=404,
        content={"detail": "资源未找到", "path": str(request.url)}
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    """500错误处理"""
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误", "path": str(request.url)}
    )


# 主函数
if __name__ == "__main__":
    print("启动FastAPI应用...")
    print("API文档: http://localhost:8000/docs")
    print("备用文档: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )