# src/utils/time.py

from datetime import timedelta
from typing import List


def format_timedelta(td: timedelta) -> str:
    """
    Return a human-readable string from a timedelta, e.g. '1d 2h 3m 4s'.
    """
    total = int(td.total_seconds())
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    parts: List[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)
