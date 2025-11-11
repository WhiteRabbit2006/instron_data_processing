"""
This module defines constants used throughout the matmech library.
"""

# --- Standard Column Name Constants ---
# These constants should be used throughout the codebase when referring to
# the standardized column names in processed DataFrames.
TIME_COL = "Total Time (s)"
POSITION_COL = "Displacement (mm)"
FORCE_COL = "Force (N)"
ROTATION_COL = "Rotation (deg)"
TORQUE_COL = "Torque (N·m)"
AXIAL_STRAIN_COL = "Axial Strain"
AXIAL_STRESS_PA_COL = "Axial Stress (Pa)"
AXIAL_STRESS_MPA_COL = "Axial Stress (MPa)"
SHEAR_STRAIN_COL = "Shear Strain (gamma)"
SHEAR_STRESS_PA_COL = "Shear Stress (tau_Pa)"
SHEAR_STRESS_MPA_COL = "Shear Stress (tau_MPa)"

# --- Default Software Type ---
DEFAULT_SOFTWARE_TYPE = "wavematrix"
