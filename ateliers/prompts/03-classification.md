<!--
Atelier 3 — faites un commit avant de lancer : --force remplace le fichier.

python bin/ia "Complète les TODO" --prompt-file ateliers/prompts/03-classification.md --file ml/entrainer_categorie.py --file ml/preparation.py --out ml/entrainer_categorie.py --force

Puis : python ml/entrainer_categorie.py
-->

Complète les TODO de ml/entrainer_categorie.py (fichier joint) : le script doit entraîner un modèle
qui devine l'état du ciel (Dégagé, Nuageux, Brouillard, Précipitations) à partir d'un relevé.

Ce que le script doit faire, dans l'ordre des TODO :
1. charger l'historique et calculer les variables, avec charger() et ajouter_variables() ;
2. découper les données DANS LE TEMPS avec decouper() (jamais au hasard), puis afficher le nombre
   d'exemples d'entraînement et de test ;
3. entraîner RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1) ;
4. afficher l'exactitude de la baseline « toujours la catégorie la plus fréquente de l'entraînement »,
   l'exactitude de la forêt sur l'entraînement puis sur le test (en pourcentage), et le rapport par
   catégorie (classification_report avec labels=CLASSES et zero_division=0) ;
5. tracer la matrice de confusion dans GRAPHIQUE avec ConfusionMatrixDisplay.from_predictions
   (labels=CLASSES), titres des axes en français : « Réalité » en ligne, « Réponse du modèle » en colonne ;
6. enregistrer dans FICHIER_MODELE, avec joblib.dump(..., compress=3), le dictionnaire
   {"modele", "variables", "classes", "exactitude_test", "date_entrainement"}, où "classes" est
   list(modele.classes_).

Contraintes :
- garde tels quels les imports, les constantes (FICHIER_MODELE, GRAPHIQUE, CLASSES) et la ligne
  sys.stdout.reconfigure ; n'ajoute aucune bibliothèque ;
- réutilise les fonctions et les listes de ml/preparation.py (fichier joint), sans les recopier ;
- les entrées sont VARIABLES_CATEGORIE, la cible est CIBLE_CATEGORIE : weather_code et categorie
  ne sont jamais dans les entrées ;
- crée les dossiers modeles/ et rapports/ s'ils n'existent pas ;
- supprime le message « Rien n'est encore entraîné » ;
- un commentaire en français par étape, noms de variables en français ;
- renvoie le fichier complet.
