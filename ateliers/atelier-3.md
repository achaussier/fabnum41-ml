# Atelier 3 — Catégoriser le ciel (45 min)

## Le but

La borne mesure la température, le vent, la pluie, la lumière. Elle ne « voit » pas le ciel. On veut
pourtant afficher sur le site : Dégagé, Nuageux, Brouillard ou Précipitations. Le modèle doit le
**deviner** à partir des mesures.

Deux choses à retenir de cet atelier : un chiffre global (« 75 % de bonnes réponses ») cache des
réussites et des échecs très différents selon la catégorie, et certaines erreurs ne viennent pas de
l'algorithme mais de **ce que les capteurs ne mesurent pas**.

## Le lien avec les jours 1 et 2

Cette fois, l'IA écrit du code, pas des tests : elle complète un squelette. Les trois réflexes
s'appliquent tels quels : commit avant, relecture avant de lancer, vérification après. Et vous savez
maintenant quoi chercher dans un script d'entraînement : l'atelier 2 vous l'a appris.

La matrice de confusion joue le rôle du rapport de tests du jour 2 : elle ne dit pas seulement
« combien d'échecs », elle dit **lesquels**.

## Ce que vous devez rendre

- `ml/entrainer_categorie.py` : complété, relu ;
- `modeles/categorie.joblib` et `rapports/matrice_confusion.png` (hors de Git) ;
- `notes.md` : questions 3.1 à 3.5 ;
- un commit.

## La démarche

1. Lire le squelette et le comparer au script de l'atelier 2.
2. Parier sur la catégorie la plus difficile.
3. Faire compléter par l'IA, **relire avant de lancer**.
4. Entraîner, comparer à la baseline.
5. Lire la matrice de confusion, puis expliquer les erreurs.

## Étapes

### 1. Lire le squelette

Ouvrez `ml/entrainer_categorie.py`. Il contient six `TODO`. Lancez-le :

```bash
python ml/entrainer_categorie.py
```

✅ *Vous devez voir :* `Rien n'est encore entraîné : complétez les TODO…`

Ouvrez à côté votre `ml/entrainer_prediction.py` corrigé. Pour chaque `TODO`, cherchez l'étape équivalente :

- lesquels se recopient presque tels quels ?
- lequel change parce qu'on devine une catégorie et non un nombre ?
- quelle est la baseline, ici ? Pourquoi la « persistance » de l'atelier 2 n'a-t-elle pas de sens ?

### 2. Parier

Relisez `VARIABLES_CATEGORIE` dans `ml/preparation.py` et la répartition des catégories de l'atelier 1.

🤔 ✍️ **Question 3.1** : quelle catégorie sera la plus difficile à reconnaître ? Laquelle sera la plus facile ?

### 3. Faire un commit, puis compléter les TODO avec l'IA

La commande ci-dessous **remplace** le fichier (`--force`). Un commit avant permet de revenir en arrière.

```bash
git add -A
```

```bash
git commit -m "avant atelier 3"
```

Lisez `ateliers/prompts/03-classification.md`. Repérez la phrase qui impose le découpage, et celle qui
interdit de donner la réponse au modèle.

```bash
python bin/ia "Complète les TODO" --prompt-file ateliers/prompts/03-classification.md --file ml/entrainer_categorie.py --file ml/preparation.py --out ml/entrainer_categorie.py --force
```

### 4. Relire avant de lancer

```bash
git diff
```

Vous êtes le relecteur. Vérifiez, ligne à l'appui :

- le découpage : quelle fonction ? Est-ce celle de la spec ?
- les entrées du modèle : `weather_code` ou `categorie` y figurent-ils ?
- la baseline : est-elle calculée sur l'entraînement, et mesurée sur le test ?
- l'IA a-t-elle ajouté quelque chose qu'on ne lui demandait pas ? Est-ce utile, inutile, gênant ?
- lisez aussi ses remarques dans le terminal, après le bloc de code : que dit-elle ne pas avoir pu vérifier ?

✍️ **Question 3.2.**

### 5. Entraîner, comparer à la baseline

```bash
python ml/entrainer_categorie.py
```

✅ *Vous devez voir :* une baseline autour de **53 %**, une forêt autour de **75 %** sur le test et
de 100 % sur l'entraînement, puis un tableau par catégorie.

✍️ **Question 3.3.** Que vous rappelle l'écart entre 100 % et 75 % ?

Dans le tableau, la colonne `recall` est le **rappel** : sur 100 heures réelles de cette catégorie,
combien le modèle en reconnaît-il ?

✍️ **Question 3.4.** Votre pronostic était-il juste ?

### 6. Lire la matrice de confusion

Ouvrez `rapports/matrice_confusion.png`. Avant de demander quoi que ce soit :

- où sont les bonnes réponses dans ce tableau ?
- quelle est la plus grosse case **en dehors** de la diagonale ? Dites-la en une phrase :
  « le modèle répond … alors que c'était … ».

Puis :

```bash
python bin/ia "Explique cette matrice" --prompt-file ateliers/prompts/03b-lire-confusion.md --image rapports/matrice_confusion.png
```

Vérifiez sur l'image deux chiffres cités par l'IA.

### 7. Expliquer les erreurs

L'IA propose une raison pour chaque confusion. Lisez bien : parle-t-elle des capteurs **de votre borne**,
ou de capteurs en général ? Que lui manquait-il pour être précise ? Relancez la commande en joignant ce
fichier, et comparez les deux réponses.

Puis cherchez vous-même la raison de la confusion la plus fréquente :

- quelles colonnes de `VARIABLES_CATEGORIE` distinguent un ciel clair d'un ciel couvert ?
- que valent ces colonnes à 3 h du matin ?

✍️ **Question 3.5.**

### 8. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 3 : catégorisation du ciel"
```

## C'est réussi si…

- [ ] Le script découpe dans le temps et ne donne jamais la réponse au modèle
- [ ] La forêt bat la baseline, et vous connaissez les deux chiffres
- [ ] Vous savez lire une case de la matrice de confusion à voix haute
- [ ] Vous savez dire quelle catégorie est la moins bien reconnue, et **pourquoi**
- [ ] Les questions 3.1 à 3.5 de `notes.md` ont une réponse

## Si ça coince

| Symptôme | Indice |
|---|---|
| `aucun bloc de code trouvé` ou `réponse tronquée` | Rien n'a été écrit : relancez la commande. |
| Le fichier produit ne marche pas | `git restore ml/entrainer_categorie.py` revient au squelette. Relancez, ou complétez les TODO à la main en vous aidant de `entrainer_prediction.py`. |
| Le script utilise `train_test_split` | Vous avez déjà rencontré ce problème. Quelle règle de `REGLES-IA.md` l'IA n'a-t-elle pas suivie ? Corrigez vous-même. |
| Une exactitude de 99 % ou 100 % sur le test | Trop beau pour être vrai. Regardez la liste des colonnes données au modèle : que contient chacune ? |
| `KeyError: 'categorie'` | La cible n'est pas dans `VARIABLES_CATEGORIE`, et c'est voulu. Dans quel tableau faut-il la prendre ? |
| Les étiquettes de la matrice se chevauchent | Ajoutez `xticks_rotation=30` à `ConfusionMatrixDisplay.from_predictions(...)`. |
| Je ne comprends pas « rappel » | Prenez la ligne « Brouillard » de la matrice : additionnez-la, puis divisez la case de la diagonale par ce total. |

La solution : `git show origin/solutions:ml/entrainer_categorie.py`.

## Pour aller plus loin

- **Une note trop belle, exprès.** Ajoutez `weather_code` aux entrées du modèle, relancez, regardez
  l'exactitude. Que s'est-il passé ? En quoi est-ce le même défaut qu'à l'atelier 2, sous une autre forme ?
  Annulez avec `git restore ml/entrainer_categorie.py` si vous n'aviez rien d'autre en cours, et relancez
  l'entraînement : l'API a besoin du bon modèle.
- Ajoutez `class_weight="balanced"` au `RandomForestClassifier` : le rappel du brouillard change-t-il ?
  À quel prix pour les autres catégories ?
- La pluie est presque toujours reconnue. Retirez `precipitation` des entrées : que se passe-t-il ?
  Qu'est-ce que cela dit de ce que le modèle a « compris » ?
