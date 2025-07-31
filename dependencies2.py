from fastapi import FastAPI, HTTPException, status, Depends
from routes import admins_router, users_router
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeTimedSerializer, BadSignature
import hashlib
import bson
from bson import ObjectId
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# import serializer
SECRET_KEY = "sdsfe45456@21!!"
serializer = URLSafeTimedSerializer(SECRET_KEY)

# client = AsyncIOMotorClient("mongodb://localhost:27017")

# MongoDB setup
# MongoDB setup
# Get MongoDB credentials from environment variables
def get_env_or_fail(var):
    value = os.getenv(var)
    if value is None:
        raise RuntimeError(f"Environment variable {var} is not set!")
    return value

username = quote_plus(get_env_or_fail("MONGODB_USERNAME"))
password = quote_plus(get_env_or_fail("MONGODB_PASSWORD"))
cluster = get_env_or_fail("MONGODB_CLUSTER")
database = os.getenv("MONGODB_DATABASE")

# Construct MongoDB connection string
MONGODB_URL = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority"

client = AsyncIOMotorClient(MONGODB_URL)

db = client.Voyage_Vista

async def get_current_user(request: Request) -> tuple:
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return None,"0"
    try:
        data = serializer.loads(session_cookie)
    except BadSignature:
        return None,"0"
    
    value = data.get("value")
    
    if value == "0":
        user = await db.users.find_one({"_id": ObjectId(data.get("user_id"))})
    elif value =="1":
        user = await db.admins.find_one({"_id": ObjectId(data.get("user_id"))})

    # print(user,value)

    if not user:
        return None,"0"
    
    return user,value

