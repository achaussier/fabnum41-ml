"""API de la station météo : elle charge les modèles entraînés et répond aux demandes.

    uvicorn api.main:app --reload
    puis http://localhost:8000/docs

Le contrat (routes, champs, codes de réponse) est décrit dans SPEC-ML.md, section « API ».
Après un nouvel entraînement, relancez uvicorn : les modèles sont lus au démarrage.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator

from ml.preparation import ajouter_variables

DOSSIER_MODELES = Path(__file__).resolve().parent.parent / "modeles"
FICHIERS = {
    "prediction": DOSSIER_MODELES / "prediction_temperature.joblib",
    "categorie": DOSSIER_MODELES / "categorie.joblib",
}


def charger_modeles() -> dict:
    """Lit les fichiers .joblib. Un modèle qui n'a pas encore été entraîné vaut None."""
    return {nom: joblib.load(chemin) if chemin.exists() else None for nom, chemin in FICHIERS.items()}


# Les modèles sont chargés une seule fois, au démarrage de l'API.
MODELES = charger_modeles()

app = FastAPI(
    title="Station météo de Blois : prévisions",
    description="Prévoit la température dans 3 heures et devine l'état du ciel à partir des relevés de la borne.",
    version="1.0.0",
)


# ------------------------------------------------------------------ ce que l'API reçoit
class Releve(BaseModel):
    """Un relevé de la borne. Les plages sont celles du dictionnaire de données."""

    reference_capteur: str = Field("9B85D927590B5B28", description="Identifiant de la borne")
    instant_mesure: datetime = Field(description="Date et heure du relevé, en UTC (2025-03-14T09:00:00Z)")
    temperature: float = Field(ge=-40, le=85, description="Température, en °C")
    humidite: int = Field(ge=0, le=100, description="Humidité, en %")
    pression_atmospherique: float = Field(ge=300, le=1100, description="Pression, en hPa")
    vent_vitesse: float = Field(ge=0, le=60, description="Vitesse du vent, en m/s")
    vent_direction: int = Field(ge=0, le=359, description="Direction du vent, en degrés")
    rafale_max: float = Field(ge=0, le=60, description="Rafale maximale, en m/s")
    precipitation: float = Field(ge=0, le=240, description="Intensité de la pluie, en mm/h")
    pluie_cumul: float | None = Field(None, ge=0, description="Cumul de pluie, en mm (facultatif)")
    luminosite: int = Field(ge=0, le=200_000, description="Luminosité, en lux")
    indice_uv: float = Field(ge=0, le=15, description="Indice UV")


class RequetePrediction(BaseModel):
    """Les quatre derniers relevés horaires, du plus ancien (il y a 3 h) au plus récent."""

    releves: list[Releve] = Field(min_length=4, max_length=4, description="4 relevés consécutifs, espacés d'une heure")

    @model_validator(mode="after")
    def verifier_que_les_releves_se_suivent(self):
        for precedent, suivant in zip(self.releves[:-1], self.releves[1:]):
            if suivant.instant_mesure - precedent.instant_mesure != timedelta(hours=1):
                raise ValueError("les relevés doivent se suivre d'heure en heure, du plus ancien au plus récent")
        return self


class RequeteCategorie(BaseModel):
    """Un seul relevé suffit pour deviner l'état du ciel."""

    releve: Releve


# ------------------------------------------------------------------ erreurs
def erreur(statut: int, message: str, code: str) -> JSONResponse:
    """Toutes les erreurs ont la même forme : un message lisible et un code court."""
    return JSONResponse(status_code=statut, content={"error": message, "code": code})


@app.exception_handler(RequestValidationError)
async def requete_invalide(requete: Request, exception: RequestValidationError) -> JSONResponse:
    # On indique quel champ pose problème, par exemple « releves.2.humidite ».
    champs = sorted({".".join(str(morceau) for morceau in detail["loc"][1:]) or "corps" for detail in exception.errors()})
    return erreur(422, "Requête invalide : " + ", ".join(champs), "requete_invalide")


def vers_tableau(releves: list[Releve]) -> pd.DataFrame:
    """Range les relevés reçus comme le CSV d'historique : une ligne par relevé, classées par date."""
    lignes = [releve.model_dump() for releve in releves]
    tableau = pd.DataFrame(lignes)
    tableau["instant_mesure"] = pd.to_datetime(tableau["instant_mesure"], utc=True)
    return tableau.set_index("instant_mesure").sort_index()


def en_texte(instant: datetime) -> str:
    """Écrit une date comme dans le reste du projet : 2025-03-14T12:00:00Z."""
    return instant.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------ routes
@app.get("/sante", summary="L'API fonctionne-t-elle ? Quels modèles sont chargés ?")
def sante() -> dict:
    return {"statut": "ok", "modeles": {nom: modele is not None for nom, modele in MODELES.items()}}


@app.post("/predict/temperature", summary="Prévoir la température dans 3 heures")
def prevoir_temperature(requete: RequetePrediction):
    """Reçoit les 4 derniers relevés horaires et renvoie la température prévue 3 heures après le dernier."""
    paquet = MODELES["prediction"]
    if paquet is None:
        return erreur(503, "Le modèle de prévision n'est pas entraîné : lancez python ml/entrainer_prediction.py", "modele_absent")

    # On calcule les mêmes variables qu'à l'entraînement, puis on garde la dernière ligne :
    # c'est la seule qui connaît les trois heures précédentes.
    variables = ajouter_variables(vers_tableau(requete.releves), avec_cible=False)
    entree = variables[paquet["variables"]].tail(1)

    # Chaque arbre de la forêt donne sa prévision. Leur moyenne est la valeur prévue,
    # leur désaccord (l'écart-type) donne l'incertitude.
    foret = paquet["modele"]
    avis_des_arbres = [arbre.predict(entree.to_numpy())[0] for arbre in foret.estimators_]
    valeur_prevue = float(foret.predict(entree)[0])
    incertitude = float(pd.Series(avis_des_arbres).std(ddof=0))

    return {
        "grandeur": "temperature",
        "instant_prevu": en_texte(requete.releves[-1].instant_mesure + timedelta(hours=3)),
        "valeur_prevue": round(valeur_prevue, 1),
        "incertitude": round(incertitude, 1),
        "unite": "°C",
    }


@app.post("/classify/conditions", summary="Deviner l'état du ciel à partir d'un relevé")
def categoriser_conditions(requete: RequeteCategorie):
    """Reçoit un relevé et renvoie la catégorie la plus probable, avec la probabilité de chacune."""
    # TODO (atelier 4) : écrire cette route d'après SPEC-ML.md, section « API »,
    # sur le modèle de prevoir_temperature() juste au-dessus.
    return erreur(501, "La route /classify/conditions n'est pas encore écrite (atelier 4)", "non_implemente")
