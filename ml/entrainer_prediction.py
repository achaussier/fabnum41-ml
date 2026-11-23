"""Entraîne le modèle qui prévoit la température dans 3 heures.

    python ml/entrainer_prediction.py

Le script affiche l'erreur moyenne du modèle et celle d'une baseline, enregistre le
modèle dans modeles/prediction_temperature.joblib et trace rapports/prediction_vs_reel.png.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")  # on écrit un fichier PNG, sans ouvrir de fenêtre
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from preparation import CIBLE_PREDICTION, CSV_HISTORIQUE, VARIABLES_PREDICTION, ajouter_variables, charger, decouper

FICHIER_MODELE = Path("modeles/prediction_temperature.joblib")
GRAPHIQUE = Path("rapports/prediction_vs_reel.png")
SEMAINE_TRACEE = ("2025-06-02", "2025-06-08")

# Sous Windows, le terminal n'affiche pas toujours les accents : on force l'UTF-8.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    # 1. Charger l'historique et calculer les variables.
    donnees = ajouter_variables(charger(CSV_HISTORIQUE))

    # 2. Découper DANS LE TEMPS : avant 2025 pour apprendre, 2025 pour tester.
    #    X : ce que le modèle regarde. y : ce qu'il doit deviner.
    entrainement, test = decouper(donnees)
    X_entrainement, y_entrainement = entrainement[VARIABLES_PREDICTION], entrainement[CIBLE_PREDICTION]
    X_test, y_test = test[VARIABLES_PREDICTION], test[CIBLE_PREDICTION]
    print("Prévoir la température dans 3 heures")
    print(f"  exemples d'entraînement : {len(X_entrainement)}")
    print(f"  exemples de test        : {len(X_test)}")

    # 3. Entraîner : la forêt apprend sur la partie entraînement.
    modele = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    modele.fit(X_entrainement, y_entrainement)

    # 4. Évaluer : erreur moyenne en °C (MAE). Plus elle est basse, mieux c'est.
    #    La baseline « persistance » : dans 3 h, il fera la même température que maintenant.
    previsions = modele.predict(X_test)
    mae_baseline = mean_absolute_error(y_test, X_test["temperature"])
    mae_entrainement = mean_absolute_error(y_entrainement, modele.predict(X_entrainement))
    mae_test = mean_absolute_error(y_test, previsions)
    print("\nErreur moyenne (MAE), en °C : plus c'est bas, mieux c'est")
    print(f"  baseline « persistance »    : {mae_baseline:.2f} °C")
    print(f"  forêt, sur l'entraînement   : {mae_entrainement:.2f} °C")
    print(f"  forêt, sur le test          : {mae_test:.2f} °C")

    # 5. Enregistrer le modèle, avec ce qu'il faut savoir pour le réutiliser.
    FICHIER_MODELE.parent.mkdir(exist_ok=True)
    joblib.dump({
        "modele": modele,
        "variables": VARIABLES_PREDICTION,
        "mae_test": round(float(mae_test), 2),
        "date_entrainement": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, FICHIER_MODELE, compress=3)
    print(f"\nModèle enregistré : {FICHIER_MODELE.as_posix()}")

    # 6. Tracer une semaine du test : ce qui était prévu, ce qu'il a vraiment fait.
    reel = y_test.sort_index().loc[SEMAINE_TRACEE[0]:SEMAINE_TRACEE[1]]
    prevu = modele.predict(X_test.loc[reel.index])
    GRAPHIQUE.parent.mkdir(exist_ok=True)
    figure, axe = plt.subplots(figsize=(11, 4.5))
    axe.plot(reel.index, reel, color="#2c3e50", marker="o", markersize=3, linewidth=1.2, label="réel")
    axe.plot(reel.index, prevu, color="#e67e22", marker="o", markersize=3, linewidth=1.2, linestyle="--", label="prévu 3 h avant")
    axe.set_title("Température dans 3 h : prévision et réalité (7 jours du jeu de test)")
    axe.set_ylabel("°C")
    axe.grid(alpha=0.3)
    axe.legend()
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.savefig(GRAPHIQUE, dpi=110)
    plt.close(figure)
    print(f"Graphique         : {GRAPHIQUE.as_posix()}")


if __name__ == "__main__":
    main()
