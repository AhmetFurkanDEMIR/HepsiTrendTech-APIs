from fastapi import APIRouter, Depends
from database.user import create_user, delete_user, update_user, login_user, get_user_id
from models.user import *
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT
from fastapi.responses import JSONResponse

routes_user = APIRouter()

@routes_user.get("/", tags=["users"])
def hi():

    return "Hi, Im HepsiTrend"

@routes_user.post("/register", tags=["users"])
def register(user: User):

    return create_user(user.dict())


@routes_user.post("/login", tags=["users"])
def login(user: LoginUser):

    ret = login_user(user.dict())

    flag = ret[0]
    user_id = ret[1]

    if flag==True:
        
        jwt = signJWT(user.user_email)
        jwt["user_id"] = user_id

        return jwt

    elif flag==None:

        return JSONResponse(content="Giriş yapabilmeniz için lütfen mail adresinizi doğrulayınız.", status_code=500)

    else:

        return JSONResponse(content="Mail veya şifre hatalı", status_code=500)
     


@routes_user.delete("/", dependencies=[Depends(JWTBearer())], tags=["users"])
def delete(user: DeleteUser):

    return delete_user(user.dict())

@routes_user.put("/", dependencies=[Depends(JWTBearer())], tags=["users"])
def update(user: UpdateUser):

    return update_user(user.dict())


@routes_user.get("/getUser/{id}", dependencies=[Depends(JWTBearer())], tags=["users"])
def get_User(id: int):
    
    return get_user_id(id)