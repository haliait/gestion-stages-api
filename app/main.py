"""
API REST de gestion des stages - Mini-projet Cloud Computing & Microservices.

Lancer en local :  uvicorn app.main:app --reload
Documentation   :  http://127.0.0.1:8000/docs  (Swagger UI)
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import Base, engine, get_db

# --- Traçabilité : journal de chaque requête (cf. cours, sécurité des API) ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("stages-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Création des tables au démarrage si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    logger.info("Base de données prête")
    yield


app = FastAPI(
    title="API Gestion des Stages",
    description=(
        "API REST permettant de gérer les stages des étudiants d'une école d'ingénieurs "
        "(création, consultation, modification, suppression). "
        "Données fictives uniquement."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def journaliser_requetes(request: Request, call_next):
    debut = time.perf_counter()
    reponse = await call_next(request)
    duree_ms = (time.perf_counter() - debut) * 1000
    logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, reponse.status_code, duree_ms)
    return reponse


def stage_ou_404(stage_id: int, db: Session):
    """Récupère un stage ou renvoie une erreur 404 s'il n'existe pas."""
    stage = crud.obtenir_stage(db, stage_id)
    if stage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stage avec l'id {stage_id} introuvable",
        )
    return stage


# ------------------------------- Endpoints -------------------------------

@app.get("/", tags=["Accueil"])
def accueil():
    return {
        "message": "Bienvenue sur l'API de gestion des stages",
        "documentation": "/docs",
        "endpoints": "/stages",
    }


@app.get("/health", tags=["Accueil"])
def sante():
    """Vérification que le service est en vie (utile pour Render)."""
    return {"status": "ok"}


@app.get("/stages", response_model=list[schemas.StageOut], tags=["Stages"])
def lister_stages(
    entreprise: str | None = Query(None, description="Filtrer par entreprise (recherche partielle)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Consulter la liste des stages."""
    return crud.lister_stages(db, entreprise=entreprise, skip=skip, limit=limit)


@app.get(
    "/stages/{stage_id}",
    response_model=schemas.StageOut,
    tags=["Stages"],
    responses={404: {"description": "Stage introuvable"}},
)
def obtenir_stage(stage_id: int, db: Session = Depends(get_db)):
    """Consulter un stage par son identifiant."""
    return stage_ou_404(stage_id, db)


@app.post(
    "/stages",
    response_model=schemas.StageOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Stages"],
)
def creer_stage(stage: schemas.StageCreate, db: Session = Depends(get_db)):
    """Créer un nouveau stage."""
    return crud.creer_stage(db, stage)


@app.put(
    "/stages/{stage_id}",
    response_model=schemas.StageOut,
    tags=["Stages"],
    responses={404: {"description": "Stage introuvable"}},
)
def modifier_stage(stage_id: int, donnees: schemas.StageUpdate, db: Session = Depends(get_db)):
    """Modifier un stage existant (tous les champs sont remplacés)."""
    stage = stage_ou_404(stage_id, db)
    return crud.modifier_stage(db, stage, donnees)


@app.delete(
    "/stages/{stage_id}",
    response_model=schemas.Message,
    tags=["Stages"],
    responses={404: {"description": "Stage introuvable"}},
)
def supprimer_stage(stage_id: int, db: Session = Depends(get_db)):
    """Supprimer un stage."""
    stage = stage_ou_404(stage_id, db)
    crud.supprimer_stage(db, stage)
    return {"message": f"Stage {stage_id} supprimé avec succès"}
