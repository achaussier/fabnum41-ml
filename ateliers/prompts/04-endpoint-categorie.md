<!--
Atelier 4 — fichiers à joindre : api/main.py et SPEC-ML.md

python bin/ia "Écris /classify/conditions" --prompt-file ateliers/prompts/04-endpoint-categorie.md --file api/main.py --file SPEC-ML.md

Pas de --out : la réponse s'affiche, vous recopiez la fonction dans api/main.py à la place du TODO.
-->

Écris la route POST /classify/conditions de api/main.py (fichier joint), à la place du TODO de la
fonction categoriser_conditions().

Le contrat est la section « API » de SPEC-ML.md (fichier joint). Prends modèle sur la fonction
prevoir_temperature(), qui est juste au-dessus dans le même fichier.

Ce que la route doit faire :
- si MODELES["categorie"] vaut None : répondre 503 avec erreur(503, ..., "modele_absent") ;
- transformer le relevé reçu en tableau avec vers_tableau([requete.releve]) ;
- y ajouter les colonnes heure et mois, calculées à partir de l'index du tableau (la date du relevé) ;
- garder les colonnes paquet["variables"], dans cet ordre ;
- demander au modèle la probabilité de chaque catégorie avec predict_proba ; les catégories sont
  dans paquet["classes"], dans le même ordre que les probabilités ;
- répondre {"categorie": la plus probable, "probabilites": {catégorie: probabilité arrondie à 0,01}},
  avec des float Python (pas des nombres numpy).

Contraintes :
- n'utilise que les fonctions, les modèles Pydantic et les imports déjà présents dans api/main.py ;
- n'appelle pas ajouter_variables() ici : elle a besoin de plusieurs relevés consécutifs ;
- ne modifie ni les autres routes ni les modèles Pydantic ;
- réponds avec la fonction categoriser_conditions() complète, décorateur compris, dans un seul bloc
  de code, puis explique en trois lignes ce que fait predict_proba.
