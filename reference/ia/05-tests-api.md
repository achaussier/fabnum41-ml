… envoi à claude-sonnet-5-5
```python
# Tests des trois routes de l'API (GET /sante, POST /predict/temperature, POST /classify/conditions).
# Ils vérifient le contrat décrit dans SPEC-ML.md, section « API », pas le code de api/main.py.
#
# Écart constaté entre le code et la spec :
# - SPEC-ML.md section 1 indique « 16 caractères » pour `reference_capteur`, mais `Releve` dans
#   api/main.py n'impose aucune longueur : une référence de 3 caractères est acceptée.
#   Le test correspondant est marqué xfail (strict) : il passera au vert quand le code sera corrigé,
#   ou il faudra le retirer si la spec précise que cette plage ne concerne pas l'API.
#
# Les tests de succès ont besoin des vrais modèles : ils sont ignorés (skip) tant que
# `python ml/entrainer_prediction.py` (ou l'entraînement du classifieur) n'a pas été lancé.

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from api import main

client = TestClient(main.app)

DEBUT = datetime(2025, 3, 14, tzinfo=timezone.utc)
CATEGORIES = {"Dégagé", "Nuageux", "Brouillard", "Précipitations"}
CHAMPS_PREDICTION = {"grandeur", "instant_prevu", "valeur_prevue", "incertitude", "unite"}


# ------------------------------------------------------------------ outils
def releve(heure, **modifications):
    """Un relevé valide, daté de `heure` heures après le 14 mars 2025 à 00:00 UTC."""
    instant = DEBUT + timedelta(hours=heure)
    donnees = {
        "instant_mesure": instant.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "temperature": 3.3,
        "humidite": 82,
        "pression_atmospherique": 997.9,
        "vent_vitesse": 3.3,
        "vent_direction": 43,
        "rafale_max": 6.1,
        "precipitation": 0.0,
        "pluie_cumul": 2629.2,
        "luminosite": 24360,
        "indice_uv": 1.8,
    }
    donnees.update(modifications)
    return donnees


def corps_prediction(heures=(6, 7, 8, 9)):
    return {"releves": [releve(heure) for heure in heures]}


def corps_categorie():
    return {"releve": releve(9)}


def verifier_forme_erreur(reponse):
    corps = reponse.json()
    assert set(corps) == {"error", "code"}
    assert isinstance(corps["error"], str) and corps["error"]
    assert isinstance(corps["code"], str) and corps["code"]


def sans_champ(corps_releve, champ):
    return {cle: valeur for cle, valeur in corps_releve.items() if cle != champ}


# Requêtes invalides pour /predict/temperature (identifiant, corps envoyé)
CAS_INVALIDES_PREDICTION = [
    ("trois_releves", corps_prediction((6, 7, 8))),
    ("cinq_releves", corps_prediction((5, 6, 7, 8, 9))),
    ("releves_non_consecutifs", corps_prediction((6, 7, 9, 10))),
    ("releves_dans_le_desordre", corps_prediction((9, 8, 7, 6))),
    ("humidite_a_150", {"releves": [releve(6), releve(7), releve(8, humidite=150), releve(9)]}),
    ("champ_obligatoire_manquant", {"releves": [releve(6), sans_champ(releve(7), "temperature"), releve(8), releve(9)]}),
]

# Requêtes invalides pour /classify/conditions
CAS_INVALIDES_CATEGORIE = [
    ("humidite_a_150", {"releve": releve(9, humidite=150)}),
    ("champ_obligatoire_manquant", {"releve": sans_champ(releve(9), "luminosite")}),
]


# ------------------------------------------------------------------ fixtures
@pytest.fixture
def reponse_prediction():
    if main.MODELES["prediction"] is None:
        pytest.skip("modèle non entraîné")
    return client.post("/predict/temperature", json=corps_prediction())


@pytest.fixture
def reponse_categorie():
    if main.MODELES["categorie"] is None:
        pytest.skip("modèle non entraîné")
    return client.post("/classify/conditions", json=corps_categorie())


# ------------------------------------------------------------------ GET /sante
def test_sante_repond_200_et_statut_ok():
    reponse = client.get("/sante")
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "ok"


def test_sante_indique_les_deux_modeles_par_un_booleen():
    modeles = client.get("/sante").json()["modeles"]
    assert set(modeles) == {"prediction", "categorie"}
    assert all(isinstance(charge, bool) for charge in modeles.values())


def test_sante_repond_200_et_signale_un_modele_absent(monkeypatch):
    monkeypatch.setitem(main.MODELES, "categorie", None)
    reponse = client.get("/sante")
    assert reponse.status_code == 200
    assert reponse.json()["modeles"]["categorie"] is False


# ------------------------------------------------------------------ POST /predict/temperature : succès
def test_prediction_repond_200(reponse_prediction):
    assert reponse_prediction.status_code == 200


def test_prediction_renvoie_exactement_les_cinq_champs_du_contrat(reponse_prediction):
    assert set(reponse_prediction.json()) == CHAMPS_PREDICTION


def test_prediction_grandeur_et_unite_sont_fixes(reponse_prediction):
    corps = reponse_prediction.json()
    assert corps["grandeur"] == "temperature"
    assert corps["unite"] == "°C"


def test_prediction_instant_prevu_est_le_dernier_releve_plus_3_heures(reponse_prediction):
    # Dernier relevé : 2025-03-14T09:00:00Z
    assert reponse_prediction.json()["instant_prevu"] == "2025-03-14T12:00:00Z"


def test_prediction_incertitude_est_positive_ou_nulle(reponse_prediction):
    assert reponse_prediction.json()["incertitude"] >= 0


def test_prediction_valeur_prevue_est_dans_une_plage_plausible(reponse_prediction):
    assert -40 <= reponse_prediction.json()["valeur_prevue"] <= 60


def test_prediction_valeur_et_incertitude_sont_arrondies_au_dixieme(reponse_prediction):
    corps = reponse_prediction.json()
    assert round(corps["valeur_prevue"], 1) == corps["valeur_prevue"]
    assert round(corps["incertitude"], 1) == corps["incertitude"]


# ------------------------------------------------------------------ POST /predict/temperature : erreurs
@pytest.mark.parametrize("corps", [cas[1] for cas in CAS_INVALIDES_PREDICTION], ids=[cas[0] for cas in CAS_INVALIDES_PREDICTION])
def test_prediction_requete_invalide_renvoie_422_requete_invalide(corps):
    reponse = client.post("/predict/temperature", json=corps)
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "requete_invalide"
    verifier_forme_erreur(reponse)


def test_prediction_modele_absent_renvoie_503_modele_absent(monkeypatch):
    monkeypatch.setitem(main.MODELES, "prediction", None)
    reponse = client.post("/predict/temperature", json=corps_prediction())
    assert reponse.status_code == 503
    assert reponse.json()["code"] == "modele_absent"
    verifier_forme_erreur(reponse)


def test_prediction_requete_invalide_passe_avant_la_verification_du_modele(monkeypatch):
    monkeypatch.setitem(main.MODELES, "prediction", None)
    reponse = client.post("/predict/temperature", json=corps_prediction((6, 7, 8)))
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "requete_invalide"


# ------------------------------------------------------------------ POST /classify/conditions : succès
def test_categorie_repond_200(reponse_categorie):
    assert reponse_categorie.status_code == 200


def test_categorie_est_l_une_des_quatre_categories(reponse_categorie):
    assert reponse_categorie.json()["categorie"] in CATEGORIES


def test_categorie_renvoie_une_probabilite_pour_chacune_des_quatre_categories(reponse_categorie):
    probabilites = reponse_categorie.json()["probabilites"]
    assert set(probabilites) == CATEGORIES
    assert all(0 <= probabilite <= 1 for probabilite in probabilites.values())


def test_categorie_probabilites_somment_a_un_a_l_arrondi_pres(reponse_categorie):
    probabilites = reponse_categorie.json()["probabilites"]
    assert sum(probabilites.values()) == pytest.approx(1, abs=0.02)


def test_categorie_probabilites_sont_arrondies_au_centieme(reponse_categorie):
    probabilites = reponse_categorie.json()["probabilites"]
    assert all(round(probabilite, 2) == probabilite for probabilite in probabilites.values())


def test_categorie_renvoyee_est_la_plus_probable(reponse_categorie):
    corps = reponse_categorie.json()
    assert corps["probabilites"][corps["categorie"]] == max(corps["probabilites"].values())


# ------------------------------------------------------------------ POST /classify/conditions : erreurs
@pytest.mark.parametrize("corps", [cas[1] for cas in CAS_INVALIDES_CATEGORIE], ids=[cas[0] for cas in CAS_INVALIDES_CATEGORIE])
def test_categorie_requete_invalide_renvoie_422_requete_invalide(corps):
    reponse = client.post("/classify/conditions", json=corps)
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "requete_invalide"
    verifier_forme_erreur(reponse)


def test_categorie_modele_absent_renvoie_503_modele_absent(monkeypatch):
    monkeypatch.setitem(main.MODELES, "categorie", None)
    reponse = client.post("/classify/conditions", json=corps_categorie())
    assert reponse.status_code == 503
    assert reponse.json()["code"] == "modele_absent"
    verifier_forme_erreur(reponse)


def test_categorie_requete_invalide_passe_avant_la_verification_du_modele(monkeypatch):
    monkeypatch.setitem(main.MODELES, "categorie", None)
    reponse = client.post("/classify/conditions", json={"releve": releve(9, humidite=150)})
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "requete_invalide"


@pytest.mark.xfail(strict=True, reason="écart avec la spec : reference_capteur devrait faire 16 caractères, l'API ne le vérifie pas")
def test_categorie_reference_capteur_trop_courte_renvoie_422():
    reponse = client.post("/classify/conditions", json={"releve": releve(9, reference_capteur="ABC")})
    assert reponse.status_code == 422
```

Remarques :
- **Écart repéré** : la spec demande 16 caractères pour `reference_capteur`, mais l'API ne le vérifie pas. Le test est en `xfail`. Si ce champ n'est pas censé être contrôlé par l'API, précisez-le dans la spec et retirez ce test.
- **Tests ignorés** : sans fichier `.joblib`, les tests de succès sont ignorés (`skip`) et pytest l'indique. Entraînez les modèles avant pour les voir tourner.
- **Cas ajoutés** : j'ai ajouté 5 relevés, l'ordre inversé et le champ manquant, car la spec les liste parmi les 422. J'ai aussi ajouté un test pour la règle « la validation passe avant la vérification du modèle ».
- **Point non couvert par la spec** : un `instant_mesure` sans fuseau (sans `Z`) est interprété avec l'heure locale du serveur dans `en_texte`. Ce n'est pas un écart avec la spec (elle impose l'UTC), mais cela vaudrait la peine de le valider.✔ fichier écrit : api/tests/test_routes.py — relisez-le, puis lancez les tests.
ℹ tokens : 9827 envoyés, 8441 reçus

