#!/usr/bin/env python3
# scripts/collect_memory.py

"""
Run periodic memory collection and dump CSVs into dumps/time/.
"""

import time
from pathlib import Path

import pandas as pd

from utils.memory import get_meminfo, get_process_info


DEFAULT_SLEEP_SECONDS = 600


def main() -> None:
    """
    Create target directory and periodically write system
    and process memory metrics to timestamped CSV files.
    """
    outdir: Path = Path("dumps/time")
    outdir.mkdir(parents=True, exist_ok=True)

    while True:
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        df_sys = pd.DataFrame([get_meminfo()])
        df_sys.to_csv(outdir / f"sys_mem_{timestamp}.csv", index=False, encoding="utf-8")

        df_proc = get_process_info()
        df_proc.to_csv(outdir / f"process_mem_{timestamp}.csv", index=False, encoding="utf-8")

        time.sleep(DEFAULT_SLEEP_SECONDS)


if __name__ == "__main__":
    main()
