# analysis_lib/common_utils.py
import os
import pandas as pd
import logging
from typing import List, Any

def load_csv_data(file_path: str, **kwargs: Any) -> pd.DataFrame:
    """Loads a generic CSV file into a pandas DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at: {file_path}")
    logging.info(f"Loading data from: {os.path.basename(file_path)}")
    return pd.read_csv(file_path, **kwargs)

def split_data_by_time(df: pd.DataFrame, split_points: List[float], time_col: str = 'Total Time (s)') -> List[pd.DataFrame]:
    """Splits a DataFrame into multiple segments based on a list of time points."""
    segments: List[pd.DataFrame] = []
    last_time = 0.0

    for end_time in split_points:
        mask = (df[time_col] > last_time) & (df[time_col] <= end_time)
        segment_df = df.loc[mask].copy()
        segments.append(segment_df)
        logging.info(f"Created segment from t={last_time:.2f}s to t={end_time:.2f}s with {len(segment_df)} data points.")
        last_time = end_time

    return segments