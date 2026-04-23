from sqlalchemy import create_engine, exc, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _ensure_postgres_database() -> None:
    url = make_url(settings.database_url)
    if url.get_backend_name() != "postgresql" or not url.database:
        return

    admin_url = url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    try:
        with admin_engine.connect() as connection:
            try:
                connection.execute(text(f'CREATE DATABASE "{url.database}"'))
            except exc.DBAPIError as error:
                message = str(getattr(error, "orig", error)).lower()
                if "already exists" not in message:
                    raise
    finally:
        admin_engine.dispose()


def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        return
    except exc.OperationalError as error:
        message = str(getattr(error, "orig", error)).lower()
        if "does not exist" not in message or "database" not in message:
            raise

    _ensure_postgres_database()
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
