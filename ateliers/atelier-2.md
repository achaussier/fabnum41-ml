# Atelier 2 — Prévoir la température dans 3 h (45 min)

## Le but

Entraîner un premier modèle, et surtout apprendre à **juger sa note**. Un modèle se résume à un chiffre :
« en moyenne, je me trompe de tant de degrés ». Tout le monde croira ce chiffre. Votre travail est de
savoir s'il est mérité.

Le modèle produit ici est celui que l'API interrogera à l'atelier 4.

## Le lien avec les jours 1 et 2

Au jour 2, le brouillon enregistré par codegen « passait » sans rien vérifier : du vert qui ne prouvait
rien. Une note de modèle peut mentir de la même façon. Elle n'est pas fausse par calcul, elle est fausse
par **la façon dont on a posé la question**.

Et comme toujours : `SPEC-ML.md` fait foi. Le script d'entraînement est du code, il peut la contredire.

## Ce que vous devez rendre

- `ml/entrainer_prediction.py` : corrigé ;
- `modeles/prediction_temperature.joblib` : le modèle (hors de Git, il se reconstruit) ;
- `notes.md` : questions 2.1 à 2.6, dont le tableau des trois erreurs ;
- un commit.

## La démarche

1. Entraîner, noter les chiffres.
2. Chercher **vous-même** ce qui contredit la spec.
3. Demander son avis à l'IA, et le vérifier.
4. Parier sur l'effet de la correction, puis corriger.
5. Comparer les deux notes, et comprendre laquelle est la vraie.

## Étapes

### 1. Lancer l'entraînement

```bash
python ml/entrainer_prediction.py
```

Comptez une vingtaine de secondes.

✅ *Vous devez voir :* trois erreurs moyennes en °C (baseline, forêt sur l'entraînement, forêt sur le test),
puis `Modèle enregistré : modeles/prediction_temperature.joblib`.

✍️ **Question 2.1.** Puis réfléchissez :

- La forêt bat-elle la baseline « persistance » ? De combien ?
- Pourquoi l'erreur sur l'entraînement est-elle bien plus basse que l'erreur sur le test ?
  (Slide « Apprendre par cœur n'est pas comprendre ».)

Ouvrez `rapports/prediction_vs_reel.png`. Une semaine compte 168 heures : les voyez-vous toutes ?

### 2. Chercher par vous-même (5 minutes, sans l'IA)

Ouvrez côte à côte `ml/entrainer_prediction.py` et `SPEC-ML.md`, sections 2 et 4.
La spec énonce des règles. Le script les respecte-t-il **toutes** ?

Prenez chaque règle une par une et cherchez la ligne du script qui l'applique. Si vous ne trouvez rien,
passez à l'étape 3 : vous comparerez.

### 3. Demander son avis à l'IA

Lisez d'abord le prompt `ateliers/prompts/02-critiquer-entrainement.md` : on y demande un diagnostic,
pas un script corrigé. Pourquoi, à votre avis ?

```bash
python bin/ia "Ce résultat est-il fiable ?" --prompt-file ateliers/prompts/02-critiquer-entrainement.md --file ml/entrainer_prediction.py --file ml/preparation.py --file SPEC-ML.md
```

L'IA désigne une ligne et une règle. **Vérifiez les deux** : la ligne existe-t-elle dans le script ?
La règle est-elle bien écrite dans la spec, à l'endroit qu'elle cite ?

✍️ **Question 2.2.**

### 4. Parier, puis corriger

🤔 ✍️ **Question 2.3** : après correction, l'erreur sur le test va-t-elle monter ou descendre ?

Corrigez ensuite `ml/entrainer_prediction.py` **vous-même** : la fonction dont vous avez besoin existe
déjà dans `ml/preparation.py`. Lisez ce qu'elle renvoie avant de l'appeler. Supprimez l'import devenu inutile.

```bash
python ml/entrainer_prediction.py
```

✅ *Vous devez voir :* environ 26 300 exemples d'entraînement et 8 750 exemples de test, et une erreur
sur le test **différente** de celle de l'étape 1.

### 5. Comparer

✍️ **Question 2.4** (le tableau). Puis :

- Votre pronostic était-il juste ?
- Le modèle n'a pas changé d'algorithme ni de données. Qu'est-ce qui a changé, exactement ?
- Laquelle des deux notes annonceriez-vous à quelqu'un qui va se servir du modèle demain ? Pourquoi ?
- Rouvrez `rapports/prediction_vs_reel.png` : qu'est-ce qui a changé sur la courbe ?

### 6. Et les tests, dans tout ça ?

```bash
pytest
```

✅ *Vous devez voir :* du vert, comme avant votre correction.

✍️ **Question 2.5** : pourquoi aucun test n'a-t-il vu ce défaut ? Qu'est-ce qui l'a révélé, à la place ?

✍️ **Question 2.6** : vos deux variables de l'atelier 1 étaient-elles les bonnes ? Pour le savoir, ajoutez
cette ligne à la fin de `main()`, relancez le script, puis retirez-la :

```python
    print(sorted(zip(modele.feature_importances_.round(3).tolist(), VARIABLES_PREDICTION), reverse=True))
```

### 7. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 2 : prévision mesurée honnêtement"
```

Le fichier `.joblib` n'est pas commité (il est dans `.gitignore`) : un modèle se **reconstruit** à partir
du code et des données.

## C'est réussi si…

- [ ] Le script n'utilise plus qu'une seule façon de séparer entraînement et test, celle de la spec
- [ ] Vous avez noté les deux notes, et vous savez dire laquelle est la vraie
- [ ] Vous savez expliquer le défaut à un collègue en une phrase, sans le mot « shuffle »
- [ ] La forêt bat toujours la baseline après correction
- [ ] Les questions 2.1 à 2.6 de `notes.md` ont une réponse

## Si ça coince

Lisez un indice à la fois, dans l'ordre.

| Symptôme | Indice |
|---|---|
| Je ne vois pas le problème | Cherchez la ligne qui sépare entraînement et test. Comment choisit-elle les lignes du test ? |
| Toujours pas | Relisez la règle n°1 de la section 4 de `SPEC-ML.md`, puis cherchez dans le script le nom de la fonction qu'elle cite. |
| L'IA ne signale rien | Avez-vous bien joint `SPEC-ML.md` ? Collez la règle n°1 de la section 4 dans la consigne et demandez si le script la respecte. |
| Je ne sais pas quoi écrire à la place | La fonction renvoie deux tableaux complets. Dans chacun, il reste à prendre les colonnes d'entrée et la colonne cible : regardez comment `X` et `y` sont construits aujourd'hui. |
| `NameError: name 'decouper' is not defined` | Regardez la ligne `from preparation import …`. |
| L'erreur a augmenté, j'ai dû casser quelque chose | Non. Relisez la règle n°1 de la section 4 : sur quelles heures le modèle était-il interrogé avant, et sur lesquelles l'est-il maintenant ? |
| L'écart entre les deux notes est petit | Quelques centièmes de degré suffisent pour la leçon : la première note était trop belle, et **rien** à l'écran ne le signalait. |

La solution : `git diff main origin/solutions -- ml/entrainer_prediction.py`.

## Pour aller plus loin

- **Un test pour la règle.** Aucun test ne protège le découpage. Écrivez **votre propre consigne** pour
  faire générer `ml/tests/test_preparation.py`, d'après les sections 2 et 4 de `SPEC-ML.md` : aucun relevé
  de 2025 dans l'entraînement, aucun relevé d'avant 2025 dans le test, et `temperature_dans_3h` vaut bien
  la température relevée trois heures plus tard. Quels fichiers faut-il joindre ? Puis `pytest ml`.
- Retirez `temperature_moins_1h` et `temperature_moins_3h` de `VARIABLES_PREDICTION` : que devient l'erreur ?
  (Remettez-les ensuite : l'API en a besoin.)
