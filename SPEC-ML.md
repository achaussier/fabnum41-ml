# SPEC-ML : ce que les modèles et l'API doivent faire

Ce document **fait foi**. Si le code le contredit, c'est le code qui a tort.
C'est lui que l'on joint à l'IA (`--file SPEC-ML.md`), pas le code.

Station : borne SenseCAP S2120 installée à **Blois (41)**, référence `9B85D927590B5B28`.

## 1. Les données

Fichier `donnees/historique_blois.csv` : un relevé par heure, du 1er janvier 2022 au 31 décembre 2025
(35 064 lignes), aux mêmes noms que la collection MongoDB `mesures`.

| Colonne | Type | Unité | Plage autorisée |
|---|---|---|---|
| `reference_capteur` | texte | – | 16 caractères |
| `instant_mesure` | date et heure UTC (`2025-03-14T09:00:00Z`) | – | – |
| `temperature` | décimal | °C | -40 à 85 |
| `humidite` | entier | % | 0 à 100 |
| `pression_atmospherique` | décimal | hPa | 300 à 1100 |
| `vent_vitesse` | décimal | m/s | 0 à 60 |
| `vent_direction` | entier | ° | 0 à 359 |
| `rafale_max` | décimal | m/s | 0 à 60 |
| `precipitation` | décimal | mm/h | 0 à 240 |
| `pluie_cumul` | décimal | mm | 0 ou plus |
| `luminosite` | entier | lux | 0 à 200 000 |
| `indice_uv` | décimal | – | 0 à 15 |
| `weather_code` | entier | code météo WMO | étiquette, jamais en entrée |
| `categorie` | texte | – | étiquette, jamais en entrée |

Les plages sont celles du dictionnaire de données du projet.

### Les catégories

| `categorie` | Codes WMO | Signification |
|---|---|---|
| `Dégagé` | 0, 1 | ciel clair, peu nuageux (de jour comme de nuit) |
| `Nuageux` | 2, 3 | partiellement nuageux, couvert |
| `Brouillard` | 45, 48 | brouillard |
| `Précipitations` | 51 et plus | bruine, pluie, neige, averses, orage |

`Brouillard` est rare (moins de 4 % des heures) : les classes sont déséquilibrées.

## 2. Modèle n°1 : prévoir la température dans 3 heures

- **Problème** : à partir des relevés des dernières heures, donner la température qu'il fera 3 heures plus tard.
  On prévoit un nombre.
- **Entrées** (`VARIABLES_PREDICTION` dans `ml/preparation.py`) : l'heure, le mois, le jour de l'année, la température,
  l'humidité, la pression, la vitesse du vent, la luminosité, la température 1 heure et 3 heures plus tôt,
  la variation de la pression sur 3 heures, l'humidité 3 heures plus tôt.
- **Sortie** : `temperature_dans_3h`, en °C.
- **Mesure de la qualité** : l'erreur moyenne en °C (MAE). « En moyenne, on se trompe de tant de degrés. »
  Plus elle est basse, mieux c'est.
- **Baseline à battre** : la « persistance ». Dans 3 heures, il fera la même température que maintenant.
- **Algorithme** : forêt aléatoire, `RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)`.
- **Fichier produit** : `modeles/prediction_temperature.joblib`, un dictionnaire
  `{modele, variables, mae_test, date_entrainement}`.

## 3. Modèle n°2 : deviner l'état du ciel

- **Problème** : à partir d'un seul relevé, dire si le ciel est `Dégagé`, `Nuageux`, dans le `Brouillard`
  ou s'il y a des `Précipitations`. On choisit une catégorie. La borne n'a pas de capteur pour cela.
- **Entrées** (`VARIABLES_CATEGORIE`) : l'heure, le mois, la température, l'humidité, la pression, la vitesse et
  la direction du vent, la rafale maximale, les précipitations, la luminosité, l'indice UV.
- **Sortie** : `categorie`, et la probabilité de chacune des quatre catégories.
- **Mesure de la qualité** : l'exactitude (la part de bonnes réponses) **et** le rappel de chaque catégorie
  (sur 100 heures de brouillard, combien le modèle en reconnaît-il ?). L'exactitude seule est trompeuse
  quand une catégorie domine.
- **Baseline à battre** : répondre toujours la catégorie la plus fréquente.
- **Algorithme** : forêt aléatoire, `RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)`.
- **Fichiers produits** : `modeles/categorie.joblib`, un dictionnaire
  `{modele, variables, classes, exactitude_test, date_entrainement}`, et `rapports/matrice_confusion.png`.

## 4. Deux règles pour tous les modèles

1. **On découpe dans le temps.** Les relevés d'avant le 1er janvier 2025 servent à l'entraînement, ceux de 2025
   servent au test (fonction `decouper()` de `ml/preparation.py`). On ne mélange jamais les lignes au hasard :
   deux relevés voisins se ressemblent trop, le modèle aurait la réponse sous les yeux et sa note serait trop belle.
2. **On compare toujours à une baseline.** Un modèle qui ne fait pas mieux que la réponse naïve ne sert à rien.

`weather_code` et `categorie` ne sont **jamais** des variables d'entrée.

## 5. API

Lancement : `uvicorn api.main:app --reload`, documentation interactive sur `http://localhost:8000/docs`.
Les modèles sont chargés au démarrage, dans le dictionnaire `MODELES` de `api/main.py`
(clés `prediction` et `categorie` ; la valeur est `None` si le fichier `.joblib` n'existe pas).

| Route | Corps envoyé | Réponse |
|---|---|---|
| `GET /sante` | – | 200 `{"statut":"ok","modeles":{"prediction":true,"categorie":false}}` |
| `POST /predict/temperature` | `{"releves":[R, R, R, R]}` | 200 `{"grandeur":"temperature","instant_prevu":"2025-03-14T12:00:00Z","valeur_prevue":14.2,"incertitude":1.1,"unite":"°C"}` |
| `POST /classify/conditions` | `{"releve": R}` | 200 `{"categorie":"Nuageux","probabilites":{"Dégagé":0.12,"Nuageux":0.71,"Brouillard":0.04,"Précipitations":0.13}}` |

**Un relevé `R`** contient les champs du tableau de la section 1, sans `weather_code` ni `categorie` :

```json
{"instant_mesure": "2025-03-14T09:00:00Z", "temperature": 3.3, "humidite": 82,
 "pression_atmospherique": 997.9, "vent_vitesse": 3.3, "vent_direction": 43, "rafale_max": 6.1,
 "precipitation": 0.0, "pluie_cumul": 2629.2, "luminosite": 24360, "indice_uv": 1.8}
```

`reference_capteur` et `pluie_cumul` sont facultatifs, tous les autres champs sont obligatoires.

**`GET /sante`** répond toujours 200. `modeles` indique, pour chaque modèle, s'il est chargé.

**`POST /predict/temperature`**
- reçoit **exactement 4 relevés**, espacés d'**une heure exactement**, du plus ancien au plus récent ;
- `instant_prevu` : l'instant du dernier relevé plus 3 heures, au format `2025-03-14T12:00:00Z` ;
- `valeur_prevue` : la température prévue, arrondie à 0,1 ;
- `incertitude` : le désaccord entre les arbres de la forêt (l'écart-type de leurs prévisions), arrondi à 0,1 ;
- `grandeur` vaut toujours `"temperature"` et `unite` vaut toujours `"°C"`.

**`POST /classify/conditions`**
- reçoit **un** relevé ;
- `categorie` : la catégorie la plus probable ;
- `probabilites` : les quatre catégories, chacune avec une probabilité entre 0 et 1 arrondie à 0,01
  (leur somme vaut 1, à l'arrondi près).

**Erreurs.** Toutes ont la forme `{"error": "message lisible", "code": "identifiant_court"}`.

| Code HTTP | `code` | Quand |
|---|---|---|
| 422 | `requete_invalide` | il n'y a pas exactement 4 relevés ; ils ne se suivent pas d'heure en heure ; un champ obligatoire manque ; une valeur sort de sa plage (humidité à 150, par exemple) |
| 503 | `modele_absent` | le modèle demandé n'a pas été entraîné (fichier `.joblib` absent) |

La validation de la requête passe **avant** la vérification du modèle : une requête invalide reçoit 422 même si le modèle est absent.

Les noms `valeur_prevue`, `incertitude` et `instant_prevu` reprennent les colonnes de la table MySQL `resultat_ia`
(`VALEUR_PREVUE`, `INCERTITUDE`, `INSTANT_PREVU`) : la réponse de l'API peut y être enregistrée telle quelle.

## 6. Décodage

La borne envoie ses mesures dans un texte hexadécimal, le *payload*. La fonction
`decoder(payload_hex)` de `station/decodeur.py` le transforme en dictionnaire.

Le payload est fait de blocs. Chaque bloc commence par un identifiant d'un octet (2 caractères), que l'on ignore.

| Caractères | Mesure | Calcul | Clé renvoyée | Unité |
|---|---|---|---|---|
| `[0:2]` | identifiant du bloc 1 | – | – | – |
| `[2:6]` | température | valeur / 10 (peut être négative) | `temperature` | °C |
| `[6:8]` | humidité | valeur telle quelle (entier) | `humidite` | % |
| `[8:16]` | luminosité | valeur telle quelle (entier) | `luminosite` | lux |
| `[16:18]` | indice UV | valeur / 10 | `indice_uv` | – |
| `[18:22]` | vitesse du vent | valeur / 10 | `vent_vitesse` | m/s |
| `[22:24]` | identifiant du bloc 2 | – | – | – |
| `[24:28]` | direction du vent | valeur telle quelle (entier) | `vent_direction` | ° |
| `[28:36]` | intensité de la pluie | valeur / 1000 | `precipitation` | mm/h |
| `[36:40]` | pression | valeur / 10 | `pression_atmospherique` | hPa |
| `[40:42]` | identifiant du bloc 3 | – | – | – |
| `[42:46]` | rafale maximale | valeur / 10 | `rafale_max` | m/s |
| `[46:54]` | cumul de pluie | valeur / 10 | `pluie_cumul` | mm |

Règles :

- Un payload **complet** fait 54 caractères (trois blocs) : les dix mesures sont renvoyées.
- Un payload de **40 caractères** (deux blocs, anciens micrologiciels) est **valide** : les huit premières mesures
  sont renvoyées, et les clés `rafale_max` et `pluie_cumul` sont **absentes** du dictionnaire.
- `humidite`, `luminosite` et `vent_direction` sont des **entiers** ; les autres valeurs sont des décimaux.
- La température est signée : `FFF2` vaut -14, soit -1,4 °C.
- Les lettres hexadécimales peuvent être en majuscules ou en minuscules.
- Un payload de moins de 40 caractères, ou qui contient autre chose que de l'hexadécimal, lève une `ValueError`.

**Payload de référence** (40 caractères, décodé par le codec officiel du fabricant) :

```
01010A5B0001C86160000902007E00000000278C
```

| Clé | Valeur attendue |
|---|---|
| `temperature` | 26.6 |
| `humidite` | 91 |
| `luminosite` | 116833 |
| `indice_uv` | 9.6 |
| `vent_vitesse` | 0.9 |
| `vent_direction` | 126 |
| `precipitation` | 0.0 |
| `pression_atmospherique` | 1012.4 |
| `rafale_max`, `pluie_cumul` | absentes |

**Payload complet** (54 caractères) :

```
01004958000009BE00000802000C00000000276B4C001900007B08
```

| Clé | Valeur attendue |
|---|---|
| `temperature` | 7.3 |
| `humidite` | 88 |
| `luminosite` | 2494 |
| `indice_uv` | 0.0 |
| `vent_vitesse` | 0.8 |
| `vent_direction` | 12 |
| `precipitation` | 0.0 |
| `pression_atmospherique` | 1009.1 |
| `rafale_max` | 2.5 |
| `pluie_cumul` | 3149.6 |

## 7. Origine des données

Données météo : [Open-Meteo](https://open-meteo.com/), licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
point de grille le plus proche de Blois (47,5861° N, 1,3359° E).

Deux colonnes sont **estimées**, car la source ne les fournit pas : `luminosite` (rayonnement solaire × 120,
plafonné à 200 000 lux) et `indice_uv` (rayonnement solaire / 110, plafonné à 11). `pluie_cumul` est la somme
des précipitations depuis le début du fichier. Avant novembre 2022, la source ne signale pas le brouillard.

La vraie borne émet toutes les 10 minutes ; l'historique est au pas d'une heure.
