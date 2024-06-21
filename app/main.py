from routers.auth import auth
from routers.user import users
from fastapi import FastAPI
from os import environ

app = FastAPI()
app.include_router(auth)
app.include_router(users)

@app.get("/")
async def home():
    return {"message":"Home"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=int(environ["SERVER_PORT"]))
    # 'main' is the file name 'main.py'
    # 'app' is the FastAPI object 'app = FastAPI()'
    # 'reload=True' tells uvicorn to restart the server if main.py changes
    # 'host="0.0.0.0"' to make available to any device on the same network