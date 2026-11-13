from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import psutil
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.events import FileEvent
from app.database import database
from app.database import event_repository
from app.database import process_repository
from app.database.models import Base, FileEventRecord, ProcessSnapshot


@pytest.fixture
def isolated_database(tmp_path, monkeypatch):
    database_path = tmp_path / "test-rdrs.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        echo=False,
    )

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(engine)

    monkeypatch.setattr(
        event_repository,
        "SessionLocal",
        session_factory,
    )
    monkeypatch.setattr(
        process_repository,
        "SessionLocal",
        session_factory,
    )

    try:
        yield session_factory
    finally:
        engine.dispose()


def make_process():
    return SimpleNamespace(
        info={
            "name": "safe-test-process",
            "pid": 12345,
            "cpu_percent": 12.5,
            "memory_percent": 1.5,
        }
    )


def test_initialise_database_creates_folder_and_tables(
    tmp_path,
    monkeypatch,
):
    database_path = tmp_path / "nested" / "initialise-test.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        echo=False,
    )

    monkeypatch.setattr(database, "DATABASE_PATH", database_path)
    monkeypatch.setattr(database, "engine", engine)

    try:
        database.initialise_database()

        assert database_path.is_file()

        with engine.connect() as connection:
            rows = connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()

        table_names = {row[0] for row in rows}

        assert "file_events" in table_names
        assert "process_snapshots" in table_names
    finally:
        engine.dispose()


def test_save_file_event_persists_fields(isolated_database):
    timestamp = datetime.now(timezone.utc)

    event = FileEvent(
        event_type="moved",
        source_path="sandbox/example.txt",
        timestamp=timestamp,
        extension=".locked",
        destination_path="sandbox/example.locked",
        previous_extension=".txt",
    )

    event_repository.save_file_event(event)

    with isolated_database() as session:
        records = session.query(FileEventRecord).all()

        assert len(records) == 1

        record = records[0]

        assert record.id is not None
        assert record.event_type == "moved"
        assert record.source_path == "sandbox/example.txt"
        assert record.destination_path == "sandbox/example.locked"
        assert record.extension == ".locked"
        assert record.previous_extension == ".txt"

        assert record.timestamp.replace(tzinfo=None) == (
            timestamp.replace(tzinfo=None)
        )


def test_save_process_snapshot_persists_fields(isolated_database):
    process_repository.save_process_snapshot(make_process())

    with isolated_database() as session:
        records = session.query(ProcessSnapshot).all()

        assert len(records) == 1

        record = records[0]

        assert record.id is not None
        assert record.process_name == "safe-test-process"
        assert record.process_id == 12345
        assert record.cpu_percent == pytest.approx(12.5)
        assert record.memory_percent == pytest.approx(1.5)
        assert isinstance(record.timestamp, datetime)


def test_take_process_snapshot_saves_mocked_processes(
    isolated_database,
    monkeypatch,
):
    process_iter = Mock(
        return_value=[make_process(), make_process()]
    )

    monkeypatch.setattr(
        process_repository.psutil,
        "process_iter",
        process_iter,
    )

    saved_count = process_repository.take_process_snapshot()

    assert saved_count == 2

    process_iter.assert_called_once_with(
        ["pid", "name", "cpu_percent", "memory_percent"]
    )

    with isolated_database() as session:
        assert session.query(ProcessSnapshot).count() == 2


def test_take_process_snapshot_handles_empty_list(monkeypatch):
    monkeypatch.setattr(
        process_repository.psutil,
        "process_iter",
        lambda attributes: [],
    )

    save_snapshot = Mock()

    monkeypatch.setattr(
        process_repository,
        "save_process_snapshot",
        save_snapshot,
    )

    assert process_repository.take_process_snapshot() == 0
    save_snapshot.assert_not_called()


@pytest.mark.parametrize(
    "error_type",
    [psutil.NoSuchProcess, psutil.AccessDenied],
)
def test_take_process_snapshot_skips_unavailable_process(
    monkeypatch,
    error_type,
):
    first_process = make_process()
    second_process = make_process()

    monkeypatch.setattr(
        process_repository.psutil,
        "process_iter",
        lambda attributes: [first_process, second_process],
    )

    save_snapshot = Mock(
        side_effect=[error_type(12345), None]
    )

    monkeypatch.setattr(
        process_repository,
        "save_process_snapshot",
        save_snapshot,
    )

    assert process_repository.take_process_snapshot() == 1
    assert save_snapshot.call_count == 2