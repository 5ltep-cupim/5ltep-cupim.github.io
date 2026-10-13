"""CUPIM schedules: reads the cron of every workflow listed in docs/registry.json from the file each
repository publishes.

  python main.py --out build                     # reads GitHub (GITHUB_TOKEN only raises the rate limit)
  python main.py --out build --offline <folder>  # reads <folder>/<repository>/.github/workflows

Writes <out>/docs/data/schedules.json, shown by the site.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from src import registry, schedules
from src.fetch import FolderSource, GitHubSource

ROOT = Path(__file__).resolve().parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", type=Path, default=ROOT / "docs" / "registry.json")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--offline", type=Path, help="read workflows from this folder instead of GitHub")
    ap.add_argument("--now", help="ISO time of the run (tests)")
    args = ap.parse_args(argv)

    data = registry.load(args.registry)
    source = FolderSource(args.offline) if args.offline else GitHubSource(os.environ.get("GITHUB_TOKEN"))
    now = args.now or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    report = schedules.run(data, source, now)
    report["registry_sha256"] = hashlib.sha256(args.registry.read_bytes()).hexdigest()
    report["commit"] = os.environ.get("GITHUB_SHA")
    if os.environ.get("GITHUB_RUN_ID"):
        report["run_url"] = (f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
                             f"{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{os.environ['GITHUB_RUN_ID']}")

    out = args.out / "docs" / "data"
    out.mkdir(parents=True, exist_ok=True)
    (out / "schedules.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    t = report["totals"]
    print(f"{len(report['items'])} workflows: " + ", ".join(f"{k} {v}" for k, v in t.items() if v))
    for item in report["items"]:
        print(f"  {item['status']:<18} {item['repository']} {item['file']} {item['cron']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
