# analysis_lib/plotting_tools.py

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import logging
import pandas as pd
from typing import Tuple, Optional, List, Dict, Any


def _calculate_axis_limits(data_series: pd.Series, snap_to_zero: bool = True) -> Tuple[float, float]:
	"""Calculates robust axis limits with padding."""
	if data_series.empty: return 0, 1
	data_min, data_max = data_series.min(), data_series.max()
	if data_min == data_max: return data_min - 0.1, data_max + 0.1

	padding = (data_max - data_min) * 0.05
	lower_lim, upper_lim = data_min - padding, data_max + padding

	if snap_to_zero:
		if data_min >= 0: lower_lim = 0
		if data_max <= 0: upper_lim = 0
	return lower_lim, upper_lim


def calculate_linear_fit(
		df: pd.DataFrame,
		x_col_base: str,
		y_col_base: str,
		y_base_units: str,
		fit_bounds: Optional[Tuple[float, float]] = None
) -> Dict[str, Any]:
	"""
	Performs a linear fit on specified data columns and returns the results.
	Separated from plotting to be reusable.
	"""
	fit_df = df.copy()
	if fit_bounds is not None and len(fit_bounds) == 2:
		lower, upper = sorted(fit_bounds)
		mask = (fit_df[x_col_base] >= lower) & (fit_df[x_col_base] <= upper)
		fit_df = fit_df.loc[mask]

	if len(fit_df) < 2:
		return {}  # Not enough data to fit

	m_base, b_base = np.polyfit(fit_df[x_col_base], fit_df[y_col_base], 1)

	modulus_val = m_base
	modulus_units = y_base_units
	if y_base_units == 'MPa':
		if abs(modulus_val) >= 1000:
			modulus_val /= 1000
			modulus_units = 'GPa'
		elif abs(modulus_val) < 1 and modulus_val != 0:
			modulus_val *= 1000
			modulus_units = 'kPa'

	return {
		"modulus_val": modulus_val,
		"modulus_units": modulus_units,
		"y_intercept": b_base,
		"x_intercept": -b_base / m_base if m_base != 0 else float('inf'),
	}


def plot_curve(
		df: pd.DataFrame, x_col_plot: str, y_col_plot: str, x_col_base: str, y_col_base: str,
		y_base_units: str, title: str, x_label: str, y_label: str, output_path: str,
		fit_line: bool = False, fit_bounds: Optional[Tuple[float, float]] = None,
		snap_x_to_zero: bool = True, snap_y_to_zero: bool = True
) -> None:
	"""Generates a static plot and performs linear analysis via a helper function."""
	fig, ax = plt.subplots(figsize=(10, 7))
	ax.plot(df[x_col_plot], df[y_col_plot], label='Experimental Data')

	if fit_line:
		fit_results = calculate_linear_fit(df, x_col_base, y_col_base, y_base_units, fit_bounds)
		if fit_results:
			logging.info("\n--- Linear Fit Analysis (in Standard Units) ---")
			logging.info(f"Calculated Modulus: {fit_results['modulus_val']:.3f} {fit_results['modulus_units']}")
			logging.info(f"Y-Intercept: {fit_results['y_intercept']:.4f} {y_base_units}")
			logging.info(f"X-Intercept: {fit_results['x_intercept']:.5f}")
			logging.info("-------------------------------------------------")

			fit_df = df.copy()
			if fit_bounds:
				mask = (fit_df[x_col_plot] >= fit_bounds[0]) & (fit_df[x_col_plot] <= fit_bounds[1])
				fit_df = fit_df.loc[mask]

			m_plot, b_plot = np.polyfit(fit_df[x_col_plot], fit_df[y_col_plot], 1)
			fit_x_vals = np.array([fit_df[x_col_plot].min(), fit_df[x_col_plot].max()])
			fit_y_vals = m_plot * fit_x_vals + b_plot
			fit_label = (
				f"Linear Fit\n"
				f"Modulus: {fit_results['modulus_val']:.2f} {fit_results['modulus_units']}\n"
				f"Y-Intercept: {fit_results['y_intercept']:.3f} {y_base_units}"
			)
			ax.plot(fit_x_vals, fit_y_vals, 'r--', linewidth=2, label=fit_label)

	ax.set_xlim(_calculate_axis_limits(df[x_col_plot], snap_x_to_zero))
	ax.set_ylim(_calculate_axis_limits(df[y_col_plot], snap_y_to_zero))
	ax.set_title(title, fontsize=16)
	ax.set_xlabel(x_label, fontsize=12)
	ax.set_ylabel(y_label, fontsize=12)
	ax.grid(True, linestyle='--', alpha=0.6)
	ax.legend(fontsize='small')
	plt.tight_layout()
	plt.savefig(output_path)
	plt.close()
	logging.info(f"Static plot saved to: {os.path.basename(output_path)}")


def animate_curve(
		df: pd.DataFrame, x_col: str, y_col: str, title: str, x_label: str, y_label: str,
		output_path: str, target_duration_s: int = 10, target_fps: int = 30,
		snap_x_to_zero: bool = True, snap_y_to_zero: bool = True
) -> None:
	"""Creates an animated plot."""
	df = df.reset_index(drop=True)
	if len(df) < 2:
		logging.warning(f"Not enough data to animate '{title}'. Skipping.")
		return

	total_frames = int(target_duration_s * target_fps)
	frame_skip = max(1, round(len(df) / total_frames))
	num_frames_to_render = len(df) // frame_skip

	logging.info(f"Creating animation for '{title}' with {num_frames_to_render} frames.")

	fig, ax = plt.subplots(figsize=(10, 7))
	ax.set_xlim(_calculate_axis_limits(df[x_col], snap_x_to_zero))
	ax.set_ylim(_calculate_axis_limits(df[y_col], snap_y_to_zero))
	ax.set_title(title, fontsize=16)
	ax.set_xlabel(x_label, fontsize=12)
	ax.set_ylabel(y_label, fontsize=12)
	ax.grid(True, linestyle='--', alpha=0.6)

	line, = ax.plot([], [], lw=2)
	point, = ax.plot([], [], 'ro', markersize=8)
	text = ax.text(0.05, 0.9, '', transform=ax.transAxes, fontsize=12, va='top')

	def init() -> Tuple[Any, ...]:
		line.set_data([], [])
		point.set_data([], [])
		text.set_text('')
		return line, point, text

	def update(frame: int) -> Tuple[Any, ...]:
		idx = frame * frame_skip
		line.set_data(df[x_col][:idx + 1], df[y_col][:idx + 1])
		point.set_data([df[x_col][idx]], [df[y_col][idx]])
		text.set_text(f'{x_label}: {df[x_col][idx]:.3f}\n{y_label}: {df[y_col][idx]:.2f}')
		return line, point, text

	ani = animation.FuncAnimation(fig, update, frames=num_frames_to_render, init_func=init, blit=True,
	                              interval=1000 / target_fps)

	logging.info(f"Saving animation to: {os.path.basename(output_path)} (this may take a moment)")
	ani.save(output_path, writer='ffmpeg', fps=target_fps)
	plt.close()
	logging.info(f"Animation saved.")