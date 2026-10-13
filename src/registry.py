"""The registry (docs/registry.json): portals, layers, the repository of each instance and what each
scheduled workflow is for. It holds no schedule: the cron is read from the published workflow file.
It is validated as a whole; one error stops the reading."""

import json
from dataclasses import dataclass, field
from pathlib import Path

LAYERS = ["L1", "L2", "L3", "L4", "L5"]


@dataclass
class Workflow:
    """One scheduled workflow of one repository, as the registry lists it."""
    owner: str
    repository: str
    file: str
    kind: str                      # instance | auxiliary | platform
    layer: str | None = None
    portal: str | None = None
    reads: list[str] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repository}"


class RegistryError(ValueError):
    pass


def load(path: Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        raise RegistryError("invalid registry:\n- " + "\n- ".join(errors))
    return data


def validate(data: dict) -> list[str]:
    errors = []
    if not str(data.get("owner", "")).strip():
        errors.append("'owner' is empty")
    portals = [p.get("id") for p in data.get("portals", [])]
    if len(portals) != len(set(portals)) or not portals:
        errors.append("portal ids must exist and be unique")
    if sum(1 for p in data.get("portals", []) if p.get("main")) != 1:
        errors.append("exactly one portal must be 'main'")
    if [layer.get("id") for layer in data.get("layers", [])] != LAYERS:
        errors.append(f"layers must be {LAYERS}, in this order")
    known_repos = set()
    for layer in data.get("layers", []):
        for portal, repo in layer.get("instances", {}).items():
            if portal not in portals:
                errors.append(f"{layer.get('id')}: unknown portal '{portal}'")
            if not isinstance(repo, str) or not repo:
                errors.append(f"{layer.get('id')}/{portal}: the instance is a repository name")
            known_repos.add(repo)
    for aux in data.get("auxiliary", []):
        known_repos.add(aux.get("repository"))
        if aux.get("layer") not in LAYERS:
            errors.append(f"{aux.get('repository')}: unknown layer '{aux.get('layer')}'")
    for where, workflows in _all_workflows(data):
        seen = set()
        for w in workflows:
            if not w.get("file") or w["file"] in seen:
                errors.append(f"{where}: workflow file missing or repeated")
            seen.add(w.get("file"))
            if "cron" in w:
                errors.append(f"{where}/{w.get('file')}: the registry holds no schedule (it is read from the workflow)")
            for ref in w.get("reads", []):
                if ref not in LAYERS and ref not in known_repos:
                    errors.append(f"{where}/{w.get('file')}: reads unknown '{ref}'")
    platform = data.get("platform", {})
    if not platform.get("owner") or not platform.get("repository"):
        errors.append("'platform' needs 'owner' and 'repository'")
    return errors


def _all_workflows(data: dict):
    for layer in data.get("layers", []):
        yield layer.get("id"), layer.get("workflows", [])
    for aux in data.get("auxiliary", []):
        yield aux.get("repository"), aux.get("workflows", [])
    yield "platform", data.get("platform", {}).get("workflows", [])


def workflows(data: dict) -> list[Workflow]:
    """Every listed workflow of every repository, in the order of the registry."""
    owner = data["owner"]
    layers = {layer["id"]: layer for layer in data["layers"]}
    out = []
    for layer in data["layers"]:
        for portal in [p["id"] for p in data["portals"]]:
            repo = layer.get("instances", {}).get(portal)
            if repo is None:
                continue
            for w in layer["workflows"]:
                reads = [layers[r]["instances"].get(portal) if r in layers else r for r in w.get("reads", [])]
                out.append(Workflow(owner, repo, w["file"], "instance", layer["id"], portal, [r for r in reads if r]))
    for aux in data.get("auxiliary", []):
        for w in aux["workflows"]:
            out.append(Workflow(owner, aux["repository"], w["file"], "auxiliary", aux["layer"]))
    platform = data["platform"]
    for w in platform["workflows"]:
        out.append(Workflow(platform["owner"], platform["repository"], w["file"], "platform"))
    return out
