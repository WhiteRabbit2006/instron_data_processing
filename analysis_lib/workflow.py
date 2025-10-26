# analysis_lib/workflow.py

import os
import pandas as pd
import copy
# noinspection PyPackages
from . import common_utils, axial_analysis, torsional_analysis, plotting_tools, config_defaults


def _resolve_column_info(df, user_key, user_units='auto'):
    if not user_key: raise ValueError("A user key (e.g., 'force', 'time') must be provided.")
    registry_key = user_key.lower()
    if registry_key not in config_defaults.DATA_COLUMN_REGISTRY:
        raise KeyError(f"Data key '{user_key}' not defined in the Data Column Registry.")
    col_info = config_defaults.DATA_COLUMN_REGISTRY[registry_key]
    standard_name = col_info['standard_name']
    if standard_name not in df.columns:
        raise KeyError(f"Required base column '{standard_name}' for '{user_key}' does not exist.")
    if user_units == 'auto':
        chosen_units = col_info['default_units']
        if 'auto_scale_options' in col_info:
            max_val = df[standard_name].abs().max() + 1e-12
            for threshold, unit_str in col_info['auto_scale_options']:
                if max_val / threshold >= 0.1:
                    chosen_units = unit_str
                    break
        user_units = chosen_units
    if user_units and user_units != col_info['default_units']:
        if user_units in col_info['conversions']:
            converted_col_name = f"{standard_name}_to_{user_units}"
            conversion_func = col_info['conversions'][user_units]
            if converted_col_name not in df.columns:
                df[converted_col_name] = conversion_func(df[standard_name])
            column_to_plot = converted_col_name
            axis_label = col_info['label'].replace(f"({col_info['default_units']})", f"({user_units})")
        else:
            raise ValueError(f"Unit conversion '{user_units}' not defined for '{user_key}'.")
    else:
        column_to_plot = standard_name
        axis_label = col_info['label']
    return column_to_plot, axis_label


def run_analysis_workflow(script_path, user_config):
    try:
        # === 1. CONFIGURATION SETUP ===
        # Merge the user's config from main.py with the system defaults.
        final_config = {
            'column_mapping': copy.deepcopy(config_defaults.DEFAULT_COLUMN_MAPPING),
            'inversion_flags': copy.deepcopy(config_defaults.DEFAULT_INVERSION_FLAGS)
        }
        for key, value in user_config.items():
            if isinstance(value, dict):
                final_config.setdefault(key, {}).update(value)
            else:
                final_config[key] = value

        # === 2. PATH AND DIRECTORY SETUP ===
        # Determine where to find data and where to save graphs.
        output_dir = os.path.join(script_path, 'graphs')
        input_file_path = os.path.join(script_path, 'data', final_config['data_file_name'])
        os.makedirs(output_dir, exist_ok=True)

        # === 3. DATA LOADING AND CLEANING ===
        # Load the raw CSV and convert it into a standardized, clean DataFrame.
        full_raw_df = common_utils.load_csv_data(input_file_path)
        clean_df = pd.DataFrame()
        mapping = final_config['column_mapping']
        inversion = final_config['inversion_flags']
        clean_df['Total Time (s)'] = full_raw_df[mapping['Total Time (s)']]
        initial_position = full_raw_df[mapping['Position (mm)']].iloc[0]
        clean_df['Displacement (mm)'] = full_raw_df[mapping['Position (mm)']] - initial_position
        force_multiplier = -1000 if inversion.get('force', False) else 1000
        clean_df['Force (N)'] = full_raw_df[mapping['Force (kN)']] * force_multiplier
        torque_multiplier = -1 if inversion.get('torque', False) else 1
        clean_df['Torque (N·m)'] = full_raw_df[mapping['Torque (N·m)']] * torque_multiplier
        clean_df['Rotation (deg)'] = full_raw_df[mapping['Rotation (deg)']]
        print("Data cleaning, unit conversion, and sign correction complete.")

        # === 4. DATA SEGMENTATION ===
        # Split the single, continuous data file into segments based on the test recipe.
        recipe = final_config['test_recipe']
        split_points = [phase['end_time'] for phase in recipe]
        data_segments = common_utils.split_data_by_time(clean_df, split_points)

        # === 5. PHASE-BY-PHASE ANALYSIS ===
        # Loop through each segment, apply the correct analysis (e.g., axial), and store the result.
        processed_data_store = {}
        for phase, segment_df in zip(recipe, data_segments):
            print(f"\n--- Analyzing Phase: {phase['name']} (Type: {phase['type']}) ---")
            if segment_df.empty:
                processed_data_store[phase['name']] = pd.DataFrame()
                continue
            geo = final_config['geometry']
            if phase['type'] == "AXIAL":
                area_m2 = (geo['axial_width_mm'] / 1000.0) * (geo['axial_thickness_mm'] / 1000.0)
                l_m = geo['gauge_length_mm'] / 1000.0
                processed_df = axial_analysis.calc_ax_prop(segment_df, area_m2, l_m)
            elif phase['type'] == "TORSIONAL":
                side1_m = geo['torsional_side1_mm'] / 1000.0
                side2_m = geo['torsional_side2_mm'] / 1000.0
                l_m = geo['gauge_length_mm'] / 1000.0
                processed_df = torsional_analysis.calc_tor_prop_rect(segment_df, side1_m, side2_m, l_m)
            else:
                processed_df = segment_df
            processed_data_store[phase['name']] = processed_df

        # === 6. PLOT GENERATION ===
        # Iterate through all plot definitions provided by the user in the config.
        plot_configs = final_config.get('plots', [])
        print(f"\n--- Generating {len(plot_configs)} requested plot definition(s) ---")

        for plot_config in plot_configs:
            target_phases = plot_config.get('phases', [])
            for phase_name in target_phases:
                df_to_plot = processed_data_store.get(phase_name) if phase_name != '__full__' else clean_df
                if df_to_plot is None or df_to_plot.empty: continue

                try:
                    # Resolve column names and units using the data registry.
                    x_col_to_plot, x_label = _resolve_column_info(df_to_plot, plot_config['x_col'],
                                                                  plot_config.get('x_units', 'auto'))
                    y_col_to_plot, y_label = _resolve_column_info(df_to_plot, plot_config['y_col'],
                                                                  plot_config.get('y_units', 'auto'))

                    # Allow 'type' to be a list (e.g., ['static', 'animated']) or a single string.
                    plot_types_config = plot_config.get('type', 'static')
                    plot_types = [plot_types_config] if isinstance(plot_types_config, str) else plot_types_config

                    for plot_type in plot_types:
                        plot_type = plot_type.lower()
                        format_keys = plot_config.copy()
                        format_keys['phase_name'] = "Full_Test" if phase_name == '__full__' else phase_name
                        base_filename = plot_config['output_filename'].format(**format_keys)

                        # Determine file suffix based on plot type.
                        suffix = '.mp4' if plot_type == 'animated' else '.png'
                        filename = base_filename + suffix
                        title = plot_config['title'].format(**format_keys)
                        output_file_path = os.path.join(output_dir, filename)

                        # Call the appropriate plotting function.
                        if plot_type == 'animated':
                            plotting_tools.animate_curve(
                                df=df_to_plot, x_col=x_col_to_plot, y_col=y_col_to_plot,
                                title=title, x_label=x_label, y_label=y_label,
                                output_path=output_file_path,
                                target_duration_s=plot_config.get('duration_s', 10),
                                target_fps=plot_config.get('fps', 30),
                                snap_x_to_zero=plot_config.get('snap_x_to_zero', True),
                                snap_y_to_zero=plot_config.get('snap_y_to_zero', True)
                            )
                        else:  # 'static'
                            plotting_tools.plot_curve(
                                df=df_to_plot,
                                x_col_plot=x_col_to_plot, y_col_plot=y_col_to_plot,
                                x_col_base=config_defaults.DATA_COLUMN_REGISTRY[plot_config['x_col'].lower()][
                                    'standard_name'],
                                y_col_base=config_defaults.DATA_COLUMN_REGISTRY[plot_config['y_col'].lower()][
                                    'standard_name'],
                                y_base_units=config_defaults.DATA_COLUMN_REGISTRY[plot_config['y_col'].lower()][
                                    'default_units'],
                                title=title, x_label=x_label, y_label=y_label,
                                output_path=output_file_path,
                                fit_line=plot_config.get('fit_line', False),
                                fit_bounds=plot_config.get('fit_bounds', None),
                                snap_x_to_zero=plot_config.get('snap_x_to_zero', True),
                                snap_y_to_zero=plot_config.get('snap_y_to_zero', True)
                            )
                except (KeyError, ValueError) as e:
                    print(
                        f"  Warning: Skipping plot '{plot_config.get('title', 'Untitled')}' for phase '{phase_name}'. Reason: {e}")

        print(f"\nMulti-phase analysis complete. Graphs saved in '{output_dir}'.")

    except Exception as e:
        print(f"\nAn unexpected error occurred in the workflow: {e}")
