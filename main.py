import uvicorn
from fastapi import FastAPI
from client import Client


app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/", status_code=201)
async def read_root(text: str):
    chat = Client()
    return {"text": chat.client_response(text)}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8888)
