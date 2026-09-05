"""Recruiter-facing copy. English and German. No planning logic."""

from __future__ import annotations

from typing import Any

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "lang.label": "Language / Sprache",
        "lang.help": (
            "Switch the whole interface to German. Die gesamte Oberfläche gibt es auch auf Deutsch."
        ),
        "lang.hint": "Deutsch verfügbar",
        "lang.sidebar": "Need German? Use Language / Sprache at the top right.",
        "synthetic.notice": (
            "LastMile Lab is a fictional portfolio case study. ViennaCart is a fictional "
            "operator. All depots, customers, order demands, routes, distances, and "
            "operating assumptions are synthetic. The application does not use proprietary "
            "customer data or live Vienna traffic information."
        ),
        "nav.home": "Home",
        "nav.dispatch": "Scenario Setup",
        "nav.routes": "Route Plan",
        "nav.compare": "Solution Comparison",
        "nav.inspect": "Model Validation",
        "nav.learn": "Illustrative Example",
        "nav.session": "Current session",
        "nav.technical": "Technical details",
        "nav.glossary": "Terminology",
        "nav.scenario": "Scenario",
        "nav.baseline": "Baseline solution",
        "nav.optimised": "Optimized solution",
        "tech.endpoint": "Service URL",
        "tech.endpoint.hint": "Address used by this interface to request scenario and route results.",
        "tech.scenario": "Active dataset",
        "tech.scenario.hint": "Internal identifier of the customer, fleet, and distance data now loaded.",
        "tech.baseline": "Nearest-neighbour result",
        "tech.baseline.hint": "Storage ID of the last baseline plan. It is created only after you run that method.",
        "tech.optimised": "OR-Tools result",
        "tech.optimised.hint": "Storage ID of the last optimised plan. It is created only after you run OR-Tools.",
        "tech.not_generated": "Not generated yet",
        "tech.help": (
            "These identifiers are bookkeeping for the local optimisation service. "
            "They are not KPIs and they are not route sequences."
        ),
        "api.connected": "Optimisation service available",
        "api.offline": "Optimisation service unavailable",
        "api.reconnect": "Load the scenario again after restarting the optimisation service.",
        "api.server": "The optimisation service returned an unexpected server error.",
        "brand.sub": "CVRP decision support",
        "glossary.body": (
            "**Tote.** A standard reusable delivery container. Demand and vehicle capacity "
            "are measured in the same unit.\n\n"
            "**Nearest-neighbour baseline.** A transparent construction method that selects "
            "the nearest feasible customer at each step. It provides a reference solution, "
            "not a guarantee of minimum distance.\n\n"
            "**Optimized solution.** The best feasible solution returned by Google OR-Tools "
            "within the selected search time.\n\n"
            "**Feasible solution.** Every customer is served exactly once and no vehicle "
            "exceeds capacity.\n\n"
            "**Illustrative example.** A six-customer scenario (internal identifier LEARNING_6) "
            "showing how a locally attractive choice can leave a customer unserved.\n\n"
            "**Schematic map.** Straight connections between stops. It does not represent "
            "road geometry, driving directions, or live traffic.\n\n"
            "**Unsplit order.** All totes for one customer must be assigned to one vehicle.\n\n"
            "**No solution returned.** The search did not produce a complete assignment. "
            "This is not, by itself, proof that the problem is infeasible."
        ),
        "footer": (
            "LastMile Lab is a fictional case study. This interface presents service results; "
            "it does not recalculate routes."
        ),
        "empty.open": "Go to Scenario Setup",
        "status.none": "No plan yet.",
        "status.unknown": "Status returned by the optimisation service.",
        "status.feasible.label": "Feasible solution",
        "status.feasible.hint": (
            "Every customer is served once and no vehicle is overloaded. "
            "For the Vienna scenario, this is the best solution found within the search time. "
            "It is not a proof of global optimality."
        ),
        "status.feasible.hint.learning_6": (
            "Every customer is served once and no vehicle is overloaded. "
            "For this six-customer example the 31.000 km plan is independently verified "
            "as the shortest complete assignment."
        ),
        "status.heuristic_incomplete.label": "Incomplete baseline",
        "status.heuristic_incomplete.hint": (
            "The greedy method built some routes but left customers out. "
            "It is not valid as a complete-solution comparison distance."
        ),
        "status.no_solution_found.label": "No complete solution returned",
        "status.no_solution_found.hint": (
            "Orders fit in principle, but the search did not return a full assignment. "
            "That is not the same as proving it is impossible."
        ),
        "status.infeasible.label": "Pre-check failed",
        "status.infeasible.hint": (
            "Either one order is larger than a vehicle, or total totes exceed the fleet. "
            "The optimiser is not started."
        ),
        "status.invalid.label": "Validation error",
        "status.invalid.hint": "The dataset did not pass validation.",
        "status.error.label": "Planning service error",
        "status.error.hint": "The optimisation service returned an unexpected error.",
        "status.pending.label": "Waiting",
        "status.pending.hint": "Waiting for a result.",
        "status.passed.label": "Pre-checks passed",
        "status.passed.hint": (
            "Every order fits on a vehicle, and the fleet has enough total space. "
            "The baseline and optimisation methods are available."
        ),
        "home.kicker": "Decision-support demonstration | Vienna",
        "home.title": "Capacitated Vehicle Routing for Urban Deliveries",
        "home.subtitle": (
            "Assign each customer order to one vehicle, choose the stop sequence, and compare "
            "a transparent nearest-neighbour baseline with a time-limited OR-Tools search for "
            "shorter feasible routes."
        ),
        "home.api": "Optimisation service",
        "home.api.help": "If the service is offline, start the FastAPI process on port 8000.",
        "home.api.on": "Online",
        "home.api.off": "Offline",
        "home.url": "Service endpoint",
        "home.url.help": "Where this screen sends requests. Local default is http://127.0.0.1:8000.",
        "home.scenario": "Active scenario",
        "home.scenario.help": (
            "Selecting another scenario clears the current baseline and optimised solutions."
        ),
        "home.model": "Problem class",
        "home.model.value": "Static CVRP",
        "home.model.help": (
            "Capacitated vehicle routing with one depot, unsplit orders, and no time windows."
        ),
        "home.about": "About this case study",
        "home.about.body": (
            "The Streamlit interface displays results only. Route construction and KPIs are "
            "computed by a local FastAPI optimisation service on port 8000. Distances are estimated "
            "(map formula plus a detour factor, or a published table) and are not live GPS traces. "
            "The recommended Vienna scenario has 24 customers, 108 totes, and four vehicles of 30 totes. "
            "The illustrative example uses six customers and the internal identifier LEARNING_6."
        ),
        "home.tech.endpoint": "Service endpoint",
        "home.tech.scenario": "Internal scenario identifier",
        "home.offline": (
            "This interface cannot reach the optimisation service. Start it on port 8000, then reload. "
            "Streamlit Community Cloud cannot host the accompanying optimisation service."
        ),
        "home.what": "Decision context",
        "home.what.cap": "A static morning delivery scenario without live traffic updates.",
        "home.what.body": (
            "ViennaCart (fictional) must visit every customer once. Each vehicle loads at the depot, "
            "delivers, and returns. Orders are measured in **totes**, which are standard "
            "delivery containers. "
            "An order cannot be split across two vehicles. The goal is **shorter total distance**, "
            "including the drive back to the depot.\n\n"
            "Hover any **tote** label in the app for a one-line definition."
        ),
        "home.walk": "Recommended review sequence",
        "home.walk.cap": (
            "Start with the Vienna scenario, then use the illustrative example to examine method behaviour."
        ),
        "home.s1.title": "1. Select the Vienna scenario",
        "home.s1.body": (
            "Review 24 orders, 108 totes, and four vehicles with capacity for 30 totes each. "
            "Zone Z1 requires more than one vehicle."
        ),
        "home.s2.title": "2. Generate both solutions",
        "home.s2.body": (
            "Run the nearest-neighbour baseline and the OR-Tools optimisation. Compare "
            "distance only when both solutions serve every customer."
        ),
        "home.s3.title": "3. Review route operations",
        "home.s3.body": (
            "Inspect stop sequences, vehicle utilisation, and schematic route connections."
        ),
        "home.s4.title": "4. Examine the illustrative example",
        "home.s4.body": (
            "With six customers the greedy plan leaves C4 out (27.000 km of partial routes). "
            "A named packing is 34.000 km. The proven shortest complete plan is 31.000 km."
        ),
        "home.cta1": "Configure the Vienna scenario",
        "home.cta2": "Open the illustrative example",
        "home.pages": "Pages",
        "home.pages.cap": (
            "Each page displays results from the FastAPI optimisation service. "
            "This browser does not solve routes."
        ),
        "home.p1": "Load a scenario, run feasibility checks, and generate both solution methods.",
        "home.p2": "Stop lists, vehicle summaries, and the schematic map.",
        "home.p3": "Side-by-side distances. Improvement % only if both plans are complete.",
        "home.p4": "See how assignments were rebuilt from the routes, in plain language and tables.",
        "home.p5": (
            "Why a greedy construction can leave customer C4 unserved, a 34.000 km feasible packing, "
            "and the verified 31.000 km optimum."
        ),
        "home.not": "What this demonstration does not include",
        "home.not.body": (
            "- Live Vienna traffic or turn-by-turn road routing\n"
            "- Delivery time windows or split orders\n"
            "- A claim that the Vienna OR-Tools result is globally optimal\n"
            "- Distances computed in this browser. Distance and utilisation are returned by "
            "the FastAPI optimisation service running on port 8000"
        ),
        "dispatch.kicker": "Workflow 1 of 5 | Scenario configuration",
        "dispatch.title": "Configure and Solve a Delivery Scenario",
        "dispatch.subtitle": (
            "Select a scenario, review capacity feasibility, and generate a "
            "nearest-neighbour baseline or an optimised OR-Tools solution."
        ),
        "dispatch.pick": "Select a scenario",
        "dispatch.pick.cap": (
            "The Vienna scenario provides an operational demonstration. The illustrative example "
            "shows why a greedy construction can leave a customer unserved."
        ),
        "dispatch.pick.help": (
            "Built-in scenarios are persistent. Generated scenarios (GEN_...) remain available "
            "only while the optimisation service is running."
        ),
        "dispatch.solve": "Generate route solutions",
        "dispatch.solve.cap": (
            "Use the baseline as a transparent reference, then run OR-Tools for comparison."
        ),
        "dispatch.settings": "Optimisation settings",
        "dispatch.need_load": (
            "The selected scenario is not active. Select Load scenario before generating a solution."
        ),
        "dispatch.time": "OR-Tools search time",
        "dispatch.time.help": (
            "How long Google OR-Tools may search: 1, 5, or 10 seconds. "
            "Five seconds is recommended for the demonstration. A longer search may find "
            "a shorter feasible solution, but does not prove global optimality."
        ),
        "dispatch.load": "Load scenario",
        "dispatch.load.help": "Fetch customers, vehicle sizes, distances, and the three capacity checks.",
        "dispatch.validate": "Run pre-checks again",
        "dispatch.validate.help": (
            "Repeat the three capacity questions. The third is information only and never blocks planning."
        ),
        "dispatch.baseline": "Generate baseline",
        "dispatch.baseline.help": (
            "Greedy nearest-neighbour: always add the closest order that still fits. "
            "On the 6-customer example this is expected to leave someone out."
        ),
        "dispatch.optimise": "Generate optimised solution",
        "dispatch.optimise.help": (
            "Search for a shorter complete plan, up to the time you selected. "
            "The screen waits until the search finishes."
        ),
        "dispatch.loaded": "Loaded {id}.",
        "dispatch.demand": "Orders and vehicle space",
        "dispatch.demand.cap": (
            "A tote is one standard delivery box. Orders and vehicle capacity use the same unit."
        ),
        "dispatch.m.customers": "Customers",
        "dispatch.m.customers.help": "A complete plan visits each customer exactly once.",
        "dispatch.m.demand": "Total demand",
        "dispatch.m.demand.help": (
            "How many totes (standard boxes) must leave the depot. "
            "One customer’s totes all travel on the same vehicle."
        ),
        "dispatch.m.fleet": "Fleet",
        "dispatch.m.fleet.help": "Identical vehicles. A vehicle may stay unused.",
        "dispatch.m.capacity": "Fleet capacity",
        "dispatch.m.capacity.help": "If total totes exceed this, planning stops before the optimiser.",
        "dispatch.m.minvans": "Vehicles needed if boxes could be split",
        "dispatch.m.minvans.help": (
            "A lower bound only. Whole orders cannot be split, so you may still need more vehicles."
        ),
        "dispatch.m.ratio": "Space used if packed perfectly",
        "dispatch.m.ratio.help": (
            "Total totes ÷ fleet totes. Necessary, but not enough, because orders stay whole."
        ),
        "dispatch.m.source": "How distance is estimated",
        "dispatch.m.source.help": (
            "Vienna uses a map formula plus a detour factor rather than live GPS data. "
            "The illustrative example uses a published fixed distance table."
        ),
        "dispatch.checks": "Feasibility pre-checks",
        "dispatch.checks.cap": (
            "The first two checks can stop solution generation. The third provides context only."
        ),
        "dispatch.checks.note": (
            "These checks only ask whether each order fits on a vehicle and whether the fleet "
            "has enough total boxes. They do **not** prove that whole orders can be grouped "
            "across vehicles. If assignment later fails, the application reports that no "
            "complete solution was returned. It does not claim that the problem is infeasible."
        ),
        "check.col.check": "Check",
        "check.col.name": "Plain-language test",
        "check.col.result": "Result",
        "check.col.stops": "Can stop planning?",
        "check.col.detail": "Detail",
        "check.ok": "OK",
        "check.fail": "Failed",
        "check.stops_yes": "Yes",
        "check.stops_no": "No, information only",
        "check.CHECK_1": "Each order fits on one vehicle",
        "check.CHECK_2": "The fleet has enough total space",
        "check.CHECK_3": "Lowest vehicle count if boxes could be split",
        "check.CHECK_4": "The data file looks complete",
        "dispatch.orders": "Customer orders",
        "dispatch.map": "Where customers are (synthetic)",
        "dispatch.map.cap": "Marker size follows tote demand. OpenStreetMap is a backdrop, not live operations.",
        "dispatch.matrix": "Distance table",
        "dispatch.matrix.cap": "The 6-customer example has no city map. Distances come from a published table.",
        "dispatch.nogeo": "This dataset has no map coordinates. Distances are shown as a table.",
        "dispatch.matrix.full": "Full distance table (km, three decimals)",
        "dispatch.matrix.full.cap": "Stored as whole metres, shown as kilometres. The table is symmetric.",
        "dispatch.runs": "Plans in this session",
        "dispatch.runs.cap": "After a run, open See routes.",
        "dispatch.simple": "Nearest-neighbour baseline",
        "dispatch.or": "Optimized solution (OR-Tools)",
        "dispatch.norun": "Not run for this dataset yet.",
        "dispatch.total": "Total distance: {km}",
        "dispatch.partial": "Partial distance (not a full plan): {km}",
        "dispatch.not_optimal": (
            "Best feasible solution found within the search time. Global optimality is not claimed."
        ),
        "dispatch.next.routes": "See the routes",
        "dispatch.next.compare": "Compare the two plans",
        "dispatch.gen": "Create another synthetic city dataset",
        "dispatch.gen.cap": (
            "Stored only in the running optimisation service. Distances remain estimates, not road routes."
        ),
        "scenario.VIENNA_STANDARD_24.label": "Vienna, 24 orders (recommended)",
        "scenario.VIENNA_STANDARD_24.help": (
            "24 synthetic customers around Vienna, 108 totes, four vehicles of 30 totes. "
            "Zone Z1 needs 35 totes, so one vehicle cannot cover a whole district."
        ),
        "scenario.LEARNING_6.label": "Illustrative example (6 customers)",
        "scenario.LEARNING_6.help": (
            "A compact worked scenario (id LEARNING_6): 20 totes on two vehicles of capacity 10. "
            "The greedy plan leaves customer C4 (5 totes) out. The optimiser should return 31.000 km. "
            "This scenario uses a fixed distance table rather than city coordinates."
        ),
        "scenario.INFEASIBLE_SINGLE_OVERSIZE.label": "Pre-check case: order exceeds vehicle capacity",
        "scenario.INFEASIBLE_SINGLE_OVERSIZE.help": (
            "One whole order does not fit on any vehicle. Planning stops; the optimiser is not run."
        ),
        "scenario.INFEASIBLE_FLEET_OVERFLOW.label": "Pre-check case: demand exceeds fleet capacity",
        "scenario.INFEASIBLE_FLEET_OVERFLOW.help": (
            "Total totes exceed fleet space. Planning stops; the optimiser is not run."
        ),
        "scenario.INFEASIBLE_BIN_PACKING.label": "Enough space, but orders will not group",
        "scenario.INFEASIBLE_BIN_PACKING.help": (
            "Each order fits, and total space is enough, but whole orders cannot be paired onto vehicles. "
            "The optimiser reports “no complete plan found”, not “impossible”."
        ),
        "scenario.generated.help": (
            "A generated synthetic city available only in the current service process."
        ),
        "scenario.fallback.help": "A built-in or generated delivery dataset.",
        "tote.help": "Tote: a standard delivery box. Demand and vehicle capacity are both counted in totes.",
        "tote.word": "totes",
        "routes.kicker": "Workflow 2 of 5 | Operational review",
        "routes.title": "Review Vehicle Routes and Capacity Utilisation",
        "routes.subtitle": (
            "Inspect stop sequences, assigned demand, route distance, and capacity utilisation "
            "for each vehicle in the selected solution."
        ),
        "routes.pick": "Which plan?",
        "routes.pick.help": "Switching only reloads saved results. It does not run the optimiser again.",
        "routes.opt": "Optimized solution",
        "routes.base": "Nearest-neighbour baseline",
        "routes.empty.title": "No plan yet",
        "routes.empty.body": (
            "Generate a baseline or optimised solution in Scenario setup, then return to this page."
        ),
        "routes.kpis": "At a glance",
        "routes.kpis.cap": "Returned by the optimisation service without browser-side recalculation.",
        "compare.kicker": "Workflow 3 of 5 | Performance comparison",
        "compare.title": "Compare Baseline and Optimised Solutions",
        "compare.subtitle": (
            "Compare solution completeness, fleet utilisation, and total distance using metrics "
            "returned by the optimisation service."
        ),
        "compare.empty.title": "Need both plans",
        "compare.empty.body": (
            "Generate the baseline and optimised solutions for the same scenario first."
        ),
        "compare.nn": "Nearest-neighbour baseline",
        "compare.nn.cap": "Deterministic greedy construction used as a transparent reference.",
        "compare.or": "Optimized solution (OR-Tools)",
        "compare.or.cap": "Best feasible solution returned within the selected search time.",
        "compare.need_both": (
            "A distance improvement is shown only when both plans serve every customer. "
            "A partial greedy plan is never given a made-up complete distance."
        ),
        "inspect.kicker": "Workflow 4 of 5 | Model validation",
        "inspect.title": "Validate Route Reconstruction and Constraints",
        "inspect.subtitle": (
            "Reconstruct assignments, selected arcs, and cumulative loads from the returned "
            "stop sequences, then reconcile them with the documented model constraints."
        ),
        "inspect.empty.title": "Nothing to check yet",
        "inspect.empty.body": "Run a plan on Plan deliveries first.",
        "learn.kicker": "Workflow 5 of 5 | Illustrative CVRP example",
        "learn.title": "Local Decisions and Global Solution Quality",
        "learn.subtitle": (
            "A six-customer case shows why a locally sensible routing choice can prevent a "
            "complete assignment, and why feasibility and minimum distance are separate questions."
        ),
        "learn.callout": (
            "**Three results use the same orders and distance matrix.** The deterministic "
            "nearest-neighbour baseline constructs 27.000 km of routes but leaves customer C4 "
            "unserved. A named reference plan serves everyone in 34.000 km. OR-Tools returns a "
            "31.000 km plan, and exhaustive enumeration independently verifies that 31.000 km "
            "is optimal."
        ),
        "learn.backend": "How the Results Are Produced",
        "learn.backend.body": (
            "**Input.** The FastAPI backend loads six unsplit customer orders, two vehicles "
            "with capacity for 10 totes each, and a fixed symmetric distance matrix.\n\n"
            "**Baseline.** Vehicles open in ID order. At each stop, the algorithm selects the "
            "nearest unserved customer whose complete order fits in the remaining capacity. "
            "Equal distances are resolved by customer ID.\n\n"
            "**Optimisation.** Google OR-Tools searches for a complete minimum-distance CVRP "
            "solution. For this small case, a separate exhaustive test evaluates all 72 feasible "
            "route-order combinations and confirms the 31 km minimum.\n\n"
            "**Reference plan.** The 34 km plan is a fixed, feasible comparison calculated from "
            "the same backend matrix. It is neither the greedy output nor an optimiser result."
        ),
        "learn.load": "Set this scenario as active",
        "learn.load.help": (
            "Applies the six-customer scenario to Route Plan, Solution Comparison, and Model Validation."
        ),
        "learn.loaded": "The other pages now use the six-customer illustrative example.",
        "export.title": "Download this plan",
        "export.cap": "Files include scenario and run identifiers. Values come from the optimisation service.",
        "export.json": "Download JSON",
        "export.csv": "Download CSV zip",
        "van.label": "Vehicle",
        "van.unused": "Unused",
        "van.route": "Route",
        "van.orders": "Delivery stops",
        "van.load": "Assigned demand",
        "van.util": "Capacity utilisation",
        "van.util.short": "utilised",
        "van.distance": "Distance",
        "van.load.hint": (
            "Assigned demand is the total number of totes allocated to this vehicle."
        ),
        "van.idle": "This vehicle was not used. Unused vehicles are permitted.",
        "van.capacity": "Capacity",
        "van.util.hint": "The bar shows capacity utilisation: assigned demand divided by vehicle capacity.",
        "note.learning": (
            "This is the expected greedy result on the 6-customer example, not a failed app. "
            "Customers left out: {unserved}. Total distance stays blank; the kilometres are a "
            "partial construction only, not the 34 km packing. Run the optimiser for the 31 km "
            "complete plan, or stay on this example page."
        ),
        "note.incomplete": (
            "The greedy method built some routes but could not serve everyone. "
            "It is not valid as a complete-solution comparison distance.{unserved}"
        ),
        "note.unserved": " Left out: {ids}.",
        "summary.ineligible": (
            "The baseline did not serve every customer ({status}), so no improvement is reported."
        ),
        "summary.unserved": "Customers left out: {ids}.",
        "summary.partial": "Constructed greedy distance is {km} as a partial plan only.",
        "summary.opt_ok": "The optimiser returned a complete plan of {km}.",
        "summary.opt_bad": "Optimiser status: {status}.",
        "summary.opt_incomplete": (
            "The baseline is complete at {km}, but the optimised result is not comparable ({status})."
        ),
        "summary.ok": (
            "The baseline covers {base_km} with {base_vans} vehicles. "
            "The optimised solution returns {opt_km} using {opt_vans} vehicles. "
            "Distance improvement: {improve}."
        ),
        "common.yes": "Yes",
        "common.no": "No",
        "common.na": "N/A",
        "unit.totes": "{n} totes",
        "unit.fleet": "{vans} × {cap} totes",
        "dist.fixed_matrix": "Published table",
        "dist.haversine_detour": "Map estimate + detour",
        "check.msg.integrity_ok": "The dataset looks complete.",
        "check.msg.demand_ok": "The largest order still fits on one vehicle.",
        "check.msg.demand_fail": "At least one order is larger than a vehicle.",
        "check.msg.fleet_ok": "Total boxes fit in the fleet.",
        "check.msg.fleet_fail": "Total boxes exceed fleet space.",
        "check.msg.minvans": (
            "If totes could be split, you would need at least {n} vehicles. "
            "This is a lower bound only. Whole orders may need more vehicles."
        ),
        "check.num": "{n}",
        "dispatch.time.1": "1 second (quick search)",
        "dispatch.time.5": "5 seconds (recommended)",
        "dispatch.time.10": "10 seconds (extended search)",
        "dispatch.run": "Run `{id}`",
        "dispatch.term": "Search stopped: `{term}`",
        "dispatch.last_validate": "Last capacity-check response (technical)",
        "dispatch.col.customer": "Customer",
        "dispatch.col.zone": "Zone",
        "dispatch.col.demand": "Demand (totes)",
        "dispatch.col.lat": "Latitude",
        "dispatch.col.lon": "Longitude",
        "dispatch.gen.seed": "Random seed",
        "dispatch.gen.seed.help": "Same seed and settings recreate the same synthetic city.",
        "dispatch.gen.customers": "Customers",
        "dispatch.gen.vans": "Vehicles",
        "dispatch.gen.capacity": "Vehicle capacity (totes)",
        "dispatch.gen.capacity.help": (
            "Every vehicle has this many tote slots. A tote is a standard delivery box."
        ),
        "dispatch.gen.detour": "Detour factor",
        "dispatch.gen.detour.help": (
            "Stretches straight-line distances a little so they feel more like city driving. "
            "Usual demo: 1.25."
        ),
        "dispatch.gen.z1": "Inner-city share (Z1)",
        "dispatch.gen.z2": "Inner-ring share (Z2)",
        "dispatch.gen.z3": "Outer-ring share (Z3)",
        "dispatch.gen.z4": "Outer share (Z4)",
        "dispatch.gen.zone.help": "How many customers land in this band. The four shares should add up to about 1.",
        "dispatch.gen.button": "Create dataset",
        "dispatch.gen.button.help": "The optimisation service retains this scenario until it restarts.",
        "dispatch.gen.ok": "Created `{id}`.",
        "routes.mismatch": (
            "This plan belongs to a different dataset. Load and solve the current dataset again."
        ),
        "routes.m.served": "Customers served",
        "routes.m.served.help": "A complete plan visits every customer exactly once.",
        "routes.m.demand": "Demand served",
        "routes.m.demand.help": "Totes (standard boxes) already on constructed routes.",
        "routes.m.vans": "Vehicles used",
        "routes.m.vans.help": "A vehicle counts as used when it visits at least one customer.",
        "routes.m.total": "Total distance",
        "routes.m.total.help": "Sum of used vehicle tours, including the drive back to the depot.",
        "routes.m.partial": "Partial distance",
        "routes.m.partial.help": (
            "Distance of the routes that were built. Not a full plan, so not a fair comparison."
        ),
        "routes.unserved": "Left out: {ids}",
        "routes.map": "Schematic map",
        "routes.map.cap": "City map as a backdrop. Lines are straight connections, not driving directions.",
        "routes.diagram": "Schematic layout",
        "routes.diagram.cap": (
            "Node positions support readability. Distances come from the service distance table."
        ),
        "routes.nogeo.l6": (
            "The 6-customer example has no city map. Routes appear as a diagram and as tables."
        ),
        "routes.nogeo": "This dataset has no map coordinates. Routes are shown as tables only.",
        "routes.seq": "Stop Lists",
        "routes.cards": "Vehicle Summaries",
        "routes.cards.cap": "Colours match the map. Unused vehicles are permitted.",
        "routes.unused": "Unused vehicles",
        "table.vehicle": "Vehicle",
        "table.used": "Used",
        "table.sequence": "Stops",
        "table.orders": "Orders",
        "table.load": "Assigned demand (totes)",
        "table.distance": "Distance",
        "table.pack": "Orders on this vehicle",
        "compare.mismatch": (
            "The two solutions belong to different scenarios. Load one scenario and generate both methods."
        ),
        "compare.reading": "What the numbers mean",
        "compare.table": "Side-by-side figures",
        "compare.improve.cap": (
            "Improvement appears only when both plans serve everyone: how much shorter the "
            "optimised solution is, as a percentage of the baseline. The optimisation service computes it."
        ),
        "compare.chart.skip": (
            "The distance chart is hidden because the baseline did not serve every customer."
        ),
        "compare.chart.distance": "Total distance",
        "compare.chart.load": "Boxes on each vehicle (totes)",
        "compare.chart.route": "Distance of each vehicle (km)",
        "compare.warn.incomplete": (
            "The baseline omitted customers. The optimised result is still shown, but the "
            "baseline distance must not be interpreted as a complete solution."
        ),
        "compare.next": "Check how the plan was rebuilt",
        "compare.kpi.status": "Status",
        "compare.kpi.eligible": "Fair to compare?",
        "compare.kpi.served": "Customers served",
        "compare.kpi.demand": "Demand served (totes)",
        "compare.kpi.vans": "Vehicles used",
        "compare.kpi.total": "Total distance",
        "compare.kpi.partial": "Partial distance",
        "compare.kpi.util": "Used-fleet capacity utilisation",
        "compare.kpi.improve": "Distance improvement",
        "compare.col.kpi": "Figure",
        "inspect.pick": "Which plan?",
        "inspect.pick.help": (
            "Tables are rebuilt from the stop list. You are not looking at hidden optimiser internals."
        ),
        "inspect.how": (
            "A customer on a vehicle is an assignment. Consecutive stops become a selected drive. "
            "A vehicle is used if it serves at least one customer. The cumulative value records "
            "demand served, not remaining onboard load."
        ),
        "inspect.solver": "How the optimiser was asked to search",
        "inspect.solver.cap": "Search configuration, distinct from the model decision variables.",
        "inspect.solver.strategy": "Start from a cheap first tour, then locally improve it.",
        "inspect.solver.time": "Search time requested: {n} s",
        "inspect.solver.term": "Search stopped: `{term}`",
        "inspect.solver.runtime": "Search runtime: {n} s",
        "inspect.demand": "Did every customer get their boxes?",
        "inspect.demand.cap": "One row per customer. A complete plan visits each customer once.",
        "inspect.constraints": "Independent checks on the rebuilt routes",
        "inspect.constraints.cap": "These checks look at the returned tours, not at hidden solver memory.",
        "inspect.loads": "Cumulative demand served by stop",
        "inspect.loads.cap": (
            "Cumulative demand served after each stop. This is not the remaining onboard load."
        ),
        "inspect.cum.sequence": "Sequence",
        "inspect.cum.node": "Node",
        "inspect.cum.demand": "Stop demand (totes)",
        "inspect.cum.served": "Cumulative demand served (totes)",
        "inspect.arcs": "Selected drives between stops",
        "inspect.arcs.cap": (
            "Outgoing counts how many selected drives leave a stop. Incoming counts how many arrive."
        ),
        "inspect.arcs.list": "Selected drives",
        "inspect.matrix.van": "Drive table for {id}",
        "inspect.matrix.all": "Full drive tables",
        "inspect.dist": "Distance table",
        "inspect.dist.cap": "Stored as metres, shown as kilometres to three decimals.",
        "inspect.dist.full": "Full distance table",
        "inspect.dist.compact": "Distances of selected drives",
        "inspect.depot": "Stored depot id `{id}` is shown as {label}.",
        "inspect.obj": "Solution distance returned by the optimisation service: {km}",
        "inspect.next": "Open the 6-customer example",
        "inspect.col.customer": "Customer",
        "inspect.col.required": "Required (totes)",
        "inspect.col.delivered": "Delivered",
        "inspect.col.vehicle": "Vehicle",
        "inspect.col.visits": "Visits",
        "inspect.col.check": "Check",
        "inspect.col.from": "From",
        "inspect.col.to": "To",
        "inspect.col.selected": "Selected drive",
        "inspect.col.leg": "Leg distance",
        "learn.inputs": "Example Inputs",
        "learn.inputs.cap": "Six unsplit orders must be assigned to two vehicles with equal capacity.",
        "learn.input.demand": "Total demand",
        "learn.input.capacity": "Fleet capacity",
        "learn.input.rule": "Order rule",
        "learn.input.rule.value": "Unsplit",
        "learn.matrix": "Distance Matrix",
        "learn.matrix.cap": (
            "Each cell is the travel distance from its row location to its column location. "
            "The matrix is symmetric and uses fixed synthetic values."
        ),
        "learn.matrix.hover": "Distances are displayed in kilometres to three decimal places.",
        "learn.matrix.c1": "Example reading: Depot to C1 is {km}.",
        "learn.demand": "Customer Demand",
        "learn.demand.cap": (
            "The 20 totes exactly equal fleet capacity, so both vehicles must be loaded to 10 totes "
            "in any complete plan."
        ),
        "learn.demand.body": (
            "Orders stay whole, so each vehicle’s customers must add to exactly 10 totes. "
            "The greedy method can still get stuck even when the first two capacity checks pass."
        ),
        "learn.actions": "Run the Backend Methods",
        "learn.actions.cap": (
            "Run the deterministic baseline to reproduce its limitation, then run OR-Tools "
            "to obtain a complete optimised plan."
        ),
        "learn.run.base": "Run the Nearest-Neighbour Baseline",
        "learn.run.base.help": (
            "Greedy nearest-neighbour: from the current stop, choose the closest unserved "
            "customer whose whole order still fits. The method never revisits an earlier choice. "
            "Expected result: 27.000 km of partial routes with customer C4 (5 totes) unserved."
        ),
        "learn.greedy.what": (
            "Greedy here means a local rule: at every stop the algorithm takes the nearest "
            "remaining customer that still fits. It does not look ahead, so a cheap early stop "
            "can leave a later order with no remaining capacity."
        ),
        "learn.run.opt": "Run the OR-Tools Optimiser",
        "learn.run.opt.help": (
            "Search for a complete capacity-feasible plan for five seconds. The expected result "
            "is the independently verified 31.000 km optimum."
        ),
        "learn.nn": "1. Nearest-Neighbour Baseline (Incomplete)",
        "learn.nn.cap": (
            "A deterministic construction method, included as a transparent benchmark rather "
            "than a guaranteed complete solution."
        ),
        "learn.nn.need": "Generate the baseline above to load the service result.",
        "learn.nn.body": (
            "Vehicle V01 selects C1, C2, and C3 for a load of 9 totes. Vehicle V02 then selects "
            "C6 and C5 for a load of 6 totes. Customer C4 requires 5 totes and no longer fits. "
            "The 27 km value therefore measures only the routes that were constructed; it is not "
            "a complete-plan distance."
        ),
        "learn.nn.steps": (
            "**V01 starts at the depot with 10 tote slots.** C1 and C6 are both 3.000 km away. "
            "The algorithm breaks the tie by customer ID and selects C1 (4 totes). Remaining "
            "capacity is 6.\n\n"
            "**From C1 the nearest feasible customer is C2** (2.000 km, 2 totes). Remaining "
            "capacity is 4.\n\n"
            "**From C2, C4 does not fit** (5 totes). The nearest customer that still fits is C3 "
            "(3.000 km, 3 totes). Remaining capacity is 1. No remaining order is 1 tote or "
            "smaller, so V01 returns to the depot. Route distance: 16.000 km.\n\n"
            "**V02 starts at the depot with 10 tote slots.** It selects C6 (4 totes) then C5 "
            "(2 totes). Remaining capacity is 4. C4 still needs 5 totes, so V02 also returns "
            "without C4. Route distance: 11.000 km.\n\n"
            "**Result stored by the backend.** Five customers are served. The constructed "
            "distance is 27.000 km. Because C4 is unserved, the status is an incomplete "
            "baseline. That distance must not be compared with 34 km or 31 km as if it were "
            "a complete plan."
        ),
        "learn.served": "Customers served: {served} / {total}",
        "learn.unserved": "Left out: {ids}",
        "learn.partial": "Partial constructed distance: {km}",
        "learn.objective": "Complete-solution distance: N/A",
        "learn.served.label": "Customers served",
        "learn.unserved.label": "Customer unserved",
        "learn.partial.label": "Partial distance",
        "learn.complete.label": "Complete-plan distance",
        "learn.arcs.nn": "Selected drives from consecutive greedy stops",
        "learn.arcs.help": (
            "Outgoing is how many selected drives leave a stop; incoming is how many arrive. "
            "These counts are rebuilt from the stop list."
        ),
        "learn.details": "Show Route Reconstruction Details",
        "learn.pack": "2. Feasible Reference Plan (34 km)",
        "learn.pack.cap": (
            "A fixed comparison plan that proves a complete assignment exists. It is not "
            "generated by either backend method."
        ),
        "learn.pack.body": (
            "Vehicle V01 serves C1, C2, and C6 in 14 km. Vehicle V02 serves C5, C4, and C3 "
            "in 20 km. Both carry exactly 10 totes, so the combined 34 km plan is feasible. "
            "Its purpose is to show that the incomplete baseline is a method limitation, not "
            "evidence that the scenario is infeasible."
        ),
        "learn.pack.total": "Reference plan distance",
        "learn.opt": "3. Verified Optimal Plan (31 km)",
        "learn.opt.cap": (
            "OR-Tools returns this plan; an independent exhaustive test confirms that no shorter "
            "complete plan exists for this six-customer matrix."
        ),
        "learn.opt.need": "Generate the optimised solution above to load the service result.",
        "learn.opt.obj": "Complete-plan distance: {km}",
        "learn.opt.body": (
            "One 13 km route serves C1, C5, and C6. The other 18 km route serves C2, C3, "
            "and C4. Both loads equal 10 totes. Exhaustive enumeration checks the two feasible "
            "customer partitions and every stop ordering, 72 combinations in total, and finds "
            "31 km as the minimum."
        ),
        "learn.arcs.opt": "Selected drives from consecutive optimiser stops",
        "learn.why": "Why the Nearest Feasible Stop Can Fail",
        "learn.why.body": (
            "The backend does not fail here. It applies a published local rule and then reports "
            "that the construction is incomplete.\n\n"
            "From C2 the nearest customer that still fits is C3 at 3.000 km. After that stop, "
            "V01 has only 1 tote slot left, so customer C4 (5 totes) can never join V01. "
            "V02 later has 4 slots left, which is also short of 5. The only remaining 5-tote "
            "order is therefore unserved.\n\n"
            "A complete plan exists if C3 is kept for the other vehicle. That is why the 34 km "
            "reference packing and the 31 km optimum can serve everyone, while the greedy "
            "construction cannot. Feasibility of the data and completeness of this method are "
            "different questions."
        ),
        "learn.edge": "Optional Validation Edge Case",
        "learn.edge.cap": (
            "This is a separate three-customer scenario. It is not part of the six-customer "
            "27/34/31 km comparison."
        ),
        "learn.bin": "When Total Capacity Is Not Enough",
        "learn.bin.cap": (
            "Enough total boxes is not the same as being able to keep every order whole."
        ),
        "learn.bin.body": (
            "This optional case is a **different** dataset from the six-customer example. "
            "It has three 6-tote orders and two 10-tote vehicles.\n\n"
            "Each order fits on one vehicle (6 ≤ 10), and total demand fits the fleet "
            "(18 ≤ 20). The first two capacity checks therefore pass. Whole orders still "
            "cannot be packed: 6 + 6 = 12, which exceeds 10, so two orders cannot share a "
            "vehicle. The third order then has no vehicle left.\n\n"
            "The backend does not add a special infeasibility proof for this grouping failure. "
            "If you ask OR-Tools anyway, the service reports that no complete plan was found. "
            "That status is not the same as proving the instance is infeasible."
        ),
        "learn.bin.validate": "Run the capacity checks",
        "learn.bin.validate.help": "The first two checks should pass. The third is information only.",
        "learn.bin.optimise": "Ask the optimiser anyway",
        "learn.bin.optimise.help": (
            "Expect “no complete plan found”. That is not the same as proving it is impossible."
        ),
        "learn.bin.caption": (
            "If grouping whole orders is impossible, the search reports that it found no complete "
            "solution. It does not relabel the scenario as infeasible."
        ),
        "packing.note": (
            "This 34.000 km plan is a named reference defined for teaching. "
            "It is not produced by the greedy button or the optimiser button. "
            "Leg lengths are taken from the optimisation service distance matrix."
        ),
        "map.schematic": (
            "Straight-line connections from estimated distances. These are not road geometry "
            "or live driving directions."
        ),
        "map.diagram": (
            "Schematic layout only. Distances come from the service table, not from this drawing. "
            "This is not a map."
        ),
    },
    "de": {
        "lang.label": "Language / Sprache",
        "lang.help": (
            "Gesamte Oberfläche auf Deutsch oder Englisch umschalten. "
            "Switch the whole interface to English or German."
        ),
        "lang.hint": "English available",
        "lang.sidebar": "Englisch nötig? Language / Sprache oben rechts verwenden.",
        "synthetic.notice": (
            "LastMile Lab ist eine fiktive Portfolio-Fallstudie. ViennaCart ist ein fiktiver "
            "Betreiber. Alle Depots, Kunden, Auftragsmengen, Touren, Distanzen und "
            "Betriebsannahmen sind synthetisch. Die Anwendung nutzt keine echten Kundendaten "
            "und keine Live-Verkehrsdaten aus Wien."
        ),
        "nav.home": "Start",
        "nav.dispatch": "Szenario einrichten",
        "nav.routes": "Tourenplan",
        "nav.compare": "Lösungsvergleich",
        "nav.inspect": "Modellvalidierung",
        "nav.learn": "Fallbeispiel",
        "nav.session": "Aktuelle Sitzung",
        "nav.technical": "Technische Details",
        "nav.glossary": "Terminologie",
        "nav.scenario": "Szenario",
        "nav.baseline": "Referenzlösung",
        "nav.optimised": "Optimierte Lösung",
        "tech.endpoint": "Dienstadresse",
        "tech.endpoint.hint": "Adresse, an die diese Oberfläche Szenario- und Tourenergebnisse anfragt.",
        "tech.scenario": "Aktiver Datensatz",
        "tech.scenario.hint": "Interne Kennung der aktuell geladenen Kunden-, Flotten- und Distanzdaten.",
        "tech.baseline": "Nächster-Nachbar-Ergebnis",
        "tech.baseline.hint": "Speicher-ID des letzten Referenzplans. Sie entsteht erst nach dem Start dieses Verfahrens.",
        "tech.optimised": "OR-Tools-Ergebnis",
        "tech.optimised.hint": "Speicher-ID des letzten Optimierungsplans. Sie entsteht erst nach dem Start von OR-Tools.",
        "tech.not_generated": "Noch nicht erzeugt",
        "tech.help": (
            "Diese Kennungen sind Buchhaltung des lokalen Optimierungsdienstes. "
            "Sie sind keine Kennzahlen und keine Stopplisten."
        ),
        "api.connected": "Optimierungsdienst verfügbar",
        "api.offline": "Optimierungsdienst nicht verfügbar",
        "api.reconnect": "Laden Sie den Datensatz erneut, nachdem der Optimierungsdienst neu gestartet wurde.",
        "api.server": "Unerwarteter Serverfehler im Optimierungsdienst. Der Dienst läuft.",
        "brand.sub": "CVRP-Entscheidungsunterstützung",
        "glossary.body": (
            "**Tote.** Ein standardisierter wiederverwendbarer Lieferbehälter. Bedarf und "
            "Fahrzeugkapazität werden in derselben Einheit gemessen.\n\n"
            "**Nächster-Nachbar-Referenzlösung.** Ein transparentes Konstruktionsverfahren, "
            "das jeweils den nächsten zulässigen Kunden auswählt. Es liefert eine Referenz, "
            "aber keine Garantie für minimale Distanz.\n\n"
            "**Optimierte Lösung.** Die beste zulässige Lösung, die Google OR-Tools innerhalb "
            "der gewählten Suchzeit zurückgibt.\n\n"
            "**Zulässige Lösung.** Jeder Kunde wird genau einmal bedient und kein Fahrzeug "
            "überschreitet seine Kapazität.\n\n"
            "**Fallbeispiel.** Ein Szenario mit sechs Kunden (interne Kennung LEARNING_6). "
            "Es zeigt, wie eine lokal attraktive Wahl einen Kunden unbedient lassen kann.\n\n"
            "**Schematische Karte.** Gerade Verbindungen zwischen Stopps. Sie zeigt weder "
            "Straßengeometrie noch Fahranweisungen oder Live-Verkehr.\n\n"
            "**Ungeteilter Auftrag.** Alle Totes eines Kunden werden einem Fahrzeug zugeordnet.\n\n"
            "**Keine Lösung zurückgegeben.** Die Suche hat keine vollständige Zuordnung geliefert. "
            "Dies allein beweist nicht, dass das Problem unzulässig ist."
        ),
        "footer": (
            "LastMile Lab ist eine fiktive Fallstudie. Diese Oberfläche zeigt Ergebnisse des "
            "Optimierungsdienstes und rechnet Touren nicht selbst neu."
        ),
        "empty.open": "Zu Szenario einrichten",
        "status.none": "Noch kein Plan.",
        "status.unknown": "Status vom Optimierungsdienst.",
        "status.feasible.label": "Zulässige Lösung",
        "status.feasible.hint": (
            "Jeder Kunde wird einmal bedient, kein Fahrzeug ist überladen. "
            "Für das Wien-Szenario ist dies die beste Lösung innerhalb der Suchzeit. "
            "Globale Optimalität wird nicht nachgewiesen."
        ),
        "status.feasible.hint.learning_6": (
            "Jeder Kunde wird einmal bedient, kein Fahrzeug ist überladen. "
            "Für dieses Sechs-Kunden-Beispiel ist der 31,000-km-Plan unabhängig als "
            "kürzeste vollständige Zuordnung bestätigt."
        ),
        "status.heuristic_incomplete.label": "Unvollständige Referenzlösung",
        "status.heuristic_incomplete.hint": (
            "Das gierige Verfahren hat einige Touren gebaut, aber Kunden ausgelassen. "
            "Diese Distanz ist kein fairer Vergleichswert."
        ),
        "status.no_solution_found.label": "Keine vollständige Lösung zurückgegeben",
        "status.no_solution_found.hint": (
            "Die Aufträge passen grundsätzlich, aber die Suche lieferte keine vollständige Zuordnung. "
            "Das ist kein Beweis, dass es unmöglich ist."
        ),
        "status.infeasible.label": "Vorprüfung nicht bestanden",
        "status.infeasible.hint": (
            "Entweder ist ein Auftrag größer als ein Fahrzeug, oder die Boxen übersteigen die Flotte. "
            "Der Optimierer startet nicht."
        ),
        "status.invalid.label": "Validierungsfehler",
        "status.invalid.hint": "Der Datensatz hat die Prüfung nicht bestanden.",
        "status.error.label": "Fehler im Optimierungsdienst",
        "status.error.hint": "Unerwarteter Fehler im Optimierungsdienst.",
        "status.pending.label": "Warten",
        "status.pending.hint": "Warte auf ein Ergebnis.",
        "status.passed.label": "Vorprüfungen bestanden",
        "status.passed.hint": (
            "Jeder Auftrag passt auf ein Fahrzeug, und die Flotte hat genug Platz. "
            "Referenzverfahren und Optimierung stehen zur Verfügung."
        ),
        "home.kicker": "Demonstration zur Entscheidungsunterstützung | Wien",
        "home.title": "Kapazitätsbeschränkte Tourenplanung für urbane Lieferungen",
        "home.subtitle": (
            "Ordnen Sie jeden Kundenauftrag einem Fahrzeug zu, wählen Sie die Stoppreihenfolge "
            "und vergleichen Sie eine transparente Nächster-Nachbar-Referenzlösung mit einer "
            "zeitlich begrenzten OR-Tools-Suche nach kürzeren zulässigen Touren."
        ),
        "home.api": "Optimierungsdienst",
        "home.api.help": "Steht hier „offline“, starten Sie zuerst den Optimierungsdienst auf Port 8000.",
        "home.api.on": "Online",
        "home.api.off": "Offline",
        "home.url": "Dienst-Endpunkt",
        "home.url.help": "Wohin diese Oberfläche Anfragen sendet. Lokal: http://127.0.0.1:8000.",
        "home.scenario": "Aktives Szenario",
        "home.scenario.help": "Ein Wechsel unter Touren planen verwirft alte einfache und optimierte Pläne.",
        "home.model": "Problemklasse",
        "home.model.value": "Statisches CVRP",
        "home.model.help": (
            "Kapazitätsbeschränkte Tourenplanung mit einem Depot, ungeteilten Aufträgen "
            "und ohne Zeitfenster."
        ),
        "home.about": "Über diese Fallstudie",
        "home.about.body": (
            "Die Streamlit-Oberfläche zeigt nur Ergebnisse. Tourenkonstruktion und Kennzahlen "
            "berechnet ein lokaler FastAPI-Optimierungsdienst auf Port 8000. Distanzen sind Schätzungen "
            "(Kartenformel plus Umwegfaktor oder eine veröffentlichte Tabelle), keine Live-GPS-Spuren. "
            "Das empfohlene Wien-Szenario umfasst 24 Kunden, 108 Totes und vier Fahrzeuge mit je 30 Totes. "
            "Das Fallbeispiel hat sechs Kunden und die interne Kennung LEARNING_6."
        ),
        "home.tech.endpoint": "Dienst-Endpunkt",
        "home.tech.scenario": "Interne Szenariokennung",
        "home.offline": (
            "Die Oberfläche erreicht den Optimierungsdienst nicht. Starten Sie ihn auf Port 8000 und laden Sie neu. "
            "Streamlit Community Cloud kann den zugehörigen Planungsdienst nicht ausführen."
        ),
        "home.what": "Entscheidungskontext",
        "home.what.cap": "Ein statisches morgendliches Lieferszenario ohne Live-Verkehrsdaten.",
        "home.what.body": (
            "ViennaCart (fiktiv) muss jeden Kunden einmal anfahren. Jedes Fahrzeug lädt im Depot, "
            "liefert und kehrt zurück. Aufträge werden in **Totes** gemessen, also "
            "standardisierten Lieferbehältern. "
            "Ein Auftrag darf nicht auf zwei Fahrzeuge aufgeteilt werden. Ziel ist eine **kürzere "
            "Gesamtdistanz**, inklusive Rückfahrt zum Depot.\n\n"
            "Zeigen Sie mit der Maus auf **Tote**, um die Kurzdefinition zu sehen."
        ),
        "home.walk": "Empfohlene Prüfreihenfolge",
        "home.walk.cap": "Beginnen Sie mit dem Wien-Szenario und prüfen Sie danach das Fallbeispiel.",
        "home.s1.title": "1. Wien-Szenario auswählen",
        "home.s1.body": (
            "Prüfen Sie 24 Aufträge, 108 Totes und vier Fahrzeuge mit je 30 Totes Kapazität. "
            "Zone Z1 benötigt mehr als ein Fahrzeug."
        ),
        "home.s2.title": "2. Beide Lösungen erzeugen",
        "home.s2.body": (
            "Der einfache Plan ist gierig und vollständig erklärt. Der Optimierer darf typischerweise "
            "5 Sekunden suchen. Distanzen nur vergleichen, wenn beide Pläne alle Kunden bedienen."
        ),
        "home.s3.title": "3. Tourbetrieb prüfen",
        "home.s3.body": (
            "Prüfen Sie Stoppreihenfolgen, Fahrzeugauslastung und schematische Verbindungen."
        ),
        "home.s4.title": "4. Fallbeispiel analysieren",
        "home.s4.body": (
            "Bei sechs Kunden lässt der gierige Plan C4 aus (27,000 km Teiltouren). "
            "Eine benannte Packung hat 34,000 km. Der bewiesen kürzeste vollständige Plan hat 31,000 km."
        ),
        "home.cta1": "Mit der Wien-Demo starten",
        "home.cta2": "Fallbeispiel öffnen",
        "home.pages": "Seiten",
        "home.pages.cap": (
            "Jede Seite zeigt Ergebnisse des FastAPI-Optimierungsdienstes. "
            "Dieser Browser löst keine Touren."
        ),
        "home.p1": "Datensatz laden, Kapazität prüfen, einfachen Plan und Optimierer starten.",
        "home.p2": "Stoplisten, Fahrzeugübersichten und die schematische Karte.",
        "home.p3": "Distanzen nebeneinander. Verbesserung % nur bei zwei vollständigen Plänen.",
        "home.p4": "Zuordnungen aus den Touren in Klartext und Tabellen nachvollziehen.",
        "home.p5": (
            "Warum eine gierige Konstruktion Kunde C4 auslassen kann, eine zulässige 34,000-km-Packung "
            "und das verifizierte 31,000-km-Optimum."
        ),
        "home.not": "Was diese Demonstration nicht umfasst",
        "home.not.body": (
            "- Live-Verkehr oder Turn-by-Turn-Straßenrouting in Wien\n"
            "- Zeitfenster oder geteilte Aufträge\n"
            "- Die Behauptung, das Wien-Ergebnis von OR-Tools sei global optimal\n"
            "- Im Browser berechnete Distanzen. Distanz und Auslastung liefert der "
            "FastAPI-Optimierungsdienst auf Port 8000"
        ),
        "dispatch.kicker": "Arbeitsablauf 1 von 5 | Szenariokonfiguration",
        "dispatch.title": "Lieferszenario konfigurieren und lösen",
        "dispatch.subtitle": (
            "Wählen Sie ein Szenario, prüfen Sie die Kapazitätsbedingungen und erzeugen Sie "
            "eine Nächster-Nachbar-Referenzlösung oder eine optimierte OR-Tools-Lösung."
        ),
        "dispatch.pick": "Datensatz wählen",
        "dispatch.pick.cap": (
            "Das Wien-Szenario dient als betriebliche Demonstration. Das Fallbeispiel zeigt "
            "die Grenzen eines gierigen Konstruktionsverfahrens."
        ),
        "dispatch.pick.help": (
            "Eingebaute Datensätze sind immer da. Erzeugte (GEN_…) gelten nur, solange der Optimierungsdienst läuft."
        ),
        "dispatch.solve": "Tourenlösungen erzeugen",
        "dispatch.solve.cap": (
            "Verwenden Sie die Referenzlösung als transparenten Vergleich und führen Sie "
            "anschließend OR-Tools aus."
        ),
        "dispatch.settings": "Optimierungseinstellungen",
        "dispatch.need_load": "Dieser Datensatz ist gewählt, aber noch nicht geladen. Zuerst „Datensatz laden“ klicken.",
        "dispatch.time": "OR-Tools-Suchzeit",
        "dispatch.time.help": (
            "Wie lange Google OR-Tools suchen darf: 1, 5 oder 10 Sekunden. "
            "5 Sekunden ist die übliche Demo. Länger kann kürzere Touren finden. "
            "Das Ergebnis bleibt „beste gefundene Lösung in dieser Zeit“, kein Beweis für die kürzestmögliche Tour."
        ),
        "dispatch.load": "Szenario laden",
        "dispatch.load.help": "Kunden, Fahrzeuggrößen, Distanzen und die drei Kapazitätsprüfungen holen.",
        "dispatch.validate": "Vorprüfungen wiederholen",
        "dispatch.validate.help": (
            "Die drei Kapazitätsfragen wiederholen. Die dritte ist nur ein Hinweis und blockiert nie."
        ),
        "dispatch.baseline": "Referenzlösung erzeugen",
        "dispatch.baseline.help": (
            "Gieriger Nächster-Nachbar: immer den nächsten Auftrag, der noch passt. "
            "Im 6-Kunden-Beispiel bleibt erwartungsgemäß jemand übrig."
        ),
        "dispatch.optimise": "Optimierte Lösung erzeugen",
        "dispatch.optimise.help": (
            "Sucht bis zur gewählten Zeit nach einem kürzeren vollständigen Plan. "
            "Die Seite wartet, bis die Suche endet."
        ),
        "dispatch.loaded": "{id} geladen.",
        "dispatch.demand": "Aufträge und Laderaum",
        "dispatch.demand.cap": (
            "Ein Tote ist eine standardisierte Lieferbox. Aufträge und Fahrzeugkapazität nutzen dieselbe Einheit."
        ),
        "dispatch.m.customers": "Kunden",
        "dispatch.m.customers.help": "Ein vollständiger Plan besucht jeden Kunden genau einmal.",
        "dispatch.m.demand": "Gesamtbedarf",
        "dispatch.m.demand.help": (
            "Wie viele Totes (Standardboxen) das Depot verlassen müssen. "
            "Die Totes eines Kunden fahren alle auf demselben Fahrzeug."
        ),
        "dispatch.m.fleet": "Flotte",
        "dispatch.m.fleet.help": "Identische Fahrzeuge. Eines darf ungenutzt bleiben.",
        "dispatch.m.capacity": "Flottenkapazität",
        "dispatch.m.capacity.help": "Übersteigen die Totes diesen Wert, stoppt die Planung vor dem Optimierer.",
        "dispatch.m.minvans": "Fahrzeuge, falls Boxen teilbar wären",
        "dispatch.m.minvans.help": (
            "Dies ist nur eine Untergrenze. Ganze Aufträge können zusätzliche Fahrzeuge erfordern."
        ),
        "dispatch.m.ratio": "Auslastung bei perfektem Packen",
        "dispatch.m.ratio.help": (
            "Totes insgesamt ÷ Flotten-Totes. Notwendig, aber nicht hinreichend, weil Aufträge ganz bleiben."
        ),
        "dispatch.m.source": "Wie Distanz geschätzt wird",
        "dispatch.m.source.help": (
            "Wien nutzt eine Kartenformel mit Umwegfaktor, keine Live-GPS-Daten. "
            "Das Fallbeispiel nutzt eine veröffentlichte feste Distanztafel."
        ),
        "dispatch.checks": "Machbarkeits-Vorprüfungen",
        "dispatch.checks.cap": (
            "Die ersten zwei Fragen können die Planung stoppen. Die dritte ist nur ein Hinweis."
        ),
        "dispatch.checks.note": (
            "Diese Prüfungen fragen nur, ob jeder Auftrag auf ein Fahrzeug passt und ob die Flotte "
            "genug Boxen insgesamt hat. Sie beweisen **nicht**, dass sich ganze Aufträge auf Fahrzeuge "
            "gruppieren lassen. Scheitert die Zuordnung später, meldet die Anwendung, dass keine "
            "vollständige Lösung zurückgegeben wurde. Sie behauptet nicht, dass das Problem unzulässig ist."
        ),
        "check.col.check": "Prüfung",
        "check.col.name": "In Klartext",
        "check.col.result": "Ergebnis",
        "check.col.stops": "Kann Planung stoppen?",
        "check.col.detail": "Detail",
        "check.ok": "OK",
        "check.fail": "Nicht bestanden",
        "check.stops_yes": "Ja",
        "check.stops_no": "Nein, nur Hinweis",
        "check.CHECK_1": "Jeder Auftrag passt auf ein Fahrzeug",
        "check.CHECK_2": "Die Flotte hat genug Platz insgesamt",
        "check.CHECK_3": "Mindestzahl Fahrzeuge, falls Boxen teilbar wären",
        "check.CHECK_4": "Die Datei sieht vollständig aus",
        "dispatch.orders": "Kundenaufträge",
        "dispatch.map": "Kundenorte (synthetisch)",
        "dispatch.map.cap": "Markierungsgröße folgt dem Tote-Bedarf. OpenStreetMap ist nur Hintergrund.",
        "dispatch.matrix": "Distanztafel",
        "dispatch.matrix.cap": "Das 6-Kunden-Beispiel hat keine Stadtkarte. Distanzen stehen in einer Tabelle.",
        "dispatch.nogeo": "Dieser Datensatz hat keine Kartenkoordinaten. Distanzen stehen als Tabelle.",
        "dispatch.matrix.full": "Vollständige Distanztafel (km, drei Nachkommastellen)",
        "dispatch.matrix.full.cap": "Intern ganze Meter, angezeigt als Kilometer. Die Tafel ist symmetrisch.",
        "dispatch.runs": "Pläne in dieser Sitzung",
        "dispatch.runs.cap": "Nach einem Lauf: Touren ansehen öffnen.",
        "dispatch.simple": "Nächster-Nachbar-Referenzlösung",
        "dispatch.or": "OR-Tools-Lösung",
        "dispatch.norun": "Für diesen Datensatz noch nicht gerechnet.",
        "dispatch.total": "Gesamtdistanz: {km}",
        "dispatch.partial": "Teildistanz (kein vollständiger Plan): {km}",
        "dispatch.not_optimal": (
            "Beste zulässige Lösung innerhalb der Suchzeit. Globale Optimalität wird nicht behauptet."
        ),
        "dispatch.next.routes": "Touren ansehen",
        "dispatch.next.compare": "Die zwei Pläne vergleichen",
        "dispatch.gen": "Weiteren synthetischen Stadtdatensatz erzeugen",
        "dispatch.gen.cap": (
            "Nur in diesem laufenden Optimierungsdienst gespeichert. Distanzen bleiben Schätzungen, keine Live-Straßen."
        ),
        "scenario.VIENNA_STANDARD_24.label": "Wien, 24 Aufträge (empfohlen)",
        "scenario.VIENNA_STANDARD_24.help": (
            "24 synthetische Kunden um Wien, 108 Totes, vier Fahrzeuge à 30 Totes. "
            "Zone Z1 braucht 35 Totes, ein Fahrzeug schafft kein ganzes Viertel."
        ),
        "scenario.LEARNING_6.label": "Fallbeispiel (6 Kunden)",
        "scenario.LEARNING_6.help": (
            "Kompaktes Fallbeispiel (id LEARNING_6): 20 Totes auf zwei Fahrzeugen mit Kapazität 10. "
            "Der gierige Plan lässt Kunde C4 aus. Der Optimierer sollte 31,000 km liefern. "
            "Dieses Szenario nutzt eine feste Distanztafel statt Stadtkoordinaten."
        ),
        "scenario.INFEASIBLE_SINGLE_OVERSIZE.label": "Vorprüfungsfall: Auftrag über Fahrzeugkapazität",
        "scenario.INFEASIBLE_SINGLE_OVERSIZE.help": (
            "Ein ganzer Auftrag passt auf kein Fahrzeug. Planung stoppt, Optimierer startet nicht."
        ),
        "scenario.INFEASIBLE_FLEET_OVERFLOW.label": "Vorprüfungsfall: Bedarf über Flottenkapazität",
        "scenario.INFEASIBLE_FLEET_OVERFLOW.help": (
            "Die Totes insgesamt übersteigen den Laderaum. Planung stoppt, Optimierer startet nicht."
        ),
        "scenario.INFEASIBLE_BIN_PACKING.label": "Genug Platz, aber Aufträge lassen sich nicht gruppieren",
        "scenario.INFEASIBLE_BIN_PACKING.help": (
            "Jeder Auftrag passt, und der Gesamtraum reicht, aber ganze Aufträge lassen sich nicht "
            "auf Fahrzeuge verteilen. Meldung: „kein vollständiger Plan gefunden“, nicht „unmöglich“."
        ),
        "scenario.generated.help": (
            "Erzeugte synthetische Stadt. Nur in diesem Dienstprozess. Distanzen sind Schätzungen."
        ),
        "scenario.fallback.help": "Eingebauter oder erzeugter Lieferdatensatz.",
        "tote.help": "Tote: eine standardisierte Lieferbox. Bedarf und Laderaum werden in Totes gezählt.",
        "tote.word": "Totes",
        "routes.kicker": "Arbeitsablauf 2 von 5 | Betriebliche Prüfung",
        "routes.title": "Fahrzeugtouren und Kapazitätsauslastung prüfen",
        "routes.subtitle": (
            "Prüfen Sie Stoppreihenfolge, zugeordneten Bedarf, Tourdistanz und "
            "Kapazitätsauslastung jedes Fahrzeugs in der ausgewählten Lösung."
        ),
        "routes.pick": "Welcher Plan?",
        "routes.pick.help": "Wechsel lädt nur gespeicherte Ergebnisse. Der Optimierer läuft nicht erneut.",
        "routes.opt": "Optimierte Lösung",
        "routes.base": "Nächster-Nachbar-Referenzlösung",
        "routes.empty.title": "Noch kein Plan",
        "routes.empty.body": "Rechnen Sie unter Touren planen den einfachen Plan oder den Optimierer, dann kommen Sie zurück.",
        "routes.kpis": "Auf einen Blick",
        "routes.kpis.cap": "Vom Optimierungsdienst übernommen. Diese Seite rechnet sie nicht neu.",
        "compare.kicker": "Arbeitsablauf 3 von 5 | Leistungsvergleich",
        "compare.title": "Referenzlösung und optimierte Lösung vergleichen",
        "compare.subtitle": (
            "Jede Zahl kommt vom Optimierungsdienst. Diese Seite rechnet Distanz und Verbesserung nicht selbst."
        ),
        "compare.empty.title": "Beide Pläne nötig",
        "compare.empty.body": "Zuerst einfachen Plan und Optimierer auf demselben Datensatz rechnen.",
        "compare.nn": "Nächster-Nachbar-Referenzlösung",
        "compare.nn.cap": "Deterministische gierige Konstruktion als transparente Referenz.",
        "compare.or": "OR-Tools-Lösung",
        "compare.or.cap": "Beste zulässige Lösung innerhalb der gewählten Suchzeit.",
        "compare.need_both": (
            "Eine Distanzverbesserung erscheint nur, wenn beide Pläne alle Kunden bedienen. "
            "Ein unvollständiger gieriger Plan bekommt keine erfundene Gesamtdistanz."
        ),
        "inspect.kicker": "Arbeitsablauf 4 von 5 | Modellvalidierung",
        "inspect.title": "Tourrekonstruktion und Nebenbedingungen validieren",
        "inspect.subtitle": (
            "Rekonstruieren Sie Zuordnungen, gewählte Kanten und kumulierte Lasten aus den "
            "Stoppreihenfolgen und gleichen Sie diese mit den dokumentierten Nebenbedingungen ab."
        ),
        "inspect.empty.title": "Noch nichts zu prüfen",
        "inspect.empty.body": "Zuerst unter Touren planen einen Plan rechnen.",
        "learn.kicker": "Arbeitsablauf 5 von 5 | CVRP-Fallbeispiel",
        "learn.title": "Lokale Entscheidungen und globale Lösungsqualität",
        "learn.subtitle": (
            "Ein Fall mit sechs Kunden zeigt, warum eine lokal sinnvolle Tourenentscheidung eine "
            "vollständige Zuordnung verhindern kann und warum Zulässigkeit und minimale Distanz "
            "getrennte Fragen sind."
        ),
        "learn.callout": (
            "**Drei Ergebnisse verwenden dieselben Aufträge und dieselbe Distanzmatrix.** Die "
            "deterministische Nächster-Nachbar-Referenz konstruiert 27,000 km an Touren, lässt aber "
            "Kunde C4 unbedient. Ein benannter Referenzplan bedient alle Kunden in 34,000 km. "
            "OR-Tools liefert einen 31,000-km-Plan; vollständige Enumeration bestätigt unabhängig "
            "dessen Optimalität."
        ),
        "learn.backend": "Wie die Ergebnisse erzeugt werden",
        "learn.backend.body": (
            "**Eingabe.** Das FastAPI-Backend lädt sechs ungeteilte Kundenaufträge, zwei Fahrzeuge "
            "mit je 10 Totes Kapazität und eine feste symmetrische Distanzmatrix.\n\n"
            "**Referenzverfahren.** Fahrzeuge werden nach ID geöffnet. An jedem Stopp wählt der "
            "Algorithmus den nächsten unbedienten Kunden, dessen vollständiger Auftrag noch passt. "
            "Distanzgleichstände werden nach Kunden-ID aufgelöst.\n\n"
            "**Optimierung.** Google OR-Tools sucht eine vollständige CVRP-Lösung mit minimaler "
            "Distanz. Für diesen kleinen Fall bewertet ein separater vollständiger Test alle 72 "
            "zulässigen Kombinationen aus Aufteilung und Stoppfolge und bestätigt das 31-km-Minimum.\n\n"
            "**Referenzplan.** Der 34-km-Plan ist ein fester zulässiger Vergleich, der aus derselben "
            "Backend-Matrix berechnet wird. Er ist weder das gierige Ergebnis noch ein Optimierungslauf."
        ),
        "learn.load": "Dieses Szenario als aktiv setzen",
        "learn.load.help": (
            "Übernimmt das Sechs-Kunden-Szenario in Tourenplan, Lösungsvergleich und Modellvalidierung."
        ),
        "learn.loaded": "Die anderen Seiten nutzen jetzt das Sechs-Kunden-Fallbeispiel.",
        "export.title": "Diesen Plan herunterladen",
        "export.cap": "Dateien enthalten Datensatz- und Lauf-id. Werte kommen vom Optimierungsdienst.",
        "export.json": "JSON herunterladen",
        "export.csv": "CSV-Zip herunterladen",
        "van.label": "Fahrzeug",
        "van.unused": "Ungenutzt",
        "van.route": "Tour",
        "van.orders": "Lieferstopps",
        "van.load": "Zugeordneter Bedarf",
        "van.util": "Kapazitätsauslastung",
        "van.util.short": "ausgelastet",
        "van.distance": "Distanz",
        "van.load.hint": (
            "Der zugeordnete Bedarf ist die Gesamtzahl der Totes auf diesem Fahrzeug."
        ),
        "van.idle": "Dieses Fahrzeug wurde nicht genutzt. Ungenutzte Fahrzeuge sind zulässig.",
        "van.capacity": "Kapazität",
        "van.util.hint": (
            "Der Balken zeigt die Kapazitätsauslastung: zugeordneter Bedarf geteilt durch Fahrzeugkapazität."
        ),
        "note.learning": (
            "Das ist das erwartete gierige Ergebnis im 6-Kunden-Beispiel, kein App-Fehler. "
            "Ausgelassen: {unserved}. Die Gesamtdistanz bleibt leer; die Kilometer sind nur eine "
            "Teilkonstruktion, nicht die 34-km-Packung. Optimierer für den vollständigen 31-km-Plan "
            "starten oder auf dieser Beispielseite bleiben."
        ),
        "note.incomplete": (
            "Das gierige Verfahren hat Touren gebaut, aber nicht alle Kunden bedient. "
            "Das ist kein fairer Vergleichswert.{unserved}"
        ),
        "note.unserved": " Ausgelassen: {ids}.",
        "summary.ineligible": (
            "Die Referenzlösung bedient nicht alle Kunden ({status}); daher wird keine "
            "Verbesserung ausgewiesen."
        ),
        "summary.unserved": "Ausgelassene Kunden: {ids}.",
        "summary.partial": "Konstruierte gierige Distanz {km} nur als Teilplan.",
        "summary.opt_ok": "Die Optimierung lieferte eine vollständige Lösung über {km}.",
        "summary.opt_bad": "Optimierer-Status: {status}.",
        "summary.opt_incomplete": (
            "Die Referenzlösung ist mit {km} vollständig; die optimierte Lösung ist nicht "
            "vergleichbar ({status})."
        ),
        "summary.ok": (
            "Die Referenzlösung umfasst {base_km} mit {base_vans} Fahrzeugen. "
            "Die optimierte Lösung umfasst {opt_km} mit {opt_vans} Fahrzeugen. "
            "Distanzverbesserung: {improve}."
        ),
        "common.yes": "Ja",
        "common.no": "Nein",
        "common.na": "k. A.",
        "unit.totes": "{n} Totes",
        "unit.fleet": "{vans} × {cap} Totes",
        "dist.fixed_matrix": "Veröffentlichte Tabelle",
        "dist.haversine_detour": "Kartenschätzung + Umweg",
        "check.msg.integrity_ok": "Der Datensatz sieht vollständig aus.",
        "check.msg.demand_ok": "Der größte Auftrag passt noch auf ein Fahrzeug.",
        "check.msg.demand_fail": "Mindestens ein Auftrag ist größer als ein Fahrzeug.",
        "check.msg.fleet_ok": "Die Boxen insgesamt passen in die Flotte.",
        "check.msg.fleet_fail": "Die Boxen insgesamt übersteigen den Laderaum.",
        "check.msg.minvans": (
            "Wären Totes teilbar, bräuchten Sie mindestens {n} Fahrzeuge. "
            "Das ist nur eine Untergrenze. Ganze Aufträge können mehr Fahrzeuge erfordern."
        ),
        "check.num": "{n}",
        "dispatch.time.1": "1 Sekunde (kurze Suche)",
        "dispatch.time.5": "5 Sekunden (empfohlen)",
        "dispatch.time.10": "10 Sekunden (erweiterte Suche)",
        "dispatch.run": "Lauf `{id}`",
        "dispatch.term": "Suche beendet: `{term}`",
        "dispatch.last_validate": "Letzte Kapazitätsprüfung (technisch)",
        "dispatch.col.customer": "Kunde",
        "dispatch.col.zone": "Zone",
        "dispatch.col.demand": "Bedarf (Totes)",
        "dispatch.col.lat": "Breite",
        "dispatch.col.lon": "Länge",
        "dispatch.gen.seed": "Zufallsstartwert",
        "dispatch.gen.seed.help": "Gleicher Startwert und gleiche Einstellungen erzeugen dieselbe synthetische Stadt.",
        "dispatch.gen.customers": "Kunden",
        "dispatch.gen.vans": "Fahrzeuge",
        "dispatch.gen.capacity": "Fahrzeugkapazität (Totes)",
        "dispatch.gen.capacity.help": (
            "Jedes Fahrzeug hat so viele Tote-Plätze. Ein Tote ist eine standardisierte Lieferbox."
        ),
        "dispatch.gen.detour": "Umwegfaktor",
        "dispatch.gen.detour.help": (
            "Streckt Luftlinie etwas, damit Distanzen eher wie Stadtverkehr wirken. Übliche Demo: 1,25."
        ),
        "dispatch.gen.z1": "Innenstadt-Anteil (Z1)",
        "dispatch.gen.z2": "Innenring-Anteil (Z2)",
        "dispatch.gen.z3": "Außenring-Anteil (Z3)",
        "dispatch.gen.z4": "Äußerer Anteil (Z4)",
        "dispatch.gen.zone.help": "Wie viele Kunden in diesem Band landen. Die vier Anteile sollten etwa 1 ergeben.",
        "dispatch.gen.button": "Datensatz erzeugen",
        "dispatch.gen.button.help": "Der Planungsdienst behält dieses Szenario bis zum Neustart.",
        "dispatch.gen.ok": "`{id}` erzeugt.",
        "routes.mismatch": (
            "Diese Lösung gehört zu einem anderen Szenario. Laden und lösen Sie das aktuelle Szenario erneut."
        ),
        "routes.m.served": "Bediente Kunden",
        "routes.m.served.help": "Ein vollständiger Plan besucht jeden Kunden genau einmal.",
        "routes.m.demand": "Bedienter Bedarf",
        "routes.m.demand.help": "Totes (Standardboxen) auf den konstruierten Touren.",
        "routes.m.vans": "Genutzte Fahrzeuge",
        "routes.m.vans.help": "Ein Fahrzeug zählt als genutzt, wenn es mindestens einen Kunden anfährt.",
        "routes.m.total": "Gesamtdistanz",
        "routes.m.total.help": "Summe der genutzten Touren, inklusive Rückfahrt zum Depot.",
        "routes.m.partial": "Teildistanz",
        "routes.m.partial.help": (
            "Distanz der gebauten Touren. Kein vollständiger Plan, daher kein fairer Vergleich."
        ),
        "routes.unserved": "Ausgelassen: {ids}",
        "routes.map": "Schematische Karte",
        "routes.map.cap": "Stadtkarte als Hintergrund. Linien sind Geraden, keine Fahranweisungen.",
        "routes.diagram": "Schematische Darstellung",
        "routes.diagram.cap": (
            "Punkte sind so angeordnet, dass das Beispiel lesbar ist. Distanzen kommen aus der Distanzmatrix."
        ),
        "routes.nogeo.l6": (
            "Das 6-Kunden-Beispiel hat keine Stadtkarte. Touren erscheinen als Diagramm und als Tabellen."
        ),
        "routes.nogeo": "Dieser Datensatz hat keine Kartenkoordinaten. Touren stehen nur als Tabellen.",
        "routes.seq": "Stopplisten",
        "routes.cards": "Fahrzeugübersicht",
        "routes.cards.cap": "Farben entsprechen der Karte. Ungenutzte Fahrzeuge sind zulässig.",
        "routes.unused": "Ungenutzte Fahrzeuge",
        "table.vehicle": "Fahrzeug",
        "table.used": "Genutzt",
        "table.sequence": "Stopps",
        "table.orders": "Aufträge",
        "table.load": "Zugeordneter Bedarf (Totes)",
        "table.distance": "Distanz",
        "table.pack": "Aufträge auf diesem Fahrzeug",
        "compare.mismatch": (
            "Die zwei Lösungen gehören zu unterschiedlichen Szenarien. Laden Sie ein Szenario "
            "und erzeugen Sie beide Methoden."
        ),
        "compare.reading": "Was die Zahlen bedeuten",
        "compare.table": "Zahlen nebeneinander",
        "compare.improve.cap": (
            "Eine Verbesserung erscheint nur, wenn beide Pläne alle Kunden bedienen: wie viel kürzer "
            "die optimierte Lösung gegenüber der Referenzlösung ist. Der Planungsdienst berechnet dies."
        ),
        "compare.chart.skip": (
            "Das Distanzdiagramm fehlt, weil die Referenzlösung nicht alle Kunden bedient."
        ),
        "compare.chart.distance": "Gesamtdistanz",
        "compare.chart.load": "Boxen je Fahrzeug (Totes)",
        "compare.chart.route": "Distanz je Fahrzeug (km)",
        "compare.warn.incomplete": (
            "Die Referenzlösung hat Kunden ausgelassen. Das Optimierungsergebnis wird dennoch "
            "angezeigt; die Referenzdistanz ist keine vollständige Lösung."
        ),
        "compare.next": "Nachvollziehen, wie der Plan rekonstruiert wurde",
        "compare.kpi.status": "Status",
        "compare.kpi.eligible": "Fair vergleichbar?",
        "compare.kpi.served": "Bediente Kunden",
        "compare.kpi.demand": "Bedienter Bedarf (Totes)",
        "compare.kpi.vans": "Genutzte Fahrzeuge",
        "compare.kpi.total": "Gesamtdistanz",
        "compare.kpi.partial": "Teildistanz",
        "compare.kpi.util": "Auslastung der genutzten Fahrzeuge",
        "compare.kpi.improve": "Distanzverbesserung",
        "compare.col.kpi": "Kennzahl",
        "inspect.pick": "Welcher Plan?",
        "inspect.pick.help": (
            "Tabellen entstehen aus der Stopliste. Sie sehen keine versteckten Optimierer-Interna."
        ),
        "inspect.how": (
            "Ein Kunde auf einem Fahrzeug ist eine Zuordnung. Aufeinanderfolgende Stopps werden "
            "zu einer gewählten Fahrt. Ein Fahrzeug ist genutzt, wenn es mindestens einen Kunden "
            "bedient. Der kumulierte Wert erfasst bedienten Bedarf, nicht verbleibende Fahrzeuglast."
        ),
        "inspect.solver": "Wie der Optimierer suchen sollte",
        "inspect.solver.cap": (
            "Suchkonfiguration, getrennt von den Entscheidungsvariablen des Modells."
        ),
        "inspect.solver.strategy": "Start mit einer günstigen Erste-Tour, dann lokale Verbesserung.",
        "inspect.solver.time": "Angeforderte Suchzeit: {n} s",
        "inspect.solver.term": "Suche beendet: `{term}`",
        "inspect.solver.runtime": "Laufzeit der Suche: {n} s",
        "inspect.demand": "Hat jeder Kunde seine Boxen erhalten?",
        "inspect.demand.cap": "Eine Zeile je Kunde. Ein vollständiger Plan besucht jeden Kunden einmal.",
        "inspect.constraints": "Unabhängige Prüfungen der rekonstruierten Touren",
        "inspect.constraints.cap": "Diese Prüfungen sehen die zurückgegebenen Touren, nicht verborgenen Solver-Speicher.",
        "inspect.loads": "Kumuliert bedienter Bedarf je Stopp",
        "inspect.loads.cap": (
            "Kumuliert bedienter Bedarf nach jedem Stopp. Dies ist nicht die verbleibende Fahrzeuglast."
        ),
        "inspect.cum.sequence": "Reihenfolge",
        "inspect.cum.node": "Knoten",
        "inspect.cum.demand": "Stoppbedarf (Totes)",
        "inspect.cum.served": "Kumuliert bedienter Bedarf (Totes)",
        "inspect.arcs": "Gewählte Fahrten zwischen Stopps",
        "inspect.arcs.cap": (
            "Ausgang zählt, wie viele gewählte Fahrten einen Stopp verlassen. Eingang zählt Ankünfte."
        ),
        "inspect.arcs.list": "Gewählte Fahrten",
        "inspect.matrix.van": "Fahrtabelle für {id}",
        "inspect.matrix.all": "Vollständige Fahrtabellen",
        "inspect.dist": "Distanztafel",
        "inspect.dist.cap": "Intern Meter, angezeigt als Kilometer mit drei Nachkommastellen.",
        "inspect.dist.full": "Vollständige Distanztafel",
        "inspect.dist.compact": "Distanzen der gewählten Fahrten",
        "inspect.depot": "Gespeicherte Depot-id `{id}` wird als {label} angezeigt.",
        "inspect.obj": "Vom Planungsdienst zurückgegebene Lösungsdistanz: {km}",
        "inspect.next": "6-Kunden-Beispiel öffnen",
        "inspect.col.customer": "Kunde",
        "inspect.col.required": "Bedarf (Totes)",
        "inspect.col.delivered": "Geliefert",
        "inspect.col.vehicle": "Fahrzeug",
        "inspect.col.visits": "Besuche",
        "inspect.col.check": "Prüfung",
        "inspect.col.from": "Von",
        "inspect.col.to": "Nach",
        "inspect.col.selected": "Gewählte Fahrt",
        "inspect.col.leg": "Schenkeldistanz",
        "learn.inputs": "Eingabedaten des Beispiels",
        "learn.inputs.cap": (
            "Sechs ungeteilte Aufträge müssen zwei Fahrzeugen mit gleicher Kapazität zugeordnet werden."
        ),
        "learn.input.demand": "Gesamtbedarf",
        "learn.input.capacity": "Flottenkapazität",
        "learn.input.rule": "Auftragsregel",
        "learn.input.rule.value": "Ungeteilt",
        "learn.matrix": "Distanzmatrix",
        "learn.matrix.cap": (
            "Jede Zelle ist die Fahrdistanz vom Ort ihrer Zeile zum Ort ihrer Spalte. "
            "Die Matrix ist symmetrisch und enthält feste synthetische Werte."
        ),
        "learn.matrix.hover": "Distanzen werden in Kilometern mit drei Nachkommastellen angezeigt.",
        "learn.matrix.c1": "Lesebeispiel: Depot nach C1 beträgt {km}.",
        "learn.demand": "Kundenbedarf",
        "learn.demand.cap": (
            "Die 20 Totes entsprechen genau der Flottenkapazität. In einem vollständigen Plan "
            "müssen daher beide Fahrzeuge je 10 Totes laden."
        ),
        "learn.demand.body": (
            "Aufträge bleiben ganz, die Kunden eines Fahrzeugs müssen also genau 10 Totes ergeben. "
            "Das Nächster-Nachbar-Verfahren kann trotzdem unvollständig bleiben, obwohl die "
            "ersten zwei Kapazitätsprüfungen bestanden werden."
        ),
        "learn.actions": "Backend-Methoden ausführen",
        "learn.actions.cap": (
            "Führen Sie zuerst die deterministische Referenz aus, um ihre Grenze zu reproduzieren, "
            "und danach OR-Tools für einen vollständigen optimierten Plan."
        ),
        "learn.run.base": "Nächster-Nachbar-Referenz ausführen",
        "learn.run.base.help": (
            "Gieriges Nächster-Nachbar-Verfahren: vom aktuellen Stopp wird der nächste unbediente "
            "Kunde gewählt, dessen ganzer Auftrag noch passt. Frühere Entscheidungen werden nicht "
            "revidiert. Erwartet: 27,000 km Teilrouten, Kunde C4 (5 Totes) unbedient."
        ),
        "learn.greedy.what": (
            "Gierig bedeutet hier eine lokale Regel: an jedem Stopp nimmt der Algorithmus den "
            "nächsten verbliebenen Kunden, der noch passt. Er plant nicht voraus. Ein günstiger "
            "früher Stopp kann später einen Auftrag ohne Restkapazität lassen."
        ),
        "learn.run.opt": "OR-Tools-Optimierer ausführen",
        "learn.run.opt.help": (
            "Fünf Sekunden Suche nach einem vollständigen kapazitätszulässigen Plan. Erwartet "
            "wird das unabhängig bestätigte Optimum von 31,000 km."
        ),
        "learn.nn": "1. Nächster-Nachbar-Referenz (unvollständig)",
        "learn.nn.cap": (
            "Ein deterministisches Konstruktionsverfahren als transparente Referenz, nicht als "
            "garantiert vollständige Lösung."
        ),
        "learn.nn.need": "Erzeugen Sie oben die Referenzlösung, um das Dienstergebnis zu laden.",
        "learn.nn.body": (
            "Fahrzeug V01 wählt C1, C2 und C3 und lädt 9 Totes. Fahrzeug V02 wählt danach C6 "
            "und C5 und lädt 6 Totes. Kunde C4 benötigt 5 Totes und passt nun in kein Fahrzeug. "
            "Die 27 km messen daher nur die konstruierten Touren und keine vollständige Lösung."
        ),
        "learn.nn.steps": (
            "**V01 startet im Depot mit 10 Tote-Plätzen.** C1 und C6 liegen beide 3,000 km "
            "entfernt. Der Algorithmus löst den Gleichstand über die Kunden-ID und wählt C1 "
            "(4 Totes). Restkapazität: 6.\n\n"
            "**Von C1 ist C2 der nächste zulässige Kunde** (2,000 km, 2 Totes). Restkapazität: 4.\n\n"
            "**Von C2 passt C4 nicht** (5 Totes). Der nächste noch passende Kunde ist C3 "
            "(3,000 km, 3 Totes). Restkapazität: 1. Kein verbliebener Auftrag ist 1 Tote oder "
            "kleiner, daher kehrt V01 zum Depot zurück. Tourdistanz: 16,000 km.\n\n"
            "**V02 startet im Depot mit 10 Tote-Plätzen.** Es wählt C6 (4 Totes) und danach C5 "
            "(2 Totes). Restkapazität: 4. C4 braucht weiter 5 Totes, daher kehrt auch V02 ohne "
            "C4 zurück. Tourdistanz: 11,000 km.\n\n"
            "**Vom Backend gespeichertes Ergebnis.** Fünf Kunden sind bedient. Die konstruierte "
            "Distanz beträgt 27,000 km. Weil C4 unbedient bleibt, ist der Status eine "
            "unvollständige Referenz. Diese Distanz darf nicht mit 34 km oder 31 km wie eine "
            "vollständige Lösung verglichen werden."
        ),
        "learn.served": "Bediente Kunden: {served} / {total}",
        "learn.unserved": "Ausgelassen: {ids}",
        "learn.partial": "Konstruierte Teildistanz: {km}",
        "learn.objective": "Distanz der vollständigen Lösung: k. A.",
        "learn.served.label": "Bediente Kunden",
        "learn.unserved.label": "Unbedienter Kunde",
        "learn.partial.label": "Teildistanz",
        "learn.complete.label": "Distanz des vollständigen Plans",
        "learn.arcs.nn": "Gewählte Fahrten aus aufeinanderfolgenden gierigen Stopps",
        "learn.arcs.help": (
            "Ausgang ist, wie viele gewählte Fahrten einen Stopp verlassen; Eingang, wie viele ankommen. "
            "Diese Zählungen entstehen aus der Stopliste."
        ),
        "learn.details": "Details der Tourrekonstruktion anzeigen",
        "learn.pack": "2. Zulässiger Referenzplan (34 km)",
        "learn.pack.cap": (
            "Ein fester Vergleichsplan, der die Existenz einer vollständigen Zuordnung belegt. "
            "Keine der beiden Backend-Methoden erzeugt ihn."
        ),
        "learn.pack.body": (
            "Fahrzeug V01 bedient C1, C2 und C6 in 14 km. Fahrzeug V02 bedient C5, C4 und C3 "
            "in 20 km. Beide laden genau 10 Totes, der kombinierte 34-km-Plan ist also zulässig. "
            "Er zeigt, dass die unvollständige Referenz eine Verfahrensgrenze und kein Beleg für "
            "Unzulässigkeit ist."
        ),
        "learn.pack.total": "Distanz des Referenzplans",
        "learn.opt": "3. Verifiziert optimaler Plan (31 km)",
        "learn.opt.cap": (
            "OR-Tools liefert diesen Plan; ein unabhängiger vollständiger Test bestätigt, dass "
            "für diese Sechs-Kunden-Matrix kein kürzerer vollständiger Plan existiert."
        ),
        "learn.opt.need": "Starten Sie oben den Optimierer, um das Ergebnis des Optimierungsdienstes zu laden.",
        "learn.opt.obj": "Distanz des vollständigen Plans: {km}",
        "learn.opt.body": (
            "Eine 13-km-Tour bedient C1, C5 und C6. Die andere 18-km-Tour bedient C2, C3 und C4. "
            "Beide Lasten betragen 10 Totes. Die vollständige Enumeration prüft die zwei zulässigen "
            "Kundenaufteilungen und jede Stoppfolge, insgesamt 72 Kombinationen, und findet 31 km "
            "als Minimum."
        ),
        "learn.arcs.opt": "Gewählte Fahrten aus aufeinanderfolgenden Optimierer-Stopps",
        "learn.why": "Warum der nächste zulässige Stopp scheitern kann",
        "learn.why.body": (
            "Das Backend scheitert hier nicht. Es wendet eine veröffentlichte lokale Regel an "
            "und meldet danach, dass die Konstruktion unvollständig ist.\n\n"
            "Von C2 ist C3 mit 3,000 km der nächste noch passende Kunde. Danach hat V01 nur "
            "noch 1 Tote-Platz, daher kann Kunde C4 (5 Totes) V01 nicht mehr erreichen. "
            "V02 hat später 4 Plätze frei, das reicht ebenfalls nicht für 5. Der einzige "
            "verbliebene 5-Tote-Auftrag bleibt unbedient.\n\n"
            "Ein vollständiger Plan existiert, wenn C3 dem anderen Fahrzeug vorbehalten bleibt. "
            "Deshalb können die 34-km-Referenzpackung und das 31-km-Optimum alle Kunden "
            "bedienen, die gierige Konstruktion aber nicht. Zulässigkeit der Daten und "
            "Vollständigkeit dieses Verfahrens sind unterschiedliche Fragen."
        ),
        "learn.edge": "Optionale Validierungsrandbedingung",
        "learn.edge.cap": (
            "Dies ist ein separates Szenario mit drei Kunden. Es gehört nicht zum "
            "Sechs-Kunden-Vergleich mit 27, 34 und 31 km."
        ),
        "learn.bin": "Wenn Gesamtkapazität allein nicht ausreicht",
        "learn.bin.cap": (
            "Genug Boxen insgesamt heißt nicht, dass jeder Auftrag ganz bleiben kann."
        ),
        "learn.bin.body": (
            "Dieser optionale Fall ist ein **anderer** Datensatz als das Sechs-Kunden-Beispiel. "
            "Er hat drei 6-Tote-Aufträge und zwei 10-Tote-Fahrzeuge.\n\n"
            "Jeder Auftrag passt auf ein Fahrzeug (6 ≤ 10), und der Gesamtbedarf passt in die "
            "Flotte (18 ≤ 20). Die ersten zwei Kapazitätsprüfungen bestehen daher. Ganze "
            "Aufträge lassen sich trotzdem nicht packen: 6 + 6 = 12 übersteigt 10, zwei "
            "Aufträge können also kein Fahrzeug teilen. Der dritte Auftrag hat danach kein "
            "Fahrzeug mehr.\n\n"
            "Das Backend ergänzt dafür keinen besonderen Unzulässigkeitsbeweis. Wenn Sie "
            "OR-Tools trotzdem starten, meldet der Dienst, dass kein vollständiger Plan "
            "gefunden wurde. Dieser Status ist kein Beweis, dass die Instanz unzulässig ist."
        ),
        "learn.bin.validate": "Kapazitätsprüfungen rechnen",
        "learn.bin.validate.help": "Die ersten zwei Prüfungen sollten passen. Die dritte ist nur ein Hinweis.",
        "learn.bin.optimise": "Trotzdem den Optimierer fragen",
        "learn.bin.optimise.help": (
            "Erwartet: „kein vollständiger Plan gefunden“. Das ist kein Beweis, dass es unmöglich ist."
        ),
        "learn.bin.caption": (
            "Wenn sich ganze Aufträge nicht gruppieren lassen, meldet die Suche, dass keine "
            "vollständige Lösung gefunden wurde. Das Szenario wird nicht als unzulässig bezeichnet."
        ),
        "packing.note": (
            "Dieser 34,000-km-Plan ist eine benannte Lehrreferenz. "
            "Er entsteht weder durch die gierige Schaltfläche noch durch den Optimierer. "
            "Schenkellängen stammen aus der Distanzmatrix des Optimierungsdienstes."
        ),
        "map.schematic": (
            "Gerade Verbindungen aus geschätzten Distanzen. Keine Straßengeometrie und keine Live-Navigation."
        ),
        "map.diagram": (
            "Nur eine schematische Darstellung. Distanzen stammen aus der Diensttabelle, "
            "nicht aus dieser Zeichnung. "
            "Das ist keine Karte."
        ),
    },
}


from workflow_copy import WORKFLOW_STRINGS  # noqa: E402

for _language, _copy in WORKFLOW_STRINGS.items():
    STRINGS[_language].update(_copy)


def current_language() -> str:
    lang = "en"
    try:
        import streamlit as st

        lang = st.session_state.get("ui_language", "en")
    except Exception:
        lang = "en"
    if lang not in STRINGS:
        return "en"
    return lang


def t(key: str, **kwargs: Any) -> str:
    lang = current_language()
    template = STRINGS[lang].get(key) or STRINGS["en"].get(key) or key
    if kwargs:
        return template.format(**kwargs)
    return template
