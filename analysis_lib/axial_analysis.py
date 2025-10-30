# analysis_lib/axial_analysis.py
import pandas as pd
import logging


def calculate_axial_properties(df, geometry):
	"""
	Calculates and adds Axial Stress and/or Axial Strain columns to the DataFrame.
	Pulls required dimensions from the geometry dictionary.

	Args:
		df (pd.DataFrame): The input DataFrame.
		geometry (dict): A dictionary containing geometric properties of the sample.
						 Expected keys: 'axial_width_mm', 'axial_thickness_mm', 'gauge_length_mm'.

	Returns:
		pd.DataFrame: The DataFrame with added axial properties.
	"""
	df_processed = df.copy()

	# Calculate Axial Stress (sigma)
	try:
		width_m = geometry['axial_width_mm'] / 1000.0
		thickness_m = geometry['axial_thickness_mm'] / 1000.0
		cross_sectional_area_m2 = width_m * thickness_m

		df_processed['Axial Stress (Pa)'] = df_processed['Force (N)'] / cross_sectional_area_m2
		df_processed['Axial Stress (MPa)'] = df_processed['Axial Stress (Pa)'] / 1e6
		logging.info("Axial stress calculated.")
	except KeyError:
		logging.warning("Could not calculate axial stress. Required keys 'axial_width_mm' or "
		                "'axial_thickness_mm' not found in geometry config.")

	# Calculate Axial Strain (epsilon) - only if it doesn't already exist
	if 'Axial Strain' not in df_processed.columns:
		try:
			gauge_length_m = geometry['gauge_length_mm'] / 1000.0
			displacement_m = df_processed['Displacement (mm)'] / 1000
			df_processed['Axial Strain'] = displacement_m / gauge_length_m
			logging.info("Axial strain calculated from displacement.")
		except KeyError:
			logging.warning("Could not calculate axial strain from displacement. Required key "
			                "'gauge_length_mm' not found in geometry config.")
	else:
		logging.info("Using pre-calculated axial strain found in data.")

	return df_processed