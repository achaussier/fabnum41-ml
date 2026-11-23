"""Entraîne le modèle qui devine l'état du ciel à partir d'un relevé.

    python ml/entrainer_categorie.py

Quatre catégories possibles : Dégagé, Nuageux, Brouillard, Précipitations.
Le script affiche l'exactitude du modèle et celle d'une baseline, le rapport par
catégorie, trace rapports/matrice_confusion.png et enregistre modeles/categorie.joblib.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")  # on écrit un fichier PNG, sans ouvrir de fenêtre
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report

from preparation import CIBLE_CATEGORIE, CSV_HISTORIQUE, VARIABLES_CATEGORIE, ajouter_variables, charger, decouper

FICHIER_MODELE = Path("modeles/categorie.joblib")
GRAPHIQUE = Path("rapports/matrice_confusion.png")
CLASSES = ["Dégagé", "Nuageux", "Brouillard", "Précipitations"]

# Sous Windows, le terminal n'affiche pas toujours les accents : on force l'UTF-8.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    # 1. Charger l'historique et calculer les variables.
    donnees = ajouter_variables(charger(CSV_HISTORIQUE))

    # 2. Découper DANS LE TEMPS : avant 2025 pour apprendre, 2025 pour tester.
    entrainement, test = decouper(donnees)
    X_entrainement, y_entrainement = entrainement[VARIABLES_CATEGORIE], entrainement[CIBLE_CATEGORIE]
    X_test, y_test = test[VARIABLES_CATEGORIE], test[CIBLE_CATEGORIE]
    print("Deviner l'état du ciel")
    print(f"  exemples d'entraînement : {len(X_entrainement)}")
    print(f"  exemples de test        : {len(X_test)}")

    # 3. Entraîner la forêt.
    modele = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    modele.fit(X_entrainement, y_entrainement)

    # 4. Évaluer. L'exactitude est la part de bonnes réponses.
    #    La baseline : répondre toujours la catégorie la plus fréquente de l'entraînement.
    previsions = modele.predict(X_test)
    plus_frequente = y_entrainement.mode()[0]
    exactitude_baseline = accuracy_score(y_test, [plus_frequente] * len(y_test))
    exactitude_entrainement = accuracy_score(y_entrainement, modele.predict(X_entrainement))
    exactitude_test = accuracy_score(y_test, previsions)
    print("\nExactitude (part de bonnes réponses) : plus c'est haut, mieux c'est")
    print(f"  baseline « toujours {plus_frequente} »  : {exactitude_baseline:.1%}")
    print(f"  forêt, sur l'entraînement    : {exactitude_entrainement:.1%}")
    print(f"  forêt, sur le test           : {exactitude_test:.1%}")

    # Le rapport par catégorie. « recall » est le rappel : sur 100 heures de
    # brouillard, combien le modèle en a-t-il reconnu ?
    print("\nRapport par catégorie")
    print(classification_report(y_test, previsions, labels=CLASSES, zero_division=0))

    # 5. Tracer la matrice de confusion : en ligne la réalité, en colonne la réponse du modèle.
    GRAPHIQUE.parent.mkdir(exist_ok=True)
    figure, axe = plt.subplots(figsize=(7, 6))
    ConfusionMatrixDisplay.from_predictions(y_test, previsions, labels=CLASSES, cmap="Blues", colorbar=False, ax=axe)
    axe.set_title("Matrice de confusion (jeu de test : 2025)")
    axe.set_xlabel("Réponse du modèle")
    axe.set_ylabel("Réalité")
    figure.tight_layout()
    figure.savefig(GRAPHIQUE, dpi=110)
    plt.close(figure)
    print(f"Graphique         : {GRAPHIQUE.as_posix()}")

    # 6. Enregistrer le modèle, avec ce qu'il faut savoir pour le réutiliser.
    FICHIER_MODELE.parent.mkdir(exist_ok=True)
    joblib.dump({
        "modele": modele,
        "variables": VARIABLES_CATEGORIE,
        "classes": list(modele.classes_),
        "exactitude_test": round(float(exactitude_test), 3),
        "date_entrainement": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, FICHIER_MODELE, compress=3)
    print(f"Modèle enregistré : {FICHIER_MODELE.as_posix()}")


if __name__ == "__main__":
    main()
