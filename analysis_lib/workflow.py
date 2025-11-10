# analysis_lib/workflow.py

import os
import pandas as pd
import copy
import logging
from typing import Dict, Any, Callable, Tuple, List
# noinspection PyPackages
from . import common_utils, axial_analysis, torsional_analysis, plotting_tools, config_defaults

# The Analysis Registry: Maps a string from the config to an analysis function.
# This makes the workflow extensible without modification.
ANALYSIS_REGISTRY: Dict[str, Callable[[pd.DataFrame, Dict[str, Any]], pd.DataFrame]] = {
	"AXIAL": axial_analysis.calculate_axial_properties,
	"TORSIONAL": torsional_analysis.calculate_torsional_properties_rect,
}


def _resolve_column_info(df: pd.DataFrame, user_key: str, user_units: str = 'auto') -> Tuple[str, str]:
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
				if max_val >= threshold * 0.1:
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


def run_analysis_workflow(script_path: str, user_config: Dict[str, Any]) -> None:
	"""The main entry point for running a complete data analysis workflow."""
	logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
	try:
		# === 1. CONFIGURATION SETUP ===
		software_type = user_config.get('software_type', 'default')
		logging.info(f"Using software profile: '{software_type}'")
		base_profile = copy.deepcopy(config_defaults.SOFTWARE_PROFILES[software_type])
		final_config = {**base_profile, **user_config}
		for key, value in user_config.items():
			if isinstance(value, dict) and key in base_profile:
				final_config[key] = {**base_profile[key], **value}

		# === 2. PATH AND DIRECTORY SETUP ===
		output_dir = os.path.join(script_path, 'graphs')
		input_file_path = os.path.join(script_path, 'data', final_config['data_file_name'])
		os.makedirs(output_dir, exist_ok=True)

		# === 3. DATA LOADING AND STANDARDIZATION ===
		full_raw_df = common_utils.load_csv_data(input_file_path)
		clean_df = pd.DataFrame()
		sources = final_config.get('column_sources', {})
		inversion_flags = final_config.get('inversion_flags', {})

		tare_options = final_config.get('tare_options', {})

		for key, source_info in sources.items():
			registry_entry = config_defaults.DATA_COLUMN_REGISTRY[key]
			standard_name = registry_entry['standard_name']
			raw_col, raw_units = source_info['raw_col'], source_info['raw_units']
			if raw_col not in full_raw_df.columns:
				logging.warning(f"Source column '{raw_col}' for '{key}' not in data file. Skipping.")
				continue
			series = full_raw_df[raw_col].copy()
			if raw_units != registry_entry['default_units']:
				convert_func = registry_entry['standardize_from'][raw_units]
				series = convert_func(series)
			if inversion_flags.get(key, False): series *= -1
			if tare_options.get(key, False):
				if not series.empty:
					series -= series.iloc[0]
					logging.info(f"Applied taring to '{key}' channel (normalized to start at zero).")
				else:
					logging.warning(f"Attempted to tare '{key}', but the series was empty.")
				# Removed the problematic line: if key == 'position': series -= series.iloc[0]
			clean_df[standard_name] = series
		logging.info("Data standardization complete.")

		# === 4. DATA SEGMENTATION ===
		recipe: List[Dict[str, Any]] = final_config['test_recipe']
		split_points = [phase['end_time'] for phase in recipe]
		
		# Get the standard name for the time column from the registry
		time_standard_name = config_defaults.DATA_COLUMN_REGISTRY['time']['standard_name']
		
		# Defensive check: Ensure the time column exists in clean_df
		if time_standard_name not in clean_df.columns:
			raise KeyError(f"Required time column '{time_standard_name}' not found in processed data. Available columns: {clean_df.columns.tolist()}")

		data_segments = common_utils.split_data_by_time(clean_df, split_points, time_col=time_standard_name)

		# === 5. PHASE-BY-PHASE ANALYSIS (USING REGISTRY) ===
		processed_data_store: Dict[str, pd.DataFrame] = {}
		for phase, segment_df in zip(recipe, data_segments):
			phase_name, analysis_type = phase['name'], phase['type']
			logging.info(f"\n--- Analyzing Phase: {phase_name} (Type: {analysis_type}) ---")
			if segment_df.empty:
				logging.warning(f"Segment for phase '{phase_name}' is empty. Skipping analysis.")
				processed_data_store[phase_name] = pd.DataFrame()
				continue

			if analysis_type in ANALYSIS_REGISTRY:
				analysis_func = ANALYSIS_REGISTRY[analysis_type]
				processed_df = analysis_func(segment_df, final_config['geometry'])
			else:
				logging.info(f"No analysis function registered for type '{analysis_type}'. Passing data through.")
				processed_df = segment_df
			processed_data_store[phase_name] = processed_df

		# === 6. PLOT GENERATION ===
		plot_configs = final_config.get('plots', [])
		logging.info(f"\n--- Generating {len(plot_configs)} requested plot definition(s) ---")
		for plot_config in plot_configs:
			target_phases = plot_config.get('phases', [])
			for phase_name in target_phases:
				df_to_plot = processed_data_store.get(phase_name)
				if df_to_plot is None or df_to_plot.empty:
					logging.warning(
						f"No data available for phase '{phase_name}' to generate plot '{plot_config.get('title', 'Untitled')}'.")
					continue
				try:
					x_col_to_plot, x_label = _resolve_column_info(df_to_plot, plot_config['x_col'],
					                                              plot_config.get('x_units', 'auto'))
					y_col_to_plot, y_label = _resolve_column_info(df_to_plot, plot_config['y_col'],
					                                              plot_config.get('y_units', 'auto'))
					plot_types_config = plot_config.get('type', 'static')
					plot_types = [plot_types_config] if isinstance(plot_types_config, str) else plot_types_config

					for plot_type in plot_types:
						plot_type = plot_type.lower()
						format_keys = {**plot_config, 'phase_name': phase_name}
						base_filename = plot_config['output_filename'].format(**format_keys)
						suffix = '.mp4' if plot_type == 'animated' else '.png'
						filename = base_filename + suffix
						title = plot_config['title'].format(**format_keys)
						output_file_path = os.path.join(output_dir, filename)

						if plot_type == 'animated':
							plotting_tools.animate_curve(
								df=df_to_plot, x_col=x_col_to_plot, y_col=y_col_to_plot, title=title,
								x_label=x_label, y_label=y_label, output_path=output_file_path,
								**plot_config.get('animation_options', {}))
						else:  # 'static'
							plotting_tools.plot_curve(
								df=df_to_plot, x_col_plot=x_col_to_plot, y_col_plot=y_col_to_plot,
								x_col_base=config_defaults.DATA_COLUMN_REGISTRY[plot_config['x_col'].lower()][
									'standard_name'],
								y_col_base=config_defaults.DATA_COLUMN_REGISTRY[plot_config['y_col'].lower()][
									'standard_name'],
								y_base_units=config_defaults.DATA_COLUMN_REGISTRY[plot_config['y_col'].lower()][
									'default_units'],
								title=title, x_label=x_label, y_label=y_label, output_path=output_file_path,
								fit_line=plot_config.get('fit_line', False), fit_bounds=plot_config.get('fit_bounds'))
				except (KeyError, ValueError) as e:
					logging.warning(f"Skipping plot for phase '{phase_name}'. Reason: {e}")
		logging.info(f"\nMulti-phase analysis complete. Graphs saved in '{output_dir}'.")
	except Exception as e:
		logging.error(f"An unexpected error occurred in the workflow: {e}", exc_info=True)
