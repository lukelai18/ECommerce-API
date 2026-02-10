import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"


# User模型测试
def test_create_user():
    """测试创建用户"""
    user_data = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25
    }
    resp = client.post("/users/", json=user_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["age"] == user_data["age"]
    assert "id" in data


def test_create_user_invalid_email():
    """测试创建用户时邮箱格式无效应返回422"""
    user_data = {
        "username": "invalid_email_user",
        "email": "not-an-email",
        "is_active": True
    }
    resp = client.post("/users", json=user_data)
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body
    assert any(err.get("loc", [None])[-1] == "email" for err in body.get("detail", []))


def test_get_user():
    """测试获取单个用户"""
    # 先创建一个用户
    user_data = {
        "name": "李四",
        "email": "lisi@example.com",
        "age": 30
    }
    create_resp = client.post("/users/", json=user_data)
    user_id = create_resp.json()["id"]
    
    # 获取用户
    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == user_id
    assert data["name"] == user_data["name"]


def test_get_users():
    """测试获取所有用户"""
    resp = client.get("/users/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_update_user():
    """测试更新用户"""
    # 先创建一个用户
    user_data = {
        "name": "王五",
        "email": "wangwu@example.com",
        "age": 28
    }
    create_resp = client.post("/users/", json=user_data)
    user_id = create_resp.json()["id"]
    
    # 更新用户
    update_data = {
        "name": "王五更新",
        "email": "wangwu.updated@example.com",
        "age": 29
    }
    resp = client.put(f"/users/{user_id}", json=update_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert data["age"] == update_data["age"]


def test_delete_user():
    """测试删除用户"""
    # 先创建一个用户
    user_data = {
        "name": "赵六",
        "email": "zhaoliu@example.com",
        "age": 32
    }
    create_resp = client.post("/users/", json=user_data)
    user_id = create_resp.json()["id"]
    
    # 删除用户
    resp = client.delete(f"/users/{user_id}")
    assert resp.status_code == 200
    
    # 确认用户已被删除
    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404


# Product模型测试
def test_create_product():
    """测试创建产品"""
    product_data = {
        "name": "笔记本电脑",
        "price": 5999.99,
        "description": "高性能笔记本电脑"
    }
    resp = client.post("/products/", json=product_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]
    assert data["description"] == product_data["description"]
    assert "id" in data


def test_get_product():
    """测试获取单个产品"""
    # 先创建一个产品
    product_data = {
        "name": "智能手机",
        "price": 2999.99,
        "description": "最新款智能手机"
    }
    create_resp = client.post("/products/", json=product_data)
    product_id = create_resp.json()["id"]
    
    # 获取产品
    resp = client.get(f"/products/{product_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == product_id
    assert data["name"] == product_data["name"]


def test_get_products():
    """测试获取所有产品"""
    resp = client.get("/products/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_update_product():
    """测试更新产品"""
    # 先创建一个产品
    product_data = {
        "name": "平板电脑",
        "price": 1999.99,
        "description": "轻薄平板电脑"
    }
    create_resp = client.post("/products/", json=product_data)
    product_id = create_resp.json()["id"]
    
    # 更新产品
    update_data = {
        "name": "平板电脑Pro",
        "price": 2499.99,
        "description": "升级版轻薄平板电脑"
    }
    resp = client.put(f"/products/{product_id}", json=update_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == update_data["name"]
    assert data["price"] == update_data["price"]
    assert data["description"] == update_data["description"]


def test_delete_product():
    """测试删除产品"""
    # 先创建一个产品
    product_data = {
        "name": "耳机",
        "price": 299.99,
        "description": "无线蓝牙耳机"
    }
    create_resp = client.post("/products/", json=product_data)
    product_id = create_resp.json()["id"]
    
    # 删除产品
    resp = client.delete(f"/products/{product_id}")
    assert resp.status_code == 200
    
    # 确认产品已被删除
    get_resp = client.get(f"/products/{product_id}")
    assert get_resp.status_code == 404


# Order模型测试
def test_create_order():
    """测试创建订单"""
    order_data = {
        "user_id": 1,
        "product_id": 1,
        "quantity": 2,
        "total_amount": 11999.98
    }
    resp = client.post("/orders/", json=order_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == order_data["user_id"]
    assert data["product_id"] == order_data["product_id"]
    assert data["quantity"] == order_data["quantity"]
    assert data["total_amount"] == order_data["total_amount"]
    assert "id" in data


def test_get_order():
    """测试获取单个订单"""
    # 先创建一个订单
    order_data = {
        "user_id": 2,
        "product_id": 2,
        "quantity": 1,
        "total_amount": 2999.99
    }
    create_resp = client.post("/orders/", json=order_data)
    order_id = create_resp.json()["id"]
    
    # 获取订单
    resp = client.get(f"/orders/{order_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == order_id
    assert data["user_id"] == order_data["user_id"]


def test_get_orders():
    """测试获取所有订单"""
    resp = client.get("/orders/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_update_order():
    """测试更新订单"""
    # 先创建一个订单
    order_data = {
        "user_id": 3,
        "product_id": 3,
        "quantity": 1,
        "total_amount": 1999.99
    }
    create_resp = client.post("/orders/", json=order_data)
    order_id = create_resp.json()["id"]
    
    # 更新订单
    update_data = {
        "user_id": 3,
        "product_id": 3,
        "quantity": 2,
        "total_amount": 3999.98
    }
    resp = client.put(f"/orders/{order_id}", json=update_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["quantity"] == update_data["quantity"]
    assert data["total_amount"] == update_data["total_amount"]


def test_delete_order():
    """测试删除订单"""
    # 先创建一个订单
    order_data = {
        "user_id": 4,
        "product_id": 4,
        "quantity": 1,
        "total_amount": 299.99
    }
    create_resp = client.post("/orders/", json=order_data)
    order_id = create_resp.json()["id"]
    
    # 删除订单
    resp = client.delete(f"/orders/{order_id}")
    assert resp.status_code == 200
    
    # 确认订单已被删除
    get_resp = client.get(f"/orders/{order_id}")
    assert get_resp.status_code == 404


# Category模型测试
def test_create_category():
    """测试创建分类"""
    category_data = {
        "name": "电子产品",
        "description": "各类电子设备"
    }
    resp = client.post("/categories/", json=category_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert "id" in data


def test_get_category():
    """测试获取单个分类"""
    # 先创建一个分类
    category_data = {
        "name": "家用电器",
        "description": "家庭使用的电器"
    }
    create_resp = client.post("/categories/", json=category_data)
    category_id = create_resp.json()["id"]
    
    # 获取分类
    resp = client.get(f"/categories/{category_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == category_id
    assert data["name"] == category_data["name"]


def test_get_categories():
    """测试获取所有分类"""
    resp = client.get("/categories/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_update_category():
    """测试更新分类"""
    # 先创建一个分类
    category_data = {
        "name": "服装",
        "description": "各类服装"
    }
    create_resp = client.post("/categories/", json=category_data)
    category_id = create_resp.json()["id"]
    
    # 更新分类
    update_data = {
        "name": "时尚服装",
        "description": "最新时尚服装"
    }
    resp = client.put(f"/categories/{category_id}", json=update_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


def test_delete_category():
    """测试删除分类"""
    # 先创建一个分类
    category_data = {
        "name": "图书",
        "description": "各类图书"
    }
    create_resp = client.post("/categories/", json=category_data)
    category_id = create_resp.json()["id"]
    
    # 删除分类
    resp = client.delete(f"/categories/{category_id}")
    assert resp.status_code == 200
    
    # 确认分类已被删除
    get_resp = client.get(f"/categories/{category_id}")
    assert get_resp.status_code == 404


# Review模型测试
def test_create_review():
    """测试创建评价"""
    review_data = {
        "product_id": 1,
        "user_id": 1,
        "rating": 5,
        "comment": "非常好的产品！"
    }
    resp = client.post("/reviews/", json=review_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["product_id"] == review_data["product_id"]
    assert data["user_id"] == review_data["user_id"]
    assert data["rating"] == review_data["rating"]
    assert data["comment"] == review_data["comment"]
    assert "id" in data


def test_get_review():
    """测试获取单个评价"""
    # 先创建一个评价
    review_data = {
        "product_id": 2,
        "user_id": 2,
        "rating": 4,
        "comment": "质量不错"
    }
    create_resp = client.post("/reviews/", json=review_data)
    review_id = create_resp.json()["id"]
    
    # 获取评价
    resp = client.get(f"/reviews/{review_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == review_id
    assert data["rating"] == review_data["rating"]


def test_get_reviews():
    """测试获取所有评价"""
    resp = client.get("/reviews/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_update_review():
    """测试更新评价"""
    # 先创建一个评价
    review_data = {
        "product_id": 3,
        "user_id": 3,
        "rating": 3,
        "comment": "一般般"
    }
    create_resp = client.post("/reviews/", json=review_data)
    review_id = create_resp.json()["id"]
    
    # 更新评价
    update_data = {
        "product_id": 3,
        "user_id": 3,
        "rating": 4,
        "comment": "还不错"
    }
    resp = client.put(f"/reviews/{review_id}", json=update_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["rating"] == update_data["rating"]
    assert data["comment"] == update_data["comment"]


def test_delete_review():
    """测试删除评价"""
    # 先创建一个评价
    review_data = {
        "product_id": 4,
        "user_id": 4,
        "rating": 2,
        "comment": "不太满意"
    }
    create_resp = client.post("/reviews/", json=review_data)
    review_id = create_resp.json()["id"]
    
    # 删除评价
    resp = client.delete(f"/reviews/{review_id}")
    assert resp.status_code == 200
    
    # 确认评价已被删除
    get_resp = client.get(f"/reviews/{review_id}")
    assert get_resp.status_code == 404


# Inventory模型测试
def test_create_inventory():
    """测试创建库存"""
    inventory_data = {
        "product_id": 1,
        "quantity": 100,
        "location": "仓库A"
    }
    resp = client.post("/inventory/", json=inventory_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["product_id"] == inventory_data["product_id"]
    assert data["quantity"] == inventory_data["quantity"]
    assert data["location"] == inventory_data["location"]
    assert "id" in data


def test_get_inventory():
    """测试获取单个库存"""
    # 先创建一个库存
    inventory_data = {
        "product_id": 2,
        "quantity": 50,
        "location": "仓库B"
    }
    create_resp = client.post("/inventory/", json=inventory_data)
    inventory_id = create_resp.json()["id"]
    
    # 获取库存
    resp = client.get(f"/inventory/{inventory_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == inventory_id
    assert data["quantity"] == inventory_data["quantity"]


def test_get_inventory_items():
    """测试获取所有库存"""
    resp = client.get("/inventory/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_update_inventory():
    """测试更新库存"""
    # 先创建一个库存
    inventory_data = {
        "product_id": 3,
        "quantity": 75,
        "location": "仓库C"
    }
    create_resp = client.post("/inventory/", json=inventory_data)
    inventory_id = create_resp.json()["id"]
    
    # 更新库存
    update_data = {
        "product_id": 3,
        "quantity": 80,
        "location": "仓库C"
    }
    resp = client.put(f"/inventory/{inventory_id}", json=update_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["quantity"] == update_data["quantity"]


def test_delete_inventory():
    """测试删除库存"""
    # 先创建一个库存
    inventory_data = {
        "product_id": 4,
        "quantity": 25,
        "location": "仓库D"
    }
    create_resp = client.post("/inventory/", json=inventory_data)
    inventory_id = create_resp.json()["id"]
    
    # 删除库存
    resp = client.delete(f"/inventory/{inventory_id}")
    assert resp.status_code == 200
    
    # 确认库存已被删除
    get_resp = client.get(f"/inventory/{inventory_id}")
    assert get_resp.status_code == 404


# Supplier模型测试
def test_create_supplier():
    """测试创建供应商"""
    supplier_data = {
        "name": "供应商A",
        "contact": "联系人A",
        "phone": "13800138000",
        "email": "supplier@example.com",
        "address": "北京市朝阳区"
    }
    resp = client.post("/suppliers/", json=supplier_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == supplier_data["name"]
    assert data["contact"] == supplier_data["contact"]
    assert data["phone"] == supplier_data["phone"]
    assert data["email"] == supplier_data["email"]
    assert data["address"] == supplier_data["address"]
    assert "id" in data


def test_get_supplier():
    """测试获取单个供应商"""
    # 先创建一个供应商
    supplier_data = {
        "name": "供应商B",
        "contact": "联系人B",
        "phone": "13900139000",
        "email": "supplierb@example.com",
        "address": "上海市浦东新区"
    }
    create_resp = client.post("/suppliers/", json=supplier_data)
    supplier_id = create_resp.json()["id"]
    
    # 获取供应商
    resp = client.get(f"/suppliers/{supplier_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == supplier_id
    assert data["name"] == supplier_data["name"]


def test_get_suppliers():
    """测试获取所有供应商"""
    resp = client.get("/suppliers/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_update_supplier():
    """测试更新供应商"""
    # 先创建一个供应商
    supplier_data = {
        "name": "供应商C",
        "contact": "联系人C",
        "phone": "13700137000",
        "email": "supplierc@example.com",
        "address": "广州市天河区"
    }
    create_resp = client.post("/suppliers/", json=supplier_data)
    supplier_id = create_resp.json()["id"]
    
    # 更新供应商
    update_data = {
        "name": "供应商C更新",
        "contact": "联系人C更新",
        "phone": "13700137001",
        "email": "supplierc.updated@example.com",
        "address": "深圳市南山区"
    }
    resp = client.put(f"/suppliers/{supplier_id}", json=update_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == update_data["name"]
    assert data["contact"] == update_data["contact"]
    assert data["phone"] == update_data["phone"]
    assert data["email"] == update_data["email"]
    assert data["address"] == update_data["address"]


def test_delete_supplier():
    """测试删除供应商"""
    # 先创建一个供应商
    supplier_data = {
        "name": "供应商D",
        "contact": "联系人D",
        "phone": "13600136000",
        "email": "supplierd@example.com",
        "address": "杭州市西湖区"
    }
    create_resp = client.post("/suppliers/", json=supplier_data)
    supplier_id = create_resp.json()["id"]
    
    # 删除供应商
    resp = client.delete(f"/suppliers/{supplier_id}")
    assert resp.status_code == 200
    
    # 确认供应商已被删除
    get_resp = client.get(f"/suppliers/{supplier_id}")
    assert get_resp.status_code == 404