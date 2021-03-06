from ingestion_edge.dockerflow import init_app
from sanic.request import Request
import pytest
import json


@pytest.fixture(autouse=True)
def init(app, mocker):
    mocker.patch("ingestion_edge.dockerflow.check_disk_bytes_free", lambda app, q: [])
    mocker.patch("ingestion_edge.dockerflow.check_queue_size", lambda q: [])
    init_app(app, {})


async def test_heartbeat(app):
    responses = []
    request = Request(b"/__heartbeat__", {}, "1.1", "GET", "http", app)
    await app.handle_request(request, lambda r: responses.append(r), None)
    assert len(responses) == 1
    response = responses.pop()
    assert response.status == 200
    assert json.loads(response.body.decode()) == {
        "status": "ok",
        "checks": {"check_disk_bytes_free": "ok", "check_queue_size": "ok"},
        "details": {},
    }


async def test_lbheartbeat(app):
    responses = []
    request = Request(b"/__lbheartbeat__", {}, "1.1", "GET", "http", app)
    await app.handle_request(request, lambda r: responses.append(r), None)
    assert len(responses) == 1
    response = responses.pop()
    assert response.status == 200
    assert response.body == b""


async def test_version(app):
    responses = []
    request = Request(b"/__version__", {}, "1.1", "GET", "http", app)
    await app.handle_request(request, lambda r: responses.append(r), None)
    assert len(responses) == 1
    response = responses.pop()
    assert response.status == 200
    assert set(json.loads(response.body.decode()).keys()) == {
        "build",
        "commit",
        "source",
        "version",
    }
