# src/domain/filters.py

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProcessFilter:
    """
    Filter configuration for selecting and ranking processes
    across memory dump series.
    """

    min_lifetime_s: int = 300
    """Minimum process lifetime in seconds."""

    min_rss_mb: int = 100
    """Minimum maximum RSS (resident set size) in MB."""

    limit: int = 10
    """Number of top entries to keep, sorted by max RSS."""

    min_subtree_rss_mb: int = 500
    """Minimum cumulative RSS of a process subtree in MB."""
