from routers.expense import expenses
from routers.income import incomes
from routers.user import users
from fastapi import FastAPI
from os import environ

app = FastAPI()
app.include_router(users)
app.include_router(expenses)
app.include_router(incomes)

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