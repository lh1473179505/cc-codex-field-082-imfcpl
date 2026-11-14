"""House sidecar essence descriptors (JSON, next to ASSETMAP.xml)."""

from __future__ import annotations

import json
from pathlib import Path


def load_descriptors(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text())
    assets = data.get("assets", data)
    return {"assets": assets, "path": str(path)}
