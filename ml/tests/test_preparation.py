"""Tests de ml/preparation.py, écrits d'après les sections 2 et 4 de SPEC-ML.md.

Ils protègent les deux règles que l'atelier 2 a fait découvrir :
  - on découpe dans le temps, jamais au hasard ;
  - la cible est la température relevée trois heures plus tard, pas une autre.

Ils ne disent rien de la qualité du modèle : celle-ci se mesure, elle ne se teste pas.
"""

import pandas as pd
import pytest

from ml.preparation import (CIBLE_CATEGORIE, CIBLE_PREDICTION, VARIABLES_CATEGORIE, VARIABLES_PREDICTION,
                            ajouter_variables, charger, decouper)

COUPURE = pd.Timestamp("2025-01-01", tz="UTC")


@pytest.fixture(scope="module")
def donnees():
    return ajouter_variables(charger())


def test_l_entrainement_ne_contient_aucun_releve_de_2025(donnees):
    entrainement, _ = decouper(donnees)

    assert entrainement.index.max() < COUPURE


def test_le_test_ne_contient_que_des_releves_de_2025(donnees):
    _, test = decouper(donnees)

    assert test.index.min() >= COUPURE


def test_le_decoupage_ne_perd_et_ne_duplique_aucun_releve(donnees):
    entrainement, test = decouper(donnees)

    assert len(entrainement) + len(test) == len(donnees)
    assert entrainement.index.intersection(test.index).empty


def test_la_cible_est_la_temperature_relevee_trois_heures_plus_tard(donnees):
    instant = pd.Timestamp("2025-03-14T09:00:00Z")

    assert donnees.loc[instant, CIBLE_PREDICTION] == donnees.loc[instant + pd.Timedelta(hours=3), "temperature"]


def test_la_temperature_passee_est_celle_relevee_trois_heures_plus_tot(donnees):
    instant = pd.Timestamp("2025-03-14T09:00:00Z")

    assert donnees.loc[instant, "temperature_moins_3h"] == donnees.loc[instant - pd.Timedelta(hours=3), "temperature"]


@pytest.mark.parametrize("colonne_interdite", ["weather_code", "categorie", CIBLE_PREDICTION])
def test_les_reponses_ne_sont_jamais_dans_les_entrees(colonne_interdite):
    assert colonne_interdite not in VARIABLES_PREDICTION
    assert colonne_interdite not in VARIABLES_CATEGORIE


def test_sans_cible_les_derniers_releves_sont_gardes():
    # L'API reçoit des relevés dont on ne connaît pas la suite : la cible ne doit pas être exigée.
    brut = charger()
    avec = ajouter_variables(brut)
    sans = ajouter_variables(brut, avec_cible=False)

    assert CIBLE_PREDICTION not in sans.columns
    assert sans.index.max() == brut.index.max()
    assert avec.index.max() == brut.index.max() - pd.Timedelta(hours=3)


def test_la_cible_de_categorie_existe_dans_les_donnees(donnees):
    assert set(donnees[CIBLE_CATEGORIE]) == {"Dégagé", "Nuageux", "Brouillard", "Précipitations"}
