from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import routes


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    application = FastAPI()
    application.include_router(routes.router)

    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture
def mock_session(monkeypatch):
    session = MagicMock()

    session.query.return_value.order_by.return_value.limit.return_value.all.return_value = []

    monkeypatch.setattr(routes, "SessionLocal", lambda: session)

    return session


def set_records(session, records):
    session.query.return_value.order_by.return_value.limit.return_value.all.return_value = records


def make_record(record_id, event_type):
    return SimpleNamespace(
        id=record_id,
        event_type=event_type,
        source_path=f"sandbox/file{record_id}.txt",
        destination_path=None,
        extension=".txt",
        previous_extension=None,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "RDRS API",
    }


def test_status(client):
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {
        "service": "RDRS",
        "api_status": "running",
        "monitoring": "configured",
        "watched_folder": "./data/sandbox",
        "simulation_mode": True,
    }


def test_alerts_when_log_is_missing(client):
    response = client.get("/alerts")

    assert response.status_code == 200
    assert response.json() == {
        "alerts": [],
        "message": "No alert log found.",
    }


def test_alerts_when_log_is_empty(client, tmp_path):
    log_path = tmp_path / "logs" / "alerts.log"
    log_path.parent.mkdir()
    log_path.write_text("", encoding="utf-8")

    response = client.get("/alerts")

    assert response.status_code == 200
    assert response.json() == {
        "alerts": [],
        "total": 0,
    }


def test_alerts_ignore_blank_lines(client, tmp_path):
    log_path = tmp_path / "logs" / "alerts.log"
    log_path.parent.mkdir()
    log_path.write_text(
        "  First alert  \n\n   \nSecond alert\n",
        encoding="utf-8",
    )

    response = client.get("/alerts")

    assert response.status_code == 200
    assert response.json() == {
        "alerts": ["First alert", "Second alert"],
        "total": 2,
    }


def test_events_when_database_is_empty(client, mock_session):
    response = client.get("/events")

    assert response.status_code == 200
    assert response.json() == {
        "events": [],
        "total": 0,
    }
    mock_session.close.assert_called_once()


def test_events_serialize_records(client, mock_session):
    record = make_record(1, "moved")
    record.destination_path = "sandbox/file1.locked"
    record.previous_extension = ".txt"
    record.extension = ".locked"

    set_records(mock_session, [record])

    response = client.get("/events")

    assert response.status_code == 200
    assert response.json() == {
        "events": [
            {
                "id": 1,
                "event_type": "moved",
                "source_path": "sandbox/file1.txt",
                "destination_path": "sandbox/file1.locked",
                "extension": ".locked",
                "previous_extension": ".txt",
                "timestamp": record.timestamp.isoformat(),
            }
        ],
        "total": 1,
    }

    query = mock_session.query.return_value.order_by.return_value
    query.limit.assert_called_once_with(50)
    mock_session.close.assert_called_once()


def test_reports_count_event_types(client, mock_session):
    records = [
        make_record(1, "created"),
        make_record(2, "modified"),
        make_record(3, "modified"),
        make_record(4, "deleted"),
        make_record(5, "moved"),
    ]

    set_records(mock_session, records)

    response = client.get("/reports")

    assert response.status_code == 200
    assert response.json() == {
        "report_period": "latest 50 events",
        "total_events": 5,
        "created_events": 1,
        "modified_events": 2,
        "deleted_events": 1,
        "moved_events": 1,
    }
    mock_session.close.assert_called_once()


def test_reports_when_database_is_empty(client, mock_session):
    response = client.get("/reports")

    assert response.status_code == 200
    assert response.json() == {
        "report_period": "latest 50 events",
        "total_events": 0,
        "created_events": 0,
        "modified_events": 0,
        "deleted_events": 0,
        "moved_events": 0,
    }
    mock_session.close.assert_called_once()


@pytest.mark.parametrize("endpoint", ["/events", "/reports"])
def test_database_session_closes_after_error(
    client,
    mock_session,
    endpoint,
):
    mock_session.query.side_effect = RuntimeError("Test database error")

    with pytest.raises(RuntimeError, match="Test database error"):
        client.get(endpoint)

    mock_session.close.assert_called_once()


def test_scan_returns_simulated_response(client, tmp_path):
    folder = tmp_path / "scan-target"
    folder.mkdir()

    source = folder / "original.txt"
    source.write_bytes(b"Original disposable test content.")

    response = client.post(
        "/scan",
        json={"folder_path": str(folder)},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "scan requested"
    assert result["folder_path"] == str(folder)
    assert result["simulation_mode"] is True
    assert source.read_bytes() == b"Original disposable test content."
    assert list(folder.iterdir()) == [source]


def test_valid_settings_do_not_write_config(client, tmp_path):
    response = client.post(
        "/settings",
        json={
            "simulation_mode": True,
            "window_seconds": 60,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "settings received"
    assert result["simulation_mode"] is True
    assert result["window_seconds"] == 60
    assert not (tmp_path / "config.yaml").exists()


@pytest.mark.parametrize("window_seconds", [0, -1])
def test_settings_reject_nonpositive_window(client, window_seconds):
    response = client.post(
        "/settings",
        json={
            "simulation_mode": True,
            "window_seconds": window_seconds,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "message": "window_seconds must be greater than zero.",
    }


@pytest.mark.parametrize("endpoint", ["/scan", "/settings"])
def test_missing_request_fields_are_rejected(client, endpoint):
    response = client.post(endpoint, json={})

    assert response.status_code == 422