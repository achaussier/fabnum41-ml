# Mon carnet de bord — jour 3

Une réponse courte par question : deux lignes suffisent. Les guides des ateliers disent à quel moment
répondre (signe ✍️) et quand écrire un pronostic **avant** de lancer une commande (signe 🤔).

Ce fichier fait partie de ce que vous rendez : il est commité avec le reste à la fin de chaque atelier.

## Atelier 0 — Réparer le décodeur

**0.1 🤔 Pronostic.** En comparant ce que renvoie `decoder()` au tableau de la spec, quelles valeurs
vous paraissent fausses ? Combien de tests rouges attendez-vous ?

> 

**0.2** Pour chaque test rouge (ou chaque groupe de tests rouges) : qui a raison, le test ou le code ?
Quelle ligne de `SPEC-ML.md` le prouve ?

> 

**0.3** Combien d'écarts différents y avait-il entre le code et la spec ? Un écart = une phrase.

> 

**0.4** `pytest` affichait `2 passed` avant que vous ne touchiez à quoi que ce soit. Pourquoi le test
fourni n'a-t-il rien vu ?

> 

**0.5** Quand vous avez cassé exprès le calcul de la pluie, vos tests l'ont-ils vu ? Pourquoi ?

> 

## Atelier 1 — Explorer les données

**1.1** Température la plus basse, la plus haute. Est-ce plausible à Blois ?

> 

**1.2** La catégorie la plus fréquente, et sa part. Quel score aurait un « modèle » qui répondrait
toujours cette catégorie ?

> 

**1.3** Que fait la pression dans les heures qui précèdent la pluie ?

> 

**1.4** Une affirmation de l'IA que vous avez pu vérifier sur un graphique, et une que vous ne pouvez
pas vérifier avec ce qu'on lui a fourni.

> 

**1.5 🤔 Pronostic.** Les deux variables qui aideront le plus à prévoir la température dans 3 heures,
et pourquoi.

> 

## Atelier 2 — Prévoir la température dans 3 h

**2.1** Les trois erreurs moyennes du premier lancement (baseline, forêt sur l'entraînement, forêt sur
le test).

> 

**2.2** La ligne qui contredit la spec, et la règle qu'elle contredit. Qui l'a trouvée : vous, ou l'IA ?

> 

**2.3 🤔 Pronostic.** Après correction, l'erreur sur le test va-t-elle monter ou descendre ? Pourquoi ?

> 

**2.4** Le tableau final :

| | Erreur moyenne sur le test |
|---|---|
| Forêt, découpage au hasard | … °C |
| Forêt, découpage dans le temps | … °C |
| Baseline « persistance » | … °C |

**2.5** `pytest` était vert avant votre correction, et il l'est toujours. Pourquoi aucun test n'a-t-il
vu ce défaut ? Qu'est-ce qui l'a révélé ?

> 

**2.6** Vos deux variables de la question 1.5 étaient-elles les bonnes ?

> 

## Atelier 3 — Catégoriser le ciel

**3.1 🤔 Pronostic.** Quelle catégorie sera la plus difficile à reconnaître, et pourquoi ?

> 

**3.2** Relecture du script écrit par l'IA : comment découpe-t-il les données ? Quelles colonnes
regarde le modèle ? Avez-vous dû corriger quelque chose ?

> 

**3.3** Baseline, exactitude sur l'entraînement, exactitude sur le test.

> 

**3.4** Le rappel de chaque catégorie. Laquelle est la mieux reconnue, laquelle la moins bien ?
Votre pronostic 3.1 était-il juste ?

> 

**3.5** Pourquoi le modèle confond-il si souvent « Dégagé » et « Nuageux » ? Est-ce la faute de
l'algorithme, ou des capteurs ?

> 

## Atelier 4 — Exposer le modèle : l'API

**4.1** Pourquoi faut-il envoyer **4** relevés pour une prévision, et un seul pour une catégorie ?

> 

**4.2** D'où vient l'`incertitude` ? Comment l'expliqueriez-vous à quelqu'un qui consulte le site ?

> 

**4.3** Vos étapes en français pour la route `/classify/conditions`, écrites **avant** d'appeler l'IA.

> 

**4.4** Une différence entre vos étapes et la fonction proposée par l'IA. Qui avait raison ?

> 

## Atelier 5 — Tester l'API

**5.1** Votre liste de cas à tester, écrite d'après `SPEC-ML.md` **avant** de générer les tests.

> 

**5.2** Un cas que l'IA a couvert et que vous aviez oublié, ou l'inverse.

> 

**5.3** Quand vous avez remplacé `hours=3` par `hours=2`, quel test est devenu rouge ?

> 

**5.4** Tous vos tests sont verts. Qu'est-ce que cela garantit ? Qu'est-ce que cela ne garantit pas,
et où trouve-t-on cette garantie-là ?

> 

## Bilan de la journée

**Ce que je vérifierais en premier si l'on me présentait un modèle « qui marche à 95 % » :**

> 
