# src/interfaces/web/renderers/proc_tree.py

from __future__ import annotations

import html
from typing import List

import pandas as pd


COLS = (
    "PID", "PPID", "lifetime",
    "rss_min", "rss_mean",
    "rss_subtree_mean", "rss_subtree_max",
    "rss_max",
    "CMD",
)


def _format_row(row: pd.Series) -> str:
    """
    Return a single HTML <tr> element with escaped cells, except PID.

    Assumes PID cell may contain leading &nbsp; indentation.
    """
    cells: List[str] = []
    for col in COLS:
        val = str(row[col])
        val = val if col == "PID" else html.escape(val)
        cells.append(f"<td>{val}</td>")
    return f"<tr>{''.join(cells)}</tr>"


def build_proc_tree(df: pd.DataFrame) -> str:
    """
    Return an HTML table representing the process tree.

    Requires a 'level' column to indent the PID cell using non-breaking spaces.
    """
    html_rows: List[str] = []
    for _, row in df.iterrows():
        row = row.copy()
        indent = "&nbsp;" * 4 * int(row["level"])
        row["PID"] = f"{indent}{row['PID']}"
        html_rows.append(_format_row(row))

    head = "".join(f"<th>{col}</th>" for col in COLS)
    body = "".join(html_rows)
    return (
        "<table class='proc-table'>"
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"
    )
