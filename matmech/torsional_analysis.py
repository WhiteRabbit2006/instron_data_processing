"""
This module provides functions for calculating torsional material properties
for specific geometries, such as solid rectangular cross-sections.
"""

import logging
from typing import Any, Dict

import numpy as np
import pandas as pd

from matmech.constants import (
    ROTATION_COL,
    SHEAR_STRAIN_COL,
    SHEAR_STRESS_MPA_COL,
    SHEAR_STRESS_PA_COL,
    TORQUE_COL,
)


def calculate_torsional_properties_rect(
    df: pd.DataFrame, geometry: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculates Shear Stress and Shear Strain for a solid rectangular cross-section.

    This function assumes the input DataFrame contains 'Rotation (deg)' and 'Torque (N·m)'.
    It adds 'Rotation (rad)', 'Shear Strain (gamma)', 'Shear Stress (tau_Pa)',
    and 'Shear Stress (tau_MPa)' columns to the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        geometry (Dict[str, Any]): A dictionary containing geometry parameters,
                                   e.g., 'torsional_side1_mm', 'torsional_side2_mm',
                                   'gauge_length_mm'.

    Returns:
        pd.DataFrame: The DataFrame with calculated torsional properties.
                      Returns the original DataFrame if critical geometry keys are missing
                      or if a zero denominator is encountered during stress calculation.
    """
    df_processed = df.copy()

    try:
        side1_m = geometry["torsional_side1_mm"] / 1000.0
        side2_m = geometry["torsional_side2_mm"] / 1000.0
        gauge_length_m = geometry["gauge_length_mm"] / 1000.0
    except KeyError as e:
        logging.error(
            f"Could not calculate torsional properties. Missing key in geometry config: {e}"
        )
        return df

    long_side_m, short_side_m = (
        (side1_m, side2_m) if side1_m >= side2_m else (side2_m, side1_m)
    )

    # Calculate alpha factor for rectangular cross-section
    # This formula is an approximation for aspect ratios > 1.
    # For square sections (aspect_ratio = 1), alpha = 0.1406.
    # For very thin sections (aspect_ratio -> inf), alpha -> 1/3.
    if short_side_m == 0:
        logging.error("Short side dimension is zero, cannot calculate torsional properties.")
        return df_processed

    aspect_ratio = long_side_m / short_side_m
    # A common approximation for alpha for rectangular sections
    alpha = (1 / 3) * (1 - 0.630 * (1 / aspect_ratio))

    # Convert rotation to radians
    df_processed["Rotation (rad)"] = np.deg2rad(df_processed[config_defaults.ROTATION_COL])

    # Calculate Shear Strain (gamma)
    # For a rectangular bar, max shear strain occurs at the midpoint of the longer side.
    # The formula used here is a simplified one, often for circular shafts or as an approximation.
    # For rectangular sections, the shear strain distribution is complex.
    # This formula assumes max shear strain at the surface of the shorter side.
    df_processed[config_defaults.SHEAR_STRAIN_COL] = (
        short_side_m * df_processed["Rotation (rad)"]
    ) / gauge_length_m

    # Calculate Shear Stress (tau)
    # The denominator is related to the torsional constant J for a rectangular section.
    # T = G * phi * J / L, where J = alpha * long_side * short_side^3
    # Max shear stress tau_max = T / (alpha * long_side * short_side^2)
    denominator = alpha * long_side_m * (short_side_m**2)
    if denominator == 0:
        logging.warning(
            "Torsional geometry resulted in a zero denominator; shear stress is infinite."
        )
        return df_processed

    df_processed[config_defaults.SHEAR_STRESS_PA_COL] = df_processed[
        config_defaults.TORQUE_COL
    ] / denominator
    df_processed[config_defaults.SHEAR_STRESS_MPA_COL] = (
        df_processed[config_defaults.SHEAR_STRESS_PA_COL] / 1e6
    )

    logging.info("Torsional properties for rectangular cross-section calculated.")
    return df_processed
