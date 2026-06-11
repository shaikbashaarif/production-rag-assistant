# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, DeclarativeBase
# from app.core.config import settings

# os.makedirs(os.path.dirname(settings.sqlite_path), exist_ok=True)
# engine = create_engine(f"sqlite:///{settings.sqlite_path}", connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# class Base(DeclarativeBase):
#     pass

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def init_db():
#     from app.db import models  # noqa
#     Base.metadata.create_all(bind=engine)


from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()