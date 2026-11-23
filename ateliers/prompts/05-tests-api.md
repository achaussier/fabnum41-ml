<!--
Atelier 5 — fichiers à joindre : api/main.py et SPEC-ML.md

python bin/ia "Teste les trois routes" --prompt-file ateliers/prompts/05-tests-api.md --file api/main.py --file SPEC-ML.md --out api/tests/test_routes.py

Puis : pytest api
-->

Écris les tests pytest des trois routes de l'API (api/main.py, fichier joint), d'après la section
« API » de SPEC-ML.md (fichier joint).

Cas à couvrir :
- GET /sante : 200, statut "ok", et les deux clés prediction et categorie dans "modeles" ;
- POST /predict/temperature, succès : 200, les cinq champs du contrat, grandeur "temperature",
  unite "°C", instant_prevu égal à l'instant du dernier relevé plus 3 heures, incertitude positive
  ou nulle, valeur_prevue dans une plage plausible (entre -40 et 60) ;
- POST /predict/temperature, erreurs 422 : 3 relevés au lieu de 4 ; relevés non consécutifs
  (deux heures d'écart entre deux relevés) ; humidité à 150 ;
- POST /classify/conditions, succès : 200, categorie parmi les quatre catégories, quatre probabilités
  entre 0 et 1 dont la somme vaut 1 à 0,02 près, et categorie est bien la plus probable ;
- POST /classify/conditions, erreur 422 : humidité à 150 ;
- modèle absent : 503 et code "modele_absent", pour chacune des deux routes POST ;
- toutes les erreurs ont la forme {"error": ..., "code": ...}.

Contraintes :
- utilise TestClient : from fastapi.testclient import TestClient, et from api import main ;
- construis les relevés avec une petite fonction releve(heure) qui renvoie un dictionnaire valide
  (reprends l'exemple de relevé de SPEC-ML.md), pour ne pas répéter les données ;
- ne teste JAMAIS une valeur prévue exacte : le modèle change à chaque entraînement ;
- pour simuler un modèle absent, utilise la fixture monkeypatch de pytest :
  monkeypatch.setitem(main.MODELES, "prediction", None) ;
- un test de succès a besoin du vrai modèle : si main.MODELES[...] vaut None, ignore ce test avec
  pytest.skip("modèle non entraîné") au lieu de le faire échouer ;
- un test par comportement, nom en français sans accent ; @pytest.mark.parametrize pour les cas d'erreur ;
- teste le CONTRAT de SPEC-ML.md, pas le code. Signale tout écart en commentaire en tête du fichier.
