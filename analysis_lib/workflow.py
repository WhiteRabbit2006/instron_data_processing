# analysis_lib/workflow.py

import os
import pandas as pd
import copy
import logging
# noinspection PyPackages
from . import common_utils, axial_analysis, torsional_analysis, plotting_tools, config_defaults


def _resolve_column_info(df, user_key, user_units='auto'):
	"""Resolves user-friendly keys (e.g., 'force') to specific DataFrame columns and plot labels."""
	if not user_key: raise ValueError("A user key (e.g., 'force', 'time') must be provided.")
	registry_key = user_key.lower()
	if registry_key not in config_defaults.DATA_COLUMN_REGISTRY:
		raise KeyError(f"Data key '{user_key}' not defined in the Data Column Registry.")
	col_info = config_defaults.DATA_COLUMN_REGISTRY[registry_key]
	standard_name = col_info['standard_name']
	if standard_name not in df.columns:
		raise KeyError(f"Required base column '{standard_name}' for '{user_key}' does not exist in the DataFrame.")
	if user_units == 'auto':
		chosen_units = col_info['default_units']
		if 'auto_scale_options' in col_info and not df[standard_name].empty:
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
	"""The main entry point for running a complete data analysis workflow."""
	# Configure logging
	logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
	try:
		# === 1. CONFIGURATION SETUP ===
		software_type = user_config.get('software_type', 'legacy_instron')
		logging.info(f"Using software profile: '{software_type}'")

		if software_type not in config_defaults.SOFTWARE_PROFILES:
			raise KeyError(f"Software type '{software_type}' not found in SOFTWARE_PROFILES.")

		base_profile = copy.deepcopy(config_defaults.SOFTWARE_PROFILES[software_type])
		final_config = {**base_profile, **user_config}
		for key, value in user_config.items():
			if isinstance(value, dict) and key in base_profile:
				final_config[key] = {**base_profile[key], **value}

		# === 2. PATH AND DIRECTORY SETUP ===
		output_dir = os.path.join(script_path, 'graphs')
		input_file_path = os.path.join(script_path, 'data', final_config['data_file_name'])
		os.makedirs(output_dir, exist_ok=True)

		# === 3. DATA LOADING AND STANDARDIZATION (CONFIG-DRIVEN) ===
		full_raw_df = common_utils.load_csv_data(input_file_path)
		clean_df = pd.DataFrame()

		sources = final_config.get('column_sources', {})
		inversion_flags = final_config.get('inversion_flags', {})

		for key, source_info in sources.items():
			registry_entry = config_defaults.DATA_COLUMN_REGISTRY[key]
			standard_name = registry_entry['standard_name']
			raw_col = source_info['raw_col']
			raw_units = source_info['raw_units']

			if raw_col not in full_raw_df.columns:
				logging.warning(f"Source column '{raw_col}' for '{key}' not found in data file. Skipping.")
				continue

			series = full_raw_df[raw_col].copy()

			if raw_units != registry_entry['default_units']:
				try:
					convert_func = registry_entry['standardize_from'][raw_units]
					series = convert_func(series)
					logging.info(
						f"Standardized '{key}': converted from '{raw_units}' to '{registry_entry['default_units']}'.")
				except KeyError:
					raise ValueError(
						f"Cannot standardize '{key}': No conversion defined from '{raw_units}' to '{registry_entry['default_units']}'.")

			if inversion_flags.get(key, False):
				series *= -1
				logging.info(f"Applied sign inversion to '{key}'.")

			if key == 'position':
				series = series - series.iloc[0]
				logging.info(f"Standardized 'position': tared to create '{standard_name}'.")

			clean_df[standard_name] = series

		logging.info("Data standardization complete.")

		# === 4. DATA SEGMENTATION ===
		recipe = final_config['test_recipe']
		split_points = [phase['end_time'] for phase in recipe]
		data_segments = common_utils.split_data_by_time(clean_df, split_points)

		# === 5. PHASE-BY-PHASE ANALYSIS ===
		processed_data_store = {}
		for phase, segment_df in zip(recipe, data_segments):
			logging.info(f"\n--- Analyzing Phase: {phase['name']} (Type: {phase['type']}) ---")
			if segment_df.empty:
				logging.warning(f"Segment for phase '{phase['name']}' is empty. Skipping analysis.")
				processed_data_store[phase['name']] = pd.DataFrame()
				continue

			geo = final_config['geometry']
			if phase['type'] == "AXIAL":
				processed_df = axial_analysis.calculate_axial_properties(segment_df, geo)
			elif phase['type'] == "TORSIONAL":
				processed_df = torsional_analysis.calculate_torsional_properties_rect(segment_df, geo)
			else:
				processed_df = segment_df
			processed_data_store[phase['name']] = processed_df

		# === 6. PLOT GENERATION ===
		plot_configs = final_config.get('plots', [])
		logging.info(f"\n--- Generating {len(plot_configs)} requested plot definition(s) ---")

		for plot_config in plot_configs:
			target_phases = plot_config.get('phases', [])
			for phase_name in target_phases:
				df_to_plot = processed_data_store.get(phase_name) if phase_name != '__full__' else clean_df
				if df_to_plot is None or df_to_plot.empty: continue

				try:
					x_col_to_plot, x_label = _resolve_column_info(df_to_plot, plot_config['x_col'],
					                                              plot_config.get('x_units', 'auto'))
					y_col_to_plot, y_label = _resolve_column_info(df_to_plot, plot_config['y_col'],
					                                              plot_config.get('y_units', 'auto'))
					plot_types_config = plot_config.get('type', 'static')
					plot_types = [plot_types_config] if isinstance(plot_types_config, str) else plot_types_config

					for plot_type in plot_types:
						plot_type = plot_type.lower()
						format_keys = plot_config.copy()
						format_keys['phase_name'] = "Full_Test" if phase_name == '__full__' else phase_name
						base_filename = plot_config['output_filename'].format(**format_keys)
						suffix = '.mp4' if plot_type == 'animated' else '.png'
						filename = base_filename + suffix
						title = plot_config['title'].format(**format_keys)
						output_file_path = os.path.join(output_dir, filename)

						if plot_type == 'animated':
							plotting_tools.animate_curve(
								df=df_to_plot, x_col=x_col_to_plot, y_col=y_col_to_plot,
								title=title, x_label=x_label, y_label=y_label,
								output_path=output_file_path,
								target_duration_s=plot_config.get('duration_s', 10),
								target_fps=plot_config.get('fps', 30),
								snap_x_to_zero=plot_config.get('snap_x_to_zero', True),
								snap_y_to_zero=plot_config.get('snap_y_to_zero', True))
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
					logging.warning(
						f"Skipping plot '{plot_config.get('title', 'Untitled')}' for phase '{phase_name}'. Reason: {e}")

		logging.info(f"\nMulti-phase analysis complete. Graphs saved in '{output_dir}'.")

	except Exception as e:
		logging.error(f"An unexpected error occurred in the workflow: {e}", exc_info=True)