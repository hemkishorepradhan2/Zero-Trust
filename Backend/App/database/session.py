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


def provide_db():
    """Wrapper dependency that calls the current `get_db` implementation.

    Using this wrapper allows tests to monkeypatch `App.database.session.get_db`
    and have the wrapper call the patched function at runtime.
    """
    # call the module-level get_db (may be monkeypatched in tests)
    gen = get_db()
    try:
        db = next(gen)
    except StopIteration:
        return

    # Ensure tables exist on the session bind if available.
    try:
        # Use Session.get_bind() which is more reliable across SQLAlchemy
        # versions to find the engine associated with this Session.
        bind = None
        try:
            bind = db.get_bind()
        except Exception:
            bind = getattr(db, "bind", None)

        if bind is not None:
            from App.database.models import Base as ModelsBase

            try:
                ModelsBase.metadata.create_all(bind=bind)
            except Exception:
                pass
    except Exception:
        pass

    try:
        yield db
    finally:
        try:
            next(gen)
        except StopIteration:
            pass
