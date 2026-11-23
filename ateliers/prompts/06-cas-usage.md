<!--
Bonus « Imaginer la suite » — le dump SQL du MCD du projet est dans ateliers/station_meteo.sql

python bin/ia "Propose trois cas d'usage" --prompt-file ateliers/prompts/06-cas-usage.md --file ateliers/station_meteo.sql --file SPEC-ML.md
-->

Le fichier SQL joint décrit la base MySQL du projet de station météo. Quatre tables nous intéressent :
resultat_ia, anomalie, seuil et alerte. SPEC-ML.md (joint) décrit les deux modèles déjà en place :
la prévision de la température dans 3 heures et la catégorie d'état du ciel.

Propose TROIS nouveaux cas d'usage du machine learning pour cette station, différents des deux
modèles existants. Pour chacun, donne :
1. la question posée, en une phrase qu'un utilisateur du site comprendrait ;
2. la famille : prévoir un nombre, choisir une catégorie, repérer l'anormal, ou regrouper ;
3. les entrées : quelles mesures de la borne, sur quelle durée ;
4. la sortie, et la baseline naïve à battre ;
5. la table où enregistrer le résultat, avec les colonnes remplies et un exemple de ligne ;
6. un risque ou une limite, en une phrase.

Contraintes :
- n'utilise que des tables et des colonnes présentes dans le fichier SQL joint, avec leur nom exact ;
- reste réaliste : une seule borne, des relevés toutes les 10 minutes, peu d'historique réel ;
- pas de formule ; une page au maximum ;
- termine par le cas que tu ferais en premier, et pourquoi.
