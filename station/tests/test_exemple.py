"""Un premier test, pour vérifier que l'installation fonctionne."""

from station.decodeur import decoder

# Payload complet (54 caractères) : trois blocs.
PAYLOAD_COMPLET = "01004958000009BE00000802000C00000000276B4C001900007B08"


def test_la_temperature_et_la_luminosite_sont_decodees():
    mesures = decoder(PAYLOAD_COMPLET)

    assert mesures["temperature"] == 7.3
    assert mesures["luminosite"] == 2494
