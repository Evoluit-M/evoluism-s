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


def compute_ols_metrics(y: pd.Series, x: pd.Series):
    """
    Run a simple OLS regression y_t = a + b x_t + e_t
    and return the model plus key diagnostics.
    """
    x_const = sm.add_constant(x)
    model = sm.OLS(y, x_const).fit()

    # Durbin–Watson for residual autocorrelation
    dw = sm.stats.stattools.durbin_watson(model.resid)

    # R-squared and p-value for the slope
    r2 = model.rsquared
    # last column is the slope on X
    slope_name = x_const.columns[-1]
    pval = float(model.pvalues.get(slope_name, np.nan))

    return model, dw, r2, pval


def compute_risk_score(r2: float, dw: float, pval: float) -> float:
    """
    Heuristic 0–100% spurious regression risk score.

    Intuition:
    - high R²  → suspicious if both series trend
    - DW far from 2 (especially close to 0) → strong autocorrelation in residuals
    - very small p-value on the slope → 'too good to be true'

    This is NOT a formal test, just an educational indicator.
    """

    # Part 1: R² (0..1)
    r2_part = max(0.0, min(1.0, r2))

    # Part 2: DW — we want penalty when DW is far from 2 towards 0
    # dw in [0,4], 'good' is near 2; we map "bad" (close to 0) to higher risk
    dw_dist = abs(2.0 - dw)  # 0 if DW=2, up to 2 if DW=0 or 4
    dw_part = max(0.0, min(1.0, (2.0 - dw_dist) / 2.0))  # 1 when DW≈0, 0 when DW≈2

    # Part 3: p-value — small p → high risk (in the spurious context)
    # if p <= 0.01 → p_part≈1; if p>=0.2 → p_part≈0
    pval = float(pval)
    if np.isnan(pval):
        p_part = 0.5  # neutral if we can't compute
    else:
        pval_clipped = max(0.0, min(1.0, pval))
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
This interactive teaching tool illustrates how **strong-looking relationships**
between two trending time series can still be **spurious**.

Upload two CSV files (or the same file twice with different columns),
choose the numeric columns, and the app will:

- fit an OLS regression  \n
  \\( Y_t = \\alpha + \\beta X_t + \\varepsilon_t \\),
- compute **Durbin–Watson** for residual autocorrelation,
- use **Newey–West** robust standard errors for \\(\\beta\\),
- estimate a **0–100% Spurious Risk Score**.
"""
    )

    with st.sidebar:
        st.header("Upload data")
        file_y = st.file_uploader(
            "CSV for Y (dependent variable)",
            type=["csv"],
            key="file_y",
        )
        file_x = st.file_uploader(
            "CSV for X (regressor)",
            type=["csv"],
            key="file_x",
        )

    if not (file_y and file_x):
        st.info("Please upload both CSV files to begin.")
        return

    col_y, col_x = st.columns(2)

    with col_y:
        st.subheader("Y series")
        try:
            y, colname_y = load_series(file_y, "Y")
            st.write(f"Selected column: `{colname_y}`")
            st.line_chart(y)
        except Exception as e:
            st.error(f"Error loading Y series: {e}")
            return

    with col_x:
        st.subheader("X series")
        try:
            x, colname_x = load_series(file_x, "X")
            st.write(f"Selected column: `{colname_x}`")
            st.line_chart(x)
        except Exception as e:
            st.error(f"Error loading X series: {e}")
            return

    n = min(len(y), len(x))
    if n < 10:
        st.error(
            f"Not enough overlapping observations after cleaning (n={n}). "
            "Need at least 10."
        )
        return

    # align lengths
    y = y.iloc[:n]
    x = x.iloc[:n]

    # core regression + classical metrics
    model, dw, r2, pval = compute_ols_metrics(y, x)

    # Newey–West robust SE for beta
    try:
        nlags = int(0.75 * n ** (1 / 3))
        robust = model.get_robustcov_results(
            cov_type="HAC",
            maxlags=max(nlags, 1),
        )
        beta = float(robust.params[1])
        beta_se = float(robust.bse[1])
        beta_p = float(robust.pvalues[1])
    except Exception:
        beta = float(model.params[1])
        beta_se = float(model.bse[1])
        beta_p = float(model.pvalues[1])

    score = compute_risk_score(r2, dw, beta_p)

    st.subheader("Spurious Risk Score")
    st.metric(
        "Risk that the apparent relationship is spurious",
        f"{score:.1f} %",
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Observations", f"{n}")
    col2.metric("R²", f"{r2:.3f}")
    col3.metric("Durbin–Watson", f"{dw:.2f}")
    col4.metric("β p-value (Newey–West)", f"{beta_p:.3g}")

    st.markdown("---")
    st.subheader("OLS summary (classical standard errors)")
    st.text(model.summary().as_text())

    st.markdown(
        """
### Interpretation

- **High score (70–100%)**  
  Very likely driven by shared trends rather than a genuine causal link.
- **Medium score (40–70%)**  
  Ambiguous zone. Investigate further: test for unit roots, cointegration,
  structural breaks, and use proper time-series models.
- **Low score (0–40%)**  
  Less likely to be *purely* spurious, but formal diagnostics are still required.

This app is an **educational stress-test**, not a full econometric workflow.
Use it to build intuition about how misleading trend-based regressions can be,
especially when mixing cross-disciplinary aggregate data.
"""
    )


if __name__ == "__main__":
    main()

