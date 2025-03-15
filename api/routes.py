from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import SessionLocal
from database.crud import (
    create_conversation,
    insert_message,
    get_messages,
    get_conversation_by_id,
    delete_conversation,
    get_latest_turn_order,
)
from pydantic import BaseModel
import uuid

router = APIRouter()

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Allowed sender types
VALID_SENDERS = {"user", "claude", "chatgpt"}

# Pydantic request model for sending messages
class MessageRequest(BaseModel):
    conversation_id: uuid.UUID
    sender: str
    text: str
    turn_order: int

# Create a new conversation
@router.post("/start_conversation")
async def start_conversation(db: AsyncSession = Depends(get_db)):
    conversation = await create_conversation(db)
    return {"conversation_id": str(conversation.id)}

# Send a message to a conversation
@router.post("/send_message")
async def send_message(request: MessageRequest, db: AsyncSession = Depends(get_db)):
    # Validate sender type
    if request.sender not in VALID_SENDERS:
        raise HTTPException(status_code=400, detail="Invalid sender type")
    
    # Check if conversation exists
    conversation = await get_conversation_by_id(db, request.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Validate turn order
    latest_turn = await get_latest_turn_order(db, request.conversation_id)
    if request.turn_order != latest_turn + 1:
        raise HTTPException(status_code=400, detail="Invalid turn order. Expected turn: {}".format(latest_turn + 1))
    
    # Insert message
    message = await insert_message(db, request.conversation_id, request.sender, request.text, request.turn_order)
    return {"message_id": str(message.id)}

# Retrieve messages from a conversation with pagination
@router.get("/get_messages")
async def get_messages_api(
    conversation_id: uuid.UUID = Query(...),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    messages = await get_messages(db, conversation_id, skip=skip, limit=limit)
    return {
        "messages": [
            {
                "id": str(msg.id),
                "sender": msg.sender,
                "text": msg.text,
                "timestamp": msg.timestamp.isoformat(),
                "turn_order": msg.turn_order,
            }
            for msg in messages
        ]
    }

# Delete a conversation and cascade delete its messages
@router.delete("/delete_conversation")
async def delete_conversation_api(conversation_id: uuid.UUID = Query(...), db: AsyncSession = Depends(get_db)):
    # Check if conversation exists
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete the conversation
    await delete_conversation(db, conversation_id)
    return {"detail": "Conversation deleted successfully"}
