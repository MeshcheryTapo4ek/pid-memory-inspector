# src/application/services.py

from __future__ import annotations

import glob
from pathlib import Path
from typing import Tuple

import pandas as pd

from adapters.dumps_reader import load_process_df, load_system_df
from config.settings import Settings
from domain.analysis.tree_stats import build as build_tree_stats, build_subtree
from domain.analysis.timeseries import pid_timeseries
from domain.filters import ProcessFilter
from utils.parser import parse_timestamp


class MetricsService:
    """
    Application-layer façade for memory-metrics use-cases.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    # --------------------------------------------------------------------- #
    # Snapshots & coverage
    # --------------------------------------------------------------------- #

    def available_stamps(self) -> list[str]:
        mask = self._settings.dumps_dir / self._settings.proc_glob
        return sorted(
            parse_timestamp(f, "process_mem_").strftime("%Y%m%d_%H%M%S")
            for f in glob.iglob(str(mask))
        )

    def system_metrics(self) -> pd.DataFrame:
        df = load_system_df(self._settings.dumps_dir / self._settings.sys_glob)
        df["ram_used_htop_MB"] = (
            df["MemTotal_MB"]
            - df["MemFree_MB"]
            - df["Buffers_MB"]
            - df["Cached_MB"]
            - df["SReclaimable_MB"]
        )
        df["swap_used_MB"] = df["SwapTotal_MB"] - df["SwapFree_MB"]
        return df

    def coverage(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        df = self.system_metrics()
        return df["TIMESTAMP"].min(), df["TIMESTAMP"].max()

    def dumps_time_bounds(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        sys_df = self.system_metrics()
        proc_df = self.process_df()
        t_min = min(sys_df["TIMESTAMP"].min(), proc_df["TIMESTAMP"].min())
        t_max = max(sys_df["TIMESTAMP"].max(), proc_df["TIMESTAMP"].max())
        return t_min, t_max

    # ------------------------------------------------------------------ #
    # Per-process snapshots
    # ------------------------------------------------------------------ #

    def process_df(self) -> pd.DataFrame:
        return load_process_df(self._settings.dumps_dir / self._settings.proc_glob)

    def snapshot_df(self, ts_str: str) -> pd.DataFrame:
        f = self._settings.dumps_dir / f"process_mem_{ts_str}.csv"
        if not f.exists():
            raise FileNotFoundError(f)
        df = pd.read_csv(f)
        df["TIMESTAMP"] = parse_timestamp(str(f), "process_mem_")
        return df

    # ------------------------------------------------------------------ #
    # Tree analytics
    # ------------------------------------------------------------------ #

    def snapshot_tree_stats(self, ts_str: str, pf: ProcessFilter) -> pd.DataFrame:
        snap = self.snapshot_df(ts_str)
        full = self.process_df()
        return build_tree_stats(full, snap, pf).head(pf.limit)

    def snapshot_level(
        self,
        ts_str: str,
        pf: ProcessFilter,
        level: int,
    ) -> pd.DataFrame:
        df = self.snapshot_tree_stats(ts_str, pf)
        return (
            df[df["level"] == level]
            .sort_values("rss_max", ascending=False)
            .head(pf.limit)
        )

    def snapshot_subtree(
        self,
        ts_str: str,
        pf: ProcessFilter,
        root_pid: int,
    ) -> pd.DataFrame:
        df = self.snapshot_tree_stats(ts_str, pf)
        return build_subtree(df, root_pid)

    def pid_plots(self, pid: int) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
        full = self.process_df()
        ts_df, child_df = pid_timeseries(full, pid)

        life = full.loc[full["PID"] == pid, "TIMESTAMP"]
        cmd = full.loc[full["PID"] == pid, "CMD"].iloc[0] if not life.empty else ""

        stats = {
            "since": life.min(),
            "until": life.max(),
            "lifetime_s": (life.max() - life.min()).total_seconds(),
            "rss_min": ts_df["rss_own"].min(),
            "rss_mean": ts_df["rss_own"].mean(),
            "rss_max": ts_df["rss_own"].max(),
            "sub_min": ts_df["rss_subtree"].min(),
            "sub_mean": ts_df["rss_subtree"].mean(),
            "sub_max": ts_df["rss_subtree"].max(),
            "cmd": cmd,
        }

        return ts_df, child_df, stats
