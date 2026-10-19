# Progress

## Step 1 — Workflow trigger + print changed files ✅
- Added `.github/workflows/ai-review.yml` (runs on `pull_request`: opened, synchronize, reopened; read-only permissions).
- Added `reviewer/github_client.py` with `get_pr_files()` (GitHub REST, handles pagination).
- Added `reviewer/main.py` that reads the PR number from `GITHUB_EVENT_PATH` and prints changed files.
- Added `tests/test_github_client.py` (requests mocked).

**How to test**
- Locally: `pip install -r requirements.txt && python -m pytest -q`
- On GitHub: push this folder to a repo, open a PR, and check the "Print changed files" step in the Actions log.

## Step 2 — config.py + github_client.py cleanup with tests ✅
- Added `reviewer/config.py`: `Config` dataclass + `load_config()` reads `GITHUB_TOKEN`, `GITHUB_REPOSITORY`, `GITHUB_EVENT_PATH`; raises `ConfigError` with a clear message.
- `reviewer/github_client.py` is now a `GitHubClient` class with one `requests.Session`; failures raise `GitHubError` (status code + URL).
- `reviewer/main.py` uses both and exits with code 1 and a clear log line on errors.
- Tests: `tests/test_config.py` (3 tests), `tests/test_github_client.py` (3 tests).

**How to test**
- `python -m pytest -q` → `6 passed`
- `python -m reviewer.main` with no env vars → `ERROR Missing required environment variable: GITHUB_TOKEN`, exit code 1.
