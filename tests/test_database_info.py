#!/usr/bin/env python3
"""测试数据库信息API"""

from fastapi.testclient import TestClient
from src.main import app

def test_database_info_api():
    """测试数据库信息API"""
    client = TestClient(app)
    
    try:
        # 测试数据库信息API
        response = client.get("/database/info")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("数据库信息API测试成功！")
            print("返回数据:")
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 验证数据结构
            assert "database_name" in data
            assert "tables" in data
            assert "total_records" in data
            assert "message" in data
            
            print("✓ 数据结构验证通过")
            
            # 验证表信息
            tables = data["tables"]
            expected_tables = ["users", "products", "orders", "categories", "reviews", "inventories", "suppliers"]
            
            for table in expected_tables:
                assert table in tables, f"缺少表: {table}"
                assert "count" in tables[table], f"表 {table} 缺少 count 字段"
                assert "fields" in tables[table], f"表 {table} 缺少 fields 字段"
            
            print("✓ 表信息验证通过")
            print(f"✓ 总记录数: {data['total_records']}")
            
            # 验证数据库名称和消息
            assert data["database_name"] == "InMemoryDatabase"
            assert "内存" in data["message"]
            
            print("✓ 数据库信息验证通过")
            print("🎉 所有测试通过！")
            
        else:
            print(f"API调用失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试数据库信息API...")
    test_database_info_api()