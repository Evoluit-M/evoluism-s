import runpy
from pathlib import Path
import streamlit as st

# ---------------------------------------------------------
# HEADER & INTRO TEXT (UX IMPROVED)
# ---------------------------------------------------------

INTRO = r"""
# 📉 *Trends Collide*: Spurious Regression Risk Score  
This interactive tool demonstrates a classic statistical pitfall:  
**two trending time series can produce a strong-looking but completely spurious relationship.**

Upload **two CSV files** (or the same file twice) and choose numeric columns.  
The app will compute:

- Ordinary Least Squares regression  
- Durbin–Watson statistic (autocorrelation test)  
- Newey–West robust standard errors  
- A **0–100% Spurious Risk Score**  
- A diagnostic plot showing why the trend is misleading  

---

## 🧠 What is a spurious regression?

A **spurious regression** occurs when:

- Two variables *trend upward over time*  
- Their correlation and OLS regression look “strong”  
- But the relationship is **not causal**, only **co-trending**

Classic examples:

- GDP vs. global temperature  
- Ice cream sales vs. drowning accidents  
- Education spending vs. height of a population cohort  

This tool helps students, researchers, and analysts detect it instantly.

---

## 📂 Required input format

Each CSV must contain:

- A **time column** (e.g., “year”, “date”, “t”)  
- One or more **numeric columns** to compare  

The files do NOT need identical timestamps — the tool merges data safely.

---

## 🎯 Intended use

This is an **educational diagnostic instrument**, not an econometric model.  
Its purpose is to help users understand:

- why trending data is dangerous in cross-disciplinary research,  
- how false significance arises,  
- how to identify suspicious correlations quickly.

For full reproducibility, code and datasets are available on GitHub.
"""

# ---------------------------------------------------------
# MAIN EXECUTION LOGIC
# ---------------------------------------------------------

def main():
    """Wrapper for automatically launching the real Streamlit app."""

    # Display intro text BEFORE loading underlying script
    st.markdown(INTRO)

    # Candidate paths for
