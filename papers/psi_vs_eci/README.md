# ψ vs ECI Paper

This folder contains the reproducible workflow for the paper:

**“ψ vs ECI: A Comparative Analysis of Cognitive–Institutional Complexity and Export Complexity as Predictors of Long-Run Growth (2000–2024)”**

## Structure

- `main_psi_vs_eci.tex` — main LaTeX file of the paper  
- `sections/` — logical split of the text:
  - `01_intro.tex`
  - `02_data_methods.tex`
  - `03_results.tex`
  - `04_robustness.tex`
  - `05_discussion.tex`
  - `06_conclusion.tex`
- `figures/` — all figures used in the paper (Figures 1–5)
- `tables/` — LaTeX tables (main regressions, robustness checks)
- `refs.bib` — bibliography for ψ vs ECI paper
- `Makefile` or `build.sh` (optional) — helper script to compile the paper

## Reproducibility

The analysis is fully reproducible from the main Evoluism-S pipeline.  
Key steps:

```bash
# build ψ–ECI growth panel
python src/C_econ/build_growth_panel_psi_eci_10y_v2_3.py

# main regressions
python src/C_econ/run_psi_vs_eci_regressions_10y_v2_3.py

# robustness checks
python src/C_econ/run_robustness_psi_eci_v3_0.py

# (optional) figures
python analysis/plot_psi_eci_figures.py
