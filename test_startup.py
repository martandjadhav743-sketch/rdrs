from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.main import app, create_report
from app.database.models import FileEventRecord, ProcessSnapshot


@pytest.fixture
def client():
    return TestClient(app)


def mocked_session(records):
    query = Mock()
    query.order_by.return_value.limit.return_value.all.return_value = records

    session = Mock()
    session.query.return_value = query
    session.close.return_value = None

    session_factory = Mock(return_value=session)

    return session, session_factory


def test_root_returns_welcome(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "RDRS API is running",
        "docs": "/docs",
    }


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "RDRS API",
    }


def test_report_generation_creates_markdown_file(
    tmp_path,
    monkeypatch,
):
    output_path = tmp_path / "reports" / "rdrs-report.md"

    monkeypatch.setattr(
        "app.main.REPORT_PATH",
        output_path,
    )

    session, session_factory = mocked_session([])

    monkeypatch.setattr(
        "app.main.SessionLocal",
        session_factory,
    )

    create_report()

    assert output_path.is_file()

    content = output_path.read_text(encoding="utf-8")

    assert content.startswith("# RDRS Activity Report")
    assert "## Summary" in content
    assert "## Recent File Events" in content
    assert "## Recent Process Snapshots" in content
    assert "## Latest Alerts" in content


def test_report_generation_uses_database_records(
    tmp_path,
    monkeypatch,
):
    output_path = tmp_path / "report.md"

    monkeypatch.setattr(
        "app.main.REPORT_PATH",
        output_path,
    )

    event_record = FileEventRecord(
        event_type="modified",
        source_path="sandbox/example.txt",
        timestamp=None,
    )

    process_record = ProcessSnapshot(
        process_name="safe-process",
        process_id=12345,
        cpu_percent=12.5,
        memory_percent=1.5,
        timestamp=None,
    )

    session = Mock()
    session.query.side_effect = [
        Mock(
            order_by=Mock(
                return_value=Mock(
                    limit=Mock(
                        return_value=Mock(
                            all=Mock(
                                return_value=[event_record]
                            )
                        )
                    )
                )
            )
        ),
        Mock(
            order_by=Mock(
                return_value=Mock(
                    limit=Mock(
                        return_value=Mock(
                            all=Mock(
                                return_value=[process_record]
                            )
                        )
                    )
                )
            )
        ),
        Mock(
            order_by=Mock(
                return_value=Mock(
                    limit=Mock(
                        return_value=Mock(
                            all=Mock(
                                return_value=[]
                            )
                        )
                    )
                )
            )
        ),
    ]
    session.close.return_value = None

    session_factory = Mock(return_value=session)

    monkeypatch.setattr(
        "app.main.SessionLocal",
        session_factory,
    )

    create_report()

    content = output_path.read_text(encoding="utf-8")

    assert "Total file events: 1" in content
    assert "Total process snapshots: 1" in content
    assert "sandbox/example.txt" in content
    assert "safe-process" in content


def test_report_generation_handles_empty_database(
    tmp_path,
    monkeypatch,
):
    output_path = tmp_path / "empty-report.md"

    monkeypatch.setattr(
        "app.main.REPORT_PATH",
        output_path,
    )

    session, session_factory = mocked_session([])

    monkeypatch.setattr(
        "app.main.SessionLocal",
        session_factory,
    )

    create_report()

    content = output_path.read_text(encoding="utf-8")

    assert "Total file events: 0" in content
    assert "Total process snapshots: 0" in content
    assert "No file events recorded." in content
    assert "No process snapshots recorded." in content


def test_report_generation_creates_parent_folder(
    tmp_path,
    monkeypatch,
):
    output_path = tmp_path / "new-folder" / "nested-report.md"

    monkeypatch.setattr(
        "app.main.REPORT_PATH",
        output_path,
    )

    session, session_factory = mocked_session([])

    monkeypatch.setattr(
        "app.main.SessionLocal",
        session_factory,
    )

    create_report()

    assert output_path.is_file()


def test_generate_report_route_returns_success(
    client,
    tmp_path,
    monkeypatch,
):
    output_path = tmp_path / "route-report.md"

    monkeypatch.setattr(
        "app.main.REPORT_PATH",
        output_path,
    )

    session, session_factory = mocked_session([])

    monkeypatch.setattr(
        "app.main.SessionLocal",
        session_factory,
    )

    response = client.post("/generate-report")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Report generated successfully",
        "report_path": str(output_path),
    }
    assert output_path.is_file()


def test_generate_report_route_returns_error(
    client,
    monkeypatch,
):
    session_factory = Mock(
        side_effect=OSError("database unavailable"),
    )

    monkeypatch.setattr(
        "app.main.SessionLocal",
        session_factory,
    )

    response = client.post("/generate-report")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Report generation failed"
    }


def test_startup_event_runs_without_monitoring(
    monkeypatch,
):
    load_config = Mock()
    initialise_database = Mock()
    take_process_snapshot = Mock(
        return_value=0
    )
    start_monitoring = Mock()

    monkeypatch.setattr(
        "app.main.load_config",
        load_config,
    )
    monkeypatch.setattr(
        "app.main.initialise_database",
        initialise_database,
    )
    monkeypatch.setattr(
        "app.main.take_process_snapshot",
        take_process_snapshot,
    )
    monkeypatch.setattr(
        "app.main.start_monitoring",
        start_monitoring,
    )

    startup_handlers = app.router.on_startup

    assert len(startup_handlers) == 1

    startup_handlers[0]()

    load_config.assert_called_once_with()
    initialise_database.assert_called_once_with()
    take_process_snapshot.assert_called_once_with()
    start_monitoring.assert_called_once_with(
        load_config.return_value.watched_folders
    )


def test_shutdown_event_closes_database_engine(monkeypatch):
    dispose = Mock()

    monkeypatch.setattr(
        "app.main.engine",
        Mock(dispose=dispose),
    )

    shutdown_handlers = app.router.on_shutdown

    assert len(shutdown_handlers) == 1

    shutdown_handlers[0]()

    dispose.assert_called_once_with()


def test_file_event_record_timestamp_defaults_to_none():
    record = FileEventRecord(
        event_type="created",
        source_path="sandbox/example.txt",
        timestamp=None,
    )

    assert record.timestamp is None


def test_process_snapshot_timestamp_defaults_to_none():
    record = ProcessSnapshot(
        process_name="safe-process",
        process_id=12345,
        cpu_percent=0.0,
        memory_percent=0.0,
        timestamp=None,
    )

    assert record.timestamp is None


def test_file_event_record_can_be_created():
    record = FileEventRecord(
        event_type="modified",
        source_path="sandbox/example.txt",
        timestamp=None,
    )

    assert record.event_type == "modified"


def test_process_snapshot_can_be_created():
    record = ProcessSnapshot(
        process_name="safe-process",
        process_id=12345,
        cpu_percent=10.0,
        memory_percent=2.0,
        timestamp=None,
    )

    assert record.process_name == "safe-process"