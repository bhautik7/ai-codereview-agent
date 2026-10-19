from unittest.mock import MagicMock, patch

import pytest

from reviewer.github_client import PER_PAGE, GitHubClient, GitHubError


def make_response(items: list[dict] | None = None, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.ok = status_code < 400
    response.status_code = status_code
    response.json.return_value = items or []
    response.text = "Bad credentials" if status_code >= 400 else ""
    return response


def test_client_sets_auth_header() -> None:
    client = GitHubClient("fake-token", "owner/repo")

    assert client.session.headers["Authorization"] == "Bearer fake-token"


def test_get_pr_files_follows_pagination() -> None:
    client = GitHubClient("fake-token", "owner/repo")
    first_page = [{"filename": f"file_{i}.py"} for i in range(PER_PAGE)]
    second_page = [{"filename": "last.py"}]

    with patch.object(client.session, "get") as mock_get:
        mock_get.side_effect = [make_response(first_page), make_response(second_page)]
        files = client.get_pr_files(7)

    assert len(files) == PER_PAGE + 1
    assert files[-1]["filename"] == "last.py"
    assert mock_get.call_count == 2
    assert mock_get.call_args_list[0].args[0] == "https://api.github.com/repos/owner/repo/pulls/7/files"


def test_get_pr_files_raises_clear_error_on_401() -> None:
    client = GitHubClient("bad-token", "owner/repo")

    with patch.object(client.session, "get", return_value=make_response(status_code=401)):
        with pytest.raises(GitHubError, match="401"):
            client.get_pr_files(7)
