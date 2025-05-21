# src/interfaces/web/snapshot_level_routes.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
import pandas as pd

from application.services import MetricsService
from config.settings import Settings
from domain.filters import ProcessFilter
from interfaces.web.renderers.proc_tree import build_proc_tree
from utils.time import format_timedelta

lvl_router = APIRouter()


def get_service() -> MetricsService:
    return MetricsService(Settings())


@lvl_router.get("/snapshot/level", response_class=HTMLResponse)
def snapshot_by_level(
    service: MetricsService = Depends(get_service),
    lvl: int = Query(..., ge=0, description="Which tree level to show"),
    ts: str | None = Query(None, description="Timestamp YYYYMMDD_HHMMSS"),
    min_life: int = Query(300, ge=0, description="Minimum lifetime in seconds"),
    min_rss: int = Query(100, ge=0, description="Minimum RSS in MB (for non-root)"),
    min_subtree: int = Query(100, ge=0, description="Minimum subtree RSS for root"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum number of rows"),
) -> HTMLResponse:
    """
    Render a process snapshot table filtered by tree level and memory criteria.
    """
    stamps = service.available_stamps()
    if not stamps:
        return HTMLResponse("<h1>No process dumps found</h1>", status_code=404)

    ts = ts or stamps[-1]
    if ts not in stamps:
        return HTMLResponse(f"<h1>Timestamp {ts} unknown</h1>", status_code=404)

    pf = ProcessFilter(
        min_lifetime_s=min_life,
        min_rss_mb=min_rss,
        min_subtree_rss_mb=min_subtree,
        limit=limit,
    )

    df_full = service.snapshot_tree_stats(ts, pf)
    if df_full.empty:
        return HTMLResponse("<h1>No rows after filtering</h1>", status_code=200)

    available_lvls = sorted(df_full["level"].unique())
    df = df_full[df_full["level"] == lvl]
    if df.empty:
        df = df_full.head(0)

    df["lifetime"] = df["lifetime"].apply(
        lambda s: format_timedelta(pd.Timedelta(seconds=s))
    )
    df["level"] = 0

    df_linked = df.copy()
    df_linked["PID"] = df_linked["PID"].apply(
        lambda p: (
            f'<a href="/api/v1/snapshot/pid?pid={p}&ts={ts}'
            f'&min_life={min_life}&min_rss={min_rss}'
            f'&min_subtree={min_subtree}&limit={limit}">{p}</a>'
        )
    )
    df_linked = df_linked.sort_values("rss_subtree_max", ascending=False)
    table_html = build_proc_tree(df_linked)

    ts_options = "\n".join(
        f'<option value="{s}" {"selected" if s == ts else ""}>{s}</option>'
        for s in stamps
    )

    lvl_links = " | ".join(
        f'<a href="/api/v1/snapshot/level?lvl={n}&ts={ts}'
        f'&min_life={min_life}&min_rss={min_rss}&min_subtree={min_subtree}&limit={limit}">'
        f'Level {n}</a>'
        for n in available_lvls
    )

    totals = (
        df.select_dtypes("number")
        .drop(columns=["level"])
        .sum(numeric_only=True)
        .to_frame(name="Σ")
        .T
    )

    totals_html = totals.to_html(
        index=False,
        classes="proc-table",
        float_format=lambda x: f"{x:,.1f}",
    )

    return HTMLResponse(
        f"""
    <html>
      <head>
        <title>Snapshot {ts} – level {lvl}</title>
        <link rel="stylesheet" href="/static/mem.css">
      </head>
      <body style="font-family:sans-serif;">
        <div class="wrapper">
          <h1>Level {lvl} – snapshot <small>{ts}</small></h1>
          <p>{lvl_links}</p>

          <form class="pure-form">
            Snapshot 
            <select name="ts">{ts_options}</select>,
            show level <input name="lvl" type="number" value="{lvl}" min="0" style="width:4em">,
            lifetime ≥ <input name="min_life" type="number" value="{min_life}" style="width:6em"> s,
            RSS ≥ <input name="min_rss" type="number" value="{min_rss}" style="width:5em"> MB,
            subtree ≥ <input name="min_subtree" type="number" value="{min_subtree}" style="width:6em"> MB,
            top <input name="limit" type="number" value="{limit}" style="width:4em"> rows
            <button class="pure-button" type="submit">Apply</button>
          </form>

          <h2>Processes</h2>
          {table_html}

          <h3>Totals</h3>
          {totals_html}

          <p><a href="/api/v1/snapshot">← back to snapshot</a></p>
        </div>
      </body>
    </html>
    """
    )
