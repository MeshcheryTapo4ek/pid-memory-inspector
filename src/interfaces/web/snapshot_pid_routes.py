# src/interfaces/web/snapshot_pid_plot.py

import html

import pandas as pd
import plotly.graph_objects as go
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from application.services import MetricsService
from config.settings import Settings
from utils.time import format_timedelta


plot_router = APIRouter()


def get_service() -> MetricsService:
    return MetricsService(Settings())


@plot_router.get("/snapshot/pid/plot", response_class=HTMLResponse)
def pid_plot(
    service: MetricsService = Depends(get_service),
    pid: int = Query(..., description="PID to plot"),
) -> HTMLResponse:
    """
    Render timeline plots and stats for a given PID and its subtree.
    """
    ts_df, child_df, stats = service.pid_plots(pid)
    if ts_df.empty:
        return HTMLResponse(f"<h1>No data for PID {pid}</h1>", status_code=404)

    # ── Summary block ───────────────────────────────────────────────────────
    duration = format_timedelta(pd.Timedelta(seconds=stats["lifetime_s"]))
    summary_html = f"""
    <table class='proc-table'>
      <tr><th colspan="2">PID {pid} summary</th></tr>
      <tr><td>cmd</td><td>{html.escape(stats['cmd'])}</td></tr>
      <tr><td>since</td><td>{stats['since']}</td></tr>
      <tr><td>until</td><td>{stats['until']}</td></tr>
      <tr><td>lifetime</td><td>{duration}</td></tr>
      <tr><td>rss min/mean/max</td>
          <td>{stats['rss_min']} / {stats['rss_mean']:.1f} / {stats['rss_max']} MB</td></tr>
      <tr><td>subtree min/mean/max</td>
          <td>{stats['sub_min']} / {stats['sub_mean']:.1f} / {stats['sub_max']} MB</td></tr>
    </table>
    """

    ts_min, ts_max = service.dumps_time_bounds()

    # ── Own + subtree plot ──────────────────────────────────────────────────
    fig = go.Figure()
    fig.add_scattergl(x=ts_df["TIMESTAMP"], y=ts_df["rss_own"], mode="lines+markers", name="RSS own")
    fig.add_scattergl(x=ts_df["TIMESTAMP"], y=ts_df["rss_subtree"], mode="lines", name="RSS subtree", line=dict(dash="dash"))
    fig.add_scattergl(x=[ts_min, ts_max], y=[0, 0], mode="lines", name="", showlegend=False, line=dict(color="rgba(0,0,0,0)"))
    fig.update_layout(height=550, hovermode="x unified")
    fig.update_xaxes(range=[ts_min, ts_max])
    html_main = fig.to_html(full_html=False, include_plotlyjs="cdn")

    # ── Children RSS plot ───────────────────────────────────────────────────
    fig2 = go.Figure()
    for child_pid, grp in child_df.groupby("PID"):
        fig2.add_scattergl(x=grp["TIMESTAMP"], y=grp["rss"], mode="lines", name=str(child_pid))
    fig2.add_scattergl(x=[ts_min, ts_max], y=[0, 0], mode="lines", name="", showlegend=False, line=dict(color="rgba(0,0,0,0)"))
    fig2.update_layout(title="Children RSS", height=550, hovermode="x unified")
    fig2.update_xaxes(range=[ts_min, ts_max])
    html_children = fig2.to_html(full_html=False, include_plotlyjs=False)

    # ── Children summary table ──────────────────────────────────────────────
    child_stats_rows = []
    for child_pid in sorted(child_df["PID"].unique()):
        _, _, cstats = service.pid_plots(child_pid)
        life = format_timedelta(pd.Timedelta(seconds=cstats["lifetime_s"]))
        rss_stat = f"{cstats['rss_min']} / {cstats['rss_mean']:.1f} / {cstats['rss_max']}"
        sub_stat = f"{cstats['sub_min']} / {cstats['sub_mean']:.1f} / {cstats['sub_max']}"
        pid_link = f'<a href="/api/v1/snapshot/pid/plot?pid={child_pid}">{child_pid}</a>'
        ppid_link = f'<a href="/api/v1/snapshot/pid/plot?pid={pid}">{pid}</a>'
        child_stats_rows.append(f"<tr><td>{pid_link}</td><td>{ppid_link}</td><td>{cstats['since']}</td><td>{cstats['until']}</td><td>{life}</td><td>{rss_stat} MB</td><td>{sub_stat} MB</td></tr>")

    child_summary_html = f"""
    <h2>Children summary</h2>
    <table class="proc-table">
      <thead>
        <tr>
          <th>PID</th><th>PPID</th><th>since</th><th>until</th>
          <th>lifetime</th><th>rss min/mean/max</th><th>subtree min/mean/max</th>
        </tr>
      </thead>
      <tbody>
        {''.join(child_stats_rows)}
      </tbody>
    </table>
    """

    # ── Mapping: PID → CMD ──────────────────────────────────────────────────
    full = service.process_df()
    child_cmds = {
        child_pid: full.loc[full["PID"] == child_pid, "CMD"].iloc[0]
        if not full.loc[full["PID"] == child_pid, "CMD"].empty
        else ""
        for child_pid in sorted(child_df["PID"].unique())
    }

    mapping_html = f"""
    <h2>Child PID → CMD</h2>
    <table class="proc-table mapping-table">
      <thead><tr><th>PID</th><th>CMD</th></tr></thead>
      <tbody>
        {''.join(
            f'<tr><td><a href="/api/v1/snapshot/pid/plot?pid={pid}">{pid}</a></td><td>{html.escape(cmd)}</td></tr>'
            for pid, cmd in child_cmds.items()
        )}
      </tbody>
    </table>
    """

    # ── Final render ────────────────────────────────────────────────────────
    return HTMLResponse(f"""
    <html>
      <head>
        <title>PID {pid} RSS timeline</title>
        <link rel="stylesheet" href="/static/mem.css">
      </head>
      <body class="wrapper">
        <h1>PID {pid}</h1>
        {summary_html}

        <h2>Own &amp; subtree RSS</h2>
        {html_main}

        <h2>Children RSS</h2>
        {html_children}

        {child_summary_html}
        {mapping_html}

        <p><a href="/api/v1/snapshot/pid?pid={pid}">← back to subtree</a></p>
      </body>
    </html>
    """)
