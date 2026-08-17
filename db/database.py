from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite:///flashtool.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)

def get_session():
    """Return a new database session."""
    return contextmanager(SessionLocal())
