import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the base class
db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 20,
    "max_overflow": 5
}

# Set secret key for session management
app.secret_key = os.urandom(24)

# Initialize the application with the extension
db.init_app(app)

# Push the application context
app_ctx = app.app_context()
app_ctx.push()

# Create database tables
with app.app_context():
    import models
    db.create_all()
    logger.info("Database tables created successfully")

# Make sure to keep the application context active
def get_app():
    return app

def get_db():
    return db