# Gaussian LOHC Workflows

A reproducible molecular-DFT workflow for screening liquid organic hydrogen
carrier (LOHC) candidates with Gaussian on HPC systems. The project focuses on
the parts of computational chemistry that are easy to audit and automate:
manifest-driven calculations, scheduler templates, thermochemistry extraction,
dehydrogenation-energy bookkeeping, and selected NPA/NBO descriptors.

All bundled energies are synthetic. No unpublished molecular structures or
research results are included.

## Capabilities

- Generate Gaussian input files and PBS Pro/SLURM job scripts from a CSV manifest
- Parse SCF energies, zero-point corrections, thermal free-energy corrections,
  imaginary frequencies, and normal termination status
- Extract Natural Population Analysis charges by atom
- Extract selected LP(N) -> BD* second-order perturbation interactions
- Calculate stepwise and average dehydrogenation energies in kJ mol^-1 H2
- Estimate gravimetric hydrogen-storage capacity from molecular formulae
- Export tidy CSV files suitable for plotting or machine-learning workflows

## Quick start

```bash
python -m lohcflow generate examples/demo/manifest.csv \
  --settings examples/demo/settings.json --output runs/demo
python -m lohcflow collect examples/demo/manifest.csv --root runs/demo \
  --output results.csv
python -m lohcflow pathway examples/demo/energies.csv --output pathway.csv
python -m lohcflow npa examples/demo/sample.log --atoms 1 2 3 4 5
```

The example uses a generic hydrogenation series and deliberately fabricated
output values. Replace the method, basis, resources, charge/multiplicity and
coordinates through the manifest and settings file.

## Energy convention

For release of `n` hydrogen molecules,

\[
\Delta E_{dehyd} = E_{dehydrogenated} + nE_{H_2} - E_{hydrogenated}
\]

The reported average is `Delta E / n`. Hartree values are converted using
2625.499639 kJ mol^-1 Hartree^-1. Gibbs corrections are used only when present
for every species involved in a comparison.

## Reproducibility and responsible sharing

- Method and basis are explicit in version-controlled settings.
- Raw output files are ignored because they can be large and may contain
  unpublished results.
- The parser records failed termination and imaginary-frequency counts.
- NBO descriptors are treated as electronic-structure descriptors, not direct
  proof of a kinetic dehydrogenation pathway.

## License

MIT.
