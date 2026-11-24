# Atelier 4 — Exposer le modèle : l'API (40 min)

## Le but

Un modèle enregistré dans un fichier ne sert à personne. Pour que le site web ou la borne puissent
l'interroger, on le place derrière une API : une adresse à laquelle on envoie des relevés, et qui
répond une prévision.

La route de prévision existe déjà. Vous écrivez celle de catégorisation, d'après le contrat de la spec.

## Le lien avec les jours 1 et 2

Aux jours 1 et 2, vous testiez une application écrite par d'autres. Ici, vous écrivez la route **et**
vous la testerez à l'atelier 5 : le contrat de `SPEC-ML.md` sert aux deux.

Deux rappels du jour 1 : l'IA ne voit que les fichiers qu'on lui joint, et elle peut appeler une
fonction qui n'existe pas. On vérifie donc chaque nom qu'elle utilise.

## Ce que vous devez rendre

- `api/main.py` : la route `POST /classify/conditions` répond 200 avec le format de la spec ;
- `notes.md` : questions 4.1 à 4.4 ;
- un commit.

## La démarche

1. Lancer l'API, essayer la route qui existe.
2. Comprendre comment elle est écrite.
3. Écrire **en français** ce que la nouvelle route doit faire.
4. Faire écrire la fonction par l'IA, la comparer à vos étapes, la recopier.
5. Vérifier le cas normal et le cas d'erreur.

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

✅ *Vous devez voir :* une `valeur_prevue` entre 8 et 9 °C et une `incertitude` proche de 2 °C.
Il a fait 6,8 °C ce jour-là à 12 h : l'écart tient-il dans l'incertitude annoncée ?

Sans VS Code, la même chose se fait dans `/docs`, ou avec le script de la rubrique « Si ça coince ».

🤔 Avant d'envoyer la requête n°3, lisez-la : que va répondre l'API, et pourquoi ? Envoyez-la.

### 3. Comprendre la route qui existe

Ouvrez `api/main.py` et lisez `prevoir_temperature()` de haut en bas.

✍️ **Question 4.1** : pourquoi faut-il **4** relevés ? (La réponse est dans `VARIABLES_PREDICTION`.)

✍️ **Question 4.2** : d'où vient l'`incertitude` ?

### 4. Constater ce qui manque

Envoyez la requête n°4 de `api.http`.

✅ *Vous devez voir :* `501` et le code `non_implemente`.

### 5. Écrire les étapes en français, avant l'IA

Lisez le contrat de `POST /classify/conditions` dans `SPEC-ML.md`, section « 5. API ».

✍️ **Question 4.3** : écrivez, en quatre à six lignes de français, ce que la route doit faire, du relevé
reçu à la réponse renvoyée. Aidez-vous de `prevoir_temperature()` : qu'est-ce qui est pareil ?
Qu'est-ce qui diffère ? Pensez au cas où le modèle n'a pas été entraîné.

### 6. Faire écrire la fonction par l'IA

Lisez `ateliers/prompts/04-endpoint-categorie.md` : ses étapes ressemblent-elles aux vôtres ?

```bash
python bin/ia "Écris /classify/conditions" --prompt-file ateliers/prompts/04-endpoint-categorie.md --file api/main.py --file SPEC-ML.md
```

Il n'y a pas de `--out` : c'est **vous** qui recopiez la fonction dans `api/main.py`, à la place de
l'actuelle `categoriser_conditions()`. Avant de coller :

- chaque fonction appelée existe-t-elle dans `api/main.py` ? Cherchez-les une par une ;
- comprenez-vous chaque ligne ? Sinon, demandez à l'IA de vous expliquer **cette** ligne ;
- l'IA signale-t-elle quelque chose qu'elle n'a pas pu vérifier ? Vérifiez-le pour elle.

✍️ **Question 4.4.**

Uvicorn se relance tout seul dès que vous enregistrez le fichier.

### 7. Vérifier

Renvoyez la requête n°4.

✅ *Vous devez voir :* `200`, une `categorie` et quatre `probabilites`.

Comparez la réponse au contrat de la spec, champ par champ : les noms, le nombre de catégories,
l'arrondi. Additionnez les probabilités : que trouvez-vous ?

🤔 Avant d'envoyer la requête n°5, lisez-la : que doit répondre l'API ? Envoyez-la.

✅ *Vous devez voir :* `422` et le code `requete_invalide`.

Vous n'avez écrit aucune ligne pour refuser cette requête. Qui l'a refusée ? Cherchez dans `api/main.py`.

Rechargez `/docs` : la nouvelle route est documentée, sans rien avoir écrit de plus.

### 8. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 4 : route /classify/conditions"
```

## C'est réussi si…

- [ ] La requête n°4 répond 200, avec exactement les champs du contrat
- [ ] La requête n°5 répond 422, avec la forme `{"error": …, "code": …}`
- [ ] Vous savez expliquer chaque ligne de la fonction que vous avez collée
- [ ] Vous savez dire ce que répond la route si le modèle n'est pas entraîné
- [ ] Les questions 4.1 à 4.4 de `notes.md` ont une réponse

## Si ça coince

| Symptôme | Indice |
|---|---|
| `No module named 'api'` | Lancez uvicorn depuis la racine du dépôt. |
| `Address already in use` | Une autre API tourne déjà : fermez-la, ou ajoutez `--port 8001`. |
| `/sante` indique `"categorie": false` | Lancez `python ml/entrainer_categorie.py`, puis arrêtez (Ctrl+C) et relancez uvicorn. |
| `500 Internal Server Error` | L'erreur détaillée est dans le terminal d'uvicorn. Lisez la dernière ligne. |
| `KeyError: 'heure'` | Le modèle attend des colonnes qui ne sont pas dans le relevé envoyé. Lesquelles ? D'où peut-on les calculer ? |
| `Object of type float32 is not JSON serializable` | Les nombres du modèle ne sont pas des nombres Python ordinaires. Quelle contrainte du prompt en parlait ? |
| La route répond encore 501 | Avez-vous remplacé **toute** la fonction, y compris la dernière ligne `return erreur(501, …)` ? |
| Pas d'extension REST Client | Voir le script ci-dessous. |

Envoyer une requête sans outil (le fichier `exemple.json` contient le corps de la requête) :

```bash
python -c "import json, urllib.request; r = urllib.request.Request('http://localhost:8000/classify/conditions', data=open('exemple.json', 'rb').read(), headers={'Content-Type': 'application/json'}); print(urllib.request.urlopen(r).read().decode())"
```

La solution : `git show origin/solutions:api/main.py`. Les lignes qui commencent par `stockage.` et
l'import `from api import stockage` appartiennent à un bonus : ne les recopiez pas.

## Pour aller plus loin

- Envoyez un relevé de nuit, puis le même en plein jour (changez `instant_mesure` et `luminosite`) :
  comment bougent les probabilités ? Est-ce cohérent avec votre réponse 3.5 ?
- La réponse reprend les noms de la table MySQL `resultat_ia`. Écrivez la requête `INSERT` qui
  enregistrerait la prévision de l'étape 2 (le dump SQL est dans `ateliers/station_meteo.sql`).
