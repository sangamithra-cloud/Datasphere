from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
import os
from config import DATABASE_URL
from sqlalchemy.pool import NullPool

DATABASE_URL=os.environ.get("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool, )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base=declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

