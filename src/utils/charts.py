"""Reusable Plotly chart builders for consistent styling across pages."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = px.colors.qualitative.Set2
TEMPLATE = "plotly_white"


def line(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "") -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, template=TEMPLATE, title=title,
                  color_discrete_sequence=PALETTE)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    return fig


def bar(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = "",
        orientation: str = "v") -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, template=TEMPLATE, title=title,
                 orientation=orientation, color_discrete_sequence=PALETTE)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    return fig


def grouped_bar(df: pd.DataFrame, x: str, y: str, color: str, title: str = "") -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, barmode="group", template=TEMPLATE,
                 title=title, color_discrete_sequence=PALETTE)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    return fig


def pie(df: pd.DataFrame, names: str, values: str, title: str = "") -> go.Figure:
    fig = px.pie(df, names=names, values=values, template=TEMPLATE, title=title,
                 color_discrete_sequence=PALETTE, hole=0.45)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


def heatmap(df: pd.DataFrame, x: str, y: str, z: str, title: str = "") -> go.Figure:
    pivot = df.pivot(index=y, columns=x, values=z)
    fig = px.imshow(pivot, template=TEMPLATE, title=title, color_continuous_scale="Blues",
                    aspect="auto", text_auto=".0f")
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig
