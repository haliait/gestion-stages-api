"""
Tests automatisés de l'API (pytest).
Lancer avec :  pytest -v
Une base SQLite temporaire est utilisée : vos vraies données ne sont pas touchées.
"""
import os
import tempfile

# La base de test doit être définie AVANT d'importer l'application
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

STAGE = {
    "nom_etudiant": "Étudiant Test",
    "entreprise": "Entreprise Démo",
    "intitule": "Développement d'une API REST",
    "date_debut": "2026-02-01",
    "date_fin": "2026-07-31",
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_accueil_et_sante(client):
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}


def test_creation_stage(client):
    r = client.post("/stages", json=STAGE)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] > 0
    assert data["entreprise"] == "Entreprise Démo"


def test_liste_stages(client):
    r = client.get("/stages")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_consultation_par_id(client):
    stage_id = client.post("/stages", json=STAGE).json()["id"]
    r = client.get(f"/stages/{stage_id}")
    assert r.status_code == 200
    assert r.json()["id"] == stage_id


def test_modification_stage(client):
    stage_id = client.post("/stages", json=STAGE).json()["id"]
    modif = {**STAGE, "entreprise": "Autre Entreprise", "intitule": "Stage Data"}
    r = client.put(f"/stages/{stage_id}", json=modif)
    assert r.status_code == 200
    assert r.json()["entreprise"] == "Autre Entreprise"
    assert client.get(f"/stages/{stage_id}").json()["intitule"] == "Stage Data"


def test_suppression_stage(client):
    stage_id = client.post("/stages", json=STAGE).json()["id"]
    r = client.delete(f"/stages/{stage_id}")
    assert r.status_code == 200
    assert client.get(f"/stages/{stage_id}").status_code == 404


def test_stage_inexistant(client):
    for methode, kwargs in [("get", {}), ("put", {"json": STAGE}), ("delete", {})]:
        r = getattr(client, methode)("/stages/99999", **kwargs)
        assert r.status_code == 404
        assert "introuvable" in r.json()["detail"]


def test_validation_dates(client):
    mauvais = {**STAGE, "date_debut": "2026-08-01", "date_fin": "2026-01-01"}
    assert client.post("/stages", json=mauvais).status_code == 422


def test_champ_manquant(client):
    incomplet = {k: v for k, v in STAGE.items() if k != "entreprise"}
    assert client.post("/stages", json=incomplet).status_code == 422


def test_filtre_entreprise(client):
    client.post("/stages", json={**STAGE, "entreprise": "FiltreCorp"})
    r = client.get("/stages", params={"entreprise": "filtre"})
    assert r.status_code == 200
    assert all("FiltreCorp" == s["entreprise"] for s in r.json())
    assert len(r.json()) >= 1
