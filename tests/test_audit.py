"""Tests for envault.audit module."""

import json
from pathlib import Path

import pytest

from envault.audit import clear_log, read_events, record_event


@pytest.fixture()
def log_file(tmp_path: Path) -> Path:
    return tmp_path / "audit.log"


class TestRecordEvent:
    def test_returns_event_dict(self, log_file):
        event = record_event("set", key="DB_URL", vault="prod", log_path=log_file)
        assert event["action"] == "set"
        assert event["key"] == "DB_URL"
        assert event["vault"] == "prod"
        assert event["success"] is True

    def test_event_written_to_file(self, log_file):
        record_event("get", key="API_KEY", log_path=log_file)
        lines = log_file.read_text().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["action"] == "get"

    def test_multiple_events_appended(self, log_file):
        record_event("set", key="A", log_path=log_file)
        record_event("delete", key="B", log_path=log_file)
        record_event("get", key="C", log_path=log_file)
        lines = log_file.read_text().splitlines()
        assert len(lines) == 3

    def test_failed_event_recorded(self, log_file):
        event = record_event("get", key="MISSING", success=False, log_path=log_file)
        assert event["success"] is False
        data = json.loads(log_file.read_text().splitlines()[0])
        assert data["success"] is False

    def test_timestamp_present_and_utc(self, log_file):
        event = record_event("set", key="X", log_path=log_file)
        assert event["timestamp"].endswith("+00:00")


class TestReadEvents:
    def test_empty_log_returns_empty_list(self, log_file):
        assert read_events(log_path=log_file) == []

    def test_missing_log_returns_empty_list(self, tmp_path):
        assert read_events(log_path=tmp_path / "nonexistent.log") == []

    def test_read_returns_events_in_order(self, log_file):
        for key in ("A", "B", "C"):
            record_event("set", key=key, log_path=log_file)
        events = read_events(log_path=log_file)
        assert [e["key"] for e in events] == ["A", "B", "C"]

    def test_limit_is_respected(self, log_file):
        for i in range(10):
            record_event("set", key=str(i), log_path=log_file)
        events = read_events(log_path=log_file, limit=3)
        assert len(events) == 3
        assert events[-1]["key"] == "9"


class TestClearLog:
    def test_clear_empties_file(self, log_file):
        record_event("set", key="X", log_path=log_file)
        clear_log(log_path=log_file)
        assert log_file.read_text() == ""

    def test_clear_on_missing_file_is_noop(self, tmp_path):
        clear_log(log_path=tmp_path / "ghost.log")  # should not raise
