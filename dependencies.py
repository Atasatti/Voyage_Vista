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

# import serializer
SECRET_KEY = "sdsfe45456@21!!"
serializer = URLSafeTimedSerializer(SECRET_KEY)

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.Voyage_Vista

async def get_current_user(request: Request) -> tuple:
    session_cookie = request.cookies.get("session")

    if not session_cookie:
        return (None,"0")
    try:
        data = serializer.loads(session_cookie)
    except BadSignature:
        return (None,"0")
    
    value = data.get("value")
    
    if value == "0":
        user = await db.users.find_one({"_id": ObjectId(data.get("user_id"))})
    elif value =="1":
        user = await db.admins.find_one({"_id": ObjectId(data.get("user_id"))})


    if not user:
        return (None,"0")
    
    return user,value

