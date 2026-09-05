"""Paired English/German copy for the three-page planning journey."""

# Keeping each pair together makes reviews of new product copy straightforward.
COPY = {
    "ux.export.prepare": ("Prepare JSON and CSV", "JSON und CSV vorbereiten"),
    "ux.preview.empty": (
        "Generate the scenario to preview customer locations here.",
        "Szenario erzeugen, um hier die Kundenstandorte zu sehen.",
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
    "ux.over.diagram.note": (
        "Illustrative published reference only. The browser is not solving a routing model, "
        "and the figure is not road geometry.",
        "Nur eine illustrative veröffentlichte Referenz. Der Browser löst kein Tourenmodell, "
        "und die Abbildung ist keine Straßengeometrie.",
    ),
    "check.audit.DEMAND_SATISFACTION": (
        "Every customer served exactly once",
        "Jeder Kunde genau einmal bedient",
    ),
    "check.audit.CAPACITY": ("Vehicle capacities respected", "Fahrzeugkapazitäten eingehalten"),
    "check.audit.DISTANCE": (
        "Distances reconciled with the matrix",
        "Distanzen mit der Matrix abgeglichen",
    ),
    "check.audit.DEPOT_CONNECTIVITY": (
        "Routes return to the depot",
        "Touren kehren zum Depot zurück",
    ),
    "check.audit.INVARIANTS": (
        "All feasible-solution invariants passed",
        "Alle Invarianten zulässiger Lösungen erfüllt",
    ),
    "nav.home": ("01  Overview", "01  Überblick"),
    "nav.dispatch": ("02  Scenarios", "02  Szenarien"),
    "nav.compare": ("03  Plan", "03  Plan"),
    "nav.method": ("Methodology", "Methodik"),
    "nav.inspect": ("Model validation", "Modellprüfung"),
    "nav.workflow": ("WORKFLOW", "ABLAUF"),
    "nav.secondary": ("MODEL & METHODS", "MODELL UND METHODEN"),
    "nav.language": ("LANGUAGE", "SPRACHE"),
    "brand.sub": ("CVRP route optimization", "CVRP-Tourenoptimierung"),
    "footer": (
        "LastMile Lab · Vienna · Estimated-distance planning",
        "LastMile Lab · Wien · Planung mit geschätzten Distanzen",
    ),
    "lang.label": ("Language / Sprache", "Language / Sprache"),
    "ux.over.kicker": (
        "Capacitated Vehicle Routing Problem (CVRP)",
        "Capacitated Vehicle Routing Problem (CVRP)",
    ),
    "ux.over.title": (
        "Optimize last-mile delivery routes under vehicle-capacity constraints",
        "Last-Mile-Touren unter Fahrzeugkapazitätsgrenzen optimieren",
    ),
    "ux.over.intro": (
        "LastMile Lab models a static, single-depot Capacitated Vehicle Routing Problem "
        "(CVRP). Each customer order must be assigned to one vehicle, every route must "
        "respect vehicle capacity, and the stop sequence is selected with the objective of "
        "minimizing total estimated fleet distance.",
        "LastMile Lab modelliert ein statisches Capacitated Vehicle Routing Problem (CVRP) "
        "mit einem Depot. Jede Kundenbestellung wird einem Fahrzeug zugeordnet, jede Tour "
        "muss die Fahrzeugkapazität einhalten, und die Stoppfolge wird so gewählt, dass die "
        "geschätzte Gesamtdistanz der Flotte minimiert wird.",
    ),
    "ux.over.compare.body": (
        "The application compares a deterministic nearest-neighbour baseline with an "
        "optimized solution returned by Google OR-Tools within a configurable search limit.",
        "Die Anwendung vergleicht eine deterministische Nächster-Nachbar-Baseline mit einer "
        "optimierten Lösung, die Google OR-Tools innerhalb eines wählbaren Suchlimits zurückgibt.",
    ),
    "ux.over.context": (
        "Synthetic Vienna scenario · One depot · Unsplit customer orders · Distance-minimization objective",
        "Synthetisches Wien-Szenario · Ein Depot · Ungeteilte Kundenaufträge · Distanzminimierung",
    ),
    "ux.over.vrp.title": ("01  Routing objective", "01  Tourenziel"),
    "ux.over.vrp": (
        "Serve every customer while minimizing total estimated fleet distance.",
        "Jeden Kunden bedienen und die geschätzte Gesamtdistanz der Flotte minimieren.",
    ),
    "ux.over.cvrp.title": ("02  Capacity constraints", "02  Kapazitätsbedingungen"),
    "ux.over.cvrp": (
        "The Capacitated Vehicle Routing Problem (CVRP) adds vehicle-capacity limits. "
        "Customer demand is measured in totes (standard reusable delivery containers), "
        "and each unsplit customer order must fit within the capacity of its assigned vehicle.",
        "Das Capacitated Vehicle Routing Problem (CVRP) ergänzt Fahrzeugkapazitätsgrenzen. "
        "Der Kundenbedarf wird in Totes (standardisierte Mehrweg-Lieferbehälter) gemessen, "
        "und jede ungeteilte Bestellung muss in die Kapazität des zugeordneten Fahrzeugs passen.",
    ),
    "ux.over.feas.title": ("03  Route feasibility", "03  Tourenzulässigkeit"),
    "ux.over.feas": (
        "Every used vehicle starts at the depot, visits its assigned customers, and returns "
        "to the depot. Each customer must be served exactly once.",
        "Jedes genutzte Fahrzeug startet am Depot, besucht die zugeordneten Kunden und kehrt "
        "zum Depot zurück. Jeder Kunde muss genau einmal bedient werden.",
    ),
    "ux.over.compare.title": ("04  Solution comparison", "04  Lösungsvergleich"),
    "ux.over.compare": (
        "The application compares a deterministic nearest-neighbour baseline with the "
        "time-limited optimized solution returned by Google OR-Tools.",
        "Die Anwendung vergleicht eine deterministische Nächster-Nachbar-Baseline mit der "
        "zeitlich begrenzten optimierten Lösung von Google OR-Tools.",
    ),
    "ux.over.proof": (
        "Vienna Standard 24 · Published reference",
        "Wien Standard 24 · Veröffentlichte Referenz",
    ),
    "ux.over.proof.cap": (
        "Reference result published 4 September 2026. The deterministic nearest-neighbour "
        "baseline covers 122.394 km. With a 5-second search limit, Google OR-Tools returned "
        "a feasible 97.193 km solution, representing a 20.6% reduction in estimated total "
        "distance. Global optimality is not claimed, and later OR-Tools runs may differ.",
        "Referenzergebnis veröffentlicht am 4. September 2026. Die deterministische "
        "Nächster-Nachbar-Baseline umfasst 122,394 km. Mit einem Suchlimit von 5 Sekunden "
        "lieferte Google OR-Tools eine zulässige Lösung von 97,193 km, also 20,6 % weniger "
        "geschätzte Gesamtdistanz. Globale Optimalität wird nicht behauptet; spätere "
        "OR-Tools-Läufe können abweichen.",
    ),
    "ux.over.disclosure": (
        "Synthetic portfolio scenario. Customer locations, demands and distances are "
        "illustrative. No retailer data or live traffic information is used.",
        "Synthetisches Portfolio-Szenario. Kundenstandorte, Bedarfe und Distanzen sind "
        "illustrativ. Es werden keine Händlerdaten und keine Live-Verkehrsdaten verwendet.",
    ),
    "ux.over.future": (
        "Current optimization objective: minimize total estimated fleet distance. Carbon "
        "emissions are outside the current model scope and may be considered in a future extension.",
        "Aktuelles Optimierungsziel: Minimierung der geschätzten Gesamtdistanz der Flotte. "
        "CO₂-Emissionen liegen außerhalb des aktuellen Modellumfangs und können in einer "
        "späteren Erweiterung betrachtet werden.",
    ),
    "ux.over.cta": ("Choose a scenario", "Szenario auswählen"),
    "ux.over.result": ("122.4 km → 97.2 km · 20.6% shorter", "122,4 km → 97,2 km · 20,6 % kürzer"),
    "ux.over.anim.baseline": ("Nearest-neighbour baseline", "Nächster-Nachbar-Baseline"),
    "ux.over.anim.optimized": ("Optimized solution", "Optimierte Lösung"),
    "ux.over.anim.km": ("122.4 km", "122,4 km"),
    "ux.over.anim.what": (
        "What is optimized: total estimated fleet distance",
        "Was optimiert wird: geschätzte Gesamtdistanz der Flotte",
    ),
    "ux.over.anim.depot": ("Depot", "Depot"),
    "empty.open": ("Go to Scenarios", "Zu Szenarien"),
    "empty.plan.title": ("No route comparison yet", "Noch kein Tourenvergleich"),
    "ux.scenarios.title": ("Choose a planning scenario", "Planungsszenario auswählen"),
    "ux.scenarios.subtitle": (
        "Select a curated preset or build a delivery wave, then run the comparison.",
        "Vordefiniertes Szenario wählen oder eine Lieferwelle erstellen und den Vergleich starten.",
    ),
    "ux.source": ("Scenario source", "Szenarioquelle"),
    "ux.presets": ("Curated presets", "Vordefinierte Szenarien"),
    "ux.custom": ("Custom scenario", "Eigenes Szenario"),
    "scenario.VIENNA_STANDARD_24.label": ("Vienna Standard 24", "Wien Standard 24"),
    "scenario.VIENNA_STANDARD_24.help": (
        "The published reference: 24 customers, 108 totes and four vehicles of 30 totes. "
        "A balanced starting point with 12 totes of spare capacity.",
        "Veröffentlichte Referenz: 24 Kunden, 108 Totes und vier Fahrzeuge mit je 30 Totes. "
        "Ausgewogener Einstieg mit 12 Totes Reserve.",
    ),
    "scenario.VIENNA_TIGHT_24.label": ("Vienna Tight Capacity 24", "Wien Knappe Kapazität 24"),
    "scenario.VIENNA_TIGHT_24.help": (
        "Same 24 orders and locations, but only 28 totes per vehicle. Just four totes of "
        "fleet reserve: unsplit order packing becomes the main challenge.",
        "Dieselben 24 Bestellungen und Standorte, aber nur 28 Totes je Fahrzeug. Die Flotte "
        "hat nur vier Totes Reserve: Die Verteilung ungeteilter Bestellungen steht im Mittelpunkt.",
    ),
    "scenario.VIENNA_WIDE_24.label": ("Vienna Wide Geography 24", "Wien Weite Wege 24"),
    "scenario.VIENNA_WIDE_24.help": (
        "Same demand and fleet as Standard 24, with stops spread farther across Vienna. "
        "Longer depot legs make geographic grouping more consequential.",
        "Gleicher Bedarf und gleiche Flotte wie bei Standard 24, mit weiter verteilten Stopps "
        "in Wien. Längere Depotfahrten erhöhen die Bedeutung geografischer Gruppierung.",
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
    "ux.custom.advanced": ("Location generation settings", "Einstellungen zur Standortgenerierung"),
    "ux.seed": ("Location seed", "Startwert für Standorte"),
    "ux.detour": ("Distance detour factor", "Umwegfaktor für Distanzen"),
    "ux.generate": ("Generate scenario", "Szenario generieren"),
    "ux.custom.changed": (
        "Your inputs have changed. Generate this scenario before running the comparison.",
        "Ihre Eingaben wurden geändert. Generieren Sie das Szenario vor dem Vergleich neu.",
    ),
    "ux.custom.ready": (
        "Scenario generated. Review the map and demand below, then run the comparison.",
        "Szenario generiert. Prüfen Sie Karte und Bedarf und starten Sie anschließend den Vergleich.",
    ),
    "ux.check.order": (
        "Check 1 · Largest order / vehicle capacity",
        "Prüfung 1 · Größte Bestellung / Fahrzeugkapazität",
    ),
    "ux.check.fleet": (
        "Check 2 · Total demand / fleet capacity",
        "Prüfung 2 · Gesamtbedarf / Flottenkapazität",
    ),
    "ux.check.spare": ("Spare capacity (totes)", "Freie Kapazität (Totes)"),
    "ux.check.min": (
        "Check 3 · Minimum vehicles by demand",
        "Prüfung 3 · Mindestfahrzeuge nach Bedarf",
    ),
    "ux.check.min.help": (
        "ceil(total demand / vehicle capacity). An informational lower bound, not a proof "
        "that all unsplit orders can be packed.",
        "Aufgerundeter Quotient aus Gesamtbedarf und Fahrzeugkapazität. Informative "
        "Untergrenze, kein Nachweis einer passenden Verteilung ungeteilter Bestellungen.",
    ),
    "ux.check.oversize": (
        "An order exceeds one vehicle's capacity. Reduce that order or increase capacity.",
        "Eine Bestellung überschreitet die Fahrzeugkapazität. Bestellbedarf reduzieren oder "
        "Kapazität erhöhen.",
    ),
    "ux.check.overflow": (
        "Total demand exceeds the fleet's capacity. Add vehicles, increase capacity or reduce demand.",
        "Der Gesamtbedarf überschreitet die Flottenkapazität. Fahrzeuge oder Kapazität ergänzen "
        "oder den Bedarf reduzieren.",
    ),
    "ux.check.invalid": (
        "Enter a positive whole number of totes for every customer.",
        "Für jeden Kunden eine positive ganze Anzahl Totes eingeben.",
    ),
    "ux.check.packing": (
        "Checks 1 and 2 are necessary, but unsplit orders may still not pack into the available "
        "vehicles. The search tests route feasibility.",
        "Prüfungen 1 und 2 sind notwendig. Ungeteilte Bestellungen lassen sich dennoch "
        "eventuell nicht auf die verfügbaren Fahrzeuge verteilen. Die Suche prüft die Tourenzulässigkeit.",
    ),
    "ux.preview": ("Delivery area", "Liefergebiet"),
    "ux.preview.summary": (
        "{n} customers · {demand} totes · {vans} vehicles × {capacity} totes",
        "{n} Kunden · {demand} Totes · {vans} Fahrzeuge × {capacity} Totes",
    ),
    "ux.run": ("Run comparison", "Vergleich starten"),
    "ux.settings": ("Search settings", "Sucheinstellungen"),
    "ux.seconds": ("OR-Tools search limit (seconds)", "OR-Tools-Suchlimit (Sekunden)"),
    "ux.stage.load": ("Loading scenario", "Szenario wird geladen"),
    "ux.stage.baseline": (
        "Building nearest-neighbour baseline",
        "Nächster-Nachbar-Baseline wird erstellt",
    ),
    "ux.stage.optimise": (
        "Searching for optimized solution with OR-Tools · Up to {n} seconds",
        "Suche nach optimierter Lösung mit OR-Tools · Bis zu {n} Sekunden",
    ),
    "ux.stage.reconcile": (
        "Validating route assignments, capacity and distances",
        "Tourenzuordnung, Kapazität und Distanzen werden geprüft",
    ),
    "ux.stage.prepare": ("Preparing comparison", "Vergleich wird vorbereitet"),
    "ux.stage.done": ("Comparison ready", "Vergleich bereit"),
    "ux.stage.failed": (
        "Comparison could not be completed",
        "Vergleich konnte nicht abgeschlossen werden",
    ),
    "ux.plan.title": ("Plan", "Plan"),
    "ux.plan.subtitle": (
        "Nearest-neighbour baseline and optimized solution for the same scenario.",
        "Nächster-Nachbar-Baseline und optimierte Lösung für dasselbe Szenario.",
    ),
    "ux.plan.summary": ("Comparison summary", "Vergleichsübersicht"),
    "ux.plan.empty": (
        "Choose a scenario and run the comparison first.",
        "Wählen Sie ein Szenario und starten Sie zuerst den Vergleich.",
    ),
    "ux.baseline": ("Nearest-neighbour baseline", "Nächster-Nachbar-Baseline"),
    "ux.optimised": ("Optimized solution (OR-Tools)", "Optimierte Lösung (OR-Tools)"),
    "ux.optimised.short": ("Optimized solution", "Optimierte Lösung"),
    "ux.kpi.baseline": ("Baseline distance", "Baseline-Distanz"),
    "ux.kpi.optimised": ("Optimized distance", "Optimierte Distanz"),
    "ux.kpi.saving": ("Distance reduction", "Distanzreduktion"),
    "ux.kpi.served": ("Customers served", "Bediente Kunden"),
    "ux.proof.served": ("Customers served", "Bediente Kunden"),
    "ux.plan.ineligible": (
        "A distance reduction is shown only when both plans are complete and comparison-eligible. "
        "A partial baseline distance is not a complete comparison distance.",
        "Eine Distanzreduktion wird nur für zwei vollständige, vergleichbare Pläne angezeigt. "
        "Die Teildistanz einer unvollständigen Baseline ist keine Vergleichsdistanz.",
    ),
    "ux.plan.partial": ("Partial constructed distance: {km}", "Konstruierte Teildistanz: {km}"),
    "ux.plan.unserved": ("Unserved customers: {ids}", "Nicht bediente Kunden: {ids}"),
    "ux.plan.routes": ("Vehicle routes", "Fahrzeugtouren"),
    "ux.plan.pick": ("Displayed plan", "Angezeigter Plan"),
    "ux.plan.table": ("Vehicle routes", "Fahrzeugtouren"),
    "ux.plan.total": ("Total distance: {km}", "Gesamtdistanz: {km}"),
    "ux.plan.reduction": ("Distance reduction: {value}", "Distanzreduktion: {value}"),
    "ux.plan.details": ("Stop-by-stop details", "Details je Stopp"),
    "ux.plan.exports": ("Download for review", "Zur Prüfung herunterladen"),
    "ux.plan.excel": (
        "JSON and CSV ZIP contain the recorded run data. A structured Excel review template "
        "is planned for a later iteration.",
        "JSON und CSV-ZIP enthalten die gespeicherten Laufdaten. Eine strukturierte "
        "Excel-Prüfvorlage ist für eine spätere Version vorgesehen.",
    ),
    "ux.plan.audit": ("Model checks", "Modellprüfungen"),
    "ux.plan.audit.failed": (
        "Some checks did not pass. Review model validation before using this plan.",
        "Einige Prüfungen sind fehlgeschlagen. Prüfen Sie die Modellvalidierung vor der "
        "Verwendung dieses Plans.",
    ),
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
        "From spreadsheet MIP to routing search",
        "Von der Tabellenkalkulations-MIP zur Tourensuche",
    ),
    "ux.method.opensolver": (
        "An earlier version of this last-mile CVRP was solved as a spreadsheet mixed-integer "
        "programme using the OpenSolver add-in for Excel. LastMile Lab keeps that formulation "
        "as documentation. The production application now obtains operational routes from "
        "Google OR-Tools RoutingModel, which constructs a feasible assignment and stop sequence "
        "and then improves it under a search limit. It does not solve the documented "
        "three-index MILP with a MIP solver.",
        "Eine frühere Version dieses Last-Mile-CVRP wurde als gemischt-ganzzahliges Programm "
        "in einer Tabellenkalkulation mit dem OpenSolver-Add-in für Excel gelöst. LastMile Lab "
        "bewahrt diese Formulierung als Dokumentation. Die produktive Anwendung ermittelt "
        "betriebliche Touren jetzt mit dem Google-OR-Tools-RoutingModel, das eine zulässige "
        "Zuordnung und Stoppfolge konstruiert und sie innerhalb eines Suchlimits verbessert. "
        "Es löst die dokumentierte Drei-Index-MILP nicht mit einem MIP-Solver.",
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
        "The common start and return location for the vehicle routes.",
        "Der gemeinsame Start- und Rückkehrort der Fahrzeugtouren.",
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
}

WORKFLOW_STRINGS = {
    language: {key: pair[index] for key, pair in COPY.items()}
    for index, language in enumerate(("en", "de"))
}
