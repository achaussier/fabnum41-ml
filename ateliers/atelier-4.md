# Atelier 4 — Exposer le modèle : l'API (40 min)

**Objectif :** un modèle ne sert que si on peut l'interroger. On le place derrière une API.

**Livrable :** la route `POST /classify/conditions` qui répond 200.

## Étapes

### 1. Lancer l'API

Dans un **premier terminal** (environnement virtuel activé) :

```bash
uvicorn api.main:app --reload
```

✅ *Vous devez voir :* `Uvicorn running on http://127.0.0.1:8000`. Laissez ce terminal ouvert.

Ouvrez http://localhost:8000/docs dans un navigateur.

### 2. Essayer ce qui existe

Dans `/docs`, dépliez `GET /sante`, cliquez sur « Try it out » puis « Execute ».

✅ *Vous devez voir :* `{"statut": "ok", "modeles": {"prediction": true, "categorie": true}}`.
Si un modèle est à `false`, il n'a pas été entraîné (ateliers 2 et 3) : entraînez-le, puis relancez uvicorn.

Ouvrez `api.http` (extension « REST Client » de VS Code) et envoyez la requête n°2.

✅ *Vous devez voir :* une `valeur_prevue` proche de 7 °C et une `incertitude` proche de 1,4.
Il a fait 6,8 °C ce jour-là à 12 h.

Sans VS Code, la même chose se fait dans `/docs`, ou avec le script de la rubrique « Si ça coince ».

Répondez :

- Pourquoi faut-il envoyer **4** relevés ? (Regardez `VARIABLES_PREDICTION` dans `ml/preparation.py`.)
- D'où vient l'`incertitude` ? (Lisez `prevoir_temperature()` dans `api/main.py`.)
- Envoyez la requête n°3 : quel code obtenez-vous, et pourquoi ?

### 3. Constater ce qui manque

Envoyez la requête n°4 de `api.http`.

✅ *Vous devez voir :* `501` et le code `non_implemente`.

### 4. Écrire la route avec l'IA

Lisez le contrat dans `SPEC-ML.md`, section « API », puis le prompt `ateliers/prompts/04-endpoint-categorie.md`.

```bash
python bin/ia "Écris /classify/conditions" --prompt-file ateliers/prompts/04-endpoint-categorie.md --file api/main.py --file SPEC-ML.md
```

Il n'y a pas de `--out` : recopiez la fonction proposée dans `api/main.py`, à la place de l'actuelle
`categoriser_conditions()`. **Lisez-la d'abord** : comprenez-vous chaque ligne ?

Uvicorn se relance tout seul dès que vous enregistrez le fichier.

### 5. Vérifier

Renvoyez la requête n°4.

✅ *Vous devez voir :* `200`, une `categorie` et quatre `probabilites` dont la somme vaut 1.

Renvoyez la requête n°5 (humidité à 150).

✅ *Vous devez voir :* `422` et le code `requete_invalide`.

Rechargez `/docs` : la nouvelle route est documentée, sans rien avoir écrit de plus.

### 6. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 4 : route /classify/conditions"
```

## Si ça coince

| Symptôme | Indice |
|---|---|
| `No module named 'api'` | Lancez uvicorn depuis la racine du dépôt. |
| `Address already in use` | Une autre API tourne déjà : fermez-la, ou ajoutez `--port 8001`. |
| `/sante` indique `"categorie": false` | Lancez `python ml/entrainer_categorie.py`, puis arrêtez (Ctrl+C) et relancez uvicorn. |
| `500 Internal Server Error` | L'erreur détaillée est dans le terminal d'uvicorn. Lisez la dernière ligne. |
| `KeyError: 'heure'` | Le modèle attend les colonnes `heure` et `mois` : calculez-les avec `tableau.index.hour` et `tableau.index.month`. |
| `Object of type float32 is not JSON serializable` | Convertissez chaque probabilité avec `float(...)` avant de l'arrondir. |
| Pas d'extension REST Client | Voir le script ci-dessous. |

Envoyer une requête sans outil (le fichier `exemple.json` contient le corps de la requête) :

```bash
python -c "import json, urllib.request; r = urllib.request.Request('http://localhost:8000/classify/conditions', data=open('exemple.json', 'rb').read(), headers={'Content-Type': 'application/json'}); print(urllib.request.urlopen(r).read().decode())"
```

## Pour aller plus loin

- Envoyez un relevé de nuit, puis le même en plein jour (changez `instant_mesure` et `luminosite`) :
  comment bougent les probabilités ?
- La réponse reprend les noms de la table MySQL `resultat_ia`. Écrivez la requête `INSERT` qui
  enregistrerait la prévision de l'étape 2 (le dump SQL est dans `ateliers/station_meteo.sql`).
