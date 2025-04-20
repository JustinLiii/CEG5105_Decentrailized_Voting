#!/usr/bin/env python3
"""
匿名账户分配系统 - 初始化脚本
- 生成RSA密钥对
- 初始化数据库表

使用方法:
python setup.py [--db-host HOST] [--db-user USER] [--db-password PASS] [--db-name NAME]
"""

import argparse
import sys
import pymysql
from Crypto.PublicKey import RSA

from blockchain import create_account, fund_account

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='匿名账户分配系统初始化工具')
    parser.add_argument('--db-host', default='localhost', help='数据库主机地址')
    parser.add_argument('--db-user', default='root', help='数据库用户名')
    parser.add_argument('--db-password', default='114514', help='数据库密码')
    parser.add_argument('--db-name', default='voter_database', help='数据库名称')
    parser.add_argument('--key-size', type=int, default=2048, help='RSA密钥大小')
    return parser.parse_args()


def generate_rsa_keys(key_size):
    """生成RSA密钥对"""
    print(f"Generating {key_size} bit RSA key pair...")
    key = RSA.generate(key_size)
    
    # 保存私钥
    with open("private.pem", "wb") as f:
        f.write(key.export_key())
    print("Private key saved at private.pem")
    
    # 保存公钥
    with open("public.pem", "wb") as f:
        f.write(key.publickey().export_key())
    print("Public key saved at public.pem")


def init_database(db_config):
    """初始化数据库表结构"""
    print(f"Connecting to DB {db_config['host']}...")
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        
        # 创建数据库（如果不存在）
        print(f"Creating DB {db_config['db']}...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['db']}")
        cursor.execute(f"USE {db_config['db']}")
        
        # 创建账户池表
        print("Creating blockchain account pool...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS account_pool (
            id INT AUTO_INCREMENT PRIMARY KEY,
            address VARCHAR(100) NOT NULL,
            is_assigned BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 创建已分配账户表
        print("Creating assigned account table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assigned_accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_hash VARCHAR(64) NOT NULL,
            account_id INT NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES account_pool(id),
            UNIQUE (user_hash)
        )
        """)
        
        # 创建已使用签名表（使用 SHA-256 哈希）
        print("Creating used signature table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS used_signatures (
            id INT AUTO_INCREMENT PRIMARY KEY,
            signature TEXT NOT NULL,
            signature_hash CHAR(64) NOT NULL,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (signature_hash)
        )
        """)
        
        # 提交更改
        conn.commit()
        print("DB initialization completed!")
        
        # 检查是否需要添加测试账户
        cursor.execute("SELECT COUNT(*) FROM account_pool")
        account_count = cursor.fetchone()[0]
        
        if account_count == 0:
            add_test_accounts = input("Add testing accounts to accout pool?(y/n): ").lower()
            if add_test_accounts == 'y':
                num_accounts = int(input("Number of test accounts to add: "))
                print(f"Adding {num_accounts} test accounts...")
                
                for i in range(num_accounts):
                    address = create_account(fund=True)[1]
                    cursor.execute(
                        "INSERT INTO account_pool (address, is_assigned) VALUES (%s, FALSE)",
                        (address,)
                    )
                
                conn.commit()
                print("Test accounts added to account pool!")
        
    except Exception as e:
        print(f"DB initialization failed: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


def main():
    """主函数"""
    args = parse_args()
    
    # 数据库配置
    db_config = {
        'host': args.db_host,
        'user': args.db_user,
        'password': args.db_password,
        'db': args.db_name
    }
    
    # 生成RSA密钥对
    generate_rsa_keys(args.key_size)
    
    # 初始化数据库
    init_database(db_config)
    
    print("\nInitialization complete! System ready")
    print("\nCommand to launch server:")
    print("python server.py")
    print("\nCommand to request account:")
    print('python assign_user_complete.py --id "123456789012345678" --name "张三"')


if __name__ == "__main__":
    main()
