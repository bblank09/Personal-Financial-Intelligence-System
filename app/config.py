import os
from dotenv import load_dotenv

load_dotenv()

# Try loading from local_config for GCP Cloud Run
try:
    from local_config import CONFIG_DB_URI, CONFIG_SECRET_KEY, CONFIG_MONGO_URI
except ImportError:
    CONFIG_DB_URI = 'sqlite:///dev.db'
    CONFIG_SECRET_KEY = 'dev-key'
    CONFIG_MONGO_URI = 'mongodb://localhost:27017/finance_db'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', CONFIG_SECRET_KEY)
    
    # Cloud run requires External URI (e.g mysql+pymysql://user:pass@host/db)
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_DATABASE_URI', CONFIG_DB_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MONGO_URI = os.environ.get('MONGO_URI', CONFIG_MONGO_URI)
