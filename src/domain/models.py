# src/domain/models.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ProcSnapshot:
    """
    A snapshot of a single process's memory usage at a point in time.
    """
    pid: int
    ppid: int
    user: str
    rss_mb: int
    vsz_mb: int
    cmd: str
    ts: datetime


@dataclass(frozen=True, slots=True)
class SysSnapshot:
    """
    A snapshot of system-wide memory metrics at a point in time.
    """
    mem_total_mb: int
    mem_free_mb: int
    mem_available_mb: int
    buffers_mb: int
    cached_mb: int
    swap_cached_mb: int
    active_anon_mb: int
    inactive_anon_mb: int
    swap_total_mb: int
    swap_free_mb: int
    anon_pages_mb: int
    sreclaimable_mb: int
    sunreclaim_mb: int
    page_tables_mb: int
    commit_limit_mb: int
    committed_as_mb: int
    anon_hugepages: int
    hugepages_total: int
    hugepages_free: int
    ts: datetime
