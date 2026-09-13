from __future__ import annotations

import csv
import json
from pathlib import Path

PBS = """#!/bin/bash
#PBS -N {name}
#PBS -A {account}
#PBS -q {queue}
#PBS -l walltime={walltime}
#PBS -l ncpus={ncpus}
#PBS -l mem={memory}
#PBS -j oe
set -euo pipefail
cd "$PBS_O_WORKDIR"
module load {module}
{executable} < {name}.gjf > {name}.log
"""

SLURM = """#!/bin/bash
#SBATCH --job-name={name}
#SBATCH --account={account}
#SBATCH --partition={queue}
#SBATCH --time={walltime}
#SBATCH --cpus-per-task={ncpus}
#SBATCH --mem={memory}
#SBATCH --output={name}.scheduler.out
set -euo pipefail
module load {module}
{executable} < {name}.gjf > {name}.log
"""


def generate(manifest_path: str | Path, settings_path: str | Path, output: str | Path) -> int:
    settings = json.loads(Path(settings_path).read_text(encoding="utf-8"))
    scheduler_template = PBS if settings["scheduler"] == "pbs" else SLURM
    destination = Path(output)
    count = 0
    with Path(manifest_path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            folder = destination / row["name"]
            folder.mkdir(parents=True, exist_ok=True)
            route = settings["route"]
            gjf = (
                f"%chk={row['name']}.chk\n%nprocshared={settings['ncpus']}\n%mem={settings['memory']}\n"
                f"# {route}\n\n{row['name']}\n\n{row['charge']} {row['multiplicity']}\n{row['coordinates'].replace('|', chr(10))}\n\n"
            )
            (folder / f"{row['name']}.gjf").write_text(gjf, encoding="utf-8")
            values = {**settings, **row}
            (folder / "submit.sh").write_text(scheduler_template.format_map(values), encoding="utf-8")
            count += 1
    return count
