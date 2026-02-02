"""FastAPI主应用模块"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
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


class OrderUpdate(BaseModel):
    """订单更新模型"""
    status: Optional[str] = None
    product_ids: Optional[List[int]] = None


class CategoryCreate(BaseModel):
    """分类创建模型"""
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    """分类更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """分类响应模型"""
    category_id: int
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    is_active: bool
    created_at: str


class ReviewCreate(BaseModel):
    """评价创建模型"""
    product_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):
    """评价更新模型"""
    rating: Optional[int] = None
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    """评价响应模型"""
    review_id: int
    product_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None
    created_at: str


class InventoryCreate(BaseModel):
    """库存创建模型"""
    product_id: int
    quantity: int
    min_stock: int = 0
    max_stock: int = 0
    location: str = "主仓库"


class InventoryUpdate(BaseModel):
    """库存更新模型"""
    quantity: Optional[int] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    location: Optional[str] = None


class InventoryResponse(BaseModel):
    """库存响应模型"""
    inventory_id: int
    product_id: int
    quantity: int
    min_stock: int
    max_stock: int
    location: str
    last_updated: str


class SupplierCreate(BaseModel):
    """供应商创建模型"""
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: str
    country: str = "中国"
    is_active: bool = True


class SupplierUpdate(BaseModel):
    """供应商更新模型"""
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(BaseModel):
    """供应商响应模型"""
    supplier_id: int
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: str
    country: str
    is_active: bool
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
    # 同步到 data_store 供订单使用
    data_store.add_user(User(
        id=user_id,
        username=record["username"],
        email=record["email"],
        created_at=datetime.fromisoformat(record["created_at"]),
        is_active=record["is_active"]
    ))
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
    
    # 同步到 data_store
    ds_user = data_store.get_user_by_id(user_id)
    if ds_user:
        if "username" in updates:
            ds_user.username = updates["username"]
        if "email" in updates:
            ds_user.email = updates["email"]
        if "is_active" in updates:
            ds_user.is_active = updates["is_active"]
    
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
    # 同步从 data_store 移除
    data_store.users = [u for u in data_store.users if u.id != user_id]
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


# 订单相关API（使用 InMemoryDatabase）
def _build_order_response(order_record: Dict[str, Any]) -> OrderResponse:
    """将订单记录转换为响应"""
    products_resp: List[ProductResponse] = []
    for pid in order_record.get("product_ids", []):
        prod = in_memory_db.get_product(pid)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"产品 {pid} 未找到")
        products_resp.append(ProductResponse(
            id=prod["product_id"],
            name=prod["name"],
            price=prod["price"],
            description=prod.get("description"),
            stock=prod["stock"],
            is_available=prod["is_available"]
        ))
    return OrderResponse(
        id=order_record["order_id"],
        user_id=order_record["user_id"],
        products=products_resp,
        total_amount=order_record.get("total_amount", 0.0),
        status=order_record.get("status", "pending"),
        created_at=order_record.get("created_at", datetime.now().isoformat())
    )


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate):
    """创建新订单"""
    # 校验用户存在
    user = in_memory_db.get_user(order.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户未找到")
    
    # 校验产品并计算金额
    total_amount = 0.0
    for pid in order.product_ids:
        prod = in_memory_db.get_product(pid)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"产品 {pid} 未找到")
        if not prod.get("is_available", False):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"产品 {prod['name']} 库存不足")
        total_amount += prod["price"]
    
    order_id = in_memory_db.create_order({
        "user_id": order.user_id,
        "product_ids": order.product_ids,
        "total_amount": total_amount,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    })
    record = in_memory_db.get_order(order_id)
    return _build_order_response(record)


@app.get("/orders", response_model=List[OrderResponse])
async def get_orders():
    """获取所有订单"""
    return [_build_order_response(o) for o in in_memory_db.list_orders()]


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    """获取指定订单"""
    record = in_memory_db.get_order(order_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单未找到")
    return _build_order_response(record)


@app.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, payload: OrderUpdate):
    """更新指定订单"""
    record = in_memory_db.get_order(order_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单未找到")
    
    updates: Dict[str, Any] = {}
    if payload.status is not None:
        updates["status"] = payload.status
    
    if payload.product_ids is not None:
        total_amount = 0.0
        for pid in payload.product_ids:
            prod = in_memory_db.get_product(pid)
            if not prod:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"产品 {pid} 未找到")
            if not prod.get("is_available", False):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"产品 {prod['name']} 库存不足")
            total_amount += prod["price"]
        updates["product_ids"] = payload.product_ids
        updates["total_amount"] = total_amount
    
    ok = in_memory_db.update_order(order_id, updates)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="更新失败")
    
    updated = in_memory_db.get_order(order_id)
    return _build_order_response(updated)


@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int):
    """删除指定订单"""
    record = in_memory_db.get_order(order_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单未找到")
    in_memory_db.delete_order(order_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# 分类相关API
@app.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate):
    """创建分类"""
    category_id = in_memory_db.create_category({
        "name": payload.name,
        "description": payload.description,
        "parent_category_id": payload.parent_category_id,
        "is_active": payload.is_active,
        "created_at": datetime.now().isoformat()
    })
    record = in_memory_db.get_category(category_id)
    return CategoryResponse(**record)


@app.get("/categories", response_model=List[CategoryResponse])
async def list_categories():
    """获取分类列表"""
    return [CategoryResponse(**c) for c in in_memory_db.list_categories()]


@app.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int):
    """获取分类详情"""
    record = in_memory_db.get_category(category_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类未找到")
    return CategoryResponse(**record)


@app.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, payload: CategoryUpdate):
    """更新分类"""
    record = in_memory_db.get_category(category_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类未找到")
    
    updates: Dict[str, Any] = {}
    for field in ["name", "description", "parent_category_id", "is_active"]:
        val = getattr(payload, field)
        if val is not None:
            updates[field] = val
    
    ok = in_memory_db.update_category(category_id, updates)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="更新失败")
    updated = in_memory_db.get_category(category_id)
    return CategoryResponse(**updated)


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int):
    """删除分类"""
    record = in_memory_db.get_category(category_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类未找到")
    in_memory_db.delete_category(category_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# 评价相关API
@app.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(payload: ReviewCreate):
    """创建评价"""
    # 校验关联
    if not in_memory_db.get_product(payload.product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品未找到")
    if not in_memory_db.get_user(payload.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户未找到")
    review_id = in_memory_db.create_review({
        "product_id": payload.product_id,
        "user_id": payload.user_id,
        "rating": payload.rating,
        "comment": payload.comment,
        "created_at": datetime.now().isoformat()
    })
    record = in_memory_db.get_review(review_id)
    return ReviewResponse(**record)


@app.get("/reviews", response_model=List[ReviewResponse])
async def list_reviews():
    """获取评价列表"""
    return [ReviewResponse(**r) for r in in_memory_db.list_reviews()]


@app.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int):
    """获取评价详情"""
    record = in_memory_db.get_review(review_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评价未找到")
    return ReviewResponse(**record)


@app.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: int, payload: ReviewUpdate):
    """更新评价"""
    record = in_memory_db.get_review(review_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评价未找到")
    
    updates: Dict[str, Any] = {}
    if payload.rating is not None:
        updates["rating"] = payload.rating
    if payload.comment is not None:
        updates["comment"] = payload.comment
    
    ok = in_memory_db.update_review(review_id, updates)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="更新失败")
    updated = in_memory_db.get_review(review_id)
    return ReviewResponse(**updated)


@app.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: int):
    """删除评价"""
    record = in_memory_db.get_review(review_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评价未找到")
    in_memory_db.delete_review(review_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# 库存相关API
@app.post("/inventories", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(payload: InventoryCreate):
    """创建库存"""
    if not in_memory_db.get_product(payload.product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品未找到")
    inventory_id = in_memory_db.create_inventory({
        "product_id": payload.product_id,
        "quantity": payload.quantity,
        "min_stock": payload.min_stock,
        "max_stock": payload.max_stock,
        "location": payload.location,
        "last_updated": datetime.now().isoformat()
    })
    record = in_memory_db.get_inventory(inventory_id)
    return InventoryResponse(**record)


@app.get("/inventories", response_model=List[InventoryResponse])
async def list_inventories():
    """获取库存列表"""
    return [InventoryResponse(**inv) for inv in in_memory_db.list_inventories()]


@app.get("/inventories/{inventory_id}", response_model=InventoryResponse)
async def get_inventory(inventory_id: int):
    """获取库存详情"""
    record = in_memory_db.get_inventory(inventory_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="库存未找到")
    return InventoryResponse(**record)


@app.put("/inventories/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(inventory_id: int, payload: InventoryUpdate):
    """更新库存"""
    record = in_memory_db.get_inventory(inventory_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="库存未找到")
    
    updates: Dict[str, Any] = {}
    for field in ["quantity", "min_stock", "max_stock", "location"]:
        val = getattr(payload, field)
        if val is not None:
            updates[field] = val
    ok = in_memory_db.update_inventory(inventory_id, updates)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="更新失败")
    updated = in_memory_db.get_inventory(inventory_id)
    return InventoryResponse(**updated)


@app.delete("/inventories/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory(inventory_id: int):
    """删除库存"""
    record = in_memory_db.get_inventory(inventory_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="库存未找到")
    in_memory_db.delete_inventory(inventory_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# 供应商相关API
@app.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(payload: SupplierCreate):
    """创建供应商"""
    supplier_id = in_memory_db.create_supplier({
        "company_name": payload.company_name,
        "contact_person": payload.contact_person,
        "email": payload.email,
        "phone": payload.phone,
        "address": payload.address,
        "country": payload.country,
        "is_active": payload.is_active,
        "created_at": datetime.now().isoformat()
    })
    record = in_memory_db.get_supplier(supplier_id)
    return SupplierResponse(**record)


@app.get("/suppliers", response_model=List[SupplierResponse])
async def list_suppliers():
    """获取供应商列表"""
    return [SupplierResponse(**s) for s in in_memory_db.list_suppliers()]


@app.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: int):
    """获取供应商详情"""
    record = in_memory_db.get_supplier(supplier_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="供应商未找到")
    return SupplierResponse(**record)


@app.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(supplier_id: int, payload: SupplierUpdate):
    """更新供应商"""
    record = in_memory_db.get_supplier(supplier_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="供应商未找到")
    
    updates: Dict[str, Any] = {}
    for field in ["company_name", "contact_person", "email", "phone", "address", "country", "is_active"]:
        val = getattr(payload, field)
        if val is not None:
            updates[field] = val
    ok = in_memory_db.update_supplier(supplier_id, updates)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="更新失败")
    updated = in_memory_db.get_supplier(supplier_id)
    return SupplierResponse(**updated)


@app.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: int):
    """删除供应商"""
    record = in_memory_db.get_supplier(supplier_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="供应商未找到")
    in_memory_db.delete_supplier(supplier_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


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