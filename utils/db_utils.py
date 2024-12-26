import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app import get_session
from models import User, Progress

logger = logging.getLogger(__name__)

def get_or_create_user(telegram_id: int, username: str = None) -> Optional[User]:
    """Get existing user or create a new one with improved error handling."""
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
            logger.info(f"Created new user with telegram_id {telegram_id}")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_or_create_user: {str(e)}")
        session.rollback()
        return None
    finally:
        session.close()

def update_progress(user_id: int, lesson_id: int, quiz_score: int) -> bool:
    """Update user's progress for a specific lesson with optimized queries."""
    session = get_session()
    try:
        # Check if progress already exists using optimized query
        progress = session.query(Progress).filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()

        if progress:
            # Update existing progress
            progress.quiz_score = quiz_score
            progress.completed = True
            progress.completed_at = datetime.utcnow()
            logger.info(f"Updated existing progress for user {user_id}, lesson {lesson_id}")
        else:
            # Create new progress
            progress = Progress(
                user_id=user_id,
                lesson_id=lesson_id,
                quiz_score=quiz_score,
                completed=True,
                completed_at=datetime.utcnow()
            )
            session.add(progress)
            logger.info(f"Created new progress for user {user_id}, lesson {lesson_id}")

        session.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_progress: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

def get_user_progress(user_id: int) -> List[Progress]:
    """Get all progress records for a user using optimized query."""
    session = get_session()
    try:
        # Use joinedload to optimize query
        progress = session.query(Progress).options(
            joinedload(Progress.user)
        ).filter_by(user_id=user_id).all()
        logger.info(f"Retrieved progress for user {user_id}: {len(progress)} records")
        return progress
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_progress: {str(e)}")
        return []
    finally:
        session.close()

def update_user_lesson(user_id: int, new_lesson: int) -> bool:
    """Update user's current lesson with improved error handling."""
    session = get_session()
    try:
        user = session.query(User).get(user_id)
        if user:
            user.current_lesson = new_lesson
            session.commit()
            logger.info(f"Updated lesson to {new_lesson} for user {user_id}")
            return True
        logger.warning(f"User {user_id} not found")
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_user_lesson: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()