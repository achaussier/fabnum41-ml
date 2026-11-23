"""Tests de decoder(), écrits d'après la section « Décodage » de SPEC-ML.md.

Écarts constatés entre le décodeur fourni au départ (branche main) et la spec :
  1. l'humidité était divisée par 10 (9.1 au lieu de 91) ;
  2. la direction du vent était divisée par 10 (12.6 au lieu de 126) ;
  3. la pression n'était pas divisée par 10 (10124 au lieu de 1012.4 hPa) ;
  4. un payload de 40 caractères, pourtant valide, provoquait une ValueError.
Ces tests échouent sur main et passent sur la branche solutions.
"""

import pytest

from station.decodeur import decoder

# Payload de référence (40 caractères, deux blocs), décodé par le codec officiel.
PAYLOAD_REFERENCE = "01010A5B0001C86160000902007E00000000278C"

# Payload complet (54 caractères, trois blocs).
PAYLOAD_COMPLET = "01004958000009BE00000802000C00000000276B4C001900007B08"


@pytest.mark.parametrize("cle, attendu", [
    ("temperature", 26.6),
    ("humidite", 91),
    ("luminosite", 116833),
    ("indice_uv", 9.6),
    ("vent_vitesse", 0.9),
    ("vent_direction", 126),
    ("precipitation", 0.0),
    ("pression_atmospherique", 1012.4),
])
def test_le_payload_de_reference_est_decode(cle, attendu):
    assert decoder(PAYLOAD_REFERENCE)[cle] == pytest.approx(attendu)


def test_un_payload_de_40_caracteres_n_a_ni_rafale_ni_cumul():
    mesures = decoder(PAYLOAD_REFERENCE)

    assert "rafale_max" not in mesures
    assert "pluie_cumul" not in mesures
    assert len(mesures) == 8


@pytest.mark.parametrize("cle, attendu", [
    ("temperature", 7.3),
    ("humidite", 88),
    ("luminosite", 2494),
    ("indice_uv", 0.0),
    ("vent_vitesse", 0.8),
    ("vent_direction", 12),
    ("precipitation", 0.0),
    ("pression_atmospherique", 1009.1),
    ("rafale_max", 2.5),
    ("pluie_cumul", 3149.6),
])
def test_le_payload_complet_est_decode(cle, attendu):
    assert decoder(PAYLOAD_COMPLET)[cle] == pytest.approx(attendu)


@pytest.mark.parametrize("cle", ["humidite", "luminosite", "vent_direction"])
def test_humidite_luminosite_et_direction_sont_des_entiers(cle):
    assert isinstance(decoder(PAYLOAD_COMPLET)[cle], int)


def test_une_temperature_negative_est_decodee():
    # FFF2 vaut -14, soit -1,4 °C.
    payload = "01FFF2" + PAYLOAD_COMPLET[6:]

    assert decoder(payload)["temperature"] == pytest.approx(-1.4)


def test_les_minuscules_sont_acceptees():
    assert decoder(PAYLOAD_COMPLET.lower()) == decoder(PAYLOAD_COMPLET)


def test_un_payload_trop_court_est_refuse():
    with pytest.raises(ValueError):
        decoder(PAYLOAD_REFERENCE[:30])


def test_un_payload_qui_n_est_pas_de_l_hexadecimal_est_refuse():
    with pytest.raises(ValueError):
        decoder("Z" * 54)
