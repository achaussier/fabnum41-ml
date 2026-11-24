… envoi à claude-sonnet-5-5
✔ fichier écrit : station/tests/test_decodeur.py — relisez-le, puis lancez les tests.
ℹ tokens : 7074 envoyés, 6536 reçus
```python
"""Tests de decoder() (station/decodeur.py).

La règle testée est la section « Décodage » de SPEC-ML.md, pas le code.

ÉCARTS CONSTATÉS entre station/decodeur.py et SPEC-ML.md (ces tests échouent tant que le code n'est pas corrigé) :
1. `humidite` est divisée par 10 dans le code ; la spec dit « valeur telle quelle (entier) » (91, pas 9.1).
2. `vent_direction` est divisée par 10 dans le code ; la spec dit « valeur telle quelle (entier) » (126, pas 12.6).
3. `pression_atmospherique` n'est pas divisée par 10 dans le code ; la spec dit « valeur / 10 » (1012.4, pas 10124).
4. Un payload de 40 caractères est valide d'après la spec (`rafale_max` et `pluie_cumul` absentes).
   Le code lit toujours les caractères [42:54] : il lève une ValueError sur un payload de 40 caractères.
5. Les identifiants de bloc (caractères [0:2], [22:24], [40:42]) sont ignorés par le code, donc un caractère
   non hexadécimal à cet endroit n'est pas rejeté ; la spec demande une ValueError dès que le payload
   contient autre chose que de l'hexadécimal.
6. Le code ne vérifie pas la longueur minimale (40 caractères) : la ValueError des payloads trop courts
   n'arrive que par hasard, quand une tranche vide est convertie. Les tests ci-dessous passent, mais la règle
   n'est pas écrite dans le code.
"""

import pytest

from station.decodeur import decoder

# Payloads recopiés depuis SPEC-ML.md
PAYLOAD_REFERENCE = "01010A5B0001C86160000902007E00000000278C"  # 40 caractères
PAYLOAD_COMPLET = "01004958000009BE00000802000C00000000276B4C001900007B08"  # 54 caractères

# Même payload complet, avec FFF2 (-14, soit -1,4 °C) à la place de la température (caractères [2:6])
PAYLOAD_COMPLET_TEMPERATURE_NEGATIVE = "01FFF258000009BE00000802000C00000000276B4C001900007B08"

VALEURS_REFERENCE = {
    "temperature": 26.6,
    "humidite": 91,
    "luminosite": 116833,
    "indice_uv": 9.6,
    "vent_vitesse": 0.9,
    "vent_direction": 126,
    "precipitation": 0.0,
    "pression_atmospherique": 1012.4,
}

VALEURS_COMPLET = {
    "temperature": 7.3,
    "humidite": 88,
    "luminosite": 2494,
    "indice_uv": 0.0,
    "vent_vitesse": 0.8,
    "vent_direction": 12,
    "precipitation": 0.0,
    "pression_atmospherique": 1009.1,
    "rafale_max": 2.5,
    "pluie_cumul": 3149.6,
}


# --- Payload de référence (40 caractères) ---

@pytest.mark.parametrize("cle, attendu", list(VALEURS_REFERENCE.items()))
def test_payload_reference_valeur_decodee(cle, attendu):
    resultat = decoder(PAYLOAD_REFERENCE)
    assert resultat[cle] == pytest.approx(attendu)


@pytest.mark.parametrize("cle_absente", ["rafale_max", "pluie_cumul"])
def test_payload_reference_sans_rafale_ni_pluie_cumul(cle_absente):
    resultat = decoder(PAYLOAD_REFERENCE)
    assert cle_absente not in resultat


# --- Payload complet (54 caractères) ---

@pytest.mark.parametrize("cle, attendu", list(VALEURS_COMPLET.items()))
def test_payload_complet_valeur_decodee(cle, attendu):
    resultat = decoder(PAYLOAD_COMPLET)
    assert resultat[cle] == pytest.approx(attendu)


# --- Types ---

@pytest.mark.parametrize("payload", [PAYLOAD_REFERENCE, PAYLOAD_COMPLET])
@pytest.mark.parametrize("cle", ["humidite", "luminosite", "vent_direction"])
def test_valeur_entiere_est_un_int(payload, cle):
    resultat = decoder(payload)
    assert type(resultat[cle]) is int


# --- Température négative ---

def test_temperature_negative_fff2_vaut_moins_1_virgule_4():
    resultat = decoder(PAYLOAD_COMPLET_TEMPERATURE_NEGATIVE)
    assert resultat["temperature"] == pytest.approx(-1.4)


# --- Minuscules ---

def test_payload_en_minuscules_donne_les_memes_valeurs():
    resultat = decoder(PAYLOAD_COMPLET.lower())
    assert resultat == pytest.approx(VALEURS_COMPLET)


# --- Payloads invalides ---

@pytest.mark.parametrize(
    "payload_trop_court",
    [
        "",
        "01010A5B",
        PAYLOAD_REFERENCE[:39],  # un caractère de moins que le minimum
    ],
)
def test_payload_trop_court_leve_valueerror(payload_trop_court):
    with pytest.raises(ValueError):
        decoder(payload_trop_court)


@pytest.mark.parametrize(
    "payload_non_hexadecimal",
    [
        "Z" * 54,
        "G" * 40,
        # un seul mauvais caractère dans une mesure (caractère [10])
        PAYLOAD_COMPLET[:10] + "G" + PAYLOAD_COMPLET[11:],
        # mauvais caractères dans un identifiant de bloc (caractères [0:2])
        "ZZ" + PAYLOAD_COMPLET[2:],
    ],
)
def test_payload_non_hexadecimal_leve_valueerror(payload_non_hexadecimal):
    with pytest.raises(ValueError):
        decoder(payload_non_hexadecimal)
```

**Remarques**
- Les payloads et valeurs attendues viennent de `SPEC-ML.md`. Seul le payload de température négative est fabriqué : c'est le payload complet avec `FFF2` à la place de `0049`.
- Plusieurs tests échouent, car le code s'écarte de la spec. Les six écarts sont listés en tête du fichier.
- Les trois premiers concernent les mauvaises divisions : `humidite`, `vent_direction` et `pression_atmospherique`.
- Le quatrième est que le payload de 40 caractères lève une `ValueError`. Tous les tests sur le payload de référence échouent donc.
- Le cinquième est que les identifiants de bloc ne sont pas vérifiés. Le cas `"ZZ" + ...` échoue donc.
- Les tests de température négative, de payload trop court et de la plupart des non-hexadécimaux passent déjà.
