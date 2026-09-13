from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .generator import generate
from .parser import extract_npa, parse_log
from .thermo import dehydrogenation_energy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lohcflow")
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("generate")
    make.add_argument("manifest")
    make.add_argument("--settings", required=True)
    make.add_argument("--output", required=True)
    collect = sub.add_parser("collect")
    collect.add_argument("manifest")
    collect.add_argument("--root", required=True)
    collect.add_argument("--output", required=True)
    pathway = sub.add_parser("pathway")
    pathway.add_argument("energies")
    pathway.add_argument("--output", required=True)
    npa = sub.add_parser("npa")
    npa.add_argument("log")
    npa.add_argument("--atoms", nargs="*", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "generate":
        print(f"Generated {generate(args.manifest, args.settings, args.output)} jobs")
    elif args.command == "collect":
        rows = []
        with Path(args.manifest).open(newline="", encoding="utf-8") as handle:
            for item in csv.DictReader(handle):
                result = parse_log(Path(args.root) / item["name"] / f"{item['name']}.log", item["name"])
                rows.append(result.as_dict())
        _write_csv(Path(args.output), rows)
    elif args.command == "pathway":
        with Path(args.energies).open(newline="", encoding="utf-8") as handle:
            data = list(csv.DictReader(handle))
        h2 = float(next(row["energy_hartree"] for row in data if row["name"] == "H2"))
        species = [row for row in data if row["name"] != "H2"]
        rows = []
        for initial, final in zip(species, species[1:]):
            n = int(initial["hydrogen_count"]) - int(final["hydrogen_count"])
            released = n // 2
            total, average = dehydrogenation_energy(float(initial["energy_hartree"]), float(final["energy_hartree"]), h2, released)
            rows.append({"step": f"{initial['name']}->{final['name']}", "released_h2": released, "delta_e_kj_mol": total, "average_kj_mol_h2": average})
        _write_csv(Path(args.output), rows)
    elif args.command == "npa":
        selected = set(args.atoms or [])
        for row in extract_npa(args.log):
            if not selected or row["atom"] in selected:
                print(f"{row['element']}{row['atom']}: {row['natural_charge']:+.6f}")
    return 0


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["name"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")
