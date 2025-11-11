"""
This module provides functions for calculating axial material properties
such as axial stress and axial strain from raw force and displacement data.
"""

import logging
from typing import Any, Dict

import pandas as pd

from matmech.constants import (
    AXIAL_STRAIN_COL,
    AXIAL_STRESS_MPA_COL,
    AXIAL_STRESS_PA_COL,
    FORCE_COL,
    POSITION_COL,
)


def calculate_axial_properties(df: pd.DataFrame, geometry: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculates and adds Axial Stress and/or Axial Strain columns to the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing 'Force (N)' and 'Displacement (mm)'.
        geometry (Dict[str, Any]): A dictionary containing geometry parameters,
                                   e.g., 'axial_width_mm', 'axial_thickness_mm', 'gauge_length_mm'.

    Returns:
        pd.DataFrame: The DataFrame with 'Axial Stress (Pa)', 'Axial Stress (MPa)',
                      and/or 'Axial Strain' columns added.
    """
    df_processed = df.copy()

    # Calculate Axial Stress
    try:
        width_m = geometry["axial_width_mm"] / 1000.0
        thickness_m = geometry["axial_thickness_mm"] / 1000.0
        cross_sectional_area_m2 = width_m * thickness_m

        if cross_sectional_area_m2 == 0:
            logging.error("Cross-sectional area is zero, cannot calculate axial stress.")
        else:
            df_processed[AXIAL_STRESS_PA_COL] = df_processed[
                FORCE_COL
            ] / cross_sectional_area_m2
            df_processed[AXIAL_STRESS_MPA_COL] = (
                df_processed[AXIAL_STRESS_PA_COL] / 1e6
            )
            logging.info("Axial stress calculated.")
    except KeyError:
        logging.warning(
            "Could not calculate axial stress. Required keys 'axial_width_mm' or "
            "'axial_thickness_mm' missing from geometry."
        )

    # Calculate Axial Strain if not already present
    if AXIAL_STRAIN_COL not in df_processed.columns:
        try:
            gauge_length_m = geometry["gauge_length_mm"] / 1000.0
            displacement_m = df_processed[POSITION_COL] / 1000.0
            if gauge_length_m == 0:
                logging.error("Gauge length is zero, cannot calculate axial strain.")
            else:
                df_processed[AXIAL_STRAIN_COL] = (
                    displacement_m / gauge_length_m
                )
                logging.info("Axial strain calculated from displacement.")
        except KeyError:
            logging.warning(
                "Could not calculate axial strain from displacement. 'gauge_length_mm' "
                "missing from geometry."
            )
    else:
        logging.info("Using pre-calculated axial strain found in data.")

    return df_processed
