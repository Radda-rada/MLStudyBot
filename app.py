import os
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
Base = declarative_base()

def get_database_url():
    """Get database URL from environment with fallback"""
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    logger.info(f"Using database URL: {db_url}")
    return db_url

# Create database engine with optimized settings
engine = create_engine(
    get_database_url(),
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create session factory with optimized settings
Session = sessionmaker(
    bind=engine,
    expire_on_commit=False,  # Prevent unnecessary DB queries
)

# Function to get a new session
def get_session():
    return Session()

def init_db():
    """Initialize database with improved error handling and data management"""
    try:
        # Import models here to avoid circular imports
        import models  # noqa: F401
        from content.lessons import LESSONS
        from content.quizzes import QUIZZES
        from models import Lesson, Quiz

        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        logger.info("Database tables created or already exist")

        session = get_session()
        try:
            # Check existing lessons and quizzes
            existing_lessons = set(lesson.id for lesson in session.query(Lesson).all())
            existing_quizzes = set(quiz.lesson_id for quiz in session.query(Quiz).all())

            # Add or update lessons
            for lesson_id, lesson_data in LESSONS.items():
                if lesson_id not in existing_lessons:
                    lesson = Lesson(
                        id=lesson_id,
                        title=lesson_data['title'],
                        content=lesson_data['content'],
                        check_question=lesson_data['check_question'],
                        check_options=str(lesson_data['check_options']),
                        check_correct=lesson_data['check_correct'],
                        materials=str(lesson_data['materials']),
                        order=lesson_id
                    )
                    session.add(lesson)
                    logger.info(f"Added new lesson: {lesson_id} - {lesson_data['title']}")

            # Add or update quizzes
            for quiz_id, quiz_data in QUIZZES.items():
                if quiz_id not in existing_quizzes:
                    quiz = Quiz(
                        lesson_id=quiz_id,
                        title=quiz_data['title'],
                        question=quiz_data['question'],
                        correct_answer=quiz_data['correct_answer'],
                        explanation=quiz_data['explanation']
                    )
                    session.add(quiz)
                    logger.info(f"Added new quiz for lesson: {quiz_id}")

            session.commit()
            logger.info("Database initialization completed successfully")

            # Log table statistics using SQLAlchemy text()
            inspector = inspect(engine)
            for table_name in inspector.get_table_names():
                result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                logger.info(f"Table {table_name} contains {result} records")

        except Exception as e:
            logger.error(f"Error during database initialization: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Critical error during database setup: {e}")
        raise

# Initialize the database
if __name__ == "__main__":
    init_db()