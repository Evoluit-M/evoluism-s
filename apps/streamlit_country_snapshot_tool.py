import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# Title + About
# ============================================================

st.title("Quick Country Snapshot — ψ and ECI (10-year Growth)")

st.markdown(
    """
This mini-app provides a **quick diagnostic snapshot** for a single country and a
single 10-year window, based on the same panel used in the article:

> **“ψ vs ECI: Cognitive–Institutional Capacity and Export Complexity  
> as Predictors of Long-Run Growth”**  
> Evoluit-M (2025)  
> Zenodo DOI: **10.5281/zenodo.XXXXXXX** (placeholder)

Data source used here (within the repository):

`data/processed/growth_panel_psi_eci_10y_v1_2.csv`
"""
)

st.divider()

# ============================================================
# Data loading (robust to column name variants)
# ============================================================

@st.cache_data
def load_panel() -> pd.DataFrame:
    """
    Load the 10-year growth panel used in the paper.

    We try to be robust to slightly different column names:
    - growth_10y, g_10y, g_10y_ann, growth10, growth_annual_10y, g_10
    - ECI or eci
    - psi or psi_ng (we standardize and call it psi_z)
    - y0,y1 or close variants
    """
    df = pd.read_csv("data/processed/growth_panel_psi_eci_10y_v1_2.csv")

    # handy mapping: lowercase -> original name
    colmap = {c.lower(): c for c in df.columns}

    # --- Country identifier (ISO3) ---
    iso_col = None
    for cand in ["iso3", "country_iso3", "iso3c", "iso_code"]:
        if cand in colmap:
            iso_col = colmap[cand]
            break

    if iso_col is None:
        st.error(
            "Cannot find ISO3 column. Expected one of: "
            "'iso3', 'country_iso3', 'iso3c', 'iso_code'.\n\n"
            f"Available columns: {list(df.columns)}"
        )
        st.stop()

    df["iso3"] = df[iso_col].astype(str)

    # Country name (optional; for nicer display)
    if "country" not in df.columns and "country_name" in colmap:
        df["country"] = df[colmap["country_name"]]

    # --- 10-year window start/end years ---
    y0_col = None
    y1_col = None

    for cand in ["y0", "start_year", "year0"]:
        if cand in colmap:
            y0_col = colmap[cand]
            break
    for cand in ["y1", "end_year", "year1"]:
        if cand in colmap:
            y1_col = colmap[cand]
            break

    if y0_col is None or y1_col is None:
        st.error(
            "The panel must contain starting/ending year columns for 10-year windows "
            "(e.g. 'y0'/'y1', 'start_year'/'end_year').\n\n"
            f"Available columns: {list(df.columns)}"
        )
        st.stop()

    df["y0"] = df[y0_col].astype(int)
    df["y1"] = df[y1_col].astype(int)

    # --- 10-year growth column ---
    growth_col = None
    growth_candidates = [
        "growth_10y",
        "g_10y",
        "g_10y_ann",
        "growth10",
        "growth_annual_10y",
        "g_10",
    ]
    for cand in growth_candidates:
        if cand in colmap:
            growth_col = colmap[cand]
            break

    # fallback: any column containing "growth"
    if growth_col is None:
        for c in df.columns:
            if "growth" in c.lower():
                growth_col = c
                break

    if growth_col is None:
        st.error(
            "Cannot find 10-year growth column.\n\n"
            "Expected one of: "
            "'growth_10y', 'g_10y', 'g_10y_ann', 'growth10', 'growth_annual_10y', 'g_10', "
            "or any column containing the word 'growth'.\n\n"
            f"Available columns: {list(df.columns)}"
        )
        st.stop()

    df["growth_10y"] = df[growth_col]

    # --- ψ / ψ_ng column ---
    # First try "psi_ng*", then fall back to "psi*"
    psi_col = None

    # psi_ng variants
    for cand in ["psi_ng", "psi_ng_std", "psi_ng_z"]:
        if cand in colmap:
            psi_col = colmap[cand]
            break

    # if no psi_ng, look for psi variants (your case: 'psi')
    if psi_col is None:
        for cand in ["psi", "psi_std", "psi_z"]:
            if cand in colmap:
                psi_col = colmap[cand]
                break

    if psi_col is None:
        st.error(
            "Cannot find ψ column. Expected one of: "
            "'psi_ng', 'psi_ng_std', 'psi_ng_z', 'psi', 'psi_std', 'psi_z'.\n\n"
            f"Available columns: {list(df.columns)}"
        )
        st.stop()

    # --- ECI column ---
    eci_col = None
    for cand in ["eci", "eci_std", "eci_z"]:
        if cand in colmap:
            eci_col = colmap[cand]
            break
    if "ECI" in df.columns and eci_col is None:
        eci_col = "ECI"

    if eci_col is None:
        st.error(
            "Cannot find ECI column. Expected one of: "
            "'eci', 'ECI', 'eci_std', 'eci_z'.\n\n"
            f"Available columns: {list(df.columns)}"
        )
        st.stop()

    # --- Standardized versions (z-scores) ---
    if "psi_z" not in df.columns:
        df["psi_z"] = (df[psi_col] - df[psi_col].mean()) / df[psi_col].std(ddof=0)

    if "eci_z" not in df.columns:
        df["eci_z"] = (df[eci_col] - df[eci_col].mean()) / df[eci_col].std(ddof=0)

    # Canonical raw copies
    df["_psi_raw"] = df[psi_col]
    df["_eci_raw"] = df[eci_col]

    return df


df = load_panel()

# ============================================================
# Sidebar controls (need mapping before dialog for nicer names)
# ============================================================

iso3_list = sorted(df["iso3"].unique())
iso3_to_name = dict(
    zip(
        df["iso3"],
        df.get("country", df["iso3"])  # fall back to iso3 if no 'country' col
    )
)

st.sidebar.header("Controls")

selected_iso3 = st.sidebar.selectbox(
    "Target country (ISO3)",
    options=iso3_list,
    # убираем дубли: если name == iso3, показываем просто код
    format_func=lambda x: iso3_to_name.get(x, x)
)

years_available = sorted(df["y0"].unique())
min_y0, max_y0 = int(min(years_available)), int(max(years_available))

selected_y0 = st.sidebar.slider(
    "Initial 10-year period (starting year)",
    min_value=min_y0,
    max_value=max_y0,
    value=min_y0,
    step=1,
    help="This corresponds to growth between y0 and y0+10."
)

st.markdown(
    """
**How to use this app (example with ARG / Argentina):**

1. Open the sidebar (top-left icon).
2. In **“Target country (ISO3)”**, choose `ARG`.
3. In **“Initial 10-year period (starting year)”**, choose `2000`.
   - This corresponds to growth between **2000 and 2010**.
4. As soon as both choices are made, a dialog will pop up with a **quick diagnostic snapshot**:
   - 10-year average growth vs world average;
   - ψ (z-score) vs world;
   - ECI (z-score) vs world;
   - short verbal interpretation.
"""
)

# ============================================================
# Quick country snapshot dialog
# ============================================================

@st.dialog("Quick country snapshot for the selected 10-year window")
def show_country_snapshot(row: pd.Series, global_slice: pd.DataFrame) -> None:
    """
    Modal dialog that gives a quick verbal summary for the chosen country
    and 10-year window.
    """
    iso3 = row["iso3"]
    display_country = iso3_to_name.get(iso3, iso3)
    y0 = int(row["y0"])
    y1 = int(row["y1"])

    # Global averages for this window
    g_world_mean = global_slice["growth_10y"].mean()
    psi_world_mean = global_slice["psi_z"].mean()
    eci_world_mean = global_slice["eci_z"].mean()

    # Country values
    g_c = row["growth_10y"]
    psi_c = row["psi_z"]
    eci_c = row["eci_z"]

    st.markdown(f"### {display_country} ({iso3}): 10-year window {y0}–{y1}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "10-year avg. growth (GDP per capita, %/year)",
            f"{g_c * 100:.2f}",
            delta=f"vs world avg: {(g_c - g_world_mean) * 100:.2f} pp"
        )
    with col2:
        st.metric(
            "ψ (z-score)",
            f"{psi_c:.2f}",
            delta=f"vs world mean: {psi_c - psi_world_mean:.2f}"
        )
    with col3:
        st.metric(
            "ECI (z-score)",
            f"{eci_c:.2f}",
            delta=f"vs world mean: {eci_c - eci_world_mean:.2f}"
        )

    st.divider()

    # --- Simple verbal categories ---

    if g_c > g_world_mean + 0.005:
        growth_msg = "The country is growing **faster** than the global average in this 10-year window."
    elif g_c < g_world_mean - 0.005:
        growth_msg = "The country is growing **slower** than the global average in this 10-year window."
    else:
        growth_msg = "The country’s growth is **close to** the global average in this 10-year window."

    def z_level(z: float) -> str:
        if z >= 1.0:
            return "is **high** (more than 1 standard deviation above the global mean)."
        elif z <= -1.0:
            return "is **low** (more than 1 standard deviation below the global mean)."
        else:
            return "is in the **medium range** (roughly around the global mean)."

    psi_msg = z_level(psi_c)
    eci_msg = z_level(eci_c)

    st.markdown("#### Interpretation in plain language")

    st.markdown(
        f"""
- **Growth:** {growth_msg}
- **Cognitive–institutional capacity (ψ):** ψ {psi_msg}
- **Export sophistication (ECI):** ECI {eci_msg}
"""
    )

    st.markdown(
        """
**How to read this:**

- If growth is **high but ψ is low**, the country may be in a catch-up phase:
  growth is driven by convergence, while deeper institutional capacity is still building.

- If ψ is **high but growth is low**, the country has a strong cognitive–institutional base,
  but something is blocking the translation into growth (e.g. macro instability, shocks, policy uncertainty).

- If both ψ and ECI are **high and growth is high**, the country is effectively
  converting structural capabilities into long-run income gains.

- If both ψ and ECI are **low and growth is low**, the country may be stuck in a
  structural trap and needs both institutional upgrading and diversification of its export basket.
"""
    )

# ============================================================
# Filter data and show snapshot
# ============================================================

# Subset: all countries for the chosen start year
df_window = df[df["y0"] == selected_y0].copy()
if df_window.empty:
    st.warning(f"No observations found for starting year y0 = {selected_y0}.")
else:
    # Row for the selected country in this window
    country_row = df_window[df_window["iso3"] == selected_iso3]

    if not country_row.empty:
        row = country_row.iloc[0]
        # Automatically show the dialog
        show_country_snapshot(row, df_window)

        st.markdown(
            f"""
Below is the **raw data** for {iso3_to_name.get(selected_iso3, selected_iso3)}
in the selected 10-year window {int(row['y0'])}–{int(row['y1'])}:
"""
        )

        cols_to_show = [
            "iso3",
            "country" if "country" in row.index else None,
            "y0",
            "y1",
            "growth_10y",
            "_psi_raw",
            "psi_z",
            "_eci_raw",
            "eci_z",
        ]
        cols_to_show = [c for c in cols_to_show if c is not None]

        st.dataframe(
            country_row[cols_to_show].rename(
                columns={
                    "iso3": "ISO3",
                    "country": "Country",
                    "y0": "Start year",
                    "y1": "End year",
                    "growth_10y": "10-year growth (per year)",
                    "_psi_raw": "ψ (raw)",
                    "psi_z": "ψ (z-score)",
                    "_eci_raw": "ECI (raw)",
                    "eci_z": "ECI (z-score)",
                }
            ),
            use_container_width=True,
        )
    else:
        st.warning(
            f"Selected country {selected_iso3} has no data for the window starting {selected_y0}."
        )
