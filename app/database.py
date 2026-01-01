from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url
from app.config import settings

# Import psycopg3 to ensure it's available before SQLAlchemy tries to detect drivers
import psycopg  # noqa: F401

# Explicitly use psycopg dialect - import it directly to avoid any auto-detection issues
from sqlalchemy.dialects.postgresql import psycopg as psycopg_dialect

# Parse URL and ensure it uses postgresql+psycopg
db_url = settings.DATABASE_URL
url = make_url(db_url)

# Force psycopg driver explicitly
if not url.drivername.endswith("+psycopg"):
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    elif "+" in url.drivername:
        # Remove any other driver suffix and add psycopg
        base = url.drivername.split("+")[0]
        url = url.set(drivername=f"{base}+psycopg")
    else:
        url = url.set(drivername="postgresql+psycopg")

# Convert URL object back to string for create_engine
db_url = str(url)

# Create engine with explicit dialect
engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

