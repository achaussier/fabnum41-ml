"""Télécharge l'historique météo de Blois et le met au format de la collection `mesures`.

    python donnees/telecharger_open_meteo.py
    python donnees/telecharger_open_meteo.py --debut 2024-01-01 --fin 2024-12-31 --sortie donnees/essai.csv

Source : Open-Meteo (https://open-meteo.com), sans clé, licence CC BY 4.0.
Le fichier donnees/historique_blois.csv est déjà dans le dépôt : ce script ne sert
qu'à le refaire ou à changer de période.

On interroge les « prévisions archivées » d'Open-Meteo (historical-forecast-api) et non
l'archive de réanalyse (archive-api) : cette dernière ne signale jamais de brouillard,
alors que la catégorie « Brouillard » fait partie des étiquettes à apprendre.
Avant novembre 2022, la source ne signale pas non plus le brouillard : c'est une limite
connue de ce jeu de données.

Deux colonnes sont des approximations, car l'archive ne les fournit pas :
  - luminosite (lux)  = rayonnement solaire (W/m²) × 120, plafonné à 200 000 ;
  - indice_uv         = rayonnement solaire (W/m²) / 110, plafonné à 11.
"""

import argparse
import io
import sys
import time
import urllib.parse
import urllib.request

import pandas as pd

API = "https://historical-forecast-api.open-meteo.com/v1/forecast"
LATITUDE = 47.5861
LONGITUDE = 1.3359
REFERENCE_CAPTEUR = "9B85D927590B5B28"

# Les colonnes du CSV, dans l'ordre (les mêmes noms que la collection `mesures`,
# plus les deux colonnes d'étiquette à la fin).
COLONNES = [
    "reference_capteur", "instant_mesure", "temperature", "humidite",
    "pression_atmospherique", "vent_vitesse", "vent_direction", "rafale_max",
    "precipitation", "pluie_cumul", "luminosite", "indice_uv",
    "weather_code", "categorie",
]

GRANDEURS = [
    "temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m",
    "wind_direction_10m", "wind_gusts_10m", "precipitation", "shortwave_radiation",
    "weather_code",
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


def telecharger_periode(debut: str, fin: str) -> pd.DataFrame:
    """Interroge Open-Meteo pour une période courte (le service est lent sur plusieurs années)."""
    parametres = urllib.parse.urlencode({
        "latitude": LATITUDE, "longitude": LONGITUDE,
        "start_date": debut, "end_date": fin,
        "hourly": ",".join(GRANDEURS),
        "wind_speed_unit": "ms", "timezone": "UTC", "format": "csv",
    })
    for essai in range(1, 6):
        try:
            with urllib.request.urlopen(f"{API}?{parametres}", timeout=120) as reponse:
                texte = reponse.read().decode("utf-8")
            break
        except OSError as erreur:
            print(f"  {debut} → {fin} : essai {essai} raté ({erreur}), on recommence…", file=sys.stderr)
            time.sleep(5)
    else:
        sys.exit(f"Open-Meteo ne répond pas pour la période {debut} → {fin}. Réessayez plus tard.")
    # Le CSV commence par un petit bloc sur le lieu, puis une ligne vide, puis les relevés.
    releves = texte[texte.index("time,"):]
    brut = pd.read_csv(io.StringIO(releves))
    # Les titres sont de la forme « temperature_2m (°C) » : on enlève l'unité.
    brut.columns = [nom.split(" (")[0] for nom in brut.columns]
    return brut


def telecharger(debut: str, fin: str) -> pd.DataFrame:
    """Télécharge la période demandée, six mois par six mois, et renvoie une ligne par heure."""
    bornes = list(pd.date_range(debut, fin, freq="6MS")) + [pd.Timestamp(fin) + pd.Timedelta(days=1)]
    if bornes[0] != pd.Timestamp(debut):
        bornes.insert(0, pd.Timestamp(debut))
    morceaux = []
    for depart, suivant in zip(bornes[:-1], bornes[1:]):
        dernier_jour = suivant - pd.Timedelta(days=1)
        print(f"  {depart:%Y-%m-%d} → {dernier_jour:%Y-%m-%d}", file=sys.stderr)
        morceaux.append(telecharger_periode(f"{depart:%Y-%m-%d}", f"{dernier_jour:%Y-%m-%d}"))
    return pd.concat(morceaux, ignore_index=True).dropna()


def convertir(brut: pd.DataFrame) -> pd.DataFrame:
    """Renomme et convertit les colonnes au format de la collection `mesures`."""
    soleil = brut["shortwave_radiation"]
    df = pd.DataFrame({
        "reference_capteur": REFERENCE_CAPTEUR,
        "instant_mesure": brut["time"] + ":00Z",
        "temperature": brut["temperature_2m"].round(1),
        "humidite": brut["relative_humidity_2m"].round().astype(int),
        "pression_atmospherique": brut["surface_pressure"].round(1),
        "vent_vitesse": brut["wind_speed_10m"].round(1),
        "vent_direction": brut["wind_direction_10m"].round().astype(int) % 360,
        "rafale_max": brut["wind_gusts_10m"].round(1),
        "precipitation": brut["precipitation"].round(1),
        "pluie_cumul": brut["precipitation"].cumsum().round(1),
        "luminosite": (soleil * 120).clip(upper=200_000).round().astype(int),
        "indice_uv": (soleil / 110).clip(upper=11).round(1),
        "weather_code": brut["weather_code"].astype(int),
    })
    df["categorie"] = df["weather_code"].map(categorie)
    return df[COLONNES]


def main() -> None:
    analyseur = argparse.ArgumentParser(description="Historique Open-Meteo de Blois, au format de la collection mesures.")
    analyseur.add_argument("--debut", default="2022-01-01", help="premier jour (AAAA-MM-JJ)")
    analyseur.add_argument("--fin", default="2025-12-31", help="dernier jour (AAAA-MM-JJ)")
    analyseur.add_argument("--sortie", default="donnees/historique_blois.csv", help="fichier CSV à écrire")
    options = analyseur.parse_args()

    print(f"Téléchargement de {options.debut} à {options.fin}…", file=sys.stderr)
    df = convertir(telecharger(options.debut, options.fin))
    df.to_csv(options.sortie, index=False, encoding="utf-8", lineterminator="\n")
    print(f"{len(df)} relevés écrits dans {options.sortie} (données Open-Meteo, CC BY 4.0)")


if __name__ == "__main__":
    main()
