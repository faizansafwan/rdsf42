def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_compare_with_seeded_data(client, seeded_repo):
    resp = client.get("/api/wind/compare?start=2026-01-01&end=2026-01-01")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["stale"] is False
    assert len(body["data"]) == 2
    first = body["data"][0]
    assert first["forecast_mw"] == 4800.0
    assert first["error_mw"] == 200.0


def test_metrics(client, seeded_repo):
    resp = client.get("/api/wind/metrics?start=2026-01-01&end=2026-01-01")
    assert resp.status_code == 200
    metrics = resp.get_json()["metrics"]
    assert metrics["n_points"] == 2
    assert metrics["bias"] is not None


def test_invalid_date(client):
    resp = client.get("/api/wind/compare?start=2025-12-01&end=2026-01-01")
    assert resp.status_code == 400


def test_admin_refresh_unauthorized(client):
    resp = client.post("/api/admin/refresh")
    assert resp.status_code == 401
