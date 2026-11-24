# Rapports de référence et déroulé exact

Ce dossier n'existe que sur la branche `solutions`. Il sert au formateur :

- à **répéter la journée** avant de l'animer, commande par commande ;
- à **comparer** en salle ce qu'obtient un stagiaire avec ce qui est attendu.

Tout ce qui est ici a été **produit en lançant les commandes ci-dessous** le 24 novembre 2026, dans un
clone neuf du tag `jour-3`, sous Linux, en Python 3.13, avec les versions de `requirements.txt`.
Seuls les chemins du poste ont été raccourcis dans les sorties.

| Dossier | Contenu |
|---|---|
| [`sorties/`](sorties/) | ce qu'affiche le terminal à chaque étape (un fichier par étape, nommé `a<atelier>-<étape>-…`) |
| [`graphiques/`](graphiques/) | les images écrites dans `rapports/` par les scripts |
| [`ia/`](ia/) | les réponses de l'IA aux huit prompts (`claude-sonnet-5-5`) |
| [`envoyer.py`](envoyer.py) | envoie une requête de `api.http` sans VS Code : `python reference/envoyer.py 4` |

**Ce qui est reproductible et ce qui ne l'est pas.** Les chiffres des scripts sont identiques d'un poste
à l'autre (graine fixée, versions figées). Les réponses de l'IA changent à chaque appel : celles de `ia/`
sont **un exemple**, pas un corrigé. Les durées affichées par `pytest` varient.

Les réponses aux questions de `notes.md` sont dans [`SOLUTIONS.md`](../SOLUTIONS.md).

---

## Le déroulé, commande par commande

Chaque étape existe en deux versions :

- **Avec l'IA** : la commande du guide. Il faut une clé dans `.env`.
- **Sans l'IA** : on prend le fichier de la branche `solutions`. C'est ce qui a servi à produire `sorties/`.

Toutes les commandes se lancent depuis la racine du dépôt, environnement virtuel activé.

### Préparer le poste

```bash
git clone https://github.com/achaussier/fabnum41-ml.git station-meteo-ml
```

```bash
cd station-meteo-ml
```

```bash
git checkout -b travail jour-3
```

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

Sous Windows : `.venv\Scripts\activate`.

```bash
pip install -r requirements.txt
```

```bash
cp .env.example .env
```

Collez la clé dans `.env` après `ANTHROPIC_API_KEY=` (inutile pour la version « sans l'IA »).

`reference/envoyer.py` n'existe pas sur `jour-3`. Pour l'avoir sous la main sans changer de branche :

```bash
git show origin/solutions:reference/envoyer.py > ../envoyer.py
```

Il est rangé au-dessus du dépôt pour ne pas être commité. Lancez-le par `python ../envoyer.py 4`.

### Atelier 0 : réparer le décodeur

| # | Commande | Résultat attendu | Sortie |
|---|---|---|---|
| 1 | `pytest` | `2 passed, 1 warning` | [a0-1](sorties/a0-1-pytest-depart.txt) |
| 2 | `python -c "from station.decodeur import decoder; print(decoder('01010A5B0001C86160000902007E00000000278C'))"` | une `ValueError` : le payload de 40 caractères est refusé | [a0-4](sorties/a0-4-decodeur-avant.txt) |
| 3 | `python -c "from station.decodeur import decoder; print(decoder('01004958000009BE00000802000C00000000276B4C001900007B08'))"` | `humidite: 8.8`, `vent_direction: 1.2`, `pression_atmospherique: 10091` : trois valeurs fausses | [a0-4](sorties/a0-4-decodeur-avant.txt) |
| 4 | **Avec l'IA :** `python bin/ia "Écris les tests de decoder()" --prompt-file ateliers/prompts/00-tests-decodeur.md --file SPEC-ML.md --file station/decodeur.py --out station/tests/test_decodeur.py` | `✔ fichier écrit : station/tests/test_decodeur.py` | [ia/00](ia/00-tests-decodeur.md) |
|   | **Sans l'IA :** `git checkout origin/solutions -- station/tests/test_decodeur.py` | | |
| 5 | `pytest station` | du rouge. Avec les tests de `solutions` : `15 failed, 15 passed`. Avec ceux de l'IA lors de l'essai : `20 failed, 16 passed` | [a0-7](sorties/a0-7-pytest-rouge.txt) |
| 6 | Corriger `station/decodeur.py` (cinq écarts, voir `SOLUTIONS.md`). Raccourci : `git checkout origin/solutions -- station/decodeur.py` | | |
| 7 | `pytest station` | `30 passed` (36 avec les tests de l'IA) | [a0-8](sorties/a0-8-pytest-vert.txt) |
| 8 | Les deux commandes des lignes 2 et 3 | les valeurs du tableau de la spec : `91`, `126`, `1012.4`, puis `88`, `12`, `1009.1` | [a0-8](sorties/a0-8-decodeur-apres.txt) |
| 9 | Dans `decoder()`, ligne `"temperature"` : remplacer `/ 10` par `/ 100`, puis `pytest station` | `4 failed, 26 passed`. Remettre `/ 10` | [a0-9](sorties/a0-9-casser-temperature.txt) |
| 10 | Ligne `"precipitation"` : remplacer `/ 1000` par `/ 100`, puis `pytest station` | **cela dépend des tests.** Avec ceux de l'IA : tout reste vert (`36 passed`), car la pluie vaut 0 dans les deux payloads de la spec. Avec ceux de `solutions` : `1 failed`, grâce au test `test_une_pluie_non_nulle_est_decodee`. Remettre `/ 1000` | [verts](sorties/a0-9-casser-pluie-tests-ia.txt), [rouge](sorties/a0-9-casser-pluie.txt) |
| 11 | `git add -A` puis `git commit -m "atelier 0 : décodeur corrigé et testé"` | | |

La ligne 10 est le moment fort de l'atelier : un stagiaire dont tous les tests restent verts vient de
trouver un trou dans ses tests. Le test à écrire est dans `station/tests/test_decodeur.py` de cette branche.

### Atelier 1 : explorer les données

| # | Commande | Résultat attendu | Sortie |
|---|---|---|---|
| 1 | `python ml/explorer.py` | températures de −9,6 à 38,2 °C ; aucune valeur manquante ; Nuageux 56,5 %, Dégagé 26,5 %, Précipitations 13,2 %, Brouillard 3,7 % ; trois images dans `rapports/` | [a1-1](sorties/a1-1-explorer.txt) |
| 2 | Ouvrir les trois images | | [température](graphiques/temperature_annee.png), [pression et pluie](graphiques/pression_pluie_mois.png), [catégories](graphiques/categories.png) |
| 3 | `python bin/ia "Que montrent ces données ?" --prompt-file ateliers/prompts/01-expliquer-donnees.md --image rapports/pression_pluie_mois.png --image rapports/categories.png` | une description des deux images. Pas de version « sans l'IA » : lire l'exemple | [ia/01](ia/01-expliquer-donnees.md) |
| 4 | `python -c "import sys; sys.path.insert(0, 'ml'); from preparation import charger, ajouter_variables; d = ajouter_variables(charger()); print(d.loc['2025-03-14 06:00':'2025-03-14 12:00', ['temperature', 'temperature_moins_3h', 'temperature_dans_3h']].to_string())"` | sept lignes ; à 9 h : `3.3`, `-0.2`, `6.8` | [a1-4](sorties/a1-4-verification.txt) |

Rien à commiter : `rapports/` est hors de Git.

### Atelier 2 : prévoir la température dans 3 h

| # | Commande | Résultat attendu | Sortie |
|---|---|---|---|
| 1 | `python ml/entrainer_prediction.py` | 26 293 exemples d'entraînement, 8 765 de test ; baseline **1,96** ; entraînement **0,29** ; test **0,79 °C** | [a2-1](sorties/a2-1-entrainement-avant.txt), [courbe à trous](graphiques/prediction_vs_reel-avant-correction.png) |
| 2 | `python bin/ia "Ce résultat est-il fiable ?" --prompt-file ateliers/prompts/02-critiquer-entrainement.md --file ml/entrainer_prediction.py --file ml/preparation.py --file SPEC-ML.md` | l'IA désigne `train_test_split(..., shuffle=True)` et la règle 1 de la section 4 | [ia/02](ia/02-critiquer-entrainement.md) |
| 3 | Corriger `ml/entrainer_prediction.py` : remplacer `train_test_split` par `decouper(donnees)`, retirer l'import. Le détail : `git diff jour-3 origin/solutions -- ml/entrainer_prediction.py`. Raccourci : `git checkout origin/solutions -- ml/entrainer_prediction.py` | | |
| 4 | `python ml/entrainer_prediction.py` | 26 301 et 8 757 exemples ; baseline **2,06** ; entraînement **0,28** ; test **0,86 °C** | [a2-4](sorties/a2-4-entrainement-apres.txt), [courbe complète](graphiques/prediction_vs_reel.png) |
| 5 | `pytest` | vert : `31 passed` avec les tests de `solutions` (37 avec ceux de l'IA) | [a2-6](sorties/a2-6-pytest.txt) |
| 6 | Ajouter à la fin de `main()` la ligne `print(sorted(zip(...)))` du guide, relancer le script, la retirer | `temperature` 0,881 ; `heure` 0,07 ; tout le reste sous 0,02 | [a2-6](sorties/a2-6-importances.txt) |
| 7 | `git add -A` puis `git commit -m "atelier 2 : prévision mesurée honnêtement"` | | |

### Atelier 3 : catégoriser le ciel

| # | Commande | Résultat attendu | Sortie |
|---|---|---|---|
| 1 | `python ml/entrainer_categorie.py` | `Rien n'est encore entraîné : complétez les TODO…` | [a3-1](sorties/a3-1-avant.txt) |
| 2 | `git add -A` puis `git commit -m "avant atelier 3"` | (rien à commiter si l'atelier 2 l'a été : c'est normal) | |
| 3 | **Avec l'IA :** `python bin/ia "Complète les TODO" --prompt-file ateliers/prompts/03-classification.md --file ml/entrainer_categorie.py --file ml/preparation.py --out ml/entrainer_categorie.py --force` | `✔ fichier écrit : ml/entrainer_categorie.py` | [ia/03](ia/03-classification.md) |
|   | **Sans l'IA :** `git checkout origin/solutions -- ml/entrainer_categorie.py` | | |
| 4 | `git diff` (ou `git diff --cached` après le raccourci) | le script complété, à relire | |
| 5 | `python ml/entrainer_categorie.py` | baseline **53,0 %** ; entraînement **100,0 %** ; test **74,9 %** ; rappels : Dégagé 0,53, Nuageux 0,85, Brouillard 0,64, Précipitations 0,86 | [a3-5](sorties/a3-5-entrainement.txt), [matrice](graphiques/matrice_confusion.png) |
| 6 | `python bin/ia "Explique cette matrice" --prompt-file ateliers/prompts/03b-lire-confusion.md --image rapports/matrice_confusion.png` | une lecture de la matrice | [ia/03b](ia/03b-lire-confusion.md) |
| 7 | `git add -A` puis `git commit -m "atelier 3 : catégorisation du ciel"` | | |

### Atelier 4 : exposer le modèle

Deux terminaux. Dans le premier :

```bash
uvicorn api.main:app --reload
```

Dans le second, les requêtes de `api.http` (extension REST Client, `/docs`, ou `python ../envoyer.py N`) :

| # | Requête | Résultat attendu | Sortie |
|---|---|---|---|
| 1 | n°1 `GET /sante` | `200`, `"prediction": true`, `"categorie": true` | [avant](sorties/a4-requetes-avant.txt) |
| 2 | n°2 prévision | `200`, `valeur_prevue` **8.7**, `incertitude` **2.1**, `instant_prevu` `2025-03-14T12:00:00Z` (il a fait 6,8 °C) | |
| 3 | n°3 trois relevés | `422`, `requete_invalide` | |
| 4 | n°4 catégorie | `501`, `non_implemente` | |
| 5 | **Avec l'IA :** `python bin/ia "Écris /classify/conditions" --prompt-file ateliers/prompts/04-endpoint-categorie.md --file api/main.py --file SPEC-ML.md`, puis coller la fonction à la place de `categoriser_conditions()` | uvicorn se relance seul | [ia/04](ia/04-endpoint-categorie.md) |
|   | **Sans l'IA :** `git checkout origin/solutions -- api/main.py api/stockage.py` | **les deux fichiers** : l'API de `solutions` importe `api/stockage.py` (bonus B) et ne démarre pas sans lui | |
| 6 | n°4 catégorie | `200`, `"categorie": "Nuageux"`, probabilités `0.0 / 0.1 / 0.86 / 0.04` | [après](sorties/a4-requetes-apres.txt) |
| 7 | n°5 humidité à 150 | `422`, `Requête invalide : releve.humidite` | |
| 8 | `git add -A` puis `git commit -m "atelier 4 : route /classify/conditions"` | | |

Arrêtez uvicorn (Ctrl+C) avant l'atelier 5, ou laissez-le : les tests n'en ont pas besoin.

### Atelier 5 : tester l'API

| # | Commande | Résultat attendu | Sortie |
|---|---|---|---|
| 1 | **Avec l'IA :** `python bin/ia "Teste les trois routes" --prompt-file ateliers/prompts/05-tests-api.md --file api/main.py --file SPEC-ML.md --out api/tests/test_routes.py` | `✔ fichier écrit : api/tests/test_routes.py` | [ia/05](ia/05-tests-api.md) |
|   | **Sans l'IA :** `git checkout origin/solutions -- api/tests/test_routes.py` | | |
| 2 | `pytest api` | aucun rouge. Avec les tests de `solutions` : `19 passed, 1 warning`. Avec ceux de l'IA lors de l'essai : `29 passed, 1 xfailed, 1 warning` | [a5-4](sorties/a5-4-pytest-api.txt) |
| 3 | Dans `prevoir_temperature()`, remplacer `timedelta(hours=3)` par `timedelta(hours=2)`, puis `pytest api` | `1 failed` : `test_l_instant_prevu_est_trois_heures_apres_le_dernier_releve`. Remettre `hours=3` | [a5-5](sorties/a5-5-casser.txt) |
| 4 | `git add -A` puis `git commit -m "atelier 5 : tests de l'API"` | | |

Le `xfailed` de l'IA porte sur `reference_capteur` : la spec ne dit pas si ses 16 caractères s'imposent à
l'API. C'est un point à trancher avec le groupe, voir `SOLUTIONS.md`.

### Vérifier l'arrivée

À la fin du parcours « sans l'IA », le dépôt de travail est identique à `solutions`, aux fichiers des
bonus près. Sur la branche `solutions`, modèles entraînés :

```bash
pytest
```

Résultat attendu : `59 passed, 1 warning` ([sortie](sorties/final-pytest.txt)). Sans les modèles :
`54 passed, 5 skipped`.

### Bonus

| Commande | Résultat attendu | Sortie |
|---|---|---|
| `python ml/regrouper.py` | 1 461 journées en 4 groupes (273, 357, 370 et 461 jours) | [regrouper](sorties/bonus-regrouper.txt) |
| `python donnees/generer_synthetique.py --debut 2022-01-01 --jours 1461 --graine 42 --pannes --sortie donnees/synthetique.csv` | `35064 relevés simulés…, dont 592 marqués comme pannes` | [anomalies](sorties/bonus-anomalies.txt) |
| `python ml/anomalies.py` | 277 pannes retrouvées sur 592 (47 %), 425 fausses alertes | |

---

## Refaire ce dossier

Après un changement de code ou de versions, rejouez le déroulé « sans l'IA » ci-dessus et recopiez :

- les images de `rapports/` dans `reference/graphiques/` (celle de l'atelier 2 avant correction sous le
  nom `prediction_vs_reel-avant-correction.png`) ;
- la sortie de chaque commande dans le fichier de `reference/sorties/` qui porte son numéro d'étape.

Les réponses de `ia/` ne se refont qu'avec une clé, et coûtent environ 60 000 jetons envoyés et 30 000 reçus.
