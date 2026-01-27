"""数据库模拟模块"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


class Database:
    """简单的内存数据库模拟类"""
    
    def __init__(self, db_name: str = "app_db"):
        """
        初始化数据库
        
        Args:
            db_name: 数据库名称，用于持久化文件名
        """
        self.db_name = db_name
        self.data_file = f"{db_name}.json"
        self.tables: Dict[str, List[Dict[str, Any]]] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """从文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.tables = json.load(f)
                print(f"数据已从 {self.data_file} 加载")
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载数据文件失败: {e}，创建新的数据库")
                self.tables = {}
        else:
            self.tables = {}
            print(f"数据库文件 {self.data_file} 不存在，创建新的数据库")
    
    def _save_data(self) -> None:
        """保存数据到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.tables, f, indent=2, ensure_ascii=False, default=str)
            print(f"数据已保存到 {self.data_file}")
        except IOError as e:
            print(f"保存数据文件失败: {e}")
    
    def create_table(self, table_name: str) -> None:
        """
        创建新表
        
        Args:
            table_name: 表名
        """
        if table_name not in self.tables:
            self.tables[table_name] = []
            print(f"表 '{table_name}' 已创建")
        else:
            print(f"表 '{table_name}' 已存在")
    
    def insert(self, table_name: str, record: Dict[str, Any]) -> str:
        """
        插入记录
        
        Args:
            table_name: 表名
            record: 要插入的记录
            
        Returns:
            记录ID
        """
        if table_name not in self.tables:
            self.create_table(table_name)
        
        # 生成唯一ID
        record_id = str(uuid.uuid4())
        record['id'] = record_id
        record['created_at'] = datetime.now().isoformat()
        
        self.tables[table_name].append(record)
        self._save_data()
        
        print(f"记录已插入到表 '{table_name}'，ID: {record_id}")
        return record_id
    
    def select(self, table_name: str, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        查询记录
        
        Args:
            table_name: 表名
            where: 查询条件
            
        Returns:
            符合条件的记录列表
        """
        if table_name not in self.tables:
            return []
        
        records = self.tables[table_name]
        
        if where is None:
            return records
        
        # 简单的条件过滤
        filtered_records = []
        for record in records:
            match = True
            for key, value in where.items():
                if key not in record or record[key] != value:
                    match = False
                    break
            if match:
                filtered_records.append(record)
        
        return filtered_records
    
    def update(self, table_name: str, record_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新记录
        
        Args:
            table_name: 表名
            record_id: 记录ID
            updates: 要更新的字段
            
        Returns:
            是否更新成功
        """
        if table_name not in self.tables:
            return False
        
        for i, record in enumerate(self.tables[table_name]):
            if record.get('id') == record_id:
                # 更新记录
                for key, value in updates.items():
                    if key != 'id':  # 不允许更新ID
                        record[key] = value
                
                record['updated_at'] = datetime.now().isoformat()
                self.tables[table_name][i] = record
                self._save_data()
                
                print(f"记录 {record_id} 已更新")
                return True
        
        print(f"记录 {record_id} 未找到")
        return False
    
    def delete(self, table_name: str, record_id: str) -> bool:
        """
        删除记录
        
        Args:
            table_name: 表名
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        if table_name not in self.tables:
            return False
        
        for i, record in enumerate(self.tables[table_name]):
            if record.get('id') == record_id:
                del self.tables[table_name][i]
                self._save_data()
                
                print(f"记录 {record_id} 已删除")
                return True
        
        print(f"记录 {record_id} 未找到")
        return False
    
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        return list(self.tables.keys())
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表信息"""
        if table_name not in self.tables:
            return {"exists": False, "count": 0, "columns": []}
        
        records = self.tables[table_name]
        if records:
            columns = list(records[0].keys())
        else:
            columns = []
        
        return {
            "exists": True,
            "count": len(records),
            "columns": columns
        }
    
    def clear_table(self, table_name: str) -> None:
        """清空表数据"""
        if table_name in self.tables:
            self.tables[table_name] = []
            self._save_data()
            print(f"表 '{table_name}' 已清空")
    
    def drop_table(self, table_name: str) -> None:
        """删除表"""
        if table_name in self.tables:
            del self.tables[table_name]
            self._save_data()
            print(f"表 '{table_name}' 已删除")
    
    def reset_database(self) -> None:
        """重置整个数据库"""
        self.tables = {}
        self._save_data()
        print("数据库已重置")


# ==================== 基于字典的内存数据库（User/Product专用） ====================

class InMemoryDatabase:
    """使用Python字典模拟的内存数据库，专注于User和Product存储"""
    
    def __init__(self):
        # 存储结构：{id: record_dict}
        self.users: Dict[int, Dict[str, Any]] = {}
        self.products: Dict[int, Dict[str, Any]] = {}
        # 自增ID计数器
        self._user_id_seq = 0
        self._product_id_seq = 0
    
    # -------- User 操作 --------
    def create_user(self, user_data: Dict[str, Any]) -> int:
        """创建用户，返回user_id"""
        self._user_id_seq += 1
        user_id = self._user_id_seq
        record = {
            "user_id": user_id,
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "is_active": user_data.get("is_active", True),
            "created_at": user_data.get("created_at", datetime.now().isoformat())
        }
        self.users[user_id] = record
        return user_id
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        return self.users.get(user_id)
    
    def list_users(self) -> List[Dict[str, Any]]:
        """获取所有用户列表"""
        return list(self.users.values())
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """更新用户信息"""
        if user_id not in self.users:
            return False
        record = self.users[user_id].copy()
        record.update({k: v for k, v in updates.items() if k != "user_id"})
        record["updated_at"] = datetime.now().isoformat()
        self.users[user_id] = record
        return True
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        return self.users.pop(user_id, None) is not None
    
    # -------- Product 操作 --------
    def create_product(self, product_data: Dict[str, Any]) -> int:
        """创建产品，返回product_id"""
        self._product_id_seq += 1
        product_id = self._product_id_seq
        record = {
            "product_id": product_id,
            "name": product_data.get("name"),
            "description": product_data.get("description"),
            "price": product_data.get("price"),
            "stock": product_data.get("stock", 0),
            "is_available": product_data.get("is_available", True),
            "created_at": product_data.get("created_at", datetime.now().isoformat())
        }
        self.products[product_id] = record
        return product_id
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取产品"""
        return self.products.get(product_id)
    
    def list_products(self) -> List[Dict[str, Any]]:
        """获取所有产品列表"""
        return list(self.products.values())
    
    def update_product(self, product_id: int, updates: Dict[str, Any]) -> bool:
        """更新产品信息"""
        if product_id not in self.products:
            return False
        record = self.products[product_id].copy()
        record.update({k: v for k, v in updates.items() if k != "product_id"})
        record["updated_at"] = datetime.now().isoformat()
        self.products[product_id] = record
        return True
    
    def delete_product(self, product_id: int) -> bool:
        """删除产品"""
        return self.products.pop(product_id, None) is not None
    
    # -------- 工具方法 --------
    def reset(self) -> None:
        """重置内存数据库"""
        self.users.clear()
        self.products.clear()
        self._user_id_seq = 0
        self._product_id_seq = 0


# 数据库连接管理器
class DatabaseManager:
    """数据库连接管理器"""
    
    _instance = None
    _databases = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def get_database(self, db_name: str = "app_db") -> Database:
        """
        获取数据库实例
        
        Args:
            db_name: 数据库名称
            
        Returns:
            Database实例
        """
        if db_name not in self._databases:
            self._databases[db_name] = Database(db_name)
        return self._databases[db_name]
    
    def list_databases(self) -> List[str]:
        """获取所有数据库名称"""
        return list(self._databases.keys())
    
    def remove_database(self, db_name: str) -> None:
        """移除数据库实例"""
        if db_name in self._databases:
            del self._databases[db_name]
            print(f"数据库 '{db_name}' 已从管理器中移除")


# 示例用法
if __name__ == "__main__":
    # 创建数据库实例
    db = Database("example_db")
    
    # 创建用户表并插入数据
    user_data = {
        "name": "张三",
        "email": "****************",
        "age": 25
    }
    user_id = db.insert("users", user_data)
    
    # 创建产品表并插入数据
    product_data = {
        "name": "Python书籍",
        "price": 59.99,
        "stock": 100
    }
    product_id = db.insert("products", product_data)
    
    # 查询数据
    users = db.select("users")
    products = db.select("products", {"price": 59.99})
    
    print(f"用户数量: {len(users)}")
    print(f"价格59.99的产品数量: {len(products)}")
    
    # 更新数据
    db.update("users", user_id, {"age": 26})
    
    # 获取数据库信息
    print(f"所有表: {db.get_all_tables()}")
    for table in db.get_all_tables():
        info = db.get_table_info(table)
        print(f"表 '{table}': {info}")
    
    print("数据库演示完成！")