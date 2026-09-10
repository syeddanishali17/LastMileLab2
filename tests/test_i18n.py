"""Frontend copy tables stay in lockstep."""

import i18n
from display import format_km, format_pct, humanize_check_message, status_label
from i18n import STRINGS, t
from workflow_copy import COPY, WORKFLOW_STRINGS


def test_english_and_german_keys_match() -> None:
    assert set(STRINGS["en"]) == set(STRINGS["de"])


def test_workflow_copy_overrides_nav_for_both_languages() -> None:
    assert set(WORKFLOW_STRINGS["en"]) == set(WORKFLOW_STRINGS["de"]) == set(COPY)
    assert STRINGS["en"]["nav.home"] == "Overview"
    assert STRINGS["de"]["nav.home"] == "Überblick"
    assert STRINGS["en"]["nav.dispatch"] == "Scenarios"
    assert STRINGS["en"]["empty.open"] == "Go to Scenarios"
    assert STRINGS["en"]["ux.van"] == "Vehicle"
    assert STRINGS["de"]["ux.van"] == "Fahrzeug"
    assert STRINGS["en"]["ux.optimised"] == "Optimized solution (OR-Tools)"
    assert STRINGS["en"]["ux.stops"] == "Customer stops"
    assert STRINGS["en"]["ux.sequence"] == "Route sequence"
    assert STRINGS["en"]["nav.secondary"] == "MODEL & METHODS"


def test_overview_english_copy_is_locked() -> None:
    en = STRINGS["en"]
    assert en["ux.over.kicker"] == "CAPACITATED VEHICLE ROUTING PROBLEM (CVRP)"
    assert en["ux.over.title"] == (
        "Optimize fleet routing to minimize travel distance under capacity constraints"
    )
    assert en["ux.over.compare.title"] == "Solution comparison"
    assert en["ux.over.compare.label"] == "COMPARISON"
    assert STRINGS["de"]["ux.over.compare.label"] == "VERGLEICH"
    assert en["ux.over.vrp.title"] == "Minimize fleet travel"
    assert en["ux.over.cvrp.title"] == "Respect vehicle capacity"
    assert en["ux.over.feas.title"] == "Serve every customer"
    assert STRINGS["de"]["ux.over.vrp.title"] == "Fahrdistanz minimieren"
    assert STRINGS["de"]["ux.over.cvrp.title"] == "Fahrzeugkapazität einhalten"
    assert STRINGS["de"]["ux.over.feas.title"] == "Jeden Kunden bedienen"
    assert en["ux.over.vrp"] == (
        "Minimize the total estimated distance travelled across all active vehicle routes."
    )
    assert STRINGS["de"]["ux.over.vrp"] == (
        "Die geschätzte Gesamtdistanz über alle aktiven Fahrzeugtouren minimieren."
    )
    assert "01  " not in en["ux.over.vrp.title"]
    assert "ux.over.author" not in en
    assert en["ux.over.about.kicker"] == "ABOUT THIS PROJECT"
    assert en["ux.over.about.title"] == "Built to make routing decisions inspectable"
    assert en["ux.over.about.body1"] == (
        "LastMile Lab is an independent portfolio project by Syed Danish Ali that applies "
        "capacitated vehicle routing to a synthetic last-mile delivery case."
    )
    assert en["ux.over.about.body2"] == (
        "It brings together scenario design, route optimization, API-based planning, "
        "solution verification, and a bilingual interactive interface in one inspectable "
        "workflow."
    )
    assert en["ux.over.about.stack"] == "CVRP · Python · FastAPI · Streamlit"
    assert STRINGS["de"]["ux.over.about.kicker"] == "ÜBER DIESES PROJEKT"
    assert STRINGS["de"]["ux.over.about.title"] == (
        "Entwickelt, um Tourenentscheidungen prüfbar zu machen"
    )
    assert STRINGS["de"]["ux.over.about.body1"] == (
        "LastMile Lab ist ein unabhängiges Portfolio-Projekt von Syed Danish Ali, das "
        "Capacitated Vehicle Routing auf einen synthetischen Last-Mile-Zustellfall anwendet."
    )
    assert STRINGS["de"]["ux.over.about.body2"] == (
        "Es verbindet Szenariodesign, Tourenoptimierung, API-basierte Planung, "
        "Lösungsprüfung und eine zweisprachige interaktive Oberfläche in einem prüfbaren "
        "Ablauf."
    )
    assert STRINGS["de"]["ux.over.about.stack"] == "CVRP · Python · FastAPI · Streamlit"
    assert "ux.over.about.body" not in en
    assert en["footer"] == "© 2026 Syed Danish Ali · LastMile Lab"
    assert STRINGS["de"]["footer"] == "© 2026 Syed Danish Ali · LastMile Lab"
    assert "ux.over.proof" not in en
    assert "ux.over.proof.cap" not in en
    assert "ux.over.disclosure" not in en
    assert "ux.over.future" not in en
    assert "ux.over.carbon" not in en
    assert "ux.over.anim.what" not in en
    assert en["ux.over.proof.kicker"] == "REFERENCE SCENARIO"
    assert STRINGS["de"]["ux.over.proof.kicker"] == "REFERENZSZENARIO"
    assert en["ux.over.proof.scenario"] == "Vienna Standard"
    assert STRINGS["de"]["ux.over.proof.scenario"] == "Wien Standard"
    assert en["ux.over.proof.line"] == (
        "122.394 km → 97.193 km · 20.6% shorter · 24/24 customers served"
    )
    assert STRINGS["de"]["ux.over.proof.line"] == (
        "122,394 km → 97,193 km · 20,6 % kürzer · 24/24 Kunden bedient"
    )
    assert en["ux.over.stage.kicker"] == "ROUTE COMPARISON"
    assert STRINGS["de"]["ux.over.stage.kicker"] == "TOURENVERGLEICH"
    assert en["ux.over.stage.title"] == "Baseline versus optimized"
    assert STRINGS["de"]["ux.over.stage.title"] == "Baseline und optimierte Lösung"
    assert en["ux.over.model.kicker"] == "MODEL LOGIC"
    assert en["ux.over.vrp.label"] == "OBJECTIVE"
    assert en["ux.over.cvrp.label"] == "CAPACITY CONSTRAINT"
    assert STRINGS["de"]["ux.over.model.kicker"] == "MODELLLOGIK"
    assert STRINGS["de"]["ux.over.vrp.label"] == "ZIEL"
    assert STRINGS["de"]["ux.over.cvrp.label"] == "KAPAZITÄTSBESCHRÄNKUNG"
    assert STRINGS["de"]["ux.over.feas.label"] == "ZULÄSSIGKEIT"
    assert en["ux.over.stage.lead"] == (
        "Compare the nearest-neighbour baseline with the optimized route plan for the "
        "same scenario."
    )
    assert STRINGS["de"]["ux.over.stage.lead"] == (
        "Nächster-Nachbar-Baseline und optimierten Tourenplan für dasselbe Szenario vergleichen."
    )
    assert "One comparison frame keeps both planning states visible" not in en["ux.over.stage.lead"]
    assert "ViennaCart" not in en["ux.over.about.body1"]
    assert "ViennaCart" not in en["ux.over.about.body2"]
    assert "Published result" not in en["ux.over.proof.kicker"]
    assert "OR-Tools" not in en["ux.over.proof.kicker"]
    assert "OR-Tools" not in en["ux.over.intro"]
    assert "OR-Tools" not in en["ux.over.proof.line"]
    assert "ux.over.context" not in en
    overview_copy = " ".join(value for key, value in en.items() if key.startswith("ux.over."))
    assert "Published reference" not in overview_copy
    assert "Published result" not in overview_copy
    assert "Published example" not in overview_copy
    assert "active vehicle to the depot" in en["ux.over.feas.hero"]
    assert en["ux.over.anim.depot"] == "Depot"
    assert "Starting point" not in en["ux.over.anim.depot"]
    assert en["ux.over.feas.tip"] == (
        "Depot: The common start and return location for all vehicle routes."
    )
    assert en["ux.proof.served"] == "Customers served"
    assert en["ux.kpi.baseline"] == "Baseline distance"
    assert en["ux.kpi.optimised"] == "Optimized distance"
    assert en["ux.kpi.saving"] == "Distance reduction"
    assert en["ux.over.cvrp"] == (
        "Each customer has an unsplit tote demand, and the total demand assigned to a vehicle "
        "cannot exceed its available capacity."
    )
    assert en["ux.over.feas"] == (
        "Every customer must be served exactly once, and every active vehicle route starts and "
        "returns to the depot."
    )
    assert "OR-Tools" not in en["ux.over.vrp"]
    assert "OR-Tools" not in en["ux.over.cvrp"]
    assert "OR-Tools" not in en["ux.over.feas"]
    assert "unsplit tote demand" in en["ux.over.cvrp"]
    assert en["ux.over.intro"].startswith("LastMile Lab models a static, single-depot")
    assert "assigns customer demand to capacity-constrained vehicles" in en["ux.over.intro"]
    assert "minimizes estimated fleet distance" in en["ux.over.intro"]
    assert STRINGS["de"]["ux.over.intro"].startswith(
        "LastMile Lab modelliert ein statisches Capacitated Vehicle Routing Problem"
    )
    assert (
        "The reference distances are from the Vienna Standard scenario, not from this schematic."
        in en["ux.over.diagram"]
    )
    assert (
        "Die Referenzdistanzen stammen vom Szenario Wien Standard, nicht von dieser Skizze."
        in STRINGS["de"]["ux.over.diagram"]
    )
    assert "Vienna Standard 24" not in en["ux.over.diagram"]
    assert "Wien Standard 24" not in STRINGS["de"]["ux.over.diagram"]
    assert en["ux.over.vrp.tip"].startswith("The objective is to reduce combined fleet travel")
    assert en["ux.over.compare.tip"].startswith("The baseline provides a transparent reference")
    assert en["ux.over.proof.tech"] == (
        "This comparison shows a feasible optimized plan for Vienna Standard 24; global "
        "optimality is not claimed."
    )
    assert STRINGS["de"]["ux.over.proof.tech"] == (
        "Dieser Vergleich zeigt einen zulässigen optimierten Plan für Wien Standard 24; "
        "globale Optimalität wird nicht behauptet."
    )
    assert en["ux.motion.pause"] == "Pause animations"
    assert en["ux.motion.replay"] == "Replay comparison"
    assert STRINGS["de"]["ux.motion.pause"] == "Animationen pausieren"
    assert STRINGS["de"]["ux.motion.replay"] == "Vergleich erneut abspielen"
    assert "ux.over.diagram.note" not in en
    assert en["ux.source"] == "Scenario Selection"
    assert en["ux.scenarios.title"] == "Scenarios"
    assert en["ux.scenarios.subtitle"] == (
        "Choose a preset scenario, review its demand and fleet configuration, then run a "
        "route comparison."
    )
    assert "published reference" not in en["scenario.VIENNA_STANDARD_24.help"].lower()
    assert en["ux.seconds"] == "Optimization search limit"
    assert en["ux.seconds.help"].startswith("Sets the maximum search time")
    assert en["ux.custom.configure"] == "Configure custom scenario"
    assert en["ux.check.order.title"] == "Order capacity"
    assert en["ux.check.fleet.title"] == "Fleet capacity"
    assert en["ux.check.min"] == "Minimum fleet requirement"
    assert en["ux.check.spare"] == "Spare fleet capacity"
    assert en["ux.custom.stale"] == "Changes not yet generated"
    assert en["ux.custom.advanced"] == "Advanced location settings"
    assert "Check 1" not in en["ux.check.order.title"]
    assert en["scenario.VIENNA_STANDARD_24.label"] == "Vienna Standard"
    assert en["scenario.VIENNA_TIGHT_24.label"] == "Vienna Tight Capacity"
    assert en["scenario.VIENNA_WIDE_24.label"] == "Vienna Wide Geography"
    assert en["scenario.VIENNA_WIDE_24.help"] == (
        "Same demand and fleet as Vienna Standard, with customer locations spread farther "
        "across Vienna."
    )
    assert "Standard 24" not in en["scenario.VIENNA_WIDE_24.help"]
    assert "Standard 24" not in STRINGS["de"]["scenario.VIENNA_WIDE_24.help"]
    assert en["scenario.VIENNA_STANDARD_24.label"].endswith("24") is False
    assert "24 customers" in en["scenario.VIENNA_STANDARD_24.meta"]
    assert en["ux.preview.capacity.value"] == "{n} totes/vehicle"
    assert "Tote" in STRINGS["de"]["ux.over.cvrp"] or "Tote" in STRINGS["de"]["ux.over.cvrp.tip"]


def test_plan_copy_is_recruiter_facing() -> None:
    en = STRINGS["en"]
    de = STRINGS["de"]
    assert en["nav.compare"] == "Plan"
    assert en["ux.plan.title"] == "Route comparison"
    assert en["ux.plan.subtitle"] == (
        "Compare a reference route plan with an optimized route plan for the same "
        "customers, demand, fleet and capacity limits."
    )
    assert en["ux.plan.why.body"].startswith("The baseline provides a consistent reference")
    assert en["ux.plan.result"] == (
        "Optimized routing reduced estimated fleet distance by {reduction} while serving all "
        "{customer_count} customers."
    )
    assert de["ux.plan.result"] == (
        "Die optimierte Tourenplanung senkte die geschätzte Flottendistanz um {reduction} "
        "und bediente alle {customer_count} Kunden."
    )
    assert en["ux.plan.result.cue"] == "Result"
    assert de["ux.plan.result.cue"] == "Ergebnis"
    assert en["ux.plan.ineligible.cue"] == "Incomplete comparison"
    assert de["ux.plan.ineligible.cue"] == "Unvollständiger Vergleich"
    assert "{reduction}" in en["ux.plan.result"]
    assert "{customer_count}" in en["ux.plan.result"]
    assert "{baseline_km}" not in en["ux.plan.result"]
    assert "{optimized_km}" not in en["ux.plan.result"]
    assert "122.394" not in en["ux.plan.result"]
    assert "97.193" not in en["ux.plan.result"]
    assert "20.6" not in en["ux.plan.result"]
    assert en["ux.plan.map.numbers"] == (
        "Stop numbers show the order in which customers are visited."
    )
    assert de["ux.plan.map.numbers"] == (
        "Stoppnummern zeigen die Reihenfolge, in der Kunden angefahren werden."
    )
    assert en["ux.plan.check.passed"] == "Passed"
    assert en["ux.plan.check.failed"] == "Failed"
    assert de["ux.plan.check.passed"] == "Bestanden"
    assert de["ux.plan.check.failed"] == "Nicht bestanden"
    assert en["ux.plan.ineligible"].startswith("A complete route comparison is not available")
    assert "baseline route plan is incomplete" not in en["ux.plan.ineligible"]
    assert "Both plans serve all" not in en["ux.plan.ineligible"]
    assert en["ux.plan.no_solution"] == "No complete solution found"
    assert "heuristic_incomplete" not in en["ux.plan.served.each"]
    assert en["scenario.generated.label"] == "Custom scenario"
    assert de["scenario.generated.label"] == "Eigenes Szenario"
    assert en["ux.plan.tab.comparison"] == "Comparison"
    assert en["ux.plan.tab.baseline"] == "Baseline details"
    assert en["ux.plan.tab.optimised"] == "Optimized details"
    assert en["ux.plan.view.baseline"] == "View baseline route details"
    assert en["ux.plan.view.optimised"] == "View optimized route details"
    assert de["ux.plan.view.baseline"] == "Baseline-Tourdetails anzeigen"
    assert de["ux.plan.view.optimised"] == "Optimierte Tourdetails anzeigen"
    assert en["ux.plan.kpi.baseline"] == "Baseline distance travelled"
    assert en["ux.plan.total"].startswith("Total fleet distance travelled")
    assert en["check.audit.INVARIANTS"] == "Solution consistency checks passed"
    assert en["check.audit.DISTANCE"] == "Route distances reconciled"
    assert en["ux.plan.exports"] == "Export results"
    assert en["ux.plan.validation"] == "Validation summary"
    assert "ux.plan.excel" not in en
    assert en["ux.optimised"] == "Optimized solution (OR-Tools)"
    assert "OR-Tools" not in en["ux.plan.opt.heading"]
    assert "OR-Tools" not in en["ux.plan.result"]
    assert "Optimal solution" not in en["ux.plan.opt.heading"]
    assert "feasible-solution invariants" not in en["check.audit.INVARIANTS"]
    assert "OR-Tools" not in de["ux.plan.opt.heading"]
    assert de["ux.plan.title"] == "Tourenvergleich"
    for key, value in en.items():
        if key.startswith("ux.plan."):
            assert "OR-Tools" not in value
            assert "Optimal solution" not in value
            assert "feasible-solution invariants" not in value


def test_methodology_and_overview_copy_use_academic_cvrp_terms() -> None:
    assert "absence of a complete solution" in STRINGS["en"]["ux.method.solver.none"]
    assert STRINGS["en"]["ux.method.opensolver.title"] == "Research lineage"
    assert "OpenSolver" in STRINGS["en"]["ux.method.opensolver"]
    assert "not the solver used by this application" in STRINGS["en"]["ux.method.opensolver"]
    assert "PATH_CHEAPEST_ARC" in STRINGS["en"]["ux.method.solver"]
    assert "GUIDED_LOCAL_SEARCH" in STRINGS["en"]["ux.method.solver"]
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


def test_recruiter_copy_does_not_point_at_localhost_api() -> None:
    banned = ("localhost", "127.0.0.1", "port 8000", "Port 8000", ":8000", ":8501")
    for table in STRINGS.values():
        for value in table.values():
            assert all(token not in value for token in banned)


def test_planning_service_starting_copy_is_recruiter_facing() -> None:
    en = STRINGS["en"]
    de = STRINGS["de"]
    assert en["ux.api.starting"] == (
        "Planning service is starting. This can take a little longer after a period of inactivity."
    )
    assert de["ux.api.starting"] == (
        "Planungsdienst wird gestartet. Nach längerer Inaktivität kann dies etwas länger dauern."
    )
    assert en["ux.api.starting.title"] == "Planning service is starting"
    assert de["ux.api.starting.title"] == "Planungsdienst wird gestartet"
    assert en["api.status.starting"] == "Planning service is starting"
    assert de["api.status.starting"] == "Planungsdienst wird gestartet"
    assert en["ux.api.offline.title"] == "Planning service unavailable"
    hosting = (
        "Render",
        "cold start",
        "cold-start",
        "free tier",
        "Free tier",
        "Community Cloud",
        "onrender",
        "streamlit.app",
    )
    for table in STRINGS.values():
        for value in table.values():
            assert all(token not in value for token in hosting)


def test_expired_run_copy_is_recruiter_facing() -> None:
    en = STRINGS["en"]
    de = STRINGS["de"]
    assert en["ux.plan.expired.title"] == "Route result expired"
    assert en["ux.plan.expired.body"] == (
        "This saved route result is no longer available. "
        "Run the scenario again to generate a new comparison."
    )
    assert en["ux.plan.expired.action"] == "Run scenario again"
    assert de["ux.plan.expired.title"] == "Tourenergebnis abgelaufen"
    assert de["ux.plan.expired.body"] == (
        "Dieses gespeicherte Tourenergebnis ist nicht mehr verfügbar. "
        "Führen Sie das Szenario erneut aus, um einen neuen Vergleich zu erzeugen."
    )
    assert de["ux.plan.expired.action"] == "Szenario erneut ausführen"
    banned = ("404", "Render", "free tier", "Free tier", "localhost", "127.0.0.1")
    for key in ("ux.plan.expired.title", "ux.plan.expired.body", "ux.plan.expired.action"):
        for table in STRINGS.values():
            assert all(token not in table[key] for token in banned)
    assert en["ux.plan.expired.title"] != en["ux.api.offline.title"]
    assert en["ux.plan.expired.title"] != en["ux.plan.no_solution"]
    assert en["status.infeasible.label"] != en["ux.plan.expired.title"]


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


def test_solution_verification_copy_is_precise() -> None:
    en = STRINGS["en"]
    de = STRINGS["de"]
    assert en["nav.inspect"] == "Solution verification"
    assert de["nav.inspect"] == "Lösungsprüfung"
    assert en["inspect.subtitle"] == (
        "Verify the returned route plan against customer-service, vehicle-capacity, "
        "route-connectivity and distance-consistency requirements."
    )
    assert de["inspect.subtitle"] == (
        "Den zurückgegebenen Tourenplan gegen die Anforderungen an Kundenbedienung, "
        "Fahrzeugkapazität, Touranbindung und Distanzkonsistenz prüfen."
    )
    assert en["inspect.verdict.pass"] == "All solution checks passed"
    assert de["inspect.verdict.pass"] == "Alle Lösungsprüfungen bestanden"
    assert en["inspect.verdict.fail"] == "One or more solution checks failed"
    assert de["inspect.verdict.fail"] == (
        "Eine oder mehrere Lösungsprüfungen sind fehlgeschlagen"
    )
    assert "{passed}" in en["inspect.verdict.count"]
    assert "{total}" in en["inspect.verdict.count"]
    assert "5" not in en["inspect.verdict.pass"]
    assert "five" not in en["inspect.verdict.pass"].lower()
    assert en["inspect.check.coverage"] == "Customer coverage"
    assert en["inspect.check.capacity"] == "Vehicle capacity"
    assert en["inspect.check.depot"] == "Depot / route connectivity"
    assert en["inspect.check.distance"] == "Distance reconciliation"
    assert en["inspect.check.invariants"] == "Solution invariants"
    assert de["inspect.check.coverage"] == "Kundenabdeckung"
    assert de["inspect.check.capacity"] == "Fahrzeugkapazität"
    assert de["inspect.check.depot"] == "Depot-/Touranbindung"
    assert de["inspect.check.distance"] == "Distanzabgleich"
    assert de["inspect.check.invariants"] == "Lösungsinvarianten"
    assert en["inspect.col.delivered"] == "Demand served (totes)"
    assert de["inspect.col.delivered"] == "Bedienter Bedarf (Totes)"
    assert en["inspect.col.selected"] == "Selected route leg"
    assert de["inspect.col.selected"] == "Gewählter Tourabschnitt"
    assert en["inspect.view.assignments"] == "View customer assignments"
    assert en["inspect.view.legs"] == "View route legs"
    assert en["inspect.view.loads"] == "View cumulative loads"
    assert en["inspect.view.distance"] == "View distance reconciliation"
    assert en["inspect.view.matrix"] == "View distance matrix"
    assert de["inspect.view.legs"] == "Tourabschnitte anzeigen"
    assert en["inspect.scope"] == (
        "Verification confirms internal consistency with the application checks; "
        "it does not prove global optimality."
    )
    assert de["inspect.scope"] == (
        "Die Prüfung bestätigt die interne Konsistenz anhand der Anwendungsprüfungen; "
        "sie beweist keine globale Optimalität."
    )
    inspect_copy = " ".join(
        value for key, value in en.items() if key.startswith("inspect.") or key == "nav.inspect"
    )
    inspect_copy_de = " ".join(
        value for key, value in de.items() if key.startswith("inspect.") or key == "nav.inspect"
    )
    lowered = inspect_copy.lower()
    assert "independent model validation" not in lowered
    assert "proven optimal" not in lowered
    assert "validated real-world" not in lowered
    assert "selected drive" not in lowered
    assert "Gewählte Fahrt" not in inspect_copy_de
    assert en["inspect.col.delivered"] != "Delivered"
    assert de["inspect.col.delivered"] != "Geliefert"
    assert en["ux.plan.validation"] == "Validation summary"
    assert en["ux.plan.validation.open"] == "View solution verification"
    assert de["ux.plan.validation.open"] == "Lösungsprüfung anzeigen"
    assert en["ux.method.inspect"] == "Open solution verification"
    assert de["ux.method.inspect"] == "Lösungsprüfung öffnen"
    assert "model validation" not in " ".join(en.values()).lower()
    assert "Modellprüfung" not in " ".join(de.values())
    assert "Modellvalidierung" not in " ".join(de.values())
    assert en["nav.secondary"] == "MODEL & METHODS"
