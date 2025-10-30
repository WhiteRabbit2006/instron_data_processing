# silicone_30a/oct_29_ave2/main.py

import os
import sys

# Find analysis_lib folder
script_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_path, '..', '..', '..'))
sys.path.append(project_root)

from analysis_lib import workflow

# This configuration has been updated to use the new, more robust `column_sources` format.
# Instead of just mapping names, we now specify the raw column name AND its units,
# allowing the workflow to automatically standardize the data.
test_config = {
    'software_type': 'bluehill',
    'data_file_name': 'silicone_30a_20251029_145648_1.csv',

    'test_recipe': [
        {'name': 'axial_pull', 'end_time': 40.0, 'type': 'AXIAL'},
    ],

    'geometry': {
        'gauge_length_mm': 110.0,
        'axial_width_mm': 30.0,
        'axial_thickness_mm': 2.65,
'torsional_side1_mm': 30.0,
        'torsional_side2_mm': 2.65
    },

    'plots': [
        {
            'type': 'static',
            'phases': ['axial_pull'],
            'x_col': 'time',
            'y_col': 'displacement',
            'title': '{y_col} vs. {x_col} for Phase: {phase_name}',
            'output_filename': '{phase_name}_{y_col}_vs_{x_col}'
        },
        {
            'type': 'static',
            'phases': ['axial_pull'],
            'x_col': 'time',
            'y_col': 'force',
            'y_units': 'kN', # Example of plotting with non-standard units
            'title': '{y_col} (kN) vs. {x_col} for Phase: {phase_name}',
            'output_filename': '{phase_name}_{y_col}_vs_{x_col}'
        },
        {
            'type': 'static',
            'phases': ['axial_pull'],
            'x_col': 'displacement',
            'y_col': 'force',
            'title': '{y_col} vs. {x_col} for Phase: {phase_name}',
            'output_filename': '{phase_name}_{y_col}_vs_{x_col}'
        },
        {
            'type': ['static', 'animated'],
            'phases': ['axial_pull'],
            'x_col': 'axial_strain',
            'y_col': 'axial_stress',
            'y_units': 'MPa', # Explicitly request MPa for stress
            'title': 'Stress-Strain Curve for {phase_name}',
            'output_filename': '{phase_name}_Stress_vs_Strain',
            'fit_line': True,
            'fit_bounds': None, # Fits over the whole range
        },
        {
            'type': 'animated',
            'phases': ['axial_pull'],
            'x_col': 'displacement',
            'y_col': 'force',
            'title': 'Animated Force vs. Displacement for {phase_name}',
            'output_filename': '{phase_name}_Force_vs_Disp_Animation'
        }
    ]
}

# Run the program
if __name__ == "__main__":
    workflow.run_analysis_workflow(script_path, test_config)