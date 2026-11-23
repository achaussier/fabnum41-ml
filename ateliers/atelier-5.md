# Atelier 5 — Tester l'API (30 min)

**Objectif :** une API de modèle se teste comme une autre. On ne vérifie pas que le modèle « a raison »
(il se trompe parfois), on vérifie le **contrat** : formats, codes d'erreur, validation des entrées,
comportement quand le modèle manque.

**Livrable :** `api/tests/test_routes.py`, vert.

## Étapes

### 1. Générer les tests des trois routes

Lisez `ateliers/prompts/05-tests-api.md`. Pourquoi interdit-on de tester une valeur prévue exacte ?

```bash
python bin/ia "Teste les trois routes" --prompt-file ateliers/prompts/05-tests-api.md --file api/main.py --file SPEC-ML.md --out api/tests/test_routes.py
```

Relisez le fichier produit, et le commentaire en tête : l'IA signale-t-elle un écart entre le code et la spec ?

### 2. Lancer pytest

```bash
pytest api
```

Le premier lancement prend quelques secondes : les modèles sont chargés.

✅ *Vous devez voir :* tout vert. Des tests marqués `s` (skipped) signalent un modèle non entraîné.

Si un test est rouge : est-ce le **test** qui a tort, ou le **code** ? `SPEC-ML.md` tranche.

### 3. Vérifier les cas d'erreur couverts

Cochez dans le fichier de tests :

- [ ] 3 relevés au lieu de 4 → 422
- [ ] relevés non consécutifs → 422
- [ ] humidité à 150 → 422
- [ ] modèle absent → 503, pour les deux routes
- [ ] la forme `{"error": …, "code": …}` de chaque erreur

Il en manque un ? Demandez-le à l'IA, ou écrivez-le en copiant un test voisin.

### 4. Casser exprès un test pour voir qu'il sert

Dans `api/main.py`, remplacez `timedelta(hours=3)` par `timedelta(hours=2)` dans `prevoir_temperature()`.

```bash
pytest api
```

✅ *Vous devez voir :* un test rouge sur `instant_prevu`. Si tout reste vert, il vous manque un test.

Remettez `hours=3`, relancez : tout redevient vert.

### 5. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 5 : tests de l'API"
```

## Si ça coince

| Symptôme | Indice |
|---|---|
| `… existe déjà : relancez avec --force` | Le fichier a déjà été généré. Relisez-le ; ajoutez `--force` pour le remplacer. |
| Tous les tests de succès sont `skipped` | Les modèles ne sont pas entraînés : `python ml/entrainer_prediction.py` et `python ml/entrainer_categorie.py`. |
| `/classify/conditions` renvoie 501 dans les tests | L'atelier 4 n'est pas terminé : la route n'est pas écrite. |
| Un test attend une température précise (`== 7.4`) | Test fragile : le modèle change à chaque entraînement. Remplacez par une plage plausible. |
| Le test « modèle absent » échoue avec 200 | Le test doit utiliser `monkeypatch.setitem(main.MODELES, "prediction", None)`. |
| Le test « modèle absent » casse les tests suivants | `monkeypatch` remet tout en place tout seul ; une affectation directe `main.MODELES[...] = None` ne le fait pas. |
| La somme des probabilités vaut 0,99 | Les probabilités sont arrondies : comparez avec `pytest.approx(1, abs=0.02)`. |

## Pour aller plus loin

- Ajoutez un test : un relevé sans le champ `temperature` → 422.
- Lancez `pytest -v` : les noms des tests racontent-ils le contrat de l'API ?
