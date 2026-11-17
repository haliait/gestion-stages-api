"""
Schémas Pydantic : ils décrivent le JSON accepté en entrée et renvoyé en
sortie. FastAPI les utilise pour valider les données et générer Swagger.
"""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StageBase(BaseModel):
        # Retire les espaces au début et à la fin des textes ("   " devient "" donc refusé)
    model_config = ConfigDict(str_strip_whitespace=True)
    nom_etudiant: str = Field(..., min_length=1, max_length=100, examples=["Étudiant Test"])
    entreprise: str = Field(..., min_length=1, max_length=100, examples=["Entreprise Démo"])
    intitule: str = Field(..., min_length=1, max_length=200, examples=["Développement d'une API REST"])
    date_debut: date = Field(..., examples=["2026-02-01"])
    date_fin: date = Field(..., examples=["2026-07-31"])

    @model_validator(mode="after")
    def verifier_dates(self):
        """Règle métier : un stage ne peut pas finir avant d'avoir commencé."""
        if self.date_fin < self.date_debut:
            raise ValueError("La date de fin doit être postérieure ou égale à la date de début")
        return self


class StageCreate(StageBase):
    """Données envoyées pour créer un stage (POST)."""


class StageUpdate(StageBase):
    """Données envoyées pour modifier un stage (PUT = remplacement complet)."""


class StageOut(BaseModel):
    """Stage renvoyé par l'API (avec son identifiant en premier)."""
    id: int
    nom_etudiant: str
    entreprise: str
    intitule: str
    date_debut: date
    date_fin: date

    model_config = ConfigDict(from_attributes=True)


class Message(BaseModel):
    message: str
