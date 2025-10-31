===============================================
 INSTRON DATA ANALYSIS LIBRARY (README.txt)
===============================================

Overview:
----------
This Python library processes, analyzes, and visualizes cyclical axial and torsional testing
data (e.g., from Instron devices using WaveMatrix or BlueHill software).

It automates the workflow from:
  - Raw CSV import
  - Standardized data cleanup
  - Phase-based analysis
  - Graph generation (static and animated)

Supported functions:
  • Axial Stress–Strain calculations (rectangular cross-sections)
  • Torsional Shear Stress–Strain calculations (rectangular cross-sections)
  • Multi-phase test segmentation by time
  • Plotting with autoscaling, linear fits, and animations


Library Structure:
-------------------
analysis_lib/
│
├── common_utils.py         # Loading and splitting CSV data by time
├── axial_analysis.py       # Calculates axial stress and strain
├── torsional_analysis.py   # Calculates shear stress and strain
├── plotting_tools.py       # Plot and animation generation
├── config_defaults.py      # Software profiles and column registry
└── workflow.py             # Main analysis workflow controller


Requirements:
-------------
Install required packages:
    pip install pandas numpy matplotlib

For animations (.mp4 output):
    sudo apt install ffmpeg


How It Works:
--------------
1. Loads raw CSV data from ./data/
2. Standardizes column names and units (based on selected software profile)
3. Splits data into segments by time (based on test recipe)
4. Applies phase-specific analysis functions (axial or torsional)
5. Generates static and/or animated plots saved to ./graphs/


Example Directory Layout:
--------------------------
project_root/
│
├── data/
│   └── my_test_run.csv
│
├── analysis_lib/
│   └── (library modules...)
│
└── main.py


FULL EXAMPLE: main.py
---------------------

The following example shows ALL available configuration options.

------------------------------------------------------------
import os
from analysis_lib.workflow import run_analysis_workflow

if __name__ == "__main__":
    # Path configuration
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    user_config = {
        # --- Software Profile (choose 'wavematrix' or 'bluehill') ---
        "software_type": "bluehill",

        # --- Input CSV file name (inside ./data) ---
        "data_file_name": "my_test_run.csv",

        # --- Geometry (in millimeters) ---
        "geometry": {
            "axial_width_mm": 10.0,
            "axial_thickness_mm": 2.0,
            "gauge_length_mm": 25.0,
            "torsional_side1_mm": 10.0,
            "torsional_side2_mm": 5.0
        },

        # --- Optional inversion and taring settings ---
        "inversion_flags": {
            "force": False,
            "torque": False
        },
        "tare_options": {
            "position": True,
            "force": True
        },

        # --- Test Phases (with end times in seconds) ---
        "test_recipe": [
            {"name": "Axial Calibration", "end_time": 5.0, "type": "AXIAL"},
            {"name": "Torsion Loading", "end_time": 10.0, "type": "TORSIONAL"}
        ],

        # --- Plot definitions ---
        "plots": [
            # Static plot with fit
            {
                "title": "Axial Stress vs. Axial Strain ({phase_name})",
                "output_filename": "axial_stress_strain_{phase_name}",
                "phases": ["Axial Calibration"],
                "x_col": "axial_strain",
                "y_col": "axial_stress",
                "fit_line": True,
                "fit_bounds": (0.0, 0.002),
                "x_units": "auto",
                "y_units": "auto",
                "type": "static"
            },

            # Animated plot
            {
                "title": "Shear Stress vs. Shear Strain ({phase_name})",
                "output_filename": "shear_stress_strain_{phase_name}",
                "phases": ["Torsion Loading"],
                "x_col": "shear_strain",
                "y_col": "shear_stress",
                "type": "animated",
                "animation_options": {
                    "target_duration_s": 8,
                    "target_fps": 24,
                    "snap_x_to_zero": True,
                    "snap_y_to_zero": True
                }
            }
        ]
    }

    # Run the full workflow
    run_analysis_workflow(SCRIPT_DIR, user_config)
------------------------------------------------------------


Configuration Reference:
-------------------------

Key                  | Type    | Description
-------------------- | ------- | -----------------------------------------------
software_type        | str     | "wavematrix" or "bluehill"
data_file_name       | str     | Name of the CSV file inside ./data/
geometry             | dict    | Required dimensions for calculations
inversion_flags      | dict    | Optional channel sign reversals
tare_options         | dict    | Taring channels to zero at start
test_recipe          | list    | Phases with "name", "end_time", "type"
plots                | list    | One or more plot configs, may include animation
fit_bounds           | tuple   | (x_min, x_max) bounds for linear fitting
animation_options    | dict    | Parameters for animations (fps, duration, etc.)


Output Files:
--------------
All output graphs and videos are written to:
    ./graphs/

Files include:
    *.png  (static plots)
    *.mp4  (animated plots)


Logging:
---------
Progress and analysis info will appear as console logs, including steps such as:
  - File loading
  - Data standardization
  - Axial/Torsional calculations
  - Linear modulus fitting results
  - Plot saving


Example Log Output:
--------------------
INFO: Using software profile: 'bluehill'
INFO: Loading data from: my_test_run.csv
INFO: Axial stress calculated.
INFO: Linear Fit Analysis — Modulus: 1.98 GPa
INFO: Static plot saved to: axial_stress_strain_Axial Calibration.png
INFO: Animation saved: shear_stress_strain_Torsion Loading.mp4


Extending the Library:
-----------------------
To register a new analysis type:

1. Create a new module function:
       def my_new_analysis(df, geometry): ...
2. Add it to the registry in workflow.py:
       ANALYSIS_REGISTRY["NEW_TYPE"] = my_new_analysis
3. Reference it in your test_recipe:
       {"name": "My New Phase", "end_time": 12.0, "type": "NEW_TYPE"}


Notes:
-------
• The data column naming conventions differ between software types.
  The file config_defaults.py defines these profiles for both WaveMatrix and BlueHill.
• Axis units and autoscaling are handled automatically but can be overridden per plot.


License:
---------
Open for research and educational use.
Attribution recommended when used in publications.

===============================================
END OF README.txt
===============================================