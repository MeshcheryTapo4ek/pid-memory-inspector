#!/usr/bin/env python3
# scripts/collect_memory.py
"""
Entrypoint: periodically dump system- and process-memory CSVs into dumps/time/.
"""

import time
from pathlib import Path

import pandas as pd

from utils.memory import get_meminfo, get_process_info


SLEEP_TIME = 600


def main() -> None:
    outdir = Path('dumps/time')
    outdir.mkdir(parents=True, exist_ok=True)

    while True:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        # System memory snapshot
        df_sys = pd.DataFrame([get_meminfo()])
        df_sys.to_csv(outdir / f'sys_mem_{timestamp}.csv', index=False)

        # Per-process snapshot
        df_proc = get_process_info()
        df_proc.to_csv(outdir / f'process_mem_{timestamp}.csv', index=False)

        # Sleep for 10 minutes
        time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
