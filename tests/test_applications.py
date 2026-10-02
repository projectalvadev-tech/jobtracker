def make(client, **overrides):
    payload = {"company": "Acme", "position": "DevOps Jr", "stack": ["Docker", "Jenkins"]}
    payload.update(overrides)
    return client.post("/applications", json=payload)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_get(client):
    r = make(client)
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "applied"
    assert data["stack"] == ["docker", "jenkins"]  # normalizado

    r = client.get(f"/applications/{data['id']}")
    assert r.status_code == 200
    assert r.json()["company"] == "Acme"


def test_stack_is_deduplicated(client):
    r = make(client, stack=["Docker", " docker ", "AWS", ""])
    assert r.json()["stack"] == ["docker", "aws"]


def test_validation_error(client):
    r = client.post("/applications", json={"company": "", "position": "x"})
    assert r.status_code == 422


def test_not_found(client):
    assert client.get("/applications/999").status_code == 404


def test_update(client):
    app_id = make(client).json()["id"]
    r = client.patch(f"/applications/{app_id}", json={"status": "interview"})
    assert r.status_code == 200
    assert r.json()["status"] == "interview"
    assert r.json()["company"] == "Acme"  # lo demás no cambia


def test_filter_by_status(client):
    make(client, company="A")
    id_b = make(client, company="B").json()["id"]
    client.patch(f"/applications/{id_b}", json={"status": "offer"})

    r = client.get("/applications", params={"status": "offer"})
    assert [a["company"] for a in r.json()] == ["B"]


def test_delete(client):
    app_id = make(client).json()["id"]
    assert client.delete(f"/applications/{app_id}").status_code == 204
    assert client.get(f"/applications/{app_id}").status_code == 404


def test_stats(client):
    make(client, stack=["docker", "jenkins"])
    make(client, company="B", stack=["docker", "terraform"])
    r = client.get("/applications/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert data["by_status"] == {"applied": 2}
    assert data["top_technologies"][0] == {"name": "docker", "count": 2}
