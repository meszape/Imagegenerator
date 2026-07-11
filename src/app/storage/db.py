from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.config import get_settings
from app.core.models import Base
engine=create_engine(get_settings().database_url, connect_args={'check_same_thread':False} if get_settings().database_url.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
def init_db(): Base.metadata.create_all(bind=engine)
def get_db()->Generator[Session,None,None]:
    db=SessionLocal();
    try: yield db
    finally: db.close()
