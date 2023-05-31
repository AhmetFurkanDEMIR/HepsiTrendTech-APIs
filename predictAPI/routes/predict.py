from fastapi import APIRouter, Depends
from database.predict import *
from auth.auth_bearer import JWTBearer
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
import uuid
import shutil
from typing import Annotated

routes_predict = APIRouter()

@routes_predict.get("/", tags=["PredictAPI"])
def hi():

    return "Hi, Im HepsiTrend"


@routes_predict.post("/")
def predict(user_id:int, gender:int, file: UploadFile = File(...)):

    try:

        imgId = uuid.uuid1()
        imgId = str(imgId)
        pathh = "uploads/{}.png".format(imgId)

        with open(pathh, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        return predict_model(gender, pathh, user_id)

    except Exception:
        return JSONResponse(content="Dosya yüklenirken bir hata oluştu.", status_code=500)
    finally:
        file.file.close()
