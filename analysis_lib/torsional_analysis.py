# analysis_lib/torsional_analysis.py
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any


def calculate_torsional_properties_rect(df: pd.DataFrame, geometry: Dict[str, Any]) -> pd.DataFrame:
	"""
	Calculates Shear Stress and Shear Strain for a solid rectangular cross-section.
	"""
	df_processed = df.copy()

	try:
		side1_m = geometry['torsional_side1_mm'] / 1000.0
		side2_m = geometry['torsional_side2_mm'] / 1000.0
		gauge_length_m = geometry['gauge_length_mm'] / 1000.0
	except KeyError as e:
		logging.error(f"Could not calculate torsional properties. Missing key in geometry config: {e}")
		return df

	long_side_m, short_side_m = (side1_m, side2_m) if side1_m >= side2_m else (side2_m, side1_m)

	aspect_ratio = long_side_m / short_side_m
	alpha = (1 / 3) * (1 - 0.630 * (1 / aspect_ratio))

	df_processed['Rotation (rad)'] = np.deg2rad(df_processed['Rotation (deg)'])
	df_processed['Shear Strain (gamma)'] = (short_side_m * df_processed['Rotation (rad)']) / gauge_length_m

	denominator = alpha * long_side_m * short_side_m ** 2
	if denominator == 0:
		logging.warning("Torsional geometry resulted in a zero denominator; shear stress is infinite.")
		return df_processed

	df_processed['Shear Stress (tau_Pa)'] = df_processed['Torque (N·m)'] / denominator
	df_processed['Shear Stress (tau_MPa)'] = df_processed['Shear Stress (tau_Pa)'] / 1e6

	logging.info("Torsional properties for rectangular cross-section calculated.")
	return df_processed