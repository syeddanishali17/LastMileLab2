"""Presentation regressions, independent of mathematical expectations."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

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
from maps import PLOTLY_MAP_CONFIG, _map_camera
from state import PLANNER_RUN_KEYS, clear_planner_runs


def test_connection_errors_do_not_instruct_localhost_api() -> None:
    ui_source = Path("frontend/components.py").read_text(encoding="utf-8")
    client_source = Path("frontend/api_client.py").read_text(encoding="utf-8")
    assert "PLANNING_START_CMD" not in ui_source
    assert "127.0.0.1" not in ui_source
    assert "Start Uvicorn" not in client_source
    assert "port 8000 first" not in client_source


def test_route_palette_and_camera_are_comparable():
    assert VEHICLE_COLOURS[:4] == ["#2563EB", "#EA580C", "#7C3AED", "#C026D3"]
    assert len(set(VEHICLE_COLOURS[:4])) == 4
    camera = _map_camera([48.12, 48.30], [16.28, 16.55])
    assert camera == _map_camera([48.30, 48.12], [16.55, 16.28])
    assert camera["zoom"] < 10
    assert PLOTLY_MAP_CONFIG["scrollZoom"] is False


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
    assert 't("ux.optimised")' not in source
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
    assert 'key="plan-pair"' in compare_src
    assert "vehicle_summary" in compare_src
    assert 't("ux.plan.view.baseline")' in compare_src
    assert 't("ux.plan.view.optimised")' in compare_src
    pair_at = compare_src.find('key="plan-pair"')
    details_at = compare_src.find('key="plan-route-details"')
    validation_at = compare_src.find('t("ux.plan.validation")')
    assert pair_at < details_at < validation_at


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
        "The optimized route plan reduces total fleet distance travelled from 80.000 km "
        "to 64.000 km, a 20.0% reduction. Both plans serve all 12 customers while "
        "respecting vehicle-capacity limits."
    )
    assert "122.394" not in lead
    assert "97.193" not in lead
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
    assert "reduces total fleet distance" not in lead
    assert "one or both route plans are incomplete" in lead
    assert detail is not None
    mismatched = plan_comparison_summary(
        _run(customers_total=12),
        _run(customers_total=24, distance_improvement_percentage=20.0),
    )
    assert "reduces total fleet distance" not in mismatched[0]
    assert not plans_comparable(_run(customers_total=12), _run(customers_total=24))


def test_overview_animation_teaches_baseline_versus_optimized():
    markup = components.cvrp_animation_html(
        "122.4 km → 97.2 km · 20.6% shorter",
        "diagram",
    )
    assert "lm-cvrp-panel" in markup
    assert "lm-cvrp-compare" in markup
    assert markup.count('class="lm-cvrp-pane"') == 2
    assert markup.count("<svg") == 2
    assert "Nearest-neighbour baseline" in markup
    assert "Optimized solution" in markup
    assert "122.4 km" in markup
    assert "97.2 km · 20.6% shorter" in markup
    assert "Total distance: 122.4 km" in markup
    assert "Total distance: 97.2 km · 20.6% shorter" in markup
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
    assert "lm-cvrp-arr-0-0-0" in markup
    assert "lm-cvrp-arr-1-3-2" in markup
    assert 'fill="#64748B"' not in markup
    assert "r=\"10.5\" fill=" not in markup
    assert "@keyframes lm-cvrp-arr-0-0-0" in components.THEME_CSS
    assert "fill: var(--lm-visit)" in components.THEME_CSS
    assert markup.count('class="lm-cvrp-cust') == 24
    assert "5s linear infinite" in components.THEME_CSS
    assert ".lm-num" in components.THEME_CSS
    assert "text-align: right" in components.THEME_CSS
    assert "animation: none" in components.THEME_CSS
    assert ".lm-route-motif::before" not in components.THEME_CSS
    assert "lm-hero-mark" in components.THEME_CSS
    assert "width: 123px" in components.THEME_CSS
    assert "margin-left: 0" in components.THEME_CSS
    assert "padding: 0 24px" in components.THEME_CSS
    assert "max-width: none" in components.THEME_CSS
    assert "text-align: justify" not in components.THEME_CSS
    assert "font-size: 18px" in components.THEME_CSS
    assert markup.find("<svg") < markup.find('class="lm-cvrp-pane-title"')
    assert "padding-top: 0" in components.THEME_CSS
    assert ".lm-proof-kicker" in components.THEME_CSS
    assert ".lm-overview-flag" in components.THEME_CSS
    assert ".lm-about" in components.THEME_CSS
    assert ".lm-about-body" in components.THEME_CSS
    assert "width: 88%" in components.THEME_CSS
    assert ".lm-concept-grid .lm-card > p" in components.THEME_CSS
    assert ".lm-concept-grid .lm-card .lm-info-text" in components.THEME_CSS
    assert "clamp(28px, 2.4vw, 34px)" in components.THEME_CSS
    assert "clamp(27px, 2.6vw, 35px)" not in components.THEME_CSS
    assert "clamp(1.75rem, 2.6vw, 2.25rem)" not in components.THEME_CSS
    assert "lm-cvrp-note" not in markup
    assert "Illustrative published reference only" not in markup
    assert "st-key-scenario_presets" in components.THEME_CSS
    assert ".lm-check-title" in components.THEME_CSS
    assert 'stSidebar"][aria-expanded="true"]' in components.THEME_CSS
    assert "272px" in components.THEME_CSS
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
    assert "stBaseButton-segmented_controlActive" in components.THEME_CSS
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


def test_overview_visit_keyframes_snap_fill_at_path_arrival():
    idle = "fill:#F8FAFC;stroke:#94A3B8;opacity:1"
    active = "fill:var(--lm-visit);stroke:var(--lm-visit);opacity:1"
    pulse_frame = "fill:var(--lm-visit);stroke:var(--lm-visit);opacity:.75"
    css = components.THEME_CSS
    for pane, routes in enumerate((components._CVRP_NN_ROUTES, components._CVRP_OPT_ROUTES)):
        for route_index, (_colour, stops) in enumerate(routes):
            arrivals = components._cvrp_arrival_pcts(stops)
            assert len(arrivals) == len(stops)
            points = [components._CVRP_DEPOT, *stops, components._CVRP_DEPOT]
            total_path = sum(
                components._cvrp_seg_len(start, end)
                for start, end in zip(points[:-1], points[1:], strict=True)
            )
            walked = 0.0
            for stop_index, percent in enumerate(arrivals):
                walked += components._cvrp_seg_len(points[stop_index], points[stop_index + 1])
                assert percent == pytest.approx(100.0 * walked / total_path, abs=1e-9)
                arrival = round(percent, 2)
                before = max(round(arrival - 0.01, 2), 0.0)
                pulse = min(round(arrival + 1.2, 2), 99.2)
                settled = min(round(arrival + 2.4, 2), 99.6)
                name = f"lm-cvrp-arr-{pane}-{route_index}-{stop_index}"
                expected = (
                    f"@keyframes {name}{{"
                    f"0%,{before:.2f}%{{{idle};}}"
                    f"{arrival:.2f}%{{{active};}}"
                    f"{pulse:.2f}%{{{pulse_frame};}}"
                    f"{settled:.2f}%,100%{{{active};}}"
                    f"}}"
                )
                assert expected in css, name
                assert pulse > arrival
                assert "cx:" not in expected
                assert "cy:" not in expected
    assert "opacity:.72" not in css
    assert "animation: lm-pane-route 5s linear infinite" in css
    assert (
        ".lm-cvrp-pane .lm-cvrp-nodes .lm-cvrp-r2 { --lm-visit: #EA580C; animation-delay: -1.25s; }"
        in css
    )
    assert (
        ".lm-cvrp-pane .lm-cvrp-nodes .lm-cvrp-r3 { --lm-visit: #7C3AED; animation-delay: -2.5s; }"
        in css
    )
    assert (
        ".lm-cvrp-pane .lm-cvrp-nodes .lm-cvrp-r4 { --lm-visit: #C026D3; animation-delay: -3.75s; }"
        in css
    )
    assert ".lm-cvrp-pane .lm-cvrp-routes path:nth-child(2) { animation-delay: -1.25s; }" in css
    assert ".lm-cvrp-pane .lm-cvrp-routes path:nth-child(3) { animation-delay: -2.5s; }" in css
    assert ".lm-cvrp-pane .lm-cvrp-routes path:nth-child(4) { animation-delay: -3.75s; }" in css
    assert "animation-duration: 5s" in css
    assert "from { stroke-dashoffset: 100; }" in css
    assert "to { stroke-dashoffset: 0; }" in css


def test_overview_page_puts_animation_and_cta_before_concept_cards():
    source = Path("frontend/pages/0_Overview.py").read_text(encoding="utf-8")
    header_at = source.index("page_header(")
    animation_at = source.index("cvrp_animation_html(")
    cta_at = source.index('st.button(t("ux.over.cta")')
    cards_at = source.index("concept_cards(")
    footer_at = source.index("render_footer()")
    about_at = source.index("render_overview_about()")
    assert header_at < animation_at < cta_at < cards_at < about_at < footer_at
    assert source.count("concept_cards(") == 1
    assert source.count('st.button(t("ux.over.cta")') == 1
    assert source.count("cvrp_animation_html(") == 1
    assert "author=" not in source
    assert "ux.over.author" not in source
    assert "kpi_cards" not in source
    assert "ux.over.proof" not in source
    assert "Customers served" not in source
    markup = components.cvrp_animation_html("97.2 km", "diagram")
    cap_at = markup.index('class="lm-cvrp-cap"')
    pause_at = markup.index("lm-motion-control")
    panel_end = markup.index("</div>", pause_at)
    assert cap_at < pause_at < panel_end
    assert markup.count("lm-motion-control") == 1
    assert markup.count('st.button') == 0


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
        [("Routing objective", "Minimize distance.", "The model minimizes distance.")]
    )
    markup = ui.markdown.call_args.args[0]
    assert 'class="lm-info"' in markup
    assert "<svg" in markup
    assert "ⓘ" not in markup
    assert 'aria-label="Routing objective"' in markup
    assert '<details class="lm-info">' in markup
    assert "The model minimizes distance." in markup
    assert "<abbr" not in markup
    assert "lm-tip" not in markup


def test_overview_about_and_footer_markup(monkeypatch):
    ui = MagicMock()
    monkeypatch.setattr(components, "st", ui)
    monkeypatch.setattr(
        components,
        "t",
        lambda key: {
            "ux.over.about.kicker": "ABOUT THIS PROJECT",
            "ux.over.about.body": (
                "LastMile Lab is an independent portfolio project designed and developed by "
                "Syed Danish Ali."
            ),
            "footer": "© 2026 Syed Danish Ali · LastMile Lab",
        }[key],
    )
    components.render_overview_about()
    markup = ui.markdown.call_args.args[0]
    assert 'class="lm-about"' in markup
    assert 'class="lm-about-kicker">ABOUT THIS PROJECT</div>' in markup
    assert "Syed Danish Ali" in markup
    assert "lm-card" not in markup
    assert "lm-hero-author" not in markup
    assert "</div>\n" not in markup
    components.render_footer()
    footer = ui.markdown.call_args.args[0]
    assert footer == '<div class="lm-footer">© 2026 Syed Danish Ali · LastMile Lab</div>'


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
