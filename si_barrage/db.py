import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Priorité à la variable d'environnement DATABASE_URL.
# Si elle n'est pas définie, on retombe sur SQLite pour le développement local.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./barrage.db")

if DATABASE_URL.startswith("sqlite"):
    print(
        "⚠️  Avertissement : DATABASE_URL non défini, utilisation de SQLite local (barrage.db)"
    )
else:
    print(f"✅ Connexion à la base de données : {DATABASE_URL}")

# SQLite nécessite check_same_thread=False ; PostgreSQL n'accepte pas ce paramètre.
_connect_args = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency to get a DB session.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
