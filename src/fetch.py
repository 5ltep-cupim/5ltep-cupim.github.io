"""Reading the workflow files of a repository: from GitHub over HTTPS (public repositories, the
token only raises the rate limit) or from a local folder (tests and offline trials)."""

import json
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
MAX_BYTES = 512 * 1024


class NotFound(Exception):
    """The repository (or its workflow folder) does not exist."""


class Unreachable(Exception):
    """Could not read now (network, rate limit, server): a gap, never a difference."""


class GitHubSource:
    def __init__(self, token: str | None = None, timeout: int = 30):
        self.token = token
        self.timeout = timeout

    def _get(self, url: str, accept: str) -> bytes:
        headers = {"Accept": accept, "User-Agent": "5ltep-cupim-check", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token and url.startswith(API):
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=self.timeout) as res:
                body = res.read(MAX_BYTES + 1)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise NotFound(url) from exc
            raise Unreachable(f"HTTP {exc.code}: {url}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise Unreachable(f"{exc}: {url}") from exc
        if len(body) > MAX_BYTES:
            raise Unreachable(f"too large: {url}")
        return body

    def workflows(self, owner: str, repo: str) -> dict[str, str]:
        listing = json.loads(self._get(f"{API}/repos/{owner}/{repo}/contents/.github/workflows",
                                       "application/vnd.github+json"))
        if not isinstance(listing, list):
            raise Unreachable(f"unexpected listing for {owner}/{repo}")
        out = {}
        for item in listing:
            name = item.get("name", "")
            if item.get("type") == "file" and name.endswith((".yml", ".yaml")):
                out[name] = self._get(item["download_url"], "text/plain").decode("utf-8", "replace")
        return out


class FolderSource:
    """<root>/<repository>/.github/workflows/*.yml; the owner is ignored."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def workflows(self, owner: str, repo: str) -> dict[str, str]:
        folder = self.root / repo / ".github" / "workflows"
        if not folder.is_dir():
            raise NotFound(str(folder))
        return {p.name: p.read_text(encoding="utf-8") for p in sorted(folder.glob("*.y*ml"))}
