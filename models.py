from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app import Base

class User(Base):
    __tablename__ = 'users'  # Changed from 'user' to 'users' for convention

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(64))
    current_lesson = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    progress = relationship('Progress', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Progress(Base):
    __tablename__ = 'progress'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Updated to match new table name
    lesson_id = Column(Integer, nullable=False)
    quiz_score = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Progress user_id={self.user_id} lesson_id={self.lesson_id}>'