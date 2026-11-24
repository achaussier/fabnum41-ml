# Atelier 5 — Tester l'API (30 min)

## Le but

Fermer la boucle : la route que vous venez d'écrire doit rester juste demain, quand quelqu'un
réentraînera le modèle ou modifiera `api/main.py`. On écrit donc les tests qui le garantissent.

Mais que teste-t-on, quand la réponse vient d'un modèle qui se trompe parfois ? Pas la valeur prévue :
elle change à chaque entraînement. On teste le **contrat** : les formats, les codes d'erreur, la
validation des entrées, le comportement quand le modèle manque.

## Le lien avec les jours 1 et 2

C'est la synthèse des deux premiers jours.

- Comme au jour 1 : les tests viennent de la spec, un test par comportement, des cas paramétrés, et on
  casse exprès le code pour vérifier que les tests servent.
- Comme au jour 2 : `TestClient` joue le rôle du navigateur de Playwright. Il envoie de vraies requêtes
  à l'application entière, sans la démarrer.
- Comme pour la régression visuelle : on n'exige pas une égalité parfaite là où elle n'a pas de sens.
  Vous aviez réglé une tolérance en pixels ; ici, une **plage plausible** pour la température.

## Ce que vous devez rendre

- `api/tests/test_routes.py` : écrit par l'IA, relu par vous, vert ;
- `notes.md` : questions 5.1 à 5.4, et le bilan de la journée ;
- un commit.

## La démarche

1. Lister **vous-même** les cas à tester, d'après la spec.
2. Faire écrire les tests, comparer à votre liste.
3. Lancer, trancher ce qui n'est pas vert.
4. Casser exprès le code.
5. Dire ce que ces tests garantissent, et ce qu'ils ne garantissent pas.

## Étapes

### 1. Lister les cas, avant l'IA

Ouvrez `SPEC-ML.md`, section « 5. API ». Pour chacune des trois routes, notez ce qu'un test devrait
vérifier : le cas normal, puis chaque ligne du tableau des erreurs. Cinq minutes, pas plus.

✍️ **Question 5.1.**

### 2. Générer les tests des trois routes

Lisez `ateliers/prompts/05-tests-api.md`.

- Pourquoi interdit-on de tester une valeur prévue exacte ? Que se passerait-il la semaine prochaine ?
- Pourquoi un test de succès est-il **ignoré**, et non rouge, quand le modèle n'est pas entraîné ?

```bash
python bin/ia "Teste les trois routes" --prompt-file ateliers/prompts/05-tests-api.md --file api/main.py --file SPEC-ML.md --out api/tests/test_routes.py
```

### 3. Relire, comparer à votre liste

Ouvrez `api/tests/test_routes.py`.

- Le commentaire en tête : l'IA signale-t-elle un écart entre le code et la spec ? Lequel ?
- Reprenez votre liste de l'étape 1 et cochez ce qui est couvert :

  - [ ] 3 relevés au lieu de 4 → 422
  - [ ] relevés non consécutifs → 422
  - [ ] humidité à 150 → 422
  - [ ] modèle absent → 503, pour les deux routes
  - [ ] la forme `{"error": …, "code": …}` de chaque erreur

- Cherchez `==` suivi d'un nombre décimal : un test attend-il une température ou une probabilité précise ?

✍️ **Question 5.2.** Il manque un cas ? Demandez-le à l'IA, ou écrivez-le en copiant un test voisin.

### 4. Lancer pytest

```bash
pytest api
```

Le premier lancement prend quelques secondes : les modèles sont chargés.

✅ *Vous devez voir :* aucun test rouge. Trois mentions sont possibles en plus de `passed` :

| Mention | Ce qu'elle veut dire | Que faire |
|---|---|---|
| `skipped` | un modèle n'est pas entraîné, le test n'a pas pu tourner | entraîner le modèle, relancer |
| `xfailed` | l'IA a écrit un test qu'elle **sait** rouge, pour signaler un écart avec la spec | lire la raison, puis décider (ci-dessous) |
| `warning` | une bibliothèque annonce un changement à venir | rien aujourd'hui |

Un test rouge, ou un `xfailed` : c'est la question du jour 1. **Le test a-t-il tort, ou le code ?**
`SPEC-ML.md` tranche. Et si la spec n'est pas assez précise pour trancher, c'est **elle** qu'il faut
compléter : dites-le au formateur, ne choisissez pas en silence.

### 5. Casser exprès un test pour voir qu'il sert

🤔 Dans `api/main.py`, vous allez remplacer `timedelta(hours=3)` par `timedelta(hours=2)` dans
`prevoir_temperature()`. Avant de relancer : quel test va devenir rouge ? Retrouvez-le dans le fichier.

```bash
pytest api
```

✅ *Vous devez voir :* un test rouge sur `instant_prevu`. Si tout reste vert, il vous manque un test.

✍️ **Question 5.3.** Remettez `hours=3`, relancez : tout redevient vert.

### 6. Ce que le vert garantit

Tous vos tests passent. Imaginez que quelqu'un remplace le modèle par un autre, qui répond toujours
« 12 °C » : vos tests resteraient-ils verts ?

✍️ **Question 5.4**, puis le **bilan de la journée**, tout en bas de `notes.md`.

### 7. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 5 : tests de l'API"
```

## C'est réussi si…

- [ ] `pytest` (tout le dépôt) n'a aucun test rouge
- [ ] Aucun test n'attend une valeur prévue exacte
- [ ] Les cinq cas d'erreur de l'étape 3 sont couverts
- [ ] Une modification volontaire du code a été détectée par un test
- [ ] Vous savez dire ce que ces tests ne garantissent pas, et où trouver cette garantie
- [ ] Les questions 5.1 à 5.4 et le bilan de `notes.md` ont une réponse

## Si ça coince

| Symptôme | Indice |
|---|---|
| `… existe déjà : relancez avec --force` | Le fichier a déjà été généré. Relisez-le ; ajoutez `--force` pour le remplacer. |
| Tous les tests de succès sont `skipped` | Que répond `GET /sante` ? Quels scripts fabriquent les fichiers `.joblib` ? |
| `/classify/conditions` renvoie 501 dans les tests | L'atelier 4 n'est pas terminé : la route n'est pas écrite. |
| Un test attend une température précise (`== 7.4`) | Test fragile. Quelle contrainte du prompt l'interdisait ? Remplacez par une plage plausible. |
| Le test « modèle absent » échoue avec 200 | Comment le test fait-il croire à l'API que le modèle manque ? Cherchez `monkeypatch` dans le prompt. |
| Le test « modèle absent » casse les tests suivants | Qui remet le modèle en place après le test ? `monkeypatch` le fait tout seul, une affectation directe non. |
| La somme des probabilités vaut 0,99 | Les probabilités sont arrondies. Quelle tolérance le prompt demandait-il ? |
| Un test est `xfailed` et je ne sais pas quoi en faire | Lisez sa raison. Cherchez la phrase de la spec sur laquelle l'IA s'appuie : s'applique-t-elle vraiment à l'API ? |

La solution : `git show origin/solutions:api/tests/test_routes.py`.

## Pour aller plus loin

- Dans `prevoir_temperature()`, remplacez `round(…, 1)` par `round(…, 2)` pour `valeur_prevue`. Un test
  le voit-il ? La spec le demande-t-elle ? Écrivez le test qui manque.
- Ajoutez un test : un relevé sans le champ `temperature` → 422.
- Lancez `pytest -v` : les noms des tests racontent-ils le contrat de l'API à quelqu'un qui n'a pas lu la spec ?
