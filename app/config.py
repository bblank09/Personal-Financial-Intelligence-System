import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_DATABASE_URI', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/finance_db')
