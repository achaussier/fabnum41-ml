# Ateliers du jour 3

Un guide par atelier. Chaque guide donne l'objectif, les étapes, ce que vous devez voir (✅),
et une rubrique « Si ça coince » avec des indices. Cherchez d'abord, lisez les indices ensuite.

| Atelier | Durée | Guide | Prompts |
|---|---|---|---|
| 0. Réparer le décodeur | 45 min | [atelier-0.md](atelier-0.md) | `00-tests-decodeur.md` |
| 1. Explorer les données | 30 min | [atelier-1.md](atelier-1.md) | `01-expliquer-donnees.md` |
| 2. Prévoir la température dans 3 h | 45 min | [atelier-2.md](atelier-2.md) | `02-critiquer-entrainement.md` |
| 3. Catégoriser le ciel | 45 min | [atelier-3.md](atelier-3.md) | `03-classification.md`, `03b-lire-confusion.md` |
| 4. Exposer le modèle : l'API | 40 min | [atelier-4.md](atelier-4.md) | `04-endpoint-categorie.md` |
| 5. Tester l'API | 30 min | [atelier-5.md](atelier-5.md) | `05-tests-api.md` |
| Bonus | – | [bonus.md](bonus.md) | `06-cas-usage.md` |

## Avant de commencer

- Toutes les commandes se lancent **depuis la racine du dépôt**, environnement virtuel activé
  (`source .venv/bin/activate`, ou `.venv\Scripts\activate` sous Windows).
- Les commandes sont écrites **sur une seule ligne** : copiez-les telles quelles.
- La commande complète de chaque appel à l'IA est en tête du fichier de prompt correspondant.
- Ajoutez `--dry-run` à une commande `bin/ia` pour voir ce qui serait envoyé, sans rien envoyer.
- La règle des jours 1 et 2 tient toujours : **ce que l'IA écrit, on le lit, on le lance, on le vérifie.**
- Faites un commit à la fin de chaque atelier : `git add -A` puis `git commit -m "atelier N"`.

## Si rien ne marche

| Symptôme | Piste |
|---|---|
| `python: command not found` | essayez `python3`, ou `py` sous Windows |
| `ModuleNotFoundError: No module named 'pandas'` | l'environnement virtuel n'est pas activé |
| `ModuleNotFoundError: No module named 'preparation'` ou `'ml'` | vous n'êtes pas à la racine du dépôt |
| `ANTHROPIC_API_KEY n'est pas définie` | le fichier `.env` manque, ou la clé n'y est pas collée |
| `… existe déjà : relancez avec --force` | `bin/ia` refuse d'écraser un fichier : relisez-le, puis ajoutez `--force` |
| `réponse tronquée` | la réponse était trop longue : demandez moins de choses à la fois |
