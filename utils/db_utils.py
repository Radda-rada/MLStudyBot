from app import db, app
from models import User, Progress
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

def get_or_create_user(telegram_id: int, username: str = None) -> Optional[User]:
    """Get existing user or create a new one."""
    with app.app_context():
        try:
            user = User.query.filter_by(telegram_id=telegram_id).first()
            if not user:
                user = User(telegram_id=telegram_id, username=username)
                db.session.add(user)
                db.session.commit()
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_or_create_user: {str(e)}")
            db.session.rollback()
            return None

def update_progress(user_id: int, lesson_id: int, quiz_score: int) -> bool:
    """Update user's progress for a specific lesson."""
    with app.app_context():
        try:
            progress = Progress(
                user_id=user_id,
                lesson_id=lesson_id,
                quiz_score=quiz_score,
                completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error in update_progress: {str(e)}")
            db.session.rollback()
            return False

def get_user_progress(user_id: int) -> List[Progress]:
    """Get all progress records for a user."""
    with app.app_context():
        try:
            return Progress.query.filter_by(user_id=user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_progress: {str(e)}")
            return []