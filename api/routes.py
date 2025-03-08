from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from database.crud import create_conversation, insert_message
import uuid
from pydantic import BaseModel

router = APIRouter()

class MessageRequest(BaseModel):
    conversation_id: uuid.UUID
    sender: str
    text: str
    turn_order: int

@router.post("/start_conversation")
async def start_conversation(db: AsyncSession = Depends(get_db)):
    conversation = await create_conversation(db)
    return {"conversation_id": str(conversation.id)}

@router.post("/send_message")
async def send_message(request: MessageRequest, db: AsyncSession = Depends(get_db)):
    message = await insert_message(db, request.conversation_id, request.sender, request.text, request.turn_order)
    return {"message_id": str(message.id)}


from fastapi import Query
from database.crud import get_messages

@router.get("/get_messages")
async def get_messages_api(conversation_id: uuid.UUID = Query(...), db: AsyncSession = Depends(get_db)):
    messages = await get_messages(db, conversation_id)
    return {"messages": [{"id": str(msg.id), "sender": msg.sender, "text": msg.text, "timestamp": msg.timestamp.isoformat()} for msg in messages]}