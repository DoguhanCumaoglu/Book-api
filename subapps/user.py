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
user = FastAPI()
user.state.limiter = limiter
user.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@user.middleware("http")
async def user_middleware(request: Request, call_next):
    headers = request.headers
    if "Authorization" in headers:
        token = request.headers["Authorization"]
        try:
            data = jwt.decode(token, jwt_secret_users, algorithms=["HS256"])
            request.state.username = data["username"]
            request.state.role=data["role"]
        except:
            return JSONResponse(status_code=403)
    else:
        return JSONResponse(status_code=403)

    response = await call_next(request)
    return response



@user.post("/recomend/book/")
@limiter.limit("5/minute")
async def recomend_book(book_kind:str,request: Request):
    try:
        test=[]
        for x in book_col.find({"kind":book_kind }).sort("number_of_sell"):
            q = {
                "book_name": x.get("book_name"),
                "author":x.get("author"),
                "number_of_page": x.get("number_of_page"),
                "number_of_sell": x.get("number_of_sell"),
                "price": x.get("price")}
            test.append(q)
        print(test[-5:])
        newlist = sorted(test[-5:], key=lambda d: d['price']) 
        print(newlist[-5:])
        return {"status": "success", "list": newlist[-5:]}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )

@user.get("/recomend/discount/book/")
@limiter.limit("5/minute")
async def recomend_discount_book(request: Request):
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
        if(len(temp2)==0):
            return {"status": "failed", "message": "No books in discount"}
        else:
             return {"status": "success", "list": temp2}

    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@user.get("/get/book/list")
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
@user.post("/buy/book/")
@limiter.limit("5/minute")
async def buy_book(book_name:str,request: Request):
    try:
        data=book_col.find_one({"book_name":book_name})
        user_col.update_one(
                {"username": request.state.username},
                {"$addToSet": {"book_list": data["book_name"]}},
            )
        return {"status": "success"}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )
@user.get("/check/your/shoplist")
@limiter.limit("5/minute")
async def check_your_shoplist(request: Request):
    try:
        data=user_col.find_one({"username":request.state.username })
        your_list=[]
        total=0
        for i in range(len(data["book_list"])):
            data2=book_col.find_one({"book_name":str(data["book_list"][i])})
            q={
            "book_name":data2["book_name"],
            "author":data2["author"],
            "kind": data2["kind"],
            }
            total=total+data2["price"]
            your_list.append(q)
        return {"status": "success", "list": your_list,"price":total}
    except:
        return JSONResponse(
                status_code=503,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )

