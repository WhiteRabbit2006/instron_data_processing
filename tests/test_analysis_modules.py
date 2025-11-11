# tests/test_analysis_modules.py
"""
Unit tests for the analysis modules (axial_analysis, torsional_analysis).

These tests verify the correctness of property calculations based on
known inputs and expected outputs.
"""

import numpy as np
import pandas as pd

from matmech import axial_analysis, torsional_analysis
from matmech.constants import (
    AXIAL_STRAIN_COL,
    AXIAL_STRESS_MPA_COL,
    FORCE_COL,
    POSITION_COL,
    ROTATION_COL,
    SHEAR_STRAIN_COL,
    TORQUE_COL,
)


def test_calculate_axial_properties():
    """Verify that axial stress and strain are calculated correctly."""
    test_data = {
        POSITION_COL: [0, 0.5, 1.0],
        FORCE_COL: [0, 500, 1000],
    }
    df = pd.DataFrame(test_data)

    geometry = {
        "gauge_length_mm": 100.0,
        "axial_width_mm": 20.0,
        "axial_thickness_mm": 5.0,
    }

    # Expected area = 20mm * 5mm = 100 mm^2 = 0.0001 m^2
    # Expected stress @ 1000N = 1000N / 0.0001m^2 = 10,000,000 Pa = 10 MPa
    # Expected strain @ 1.0mm = 1.0mm / 100mm = 0.01

    result_df = axial_analysis.calculate_axial_properties(df, geometry)

    assert AXIAL_STRAIN_COL in result_df.columns
    assert AXIAL_STRESS_MPA_COL in result_df.columns

    assert np.isclose(result_df[AXIAL_STRAIN_COL].iloc[-1], 0.01)
    assert np.isclose(result_df[AXIAL_STRESS_MPA_COL].iloc[-1], 10.0)


def test_calculate_torsional_properties_rect():
    """Verify that torsional shear stress and strain are calculated correctly."""
    test_data = {
        ROTATION_COL: [0, 45, 90],
        TORQUE_COL: [0, 10, 20],
    }
    df = pd.DataFrame(test_data)

    geometry = {
        "gauge_length_mm": 100.0,
        "torsional_side1_mm": 20.0,  # long side
        "torsional_side2_mm": 10.0,  # short side
    }

    result_df = torsional_analysis.calculate_torsional_properties_rect(df, geometry)

    # Expected rotation @ 90deg = pi/2 radians
    # Expected shear strain @ 90deg = (short_side_m * rad) / L_m
    # = (0.010m * pi/2) / 0.100m = pi/20 = 0.157
    assert SHEAR_STRAIN_COL in result_df.columns
    assert np.isclose(result_df[SHEAR_STRAIN_COL].iloc[-1], np.pi / 20)
