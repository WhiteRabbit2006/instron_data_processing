# analysis_lib/torsional_analysis.py
import pandas as pd
import numpy as np


def calc_tor_prop_rect(df, side1_m, side2_m, L_m):
    """
    Calculates and adds Shear Stress and Shear Strain columns for a solid rectangular cross-section.
    Assumes input DataFrame contains raw 'Torque (N·m)' and 'Rotation (deg)'.
    """
    df_processed = df.copy()

    # Determine long and short sides for the formula
    if side1_m >= side2_m:
        long_side_m, short_side_m = side1_m, side2_m
    else:
        long_side_m, short_side_m = side2_m, side1_m

    aspect_ratio = long_side_m / short_side_m
    alpha = (1 / 3) * (1 - 0.630 * (1 / aspect_ratio))

    # Calculate Shear Strain (gamma)
    df_processed['Rotation (rad)'] = df_processed['Rotation (deg)'] * (np.pi / 180)
    df_processed['Shear Strain (gamma)'] = (short_side_m * df_processed['Rotation (rad)']) / L_m

    # Calculate Shear Stress (tau)
    denominator = alpha * long_side_m * short_side_m ** 2
    df_processed['Shear Stress (tau_Pa)'] = df_processed['Torque (N·m)'] / denominator
    df_processed['Shear Stress (tau_MPa)'] = df_processed['Shear Stress (tau_Pa)'] / 1e6

    print("Torsional properties for rectangular cross-section calculated.")
    return df_processed