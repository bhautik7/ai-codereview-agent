"""Entry point: runs the review pipeline for one pull request."""

import logging
import sys

from reviewer.config import ConfigError, load_config
from reviewer.github_client import GitHubClient, GitHubError

logger = logging.getLogger("reviewer")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        config = load_config()
        client = GitHubClient(config.github_token, config.repo)
        files = client.get_pr_files(config.pr_number)
    except (ConfigError, GitHubError) as exc:
        logger.error("%s", exc)
        return 1

    print(f"PR #{config.pr_number} in {config.repo} changed {len(files)} file(s):")
    for file in files:
        print(f"  [{file['status']}] {file['filename']} (+{file['additions']} / -{file['deletions']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
