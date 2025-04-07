# 用户端
import blind_signature.rsa as blind_rsa
from Crypto.PublicKey import RSA
import hashlib
import json

with open("public.pem", "rb") as f:
    pub_key = RSA.import_key(f.read())

public_numbers = blind_rsa.RSAPublicNumbers(pub_key.n, pub_key.e)

user_info = {
    "id_number": "123456789012345678",
    "name": "张三"
}
user_hash = hashlib.sha256(json.dumps(user_info, sort_keys=True).encode()).hexdigest()
message = int(user_hash, 16)

blinded_msg, r = blind_rsa.blind(public_numbers, message)

