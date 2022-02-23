import pymongo
from pymongo import MongoClient

db_url = "mongodb+srv://dodikral:dodi3312@cluster0.kkbju.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

client = pymongo.MongoClient(db_url)
db = "test"
user_col = client[db]["user"]
book_col = client[db]["book"]

