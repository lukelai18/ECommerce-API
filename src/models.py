"""数据模型模块"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


# ==================== Pydantic 数据模型 ====================

class UserPydantic(BaseModel):
    """Pydantic用户数据模型"""
    user_id: int
    username: str
    email: EmailStr
    created_at: datetime
    
    class Config:
        """配置类"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "user_id": 1,
                "username": "john_doe",
                "email": "****************",
                "created_at": "2024-01-01T12:00:00"
            }
        }


class UserCreatePydantic(BaseModel):
    """Pydantic用户创建模型"""
    username: str
    email: EmailStr
    
    @validator('username')
    def username_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('用户名不能为空')
        if len(v) < 3:
            raise ValueError('用户名长度至少为3个字符')
        return v.strip()
    
    @validator('email')
    def validate_email_format(cls, v):
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v
    
    class Config:
        """配置类"""
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "****************"
            }
        }


class UserUpdatePydantic(BaseModel):
    """Pydantic用户更新模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @validator('username')
    def username_validation(cls, v):
        if v is not None:
            if not v or len(v.strip()) == 0:
                raise ValueError('用户名不能为空')
            if len(v) < 3:
                raise ValueError('用户名长度至少为3个字符')
        return v.strip() if v else v


class ProductPydantic(BaseModel):
    """Pydantic产品数据模型"""
    product_id: int
    name: str
    description: Optional[str] = None
    price: float
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('产品名称不能为空')
        if len(v) > 100:
            raise ValueError('产品名称长度不能超过100个字符')
        return v.strip()
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('产品价格必须大于0')
        return v
    
    @validator('description')
    def description_validation(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('产品描述长度不能超过500个字符')
        return v
    
    class Config:
        """配置类"""
        schema_extra = {
            "example": {
                "product_id": 1,
                "name": "Python编程书籍",
                "description": "Python编程入门指南",
                "price": 59.99
            }
        }


class ProductCreatePydantic(BaseModel):
    """Pydantic产品创建模型"""
    name: str
    description: Optional[str] = None
    price: float
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('产品名称不能为空')
        if len(v) > 100:
            raise ValueError('产品名称长度不能超过100个字符')
        return v.strip()
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('产品价格必须大于0')
        return v
    
    @validator('description')
    def description_validation(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('产品描述长度不能超过500个字符')
        return v
    
    class Config:
        """配置类"""
        schema_extra = {
            "example": {
                "name": "Python编程书籍",
                "description": "Python编程入门指南",
                "price": 59.99
            }
        }


class ProductUpdatePydantic(BaseModel):
    """Pydantic产品更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    
    @validator('name')
    def name_validation(cls, v):
        if v is not None:
            if not v or len(v.strip()) == 0:
                raise ValueError('产品名称不能为空')
            if len(v) > 100:
                raise ValueError('产品名称长度不能超过100个字符')
        return v.strip() if v else v
    
    @validator('price')
    def price_validation(cls, v):
        if v is not None and v <= 0:
            raise ValueError('产品价格必须大于0')
        return v
    
    @validator('description')
    def description_validation(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('产品描述长度不能超过500个字符')
        return v


class ProductWithStockPydantic(BaseModel):
    """Pydantic产品完整模型（包含库存信息）"""
    product_id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    is_available: bool = True


# ==================== 新增5个Pydantic数据模型 ====================

class OrderPydantic(BaseModel):
    """Pydantic订单数据模型"""
    order_id: int
    user_id: int
    products: List[ProductPydantic]
    total_amount: float
    status: str = "pending"
    created_at: datetime
    
    class Config:
        """配置类"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CategoryPydantic(BaseModel):
    """Pydantic分类数据模型"""
    category_id: int
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    is_active: bool = True
    created_at: datetime
    
    @validator('name')
    def validate_category_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('分类名称不能为空')
        if len(v) > 50:
            raise ValueError('分类名称长度不能超过50个字符')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v) > 200:
            raise ValueError('分类描述长度不能超过200个字符')
        return v
    
    class Config:
        """配置类"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "category_id": 1,
                "name": "电子产品",
                "description": "各类电子设备和配件",
                "parent_category_id": None,
                "is_active": True,
                "created_at": "2024-01-01T12:00:00"
            }
        }


class ReviewPydantic(BaseModel):
    """Pydantic评价数据模型"""
    review_id: int
    product_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('评分必须在1-5之间')
        return v
    
    @validator('comment')
    def validate_comment(cls, v):
        if v is not None and len(v) > 1000:
            raise ValueError('评价内容长度不能超过1000个字符')
        return v
    
    class Config:
        """配置类"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "review_id": 1,
                "product_id": 1,
                "user_id": 1,
                "rating": 5,
                "comment": "非常好的产品，值得推荐！",
                "created_at": "2024-01-01T12:00:00"
            }
        }


class InventoryPydantic(BaseModel):
    """Pydantic库存数据模型"""
    inventory_id: int
    product_id: int
    quantity: int
    min_stock: int = 10
    max_stock: int = 1000
    location: str = "主仓库"
    last_updated: datetime
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('库存数量不能为负数')
        return v
    
    @validator('min_stock')
    def validate_min_stock(cls, v):
        if v < 0:
            raise ValueError('最小库存不能为负数')
        return v
    
    @validator('max_stock')
    def validate_max_stock(cls, v, values):
        if v <= 0:
            raise ValueError('最大库存必须大于0')
        if 'min_stock' in values and v <= values['min_stock']:
            raise ValueError('最大库存必须大于最小库存')
        return v
    
    @validator('location')
    def validate_location(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('库存位置不能为空')
        if len(v) > 100:
            raise ValueError('库存位置长度不能超过100个字符')
        return v.strip()
    
    class Config:
        """配置类"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "inventory_id": 1,
                "product_id": 1,
                "quantity": 50,
                "min_stock": 10,
                "max_stock": 100,
                "location": "主仓库A区",
                "last_updated": "2024-01-01T12:00:00"
            }
        }


class SupplierPydantic(BaseModel):
    """Pydantic供应商数据模型"""
    supplier_id: int
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: str
    country: str = "中国"
    is_active: bool = True
    created_at: datetime
    
    @validator('company_name')
    def validate_company_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('公司名称不能为空')
        if len(v) > 100:
            raise ValueError('公司名称长度不能超过100个字符')
        return v.strip()
    
    @validator('contact_person')
    def validate_contact_person(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('联系人不能为空')
        if len(v) > 50:
            raise ValueError('联系人长度不能超过50个字符')
        return v.strip()
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('联系电话不能为空')
        if len(v) > 20:
            raise ValueError('联系电话长度不能超过20个字符')
        return v.strip()
    
    @validator('address')
    def validate_address(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('地址不能为空')
        if len(v) > 200:
            raise ValueError('地址长度不能超过200个字符')
        return v.strip()
    
    @validator('country')
    def validate_country(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('国家不能为空')
        if len(v) > 50:
            raise ValueError('国家名称长度不能超过50个字符')
        return v.strip()
    
    class Config:
        """配置类"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "supplier_id": 1,
                "company_name": "科技有限公司",
                "contact_person": "张经理",
                "email": "****************",
                "phone": "13800138000",
                "address": "北京市朝阳区科技园区",
                "country": "中国",
                "is_active": True,
                "created_at": "2024-01-01T12:00:00"
            }
        }


class OrderDetailPydantic(BaseModel):
    """Pydantic订单详情数据模型"""
    order_detail_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    discount: float = 0.0
    subtotal: float
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('数量必须大于0')
        return v
    
    @validator('unit_price')
    def validate_unit_price(cls, v):
        if v <= 0:
            raise ValueError('单价必须大于0')
        return v
    
    @validator('discount')
    def validate_discount(cls, v):
        if v < 0 or v > 1:
            raise ValueError('折扣必须在0-1之间')
        return v
    
    @validator('subtotal')
    def validate_subtotal(cls, v, values):
        if v <= 0:
            raise ValueError('小计必须大于0')
        expected_subtotal = values.get('quantity', 0) * values.get('unit_price', 0) * (1 - values.get('discount', 0))
        if abs(v - expected_subtotal) > 0.01:  # 允许0.01的浮点误差
            raise ValueError(f'小计计算不正确，期望值为{expected_subtotal}')
        return v
    
    class Config:
        """配置类"""
        schema_extra = {
            "example": {
                "order_detail_id": 1,
                "order_id": 1,
                "product_id": 1,
                "quantity": 2,
                "unit_price": 59.99,
                "discount": 0.1,
                "subtotal": 107.98
            }
        }


# ==================== 原始数据类模型 ====================

@dataclass
class User:
    """用户模型（原始数据类）"""
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool = True
    
    def __post_init__(self):
        """初始化后的处理"""
        if not self.email or '@' not in self.email:
            raise ValueError("无效的邮箱地址")
    
    def to_pydantic(self) -> UserPydantic:
        """转换为Pydantic模型"""
        return UserPydantic(
            user_id=self.id,
            username=self.username,
            email=self.email,
            created_at=self.created_at
        )


@dataclass
class Product:
    """产品模型（原始数据类）"""
    id: int
    name: str
    price: float
    description: str
    stock: int = 0
    
    @property
    def is_available(self) -> bool:
        """检查产品是否有库存"""
        return self.stock > 0
    
    def update_stock(self, quantity: int) -> None:
        """更新库存数量"""
        if self.stock + quantity < 0:
            raise ValueError("库存不足")
        self.stock += quantity
    
    def to_pydantic(self) -> ProductPydantic:
        """转换为Pydantic模型"""
        return ProductPydantic(
            product_id=self.id,
            name=self.name,
            price=self.price,
            description=self.description,
            stock=self.stock,
            is_available=self.is_available
        )


@dataclass
class Order:
    """订单模型（原始数据类）"""
    id: int
    user_id: int
    products: List[Product]
    total_amount: float
    status: str = "pending"
    created_at: datetime = None
    
    def __post_init__(self):
        """初始化后的处理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        
        if self.status not in ["pending", "confirmed", "shipped", "delivered", "cancelled"]:
            raise ValueError("无效的订单状态")
    
    def add_product(self, product: Product) -> None:
        """添加产品到订单"""
        self.products.append(product)
        self.total_amount += product.price
    
    def update_status(self, new_status: str) -> None:
        """更新订单状态"""
        valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
        if new_status not in valid_statuses:
            raise ValueError(f"无效的状态: {new_status}")
        self.status = new_status
    
    def to_pydantic(self) -> OrderPydantic:
        """转换为Pydantic模型"""
        return OrderPydantic(
            order_id=self.id,
            user_id=self.user_id,
            products=[p.to_pydantic() for p in self.products],
            total_amount=self.total_amount,
            status=self.status,
            created_at=self.created_at
        )


class DataStore:
    """简单的数据存储类"""
    
    def __init__(self):
        self.users: List[User] = []
        self.products: List[Product] = []
        self.orders: List[Order] = []
    
    def add_user(self, user: User) -> None:
        """添加用户"""
        self.users.append(user)
    
    def add_product(self, product: Product) -> None:
        """添加产品"""
        self.products.append(product)
    
    def add_order(self, order: Order) -> None:
        """添加订单"""
        self.orders.append(order)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """根据ID获取产品"""
        for product in self.products:
            if product.id == product_id:
                return product
        return None
    
    def get_available_products(self) -> List[Product]:
        """获取可用的产品列表"""
        return [product for product in self.products if product.is_available]
    
    def get_all_users_pydantic(self) -> List[UserPydantic]:
        """获取所有用户的Pydantic模型列表"""
        return [user.to_pydantic() for user in self.users]
    
    def get_all_products_pydantic(self) -> List[ProductPydantic]:
        """获取所有产品的Pydantic模型列表"""
        return [product.to_pydantic() for product in self.products]
    
    def get_all_orders_pydantic(self) -> List[OrderPydantic]:
        """获取所有订单的Pydantic模型列表"""
        return [order.to_pydantic() for order in self.orders]


# ==================== 示例用法 ====================

if __name__ == "__main__":
    print("=== 数据模型演示 ===")
    
    # 创建数据存储实例
    store = DataStore()
    
    # 创建示例用户
    user1 = User(
        id=1,
        username="john_doe",
        email="****************",
        created_at=datetime.now()
    )
    store.add_user(user1)
    
    # 创建示例产品
    product1 = Product(
        id=1,
        name="Python编程书籍",
        price=59.99,
        description="Python编程入门指南",
        stock=10
    )
    store.add_product(product1)
    
    # 创建示例订单
    order1 = Order(
        id=1,
        user_id=1,
        products=[product1],
        total_amount=59.99
    )
    store.add_order(order1)
    
    print("数据模型示例已创建完成！")
    print(f"用户数: {len(store.users)}")
    print(f"产品数: {len(store.products)}")
    print(f"订单数: {len(store.orders)}")
    print(f"可用产品数: {len(store.get_available_products())}")
    
    # 演示Pydantic模型
    print("\n=== Pydantic模型演示 ===")
    user_pydantic = user1.to_pydantic()
    print(f"用户Pydantic模型: {user_pydantic}")
    print(f"JSON格式: {user_pydantic.json(indent=2)}")
    
    # 演示创建Pydantic用户
    print("\n=== 创建Pydantic用户演示 ===")
    try:
        new_user_data = {
            "username": "jane_smith",
            "email": "****************"
        }
        new_user_pydantic = UserCreatePydantic(**new_user_data)
        print(f"新用户Pydantic模型创建成功: {new_user_pydantic}")
    except ValueError as e:
        print(f"创建失败: {e}")