"""Bonus : convertit le CSV d'historique en JSON importable dans MongoDB.

    python donnees/vers_mongo.py donnees/historique_blois.csv > mesures.json
    mongoimport --uri "$MONGODB_URI" --collection mesures --jsonArray --file mesures.json

Sous PowerShell, préférez l'option --sortie (la redirection « > » y change l'encodage) :

    python donnees/vers_mongo.py donnees/historique_blois.csv --sortie mesures.json

Chaque ligne devient un document de la collection `mesures`. Les colonnes d'étiquette
(weather_code, categorie) ne sont pas exportées : la borne ne les mesure pas.
La date est écrite au format « Extended JSON » ({"$date": ...}) pour que MongoDB
la range comme une vraie date, et non comme un texte.
"""

import argparse
import csv
import json
import sys

ENTIERS = {"humidite", "vent_direction", "luminosite"}
IGNOREES = {"weather_code", "categorie", "panne_injectee"}


def convertir(ligne: dict) -> dict:
    document = {}
    for nom, valeur in ligne.items():
        if nom in IGNOREES:
            continue
        if nom == "reference_capteur":
            document[nom] = valeur
        elif nom == "instant_mesure":
            document[nom] = {"$date": valeur}
        elif nom in ENTIERS:
            document[nom] = int(valeur)
        else:
            document[nom] = float(valeur)
    return document


def main() -> None:
    analyseur = argparse.ArgumentParser(description="CSV de relevés → JSON pour mongoimport --jsonArray.")
    analyseur.add_argument("csv", help="fichier CSV à convertir")
    analyseur.add_argument("--sortie", help="fichier JSON à écrire (par défaut : la sortie standard)")
    options = analyseur.parse_args()

    with open(options.csv, encoding="utf-8", newline="") as fichier:
        documents = [convertir(ligne) for ligne in csv.DictReader(fichier)]

    # ensure_ascii : le JSON ne contient que des caractères simples, quel que soit le terminal.
    texte = json.dumps(documents, ensure_ascii=True, indent=1)
    if options.sortie:
        with open(options.sortie, "w", encoding="utf-8") as fichier:
            fichier.write(texte + "\n")
        print(f"{len(documents)} documents écrits dans {options.sortie}", file=sys.stderr)
    else:
        print(texte)


if __name__ == "__main__":
    main()
