# Bonus

Pour celles et ceux qui ont terminé les ateliers 0 à 5.

**Le but :** voler de vos propres ailes. Il n'y a plus de prompt fourni (sauf pour le bonus D) : c'est
à vous de rédiger la consigne, de choisir les fichiers à joindre et de vérifier le résultat, comme au
jour 2 quand vous aviez écrit votre propre scénario.

**Avant chaque appel à l'IA**, écrivez trois lignes dans `notes.md` :

1. ce que le script doit produire, et comment vous saurez qu'il est juste ;
2. les fichiers à joindre (l'IA ne voit que ceux-là) ;
3. la règle de `SPEC-ML.md` ou de `REGLES-IA.md` qui s'applique.

**Après**, relisez, lancez, et comparez à ce que vous aviez écrit en 1.

Les bonus sont indépendants : choisissez celui qui vous intéresse. Les solutions sont sur la branche `solutions`.

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

À réfléchir avant d'écrire : ici, il n'y a pas de catégorie à deviner, le modèle cherche seul ce qui est
« bizarre ». Un capteur figé pendant six heures donne-t-il une valeur bizarre ? Que faudrait-il montrer
au modèle pour qu'il le remarque ?

Et pour juger le résultat : retrouver toutes les pannes en sonnant mille fausses alertes, est-ce un bon détecteur ?

## B. Enregistrer les prévisions

Écrivez `api/stockage.py` : si la variable `MYSQL_DSN` est définie dans `.env`, chaque réponse de l'API est
insérée dans la table `resultat_ia` (`TYPE_RESULTAT` vaut `PREVISION_TEMPERATURE` ou `CATEGORIE`).
Si elle n'est pas définie, l'API fonctionne comme avant.

```bash
pip install -r requirements-bonus.txt
```

À réfléchir avant d'écrire : que doit répondre l'API si la base MySQL est en panne ? Comment le testeriez-vous
sans base de données ?

## C. Regrouper les journées

Écrivez `ml/regrouper.py` : un `KMeans` à 4 groupes sur des **journées** (température moyenne, amplitude,
pluie du jour, vent moyen…). Affichez la moyenne de chaque groupe, puis donnez-lui un nom
(« belle journée d'été », « journée de pluie »…). Ici, il n'y a pas de bonne réponse à retrouver :
c'est vous qui interprétez.

À réfléchir avant d'écrire : `KMeans` compare des distances. La pression tourne autour de 1 000, le vent
autour de 3 : laquelle des deux colonnes pèsera le plus, si l'on ne fait rien ?

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
