# Solutions du jour 3

Cette branche (`solutions`) contient le dépôt une fois les ateliers 0 à 5 et les bonus terminés.
`pytest` y passe entièrement (59 tests, une fois les deux modèles entraînés).

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

Il reprend les erreurs du collecteur d'origine (`mqtt_meteo.py`). Cinq écarts avec la section « Décodage »
de `SPEC-ML.md` :

| Écart | Avec le payload de référence | Attendu |
|---|---|---|
| humidité divisée par 10 | 9.1 | 91 |
| direction du vent divisée par 10 | 12.6 | 126 |
| pression non divisée par 10 | 10124 | 1012.4 hPa |
| payload de 40 caractères refusé | `ValueError` | 8 mesures, sans `rafale_max` ni `pluie_cumul` |
| identifiant de bloc non hexadécimal accepté (`ZZ…`) | décodé sans erreur | `ValueError` |

Le cinquième écart a été trouvé par l'IA lors de l'essai du prompt 00 : le décodeur ne lit pas les
identifiants de bloc, donc il ne les contrôle pas. Tous les stagiaires ne l'auront pas, selon les tests
que l'IA leur écrit. C'est une bonne occasion de comparer les fichiers de tests entre voisins.

**Comment le trouver :** générer les tests depuis la spec (prompt 00), lancer `pytest station`.
Sur `main`, `station/tests/test_decodeur.py` donne 15 tests rouges sur 30 ; sur `solutions`, tout est vert.
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

## Réponses attendues du carnet de bord (`notes.md`)

Les stagiaires répondent en deux lignes. Ce qui compte est le raisonnement, pas la formulation.

### Atelier 0

- **0.1** Avec le payload complet : humidité 8.8 au lieu de 88, direction 1.2 au lieu de 12, pression 10091 au
  lieu de 1009.1. Avec le payload de référence : `ValueError`, alors qu'il est valide.
- **0.2** Dans tous les cas attendus, le test suit la spec et le code a tort. Si un stagiaire trouve un test
  faux, c'est une trouvaille : faites-la partager.
- **0.3** Cinq (tableau ci-dessus). Quatre est une bonne réponse si l'IA n'a pas testé les identifiants de bloc.
- **0.4** Le test fourni ne regarde que la température et la luminosité, deux valeurs que le décodeur calcule
  bien. Un test vert ne dit rien de ce qu'il ne regarde pas.
- **0.5** Non. La pluie vaut 0 dans les deux payloads de la spec, et 0 / 100 = 0 / 1000. La ligne est pourtant
  « couverte » au sens du jour 1 : la couverture mesure ce qui est exécuté, pas ce qui est vérifié. Le test
  qui manque est dans `station/tests/test_decodeur.py` (`test_une_pluie_non_nulle_est_decodee`).

### Atelier 1

- **1.1** -9,6 °C et 38,2 °C : plausible à Blois, et dans la plage -40 à 85 de la spec.
- **1.2** Nuageux, 56,5 % des heures. Un « modèle » qui répondrait toujours Nuageux aurait donc 56,5 % sur tout
  l'historique (53,0 % sur 2025 seul, le chiffre de l'atelier 3).
- **1.3** Elle baisse dans les heures qui précèdent. Pas à chaque fois, ni de la même hauteur : c'est une
  tendance, pas une loi.
- **1.4** Libre. Vérifiable : les dates des épisodes de pluie d'octobre 2024. Non vérifiable : tout ce qui porte
  sur la température ou sur les autres mois, absents des deux images.
- **1.5** Pronostic libre. La réponse (question 2.6) : `temperature` et `heure`.

### Atelier 2

- **2.1** Baseline 1,96 °C, entraînement 0,29 °C, test 0,79 °C.
- **2.2** `train_test_split(X, y, test_size=0.25, shuffle=True, random_state=42)` contredit la règle n°1 de la
  section 4. Essai du 24 novembre 2026 : l'IA la trouve du premier coup.
- **2.3** Elle monte. Avant, le modèle était interrogé sur des heures dont il connaissait les voisines.
- **2.4** Au hasard 0,79 °C ; dans le temps 0,86 °C ; baseline (sur 2025) 2,06 °C.
- **2.5** Les tests vérifient du code contre une règle (le décodeur, l'API). Aucun ne vérifiait la **façon de
  mesurer**. Le défaut a été révélé par une relecture du script contre la spec. La rubrique « Pour aller plus
  loin » fait écrire les tests qui manquaient : `ml/tests/test_preparation.py`.
- **2.6** Importance des variables : `temperature` 0,88, `heure` 0,07, `luminosite` 0,01. Les autres pèsent moins.

### Atelier 3

- **3.1** Pronostic libre. Beaucoup répondront « Brouillard » (rare). La réponse est « Dégagé ».
- **3.2** `decouper()`, entrées = `VARIABLES_CATEGORIE`. Lors de l'essai, l'IA a ajouté un `dropna` non demandé
  (sans effet ici : aucune valeur ne manque) et a signalé que `SPEC-ML.md` n'était pas joint.
- **3.3** Baseline 53,0 %, entraînement 100,0 %, test 74,9 %. L'écart 100 / 75 est le « par cœur » de l'atelier 2.
- **3.4** Rappels : Dégagé 53 %, Nuageux 85 %, Brouillard 64 %, Précipitations 86 %.
- **3.5** La nuit, la luminosité et l'indice UV valent 0, que le ciel soit clair ou couvert : il ne reste rien
  pour les distinguer. C'est une limite des capteurs. Lors de l'essai, l'IA a répondu « je ne connais pas la
  liste exacte de vos capteurs » : il fallait joindre `SPEC-ML.md` (étape 7 du guide).
- **Pour aller plus loin** : avec `weather_code` en entrée, l'exactitude sur le test atteint 100,0 %. Le modèle
  lit la réponse.

### Atelier 4

- **4.1** `temperature_moins_3h`, `variation_pression_3h` et `humidite_moins_3h` demandent le relevé de 3 heures
  plus tôt : il faut 4 relevés qui se suivent. `VARIABLES_CATEGORIE` ne contient que des mesures de l'instant.
- **4.2** Les 200 arbres de la forêt donnent chacun une prévision ; l'incertitude est leur désaccord
  (l'écart-type). « Les arbres ne sont pas d'accord à plus ou moins 2 °C près. »
- **4.3** Vérifier que le modèle est chargé (sinon 503) ; mettre le relevé en tableau ; ajouter `heure` et
  `mois` ; garder les colonnes du modèle ; demander les probabilités ; renvoyer la plus probable et les quatre.
- **4.4** Libre. Oubli le plus fréquent dans les étapes écrites à la main : le cas « modèle absent ».
- **Requête n°5** : c'est Pydantic qui la refuse (`humidite: int = Field(ge=0, le=100)`), et le gestionnaire
  `RequestValidationError` qui lui donne la forme `{"error", "code"}`.

### Atelier 5

- **5.1 et 5.2** Libres. Lors de l'essai, l'IA a ajouté cinq relevés, l'ordre inversé, un champ manquant et la
  règle « la validation passe avant la vérification du modèle ».
- **5.3** Le test sur `instant_prevu` (dernier relevé + 3 heures).
- **5.4** Le vert garantit le contrat : formats, codes, validation. Il ne garantit pas que le modèle est bon :
  un modèle qui répondrait toujours 12 °C laisserait tout vert. La qualité se lit dans la note mesurée à
  l'entraînement (`mae_test`, `exactitude_test`) et dans la comparaison à la baseline.

**Un `xfailed` à l'atelier 5.** Lors de l'essai, l'IA a écrit un test `xfail` : la section 1 de la spec dit que
`reference_capteur` fait 16 caractères, et l'API ne le contrôle pas. La spec ne dit pas si cette règle
s'applique à l'API. C'est la bonne discussion à avoir : quand la spec ne tranche pas, on la complète, on ne
choisit pas en silence. Sur cette branche, l'API n'impose pas de longueur.

## Essai des prompts contre l'API réelle

Joués le 24 novembre 2026 avec `claude-sonnet-5-5`, dans un clone neuf de `main`, dans l'ordre des ateliers.
Les réponses varient d'un appel à l'autre : vos stagiaires n'obtiendront pas exactement la même chose.

| Prompt | Résultat |
|---|---|
| 00 | 36 tests écrits ; 20 rouges sur `main` ; six écarts annoncés en tête de fichier, tous réels ; 36 verts avec le décodeur de cette branche |
| 01 | description juste des deux images, épisodes de pluie bien datés |
| 02 | le découpage au hasard est trouvé du premier coup, avec la ligne et la règle ; depuis sa réécriture, le prompt ne donne plus le code corrigé, mais la fonction à utiliser et deux questions |
| 03 | script complet, qui tourne du premier coup et retrouve 53,0 % / 100,0 % / 74,9 % |
| 03b | chiffres lus correctement sur l'image ; explication physique vague tant que la spec n'est pas jointe |
| 04 | fonction correcte, collée telle quelle : 200 sur la requête n°4, 422 sur la n°5 |
| 05 | 30 tests : 29 verts et 1 `xfailed` (voir ci-dessus) ; le passage de `hours=3` à `hours=2` est détecté |
| 06 | trois cas d'usage réalistes, avec les colonnes exactes des tables |

Coût de l'ensemble : environ 60 000 jetons envoyés et 30 000 reçus par stagiaire.

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

- Les scripts ont été lancés sous Linux en Python 3.12, 3.13 et 3.14, pas sous Windows.
- Les durées des ateliers : les guides demandent maintenant un pronostic et des réponses écrites dans
  `notes.md`. Si le temps manque, l'étape « casser exprès » de l'atelier 0 et la question 2.6 peuvent sauter.
- `pytest` affiche `1 warning` (une bibliothèque de test annonce un changement à venir) : sans conséquence.
