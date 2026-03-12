import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/social_media_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed_in_production")
    # Add other configurations like Redis URL if needed
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
