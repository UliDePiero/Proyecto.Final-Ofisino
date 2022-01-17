
def test_that_home_says_hello_world(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.headers['content-type'] == 'application/json'
    assert resp.json == {'Hello': 'World'}
