"""Tests des trois routes de l'API, écrits d'après la section « API » de SPEC-ML.md.

On teste le contrat (formats, codes, validation), jamais une valeur prévue exacte :
le modèle change à chaque entraînement.
Les tests de succès ont besoin des modèles entraînés ; sinon ils sont ignorés.
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from api import main

client = TestClient(main.app)

CATEGORIES = {"Dégagé", "Nuageux", "Brouillard", "Précipitations"}
DEBUT = datetime(2025, 3, 14, 6, 0, tzinfo=timezone.utc)


def releve(heure: int, **modifications) -> dict:
    """Un relevé valide, `heure` heures après 6 h le 14 mars 2025. Les champs passés en plus le modifient."""
    donnees = {
        "instant_mesure": (DEBUT + timedelta(hours=heure)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "temperature": 3.3, "humidite": 82, "pression_atmospherique": 997.9,
        "vent_vitesse": 3.3, "vent_direction": 43, "rafale_max": 6.1,
        "precipitation": 0.0, "pluie_cumul": 2629.2, "luminosite": 24360, "indice_uv": 1.8,
    }
    donnees.update(modifications)
    return donnees


def quatre_releves() -> list[dict]:
    return [releve(heure) for heure in range(4)]


def exiger_le_modele(nom: str) -> None:
    if main.MODELES[nom] is None:
        pytest.skip(f"modèle « {nom} » non entraîné")


# ------------------------------------------------------------------ /sante
def test_sante_repond_ok_et_liste_les_deux_modeles():
    reponse = client.get("/sante")

    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "ok"
    assert set(reponse.json()["modeles"]) == {"prediction", "categorie"}


def test_sante_signale_un_modele_absent(monkeypatch):
    monkeypatch.setitem(main.MODELES, "categorie", None)

    assert client.get("/sante").json()["modeles"]["categorie"] is False


# ------------------------------------------------------------------ /predict/temperature
def test_la_prevision_renvoie_les_cinq_champs_du_contrat():
    exiger_le_modele("prediction")

    reponse = client.post("/predict/temperature", json={"releves": quatre_releves()})

    assert reponse.status_code == 200
    corps = reponse.json()
    assert set(corps) == {"grandeur", "instant_prevu", "valeur_prevue", "incertitude", "unite"}
    assert corps["grandeur"] == "temperature"
    assert corps["unite"] == "°C"


def test_l_instant_prevu_est_trois_heures_apres_le_dernier_releve():
    exiger_le_modele("prediction")

    corps = client.post("/predict/temperature", json={"releves": quatre_releves()}).json()

    # Dernier relevé à 9 h, donc prévision pour 12 h.
    assert corps["instant_prevu"] == "2025-03-14T12:00:00Z"


def test_la_valeur_prevue_est_plausible_et_l_incertitude_positive():
    exiger_le_modele("prediction")

    corps = client.post("/predict/temperature", json={"releves": quatre_releves()}).json()

    assert -40 <= corps["valeur_prevue"] <= 60
    assert corps["incertitude"] >= 0


@pytest.mark.parametrize("releves", [
    pytest.param([releve(0), releve(1), releve(2)], id="3 relevés au lieu de 4"),
    pytest.param([releve(0), releve(1), releve(2), releve(3), releve(4)], id="5 relevés au lieu de 4"),
    pytest.param([releve(0), releve(1), releve(3), releve(4)], id="relevés non consécutifs"),
    pytest.param([releve(3), releve(2), releve(1), releve(0)], id="relevés dans le désordre"),
    pytest.param([releve(0), releve(1), releve(2), releve(3, humidite=150)], id="humidité à 150"),
    pytest.param([releve(0), releve(1), releve(2), releve(3, pression_atmospherique=10124)], id="pression non convertie"),
])
def test_une_demande_de_prevision_invalide_est_refusee(releves):
    reponse = client.post("/predict/temperature", json={"releves": releves})

    assert reponse.status_code == 422
    assert reponse.json()["code"] == "requete_invalide"
    assert reponse.json()["error"]


def test_un_champ_obligatoire_manquant_est_refuse():
    incomplet = releve(3)
    del incomplet["temperature"]

    reponse = client.post("/predict/temperature", json={"releves": [releve(0), releve(1), releve(2), incomplet]})

    assert reponse.status_code == 422


def test_la_prevision_repond_503_si_le_modele_est_absent(monkeypatch):
    monkeypatch.setitem(main.MODELES, "prediction", None)

    reponse = client.post("/predict/temperature", json={"releves": quatre_releves()})

    assert reponse.status_code == 503
    assert reponse.json()["code"] == "modele_absent"
    assert reponse.json()["error"]


def test_une_demande_invalide_recoit_422_meme_sans_modele(monkeypatch):
    monkeypatch.setitem(main.MODELES, "prediction", None)

    reponse = client.post("/predict/temperature", json={"releves": [releve(0)]})

    assert reponse.status_code == 422


# ------------------------------------------------------------------ /classify/conditions
def test_la_categorisation_renvoie_une_categorie_et_quatre_probabilites():
    exiger_le_modele("categorie")

    reponse = client.post("/classify/conditions", json={"releve": releve(3)})

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["categorie"] in CATEGORIES
    assert set(corps["probabilites"]) == CATEGORIES
    assert all(0 <= probabilite <= 1 for probabilite in corps["probabilites"].values())
    assert sum(corps["probabilites"].values()) == pytest.approx(1, abs=0.02)


def test_la_categorie_renvoyee_est_la_plus_probable():
    exiger_le_modele("categorie")

    corps = client.post("/classify/conditions", json={"releve": releve(3)}).json()

    assert corps["probabilites"][corps["categorie"]] == max(corps["probabilites"].values())


def test_un_releve_a_150_d_humidite_est_refuse():
    reponse = client.post("/classify/conditions", json={"releve": releve(3, humidite=150)})

    assert reponse.status_code == 422
    assert reponse.json()["code"] == "requete_invalide"


def test_la_categorisation_repond_503_si_le_modele_est_absent(monkeypatch):
    monkeypatch.setitem(main.MODELES, "categorie", None)

    reponse = client.post("/classify/conditions", json={"releve": releve(3)})

    assert reponse.status_code == 503
    assert reponse.json()["code"] == "modele_absent"
