import streamlit as st
import pandas as pd
from pathlib import Path

from ccm_calculator import run_scenario, innovation_multiplier

APP_TITLE = "Cognitive Capital Multiplier (CCM) – Scenario Calculator"
BETA_DEFAULT = 0.69
BETA_LOW = 0.62
BETA_HIGH = 0.78

INTRO_TEXT = r"""
## 📘 What is cognitive capital?

**Cognitive capital** is an integrated indicator of a country's human potential.

In this project it combines three components, all taken from *real international datasets*:

- **Average years of schooling** among adults  
- **Share of adults with tertiary education (university degree)**  
- **Quality of schooling**, measured by international PISA tests  

These dimensions come from UNESCO, the World Bank, OECD and PISA.
They capture how much *high-quality* education a society has accumulated – the foundation
for innovation, high-tech exports and advanced institutions.

---

## 📘 What is β (beta)?

**Beta (β)** is the elasticity of innovation with respect to cognitive capital.

In simple terms:

> β tells us how strongly innovation responds when cognitive capital increases.

From an empirical panel of **85 countries, 2001–2024**, the estimated elasticity is:

- Central estimate: **β ≈ 0.69**
- 95% CI: **0.62–0.78**

Interpretation:

> A +1 SD increase in cognitive capital is associated with roughly a **doubling**
> of innovation output after 5–8 years.

---

## 📘 What does this calculator do?

The CCM tool implements the long-run scenario formula:

\[
\text{Innovation}_{2040} \approx \text{Innovation}_{2024} \cdot e^{\beta \cdot \Delta C}
\]

Where:
- Innovation\_2024 is the baseline (e.g., high-tech exports),
- ΔC is the improvement in cognitive capital (in SD),
- β is the empirically estimated elasticity.

**In practice:**  
You choose a country, set ΔC, and the tool shows the implied multiplier on innovation
and an approximate projection for high-tech exports in 2040.

The aim is not to deliver precise forecasts, but to provide a transparent way
to reason about *orders of magnitude* for long-run gains from cognitive-capital policies.

---

## 📘 Example: Israel

- Cognitive capital 2024: **2.18 SD**  
- Improvement ΔC = **+1.20 SD**  
- β = **0.69**

\[
e^{0.69 \cdot 1.20} \approx 2.0
\]

Meaning:

> Innovation output and high-tech exports could **double** over 10–15 years,
> under historically plausible improvements in cognitive capital.

---

## 📘 Data sources

This tool uses **real open data**:

- UNESCO Institute for Statistics  
- World Bank education & tertiary attainment  
- OECD PISA  
- WIPO patent databases  
- UN Comtrade high-tech export data  

The underlying panel regression and datasets are documented in detail at:  
🔗 https://doi.org/10.5281/zenodo.17454336

---

## 📘 Why only 10 countries here?

The app uses a minimal illustrative sample to keep performance high and the interface simple:

- lower-capital cases (India, Brazil),
- mid-capital cases (UAE, Estonia),
- leaders (United States, Singapore, South Korea).

The **full research panel includes 85 countries**.

---

## 📘 Why exactly 85 countries in the study?

Only countries with **reasonably complete and consistent data** for 2001–2024 are included:
education, tertiary attainment, PISA, patents, and high-tech exports.

Many countries lack reliable coverage and would introduce noise and bias,
so they are excluded from the core regression sample.  
The CCM tool intentionally trades coverage for **data quality and transparency**.

---

## 📘 Access to all 85 countries

💡 Yes — this is possible.

An extended version of the CCM tool can include:

- all **85 countries**,  
- the full 2001–2024 panel,  
- interactive time-series charts,  
- custom Excel uploads,  
- country-specific policy analysis.

Useful for:

- consulting,  
- government strategy units,  
- international organisations,  
- university research centres.

📩 For collaboration, custom scenarios or access to extended tools,  
please contact: **evoluit-m@proton.me**
"""


@st.cache_data
def load_countries(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["country"] = df["country"].astype(str)
    return df


def main():
    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide",
    )

    st.title(APP_TITLE)
    st.markdown(INTRO_TEXT)

    # Load data
    csv_path = Path(__file__).parent / "sample_countries.csv"
    df = load_countries(csv_path)

    # Sidebar controls
    st.sidebar.header("Scenario controls")

    country_name = st.sidebar.selectbox(
        "Country",
        options=df["country"].tolist(),
        index=0,
    )

    beta = st.sidebar.slider(
        "Elasticity β",
        min_value=0.50,
        max_value=0.90,
        value=BETA_DEFAULT,
        step=0.01,
        help="Central estimate in the paper: β ≈ 0.69 (95% CI: 0.62–0.78).",
    )

    delta_c = st.sidebar.slider(
        "Change in cognitive capital ΔC (SD, 2024 → 2040)",
        min_value=0.0,
        max_value=1.5,
        value=1.2,
        step=0.05,
        help="Ambitious but historically observed trajectories are around +1.0–1.2 SD.",
    )

    use_custom_baseline = st.sidebar.checkbox(
        "Use custom baseline exports for selected country",
        value=False,
    )

    row = df[df["country"] == country_name].iloc[0]

    if use_custom_baseline:
        baseline_exports = st.sidebar.number_input(
            "Baseline high-tech exports 2024 (bn USD)",
            min_value=0.0,
            value=float(row["baseline_hitech_exports_2024_bn"]),
            step=10.0,
        )
    else:
        baseline_exports = float(row["baseline_hitech_exports_2024_bn"])

    # Compute scenario for selected country
    scenario = run_scenario(
        country=country_name,
        c_quality_2024=float(row["C_quality_2024_SD"]),
        delta_c=delta_c,
        beta=beta,
        exports_2024=baseline_exports,
    )

    # Selected country metrics
    st.subheader("Selected country scenario")

    col1, col2, col3 = st.columns(3)
    col1.metric("Country", scenario.country)
    col2.metric("C_quality 2024 (SD)", f"{scenario.c_quality_2024:.2f}")
    col3.metric("ΔC 2024→2040 (SD)", f"{scenario.delta_c:.2f}")

    st.metric(
        "Innovation / exports multiplier",
        f"{scenario.multiplier:.2f}×",
    )

    if scenario.exports_2040 is not None:
        st.metric(
            "High-tech exports 2040 (bn USD)",
            f"{scenario.exports_2040:.1f}",
        )

    st.markdown("---")

  # Build comparison table (using the same ΔC for all countries)
    rows = []
    for _, r in df.iterrows():
        # use the global delta_c slider value for all countries
        m = innovation_multiplier(beta, delta_c)
        exports_2040 = r["baseline_hitech_exports_2024_bn"] * m

        rows.append({
            "Country": r["country"],
            "C_quality_2024_SD": r["C_quality_2024_SD"],
            "Delta_C_2024_2040_SD": delta_c,
            "Multiplier": m,
            "Exports_2024_bn": r["baseline_hitech_exports_2024_bn"],
            "Exports_2040_bn": exports_2040,
        })

    df_out = pd.DataFrame(rows)


    df_out = pd.DataFrame(rows)

    def highlight(row_):
        # very soft highlight for the selected country
        color = "background-color: rgba(255, 255, 150, 0.12)"
        return [color if row_["Country"] == scenario.country else "" for _ in row_]

    st.subheader("Illustrative scenarios for all sample countries")
    st.dataframe(
        df_out.style.format(
            {
                "C_quality_2024_SD": "{:.2f}",
                "Delta_C_2024_2040_SD": "{:.2f}",
                "Multiplier": "{:.2f}",
                "Exports_2024_bn": "{:.1f}",
                "Exports_2040_bn": "{:.1f}",
            }
        ).apply(highlight, axis=1),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown(
        """
### ⚠️ Limitations & Intended Use

This calculator is a **simplified exploratory tool**.  
It is designed to help policymakers, analysts, students and researchers
quickly understand **the scale** of potential long-run innovation effects
associated with changes in cognitive capital.

It **does not**:
- forecast exact values,  
- account for economic shocks or crises,  
- include R&D spending, institutional quality or geopolitics,  
- model saturation effects or feedback loops.

The results should be interpreted as **transparent what-if scenarios**,  
not precise predictions.

For full reproducibility, please refer to the GitHub repository and Zenodo archive.
"""
    )


if __name__ == "__main__":
    main()
                "Country": r["country"],
                "Multiplier": m,
                "Exports_2024_bn": r["baseline_hitech_exports_2024_bn"],

