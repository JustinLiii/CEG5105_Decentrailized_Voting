#!/usr/bin/env python3
"""
匿名账户分配系统 - 服务器端
"""
import logging
import os
from contextlib import asynccontextmanager

import jwt
from assign import AnonymousAccountAllocatorDB
from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Loading the environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '114514'),
    'db': os.environ.get('DB_NAME', 'voter_database'),
}

# 密钥文件路径
PRIVATE_KEY_PATH = os.environ.get('PRIVATE_KEY_PATH', 'private.pem')
PUBLIC_KEY_PATH = os.environ.get('PUBLIC_KEY_PATH', 'public.pem')

# 全局账户分配器实例
allocator = None
        
@asynccontextmanager
async def lifespan(app: FastAPI):
    """初始化账户分配器"""
    global allocator
    try:
        allocator = AnonymousAccountAllocatorDB(
            DB_CONFIG,
            PRIVATE_KEY_PATH,
            PUBLIC_KEY_PATH
        )
    except Exception as e:
        logger.error(f"初始化账户分配器失败: {e}")
    yield


app = FastAPI(lifespan=lifespan)

# Define the allowed origins for CORS
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInfo(BaseModel):
    voter_id: str
    voter_name: str
    
async def authenticate(user_info: UserInfo):
    # should be replaced with actual voter authentication logic
    # if cannot authenticate
    # raise HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Forbidden"
    # )
    pass

async def get_role(voter_id):
    if voter_id == 'admin':
        return 'admin'
    else:
        return 'user'

# Define the POST endpoint for login
@app.post("/login")
async def login(user_info: UserInfo, response: Response):
    await authenticate(user_info)
    role = await get_role(user_info.voter_id)

    # Assuming authentication is successful, generate a token
    token = jwt.encode({'voter_name': user_info.voter_name, 'voter_id': user_info.voter_id, 'role': role}, os.environ['SECRET_KEY'], algorithm='HS256')
    
    # 设置 cookie：将 token 放入 HttpOnly + Secure Cookie + samesite="Lax"
    # Set cookie: HttpOnly + Secure Cookie + samesite="Lax"
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return {'token': token, 'role': role}

class BlindMessage(BaseModel):
    """盲签名请求模型"""
    blinded_message: str
@app.post('/blind_sign')
def blind_sign(data: BlindMessage):
    """处理盲签名请求"""
    if not allocator:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器未正确初始化"
        )

    try:
        blinded_message = int(data.blinded_message)
        blind_signature = allocator.sign_blinded_identity(blinded_message)
        return {'blind_signature': str(blind_signature)}
    except Exception as e:
        logger.error(f"盲签名失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理请求失败: {str(e)}"
        )
        
@app.get("/protected")
async def protected_route(access_token: str = Cookie(None)):
    payload = jwt.decode(access_token, os.environ["SECRET_KEY"], algorithms=["HS256"])
    return {"message": "Welcome!", "user": payload}

class SignedUserInfo(BaseModel):
    user_hash: str
    signature: str
@app.post('/assign_account')
def assign_account(data: SignedUserInfo):
    print(f"received message: {data.user_hash}")
    """处理账户分配请求"""
    if not allocator:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器未正确初始化"
        )

    user_hash = int(data.user_hash)
    signature = int(data.signature)
    # 分配账户
    account_address = allocator.assign_account(user_hash, signature)
    return {'account_address': account_address}

@app.get('/public.pem')
def give_public_key():
    with open('public.pem', 'rb') as f:
        public_key = f.read()
    return Response(content=public_key, media_type='application/x-pem-file')

@app.get('/deployed.json')
def give_contract_info():
    with open('deployed.json', 'r') as f:
        contract_info = f.read()
    return Response(content=contract_info, media_type='application/json')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)