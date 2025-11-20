import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm


def load_series(file, label: str):
    """
    Load a numeric time series from a CSV file and let the user
    choose which numeric column to use.
    """
    df = pd.read_csv(file)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        raise ValueError(f"No numeric columns found in the {label} file.")

    col = st.selectbox(
        f"Select numeric column for {label}",
        num_cols,
        key=f"col_{label}",
    )
    series = df[col].dropna().astype(float).reset_index(drop=True)
    return series, col


def generate_demo_data(n: int = 40):
    """
    Generate two trending series that are deliberately spurious:
    both follow a random walk with drift and are independent.
    """
    rng = np.random.default_rng(42)
    years = np.arange(1980, 1980 + n)

    eps_y = rng.normal(0, 1, size=n)
    eps_x = rng.normal(0, 1, size=n)

    y = np.cumsum(0.5 + eps_y) + 10.0
    x = np.cumsum(0.4 + eps_x) + 5.0

    df_y = pd.DataFrame({"Year": years, "Demo_Y": y})
    df_x = pd.DataFrame({"Year": years, "Demo_X": x})

    return df_y, df_x


def compute_ols_metrics(y: pd.Series, x: pd.Series):
    """
    Fit OLS regression y_t = a + b x_t + e_t and return model and diagnostics.
    """
    x_const = sm.add_constant(x)
    model = sm.OLS(y, x_const).fit()

    dw = sm.stats.stattools.durbin_watson(model.resid)
    r2 = model.rsquared

    slope_name = x_const.columns[-1]
    pval = float(model.pvalues.get(slope_name, np.nan))

    return model, dw, r2, pval


def compute_risk_score(r2: float, dw: float, pval: float) -> float:
    """
    Compute heuristic 0-100 percent spurious regression risk score.
    """
    r2_part = max(0.0, min(1.0, r2))

    dw_dist = abs(2.0 - dw)
    dw_part = max(0.0, min(1.0, (2.0 - dw_dist) / 2.0))

    if np.isnan(pval):
        p_part = 0.5
    else:
        pval_clipped = max(0.0, min(1.0, float(pval)))
        p_part = 1.0 - min(1.0, pval_clipped / 0.2)

    score = 100.0 * (0.4 * r2_part + 0.3 * dw_part + 0.3 * p_part)
    return float(np.clip(score, 0.0, 100.0))


def main():
    st.set_page_config(
        page_title="Trends Collide – Spurious Regression Risk",
        layout="wide",
    )

    st.title("Trends Collide: Spurious Regression Risk Score")

    st.markdown(
        """
This interactive teaching tool shows how strong-looking relationships
between two trending time series can still be spurious.

It is designed for:

- students learning econometrics,
- researchers working with cross-disciplinary aggregate data,
- policy analysts studying long-run indicators,
- journalists interpreting bold statistical claims.

The tool stress-tests regressions between aggregate indicators using:

- R²,
- Durbin–Watson statistic,
- Newey–West robust p-values,
- and a combined 0-100% Spurious Regression Risk Score.
"""
    )

    st.markdown("---")

    with st.expander("Quick guide – how to use this tool", expanded=True):
        st.markdown(
            """
You need two time-series variables. Examples:

- GDP per capita, high-tech exports, patent counts
- political indices, survey scores
- macroeconomic indicators
- aggregate neuroimaging or cognitive measures

You can either:

1. Use the built-in demo data (recommended for a first try), or
2. Upload your own CSV files.

Each CSV must contain at least one numeric column.

Format example:

Year,Variable
2001, 1.2
2002, 1.4
...
"""
        )

    st.markdown("---")

    st.subheader("Choose data source")

    use_demo = st.checkbox(
        "Use built-in demo data instead of uploading CSV files",
        value=False,
    )

    if use_demo:
        df_y, df_x = generate_demo_data()
        st.markdown("### Demo data (independent trending series)")
        st.dataframe(df_y.head(10))
        st.dataframe(df_x.head(10))

        y = df_y["Demo_Y"]
        x = df_x["Demo_X"]
        y_label = "Demo_Y"
        x_label = "Demo_X"
    else:
        file_y = st.file_uploader(
            "Upload CSV for Y (dependent variable)",
            type=["csv"],
            key="file_y",
        )
        file_x = st.file_uploader(
            "Upload CSV for X (independent variable)",
            type=["csv"],
            key="file_x",
        )

        if file_y is None or file_x is None:
            st.warning("Please upload both CSV files or enable demo mode.")
            return

        y, y_label = load_series(file_y, "Y")
        x, x_label = load_series(file_x, "X")

    st.markdown("---")
    st.subheader("Regression diagnostics")

    model, dw, r2, pval = compute_ols_metrics(y, x)

    st.write("OLS summary:")
    st.text(model.summary().as_text())

    st.markdown(f"- R²: {r2:.3f}")
    st.markdown(f"- Durbin–Watson: {dw:.3f}")
    st.markdown(f"- Newey–West p-value (slope): {pval:.4f}")

    score = compute_risk_score(r2, dw, pval)

    st.markdown(
        f"""
## Spurious Regression Risk Score: {score:.1f}%

Interpretation:

- 80-100% → almost certainly spurious
- 60-80% → highly suspicious
- 40-60% → ambiguous, depends on domain
- 0-40%  → relatively safer
"""
    )

    st.markdown("---")
    st.subheader("Visualisation")

    st.markdown(f"Y series ({y_label})")
    st.line_chart(pd.DataFrame({"Y": y}))

    st.markdown(f"X series ({x_label})")
    st.line_chart(pd.DataFrame({"X": x}))

    st.markdown("---")
    st.markdown(
        """
Reference:

An Interactive Teaching Note on Spurious Regressions in Cross-Disciplinary Aggregate Data  
DOI: https://doi.org/10.5281/zenodo.17600820

This app is part of the Evoluism theoretical-methods series.
"""
    )


if __name__ == "__main__":
    main()
