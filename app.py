import os
import logging
from sqlalchemy import create_engine, inspect
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

# Create all tables
def init_db():
    try:
        # Drop all tables first to ensure clean state
        Base.metadata.drop_all(engine)

        # Import models here to avoid circular imports
        import models  # noqa: F401

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"Existing tables: {existing_tables}")

        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")

        # Log created tables
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        logger.info(f"Tables after creation: {created_tables}")

        # Now create the initial data
        session = get_session()
        try:
            # Import data from content files
            from content.lessons import LESSONS
            from content.quizzes import QUIZZES
            from models import Lesson, Quiz

            # Add lessons
            for lesson_id, lesson_data in LESSONS.items():
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

            # Add quizzes
            for quiz_id, quiz_data in QUIZZES.items():
                quiz = Quiz(
                    lesson_id=quiz_id,
                    title=quiz_data['title'],
                    question=quiz_data['question'],
                    correct_answer=quiz_data['correct_answer'],
                    explanation=quiz_data['explanation']
                )
                session.add(quiz)

            session.commit()
            logger.info("Initial data loaded successfully")

        except Exception as e:
            logger.error(f"Error loading initial data: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

init_db()