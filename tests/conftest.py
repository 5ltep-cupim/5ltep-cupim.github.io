"""Shared helpers: the real registry, and a folder of workflow files built from it (each with a known
schedule, plus a tests.yml without one), which a test then changes."""

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import registry  # noqa: E402

REGISTRY = ROOT / "docs" / "registry.json"
NOW = "2026-10-13T06:40:00Z"
CRON = "30 3 * * 1"


@pytest.fixture
def reg():
    return copy.deepcopy(registry.load(REGISTRY))


def workflow_text(crons) -> str:
    lines = ["name: x", "on:", "  schedule:"] + [f"    - cron: '{c}'  # comment" for c in crons]
    return "\n".join(lines + ["  workflow_dispatch:", "jobs: {}", ""])


@pytest.fixture
def published(tmp_path, reg):
    """<tmp>/<repository>/.github/workflows/<file> for every listed workflow, plus tests.yml."""
    for w in registry.workflows(reg):
        folder = tmp_path / w.repository / ".github" / "workflows"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / w.file).write_text(workflow_text([CRON]), encoding="utf-8")
        (folder / "tests.yml").write_text("name: Tests\non:\n  push:\njobs: {}\n", encoding="utf-8")
    return tmp_path


def write_json(path: Path, data) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path
