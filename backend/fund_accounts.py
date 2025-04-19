# import argparse
# import pymysql
from blockchain import fund_account, get_txn_gas, create_account

addr, sk = create_account()

fund_account(addr, 1)

# def parse_args():
#     """解析命令行参数"""
#     parser = argparse.ArgumentParser(description='匿名账户分配系统初始化工具')
#     parser.add_argument('--db-host', default='localhost', help='数据库主机地址')
#     parser.add_argument('--db-user', default='root', help='数据库用户名')
#     parser.add_argument('--db-password', default='114514', help='数据库密码')
#     parser.add_argument('--db-name', default='voter_database', help='数据库名称')
#     parser.add_argument('--key-size', type=int, default=2048, help='RSA密钥大小')
#     return parser.parse_args()

# args = parse_args()

# # 数据库配置
# db_config = {
#     'host': args.db_host,
#     'user': args.db_user,
#     'password': args.db_password,
#     'db': args.db_name
# }

# try:
#     # 连接数据库
#     conn = pymysql.connect(
#         host=db_config['host'],
#         user=db_config['user'],
#         password=db_config['password']
#     )
#     cursor = conn.cursor()
#     cursor.execute(f"USE {db_config['db']}")
    
#     cursor.execute("SELECT id, address FROM account_pool")
#     accounts = cursor.fetchall()
#     gas = get_txn_gas()
#     for account in accounts:
#         fund_account(account, gas)
# except Exception as e:
#     raise e
# finally:
#     cursor.close()
#     conn.close()