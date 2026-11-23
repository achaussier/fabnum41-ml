"""Décodage du message envoyé par la borne SenseCAP S2120.

La borne envoie ses mesures sous la forme d'un texte hexadécimal (le « payload »),
découpé en blocs. Le détail du découpage est dans SPEC-ML.md, section « Décodage ».
"""


def _entier(payload_hex: str, debut: int, fin: int) -> int:
    """Lit un morceau du payload et le convertit en nombre entier."""
    return int(payload_hex[debut:fin], 16)


def _entier_signe(payload_hex: str, debut: int, fin: int) -> int:
    """Comme _entier, mais pour une valeur qui peut être négative (la température)."""
    valeur = _entier(payload_hex, debut, fin)
    maximum = 16 ** (fin - debut)
    return valeur - maximum if valeur >= maximum // 2 else valeur


def decoder(payload_hex: str) -> dict:
    """Transforme le payload de la borne en dictionnaire de mesures."""
    payload_hex = payload_hex.strip()
    return {
        "temperature": _entier_signe(payload_hex, 2, 6) / 10,
        "humidite": _entier(payload_hex, 6, 8) / 10,
        "luminosite": _entier(payload_hex, 8, 16),
        "indice_uv": _entier(payload_hex, 16, 18) / 10,
        "vent_vitesse": _entier(payload_hex, 18, 22) / 10,
        "vent_direction": _entier(payload_hex, 24, 28) / 10,
        "precipitation": _entier(payload_hex, 28, 36) / 1000,
        "pression_atmospherique": _entier(payload_hex, 36, 40),
        "rafale_max": _entier(payload_hex, 42, 46) / 10,
        "pluie_cumul": _entier(payload_hex, 46, 54) / 10,
    }
