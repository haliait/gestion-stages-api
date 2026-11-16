"""
Configuration de la base de données SQLite avec SQLAlchemy.

Le chemin de la base peut être changé avec la variable d'environnement
DATABASE_URL (utile pour les tests ou pour Docker).
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Par défaut : fichier data/stages.db à la racine du projet
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/stages.db")

# On crée le dossier du fichier SQLite s'il n'existe pas encore
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "", 1)
    if db_path and db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

# check_same_thread=False : nécessaire avec SQLite car FastAPI peut
# traiter une requête sur un autre thread que celui qui a ouvert la connexion
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe de base de tous les modèles (tables)."""


def get_db():
    """Dépendance FastAPI : ouvre une session par requête puis la ferme."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
