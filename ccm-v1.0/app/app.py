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

---

## 📘 Example: Israel

- Cognitive capital 2024: **2.18 SD**  
- Improvement ΔC = **+1.20 SD**  
- β = **0.69**

\[
e^{0.69 \cdot 1.20} \approx 2.0
\]

Meaning:

> Innovation output and high-tech exports could **double** over 10–15 years.

---

## 📘 Data sources

This tool uses **real open data**:

- UNESCO Institute for Statistics  
- World Bank education & tertiary attainment  
- OECD PISA  
- WIPO patent databases  
- UN Comtrade high-tech export data  

Full documented dataset and regression analysis:  
🔗 https://doi.org/10.5281/zenodo.17454336

---

## 📘 Why only 10 countries here?

The app uses a minimal example set to keep performance high and the interface simple:

- lower-capital cases (India, Brazil)
- mid-capital cases (UAE, Estonia)
- leaders (USA, Singapore, Korea)

The **full research panel has 85 countries**.

---

## 📘 Why exactly 85 countries in the study?

Only countries with **complete and consistent data** for 2001–2024 are included:
education, tertiary attainment, PISA, patents, and high-tech exports.

Many countries lack reliable data and cannot be included without harming accuracy.

---

## 📘 Access to all 85 countries

💡 Yes — this is possible.

We can prepare an extended version of the CCM tool with:

- all **85 countries**  
- complete 2001–2024 dataset  
- interactive time-series charts  
- custom Excel uploads  
- country-specific policy analysis  

Useful for:

- consulting  
- government strategy units  
- international organizations  
- university research centers  

📩 Contact: **evoluit-m@proton.me**
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

    # Sidebar
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
    )

    delta_c = st.sidebar.slider(
        "Change in cognitive capital ΔC (SD, 2024 → 2040)",
        min_value=0.0,
        max_value=1.5,
        value=1.2,
        step=0.05,
    )

    use_custom_baseline = st.sidebar.checkbox(
        "Use custom baseline exports for selected country",
        value=False,
    )

    row = df[df["country"] == country_name].iloc[0]

    baseline_exports = (
        st.sidebar.number_input(
            "Baseline high-tech exports 2024 (bn USD)",
            min_value=0.0,
            value=float(row["baseline_hitech_exports_2024_bn"]),
            step=10.0,
        )
        if use_custom_baseline
        else float(row["baseline_hitech_exports_2024_bn"])
    )

    # Compute scenario
    scenario = run_scenario(
        country=country_name,
        c_quality_2024=float(row["C_quality_2024_SD"]),
        delta_c=delta_c,
        beta=beta,
        exports_2024=baseline_exports,
    )

    st.subheader("Selected country scenario")

    col1, col2, col3 = st.columns(3)
    col1.metric("Country", scenario.country)
    col2.metric("C_quality 2024 (SD)", f"{scenario.c_quality_2024:.2f}")
    col3.metric("ΔC (SD)", f"{scenario.delta_c:.2f}")

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

        rows.append(
            {
                "Country": r["country"],
                "C_quality_2024_SD": r["C_quality_2024_SD"],
                "Delta_C_2024_2040_SD": delta_c,
                "Multiplier": m,
                "Exports_2024_bn": r["baseline_hitech_exports_2024_bn"],
                "Exports_2040_bn": exports_2040,
            }
        )


    df_out = pd.DataFrame(rows)

    def highlight(row):
        return ["background-color: #fff3b0" if row["Country"] == scenario.country else "" for _ in row]

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


if __name__ == "__main__":
    main()

