"""Parse IMF EditRate strings. Conversion and homogenization are left to compose."""

from __future__ import annotations


class EditRateError(ValueError):
    pass


def parse_edit_rate(text: str) -> tuple[int, int]:
    """Parse 'n d' or 'n' (denominator defaults to 1)."""
    parts = text.split()
    if len(parts) == 1:
        n, d = int(parts[0]), 1
    elif len(parts) == 2:
        n, d = int(parts[0]), int(parts[1])
    else:
        raise EditRateError(f"invalid edit rate: {text!r}")
    if n <= 0 or d <= 0:
        raise EditRateError(f"invalid edit rate: {text!r}")
    return n, d


def format_edit_rate(rate: tuple[int, int]) -> str:
    return f"{rate[0]} {rate[1]}"
