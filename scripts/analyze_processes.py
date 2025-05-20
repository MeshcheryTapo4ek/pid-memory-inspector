#!/usr/bin/env python3
# scripts/analyze_processes.py
"""
Entrypoint: analyze process memory dumps, save top-10 spread table and generate plots.
"""

import os
from typing import List

from utils.parser import find_csv_files
from utils.process_analysis import (
    load_all_records,
    compute_rss_spread,
    get_pids_by_rss_spread,
    plot_rss_for_pids,
)

MOST_VARIOUS_N = 10

def main() -> None:
    directory = os.path.join("dumps", "time")
    pattern = "process_mem_*.csv"
    files: List[str] = find_csv_files(directory, pattern)
    if not files:
        print(f"No files found in '{directory}'.")
        return

    # Загружаем все записи и считаем spread
    df_all = load_all_records(files)
    spreads = compute_rss_spread(df_all)

    # Переставляем CMD в конец
    spreads = spreads[["PID", "min_RSS", "max_RSS", "spread", "CMD"]]

    # Сохраняем топ-MOST_VARIOUS_N процессов по spread в CSV
    top = spreads.head(MOST_VARIOUS_N)
    

    # Выводим его в консоль
    print("\nTop MOST_VARIOUS_N processes by RSS spread:")
    print(top.to_string(index=False))

    # Строим графики по этим PID
    pids: List[int] = get_pids_by_rss_spread(top)
    plot_rss_for_pids(df_all, pids, output_dir="rss_pid_plots")

    csv_fname = "rss_pid_plots/top_rss_spread.csv"
    top.to_csv(csv_fname, index=False)
    print(f"Saved top-10 RSS spread table → {csv_fname}")


if __name__ == "__main__":
    main()
