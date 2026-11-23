# Règles du projet Station météo (machine learning)

## Code
- Python 3.12 ou plus récent, scikit-learn, pandas, FastAPI
- Noms de variables, de fonctions et de tests en français
- N'utiliser que des fonctions qui existent dans les fichiers joints ou dans ces bibliothèques
- Réutiliser `ml/preparation.py` (charger, ajouter_variables, decouper) plutôt que réécrire

## Tests
- pytest, un test = un comportement, nom de test en français
- `SPEC-ML.md` fait foi, pas le code : on teste la règle
- Signaler tout écart entre le code et la spec, en commentaire en tête du fichier

## Machine learning
- Toujours découper les données dans le temps (`decouper()`), jamais au hasard
- Toujours comparer le modèle à une baseline naïve
- Ne jamais mettre `weather_code` ni `categorie` dans les variables d'entrée
- Mesurer sur le jeu de test, jamais sur les données d'entraînement

## Explications
- Public débutant, sans bagage mathématique : expliquer sans formule
- Phrases courtes, un exemple tiré de la station plutôt qu'une définition
