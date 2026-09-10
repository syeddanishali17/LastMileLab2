"""Presentation regressions, independent of mathematical expectations."""

from pathlib import Path
from unittest.mock import MagicMock

import api_client
import components
import state
from api_client import ApiError, is_missing_run
from display import (
    VEHICLE_COLOURS,
    format_sequence,
    plan_comparison_summary,
    plans_comparable,
    scenario_label,
)
from maps import (
    BASE_MAP_STYLE,
    CUSTOMER_FILL,
    DEPOT_FILL,
    PLOTLY_CHART_KWARGS,
    PLOTLY_MAP_CONFIG,
    PLOTLY_PLAN_CHART_KWARGS,
    PLOTLY_PLAN_MAP_CONFIG,
    ROUTE_HALO_WIDTH,
    ROUTE_LINE_WIDTH,
    _map_camera,
    customer_map,
    route_map,
)
from state import PLANNER_RUN_KEYS, clear_planner_runs, ensure_session


def test_connection_errors_do_not_instruct_localhost_api() -> None:
    ui_source = Path("frontend/components.py").read_text(encoding="utf-8")
    client_source = Path("frontend/api_client.py").read_text(encoding="utf-8")
    assert "PLANNING_START_CMD" not in ui_source
    assert "127.0.0.1" not in ui_source
    assert "Start Uvicorn" not in client_source
    assert "port 8000 first" not in client_source


def test_route_palette_and_camera_are_comparable():
    assert VEHICLE_COLOURS[:4] == ["#2563EB", "#D8893B", "#6775C9", "#C026D3"]
    assert len(set(VEHICLE_COLOURS[:4])) == 4
    camera = _map_camera([48.12, 48.30], [16.28, 16.55])
    assert camera == _map_camera([48.30, 48.12], [16.55, 16.28])
    assert camera["style"] == BASE_MAP_STYLE
    assert "positron" in BASE_MAP_STYLE
    assert "open-street-map" not in BASE_MAP_STYLE
    assert camera["zoom"] < 10
    assert PLOTLY_MAP_CONFIG["scrollZoom"] is False
    assert "displayModeBar" not in PLOTLY_MAP_CONFIG
    assert PLOTLY_PLAN_MAP_CONFIG["scrollZoom"] is False
    assert PLOTLY_PLAN_MAP_CONFIG["displayModeBar"] is False
    assert PLOTLY_CHART_KWARGS["config"] is PLOTLY_MAP_CONFIG
    assert PLOTLY_PLAN_CHART_KWARGS["config"] is PLOTLY_PLAN_MAP_CONFIG
    assert 2.8 <= ROUTE_LINE_WIDTH <= 3.2
    assert 4.0 <= ROUTE_HALO_WIDTH <= 4.5
    assert CUSTOMER_FILL == "#64748B"
    assert DEPOT_FILL == "#102F46"


def _geo_scenario() -> dict:
    return {
        "scenario_id": "VIENNA_STANDARD_24",
        "depot": {"depot_id": "DEPOT", "latitude": 48.17, "longitude": 16.44},
        "customers": [
            {
                "customer_id": "C01",
                "latitude": 48.18,
                "longitude": 16.45,
                "demand_totes": 8,
                "zone_id": "Z1",
            },
            {
                "customer_id": "C02",
                "latitude": 48.19,
                "longitude": 16.46,
                "demand_totes": 5,
                "zone_id": "Z2",
            },
            {
                "customer_id": "C03",
                "latitude": 48.205,
                "longitude": 16.47,
                "demand_totes": 4,
                "zone_id": "Z3",
            },
        ],
    }


def _route_payload(*sequences: tuple[str, list[str]]) -> dict:
    return {
        "vehicle_kpis": [
            {
                "vehicle_id": vehicle_id,
                "sequence": sequence,
                "is_used": len(sequence) >= 2,
                "customer_count": max(len(sequence) - 2, 0),
                "assigned_demand_totes": 0,
                "capacity_totes": 80,
                "remaining_capacity_totes": 80,
                "route_distance_metres": 1000,
            }
            for vehicle_id, sequence in sequences
        ]
    }


def test_geographic_maps_use_shared_carto_positron() -> None:
    frontend = Path("frontend")
    maps_src = (frontend / "maps.py").read_text(encoding="utf-8")
    assert "BASE_MAP_STYLE =" in maps_src
    assert "positron-gl-style" in maps_src
    assert '"style": BASE_MAP_STYLE' in maps_src
    assert "open-street-map" not in maps_src
    assert "cartodb-basemaps" not in maps_src
    assert "mapbox_style" not in maps_src
    for path in frontend.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "open-street-map" not in source
        if path.name != "maps.py":
            assert "positron-gl-style" not in source
            assert "carto-positron" not in source
            assert "mapbox_style" not in source
    inspector = Path("frontend/pages/4_Model_Inspector.py").read_text(encoding="utf-8")
    assert "plotly_chart" not in inspector
    assert "route_map" not in inspector
    assert "customer_map" not in inspector
    assert "mapboxgl-ctrl-attrib" not in components.THEME_CSS
    assert "maplibregl-ctrl-attrib" not in components.THEME_CSS
    assert ".mapboxgl-ctrl { display: none" not in components.THEME_CSS


def test_customer_and_route_maps_share_camera_hover_and_semantics() -> None:
    scenario = _geo_scenario()
    baseline = route_map(
        scenario,
        _route_payload(
            ("V01", ["DEPOT", "C01", "C02", "DEPOT"]),
            ("V02", ["DEPOT", "DEPOT"]),
        ),
    )
    optimised = route_map(
        scenario,
        _route_payload(("V01", ["DEPOT", "C02", "C01", "DEPOT"])),
        unserved_ids=["C03"],
    )
    geography = customer_map(scenario)
    for figure in (geography, baseline, optimised):
        assert figure.layout.mapbox.style == BASE_MAP_STYLE
        assert figure.layout.showlegend is False
        assert figure.layout.uirevision == "VIENNA_STANDARD_24"
        hover = " ".join(
            str(trace.hovertemplate or "") + " " + " ".join(trace.hovertext or [])
            for trace in figure.data
        )
        assert "Zone" not in hover
        assert "w_ik" not in hover
        assert "heuristic" not in hover
        assert "solver" not in hover.lower()
    assert geography.layout.mapbox.center == baseline.layout.mapbox.center
    assert baseline.layout.mapbox.center == optimised.layout.mapbox.center
    assert geography.layout.mapbox.zoom == baseline.layout.mapbox.zoom
    assert baseline.layout.mapbox.zoom == optimised.layout.mapbox.zoom
    assert baseline.layout.height == optimised.layout.height
    customer_hover = " ".join(str(trace.hovertemplate or "") for trace in geography.data)
    assert "Customer %{customdata[0]}" in customer_hover
    assert "Demand: %{customdata[1]} totes" in customer_hover
    depot_hover = [trace.hovertemplate for trace in geography.data if trace.hovertemplate]
    assert any(template == "<b>Depot</b><extra></extra>" for template in depot_hover)
    stop_hover = " ".join(
        " ".join(trace.hovertext)
        for trace in baseline.data
        if trace.hovertext
    )
    assert "Customer C01" in stop_hover
    assert "Stop 1" in stop_hover
    assert "Demand: 8 totes" in stop_hover
    assert "Vehicle: V01" in stop_hover
    assert "Customer C02" in stop_hover
    assert "Stop 2" in stop_hover
    line_widths = [
        float(trace.line.width)
        for trace in baseline.data
        if trace.mode == "lines" and trace.line and trace.line.width is not None
    ]
    assert ROUTE_HALO_WIDTH in line_widths
    assert ROUTE_LINE_WIDTH in line_widths
    route_colours = [
        trace.line.color
        for trace in baseline.data
        if trace.mode == "lines" and trace.name == "V01"
    ]
    assert route_colours == [VEHICLE_COLOURS[0]]
    stop_text = [
        list(trace.text)
        for trace in baseline.data
        if trace.mode == "markers+text" and trace.text and list(trace.text) == ["1", "2"]
    ]
    assert stop_text == [["1", "2"]]
    unserved_hover = " ".join(str(trace.hovertemplate or "") for trace in optimised.data)
    assert "Unserved" in unserved_hover
    other = customer_map({**scenario, "scenario_id": "VIENNA_LARGE_40"})
    assert other.layout.uirevision == "VIENNA_LARGE_40"
    assert other.layout.uirevision != geography.layout.uirevision
    nested = customer_map(
        {
            "scenario": {"scenario_id": "VIENNA_WIDE_24"},
            "depot": scenario["depot"],
            "customers": scenario["customers"],
        }
    )
    assert nested.layout.uirevision == "VIENNA_WIDE_24"
    depot_only = customer_map(
        {
            "depot": {**scenario["depot"], "scenario_id": "VIENNA_TIGHT_24"},
            "customers": scenario["customers"],
        }
    )
    assert depot_only.layout.uirevision == "VIENNA_TIGHT_24"


def test_export_does_not_fetch_on_ordinary_rerun(monkeypatch):
    ui = MagicMock()
    ui.session_state = {}
    ui.button.return_value = False
    ui.columns.return_value = [MagicMock(), MagicMock()]
    fetch = MagicMock()
    monkeypatch.setattr(components, "st", ui)
    monkeypatch.setattr(components, "call_api", fetch)
    components.export_buttons("run-1", visible=True)
    fetch.assert_not_called()


def test_numeric_table_formats_and_vehicle_key(monkeypatch):
    ui = MagicMock()
    monkeypatch.setattr(components, "st", ui)
    components.static_table(
        [{"Vehicle": "V01", "Distance": "30.101 km", "Stops": 6}],
        numeric_columns={"Distance", "Stops"},
        row_header="Vehicle",
    )
    markup = ui.markdown.call_args.args[0]
    assert '<td class="lm-num">30.101 km</td>' in markup
    assert VEHICLE_COLOURS[0] in markup
    assert 'scope="row"' in markup


def test_plan_sequence_uses_readable_arrows_and_depot_label():
    assert format_sequence(["DEPOT", "C022", "DEPOT"]) == "Depot → C022 → Depot"


def test_plan_page_does_not_hardcode_vienna_standard_figures() -> None:
    source = Path("frontend/pages/3_Baseline_vs_Optimised.py").read_text(encoding="utf-8")
    helper = Path("frontend/display.py").read_text(encoding="utf-8")
    assert "122.394" not in source
    assert "97.193" not in source
    assert "20.6" not in source
    assert 't("ux.optimised")' not in source.replace('t("ux.optimised.short")', "")
    assert "Optimized solution (OR-Tools)" not in source
    summary_src = helper.split("def plan_comparison_summary")[1].split("def operational_summary")[0]
    assert "122.394" not in summary_src


def test_plan_comparison_maps_precede_route_details() -> None:
    source = Path("frontend/pages/3_Baseline_vs_Optimised.py").read_text(encoding="utf-8")
    side_src = source.split("def render_plan_side")[1].split("def render_comparison")[0]
    compare_src = source.split("def render_comparison")[1].split("def render_detail")[0]
    assert "vehicle_summary" not in side_src
    assert "route_sequences" not in side_src
    assert "plotly_chart" in side_src
    assert "render_feasible_status" not in side_src
    assert "ux.plan.feasible" not in side_src
    assert "ux.plan.reduction" not in side_src
    assert "ux.plan.total" not in side_src
    assert "panel_distance" in side_src
    assert 't("ux.baseline")' in side_src
    assert "ux.optimised.short" in side_src
    assert 'key="plan-pair"' in compare_src
    assert "vehicle_summary" in compare_src
    assert 't("ux.plan.view.baseline")' in compare_src
    assert 't("ux.plan.view.optimised")' in compare_src
    assert "render_route_legend" in compare_src
    assert compare_src.count("render_route_legend") == 1
    pair_at = compare_src.find('key="plan-pair"')
    legend_at = compare_src.find("render_route_legend")
    details_at = compare_src.find('key="plan-route-details"')
    validation_at = compare_src.find('t("ux.plan.validation")')
    assert pair_at < legend_at < details_at < validation_at


def test_plan_comparison_divider_css() -> None:
    css = components.THEME_CSS
    assert "--lm-border: #CCD9DF" in css
    pair_rule = css.split(
        '.st-key-plan-pair [data-testid="stHorizontalBlock"] {', 1
    )[1].split("}", 1)[0]
    assert "position: relative" in pair_rule
    divider = css.split(
        '.st-key-plan-pair [data-testid="stHorizontalBlock"]::after {', 1
    )[1].split("}", 1)[0]
    assert "width: 1px" in divider
    assert "background: #CCD9DF" in divider
    assert "left: 50%" in divider
    assert "translateX(-50%)" in divider
    stacked = css.split("@media (max-width: 1220px)", 1)[1].split("@media", 1)[0]
    assert "flex-direction: column" in stacked
    stacked_divider = stacked.split(
        '.st-key-plan-pair [data-testid="stHorizontalBlock"]::after {', 1
    )[1].split("}", 1)[0]
    assert "display: none" in stacked_divider
    stacked_first = stacked.split(
        '.st-key-plan-pair [data-testid="stColumn"]:first-child {', 1
    )[1].split("}", 1)[0]
    assert "border-bottom: 1px solid #CCD9DF" in stacked_first


def test_custom_scenario_label_is_friendly() -> None:
    assert scenario_label("GEN_abc123") == "Custom scenario"
    assert scenario_label("VIENNA_STANDARD_24") == "Vienna Standard"
    assert scenario_label("VIENNA_TIGHT_24") == "Vienna Tight Capacity"


def _run(**fields):
    payload = {
        "scenario_id": "DEMO",
        "comparison_eligible": True,
        "status": "feasible",
        "objective_distance_metres": 80000,
        "customers_served": 12,
        "customers_total": 12,
        "distance_improvement_percentage": None,
    }
    payload.update(fields)
    return payload


def test_plan_comparison_summary_interpolates_run_values() -> None:
    lead, detail = plan_comparison_summary(
        _run(),
        _run(objective_distance_metres=64000, distance_improvement_percentage=20.0),
    )
    assert detail is None
    assert lead == (
        "Optimized routing reduced estimated fleet distance by 20.0% while serving all "
        "12 customers."
    )
    assert "80.000" not in lead
    assert "64.000" not in lead
    assert "122.394" not in lead
    assert "97.193" not in lead
    assert "OR-Tools" not in lead
    assert "optimal" not in lead.lower()


def test_plan_comparison_summary_interpolates_german(monkeypatch) -> None:
    import i18n

    monkeypatch.setattr(i18n, "current_language", lambda: "de")
    lead, detail = plan_comparison_summary(
        _run(),
        _run(objective_distance_metres=64000, distance_improvement_percentage=20.0),
    )
    assert detail is None
    assert lead == (
        "Die optimierte Tourenplanung senkte die geschätzte Flottendistanz um 20,0 % "
        "und bediente alle 12 Kunden."
    )
    assert "20.6" not in lead
    assert "OR-Tools" not in lead


def test_plan_comparison_summary_incomplete_baseline_omits_reduction() -> None:
    lead, detail = plan_comparison_summary(
        _run(
            comparison_eligible=False,
            status="heuristic_incomplete",
            objective_distance_metres=None,
            customers_served=5,
            customers_total=6,
        ),
        _run(
            objective_distance_metres=31000,
            customers_served=6,
            customers_total=6,
        ),
    )
    assert "one or both route plans are incomplete" in lead
    assert "baseline route plan is incomplete" not in lead
    assert "Both plans serve all" not in lead
    assert "%" not in lead
    assert detail is not None
    assert "Baseline: 5 / 6 customers served · Incomplete plan" in detail
    assert "Optimized: 6 / 6 customers served · Feasible plan" in detail
    assert "heuristic_incomplete" not in detail
    assert not plans_comparable(
        _run(comparison_eligible=False, status="heuristic_incomplete"),
        _run(),
    )


def test_plan_comparison_summary_optimized_incomplete_uses_generic_fallback() -> None:
    lead, detail = plan_comparison_summary(
        _run(),
        _run(
            comparison_eligible=False,
            status="no_solution_found",
            objective_distance_metres=None,
            customers_served=0,
            distance_improvement_percentage=None,
        ),
    )
    assert "one or both route plans are incomplete" in lead
    assert "baseline route plan is incomplete" not in lead
    assert detail is not None
    assert "Baseline: 12 / 12 customers served · Feasible plan" in detail
    assert "Optimized: 0 / 12 customers served · No complete solution found" in detail
    assert "no_solution_found" not in detail
    assert "heuristic_incomplete" not in f"{lead}\n{detail}"


def test_plan_comparison_summary_both_incomplete_shows_both_statuses() -> None:
    lead, detail = plan_comparison_summary(
        _run(
            comparison_eligible=False,
            status="heuristic_incomplete",
            customers_served=5,
            customers_total=6,
        ),
        _run(
            comparison_eligible=False,
            status="no_solution_found",
            customers_served=0,
            customers_total=6,
        ),
    )
    assert "complete route comparison is not available" in lead
    assert detail is not None
    assert "Incomplete plan" in detail
    assert "No complete solution found" in detail
    assert "%" not in lead


def test_plan_comparison_summary_rejects_mismatched_runs() -> None:
    lead, detail = plan_comparison_summary(
        _run(scenario_id="A", customers_total=12),
        _run(
            scenario_id="B",
            customers_total=12,
            objective_distance_metres=64000,
            distance_improvement_percentage=20.0,
        ),
    )
    assert "reduced estimated fleet distance" not in lead
    assert "one or both route plans are incomplete" in lead
    assert detail is not None
    mismatched = plan_comparison_summary(
        _run(customers_total=12),
        _run(customers_total=24, distance_improvement_percentage=20.0),
    )
    assert "reduced estimated fleet distance" not in mismatched[0]
    assert not plans_comparable(_run(customers_total=12), _run(customers_total=24))


def test_plan_shared_legend_uses_vehicle_palette_once() -> None:
    source = Path("frontend/pages/3_Baseline_vs_Optimised.py").read_text(encoding="utf-8")
    maps_src = Path("frontend/maps.py").read_text(encoding="utf-8")
    legend_src = source.split("def render_route_legend")[1].split("def vehicle_summary")[0]
    compare_src = source.split("def render_comparison")[1].split("def render_detail")[0]
    assert 'ROUTE_LEGEND_VEHICLES = ("V01", "V02", "V03", "V04")' in source
    assert "VEHICLE_COLOURS" in legend_src
    assert "lm-plan-legend" in legend_src
    assert "ux.plan.map.numbers" in legend_src
    assert compare_src.count("render_route_legend") == 1
    detail_src = source.split("def render_detail")[1]
    assert "render_route_legend()" in detail_src
    assert 'st.caption(t("ux.plan.map.numbers"))' not in source
    assert "showlegend=False" in maps_src
    assert ".lm-plan-legend" in components.THEME_CSS
    assert ".lm-plan-legend-note" in components.THEME_CSS
    assert ".lm-plan-verdict" in components.THEME_CSS
    assert ".lm-plan-distance" in components.THEME_CSS


def test_scenarios_generate_action_order() -> None:
    source = Path("frontend/pages/1_Dispatch_Setup.py").read_text(encoding="utf-8")
    builder = source.split("def custom_builder")[1].split("def render_search_limit")[0]
    search_at = builder.index("render_search_limit()")
    generate_at = builder.index('t("ux.generate")')
    reset_at = builder.index('t("ux.custom.reset")')
    ready_at = builder.index('t("ux.custom.ready")')
    assert search_at < generate_at < reset_at < ready_at
    generate_line = builder[generate_at : generate_at + 180]
    reset_line = builder[reset_at : reset_at + 160]
    assert 'type="primary"' in generate_line
    assert 'type="secondary"' in reset_line
    assert '_banner("ready"' in builder
    assert 'key="_search_seconds"' in source
    assert 't("ux.run")' in source
    assert 'type="primary"' in source.split("def run_comparison_button")[1]


def test_plan_validation_uses_passed_failed_labels() -> None:
    source = Path("frontend/pages/3_Baseline_vs_Optimised.py").read_text(encoding="utf-8")
    matrix_src = source.split("def validation_matrix")[1].split("def validation_list")[0]
    list_src = source.split("def validation_list")[1].split("def render_exports")[0]
    assert "ux.plan.check.passed" in source
    assert "ux.plan.check.failed" in source
    assert "check_result_cell" in matrix_src
    assert "check_outcome_label" in list_src
    assert "'✓'" not in matrix_src
    assert "'✗'" not in matrix_src
    assert "'✓'" not in list_src
    assert "'✗'" not in list_src
    assert 'kind = "is-pass"' in source
    assert "is-fail" in source


def test_overview_animation_teaches_baseline_versus_optimized():
    markup = components.cvrp_animation_html(
        "122.4 km → 97.2 km · 20.6% shorter",
        "diagram",
    )
    assert "lm-cvrp-panel" in markup
    assert "lm-cvrp-compare" in markup
    assert 'class="lm-cvrp-pane lm-cvrp-pane-baseline"' in markup
    assert 'class="lm-cvrp-pane lm-cvrp-pane-optimized"' in markup
    assert markup.count("lm-cvrp-pane-baseline") == 1
    assert markup.count("lm-cvrp-pane-optimized") == 1
    assert markup.count("<svg") == 2
    assert "Nearest-neighbour baseline" in markup
    assert "Optimized solution" in markup
    assert "122.4 km" in markup
    assert "97.2 km" in markup
    assert "Total distance: 122.4 km" not in markup
    assert "Total distance: 97.2 km" not in markup
    assert ">1</text>" in markup
    assert ">2</text>" in markup
    assert ">3</text>" in markup
    assert markup.count(">C1</text>") == 2
    assert markup.count(">C12</text>") == 2
    assert "lm-cvrp-ids" in markup
    assert "lm-cvrp-dot-nn" not in markup
    assert "lm-cvrp-dot-opt" not in markup
    assert "lm-nn-track" not in markup
    assert "lm-opt-track" not in markup
    assert "◂" not in components.THEME_CSS
    assert "lm-cvrp-route-tracks" in markup
    assert "lm-cvrp-cust" in markup
    assert "lm-cvrp-arr-0-0-0" not in markup
    assert "lm-cvrp-arr-1-3-2" not in markup
    assert 'fill="#64748B"' not in markup
    assert "r=\"10.5\" fill=" not in markup
    assert "@keyframes lm-cvrp-arr-0-0-0" not in components.THEME_CSS
    assert "fill: var(--lm-visit)" in components.THEME_CSS
    assert markup.count('class="lm-cvrp-cust') == 24
    assert "5s linear infinite" not in components.THEME_CSS
    assert "lm-cvrp-running" in markup
    assert 'type="button"' in markup
    assert "lm-cvrp-replay" in markup
    assert "Replay comparison" in markup
    assert "Pause animations" not in markup
    assert ".lm-num" in components.THEME_CSS
    assert "text-align: right" in components.THEME_CSS
    assert "animation: none" in components.THEME_CSS
    assert ".lm-route-motif::before" not in components.THEME_CSS
    assert "lm-hero-mark" in components.THEME_CSS
    assert "width: 92px" in components.THEME_CSS
    assert "width: 123px" not in components.THEME_CSS
    assert "margin-left: 0" in components.THEME_CSS
    assert "padding: 0 24px" in components.THEME_CSS
    assert "max-width: none" in components.THEME_CSS
    assert "text-align: justify" not in components.THEME_CSS
    assert "font-size: 18px" in components.THEME_CSS
    assert markup.find('class="lm-cvrp-pane-title"') < markup.find("<svg")
    assert "padding-top: 0" in components.THEME_CSS
    assert ".lm-proof-kicker" in components.THEME_CSS
    assert ".lm-overview-flag" in components.THEME_CSS
    assert ".lm-about" in components.THEME_CSS
    assert ".lm-about-body" in components.THEME_CSS
    assert ".lm-about-title" in components.THEME_CSS
    assert "grid-template-columns: minmax(0, 0.34fr) minmax(0, 0.66fr)" in components.THEME_CSS
    assert "max-width: 720px" in components.THEME_CSS
    assert "width: 88%" not in components.THEME_CSS
    assert ".lm-concept {" in components.THEME_CSS
    assert ".lm-concept-grid .lm-card > p" not in components.THEME_CSS
    assert ".lm-concept-grid .lm-card .lm-info-text" not in components.THEME_CSS
    concept_rule = components.THEME_CSS.split(".lm-concept {", 1)[1].split("}", 1)[0]
    assert "box-shadow: none" in concept_rule
    assert "border-top" not in concept_rule
    assert "border: none" in concept_rule
    assert "border-radius: 0" in concept_rule
    assert "repeat(4, minmax(0, 1fr))" in components.THEME_CSS
    assert "clamp(40px, 2.5vw, 42px)" in components.THEME_CSS
    assert "clamp(28px, 2.4vw, 34px)" not in components.THEME_CSS
    assert "clamp(27px, 2.6vw, 35px)" not in components.THEME_CSS
    assert "clamp(1.75rem, 2.6vw, 2.25rem)" not in components.THEME_CSS
    assert "lm-cvrp-note" not in markup
    assert "Illustrative published reference only" not in markup
    assert "st-key-scenario_presets" in components.THEME_CSS
    assert ".lm-check-title" in components.THEME_CSS
    assert 'stSidebar"][aria-expanded="true"]' in components.THEME_CSS
    assert "248px" in components.THEME_CSS
    assert ".lm-preview-surface" in components.THEME_CSS
    assert ".lm-custom-secondary" in components.THEME_CSS
    assert ".lm-offline-title" in components.THEME_CSS
    assert ".lm-feas-card.is-pass" in components.THEME_CSS
    assert ".lm-feas-card.is-fail" in components.THEME_CSS
    assert "st-key-scenario-preview" in components.THEME_CSS
    assert 'stElementContainer"]:has(.lm-scenarios-flag)' not in components.THEME_CSS
    assert ".st-key-custom-configure { margin-top: 0; }" in components.THEME_CSS
    assert ".lm-custom-configure-gap" in components.THEME_CSS
    assert "font-size: 19px" in components.THEME_CSS
    assert ".st-key-plan-inspect button" in components.THEME_CSS
    assert ".lm-plan-matrix" in components.THEME_CSS
    assert ".st-key-plan_view" in components.THEME_CSS
    assert "st-key-_search_seconds" in components.THEME_CSS
    assert "st-key-inspect_plan" in components.THEME_CSS
    assert "stBaseButton-segmented_controlActive" in components.THEME_CSS
    plan_view_css = components.THEME_CSS.split(
        ".stApp:has(.lm-plan-flag) .st-key-plan_view", 1
    )[1]
    assert "background: var(--lm-teal) !important" in plan_view_css
    assert "min-height: 44px !important" in plan_view_css
    assert "outline: 3px solid var(--lm-focus) !important" in plan_view_css
    assert ".st-key-scenario-generate" in components.THEME_CSS
    assert ".st-key-method-inspect" in components.THEME_CSS
    assert ".lm-plan-heading" in components.THEME_CSS
    assert ".lm-plan-method-break" not in components.THEME_CSS
    assert "ux.plan.excel" not in components.THEME_CSS
    assert ".st-key-plan-pair .lm-table" in components.THEME_CSS
    assert ".st-key-plan-route-details" in components.THEME_CSS
    assert "@media (max-width: 1449px)" not in components.THEME_CSS
    assert "@media (max-width: 1220px)" in components.THEME_CSS
    assert "st-key-demand-editor" in components.THEME_CSS
    assert "max-width: 580px" in components.THEME_CSS
    dt_css = components.THEME_CSS.split(".stApp .lm-preview-stats dt {", 1)[1].split("}", 1)[0]
    dd_css = components.THEME_CSS.split(".stApp .lm-preview-stats dd {", 1)[1].split("}", 1)[0]
    assert "font-size: 12.5px" in dt_css
    assert "font-size: 11px" in dd_css
    assert "var(--lm-muted)" in dt_css
    assert "var(--lm-navy)" in dd_css


def test_overview_route_story_is_one_shot_and_sequential():
    css = components.THEME_CSS
    markup = components.cvrp_animation_html("97.2 km", "diagram")
    assert "animation: lm-pane-route 5s linear infinite" not in css
    assert "lm-cvrp-arr-" not in css
    assert "lm-cvrp-arr-" not in markup
    assert "opacity:.75" not in css
    assert "cx:" not in css.split("@keyframes lm-cust-activate", 1)[1].split("@keyframes", 1)[0]
    assert "cy:" not in css.split("@keyframes lm-cust-activate", 1)[1].split("@keyframes", 1)[0]
    assert ".lm-cvrp-running .lm-cvrp-pane-baseline .lm-cvrp-routes path {" in css
    assert "animation-name: lm-baseline-soften;" in css
    assert "animation-delay: 1.6s;" in css
    assert "animation-iteration-count: 1;" in css
    assert "animation-fill-mode: forwards;" in css
    assert "path:nth-child(1)" in css
    assert "path:nth-child(2)" in css
    assert "path:nth-child(3)" in css
    assert "path:nth-child(4)" in css
    assert "animation-delay: 2.0s;" in css
    assert "animation-delay: 2.8s;" in css
    assert "animation-delay: 3.6s;" in css
    assert "animation-delay: 4.4s;" in css
    assert "animation-delay: 5.2s;" in css
    assert "@keyframes lm-opt-reveal" in css
    assert "from { stroke-dashoffset: 100; opacity: 0; }" in css
    assert "to { stroke-dashoffset: 0; opacity: 1; }" in css
    assert "to { opacity: 0.6; }" in css
    assert ".lm-cvrp-pane-baseline .lm-cvrp-routes path { opacity: 0.6 !important; }" in css
    assert ".lm-cvrp-pane-optimized .lm-cvrp-pane-km { opacity: 1 !important; }" in css
    assert ".lm-motion-tools, .lm-cvrp-replay-tools { display: none; }" in css
    assert "button.lm-cvrp-replay" in css
    assert "type=\"button\"" in markup
    assert "hidden" in markup
    assert "classList.remove(\"lm-cvrp-running\")" in markup
    assert "classList.add(\"lm-cvrp-running\")" in markup
    assert "animation-iteration-count: infinite" not in css.split(".lm-cvrp-running", 1)[1].split(
        ".lm-motion-tools", 1
    )[0]
    assert components.CVRP_STORY_MS == 6200
    assert "var STORY_MS = 6200;" in components._CVRP_STORY_JS
    method = components.methodology_animation_html()
    assert "Pause animations" in method
    assert "lm-motion-pause" in method
    assert "Replay comparison" not in method


def test_overview_page_puts_animation_and_cta_before_concept_cards():
    source = Path("frontend/pages/0_Overview.py").read_text(encoding="utf-8")
    header_at = source.index("page_header(")
    proof_at = source.index("render_overview_reference_proof(")
    animation_at = source.index("render_cvrp_animation(")
    cta_at = source.index('st.button(t("ux.over.cta")')
    cards_at = source.index("concept_cards(")
    footer_at = source.index("render_footer()")
    about_at = source.index("render_overview_about()")
    assert header_at < proof_at < animation_at < cta_at < cards_at < about_at < footer_at
    assert source.count("concept_cards(") == 1
    assert source.count('st.button(t("ux.over.cta")') == 1
    assert source.count("render_cvrp_animation(") == 1
    assert source.count("render_overview_reference_proof(") == 1
    assert "extra=" not in source
    assert "ux.over.feas.hero" not in source
    assert "ux.over.compare.body" not in source
    assert "author=" not in source
    assert "ux.over.author" not in source
    assert "kpi_cards" not in source
    assert "ux.over.proof.tech" not in source
    assert "Customers served" not in source
    assert "st.page_link" not in source
    assert "ux.over.method" not in source
    assert source.count("ux.over.compare.title") == 1
    assert source.count("ux.over.vrp.tip") == 1
    assert source.count("ux.over.vrp.title") == 1
    assert source.count("ux.over.cvrp.title") == 1
    assert source.count("ux.over.feas.title") == 1
    assert source.count("ux.over.compare.label") == 1
    css = components.THEME_CSS
    proof_rule = css.split(".lm-overview-proof {", 1)[1].split("}", 1)[0]
    assert "box-shadow: none" in proof_rule
    assert "border: none" in proof_rule
    assert ".stApp:has(.lm-overview-flag) .lm-hero-route" in css
    assert "animation: lm-hero-route 7s ease-in-out infinite" in css
    markup = components.cvrp_animation_html("97.2 km", "diagram")
    cap_at = markup.index('class="lm-cvrp-cap"')
    replay_at = markup.index("lm-cvrp-replay")
    panel_end = markup.index("</div>", replay_at)
    assert cap_at < replay_at < panel_end
    assert markup.count("lm-cvrp-replay") >= 1
    assert 'type="button"' in markup
    assert "lm-motion-control" not in markup
    assert markup.count("st.button") == 0


def test_overview_reference_proof_is_lightweight_typography(monkeypatch):
    monkeypatch.setattr(
        components,
        "t",
        lambda key: {
            "ux.over.proof.kicker": "REFERENCE SCENARIO",
            "ux.over.proof.scenario": "Vienna Standard",
            "ux.over.proof.line": (
                "122.394 km → 97.193 km · 20.6% shorter · 24/24 customers served"
            ),
        }[key],
    )
    markup = components.overview_reference_proof_html()
    assert 'class="lm-overview-proof"' in markup
    assert 'class="lm-proof-kicker">REFERENCE SCENARIO</p>' in markup
    assert 'class="lm-proof-name">Vienna Standard</p>' in markup
    assert "122.394 km → 97.193 km" in markup
    assert "20.6% shorter" in markup
    assert "24/24 customers served" in markup
    assert "Reference scenario · Vienna Standard" not in markup
    assert "Vienna Standard 24" not in markup
    assert "lm-card" not in markup
    assert "style=" not in markup
    assert "optimal route" not in markup.lower()
    ui = MagicMock()
    monkeypatch.setattr(components, "st", ui)
    components.render_overview_reference_proof()
    ui.markdown.assert_called_once()
    assert ui.markdown.call_args.kwargs["unsafe_allow_html"] is True
    assert ui.markdown.call_args.args[0] == markup


def test_hero_author_stays_inside_html_without_blank_gaps(monkeypatch):
    ui = MagicMock()
    monkeypatch.setattr(components, "st", ui)
    components.page_header(
        "Title",
        "Intro paragraph.",
        kicker="CVRP",
        extra=["Objective paragraph.", "Comparison paragraph."],
        compact=False,
    )
    markup = ui.markdown.call_args.args[0]
    assert "lm-hero-author" not in markup
    assert "A portfolio project by Syed Danish Ali" not in markup
    assert "</p>\n" not in markup.split('class="lm-hero-copy">', 1)[1]
    assert markup.count("<p class=") + markup.count("<p>") >= 3
    assert markup.strip().endswith("</div>")
    ui = MagicMock()
    monkeypatch.setattr(components, "st", ui)
    components.concept_cards(
        [("Minimize fleet travel", "Minimize the total estimated distance travelled.")]
    )
    markup = ui.markdown.call_args.args[0]
    assert 'class="lm-concept-grid"' in markup
    assert 'class="lm-concept"' in markup
    assert "lm-card" not in markup
    assert 'class="lm-info"' not in markup
    assert "ⓘ" not in markup
    assert "<details" not in markup
    assert "<abbr" not in markup
    assert "lm-tip" not in markup
    assert "Minimize fleet travel" in markup
    assert "Minimize the total estimated distance travelled." in markup
    hover_rule = components.THEME_CSS.split(".lm-concept:hover,", 1)[1].split("}", 1)[0]
    assert "transform: none" in hover_rule
    assert "box-shadow: none" in hover_rule
    assert "translateY" not in hover_rule
    assert "cursor: pointer" not in hover_rule


def test_p0g_overview_visual_locks():
    overview = Path("frontend/pages/0_Overview.py").read_text(encoding="utf-8")
    css = components.THEME_CSS
    markup = components.cvrp_animation_html(
        "122.4 km → 97.2 km · 20.6% shorter",
        "diagram",
    )
    proof = components.overview_reference_proof_html()
    assert "REFERENCE SCENARIO" in proof or "ux.over.proof.kicker" in overview
    assert "lm-proof-name" in proof
    assert "Vienna Standard 24" not in proof
    assert "Vienna Standard 24" not in markup
    assert "Wien Standard 24" not in markup
    assert "VIENNA_STANDARD_24" in Path("frontend/workflow_copy.py").read_text(encoding="utf-8")
    assert "ROUTE COMPARISON" in markup
    assert "Baseline versus optimized" in markup
    assert "for the same scenario." in markup
    heading_at = markup.index('class="lm-cvrp-heading"')
    lead_at = markup.index('class="lm-cvrp-lead"')
    intro_copy_close = markup.index("</div>", heading_at)
    assert heading_at < lead_at < intro_copy_close
    intro_rule = css.split(".lm-cvrp-intro {", 1)[1].split("}", 1)[0]
    assert "display: block" in intro_rule
    assert "justify-content: space-between" not in intro_rule
    lead_rule = css.split(".lm-cvrp-lead {", 1)[1].split("}", 1)[0]
    assert "text-align: left" in lead_rule
    assert "text-align: right" not in lead_rule
    assert "max-width: 640px" in lead_rule
    about_rule = css.split(".stApp:has(.lm-overview-flag) .lm-about {", 1)[1].split("}", 1)[0]
    assert "text-align: left" in about_rule
    assert "text-align: center" not in about_rule
    assert "One comparison frame keeps both planning states visible" not in markup
    assert 'class="lm-cvrp-frame"' in markup
    assert markup.count('class="lm-cvrp-frame"') == 1
    assert "lm-cvrp-well" in markup
    assert markup.count("lm-cvrp-well") == 2
    assert "BASELINE" in markup
    assert "OPTIMIZED" in markup
    assert "OPTIMIZED SOLUTION" not in markup
    assert "122.4 km" in markup
    assert "97.2 km" in markup
    assert components.CVRP_STORY_MS == 6200
    assert "lm-cvrp-running" in markup
    assert "classList.remove(\"lm-cvrp-running\")" in markup
    assert "--lm-surface-soft: #EAF1F3" in css
    assert "--lm-well: #F7FAFB" in css
    assert "--lm-border: #CCD9DF" in css
    assert "--lm-teal-hover: #096864" in css
    assert "background: var(--lm-teal) !important" in css
    assert "st-key-overview-cta" in css
    assert 'key="overview-cta"' in overview
    assert "#184866" in css
    assert "3px solid #62D6C8" in css
    assert "3px solid transparent" in css
    assert ".stApp:has(.lm-overview-flag) [data-testid=\"stSidebarNavLink\"][href$=\"/\"]" in css
    assert "[href*=\"/scenarios\"]" in css
    assert ".stApp:has(.lm-plan-flag) [data-testid=\"stSidebarNavLink\"][href*=\"/plan\"]" in css
    assert "st.radio(" in Path("frontend/components.py").read_text(encoding="utf-8")
    assert "planning_availability()" in Path("frontend/components.py").read_text(encoding="utf-8")
    assert ".lm-api-status" in css
    assert ".lm-api-dot" in css
    assert "#087A5A" in css
    concept_rule = css.split(".lm-concept {", 1)[1].split("}", 1)[0]
    assert "border-top" not in concept_rule
    assert "box-shadow: none" in concept_rule
    home = Path("frontend/Home.py").read_text(encoding="utf-8")
    assert "st.navigation(" in home
    assert 'position="sidebar"' in home
    scenarios = Path("frontend/pages/1_Dispatch_Setup.py").read_text(encoding="utf-8")
    plan = Path("frontend/pages/3_Baseline_vs_Optimised.py").read_text(encoding="utf-8")
    method = Path("frontend/pages/6_Methodology.py").read_text(encoding="utf-8")
    inspect = Path("frontend/pages/4_Model_Inspector.py").read_text(encoding="utf-8")
    assert "lm-cvrp-section" not in scenarios
    assert "lm-cvrp-section" not in plan
    assert "lm-cvrp-section" not in method
    assert "lm-cvrp-section" not in inspect
    assert "render_plan_verdict" in plan
    assert "st.segmented_control(" in plan
    assert 'key="plan_view"' in plan
    assert 'st.button(t("ux.method.inspect")' in method
    assert "st.page_link" not in method
    assert "pages/4_Model_Inspector.py" in method
    assert "inspect.subtitle" in inspect
    footer_src = Path("frontend/components.py").read_text(encoding="utf-8")
    assert "https://www.linkedin.com/in/syeddanishali16/" in footer_src
    assert "https://github.com/syeddanishali17/LastMileLab2" in footer_src
    brand = Path("frontend/assets/brand.svg").read_text(encoding="utf-8")
    assert 'rx="7"' not in brand
    assert 'rx="7"' not in components.HERO_MARK_SVG
    assert 'class="lm-hero-mark"' in components.HERO_MARK_SVG
    assert "truck" not in brand.lower()
    assert "<rect width=\"32\" height=\"32\"" not in brand


def test_p0g1_rhythm_motion_and_shared_primitives():
    css = components.THEME_CSS
    running = css.split(".lm-cvrp-running", 1)[1].split(".lm-motion-tools", 1)[0]
    nav_rule = css.split('[data-testid="stSidebarNavLink"] {', 1)[1].split("}", 1)[0]
    hover_rule = css.split('[data-testid="stSidebarNavLink"]:hover {', 1)[1].split("}", 1)[0]
    active_rule = css.split(
        '[data-testid="stSidebarNavLink"][aria-current="page"],', 1
    )[1].split("}", 1)[0]
    primary_rule = css.split(".stButton > button[kind=\"primary\"]", 1)[1].split("}", 1)[0]
    overview_width = css.split(
        ".stApp:has(.lm-overview-flag) [data-testid=\"stMainBlockContainer\"] {", 1
    )[1].split("}", 1)[0]
    assert components.CVRP_STORY_MS == 6200
    assert f"var STORY_MS = {components.CVRP_STORY_MS};" in components._CVRP_STORY_JS
    assert "animation-iteration-count: infinite" not in running
    assert "animation-iteration-count: 1;" in running
    assert "animation-fill-mode: forwards;" in running
    assert components._CVRP_DEPOT == (320, 185)
    assert components._CVRP_NN_ROUTES == [
        ("#2563EB", [(200, 70), (445, 65), (140, 95)]),
        ("#D8893B", [(520, 100), (175, 145), (500, 250)]),
        ("#6775C9", [(485, 155), (125, 245), (545, 285)]),
        ("#C026D3", [(430, 295), (200, 265), (155, 305)]),
    ]
    assert components._CVRP_OPT_ROUTES == [
        ("#2563EB", [(200, 70), (140, 95), (175, 145)]),
        ("#D8893B", [(445, 65), (520, 100), (485, 155)]),
        ("#6775C9", [(500, 250), (545, 285), (430, 295)]),
        ("#C026D3", [(200, 265), (125, 245), (155, 305)]),
    ]
    assert "max-width: 1300px" in overview_width
    assert "background: var(--lm-teal) !important" in primary_rule
    assert "--lm-teal: #0B7A75" in css
    assert "--lm-teal-hover: #096864" in css
    assert "font-size: 14.5px !important" in nav_rule
    assert "font-weight: 500 !important" in nav_rule
    assert "rgba(255, 255, 255, 0.06)" in hover_rule
    assert "#184866" in active_rule
    assert "3px solid #62D6C8" in active_rule
    assert "rgba(79, 209, 197, 0.10)" not in hover_rule
    assert ".stApp:has(.lm-overview-flag)" in css
    assert "lm-cvrp-section" not in Path("frontend/pages/1_Dispatch_Setup.py").read_text(
        encoding="utf-8"
    )


def test_overview_about_and_footer_markup(monkeypatch):
    ui = MagicMock()
    monkeypatch.setattr(components, "st", ui)
    monkeypatch.setattr(
        components,
        "t",
        lambda key: {
            "ux.over.about.kicker": "ABOUT THIS PROJECT",
            "ux.over.about.title": "Built to make routing decisions inspectable",
            "ux.over.about.body1": (
                "LastMile Lab is an independent portfolio project by Syed Danish Ali that applies "
                "capacitated vehicle routing to a synthetic last-mile delivery case."
            ),
            "ux.over.about.body2": (
                "It brings together scenario design, route optimization, API-based planning, "
                "solution verification, and a bilingual interactive interface in one inspectable "
                "workflow."
            ),
            "ux.over.about.stack": "CVRP · Python · FastAPI · Streamlit",
            "footer": "© 2026 Syed Danish Ali · LastMile Lab",
        }[key],
    )
    components.render_overview_about()
    markup = ui.markdown.call_args.args[0]
    assert 'class="lm-about"' in markup
    assert 'class="lm-about-left"' in markup
    assert 'class="lm-about-right"' in markup
    assert 'class="lm-about-kicker">ABOUT THIS PROJECT</div>' in markup
    assert 'class="lm-about-title">Built to make routing decisions inspectable</h2>' in markup
    assert "Syed Danish Ali" in markup
    assert "CVRP · Python · FastAPI · Streamlit" in markup
    assert "lm-card" not in markup
    assert "lm-hero-author" not in markup
    assert "</div>\n" not in markup
    assert "linkedin.com" not in markup
    assert "github.com" not in markup
    components.render_footer()
    footer = ui.markdown.call_args.args[0]
    assert "© 2026 Syed Danish Ali · LastMile Lab" in footer
    assert "Syed Danish Ali" in footer
    assert "LastMile Lab" in footer
    assert "LinkedIn" in footer
    assert "GitHub" in footer
    assert 'href="https://www.linkedin.com/in/syeddanishali16/"' in footer
    assert 'href="https://github.com/syeddanishali17/LastMileLab2"' in footer
    assert 'href="mailto:danishraza16@icloud.com"' in footer
    assert "danishraza16@icloud.com" in footer
    assert footer.count('target="_blank"') == 2
    assert footer.count('rel="noopener noreferrer"') == 2
    assert 'aria-label="Syed Danish Ali on LinkedIn"' in footer
    assert 'aria-label="LastMile Lab source code on GitHub">' in footer
    assert 'aria-label="Email Syed Danish Ali at danishraza16@icloud.com"' in footer
    assert footer == (
        '<div class="lm-footer">'
        '<span class="lm-footer-copy">© 2026 Syed Danish Ali · LastMile Lab</span>'
        '<span class="lm-footer-links">'
        '<a class="lm-footer-link" href="https://www.linkedin.com/in/syeddanishali16/" '
        'target="_blank" rel="noopener noreferrer" '
        'aria-label="Syed Danish Ali on LinkedIn">LinkedIn</a>'
        '<span class="lm-footer-sep" aria-hidden="true"> · </span>'
        '<a class="lm-footer-link" href="https://github.com/syeddanishali17/LastMileLab2" '
        'target="_blank" rel="noopener noreferrer" '
        'aria-label="LastMile Lab source code on GitHub">GitHub</a>'
        '<span class="lm-footer-sep" aria-hidden="true"> · </span>'
        '<a class="lm-footer-link" href="mailto:danishraza16@icloud.com" '
        'aria-label="Email Syed Danish Ali at danishraza16@icloud.com">'
        "danishraza16@icloud.com</a>"
        "</span>"
        "</div>"
    )
    footer_link_css = components.THEME_CSS.split(".lm-footer a {", 1)[1].split("}", 1)[0]
    assert "border-radius: 999px" not in footer_link_css
    assert "box-shadow" not in footer_link_css
    assert "gradient" not in footer_link_css.lower()


def test_term_placeholders_do_not_nest_inside_titles():
    markup = components.with_terms(
        "A search limit returns the best feasible solution.",
        [
            ("search limit", "tip.search"),
            ("feasible solution", "tip.feasible"),
        ],
    )
    assert markup.count("<abbr") == 2
    assert 'title="' in markup
    assert "<abbr" not in markup.split('title="', 1)[1].split('"', 1)[0]


def test_methodology_animation_shows_assignment_and_sequencing():
    markup = components.methodology_animation_html()
    assert "lm-assign" in markup
    assert "Assignment and sequencing under capacity" in markup
    assert "Spreadsheet formulation" in markup
    assert "lm-cons-grid .lm-card:nth-child(n+4)" in components.THEME_CSS


def _vienna_payload(*, status: str = "passed") -> dict:
    return {
        "scenario": {"scenario_id": "VIENNA_STANDARD_24", "customer_count": 24},
        "precheck": {"status": status},
        "customers": [],
    }


def _install_ui(monkeypatch, *, offline: bool | None = False) -> MagicMock:
    ui = MagicMock()
    ui.session_state = {} if offline is None else {"_planning_offline": offline}
    monkeypatch.setattr(components, "st", ui)
    return ui


def test_health_probe_uses_short_timeout_and_succeeds(monkeypatch) -> None:
    seen: dict[str, float] = {}

    class Response:
        is_success = True

    def fake_get(url, timeout):
        seen["url"] = url
        seen["timeout"] = timeout
        return Response()

    monkeypatch.setattr("httpx.get", fake_get)
    assert components.HEALTH_PROBE_TIMEOUT_SECONDS == 0.6
    assert components.planning_service_up() is True
    assert seen["timeout"] == 0.6
    assert seen["url"].endswith("/health")


def test_quick_health_success_keeps_vienna_run_ready(monkeypatch) -> None:
    ui = _install_ui(monkeypatch)
    payload = _vienna_payload()
    get_scenario = MagicMock(return_value=payload)
    monkeypatch.setattr(components, "planning_service_up", lambda: True)
    monkeypatch.setattr(api_client, "get_scenario", get_scenario)

    loaded = components.fetch_preset_scenario("VIENNA_STANDARD_24")
    assert loaded is payload
    assert components.comparison_ready(loaded)
    get_scenario.assert_called_once_with("VIENNA_STANDARD_24")
    ui.spinner.assert_not_called()
    ui.empty.assert_not_called()
    assert ui.session_state.get("_planning_offline") is False


def test_failed_health_recovers_when_scenario_request_succeeds(monkeypatch) -> None:
    ui = _install_ui(monkeypatch, offline=False)
    payload = _vienna_payload()
    get_scenario = MagicMock(return_value=payload)
    monkeypatch.setattr(components, "planning_service_up", lambda: False)
    monkeypatch.setattr(api_client, "get_scenario", get_scenario)

    loaded = components.fetch_preset_scenario("VIENNA_STANDARD_24")
    assert loaded is payload
    assert components.comparison_ready(loaded)
    get_scenario.assert_called_once_with("VIENNA_STANDARD_24")
    ui.spinner.assert_called_once()
    assert "Planning service is starting" in ui.spinner.call_args.args[0]
    assert ui.session_state.get("_planning_offline") is False
    assert "Render" not in components._starting_notice_html()
    assert "cold start" not in components._starting_notice_html().lower()


def test_failed_health_and_failed_request_are_unavailable(monkeypatch) -> None:
    ui = _install_ui(monkeypatch, offline=False)
    get_scenario = MagicMock(
        side_effect=ApiError("Planning service unavailable.", kind="timeout")
    )
    monkeypatch.setattr(components, "planning_service_up", lambda: False)
    monkeypatch.setattr(api_client, "get_scenario", get_scenario)

    loaded = components.fetch_preset_scenario("VIENNA_STANDARD_24")
    assert loaded is None
    assert not components.comparison_ready(loaded)
    assert ui.session_state["_planning_offline"] is True
    get_scenario.assert_called_once_with("VIENNA_STANDARD_24")
    ui.warning.assert_not_called()
    ui.exception.assert_not_called()

    loaded_again = components.fetch_preset_scenario("VIENNA_STANDARD_24")
    assert loaded_again is None
    get_scenario.assert_called_once()


def test_run_comparison_stays_blocked_for_failed_precheck(monkeypatch) -> None:
    _install_ui(monkeypatch)
    payload = _vienna_payload(status="infeasible")
    monkeypatch.setattr(components, "planning_service_up", lambda: True)
    monkeypatch.setattr(api_client, "get_scenario", MagicMock(return_value=payload))
    loaded = components.fetch_preset_scenario("VIENNA_STANDARD_24")
    assert loaded is payload
    assert not components.comparison_ready(loaded)
    source = Path("frontend/pages/1_Dispatch_Setup.py").read_text(encoding="utf-8")
    assert "disabled=not ready" in source
    assert "if not planning_service_up()" not in source
    client = Path("frontend/api_client.py").read_text(encoding="utf-8")
    assert "timeout: float = 90.0" in client


def test_sidebar_treats_missed_health_as_starting_until_confirmed_down(monkeypatch) -> None:
    ui = _install_ui(monkeypatch, offline=None)
    monkeypatch.setattr(components, "planning_service_up", lambda: False)
    monkeypatch.setattr(
        components,
        "t",
        lambda key: {
            "api.status.on": "Planning service available",
            "api.status.off": "Planning service unavailable",
            "api.status.starting": "Planning service is starting",
        }[key],
    )
    components._render_service_status()
    markup = ui.markdown.call_args.args[0]
    assert "Planning service is starting" in markup
    assert "Planning service unavailable" not in markup

    ui.session_state["_planning_offline"] = True
    components._render_service_status()
    markup = ui.markdown.call_args.args[0]
    assert "Planning service unavailable" in markup


def test_classify_planning_availability_phases() -> None:
    assert components.classify_planning_availability(health_ok=True, offline_confirmed=True) == "up"
    assert (
        components.classify_planning_availability(health_ok=False, offline_confirmed=False)
        == "starting"
    )
    assert (
        components.classify_planning_availability(health_ok=False, offline_confirmed=True)
        == "down"
    )


class _Session(dict):
    def __getattr__(self, name: str):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: object) -> None:
        self[name] = value


def _missing_run(run_id: str = "gone") -> ApiError:
    return ApiError(
        f"UNKNOWN_RUN: Run '{run_id}' was not found.",
        status_code=404,
        kind="not_found",
        code="UNKNOWN_RUN",
    )


def _planner_ui(monkeypatch, **initial) -> tuple[MagicMock, _Session]:
    session = _Session(initial)
    ui = MagicMock()
    ui.session_state = session
    ui.button.return_value = False
    monkeypatch.setattr(components, "st", ui)
    monkeypatch.setattr(state, "st", ui)
    return ui, session


def _install_run_api(monkeypatch, *, get_run, get_routes=None, get_checks=None, get_scenario=None):
    monkeypatch.setattr(api_client, "get_run", get_run)
    monkeypatch.setattr(
        api_client,
        "get_routes",
        get_routes or (lambda run_id: {"run_id": run_id, "stops": [], "vehicle_kpis": []}),
    )
    monkeypatch.setattr(
        api_client,
        "get_checks",
        get_checks or (lambda run_id: {"run_id": run_id, "checks": []}),
    )
    monkeypatch.setattr(
        api_client,
        "get_scenario",
        get_scenario or (lambda scenario_id: {"scenario_id": scenario_id}),
    )


def _populated_run_session(**extra):
    values = {
        "scenario_id": "VIENNA_STANDARD_24",
        "ui_language": "de",
        "solver_time_limit_seconds": 10,
        "baseline_run_id": "run-b",
        "optimised_run_id": "run-o",
        "_baseline_summary": {"run_id": "run-b", "scenario_id": "VIENNA_STANDARD_24"},
        "_optimised_summary": {"run_id": "run-o", "scenario_id": "VIENNA_STANDARD_24"},
        "_export_payloads": {("run-b", "json"): b"{}"},
        "_custom_config": {"n": 24},
        "_planning_offline": False,
        "plan_view": "baseline",
    }
    values.update(extra)
    return values


def _run_payload(run_id: str, *, status: str = "feasible") -> dict:
    return {
        "run_id": run_id,
        "run_type": "baseline" if run_id.endswith("b") else "optimised",
        "scenario_id": "VIENNA_STANDARD_24",
        "status": status,
        "unserved_customer_ids": [],
        "comparison_eligible": status == "feasible",
    }


def test_is_missing_run_distinguishes_genuine_run_404() -> None:
    assert is_missing_run(_missing_run("run-b"))
    assert not is_missing_run(
        ApiError(
            "UNKNOWN_SCENARIO: Scenario 'x' was not found.",
            status_code=404,
            kind="not_found",
            code="UNKNOWN_SCENARIO",
        )
    )
    assert not is_missing_run(ApiError("Planning service unavailable.", kind="connection"))
    assert not is_missing_run(ApiError("HTTP 404: Not Found", status_code=404, kind="not_found"))
    assert not is_missing_run(ApiError("invalid input", status_code=400, kind="invalid"))


def test_clear_planner_runs_drops_only_comparison_keys(monkeypatch) -> None:
    _planner_ui(monkeypatch, **_populated_run_session(_plan_bundle={"keep": False}))
    clear_planner_runs()
    session = state.st.session_state
    assert PLANNER_RUN_KEYS == (
        "_plan_bundle",
        "baseline_run_id",
        "optimised_run_id",
        "_baseline_summary",
        "_optimised_summary",
        "_export_payloads",
    )
    assert "_plan_bundle" not in session
    assert "_export_payloads" not in session
    assert session.baseline_run_id is None
    assert session.optimised_run_id is None
    assert session["_baseline_summary"] is None
    assert session["_optimised_summary"] is None
    assert session.plan_view == "comparison"
    assert session["scenario_id"] == "VIENNA_STANDARD_24"
    assert session["ui_language"] == "de"
    assert session["solver_time_limit_seconds"] == 10
    assert session["_custom_config"] == {"n": 24}
    assert session["_planning_offline"] is False


def test_ensure_session_restores_language_after_widget_reset(monkeypatch) -> None:
    _planner_ui(
        monkeypatch,
        ui_language="en",
        ui_language_persist="de",
        scenario_id="VIENNA_STANDARD_24",
    )
    ensure_session()
    session = state.st.session_state
    assert session["ui_language"] == "de"
    assert session["ui_language_persist"] == "de"
    clear_planner_runs()
    assert session["ui_language"] == "de"
    assert session["ui_language_persist"] == "de"


def test_valid_stored_runs_still_resolve(monkeypatch) -> None:
    _planner_ui(monkeypatch, **_populated_run_session())
    _install_run_api(
        monkeypatch,
        get_run=lambda run_id: _run_payload(run_id),
    )
    result = components.resolve_plan_bundle(
        {"run_id": "run-b"},
        {"run_id": "run-o"},
        "VIENNA_STANDARD_24",
    )
    assert result.status == "ok"
    assert result.payload["baseline"]["run"]["run_id"] == "run-b"
    assert result.payload["optimised"]["run"]["run_id"] == "run-o"
    session = state.st.session_state
    assert session["baseline_run_id"] == "run-b"
    assert session["optimised_run_id"] == "run-o"
    assert session["ui_language"] == "de"
    assert session["_plan_bundle"] is result.payload


def test_valid_cached_runs_still_render_without_refetching_routes(monkeypatch) -> None:
    cached = {
        "scenario": {"scenario_id": "VIENNA_STANDARD_24"},
        "baseline": {"run": _run_payload("run-b")},
        "optimised": {"run": _run_payload("run-o")},
    }
    _planner_ui(monkeypatch, **_populated_run_session(_plan_bundle=cached))
    seen: list[str] = []

    def get_run(run_id: str) -> dict:
        seen.append(run_id)
        return _run_payload(run_id)

    routes = MagicMock()
    _install_run_api(monkeypatch, get_run=get_run, get_routes=routes)
    result = components.resolve_plan_bundle(
        {"run_id": "run-b"},
        {"run_id": "run-o"},
        "VIENNA_STANDARD_24",
    )
    assert result.status == "ok"
    assert result.payload is cached
    assert seen == ["run-b", "run-o"]
    routes.assert_not_called()


def test_missing_baseline_run_is_expired_not_partial(monkeypatch) -> None:
    ui, session = _planner_ui(monkeypatch, **_populated_run_session(_plan_bundle={"stale": True}))

    def get_run(run_id: str) -> dict:
        if run_id == "run-b":
            raise _missing_run(run_id)
        return _run_payload(run_id)

    _install_run_api(monkeypatch, get_run=get_run)
    result = components.resolve_plan_bundle(
        {"run_id": "run-b"},
        {"run_id": "run-o"},
        "VIENNA_STANDARD_24",
    )
    assert result.status == "expired"
    assert result.payload is None
    assert session.get("_plan_bundle") is None
    assert session.baseline_run_id is None
    assert session.optimised_run_id is None
    assert session["ui_language"] == "de"
    assert session["scenario_id"] == "VIENNA_STANDARD_24"
    ui.error.assert_not_called()
    ui.exception.assert_not_called()
    ui.warning.assert_not_called()


def test_cached_bundle_expires_when_a_stored_run_is_gone(monkeypatch) -> None:
    cached = {
        "scenario": {"scenario_id": "VIENNA_STANDARD_24"},
        "baseline": {"run": _run_payload("run-b")},
        "optimised": {"run": _run_payload("run-o")},
    }
    ui, session = _planner_ui(monkeypatch, **_populated_run_session(_plan_bundle=cached))
    _install_run_api(monkeypatch, get_run=MagicMock(side_effect=_missing_run("run-b")))
    result = components.resolve_plan_bundle(
        {"run_id": "run-b"},
        {"run_id": "run-o"},
        "VIENNA_STANDARD_24",
    )
    assert result.status == "expired"
    assert result.payload is None
    assert session.get("_plan_bundle") is None
    assert session.baseline_run_id is None
    assert session.optimised_run_id is None
    ui.error.assert_not_called()
    ui.exception.assert_not_called()


def test_missing_optimised_run_is_expired_not_partial(monkeypatch) -> None:
    ui, session = _planner_ui(monkeypatch, **_populated_run_session())

    def get_run(run_id: str) -> dict:
        if run_id == "run-o":
            raise _missing_run(run_id)
        return _run_payload(run_id)

    _install_run_api(monkeypatch, get_run=get_run)
    result = components.resolve_plan_bundle(
        {"run_id": "run-b"},
        {"run_id": "run-o"},
        "VIENNA_STANDARD_24",
    )
    assert result.status == "expired"
    assert session.baseline_run_id is None
    assert session.optimised_run_id is None
    assert session.get("_plan_bundle") is None
    ui.error.assert_not_called()
    markup_calls = [str(call.args) for call in ui.markdown.call_args_list]
    assert not any("404" in item for item in markup_calls)


def test_missing_verification_run_is_expired(monkeypatch) -> None:
    ui, session = _planner_ui(monkeypatch, **_populated_run_session())
    _install_run_api(
        monkeypatch,
        get_run=MagicMock(side_effect=_missing_run("run-o")),
    )
    result = components.fetch_verification_view("run-o", "VIENNA_STANDARD_24")
    assert result.status == "expired"
    assert result.payload is None
    assert session.baseline_run_id is None
    assert session.optimised_run_id is None
    assert session["ui_language"] == "de"
    ui.error.assert_not_called()
    ui.exception.assert_not_called()


def test_backend_unavailable_is_not_expired_run(monkeypatch) -> None:
    ui, session = _planner_ui(monkeypatch, **_populated_run_session())
    _install_run_api(
        monkeypatch,
        get_run=MagicMock(side_effect=ApiError("Planning service unavailable.", kind="connection")),
    )
    result = components.resolve_plan_bundle(
        {"run_id": "run-b"},
        {"run_id": "run-o"},
        "VIENNA_STANDARD_24",
    )
    assert result.status == "unavailable"
    assert session["baseline_run_id"] == "run-b"
    assert session["optimised_run_id"] == "run-o"
    assert session["_baseline_summary"]["run_id"] == "run-b"
    ui.error.assert_called_once()
    assert ui.error.call_args.args[0] == "Planning service unavailable"
    assert "404" not in str(ui.error.call_args)
    assert "Route result expired" not in str(ui.error.call_args)
    ui.exception.assert_not_called()

    verification = components.fetch_verification_view("run-o", "VIENNA_STANDARD_24")
    assert verification.status == "unavailable"
    assert session["optimised_run_id"] == "run-o"


def test_cached_comparison_is_kept_when_backend_is_unavailable(monkeypatch) -> None:
    cached = {
        "scenario": {"scenario_id": "VIENNA_STANDARD_24"},
        "baseline": {"run": _run_payload("run-b")},
        "optimised": {"run": _run_payload("run-o")},
    }
    ui, session = _planner_ui(monkeypatch, **_populated_run_session(_plan_bundle=cached))
    _install_run_api(
        monkeypatch,
        get_run=MagicMock(side_effect=ApiError("Planning service unavailable.", kind="connection")),
    )
    result = components.resolve_plan_bundle(
        {"run_id": "run-b"},
        {"run_id": "run-o"},
        "VIENNA_STANDARD_24",
    )
    assert result.status == "ok"
    assert result.payload is cached
    assert session["baseline_run_id"] == "run-b"
    assert session["optimised_run_id"] == "run-o"
    ui.error.assert_not_called()
    ui.exception.assert_not_called()


def test_infeasible_and_no_solution_payloads_are_not_expired(monkeypatch) -> None:
    _planner_ui(monkeypatch, **_populated_run_session())

    def get_run(run_id: str) -> dict:
        status = "infeasible" if run_id == "run-b" else "no_solution_found"
        return _run_payload(run_id, status=status)

    _install_run_api(monkeypatch, get_run=get_run)
    result = components.resolve_plan_bundle(
        {"run_id": "run-b"},
        {"run_id": "run-o"},
        "VIENNA_STANDARD_24",
    )
    assert result.status == "ok"
    assert result.payload["baseline"]["run"]["status"] == "infeasible"
    assert result.payload["optimised"]["run"]["status"] == "no_solution_found"
    assert state.st.session_state["baseline_run_id"] == "run-b"


def test_expired_result_state_copy_and_action(monkeypatch) -> None:
    ui, _ = _planner_ui(monkeypatch)
    components.expired_result_state()
    markup = ui.markdown.call_args.args[0]
    assert "Route result expired" in markup
    assert "This saved route result is no longer available." in markup
    assert "Run the scenario again to generate a new comparison." in markup
    assert "404" not in markup
    assert "infeasible" not in markup.lower()
    assert "no_solution_found" not in markup
    assert "Planning service unavailable" not in markup
    ui.button.assert_called_once()
    assert ui.button.call_args.args[0] == "Run scenario again"
    assert ui.button.call_args.kwargs["type"] == "primary"
    ui.switch_page.assert_not_called()

    ui.button.return_value = True
    components.expired_result_state()
    ui.switch_page.assert_called_with("pages/1_Dispatch_Setup.py")


def test_call_api_does_not_surface_raw_run_404(monkeypatch) -> None:
    ui, _ = _planner_ui(monkeypatch)

    def boom() -> None:
        raise _missing_run("run-b")

    assert components.call_api(boom) is None
    ui.error.assert_not_called()
    ui.exception.assert_not_called()
    ui.caption.assert_not_called()

    def missing_scenario() -> None:
        raise ApiError(
            "UNKNOWN_SCENARIO: Scenario 'x' was not found.",
            status_code=404,
            kind="not_found",
            code="UNKNOWN_SCENARIO",
        )

    components.call_api(missing_scenario)
    assert "404" not in str(ui.error.call_args)
    assert "was not found" not in str(ui.error.call_args)


def test_plan_and_inspect_recover_expired_runs_without_autorun() -> None:
    plan = Path("frontend/pages/3_Baseline_vs_Optimised.py").read_text(encoding="utf-8")
    inspect = Path("frontend/pages/4_Model_Inspector.py").read_text(encoding="utf-8")
    assert "resolve_plan_bundle" in plan
    assert "expired_result_state" in plan
    assert "run_baseline" not in plan
    assert "run_optimise" not in plan
    assert "call_api" not in plan
    assert "fetch_verification_view" in inspect
    assert "expired_result_state" in inspect
    assert "run_baseline" not in inspect
    assert "run_optimise" not in inspect
    assert "status_badge" not in Path("frontend/components.py").read_text(encoding="utf-8").split(
        "def expired_result_state"
    )[1].split("def render_check_table")[0]


def test_solution_verification_page_hierarchy_and_states() -> None:
    home = Path("frontend/Home.py").read_text(encoding="utf-8")
    inspect = Path("frontend/pages/4_Model_Inspector.py").read_text(encoding="utf-8")
    overview = Path("frontend/pages/0_Overview.py").read_text(encoding="utf-8")
    scenarios = Path("frontend/pages/1_Dispatch_Setup.py").read_text(encoding="utf-8")
    plan = Path("frontend/pages/3_Baseline_vs_Optimised.py").read_text(encoding="utf-8")
    assert 'url_path="validation"' in home
    assert 't("nav.secondary")' in home
    assert 't("nav.inspect")' in home
    body = inspect.split("page_header(")[1]
    subtitle_at = body.find('t("inspect.subtitle")')
    pick_at = body.find('t("inspect.pick")')
    expired_at = body.find("expired_result_state()")
    verdict_at = body.find("verdict_copy")
    checks_at = body.find('t("inspect.checks")')
    meta_at = body.find("run_metadata_items")
    scope_at = body.find('t("inspect.scope")')
    assignments_at = body.find('t("inspect.view.assignments")')
    legs_at = body.find('t("inspect.view.legs")')
    loads_at = body.find('t("inspect.view.loads")')
    distance_at = body.find('t("inspect.view.distance")')
    matrix_at = body.find('t("inspect.view.matrix")')
    assert subtitle_at < pick_at < expired_at < verdict_at < checks_at < meta_at < scope_at
    assert scope_at < assignments_at < legs_at < loads_at < distance_at < matrix_at
    assert inspect.count("expanded=False") >= 5
    assert inspect.count("st.expander(") == 5
    assert "empty_state" in inspect
    assert "NON_SUCCESS_STATUSES" in inspect
    assert "status_badge" in inspect
    assert "run_baseline" not in inspect
    assert "run_optimise" not in inspect
    assert "All five" not in inspect
    assert "5 of 5" not in inspect
    assert "giant" not in inspect.lower()
    assert inspect.count("st.success") == 0
    assert ".lm-inspect-verdict" in components.THEME_CSS
    assert ".lm-inspect-verdict.is-fail" in components.THEME_CSS
    assert "lm-inspect-runid" in components.THEME_CSS
    assert "concept_cards" in overview
    assert "render_overview_reference_proof" in overview
    assert "ux.plan.why.title" in plan
    assert "render_plan_verdict" in plan
    assert "render_route_legend" in plan
    assert "ux.custom.configure" in scenarios


def test_solution_verification_helpers_use_returned_checks(monkeypatch) -> None:
    import inspector

    monkeypatch.setattr("i18n.current_language", lambda: "en")
    checks = [
        {
            "code": "DEMAND_SATISFACTION",
            "name": "demand_satisfaction",
            "passed": True,
            "message": "x",
        },
        {"code": "CAPACITY", "name": "vehicle_capacity", "passed": True, "message": "x"},
        {"code": "DISTANCE", "name": "distance_reconciliation", "passed": True, "message": "x"},
        {
            "code": "DEPOT_CONNECTIVITY",
            "name": "depot_connectivity",
            "passed": True,
            "message": "x",
        },
        {"code": "INVARIANTS", "name": "solution_invariants", "passed": True, "message": "x"},
    ]
    passed, total = inspector.checks_passed_count(checks)
    ok, text = inspector.verdict_copy(checks)
    assert (passed, total) == (5, 5)
    assert ok is True
    assert text == "All solution checks passed"
    assert inspector.check_name(checks[0]) == "Customer coverage"
    assert "demand_satisfaction" not in inspector.check_name(checks[0])
    failed = [{**checks[0], "passed": False}, *checks[1:]]
    ok_fail, fail_text = inspector.verdict_copy(failed)
    assert ok_fail is False
    assert fail_text == "One or more solution checks failed"
    four = checks[:4]
    passed_four, total_four = inspector.checks_passed_count(four)
    assert (passed_four, total_four) == (4, 4)
    ok_four, _ = inspector.verdict_copy(four)
    assert ok_four is True
    meta = inspector.run_metadata_items(
        {
            "scenario_id": "VIENNA_STANDARD_24",
            "run_type": "optimised",
            "run_id": "OPT_demo",
            "solver_termination": "success",
            "solver_time_limit_seconds": 5,
            "solver_runtime_seconds": 5.01,
        }
    )
    values = {label: (value, css) for label, value, css in meta}
    assert values["Scenario"][0] == "Vienna Standard"
    assert values["Method"][0] == "Optimized solution (OR-Tools)"
    assert values["Solver termination"][0] == "Success"
    assert values["Requested search limit"][0] == "5 s"
    assert values["Actual runtime"][0] == "5.01 s"
    assert values["Run ID"] == ("OPT_demo", "lm-inspect-runid")
    baseline_meta = inspector.run_metadata_items(
        {
            "scenario_id": "VIENNA_STANDARD_24",
            "run_type": "baseline",
            "run_id": "BASE_demo",
            "solver_termination": "not_run",
            "solver_time_limit_seconds": None,
            "solver_runtime_seconds": None,
        }
    )
    baseline_values = {label: value for label, value, _css in baseline_meta}
    assert baseline_values["Method"] == "Nearest-neighbour baseline"
    assert baseline_values["Requested search limit"] == "N/A"
    assert baseline_values["Actual runtime"] == "N/A"
    assert baseline_values["Solver termination"] == "N/A"
    connectivity = inspector.incoming_outgoing(
        [{"from_id": "DEPOT", "to_id": "C001"}],
        ["DEPOT", "C001"],
    )
    assert "outgoing reconstructed arcs" not in connectivity[0]
    assert "Incoming route legs" in connectivity[0]
    assert inspector.demand_check_label("Pass") == "Passed"
    assert inspector.demand_check_label("Fail") == "Failed"
