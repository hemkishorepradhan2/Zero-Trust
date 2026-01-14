from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Place the SQLite DB next to this file for predictable location
db_path = Path(__file__).resolve().parent / "accessguard.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path.as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
