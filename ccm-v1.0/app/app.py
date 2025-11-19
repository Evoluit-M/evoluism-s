import streamlit as st
import pandas as pd
from pathlib import Path

from ccm_calculator import run_scenario, innovation_multiplier

APP_TITLE = "Cognitive Capital Multiplier (CCM) – Scenario Calculator"
BETA_DEFAULT = 0.69
BETA_LOW = 0.62
BETA_HIGH = 0.78


def load_countries(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["country"] = df["country"].astype(str)
    return df


def main():
    st.set_page_config(
        page_title="CCM – Cognitive Capital Multiplier",
        layout="centered",
    )

    st.title("Cognitive Capital Multiplier (CCM)")
    st.caption(
        "Open-source scenario calculator based on the Evoluism CCM paper "
        "(DOI: 10.5281/zenodo.17635565)."
    )

    st.markdown(
        '''
This tool is intentionally **simple** and **transparent**:

- Cognitive capital levels `C` are expressed in **standard deviations (SD)** 
  relative to the 2024 global mean.
- The long-run relationship between cognitive capital and innovation is
  approximated by a **log-linear elasticity**:

  \\[
  \\text{Innovation}_{2040} \\approx
  \\text{Innovation}_{2024} \\times \\exp(\\beta \\cdot \\Delta C).
  \\]

- Empirical estimate: **β ≈ 0.69** (95% CI: 0.62–0.78).
        '''
    )

    # Load sample country data
    data_path = Path(__file__).parent / "sample_countries.csv"
    df_countries = load_countries(data_path)

    st.sidebar.header("Scenario settings")

    country_name = st.sidebar.selectbox(
        "Country",
        options=df_countries["country"].tolist(),
        index=0,
    )

    row = df_countries[df_countries["country"] == country_name].iloc[0]
    c_quality_2024 = float(row["C_quality_2024_SD"])
    exports_2024 = float(row["baseline_hitech_exports_2024_bn"])
    patents_index_2024 = float(row["baseline_patents_index"])

    st.sidebar.markdown("### Cognitive capital change (ΔC)")
    delta_c = st.sidebar.slider(
        "ΔC (SD, 2024–2040)",
        min_value=-0.5,
        max_value=1.5,
        value=1.2,
        step=0.1,
        help="Ambitious but historically observed trajectories are around +1.0 to +1.2 SD.",
    )

    st.sidebar.markdown("### Elasticity β")
    beta = st.sidebar.slider(
        "β (elasticity)",
        min_value=0.50,
        max_value=0.90,
        value=BETA_DEFAULT,
        step=0.01,
        help="Empirical estimate: β ≈ 0.69 (95% CI: 0.62–0.78).",
    )

    st.sidebar.markdown(
        f"95% CI band: **[{BETA_LOW:.2f}, {BETA_HIGH:.2f}]**"
    )

    st.sidebar.caption(
        "Note: this is a *scenario* tool, not a forecast. "
        "Results should be interpreted as rough orders of magnitude."
    )

    # Run scenario
    scenario = run_scenario(
        country=country_name,
        c_quality_2024=c_quality_2024,
        delta_c=delta_c,
        beta=beta,
        patents_2024=patents_index_2024,
        exports_2024=exports_2024,
    )

    st.subheader("Scenario summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Country", scenario.country)
    col2.metric("C_quality (2024, SD)", f"{scenario.c_quality_2024:.2f}")
    col3.metric("ΔC (2024–2040, SD)", f"{scenario.delta_c:.2f}")

    multiplier_central = scenario.multiplier
    multiplier_low = innovation_multiplier(BETA_LOW, delta_c)
    multiplier_high = innovation_multiplier(BETA_HIGH, delta_c)

    st.markdown("### Innovation multiplier")

    st.markdown(
        f"""
- Central estimate (β = {beta:.2f}): **×{multiplier_central:.2f}**
- 95% CI (β = 0.62–0.78): **×{multiplier_low:.2f} – ×{multiplier_high:.2f}**
"""
    )

    st.markdown("### High-tech exports scenario (approximate)")

    exports_2040 = scenario.exports_2040
    exports_low = exports_2024 * multiplier_low
    exports_high = exports_2024 * multiplier_high

    table = pd.DataFrame(
        {
            "": ["2024 baseline", "2040 (central)", "2040 (low β)", "2040 (high β)"],
            "High-tech exports (bn USD, approx.)": [
                exports_2024,
                exports_2040,
                exports_low,
                exports_high,
            ],
            "Multiplier vs 2024": [
                1.0,
                multiplier_central,
                multiplier_low,
                multiplier_high,
            ],
        }
    )

    st.dataframe(
        table.style.format(
            {
                "High-tech exports (bn USD, approx.)": "{:,.1f}",
                "Multiplier vs 2024": "{:,.2f}",
            }
        ),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown(
        """
#### How to interpret this tool

- It is **not** a precise forecast; it only translates a **log-linear elasticity**
  into long-run magnitudes.
- Cognitive capital is only **one** driver of innovation. The tool does not
  explicitly model R&D spending, institutions, culture or geopolitics.
- The primary value is to help policymakers reason about the *order of magnitude*
  of potential gains from sustained investment in cognitive capital.

For details, see the CCM paper and the documentation in this repository.
"""
    )


if __name__ == "__main__":
    main()
