"""Paired English/German copy for the three-page planning journey."""

# Keeping each pair together makes reviews of new product copy straightforward.
COPY = {
    "ux.motion.pause": ("Pause animations", "Animationen pausieren"),
    "ux.export.prepare": ("Prepare JSON and CSV", "JSON und CSV vorbereiten"),
    "ux.preview.empty": (
        "Select a preset and generate the scenario to preview customer locations and fleet capacity.",
        "Wählen Sie ein Vorgabeszenario und erzeugen Sie es, um Kundenstandorte und Flottenkapazität "
        "anzuzeigen.",
    ),
    "ux.preview.empty.custom": (
        "Generate the scenario to preview customer locations and fleet capacity.",
        "Szenario generieren, um Kundenstandorte und Flottenkapazität anzuzeigen.",
    ),
    "ux.map.legend": (
        "Numbers show customer-stop order. Depot start and return are not numbered.",
        "Zahlen zeigen die Kundenstopp-Reihenfolge. Depotstart und -rückkehr sind nicht nummeriert.",
    ),
    "ux.over.diagram": (
        "Illustrative CVRP structure: multiple vehicle routes leave one depot, each "
        "customer is served exactly once, and every used vehicle returns to the depot.",
        "Illustrative CVRP-Struktur: mehrere Fahrzeugtouren verlassen ein Depot, jeder "
        "Kunde wird genau einmal bedient, und jedes genutzte Fahrzeug kehrt zum Depot zurück.",
    ),
    "check.audit.DEMAND_SATISFACTION": (
        "Every customer served exactly once",
        "Jeder Kunde genau einmal bedient",
    ),
    "check.audit.CAPACITY": ("Vehicle capacities respected", "Fahrzeugkapazitäten eingehalten"),
    "check.audit.DISTANCE": (
        "Route distances reconciled",
        "Tourdistanzen abgeglichen",
    ),
    "check.audit.DEPOT_CONNECTIVITY": (
        "Routes return to the depot",
        "Touren kehren zum Depot zurück",
    ),
    "check.audit.INVARIANTS": (
        "Solution consistency checks passed",
        "Konsistenzprüfungen der Lösung erfüllt",
    ),
    "nav.home": ("Overview", "Überblick"),
    "nav.dispatch": ("Scenarios", "Szenarien"),
    "nav.compare": ("Plan", "Plan"),
    "nav.method": ("Methodology", "Methodik"),
    "nav.inspect": ("Model validation", "Modellprüfung"),
    "nav.workflow": ("WORKFLOW", "ABLAUF"),
    "nav.secondary": ("MODEL & METHODS", "MODELL UND METHODEN"),
    "nav.language": ("LANGUAGE", "SPRACHE"),
    "brand.sub": ("CVRP route optimization", "CVRP-Tourenoptimierung"),
    "footer": (
        "© 2026 Syed Danish Ali · LastMile Lab",
        "© 2026 Syed Danish Ali · LastMile Lab",
    ),
    "lang.label": ("Language / Sprache", "Language / Sprache"),
    "ux.over.kicker": (
        "CAPACITATED VEHICLE ROUTING PROBLEM (CVRP)",
        "CAPACITATED VEHICLE ROUTING PROBLEM (CVRP)",
    ),
    "ux.over.title": (
        "Optimize fleet routing to minimize travel distance under capacity constraints",
        "Flottentouren unter Kapazitätsgrenzen optimieren, um die Fahrdistanz zu minimieren",
    ),
    "ux.over.intro": (
        "LastMile Lab models a static, single-depot Capacitated Vehicle Routing Problem "
        "(CVRP) for last-mile delivery. It determines how customer demand is assigned across "
        "vehicles and the sequence in which each route serves its customers.",
        "LastMile Lab modelliert ein statisches Capacitated Vehicle Routing Problem (CVRP) "
        "mit einem Depot für die Last-Mile-Zustellung. Es bestimmt, wie der Kundenbedarf auf "
        "Fahrzeuge verteilt wird und in welcher Reihenfolge jede Tour ihre Kunden bedient.",
    ),
    "ux.over.feas.hero": (
        "The objective is to minimize total estimated fleet distance while serving every "
        "customer exactly once, respecting vehicle-capacity constraints, and returning each "
        "active vehicle to the depot.",
        "Das Ziel ist, die geschätzte Gesamtdistanz der Flotte zu minimieren, jeden Kunden "
        "genau einmal zu bedienen, die Fahrzeugkapazität einzuhalten und jedes aktive "
        "Fahrzeug zum Depot zurückzuführen.",
    ),
    "ux.over.compare.body": (
        "The application compares a transparent nearest-neighbour baseline with an optimized "
        "route plan to show how routing decisions affect total fleet distance.",
        "Die Anwendung vergleicht eine transparente Nächster-Nachbar-Baseline mit einem "
        "optimierten Tourenplan, um zu zeigen, wie Tourenentscheidungen die Gesamtdistanz der "
        "Flotte beeinflussen.",
    ),
    "ux.over.about.kicker": (
        "ABOUT THIS PROJECT",
        "ÜBER DIESES PROJEKT",
    ),
    "ux.over.about.body": (
        "LastMile Lab is an independent portfolio project designed and developed by "
        "Syed Danish Ali. It applies capacitated vehicle routing concepts to a synthetic "
        "last-mile delivery case and brings together optimization, API-based planning, "
        "solution verification, and a bilingual interactive interface.",
        "LastMile Lab ist ein unabhängiges Portfolio-Projekt, entworfen und entwickelt "
        "von Syed Danish Ali. Es wendet Konzepte des Capacitated Vehicle Routing auf einen "
        "synthetischen Last-Mile-Zustellfall an und verbindet Optimierung, API-basierte "
        "Planung, Lösungsverifikation und eine zweisprachige interaktive Oberfläche.",
    ),
    "ux.over.vrp.title": ("Routing objective", "Tourenziel"),
    "ux.over.vrp": (
        "Minimize the total estimated distance travelled across all active vehicle routes "
        "while serving every customer.",
        "Die geschätzte Gesamtdistanz über alle aktiven Fahrzeugtouren minimieren und dabei "
        "jeden Kunden bedienen.",
    ),
    "ux.over.vrp.tip": (
        "The objective is to reduce combined fleet travel while satisfying the model's routing "
        "and capacity requirements.",
        "Das Ziel ist, die kombinierte Flottenfahrt zu reduzieren und dabei die Touren- und "
        "Kapazitätsanforderungen des Modells zu erfüllen.",
    ),
    "ux.over.cvrp.title": ("Capacity constraints", "Kapazitätsbedingungen"),
    "ux.over.cvrp": (
        "Each customer has an unsplit tote demand, and the total demand assigned to a vehicle "
        "cannot exceed its available capacity.",
        "Jeder Kunde hat einen ungeteilten Tote-Bedarf, und der einem Fahrzeug zugeordnete "
        "Gesamtbedarf darf dessen verfügbare Kapazität nicht überschreiten.",
    ),
    "ux.over.cvrp.tip": (
        "Each customer order remains on one vehicle, and the combined tote demand on that "
        "route must stay within vehicle capacity.",
        "Jeder Kundenauftrag bleibt auf einem Fahrzeug, und der kombinierte Tote-Bedarf dieser "
        "Tour muss innerhalb der Fahrzeugkapazität bleiben.",
    ),
    "ux.over.feas.title": ("Feasibility requirements", "Zulässigkeitsanforderungen"),
    "ux.over.feas": (
        "Every customer must be served exactly once, and every active vehicle route starts and "
        "returns to the depot.",
        "Jeder Kunde muss genau einmal bedient werden, und jede aktive Fahrzeugtour startet am "
        "Depot und kehrt dorthin zurück.",
    ),
    "ux.over.feas.tip": (
        "Depot: The common start and return location for all vehicle routes.",
        "Depot: Der gemeinsame Start- und Rückkehrort aller Fahrzeugtouren.",
    ),
    "ux.over.compare.title": ("Solution comparison", "Lösungsvergleich"),
    "ux.over.compare": (
        "Compare a deterministic nearest-neighbour baseline with an optimized route plan to "
        "evaluate the reduction in total fleet distance.",
        "Eine deterministische Nächster-Nachbar-Baseline mit einem optimierten Tourenplan "
        "vergleichen, um die Reduktion der Gesamtdistanz der Flotte zu bewerten.",
    ),
    "ux.over.compare.tip": (
        "The baseline provides a transparent reference point for assessing the improvement "
        "achieved by the optimized plan.",
        "Die Baseline liefert einen transparenten Referenzpunkt, um die Verbesserung durch den "
        "optimierten Plan zu bewerten.",
    ),
    "ux.over.proof.kicker": (
        "Vienna Standard 24 · Route comparison",
        "Wien Standard 24 · Tourenvergleich",
    ),
    "ux.over.proof.tech": (
        "This comparison shows a feasible optimized plan for Vienna Standard 24; global "
        "optimality is not claimed.",
        "Dieser Vergleich zeigt einen zulässigen optimierten Plan für Wien Standard 24; "
        "globale Optimalität wird nicht behauptet.",
    ),
    "ux.over.cta": ("Choose a scenario", "Szenario auswählen"),
    "ux.over.result": ("122.4 km → 97.2 km · 20.6% shorter", "122,4 km → 97,2 km · 20,6 % kürzer"),
    "ux.over.anim.baseline": ("Nearest-neighbour baseline", "Nächster-Nachbar-Baseline"),
    "ux.over.anim.optimized": ("Optimized solution", "Optimierte Lösung"),
    "ux.over.anim.km": ("122.4 km", "122,4 km"),
    "ux.over.anim.total": ("Total distance", "Gesamtdistanz"),
    "ux.over.anim.depot": ("Depot", "Depot"),
    "empty.open": ("Go to Scenarios", "Zu Szenarien"),
    "empty.plan.title": ("No route comparison yet", "Noch kein Tourenvergleich"),
    "ux.scenarios.title": ("Scenarios", "Szenarien"),
    "ux.scenarios.subtitle": (
        "Choose a preset scenario, review its demand and fleet configuration, then run a "
        "route comparison.",
        "Vorgabeszenario wählen, Bedarf und Flotte prüfen und anschließend einen Tourenvergleich starten.",
    ),
    "ux.source": ("Scenario Selection", "Szenarioauswahl"),
    "ux.presets": ("Scenario presets", "Szenariovorgaben"),
    "ux.custom": ("Custom scenario", "Eigenes Szenario"),
    "scenario.generated.label": ("Custom scenario", "Eigenes Szenario"),
    "ux.custom.intro": (
        "Build a delivery wave with your own customer, demand and fleet settings.",
        "Eine Lieferwelle mit eigenen Kunden-, Bedarfs- und Flotteneinstellungen erstellen.",
    ),
    "ux.custom.configure": ("Configure custom scenario", "Eigenes Szenario konfigurieren"),
    "ux.custom.back": ("Use a preset scenario", "Vorgabeszenario verwenden"),
    "ux.custom.fleet": ("Fleet setup", "Flotteneinrichtung"),
    "ux.custom.checks": ("Pre-run feasibility checks", "Zulässigkeitsprüfungen vor dem Lauf"),
    "ux.custom.reset": ("Reset to defaults", "Auf Standardwerte zurücksetzen"),
    "ux.custom.stale": ("Changes not yet generated", "Änderungen noch nicht generiert"),
    "scenario.VIENNA_STANDARD_24.label": ("Vienna Standard", "Wien Standard"),
    "scenario.VIENNA_STANDARD_24.meta": (
        "24 customers · 108 totes · 4 vehicles · 30 totes/vehicle",
        "24 Kunden · 108 Totes · 4 Fahrzeuge · 30 Totes/Fahrzeug",
    ),
    "scenario.VIENNA_STANDARD_24.help": (
        "Balanced-capacity scenario with 12 totes of spare fleet capacity.",
        "Szenario mit ausgewogener Kapazität und 12 Totes Reserve in der Flotte.",
    ),
    "scenario.VIENNA_TIGHT_24.label": ("Vienna Tight Capacity", "Wien Knappe Kapazität"),
    "scenario.VIENNA_TIGHT_24.meta": (
        "24 customers · 108 totes · 4 vehicles · 28 totes/vehicle",
        "24 Kunden · 108 Totes · 4 Fahrzeuge · 28 Totes/Fahrzeug",
    ),
    "scenario.VIENNA_TIGHT_24.help": (
        "Same demand and locations, with only 4 totes of spare fleet capacity.",
        "Gleicher Bedarf und gleiche Standorte, mit nur 4 Totes Reserve in der Flotte.",
    ),
    "scenario.VIENNA_WIDE_24.label": ("Vienna Wide Geography", "Wien Weite Wege"),
    "scenario.VIENNA_WIDE_24.meta": (
        "24 customers · 108 totes · 4 vehicles · 30 totes/vehicle",
        "24 Kunden · 108 Totes · 4 Fahrzeuge · 30 Totes/Fahrzeug",
    ),
    "scenario.VIENNA_WIDE_24.help": (
        "Same demand and fleet as Vienna Standard, with customer locations spread farther across Vienna.",
        "Gleicher Bedarf und gleiche Flotte wie Wien Standard, mit weiter über Wien verteilten Kundenstandorten.",
    ),
    "ux.custom.help": (
        "Set the fleet, then edit each order's tote demand. Locations are generated in the "
        "existing Vienna zones; no addresses or coordinates are needed.",
        "Flotte festlegen und den Tote-Bedarf jeder Bestellung bearbeiten. Standorte entstehen "
        "in den vorhandenen Wiener Zonen; Adressen oder Koordinaten sind nicht erforderlich.",
    ),
    "ux.custom.count": ("Customers", "Kunden"),
    "ux.custom.vans": ("Vehicles available", "Verfügbare Fahrzeuge"),
    "ux.custom.capacity": ("Capacity per vehicle (totes)", "Kapazität je Fahrzeug (Totes)"),
    "ux.custom.orders": ("Order demand", "Bestellbedarf"),
    "ux.customer": ("Customer", "Kunde"),
    "ux.totes": ("Totes", "Totes"),
    "ux.custom.advanced": ("Advanced location settings", "Erweiterte Standorteinstellungen"),
    "ux.seed": ("Location seed", "Startwert für Standorte"),
    "ux.seed.help": (
        "Controls the reproducible generation of synthetic customer locations.",
        "Steuert die reproduzierbare Erzeugung synthetischer Kundenstandorte.",
    ),
    "ux.detour": ("Distance detour factor", "Umwegfaktor für Distanzen"),
    "ux.detour.help": (
        "Adjusts straight-line geographic distance to approximate additional travel distance.",
        "Passt die geradlinige geografische Distanz an, um zusätzlichen Reiseaufwand anzunähern.",
    ),
    "ux.generate": ("Generate scenario", "Szenario generieren"),
    "ux.custom.changed": (
        "Generate this scenario before running the comparison.",
        "Generieren Sie das Szenario vor dem Vergleich neu.",
    ),
    "ux.custom.ready": (
        "Scenario generated. Review the map and demand in the preview, then run the comparison.",
        "Szenario generiert. Prüfen Sie Karte und Bedarf in der Vorschau und starten Sie "
        "anschließend den Vergleich.",
    ),
    "ux.check.pass": ("Pass", "Bestanden"),
    "ux.check.fail": ("Fail", "Nicht bestanden"),
    "ux.check.order.title": ("Order capacity", "Auftragskapazität"),
    "ux.check.order.largest": ("Largest order: {n} totes", "Größte Bestellung: {n} Totes"),
    "ux.check.order.capacity": ("Vehicle capacity: {n} totes", "Fahrzeugkapazität: {n} Totes"),
    "ux.check.order.tip": (
        "The largest customer order must fit within a single vehicle because orders are not split.",
        "Die größte Kundenbestellung muss in ein einzelnes Fahrzeug passen, weil Bestellungen "
        "nicht aufgeteilt werden.",
    ),
    "ux.check.fleet.title": ("Fleet capacity", "Flottenkapazität"),
    "ux.check.fleet.demand": ("Total demand: {n} totes", "Gesamtbedarf: {n} Totes"),
    "ux.check.fleet.capacity": ("Fleet capacity: {n} totes", "Flottenkapazität: {n} Totes"),
    "ux.check.fleet.tip": (
        "Total available fleet capacity must be at least as large as total customer demand.",
        "Die verfügbare Flottenkapazität muss mindestens so groß sein wie der gesamte Kundenbedarf.",
    ),
    "ux.check.spare": ("Spare fleet capacity", "Freie Flottenkapazität"),
    "ux.check.spare.value": ("{n} totes", "{n} Totes"),
    "ux.check.min": ("Minimum fleet requirement", "Mindestflottenbedarf"),
    "ux.check.min.required": ("Minimum required: {n}", "Mindestbedarf: {n}"),
    "ux.check.min.available": ("Available: {n}", "Verfügbar: {n}"),
    "ux.check.min.help": (
        "This is the minimum number of vehicles implied by total demand and vehicle capacity.",
        "Das ist die Mindestzahl an Fahrzeugen aus Gesamtbedarf und Fahrzeugkapazität.",
    ),
    "ux.check.oversize": (
        "An order exceeds one vehicle's capacity. Reduce that order or increase capacity.",
        "Eine Bestellung überschreitet die Fahrzeugkapazität. Bestellbedarf reduzieren oder "
        "Kapazität erhöhen.",
    ),
    "ux.check.oversize.row": (
        "{id} exceeds vehicle capacity ({demand} > {capacity} totes).",
        "{id} überschreitet die Fahrzeugkapazität ({demand} > {capacity} Totes).",
    ),
    "ux.check.overflow": (
        "Fleet capacity is insufficient. Increase the number of vehicles, increase vehicle "
        "capacity, or reduce customer demand before generating the scenario.",
        "Die Flottenkapazität reicht nicht aus. Erhöhen Sie die Fahrzeugzahl oder die "
        "Fahrzeugkapazität, oder reduzieren Sie den Kundenbedarf, bevor Sie das Szenario generieren.",
    ),
    "ux.check.invalid": (
        "Enter a positive whole number of totes for every customer.",
        "Für jeden Kunden eine positive ganze Anzahl Totes eingeben.",
    ),
    "ux.check.packing": (
        "Passing these checks does not guarantee a complete feasible route plan. Unsplit customer "
        "orders may still prevent all demand from being packed into the available vehicles.",
        "Bestandene Prüfungen garantieren keinen vollständigen zulässigen Tourenplan. Ungeteilte "
        "Kundenbestellungen können trotzdem verhindern, dass der gesamte Bedarf auf die verfügbaren "
        "Fahrzeuge verteilt wird.",
    ),
    "ux.preview": ("Scenario preview", "Szenariovorschau"),
    "ux.preview.summary": (
        "{n} customers · {demand} totes · {vans} vehicles × {capacity} totes",
        "{n} Kunden · {demand} Totes · {vans} Fahrzeuge × {capacity} Totes",
    ),
    "ux.preview.customers": ("Customers", "Kunden"),
    "ux.preview.demand": ("Total demand", "Gesamtbedarf"),
    "ux.preview.demand.value": ("{n} totes", "{n} Totes"),
    "ux.preview.fleet": ("Fleet", "Flotte"),
    "ux.preview.fleet.value": ("{n} vehicles", "{n} Fahrzeuge"),
    "ux.preview.capacity": ("Capacity", "Kapazität"),
    "ux.preview.capacity.value": ("{n} totes/vehicle", "{n} Totes/Fahrzeug"),
    "ux.preview.spare": ("Spare capacity", "Freie Kapazität"),
    "ux.preview.spare.value": ("{n} totes", "{n} Totes"),
    "ux.run": ("Run comparison", "Vergleich starten"),
    "ux.settings": ("Search settings", "Sucheinstellungen"),
    "ux.seconds": ("Optimization search limit", "Optimierungs-Suchlimit"),
    "ux.seconds.opt": ("{n} s", "{n} s"),
    "ux.seconds.help": (
        "Sets the maximum search time used to improve the route plan.",
        "Legt die maximale Suchzeit fest, um den Tourenplan zu verbessern.",
    ),
    "ux.api.offline.title": ("Planning service unavailable", "Planungsdienst nicht verfügbar"),
    "ux.api.offline.body": (
        "Scenario generation and comparison cannot run until the planning service is restored.",
        "Szenarien können erst erzeugt oder verglichen werden, wenn der Planungsdienst wieder erreichbar ist.",
    ),
    "ux.api.starting.title": ("Planning service is starting", "Planungsdienst wird gestartet"),
    "ux.api.starting.body": (
        "This can take a little longer after a period of inactivity.",
        "Nach längerer Inaktivität kann dies etwas länger dauern.",
    ),
    "ux.api.starting": (
        "Planning service is starting. This can take a little longer after a period of inactivity.",
        "Planungsdienst wird gestartet. Nach längerer Inaktivität kann dies etwas länger dauern.",
    ),
    "ux.api.command": ("Show startup command", "Startbefehl anzeigen"),
    "ux.stage.load": ("Loading scenario", "Szenario wird geladen"),
    "ux.stage.baseline": (
        "Building nearest-neighbour baseline",
        "Nächster-Nachbar-Baseline wird erstellt",
    ),
    "ux.stage.optimise": (
        "Searching for optimized solution with OR-Tools",
        "Suche nach optimierter Lösung mit OR-Tools",
    ),
    "ux.stage.optimise.detail": (
        "Up to {n} seconds",
        "Bis zu {n} Sekunden",
    ),
    "ux.stage.reconcile": (
        "Validating routes, capacity and distances",
        "Touren, Kapazität und Distanzen werden geprüft",
    ),
    "ux.stage.prepare": ("Preparing comparison", "Vergleich wird vorbereitet"),
    "ux.stage.done": ("Comparison ready", "Vergleich bereit"),
    "ux.stage.failed": (
        "Comparison could not be completed",
        "Vergleich konnte nicht abgeschlossen werden",
    ),
    "ux.plan.title": ("Route comparison", "Tourenvergleich"),
    "ux.plan.subtitle": (
        "Compare a reference route plan with an optimized route plan for the same "
        "customers, demand, fleet and capacity limits.",
        "Einen Referenz-Tourenplan mit einem optimierten Tourenplan für dieselben "
        "Kunden, denselben Bedarf, dieselbe Flotte und dieselben Kapazitätsgrenzen vergleichen.",
    ),
    "ux.plan.summary": ("Comparison summary", "Vergleichsübersicht"),
    "ux.plan.empty": (
        "Choose a scenario and run the comparison first.",
        "Wählen Sie ein Szenario und starten Sie zuerst den Vergleich.",
    ),
    "ux.plan.expired.title": ("Route result expired", "Tourenergebnis abgelaufen"),
    "ux.plan.expired.body": (
        "This saved route result is no longer available. "
        "Run the scenario again to generate a new comparison.",
        "Dieses gespeicherte Tourenergebnis ist nicht mehr verfügbar. "
        "Führen Sie das Szenario erneut aus, um einen neuen Vergleich zu erzeugen.",
    ),
    "ux.plan.expired.action": ("Run scenario again", "Szenario erneut ausführen"),
    "ux.plan.scenario": ("Scenario: {name}", "Szenario: {name}"),
    "ux.plan.tab.comparison": ("Comparison", "Vergleich"),
    "ux.plan.tab.baseline": ("Baseline details", "Baseline-Details"),
    "ux.plan.tab.optimised": ("Optimized details", "Optimierte Details"),
    "ux.plan.why.title": ("Why compare two route plans?", "Warum zwei Tourenpläne vergleichen?"),
    "ux.plan.why.body": (
        "The baseline provides a consistent reference route plan built from the same scenario "
        "inputs. Comparing it with the optimized route plan shows how much total fleet "
        "distance travelled can be reduced without changing customer demand, fleet size or "
        "vehicle capacity.",
        "Die Baseline liefert einen konsistenten Referenz-Tourenplan aus denselben "
        "Szenarioeingaben. Der Vergleich mit dem optimierten Tourenplan zeigt, wie stark die "
        "zurückgelegte Gesamtdistanz der Flotte reduziert werden kann, ohne Kundenbedarf, "
        "Flottengröße oder Fahrzeugkapazität zu ändern.",
    ),
    "ux.plan.why.tip": (
        "A deterministic nearest-neighbour method used as a reference for measuring the "
        "improvement achieved through optimization.",
        "Eine deterministische Nächster-Nachbar-Methode als Referenz, um die Verbesserung "
        "durch die Optimierung zu messen.",
    ),
    "ux.plan.result": (
        "The optimized route plan reduces total fleet distance travelled from {baseline_km} "
        "to {optimized_km}, a {reduction} reduction. Both plans serve all {customer_count} "
        "customers while respecting vehicle-capacity limits.",
        "Der optimierte Tourenplan senkt die zurückgelegte Gesamtdistanz der Flotte von "
        "{baseline_km} auf {optimized_km}, eine Reduktion um {reduction}. Beide Pläne "
        "bedienen alle {customer_count} Kunden und halten die Fahrzeugkapazitätsgrenzen ein.",
    ),
    "ux.plan.kpi.baseline": ("Baseline distance travelled", "Zurückgelegte Baseline-Distanz"),
    "ux.plan.kpi.optimised": ("Optimized distance travelled", "Zurückgelegte optimierte Distanz"),
    "ux.plan.kpi.saving": ("Distance reduction", "Distanzreduktion"),
    "ux.plan.kpi.served": ("Customers served", "Bediente Kunden"),
    "ux.plan.map.guide": (
        "Map lines show the route sequence schematically. They do not represent actual road "
        "paths or live navigation.",
        "Kartenlinien zeigen die Tourfolge schematisch. Sie stellen keine echten Straßenwege "
        "und keine Live-Navigation dar.",
    ),
    "ux.plan.map.numbers": (
        "Numbers indicate the order of customer stops. Depot departure and return are not numbered.",
        "Zahlen zeigen die Reihenfolge der Kundenstopps. Depotstart und -rückkehr sind nicht nummeriert.",
    ),
    "ux.plan.map.depot": (
        "Depot: The common start and return point for all vehicle routes.",
        "Depot: Der gemeinsame Start- und Rückkehrpunkt aller Fahrzeugtouren.",
    ),
    "ux.plan.baseline.heading": ("Baseline route plan", "Baseline-Tourenplan"),
    "ux.plan.baseline.method": (
        "Nearest-neighbour reference method",
        "Nächster-Nachbar-Referenzmethode",
    ),
    "ux.plan.baseline.method.tip": (
        "A deterministic routing method that repeatedly selects the nearest feasible unserved "
        "customer.",
        "Eine deterministische Tourenmethode, die wiederholt den nächsten zulässigen noch "
        "nicht bedienten Kunden wählt.",
    ),
    "ux.plan.baseline.sub": (
        "Inspect the deterministic reference plan used to measure the effect of route "
        "optimization.",
        "Den deterministischen Referenzplan prüfen, mit dem die Wirkung der Tourenoptimierung "
        "gemessen wird.",
    ),
    "ux.plan.opt.heading": ("Optimized route plan", "Optimierter Tourenplan"),
    "ux.plan.opt.tip": (
        "The plan is the best feasible result found within the selected search time. Global "
        "optimality is not claimed.",
        "Der Plan ist das beste zulässige Ergebnis innerhalb der gewählten Suchzeit. Globale "
        "Optimalität wird nicht behauptet.",
    ),
    "ux.plan.opt.sub": (
        "Inspect the improved route plan produced for the same customer demand, fleet and "
        "capacity limits.",
        "Den verbesserten Tourenplan für denselben Kundenbedarf, dieselbe Flotte und dieselben "
        "Kapazitätsgrenzen prüfen.",
    ),
    "ux.plan.feasible": ("Feasible plan", "Zulässiger Plan"),
    "ux.plan.feasible.text": (
        "All customers are served and vehicle-capacity limits are respected.",
        "Alle Kunden werden bedient und die Fahrzeugkapazitätsgrenzen eingehalten.",
    ),
    "ux.plan.incomplete": ("Incomplete plan", "Unvollständiger Plan"),
    "ux.plan.no_solution": ("No complete solution found", "Keine vollständige Lösung gefunden"),
    "ux.baseline": ("Nearest-neighbour baseline", "Nächster-Nachbar-Baseline"),
    "ux.optimised": ("Optimized solution (OR-Tools)", "Optimierte Lösung (OR-Tools)"),
    "ux.optimised.short": ("Optimized solution", "Optimierte Lösung"),
    "ux.kpi.baseline": ("Baseline distance", "Baseline-Distanz"),
    "ux.kpi.optimised": ("Optimized distance", "Optimierte Distanz"),
    "ux.kpi.saving": ("Distance reduction", "Distanzreduktion"),
    "ux.kpi.served": ("Customers served", "Bediente Kunden"),
    "ux.proof.served": ("Customers served", "Bediente Kunden"),
    "ux.plan.ineligible": (
        "A complete route comparison is not available because one or both route plans are "
        "incomplete. Review the individual plan results below.",
        "Ein vollständiger Tourenvergleich ist nicht verfügbar, weil einer oder beide "
        "Tourenpläne unvollständig sind. Prüfen Sie die einzelnen Planergebnisse unten.",
    ),
    "ux.plan.served.each": (
        "Baseline: {baseline_served} / {baseline_total} customers served · {baseline_status}\n"
        "Optimized: {optimised_served} / {optimised_total} customers served · {optimised_status}",
        "Baseline: {baseline_served} / {baseline_total} Kunden bedient · {baseline_status}\n"
        "Optimiert: {optimised_served} / {optimised_total} Kunden bedient · {optimised_status}",
    ),
    "ux.plan.partial": ("Partial constructed distance: {km}", "Konstruierte Teildistanz: {km}"),
    "ux.plan.unserved": ("Unserved customers: {ids}", "Nicht bediente Kunden: {ids}"),
    "ux.plan.routes": ("Vehicle routes", "Fahrzeugtouren"),
    "ux.plan.view.baseline": (
        "View baseline route details",
        "Baseline-Tourdetails anzeigen",
    ),
    "ux.plan.view.optimised": (
        "View optimized route details",
        "Optimierte Tourdetails anzeigen",
    ),
    "ux.plan.pick": ("Plan view", "Planansicht"),
    "ux.plan.table": ("Vehicle routes", "Fahrzeugtouren"),
    "ux.plan.total": (
        "Total fleet distance travelled: {km}",
        "Zurückgelegte Gesamtdistanz der Flotte: {km}",
    ),
    "ux.plan.reduction": ("{reduction} lower than the baseline", "{reduction} niedriger als die Baseline"),
    "ux.plan.details": ("Detailed route data", "Detaillierte Tourdaten"),
    "ux.plan.details.cap": (
        "Inspect the stop sequence, customer demand and distance travelled on each route.",
        "Stoppfolge, Kundenbedarf und zurückgelegte Distanz je Tour prüfen.",
    ),
    "ux.plan.sequences": ("Route sequences", "Tourfolgen"),
    "ux.plan.load": ("Load / capacity", "Beladung / Kapazität"),
    "ux.plan.customers": ("Customers served", "Bediente Kunden"),
    "ux.plan.travelled": ("Distance travelled", "Zurückgelegte Distanz"),
    "ux.plan.totes": ("totes", "Totes"),
    "ux.plan.col.stop": ("Stop no.", "Stopp-Nr."),
    "ux.plan.col.location": ("Location", "Ort"),
    "ux.plan.col.demand": ("Demand (totes)", "Bedarf (Totes)"),
    "ux.plan.col.leg": ("Leg distance", "Teilstrecke"),
    "ux.plan.col.cumulative": ("Cumulative demand (totes)", "Kumulativer Bedarf (Totes)"),
    "ux.plan.exports": ("Export results", "Ergebnisse exportieren"),
    "ux.plan.exports.cap": (
        "Download the recorded route data for further analysis or review.",
        "Die gespeicherten Tourdaten zur weiteren Analyse oder Prüfung herunterladen.",
    ),
    "ux.plan.export.baseline": ("Baseline data", "Baseline-Daten"),
    "ux.plan.export.optimised": ("Optimized data", "Optimierte Daten"),
    "ux.plan.validation": ("Validation summary", "Validierungsübersicht"),
    "ux.plan.validation.intro": (
        "Both route plans pass the core customer-service, capacity, distance and "
        "route-continuity checks.",
        "Beide Tourenpläne bestehen die zentralen Prüfungen zu Kundenbedienung, Kapazität, "
        "Distanz und Tourkontinuität.",
    ),
    "ux.plan.validation.check": ("Validation check", "Validierungsprüfung"),
    "ux.plan.validation.open": ("View model validation", "Modellprüfung anzeigen"),
    "ux.plan.review": ("Technical review", "Technische Prüfung"),
    "ux.plan.review.body": (
        "Explore how the route plans were validated or review the model formulation, "
        "assumptions and solution approach.",
        "Prüfen, wie die Tourenpläne validiert wurden, oder Formulierung, Annahmen und "
        "Lösungsansatz des Modells nachlesen.",
    ),
    "ux.plan.audit": ("Model checks", "Modellprüfungen"),
    "ux.plan.audit.failed": (
        "Some checks did not pass. Review model validation before using this plan.",
        "Einige Prüfungen sind fehlgeschlagen. Prüfen Sie die Modellvalidierung vor der "
        "Verwendung dieses Plans.",
    ),
    "ux.plan.method.open": ("Open methodology", "Methodik öffnen"),
    "ux.van": ("Vehicle", "Fahrzeug"),
    "ux.load": ("Load (totes)", "Beladung (Totes)"),
    "ux.stops": ("Customer stops", "Kundenstopps"),
    "ux.stops.help": (
        "Number of customers served by this vehicle. Depot start and return are not included.",
        "Anzahl der von diesem Fahrzeug bedienten Kunden. Depotstart und -rückkehr sind nicht enthalten.",
    ),
    "ux.distance": ("Route distance", "Tourdistanz"),
    "ux.sequence": ("Route sequence", "Tourfolge"),
    "ux.stop": ("Stop", "Stopp"),
    "ux.leg": ("Leg distance", "Teilstrecke"),
    "ux.cumulative": ("Demand served so far (totes)", "Bisher bedienter Bedarf (Totes)"),
    "ux.method.title": (
        "Vehicle Routing Model and Solution Methods",
        "Tourenplanungsmodell und Lösungsmethoden",
    ),
    "ux.method.subtitle": (
        "The formulation, assumptions, constraints, baseline construction and OR-Tools search "
        "used in LastMile Lab.",
        "Formulierung, Annahmen, Nebenbedingungen, Baseline-Konstruktion und OR-Tools-Suche "
        "in LastMile Lab.",
    ),
    "ux.method.vrp.title": ("Vehicle Routing Problem (VRP)", "Vehicle Routing Problem (VRP)"),
    "ux.method.vrp": (
        "The Vehicle Routing Problem (VRP) determines how a fleet should serve a set of "
        "locations from a depot. The routing decision has two closely related parts: "
        "assignment of customers to vehicles, and sequencing of the stops on each vehicle "
        "route. The objective function in this application is the total estimated distance "
        "travelled by used vehicles.",
        "Das Vehicle Routing Problem (VRP) bestimmt, wie eine Flotte eine Menge von Orten "
        "von einem Depot aus bedienen soll. Die Tourenentscheidung hat zwei eng verbundene "
        "Teile: die Zuordnung von Kunden zu Fahrzeugen und die Sequenzierung der Stopps auf "
        "jeder Fahrzeugtour. Die Zielfunktion in dieser Anwendung ist die geschätzte "
        "Gesamtdistanz der genutzten Fahrzeuge.",
    ),
    "ux.method.vrp.feas": (
        "A feasible plan must serve every customer exactly once and return each used vehicle "
        "to the depot.",
        "Ein zulässiger Plan muss jeden Kunden genau einmal bedienen und jedes genutzte "
        "Fahrzeug zum Depot zurückführen.",
    ),
    "ux.method.cvrp.title": (
        "Capacitated Vehicle Routing Problem (CVRP)",
        "Capacitated Vehicle Routing Problem (CVRP)",
    ),
    "ux.method.cvrp": (
        "LastMile Lab uses the capacitated variant of the VRP. Each customer has a demand "
        "in totes (standard reusable delivery containers), and each vehicle has the same "
        "fixed tote capacity. Orders are unsplit: the entire demand of one customer must "
        "remain on one vehicle. Assigned demand cannot exceed vehicle capacity.",
        "LastMile Lab verwendet die kapazitätsbeschränkte Variante des VRP. Jeder Kunde hat "
        "einen Bedarf in Totes (standardisierte Mehrweg-Lieferbehälter), und jedes Fahrzeug "
        "hat dieselbe feste Tote-Kapazität. Aufträge sind ungeteilt: der gesamte Bedarf eines "
        "Kunden bleibt auf einem Fahrzeug. Der zugeordnete Bedarf darf die Fahrzeugkapazität "
        "nicht überschreiten.",
    ),
    "ux.method.cvrp.unused": (
        "The fleet is homogeneous. Vehicles may remain unused if they are not required.",
        "Die Flotte ist homogen. Fahrzeuge dürfen ungenutzt bleiben, wenn sie nicht benötigt werden.",
    ),
    "ux.method.obj.title": ("Distance-minimization objective", "Distanzminimierungsziel"),
    "ux.method.obj": (
        "The objective function minimizes the total estimated distance travelled over all "
        "used vehicle routes, including the return to the depot.",
        "Die Zielfunktion minimiert die geschätzte Gesamtdistanz über alle genutzten "
        "Fahrzeugtouren, einschließlich der Rückkehr zum Depot.",
    ),
    "ux.method.obj.formula.title": ("Documented objective expression", "Dokumentierter Zielausdruck"),
    "ux.method.obj.formula": (
        "minimize  sum over vehicles k, origins i and destinations j of  d_ij · x_ijk",
        "minimiere  Summe über Fahrzeuge k, Ursprünge i und Ziele j von  d_ij · x_ijk",
    ),
    "ux.method.obj.formula.note": (
        "This compact expression matches the documented mixed-integer formulation. Decision "
        "variables x_ijk indicate whether vehicle k travels from node i to node j. The "
        "production application does not solve that programme with a MIP solver.",
        "Dieser kompakte Ausdruck entspricht der dokumentierten gemischt-ganzzahligen "
        "Formulierung. Entscheidungsvariablen x_ijk geben an, ob Fahrzeug k von Knoten i nach "
        "Knoten j fährt. Die produktive Anwendung löst dieses Programm nicht mit einem MIP-Solver.",
    ),
    "ux.method.cons.title": ("Core constraints", "Kernnebenbedingungen"),
    "ux.method.cons.service.title": ("Demand satisfaction", "Bedarfsdeckung"),
    "ux.method.cons.service": (
        "Every customer must be served exactly once.",
        "Jeder Kunde muss genau einmal bedient werden.",
    ),
    "ux.method.cons.capacity.title": ("Vehicle capacity", "Fahrzeugkapazität"),
    "ux.method.cons.capacity": (
        "Assigned tote demand on a vehicle cannot exceed that vehicle's capacity.",
        "Der einem Fahrzeug zugeordnete Tote-Bedarf darf dessen Kapazität nicht überschreiten.",
    ),
    "ux.method.cons.unsplit.title": ("Unsplit orders", "Ungeteilte Aufträge"),
    "ux.method.cons.unsplit": (
        "All totes for one customer remain on the same vehicle.",
        "Alle Totes eines Kunden bleiben auf demselben Fahrzeug.",
    ),
    "ux.method.cons.depot.title": ("Depot continuity", "Depotkontinuität"),
    "ux.method.cons.depot": (
        "Every used vehicle starts at the depot and returns to the depot. Unused vehicles "
        "are permitted.",
        "Jedes genutzte Fahrzeug startet am Depot und kehrt zum Depot zurück. Ungenutzte "
        "Fahrzeuge sind zulässig.",
    ),
    "ux.method.cons.route.title": ("Route continuity", "Tourkontinuität"),
    "ux.method.cons.route": (
        "Each used vehicle follows one continuous stop sequence from the depot and back.",
        "Jedes genutzte Fahrzeug folgt einer zusammenhängenden Stoppfolge vom Depot und zurück.",
    ),
    "ux.method.figure.caption": (
        "Assignment of unsplit orders to vehicles, then sequencing from the depot under capacity.",
        "Zuordnung ungeteilter Aufträge zu Fahrzeugen, danach Sequenzierung vom Depot unter Kapazität.",
    ),
    "ux.method.figure.label": (
        "Assignment and sequencing under capacity",
        "Zuordnung und Sequenzierung unter Kapazität",
    ),
    "ux.method.figure.sheet": (
        "Spreadsheet formulation",
        "Tabellenkalkulationsformulierung",
    ),
    "ux.method.opensolver.title": (
        "Research lineage",
        "Forschungslinie",
    ),
    "ux.method.opensolver": (
        "Earlier modelling work for this last-mile CVRP was solved as a spreadsheet "
        "mixed-integer programme using the OpenSolver add-in for Excel. That formulation "
        "remains in the repository as documentation of the research lineage. OpenSolver is "
        "not the solver used by this application.",
        "Frühere Modellierungsarbeit zu diesem Last-Mile-CVRP wurde als gemischt-ganzzahliges "
        "Programm in einer Tabellenkalkulation mit dem OpenSolver-Add-in für Excel gelöst. "
        "Diese Formulierung bleibt im Repository als Dokumentation der Forschungslinie. "
        "OpenSolver ist nicht der Solver dieser Anwendung.",
    ),
    "ux.method.baseline.title": ("Nearest-neighbour baseline", "Nächster-Nachbar-Baseline"),
    "ux.method.baseline": (
        "The nearest-neighbour baseline is a deterministic, capacity-aware construction "
        "heuristic. For each vehicle, the method repeatedly selects the nearest unserved "
        "customer whose complete order still fits within the remaining capacity. When no "
        "additional feasible customer fits, the vehicle returns to the depot and the next "
        "vehicle is opened.",
        "Die Nächster-Nachbar-Baseline ist eine deterministische, kapazitätsbewusste "
        "Konstruktionsheuristik. Für jedes Fahrzeug wählt das Verfahren wiederholt den nächsten "
        "unbedienten Kunden, dessen vollständige Bestellung noch in die Restkapazität passt. "
        "Passt kein weiterer zulässiger Kunde, kehrt das Fahrzeug zum Depot zurück und das "
        "nächste Fahrzeug wird geöffnet.",
    ),
    "ux.method.baseline.limit": (
        "Because the method makes locally attractive choices without looking ahead, it can "
        "leave a customer unserved even when a complete feasible assignment exists. It "
        "therefore serves as a transparent benchmark, not as a guarantee of the "
        "minimum-distance solution.",
        "Weil das Verfahren lokal attraktive Entscheidungen ohne Vorausschau trifft, kann ein "
        "Kunde unbedient bleiben, obwohl eine vollständige zulässige Zuordnung existiert. Es "
        "dient daher als transparente Referenz, nicht als Garantie für die distanzminimale Lösung.",
    ),
    "ux.method.solver.title": (
        "Optimized solution using Google OR-Tools",
        "Optimierte Lösung mit Google OR-Tools",
    ),
    "ux.method.solver": (
        "Google OR-Tools RoutingModel first constructs a feasible assignment and stop sequence "
        "with the PATH_CHEAPEST_ARC first-solution strategy. GUIDED_LOCAL_SEARCH then looks "
        "for shorter feasible routes. Customer visits are mandatory, and vehicle capacities "
        "are enforced by the routing model.",
        "Das Google-OR-Tools-RoutingModel konstruiert zuerst eine zulässige Zuordnung und "
        "Stoppfolge mit der Erstlösungsstrategie PATH_CHEAPEST_ARC. GUIDED_LOCAL_SEARCH sucht "
        "anschließend nach kürzeren zulässigen Touren. Kundenbesuche sind verpflichtend, und "
        "Fahrzeugkapazitäten werden durch das Routing-Modell erzwungen.",
    ),
    "ux.method.solver.limit": (
        "A search limit of 1, 5 or 10 seconds can be selected. The application reports the "
        "best feasible solution returned within that limit. Except for an independently "
        "verified teaching fixture, a time-limited result must not be described as globally optimal.",
        "Ein Suchlimit von 1, 5 oder 10 Sekunden kann gewählt werden. Die Anwendung berichtet "
        "die beste zulässige Lösung innerhalb dieses Limits. Außer bei einer unabhängig geprüften "
        "Lehrinstanz darf ein zeitlich begrenztes Ergebnis nicht als global optimal bezeichnet werden.",
    ),
    "ux.method.solver.none": (
        "The absence of a complete solution within the selected search limit is not, by itself, "
        "proof that the scenario is infeasible.",
        "Das Ausbleiben einer vollständigen Lösung innerhalb des gewählten Suchlimits ist für "
        "sich genommen kein Beweis, dass das Szenario unzulässig ist.",
    ),
    "ux.method.impl.title": ("Implementation note", "Implementierungshinweis"),
    "ux.method.impl": (
        "The documented mathematical formulation describes the CVRP structure with three-index "
        "route variables. The production application solves the routing problem through Google "
        "OR-Tools RoutingModel. Model validation reconstructs assignment and route views from "
        "the returned stop sequences; it does not read hidden solver decision variables.",
        "Die dokumentierte mathematische Formulierung beschreibt die CVRP-Struktur mit "
        "Drei-Index-Tourvariablen. Die produktive Anwendung löst das Tourenproblem mit dem "
        "Google-OR-Tools-RoutingModel. Die Modellprüfung rekonstruiert Zuordnungs- und "
        "Touransichten aus den zurückgegebenen Stoppfolgen; sie liest keine verborgenen "
        "Solver-Entscheidungsvariablen.",
    ),
    "ux.method.assumptions.title": ("Distance model and current scope", "Distanzmodell und aktueller Umfang"),
    "ux.method.assumptions": (
        "Customer and depot coordinates are synthetic. Geographic distance is estimated with "
        "the Haversine method, and a configured detour factor adjusts that estimate toward "
        "urban travel. Displayed connections are schematic: they are not road geometry. The "
        "current model does not include live traffic, time windows, split deliveries, or "
        "carbon-emissions optimization.",
        "Kunden- und Depotkoordinaten sind synthetisch. Die geografische Distanz wird mit dem "
        "Haversine-Verfahren geschätzt, ein konfigurierter Umwegfaktor nähert innerstädtische "
        "Wege an. Angezeigte Verbindungen sind schematisch und keine Straßengeometrie. Das "
        "aktuelle Modell enthält keinen Live-Verkehr, keine Zeitfenster, keine Teillieferungen "
        "und keine CO₂-Optimierung.",
    ),
    "ux.method.audit": (
        "The validation view independently checks customer coverage, vehicle capacity, depot "
        "connectivity, route-distance reconciliation and solution invariants using the route "
        "sequences returned by the planning service.",
        "Die Prüfansicht kontrolliert unabhängig Kundenabdeckung, Fahrzeugkapazität, "
        "Depotanbindung, Distanzabgleich und Lösungsinvarianten anhand der vom Planungsdienst "
        "zurückgegebenen Tourfolgen.",
    ),
    "ux.method.scope.note": (
        "This application is a static CVRP. It does not implement warehouse putaway or "
        "retrieval routing, vehicle routing with time windows, heterogeneous fleets, or "
        "carbon minimization.",
        "Diese Anwendung ist ein statisches CVRP. Sie implementiert keine Lagerplatz- oder "
        "Kommissionierrouten, kein VRP mit Zeitfenstern, keine heterogene Flotte und keine "
        "CO₂-Minimierung.",
    ),
    "ux.status.feasible": (
        "Every customer is served and vehicle-capacity constraints are satisfied.",
        "Jeder Kunde wird bedient und die Fahrzeugkapazitätsbedingungen sind erfüllt.",
    ),
    "ux.status.search": (
        "OR-Tools returned the best feasible solution found within the selected search limit. "
        "Global optimality is not claimed.",
        "OR-Tools lieferte die beste zulässige Lösung innerhalb des gewählten Suchlimits. "
        "Globale Optimalität wird nicht behauptet.",
    ),
    "ux.inspect.baseline": (
        "Deterministic nearest-neighbour construction; no solver search was used.",
        "Deterministische Nächster-Nachbar-Konstruktion; keine Solver-Suche verwendet.",
    ),
    "inspect.empty.body": (
        "Choose a scenario and run the comparison first.",
        "Wählen Sie ein Szenario und starten Sie zuerst den Vergleich.",
    ),
    "inspect.empty.title": ("No route comparison yet", "Noch kein Tourenvergleich"),
    "routes.opt": ("Optimized solution", "Optimierte Lösung"),
    "dispatch.or": ("Optimized solution (OR-Tools)", "Optimierte Lösung (OR-Tools)"),
    "compare.or": ("Optimized solution (OR-Tools)", "Optimierte Lösung (OR-Tools)"),
    "nav.optimised": ("Optimized solution", "Optimierte Lösung"),
    "ux.map.customers": ("Customers", "Kunden"),
    "ux.map.unserved": ("Unserved", "Unbedient"),
    "ux.map.demand": ("Demand", "Bedarf"),
    "ux.map.stop": ("stop", "Stopp"),
    "ux.error": (
        "The planning service could not complete this request. Please retry.",
        "Der Planungsdienst konnte die Anfrage nicht abschließen. Bitte erneut versuchen.",
    ),
    "tip.vrp": (
        "Vehicle Routing Problem: designing routes for a fleet that serves multiple locations from a depot.",
        "Vehicle Routing Problem: Touren für eine Flotte entwerfen, die mehrere Orte von einem Depot aus bedient.",
    ),
    "tip.cvrp": (
        "Capacitated VRP: a VRP in which each vehicle has a load limit.",
        "Kapazitätsbeschränktes VRP: ein VRP, in dem jedes Fahrzeug eine Lastgrenze hat.",
    ),
    "tip.tote": (
        "A standard reusable delivery container used as the common demand and capacity unit in this case study.",
        "Ein standardisierter Mehrweg-Lieferbehälter als gemeinsame Bedarfs- und Kapazitätseinheit in dieser Fallstudie.",
    ),
    "tip.depot": (
        "Depot: The common start and return location for all vehicle routes.",
        "Depot: Der gemeinsame Start- und Rückkehrort aller Fahrzeugtouren.",
    ),
    "tip.nn": (
        "A greedy construction rule that chooses the nearest currently feasible unserved customer.",
        "Eine gierige Konstruktionsregel, die den derzeit nächsten zulässigen unbedienten Kunden wählt.",
    ),
    "tip.feasible": (
        "A complete plan that serves every customer and satisfies all enforced constraints.",
        "Ein vollständiger Plan, der jeden Kunden bedient und alle durchgesetzten Nebenbedingungen erfüllt.",
    ),
    "tip.search": (
        "The maximum amount of time OR-Tools is allowed to search for an improved feasible solution.",
        "Die maximale Zeit, in der OR-Tools nach einer verbesserten zulässigen Lösung suchen darf.",
    ),
    "tip.detour": (
        "A multiplier applied to geographic distance to approximate urban travel.",
        "Ein Multiplikator auf die geografische Distanz zur Annäherung innerstädtischer Wege.",
    ),
    "tip.minvans": (
        "A lower bound based on total demand. It does not prove that unsplit orders can be packed into exactly that number of vehicles.",
        "Eine Untergrenze anhand des Gesamtbedarfs. Sie beweist nicht, dass ungeteilte Aufträge genau auf diese Fahrzeugzahl verteilt werden können.",
    ),
    "tip.haversine": (
        "A straight-line distance over the Earth's surface calculated from latitude and longitude.",
        "Eine geradlinige Distanz über die Erdoberfläche aus Breite und Länge.",
    ),
    "api.status.on": ("Planning service available", "Planungsdienst verfügbar"),
    "api.status.off": ("Planning service unavailable", "Planungsdienst nicht verfügbar"),
    "api.status.starting": ("Planning service is starting", "Planungsdienst wird gestartet"),
}

WORKFLOW_STRINGS = {
    language: {key: pair[index] for key, pair in COPY.items()}
    for index, language in enumerate(("en", "de"))
}
