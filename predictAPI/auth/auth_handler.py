import time
from typing import Dict
import jwt
from database.db import *

JWT_SECRET = "hepsitrendtech_dkfsdlf5*-43flkofds,54s6aDDFDS54345ds,fds855+^&%+^da,,FDSKfDSFDs,+45wF=+^FDOSÇ"
JWT_ALGORITHM = "HS256"


def token_response(token: str):
    return {
        "access_token": token
    }  

def signJWT(user_email: str) -> Dict[str, str]:

    #5 gun: 432000
    payload = {
        "user_email": user_email,
        "expires": time.time() + 432000
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    print(token.decode("utf-8") )

    cursor.execute(
        'update tbl_users set user_token=%s where user_email=%s',
        (token.decode("utf-8"), user_email,))
    conn.commit()

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}