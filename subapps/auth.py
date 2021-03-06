from fastapi import FastAPI
from pydantic import BaseModel
import pymongo, bcrypt, jwt, time, re
from fastapi import Request
from fastapi.responses import JSONResponse
from core.db_items import *
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


jwt_secret_users = "acaipgizlisifre"
limiter = Limiter(key_func=get_remote_address)
auth = FastAPI()
auth.state.limiter = limiter
auth.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
def regexs(n):
    regex = ""
    if n == 0: 
        regex = r"^[a-zA-Z-ğĞöÖıİüÜçÇşŞ]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$"
    elif n == 1:  
        regex = r"^[a-zA-Z-ğĞöÖıİüÜçÇşŞ]+(([a-zA-Z0-9])?[a-zA-Z0-9]*)*$"
    return regex
class login(BaseModel):
    username: str
    password: str


class register(BaseModel):
    name: str
    surname: str
    username: str
    password: str

@auth.post("/login/")
@limiter.limit("5/minute")
async def login(user: login,request: Request):
    try:
        if(user.username.startswith("admin")):
            data = user_col.find_one({"username": user.username})
            bcrypt_pass = str.encode(user.password)
            hashed = data["password"]
            if bcrypt.checkpw(bcrypt_pass, hashed):
                ts = time.time()
                data = user_col.find_one({"username": user.username})
                token = jwt.encode(
                {"username": user.username, "timestamp": ts,"role": "admin"},
                jwt_secret_users,
                algorithm="HS256",
                )
            return {"status": "success", "token": token}
        else:
            data = user_col.find_one({"username": user.username})
            bcrypt_pass = str.encode(user.password)
            hashed = data["password"]
            if bcrypt.checkpw(bcrypt_pass, hashed):
                ts = time.time()
                data = user_col.find_one({"username": user.username})
                token = jwt.encode(
                    {"username": user.username,"timestamp": ts,"role": "user"},
                    jwt_secret_users,
                    algorithm="HS256",
                )
                return {"status": "success", "token": token}
            else:
                return {
                "status": "failed",
                "message": "Username or Password is wrong",
            }
    except:
        return JSONResponse(
            status_code=503,
            content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@auth.post("/register/")
@limiter.limit("5/minute")
def register(user: register,request: Request):
    try:
        if(len(user.password)<4):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "failed",
                    "message": "Password should be longer than 3 characters",
                },
            )
        else:
            bcrypt_pass = str.encode(user.password)
            hashed = bcrypt.hashpw(bcrypt_pass, bcrypt.gensalt())
            check = {"username": user.username}
       
        if not re.match(regexs(0), user.name):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "failed",
                    "message": "Name can not contain numbers or symbols",
                },
            )
        elif not re.match(regexs(0), user.surname):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "failed",
                    "message": "Surname can not contain numbers or symbols",
                },
            )
        elif not re.match(regexs(1), user.username):
            return JSONResponse(
                status_code=400,
                content={"status": "failed", "message": "Username format is wrong!"},
            )
        elif len(user.username) < 4 or len(user.username) > 11:
            return JSONResponse(
                status_code=400,
                content={
                    "status ": "failed",
                    "message": "length of username must be between 4 and 11",
                },
            )
        if user_col.count_documents(check):
            return JSONResponse(
                status_code=400,
                content={"status": "failed", "message": "This username taken before!"},
            )
        if (user.username.startswith("admin")):
            ts = time.time()
            q = {
            "password": hashed,
            "name": user.name.capitalize(),
            "surname": user.surname.capitalize(),
            "username": user.username,
            "timestamp": ts,
            }
            user_col.insert_one(q)
            token = jwt.encode(
                {"username": user.username, "timestamp": ts,"role": "admin"},
                jwt_secret_users,
                algorithm="HS256",
            )
            return {"status": "success", "token": token}
        else:
            ts = time.time()
            q = {
            "password": hashed,
            "name": user.name.capitalize(),
            "surname": user.surname.capitalize(),
            "username": user.username,
            "timestamp": ts,
            "book_list": []
            }
            user_col.insert_one(q)
            token = jwt.encode(
            {"username": user.username, "timestamp": ts, "role": "user"},
            jwt_secret_users,
            algorithm="HS256",
            )
            return {"status": "success", "token": token}
    except:
        return JSONResponse(
            status_code=503,
            content={
                "status": "failed",
                "message": "Database error!",
            },
        )
