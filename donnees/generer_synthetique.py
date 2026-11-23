"""Fabrique un historique météo SIMULÉ, au même format que donnees/historique_blois.csv.

    python donnees/generer_synthetique.py --debut 2022-01-01 --jours 1461 --graine 42 --pannes --sortie donnees/synthetique.csv

ATTENTION : ces données sont inventées par des règles écrites plus bas. Un modèle
entraîné dessus ne fait que réapprendre les règles du générateur : il ne sait rien
de la vraie météo. C'est pratique pour essayer une chaîne de bout en bout sans réseau
et pour le bonus « anomalies » (on sait où les pannes ont été placées), pas pour
prévoir le temps qu'il fera à Blois.

Ce qui est simulé :
  - le cycle des saisons et le cycle jour / nuit, à la latitude de Blois ;
  - une alternance « anticyclone / perturbation » tirée au hasard, heure après heure
    (une chaîne de Markov : l'état de l'heure suivante ne dépend que de l'état actuel).
    Cet état pilote ensemble la pression, les nuages, l'humidité, le vent et la pluie.
    La pression commence à baisser quelques heures AVANT la pluie.

Avec --pannes, trois défauts de capteur sont ajoutés, et la colonne `panne_injectee`
indique les lignes touchées :
  - une valeur figée pendant 6 heures ;
  - un pic isolé aberrant ;
  - une dérive lente de l'humidité sur plusieurs jours.
"""

import argparse
import sys

import numpy as np
import pandas as pd

REFERENCE_CAPTEUR = "9B85D927590B5B28"
LATITUDE = 47.5861
AVANCE_PRESSION = 6  # la pression réagit 6 h avant l'arrivée de la pluie

COLONNES = [
    "reference_capteur", "instant_mesure", "temperature", "humidite",
    "pression_atmospherique", "vent_vitesse", "vent_direction", "rafale_max",
    "precipitation", "pluie_cumul", "luminosite", "indice_uv",
    "weather_code", "categorie",
]


def categorie(code: int) -> str:
    """Regroupe les codes météo WMO en quatre catégories."""
    if code in (0, 1):
        return "Dégagé"
    if code in (2, 3):
        return "Nuageux"
    if code in (45, 48):
        return "Brouillard"
    return "Précipitations"


def lisser(cible: np.ndarray, depart: float, vitesse: float, bruit: np.ndarray) -> np.ndarray:
    """Fait suivre une cible en douceur : chaque heure, on parcourt une partie de l'écart."""
    valeurs = np.empty(len(cible))
    actuelle = depart
    for i in range(len(cible)):
        actuelle += vitesse * (cible[i] - actuelle) + bruit[i]
        valeurs[i] = actuelle
    return valeurs


def simuler(debut: str, jours: int, hasard: np.random.Generator) -> pd.DataFrame:
    n = jours * 24
    instants = pd.date_range(debut, periods=n, freq="h", tz="UTC")
    heure = instants.hour.to_numpy()
    jour_annee = instants.day_of_year.to_numpy()
    # +1 au cœur de l'été, -1 au cœur de l'hiver.
    saison = np.cos(2 * np.pi * (jour_annee - 200) / 365.25)

    # --- 1. Anticyclone ou perturbation ? (chaîne de Markov) -------------------
    # On tire d'abord « le temps qu'il fera » avec quelques heures d'avance :
    # la pression suivra cet état tout de suite, la pluie seulement plus tard.
    total = n + AVANCE_PRESSION
    perturbation_annoncee = np.zeros(total, dtype=bool)
    etat = False
    tirages = hasard.random(total)
    for i in range(total):
        hiver = 1 - saison[min(i, n - 1)]          # 0 en été, 2 en hiver
        chance_arrivee = (1 + 0.35 * hiver) / 110  # une perturbation tous les 3 à 5 jours
        chance_depart = 1 / 34                     # elle dure environ un jour et demi
        if etat and tirages[i] < chance_depart:
            etat = False
        elif not etat and tirages[i] < chance_arrivee:
            etat = True
        perturbation_annoncee[i] = etat
    annonce = perturbation_annoncee[AVANCE_PRESSION:]  # ce qui arrive dans 6 h
    perturbation = perturbation_annoncee[:n]           # ce qui se passe maintenant

    # --- 2. Pression, nuages ---------------------------------------------------
    pression = lisser(np.where(annonce, 993.0, 1014.0), 1008.0, 0.07, hasard.normal(0, 0.35, n))
    nuages = lisser(np.where(perturbation, 0.95, 0.25), 0.5, 0.15, hasard.normal(0, 0.07, n)).clip(0, 1)

    # --- 3. Soleil : hauteur dans le ciel selon l'heure et la saison ------------
    declinaison = np.radians(23.44) * np.cos(2 * np.pi * (jour_annee - 172) / 365.25)
    angle_horaire = np.radians(15 * (heure + 0.1 - 12))  # midi solaire ≈ 12 h UTC à Blois
    hauteur = (np.sin(np.radians(LATITUDE)) * np.sin(declinaison)
               + np.cos(np.radians(LATITUDE)) * np.cos(declinaison) * np.cos(angle_horaire)).clip(0)
    rayonnement = 1000 * hauteur * (1 - 0.75 * nuages ** 2)

    # --- 4. Température --------------------------------------------------------
    moyenne_saison = 12.5 + 8.5 * saison
    amplitude_jour = (2.5 + 2.5 * (saison + 1)) * (1 - 0.6 * nuages)
    cycle_jour = amplitude_jour * np.cos(2 * np.pi * (heure - 14.5) / 24)
    masse_air = lisser(np.where(perturbation, -1.5 * saison, 1.0 * saison), 0.0, 0.02, hasard.normal(0, 0.28, n))
    temperature = moyenne_saison + cycle_jour + masse_air + hasard.normal(0, 0.3, n)

    # --- 5. Vent ---------------------------------------------------------------
    vent = lisser(np.where(perturbation, 5.5, 2.3), 3.0, 0.2, hasard.normal(0, 0.35, n))
    vent = (vent + 0.8 * hauteur).clip(0)
    rafale = vent * (1.7 + hasard.random(n) * 0.6) + 0.4
    direction = lisser(np.where(perturbation, 235.0, 60.0), 180.0, 0.12, hasard.normal(0, 9, n)) % 360

    # --- 6. Pluie : seulement pendant une perturbation -------------------------
    il_pleut = perturbation & (hasard.random(n) < 0.15 + 0.4 * nuages)
    precipitation = np.where(il_pleut, hasard.exponential(0.9, n) + 0.1, 0.0)

    # --- 7. Humidité, puis brouillard -----------------------------------------
    humidite = (78 - 2.6 * cycle_jour + 14 * nuages - 6 * saison + 8 * il_pleut
                + hasard.normal(0, 3, n)).clip(18, 100)
    nuit_calme = (~perturbation) & (heure <= 8) & (saison < 0) & (vent < 2.2) & (humidite > 88)
    brouillard = nuit_calme & (hasard.random(n) < 0.45)
    humidite = np.where(brouillard, np.maximum(humidite, 97), humidite)
    rayonnement = np.where(brouillard, rayonnement * 0.4, rayonnement)

    # --- 8. Code météo WMO, cohérent avec ce qui précède ------------------------
    code = np.select(
        [il_pleut & (temperature < 0.5), precipitation >= 4, precipitation >= 1.2, precipitation >= 0.5,
         il_pleut, brouillard, nuages < 0.2, nuages < 0.4, nuages < 0.7],
        [71, 65, 63, 61, 51, 45, 0, 1, 2], default=3)

    df = pd.DataFrame({
        "reference_capteur": REFERENCE_CAPTEUR,
        "instant_mesure": instants.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "temperature": temperature.round(1),
        "humidite": humidite.round().astype(int),
        "pression_atmospherique": pression.round(1),
        "vent_vitesse": vent.round(1),
        "vent_direction": direction.round().astype(int) % 360,
        "rafale_max": rafale.round(1),
        "precipitation": precipitation.round(1),
        "pluie_cumul": 0.0,
        "luminosite": (rayonnement * 120).clip(max=200_000).round().astype(int),
        "indice_uv": (rayonnement / 110).clip(max=11).round(1),
        "weather_code": code,
    })
    df["pluie_cumul"] = df["precipitation"].cumsum().round(1)
    df["categorie"] = df["weather_code"].map(categorie)
    return df[COLONNES]


def injecter_pannes(df: pd.DataFrame, hasard: np.random.Generator) -> pd.DataFrame:
    """Abîme quelques relevés comme le ferait un capteur en panne, et note lesquels."""
    df = df.copy()
    n = len(df)
    panne = np.zeros(n, dtype=bool)
    colonne = {nom: df.columns.get_loc(nom) for nom in df.columns}

    # Valeur figée pendant 6 heures : le capteur répète son dernier relevé.
    for debut in hasard.choice(n - 6, size=max(1, n // 700), replace=False):
        nom = hasard.choice(["temperature", "humidite", "pression_atmospherique", "vent_vitesse"])
        df.iloc[debut:debut + 6, colonne[nom]] = df.iloc[debut, colonne[nom]]
        panne[debut + 1:debut + 6] = True

    # Pic isolé : une seule valeur absurde, puis tout redevient normal.
    pics = {"temperature": 22.0, "pression_atmospherique": -70.0, "vent_vitesse": 28.0}
    for position in hasard.choice(n, size=max(1, n // 400), replace=False):
        nom = hasard.choice(list(pics))
        df.iloc[position, colonne[nom]] = round(df.iloc[position, colonne[nom]] + pics[nom], 1)
        panne[position] = True

    # Dérive lente : l'humidité affichée grimpe peu à peu pendant 4 jours.
    for debut in hasard.choice(n - 96, size=max(1, n // 8000), replace=False):
        derive = np.linspace(0, 30, 96)
        valeurs = df.iloc[debut:debut + 96, colonne["humidite"]].to_numpy() + derive
        df.iloc[debut:debut + 96, colonne["humidite"]] = valeurs.clip(max=100).round().astype(int)
        panne[debut + 32:debut + 96] = True  # au début, la dérive est trop faible pour compter

    df["panne_injectee"] = panne
    return df


def main() -> None:
    analyseur = argparse.ArgumentParser(description="Historique météo simulé, au format de la collection mesures.")
    analyseur.add_argument("--debut", default="2022-01-01", help="premier jour (AAAA-MM-JJ)")
    analyseur.add_argument("--jours", type=int, default=1461, help="nombre de jours à simuler")
    analyseur.add_argument("--graine", type=int, default=42, help="même graine = mêmes données")
    analyseur.add_argument("--pannes", action="store_true", help="ajoute des pannes de capteur et la colonne panne_injectee")
    analyseur.add_argument("--sortie", default="donnees/synthetique.csv", help="fichier CSV à écrire")
    options = analyseur.parse_args()

    hasard = np.random.default_rng(options.graine)
    df = simuler(options.debut, options.jours, hasard)
    if options.pannes:
        df = injecter_pannes(df, hasard)
    df.to_csv(options.sortie, index=False, encoding="utf-8", lineterminator="\n")

    message = f"{len(df)} relevés simulés écrits dans {options.sortie}"
    if options.pannes:
        message += f", dont {int(df['panne_injectee'].sum())} marqués comme pannes"
    print(message, file=sys.stderr)


if __name__ == "__main__":
    main()
