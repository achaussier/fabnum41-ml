"""Entraîne le modèle qui devine l'état du ciel à partir d'un relevé.

    python ml/entrainer_categorie.py

Quatre catégories possibles : Dégagé, Nuageux, Brouillard, Précipitations.

SQUELETTE À COMPLÉTER (atelier 3). Les noms ci-dessous sont imposés : l'API et
SPEC-ML.md s'appuient dessus. Le script ml/entrainer_prediction.py peut servir de
modèle pour la forme, mais attention : ici on devine une catégorie, pas un nombre.
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
    # TODO 1. Charger l'historique (CSV_HISTORIQUE) et calculer les variables,
    #         avec charger() et ajouter_variables() de preparation.py.

    # TODO 2. Découper les données en deux parties, entraînement et test.
    #         Les entrées sont les colonnes VARIABLES_CATEGORIE, la cible est CIBLE_CATEGORIE.
    #         Afficher le nombre d'exemples de chaque partie.

    # TODO 3. Entraîner un RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1).

    # TODO 4. Évaluer sur le test et afficher :
    #         - l'exactitude de la baseline « toujours la catégorie la plus fréquente »
    #           (la plus fréquente dans l'entraînement) ;
    #         - l'exactitude de la forêt sur l'entraînement, puis sur le test ;
    #         - le rapport par catégorie (classification_report, labels=CLASSES).

    # TODO 5. Tracer la matrice de confusion dans GRAPHIQUE (rapports/matrice_confusion.png) :
    #         en ligne la réalité, en colonne la réponse du modèle, dans l'ordre de CLASSES.

    # TODO 6. Enregistrer dans FICHIER_MODELE (modeles/categorie.joblib) un dictionnaire :
    #         {"modele": ..., "variables": VARIABLES_CATEGORIE, "classes": liste des classes du modèle,
    #          "exactitude_test": ..., "date_entrainement": ...}
    #         avec joblib.dump(..., compress=3), comme dans entrainer_prediction.py.

    print("Rien n'est encore entraîné : complétez les TODO de ml/entrainer_categorie.py (atelier 3).")


if __name__ == "__main__":
    main()
