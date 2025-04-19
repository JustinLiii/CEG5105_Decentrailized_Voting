#!/usr/bin/env python3
# 用户端完整脚本
import blind_signature.rsa as blind_rsa
from Crypto.PublicKey import RSA
import hashlib
import json
import requests
import argparse
import sys

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='匿名账户分配系统 - 用户端')
    parser.add_argument('--id', required=True, help='用户身份证号')
    parser.add_argument('--name', required=True, help='用户姓名')
    parser.add_argument('--server', default='http://localhost:5000', help='服务器地址')
    parser.add_argument('--pubkey', default='public.pem', help='RSA公钥文件路径')
    return parser.parse_args()

def blind_sign_request(user_name, user_id, server_url):
    user_info = {
        "voter_id": user_id,
        "voter_name": user_name
    }
    """执行盲签名请求流程"""
    # 步骤1: 加载公钥
    public_key_path = "public.pem"
    try:
        with open(public_key_path, "rb") as f:
            pub_key = RSA.import_key(f.read())
        public_numbers = blind_rsa.RSAPublicNumbers(pub_key.n, pub_key.e)
    except Exception as e:
        print(f"无法加载公钥文件: {e}")
        sys.exit(1)
    
    # 步骤2: 对用户信息进行哈希处理
    user_hash = hashlib.sha256(json.dumps(user_info, sort_keys=True).encode()).hexdigest()
    message = int(user_hash, 16)
    
    # 步骤3: 盲化消息
    blinded_msg, r = blind_rsa.blind(public_numbers, message)
    
    # 步骤4: 向服务器请求盲签名

    response = requests.post(
        f"{server_url}/blind_sign",
        json={"blinded_message": str(blinded_msg)}
    )
    response.raise_for_status()
    data = response.json()
    blinded_signature = int(data['blind_signature'])

    
    # 步骤5: 解盲签名
    signature = blind_rsa.unblind(public_numbers, blinded_signature, r)
    
    # 步骤6: 验证签名
    is_valid = blind_rsa.verify(public_numbers, message, signature)
    if not is_valid:
        print("签名验证失败！")
        sys.exit(1)
    
    print("签名验证成功！")
    
    # 步骤7: 请求分配账户
    try: 
        print(f"message: {message}")
        print(f'str(message): {str(message)}')
        response = requests.post(
            f"{server_url}/assign_account",
            json={
                "user_hash": str(message),
                "signature": str(signature)
            }
        )
        response.raise_for_status()
        data = response.json()
        account_address = data['account_address']
        print(f"成功获取匿名账户: {account_address}")
        return account_address
    except Exception as e:
        print(f"请求分配账户失败: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"服务器返回: {e.response.text}")

def main():
    """主函数"""
    args = parse_args()
    
    # 构建用户信息
    user_info = {
        "id_number": args.id,
        "name": args.name
    }
    
    print(f"正在为用户 {args.name} 请求匿名账户...")
    account = blind_sign_request(args.name, args.id, args.server)
    
    # 保存到本地配置文件
    with open(f"{args.name}_account.json", "w") as f:
        json.dump({
            "account_address": account,
            "user_info_hash": hashlib.sha256(json.dumps(user_info, sort_keys=True).encode()).hexdigest()
        }, f, indent=2)
    
    print(f"账户信息已保存到 {args.name}_account.json")

if __name__ == "__main__":
    main()