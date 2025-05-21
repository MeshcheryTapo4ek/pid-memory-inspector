# src/adapters/dumps_reader.py

import glob
from pathlib import Path
from typing import Union

import pandas as pd

from utils.parser import parse_timestamp


def load_system_df(glob_mask: Union[str, Path]) -> pd.DataFrame:
    """
    Return system memory metrics across all matching dumps, with TIMESTAMP column.
    """
    dfs: list[pd.DataFrame] = []
    for fname in glob.iglob(str(glob_mask)):
        ts = parse_timestamp(fname, "sys_mem_")
        df = pd.read_csv(fname)
        df["TIMESTAMP"] = ts
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True).sort_values("TIMESTAMP")


def load_process_df(glob_mask: Union[str, Path]) -> pd.DataFrame:
    """
    Return per-process memory snapshots from all matching dumps, with TIMESTAMP column.
    """
    dfs: list[pd.DataFrame] = []
    for fname in glob.iglob(str(glob_mask)):
        ts = parse_timestamp(fname, "process_mem_")
        df = pd.read_csv(fname)
        df["TIMESTAMP"] = ts
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True).sort_values(["PID", "TIMESTAMP"])
