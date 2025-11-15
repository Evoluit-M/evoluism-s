# Interactive Stress-Test App  
"An Interactive Teaching Note on Spurious Regressions"

**Live Demo** → https://trends-collide.streamlit.app  
**Reproducibility** → https://mybinder.org/v2/gh/Evoluit-M/Evoluism-S/data-and-analysis  
**Article DOI** → https://doi.org/10.5281/zenodo.17600821

### Features
- Upload two time series → get **Spurious Risk Score (0–100%)**
- OLS + Durbin–Watson + Newey–West + Mixed models
- ARIMA(1,1,0), fractional integration, structural breaks

### Run locally
```bash
pip install -r app/requirements_app.txt
streamlit run app/streamlit_spurious_test.py
