# Ateliers du jour 3

Un guide par atelier, à suivre dans l'ordre. Le but est que vous **cherchiez** : les guides disent
quoi faire et quoi observer, pas ce que vous devez découvrir.

| Atelier | Durée | Guide | On repart avec… | Prompts |
|---|---|---|---|---|
| 0. Réparer le décodeur | 45 min | [atelier-0.md](atelier-0.md) | des mesures justes, prouvées par des tests | `00-tests-decodeur.md` |
| 1. Explorer les données | 30 min | [atelier-1.md](atelier-1.md) | une idée de ce que les données savent dire | `01-expliquer-donnees.md` |
| 2. Prévoir la température dans 3 h | 45 min | [atelier-2.md](atelier-2.md) | un modèle, et une note en laquelle on peut croire | `02-critiquer-entrainement.md` |
| 3. Catégoriser le ciel | 45 min | [atelier-3.md](atelier-3.md) | un second modèle, et la liste de ce qu'il rate | `03-classification.md`, `03b-lire-confusion.md` |
| 4. Exposer le modèle : l'API | 40 min | [atelier-4.md](atelier-4.md) | une route qui répond | `04-endpoint-categorie.md` |
| 5. Tester l'API | 30 min | [atelier-5.md](atelier-5.md) | un contrat vérifié à chaque `pytest` | `05-tests-api.md` |
| Bonus | – | [bonus.md](bonus.md) | pour les plus rapides | `06-cas-usage.md` |

## Ce qui ne change pas depuis les jours 1 et 2

Le sujet est nouveau (Python, des modèles), la méthode est la même. Vous la connaissez déjà.

| Jours 1 et 2 (MiniShop) | Jour 3 (station météo) |
|---|---|
| `SPEC.md` fait foi, pas le code | `SPEC-ML.md` fait foi, pas le code |
| `REGLES-IA.md`, envoyé à chaque appel | le même fichier, avec quatre règles de plus pour les modèles |
| `php bin/ia … --file … --out …` | `python bin/ia …`, mêmes options |
| PHPUnit, `#[DataProvider]` | pytest, `@pytest.mark.parametrize` |
| on teste la règle, pas le code | ateliers 0 et 5 |
| un test rouge n'est pas forcément un mauvais test | atelier 0 : qui a raison, le test ou le code ? |
| casser exprès le code pour voir si les tests servent | ateliers 0 et 5 |
| un test qui passe sans rien vérifier | atelier 2 : une note de modèle trop belle |
| une tolérance plutôt qu'une égalité au pixel près | atelier 5 : une plage plausible plutôt qu'une valeur exacte |
| vérifier le diagnostic de l'IA dans la trace | vérifier ce que dit l'IA dans les chiffres et sur les graphiques |

Ce qui est vraiment nouveau : **un modèle ne se teste pas comme une fonction.** `decoder()` a une bonne
réponse, écrite dans la spec. Un modèle se trompe parfois, et c'est normal. On ne vérifie donc pas qu'il
« a raison » : on **mesure** de combien il se trompe, sur des données qu'il n'a jamais vues, et on compare
à une réponse naïve (la *baseline*). Les tests, eux, vérifient tout ce qui l'entoure : le décodage, le
contrat de l'API, les cas d'erreur.

## Comment lire un guide

Chaque guide a les mêmes rubriques :

- **Le but** : pourquoi on fait cet atelier, et ce qu'il apporte au projet.
- **Le lien avec les jours 1 et 2** : le réflexe que vous réutilisez.
- **Ce que vous devez rendre** : les fichiers et les réponses attendus à la fin.
- **La démarche** : le chemin en quelques lignes, pour savoir où vous allez.
- **Les étapes** : la commande à lancer, puis ✅ *ce que vous devez voir*.
- **C'est réussi si…** : la liste à cocher avant de passer à la suite.
- **Si ça coince** : des indices, du plus léger au plus précis. Lisez-en un à la fois.

Deux signes reviennent :

- 🤔 **Pronostic** : écrivez votre réponse **avant** de lancer la commande. Se tromper ici ne coûte rien,
  et c'est la seule façon de savoir si le résultat vous surprend.
- ✍️ **À noter** : une question à laquelle répondre dans `notes.md`, à la racine du dépôt. Le fichier
  contient déjà toutes les questions. Deux lignes suffisent par réponse.

## Avant de commencer

- Toutes les commandes se lancent **depuis la racine du dépôt**, environnement virtuel activé
  (`source .venv/bin/activate`, ou `.venv\Scripts\activate` sous Windows).
- Les commandes sont écrites **sur une seule ligne** : copiez-les en entier.
- La commande complète de chaque appel à l'IA est en tête du fichier de prompt correspondant.
- Ajoutez `--dry-run` à une commande `bin/ia` pour voir ce qui serait envoyé, sans rien envoyer.

## Les trois réflexes, toujours les mêmes

1. **Commiter avant de lancer l'IA.** Si le résultat ne convient pas : `git restore .` et on recommence.
2. **Relire avant de lancer, lancer avant d'accepter.** Ce que l'IA écrit n'est qu'une proposition.
3. **Un résultat surprenant se vérifie.** Un test rouge, une note trop belle, une affirmation de l'IA :
   `SPEC-ML.md` et les données tranchent, pas l'intuition.

## Vraiment bloqué ?

Dans l'ordre :

1. Relire le message d'erreur en entier (la réponse y est souvent).
2. La rubrique « Si ça coince » du guide.
3. Demander à l'IA : collez l'erreur dans `erreur.txt`, puis
   `python bin/ia "Explique cette erreur et comment la corriger" --file erreur.txt`.
4. Votre voisin, puis le formateur.
5. En dernier recours, la branche `solutions`.

Regarder un fichier de solution sans quitter votre travail :

```bash
git show origin/solutions:station/decodeur.py
```

Voir tout ce que la solution change dans un fichier :

```bash
git diff main origin/solutions -- ml/entrainer_prediction.py
```

## Si rien ne marche

| Symptôme | Piste |
|---|---|
| `python: command not found` | essayez `python3`, ou `py` sous Windows |
| `ModuleNotFoundError: No module named 'pandas'` | l'environnement virtuel n'est pas activé |
| `ModuleNotFoundError: No module named 'preparation'` ou `'ml'` | vous n'êtes pas à la racine du dépôt |
| `ANTHROPIC_API_KEY n'est pas définie` | le fichier `.env` manque, ou la clé n'y est pas collée |
| `… existe déjà : relancez avec --force` | `bin/ia` refuse d'écraser un fichier : relisez-le, puis ajoutez `--force` |
| `réponse tronquée` | la réponse était trop longue : demandez moins de choses à la fois |
