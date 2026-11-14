"""PackingList (SMPTE ST 429-8) subset parser."""

from __future__ import annotations

from pathlib import Path

from . import ns, xmlutil


def parse_packinglist(path: str | Path) -> dict:
    root = xmlutil.load(path)
    assets = []
    listing = xmlutil.child(root, ns.PKL, "AssetList")
    if listing is not None:
        for asset in xmlutil.children(listing, ns.PKL, "Asset"):
            assets.append(
                {
                    "id": xmlutil.child_text(asset, ns.PKL, "Id"),
                    "hash": xmlutil.child_text(asset, ns.PKL, "Hash"),
                    "size": xmlutil.child_text(asset, ns.PKL, "Size"),
                    "type": xmlutil.child_text(asset, ns.PKL, "Type"),
                    "original_file_name": xmlutil.child_text(asset, ns.PKL, "OriginalFileName"),
                    "annotation": xmlutil.child_text(asset, ns.PKL, "AnnotationText"),
                }
            )
    return {
        "id": xmlutil.child_text(root, ns.PKL, "Id"),
        "issue_date": xmlutil.child_text(root, ns.PKL, "IssueDate"),
        "issuer": xmlutil.child_text(root, ns.PKL, "Issuer"),
        "annotation": xmlutil.child_text(root, ns.PKL, "AnnotationText"),
        "assets": assets,
        "path": str(path),
    }
