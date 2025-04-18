# Import required modules 
import os

import jwt
from dotenv import load_dotenv
# import mysql.connector
from fastapi import FastAPI, HTTPException, Request, status, Response, Cookie
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

# Loading the environment variables
load_dotenv()

# Initialize the todoapi app
app = FastAPI()

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

# Connect to the MySQL database
# try:
#     cnx = mysql.connector.connect(
#         user=os.environ['MYSQL_USER'],
#         password=os.environ['MYSQL_PASSWORD'],
#         host=os.environ['MYSQL_HOST'],
#         database=os.environ['MYSQL_DB'],
#     )
#     cursor = cnx.cursor()
# except mysql.connector.Error as err:
#     if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#         print("Something is wrong with your user name or password")
#     elif err.errno == errorcode.ER_BAD_DB_ERROR:
#         print("Database does not exist")
#     else:
#         print(err)

# Define the authentication middleware
async def authenticate(request: Request):
    pass
    # try:
    #     api_key = request.headers.get('authorization').replace("Bearer ", "")
    #     cursor.execute("SELECT * FROM voters WHERE voter_id = %s", (api_key,))
    #     if api_key not in [row[0] for row in cursor.fetchall()]:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Forbidden"
    #         )
    # except:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Forbidden"
    #     )

# Define the POST endpoint for login
@app.get("/login")
async def login(request: Request, response: Response, voter_id: str, password: str):
    await authenticate(request)
    role = await get_role(voter_id, password)

    # Assuming authentication is successful, generate a token
    token = jwt.encode({'password': password, 'voter_id': voter_id, 'role': role}, os.environ['SECRET_KEY'], algorithm='HS256')
    
    # 设置 cookie：将 token 放入 HttpOnly + Secure Cookie + samesite="Lax"
    # Set cookie: HttpOnly + Secure Cookie + samesite="Lax"
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    
    return {'token': token, 'role': role}

@app.get("/protected")
async def protected_route(access_token: str = Cookie(None)):
    payload = jwt.decode(access_token, os.environ["SECRET_KEY"], algorithms=["HS256"])
    return {"message": "Welcome!", "user": payload}

# Replace 'admin' with the actual role based on authentication
async def get_role(voter_id, password):
    if voter_id == 'admin':
        return 'admin'
    else:
        return 'user'
    # try:
    #     cursor.execute("SELECT role FROM voters WHERE voter_id = %s AND password = %s", (voter_id, password,))
    #     role = cursor.fetchone()
    #     if role:
    #         return role[0]
    #     else:
    #         raise HTTPException(
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #             detail="Invalid voter id or password"
    #         )
    # except mysql.connector.Error as err:
    #     print(err)
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Database error"
    #     )
