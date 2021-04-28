from src.public_api import create_app
import pytest

@pytest.fixture
def client():
    app = create_app()

    with app.test_client() as client:
        yield client

def test_sanity(client):
    assert client is not None

def test_sanity_basic_query(client):

    return

    import json

    # Should return the most recent domains from DB
    response = client.get("/api/domains")

    data = json.loads(response.data)

    assert data["results"][0]["name"] == "boston"

    assert data["pages"] == 7000
    

def test_sanity_keyword_query(client):

    import json

    # Should return the most recent domains from DB
    response = client.get("/api/domains?term=tacos")

    data = json.loads(response.data)

    assert data["results"][0]["name"] == "tacojohns"

    pass

def test_database_connection(client):
    pass

def test_user_authentication_query():
    pass

def test_unauthenticated_user_query(): 
    pass

