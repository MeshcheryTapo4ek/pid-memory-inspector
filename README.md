# pid-memory-inspector

A minimal yet powerful toolkit to continuously collect and deeply analyze system and per-process memory usage on Linux. This repository automates:

- Scheduled snapshots of **system-wide** memory stats from `/proc/meminfo`.
- Periodic captures of **every running process**’s RSS and VSZ via `ps`.
- Storage of raw data in **timestamped CSV files** for auditability.
- Analysis scripts that compute advanced metrics, generate summary tables, and produce publication-quality plots.

---

## 🚀 Features

1. **Automated Data Collection**  
   - **`collect_memory.py`**: Daemon-style script that every 10 minutes:
     - Reads `/proc/meminfo` and writes selected fields in MB to `dumps/time/sys_mem_<timestamp>.csv`.
     - Executes `ps -eo pid,ppid,user,rss,vsz,cmd` and writes to `dumps/time/process_mem_<timestamp>.csv`.

2. **Rich System Analysis**  
   - **Metrics computed**:
     - **RAM Used (htop method)**: `MemTotal - MemFree - Buffers - Cached - SReclaimable`.
     - **Swap Used**: `SwapTotal - SwapFree`.
     - **Total RAM Usage %**: `RAM Used / MemTotal * 100`.
   - **Outputs**:
     - `plots/system/system_metrics.csv` — tabular export of all computed metrics.
     - Time-series plots:
       - `ram_used_htop.png`
       - `swap_used.png`
       - `ram_vs_swap.png`
       - `ram_used_pct.png`

3. **Comprehensive Process Analysis**  
   - **Metrics computed**:
     - **Per-PID RSS Spread**: Difference between the maximum and minimum RSS observed.
   - **Outputs**:
     - `plots/processes/top10_rss_spread.csv` — top‑10 processes by RSS spread, with columns: `PID`, `min_RSS`, `max_RSS`, `spread`, `CMD`.
     - Individual PID time-series plots: `plots/processes/rss_pid_<PID>.png`.

4. **Modular Utility Libraries**  
   - **`scripts/utils/parser.py`**: Discover CSV files and parse their timestamps.
   - **`scripts/utils/system_analysis.py`**: Load system CSVs, compute metrics, and plotting functions.
   - **`scripts/utils/process_analysis.py`**: Load process CSVs, compute spreads, and generate per-PID plots.

5. **Extensible & Configurable**  
   - All **intervals**, **paths**, and **patterns** are configurable via constants at the top of each script.
   - Easy to add new metrics or filters by editing utility modules.
   - Modular design keeps **collection**, **analysis**, and **visualization** separate, facilitating tests and extensions.

---

## 📂 Project Structure

```
.
├── .gitignore
├── Makefile                     # run, lint, test targets
├── requirements.txt             # pandas, matplotlib
├── requirements-dev.txt         # pytest, black, ruff, mypy
├── dumps/
│   └── time/                    # CSV snapshots
├── plots/
│   ├── system/                  # system analysis outputs
│   └── processes/               # process analysis outputs
└── scripts/
    ├── collect_memory.py        # entrypoint for data collection
    ├── analyze_system.py        # entrypoint for system analysis
    ├── analyze_processes.py     # entrypoint for process analysis
    └── utils/
        ├── __init__.py
        ├── parser.py            # helpers for file discovery & timestamp parsing
        ├── system_analysis.py   # system metrics & plotting utilities
        └── process_analysis.py  # process metrics & plotting utilities
```

---

## 📝 Data Collection (`collect_memory.py`)

- **Interval**: default 10 minutes (`600s`), configurable at the top of the script.
- **Output Path**: `dumps/time`, created if missing.
- **System CSV**:  
  - Filename: `sys_mem_<YYYYMMDD_HHMMSS>.csv`  
  - Columns: `MemTotal_MB`, `MemFree_MB`, `MemAvailable_MB`, …, `HugePages_Free`.
- **Process CSV**:  
  - Filename: `process_mem_<YYYYMMDD_HHMMSS>.csv`  
  - Columns: `PID`, `PPID`, `USER`, `RSS_MB`, `VSZ_MB`, `CMD`.

---

## 📊 System Analysis (`analyze_system.py`)

1. **Discovery**: finds all `sys_mem_*.csv` under `dumps/time`.
2. **Metrics**: invokes `utils.system_analysis.load_and_compute_metrics()`.
3. **Summary**: prints total time span and duration.
4. **Exports**:
   - Raw metrics CSV: `plots/system/system_metrics.csv`.
   - Time-series plots:  
     - `ram_used_htop.png`  
     - `swap_used.png`  
     - `ram_vs_swap.png`  
     - `ram_used_pct.png`

---

## 🔍 Process Analysis (`analyze_processes.py`)

1. **Discovery**: finds all `process_mem_*.csv` under `dumps/time`.
2. **Aggregation**: loads and concatenates all snapshots via `utils.process_analysis.load_all_records()`.
3. **Spread Calculation**: groups by `PID`, computing `min_RSS`, `max_RSS`, `spread`, and captures first `CMD`.
4. **Exports**:
   - Top-10 CSV: `plots/processes/top10_rss_spread.csv`.
   - Console table of top-10 processes.
   - Per-PID plots: `plots/processes/rss_pid_<PID>.png`.

---

## ✨ Extending the Toolkit

- **Add new metrics**: modify `load_and_compute_metrics()` or `compute_rss_spread()`.  
- **Custom filters**: extend `analyze_processes.py` with substring filters on `CMD`.  
- **Integration**: ingest CSVs into BI tools or dashboards.  
- **Alerts**: wrap analysis into cronjobs or monitoring alerts for unusual memory spikes.

---