from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import motor
from pydantic import BaseModel
import hashlib
import os
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi import Form, Request
from fastapi.templating import Jinja2Templates
import pydantic
import bson
from bson import ObjectId
from dependencies import get_current_user
from datetime import date, datetime



router = APIRouter()


# Get the directory path of the current script (routes/users_router.py)
# current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the templates directory
# templates = os.path.join(current_dir, '..', 'templates')

templates = Jinja2Templates(directory="templates")
# print(templates)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db(request: Request):
    return request.app.mongodb

def get_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Pydantic models
class User(BaseModel):
    username: str
    password: str

class UserInDB(User):
    hashed_password: str

# Helper functions
async def verify_password(plain_password, hashed_password):
    return get_password_hash(plain_password) == hashed_password

async def authenticate_user(username: str, password: str, db = Depends(get_db)):    
    users_collection = db.users
    user = await users_collection.find_one({"username": username})
    if user and await verify_password(password, user['hashed_password']):
        return user
    return None


@router.post("/package-choosen")
async def add_user_package(request: Request, destination: str = Form(...), number_of_guests: int = Form(...), 
                           arrival_date: date = Form(...), leaving_date: date = Form(...), db=Depends(get_db), user1=Depends(get_current_user)):
    user = user1[0]
    value = user1[1]

    if value == "0":
        
        users_collection = db.user_package    
        
        user_id = user["_id"]
        print(user_id)
        
        user_package = {
            "user_id": ObjectId(user_id),
            "destination": destination,
            "number_of_guests": number_of_guests,
            "arrival_date": arrival_date,
            "leaving_date": leaving_date
        }

        print(user_package)
            
        # Insert the new user into the database
        try:    
            await users_collection.insert_one({"user_id": ObjectId(user_id),"destination": destination,
                "number_of_guests": number_of_guests,"arrival_date": str(arrival_date),"leaving_date": str(leaving_date)})
        except Exception as e:
            print(e)


        # Return the user_management.html template with all users
        # data_package = await db.admin_package.find().to_list(length=None)
        # data_review = await db.users_reviews.find().to_list(length=None)

        # message = f"Your Packae has been added"

        # return templates.TemplateResponse("index.html", {"request": request,"message": message ,"display_table": True, "admin_packages": data_package, "users_reviews":data_review})
        return templates.TemplateResponse("congratulation.html", {"request": request},status_code=201)
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    



@router.get("/view-packages", response_class=HTMLResponse)
async def view_packages_page(request: Request, db=Depends(get_db), user1=Depends(get_current_user)):
    
    user = user1[0]
    value = user1[1]

    if value == "0":
        users_collection = db.user_package

        user_id = user["_id"]
        print(user_id)


        # Check if the username is already registered
        existing_user = await users_collection.find_one({"user_id": ObjectId(user_id)})
        print(existing_user)

        if not existing_user:
            return templates.TemplateResponse("show_packages.html", 
                                            {"request": request, "error_message": "No packages have been choosen yet"},status_code=400)   
            

        # Fetch all users from the database
        data = await users_collection.find({"user_id": ObjectId(user_id)}).to_list(length=None)

        print(data,"This is the data")

        # Return the user_management.html template with all users
        return templates.TemplateResponse("show_packages.html", 
                                    {"request": request, "display_table": True, "packages": data},
                                    status_code=201)
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)




@router.post("/packages/update/{package_id}")
async def update_package(request: Request, package_id:str, destination: str = Form(...), number_of_guests: str = Form(...), 
                         arrival_date: date = Form(...), leaving_date: date = Form(...), db=Depends(get_db), user1=Depends(get_current_user)):

    user = user1[0]
    value = user1[1]

    if value == "0":
        user_id = user["_id"]


        # Find the user by user_id
        user = await db.user_package.find_one({"user_id": ObjectId(user_id)})

        if not user:
            return templates.TemplateResponse("show_packages.html", 
                                            {"request": request, "error_message": "User id not found"},
                                            status_code=400)
        
        # Update the username
        await db.user_package.update_one({"_id": ObjectId(package_id)}, {"$set": {"destination": destination,"number_of_guests": number_of_guests,
                                                                                "arrival_date": str(arrival_date),"leaving_date": str(leaving_date)}})

        # Fetch all users from the database
        packages = await db.user_package.find({"user_id": ObjectId(user_id)}).to_list(length=None)

        # Render the user management page with the success message
        success_message = f"User with ID {user_id} updated successfully"

        return templates.TemplateResponse("show_packages.html", 
                                    {"request": request, "display_table": True, "packages": packages,  "success_message": success_message},
                                    status_code=201)

    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    


@router.get("/packages/update/{package_id}")
async def update_page(request: Request, package_id:str, db=Depends(get_db), user1=Depends(get_current_user)):


    user = user1[0]
    value = user1[1]

    if value == "0":
        # Fetch user data by ID
        package = await db.user_package.find_one({"_id": ObjectId(package_id)})

        if package is None:
            # If user not found, redirect with error message
            return templates.TemplateResponse("update_user.html", 
                                            {"request": request, "error_message": f"Package in sot found"},
                                            status_code=400)
    
        return templates.TemplateResponse("update_user.html", {"request": request, "display_table": True, "package": package})
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    

    
@router.post("/packages/delete/{package_id}")
async def delete_package(request: Request, package_id:str, db=Depends(get_db), user1 = Depends(get_current_user)):
    
    user = user1[0]
    value = user1[1]

    if value == "0":
        user_id = user["_id"]

        # Find the user by user_id
        user = await db.user_package.find_one({"user_id": ObjectId(user_id)})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete the user
        await db.user_package.delete_one({"_id": ObjectId(package_id)})    

        # success_message = f"User {user_id} with package of id {package_id} is deleted deleted successfully" 
        
        data = await db.user_package.find({"user_id": ObjectId(user_id)}).to_list(length=None)

        if data is None:
            # If user not found, redirect with error message
            return templates.TemplateResponse("show_packages.html", 
                                            {"request": request, "error_message": "No users found"},
                                            status_code=400)
        
        response = RedirectResponse(url="/users/view-packages", status_code=status.HTTP_303_SEE_OTHER,)

        return response
    


@router.post("/add-review", response_class=HTMLResponse)
async def add_user_review(request: Request, review_of_customer: str = Form(...), stars: str = Form(...), db=Depends(get_db), user1=Depends(get_current_user)):

    user = user1[0]
    value = user1[1]

    if value == "0":
        users_review_collection = db.users_reviews
        users_collection = db.users

        existing_user = await users_collection.find_one({"_id": user["_id"]})

        profile_image = "profile icon.png"

        username = user["username"]

        if not existing_user:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Username not registered"}, status_code=400)
        
        await users_review_collection.insert_one({"name": username, "profile_image": profile_image,"comment": review_of_customer, "stars":int(stars)})
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)



@router.post("/update")
async def update_user_Profile(request: Request, username: str = Form(...), db=Depends(get_db), user1=Depends(get_current_user)):

    user = user1[0]
    value = user1[1]

    if value == "0":
        user_id = user["_id"]

        # Find the user by user_id
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return templates.TemplateResponse("update_Profile.html", 
                                            {"request": request, "error_message": "Username not found"},
                                            status_code=400)
        
        # Update the username
        await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": username}})

        # Fetch all users from the database
        users_cursor = db.users.find()
        users = await users_cursor.to_list(length=100)  # Adjust length as needed

        # Render the user management page with the success message
        success_message = f"User with ID {user_id} updated successfully"
        
        return templates.TemplateResponse("index.html", 
                                        {"request": request, "users": users, "display_table": True, "success_message": success_message})
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    


@router.get("/update")
async def update_user_Profile_page(request: Request, db=Depends(get_db), user1=Depends(get_current_user)):

    user = user1[0]
    value = user1[1]

    if value == "0":
        user_id = user["_id"]
        # Fetch user data by ID
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            # If user not found, redirect with error message
            return templates.TemplateResponse("update_Profile.html", 
                                            {"request": request, "error_message": "Username not found"},
                                            status_code=400)
        
        return templates.TemplateResponse("update_Profile.html", {"request": request, "display_table": True, "user": user})
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    

    


@router.post("/delete")
async def delete_user_Profile(request: Request, db=Depends(get_db), user1=Depends(get_current_user)):

    user = user1[0]
    value = user1[1]

    if value == "0":
        user_id = user["_id"]

        # Find the user by user_id
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Delete the user
        await db.users.delete_one({"_id": ObjectId(user_id)})    
        success_message = f"User with Username {user["username"]} deleted successfully"    
        # Fetch all users from the database    
        users = await db.users.find().to_list(length=None)
        if users is None:
            # If user not found, redirect with error message
            return templates.TemplateResponse("update_Profile.html", 
                                            {"request": request, "error_message": "No users found"},
                                            status_code=400)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    
    
   