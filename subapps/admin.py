from fastapi import FastAPI
from pydantic import BaseModel
import jwt, time
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
    amount_of_stock:int

class update_data(BaseModel):
    data: str



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
            "amount_of_stock":book.amount_of_stock,
            "timestamp":ts
        }
        book_col.insert_one(q)
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.post("/update/book/name")
async def update_book_name(book_name:str,update: update_data):
    try:
        book_col.update_one(
            {"book_name": book_name}, {"$set": {"book_name": update.data.capitalize()}}
        )
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )

@admin.post("/update/author/name")
async def update_author_name(book_name:str,update: update_data):
    try:
        book_col.update_one(
            {"book_name": book_name}, {"$set": {"author": update.data.capitalize()}}
        )
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )

@admin.post("/update/number/of/page")
async def update_number_of_page(book_name:str,update: update_data):
    try:
        book_col.update_one(
            {"book_name": book_name}, {"$set": {"number_of_page": int(update.data)}}
        )
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.post("/update/kind/of/book")
async def update_kind(book_name:str,update: update_data):
    try:
        book_col.update_one(
            {"book_name": book_name}, {"$set": {"kind": update.data}}
        )
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.post("/update/price/of/book")
async def uptade_price_of_book(book_name:str,update: update_data):
    try:
        book_col.update_one(
            {"book_name": book_name}, {"$set": {"price": int(update.data)}}
        )
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.post("/update/number/of/sell")
async def uptade_number_of_sell(book_name:str,update: update_data):
    try:
        book_col.update_one(
            {"book_name": book_name}, {"$set": {"number_of_sell": int(update.data)}}
        )
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.post("/update/amount/of/stock")
async def uptade_amount_of_stock(book_name:str,update: update_data):
    try:
        book_col.update_one(
            {"book_name": book_name}, {"$set": {"amount_of_stock": int(update.data)}}
        )
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.post("delete/book")
async def delete_book(update:update_data):
    try:
        q={'book_name': update.data}
        book_col.delete_one(q)
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
