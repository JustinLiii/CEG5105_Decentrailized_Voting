"""
RSA盲签名算法实现

该模块提供了基于RSA算法的盲签名实现，包括：
- 盲化消息
- 签名盲化消息
- 解盲签名
- 验证签名
"""

import random
from typing import Tuple


class RSAPublicNumbers:
    """RSA公钥参数"""
    
    def __init__(self, n: int, e: int):
        """
        初始化RSA公钥参数
        
        Args:
            n: RSA模数
            e: 公钥指数
        """
        self.n = n
        self.e = e


class RSAPrivateNumbers:
    """RSA私钥参数"""
    
    def __init__(self, p: int, q: int, d: int):
        """
        初始化RSA私钥参数
        
        Args:
            p: 第一个素数
            q: 第二个素数
            d: 私钥指数
        """
        self.p = p
        self.q = q
        self.d = d
        self.n = p * q


def blind(public_numbers: RSAPublicNumbers, message: int) -> Tuple[int, int]:
    """
    对消息进行盲化处理
    
    Args:
        public_numbers: RSA公钥参数
        message: 要盲化的消息（整数形式）
    
    Returns:
        盲化后的消息和盲因子r的元组
    """
    # 生成随机盲因子r，确保与n互质
    n = public_numbers.n
    while True:
        r = random.randint(2, n-1)
        if gcd(r, n) == 1:
            break
    
    # 计算盲化消息: m' = m * r^e mod n
    blinded_message = (message * pow(r, public_numbers.e, n)) % n
    
    return blinded_message, r


def sign(private_numbers: RSAPrivateNumbers, blinded_message: int) -> int:
    """
    对盲化消息进行签名
    
    Args:
        private_numbers: RSA私钥参数
        blinded_message: 盲化后的消息
    
    Returns:
        对盲化消息的签名
    """
    # 计算签名: s' = (m')^d mod n
    return pow(blinded_message, private_numbers.d, private_numbers.n)


def unblind(public_numbers: RSAPublicNumbers, blinded_signature: int, r: int) -> int:
    """
    解盲签名
    
    Args:
        public_numbers: RSA公钥参数
        blinded_signature: 盲化消息的签名
        r: 盲因子
    
    Returns:
        解盲后的签名
    """
    # 计算 r 的模反元素
    r_inv = modinv(r, public_numbers.n)
    
    # 计算解盲签名: s = s' * r^(-1) mod n
    signature = (blinded_signature * r_inv) % public_numbers.n
    
    return signature


def verify(public_numbers: RSAPublicNumbers, message: int, signature: int) -> bool:
    """
    验证签名
    
    Args:
        public_numbers: RSA公钥参数
        message: 原始消息
        signature: 签名
    
    Returns:
        签名是否有效
    """
    # 验证: m == s^e mod n
    calculated = pow(signature, public_numbers.e, public_numbers.n)
    return calculated == message


def gcd(a: int, b: int) -> int:
    """
    计算最大公约数
    
    Args:
        a: 第一个整数
        b: 第二个整数
    
    Returns:
        a和b的最大公约数
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    扩展欧几里得算法，用于计算模反元素
    非递归实现，避免栈溢出
    
    Args:
        a: 第一个整数
        b: 第二个整数
    
    Returns:
        (gcd, x, y)，其中gcd是a和b的最大公约数，x和y满足ax + by = gcd
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    
    return old_r, old_s, old_t


def modinv(a: int, m: int) -> int:
    """
    计算模反元素
    
    Args:
        a: 要求反元素的整数
        m: 模数
    
    Returns:
        a在模m下的乘法逆元，即满足(a * x) % m = 1的x
    
    Raises:
        ValueError: 如果a和m不互质，则无法计算模反元素
    """
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("模反元素不存在")
    else:
        return x % m 