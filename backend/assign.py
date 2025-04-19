import pymysql
import secrets
import hashlib
import json
from datetime import datetime

import blind_signature.rsa as blind_rsa
from Crypto.PublicKey import RSA

class AnonymousAccountAllocatorDB:
    def __init__(self, db_config, private_key_path, public_key_path):
        self.conn = pymysql.connect(**db_config)
        self.cursor = self.conn.cursor()

        # 加载 RSA 密钥
        with open(private_key_path, "rb") as f:
            self.private_key = RSA.import_key(f.read())
        with open(public_key_path, "rb") as f:
            self.public_key = RSA.import_key(f.read())

        self.private_numbers = blind_rsa.RSAPrivateNumbers(
            self.private_key.p, self.private_key.q, self.private_key.d
        )
        self.public_numbers = blind_rsa.RSAPublicNumbers(
            self.public_key.n, self.public_key.e
        )

    # def _hash_user_identity(self, user_info):
    #     """
    #     使用 SHA-256 对用户身份信息进行哈希处理（不可逆）。
    #     """
    #     user_str = json.dumps(user_info, sort_keys=True)
    #     return hashlib.sha256(user_str.encode()).hexdigest()

    def sign_blinded_identity(self, blinded_msg: int) -> int:
        """
        管理员对用户提交的盲化消息进行签名。
        """
        return blind_rsa.sign(self.private_numbers, blinded_msg)

    def verify_signature(self, user_hash: int, signature: int) -> bool:
        """
        验证用户提供的签名是否对其身份哈希有效。
        """
        return blind_rsa.verify(self.public_numbers, user_hash, signature)

    def is_signature_used(self, signature: int) -> bool:
        """
        检查签名是否已使用（防止重复领取）。
        """
        signature_hex = hex(signature)
        signature_hash = hashlib.sha256(signature_hex.encode()).hexdigest()
        self.cursor.execute("SELECT id FROM used_signatures WHERE signature_hash = %s", (signature_hash,))
        return self.cursor.fetchone() is not None

    def mark_signature_used(self, signature: int):
        """
        记录签名为已使用。
        """
        signature_hex = hex(signature)
        signature_hash = hashlib.sha256(signature_hex.encode()).hexdigest()
        self.cursor.execute(
            "INSERT INTO used_signatures (signature, signature_hash, used_at) VALUES (%s, %s, %s)",
            (signature_hex, signature_hash, datetime.utcnow())
        )
        self.conn.commit()

    def assign_account(self, user_hash: int, signature: int):
        """
        分配一个匿名账户，但前提是签名合法且未被使用。
        """
        user_hash_hex = f"{user_hash:x}"
        if not self.verify_signature(user_hash, signature):
            raise Exception("签名无效，无法分配账户。")

        if self.is_signature_used(signature):
            raise Exception("该签名已被使用，无法重复领取。")

        # 检查是否已分配过
        self.cursor.execute("SELECT account_id FROM assigned_accounts WHERE user_hash = %s", (user_hash_hex,))
        result = self.cursor.fetchone()
        if result:
            account_id = result[0]
            self.cursor.execute("SELECT address FROM account_pool WHERE id = %s", (account_id,))
            return self.cursor.fetchone()[0]

        # 获取所有未分配账户
        self.cursor.execute("SELECT id, address FROM account_pool WHERE is_assigned = FALSE")
        available_accounts = self.cursor.fetchall()

        if not available_accounts:
            raise Exception("No more accounts available.")

        # 混合用户哈希和加密随机数
        seed = user_hash ^ secrets.randbits(256)
        index = seed % len(available_accounts)

        selected_account = available_accounts[index]
        account_id, account_address = selected_account

        # 更新账户为已分配
        self.cursor.execute("UPDATE account_pool SET is_assigned = TRUE WHERE id = %s", (account_id,))
        # 插入分配记录
        self.cursor.execute(
            "INSERT INTO assigned_accounts (user_hash, account_id, assigned_at) VALUES (%s, %s, %s)",
            (user_hash_hex, account_id, datetime.utcnow())
        )

        # 记录签名为已使用
        self.mark_signature_used(signature)

        self.conn.commit()
        return account_address

    def close(self):
        self.cursor.close()
        self.conn.close()
