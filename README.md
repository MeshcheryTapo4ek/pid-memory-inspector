# PID Memory Inspector

**PID Memory Inspector** is a powerful visualization and diagnostics tool for tracking memory usage per process over time — with full support for process trees and snapshots.

---

## ✨ Features

- 📈 Live-like graphs of RAM and Swap usage
- 🌲 Tree-based process snapshots at any point in time
- 🔍 Drill-down into any PID: its own memory + all children
- 📊 Graphs: own RSS, subtree RSS, children trends
- 🧠 Filter by lifetime, RSS thresholds, subtree memory
- 🧭 Per-level tree exploration (level 0 / 1 / 2 / ...)
- 🔗 Clickable PID / PPID navigation
- 📎 Auto-aggregated summaries and stats
- 📁 Works with CSV dumps from `dumps/time/`

---

## 🚀 How it works

1. **Collect memory usage dumps** with:
   ```bash
   python scripts/collect_memory.py
   ```
   This periodically creates:
   - `sys_mem_*.csv` — system metrics (`/proc/meminfo`)
   - `process_mem_*.csv` — processes (`ps` dump)

2. **Run the app**:
   ```bash
   make run
   # or
   uvicorn src.app:create_app --reload --factory
   ```

3. **Open in browser**:
   [http://localhost:8000](http://localhost:8000)

---

## 🧩 Interface overview

- `/api/v1/` — Home dashboard: RAM + Swap graphs
- `/api/v1/snapshot/level?lvl=N` — Processes at level N
- `/api/v1/snapshot/pid?pid=...` — Explore subtree of a given PID
- `/api/v1/snapshot/pid/plot?pid=...` — Graphs + stats for PID + children

All views are interactive, filterable, and linked via PID navigation.

---

## 🔧 Project structure

- `scripts/collect_memory.py` — CSV memory dumper
- `src/application/` — orchestration layer (MetricsService)
- `src/domain/` — core logic: tree stats, filters, timelines
- `src/interfaces/web/` — FastAPI routes, HTML + Plotly
- `static/mem.css` — table styling

---

## 🤖 Tech stack

- **Python 3.11** + FastAPI
- **Pandas** for data handling
- **Plotly** for visualizations
- **PureCSS** for lightweight styling
- Custom layered architecture

---

## 🗂️ Example filters

- `lifetime ≥ 300s`
- `RSS ≥ 100 MB`
- `subtree_rss ≥ 500 MB`

---

## 🔮 Future ideas

- [ ] Per-process `Swap:` from `/proc/<pid>/smaps_rollup`
- [ ] CGroup-aware memory rollups
- [ ] Export to JSON / PNG / CSV
- [ ] Alerting on anomalies (spikes, leaks)

---

Made with ♥ for anyone who's ever had to answer:  
> *"Wait... what process is eating all the RAM?"*