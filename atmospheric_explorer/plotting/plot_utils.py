"""
Plotting utilities.
"""
from __future__ import annotations

import re
from math import ceil, log10

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from atmospheric_explorer.loggers import get_logger
from atmospheric_explorer.utils import hex_to_rgb

logger = get_logger("atmexp")


def _add_ci(
    fig: go.Figure,
    trace: go.Figure,
    dataset: pd.DataFrame,
    labels: list[str],
) -> None:
    """Add confidence intervals to a plotly trace"""
    line_color = ",".join([str(n) for n in hex_to_rgb(trace.line.color)])
    if len(labels) > 1:
        regex = re.compile("label=(.+?)(?=<br>)")
        label = regex.search(trace.hovertemplate)[1]
    else:
        label = labels[0]
    label_index = labels.index(label)
    total_rows = ceil(len(labels) / 2)
    label_row = total_rows - label_index // 2
    label_col = label_index % 2 + 1
    df_label = dataset[dataset["label"] == label]
    times = df_label.index.tolist()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=df_label["lower"].to_list(),
            line_color=f"rgba({line_color}, 0)",
            fill=None,
            fillcolor=f"rgba({line_color}, 0.2)",
            showlegend=False,
            mode="lines",
            name=f"CI {trace.legendgroup}",
            legendgroup=f"CI {trace.legendgroup}",
            hovertemplate="Lower: %{y}<extra></extra>",
            hoverlabel={"bgcolor": f"rgba({line_color}, 0.2)"},
        ),
        row=label_row,
        col=label_col,
    )
    fig.add_trace(
        go.Scatter(
            x=times,
            y=df_label["upper"].to_list(),
            line_color=f"rgba({line_color}, 0)",
            fill="tonexty",
            fillcolor=f"rgba({line_color}, 0.2)",
            showlegend=False,
            mode="lines",
            name=f"CI {trace.legendgroup}",
            legendgroup=f"CI {trace.legendgroup}",
            hoverinfo="name+text+y",
            hovertemplate="Upper: %{y}<extra></extra>",
            hoverlabel={"bgcolor": f"rgba({line_color}, 0.2)"},
        ),
        row=label_row,
        col=label_col,
    )


def line_with_ci_subplots(
    dataset: pd.DataFrame,
    unit: str,
    title: str,
    add_ci: bool = False,
    color: str | None = None,
) -> go.Figure:
    """\
    Facet line plot on countries/administrative entinties.
    This function plots the yearly mean of a quantity along with its CI.

    Parameters:
        dataset (pd.DataFrame): pandas dataframe with (at least) columns
                                    'label','color','mean','lower','upper'
        col_num (int): number of maximum columns in the facet plot
        unit (str): unit of measure
        title (str): plot title
    """
    labels = sorted(dataset["label"].unique())
    colors = sorted(dataset[color].unique())
    if len(labels) > 1:
        fig = px.line(
            data_frame=dataset,
            y="value",
            color=color,
            facet_col="label",
            facet_col_wrap=(2 if len(labels) >= 2 else 1),
            facet_col_spacing=0.04,
            facet_row_spacing=0.15 if len(labels) > 3 else 0.2,
            color_discrete_sequence=px.colors.qualitative.D3,
            category_orders={f"{color}": colors, "label": labels},
        )
    else:
        fig = px.line(
            data_frame=dataset,
            y="value",
            color=color,
            color_discrete_sequence=px.colors.qualitative.D3,
            category_orders={f"{color}": colors},
        )
    if len(colors) <= 1:
        fig.update_layout(showlegend=False)
    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("label=")[-1], font={"size": 14})
    )
    fig.update_yaxes(title=unit, col=1)
    fig.update_yaxes(showticklabels=True, matches=None)
    fig.update_xaxes(showticklabels=True, matches=None)
    total_rows = ceil(len(labels) / 2)
    if len(labels) % 2 != 0:
        fig.update_xaxes(title="Year", col=2, row=total_rows)
    base_height = 220 if len(labels) >= 3 else 300
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "xref": "paper",
            "font": {"size": 19},
        },
        height=base_height * total_rows,
        hovermode="closest",
    )
    fig.update_traces(mode="lines+markers")
    if add_ci:
        fig.for_each_trace(
            lambda tr: _add_ci(
                fig,
                tr,
                dataset[dataset["color"] == tr.legendgroup],
                labels,
            )
        )
        fig.update_traces(
            selector=-2 * len(labels) - 1, showlegend=True
        )  # legend for ci
        fig.update_traces(selector=-1, showlegend=True)  # legend for ci
    return fig


def sequential_colorscale_bar(
    values: list[float] | list[int], colors: list[str]
) -> tuple[list, dict]:
    """Compute a sequential colorscale and colorbar form a list of values and a list of colors"""
    vals = np.array(values)
    vals.sort()
    separators = np.linspace(vals.min(), vals.max(), len(colors) + 1)
    separators_scaled = np.linspace(0, 1, len(colors) + 1)
    color_scale_custom = []
    for i, color in enumerate(colors):
        color_scale_custom.append([separators_scaled[i], color])
        color_scale_custom.append([separators_scaled[i + 1], color])
    tickvals = [
        np.mean(separators[k : k + 2]) for k in range(len(separators) - 1)
    ]  # position of tick text
    logger.debug("Separators for colorbar: %s", separators)
    if (separators.max() - separators.min()) < (len(separators) - 1):
        n_decimals = int(
            round(1 - log10(separators.max() / (len(separators) - 1)), 0)
        )  # number of decimals needed to distinguish color levels
        logger.debug("Colorbar decimals: %i", n_decimals)
        ticktext = (
            [f"<{separators[1]:.{n_decimals}f}"]
            + [
                f"{separators[k]:.{n_decimals}f}-{separators[k+1]:.{n_decimals}f}"
                for k in range(1, len(separators) - 2)
            ]
            + [f">{separators[-2]:.{n_decimals}f}"]
        )
    else:
        logger.debug("Colorbar decimals: 0")
        ticktext = (
            [f"<{separators[1]:.0f}"]
            + [
                f"{separators[k]:.0f}-{separators[k+1]:.0f}"
                for k in range(1, len(separators) - 2)
            ]
            + [f">{separators[-2]:.0f}"]
        )
    colorbar_custom = {
        "thickness": 25,
        "tickvals": tickvals,
        "ticktext": ticktext,
        "xpad": 0,
    }
    return color_scale_custom, colorbar_custom
