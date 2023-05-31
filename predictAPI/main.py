import uvicorn
from fastapi import FastAPI
from routes.predict import routes_predict
from pathlib import Path
from mangum import Mangum



app = FastAPI()

app.include_router(routes_predict, prefix="/predict")

if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", port=5006)