"""Reads the schedule (cron, UTC) of every workflow the registry lists, from the file each repository
publishes, so the site shows the schedule in force. It informs; it compares nothing.

Status of an item (one workflow of one repository):
  read                the workflow file was read (its crons may be empty: no schedule)
  missing_repository  the repository does not exist (or has no workflow folder)
  missing_workflow    the repository exists, the listed workflow file does not
  unlisted            a published workflow with a schedule that the registry does not list
  unreachable         could not read now (network, rate limit): a gap
"""

import re
from collections import OrderedDict

from src.fetch import NotFound, Unreachable
from src.registry import workflows

STATUSES = ["read", "missing_repository", "missing_workflow", "unlisted", "unreachable"]
CRON_LINE = re.compile(r"""^\s*-\s*cron:\s*(['"])(.+?)\1""", re.M)


def published_crons(text: str) -> list[str]:
    return [" ".join(m.group(2).split()) for m in CRON_LINE.finditer(text)]


def run(registry: dict, source, now: str) -> dict:
    by_repo: "OrderedDict[str, list]" = OrderedDict()
    for w in workflows(registry):
        by_repo.setdefault(w.full_name, []).append(w)

    items = []
    for full_name, listed in by_repo.items():
        owner, repo = full_name.split("/", 1)
        base = {"repository": full_name, "kind": listed[0].kind, "layer": listed[0].layer, "portal": listed[0].portal}
        try:
            published, error = source.workflows(owner, repo), None
        except NotFound:
            published, error = None, "missing_repository"
        except Unreachable as exc:
            published, error = None, "unreachable"
            base = {**base, "reason": str(exc)[:300]}
        for w in listed:
            item = {**base, "file": w.file, "cron": None}
            if error:
                item["status"] = error
            elif w.file not in published:
                item["status"] = "missing_workflow"
            else:
                item["status"], item["cron"] = "read", published_crons(published[w.file])
            items.append(item)
        if published:
            known = {w.file for w in listed}
            for name, text in published.items():
                crons = published_crons(text)
                if name not in known and crons:
                    items.append({**base, "file": name, "cron": crons, "status": "unlisted"})

    totals = {s: sum(1 for i in items if i["status"] == s) for s in STATUSES}
    return {"generated_at": now, "owner": registry["owner"], "totals": totals, "items": items}
