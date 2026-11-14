"""Build a new IMF CompositionPlaylist. Not implemented in the initial snapshot."""

from __future__ import annotations


class NotImplementedCompose(NotImplementedError):
    pass


def compose(package_dir: str, policy_path: str, output_cpl: str, report_path: str) -> int:
    raise NotImplementedCompose(
        "imfcpl.compose.compose is not implemented yet; AssetMap / PKL / CPL probe already work"
    )
