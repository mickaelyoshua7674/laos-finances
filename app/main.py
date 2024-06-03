from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message":"Home"}

@app.get("/hi")
def hw():
    return {"message":"Hello World!"}

if __name__ == "__main__":
    from os import environ
    import uvicorn

    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=int(environ["SERVER_PORT"]))
    # 'main' is the file name 'main.py'
    # 'app' is the FastAPI object 'app = FastAPI()'
    # 'reload=True' tells uvicorn to restart the server if main.py changes