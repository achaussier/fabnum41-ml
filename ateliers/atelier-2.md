# Atelier 2 — Prévoir la température dans 3 h (45 min)

**Objectif :** un modèle qui bat la baseline, **mesuré honnêtement**.

**Livrable :** `modeles/prediction_temperature.joblib` et **trois** erreurs moyennes notées dans `notes.md`.

## Étapes

### 1. Lancer l'entraînement

```bash
python ml/entrainer_prediction.py
```

Comptez une vingtaine de secondes.

✅ *Vous devez voir :* trois erreurs moyennes en °C (baseline, forêt sur l'entraînement, forêt sur le test),
puis `Modèle enregistré : modeles/prediction_temperature.joblib`.

Notez les trois chiffres. Puis répondez :

- La forêt bat-elle la baseline « persistance » ? De combien ?
- Pourquoi l'erreur sur l'entraînement est-elle bien plus basse que l'erreur sur le test ?
  (Slide « Apprendre par cœur n'est pas comprendre ».)

Ouvrez `rapports/prediction_vs_reel.png`. La courbe vous paraît-elle normale ? Regardez bien les points.

### 2. Faire relire le script par l'IA

```bash
python bin/ia "Ce résultat est-il fiable ?" --prompt-file ateliers/prompts/02-critiquer-entrainement.md --file ml/entrainer_prediction.py --file ml/preparation.py --file SPEC-ML.md
```

### 3. Trouver le détail qui cloche

Un détail du script contredit **un réflexe vu ce matin** et **une règle de `SPEC-ML.md`** (section 4).
Lequel ? Trouvez la ligne. Vérifiez par vous-même ce que dit l'IA : a-t-elle raison ?

### 4. Corriger, relancer, comparer

Corrigez `ml/entrainer_prediction.py` en réutilisant une fonction qui existe déjà dans `ml/preparation.py`.
Supprimez l'import devenu inutile.

```bash
python ml/entrainer_prediction.py
```

✅ *Vous devez voir :* environ 26 300 exemples d'entraînement et 8 750 exemples de test, et une erreur
sur le test **plus haute** qu'avant. C'est normal : c'est la vraie.

Complétez `notes.md` :

| | Erreur moyenne sur le test |
|---|---|
| Forêt, découpage au hasard | … °C |
| Forêt, découpage dans le temps | … °C |
| Baseline « persistance » | … °C |

Rouvrez `rapports/prediction_vs_reel.png` : qu'est-ce qui a changé sur la courbe ?

### 5. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 2 : prévision mesurée honnêtement"
```

Le fichier `.joblib` n'est pas commité (il est dans `.gitignore`) : un modèle se **reconstruit** à partir du code et des données.

## Si ça coince

| Symptôme | Indice |
|---|---|
| Je ne vois pas le problème | Cherchez la ligne qui sépare entraînement et test. Comment choisit-elle les lignes de test ? |
| L'IA ne signale rien | Collez dans la consigne la règle n°1 de la section 4 de `SPEC-ML.md` et demandez si le script la respecte. |
| Je ne sais pas quoi écrire à la place | `decouper(donnees)` renvoie deux tableaux : `entrainement` et `test`. Il reste à prendre les colonnes `VARIABLES_PREDICTION` et `CIBLE_PREDICTION` dans chacun. |
| `NameError: name 'decouper' is not defined` | Ajoutez `decouper` à la ligne `from preparation import …`. |
| L'erreur a augmenté, j'ai dû casser quelque chose | Non : avant, le modèle était interrogé sur des heures encadrées par des heures qu'il connaissait. Maintenant il est interrogé sur 2025, qu'il n'a jamais vue. |
| L'écart entre les deux erreurs est petit | Quelques centièmes de degré suffisent : l'important est que la première note était **trop belle**, et que rien ne le signalait. |

## Pour aller plus loin

- Vos deux variables de l'atelier 1 étaient-elles utiles ? Ajoutez à la fin du script :
  `print(sorted(zip(modele.feature_importances_.round(3), VARIABLES_PREDICTION), reverse=True))`
- Retirez `temperature_moins_1h` et `temperature_moins_3h` de `VARIABLES_PREDICTION` : que devient l'erreur ?
  (Remettez-les ensuite : l'API en a besoin.)
