from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Junction table for User <-> Chat relationship
chat_members = Table(
    'chat_members',
    Base.metadata,
    Column('user_id', BigInteger, ForeignKey('users.id'), primary_key=True),
    Column('chat_id', BigInteger, ForeignKey('chats.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    phone_number = Column(String)
    is_contact = Column(Boolean, default=False)
    
    messages = relationship("Message", back_populates="sender")
    chats = relationship("Chat", secondary=chat_members, back_populates="members")

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(BigInteger, primary_key=True)
    title = Column(String)
    type = Column(String) # private, group, supergroup, channel
    
    messages = relationship("Message", back_populates="chat")
    members = relationship("User", secondary=chat_members, back_populates="chats")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(BigInteger, primary_key=True) # Message ID within the chat
    chat_id = Column(BigInteger, ForeignKey('chats.id'), primary_key=True) # Composite PK
    sender_id = Column(BigInteger, ForeignKey('users.id'))
    date = Column(DateTime, default=datetime.utcnow)
    content_type = Column(String) # text, photo, video, voice, document
    text = Column(Text)
    file_id = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    is_downloaded = Column(Boolean, default=False)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")

class SyncState(Base):
    """Tracks the last synchronized message ID per chat for delta logic."""
    __tablename__ = 'sync_state'
    chat_id = Column(BigInteger, primary_key=True)
    last_message_id = Column(BigInteger)