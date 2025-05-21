# src/interfaces/web/routes.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go

from application.services import MetricsService
from config.settings import Settings
from interfaces.web.plots.dashboard import build_dashboard
from interfaces.web.plots.ram import ram_traces
from interfaces.web.plots.swap import swap_traces
from utils.time import format_timedelta


router = APIRouter()


def get_service() -> MetricsService:
    return MetricsService(Settings())


@router.get("/", response_class=HTMLResponse)
def index(
    svc: MetricsService = Depends(get_service),
    cols: int = 2,
    height: int = 500,
) -> str:
    """
    Render dashboard with RAM and Swap usage charts.
    """
    df = svc.system_metrics()
    if df.empty:
        raise HTTPException(status_code=404, detail="No system snapshots found")

    start, end = svc.coverage()
    delta = format_timedelta(end - start)
    ts_min, ts_max = svc.dumps_time_bounds()

    # --- RAM figure ---
    ram_fig = go.Figure(ram_traces(df), layout=dict(title="RAM usage (htop)"))
    ram_fig.update_xaxes(range=[ts_min, ts_max])
    ram_fig.add_scatter(
        x=[ts_min, ts_max],
        y=[0, 0],
        mode="lines",
        name="",
        showlegend=False,
        line=dict(color="rgba(0,0,0,0)"),
    )

    # --- Swap figure ---
    swap_fig = go.Figure(swap_traces(df), layout=dict(title="Swap usage"))
    swap_fig.update_xaxes(range=[ts_min, ts_max])
    swap_fig.add_scatter(
        x=[ts_min, ts_max],
        y=[0, 0],
        mode="lines",
        name="",
        showlegend=False,
        line=dict(color="rgba(0,0,0,0)"),
    )

    dash_html = build_dashboard(
        [ram_fig, swap_fig],
        n_cols=cols,
        height=height,
    ).to_html(full_html=False, include_plotlyjs="cdn")

    return f"""
    <html>
      <head>
        <title>Memory Inspector</title>
        <link rel="stylesheet" href="/static/mem.css">
      </head>
      <body style="font-family:sans-serif;">
        <div class="wrapper">
          <h1>Memory Inspector</h1>
          <p><b>Coverage:</b> {start} → {end} ({delta})</p>
          {dash_html}
          <p>
            <a class="pure-button" href="/api/v1/snapshot/level?lvl=0">
              Snapshot by level →
            </a>
          </p>
        </div>
      </body>
    </html>
    """
