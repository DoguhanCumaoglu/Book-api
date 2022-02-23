from fastapi import FastAPI
from subapps.auth import auth
from subapps.admin import admin
from subapps.user import user
from fastapi.middleware.cors import CORSMiddleware
import pymongo
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/auth", auth)
app.mount("/admin", admin)
app.mount("/user", user)

@app.get("/")
def root():
    return {"message": "alive"}