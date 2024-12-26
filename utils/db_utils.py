import logging
from typing import Optional, List, Dict
from datetime import datetime
from functools import lru_cache
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from contextlib import contextmanager
from app import get_session
from models import User, Progress, UserStatistics, LessonAttempt, Lesson, Quiz

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
                # Создаем статистику для нового пользователя
                stats = UserStatistics(user_id=user.id)
                session.add(stats)
                session.commit()
                logger.info(f"Created new user with telegram_id {telegram_id}")
                get_cached_user.cache_clear()
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_or_create_user: {str(e)}")
            return None

def start_lesson_attempt(user_id: int, lesson_id: int) -> Optional[LessonAttempt]:
    """Create new lesson attempt."""
    with session_scope() as session:
        try:
            attempt = LessonAttempt(user_id=user_id, lesson_id=lesson_id)
            session.add(attempt)
            session.commit()
            return attempt
        except SQLAlchemyError as e:
            logger.error(f"Error creating lesson attempt: {str(e)}")
            return None

def complete_lesson_attempt(attempt_id: int, success: bool) -> bool:
    """Complete lesson attempt and update statistics."""
    with session_scope() as session:
        try:
            attempt = session.query(LessonAttempt).get(attempt_id)
            if not attempt:
                return False

            attempt.completed_at = datetime.utcnow()
            attempt.success = success

            # Обновляем статистику пользователя
            stats = session.query(UserStatistics).filter_by(user_id=attempt.user_id).first()
            if stats:
                if success:
                    stats.completed_lessons += 1
                stats.total_attempts += 1
                stats.last_activity = datetime.utcnow()

                # Обновляем среднюю оценку
                progress = session.query(Progress).filter_by(
                    user_id=attempt.user_id
                ).all()
                if progress:
                    avg_score = sum(p.quiz_score for p in progress) / len(progress)
                    stats.average_score = avg_score

            session.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error completing lesson attempt: {str(e)}")
            return False

def get_user_statistics(user_id: int) -> Optional[Dict]:
    """Get detailed statistics for user."""
    with session_scope() as session:
        try:
            stats = session.query(UserStatistics).filter_by(user_id=user_id).first()
            if not stats:
                return None

            # Получаем дополнительную информацию
            total_attempts = session.query(func.count(LessonAttempt.id))\
                .filter_by(user_id=user_id).scalar()
            successful_attempts = session.query(func.count(LessonAttempt.id))\
                .filter_by(user_id=user_id, success=True).scalar()

            return {
                "total_time_spent": stats.total_time_spent,
                "average_score": stats.average_score,
                "completed_lessons": stats.completed_lessons,
                "total_attempts": total_attempts,
                "successful_attempts": successful_attempts,
                "success_rate": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
                "last_activity": stats.last_activity
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return None

def get_all_users_statistics() -> List[Dict]:
    """Get statistics for all users (admin function)."""
    with session_scope() as session:
        try:
            users = session.query(User).options(
                joinedload(User.statistics)
            ).all()

            result = []
            for user in users:
                if user.statistics:
                    stats = {
                        "user_id": user.id,
                        "username": user.username,
                        "telegram_id": user.telegram_id,
                        "current_lesson": user.current_lesson,
                        "total_time_spent": user.statistics.total_time_spent,
                        "average_score": user.statistics.average_score,
                        "completed_lessons": user.statistics.completed_lessons,
                        "total_attempts": user.statistics.total_attempts,
                        "last_activity": user.statistics.last_activity
                    }
                    result.append(stats)

            return result
        except SQLAlchemyError as e:
            logger.error(f"Error getting all users statistics: {str(e)}")
            return []

def update_progress(user_id: int, lesson_id: int, quiz_score: int) -> bool:
    """Update user's progress for a specific lesson with optimized queries."""
    with session_scope() as session:
        try:
            progress = session.query(Progress).filter_by(
                user_id=user_id,
                lesson_id=lesson_id
            ).first()

            if progress:
                progress.quiz_score = quiz_score
                progress.completed = True
                progress.completed_at = datetime.utcnow()
                progress.attempts += 1
            else:
                progress = Progress(
                    user_id=user_id,
                    lesson_id=lesson_id,
                    quiz_score=quiz_score,
                    completed=True,
                    completed_at=datetime.utcnow()
                )
                session.add(progress)

            # Обновляем статистику пользователя
            stats = session.query(UserStatistics).filter_by(user_id=user_id).first()
            if stats:
                stats.last_activity = datetime.utcnow()
                # Обновляем среднюю оценку
                all_progress = session.query(Progress).filter_by(user_id=user_id).all()
                avg_score = sum(p.quiz_score for p in all_progress) / len(all_progress) if all_progress else 0  # Handle empty progress list
                stats.average_score = avg_score

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
            session.flush()
            user = session.query(User).get(user_id)
            session.refresh(user)

            if user:
                old_lesson = user.current_lesson
                logger.info(f"Updating lesson for user {user_id} from {old_lesson} to {new_lesson}")

                user.current_lesson = new_lesson

                # Обновляем время последней активности
                stats = session.query(UserStatistics).filter_by(user_id=user_id).first()
                if stats:
                    stats.last_activity = datetime.utcnow()

                session.commit()
                get_cached_user.cache_clear()

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