from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

def get_db_config():
    
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    port = os.environ.get('POSTGRES_PORT', '25432')
    database = os.environ.get('POSTGRES_DB', 'store_data')
    user = os.environ.get('POSTGRES_USER', 'postgres')
    password = os.environ.get('POSTGRES_PASSWORD', 'b50a8e36c91ef15f')
    
    config = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return config

SQL_ALCHEMY_DATABASE_URL = get_db_config()

engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()