<!--
Atelier 2 — à lancer après : python ml/entrainer_prediction.py

python bin/ia "Ce résultat est-il fiable ?" --prompt-file ateliers/prompts/02-critiquer-entrainement.md --file ml/entrainer_prediction.py --file ml/preparation.py --file SPEC-ML.md

Astuce : collez aussi les erreurs affichées par le script dans la consigne, entre les guillemets.
-->

Relis le script ml/entrainer_prediction.py (fichier joint). Il entraîne un modèle qui prévoit la
température dans 3 heures et affiche son erreur moyenne. ml/preparation.py et SPEC-ML.md sont joints.

Réponds à ces questions, dans l'ordre :
1. Le script respecte-t-il toutes les règles de SPEC-ML.md (sections 2 et 4) ? Cite chaque écart avec
   la ligne de code concernée et la règle qu'elle contredit.
2. L'erreur affichée « sur le test » est-elle digne de confiance ? Explique pourquoi avec une image
   simple (par exemple un examen), sans formule.
3. Le modèle est-il bien comparé à une baseline ? Laquelle ?
4. Que faut-il modifier, précisément ? Donne uniquement les lignes à changer, en réutilisant
   les fonctions qui existent déjà dans ml/preparation.py.
5. Après correction, l'erreur affichée va-t-elle monter ou descendre ? Pourquoi est-ce une bonne nouvelle ?

Contraintes :
- ne signale que des problèmes réellement présents dans les fichiers joints ;
- ne réécris pas tout le script.
