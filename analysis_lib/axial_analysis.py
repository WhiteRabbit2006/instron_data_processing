# analysis_lib/axial_analysis.py
import pandas as pd
import logging
from typing import Dict, Any


def calculate_axial_properties(df: pd.DataFrame, geometry: Dict[str, Any]) -> pd.DataFrame:
	"""
	Calculates and adds Axial Stress and/or Axial Strain columns to the DataFrame.
	"""
	df_processed = df.copy()

	try:
		width_m = geometry['axial_width_mm'] / 1000.0
		thickness_m = geometry['axial_thickness_mm'] / 1000.0
		cross_sectional_area_m2 = width_m * thickness_m

		df_processed['Axial Stress (Pa)'] = df_processed['Force (N)'] / cross_sectional_area_m2
		df_processed['Axial Stress (MPa)'] = df_processed['Axial Stress (Pa)'] / 1e6
		logging.info("Axial stress calculated.")
	except KeyError:
		logging.warning(
			"Could not calculate axial stress. Required keys 'axial_width_mm' or 'axial_thickness_mm' missing from geometry.")

	if 'Axial Strain' not in df_processed.columns:
		try:
			gauge_length_m = geometry['gauge_length_mm'] / 1000.0
			displacement_m = df_processed['Displacement (mm)'] / 1000.0
			df_processed['Axial Strain'] = displacement_m / gauge_length_m
			logging.info("Axial strain calculated from displacement.")
		except KeyError:
			logging.warning(
				"Could not calculate axial strain from displacement. 'gauge_length_mm' missing from geometry.")
	else:
		logging.info("Using pre-calculated axial strain found in data.")

	return df_processed