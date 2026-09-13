from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

SCF = re.compile(r"SCF Done:\s+E\([^)]+\)\s+=\s+([-+\d.DEd]+)")
ZPE = re.compile(r"Zero-point correction=\s*([-+\d.]+)")
THERMAL_G = re.compile(r"Thermal correction to Gibbs Free Energy=\s*([-+\d.]+)")
FREQUENCIES = re.compile(r"Frequencies --\s+(.+)")
NPA_ROW = re.compile(r"^\s*([A-Z][a-z]?)\s+(\d+)\s+([-+\d.]+)\s+", re.MULTILINE)
NBO_ROW = re.compile(
    r"LP\s*\(\s*\d+\)\s*([A-Z][a-z]?)\s+(\d+).*?BD\*\s*\(\s*\d+\)\s*([A-Z][a-z]?)\s+(\d+)\s*-\s*([A-Z][a-z]?)\s+(\d+).*?([-+\d.]+)\s+[-+\d.]+\s+[-+\d.]+"
)


@dataclass
class GaussianResult:
    name: str
    electronic_hartree: float | None
    zpe_hartree: float | None
    thermal_g_hartree: float | None
    gibbs_hartree: float | None
    imaginary_frequencies: int
    normal_termination: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _last(pattern: re.Pattern[str], text: str) -> float | None:
    matches = pattern.findall(text)
    return float(matches[-1].replace("D", "E")) if matches else None


def parse_log(path: str | Path, name: str | None = None) -> GaussianResult:
    source = Path(path)
    text = source.read_text(errors="replace")
    electronic = _last(SCF, text)
    correction = _last(THERMAL_G, text)
    frequencies = [float(value) for line in FREQUENCIES.findall(text) for value in line.split()]
    return GaussianResult(
        name=name or source.stem,
        electronic_hartree=electronic,
        zpe_hartree=_last(ZPE, text),
        thermal_g_hartree=correction,
        gibbs_hartree=electronic + correction if electronic is not None and correction is not None else None,
        imaginary_frequencies=sum(value < 0 for value in frequencies),
        normal_termination="Normal termination of Gaussian" in text,
    )


def extract_npa(path: str | Path) -> list[dict[str, object]]:
    text = Path(path).read_text(errors="replace")
    anchor = text.rfind("Summary of Natural Population Analysis")
    section = text[anchor:] if anchor >= 0 else ""
    return [{"element": element, "atom": int(atom), "natural_charge": float(charge)} for element, atom, charge in NPA_ROW.findall(section)]


def extract_lp_n_to_bd_star(path: str | Path) -> list[dict[str, object]]:
    text = Path(path).read_text(errors="replace")
    rows = []
    for donor_element, donor_atom, a_element, a_atom, b_element, b_atom, e2 in NBO_ROW.findall(text):
        if donor_element == "N":
            rows.append({
                "donor": f"N{donor_atom}",
                "acceptor": f"{a_element}{a_atom}-{b_element}{b_atom}",
                "e2_kcal_mol": float(e2),
            })
    return rows
