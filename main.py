from fastapi import FastAPI
from api.routes import router

app = FastAPI()

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")
