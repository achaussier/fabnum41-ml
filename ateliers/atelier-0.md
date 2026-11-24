# Atelier 0 — Réparer le décodeur (45 min)

## Le but

La borne n'envoie pas « 26,6 °C » : elle envoie un texte hexadécimal, le *payload*. La fonction
`decoder()` le transforme en mesures. Tout le reste de la journée s'appuie dessus : un modèle apprend ce
qu'on lui montre, et **il ne proteste jamais**. Si le décodeur se trompe, le modèle apprendra des valeurs
fausses, sans la moindre erreur à l'écran.

À la fin de l'atelier, vous saurez dire si le décodeur respecte sa règle, et vous pourrez le prouver.

## Le lien avec les jours 1 et 2

C'est l'atelier 1 du jour 1, dans un autre langage. Vous aviez fait écrire les tests de `PriceCalculator`
d'après `SPEC.md`, et un test rouge avait révélé un défaut du code. Ici : pytest au lieu de PHPUnit,
`@pytest.mark.parametrize` au lieu de `#[DataProvider]`, `SPEC-ML.md` au lieu de `SPEC.md`.
La question centrale est la même : **quand un test est rouge, qui a raison ?**

## Ce que vous devez rendre

- `station/tests/test_decodeur.py` : écrit par l'IA, **relu par vous**, vert ;
- `station/decodeur.py` : corrigé ;
- `notes.md` : questions 0.1 à 0.5 ;
- un commit.

## La démarche

1. Lire la règle, puis décoder deux valeurs **à la main**.
2. Comparer avec ce que renvoie le code, et écrire un pronostic.
3. Faire écrire les tests d'après la spec, les relire.
4. Lancer : du rouge. Trancher chaque cas avec la spec.
5. Corriger le code, un écart à la fois.
6. Casser exprès le code, pour voir si les tests servent.

## Étapes

### 1. Vérifier l'installation

```bash
pytest
```

✅ *Vous devez voir :* `2 passed`.

Ouvrez `station/tests/test_exemple.py` : que vérifie ce test, exactement ? Gardez la réponse en tête.

### 2. Lire la règle

Ouvrez `SPEC-ML.md`, section **« 6. Décodage »**. Repérez :

- le tableau de découpage (quels caractères, quel calcul, quelle unité) ;
- les six règles sous le tableau ;
- le **payload de référence** et le **payload complet**, avec leurs valeurs attendues.

Ouvrez ensuite `station/decodeur.py`. Lisez-le, ne corrigez rien.

### 3. Décoder à la main

Prenez le payload de référence : `01010A5B0001C86160000902007E00000000278C`.

Avec le tableau de la spec, retrouvez vous-même l'**humidité** et la **pression** : quels caractères,
quelle valeur hexadécimale, quel calcul ? Pour convertir de l'hexadécimal :

```bash
python -c "print(int('5B', 16))"
```

Vos deux résultats sont-ils ceux du tableau « valeur attendue » de la spec ? Si oui, vous savez lire la règle.

### 4. Comparer avec le code

Demandez la même chose au décodeur :

```bash
python -c "from station.decodeur import decoder; print(decoder('01010A5B0001C86160000902007E00000000278C'))"
```

Puis avec le payload complet :

```bash
python -c "from station.decodeur import decoder; print(decoder('01004958000009BE00000802000C00000000276B4C001900007B08'))"
```

Comparez chaque sortie au tableau de la spec, ligne par ligne.

🤔 ✍️ **Question 0.1** : quelles valeurs vous paraissent fausses ? Combien de tests rouges attendez-vous ?

### 5. Faire écrire les tests d'après la spec

Lisez `ateliers/prompts/00-tests-decodeur.md` avant de lancer la commande.

- Pourquoi joint-on `SPEC-ML.md` **et** le code ? Que risque-t-on en ne joignant que le code ?
- Quelle phrase du prompt empêche l'IA de recopier les valeurs que le code calcule ?

```bash
python bin/ia "Écris les tests de decoder()" --prompt-file ateliers/prompts/00-tests-decodeur.md --file SPEC-ML.md --file station/decodeur.py --out station/tests/test_decodeur.py
```

✅ *Vous devez voir :* la réponse de l'IA, puis `✔ fichier écrit : station/tests/test_decodeur.py`.

### 6. Relire, avant de lancer quoi que ce soit

Ouvrez le fichier produit.

- Le commentaire en tête : quels écarts l'IA annonce-t-elle ? Sont-ils ceux de votre pronostic ?
- Les valeurs attendues : prenez-en trois au hasard et retrouvez-les dans `SPEC-ML.md`.
- Y a-t-il un cas que la spec ne demande pas ? Un cas de la spec qui manque ?

### 7. Lancer, puis trancher

```bash
pytest station
```

✅ *Vous devez voir :* du **rouge**, et pas qu'un peu. C'est le résultat attendu.

Ne corrigez rien tout de suite. Regroupez les tests rouges par cause, puis, pour chaque groupe :

- lisez la valeur attendue et la valeur obtenue ;
- retrouvez la ligne de `SPEC-ML.md` concernée ;
- décidez : le test contredit la spec (le **test** est faux), ou le test suit la spec (le **code** est faux) ?

✍️ **Question 0.2.**

### 8. Corriger jusqu'au vert

Corrigez `station/decodeur.py`, **un écart à la fois**, en relançant `pytest station` après chaque
correction : le nombre de tests rouges doit baisser à chaque fois.

✅ *Vous devez voir, à la fin :* tous les tests verts.

✍️ **Questions 0.3 et 0.4.**

### 9. Casser exprès, pour voir si les tests servent

Comme au jour 1 : une modification, on relance, on observe, on annule.

1. Dans `decoder()`, remplacez le `/ 10` de la température par `/ 100`. Relancez `pytest station`.

   ✅ *Vous devez voir :* du rouge. Remettez `/ 10`.

2. Remplacez maintenant le `/ 1000` de la pluie par `/ 100`. Relancez.

   Que voyez-vous ? Regardez la valeur de la pluie dans les deux payloads de la spec : comprenez-vous pourquoi ?

✍️ **Question 0.5.** Remettez `/ 1000` avant de continuer.

### 10. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 0 : décodeur corrigé et testé"
```

## C'est réussi si…

- [ ] `pytest station` est entièrement vert
- [ ] Vous n'avez modifié **aucun test** pour le faire passer sans l'avoir comparé à la spec
- [ ] Vous savez dire combien d'écarts il y avait, et citer la ligne de la spec pour chacun
- [ ] Vous savez expliquer pourquoi `2 passed` ne prouvait rien au départ
- [ ] Les questions 0.1 à 0.5 de `notes.md` ont une réponse

## Si ça coince

Lisez un indice à la fois, dans l'ordre.

| Symptôme | Indice |
|---|---|
| Tous les tests sont verts dès le départ | D'où viennent les valeurs attendues : de la spec, ou du code ? Cherchez dans le fichier de tests la valeur d'humidité du payload de référence, et comparez avec la spec. |
| `ValueError: invalid literal for int() with base 16: ''` | Que vaut `'abc'[5:8]` en Python ? Et donc, que lit le décodeur au-delà du 40ᵉ caractère d'un payload de 40 caractères ? |
| Une valeur est dix fois trop petite ou dix fois trop grande | Relisez la colonne « Calcul » du tableau pour cette mesure, puis la ligne correspondante de `decoder()`. |
| Un test attend un `int` et reçoit un `float` | En Python, `91 / 1` vaut `91.0`. Quelle opération faut-il retirer ? |
| Le payload de 40 caractères passe, mais deux clés sont en trop | Relisez la règle sur les payloads de 40 caractères : « absentes » ne veut pas dire « à zéro » ni « à `None` ». |
| Un test sur un payload « non hexadécimal » reste rouge | Le décodeur lit-il **tous** les caractères du payload ? Que dit la dernière règle de la spec ? |
| Un test échoue alors que la spec vous semble respectée | L'IA se trompe aussi. Relisez le test : si c'est lui qui contredit la spec, corrigez-le, et notez-le en 0.2. |
| Un test compare `0.9 == 0.9` et échoue | Les décimaux se comparent avec `pytest.approx(0.9)`. |

La solution est sur la branche `solutions` : `git show origin/solutions:station/decodeur.py`.

## Pour aller plus loin

- Écrivez le test qui manquait à l'étape 9 : un payload où la pluie n'est pas nulle. Calculez la valeur
  attendue **à la main**, d'après le tableau de la spec, pas avec le code.
- Faites relire vos tests, comme au jour 1 :
  `python bin/ia "Signale les assertions faibles ou redondantes" --file station/tests/test_decodeur.py --file SPEC-ML.md`.
  Êtes-vous d'accord avec chaque remarque ?
- Dans le projet d'origine, la pression n'a jamais été enregistrée dans MongoDB. Relisez la slide
  « Avant le modèle : des données justes » : pourquoi personne ne s'en est aperçu ?
