# ---------------------------------------------------------------
# Image Docker de l'API Gestion des Stages (FastAPI + SQLite)
# ---------------------------------------------------------------

# 1) Image de base : Python 3.12 version légère
FROM python:3.12-slim

# 2) Bonnes pratiques Python dans un conteneur
#    - pas de fichiers .pyc, logs affichés immédiatement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATABASE_URL=sqlite:///./data/stages.db

# 3) Dossier de travail dans le conteneur
WORKDIR /app

# 4) Installation des dépendances (copiées seules d'abord pour profiter
#    du cache Docker : elles ne sont réinstallées que si requirements.txt change)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5) Copie du code de l'application
COPY app ./app

# 6) Utilisateur non-root (sécurité) + dossier pour la base SQLite
RUN useradd --create-home appuser && mkdir -p /app/data && chown -R appuser /app
USER appuser

# 7) Port exposé (documentation). Render fournit son propre port via $PORT.
EXPOSE 8000

# 8) Commande de démarrage : on écoute sur 0.0.0.0 (obligatoire dans un
#    conteneur) et sur $PORT s'il est défini (Render), sinon 8000 (en local)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
