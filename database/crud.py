from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.models import Message, Conversation
import uuid
from datetime import datetime

# Insert a new message into a conversation
async def insert_message(db: AsyncSession, conversation_id: uuid.UUID, sender: str, text: str, turn_order: int):
    new_message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        sender=sender,
        text=text,
        timestamp=datetime.utcnow(),
        turn_order=turn_order
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

# Retrieve messages from a conversation with pagination
async def get_messages(db: AsyncSession, conversation_id: uuid.UUID, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .offset(skip)
        .limit(limit)
        .order_by(Message.timestamp)
    )
    return result.scalars().all()

# Create a new conversation
async def create_conversation(db: AsyncSession):
    new_conversation = Conversation(id=uuid.uuid4())
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)
    return new_conversation

# Get a conversation by its ID
async def get_conversation_by_id(db: AsyncSession, conversation_id: uuid.UUID):
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    return result.scalars().first()

# Delete a conversation (messages will be cascade-deleted)
async def delete_conversation(db: AsyncSession, conversation_id: uuid.UUID):
    conversation = await get_conversation_by_id(db, conversation_id)
    if conversation:
        await db.delete(conversation)
        await db.commit()

# Get the latest turn order in a conversation
async def get_latest_turn_order(db: AsyncSession, conversation_id: uuid.UUID):
    result = await db.execute(
        select(Message.turn_order)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.turn_order.desc())
        .limit(1)
    )
    latest_turn = result.scalar()
    return latest_turn if latest_turn is not None else 0