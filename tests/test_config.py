import json
from pathlib import Path

import pytest

from reviewer.config import ConfigError, load_config


def write_event(tmp_path: Path, payload: dict) -> str:
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(payload), encoding="utf-8")
    return str(event_file)


def test_load_config_reads_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_EVENT_PATH", write_event(tmp_path, {"pull_request": {"number": 42}}))

    config = load_config()

    assert config.github_token == "fake-token"
    assert config.repo == "owner/repo"
    assert config.pr_number == 42


def test_load_config_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")

    with pytest.raises(ConfigError, match="GITHUB_TOKEN"):
        load_config()


def test_load_config_not_a_pr_event(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_EVENT_PATH", write_event(tmp_path, {"push": {}}))

    with pytest.raises(ConfigError, match="pull_request"):
        load_config()
