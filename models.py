from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index, Text, Float
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
    statistics = relationship('UserStatistics', backref='user', uselist=False)

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
    attempts = Column(Integer, default=1)  # Добавляем подсчет попыток

    # Add composite index for faster progress lookups
    __table_args__ = (
        Index('idx_user_lesson', 'user_id', 'lesson_id'),
    )

    def __repr__(self):
        return f'<Progress user_id={self.user_id} lesson_id={self.lesson_id}>'

class UserStatistics(Base):
    __tablename__ = 'user_statistics'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    total_time_spent = Column(Integer, default=0)  # в минутах
    average_score = Column(Float, default=0.0)
    completed_lessons = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_user_stats', 'user_id'),
    )

    def __repr__(self):
        return f'<UserStatistics user_id={self.user_id}>'

class LessonAttempt(Base):
    __tablename__ = 'lesson_attempts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    success = Column(Boolean, default=False)

    __table_args__ = (
        Index('idx_user_lesson_attempt', 'user_id', 'lesson_id'),
    )

    def __repr__(self):
        return f'<LessonAttempt user_id={self.user_id} lesson_id={self.lesson_id}>'

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    check_question = Column(String(255), nullable=False)
    check_options = Column(Text, nullable=False)  # Stored as JSON string
    check_correct = Column(String(10), nullable=False)
    materials = Column(Text, nullable=False)  # Stored as JSON string
    order = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    estimated_time = Column(Integer, default=30)  # Примерное время прохождения в минутах

    quiz = relationship("Quiz", backref="lesson", uselist=False)
    attempts = relationship("LessonAttempt", backref="lesson")

    def __repr__(self):
        return f'<Lesson {self.title}>'

class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    correct_answer = Column(String(10), nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Quiz {self.title}>'