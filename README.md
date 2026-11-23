# station-meteo-ml

Dépôt du **jour 3** du parcours IA : découvrir le machine learning sur le projet fil rouge,
la station météo connectée de **Blois (41)** (borne SenseCAP S2120).

Objectif de la journée : comprendre ce qu'est un modèle, savoir où le placer, et repartir avec
**deux routes d'API qui fonctionnent** : une prévision (la température dans 3 heures) et une
catégorisation (l'état du ciel).

Comme les jours précédents, l'IA passe uniquement par le script `bin/ia`. Il n'y a pas de notebook :
que des scripts que l'on lance et que l'on lit.

## Installation

Python 3.12, 3.13 ou 3.14.

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

Sous Windows : `.venv\Scripts\activate` à la place de la ligne précédente.

```bash
pip install -r requirements.txt
```

```bash
cp .env.example .env
```

Sous Windows (invite de commandes) : `copy .env.example .env`.
Ouvrez ensuite `.env` et collez votre clé après `ANTHROPIC_API_KEY=`. Ce fichier ne va **jamais** dans Git.

```bash
pytest
```

Vous devez voir `2 passed`.

## Ce que contient le dépôt

```
station-meteo-ml/
├── donnees/
│   ├── historique_blois.csv        4 ans de relevés horaires à Blois (35 064 lignes)
│   ├── telecharger_open_meteo.py   refait ce CSV depuis Open-Meteo
│   ├── generer_synthetique.py      plan B hors ligne : des données simulées, avec des pannes
│   └── vers_mongo.py               bonus : CSV → JSON pour mongoimport
├── station/decodeur.py             décodage du message de la borne (atelier 0)
├── ml/
│   ├── preparation.py              charger(), ajouter_variables(), decouper()
│   ├── explorer.py                 résumé chiffré et graphiques (atelier 1)
│   ├── entrainer_prediction.py     modèle « température dans 3 h » (atelier 2)
│   └── entrainer_categorie.py      modèle « état du ciel », à compléter (atelier 3)
├── api/main.py                     l'API FastAPI qui charge les modèles (ateliers 4 et 5)
├── modeles/                        les modèles entraînés (.joblib), hors de Git
├── rapports/                       les graphiques produits, hors de Git
├── bin/ia                          le script pour interroger l'IA
├── ateliers/                       un guide par atelier, et les prompts
├── api.http                        des requêtes prêtes à envoyer à l'API
├── SPEC-ML.md                      la référence : problèmes, mesures, contrat de l'API, décodage
└── REGLES-IA.md                    les règles envoyées à l'IA à chaque appel
```

**`SPEC-ML.md` fait foi.** C'est lui que l'on donne à l'IA, pas le code.

## Les commandes de la journée

| Pour… | Commande |
|---|---|
| lancer les tests | `pytest` (ou `pytest station`, `pytest api`) |
| explorer les données | `python ml/explorer.py` |
| entraîner la prévision | `python ml/entrainer_prediction.py` |
| entraîner la catégorisation | `python ml/entrainer_categorie.py` |
| lancer l'API | `uvicorn api.main:app --reload`, puis http://localhost:8000/docs |
| interroger l'IA | `python bin/ia "consigne" --file … --image … --out …` |
| voir la requête sans l'envoyer | ajouter `--dry-run` |

Toutes les commandes se lancent **depuis la racine du dépôt**, environnement virtuel activé.

Les ateliers sont dans [`ateliers/`](ateliers/README.md).

## Les données

`donnees/historique_blois.csv` contient un relevé **par heure** du 1er janvier 2022 au 31 décembre 2025,
avec les mêmes noms de colonnes que la collection MongoDB `mesures` du projet, plus deux colonnes
d'étiquette (`weather_code`, `categorie`). Le fichier est versionné : aucune connexion n'est nécessaire.

À savoir :

- la vraie borne émet **toutes les 10 minutes** ; l'historique est au pas d'une heure ;
- `luminosite` et `indice_uv` sont **estimés** à partir du rayonnement solaire (la source ne les fournit pas) ;
- avant novembre 2022, la source ne signale pas le brouillard ;
- les vrais relevés de la borne (une semaine à ce jour) servent à essayer le modèle, pas à l'entraîner.

Plan B sans réseau, et jeu de données du bonus « anomalies » :

```bash
python donnees/generer_synthetique.py --debut 2022-01-01 --jours 1461 --graine 42 --pannes --sortie donnees/synthetique.csv
```

Ces données sont simulées : un modèle entraîné dessus ne fait que réapprendre les règles du générateur.

### Attribution

Données météo : [Open-Meteo.com](https://open-meteo.com/), sous licence
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Elles ont été converties au format du projet
par `donnees/telecharger_open_meteo.py` (renommage des colonnes, estimation de la luminosité et de l'UV,
cumul de pluie, regroupement des codes météo en quatre catégories).

## Les solutions

Elles sont sur la branche `solutions`. Essayez d'abord : les guides contiennent des indices.
