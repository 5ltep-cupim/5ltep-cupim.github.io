"""The reading of the published schedules: each status, and the accept step."""

import json
import shutil

import pytest

from conftest import CRON, NOW, ROOT, workflow_text, write_json
from src import accept, schedules
from src.fetch import FolderSource, NotFound, Unreachable

import main


def by_key(report):
    return {(i["repository"].split("/")[1], i["file"]): i for i in report["items"]}


def test_every_listed_workflow_is_read(reg, published):
    report = schedules.run(reg, FolderSource(published), NOW)
    assert report["totals"]["read"] == len(report["items"])
    assert all(i["cron"] == [CRON] for i in report["items"])


def test_published_crons_reads_quotes_spacing_and_comments():
    text = "on:\n  schedule:\n    - cron: '0 6 5 * *'   # monthly\n    - cron: \"10  */6 * * *\"\n"
    assert schedules.published_crons(text) == ["0 6 5 * *", "10 */6 * * *"]


def test_the_site_shows_the_schedule_in_force(reg, published):
    (published / "5ltep-layer2-recife/.github/workflows/layer2.yml").write_text(workflow_text(["0 9 * * 3", "0 9 * * 6"]))
    items = by_key(schedules.run(reg, FolderSource(published), NOW))
    assert items[("5ltep-layer2-recife", "layer2.yml")]["cron"] == ["0 9 * * 3", "0 9 * * 6"]
    assert items[("5ltep-layer2", "layer2.yml")]["cron"] == [CRON]


def test_a_workflow_without_schedule_is_read_with_no_cron(reg, published):
    (published / "5ltep-layer4/.github/workflows/compress.yml").write_text("on:\n  workflow_dispatch:\n")
    item = by_key(schedules.run(reg, FolderSource(published), NOW))[("5ltep-layer4", "compress.yml")]
    assert item["status"] == "read" and item["cron"] == []


def test_missing_workflow_and_missing_repository(reg, published):
    (published / "5ltep-layer3/.github/workflows/model-check.yml").unlink()
    shutil.rmtree(published / "5ltep-layer5-recife")
    items = by_key(schedules.run(reg, FolderSource(published), NOW))
    assert items[("5ltep-layer3", "model-check.yml")]["status"] == "missing_workflow"
    assert items[("5ltep-layer5-recife", "layer5.yml")]["status"] == "missing_repository"


def test_a_scheduled_workflow_not_in_the_registry_is_shown(reg, published):
    (published / "5ltep-layer1/.github/workflows/extra.yml").write_text(workflow_text(["0 1 * * *"]))
    items = by_key(schedules.run(reg, FolderSource(published), NOW))
    assert items[("5ltep-layer1", "extra.yml")]["status"] == "unlisted"
    assert ("5ltep-layer1", "tests.yml") not in items          # no schedule: not shown


def test_unreachable_is_a_gap(reg, published):
    class Flaky(FolderSource):
        def workflows(self, owner, repo):
            if repo == "5ltep-layer3-aneel":
                raise Unreachable("HTTP 503")
            return super().workflows(owner, repo)

    item = by_key(schedules.run(reg, Flaky(published), NOW))[("5ltep-layer3-aneel", "layer3.yml")]
    assert item["status"] == "unreachable" and item["cron"] is None


def test_folder_source_without_repository():
    with pytest.raises(NotFound):
        FolderSource(ROOT / "nowhere").workflows("x", "y")


def test_main_writes_only_what_accept_takes(published, tmp_path):
    out = tmp_path / "build"
    assert main.main(["--out", str(out), "--offline", str(published), "--now", NOW]) == 0
    report = json.loads((out / "docs/data/schedules.json").read_text(encoding="utf-8"))
    assert report["generated_at"] == NOW and len(report["registry_sha256"]) == 64
    assert accept.accept(out, tmp_path / "repo") == sorted(accept.EXPECTED)


def test_accept_refuses_anything_else(tmp_path):
    build = tmp_path / "build" / "docs" / "data"
    build.mkdir(parents=True)
    write_json(build / "schedules.json", {})
    (build / "index.html").write_text("<script>")
    with pytest.raises(SystemExit):
        accept.accept(tmp_path / "build", tmp_path / "repo")
    (build / "index.html").unlink()
    (build / "schedules.json").write_text("[1]")
    with pytest.raises(SystemExit):
        accept.accept(tmp_path / "build", tmp_path / "repo")
