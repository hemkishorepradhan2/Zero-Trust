from fastapi import FastAPI, HTTPException
from schemas import LoginRequest
from schemas import UserResponse
from fastapi import Depends
from login import router
app=FastAPI()
app.include_router(router)
# name=4
# global track
# track=0
# @app.get("/health")
# def health_check():
#     return {"status":"ok"}
# @app.get("/")
# def home():
#     return {"message":"Welcome to trustzero"}

# #practised path parameters
# @app.get("/users/{user_id}")
# def get_user(user_id:int):
#     if user_id == 4:
#         return {"message":"Authenticated"}
#     else:
    
#         global track
#         track = track+1
#         return {"message":"You are not allowed to access this endpoint"}
# @app.get("/logs")
# def logs():
#     return {
#         "message":f"No of times unauthenticated user tried to login {track}"
#     }

#query parameters
# users=["hem","silver",'john','caroline']
# users_roles={
#     "hem":"admin",
#     "john":"user"
# }
# @app.get("/search")
# def search_users(user:str , role:str):
#     if user in users:
#         if (role=="admin" and users_roles[users]=="admin"):
#             return {
#                 "Message":"Welcome Admin!!"
#             }
#         elif (role=="user" and users_roles[users]=="user"):
#             return {
#                 "Message":"Welcome user!!"
#             }
#         else:
#             return {
#                 "Message":"Wrong input"
            
#         }
        
# @app.post('/login')
# def login(data:LoginRequest):
#     return {
#         "Message":f"Your username is {data.username} and password is {data.password}"
#     }


# @app.get("/user",response_model=UserResponse)
# def get_user():
#     return {
#         "id":1,
#         "username":"hem_kishore_991",
#         "role":"ADMIN",
#         "password":"secret"

#     }


# depends

# def get_current_user():
#     return {
#         "username":"Hem",
#         "role":"USER"
#     }
# @app.get("/secure")
# def secure(user=Depends(get_current_user)):
#     if user["role"]!="ADMIN":
#         raise HTTPException(403)