import pytest
import yaml
from pydantic import ValidationError

from app.core.config import load_config
from app.core.entropy import file_entropy, shannon_entropy


def valid_config_data():
    return {
        "watched_folders": ["./data/sandbox"],
        "monitor": {
            "window_seconds": 60,
            "sample_bytes": 65536,
        },
        "thresholds": {
            "modified_files_per_minute": 20,
            "renames_per_minute": 10,
            "extension_changes_per_minute": 10,
            "average_entropy": 7.0,
        },
        "scoring": {
            "rapid_encryption": 40,
            "mass_rename": 30,
            "high_entropy": 25,
            "cpu_spike": 15,
            "unknown_program": 10,
        },
        "response": {
            "simulation_mode": True,
            "quarantine_folder": "./data/quarantine",
        },
    }


def test_load_valid_config(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(valid_config_data()),
        encoding="utf-8",
    )

    config = load_config(str(config_path))

    assert config.watched_folders == ["./data/sandbox"]
    assert config.monitor.window_seconds == 60
    assert config.monitor.sample_bytes == 65536

    assert config.thresholds.modified_files_per_minute == 20
    assert config.thresholds.renames_per_minute == 10
    assert config.thresholds.extension_changes_per_minute == 10
    assert config.thresholds.average_entropy == 7.0

    assert config.scoring.rapid_encryption == 40
    assert config.scoring.mass_rename == 30
    assert config.scoring.high_entropy == 25
    assert config.scoring.cpu_spike == 15
    assert config.scoring.unknown_program == 10

    assert config.response.simulation_mode is True
    assert config.response.quarantine_folder == "./data/quarantine"


def test_load_config_from_default_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(valid_config_data()),
        encoding="utf-8",
    )

    config = load_config()

    assert config.monitor.window_seconds == 60
    assert config.response.simulation_mode is True


def test_missing_config_file(tmp_path):
    missing_path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        load_config(str(missing_path))


def test_config_missing_required_section(tmp_path):
    data = valid_config_data()
    del data["monitor"]

    config_path = tmp_path / "incomplete.yaml"
    config_path.write_text(
        yaml.safe_dump(data),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(str(config_path))


def test_config_invalid_field_type(tmp_path):
    data = valid_config_data()
    data["monitor"]["window_seconds"] = "not-a-number"

    config_path = tmp_path / "invalid-type.yaml"
    config_path.write_text(
        yaml.safe_dump(data),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(str(config_path))


def test_config_malformed_yaml(tmp_path):
    config_path = tmp_path / "malformed.yaml"
    config_path.write_text(
        "watched_folders: [unfinished",
        encoding="utf-8",
    )

    with pytest.raises(yaml.YAMLError):
        load_config(str(config_path))


def test_empty_bytes_have_zero_entropy():
    assert shannon_entropy(b"") == 0.0


def test_repeated_byte_has_zero_entropy():
    assert shannon_entropy(b"A" * 1000) == 0.0


def test_two_equally_common_bytes_have_entropy_one():
    assert shannon_entropy(b"AB" * 500) == pytest.approx(1.0)


def test_all_byte_values_have_entropy_eight():
    data = bytes(range(256))

    assert shannon_entropy(data) == pytest.approx(8.0)


def test_file_entropy_matches_byte_entropy(tmp_path):
    data = b"RDRS safe entropy test."
    source = tmp_path / "sample.bin"
    source.write_bytes(data)

    assert file_entropy(source) == pytest.approx(
        shannon_entropy(data)
    )


def test_file_entropy_accepts_string_path(tmp_path):
    source = tmp_path / "string-path.bin"
    source.write_bytes(b"AB" * 100)

    assert file_entropy(str(source)) == pytest.approx(1.0)


def test_empty_file_has_zero_entropy(tmp_path):
    source = tmp_path / "empty.bin"
    source.write_bytes(b"")

    assert file_entropy(source) == 0.0


def test_file_entropy_uses_requested_sample_size(tmp_path):
    source = tmp_path / "sample-limit.bin"
    source.write_bytes(b"A" * 100 + bytes(range(256)))

    assert file_entropy(source, sample_size=100) == 0.0
    assert file_entropy(source) > 0.0


def test_file_entropy_default_sample_limit(tmp_path):
    source = tmp_path / "default-limit.bin"
    source.write_bytes(b"A" * 65536 + bytes(range(256)))

    assert file_entropy(source) == 0.0


def test_missing_entropy_file(tmp_path):
    missing_path = tmp_path / "missing.bin"

    with pytest.raises(FileNotFoundError):
        file_entropy(missing_path)