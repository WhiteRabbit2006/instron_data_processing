# oct_22/main.py

import os
import sys

# Find analysis_lib folder
script_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_path, '..', '..'))
sys.path.append(project_root)

from analysis_lib import workflow

test_config = {
    'data_file_name': 'Test7.steps.tracking.csv',

    'test_recipe': [
        {'name': 'axial', 'end_time': 10.0, 'type': 'AXIAL'},
        {'name': 'torsional', 'end_time': 15.0, 'type': 'TORSIONAL'}
    ],

    'geometry': {
        'gauge_length_mm': 57.0,
        'axial_width_mm': 30.0,
        'axial_thickness_mm': 2.65,
        'torsional_side1_mm': 30.0,
        'torsional_side2_mm': 2.65
    },

    'plots': [
        {
            'type': 'static',
            'phases': ['__full__'],
            'x_col': 'time',
            'y_col': 'displacement',
            'title': '{y_col} vs. {x_col}',
            'output_filename': '{phase_name}_{y_col}_{x_col}'
        },
        {
            'type': ['static', 'animated'],
            'phases': ['axial'],
            'x_col': 'axial_strain',
            'y_col': 'axial_stress',
            'title': '{y_col} vs. {x_col}',
            'output_filename': '{phase_name}_{y_col}_{x_col}',
            'fit_line': True,
            'fit_bounds': None,
        },
        {
            'type': 'animated',
            'phases': ['torsional'],
            'x_col': 'shear_strain',
            'y_col': 'shear_stress',
            'title': '{y_col} vs. {x_col}',
            'output_filename': '{phase_name}_{y_col}_{x_col}',
            'fit_line': True,
            'fit_bounds': None
        }
    ]
}

# Run the program
if __name__ == "__main__":
    workflow.run_analysis_workflow(script_path, test_config)