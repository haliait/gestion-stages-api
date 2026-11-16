"""Opérations CRUD (Create, Read, Update, Delete) sur la table stages."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def lister_stages(db: Session, entreprise: str | None = None, skip: int = 0, limit: int = 100):
    requete = select(models.Stage)
    if entreprise:
        requete = requete.where(models.Stage.entreprise.ilike(f"%{entreprise}%"))
    requete = requete.order_by(models.Stage.id).offset(skip).limit(limit)
    return db.scalars(requete).all()


def obtenir_stage(db: Session, stage_id: int):
    return db.get(models.Stage, stage_id)


def creer_stage(db: Session, donnees: schemas.StageCreate):
    stage = models.Stage(**donnees.model_dump())
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage


def modifier_stage(db: Session, stage: models.Stage, donnees: schemas.StageUpdate):
    for champ, valeur in donnees.model_dump().items():
        setattr(stage, champ, valeur)
    db.commit()
    db.refresh(stage)
    return stage


def supprimer_stage(db: Session, stage: models.Stage):
    db.delete(stage)
    db.commit()
