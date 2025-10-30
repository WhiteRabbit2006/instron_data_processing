# analysis_lib/plotting_tools.py

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import logging


def _calculate_axis_limits(data_series, snap_to_zero=True):
	"""
	Calculates robust axis limits with padding and a configurable "snap to zero" feature.
	"""
	if data_series.empty:
		return 0, 1
	data_min = data_series.min()
	data_max = data_series.max()
	if data_min == data_max:
		return data_min - abs(data_min * 0.1) - 0.1, data_max + abs(data_max * 0.1) + 0.1
	padding = (data_max - data_min) * 0.05
	lower_lim = data_min - padding
	upper_lim = data_max + padding
	if snap_to_zero:
		if data_min >= 0:
			lower_lim = 0
		if data_max <= 0:
			upper_lim = 0
	return lower_lim, upper_lim


def plot_curve(df, x_col_plot, y_col_plot, x_col_base, y_col_base,
               y_base_units, title, x_label, y_label, output_path,
               fit_line=False, fit_bounds=None,
               snap_x_to_zero=True, snap_y_to_zero=True):
	"""
	Generates a static plot with configurable axis snapping and performs linear analysis.
	"""
	fig, ax = plt.subplots(figsize=(10, 7))
	ax.plot(df[x_col_plot], df[y_col_plot], label='Experimental Data')

	if fit_line:
		if fit_bounds is not None and len(fit_bounds) == 2:
			lower_bound, upper_bound = sorted(fit_bounds)
			mask = (df[x_col_plot] >= lower_bound) & (df[x_col_plot] <= upper_bound)
			fit_df = df[mask].copy()
			fit_region_text = f"from {lower_bound:.4f} to {upper_bound:.4f} ({x_label.split(' ')[-1].strip('()')})"
		else:
			fit_df = df.copy()
			fit_region_text = "full data range"
		if not fit_df.empty and len(fit_df) > 1:
			m_base, b_base = np.polyfit(fit_df[x_col_base], fit_df[y_col_base], 1)
			modulus_val = m_base
			modulus_units = y_base_units
			if y_base_units == 'MPa':
				if modulus_val >= 1000:
					modulus_val /= 1000
					modulus_units = 'GPa'
				elif modulus_val < 1 and modulus_val != 0:
					modulus_val *= 1000
					modulus_units = 'kPa'
			y_intercept = b_base
			x_intercept = -b_base / m_base if m_base != 0 else float('inf')

			# Use logging for structured analysis output
			logging.info("\n--- Linear Fit Analysis (in Standard Units) ---")
			logging.info(f"Fit Region:       {fit_region_text}")
			logging.info(f"Calculated Modulus: {modulus_val:.3f} {modulus_units}")
			logging.info(f"Y-Intercept (Stress-Axis):  {y_intercept:.4f} {y_base_units}")
			logging.info(f"X-Intercept (Strain-Axis):  {x_intercept:.5f} (unitless)")
			logging.info("-------------------------------------------------")

			m_plot, b_plot = np.polyfit(fit_df[x_col_plot], fit_df[y_col_plot], 1)
			fit_x_values = np.array([fit_df[x_col_plot].min(), fit_df[x_col_plot].max()])
			fit_y_values = m_plot * fit_x_values + b_plot
			fit_label = (
				f'Linear Fit (Region: {fit_region_text})\n'
				f'Modulus: {modulus_val:.2f} {modulus_units}\n'
				f'Y-Intercept: {y_intercept:.3f} {y_base_units}\n'
				f'X-Intercept: {x_intercept:.4f}'
			)
			ax.plot(fit_x_values, fit_y_values, 'r--', linewidth=2, label=fit_label)

	x_lims = _calculate_axis_limits(df[x_col_plot], snap_to_zero=snap_x_to_zero)
	y_lims = _calculate_axis_limits(df[y_col_plot], snap_to_zero=snap_y_to_zero)
	ax.set_xlim(x_lims)
	ax.set_ylim(y_lims)

	ax.set_title(title, fontsize=16)
	ax.set_xlabel(x_label, fontsize=12)
	ax.set_ylabel(y_label, fontsize=12)
	ax.grid(True, linestyle='--', alpha=0.6)
	ax.legend(fontsize='small')
	plt.tight_layout()
	plt.savefig(output_path)
	plt.close()
	logging.info(f"Static plot saved to: {os.path.basename(output_path)}")


def animate_curve(df, x_col, y_col, title, x_label, y_label, output_path,
                  target_duration_s=10, target_fps=30,
                  snap_x_to_zero=True, snap_y_to_zero=True):
	"""
	Creates an animated plot. Duration and FPS determine the playback speed.
	"""
	df = df.reset_index(drop=True)

	total_data_points = len(df)
	if total_data_points < 2:
		logging.warning(f"Not enough data (< 2 points) to create animation for '{title}'. Skipping.")
		return

	total_frames_target = int(target_duration_s * target_fps)
	ideal_frame_skip = total_data_points / total_frames_target

	if ideal_frame_skip < 1:
		frame_skip = 1
		num_frames_to_render = total_data_points
		logging.warning(f"Not enough data for a full {target_duration_s}s video at {target_fps} FPS.")
		logging.warning(f"Using every data point (frame_skip=1). Video will be shorter.")
	else:
		frame_skip = max(1, round(ideal_frame_skip))
		num_frames_to_render = total_data_points // frame_skip

	logging.info(f"\nCreating animation for '{title}':")
	logging.info(f"  - Target: {target_duration_s}s at {target_fps} FPS ({total_frames_target} target frames).")
	logging.info(f"  - Data: {total_data_points} points available.")
	logging.info(f"  - Calculated frame_skip: {frame_skip} (to produce {num_frames_to_render} frames).")

	fig, ax = plt.subplots(figsize=(10, 7))
	x_lims = _calculate_axis_limits(df[x_col], snap_to_zero=snap_x_to_zero)
	y_lims = _calculate_axis_limits(df[y_col], snap_to_zero=snap_y_to_zero)
	ax.set_xlim(x_lims)
	ax.set_ylim(y_lims)
	ax.set_title(title, fontsize=16)
	ax.set_xlabel(x_label, fontsize=12)
	ax.set_ylabel(y_label, fontsize=12)
	ax.grid(True, linestyle='--', alpha=0.6)

	line, = ax.plot([], [], lw=2)
	point, = ax.plot([], [], 'ro', markersize=8)
	text = ax.text(0.05, 0.9, '', transform=ax.transAxes, fontsize=12, va='top')

	def init():
		line.set_data([], [])
		point.set_data([], [])
		text.set_text('')
		return line, point, text

	def update(frame):
		idx = frame * frame_skip
		if idx >= len(df): return line, point, text
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