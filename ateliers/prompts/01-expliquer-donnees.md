<!--
Atelier 1 — à lancer après : python ml/explorer.py

python bin/ia "Que montrent ces données ?" --prompt-file ateliers/prompts/01-expliquer-donnees.md --image rapports/pression_pluie_mois.png --image rapports/categories.png

Variante sans image : collez le résumé affiché par explorer.py entre les guillemets de la consigne.
-->

Tu regardes l'historique d'une station météo installée à Blois : un relevé par heure pendant quatre ans
(température, humidité, pression, vent, pluie, luminosité), et pour chaque heure une catégorie
d'état du ciel (Dégagé, Nuageux, Brouillard, Précipitations).

On te fournit des graphiques produits par ml/explorer.py, ou le résumé chiffré qu'il affiche.

Explique, pour des développeurs qui découvrent le machine learning :
1. ce que montre chaque graphique (ou chaque partie du résumé), en deux ou trois phrases ;
2. ce que l'on remarque sur la pression dans les heures qui précèdent la pluie ;
3. quelle catégorie est rare, et pourquoi ce sera une difficulté pour un modèle ;
4. deux variables qui aideront à prévoir la température dans 3 heures, et deux qui aideront
   à deviner l'état du ciel, avec la raison en une phrase.

Contraintes :
- ne décris que ce qui est visible dans ce qu'on t'a fourni : si une information manque, dis-le ;
- pas de formule, pas de jargon : si tu emploies un mot technique, explique-le en une phrase ;
- une demi-page au maximum.
