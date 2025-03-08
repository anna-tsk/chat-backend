from fastapi import FastAPI
from api.routes import router

app = FastAPI()

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}