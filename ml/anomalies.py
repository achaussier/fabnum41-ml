"""Bonus : repérer les pannes de capteur avec un détecteur d'anomalies.

    python donnees/generer_synthetique.py --debut 2022-01-01 --jours 1461 --graine 42 --pannes --sortie donnees/synthetique.csv
    python ml/anomalies.py

Ici, pas de réponse à apprendre : l'IsolationForest cherche tout seul les relevés qui ne
ressemblent pas aux autres. Comme les pannes ont été placées exprès par le générateur
(colonne panne_injectee), on peut ensuite vérifier ce qu'il a trouvé.

Sortie : rapports/anomalies.csv, aux colonnes de la table MySQL `anomalie`.
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest

from preparation import charger

CSV_SYNTHETIQUE = "donnees/synthetique.csv"
SORTIE = Path("rapports/anomalies.csv")
PART_ATTENDUE = 0.02  # on s'attend à environ 2 % de relevés anormaux

# Les mesures surveillées, et leur code dans la table `grandeur`.
GRANDEURS = {
    "temperature": "TEMPERATURE",
    "humidite": "HUMIDITE",
    "pression_atmospherique": "PRESSION",
    "vent_vitesse": "VENT_VITESSE",
}

# Sous Windows, le terminal n'affiche pas toujours les accents : on force l'UTF-8.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def preparer(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule, pour chaque mesure, ce qui trahit une panne.

    saut          l'écart avec l'heure précédente (un pic isolé fait un grand saut)
    heures_figee  depuis combien d'heures la valeur n'a pas bougé, au-delà de 2 (un capteur bloqué)
    ecart_semaine l'écart avec la moyenne des 7 derniers jours (une dérive lente)
    """
    variables = pd.DataFrame(index=df.index)
    for nom in GRANDEURS:
        valeur = df[nom]
        variables[f"{nom}_saut"] = valeur.diff().abs()
        a_bouge = valeur.diff().fillna(1) != 0
        heures_sans_bouger = (~a_bouge).groupby(a_bouge.cumsum()).cumsum()
        # Deux heures de suite à la même valeur, c'est banal : on ne compte qu'au-delà.
        variables[f"{nom}_heures_figee"] = heures_sans_bouger.clip(lower=2) - 2
        variables[f"{nom}_ecart_semaine"] = valeur - valeur.rolling("7D").mean()
    return variables.dropna()


def main() -> None:
    if not Path(CSV_SYNTHETIQUE).is_file():
        sys.exit(f"{CSV_SYNTHETIQUE} est absent : lancez d'abord generer_synthetique.py avec --pannes (voir en tête de ce fichier).")
    df = charger(CSV_SYNTHETIQUE)
    if "panne_injectee" not in df.columns:
        sys.exit("La colonne panne_injectee manque : regénérez le fichier avec l'option --pannes.")

    variables = preparer(df)
    df = df.loc[variables.index]

    # Le détecteur ne voit PAS la colonne panne_injectee : il n'a que les mesures.
    detecteur = IsolationForest(n_estimators=200, contamination=PART_ATTENDUE, random_state=42, n_jobs=-1)
    suspect = detecteur.fit_predict(variables) == -1
    # score_samples : plus le score est bas, plus le relevé est étrange. On le ramène entre 0 et 100.
    score = -detecteur.score_samples(variables) * 100

    vraie_panne = df["panne_injectee"].astype(bool)
    trouvees = int((suspect & vraie_panne).sum())
    print("Détection des pannes de capteur (données simulées)")
    print(f"  relevés analysés        : {len(df)}")
    print(f"  pannes injectées        : {int(vraie_panne.sum())}")
    print(f"  relevés signalés        : {int(suspect.sum())}")
    print(f"  pannes retrouvées       : {trouvees} sur {int(vraie_panne.sum())} ({trouvees / vraie_panne.sum():.0%})")
    print(f"  fausses alertes         : {int((suspect & ~vraie_panne).sum())}")
    print(f"  baseline « au hasard »  : {PART_ATTENDUE:.0%} des pannes retrouvées, en signalant autant de relevés")

    # Pour chaque relevé suspect, on cherche la mesure la plus inhabituelle :
    # celle dont les indices s'éloignent le plus de leur valeur ordinaire.
    ecarts = ((variables - variables.mean()) / variables.std()).abs()
    par_grandeur = pd.DataFrame({nom: ecarts.filter(like=nom).max(axis=1) for nom in GRANDEURS})
    coupable = par_grandeur[suspect].idxmax(axis=1)

    anomalies = pd.DataFrame({
        "INSTANT_MESURE_ANORMALE": coupable.index.strftime("%Y-%m-%d %H:%M:%S"),
        "VALEUR_MESUREE": [df.at[instant, nom] for instant, nom in coupable.items()],
        "SCORE_ANOMALIE": score[suspect].round(2),
        "CODE_GRANDEUR": coupable.map(GRANDEURS).to_numpy(),
    })
    SORTIE.parent.mkdir(exist_ok=True)
    anomalies.to_csv(SORTIE, index=False, encoding="utf-8", lineterminator="\n")
    print(f"\n{len(anomalies)} lignes au format de la table anomalie : {SORTIE.as_posix()}")
    print(anomalies.sort_values("SCORE_ANOMALIE", ascending=False).head(5).to_string(index=False))


if __name__ == "__main__":
    main()
