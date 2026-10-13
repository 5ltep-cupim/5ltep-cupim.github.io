"""README and LEIAME walk together and agree with the registry; texts keep the humility premise;
workflows keep the security rules; the site names every gap the reading can produce."""

import re

import pytest

from conftest import ROOT
from src import registry, schedules

README = (ROOT / "README.md").read_text(encoding="utf-8")
LEIAME = (ROOT / "LEIAME.md").read_text(encoding="utf-8")
APP = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")


def headings(text):
    return re.findall(r"^#{1,6} ", text, flags=re.M)


def code_blocks(text):
    return re.findall(r"```.*?```", text, flags=re.S)


def test_readme_and_leiame_have_the_same_structure():
    assert headings(README) == headings(LEIAME)


def test_readme_and_leiame_have_the_same_code_blocks():
    assert code_blocks(README) == code_blocks(LEIAME)


def test_readme_and_leiame_link_to_each_other():
    assert "(LEIAME.md)" in README.split("\n\n")[1]
    assert "(README.md)" in LEIAME.split("\n\n")[1]


@pytest.mark.parametrize("name", ["README.md", "LEIAME.md"])
def test_texts_link_every_repository_of_the_registry_under_its_owner(reg, name):
    text = (ROOT / name).read_text(encoding="utf-8")
    repos = {w.repository for w in registry.workflows(reg) if w.kind != "platform"}
    for repo in repos:
        assert f"https://github.com/{reg['owner']}/{repo})" in text, repo
    linked = set(re.findall(r"https://github\.com/([\w.-]+)/5ltep-layer", text))
    assert linked == {reg["owner"]}, "a link points to an old owner"


def test_citation_points_to_the_platform_repository(reg):
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    p = reg["platform"]
    assert f"https://github.com/{p['owner']}/{p['repository']}" in text


def test_the_site_names_every_gap():
    for status in set(schedules.STATUSES) - {"read", "unlisted"}:
        assert APP.count(f"s_{status}:") == 2, status          # English and Portuguese


def test_the_site_links_to_the_editor_and_to_the_runs():
    assert "/edit/main/.github/workflows/" in APP and "/actions/workflows/" in APP


FORBIDDEN = [r"ranking (of|dos) ", r"\bworst portal", r"pior portal", r"will be adopted", r"será adotad",
             r"\bfraud", r"\bfraude"]


@pytest.mark.parametrize("name", ["README.md", "LEIAME.md", "docs/app.js"])
def test_texts_keep_the_humility_premise(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    text = re.sub(r"not a ranking of the agencies|não é ranking dos órgãos|não ranking dos órgãos", "", text)
    for pattern in FORBIDDEN:
        assert not re.search(pattern, text, flags=re.I), f"{name}: '{pattern}'"


@pytest.mark.parametrize("workflow", sorted((ROOT / ".github" / "workflows").glob("*.yml")), ids=lambda p: p.name)
def test_no_expression_inside_run(workflow):
    text = workflow.read_text(encoding="utf-8")
    for block in re.findall(r"run: \|\n((?:\s{10,}.*\n)+)|run: (.*)", text):
        assert "${{" not in "".join(block), f"{workflow.name}: expression inside run:"


def test_the_job_that_reads_does_not_write():
    text = (ROOT / ".github" / "workflows" / "cupim.yml").read_text(encoding="utf-8")
    reader = text.split("  publish:")[0].split("  read:")[1]
    assert "contents: read" in reader and "contents: write" not in reader and "git push" not in reader


def test_the_platform_workflow_is_listed_and_scheduled(reg):
    for w in reg["platform"]["workflows"]:
        text = (ROOT / ".github" / "workflows" / w["file"]).read_text(encoding="utf-8")
        assert schedules.published_crons(text)
