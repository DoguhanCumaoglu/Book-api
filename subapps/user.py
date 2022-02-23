from fastapi import FastAPI
from pydantic import BaseModel
import jwt, time
from fastapi.responses import JSONResponse
from core.db_items import *
from fastapi import Request

jwt_secret_users = "acaipgizlisifre"
user = FastAPI()


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
async def recomend_book(book_kind:str):
    try:
        test=[]
        for x in book_col.find({"kind":book_kind }).sort("number_of_sell"):
             q = {
                "book_name": x.get("book_name"),
                "number_of_sell": x.get("number_of_sell"),
                "price": x.get("price")}
            
             test.append(q) 
        print(test[-5:])
       
    
        return {"status": test}
    except:
        return JSONResponse(
                status_code=400,
                content={
                "status": "failed",
                "message": "Database error!",
            },
        )