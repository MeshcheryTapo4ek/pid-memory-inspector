"""
Memory utilities to collect system and process memory metrics.
"""

from typing import Dict
import subprocess
import pandas as pd


def get_meminfo() -> Dict[str, int]:
    """
    Read /proc/meminfo and return selected metrics.
    Values are in MB, except HugePages counts.
    """
    wanted = [
        'MemTotal', 'MemFree', 'MemAvailable', 'Buffers', 'Cached',
        'SwapTotal', 'SwapFree', 'SwapCached',
        'Active(anon)', 'Inactive(anon)', 'AnonPages',
        'SReclaimable', 'SUnreclaim',
        'PageTables',
        'Committed_AS', 'CommitLimit',
        'AnonHugePages', 'HugePages_Total', 'HugePages_Free'
    ]
    meminfo: Dict[str, int] = {}
    with open('/proc/meminfo') as f:
        for line in f:
            key, *rest = line.split(':')
            if key not in wanted:
                continue
            value_kb = int(rest[0].strip().split()[0])
            # convert to MB unless this is a page count
            if key.startswith('HugePages'):
                meminfo[key] = value_kb
            else:
                meminfo[f'{key}_MB'] = value_kb // 1024
    return meminfo


def get_process_info() -> pd.DataFrame:
    """
    Collect info about all running processes via `ps`.
    Returns a DataFrame with columns:
    PID, PPID, USER, RSS_MB, VSZ_MB, CMD.
    """
    cmd = ['ps', '-eo', 'pid,ppid,user,rss,vsz,cmd', '--sort=-rss']
    output = subprocess.check_output(cmd).decode().splitlines()
    rows = []
    for line in output[1:]:
        parts = line.strip().split(None, 5)
        if len(parts) < 6:
            continue
        pid, ppid, user, rss, vsz, cmdline = parts
        try:
            rss_mb = int(rss) // 1024
            vsz_mb = int(vsz) // 1024
        except ValueError:
            rss_mb = vsz_mb = 0
        rows.append({
            'PID': pid,
            'PPID': ppid,
            'USER': user,
            'RSS_MB': rss_mb,
            'VSZ_MB': vsz_mb,
            'CMD': cmdline,
        })
    return pd.DataFrame(rows)
