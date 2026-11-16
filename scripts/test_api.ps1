# Teste tous les endpoints de l'API depuis PowerShell (Windows).
# Usage :  .\scripts\test_api.ps1
#          .\scripts\test_api.ps1 -BaseUrl https://mon-api.onrender.com
param([string]$BaseUrl = "http://127.0.0.1:8000")

$ErrorActionPreference = "Stop"
Write-Host "== Tests sur $BaseUrl ==" -ForegroundColor Cyan

function Envoyer($Methode, $Chemin, $Corps = $null) {
    $params = @{ Method = $Methode; Uri = "$BaseUrl$Chemin"; ContentType = "application/json; charset=utf-8" }
    if ($Corps) { $params.Body = [System.Text.Encoding]::UTF8.GetBytes(($Corps | ConvertTo-Json)) }
    try {
        $r = Invoke-WebRequest @params -UseBasicParsing
        $texte = [System.Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray())
        return @{ Code = [int]$r.StatusCode; Contenu = $texte }
    } catch {
        $code = [int]$_.Exception.Response.StatusCode
        return @{ Code = $code; Contenu = $_.ErrorDetails.Message }
    }
}

function Afficher($Titre, $Attendu, $Res) {
    $ok = if ($Res.Code -eq $Attendu) { "OK" } else { "ECHEC" }
    $couleur = if ($ok -eq "OK") { "Green" } else { "Red" }
    Write-Host "`n$Titre -> HTTP $($Res.Code) (attendu $Attendu) [$ok]" -ForegroundColor $couleur
    Write-Host $Res.Contenu
}

$stage = @{ nom_etudiant = "Étudiant Test"; entreprise = "Entreprise Démo"; intitule = "Développement API REST"; date_debut = "2026-02-01"; date_fin = "2026-07-31" }

Afficher "1) GET /"              200 (Envoyer GET "/")
$res = Envoyer POST "/stages" $stage
Afficher "2) POST /stages"       201 $res
$id = ($res.Contenu | ConvertFrom-Json).id

Afficher "3) GET /stages"        200 (Envoyer GET "/stages")
Afficher "4) GET /stages/$id"    200 (Envoyer GET "/stages/$id")

$modif = $stage.Clone(); $modif.entreprise = "Nouvelle Entreprise"; $modif.intitule = "API REST + Docker"
Afficher "5) PUT /stages/$id"    200 (Envoyer PUT "/stages/$id" $modif)
Afficher "6) DELETE /stages/$id" 200 (Envoyer DELETE "/stages/$id")
Afficher "7) GET /stages/$id (inexistant)" 404 (Envoyer GET "/stages/$id")

$mauvais = $stage.Clone(); $mauvais.date_debut = "2026-09-01"; $mauvais.date_fin = "2026-01-01"
Afficher "8) POST dates invalides" 422 (Envoyer POST "/stages" $mauvais)
