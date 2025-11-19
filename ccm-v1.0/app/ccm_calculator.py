"""
Core calculations for the Cognitive Capital Multiplier (CCM).

This module is intentionally simple and transparent so that
policymakers, analysts and students can inspect and reuse the logic.

All levels of cognitive capital C are expressed in standard deviations (SD)
relative to the 2024 global mean, consistent with the CCM paper.

Author: Evoluit-M (Evoluism Initiative)
License: MIT
"""

import math
from dataclasses import dataclass


# ---- Basic and quality-adjusted cognitive capital ------------------------


def c_basic(mean_years_schooling: float,
            tertiary_attainment_rate: float) -> float:
    """
    Basic cognitive capital metric C_basic.

    Parameters
    ----------
    mean_years_schooling : float
        Average years of schooling for adults (typically 25–64).
    tertiary_attainment_rate : float
        Share of adults with tertiary education (0–1 or 0–100).

    Notes
    -----
    In the empirical work this metric is later standardised to SD units
    relative to the 2024 global mean. The function here just computes
    the weighted sum; scaling/standardising is left to the user.
    """
    # allow 0–100 or 0–1
    if tertiary_attainment_rate > 1:
        tertiary_attainment_rate = tertiary_attainment_rate / 100.0

    return 0.6 * mean_years_schooling + 0.4 * tertiary_attainment_rate


def c_quality(c_basic_value: float,
              pisa_score: float) -> float:
    """
    Quality-adjusted metric C_quality as used in the paper:

        C_quality = C_basic * (1 + 0.004 * (PISA - 490))

    where 490 is approximately the 2001–2024 global mean PISA score.
    """
    return c_basic_value * (1.0 + 0.004 * (pisa_score - 490.0))


# ---- Exponential CCM formula --------------------------------------------


def innovation_multiplier(beta: float,
                          delta_c: float) -> float:
    """
    Long-run multiplier implied by the log-linear regression:

        Innovation_2040 ≈ Innovation_2024 * exp(beta * ΔC)

    Parameters
    ----------
    beta : float
        Elasticity of innovation with respect to cognitive capital.
        Empirical estimate: beta ≈ 0.69 (95% CI: 0.62–0.78).
    delta_c : float
        Change in C_quality between 2024 and 2040, in SD units.

    Returns
    -------
    float
        Expected multiplicative change in innovation output.
    """
    return math.exp(beta * delta_c)


@dataclass
class ScenarioResult:
    country: str
    c_quality_2024: float
    delta_c: float
    beta: float
    multiplier: float
    patents_2024: float | None = None
    patents_2040: float | None = None
    exports_2024: float | None = None
    exports_2040: float | None = None


def run_scenario(country: str,
                 c_quality_2024: float,
                 delta_c: float,
                 beta: float = 0.69,
                 patents_2024: float | None = None,
                 exports_2024: float | None = None) -> ScenarioResult:
    """
    Convenience wrapper to compute a single CCM scenario.
    """
    m = innovation_multiplier(beta, delta_c)

    patents_2040 = patents_2024 * m if patents_2024 is not None else None
    exports_2040 = exports_2024 * m if exports_2024 is not None else None

    return ScenarioResult(
        country=country,
        c_quality_2024=c_quality_2024,
        delta_c=delta_c,
        beta=beta,
        multiplier=m,
        patents_2024=patents_2024,
        patents_2040=patents_2040,
        exports_2024=exports_2024,
        exports_2040=exports_2040,
    )
