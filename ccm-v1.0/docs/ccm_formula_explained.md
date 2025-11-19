# CCM formula – additional explanation

This note explains the key formula used in the Cognitive Capital Multiplier
(CCM) calculator.

## 1. From regression to multiplier

The empirical work estimates a log-linear relationship:

\[
\ln(\text{Innovation}_t) = \dots + \beta \cdot C_{t-5\ldots-8} + \varepsilon_t,
\]

where:

- \( \text{Innovation}_t \) is an innovation output indicator
  (patents, high-tech exports),
- \( C_{t-5\ldots-8} \) is a lagged measure of **quality-adjusted cognitive
  capital**, expressed in standard deviations (SD) relative to the 2024
  global mean,
- β is the elasticity of innovation with respect to cognitive capital.

The estimated elasticity is:

\[
\beta \approx 0.69 \quad (95\%~\text{CI}:~0.62\text{–}0.78).
\]

If cognitive capital rises by \( \Delta C \) SD in the long run, the change
in log innovation is approximately:

\[
\Delta \ln(\text{Innovation}) \approx \beta \cdot \Delta C.
\]

Exponentiating both sides yields the multiplicative effect:

\[
\frac{\text{Innovation}_{\text{new}}}{\text{Innovation}_{\text{old}}}
\approx \exp(\beta \cdot \Delta C).
\]

This is the **only mathematically consistent** way to extrapolate a
log-linear regression.

## 2. CCM scenario formula

For a baseline year 2024 and a horizon around 2040, the CCM uses:

\[
\text{Innovation}_{2040} \approx
\text{Innovation}_{2024} \times \exp(\beta \cdot \Delta C).
\]

Where:

- \( \text{Innovation}_{2024} \) is a baseline level (e.g. high-tech exports),
- \( \Delta C = C_{\text{quality}, 2040} - C_{\text{quality}, 2024} \)
  is measured in SD units,
- β is typically set to 0.69, but users can explore the 95% CI band
  0.62–0.78.

Example:

- \( \beta = 0.69 \),
- \( \Delta C = 1.2 \) SD.

Then:

\[
\text{multiplier} = \exp(0.69 \times 1.2) \approx 2.0.
\]

So innovation output roughly doubles relative to the 2024 baseline,
consistent with the main scenarios in the CCM paper.

## 3. Limitations

- The relationship is **correlational**, not strictly causal.
- β is estimated on historical data (2001–2024); applying it to 2040
  assumes a stable elasticity.
- Many other factors (R&D spending, institutions, geopolitics) are not
  explicitly modelled.

Therefore the calculator is best interpreted as a **bounded scenario tool**
rather than as a precise forecast.
