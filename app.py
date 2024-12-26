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

# Create database engine with optimized pool settings
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
        # Import models here to avoid circular imports
        import models  # noqa: F401

        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"Existing tables: {existing_tables}")

        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")

        # Log created tables
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        logger.info(f"Tables after creation: {created_tables}")

    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

init_db()