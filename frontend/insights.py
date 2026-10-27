"""Operational read-outs derived from returned routes: search convergence, shift
timeline, driver hours and CO2e. Display-side estimates only; the planner still
optimises distance alone, and every assumption below is stated in the UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import plotly.graph_objects as go

from display import display_node, format_decimal, vehicle_colour
from i18n import t

# Illustrative operating assumptions for the morning wave (shown beside the charts).
DEPARTURE_MINUTE = 8 * 60
URBAN_SPEED_KMH = 25.0
SERVICE_MINUTES_PER_STOP = 5.0
# Order-of-magnitude well-to-wheel factor for a diesel light commercial van.
CO2E_KG_PER_KM = 0.27

INK = "#0C1424"
MUTED = "#56627A"
GRID = "#E3E8F2"
PRIMARY = "#4F46E5"
BASELINE = "#64748B"
FONT = "Inter, Segoe UI, system-ui, sans-serif"


@dataclass(frozen=True)
class Segment:
    vehicle_id: str
    kind: str  # "drive" or "service"
    start_min: float
    minutes: float
    node_id: str
    distance_m: int = 0
    demand: int = 0


@dataclass(frozen=True)
class ShiftSummary:
    segments: list[Segment]
    return_minute: float | None
    driver_hours: float
    co2e_kg: float


def clock(minute: float) -> str:
    minute = int(round(minute))
    return f"{minute // 60 % 24:02d}:{minute % 60:02d}"


def drive_minutes(metres: float) -> float:
    return metres / 1000 / URBAN_SPEED_KMH * 60


def shift_summary(routes: dict[str, Any]) -> ShiftSummary:
    """Lay every used route on a clock: drive each leg, then serve the stop."""
    by_vehicle: dict[str, list[dict[str, Any]]] = {}
    for stop in routes.get("stops") or []:
        by_vehicle.setdefault(stop["vehicle_id"], []).append(stop)
    segments: list[Segment] = []
    returns: list[float] = []
    total_minutes = 0.0
    total_metres = 0
    for vehicle_id in sorted(by_vehicle):
        stops = sorted(by_vehicle[vehicle_id], key=lambda stop: stop["sequence_number"])
        if not any(stop.get("node_type") == "customer" for stop in stops):
            continue
        now = float(DEPARTURE_MINUTE)
        for stop in stops[1:]:
            leg = int(stop.get("leg_distance_metres") or 0)
            total_metres += leg
            minutes = drive_minutes(leg)
            segments.append(Segment(vehicle_id, "drive", now, minutes, stop["node_id"], leg))
            now += minutes
            if stop.get("node_type") == "customer":
                segments.append(
                    Segment(
                        vehicle_id,
                        "service",
                        now,
                        SERVICE_MINUTES_PER_STOP,
                        stop["node_id"],
                        demand=int(stop.get("demand_totes") or 0),
                    )
                )
                now += SERVICE_MINUTES_PER_STOP
        returns.append(now)
        total_minutes += now - DEPARTURE_MINUTE
    return ShiftSummary(
        segments=segments,
        return_minute=max(returns) if returns else None,
        driver_hours=total_minutes / 60,
        co2e_kg=total_metres / 1000 * CO2E_KG_PER_KM,
    )


def _axis(**extra: Any) -> dict[str, Any]:
    return {
        "showgrid": True,
        "gridcolor": GRID,
        "zeroline": False,
        "automargin": True,
        "linecolor": GRID,
        "tickfont": {"size": 12, "color": MUTED, "family": FONT},
        "title": {"font": {"size": 12, "color": MUTED, "family": FONT}},
        **extra,
    }


def _base_layout(height: int) -> dict[str, Any]:
    return {
        "height": height,
        "margin": {"l": 8, "r": 16, "t": 12, "b": 8},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": FONT, "color": INK},
        "hoverlabel": {
            "bgcolor": "#FFFFFF",
            "bordercolor": "#DCE2EE",
            "font": {"size": 13, "color": INK, "family": FONT},
        },
        "template": "none",
    }


def convergence_figure(
    trace: list[dict[str, Any]],
    *,
    baseline_m: int | None,
    time_limit_s: float | None,
) -> go.Figure | None:
    """Best-so-far route distance against search time (log scale, milliseconds)."""
    if not trace:
        return None
    # A log axis cannot show t=0, so the first incumbent sits at 0.1 ms at the earliest.
    xs = [max(float(point["elapsed_seconds"]) * 1000, 0.1) for point in trace]
    ys = [point["objective_distance_metres"] / 1000 for point in trace]
    end_ms = max(xs[-1] * 1.5, float(time_limit_s or 0) * 1000)
    fig = go.Figure()
    if baseline_m:
        fig.add_hline(
            y=baseline_m / 1000,
            line={"color": BASELINE, "width": 1.5, "dash": "dash"},
            annotation={
                "text": t("ux.insight.conv.baseline"),
                "font": {"size": 12, "color": MUTED},
                "xanchor": "right",
                "x": 1,
                "yanchor": "bottom",
            },
        )
    fig.add_trace(
        go.Scatter(
            x=xs + [end_ms],
            y=ys + [ys[-1]],
            mode="lines",
            line={"color": PRIMARY, "width": 2, "shape": "hv"},
            fill="tozeroy",
            fillcolor="rgba(99, 102, 241, 0.07)",
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            marker={"size": 8, "color": PRIMARY, "line": {"color": "#FFFFFF", "width": 2}},
            customdata=[[index + 1, format_decimal(y, 3)] for index, y in enumerate(ys)],
            hovertemplate=(
                f"<b>{t('ux.insight.conv.hover')} %{{customdata[0]}}</b><br>"
                "%{x:.1f} ms · %{customdata[1]} km<extra></extra>"
            ),
            showlegend=False,
        )
    )
    low = min(ys + ([baseline_m / 1000] if baseline_m else []))
    high = max(ys + ([baseline_m / 1000] if baseline_m else []))
    pad = max((high - low) * 0.12, 0.5)
    fig.update_layout(
        **_base_layout(300),
        xaxis=_axis(type="log", title={"text": t("ux.insight.conv.x")}, ticksuffix=" ms"),
        yaxis=_axis(
            title={"text": t("ux.insight.conv.y")},
            range=[low - pad * 1.5, high + pad],
            ticksuffix=" km",
        ),
        hovermode="closest",
    )
    return fig


def timeline_figure(summary: ShiftSummary) -> go.Figure | None:
    """Gantt of each van's morning: coloured drive legs, dark service stops."""
    if not summary.segments:
        return None
    vehicles = sorted({segment.vehicle_id for segment in summary.segments}, reverse=True)
    fig = go.Figure()
    for vehicle_id in sorted(vehicles):
        drives = [s for s in summary.segments if s.vehicle_id == vehicle_id and s.kind == "drive"]
        fig.add_trace(
            go.Bar(
                y=[vehicle_id] * len(drives),
                x=[s.minutes for s in drives],
                base=[s.start_min for s in drives],
                orientation="h",
                name=vehicle_id,
                marker={
                    "color": vehicle_colour(vehicle_id),
                    "line": {"color": "#FFFFFF", "width": 1},
                },
                customdata=[
                    [
                        clock(s.start_min),
                        format_decimal(s.distance_m / 1000, 1),
                        round(s.minutes),
                        display_node(s.node_id),
                    ]
                    for s in drives
                ],
                hovertemplate=(
                    f"<b>{vehicle_id}</b> · {t('ux.insight.time.drive')} → %{{customdata[3]}}<br>"
                    "%{customdata[0]} · %{customdata[1]} km · %{customdata[2]} min<extra></extra>"
                ),
                width=0.56,
            )
        )
    services = [s for s in summary.segments if s.kind == "service"]
    fig.add_trace(
        go.Bar(
            y=[s.vehicle_id for s in services],
            x=[s.minutes for s in services],
            base=[s.start_min for s in services],
            orientation="h",
            name=t("ux.insight.time.service"),
            marker={"color": INK, "line": {"color": "#FFFFFF", "width": 1}},
            customdata=[[clock(s.start_min), s.node_id, s.demand] for s in services],
            hovertemplate=(
                f"<b>%{{y}}</b> · {t('ux.insight.time.service')} %{{customdata[1]}}<br>"
                f"%{{customdata[0]}} · %{{customdata[2]}} {t('ux.plan.totes')}<extra></extra>"
            ),
            width=0.56,
        )
    )
    start = DEPARTURE_MINUTE
    end = summary.return_minute or start + 60
    ticks = list(range(start, int(end) + 31, 30))
    fig.update_layout(
        **_base_layout(64 + 46 * len(vehicles)),
        barmode="overlay",
        bargap=0.3,
        showlegend=True,
        legend={
            "orientation": "h",
            "y": 1.02,
            "yanchor": "bottom",
            "x": 0,
            "font": {"size": 12, "color": INK},
            "bgcolor": "rgba(0,0,0,0)",
        },
        xaxis=_axis(
            tickvals=ticks,
            ticktext=[clock(tick) for tick in ticks],
            range=[start - 4, end + 6],
        ),
        yaxis=_axis(
            showgrid=False,
            categoryorder="array",
            categoryarray=vehicles,
            tickfont={"size": 12, "color": INK, "family": FONT},
        ),
    )
    fig.update_layout(margin={"l": 8, "r": 16, "t": 36, "b": 8})
    return fig


def hours_label(hours: float) -> str:
    total = int(round(hours * 60))
    return f"{total // 60} h {total % 60:02d} m"
