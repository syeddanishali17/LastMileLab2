"""Plotly geographic figures on CARTO Positron. Lines are schematic, not road geometry."""

from __future__ import annotations

import math
from typing import Any

import plotly.graph_objects as go

from display import display_node, vehicle_colour
from i18n import t

LEARNING_DIAGRAM_POSITIONS = {
    "DEPOT_L6": (0.0, 0.0),
    "C1": (1.15, 0.55),
    "C2": (1.45, -0.35),
    "C3": (0.35, -1.15),
    "C4": (-0.95, -0.85),
    "C5": (-1.35, 0.15),
    "C6": (-0.55, 1.05),
}

DIAGRAM_CAPTION = (
    "Schematic node diagram. Node positions are teaching layout only. "
    "Distances come from the backend matrix, not from this drawing. This is not a map."
)

_VIENNA_COS_LAT = math.cos(math.radians(48.2))
# Plotly's named "carto-positron" still points at CartoDB Fastly rasters that CARTO
# now watermarks without an API key. The public Positron GL style is the token-free
# equivalent and keeps Scattermapbox + center/zoom camera behaviour.
BASE_MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
CUSTOMER_FILL = "#64748B"
DEPOT_FILL = "#102F46"
DEPOT_RING = "#FFFFFF"
ROUTE_HALO = "#FFFFFF"
ROUTE_LINE_WIDTH = 3.0
ROUTE_HALO_WIDTH = 4.4
ROUTE_LINE_OPACITY = 0.92
CUSTOMER_MARKER_SIZE = 10
CUSTOMER_HALO_SIZE = 13
STOP_MARKER_SIZE = 14
STOP_HALO_SIZE = 17
DEPOT_CORE_SIZE = 12
DEPOT_RING_SIZE = 17
UNSERVED_FILL = "#B42318"


def _finite_coords(
    lats: list[float | None],
    lons: list[float | None],
) -> tuple[list[float], list[float]]:
    pairs = [
        (float(lat), float(lon))
        for lat, lon in zip(lats, lons, strict=False)
        if lat is not None and lon is not None and math.isfinite(lat) and math.isfinite(lon)
    ]
    return [lat for lat, _lon in pairs], [lon for _lat, lon in pairs]


def _fan_offset_index(index: int, used_count: int) -> tuple[float, float]:
    """Nudge polylines so overlapping depot rays stay readable (~25 m)."""
    if used_count <= 1:
        return 0.0, 0.0
    angle = (2 * math.pi * index) / used_count
    metres = 28.0
    dlat = (metres * math.cos(angle)) / 111_000
    dlon = (metres * math.sin(angle)) / (111_000 * max(_VIENNA_COS_LAT, 0.2))
    return dlat, dlon


def _map_camera(lats: list[float], lons: list[float]) -> dict[str, Any]:
    """Center + zoom. Do not use mapbox.bounds: it can blank raster tiles in Streamlit."""
    south, north = min(lats), max(lats)
    west, east = min(lons), max(lons)
    lat_span = max(north - south, 0.02)
    lon_span = max(east - west, 0.02)
    # Fit every stop even in a narrow paired map. Same camera for both plans.
    zoom = min(
        math.log2(360 * 260 / (512 * lon_span)),
        math.log2(360 * 340 * _VIENNA_COS_LAT / (512 * lat_span)),
    )
    return {
        "style": BASE_MAP_STYLE,
        "center": {"lat": (south + north) / 2, "lon": (west + east) / 2},
        "zoom": zoom,
    }


def _scenario_revision(scenario: dict[str, Any], fallback: str) -> str:
    nested = scenario.get("scenario")
    if isinstance(nested, dict) and nested.get("scenario_id"):
        return str(nested["scenario_id"])
    if scenario.get("scenario_id"):
        return str(scenario["scenario_id"])
    depot = scenario.get("depot")
    if isinstance(depot, dict) and depot.get("scenario_id"):
        return str(depot["scenario_id"])
    return fallback


def _geo_layout(
    lats: list[float],
    lons: list[float],
    *,
    height: int,
    uirevision: str,
) -> dict[str, Any]:
    return {
        "mapbox": _map_camera(lats, lons),
        "margin": {"l": 0, "r": 0, "t": 4, "b": 0},
        "height": height,
        "showlegend": False,
        "hovermode": "closest",
        "uirevision": uirevision,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "template": "none",
        "hoverlabel": {
            "bgcolor": "#FFFFFF",
            "bordercolor": "#CCD9DF",
            "font": {"size": 13, "color": "#172B3A"},
        },
    }


def _legend_layout() -> dict[str, Any]:
    return {
        "orientation": "h",
        "y": 1.01,
        "x": 0,
        "yanchor": "bottom",
        "bgcolor": "rgba(234,241,243,0.96)",
        "bordercolor": "#CCD9DF",
        "borderwidth": 0,
        "font": {"size": 12, "color": "#172B3A"},
    }


def _scattermap(**kwargs: Any) -> go.Scattermapbox:
    kwargs.setdefault("showlegend", False)
    return go.Scattermapbox(**kwargs)


def _add_circle_halo(
    fig: go.Figure,
    lats: list[float],
    lons: list[float],
    *,
    size: float,
) -> None:
    fig.add_trace(
        _scattermap(
            lat=lats,
            lon=lons,
            mode="markers",
            marker={"size": size, "color": DEPOT_RING, "opacity": 1, "allowoverlap": True},
            hoverinfo="skip",
            name="halo",
        )
    )


def _customer_hover_template() -> str:
    return (
        f"<b>{t('ux.customer')} %{{customdata[0]}}</b><br>"
        f"{t('ux.map.demand')}: %{{customdata[1]}} totes"
        "<extra></extra>"
    )


def _stop_hover_text(
    customer_id: str,
    stop_number: int,
    demand_totes: int,
    vehicle_id: str,
) -> str:
    return (
        f"{t('ux.customer')} {customer_id}<br>"
        f"{t('ux.stop')} {stop_number}<br>"
        f"{t('ux.map.demand')}: {demand_totes} totes<br>"
        f"{t('ux.van')}: {vehicle_id}"
    )


def _add_depot_marker(fig: go.Figure, latitude: float, longitude: float) -> None:
    """Scattermapbox only reliably draws circles. Keep the depot navy and compact."""
    fig.add_trace(
        _scattermap(
            lat=[latitude],
            lon=[longitude],
            mode="markers",
            marker={
                "size": DEPOT_RING_SIZE,
                "color": DEPOT_RING,
                "opacity": 1,
                "allowoverlap": True,
            },
            hoverinfo="skip",
            name="Depot ring",
        )
    )
    fig.add_trace(
        _scattermap(
            lat=[latitude],
            lon=[longitude],
            mode="markers+text",
            marker={
                "size": DEPOT_CORE_SIZE,
                "color": DEPOT_FILL,
                "opacity": 1,
                "allowoverlap": True,
            },
            text=["Depot"],
            textposition="top right",
            textfont={"size": 12, "color": DEPOT_FILL, "family": "Arial"},
            name="Depot",
            hovertemplate="<b>Depot</b><extra></extra>",
        )
    )


def customer_map(scenario: dict[str, Any]) -> go.Figure:
    depot = scenario["depot"]
    customers = [
        customer
        for customer in scenario["customers"]
        if customer.get("latitude") is not None and customer.get("longitude") is not None
    ]
    lats, lons = _finite_coords(
        [depot["latitude"], *[customer["latitude"] for customer in customers]],
        [depot["longitude"], *[customer["longitude"] for customer in customers]],
    )
    if not lats:
        lats, lons = [48.17], [16.44]
    fig = go.Figure()
    if customers:
        customer_lats = [customer["latitude"] for customer in customers]
        customer_lons = [customer["longitude"] for customer in customers]
        _add_circle_halo(fig, customer_lats, customer_lons, size=CUSTOMER_HALO_SIZE)
        fig.add_trace(
            _scattermap(
                lat=customer_lats,
                lon=customer_lons,
                mode="markers",
                marker={
                    "size": CUSTOMER_MARKER_SIZE,
                    "color": CUSTOMER_FILL,
                    "opacity": 1,
                    "allowoverlap": True,
                },
                customdata=[
                    [customer["customer_id"], customer["demand_totes"]]
                    for customer in customers
                ],
                hovertemplate=_customer_hover_template(),
                name=t("ux.map.customers"),
            )
        )
    _add_depot_marker(fig, depot["latitude"], depot["longitude"])
    fig.update_layout(**_geo_layout(
        lats,
        lons,
        height=400,
        uirevision=_scenario_revision(scenario, "customers"),
    ))
    return fig


def route_map(
    scenario: dict[str, Any],
    routes_payload: dict[str, Any],
    unserved_ids: list[str] | None = None,
) -> go.Figure:
    depot = scenario["depot"]
    customers = {customer["customer_id"]: customer for customer in scenario["customers"]}
    unserved = set(unserved_ids or [])
    coords = {
        depot["depot_id"]: (depot["latitude"], depot["longitude"]),
        **{
            customer_id: (row["latitude"], row["longitude"])
            for customer_id, row in customers.items()
            if row.get("latitude") is not None and row.get("longitude") is not None
        },
    }
    used = [
        vehicle
        for vehicle in routes_payload.get("vehicle_kpis", [])
        if vehicle.get("is_used") and len(vehicle.get("sequence") or []) >= 2
    ]
    lats, lons = _finite_coords(
        [depot["latitude"], *[row["latitude"] for row in customers.values()]],
        [depot["longitude"], *[row["longitude"] for row in customers.values()]],
    )
    if not lats:
        lats, lons = [48.17], [16.44]
    fig = go.Figure()

    numbered: set[str] = set()
    polylines: list[tuple[str, str, list[float], list[float]]] = []
    stop_sets: list[tuple[str, list[float], list[float], list[str], list[str]]] = []
    for vehicle in used:
        sequence: list[str] = vehicle.get("sequence") or []
        points = [
            coords[node_id]
            for node_id in sequence
            if node_id in coords
            and coords[node_id][0] is not None
            and coords[node_id][1] is not None
        ]
        if len(points) < 2:
            continue
        route_lats = [lat for lat, _lon in points]
        route_lons = [lon for _lat, lon in points]
        colour = vehicle_colour(vehicle["vehicle_id"])
        polylines.append((vehicle["vehicle_id"], colour, route_lats, route_lons))
        stop_lats = []
        stop_lons = []
        stop_text = []
        stop_hover = []
        customer_order = 0
        for node_id in sequence:
            if node_id not in customers:
                continue
            customer_order += 1
            numbered.add(node_id)
            lat, lon = coords[node_id]
            stop_lats.append(lat)
            stop_lons.append(lon)
            stop_text.append(str(customer_order))
            stop_hover.append(
                _stop_hover_text(
                    node_id,
                    customer_order,
                    customers[node_id]["demand_totes"],
                    vehicle["vehicle_id"],
                )
            )
        if stop_lats:
            stop_sets.append((colour, stop_lats, stop_lons, stop_text, stop_hover))

    leftover = [
        row
        for row in customers.values()
        if row["customer_id"] in unserved
        and row.get("latitude") is not None
        and row.get("longitude") is not None
    ]
    unassigned = [
        row
        for row in customers.values()
        if row["customer_id"] not in numbered
        and row["customer_id"] not in unserved
        and row.get("latitude") is not None
        and row.get("longitude") is not None
    ]

    if unassigned:
        unassigned_lats = [row["latitude"] for row in unassigned]
        unassigned_lons = [row["longitude"] for row in unassigned]
        _add_circle_halo(fig, unassigned_lats, unassigned_lons, size=CUSTOMER_HALO_SIZE)
        fig.add_trace(
            _scattermap(
                lat=unassigned_lats,
                lon=unassigned_lons,
                mode="markers",
                marker={
                    "size": CUSTOMER_MARKER_SIZE,
                    "color": CUSTOMER_FILL,
                    "opacity": 1,
                    "allowoverlap": True,
                },
                customdata=[[row["customer_id"], row["demand_totes"]] for row in unassigned],
                hovertemplate=_customer_hover_template(),
                name=t("ux.map.customers"),
            )
        )
    if leftover:
        leftover_lats = [row["latitude"] for row in leftover]
        leftover_lons = [row["longitude"] for row in leftover]
        _add_circle_halo(fig, leftover_lats, leftover_lons, size=CUSTOMER_HALO_SIZE + 2)
        fig.add_trace(
            _scattermap(
                lat=leftover_lats,
                lon=leftover_lons,
                mode="markers+text",
                marker={
                    "size": CUSTOMER_MARKER_SIZE + 3,
                    "color": UNSERVED_FILL,
                    "opacity": 1,
                    "allowoverlap": True,
                },
                text=[row["customer_id"] for row in leftover],
                textposition="top right",
                customdata=[[row["customer_id"], row["demand_totes"]] for row in leftover],
                hovertemplate=(
                    f"<b>{t('ux.customer')} %{{customdata[0]}}</b><br>"
                    + t("ux.map.unserved")
                    + f"<br>{t('ux.map.demand')}: %{{customdata[1]}} totes<extra></extra>"
                ),
                name=t("ux.map.unserved"),
            )
        )

    for _vehicle_id, _colour, route_lats, route_lons in polylines:
        fig.add_trace(
            _scattermap(
                lat=route_lats,
                lon=route_lons,
                mode="lines",
                line={"width": ROUTE_HALO_WIDTH, "color": ROUTE_HALO},
                hoverinfo="skip",
                opacity=0.9,
                name="route-halo",
            )
        )
    for vehicle_id, colour, route_lats, route_lons in polylines:
        fig.add_trace(
            _scattermap(
                lat=route_lats,
                lon=route_lons,
                mode="lines",
                line={"width": ROUTE_LINE_WIDTH, "color": colour},
                name=vehicle_id,
                hoverinfo="skip",
                opacity=ROUTE_LINE_OPACITY,
            )
        )
    for colour, stop_lats, stop_lons, _stop_text, _stop_hover in stop_sets:
        _add_circle_halo(fig, stop_lats, stop_lons, size=STOP_HALO_SIZE)
    for colour, stop_lats, stop_lons, stop_text, stop_hover in stop_sets:
        fig.add_trace(
            _scattermap(
                lat=stop_lats,
                lon=stop_lons,
                mode="markers+text",
                marker={
                    "size": STOP_MARKER_SIZE,
                    "color": colour,
                    "opacity": 1,
                    "allowoverlap": True,
                },
                text=stop_text,
                textfont={"size": 10, "color": "#FFFFFF", "family": "Arial"},
                textposition="middle center",
                hovertext=stop_hover,
                hoverinfo="text",
                name=f"{colour} {t('ux.stops')}",
            )
        )

    _add_depot_marker(fig, depot["latitude"], depot["longitude"])
    fig.update_layout(**_geo_layout(
        lats,
        lons,
        height=430,
        uirevision=_scenario_revision(scenario, "route-map"),
    ))
    return fig


def learning_schematic(
    sequences: list[tuple[str, list[str]]],
    unserved_ids: list[str] | None = None,
) -> go.Figure:
    fig = go.Figure()
    unserved = set(unserved_ids or [])
    for vehicle_id, sequence in sequences:
        colour = vehicle_colour(vehicle_id)
        points = [
            LEARNING_DIAGRAM_POSITIONS[node_id]
            for node_id in sequence
            if node_id in LEARNING_DIAGRAM_POSITIONS
        ]
        if len(points) < 2:
            continue
        fig.add_trace(
            go.Scatter(
                x=[point[0] for point in points],
                y=[point[1] for point in points],
                mode="lines",
                line={"width": 10, "color": "rgba(255,255,255,0.95)"},
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[point[0] for point in points],
                y=[point[1] for point in points],
                mode="lines+markers",
                line={"width": 4, "color": colour},
                marker={"size": 9, "color": colour},
                name=vehicle_id,
                hovertemplate=f"{vehicle_id}: %{{x:.2f}}, %{{y:.2f}}<extra></extra>",
            )
        )
        for start, end in zip(points, points[1:], strict=False):
            fig.add_annotation(
                x=end[0],
                y=end[1],
                ax=start[0],
                ay=start[1],
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowwidth=2.2,
                arrowcolor=colour,
                standoff=10,
                startstandoff=8,
            )
        order = 0
        for node_id in sequence:
            if node_id.startswith("DEPOT") or node_id not in LEARNING_DIAGRAM_POSITIONS:
                continue
            order += 1
            x, y = LEARNING_DIAGRAM_POSITIONS[node_id]
            fig.add_annotation(
                x=x,
                y=y,
                text=str(order),
                showarrow=False,
                font={"size": 11, "color": "white"},
                bgcolor=colour,
                borderpad=3,
            )

    customer_ids = [
        node_id
        for node_id in LEARNING_DIAGRAM_POSITIONS
        if node_id not in unserved and not node_id.startswith("DEPOT")
    ]
    fig.add_trace(
        go.Scatter(
            x=[LEARNING_DIAGRAM_POSITIONS["DEPOT_L6"][0]],
            y=[LEARNING_DIAGRAM_POSITIONS["DEPOT_L6"][1]],
            mode="markers+text",
            marker={
                "size": 22,
                "color": DEPOT_FILL,
                "line": {"width": 3, "color": DEPOT_RING},
            },
            text=["Depot"],
            textposition="bottom center",
            name="Depot",
            hoverinfo="text",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[LEARNING_DIAGRAM_POSITIONS[node_id][0] for node_id in customer_ids],
            y=[LEARNING_DIAGRAM_POSITIONS[node_id][1] for node_id in customer_ids],
            mode="markers+text",
            marker={"size": 16, "color": CUSTOMER_FILL},
            text=[display_node(node_id) for node_id in customer_ids],
            textposition="top center",
            name="Customers",
            hoverinfo="text",
        )
    )
    if unserved:
        leftover = [node_id for node_id in unserved if node_id in LEARNING_DIAGRAM_POSITIONS]
        if leftover:
            fig.add_trace(
                go.Scatter(
                    x=[LEARNING_DIAGRAM_POSITIONS[node_id][0] for node_id in leftover],
                    y=[LEARNING_DIAGRAM_POSITIONS[node_id][1] for node_id in leftover],
                    mode="markers+text",
                    marker={"size": 20, "color": "#c2410c"},
                    text=[display_node(node_id) for node_id in leftover],
                    textposition="top center",
                    name="Unserved",
                )
            )
    fig.update_layout(
        title=None,
        xaxis={"visible": False, "range": [-1.9, 1.9]},
        yaxis={"visible": False, "scaleanchor": "x", "range": [-1.7, 1.6]},
        height=460,
        margin={"l": 20, "r": 20, "t": 16, "b": 80},
        legend=_legend_layout(),
        plot_bgcolor="#EAF1F3",
        paper_bgcolor="#EAF1F3",
        template="none",
        uirevision="learning-schematic",
    )
    return fig


PLOTLY_MAP_CONFIG = {"scrollZoom": False, "displaylogo": False}
PLOTLY_PLAN_MAP_CONFIG = {**PLOTLY_MAP_CONFIG, "displayModeBar": False}
PLOTLY_CHART_KWARGS = {
    "use_container_width": True,
    "config": PLOTLY_MAP_CONFIG,
    "theme": None,
}
PLOTLY_PLAN_CHART_KWARGS = {
    "use_container_width": True,
    "config": PLOTLY_PLAN_MAP_CONFIG,
    "theme": None,
}
