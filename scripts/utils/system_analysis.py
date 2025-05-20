# scripts/utils/system_analysis.py
"""
Load system-memory CSVs, compute metrics, and plotting functions.
"""

from typing import List
from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt

from .parser import parse_timestamp


def load_and_compute_metrics(files: List[str]) -> pd.DataFrame:
    """
    Load each sys_mem CSV and compute:
      - ram_used_htop_MB  = MemTotal_MB - MemFree_MB - Buffers_MB - Cached_MB - SReclaimable_MB
      - swap_used_MB      = SwapTotal_MB - SwapFree_MB
    Return a DataFrame sorted by 'datetime'.
    """
    records: list[dict] = []
    for fpath in files:
        ts = parse_timestamp(fpath, "sys_mem_")
        df = pd.read_csv(fpath)
        row = df.iloc[0]
        total_ram = int(row["MemTotal_MB"])

        ram_used = (
            row["MemTotal_MB"]
            - row["MemFree_MB"]
            - row["Buffers_MB"]
            - row["Cached_MB"]
            - row["SReclaimable_MB"]
        )
        swap_used = row["SwapTotal_MB"] - row["SwapFree_MB"]

        records.append({
            "datetime": ts,
            "ram_used_htop_MB": int(ram_used),
            "swap_used_MB": int(swap_used),
            "total_ram_MB": total_ram,
        })

    return pd.DataFrame(records).sort_values("datetime")


def format_timedelta(td: timedelta) -> str:
    """
    Convert a timedelta into a human-readable string, e.g. '1d 2h 3m 4s'.
    """
    total_seconds = int(td.total_seconds())
    days, rem = divmod(total_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def plot_and_save(x: pd.Series, y: pd.Series, title: str, ylabel: str, out_filename: str) -> None:
    """
    Plot a line chart of `y` vs `x` with `title` and `ylabel`, then save to `out_filename`.
    """
    plt.figure()
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_filename)
    plt.close()
