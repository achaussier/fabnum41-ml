<!--
Atelier 0 — fichiers à joindre : SPEC-ML.md et station/decodeur.py

python bin/ia "Écris les tests de decoder()" --prompt-file ateliers/prompts/00-tests-decodeur.md --file SPEC-ML.md --file station/decodeur.py --out station/tests/test_decodeur.py

Puis : pytest station
-->

Écris des tests pytest pour la fonction decoder() de station/decodeur.py (fichier joint).

La règle à tester est la section « Décodage » de SPEC-ML.md (fichier joint), pas le code.

Cas à couvrir :
- le payload de référence (40 caractères) : chacune des huit valeurs attendues du tableau,
  et l'absence des clés rafale_max et pluie_cumul ;
- le payload complet (54 caractères) : chacune des dix valeurs attendues du tableau ;
- le type des valeurs : humidite, luminosite et vent_direction sont des entiers (int) ;
- une température négative ;
- un payload en minuscules ;
- un payload trop court, et un payload qui n'est pas de l'hexadécimal : ValueError.

Contraintes :
- importe la fonction ainsi : from station.decodeur import decoder
- un test par comportement, nom de test en français, sans accent dans le nom de la fonction ;
- pour les décimaux, compare avec pytest.approx ;
- utilise @pytest.mark.parametrize pour les tableaux de valeurs attendues, afin qu'une valeur
  fausse n'empêche pas de voir les autres ;
- recopie les payloads et les valeurs attendues depuis SPEC-ML.md, sans les recalculer avec le code ;
- teste la RÈGLE, pas le code. Si le code contredit la spec, écris quand même le test d'après
  la spec, et signale chaque écart dans un commentaire en tête du fichier.
