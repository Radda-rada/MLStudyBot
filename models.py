from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(64))
    current_lesson = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    progress = relationship('Progress', backref='user', lazy=True)

    # Add index for faster lookups
    __table_args__ = (
        Index('idx_telegram_id', 'telegram_id'),
    )

    def __repr__(self):
        return f'<User {self.username}>'

class Progress(Base):
    __tablename__ = 'progress'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    lesson_id = Column(Integer, nullable=False)
    quiz_score = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    # Add composite index for faster progress lookups
    __table_args__ = (
        Index('idx_user_lesson', 'user_id', 'lesson_id'),
    )

    def __repr__(self):
        return f'<Progress user_id={self.user_id} lesson_id={self.lesson_id}>'