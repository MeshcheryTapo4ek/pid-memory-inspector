#!/usr/bin/env python3
# scripts/analyze_system.py
"""
Entrypoint: analyze system memory dumps and generate plots.
"""

import os
import matplotlib.pyplot as plt


from utils.parser import find_csv_files
from utils.system_analysis import (
    load_and_compute_metrics,
    format_timedelta,
    plot_and_save,
)


def main() -> None:
    directory = os.path.join("dumps", "time")
    pattern = "sys_mem_*.csv"
    files = find_csv_files(directory, pattern)
    if not files:
        print(f"No files found in '{directory}'.")
        return

    df = load_and_compute_metrics(files)
    start, end = df["datetime"].min(), df["datetime"].max()
    duration = end - start
    print(f"Logs cover: {start} → {end} (duration: {format_timedelta(duration)})")

    # ensure output dir exists
    out_plots = os.path.join("plots", "system")
    os.makedirs(out_plots, exist_ok=True)

    # save system‐metrics table as CSV
    df.to_csv(os.path.join("plots", "system", "system_metrics.csv"), index=False)

    # plot RAM used
    plot_and_save(
        x=df["datetime"],
        y=df["ram_used_htop_MB"],
        title="RAM Used (htop method) Over Time",
        ylabel="RAM Used (MB)",
        out_filename=os.path.join(out_plots, "ram_used_htop.png"),
    )
    # plot Swap used
    plot_and_save(
        x=df["datetime"],
        y=df["swap_used_MB"],
        title="Swap Used Over Time",
        ylabel="Swap Used (MB)",
        out_filename=os.path.join(out_plots, "swap_used.png"),
    )

    # plot RAM vs Swap on one chart
    plt.figure()
    plt.plot(df["datetime"], df["ram_used_htop_MB"], label="RAM Used (MB)")
    plt.plot(df["datetime"], df["swap_used_MB"], label="Swap Used (MB)")
    plt.title("RAM vs Swap Usage Over Time")
    plt.xlabel("Time")
    plt.ylabel("MB")
    plt.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(out_plots, "ram_vs_swap.png"))
    plt.close()

    # plot Total RAM Usage % over time
    df["ram_used_pct"] = df["ram_used_htop_MB"] / df["total_ram_MB"] * 100
    plot_and_save(
        x=df["datetime"],
        y=df["ram_used_pct"],
        title="Total RAM Usage Percentage Over Time",
        ylabel="RAM Used (%)",
        out_filename=os.path.join(out_plots, "ram_used_pct.png"),
    )


if __name__ == "__main__":
    main()
