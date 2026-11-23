# Atelier 3 — Catégoriser le ciel (45 min)

**Objectif :** un modèle qui devine l'état du ciel (Dégagé, Nuageux, Brouillard, Précipitations)
à partir de nos capteurs. La borne n'a pas de capteur pour cela.

**Livrable :** `modeles/categorie.joblib` et `rapports/matrice_confusion.png`.

## Étapes

### 1. Lire le squelette

Ouvrez `ml/entrainer_categorie.py`. Il contient six `TODO`. Lancez-le :

```bash
python ml/entrainer_categorie.py
```

✅ *Vous devez voir :* `Rien n'est encore entraîné : complétez les TODO…`

Comparez avec `ml/entrainer_prediction.py` : quelles étapes sont les mêmes ? Qu'est-ce qui change
quand on devine une catégorie au lieu d'un nombre ?

### 2. Faire un commit, puis compléter les TODO avec l'IA

La commande ci-dessous **remplace** le fichier (`--force`). Un commit avant permet de revenir en arrière.

```bash
git add -A
```

```bash
git commit -m "avant atelier 3"
```

```bash
python bin/ia "Complète les TODO" --prompt-file ateliers/prompts/03-classification.md --file ml/entrainer_categorie.py --file ml/preparation.py --out ml/entrainer_categorie.py --force
```

**Relisez le fichier avant de le lancer.** Vérifiez en particulier :

- comment les données sont-elles découpées ? (Rappelez-vous l'atelier 2.)
- `weather_code` ou `categorie` apparaissent-ils dans les entrées du modèle ?

```bash
git diff
```

### 3. Entraîner, comparer à la baseline

```bash
python ml/entrainer_categorie.py
```

✅ *Vous devez voir :* une baseline « toujours Nuageux » autour de **53 %**, une forêt autour de **75 %**
sur le test et de 100 % sur l'entraînement, puis un tableau par catégorie.

Dans le tableau, la colonne `recall` est le **rappel** : sur 100 heures réelles de cette catégorie,
combien le modèle en reconnaît-il ?

- Quelle catégorie a le meilleur rappel ? Pourquoi est-elle facile ? (Regardez `VARIABLES_CATEGORIE`.)
- Quelle catégorie a le plus mauvais rappel ?

### 4. Lire la matrice de confusion

Ouvrez `rapports/matrice_confusion.png`, puis :

```bash
python bin/ia "Explique cette matrice" --prompt-file ateliers/prompts/03b-lire-confusion.md --image rapports/matrice_confusion.png
```

Vérifiez les chiffres que cite l'IA sur l'image.

### 5. Pourquoi le brouillard est-il raté ?

Sur les heures de brouillard de 2025, combien sont reconnues ? Avec quoi les autres sont-elles confondues ?
Et « Dégagé » : pourquoi le modèle le confond-il si souvent avec « Nuageux » ? Pensez à la nuit :
que vaut la luminosité à 3 h du matin, que le ciel soit clair ou couvert ?

### 6. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 3 : catégorisation du ciel"
```

## Si ça coince

| Symptôme | Indice |
|---|---|
| `aucun bloc de code trouvé` ou `réponse tronquée` | Relancez la commande : rien n'a été écrit. |
| Le fichier produit ne marche pas | `git checkout ml/entrainer_categorie.py` revient au squelette. Relancez, ou complétez les TODO à la main en vous aidant de `entrainer_prediction.py`. |
| Le script utilise `train_test_split` | C'est le piège de l'atelier 2. Demandez à l'IA d'utiliser `decouper()`, ou corrigez vous-même. |
| Une exactitude de 99 % | Trop beau : `weather_code` ou `categorie` est sans doute dans les entrées. Le modèle a la réponse sous les yeux. |
| `KeyError: 'categorie'` | La cible se prend dans le tableau complet : `entrainement[CIBLE_CATEGORIE]`. |
| Les étiquettes de la matrice se chevauchent | Ajoutez `xticks_rotation=30` à `ConfusionMatrixDisplay.from_predictions(...)`. |

## Pour aller plus loin

- Ajoutez `class_weight="balanced"` au `RandomForestClassifier` : le rappel du brouillard change-t-il ?
  À quel prix pour les autres catégories ?
- La pluie est presque toujours reconnue. Retirez `precipitation` des entrées : que se passe-t-il ?
  Qu'est-ce que cela dit de ce que le modèle a « compris » ?
