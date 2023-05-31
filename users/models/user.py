from pydantic import BaseModel, Field


class User(BaseModel):

    user_name: str
    user_surname: str
    user_email: str
    user_phone: str
    user_password: str
    user_code: str


class UpdateUser(BaseModel):

    user_email: str
    user_name: str
    user_surname: str
    user_password: str

class LoginUser(BaseModel):

    user_email: str
    user_password: str


class DeleteUser(BaseModel):

    user_email: str
    user_password: str