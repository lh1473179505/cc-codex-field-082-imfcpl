"""AssetMap (SMPTE ST 429-9) subset parser."""

from __future__ import annotations

from pathlib import Path

from . import ns, xmlutil


def parse_assetmap(path: str | Path) -> dict:
    root = xmlutil.load(path)
    assets = []
    listing = xmlutil.child(root, ns.AM, "AssetList")
    if listing is not None:
        for asset in xmlutil.children(listing, ns.AM, "Asset"):
            aid = xmlutil.child_text(asset, ns.AM, "Id")
            packing = xmlutil.child(asset, ns.AM, "PackingList")
            is_pkl = packing is not None and (packing.text or "").strip().lower() in {"true", "1"}
            chunks = []
            cl = xmlutil.child(asset, ns.AM, "ChunkList")
            if cl is not None:
                for ch in xmlutil.children(cl, ns.AM, "Chunk"):
                    chunks.append(
                        {
                            "path": xmlutil.child_text(ch, ns.AM, "Path"),
                            "volume_index": xmlutil.child_text(ch, ns.AM, "VolumeIndex"),
                            "offset": xmlutil.child_text(ch, ns.AM, "Offset"),
                            "length": xmlutil.child_text(ch, ns.AM, "Length"),
                        }
                    )
            assets.append({"id": aid, "packing_list": is_pkl, "chunks": chunks})
    return {
        "id": xmlutil.child_text(root, ns.AM, "Id"),
        "volume_count": xmlutil.child_text(root, ns.AM, "VolumeCount"),
        "issue_date": xmlutil.child_text(root, ns.AM, "IssueDate"),
        "issuer": xmlutil.child_text(root, ns.AM, "Issuer"),
        "annotation": xmlutil.child_text(root, ns.AM, "AnnotationText"),
        "assets": assets,
        "path": str(path),
    }
