from fastapi import FastAPI
from pydantic import BaseModel
import jwt, time
from fastapi.responses import JSONResponse
from core.db_items import *
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

jwt_secret_users = "acaipgizlisifre"
limiter = Limiter(key_func=get_remote_address)
admin = FastAPI()
admin.state.limiter = limiter
admin.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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
@limiter.limit("5/minute")
async def add_book(book: books,request: Request):
    try:
        ts = time.time()
        q = {
            "book_name": book.book_name.capitalize(),
            "author": book.author.capitalize(),
            "number_of_page": book.number_of_page,
            "kind": book.kind,
            "price": book.price,
            "new_price":0,
            "number_of_sell":book.number_of_sell,
            "amount_of_stock":book.amount_of_stock,
            "amount_of_discount":None,
            "timestamp":ts
        }
        book_col.insert_one(q)
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )

@admin.post("/make/discount/")
@limiter.limit("5/minute")
async def make_discount(book_name:str, discount_ratio:int,request: Request):
    try:
        data = book_col.find_one({"book_name": book_name})
        temp=data["price"]
        new_temp=(temp*discount_ratio)/100
        new_temp=temp-new_temp
        book_col.update({"book_name": book_name}, {"$set": {"new_price": new_temp}})
        book_col.update({"book_name": book_name}, {"$set": {"amount_of_discount": discount_ratio}})
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )

@admin.post("/remove/discount/")
@limiter.limit("5/minute")
async def remove_discount(book_name:str,request: Request):
    try:
        data = book_col.find_one({"book_name": book_name})
        book_col.update({"book_name": book_name}, {"$set": {"amount_of_discount": 0}})
        book_col.update({"book_name": book_name}, {"$set": {"new_price": 0}})
        return {"status": "succes"}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )


@admin.put("/update/book/name")
@limiter.limit("5/minute")
async def update_book_name(book_name:str,update: update_data,request: Request):
    try:
        if(book_col.find_one({"book_name": book_name})!=None):
            book_col.update_one({"book_name": book_name}, {"$set": {"book_name": update.data.capitalize()}}
            )
            return {"status": "success"} 
        else:
            return {"failed": "Book could not found."}
            
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )

@admin.put("/update/author/name")
@limiter.limit("5/minute")
async def update_author_name(book_name:str,update: update_data,request: Request):
    try:
        if(book_col.find_one({"book_name": book_name})!=None):
            book_col.update_one(
            {"book_name": book_name}, {"$set": {"author": update.data.capitalize()}}
            )
            return {"status": "success"}
        else:
             return {"failed": "Book could not found."}
           
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )

@admin.get("/get/book/list")
@limiter.limit("5/minute")
async def get_book_list(request: Request):
    try:
        temp2=[]
        temp=book_col.find({})
        for x in temp:
            if(x.get("new_price")!=0):
                q = {
                "book_name": x.get("book_name"),
                "author":x.get("author"),
                "kind": x.get("kind"),
                "amount_of_stock":x.get("amount_of_stock"),
                "number_of_page": x.get("number_of_page"),
                "number_of_sell": x.get("number_of_sell"),
                "price": x.get("price"),
                "amount_of_discount" + " %" :  x.get("amount_of_discount"),
                "new_price": x.get("new_price")}
                temp2.append(q)
            else:
                b = {
                "book_name": x.get("book_name"),
                "author":x.get("author"),
                "kind": x.get("kind"),
                "amount_of_stock":x.get("amount_of_stock"),
                "number_of_page": x.get("number_of_page"),
                "number_of_sell": x.get("number_of_sell"),
                "amount_of_discount" + " %" :  x.get("amount_of_discount"),
                "price": x.get("price")}
                temp2.append(b)
        return {"status": "success", "list": temp2}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )

@admin.put("/update/number/of/page")
@limiter.limit("5/minute")
async def update_number_of_page(book_name:str,update: update_data,request: Request):
    try:
        if(book_col.find_one({"book_name": book_name})!=None):
            book_col.update_one(
            {"book_name": book_name}, {"$set": {"number_of_page": int(update.data)}}
            )
            return {"status": "success"}
        else: 
            return {"failed": "Book could not found."}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.put("/update/kind/of/book")
@limiter.limit("5/minute")
async def update_kind(book_name:str,update: update_data,request: Request):
    try:
        if(book_col.find_one({"book_name": book_name})!=None):
            book_col.update_one(
            {"book_name": book_name}, {"$set": {"kind": update.data}}
            )
            return {"status": "success"}
           
        else:
            return {"failed": "Book could not found."}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.put("/update/price/of/book")
@limiter.limit("5/minute")
async def uptade_price_of_book(book_name:str,update: update_data,request: Request):
    try:
        if(book_col.find_one({"book_name": book_name})!=None):
            book_col.update_one(
            {"book_name": book_name}, {"$set": {"price": int(update.data)}}
            )
            return {"status": "success"}
        else:
            return {"failed": "Book could not found."}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.put("/update/number/of/sell")
@limiter.limit("5/minute")
async def uptade_number_of_sell(book_name:str,update: update_data,request: Request):
    try:
        if(book_col.find_one({"book_name": book_name})!=None):
            book_col.update_one(
            {"book_name": book_name}, {"$set": {"number_of_sell": int(update.data)}}
            )
            return {"status": "success"}
        else:
            return {"failed": "Book could not found."}
           
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.put("/update/amount/of/stock")
@limiter.limit("5/minute")
async def uptade_amount_of_stock(book_name:str,update: update_data,request: Request):
    try:
        if(book_col.find_one({"book_name": book_name})!=None):
            book_col.update_one(
            {"book_name": book_name}, {"$set": {"amount_of_stock": int(update.data)}}
            )
            return {"status": "success"}
        else:
            return {"failed": "Book could not found."}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@admin.delete("/delete/book")
@limiter.limit("5/minute")
async def delete_book(update:update_data,request: Request):
    try:
        q={"book_name": update.data}
        if(book_col.remove(q)):
            return {"status": "success"}
        else:    
            return {"failed": "Book could not found."}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
