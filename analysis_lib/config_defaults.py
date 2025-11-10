# analysis_lib/config_defaults.py

from typing import Dict, Any, List, Tuple, Callable
import numpy as np

SOFTWARE_PROFILES: Dict[str, Dict[str, Any]] = {
    'wavematrix': {
        'description': 'Profile for using WaveMatrix testing software.',
        'column_sources': {
            'time':       {'raw_col': 'Total Time (s)', 'raw_units': 's'},
            'position':   {'raw_col': 'Position (mm)', 'raw_units': 'mm'},
            'force':      {'raw_col': 'Force (kN)', 'raw_units': 'kN'},
            'rotation':   {'raw_col': 'Rotation (deg)', 'raw_units': 'deg'},
            'torque':     {'raw_col': 'Torque (N·m)', 'raw_units': 'N·m'}
        },
        'inversion_flags': { 'force': False, 'torque': False }
    },
    'bluehill': {
        'description': 'Profile for using BlueHill testing software.',
        'column_sources': {
            'time':          {'raw_col': 'Time (s)', 'raw_units': 's'},
            'position':      {'raw_col': 'Displacement (mm)', 'raw_units': 'mm'},
            'force':         {'raw_col': 'Force (kN)', 'raw_units': 'kN'},
            'axial_strain':  {'raw_col': 'AVE2 (%)', 'raw_units': 'percent'}
        },
        'inversion_flags': { 'force': False, 'torque': False}
    }
}

DATA_COLUMN_REGISTRY: Dict[str, Dict[str, Any]] = {
    'time': {
        'standard_name': 'Total Time (s)',
        'label': 'Time (s)',
        'default_units': 's',
        'conversions': { 'ms': lambda x: x * 1e3, 'min': lambda x: x / 60 },
        'standardize_from': { 'ms': lambda x: x / 1e3, 'min': lambda x: x * 60 },
        'auto_scale_options': [ (60, 'min'), (1, 's'), (1e-3, 'ms') ]
    },
    'position': {
        'standard_name': 'Displacement (mm)', 'label': 'Displacement (mm)', 'default_units': 'mm',
        'conversions': { 'm': lambda x: x / 1000, 'um': lambda x: x * 1000, 'in': lambda x: x / 25.4 },
        'standardize_from': { 'm': lambda x: x * 1000, 'um': lambda x: x / 1000, 'in': lambda x: x * 25.4 },
        'auto_scale_options': [ (1000, 'm'), (1, 'mm'), (1e-3, 'um') ]
    },
    'displacement': {
        'standard_name': 'Displacement (mm)', 'label': 'Displacement (mm)', 'default_units': 'mm',
        'conversions': { 'm': lambda x: x / 1000, 'um': lambda x: x * 1000, 'in': lambda x: x / 25.4 }
    },
    'force': {
        'standard_name': 'Force (N)', 'label': 'Force (N)', 'default_units': 'N',
        'conversions': { 'kN': lambda x: x / 1000, 'lbf': lambda x: x * 0.224809 },
        'standardize_from': { 'kN': lambda x: x * 1000, 'lbf': lambda x: x * 4.44822 },
        'auto_scale_options': [ (1e3, 'kN'), (1, 'N') ]
    },
    'torque': {
        'standard_name': 'Torque (N·m)', 'label': 'Torque (N·m)', 'default_units': 'N·m',
        'conversions': { 'kN·m': lambda x: x / 1000, 'lbf·in': lambda x: x * 8.85075 },
        'standardize_from': { 'kN·m': lambda x: x * 1000, 'lbf·in': lambda x: x / 0.112985 },
        'auto_scale_options': [(1e3, 'kN·m'), (1, 'N·m')]
    },
    'rotation': {
        'standard_name': 'Rotation (deg)', 'label': 'Rotation (deg)', 'default_units': 'deg',
        'conversions': { 'rad': lambda x: np.deg2rad(x), 'rev': lambda x: x / 360 },
        'standardize_from': { 'rad': lambda x: np.rad2deg(x), 'rev': lambda x: x * 360 },
        'auto_scale_options': [(360, 'rev'), (1, 'deg')]
    },
    'axial_strain': {
        'standard_name': 'Axial Strain', 'label': 'Axial Strain (ε)', 'default_units': 'unitless',
        'conversions': { 'percent': lambda x: x * 100, 'microstrain': lambda x: x * 1e6 },
        'standardize_from': { 'percent': lambda x: x / 100, 'microstrain': lambda x: x / 1e6 }
    },
    'axial_stress': {
        'standard_name': 'Axial Stress (MPa)', 'label': 'Axial Stress (σ) (MPa)', 'default_units': 'MPa',
        'conversions': { 'GPa': lambda x: x / 1000, 'kPa': lambda x: x * 1000, 'psi': lambda x: x * 145.038, 'ksi': lambda x: x * 0.145038 },
        'standardize_from': { 'Pa': lambda x: x / 1e6, 'GPa': lambda x: x * 1000, 'kPa': lambda x: x / 1000, 'psi': lambda x: x / 145.038 },
        'auto_scale_options': [ (1000, 'GPa'), (1, 'MPa'), (1e-3, 'kPa') ]
    },
    'shear_strain': {
        'standard_name': 'Shear Strain (gamma)', 'label': 'Shear Strain (γ)', 'default_units': 'unitless',
        'conversions': { 'percent': lambda x: x * 100 }
    },
    'shear_stress': {
        'standard_name': 'Shear Stress (tau_MPa)', 'label': 'Shear Stress (τ) (MPa)', 'default_units': 'MPa',
        'conversions': { 'GPa': lambda x: x / 1000, 'kPa': lambda x: x * 1000 },
        'auto_scale_options': [ (1000, 'GPa'), (1, 'MPa'), (1e-3, 'kPa') ]
    }
}

DEFAULT_PLOTS: Dict[str, Dict[str, Any]] = {
    # Axial Plots
    'time_position_static': {
        'x_col': 'time', 'y_col': 'position',
        'title': '{phase_name} - Position vs. Time',
        'output_filename': '{phase_name}_position_time_static',
        'phases': ['*'], 'type': 'static'
    },
    'time_position_animated': {
        'x_col': 'time', 'y_col': 'position',
        'title': '{phase_name} - Position vs. Time (Animated)',
        'output_filename': '{phase_name}_position_time_animated',
        'phases': ['*'], 'type': 'animated'
    },
    'force_position_static': {
        'x_col': 'position', 'y_col': 'force',
        'title': '{phase_name} - Force vs. Position',
        'output_filename': '{phase_name}_force_position_static',
        'phases': ['*'], 'type': 'static'
    },
    'force_position_animated': {
        'x_col': 'position', 'y_col': 'force',
        'title': '{phase_name} - Force vs. Position (Animated)',
        'output_filename': '{phase_name}_force_position_animated',
        'phases': ['*'], 'type': 'animated'
    },
    'stress_strain_static': {
        'x_col': 'axial_strain', 'y_col': 'axial_stress',
        'title': '{phase_name} - Axial Stress vs. Axial Strain',
        'output_filename': '{phase_name}_axial_stress_strain_static',
        'phases': ['*'], 'type': 'static',
        'fit_line': True
    },
    'stress_strain_animated': {
        'x_col': 'axial_strain', 'y_col': 'axial_stress',
        'title': '{phase_name} - Axial Stress vs. Axial Strain (Animated)',
        'output_filename': '{phase_name}_axial_stress_strain_animated',
        'phases': ['*'], 'type': 'animated'
    },

    # Torsional Plots
    'time_rotation_static': {
        'x_col': 'time', 'y_col': 'rotation',
        'title': '{phase_name} - Rotation vs. Time',
        'output_filename': '{phase_name}_rotation_time_static',
        'phases': ['*'], 'type': 'static'
    },
    'time_rotation_animated': {
        'x_col': 'time', 'y_col': 'rotation',
        'title': '{phase_name} - Rotation vs. Time (Animated)',
        'output_filename': '{phase_name}_rotation_time_animated',
        'phases': ['*'], 'type': 'animated'
    },
    'torque_rotation_static': {
        'x_col': 'rotation', 'y_col': 'torque',
        'title': '{phase_name} - Torque vs. Rotation',
        'output_filename': '{phase_name}_torque_rotation_static',
        'phases': ['*'], 'type': 'static'
    },
    'torque_rotation_animated': {
        'x_col': 'rotation', 'y_col': 'torque',
        'title': '{phase_name} - Torque vs. Rotation (Animated)',
        'output_filename': '{phase_name}_torque_rotation_animated',
        'phases': ['*'], 'type': 'animated'
    },
    'shear_stress_shear_strain_static': {
        'x_col': 'shear_strain', 'y_col': 'shear_stress',
        'title': '{phase_name} - Shear Stress vs. Shear Strain',
        'output_filename': '{phase_name}_shear_stress_strain_static',
        'phases': ['*'], 'type': 'static',
        'fit_line': True
    },
    'shear_stress_shear_strain_animated': {
        'x_col': 'shear_strain', 'y_col': 'shear_stress',
        'title': '{phase_name} - Shear Stress vs. Shear Strain (Animated)',
        'output_filename': '{phase_name}_shear_stress_strain_animated',
        'phases': ['*'], 'type': 'animated'
    },
}
