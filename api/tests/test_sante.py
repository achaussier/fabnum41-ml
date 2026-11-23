"""Un premier test de l'API, pour vérifier que l'installation fonctionne."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_la_route_sante_repond():
    reponse = client.get("/sante")

    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "ok"
