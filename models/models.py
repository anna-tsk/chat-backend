from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
import datetime

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String, nullable=False)  # "user", "claude", or "chatgpt"
    text = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    turn_order = Column(Integer)

    # Relationship to conversations
    conversation = relationship("Conversation", back_populates="messages")
