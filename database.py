from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
import os
from config import DATABASE_URL


DATABASE_URL=os.environ.get("DATABASE_URL")

engine=create_engine(DATABASE_URL)
sessionLocal=sessionmaker(autocommit=False,autoflush=False,future=True,bind=engine)
Base=declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

