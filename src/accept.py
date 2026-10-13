"""The publish job accepts only the expected files: python -m src.accept <build> <repository root>.

The job that reads GitHub hands over an artifact; this job writes to the repository and reads
nothing external. Anything unexpected (another path, invalid JSON, an oversized file) stops it."""

import json
import shutil
import sys
from pathlib import Path

EXPECTED = {"docs/data/schedules.json"}
MAX_BYTES = 2 * 1024 * 1024


def accept(build: Path, root: Path) -> list[str]:
    files = sorted(p.relative_to(build).as_posix() for p in build.rglob("*") if p.is_file())
    unexpected = [f for f in files if f not in EXPECTED]
    if unexpected or set(files) != EXPECTED:
        raise SystemExit(f"refused: unexpected {unexpected}, missing {sorted(EXPECTED - set(files))}")
    for rel in files:
        path = build / rel
        if path.stat().st_size > MAX_BYTES:
            raise SystemExit(f"refused: {rel} is larger than {MAX_BYTES} bytes")
        if not isinstance(json.loads(path.read_text(encoding="utf-8")), dict):
            raise SystemExit(f"refused: {rel} is not a JSON object")
    for rel in files:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(build / rel, target)
    return files


if __name__ == "__main__":
    print("accepted:", ", ".join(accept(Path(sys.argv[1]), Path(sys.argv[2]))))
