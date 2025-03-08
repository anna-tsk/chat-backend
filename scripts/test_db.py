import asyncio
from database.database import SessionLocal
from database.crud import create_conversation, insert_message, get_messages

async def test():
    async with SessionLocal() as db:
        # First, create a conversation
        conversation = await create_conversation(db)
        conversation_id = conversation.id
        print(f"Created conversation with ID: {conversation_id}")

        # Now insert a message
        msg = await insert_message(db, conversation_id, "user", "Hello, world!", 1)
        print("Inserted:", msg)

        # Retrieve messages
        messages = await get_messages(db, conversation_id)
        print("Retrieved Messages:", messages)

if __name__ == "__main__":
    asyncio.run(test())
