"""Bonus : enregistre chaque réponse de l'API dans la table MySQL `resultat_ia`.

Rien ne se passe tant que la variable MYSQL_DSN n'est pas définie (dans l'environnement
ou dans le fichier .env), par exemple :

    MYSQL_DSN=mysql://utilisateur:mot_de_passe@localhost:3306/station_meteo

Il faut alors installer les dépendances bonus : pip install -r requirements-bonus.txt

Règle importante : une panne de la base ne doit jamais empêcher l'API de répondre.
En cas d'erreur, on l'écrit dans le journal et on continue.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

journal = logging.getLogger("uvicorn.error")

# Correspondance entre la grandeur prévue et la table `grandeur` de la base.
CODE_GRANDEUR_TEMPERATURE = "TEMPERATURE"


def lire_dsn() -> str | None:
    """Cherche MYSQL_DSN dans l'environnement, puis dans le fichier .env."""
    if os.environ.get("MYSQL_DSN"):
        return os.environ["MYSQL_DSN"]
    fichier = Path(".env")
    if fichier.is_file():
        for ligne in fichier.read_text(encoding="utf-8").splitlines():
            if ligne.strip().startswith("MYSQL_DSN="):
                return ligne.split("=", 1)[1].strip().strip("\"'") or None
    return None


def inserer(type_resultat: str, contenu_resume: str | None, valeur_prevue: float | None,
            incertitude: float | None, instant_prevu: datetime | None, code_grandeur: str | None) -> bool:
    """Insère une ligne dans resultat_ia. Renvoie True si la ligne a été écrite."""
    dsn = lire_dsn()
    if not dsn:
        return False
    try:
        import pymysql  # importé ici : l'API fonctionne sans cette bibliothèque tant que MYSQL_DSN est vide

        adresse = urlparse(dsn)
        connexion = pymysql.connect(
            host=adresse.hostname, port=adresse.port or 3306,
            user=unquote(adresse.username or ""), password=unquote(adresse.password or ""),
            database=adresse.path.lstrip("/"), charset="utf8mb4", connect_timeout=3,
        )
        with connexion:
            with connexion.cursor() as curseur:
                # Les valeurs passent en paramètres (%s) : jamais de texte collé dans la requête SQL.
                curseur.execute(
                    "INSERT INTO resultat_ia (TYPE_RESULTAT, CONTENU_RESUME, VALEUR_PREVUE, INCERTITUDE, INSTANT_PREVU, CODE_GRANDEUR) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (type_resultat, contenu_resume, valeur_prevue, incertitude, instant_prevu, code_grandeur),
                )
            connexion.commit()
        return True
    except Exception as probleme:  # la base est en panne ? L'API répond quand même.
        journal.warning("resultat_ia : enregistrement impossible (%s)", probleme)
        return False


def enregistrer_prevision(reponse: dict) -> bool:
    """Enregistre la réponse de /predict/temperature."""
    instant = datetime.strptime(reponse["instant_prevu"], "%Y-%m-%dT%H:%M:%SZ")
    return inserer("PREVISION_TEMPERATURE", None, reponse["valeur_prevue"], reponse["incertitude"],
                   instant, CODE_GRANDEUR_TEMPERATURE)


def enregistrer_categorie(instant_mesure: datetime, reponse: dict) -> bool:
    """Enregistre la réponse de /classify/conditions : la catégorie va dans CONTENU_RESUME."""
    probabilite = reponse["probabilites"][reponse["categorie"]]
    resume = f"{reponse['categorie']} (probabilité {probabilite:.2f})"
    return inserer("CATEGORIE", resume, None, None, instant_mesure.replace(tzinfo=None), None)
