# Atelier 1 — Explorer les données (30 min)

**Objectif :** connaître ses données avant de leur faire confiance.

## Étapes

### 1. Lancer l'exploration

```bash
python ml/explorer.py
```

✅ *Vous devez voir :* `Nombre de relevés : 35064`, un tableau minimum / moyenne / maximum,
« Valeurs manquantes : aucune », la répartition des quatre catégories, puis trois noms de fichiers.

Lisez le résumé et répondez :

- Quelle est la température la plus basse, la plus haute ? Est-ce plausible à Blois ?
- Quelle catégorie est la plus fréquente ? Laquelle est rare ?

### 2. Ouvrir les graphiques

Ils sont dans `rapports/` :

- `temperature_annee.png` : que voit-on sur la courbe rouge ? Et dans l'épaisseur de la zone bleue ?
- `pression_pluie_mois.png` : que fait la pression **avant** les barres de pluie ?
- `categories.png` : si un modèle répondait toujours la catégorie la plus fréquente, quel serait son score ?

### 3. Les faire commenter par l'IA

```bash
python bin/ia "Que montrent ces données ?" --prompt-file ateliers/prompts/01-expliquer-donnees.md --image rapports/pression_pluie_mois.png --image rapports/categories.png
```

Comparez sa réponse à ce que **vous** avez vu. A-t-elle inventé quelque chose qui n'est pas sur les images ?

### 4. Lire la préparation

Ouvrez `ml/preparation.py` et lisez `ajouter_variables()`. Pour la ligne du 14 mars 2025 à 9 h :

- que contient `temperature_moins_3h` ?
- que contient `temperature_dans_3h` ? Pourquoi l'appelle-t-on la « cible » ?

### 5. Noter deux variables utiles

Écrivez dans un fichier `notes.md` deux variables qui, selon vous, aideront à prévoir la température
dans 3 heures, et pourquoi. Vous vérifierez à l'atelier 2.

## Si ça coince

| Symptôme | Indice |
|---|---|
| `No module named 'preparation'` | Lancez la commande depuis la racine du dépôt, pas depuis `ml/`. |
| Les accents s'affichent mal sous Windows | Utilisez le terminal de VS Code ou Windows Terminal. |
| `image introuvable` | Les graphiques n'existent qu'après `python ml/explorer.py`. |
| L'IA parle de choses invisibles sur l'image | C'est une hallucination : dites-lui « ne décris que ce qui est visible », ou collez le résumé chiffré dans la consigne. |

## Pour aller plus loin

```bash
python donnees/generer_synthetique.py --debut 2022-01-01 --jours 1461 --graine 42 --pannes --sortie donnees/synthetique.csv
```

```bash
python ml/explorer.py donnees/synthetique.csv
```

Comparez les graphiques avec ceux des vraies données. Qu'est-ce qui paraît « trop propre » ?
