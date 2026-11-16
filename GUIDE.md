# Guide pas à pas : réalisation, VS Code, tests, Docker, GitHub, Render

Ce guide explique **comment le projet a été construit** puis **comment vous pouvez le reprendre** sur votre machine jusqu'au déploiement public. Les commandes sont données pour **Windows (PowerShell)**, avec l'équivalent macOS/Linux quand il diffère.

---

## 0. Prérequis à installer

| Outil | Pourquoi | Vérification |
|---|---|---|
| **Python 3.11 ou plus** (cocher *Add python.exe to PATH* à l'installation) | exécuter l'API | `python --version` |
| **VS Code** | éditeur | — |
| **Git** | envoyer le code sur GitHub | `git --version` |
| **Docker Desktop** (doit être *démarré*) | Partie 3 | `docker --version` |
| Comptes **GitHub** et **Render** (inscription Render possible avec le compte GitHub) | Partie 4 | — |
| **Postman** (facultatif, Swagger suffit) | Partie 2 | — |

---

## 1. Comment le projet a été réalisé

### Étape 1 : Analyse de l'énoncé et choix techniques
- Ressource à gérer : **Stage** (id, nom de l'étudiant, entreprise, intitulé, date de début, date de fin).
- **FastAPI** (proposé par l'énoncé) : il génère automatiquement la documentation **Swagger / OpenAPI** vue en cours (*« standard Spec Open API »*).
- **SQLite** via **SQLAlchemy** : base dans un simple fichier, sans serveur à installer.
- Respect des **4 règles REST** du cours :
  1. chaque ressource a un URI unique (`/stages/3`) ;
  2. CRUD via les méthodes HTTP `POST` / `GET` / `PUT` / `DELETE` ;
  3. réponses au format **JSON** ;
  4. codes HTTP standards (201, 200, 404, 422).

### Étape 2 : Découpage du code (séparation des responsabilités)
| Fichier | Rôle |
|---|---|
| `app/database.py` | connexion à SQLite ; chemin configurable via la variable d'environnement `DATABASE_URL` |
| `app/models.py` | la table `stages` (une colonne par champ) |
| `app/schemas.py` | format JSON accepté/renvoyé + **règle métier** : `date_fin ≥ date_debut` |
| `app/crud.py` | fonctions créer / lire / modifier / supprimer |
| `app/main.py` | les endpoints, la gestion du **404** et un **journal des requêtes** (pilier *traçabilité* de la sécurité des API vu en cours) |

### Étape 3 : Tests
- **10 tests automatisés** (`tests/test_api.py`) couvrant exactement les points de la Partie 2 : création, liste, modification, suppression, stage inexistant, plus la validation des données.
- Une **collection Postman**, un fichier `requetes.http` pour VS Code et deux **scripts** (curl / PowerShell) pour tester aussi l'URL Render.
- Vérification réelle : serveur lancé puis tous les endpoints appelés avec curl → codes 201 / 200 / 200 / 200 / 200 / 404 / 422 obtenus.

### Étape 4 : Conteneurisation
`Dockerfile` basé sur `python:3.12-slim` :
- installation des dépendances **avant** la copie du code (cache Docker plus efficace) ;
- exécution avec un **utilisateur non-root** (sécurité) ;
- écoute sur `0.0.0.0` et sur le port `$PORT` s'il existe (**Render impose 10000**), sinon 8000 en local. Le **même** Dockerfile marche donc en local et sur Render, sans modification.

### Étape 5 : Préparation du déploiement
- `.gitignore` : on ne pousse ni l'environnement virtuel ni la base `.db`.
- `.dockerignore` : l'image ne contient que le code utile.
- Endpoint `/health` pour le *Health Check* de Render.

---

## 2. Ouvrir le projet dans VS Code

1. **Décompressez** `gestion-stages-api.zip` (clic droit → *Extraire tout…*), par exemple dans `Documents\gestion-stages-api`.
2. Ouvrez VS Code → **Fichier → Ouvrir le dossier…** → choisissez le dossier `gestion-stages-api` (celui qui contient `Dockerfile`, **pas** le dossier parent).
3. VS Code propose d'installer les **extensions recommandées** (Python, Docker, REST Client) → acceptez.
4. Ouvrez un terminal intégré : **Terminal → Nouveau terminal** (ou ``Ctrl+` ``).

### Créer l'environnement virtuel et installer les dépendances
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```
macOS/Linux :
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```
✅ `(.venv)` apparaît au début de la ligne du terminal.
Dans VS Code : `Ctrl+Shift+P` → *Python: Select Interpreter* → choisissez celui de `.venv`.

> **Erreur « l'exécution de scripts est désactivée »** (Windows) : lancez une fois
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` puis réessayez l'activation.

---

## 3. Lancer l'API en local

```powershell
uvicorn app.main:app --reload
```
Le terminal affiche `Uvicorn running on http://127.0.0.1:8000`.

| Adresse | Contenu |
|---|---|
| http://127.0.0.1:8000 | message d'accueil |
| http://127.0.0.1:8000/docs | **Swagger UI** (tester les endpoints) |
| http://127.0.0.1:8000/redoc | autre présentation de la doc |

Alternative VS Code : onglet **Exécuter et déboguer** (`Ctrl+Shift+D`) → *Lancer l'API (uvicorn --reload)* → ▶.

Arrêter le serveur : `Ctrl+C` dans le terminal.

---

## 4. Tester l'API (Partie 2)

Laissez le serveur tourner et utilisez **un deuxième terminal** (bouton **+** du panneau terminal ; pensez à réactiver `.venv`).

### 4.1 Avec Swagger (recommandé pour les captures)
Sur http://127.0.0.1:8000/docs :
1. **POST /stages** → *Try it out* → modifiez le JSON d'exemple → *Execute* → **201** et l'`id` créé.
2. **GET /stages** → *Try it out* → *Execute* → la liste.
3. **PUT /stages/{stage_id}** → saisissez l'id, modifiez le JSON → **200**.
4. **DELETE /stages/{stage_id}** → **200** « Stage 1 supprimé avec succès ».
5. **GET /stages/{stage_id}** avec l'id supprimé (ou `999`) → **404** « Stage avec l'id 1 introuvable ».
6. *(bonus)* POST avec `date_fin` avant `date_debut` → **422**.

### 4.2 Avec l'extension REST Client de VS Code
Ouvrez `requetes.http` → cliquez sur **Send Request** au-dessus de chaque bloc, dans l'ordre. La réponse s'affiche à droite.

### 4.3 Avec Postman
1. **Import** → sélectionnez `postman/Gestion_Stages.postman_collection.json`.
2. Cliquez sur la collection → onglet **Variables** → `baseUrl` = `http://127.0.0.1:8000` → **Save**.
3. Clic droit sur la collection → **Run collection** → *Run*. Les 8 requêtes s'enchaînent ; l'id créé est réutilisé automatiquement et chaque requête vérifie son code HTTP (tout doit être vert).

### 4.4 En ligne de commande
PowerShell :
```powershell
.\scripts\test_api.ps1
```
Git Bash / macOS / Linux :
```bash
./scripts/test_api.sh
```
Requêtes à la main (sous PowerShell, tapez bien **`curl.exe`**, car `curl` y désigne une autre commande) :
```powershell
curl.exe http://127.0.0.1:8000/stages
curl.exe -X DELETE http://127.0.0.1:8000/stages/1
```
Pour un POST sous PowerShell, le plus simple :
```powershell
$body = @{ nom_etudiant="Étudiant Test"; entreprise="Entreprise Démo"; intitule="API REST"; date_debut="2026-02-01"; date_fin="2026-07-31" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/stages -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($body))
```

### 4.5 Tests automatisés
```powershell
pytest -v
```
Résultat attendu : `10 passed`. Ils utilisent une base temporaire et ne touchent pas à vos données.

---

## 5. Docker (Partie 3)

Ouvrez **Docker Desktop** et attendez « Engine running ». Arrêtez uvicorn (`Ctrl+C`) pour libérer le port 8000.

```powershell
# 1. Construire l'image
docker build -t gestion-stages-api .

# 2. Lancer un conteneur (port 8000 de votre PC -> port 8000 du conteneur)
docker run -d -p 8000:8000 --name stages-api gestion-stages-api

# 3. Vérifier qu'il tourne
docker ps
docker logs stages-api

# 4. Vérifier que l'API répond depuis le conteneur
curl.exe http://localhost:8000/health
.\scripts\test_api.ps1 -BaseUrl http://localhost:8000
```
**5. Swagger dans le conteneur** : http://localhost:8000/docs

Simuler Render en local (port 10000 fourni par la variable `PORT`) :
```powershell
docker run -d -p 10000:10000 -e PORT=10000 --name stages-render gestion-stages-api
```
→ http://localhost:10000/docs

Nettoyage :
```powershell
docker stop stages-api stages-render
docker rm stages-api stages-render
```
> Avec l'extension Docker de VS Code, vous voyez aussi images et conteneurs dans la barre latérale (icône baleine) : clic droit → *View Logs*, *Stop*, etc.

---

## 6. Déposer le code sur GitHub (Partie 4, étape 1)

1. Sur https://github.com → **New repository** → nom : `gestion-stages-api` → **Public** → ne cochez **rien** (ni README ni .gitignore) → *Create repository*.
2. Dans le terminal VS Code, à la racine du projet :
```powershell
git init
git add .
git commit -m "API REST gestion des stages : FastAPI, SQLite, Docker"
git branch -M main
git remote add origin https://github.com/VOTRE_PSEUDO/gestion-stages-api.git
git push -u origin main
```
La première fois, Git demande votre identité :
```powershell
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@exemple.com"
```
et une fenêtre de connexion GitHub s'ouvre lors du `push`.

✅ Rafraîchissez la page GitHub : les fichiers sont là, sans `.venv` ni `data/`.

*(Alternative sans terminal : icône **Source Control** de VS Code → *Publish to GitHub*.)*

---

## 7. Déployer sur Render (Partie 4, étapes 2 à 6)

1. https://render.com → **Get Started** → inscription **avec GitHub** (le plus simple).
2. Tableau de bord → **New → Web Service**.
3. Source **Git Provider / GitHub** → autorisez Render à accéder au dépôt `gestion-stages-api` → sélectionnez-le.
4. Formulaire :
   | Champ | Valeur |
   |---|---|
   | Name | `gestion-stages-api` (donnera l'URL) |
   | Region | Frankfurt (EU) |
   | Branch | `main` |
   | **Language** | **Docker** |
   | **Instance Type** | **Free** |
   | Advanced → Health Check Path | `/health` |
   Rien d'autre à renseigner : Render lit le `Dockerfile` et fournit `PORT=10000`, que notre commande de démarrage utilise.
5. **Create Web Service** → l'onglet **Logs** montre la construction de l'image puis
   `Uvicorn running on http://0.0.0.0:10000`. Le statut passe à **Live** (quelques minutes).
6. L'**URL publique** est affichée en haut : `https://gestion-stages-api-xxxx.onrender.com`.
   → Reportez-la dans le `README.md`, puis `git add . ; git commit -m "Ajout URL Render" ; git push`. Render redéploie automatiquement à chaque `push`.

---

## 8. Tester l'API déployée (Partie 4, étape 7)

- Navigateur : `https://VOTRE-URL.onrender.com/docs` → refaire les tests Swagger du §4.1.
- Postman : variable `baseUrl` = votre URL Render → *Run collection*.
- Scripts :
```powershell
.\scripts\test_api.ps1 -BaseUrl https://VOTRE-URL.onrender.com
```
```bash
./scripts/test_api.sh https://VOTRE-URL.onrender.com
```
> Plan gratuit : après 15 min sans requête, le service s'endort ; le premier appel prend environ 1 minute. Les données SQLite sont effacées à chaque redémarrage ou redéploiement (normal, c'est la remarque de l'énoncé).

---

## 9. Captures d'écran à fournir (livrable 5)

Enregistrez-les dans le dossier `captures/` :

| # | Capture | Démontre |
|---|---|---|
| 1 | Swagger local, liste des endpoints | Partie 1 |
| 2 | POST → 201 | création |
| 3 | GET /stages → liste | consultation |
| 4 | PUT → 200 | modification |
| 5 | DELETE → 200 | suppression |
| 6 | GET id inexistant → 404 | stage inexistant |
| 7 | Terminal : `docker build` réussi + `docker ps` | Partie 3 |
| 8 | Swagger sur `localhost:8000` avec le conteneur lancé | Partie 3 |
| 9 | Render : statut **Live** + logs de démarrage | Partie 4 |
| 10 | Swagger ou Postman (Run collection tout vert) sur l'URL Render | API publique |
| 11 | *(bonus)* `pytest -v` → 10 passed | qualité |

## 10. Checklist des livrables

- [ ] 1. Lien du dépôt GitHub
- [ ] 2. `Dockerfile` (dans le dépôt)
- [ ] 3. URL publique Render
- [ ] 4. Documentation des endpoints → `README.md`
- [ ] 5. Captures d'écran → `captures/`

---

## 11. Problèmes fréquents

| Symptôme | Solution |
|---|---|
| `python` introuvable | Réinstaller Python en cochant *Add to PATH*, ou utiliser `py` à la place de `python` |
| `uvicorn` introuvable | L'environnement `.venv` n'est pas activé → `.venv\Scripts\activate` |
| `ModuleNotFoundError: app` | Le terminal n'est pas à la racine du projet → `cd` dans le dossier qui contient `app/` |
| Port 8000 déjà utilisé | Arrêter l'autre serveur/conteneur, ou `docker run -p 8080:8000 …` puis http://localhost:8080 |
| `docker: error during connect` | Docker Desktop n'est pas démarré |
| Render : *No open ports detected* | Vérifier que le `Dockerfile` est intact (commande avec `--host 0.0.0.0 --port ${PORT:-8000}`) |
| Render : *Failed to build* | Lire l'onglet Logs ; vérifier que `requirements.txt` et `Dockerfile` sont bien poussés sur GitHub |
| Les stages ont disparu sur Render | Normal sur le plan gratuit (redémarrage = base SQLite réinitialisée) |
