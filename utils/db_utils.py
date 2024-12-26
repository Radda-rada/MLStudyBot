import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import get_session
from models import User, Progress

logger = logging.getLogger(__name__)

def get_or_create_user(telegram_id: int, username: str = None) -> Optional[User]:
    """Get existing user or create a new one."""
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_or_create_user: {str(e)}")
        session.rollback()
        return None
    finally:
        session.close()

def update_progress(user_id: int, lesson_id: int, quiz_score: int) -> bool:
    """Update user's progress for a specific lesson."""
    session = get_session()
    try:
        progress = Progress(
            user_id=user_id,
            lesson_id=lesson_id,
            quiz_score=quiz_score,
            completed=True,
            completed_at=datetime.utcnow()
        )
        session.add(progress)
        session.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_progress: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

def get_user_progress(user_id: int) -> List[Progress]:
    """Get all progress records for a user."""
    session = get_session()
    try:
        return session.query(Progress).filter_by(user_id=user_id).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_progress: {str(e)}")
        return []
    finally:
        session.close()

def update_user_lesson(user_id: int, new_lesson: int) -> bool:
    """Update user's current lesson."""
    session = get_session()
    try:
        user = session.query(User).get(user_id)
        if user:
            user.current_lesson = new_lesson
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_user_lesson: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()