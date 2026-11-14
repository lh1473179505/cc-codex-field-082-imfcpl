"""Minimal namespace-aware XML helpers. Stdlib only."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


def load(path: str | Path) -> ET.Element:
    tree = ET.parse(path)
    return tree.getroot()


def local(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def child(el: ET.Element, ns: str, name: str) -> ET.Element | None:
    return el.find(f"{{{ns}}}{name}")


def child_text(el: ET.Element, ns: str, name: str, default: str | None = None) -> str | None:
    node = child(el, ns, name)
    if node is None or node.text is None:
        return default
    return node.text.strip()


def children(el: ET.Element, ns: str, name: str) -> list[ET.Element]:
    return list(el.findall(f"{{{ns}}}{name}"))


def iter_children(el: ET.Element) -> list[ET.Element]:
    return list(el)


def q(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"
