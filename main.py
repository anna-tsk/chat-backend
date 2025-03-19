from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from api.routes import router
from database.database import engine, Base, SessionLocal
from database.crud import insert_message, create_conversation
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import openai
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize AI clients
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async with SessionLocal() as db:
        try:
            # ✅ Default AI model
            selected_model = "gpt"
            await websocket.send_text(f"🤖 Default AI Model: {selected_model}. Type 'set_model:claude' or 'set_model:gpt' to switch.")

            # ✅ Create a new conversation when WebSocket starts
            conversation = await create_conversation(db)
            conversation_id = conversation.id

            while True:
                # ✅ Receive message from user
                user_message = await websocket.receive_text()

                # ✅ Allow users to switch AI models
                if user_message.startswith("set_model:"):
                    new_model = user_message.split(":")[1].strip().lower()
                    if new_model in ["gpt", "claude"]:
                        selected_model = new_model
                        await websocket.send_text(f"✅ AI Model switched to: {selected_model}")
                    else:
                        await websocket.send_text("❌ Invalid model. Choose 'set_model:gpt' or 'set_model:claude'.")
                    continue  # Don't process as a regular message

                # ✅ Get the latest turn order
                from database.crud import get_latest_turn_order
                latest_turn = await get_latest_turn_order(db, conversation_id)

                # ✅ Store user message in database
                message = await insert_message(
                    db=db,
                    conversation_id=conversation_id,
                    sender="user",
                    text=user_message,
                    turn_order=latest_turn + 1
                )

                # ✅ Get AI response using selected model
                ai_response = await get_ai_response(user_message, conversation_id, db, model=selected_model)

                # ✅ Store AI response in database
                await insert_message(
                    db=db,
                    conversation_id=conversation_id,
                    sender="ai",
                    text=ai_response,
                    turn_order=latest_turn + 2
                )

                # ✅ Send AI response to user
                await websocket.send_text(f"AI ({selected_model}): {ai_response}")

        except WebSocketDisconnect:
            print("Client disconnected")

async def get_ai_response(user_message: str, conversation_id: uuid.UUID, db: AsyncSession, model="gpt"):
    """
    Sends the user's message to an AI model and returns the AI's response.
    Uses OpenAI (ChatGPT) or Anthropic (Claude).
    """
    # Get past messages for context
    from database.crud import get_messages
    past_messages = await get_messages(db, conversation_id)
    conversation_history = "\n".join([f"{msg.sender}: {msg.text}" for msg in past_messages])

    if model == "gpt":
        # ✅ Use OpenAI (ChatGPT)
        response = openai_client.chat.completions.create(
            model="gpt",
            messages=[
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": conversation_history},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content

    elif model == "claude":
        # ✅ Use Anthropic (Claude)
        response = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=500,
            system="You are an AI assistant.",
            messages=[
                {"role": "user", "content": conversation_history},
                {"role": "user", "content": user_message}
            ]
        )
        return response.content[0].text  # Claude's responses come as a list

    else:
        return "Error: Unknown AI model selected."