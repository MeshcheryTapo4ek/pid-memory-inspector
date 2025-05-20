# scripts/utils/process_analysis.py
"""
Load process-memory CSVs, analyze RSS spread, and per-PID plotting.
"""

import os
from typing import List
import pandas as pd
import matplotlib.pyplot as plt

from .parser import parse_timestamp


def load_all_records(files: List[str]) -> pd.DataFrame:
    """
    Read each process_mem CSV, extract PID, CMD, RSS_MB, add 'datetime',
    and concatenate into one DataFrame.
    """
    rows: list[pd.DataFrame] = []
    for path in files:
        ts = parse_timestamp(path, "process_mem_")
        df = pd.read_csv(path, usecols=["PID", "CMD", "RSS_MB"])
        df["datetime"] = ts
        rows.append(df)
    return pd.concat(rows, ignore_index=True)


def compute_rss_spread(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each PID compute:
      - min_RSS: minimal RSS_MB seen
      - max_RSS: maximal RSS_MB seen
      - spread : max_RSS - min_RSS
      - CMD    : first encountered CMD
    Return sorted DataFrame by descending 'spread'.
    """
    agg = df.groupby("PID").agg(
        min_RSS=("RSS_MB", "min"),
        max_RSS=("RSS_MB", "max"),
        CMD=("CMD", "first"),
    ).reset_index()
    agg["spread"] = agg["max_RSS"] - agg["min_RSS"]
    return agg.sort_values("spread", ascending=False)


def get_pids_by_rss_spread(spreads_df: pd.DataFrame) -> List[int]:
    """
    Given a DataFrame returned by compute_rss_spread(),
    return the list of PIDs in descending order of 'spread'.
    """
    return spreads_df["PID"].tolist()


def plot_rss_for_pids(df: pd.DataFrame, pids: List[int], output_dir: str) -> None:
    """
    For each PID in 'pids', plot RSS_MB over time and save to output_dir/rss_pid_<PID>.png.
    """
    os.makedirs(output_dir, exist_ok=True)
    pivot = df.pivot(index="datetime", columns="PID", values="RSS_MB")

    for pid in pids:
        if pid not in pivot.columns:
            continue
        plt.figure()
        plt.plot(pivot.index, pivot[pid], marker="o", linewidth=1)
        plt.title(f"RSS Over Time for PID {pid}")
        plt.xlabel("Time")
        plt.ylabel("RSS (MB)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        fname = os.path.join(output_dir, f"rss_pid_{pid}.png")
        plt.savefig(fname)
        plt.close()
