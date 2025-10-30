# analysis_lib/torsional_analysis.py
import pandas as pd
import numpy as np
import logging


def calculate_torsional_properties_rect(df, geometry):
	"""
	Calculates Shear Stress and Shear Strain for a solid rectangular cross-section.
	Pulls required dimensions from the geometry dictionary. Assumes input DataFrame
	contains standardized 'Torque (N·m)' and 'Rotation (deg)'.

	Args:
		df (pd.DataFrame): The input DataFrame.
		geometry (dict): A dictionary containing geometric properties. Expected keys:
						 'torsional_side1_mm', 'torsional_side2_mm', 'gauge_length_mm'.

	Returns:
		pd.DataFrame: The DataFrame with added torsional properties.
	"""
	df_processed = df.copy()

	try:
		side1_m = geometry['torsional_side1_mm'] / 1000.0
		side2_m = geometry['torsional_side2_mm'] / 1000.0
		gauge_length_m = geometry['gauge_length_mm'] / 1000.0
	except KeyError as e:
		logging.error(f"Could not calculate torsional properties. Missing key in geometry config: {e}")
		return df  # Return original dataframe if geometry is missing

	# Determine long and short sides for the formula
	long_side_m, short_side_m = (side1_m, side2_m) if side1_m >= side2_m else (side2_m, side1_m)

	aspect_ratio = long_side_m / short_side_m
	alpha = (1 / 3) * (1 - 0.630 * (1 / aspect_ratio))  # Approximation for rectangular torsion

	# Calculate Shear Strain (gamma)
	df_processed['Rotation (rad)'] = np.deg2rad(df_processed['Rotation (deg)'])
	df_processed['Shear Strain (gamma)'] = (short_side_m * df_processed['Rotation (rad)']) / gauge_length_m

	# Calculate Shear Stress (tau)
	denominator = alpha * long_side_m * short_side_m ** 2
	if denominator == 0:
		logging.warning("Torsional geometry resulted in a zero denominator; shear stress cannot be calculated.")
		return df_processed

	df_processed['Shear Stress (tau_Pa)'] = df_processed['Torque (N·m)'] / denominator
	df_processed['Shear Stress (tau_MPa)'] = df_processed['Shear Stress (tau_Pa)'] / 1e6

	logging.info("Torsional properties for rectangular cross-section calculated.")
	return df_processed