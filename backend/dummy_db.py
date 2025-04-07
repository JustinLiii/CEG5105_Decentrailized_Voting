"""
匿名账户分配系统 - 内存数据库模拟
用于测试盲签名和账户分配流程，不需要实际数据库
"""

import datetime
from typing import List, Dict, Any, Tuple, Optional


class DummyDB:
    """模拟数据库连接"""
    
    def __init__(self):
        self.tables = {
            'account_pool': [],
            'assigned_accounts': [],
            'used_signatures': []
        }
        self._cursor = DummyCursor(self)
    
    def cursor(self):
        """返回数据库游标"""
        return self._cursor
    
    def commit(self):
        """模拟提交事务"""
        pass
    
    def close(self):
        """模拟关闭连接"""
        pass


class DummyCursor:
    """模拟数据库游标"""
    
    def __init__(self, db: DummyDB):
        self.db = db
        self.last_query = None
        self.last_params = None
        self.fetch_results = None
    
    def execute(self, query: str, params=None):
        """模拟执行SQL查询"""
        self.last_query = query.lower()
        self.last_params = params
        
        # 处理SELECT查询
        if 'select' in self.last_query:
            if 'from account_pool where id =' in self.last_query:
                # 查询特定账户
                account_id = params[0]
                self.fetch_results = next(
                    (acc for acc in self.db.tables['account_pool'] if acc['id'] == account_id),
                    None
                )
                if self.fetch_results:
                    self.fetch_results = (self.fetch_results['address'],)
            
            elif 'from account_pool where is_assigned = false' in self.last_query:
                # 查询未分配账户
                available = [
                    (acc['id'], acc['address']) 
                    for acc in self.db.tables['account_pool'] 
                    if not acc['is_assigned']
                ]
                self.fetch_results = available
            
            elif 'from assigned_accounts where user_hash =' in self.last_query:
                # 查询用户已分配账户
                user_hash = params[0]
                assigned = next(
                    (acc for acc in self.db.tables['assigned_accounts'] if acc['user_hash'] == user_hash),
                    None
                )
                if assigned:
                    self.fetch_results = (assigned['account_id'],)
                else:
                    self.fetch_results = None
            
            elif 'from used_signatures where signature =' in self.last_query:
                # 查询签名是否已使用
                signature = params[0]
                used = next(
                    (sig for sig in self.db.tables['used_signatures'] if sig['signature'] == signature),
                    None
                )
                if used:
                    self.fetch_results = (used['id'],)
                else:
                    self.fetch_results = None
            
            elif 'count(*)' in self.last_query:
                # 计数查询
                table_name = self.last_query.split('from')[1].strip().split()[0]
                count = len(self.db.tables.get(table_name, []))
                self.fetch_results = (count,)
        
        # 处理INSERT查询
        elif 'insert into' in self.last_query:
            if 'account_pool' in self.last_query:
                # 插入新账户
                new_id = len(self.db.tables['account_pool']) + 1
                address = params[0]
                self.db.tables['account_pool'].append({
                    'id': new_id,
                    'address': address,
                    'is_assigned': False,
                    'created_at': datetime.datetime.now()
                })
            
            elif 'assigned_accounts' in self.last_query:
                # 分配账户
                new_id = len(self.db.tables['assigned_accounts']) + 1
                user_hash = params[0]
                account_id = params[1]
                self.db.tables['assigned_accounts'].append({
                    'id': new_id,
                    'user_hash': user_hash,
                    'account_id': account_id,
                    'assigned_at': datetime.datetime.now()
                })
            
            elif 'used_signatures' in self.last_query:
                # 记录已使用签名
                new_id = len(self.db.tables['used_signatures']) + 1
                signature = params[0]
                self.db.tables['used_signatures'].append({
                    'id': new_id,
                    'signature': signature,
                    'used_at': datetime.datetime.now()
                })
        
        # 处理UPDATE查询
        elif 'update account_pool set is_assigned = true where id =' in self.last_query:
            # 标记账户为已分配
            account_id = params[0]
            for acc in self.db.tables['account_pool']:
                if acc['id'] == account_id:
                    acc['is_assigned'] = True
                    break
    
    def fetchone(self):
        """返回单条结果"""
        return self.fetch_results
    
    def fetchall(self):
        """返回所有结果"""
        return self.fetch_results if self.fetch_results else []
    
    def close(self):
        """关闭游标"""
        pass


def get_mock_db():
    """获取模拟数据库连接"""
    db = DummyDB()
    
    # 添加一些测试账户
    for i in range(10):
        db.cursor().execute(
            "INSERT INTO account_pool (address, is_assigned) VALUES (%s, FALSE)",
            (f"0xTestAccount{i+1:04d}",)
        )
    
    return db 