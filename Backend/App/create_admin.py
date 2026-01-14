import os
from App.database.session import SessionLocal, engine
from App.database.models import Base, User
from App.core.security import hash_password


def ensure_db():
    Base.metadata.create_all(bind=engine)


def create_initial_admin(username: str, password: str, email: str = "admin@example.com"):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.role == "admin").first()
        if existing:
            print("Admin user already exists:", existing.username)
            return

        admin = User(username=username, email=email, password=hash_password(password), role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Created admin user:", admin.username)
    finally:
        db.close()


if __name__ == "__main__":
    ensure_db()
    u = os.getenv("INIT_ADMIN_USER", "admin")
    p = os.getenv("INIT_ADMIN_PASS", "adminpass")
    create_initial_admin(u, p)
