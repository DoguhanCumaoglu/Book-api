from urllib import request
from fastapi import FastAPI
from pydantic import BaseModel
import pymongo, bcrypt, jwt, time, re
from fastapi.responses import JSONResponse
from core.db_items import *
from fastapi import Request

jwt_secret_users = "acaipgizlisifre"
admin = FastAPI()


class books(BaseModel):
    book_name: str
    author: str
    number_of_page: int
    kind: str
    price:int
    number_of_sell:int


@admin.middleware("http")
async def admin_middleware(request: Request, call_next):
    headers = request.headers
    if "Authorization" in headers:
        token = request.headers["Authorization"]
        try:
            data = jwt.decode(token, jwt_secret_users, algorithms=["HS256"])
            request.state.username = data["username"]
            request.state.role=data["role"]
            if(request.state.role!="admin"):
                 return JSONResponse(status_code=403)
        except:
            return JSONResponse(status_code=403)
    else:
        return JSONResponse(status_code=403)

    response = await call_next(request)
    return response


@admin.post("/add/book/")
async def add_book(book: books):
    try:
        ts = time.time()
        q = {
            "book_name": book.book_name.capitalize(),
            "author": book.author.capitalize(),
            "number_of_page": book.number_of_page,
            "kind": book.kind,
            "price": book.price,
            "number_of_sell":book.number_of_sell,
            "timestamp":ts
        }
        book_col.insert_one(q)
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
