import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ============================================================
# TITLE + ABOUT
# ============================================================

st.title("Country Diagnostic Tool: ψ and ECI (10-year Growth Analysis)")

st.markdown(
    """
This interactive diagnostic tool allows users to explore **how a country’s
structural capabilities** — cognitive–institutional capacity (**ψ**) and 
export sophistication (**ECI**) — relate to **long-run 10-year GDP per capita 
growth**.

It is part of the replication package for the research article:

> **“ψ vs ECI: Cognitive–Institutional Capacity and Export Complexity  
> as Predictors of Long-Run Growth”**  
> Evoluit-M (2025)  
> Zenodo DOI: **10.5281/zenodo.XXXXXXX** (placeholder)

Dataset used here comes from the repository accompanying the article
(`data/processed/growth_panel_psi_eci_10y_v1_2.csv`).
    """
)

st.divider()

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_panel() -> pd.DataFrame:
    df = pd.read_csv("data/processed/growth_panel_psi_eci_10y_v1_2.csv")

    return df


df = load_panel()

# ============================================================
# SIDEBAR INPUTS
# ============================================================

st.sidebar.header("Settings")

all_iso = sorted(df["iso3"].unique())
country = st.sidebar.selectbox("Target country (ISO3):", all_iso, index=all_iso.index("ARG") if "ARG" in all_iso else 0)

y0_min = int(df["y0"].min())
y0_max = int(df["y0"].max())

y0_range = st.sidebar.slider(
    "Filter by starting year (y0):",
    min_value=y0_min,
    max_value=y0_max,
    value=(y0_min, y0_max),
    step=1
)

metric = st.sidebar.selectbox(
    "Metric on the X-axis:",
    ["psi", "eci"],
    index=0
)

# ============================================================
# FILTER DATA
# ============================================================

df_country = df[df["iso3"] == country].copy()
df_country = df_country[(df_country["y0"] >= y0_range[0]) & (df_country["y0"] <= y0_range[1])]

if df_country.empty:
    st.error("No data available for this country in the selected year range.")
    st.stop()

# ============================================================
# GLOBAL SUMMARY FOR THE SELECTED WINDOW
# ============================================================

st.subheader(f"Summary for {country} (selected window: {y0_range[0]}–{y0_range[1]})")

avg_growth = df_country["gdp_growth"].mean()
avg_psi = df_country["psi"].mean()
avg_eci = df_country["eci"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Avg 10-year growth (%)", f"{avg_growth:.2f}")
col2.metric("Avg ψ (z-score)", f"{avg_psi:.2f}")
col3.metric("Avg ECI (z-score)", f"{avg_eci:.2f}")

st.markdown(
    """
**Interpretation:**

- **Avg 10-year growth** shows how fast the country grew across selected starting years.  
- **ψ (z-score)** reflects cognitive–institutional capacity vs. global mean.  
- **ECI (z-score)** reflects export sophistication vs. global mean.
    """
)

# ============================================================
# GROWTH OVER TIME
# ============================================================

st.subheader("10-year GDP per capita growth over time")

chart_growth = (
    alt.Chart(df_country)
    .mark_line(point=True)
    .encode(
        x="y0:O",
        y=alt.Y("gdp_growth:Q", title="10-year annualized growth (%)"),
        tooltip=["y0", "y1", "gdp_growth"]
    )
    .properties(height=350)
)

st.altair_chart(chart_growth, use_container_width=True)

# ============================================================
# ψ AND ECI OVER TIME
# ============================================================

st.subheader("ψ and ECI (standardized) over time")

df_long = df_country.melt(
    id_vars=["iso3", "y0"],
    value_vars=["psi", "eci"],
    var_name="indicator",
    value_name="value"
)

chart_caps = (
    alt.Chart(df_long)
    .mark_line(point=True)
    .encode(
        x="y0:O",
        y="value:Q",
        color="indicator:N",
        tooltip=["y0", "indicator", "value"]
    )
    .properties(height=350)
)

st.altair_chart(chart_caps, use_container_width=True)

# ============================================================
# TABLE OF WINDOWS
# ============================================================

st.subheader(f"All 10-year windows for {country}")

st.dataframe(
    df_country[["iso3", "y0", "y1", "gdp_growth", "psi", "eci"]],
    use_container_width=True
)

# ============================================================
# INTERPRETATION GUIDE
# ============================================================

st.markdown(
    """
## How to interpret what you see

Use the charts and table together:

- **High growth, low ψ and low ECI**  
  → the country is in a **catch-up phase**: growing fast while still building
  institutional and structural capabilities.

- **Low growth, high ψ and/or high ECI**  
  → the country has **latent potential**, but something is blocking growth  
    (macroeconomic instability, shocks, or policy weaknesses).

- **High ψ, high ECI, high growth**  
  → **strong structural performer**: both institutional capacity and export
  sophistication are high and translate into growth.

- **Low ψ, low ECI, low growth**  
  → **structural trap**: low capabilities and low growth reinforce each other.

This tool is **diagnostic, not predictive**.  
It summarises past patterns; it does **not** generate mechanical forecasts.
    """
)
