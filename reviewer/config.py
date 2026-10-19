"""Reads all settings for the reviewer from environment variables."""

import json
import os
from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when a required setting is missing or invalid."""


@dataclass(frozen=True)
class Config:
    github_token: str
    repo: str
    pr_number: int


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def _read_pr_number(event_path: str) -> int:
    """Read the PR number from the GitHub event payload file."""
    try:
        with open(event_path, encoding="utf-8") as f:
            event = json.load(f)
        return int(event["pull_request"]["number"])
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Could not read GitHub event file {event_path}: {exc}") from exc
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigError("GitHub event has no pull_request number. Is this a pull_request event?") from exc


def load_config() -> Config:
    """Build the Config from env vars. Raises ConfigError with a clear message."""
    return Config(
        github_token=_require_env("GITHUB_TOKEN"),
        repo=_require_env("GITHUB_REPOSITORY"),
        pr_number=_read_pr_number(_require_env("GITHUB_EVENT_PATH")),
    )
