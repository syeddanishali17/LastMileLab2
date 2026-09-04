"""Plotly OpenStreetMap figures. Lines are schematic, not road geometry."""

from __future__ import annotations

import math
from typing import Any

import plotly.graph_objects as go

from display import display_node, vehicle_colour

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
DEPOT_FILL = "#0f2744"
DEPOT_RING = "#d4a017"


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
    """Center + zoom. Do not use mapbox.bounds: it blanks OSM tiles in Streamlit."""
    south, north = min(lats), max(lats)
    west, east = min(lons), max(lons)
    lat_span = max(north - south, 0.02)
    lon_span = max(east - west, 0.02)
    span = max(lat_span, lon_span * _VIENNA_COS_LAT)
    if span > 0.30:
        zoom = 9.8
    elif span > 0.15:
        zoom = 10.5
    elif span > 0.08:
        zoom = 11.2
    else:
        zoom = 12.0
    return {
        "style": "open-street-map",
        "center": {"lat": (south + north) / 2, "lon": (west + east) / 2},
        "zoom": zoom,
    }


def _legend_layout() -> dict[str, Any]:
    return {
        "orientation": "h",
        "y": -0.14,
        "x": 0,
        "yanchor": "top",
        "bgcolor": "rgba(244,247,250,0.96)",
        "bordercolor": "#D7E0E8",
        "borderwidth": 1,
        "font": {"size": 12, "color": "#172B3A"},
    }


def _add_depot_marker(fig: go.Figure, latitude: float, longitude: float) -> None:
    """OSM Scattermapbox only reliably draws circles. Keep the depot dark, not white."""
    fig.add_trace(
        go.Scattermapbox(
            lat=[latitude],
            lon=[longitude],
            mode="markers",
            marker={"size": 22, "color": DEPOT_RING, "opacity": 1},
            hoverinfo="skip",
            showlegend=False,
            name="Depot ring",
        )
    )
    fig.add_trace(
        go.Scattermapbox(
            lat=[latitude],
            lon=[longitude],
            mode="markers+text",
            marker={"size": 14, "color": DEPOT_FILL, "opacity": 1},
            text=["Depot"],
            textposition="top right",
            textfont={"size": 13, "color": DEPOT_FILL, "family": "Arial Black"},
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
    fig.add_trace(
        go.Scattermapbox(
            lat=[customer["latitude"] for customer in customers],
            lon=[customer["longitude"] for customer in customers],
            mode="markers",
            marker={
                "size": [11 + customer["demand_totes"] * 1.3 for customer in customers],
                "color": "#1f4e79",
                "opacity": 1,
            },
            customdata=[
                [customer["customer_id"], customer["demand_totes"], customer.get("zone_id") or ""]
                for customer in customers
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Demand: %{customdata[1]} totes"
                "<br>Zone: %{customdata[2]}<extra></extra>"
            ),
            name="Customers",
        )
    )
    _add_depot_marker(fig, depot["latitude"], depot["longitude"])
    fig.update_layout(
        mapbox=_map_camera(lats, lons),
        margin={"l": 0, "r": 0, "t": 8, "b": 88},
        height=520,
        legend=_legend_layout(),
        hovermode="closest",
        paper_bgcolor="rgba(0,0,0,0)",
        template="none",
    )
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

    served = [
        row
        for row in customers.values()
        if row["customer_id"] not in unserved
        and row.get("latitude") is not None
        and row.get("longitude") is not None
    ]
    leftover = [
        row
        for row in customers.values()
        if row["customer_id"] in unserved
        and row.get("latitude") is not None
        and row.get("longitude") is not None
    ]
    if served:
        fig.add_trace(
            go.Scattermapbox(
                lat=[row["latitude"] for row in served],
                lon=[row["longitude"] for row in served],
                mode="markers",
                marker={
                    "size": [9 + row["demand_totes"] for row in served],
                    "color": "#6b7280",
                    "opacity": 1,
                },
                customdata=[[row["customer_id"], row["demand_totes"]] for row in served],
                hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} totes<extra></extra>",
                name="Customers",
            )
        )
    if leftover:
        fig.add_trace(
            go.Scattermapbox(
                lat=[row["latitude"] for row in leftover],
                lon=[row["longitude"] for row in leftover],
                mode="markers+text",
                marker={"size": 14, "color": "#c2410c"},
                text=[row["customer_id"] for row in leftover],
                textposition="top right",
                customdata=[[row["customer_id"], row["demand_totes"]] for row in leftover],
                hovertemplate=(
                    "<b>%{customdata[0]} unserved</b><br>%{customdata[1]} totes<extra></extra>"
                ),
                name="Unserved",
            )
        )

    for index, vehicle in enumerate(used):
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
        dlat, dlon = _fan_offset_index(index, len(used))
        route_lats = [lat + dlat for lat, _lon in points]
        route_lons = [lon + dlon for _lat, lon in points]
        colour = vehicle_colour(vehicle["vehicle_id"])
        hover = [
            f"{vehicle['vehicle_id']}: {display_node(origin)} → {display_node(dest)}"
            for origin, dest in zip(sequence, sequence[1:], strict=False)
        ]
        hover.append(hover[-1] if hover else vehicle["vehicle_id"])
        fig.add_trace(
            go.Scattermapbox(
                lat=route_lats,
                lon=route_lons,
                mode="lines",
                line={"width": 8, "color": "rgba(15, 23, 42, 0.75)"},
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scattermapbox(
                lat=route_lats,
                lon=route_lons,
                mode="lines",
                line={"width": 4.5, "color": colour},
                name=vehicle["vehicle_id"],
                hovertext=hover,
                hoverinfo="text",
                opacity=0.95,
            )
        )
        stop_lats = []
        stop_lons = []
        stop_text = []
        stop_hover = []
        customer_order = 0
        for node_id in sequence:
            if node_id not in customers:
                continue
            customer_order += 1
            lat, lon = coords[node_id]
            stop_lats.append(lat)
            stop_lons.append(lon)
            stop_text.append(str(customer_order))
            stop_hover.append(
                f"{vehicle['vehicle_id']} stop {customer_order}: {node_id} "
                f"({customers[node_id]['demand_totes']} totes)"
            )
        if stop_lats:
            fig.add_trace(
                go.Scattermapbox(
                    lat=stop_lats,
                    lon=stop_lons,
                    mode="markers+text",
                    marker={"size": 18, "color": colour},
                    text=stop_text,
                    textfont={"size": 11, "color": "white"},
                    textposition="middle center",
                    hovertext=stop_hover,
                    hoverinfo="text",
                    showlegend=False,
                    name=f"{vehicle['vehicle_id']} stops",
                )
            )

    _add_depot_marker(fig, depot["latitude"], depot["longitude"])
    fig.update_layout(
        mapbox=_map_camera(lats, lons),
        margin={"l": 0, "r": 0, "t": 8, "b": 96},
        height=640,
        legend=_legend_layout(),
        hovermode="closest",
        uirevision="route-map",
        paper_bgcolor="rgba(0,0,0,0)",
        template="none",
    )
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
            marker={"size": 16, "color": "#1f4e79"},
            text=[display_node(node_id) for node_id in customer_ids],
            textposition="top center",
            name="Customers",
            hoverinfo="text",
        )
    )
    if unserved:
        leftover = [
            node_id for node_id in unserved if node_id in LEARNING_DIAGRAM_POSITIONS
        ]
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
        plot_bgcolor="#F4F7FA",
        paper_bgcolor="#F4F7FA",
        template="none",
        uirevision="learning-schematic",
    )
    return fig


PLOTLY_MAP_CONFIG = {"scrollZoom": True, "displaylogo": False}
PLOTLY_CHART_KWARGS = {
    "use_container_width": True,
    "config": PLOTLY_MAP_CONFIG,
    "theme": None,
}
