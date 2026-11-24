… envoi à claude-sonnet-5-5
ℹ tokens : 11369 envoyés, 5402 reçus
# Trois cas d'usage pour la station de Blois

## 1. « Le vent va-t-il se renforcer dans les 3 heures ? »

1. **Question :** quelle sera la rafale maximale dans 3 heures ?
2. **Famille :** prévoir un nombre.
3. **Entrées :** les 6 dernières heures de `vent_vitesse`, `rafale_max` et `pression_atmospherique` (relevés de 10 minutes résumés à l'heure), plus l'heure et le mois.
4. **Sortie :** la rafale prévue en m/s, avec une incertitude. **Baseline :** la persistance (« dans 3 h, la rafale sera la même que maintenant »).
5. **Table `resultat_ia` :**

| Colonne | Valeur |
|---|---|
| `TYPE_RESULTAT` | `prevision_rafale` |
| `CONTENU_RESUME` | `Rafales prévues à 14,2 m/s` |
| `VALEUR_PREVUE` | 14.20 |
| `INCERTITUDE` | 2.30 |
| `INSTANT_PREVU` | 2025-03-14 12:00:00 |
| `CODE_GRANDEUR` | `rafale_max` |

   Le site peut comparer `VALEUR_PREVUE` à `seuil.VALEUR_SEUIL` (même `CODE_GRANDEUR`) pour afficher « proche du seuil vent fort ». On n'écrit rien dans `alerte` : une alerte part d'une mesure réelle, pas d'une prévision.
6. **Limite :** les pics de vent sont brefs et rares, donc le modèle les sous-estimera, et la persistance sera difficile à battre.

## 2. « Un de mes capteurs est-il en train de dérailler ? »

1. **Question :** cette mesure est-elle normale, ou la borne a-t-elle un problème ?
2. **Famille :** repérer l'anormal.
3. **Entrées :** `temperature`, `humidite`, `pression_atmospherique` et `vent_vitesse` des dernières 24 h, au pas de 10 minutes. On apprend ce qui est « normal » sur 2022-2024.
4. **Sortie :** un score d'anormalité par relevé. **Baseline :** la règle simple « valeur hors de la plage autorisée » (par exemple humidité à 150 %). Le modèle doit repérer ce que cette règle laisse passer, comme une valeur bloquée ou un saut brutal.
5. **Table `anomalie` :**

| Colonne | Valeur |
|---|---|
| `INSTANT_MESURE_ANORMALE` | 2025-07-02 14:10:00 |
| `VALEUR_MESUREE` | 2.10 |
| `SCORE_ANOMALIE` | 4.80 |
| `CODE_GRANDEUR` | `temperature` |

   `DATE_DETECTION` se remplit seule. Il n'y a qu'une ligne par grandeur et par instant (clé unique).
6. **Limite :** on n'a aucune vraie panne étiquetée. Pour mesurer sur 2025, il faudra injecter de fausses pannes dans le jeu de test, et un orage violent peut ressembler à une panne.

## 3. « À quel type de journée ressemble aujourd'hui ? »

1. **Question :** cette journée est-elle plutôt « fraîche et pluvieuse », « chaude et sèche », « venteuse » ?
2. **Famille :** regrouper.
3. **Entrées :** un résumé par journée de 24 h : température min et max, humidité moyenne, variation de `pression_atmospherique`, `vent_vitesse` moyen, `precipitation` totale. Pas de `weather_code` ni de `categorie`.
4. **Sortie :** un numéro de groupe (3 à 5 groupes). **Baseline :** regrouper simplement par saison, d'après le mois.
5. **Table `resultat_ia` :**

| Colonne | Valeur |
|---|---|
| `TYPE_RESULTAT` | `type_journee` |
| `CONTENU_RESUME` | `Journée type 2 : fraîche, humide, pression en baisse` |
| `VALEUR_PREVUE`, `INCERTITUDE`, `INSTANT_PREVU`, `CODE_GRANDEUR` | `NULL` (colonnes facultatives) |

6. **Limite :** il n'y a pas de « bonne réponse » à mesurer, et sur 4 ans les groupes risquent de recopier les saisons. Il faut les nommer à la main et vérifier qu'ils tiennent sur 2025.

## Celui que je ferais en premier : le n°1

- Il ressemble au modèle de température : on réutilise `charger`, `ajouter_variables` (à étendre) et `decouper` de `ml/preparation.py`.
- Le résultat se mesure clairement : l'erreur moyenne en m/s, comparée à la persistance, sur 2025.
- Il est utile tout de suite, car il se relie aux seuils et aux alertes déjà en base.

Les nos 2 et 3 demandent d'abord de décider comment les évaluer, ce qui est plus délicat pour un débutant.

**À vérifier avant de coder :** `resultat_ia.CODE_GRANDEUR` et `anomalie.CODE_GRANDEUR` doivent exister dans la table `grandeur`. Le dump ne contient que la structure, pas les lignes. J'ai supposé que les codes reprennent les noms de colonnes de `SPEC-ML.md`.
