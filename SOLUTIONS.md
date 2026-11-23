# Solutions du jour 3

Cette branche (`solutions`) contient le dépôt une fois les ateliers 0 à 5 et les bonus terminés.
`pytest` y passe entièrement (46 tests).

Pour comparer avec le point de départ : `git diff main solutions -- station/decodeur.py`.

## Chiffres de référence

Obtenus avec `donnees/historique_blois.csv` (35 064 relevés), jeu de test = année 2025.
Les forêts sont entraînées avec `random_state=42` : vous devez retrouver ces chiffres au centième près.

### Prévision de la température dans 3 heures (erreur moyenne, MAE)

| | Erreur moyenne |
|---|---|
| **Baseline « persistance », sur 2025** | **2,06 °C** |
| **Forêt aléatoire, découpage dans le temps (test = 2025)** | **0,86 °C** |
| Forêt aléatoire, sur ses données d'entraînement | 0,28 °C |
| Forêt aléatoire, découpage au hasard (script de `main`) | 0,79 °C |
| Baseline « persistance », découpage au hasard | 1,96 °C |

**Pour la slide « Réflexe n°1 : battre une baseline » : baseline 2,06 °C, forêt aléatoire 0,86 °C.**

La forêt divise l'erreur de la baseline par 2,4. L'écart entre 0,28 °C (entraînement) et 0,86 °C (test)
illustre le sur-apprentissage : la forêt récite en partie ce qu'elle a vu.

### Catégorie d'état du ciel (test = 2025, 8 757 heures)

| | Exactitude |
|---|---|
| Baseline « toujours Nuageux » | 53,0 % |
| **Forêt aléatoire** | **74,9 %** |
| Forêt aléatoire, sur ses données d'entraînement | 100,0 % |

| Catégorie | Heures en 2025 | Rappel | Précision |
|---|---|---|---|
| Dégagé | 2 571 | 53 % | 66 % |
| Nuageux | 4 643 | 85 % | 73 % |
| Brouillard | 437 | 64 % | 93 % |
| Précipitations | 1 106 | 86 % | 100 % |

À dire aux stagiaires :

- **Précipitations** est presque un cadeau : la borne mesure la pluie (`precipitation`). Les 14 % manqués sont
  des heures que la source classe en pluie alors que le cumul de l'heure vaut 0,0 mm.
- **Brouillard** : un tiers des heures de brouillard est manqué (rappel de 64 %), presque toujours au profit de
  « Nuageux ». En revanche, quand le modèle dit « Brouillard », il a raison 93 fois sur 100. Catégorie rare
  (3,7 % des heures), et absente des dix premiers mois de 2022 dans la source.
- **Dégagé** est en réalité la catégorie la moins bien reconnue (rappel de 53 %) : la nuit, la luminosité vaut 0
  que le ciel soit clair ou couvert. Les capteurs de la borne ne « voient » pas les nuages dans le noir.
  C'est une limite des données, pas de l'algorithme.

## Les deux défauts volontaires de `main`

### Défaut n°1 : le décodeur (`station/decodeur.py`, atelier 0)

Il reprend les erreurs du collecteur d'origine (`mqtt_meteo.py`). Quatre écarts avec la section « Décodage »
de `SPEC-ML.md` :

| Écart | Avec le payload de référence | Attendu |
|---|---|---|
| humidité divisée par 10 | 9.1 | 91 |
| direction du vent divisée par 10 | 12.6 | 126 |
| pression non divisée par 10 | 10124 | 1012.4 hPa |
| payload de 40 caractères refusé | `ValueError` | 8 mesures, sans `rafale_max` ni `pluie_cumul` |

**Comment le trouver :** générer les tests depuis la spec (prompt 00), lancer `pytest station`.
Sur `main`, `station/tests/test_decodeur.py` donne 14 tests rouges sur 27 ; sur `solutions`, tout est vert.
Le test d'exemple fourni (`test_exemple.py`) ne vérifie que la température et la luminosité : il ne révèle rien.

Si l'IA produit des tests tous verts sur `main`, c'est qu'elle a recopié les valeurs du code au lieu de celles
de la spec : c'est le réflexe du jour 1 (« tester la règle, pas le code »).

### Défaut n°2 : le découpage au hasard (`ml/entrainer_prediction.py`, atelier 2)

Le script de `main` sépare entraînement et test avec `train_test_split(..., shuffle=True)` au lieu de `decouper()`.
Le test contient alors des heures encadrées par des heures d'entraînement : la note est trop belle.

| Découpage | Erreur sur le test |
|---|---|
| au hasard (`main`) | 0,79 °C |
| dans le temps (`solutions`) | 0,86 °C |

**Comment le trouver :** la règle n°1 de la section 4 de `SPEC-ML.md`, le réflexe n°2 du matin, ou le prompt 02.
Indice visuel : sur `main`, la courbe de `rapports/prediction_vs_reel.png` a des trous (un quart des heures seulement).

**À savoir avant d'animer :** l'écart est réel mais modeste, **8 %** (0,79 → 0,86 °C), et non les 15 % visés
par le cahier des charges. Plusieurs jeux de variables ont été essayés pour le creuser :

| Variables | Au hasard | Dans le temps | Écart |
|---|---|---|---|
| celles du cahier des charges | 0,81 | 0,86 | 6 % |
| **+ `jour_annee` (retenu)** | **0,79** | **0,86** | **8 %** |
| + `jour_annee`, `annee` et `pluie_cumul` | 0,78 | 0,88 | 12 % |
| + un numéro de ligne (la fuite la plus forte possible) | 0,80 | 0,91 | 13 % |
| sans les températures passées, + toutes les mesures | 0,77 | 0,90 | 15 % |

Avec les températures d'il y a 1 h et 3 h en entrée, le modèle tire peu de profit des heures voisines :
la fuite plafonne vers 12 %. Les deux dernières lignes dépassent ce plafond en dégradant le modèle honnête
(un compteur qui ne fait que grandir, ou la suppression de variables dont l'API a besoin) : elles n'ont pas été
retenues. Le message pédagogique tient avec 8 % : la première note était trop belle **et rien ne le signalait**.

## Bonus

### `ml/anomalies.py` (IsolationForest)

```bash
python donnees/generer_synthetique.py --debut 2022-01-01 --jours 1461 --graine 42 --pannes --sortie donnees/synthetique.csv
python ml/anomalies.py
```

592 relevés marqués `panne_injectee`. Le détecteur en signale 702 (2 %) et retrouve **277 pannes (47 %)**, avec
425 fausses alertes. Par type : presque tous les pics isolés, les deux tiers de la dérive d'humidité, très peu de
capteurs figés. Tirer au hasard 2 % des relevés n'en retrouverait que 2 %.

Discussion utile : un capteur figé se détecte mieux avec une **règle** (« même valeur depuis 6 heures ») qu'avec un
modèle. Le machine learning ne remplace pas les règles simples, il les complète.
La sortie `rapports/anomalies.csv` reprend les colonnes de la table `anomalie`.

### `api/stockage.py` (MySQL)

Si `MYSQL_DSN` est défini, chaque réponse est insérée dans `resultat_ia` :

| Route | `TYPE_RESULTAT` | Colonnes remplies |
|---|---|---|
| `/predict/temperature` | `PREVISION_TEMPERATURE` | `VALEUR_PREVUE`, `INCERTITUDE`, `INSTANT_PREVU`, `CODE_GRANDEUR` |
| `/classify/conditions` | `CATEGORIE` | `CONTENU_RESUME` (« Nuageux (probabilité 0.71) »), `INSTANT_PREVU` (instant du relevé) |

Deux points à adapter à la base réelle :

- `CODE_GRANDEUR` est une clé étrangère vers la table `grandeur`. Le code utilisé est `TEMPERATURE`
  (constante `CODE_GRANDEUR_TEMPERATURE`) : il doit exister dans `grandeur`, sinon l'insertion est refusée.
- Le dump fourni ne contient pas les contraintes `CHECK` (phpMyAdmin ne les exporte pas). Si `TYPE_RESULTAT`
  est limité à une liste de valeurs, il faut y ajouter `PREVISION_TEMPERATURE` et `CATEGORIE`.

Une panne de la base n'empêche jamais l'API de répondre : l'erreur part dans le journal d'uvicorn.

### `ml/regrouper.py` (KMeans)

```bash
python ml/regrouper.py
```

Quatre groupes de journées. Une lecture possible des moyennes :

| Groupe | Jours | Ce qu'on y voit | Nom possible |
|---|---|---|---|
| 0 | 273 | 8 mm de pluie, pression basse (998 hPa), vent fort | journée de pluie |
| 1 | 357 | 20 °C, 14 °C d'amplitude, air sec, très lumineux | belle journée d'été |
| 2 | 370 | 6,5 °C, humide, pression haute, peu de lumière | journée d'hiver calme et grise |
| 3 | 461 | 14 °C, 9 °C d'amplitude, un peu de pluie | journée de mi-saison |

Il n'y a pas de « bonne » réponse : c'est le propre du non supervisé.

### Prompt 06 (cas d'usage)

Pas de corrigé unique. Réponses attendues : alerte anticipée de gel ou de canicule (tables `seuil` et `alerte`),
estimation d'une mesure manquante, détection de capteur défaillant (table `anomalie`), résumé quotidien rédigé
par un modèle de langage (`CONTENU_RESUME`).

## Ce qui n'a pas été vérifié

- Les prompts n'ont pas été joués contre l'API Claude réelle (pas de clé disponible le jour de la construction) :
  `bin/ia` a été vérifié en `--dry-run` et contre un faux serveur local. Jouez les prompts 00, 03 et 05 une fois
  avant la séance.
- Les scripts ont été lancés sous Linux en Python 3.12, 3.13 et 3.14, pas sous Windows.
