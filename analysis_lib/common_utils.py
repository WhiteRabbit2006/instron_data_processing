# analysis_lib/common_utils.py
import os
import pandas as pd
import logging

def load_csv_data(file_path, **kwargs):
    """
    Loads a generic CSV file into a pandas DataFrame.
    Accepts additional keyword arguments for pandas.read_csv.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at: {file_path}")
    logging.info(f"Loading data from: {os.path.basename(file_path)}")
    return pd.read_csv(file_path, **kwargs)


def split_data_by_time(df, split_points, time_col='Total Time (s)'):
    """
    Splits a DataFrame into multiple segments based on a list of time points.

    Args:
        df (pd.DataFrame): The DataFrame to split.
        split_points (list of floats): A list of end times for each segment.
                                       e.g., [10, 15] for 0-10s and 10-15s segments.
        time_col (str): The name of the time column to use for splitting.

    Returns:
        list of pd.DataFrame: A list containing the DataFrame segments in order.
    """
    segments = []
    last_time = 0

    for end_time in split_points:
        # Create a boolean mask for the current time window
        mask = (df[time_col] > last_time) & (df[time_col] <= end_time)
        segment_df = df[mask].copy() # Use .copy() to avoid SettingWithCopyWarning
        segments.append(segment_df)
        logging.info(f"Created segment from t={last_time:.2f}s to t={end_time:.2f}s with {len(segment_df)} data points.")
        last_time = end_time  # Update the start time for the next segment

    return segments