"""CompositionPlaylist (SMPTE ST 2067-3) subset parser. Does not retime resources."""

from __future__ import annotations

from pathlib import Path

from . import ns, rate, xmlutil


def _int_or_none(text: str | None) -> int | None:
    if text is None or text == "":
        return None
    return int(text)


def _parse_resource(res: object) -> dict:
    er_text = xmlutil.child_text(res, ns.CPL, "EditRate")
    return {
        "id": xmlutil.child_text(res, ns.CPL, "Id"),
        "annotation": xmlutil.child_text(res, ns.CPL, "Annotation"),
        "edit_rate": rate.parse_edit_rate(er_text) if er_text else None,
        "intrinsic_duration": _int_or_none(xmlutil.child_text(res, ns.CPL, "IntrinsicDuration")),
        "entry_point": _int_or_none(xmlutil.child_text(res, ns.CPL, "EntryPoint")),
        "source_duration": _int_or_none(xmlutil.child_text(res, ns.CPL, "SourceDuration")),
        "repeat_count": _int_or_none(xmlutil.child_text(res, ns.CPL, "RepeatCount")) or 1,
        "track_file_id": xmlutil.child_text(res, ns.CPL, "TrackFileId"),
    }


def _sequence_kind(tag: str) -> str | None:
    local = xmlutil.local(tag)
    return ns.SEQ_LOCAL.get(local)


def parse_cpl(path: str | Path) -> dict:
    root = xmlutil.load(path)
    app_ids = []
    app = xmlutil.child(root, ns.CPL, "ApplicationIdentificationList")
    if app is None:
        app = xmlutil.child(root, ns.CPL, "ApplicationIdentification")
    if app is not None:
        if xmlutil.local(app.tag) == "ApplicationIdentification" and (app.text or "").strip() and not list(app):
            app_ids.append(app.text.strip())
        else:
            for child in xmlutil.iter_children(app):
                if xmlutil.local(child.tag) == "ApplicationIdentification" and child.text:
                    app_ids.append(child.text.strip())
    er_text = xmlutil.child_text(root, ns.CPL, "EditRate")
    segments = []
    sl = xmlutil.child(root, ns.CPL, "SegmentList")
    if sl is not None:
        for seg in xmlutil.children(sl, ns.CPL, "Segment"):
            sequences = []
            seq_list = xmlutil.child(seg, ns.CPL, "SequenceList")
            if seq_list is not None:
                for seq in xmlutil.iter_children(seq_list):
                    kind = _sequence_kind(seq.tag)
                    if not kind:
                        continue
                    # Sequence children live in the CPL namespace even when
                    # the sequence element itself is in the 2067-2 namespace.
                    resources = []
                    rl = xmlutil.child(seq, ns.CPL, "ResourceList")
                    if rl is not None:
                        for res in xmlutil.children(rl, ns.CPL, "Resource"):
                            resources.append(_parse_resource(res))
                    sequences.append(
                        {
                            "kind": kind,
                            "local_name": xmlutil.local(seq.tag),
                            "id": xmlutil.child_text(seq, ns.CPL, "Id"),
                            "track_id": xmlutil.child_text(seq, ns.CPL, "TrackId"),
                            "resources": resources,
                        }
                    )
            segments.append(
                {
                    "id": xmlutil.child_text(seg, ns.CPL, "Id"),
                    "annotation": xmlutil.child_text(seg, ns.CPL, "Annotation"),
                    "sequences": sequences,
                }
            )
    markers = []
    # MarkerSequence, if present, is under Segment SequenceList (2067-3).
    for seg in segments:
        for seq in list(seg["sequences"]):
            if seq["local_name"] == "MarkerSequence" or seq["kind"] is None:
                pass
    # Also accept a house-extended MarkerList under the CPL root.
    ml = xmlutil.child(root, ns.CPL, "MarkerList")
    if ml is not None:
        for mk in xmlutil.children(ml, ns.CPL, "Marker"):
            markers.append(
                {
                    "label_kind": xmlutil.child_text(mk, ns.CPL, "Label"),
                    "offset_eu": _int_or_none(xmlutil.child_text(mk, ns.CPL, "Offset")),
                    "annotation": xmlutil.child_text(mk, ns.CPL, "Annotation"),
                }
            )
    return {
        "id": xmlutil.child_text(root, ns.CPL, "Id"),
        "annotation": xmlutil.child_text(root, ns.CPL, "Annotation"),
        "issue_date": xmlutil.child_text(root, ns.CPL, "IssueDate"),
        "issuer": xmlutil.child_text(root, ns.CPL, "Issuer"),
        "creator": xmlutil.child_text(root, ns.CPL, "Creator"),
        "content_title": xmlutil.child_text(root, ns.CPL, "ContentTitle"),
        "content_kind": xmlutil.child_text(root, ns.CPL, "ContentKind"),
        "edit_rate": rate.parse_edit_rate(er_text) if er_text else None,
        "application_identification": app_ids,
        "segments": segments,
        "markers": markers,
        "path": str(path),
    }
