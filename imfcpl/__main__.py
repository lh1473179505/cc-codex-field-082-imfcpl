from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import compose, probe


def cmd_probe(args: argparse.Namespace) -> int:
    try:
        info = probe.probe_package(args.package)
    except FileNotFoundError as e:
        sys.stderr.write(str(e) + "\n")
        return 2
    text = probe.format_probe(info)
    if args.out:
        Path(args.out).write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    try:
        return compose.compose(args.package, args.policy, args.output, args.report)
    except compose.NotImplementedCompose as e:
        sys.stderr.write(str(e) + "\n")
        return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="imfcpl")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("probe", help="inventory an IMF package")
    sp.add_argument("--package", required=True)
    sp.add_argument("--out", default=None)
    sp.set_defaults(func=cmd_probe)
    sc = sub.add_parser("compose", help="write a new CompositionPlaylist")
    sc.add_argument("--package", required=True)
    sc.add_argument("--policy", required=True)
    sc.add_argument("--output", required=True)
    sc.add_argument("--report", required=True)
    sc.set_defaults(func=cmd_compose)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
