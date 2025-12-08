import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ------------------------------------------------------------
# Streamlit App: Global Explorer — ψ & ECI
# Based on the paper:
# “ψ vs ECI: Cognitive–Institutional Capacity and Export Complexity
#  as Predictors of Long-Run Growth”
#  Zenodo DOI (placeholder): 10.5281/zenodo.XXXXXXX
# ------------------------------------------------------------

st.set_page_config(
    page_title="Global Explorer — ψ & ECI",
    layout="wide"
)

# ------------------------------------------------------------
# Load the dataset
# ------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/processed/growth_panel_psi_eci_10y_v1_2.csv")
    return df

df = load_data()

df["psi_z"] = (df["psi"] - df["psi"].mean()) / df["psi"].std()
df["eci_z"] = (df["eci"] - df["eci"].mean()) / df["eci"].std()

countries = sorted(df["iso3"].unique())

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
st.sidebar.header("Controls")

y0_min = int(df["y0"].min())
y0_max = int(df["y0"].max())

y0_choice = st.sidebar.slider(
    "Initial 10-year window (start year)",
    min_value=y0_min,
    max_value=y0_max,
    value=2000
)

country_focus = st.sidebar.selectbox(
    "Focus country (ISO3)",
    countries,
    index=countries.index("ARG") if "ARG" in countries else 0
)

x_metric = st.sidebar.selectbox(
    "X-axis metric",
    ["psi_z", "eci_z"],
    format_func=lambda x: "ψ (cognitive index)" if x == "psi_z" else "ECI (export complexity)"
)

# Filter selected window
df_window = df[df["y0"] == y0_choice]

# ------------------------------------------------------------
# Title and description
# ------------------------------------------------------------
st.title("Global Explorer — ψ & ECI")

st.markdown(
    """
This interactive page provides a **global view** of how countries perform in terms of:

- **ψ (cognitive–institutional capacity)**  
- **ECI (export complexity)**  
- **10-year GDP per capita growth**

based on the paper:  
**“ψ vs ECI: Cognitive–Institutional Capacity and Export Complexity as Predictors of Long-Run Growth”**  
Zenodo DOI: *10.5281/zenodo.17808798*
"""
)

# ------------------------------------------------------------
# How-to example with Argentina
# ------------------------------------------------------------
st.markdown(
    """
## How to use this app (example: Argentina, ARG)

Suppose a **user** wants to analyse **Argentina (ARG)** and see how it compares
to other countries:

1. Open the **sidebar**.  
2. Set the **start year** (e.g., 2000).  
   This corresponds to a growth window **2000 → 2010**.  
3. In **“Focus country (ISO3)”**, choose **ARG**.  
4. Choose what to place on the X-axis:
   - **ψ (cognitive index)**  
   - **ECI (export complexity)**

The app will display:

- **Global statistics** for that 10-year window  
- A **scatterplot** of all countries (each dot is a country-window)  
- The focus country highlighted  
- Simple interpretation guidelines so that any user
  (including policymakers or researchers) can understand
  the meaning of the country’s position.
"""
)

# ------------------------------------------------------------
# Global statistics for this window
# ------------------------------------------------------------
st.subheader(f"Global summary for window starting in {y0_choice}")

avg_growth = df_window["gdp_growth"].mean()
corr_psi = df_window["gdp_growth"].corr(df_window["psi_z"])
corr_eci = df_window["gdp_growth"].corr(df_window["eci_z"])

col1, col2, col3 = st.columns(3)
col1.metric("Avg 10-year growth (%)", f"{avg_growth:.2f}")
col2.metric("Corr(growth, ψ)", f"{corr_psi:.2f}")
col3.metric("Corr(growth, ECI)", f"{corr_eci:.2f}")

# ------------------------------------------------------------
# Scatterplot
# ------------------------------------------------------------
st.subheader("Global scatterplot")

highlight = alt.selection_point(fields=["iso3"], value=country_focus)

scatter = (
    alt.Chart(df_window)
    .mark_circle(size=60)
    .encode(
        x=alt.X(x_metric, title="ψ (z-score)" if x_metric == "psi_z" else "ECI (z-score)"),
        y=alt.Y("gdp_growth", title="10-year GDPpc growth (%)"),
        opacity=alt.condition(highlight, alt.value(1.0), alt.value(0.2)),
        color=alt.condition(highlight, alt.value("red"), alt.value("steelblue")),
        tooltip=["iso3", "y0", "y1", x_metric, "gdp_growth"]
    )
    .add_params(highlight)
    .properties(height=400)
)

st.altair_chart(scatter, use_container_width=True)

# ------------------------------------------------------------
# Interpretation block
# ------------------------------------------------------------
st.markdown(
    f"""
## How to interpret the position of {country_focus}

- If {country_focus} is **above** the global cloud →  
  **Growing faster** than what its ψ/ECI suggest.

- If {country_focus} is **below** the cloud →  
  **Underperforming** relative to structural capabilities.

- If {country_focus} has **high ψ_z and high ECI_z** →  
  Strong structural base (institutions + complex exports).

- If both ψ_z and ECI_z are **low** →  
  Potential structural trap.

- If ψ_z is **high** but growth is **low** →  
  Capabilities exist, but something is blocking growth  
  (instability, shocks, macro constraints).

This tool is **diagnostic**, not predictive —  
it summarises structural potential and realised growth.
"""
)

# ------------------------------------------------------------
# Show filtered window
# ------------------------------------------------------------
st.subheader("All countries in this 10-year window")

st.dataframe(
    df_window[
        ["iso3", "y0", "y1", "gdp_growth", "psi", "psi_z", "eci", "eci_z"]
    ].sort_values("gdp_growth", ascending=False)
)
