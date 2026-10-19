"""Small wrapper around the GitHub REST API."""

import requests

GITHUB_API_URL = "https://api.github.com"
PER_PAGE = 100
TIMEOUT_SECONDS = 30


class GitHubError(Exception):
    """Raised when a GitHub API call fails."""


class GitHubClient:
    def __init__(self, token: str, repo: str) -> None:
        self.repo = repo
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def _get(self, url: str, params: dict | None = None) -> list | dict:
        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            raise GitHubError(f"GitHub request failed: GET {url}: {exc}") from exc
        if not response.ok:
            raise GitHubError(
                f"GitHub API error {response.status_code} for GET {url}: {response.text[:200]}"
            )
        return response.json()

    def get_pr_files(self, pr_number: int) -> list[dict]:
        """Return all changed files of a pull request, following pagination."""
        url = f"{GITHUB_API_URL}/repos/{self.repo}/pulls/{pr_number}/files"
        files: list[dict] = []
        page = 1
        while True:
            batch = self._get(url, params={"per_page": PER_PAGE, "page": page})
            files.extend(batch)
            if len(batch) < PER_PAGE:
                return files
            page += 1
