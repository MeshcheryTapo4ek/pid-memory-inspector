# scripts/utils/parser.py
"""
Utilities for locating CSV dumps and parsing their timestamps.
"""

import os
import glob
from typing import List
import pandas as pd


def find_csv_files(directory: str, pattern: str) -> List[str]:
    """
    Return a sorted list of file paths in `directory` matching `pattern`.
    """
    search_path = os.path.join(directory, pattern)
    return sorted(glob.glob(search_path))


def parse_timestamp(path: str, prefix: str) -> pd.Timestamp:
    """
    Extract a timestamp from `path` by removing `prefix` and '.csv',
    then parsing with format 'YYYYMMDD_HHMMSS'.
    """
    base = os.path.basename(path)
    ts_str = base.replace(prefix, "").replace(".csv", "")
    return pd.to_datetime(ts_str, format="%Y%m%d_%H%M%S")
