"""Inventory an IMF package: AssetMap, PackingList, CPL virtual tracks, sidecar descriptors."""

from __future__ import annotations

import json
from pathlib import Path

from . import am, cpl, descriptors, pkl


def _resolve(package_dir: Path, rel: str | None) -> Path | None:
    if not rel:
        return None
    return (package_dir / rel).resolve()


def probe_package(package_dir: str | Path) -> dict:
    root = Path(package_dir)
    am_path = root / "ASSETMAP.xml"
    if not am_path.is_file():
        raise FileNotFoundError(f"ASSETMAP.xml not found under {root}")
    assetmap = am.parse_assetmap(am_path)
    pkl_path = None
    other_xml = []
    for asset in assetmap["assets"]:
        for chunk in asset["chunks"]:
            p = _resolve(root, chunk.get("path"))
            if p is None or not p.is_file():
                continue
            if asset.get("packing_list"):
                pkl_path = p
            elif p.name.upper().endswith(".XML") and p.name.upper() != "ASSETMAP.XML":
                other_xml.append(p)
    packing = pkl.parse_packinglist(pkl_path) if pkl_path else None
    cpls = []
    for p in other_xml:
        try:
            parsed = cpl.parse_cpl(p)
        except Exception:
            continue
        if parsed.get("segments") is not None and parsed.get("id"):
            cpls.append(parsed)
    # Also pick up any CPL*.xml not listed (should not happen in a valid map).
    desc_path = root / "descriptors.json"
    desc = descriptors.load_descriptors(desc_path) if desc_path.is_file() else {"assets": {}}
    return {
        "package": str(root),
        "assetmap": assetmap,
        "packinglist": packing,
        "cpls": cpls,
        "descriptor_ids": sorted(desc["assets"].keys()),
        "descriptor_count": len(desc["assets"]),
    }


def format_probe(info: dict) -> str:
    return json.dumps(info, ensure_ascii=False, indent=2)
