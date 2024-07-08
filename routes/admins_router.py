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
from dependencies2 import get_current_user
from datetime import date

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


@router.get("/show-packages")
async def admin_management(request: Request, user1 = Depends(get_current_user), db=Depends(get_db)):

    user = user1[0]
    value = user1[1]

    if value == "1":
        if user:
            package_collection = db.admin_package
            packages = await package_collection.find().to_list(length=None)

            return templates.TemplateResponse("show_admin_packages.html", {"request": request, "display_table": bool(packages), "packages": packages})
        return RedirectResponse("/login")
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)


    



@router.post("/update-Package/{package_id}")
async def update_admin(request: Request, package_id: str, image_path: str = Form(...),
                        destination_name: str = Form(...), guest_allowed: int= Form(...), description: str= Form(...), 
                        discounted_price:int = Form(...) ,original_price: int = Form(...), stars:int = Form(...), db=Depends(get_db), user1 = Depends(get_current_user)):

    # image_path,destination_name,guest_allowed,description,discounted_price,original_price,stars



    user = user1[0]
    value = user1[1]

    if value == "1":
        
        # Find the user by user_id
        package = await db.admin_package.find_one({"_id": ObjectId(package_id)})

        if not package:
            return templates.TemplateResponse("show_admin_packages.html", 
                                            {"request": request, "error_message": "Package not found"},
                                            status_code=400)
        
        # Update the username
        await db.admin_package.update_one({"_id": ObjectId(package_id)}, 
                                        {"$set": {
                                                    "image_path": image_path,
                                                    "destination_name": destination_name,
                                                    "guest_allowed": guest_allowed,
                                                    "description": description,
                                                    "discounted_price": discounted_price,
                                                    "original_price": original_price,
                                                    "stars": stars
                                                }})

        # Fetch all users from the database
        packages = await db.admin_package.find().to_list(length=None)
        

        # Render the user management page with the success message
        success_message = f"package with ID {package_id} updated successfully"

        # return RedirectResponse(url="/admins/show_admin_packages", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse("show_admin_packages.html", {"request": request, "display_table": bool(packages), "packages": packages, "success_message": success_message})

    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)





@router.get("/update-Package/{package_id}")
async def update_admin_page(request: Request, package_id: str, db=Depends(get_db), user1 = Depends(get_current_user)):


    user = user1[0]
    value = user1[1]

    if value == "1":
        # Fetch user data by ID
        package = await db.admin_package.find_one({"_id": ObjectId(package_id)})

        if package is None:
            # If user not found, redirect with error message
            return templates.TemplateResponse("update_admin_package.html", 
                                            {"request": request, "error_message": "Package not found"},
                                            status_code=400)
        
        return templates.TemplateResponse("update_admin_package.html", {"request": request, "display_table": True, "package": package})
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    
@router.post("/add-Package")
async def update_admin(request: Request, image_path: str = Form(...),
                        destination_name: str = Form(...), guest_allowed: int= Form(...), description: str= Form(...), 
                        discounted_price:int = Form(...) ,original_price: int = Form(...), stars:int = Form(...), db=Depends(get_db), 
                        user1 = Depends(get_current_user)):

    # image_path,destination_name,guest_allowed,description,discounted_price,original_price,stars



    user = user1[0]
    value = user1[1]

    if value == "1":
        
        # Find the user by user_id
        # package = await db.admin_package.find_one({"_id": ObjectId(package_id)})

        # if not package:
        #     return templates.TemplateResponse("show_admin_packages.html", 
        #                                     {"request": request, "error_message": "Package not found"},
        #                                     status_code=400)
        
        # Update the username
        await db.admin_package.insert_one({
            "image_path": image_path,
            "destination_name": destination_name,
            "guest_allowed": guest_allowed,
            "description": description,
            "discounted_price": discounted_price,
            "original_price": original_price,
            "stars": stars
        })


        

        # Render the user management page with the success message
        success_message = f"package has been added successfully"

        # return RedirectResponse(url="/admins/show_admin_packages", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse("admin_index.html", {"request": request, "success_message": success_message})

    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)


@router.get("/add-Package")
async def update_admin_page(request: Request, db=Depends(get_db), user1 = Depends(get_current_user)):
    user = user1[0]
    value = user1[1]

    if value == "1":
        return templates.TemplateResponse("add_admin_packages.html", {"request": request })
    
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    


@router.post("/delete-Package/{package_id}")
async def delete_admin(request: Request, package_id: str, db=Depends(get_db), user1 = Depends(get_current_user)):

    user = user1[0]
    value = user1[1]

    if value == "1":
        # Find the user by user_id
        package = await db.admin_package.find_one({"_id": ObjectId(package_id)})

        if not package:
            # If user not found, redirect with error message
            return templates.TemplateResponse("show_admin_packages.html", 
                                            {"request": request, "error_message": "No packages found"},
                                            status_code=400)
            # raise HTTPException(status_code=404, detail="Package not found")
        
        # Delete the user
        await db.admin_package.delete_one({"_id": ObjectId(package_id)})    

        success_message = f"Package deleted successfully"   

        # Fetch all users from the database    
        packages = await db.admin_package.find().to_list(length=None)

        if packages is None:
            # If user not found, redirect with error message
            return templates.TemplateResponse("show_admin_packages.html", 
                                            {"request": request, "error_message": "No packages found"},
                                            status_code=400)
        
        return templates.TemplateResponse("show_admin_packages.html", {"request": request, "display_table": True, "packages": packages, "success_message": success_message})
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)


    




@router.get("/show-admins")
async def admin_management(request: Request, user1 = Depends(get_current_user), db=Depends(get_db)):
    user = user1[0]
    value = user1[1]

    if value == "1":
        user = user1[0]

        if user:
            users_collection = db.admins
            users = await users_collection.find().to_list(length=None)
            return templates.TemplateResponse("show_admins.html", {"request": request, "display_table": bool(users), "users": users})
        return RedirectResponse("/login")
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)

    

@router.post("/register")
async def register_admin(request: Request, username: str = Form(...), password: str = Form(...), db=Depends(get_db), user1 = Depends(get_current_user)):
    user = user1[0]
    value = user1[1]

    if value == "1":
        users_collection = db.admins
        # Hash the password
        hashed_password = get_password_hash(password)
        # Check if the username is already registered
        existing_user = await users_collection.find_one({"username": username})
        if existing_user:
            return templates.TemplateResponse("show_admins.html", 
                                            {"request": request, "error_message": "Username already registered"},
                                            status_code=400)        
        # Insert the new user into the database    
        await users_collection.insert_one({"username": username, "hashed_password": hashed_password})
        # Fetch all users from the database
        all_users = await users_collection.find().to_list(length=None)

        # Return the user_management.html template with all users
        return templates.TemplateResponse("admin_index.html", 
                                    {"request": request, "display_table": True, "users": all_users},
                                    status_code=201)
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    
# /register

@router.get("/register")
async def update_admin_page(request: Request, db=Depends(get_db), user1 = Depends(get_current_user)):


    user = user1[0]
    value = user1[1]

    if value == "1":
        # Fetch user data by ID
        # user = await db.admins.find_one({"_id": ObjectId(user_id)})
        if user is None:
            # If user not found, redirect with error message
            return templates.TemplateResponse("add_new_admin.html", 
                                            {"request": request, "error_message": "Username not found"},
                                            status_code=400)
        
        return templates.TemplateResponse("add_new_admin.html", {"request": request, "display_table": True, "user": user})
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)






@router.post("/update/{user_id}")
async def update_admin(request: Request, user_id: str, username: str = Form(...), db=Depends(get_db), user1 = Depends(get_current_user)):


    user = user1[0]
    value = user1[1]

    if value == "1":
        # Find the user by user_id
        user = await db.admins.find_one({"_id": ObjectId(user_id)})
        if not user:
            return templates.TemplateResponse("show_admins.html", 
                                            {"request": request, "error_message": "Username not found"},
                                            status_code=400)
        
        # Update the username
        await db.admins.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": username}})

        # Fetch all users from the database
        users_cursor = db.admins.find()
        users = await users_cursor.to_list(length=None)  # Adjust length as needed

        # Render the user management page with the success message
        success_message = f"User with ID {user_id} updated successfully"

        # return RedirectResponse(url="/admins/show-admins", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse("show_admins.html", 
                                        {"request": request, "users": users, "display_table": True, "success_message": success_message})
        
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)
    


@router.get("/update/{user_id}")
async def update_admin_page(user_id: str, request: Request, db=Depends(get_db), user1 = Depends(get_current_user)):


    user = user1[0]
    value = user1[1]

    if value == "1":
        # Fetch user data by ID
        user = await db.admins.find_one({"_id": ObjectId(user_id)})
        if user is None:
            # If user not found, redirect with error message
            return templates.TemplateResponse("update_admin.html", 
                                            {"request": request, "error_message": "Username not found"},
                                            status_code=400)
        return templates.TemplateResponse("update_admin.html", {"request": request, "display_table": True, "user": user})
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)

    


@router.post("/delete/{user_id}")
async def delete_admin(request: Request, user_id: str, db=Depends(get_db), user1 = Depends(get_current_user)):


    user = user1[0]
    value = user1[1]

    if value == "1":
        # Find the user by user_id
        user = await db.admins.find_one({"_id": ObjectId(user_id)})
        if user is None:
            users = await db.admins.find().to_list(length=None)
            # If user not found, redirect with error message
            return templates.TemplateResponse("show_admins.html", 
                                            {"request": request, "display_table": True, "users": users, "error_message": "No users found"},status_code=404)
        
        # Delete the user
        await db.admins.delete_one({"_id": ObjectId(user_id)})    
        success_message = f"User with Username {user["username"]} deleted successfully"   

        # Fetch all users from the database    
        users = await db.admins.find().to_list(length=None)
        if users is None:
            # If user not found, redirect with error message
            return templates.TemplateResponse("show_admins.html", 
                                            {"request": request, "error_message": "No users found"},
                                            status_code=400)
        return templates.TemplateResponse("show_admins.html", {"request": request, "display_table": True, "users": users, "success_message": success_message})
    else:
        return templates.TemplateResponse("error.html", 
                                    {"request": request},
                                    status_code=401)



