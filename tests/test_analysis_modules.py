# tests/test_analysis_modules.py

import pandas as pd
import numpy as np
from analysis_lib import axial_analysis, torsional_analysis


def test_calculate_axial_properties():
	"""Verify that axial stress and strain are calculated correctly."""
	test_data = {
		'Displacement (mm)': [0, 0.5, 1.0],
		'Force (N)': [0, 500, 1000]
	}
	df = pd.DataFrame(test_data)

	geometry = {
		'gauge_length_mm': 100.0,
		'axial_width_mm': 20.0,
		'axial_thickness_mm': 5.0
	}

	# Expected area = 20mm * 5mm = 100 mm^2 = 0.0001 m^2
	# Expected stress @ 1000N = 1000N / 0.0001m^2 = 10,000,000 Pa = 10 MPa
	# Expected strain @ 1.0mm = 1.0mm / 100mm = 0.01

	result_df = axial_analysis.calculate_axial_properties(df, geometry)

	assert 'Axial Strain' in result_df.columns
	assert 'Axial Stress (MPa)' in result_df.columns

	assert np.isclose(result_df['Axial Strain'].iloc[-1], 0.01)
	assert np.isclose(result_df['Axial Stress (MPa)'].iloc[-1], 10.0)


def test_calculate_torsional_properties_rect():
	"""Verify that torsional shear stress and strain are calculated correctly."""
	test_data = {
		'Rotation (deg)': [0, 45, 90],
		'Torque (N·m)': [0, 10, 20]
	}
	df = pd.DataFrame(test_data)

	geometry = {
		'gauge_length_mm': 100.0,
		'torsional_side1_mm': 20.0,  # long side
		'torsional_side2_mm': 10.0,  # short side
	}

	result_df = torsional_analysis.calculate_torsional_properties_rect(df, geometry)

	# Expected rotation @ 90deg = pi/2 radians
	# Expected shear strain @ 90deg = (short_side_m * rad) / L_m
	# = (0.010m * pi/2) / 0.100m = pi/20 = 0.157
	assert 'Shear Strain (gamma)' in result_df.columns
	assert np.isclose(result_df['Shear Strain (gamma)'].iloc[-1], np.pi / 20)