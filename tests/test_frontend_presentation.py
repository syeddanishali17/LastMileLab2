"""Presentation regressions, independent of mathematical expectations."""

from unittest.mock import MagicMock

import components
from display import VEHICLE_COLOURS
from maps import PLOTLY_MAP_CONFIG, _map_camera


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


def test_overview_animation_teaches_baseline_versus_optimized():
    markup = components.cvrp_animation_html(
        "122.4 km → 97.2 km · 20.6% shorter",
        "diagram",
    )
    assert "lm-cvrp-panel" in markup
    assert "Nearest-neighbour baseline" in markup
    assert "Optimized solution" in markup
    assert "122.4 km" in markup
    assert ">1</text>" in markup
    assert ">2</text>" in markup
    assert ">3</text>" in markup
    assert "lm-cvrp-dot-nn" in markup
    assert "◂" not in components.THEME_CSS
    assert "lm-loop-depot" in components.THEME_CSS
    assert ".lm-num" in components.THEME_CSS
    assert "text-align: right" in components.THEME_CSS
    assert "animation: none" in components.THEME_CSS
    assert "10s" in components.THEME_CSS
    assert ".lm-route-motif::before" not in components.THEME_CSS


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
