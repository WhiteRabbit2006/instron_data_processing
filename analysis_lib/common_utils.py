# analysis_lib/common_utils.py
"""
This module provides common utility functions used across the analysis library,
such as loading data from CSV files and splitting DataFrames by time points.
"""

import logging
import os
from typing import Any, List

import pandas as pd


def load_csv_data(file_path: str, **kwargs: Any) -> pd.DataFrame:
    """
    Loads a generic CSV file into a pandas DataFrame.

    Args:
        file_path (str): The full path to the CSV file.
        **kwargs (Any): Additional keyword arguments to pass to pandas.read_csv.

    Returns:
        pd.DataFrame: The loaded data.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at: {file_path}")
    logging.info(f"Loading data from: {os.path.basename(file_path)}")
    return pd.read_csv(file_path, **kwargs)


def split_data_by_time(
    df: pd.DataFrame, split_points: List[float], time_col: str
) -> List[pd.DataFrame]:
    """
    Splits a DataFrame into multiple segments based on a list of time points.

    Each segment includes data from the end of the previous segment (exclusive)
    up to the current split point (inclusive).

    Args:
        df (pd.DataFrame): The input DataFrame to split.
        split_points (List[float]): A list of time points (in seconds) at which
                                    to split the data.
        time_col (str): The name of the time column in the DataFrame.

    Returns:
        List[pd.DataFrame]: A list of DataFrames, each representing a segment
                            of the original data.
    """
    segments: List[pd.DataFrame] = []
    last_time = 0.0

    for end_time in split_points:
        # Ensure the mask correctly handles the start of the first segment
        # and subsequent segments without overlapping or missing data.
        mask = (df[time_col] > last_time) & (df[time_col] <= end_time)
        segment_df = df.loc[mask].copy()
        segments.append(segment_df)
        logging.info(
            f"Created segment from t={last_time:.2f}s to t={end_time:.2f}s "
            f"with {len(segment_df)} data points."
        )
        last_time = end_time

    return segments
