from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Message
import uuid
from datetime import datetime

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


from sqlalchemy.future import select

async def get_messages(db: AsyncSession, conversation_id: uuid.UUID):
    result = await db.execute(select(Message).where(Message.conversation_id == conversation_id))
    return result.scalars().all()



from models.models import Conversation

async def create_conversation(db: AsyncSession):
    new_conversation = Conversation(id=uuid.uuid4())
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)
    return new_conversation


