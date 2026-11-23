"""Bonus : regrouper les journées qui se ressemblent.

    python ml/regrouper.py

Ici, pas de réponse à retrouver : KMeans range les journées en 4 groupes, d'après leurs
ressemblances. C'est ensuite à nous de regarder la moyenne de chaque groupe et de lui
donner un nom (« belle journée d'été », « journée de pluie »…).
"""

import sys

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from preparation import CSV_HISTORIQUE, charger

NOMBRE_DE_GROUPES = 4

# Sous Windows, le terminal n'affiche pas toujours les accents : on force l'UTF-8.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def resumer_par_jour(df):
    """Une ligne par journée : ce qui la caractérise."""
    par_jour = df.resample("D")
    journees = par_jour.agg(
        temperature_moyenne=("temperature", "mean"),
        temperature_min=("temperature", "min"),
        temperature_max=("temperature", "max"),
        humidite_moyenne=("humidite", "mean"),
        pression_moyenne=("pression_atmospherique", "mean"),
        vent_moyen=("vent_vitesse", "mean"),
        pluie_du_jour=("precipitation", "sum"),
        luminosite_max=("luminosite", "max"),
    )
    journees["amplitude"] = journees["temperature_max"] - journees["temperature_min"]
    return journees.drop(columns=["temperature_min", "temperature_max"]).dropna()


def main() -> None:
    journees = resumer_par_jour(charger(CSV_HISTORIQUE))

    # KMeans compare des distances : sans mise à la même échelle, la luminosité
    # (des dizaines de milliers de lux) écraserait la température (quelques degrés).
    echelle = StandardScaler().fit_transform(journees)
    journees["groupe"] = KMeans(n_clusters=NOMBRE_DE_GROUPES, random_state=42, n_init=10).fit_predict(echelle)

    print(f"{len(journees)} journées rangées en {NOMBRE_DE_GROUPES} groupes\n")
    print("Moyenne de chaque groupe")
    moyennes = journees.groupby("groupe").mean().round(1)
    moyennes.insert(0, "nombre_de_jours", journees["groupe"].value_counts().sort_index())
    print(moyennes.T.to_string())

    print("\nMois le plus fréquent de chaque groupe")
    for groupe, mois in journees.groupby("groupe").apply(lambda g: g.index.month.value_counts().idxmax()).items():
        print(f"  groupe {groupe} : mois n°{mois}")

    print("\nÀ vous : quel nom donneriez-vous à chaque groupe ?")


if __name__ == "__main__":
    main()
