"""The registry is valid, complete, holds no schedule and expands to one entry per workflow of each
repository."""

import pytest

from src import registry


def test_the_published_registry_is_valid(reg):
    assert registry.validate(reg) == []


def test_every_layer_has_an_instance_for_every_portal(reg):
    portals = {p["id"] for p in reg["portals"]}
    for layer in reg["layers"]:
        assert set(layer["instances"]) == portals, layer["id"]


def test_one_entry_per_instance_and_workflow(reg):
    ws = registry.workflows(reg)
    per_layer = sum(len(layer["workflows"]) * len(layer["instances"]) for layer in reg["layers"])
    aux = sum(len(a["workflows"]) for a in reg["auxiliary"])
    assert len(ws) == per_layer + aux + len(reg["platform"]["workflows"])
    assert len({(w.full_name, w.file) for w in ws}) == len(ws)


def test_layer5_reads_the_layers_of_its_own_portal(reg):
    l5 = {w.portal: w for w in registry.workflows(reg) if w.layer == "L5"}
    assert l5["aneel"].reads == ["5ltep-layer1-aneel", "5ltep-layer2-aneel", "5ltep-layer3-aneel", "5ltep-layer4-aneel"]


def test_moving_the_repositories_changes_one_value(reg):
    reg["owner"] = "5ltep-cupim"
    assert all(w.full_name.startswith("5ltep-cupim/") for w in registry.workflows(reg))


@pytest.mark.parametrize("change, message", [
    (lambda r: r.update(owner=""), "'owner' is empty"),
    (lambda r: r["layers"][1]["workflows"][0].update(cron=["30 4 * * 3"]), "holds no schedule"),
    (lambda r: r["layers"][4]["workflows"][0].update(reads=["L9"]), "reads unknown"),
    (lambda r: r["layers"][0]["instances"].update(x="5ltep-layer1-x"), "unknown portal"),
    (lambda r: r["portals"][1].update(main=True), "exactly one portal"),
    (lambda r: r["layers"].pop(), "layers must be"),
])
def test_errors_are_reported(reg, change, message):
    change(reg)
    assert any(message in e for e in registry.validate(reg))
