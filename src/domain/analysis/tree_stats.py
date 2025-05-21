# src/domain/analysis/tree_stats.py

"""
Build a PID tree for a snapshot and enrich it with time-series aggregates.

Returned DataFrame columns:
    level               int
    PID, PPID           int
    lifetime            float (seconds)
    rss_min/mean/max    float
    rss_subtree_mean    float
    rss_subtree_max     float
    CMD                 str
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

import pandas as pd

from domain.filters import ProcessFilter


def build(
    df_full: pd.DataFrame,
    df_snapshot: pd.DataFrame,
    flt: ProcessFilter,
) -> pd.DataFrame:
    """
    Return enriched tree of processes present in the given snapshot,
    augmented with time-series memory stats and filtered by criteria.
    """
    # 1. Aggregate own-RSS stats across full history
    grp = df_full.groupby(["PID", "PPID", "CMD"])
    stats = grp["RSS_MB"].agg(
        rss_min="min",
        rss_mean="mean",
        rss_max="max",
    ).reset_index()
    stats["lifetime"] = (
        grp["TIMESTAMP"].max() - grp["TIMESTAMP"].min()
    ).dt.total_seconds().values

    # 2. Keep only processes visible in snapshot
    stats = stats.merge(
        df_snapshot[["PID", "PPID"]], on=["PID", "PPID"], how="inner"
    )

    # 3. Build parent → children mapping
    children: Dict[int, List[int]] = defaultdict(list)
    for pid, ppid in stats[["PID", "PPID"]].itertuples(index=False):
        children[int(ppid)].append(int(pid))

    # 4. Assign tree levels
    levels = _assign_levels(stats, children)
    stats["level"] = stats["PID"].map(levels)

    # 5. Calculate subtree RSS
    subtree_max, subtree_mean = _calc_subtree_rss(stats, children)
    stats["rss_subtree_max"] = stats["PID"].map(subtree_max)
    stats["rss_subtree_mean"] = stats["PID"].map(subtree_mean)

    # 6. Apply filters
    stats = _apply_filters(stats, flt)

    return stats.sort_values(["level", "rss_max"], ascending=[True, False]).reset_index(drop=True)


def _assign_levels(
    stats: pd.DataFrame,
    children: Dict[int, List[int]],
) -> Dict[int, int]:
    """
    Return mapping PID → level in tree using DFS from roots.
    """
    pids = set(stats["PID"])
    roots = [
        pid
        for pid, ppid in stats[["PID", "PPID"]].itertuples(index=False)
        if ppid not in pids
    ]
    levels: Dict[int, int] = {}

    def dfs(pid: int, lvl: int) -> None:
        levels[pid] = lvl
        for ch in children.get(pid, []):
            dfs(ch, lvl + 1)

    for root_pid in roots:
        dfs(root_pid, 0)

    return levels


def _calc_subtree_rss(
    stats: pd.DataFrame,
    children: Dict[int, List[int]],
) -> Tuple[Dict[int, float], Dict[int, float]]:
    """
    Return mappings: PID → cumulative rss_max, rss_mean over subtree.
    """
    rss_max_map = stats.set_index("PID")["rss_max"].to_dict()
    rss_mean_map = stats.set_index("PID")["rss_mean"].to_dict()

    subtree_max: Dict[int, float] = {}
    subtree_mean: Dict[int, float] = {}

    def dfs(pid: int) -> None:
        m_max = rss_max_map[pid]
        m_mean = rss_mean_map[pid]
        for ch in children.get(pid, []):
            dfs(ch)
            m_max += subtree_max[ch]
            m_mean += subtree_mean[ch]
        subtree_max[pid] = m_max
        subtree_mean[pid] = m_mean

    for pid in stats["PID"]:
        if pid not in subtree_max:
            dfs(pid)

    return subtree_max, subtree_mean


def _apply_filters(
    df: pd.DataFrame,
    flt: ProcessFilter,
) -> pd.DataFrame:
    """
    Return filtered rows based on lifetime, own-RSS and subtree-RSS.
    """
    lvl0 = (df["level"] == 0) & (df["rss_subtree_max"] >= flt.min_subtree_rss_mb)
    deeper = (df["level"] > 0) & (df["rss_max"] >= flt.min_rss_mb)
    time_ok = df["lifetime"] >= flt.min_lifetime_s
    return df[time_ok & (lvl0 | deeper)]


def build_subtree(df: pd.DataFrame, root_pid: int) -> pd.DataFrame:
    """
    Return a subtree of all descendants for the given root PID, including root.
    """
    want = {root_pid}
    added = True
    while added:
        added = False
        for pid, ppid in df[["PID", "PPID"]].itertuples(index=False):
            if ppid in want and pid not in want:
                want.add(pid)
                added = True

    out = df[df["PID"].isin(want)].copy()

    match = out.loc[out["PID"] == root_pid, "level"]
    if match.empty:
        return out.head(0)

    root_level = int(match.iloc[0])
    out["level"] = out["level"] - root_level

    return out.sort_values(["level", "rss_max"], ascending=[True, False])
