"""Frontend copy tables stay in lockstep."""

import i18n
from display import format_km, format_pct, humanize_check_message, status_label
from i18n import STRINGS, t
from workflow_copy import COPY, WORKFLOW_STRINGS


def test_english_and_german_keys_match() -> None:
    assert set(STRINGS["en"]) == set(STRINGS["de"])


def test_workflow_copy_overrides_nav_for_both_languages() -> None:
    assert set(WORKFLOW_STRINGS["en"]) == set(WORKFLOW_STRINGS["de"]) == set(COPY)
    assert STRINGS["en"]["nav.home"] == "01  Overview"
    assert STRINGS["de"]["nav.home"] == "01  Überblick"
    assert STRINGS["en"]["nav.dispatch"] == "02  Scenarios"
    assert STRINGS["en"]["empty.open"] == "Go to Scenarios"
    assert STRINGS["en"]["ux.van"] == "Vehicle"
    assert STRINGS["de"]["ux.van"] == "Fahrzeug"
    assert STRINGS["en"]["ux.optimised"] == "Optimized solution (OR-Tools)"
    assert STRINGS["en"]["ux.stops"] == "Customer stops"
    assert STRINGS["en"]["ux.sequence"] == "Route sequence"
    assert STRINGS["en"]["nav.secondary"] == "MODEL & METHODS"


def test_methodology_and_overview_copy_use_academic_cvrp_terms() -> None:
    assert "totes (standard reusable delivery containers)" in STRINGS["en"]["ux.over.cvrp"]
    assert "Totes (standardisierte Mehrweg-Lieferbehälter)" in STRINGS["de"]["ux.over.cvrp"]
    assert STRINGS["en"]["ux.over.compare"].startswith("The application compares")
    assert "absence of a complete solution" in STRINGS["en"]["ux.method.solver.none"]
    assert "OpenSolver" in STRINGS["en"]["ux.method.opensolver"]
    assert "does not solve the documented three-index MILP" in STRINGS["en"]["ux.method.opensolver"]
    assert "not be described as globally optimal" in STRINGS["en"]["ux.method.solver.limit"]
    assert "repository Haversine" not in STRINGS["en"]["ux.method.assumptions"]
    assert "Geographic distance is estimated with the Haversine method" in (
        STRINGS["en"]["ux.method.assumptions"]
    )


def test_status_badge_copy_is_human() -> None:
    assert status_label("passed") == "Pre-checks passed"


def test_user_facing_copy_avoids_em_dashes() -> None:
    for language in STRINGS.values():
        assert all("—" not in value for value in language.values())


def test_german_number_formatting(monkeypatch) -> None:
    monkeypatch.setattr(i18n, "current_language", lambda: "de")
    assert format_km(30101) == "30,101 km"
    assert format_pct(0.967) == "96,7 %"


def test_check_three_message_is_plain() -> None:
    text = humanize_check_message(
        {
            "code": "CHECK_3",
            "passed": True,
            "message": (
                "minimum vehicles by aggregate demand = 4 "
                "(informational; not a feasibility proof)"
            ),
        }
    )
    assert "4" in text
    assert "informational" not in text
    assert t("check.msg.minvans", n=4) == text
