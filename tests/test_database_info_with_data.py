#!/usr/bin/env python3
"""测试数据库信息API（包含数据）"""

from fastapi.testclient import TestClient
from src.main import app

def test_database_info_with_data():
    """测试数据库信息API（在添加数据后）"""
    client = TestClient(app)
    
    try:
        print("=== 测试1：初始状态 ===")
        # 测试初始状态
        response = client.get("/database/info")
        assert response.status_code == 200
        data = response.json()
        print(f"初始总记录数: {data['total_records']}")
        assert data["total_records"] == 0
        
        print("=== 测试2：添加用户后 ===")
        # 添加一个用户
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "is_active": True
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 200
        user = response.json()
        print(f"创建用户: {user['username']}")
        
        # 再次检查数据库信息
        response = client.get("/database/info")
        assert response.status_code == 200
        data = response.json()
        print(f"添加用户后总记录数: {data['total_records']}")
        assert data["total_records"] == 1
        assert data["tables"]["users"]["count"] == 1
        assert data["tables"]["products"]["count"] == 0
        
        print("=== 测试3：添加产品后 ===")
        # 添加一个产品
        product_data = {
            "name": "测试产品",
            "description": "这是一个测试产品",
            "price": 99.99,
            "stock": 10,
            "is_available": True
        }
        response = client.post("/products", json=product_data)
        assert response.status_code == 200
        product = response.json()
        print(f"创建产品: {product['name']}")
        
        # 再次检查数据库信息
        response = client.get("/database/info")
        assert response.status_code == 200
        data = response.json()
        print(f"添加产品后总记录数: {data['total_records']}")
        assert data["total_records"] == 2
        assert data["tables"]["users"]["count"] == 1
        assert data["tables"]["products"]["count"] == 1
        
        print("=== 测试4：验证所有表字段信息 ===")
        # 验证所有表的字段信息
        tables = data["tables"]
        
        # 验证用户表字段
        user_fields = tables["users"]["fields"]
        expected_user_fields = ["user_id", "username", "email", "is_active", "created_at", "updated_at"]
        for field in expected_user_fields:
            assert field in user_fields, f"用户表缺少字段: {field}"
        
        # 验证产品表字段
        product_fields = tables["products"]["fields"]
        expected_product_fields = ["product_id", "name", "description", "price", "stock", "is_available", "created_at", "updated_at"]
        for field in expected_product_fields:
            assert field in product_fields, f"产品表缺少字段: {field}"
        
        # 验证其他表的字段
        for table_name, table_info in tables.items():
            assert "count" in table_info, f"表 {table_name} 缺少 count 字段"
            assert "fields" in table_info, f"表 {table_name} 缺少 fields 字段"
            assert isinstance(table_info["count"], int), f"表 {table_name} 的 count 应该是整数"
            assert isinstance(table_info["fields"], list), f"表 {table_name} 的 fields 应该是列表"
        
        print("✓ 所有表字段验证通过")
        
        print("=== 测试5：验证数据库信息 ===")
        # 验证数据库信息
        assert data["database_name"] == "InMemoryDatabase"
        assert "内存" in data["message"]
        assert data["total_records"] == 2
        
        print("✓ 数据库信息验证通过")
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("开始测试数据库信息API（包含数据）...")
    success = test_database_info_with_data()
    if success:
        print("\n✅ 测试完成：所有测试都通过了！")
    else:
        print("\n❌ 测试失败：某些测试未通过！")