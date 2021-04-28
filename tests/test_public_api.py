from src.public_api import create_app
import pytest

@pytest.fixture
def client():
    app = create_app()

    with app.test_client() as client:
        yield client

def test_basic_sanity(client):
    assert client is not None

def test_basic_query(client):

    return

    import json

    # Should return the most recent domains from DB
    response = client.get("/api/domains")

    data = json.loads(response.data)

    assert len(data["results"]) == 500
    assert data["pages"] == 7000
    

def test_keyword_query(client):

    import json

    # Should return the most recent domains from DB
    response = client.get("/api/domains?term=tacos")

    data = json.loads(response.data)

    assert len(data["results"]) == 500
    assert data["pages"] == 7000

    pass

def test_database_connection(client):
    pass

def test_user_authentication_query():
    pass

def test_unauthenticated_user_query(): 
    pass

