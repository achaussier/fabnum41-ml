# Atelier 1 — Explorer les données (30 min)

## Le but

Avant d'entraîner quoi que ce soit, on regarde. Un modèle ne trouvera dans les données que ce qui s'y
trouve déjà : si la pression ne bouge pas avant la pluie, aucun algorithme ne l'inventera. Cet atelier
sert à savoir **ce que les données peuvent dire**, et ce qui leur manque.

Vous y fixez aussi deux repères dont vous aurez besoin plus tard : la part de la catégorie la plus
fréquente (atelier 3) et vos deux variables favorites (atelier 2).

## Le lien avec les jours 1 et 2

Au jour 1, vous aviez commencé par faire un achat à la main et par lire `SPEC.md` avant d'écrire un seul
test. C'est le même geste : **connaître le terrain avant de demander quoi que ce soit à l'IA**. Et comme
au jour 2 avec les traces, ce que dit l'IA sur une image se vérifie sur l'image.

## Ce que vous devez rendre

- les trois graphiques de `rapports/`, que vous savez commenter ;
- `notes.md` : questions 1.1 à 1.5 ;
- pas de code à écrire dans cet atelier.

## La démarche

1. Lancer l'exploration et lire le résumé chiffré.
2. Regarder les trois graphiques et répondre **vous-même**.
3. Seulement ensuite, demander à l'IA, et comparer.
4. Lire comment les variables du modèle sont fabriquées.
5. Parier sur deux variables.

## Étapes

### 1. Lancer l'exploration

```bash
python ml/explorer.py
```

✅ *Vous devez voir :* `Nombre de relevés : 35064`, un tableau minimum / moyenne / maximum,
« Valeurs manquantes : aucune », la répartition des quatre catégories, puis trois noms de fichiers.

✍️ **Questions 1.1 et 1.2.** Pour la 1.1, comparez aux « plages autorisées » de la section 1 de `SPEC-ML.md` :
une valeur en dehors de sa plage serait le signe d'un capteur ou d'un décodeur en défaut.

### 2. Regarder les graphiques, sans l'IA

Ils sont dans `rapports/`. Pour chacun, répondez avant de passer au suivant :

- `temperature_annee.png` : que montre la courbe rouge ? Et l'épaisseur du tracé bleu autour d'elle ?
  À quelle période de l'année ce tracé est-il le plus large ?
- `pression_pluie_mois.png` : repérez trois épisodes de pluie. Que fait la pression dans les heures
  qui les précèdent ? Est-ce vrai pour les trois ?
- `categories.png` : quelle catégorie domine ? Laquelle est rare ?

✍️ **Question 1.3.**

### 3. Demander à l'IA, puis comparer

```bash
python bin/ia "Que montrent ces données ?" --prompt-file ateliers/prompts/01-expliquer-donnees.md --image rapports/pression_pluie_mois.png --image rapports/categories.png
```

Lisez sa réponse en gardant les deux images ouvertes.

- Dit-elle la même chose que vous sur la pression ? Si non, qui a raison ? Retournez voir l'image.
- Cite-t-elle des dates ou des chiffres ? Vérifiez-en deux.
- Parle-t-elle de quelque chose qui n'est sur aucune des deux images ?

✍️ **Question 1.4.**

### 4. Lire la préparation

Ouvrez `ml/preparation.py` et lisez `ajouter_variables()`. Prenez la ligne du 14 mars 2025 à 9 h :

- que contient `temperature_moins_3h` : la température de quelle heure ?
- que contient `temperature_dans_3h` : la température de quelle heure ? Pourquoi l'appelle-t-on la « cible » ?
- au moment où la borne envoie son relevé de 9 h, laquelle de ces deux valeurs connaît-on déjà ?

Vérifiez votre réponse :

```bash
python -c "import sys; sys.path.insert(0, 'ml'); from preparation import charger, ajouter_variables; d = ajouter_variables(charger()); print(d.loc['2025-03-14 06:00':'2025-03-14 12:00', ['temperature', 'temperature_moins_3h', 'temperature_dans_3h']].to_string())"
```

### 5. Parier sur deux variables

Relisez la liste `VARIABLES_PREDICTION`.

🤔 ✍️ **Question 1.5** : les deux variables qui, selon vous, aideront le plus à prévoir la température
dans 3 heures, et pourquoi. Vous vérifierez à l'atelier 2.

## C'est réussi si…

- [ ] Vous savez dire, graphique à l'appui, ce que fait la pression avant la pluie
- [ ] Vous connaissez la part de la catégorie la plus fréquente, et ce que cela implique pour un modèle
- [ ] Vous avez vérifié au moins deux affirmations de l'IA sur les images
- [ ] Vous savez expliquer la différence entre une variable d'entrée et la cible
- [ ] Les questions 1.1 à 1.5 de `notes.md` ont une réponse

## Si ça coince

| Symptôme | Indice |
|---|---|
| `No module named 'preparation'` | Lancez la commande depuis la racine du dépôt, pas depuis `ml/`. |
| Les accents s'affichent mal sous Windows | Utilisez le terminal de VS Code ou Windows Terminal. |
| `image introuvable` | Les graphiques n'existent qu'après `python ml/explorer.py`. |
| Je ne vois rien de net sur la pression | Ne regardez pas tout le mois : choisissez **un** épisode de pluie et remontez la courbe sur les 12 heures d'avant. |
| L'IA parle de choses invisibles sur l'image | C'est une invention. Quelle phrase du prompt devait l'en empêcher ? Relancez en collant le résumé chiffré de l'étape 1 dans la consigne. |
| Je ne sais pas quelles variables choisir | Pour deviner la température de 15 h, que voudriez-vous savoir à midi ? |

## Pour aller plus loin

```bash
python donnees/generer_synthetique.py --debut 2022-01-01 --jours 1461 --graine 42 --pannes --sortie donnees/synthetique.csv
```

```bash
python ml/explorer.py donnees/synthetique.csv
```

Comparez les graphiques avec ceux des vraies données. Qu'est-ce qui paraît « trop propre » ? Pourquoi un
modèle entraîné sur ces données simulées serait-il inutile pour prévoir le temps à Blois ?
