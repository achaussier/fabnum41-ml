"""Explorer l'historique avant de s'en servir : un résumé chiffré et trois graphiques.

    python ml/explorer.py
    python ml/explorer.py donnees/synthetique.csv

Les graphiques sont écrits dans rapports/ :
    temperature_annee.png       la température sur un an
    pression_pluie_mois.png     la pression et la pluie sur un mois
    categories.png              la répartition des catégories
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # on écrit des fichiers PNG, sans ouvrir de fenêtre
import matplotlib.pyplot as plt

from preparation import CSV_HISTORIQUE, charger

RAPPORTS = Path("rapports")
ANNEE_TRACEE = "2024"
MOIS_TRACE = "2024-10"
MESURES = [
    "temperature", "humidite", "pression_atmospherique", "vent_vitesse", "vent_direction",
    "rafale_max", "precipitation", "pluie_cumul", "luminosite", "indice_uv",
]

# Sous Windows, le terminal n'affiche pas toujours les accents : on force l'UTF-8.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def resumer(df) -> None:
    """Affiche les chiffres clés de l'historique."""
    print(f"Nombre de relevés : {len(df)}")
    print(f"Période           : du {df.index.min():%d/%m/%Y %H:%M} au {df.index.max():%d/%m/%Y %H:%M} (UTC)")

    print("\nMinimum, moyenne et maximum de chaque mesure")
    print(df[MESURES].agg(["min", "mean", "max"]).T.rename(
        columns={"min": "minimum", "mean": "moyenne", "max": "maximum"}).round(1).to_string())

    manquantes = df.isna().sum()
    print("\nValeurs manquantes")
    if manquantes.sum() == 0:
        print("  aucune")
    else:
        print(manquantes[manquantes > 0].to_string())

    print("\nRépartition des catégories (l'étiquette que le modèle devra deviner)")
    parts = df["categorie"].value_counts(normalize=True) * 100
    for nom, part in parts.items():
        print(f"  {nom:15s} {part:5.1f} %   {'#' * round(part / 2)}")


def tracer_temperature(df) -> None:
    annee = df.loc[ANNEE_TRACEE, "temperature"]
    figure, axe = plt.subplots(figsize=(11, 4.5))
    axe.plot(annee.index, annee, color="#9ec5e8", linewidth=0.5, label="chaque heure")
    axe.plot(annee.resample("D").mean(), color="#c0392b", linewidth=1.6, label="moyenne du jour")
    axe.set_title(f"Température à Blois en {ANNEE_TRACEE}")
    axe.set_ylabel("°C")
    axe.grid(alpha=0.3)
    axe.legend()
    figure.tight_layout()
    figure.savefig(RAPPORTS / "temperature_annee.png", dpi=110)
    plt.close(figure)


def tracer_pression_pluie(df) -> None:
    mois = df.loc[MOIS_TRACE]
    figure, axe_pression = plt.subplots(figsize=(11, 4.5))
    axe_pression.plot(mois.index, mois["pression_atmospherique"], color="#2c3e50", linewidth=1.6)
    axe_pression.set_ylabel("Pression (hPa)", color="#2c3e50")
    axe_pression.grid(alpha=0.3)

    axe_pluie = axe_pression.twinx()  # un deuxième axe vertical, à droite, pour la pluie
    axe_pluie.bar(mois.index, mois["precipitation"], width=0.04, color="#2e86de", alpha=0.8)
    axe_pluie.set_ylabel("Précipitations (mm/h)", color="#2e86de")
    axe_pluie.set_ylim(0, max(4.0, mois["precipitation"].max() * 1.1))

    axe_pression.set_title(f"Pression (courbe) et pluie (barres) à Blois, {MOIS_TRACE}")
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.savefig(RAPPORTS / "pression_pluie_mois.png", dpi=110)
    plt.close(figure)


def tracer_categories(df) -> None:
    parts = df["categorie"].value_counts(normalize=True) * 100
    figure, axe = plt.subplots(figsize=(7, 4.5))
    barres = axe.bar(parts.index, parts.values, color=["#7f8c8d", "#f1c40f", "#2e86de", "#bdc3c7"][:len(parts)])
    axe.bar_label(barres, labels=[f"{part:.1f} %" for part in parts.values])
    axe.set_title("Répartition des catégories (part des heures)")
    axe.set_ylabel("% des relevés")
    axe.set_ylim(0, parts.max() * 1.15)
    figure.tight_layout()
    figure.savefig(RAPPORTS / "categories.png", dpi=110)
    plt.close(figure)


def main() -> None:
    chemin = sys.argv[1] if len(sys.argv) > 1 else CSV_HISTORIQUE
    df = charger(chemin)
    resumer(df)

    RAPPORTS.mkdir(exist_ok=True)
    tracer_temperature(df)
    tracer_pression_pluie(df)
    tracer_categories(df)
    print("\nGraphiques écrits dans rapports/ :")
    for nom in ("temperature_annee.png", "pression_pluie_mois.png", "categories.png"):
        print(f"  rapports/{nom}")


if __name__ == "__main__":
    main()
