# analysis_lib/config_defaults.py

# This file contains the default configuration settings and the comprehensive data column registry.

# Default mapping for raw column names. Primarily for the legacy data cleaning method.
DEFAULT_COLUMN_MAPPING = {
    'Total Time (s)': 'Total Time (s)',
    'Position (mm)': 'Position (mm)',
    'Force (kN)': 'Force (kN)',
    'Rotation (deg)': 'Rotation (deg)',
    'Torque (N·m)': 'Torque (N·m)'
}

# Default flags for inverting data signs. Primarily for the legacy data cleaning method.
DEFAULT_INVERSION_FLAGS = {
    'force': False,
    'torque': True
}

# --- THE COMPREHENSIVE DATA COLUMN REGISTRY ---
# This is the single source of truth for all known data types in the framework.
# It defines standard names, units, and conversion logic, making the system extensible.
DATA_COLUMN_REGISTRY = {
    # --- Base Columns (Read from raw data) ---
    'time': {
        'standard_name': 'Total Time (s)',      # The internal, standardized column name.
        'label': 'Time (s)',                    # The human-readable label for plots.
        'default_units': 's',                   # The base unit all calculations rely on.
        'conversions': {                        # Functions to convert FROM base units TO other units.
            'ms': lambda x: x * 1e3,
            'min': lambda x: x / 60,
        },
        'auto_scale_options': [                 # Thresholds for automatically selecting a readable unit.
            (60, 'min'), (1, 's'), (1e-3, 'ms')
        ]
    },
    'displacement': {
        'standard_name': 'Displacement (mm)',
        'label': 'Displacement (mm)',
        'default_units': 'mm',
        'conversions': {
            'm': lambda x: x / 1000,
            'um': lambda x: x * 1000,
            'in': lambda x: x / 25.4,
        },
        'auto_scale_options': [
            (1000, 'm'), (1, 'mm'), (1e-3, 'um')
        ]
    },
    'force': {
        'standard_name': 'Force (N)',
        'label': 'Force (N)',
        'default_units': 'N',
        'conversions': {
            'kN': lambda x: x / 1000,
            'lbf': lambda x: x * 0.224809,
        },
        'auto_scale_options': [
            (1e3, 'kN'), (1, 'N')
        ]
    },
    'torque': {
        'standard_name': 'Torque (N·m)',
        'label': 'Torque (N·m)',
        'default_units': 'N·m',
        'conversions': {
            'kN·m': lambda x: x / 1000,
            'lbf·in': lambda x: x * 8.85075,
        },
        'auto_scale_options': [(1e3, 'kN·m'), (1, 'N·m')]
    },
    'rotation': {
        'standard_name': 'Rotation (deg)',
        'label': 'Rotation (deg)',
        'default_units': 'deg',
        'conversions': {
            'rad': lambda x: x * (3.14159 / 180.0),
            'rev': lambda x: x / 360
        },
        'auto_scale_options': [(360, 'rev'), (1, 'deg')]
    },
    # --- Calculated Columns (Derived from base columns) ---
    'axial_strain': {
        'standard_name': 'Axial Strain',
        'label': 'Axial Strain (ε)',
        'default_units': 'unitless',
        'conversions': {
            'percent': lambda x: x * 100,
            'microstrain': lambda x: x * 1e6
        }
    },
    'axial_stress': {
        'standard_name': 'Axial Stress (MPa)',
        'label': 'Axial Stress (σ) (MPa)',
        'default_units': 'MPa',
        'conversions': {
            'GPa': lambda x: x / 1000,
            'kPa': lambda x: x * 1000,
            'psi': lambda x: x * 145.038,
            'ksi': lambda x: x * 0.145038
        },
        'auto_scale_options': [
            (1000, 'GPa'), (1, 'MPa'), (1e-3, 'kPa')
        ]
    },
    'shear_strain': {
        'standard_name': 'Shear Strain (gamma)',
        'label': 'Shear Strain (γ)',
        'default_units': 'unitless',
        'conversions': {
            'percent': lambda x: x * 100,
        }
    },
    'shear_stress': {
        'standard_name': 'Shear Stress (tau_MPa)',
        'label': 'Shear Stress (τ) (MPa)',
        'default_units': 'MPa',
        'conversions': {
            'GPa': lambda x: x / 1000,
            'kPa': lambda x: x * 1000,
        },
        'auto_scale_options': [
            (1000, 'GPa'), (1, 'MPa'), (1e-3, 'kPa')
        ]
    }
}