from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return "Home"

@app.get("/hi")
def hw():
    return {"Hello":"World"}

if __name__ == "__main__":
    from os import environ
    import uvicorn

    uvicorn.run("main:app", reload=True, port=int(environ["SERVER_PORT"]))
    # 'main' is the file name 'main.py'
    # 'app' is the FastAPI object 'app = FastAPI()'
    # 'reload=True' tells uvicorn to restart the server if main.py changes