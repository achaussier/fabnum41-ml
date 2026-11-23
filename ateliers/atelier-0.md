# Atelier 0 — Réparer le décodeur (45 min)

**Objectif :** des données justes avant tout modèle. Un modèle apprend ce qu'on lui montre :
si le décodeur se trompe, le modèle apprendra des valeurs fausses.

## Étapes

### 1. Vérifier l'installation

```bash
pytest
```

✅ *Vous devez voir :* `2 passed`.

### 2. Lire la règle

Ouvrez `SPEC-ML.md`, section **« Décodage »**. Repérez :

- le tableau de découpage (quels caractères, quel calcul, quelle unité) ;
- le **payload de référence** et ses valeurs attendues ;
- ce qui doit se passer pour un payload de 40 caractères.

Ouvrez ensuite `station/decodeur.py`. Ne corrigez rien pour l'instant.

### 3. Essayer à la main

```bash
python -c "from station.decodeur import decoder; print(decoder('01004958000009BE00000802000C00000000276B4C001900007B08'))"
```

Comparez avec le tableau « Payload complet » de la spec. Tout vous paraît-il plausible ?
Une humidité, une direction du vent, une pression : dans quelles unités les attend-on ?

### 4. Faire générer les tests depuis la spec

Lisez `ateliers/prompts/00-tests-decodeur.md`. Pourquoi demande-t-on de tester « la règle, pas le code » ?

```bash
python bin/ia "Écris les tests de decoder()" --prompt-file ateliers/prompts/00-tests-decodeur.md --file SPEC-ML.md --file station/decodeur.py --out station/tests/test_decodeur.py
```

Relisez le fichier produit, en particulier le commentaire en tête : quels écarts l'IA signale-t-elle ?

### 5. Lancer les tests

```bash
pytest station
```

✅ *Vous devez voir :* du **rouge**. C'est le résultat attendu : les tests viennent de la spec, le code a tort.

Notez les tests qui échouent. Combien de problèmes différents y a-t-il ?

### 6. Corriger jusqu'au vert

Corrigez `station/decodeur.py`, un problème à la fois, en relançant `pytest station` après chaque correction.

✅ *Vous devez voir, à la fin :* tous les tests verts.

### 7. Commit

```bash
git add -A
```

```bash
git commit -m "atelier 0 : décodeur corrigé et testé"
```

## Si ça coince

| Symptôme | Indice |
|---|---|
| Tous les tests sont verts dès le départ | L'IA a peut-être recopié les valeurs du code. Vérifiez qu'un test attend bien `humidite == 91` pour le payload de référence. |
| `ValueError: invalid literal for int() with base 16: ''` | Que renvoie `payload_hex[42:46]` quand le payload ne fait que 40 caractères ? |
| Le test d'humidité échoue avec `9.1` | La borne envoie l'humidité en pourcentage entier. Y a-t-il une division en trop ? |
| Le test de pression échoue avec `10124` | La borne envoie des dixièmes d'hectopascal. |
| Un test échoue alors que la spec vous semble respectée | Relisez le test : l'IA se trompe aussi. La spec fait foi, pas le test. |
| Un test compare `0.9 == 0.9` et échoue | Les décimaux se comparent avec `pytest.approx(0.9)`. |

Il y a **quatre** problèmes à trouver. La solution est sur la branche `solutions`.

## Pour aller plus loin

Dans le projet d'origine, la pression n'a jamais été enregistrée dans MongoDB. Relisez la slide
« Avant le modèle : des données justes » : pourquoi personne ne s'en est aperçu ?
