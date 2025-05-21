# src/domain/analysis/timeseries.py

from typing import Dict, List, Set, Tuple

import pandas as pd


def collect_subtree_pids(df: pd.DataFrame, root: int) -> Set[int]:
    """
    Return the set of all PIDs in the subtree rooted at `root`, including the root.
    """
    tree: Dict[int, List[int]] = {}
    for pid, ppid in df[["PID", "PPID"]].itertuples(index=False):
        tree.setdefault(ppid, []).append(pid)

    seen: Set[int] = {root}
    queue: List[int] = [root]

    while queue:
        current = queue.pop()
        for child in tree.get(current, []):
            if child not in seen:
                seen.add(child)
                queue.append(child)

    return seen


def pid_timeseries(df: pd.DataFrame, root: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Return time series for a root PID:
    - First dataframe: TIMESTAMP, rss_own, rss_subtree
    - Second dataframe (long): TIMESTAMP, PID, rss
    """
    all_pids = collect_subtree_pids(df, root)

    ts_rows: List[Dict[str, int | float | pd.Timestamp]] = []
    child_rows: List[Dict[str, int | float | pd.Timestamp]] = []

    for timestamp, snap in df.groupby("TIMESTAMP"):
        own_rss = snap.loc[snap["PID"] == root, "RSS_MB"].sum()
        subtree_rss = snap.loc[snap["PID"].isin(all_pids), "RSS_MB"].sum()

        ts_rows.append({
            "TIMESTAMP": timestamp,
            "rss_own": own_rss,
            "rss_subtree": subtree_rss,
        })

        for pid, rss in snap[snap["PID"].isin(all_pids)][["PID", "RSS_MB"]].itertuples(index=False):
            child_rows.append({
                "TIMESTAMP": timestamp,
                "PID": pid,
                "rss": rss,
            })

    return pd.DataFrame(ts_rows), pd.DataFrame(child_rows)
