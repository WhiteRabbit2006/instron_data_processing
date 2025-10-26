Mechanical Testing Analysis Library - Quickstart Guide
======================================================

This is a Python framework for automating the analysis of mechanical testing data. It processes raw CSV files from multiphase experiments (e.g., axial then torsional) to calculate material properties and generate plots and animations.


How to Use
----------
The entire analysis is controlled by a single configuration file. You do not need to edit the library code.

**1. Set up your folder:**
   Create a test folder containing:
   - A `data/` subfolder with your raw `.csv` file.
   - A `main.py` file.

**2. Configure `main.py`:**
   Edit the `test_config` dictionary in `main.py` to describe your test. A complete example is provided below.

**3. Run the script:**
   From your terminal, navigate to the test folder and run `python main.py`. Results will appear in a new `graphs/` folder.


Example `main.py` Configuration
--------------------------------
```python
# main.py

import os
import sys
# This block allows the script to find the 'analysis_lib' folder
script_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_path, '..', '..'))
sys.path.append(project_root)
from analysis_lib import workflow

# --- All user settings go in this dictionary ---
test_config = {
    # The name of your raw data file in the `data/` folder.
    'data_file_name': 'Test7.steps.tracking.csv',

    # Defines the sequence of experimental phases.
    'test_recipe': [
        {'name': 'axial_compression', 'end_time': 10.0, 'type': 'AXIAL'},
        {'name': 'torsional_twist', 'end_time': 15.0, 'type': 'TORSIONAL'}
    ],

    # All necessary sample dimensions in millimeters.
    'geometry': {
        'gauge_length_mm': 57.0,
        'axial_width_mm': 30.0,
        'axial_thickness_mm': 2.65,
        'torsional_side1_mm': 30.0,
        'torsional_side2_mm': 2.65
    },

    # A list of all plots to generate.
    'plots': [
        {
            'type': ['static', 'animated'],      # Generate both a .png and .mp4
            'phases': ['axial_compression'],     # Which phase to plot data from
            'x_col': 'axial_strain',
            'y_col': 'axial_stress',
            'title': '{y_col} vs. {x_col}',
            'output_filename': '{phase_name}_{y_col}_{x_col}',
            'fit_line': True,                    # Perform a linear regression
            'snap_y_to_zero': False,             # "Zoom in" on the y-axis if data is far from zero
        }
    ]
}

if __name__ == "__main__":
    workflow.run_analysis_workflow(script_path, test_config)