from fastapi import FastAPI, HTTPException, status, Depends, Request, Form
from routes import admins_router, users_router
from motor.motor_asyncio import AsyncIOMotorClient
# from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeTimedSerializer, BadSignature
import hashlib
import bson
from bson import ObjectId
from dependencies import get_current_user
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Secret key for session management
SECRET_KEY = "sdsfe45456@21!!"
serializer = URLSafeTimedSerializer(SECRET_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This is for development only, specify actual domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()


app.include_router(users_router.router, tags=["User_Router"], prefix="/users")
app.include_router(admins_router.router, tags= ["Admin Router"] , prefix="/admins")


# Setup Jinja2Templates for HTML rendering
templates = Jinja2Templates(directory="templates")
# MongoDB setup
client = AsyncIOMotorClient("mongodb://localhost:27017")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = client
    app.mongodb = client.Voyage_Vista

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

def get_db(request: Request):
    return request.app.mongodb

# Index page route
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user1 = Depends(get_current_user), db = Depends(get_db)):

    user = user1[0]
    value = user1[1]


    if value == "0":
        if not user:
            return templates.TemplateResponse("login.html", {"request": request})
        
        data_package = await db.admin_package.find().to_list(length=None)
        data_review = await db.users_reviews.find().to_list(length=None)


        data_review_reverse = data_review[::-1][0:8]

        return templates.TemplateResponse("index.html", {"request": request, "display_table": True, "admin_packages": data_package, "users_reviews":data_review_reverse})
    
    elif value == "1":
        return templates.TemplateResponse("admin_index.html", {"request": request})


def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def require_login(user = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), themeValue: str = Form(...) ,db = Depends(get_db)):
    
    print(themeValue)
    

    if themeValue == "0":    
        user = await db.users.find_one({"username": username})
        if not user or user["hashed_password"] != get_password_hash(password):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    elif themeValue == "1":
        user = await db.admins.find_one({"username": username})
        if not user or user["hashed_password"] != get_password_hash(password):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # response = templates.TemplateResponse("index.html", {"request": request})

    session_data = {"user_id": str(user["_id"]), "value":themeValue}
    session_cookie = serializer.dumps(session_data)
    print(session_cookie)
    response.set_cookie("session", session_cookie)
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, username: str = Form(...), password: str = Form(...), db=Depends(get_db)):

    users_collection = db.users
    # Hash the password
    hashed_password = get_password_hash(password)
    # Check if the username is already registered
    existing_user = await users_collection.find_one({"username": username})

    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already registered"}, status_code=400)  
    
    await users_collection.insert_one({"username": username, "hashed_password": hashed_password})
    
    user = await db.users.find_one({"username": username})

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    session_data = {"user_id": str(user["_id"]), "value":"0"}
    session_cookie = serializer.dumps(session_data)
    response.set_cookie("session", session_cookie)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("session")
    return response

