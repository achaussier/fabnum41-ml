"""Préparation des données : tout ce qui se passe AVANT l'entraînement d'un modèle.

Trois fonctions, utilisées par les scripts d'entraînement et par l'API :

    charger(chemin)          lit le CSV et le range dans l'ordre du temps
    ajouter_variables(df)    calcule les colonnes que le modèle regardera
    decouper(df)             sépare l'historique en deux : entraînement et test

Vocabulaire :
    variable d'entrée   une colonne que le modèle a le droit de regarder
    cible               la colonne qu'il doit deviner
"""

import pandas as pd

CSV_HISTORIQUE = "donnees/historique_blois.csv"

# Ce que le modèle de prévision doit deviner : la température 3 heures plus tard.
CIBLE_PREDICTION = "temperature_dans_3h"

# Ce que le modèle de catégorisation doit deviner : l'état du ciel.
CIBLE_CATEGORIE = "categorie"

# Les colonnes que le modèle de prévision regarde.
VARIABLES_PREDICTION = [
    "heure",
    "mois",
    "jour_annee",
    "temperature",
    "humidite",
    "pression_atmospherique",
    "vent_vitesse",
    "luminosite",
    "temperature_moins_1h",
    "temperature_moins_3h",
    "variation_pression_3h",
    "humidite_moins_3h",
]

# Les colonnes que le modèle de catégorisation regarde : un seul relevé suffit.
# On n'y met jamais weather_code ni categorie : ce serait lui donner la réponse.
VARIABLES_CATEGORIE = [
    "heure",
    "mois",
    "temperature",
    "humidite",
    "pression_atmospherique",
    "vent_vitesse",
    "vent_direction",
    "rafale_max",
    "precipitation",
    "luminosite",
    "indice_uv",
]


def charger(chemin: str = CSV_HISTORIQUE) -> pd.DataFrame:
    """Lit le CSV des relevés et le range dans l'ordre du temps.

    La colonne instant_mesure devient l'index du tableau : on peut alors écrire
    df.loc["2025-03-14"] pour obtenir tous les relevés d'une journée.
    """
    df = pd.read_csv(chemin, encoding="utf-8")
    df["instant_mesure"] = pd.to_datetime(df["instant_mesure"], utc=True)
    return df.set_index("instant_mesure").sort_index()


def ajouter_variables(df: pd.DataFrame, avec_cible: bool = True) -> pd.DataFrame:
    """Ajoute les colonnes calculées à partir des relevés.

    heure, mois              le moment du relevé (il fait plus chaud à 15 h qu'à 6 h)
    jour_annee               le numéro du jour dans l'année, de 1 à 366 (la saison)
    temperature_moins_1h     la température une heure plus tôt
    temperature_moins_3h     la température trois heures plus tôt
    variation_pression_3h    de combien la pression a bougé en trois heures
    humidite_moins_3h        l'humidité trois heures plus tôt
    temperature_dans_3h      la cible : la température trois heures plus tard

    Les lignes incomplètes sont supprimées (les toutes premières n'ont pas de passé,
    les toutes dernières n'ont pas de futur).

    avec_cible=False : pour l'API, qui reçoit des relevés dont on ne connaît pas la suite.
    """
    df = df.copy()
    df["heure"] = df.index.hour
    df["mois"] = df.index.month
    df["jour_annee"] = df.index.day_of_year

    # shift(freq="3h") décale les relevés de trois heures : en face de 12 h,
    # on trouve la valeur relevée à 9 h.
    df["temperature_moins_1h"] = df["temperature"].shift(freq="1h")
    df["temperature_moins_3h"] = df["temperature"].shift(freq="3h")
    df["variation_pression_3h"] = df["pression_atmospherique"] - df["pression_atmospherique"].shift(freq="3h")
    df["humidite_moins_3h"] = df["humidite"].shift(freq="3h")

    colonnes_obligatoires = list(VARIABLES_PREDICTION)
    if avec_cible:
        df[CIBLE_PREDICTION] = df["temperature"].shift(freq="-3h")
        colonnes_obligatoires.append(CIBLE_PREDICTION)

    return df.dropna(subset=colonnes_obligatoires)


def decouper(df: pd.DataFrame, date_coupure: str = "2025-01-01") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sépare l'historique en deux, DANS LE TEMPS.

    Tout ce qui est avant la date sert à l'entraînement, tout ce qui est après sert
    au test. Le modèle est donc interrogé sur une période qu'il n'a jamais vue,
    exactement comme il le sera demain.
    """
    coupure = pd.Timestamp(date_coupure, tz="UTC")
    entrainement = df[df.index < coupure]
    test = df[df.index >= coupure]
    return entrainement, test
