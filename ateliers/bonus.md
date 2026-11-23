# Bonus

Pour celles et ceux qui ont terminé. À écrire avec `bin/ia`, sans prompt fourni (sauf le dernier) :
c'est à vous de rédiger la consigne, de joindre les bons fichiers et de vérifier le résultat.
Les solutions sont sur la branche `solutions`.

## A. Détecter les pannes de capteur

Fabriquez un historique simulé où des pannes ont été placées exprès :

```bash
python donnees/generer_synthetique.py --debut 2022-01-01 --jours 1461 --graine 42 --pannes --sortie donnees/synthetique.csv
```

La colonne `panne_injectee` dit où elles sont. Écrivez `ml/anomalies.py` :

- un `IsolationForest` (scikit-learn) cherche les relevés qui ne ressemblent pas aux autres, **sans** regarder `panne_injectee` ;
- on compare ensuite ses alertes à `panne_injectee` : combien de pannes retrouvées, combien de fausses alertes ?
- la sortie reprend les colonnes de la table `anomalie` : `INSTANT_MESURE_ANORMALE`, `VALEUR_MESUREE`,
  `SCORE_ANOMALIE`, `CODE_GRANDEUR` (voir `ateliers/station_meteo.sql`).

Indice : un capteur figé ne se voit pas sur un relevé isolé. Donnez au modèle l'**écart avec l'heure précédente**.

## B. Enregistrer les prévisions

Écrivez `api/stockage.py` : si la variable `MYSQL_DSN` est définie dans `.env`, chaque réponse de l'API est
insérée dans la table `resultat_ia` (`TYPE_RESULTAT` vaut `PREVISION_TEMPERATURE` ou `CATEGORIE`).
Si elle n'est pas définie, l'API fonctionne comme avant.

```bash
pip install -r requirements-bonus.txt
```

Indice : une panne de la base ne doit **jamais** empêcher l'API de répondre.

## C. Regrouper les journées

Écrivez `ml/regrouper.py` : un `KMeans` à 4 groupes sur des **journées** (température moyenne, amplitude,
pluie du jour, vent moyen…). Affichez la moyenne de chaque groupe, puis donnez-lui un nom
(« belle journée d'été », « journée de pluie »…). Ici, il n'y a pas de bonne réponse à retrouver :
c'est vous qui interprétez.

Indice : `KMeans` compare des distances. Mettez les colonnes à la même échelle avec `StandardScaler`.

## D. Imaginer la suite

```bash
python bin/ia "Propose trois cas d'usage" --prompt-file ateliers/prompts/06-cas-usage.md --file ateliers/station_meteo.sql --file SPEC-ML.md
```

Lequel des trois feriez-vous en premier ? De quelles données auriez-vous besoin ?

## E. Les vrais relevés de la borne

Envoyez l'historique dans votre base MongoDB, au format de la collection `mesures` :

```bash
python donnees/vers_mongo.py donnees/historique_blois.csv --sortie mesures.json
```

```bash
mongoimport --uri "votre-adresse-atlas" --collection mesures --jsonArray --file mesures.json
```

Puis exportez quatre vrais relevés consécutifs de la borne et envoyez-les à `/predict/temperature`.
Que répond l'API quand la pression manque ? Est-ce le bon comportement ?
