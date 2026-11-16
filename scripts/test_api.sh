#!/usr/bin/env bash
# Teste tous les endpoints de l'API avec curl (Linux, macOS, Git Bash sous Windows).
# Usage :  ./scripts/test_api.sh                         (local, port 8000)
#          ./scripts/test_api.sh https://mon-api.onrender.com   (Render)
BASE_URL="${1:-http://127.0.0.1:8000}"
JSON="Content-Type: application/json"

echo "== Tests sur $BASE_URL =="

echo -e "\n1) Accueil (GET /)"
curl -s "$BASE_URL/"; echo

echo -e "\n2) Création d'un stage (POST /stages) -> attendu 201"
REPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/stages" -H "$JSON" \
  -d '{"nom_etudiant":"Étudiant Test","entreprise":"Entreprise Démo","intitule":"Développement API REST","date_debut":"2026-02-01","date_fin":"2026-07-31"}')
echo "$REPONSE"
ID=$(echo "$REPONSE" | head -n1 | sed -E 's/.*"id":([0-9]+).*/\1/')
echo "   -> id créé : $ID"

echo -e "\n3) Liste des stages (GET /stages) -> attendu 200"
curl -s -w "\n[HTTP %{http_code}]" "$BASE_URL/stages"; echo

echo -e "\n4) Consultation (GET /stages/$ID) -> attendu 200"
curl -s -w "\n[HTTP %{http_code}]" "$BASE_URL/stages/$ID"; echo

echo -e "\n5) Modification (PUT /stages/$ID) -> attendu 200"
curl -s -w "\n[HTTP %{http_code}]" -X PUT "$BASE_URL/stages/$ID" -H "$JSON" \
  -d '{"nom_etudiant":"Étudiant Test","entreprise":"Nouvelle Entreprise","intitule":"API REST + Docker","date_debut":"2026-02-01","date_fin":"2026-08-31"}'; echo

echo -e "\n6) Suppression (DELETE /stages/$ID) -> attendu 200"
curl -s -w "\n[HTTP %{http_code}]" -X DELETE "$BASE_URL/stages/$ID"; echo

echo -e "\n7) Stage inexistant (GET /stages/$ID) -> attendu 404"
curl -s -w "\n[HTTP %{http_code}]" "$BASE_URL/stages/$ID"; echo

echo -e "\n8) Dates invalides (POST /stages) -> attendu 422"
curl -s -o /dev/null -w "[HTTP %{http_code}]" -X POST "$BASE_URL/stages" -H "$JSON" \
  -d '{"nom_etudiant":"X","entreprise":"Y","intitule":"Z","date_debut":"2026-09-01","date_fin":"2026-01-01"}'; echo
