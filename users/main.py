import uvicorn
from fastapi import FastAPI
from routes.user import routes_user
from pathlib import Path
from mangum import Mangum


app = FastAPI()

app.include_router(routes_user, prefix="/user")

if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", port=8081, debug=False)