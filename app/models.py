"""Modèle SQLAlchemy : correspond à la table `stages` dans SQLite."""
from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Stage(Base):
    __tablename__ = "stages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nom_etudiant: Mapped[str] = mapped_column(String(100), nullable=False)
    entreprise: Mapped[str] = mapped_column(String(100), nullable=False)
    intitule: Mapped[str] = mapped_column(String(200), nullable=False)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
