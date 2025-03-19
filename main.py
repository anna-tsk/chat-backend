from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from api.routes import router
from database.database import engine, Base, SessionLocal
from database.crud import create_conversation, insert_message
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Manually create a DB session (Fix for WebSockets)
    async with SessionLocal() as db:
        try:
            conversation = await create_conversation(db)
            conversation_id = conversation.id  # Use the newly created conversation ID

            while True:
                # Receive message from client
                data = await websocket.receive_text()

                # Store message in database
                message = await insert_message(
                    db=db,
                    conversation_id=conversation_id,
                    sender="user",
                    text=data,
                    turn_order=0  # We'll handle turn order properly later
                )

                # Echo back with confirmation of storage
                await websocket.send_text(f"Stored: {message.text}")

        except WebSocketDisconnect:
            print("Client disconnected")
