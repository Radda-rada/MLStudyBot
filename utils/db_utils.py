import logging
from typing import Optional, List
from datetime import datetime
from functools import lru_cache
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from contextlib import contextmanager
from app import get_session
from models import User, Progress

logger = logging.getLogger(__name__)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Session error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

@lru_cache(maxsize=100)
def get_cached_user(telegram_id: int) -> Optional[User]:
    """Get user from cache or database."""
    with session_scope() as session:
        return session.query(User).filter_by(telegram_id=telegram_id).first()

def get_or_create_user(telegram_id: int, username: str = None) -> Optional[User]:
    """Get existing user or create a new one with improved error handling."""
    # Try to get from cache first
    user = get_cached_user(telegram_id)
    if user:
        logger.info(f"Found cached user: {user.id}, current_lesson: {user.current_lesson}")
        return user

    with session_scope() as session:
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                user = User(telegram_id=telegram_id, username=username, current_lesson=1)
                session.add(user)
                session.commit()
                logger.info(f"Created new user with telegram_id {telegram_id}, current_lesson: 1")
                # Update cache
                get_cached_user.cache_clear()
            else:
                logger.info(f"Found existing user: {user.id}, current_lesson: {user.current_lesson}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_or_create_user: {str(e)}")
            return None

def update_progress(user_id: int, lesson_id: int, quiz_score: int) -> bool:
    """Update user's progress for a specific lesson with optimized queries."""
    with session_scope() as session:
        try:
            # Use efficient upsert operation
            progress = session.query(Progress).filter_by(
                user_id=user_id,
                lesson_id=lesson_id
            ).first()

            if progress:
                progress.quiz_score = quiz_score
                progress.completed = True
                progress.completed_at = datetime.utcnow()
            else:
                progress = Progress(
                    user_id=user_id,
                    lesson_id=lesson_id,
                    quiz_score=quiz_score,
                    completed=True,
                    completed_at=datetime.utcnow()
                )
                session.add(progress)

            session.commit()
            logger.info(f"Updated progress for user {user_id}, lesson {lesson_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error in update_progress: {str(e)}")
            return False

@lru_cache(maxsize=50)
def get_user_progress(user_id: int) -> List[Progress]:
    """Get all progress records for a user using optimized query."""
    with session_scope() as session:
        try:
            progress = session.query(Progress).options(
                joinedload(Progress.user)
            ).filter_by(user_id=user_id).all()
            logger.info(f"Retrieved progress for user {user_id}: {len(progress)} records")
            return progress
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_progress: {str(e)}")
            return []

def update_user_lesson(user_id: int, new_lesson: int) -> bool:
    """Update user's current lesson with improved error handling."""
    with session_scope() as session:
        try:
            # Explicitly flush the session to ensure we have the latest data
            session.flush()

            # Get user with explicit refresh
            user = session.query(User).get(user_id)
            session.refresh(user)

            if user:
                old_lesson = user.current_lesson
                logger.info(f"Updating lesson for user {user_id} from {old_lesson} to {new_lesson}")

                # Update the lesson
                user.current_lesson = new_lesson
                session.commit()

                # Clear cache to ensure fresh data
                get_cached_user.cache_clear()

                # Verify the update
                session.refresh(user)
                if user.current_lesson == new_lesson:
                    logger.info(f"Successfully updated lesson to {new_lesson} for user {user_id}")
                    return True
                else:
                    logger.error(f"Lesson update verification failed for user {user_id}")
                    return False

            logger.warning(f"User {user_id} not found")
            return False

        except SQLAlchemyError as e:
            logger.error(f"Database error in update_user_lesson: {str(e)}")
            return False