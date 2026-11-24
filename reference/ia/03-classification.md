… envoi à claude-sonnet-5-5
✔ fichier écrit : ml/entrainer_categorie.py — relisez-le, puis lancez les tests.
ℹ tokens : 4708 envoyés, 3337 reçus
```python
"""Entraîne le modèle qui devine l'état du ciel à partir d'un relevé.

    python ml/entrainer_categorie.py

Quatre catégories possibles : Dégagé, Nuageux, Brouillard, Précipitations.

Les noms ci-dessous sont imposés : l'API et SPEC-ML.md s'appuient dessus.
Le script ml/entrainer_prediction.py peut servir de modèle pour la forme, mais
attention : ici on devine une catégorie, pas un nombre.
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
    #    On écarte les relevés où une entrée ou la catégorie manque.
    historique = charger(CSV_HISTORIQUE)
    donnees = ajouter_variables(historique)
    donnees = donnees.dropna(subset=VARIABLES_CATEGORIE + [CIBLE_CATEGORIE])

    # 2. Découper dans le temps : le passé pour apprendre, le futur pour tester.
    entrainement, test = decouper(donnees)
    entrees_entrainement = entrainement[VARIABLES_CATEGORIE]
    reponses_entrainement = entrainement[CIBLE_CATEGORIE]
    entrees_test = test[VARIABLES_CATEGORIE]
    reponses_test = test[CIBLE_CATEGORIE]
    print(f"Exemples d'entraînement : {len(entrainement)}")
    print(f"Exemples de test : {len(test)}")

    # 3. Entraîner la forêt aléatoire.
    modele = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    modele.fit(entrees_entrainement, reponses_entrainement)

    # 4. Évaluer : baseline, forêt sur l'entraînement, forêt sur le test.
    categorie_la_plus_frequente = reponses_entrainement.mode()[0]
    exactitude_baseline = (reponses_test == categorie_la_plus_frequente).mean()
    predictions_entrainement = modele.predict(entrees_entrainement)
    exactitude_entrainement = accuracy_score(reponses_entrainement, predictions_entrainement)
    predictions_test = modele.predict(entrees_test)
    exactitude_test = accuracy_score(reponses_test, predictions_test)

    print(f"\nBaseline (toujours « {categorie_la_plus_frequente} ») : {exactitude_baseline:.1%} sur le test")
    print(f"Forêt sur l'entraînement : {exactitude_entrainement:.1%}")
    print(f"Forêt sur le test : {exactitude_test:.1%}")
    print("\nRapport par catégorie (test) :")
    print(classification_report(reponses_test, predictions_test, labels=CLASSES, zero_division=0))

    # 5. Tracer la matrice de confusion : réalité en ligne, réponse du modèle en colonne.
    GRAPHIQUE.parent.mkdir(parents=True, exist_ok=True)
    figure, axe = plt.subplots(figsize=(7, 6))
    ConfusionMatrixDisplay.from_predictions(
        reponses_test,
        predictions_test,
        labels=CLASSES,
        ax=axe,
        cmap="Blues",
    )
    axe.set_xlabel("Réponse du modèle")
    axe.set_ylabel("Réalité")
    axe.set_title("Matrice de confusion (jeu de test)")
    figure.tight_layout()
    figure.savefig(GRAPHIQUE)
    plt.close(figure)
    print(f"Matrice de confusion enregistrée : {GRAPHIQUE}")

    # 6. Enregistrer le modèle avec ce dont l'API a besoin pour s'en servir.
    FICHIER_MODELE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "modele": modele,
            "variables": VARIABLES_CATEGORIE,
            "classes": list(modele.classes_),
            "exactitude_test": float(exactitude_test),
            "date_entrainement": datetime.now(timezone.utc).isoformat(),
        },
        FICHIER_MODELE,
        compress=3,
    )
    print(f"Modèle enregistré : {FICHIER_MODELE}")


if __name__ == "__main__":
    main()
```

Remarques :
- **Lancement** : depuis la racine du projet, pour que `donnees/historique_blois.csv` soit trouvé.
- **Lignes écartées** : j'ai ajouté un `dropna` sur les entrées et la catégorie. Sans lui, un relevé avec une valeur manquante pourrait faire échouer l'entraînement. Le nombre d'exemples affiché en tient compte.
- **Comment lire les résultats** : si la forêt est très haute sur l'entraînement (proche de 100 %) mais plus basse sur le test, elle a en partie appris les exemples par cœur. Seul le score du test compte. Il doit être nettement au-dessus de la baseline, sinon le modèle n'apporte rien.
- **Spec** : `SPEC-ML.md` n'est pas joint. Je n'ai donc pas pu vérifier d'écart éventuel avec la spec, ni écrire le commentaire d'écart en tête de fichier.
