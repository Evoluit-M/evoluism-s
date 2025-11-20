import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm


def load_series(file, label: str):
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
    x_const = sm.add_constant(x)
    model = sm.OLS(y, x_const).fit()
    dw = sm.stats.stattools.durbin_watson(model.resid)
    r2 = model.rsquared
    slope_name = x_const.columns[-1]
    pval = float(model.pvalues.get(slope_name, np.nan))
    return model, dw, r2, pval


def compute_risk_score(r2: float, dw: float, pval: float) -> float:
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
"""
    )

    st.markdown("---")

    with st.sidebar:
        st.header("Data options")
        use_demo = st.checkbox(
            "Use built-in demo data (no upload needed)",
            value=True,
        )
        st.markdown("----")
        file_y = None
        file_x = None
        if not use_demo:
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

    if use_demo:
        df_y_demo, df_x_demo = generate_demo_data()
        st.subheader("Demo mode: independent trending series")
        y = df_y_demo["Demo_Y"]
        x = df_x_demo["Demo_X"]
        colname_y = "Demo_Y"
        colname_x = "Demo_X"
    else:
        if not (file_y and file_x):
            st.info("Please upload both CSV files in the sidebar to begin.")
            return
        try:
            y, colname_y = load_series(file_y, "Y")
        except Exception as e:
            st.error(f"Error loading Y series: {e}")
            return
        try:
            x, colname_x = load_series(file_x, "X")
        except Exception as e:
            st.error(f"Error loading X series: {e}")
            return

    n = min(len(y), len(x))
    if n < 10:
        st.error(
            f"Not enough overlapping observations (n={n}). Need at least 10."
        )
        return

    y = y.iloc[:n]
    x = x.iloc[:n]

    st.subheader("Time series overview")
    col_plot1, col_plot2 = st.columns(2)
    with col_plot1:
        st.markdown(f"**Y series (`{colname_y}`)**")
        st.line_chart(y)
    with col_plot2:
        st.markdown(f"**X series (`{colname_x}`)**")
        st.line_chart(x)

    model, dw, r2, pval = compute_ols_metrics(y, x)

    try:
        nlags = int(0.75 * n ** (1 / 3))
        robust = model.get_robustcov_results(
            cov_type="HAC",
            maxlags=max(nlags, 1),
        )
        beta_p = float(robust.pvalues[1])
    except Exception:
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
    st.subheader("OLS summary")
    st.text(model.summary().as_text())


if __name__ == "__main__":
    main()
