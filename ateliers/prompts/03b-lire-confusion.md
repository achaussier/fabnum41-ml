<!--
Atelier 3 — à lancer après : python ml/entrainer_categorie.py

python bin/ia "Explique cette matrice" --prompt-file ateliers/prompts/03b-lire-confusion.md --image rapports/matrice_confusion.png

Astuce : collez aussi le « rapport par catégorie » affiché par le script dans la consigne.
-->

L'image jointe est la matrice de confusion d'un modèle qui devine l'état du ciel à partir des relevés
d'une station météo. En ligne : ce qui s'est vraiment passé. En colonne : la réponse du modèle.
Les quatre catégories sont Dégagé, Nuageux, Brouillard et Précipitations.

Explique, pour des développeurs qui découvrent le machine learning :
1. comment lire ce tableau, en prenant une case comme exemple ;
2. la catégorie la mieux reconnue et la moins bien reconnue, avec les chiffres lus sur l'image ;
3. les deux confusions les plus fréquentes (« le modèle répond X alors que c'était Y »), et une raison
   physique plausible pour chacune : que mesurent les capteurs, et que ne mesurent-ils pas ?
4. le cas du brouillard : sur le nombre d'heures de brouillard réelles, combien sont reconnues ?
   Pourquoi une catégorie rare est-elle plus difficile à apprendre ?
5. une seule piste d'amélioration, concrète et réaliste pour ce projet.

Contraintes :
- cite uniquement des chiffres lisibles sur l'image ; si un chiffre est illisible, dis-le ;
- pas de formule ; explique « rappel » avec une phrase du type « sur 100 heures de brouillard… » ;
- une demi-page au maximum.
