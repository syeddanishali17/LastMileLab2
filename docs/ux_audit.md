# Frontend product design audit and improvement guide

## Outcome

The frontend now has one navigation system and a coherent three-stage journey:
understand the problem, configure a scenario, then inspect both returned plans.
The final implementation pass was limited to P1 map framing and active-navigation
fixes found during the browser audit. No additional solver or API contract edits
were made during this redesign pass. Earlier scenario/API work remains in the
working tree, as do unrelated local changes.

## Findings and decisions

| Previous problem | Impact | Implemented decision |
|---|---|---|
| Top links duplicated sidebar links; current page unclear | Users lose their location | Native grouped sidebar only; bold active row, left bar and textual marker; current page named above heading |
| Uneven educational cards competed with the project story | Recruiter must decode the interface before understanding CVRP | Plain-language VRP, capacity and comparison narrative alongside a restrained route diagram |
| Published and live results could be confused | Weakens credibility | Overview explicitly labels the published benchmark; Plan displays API responses only |
| Presets hidden in a dropdown | Alternatives and planning tensions invisible | Three native radio choices with persistent summaries |
| Inputs and map separated vertically | Extra scrolling and context switching | Two-column scenario workspace, naturally stacked on small screens |
| Generate and Run competed as primary actions | Unclear next step | Generate is secondary; Run comparison is primary and disabled until inputs have a matching generated scenario |
| Search limit hidden and could initialise at one second | Unexpected solver behaviour | Visible 1/5/10 radio, five-second default, saved canonical setting |
| Exports fetched during every page rerun | Avoidable delay and backend traffic | Explicit preparation per run; cached bytes; downloads do not rerun the page |
| One-off HTTP clients | Repeated connection setup during a multi-request workflow | Reused HTTP client; existing backend URL configuration retained |
| Large demand bubbles and heavy route outlines | Stops obscure geography and each other | Small neutral input markers; slim route lines and numbered vehicle-colour stops |
| Fixed camera clipped outer stops | Incorrect impression of route coverage | Conservative dataset-derived camera shared by both plans, including narrow maps |
| Mixed numeric alignment | Difficult scanning and comparison | Dispatch and stop tables align quantities right, including unit-bearing strings; tabular numbers and light row separators |
| Vehicle identity disconnected from details | Hard to match map and table | Stable V01-V04 colours in routes, compact legend and vehicle cells |

## Research translated into this product

[Onfleet Route Plans](https://support.onfleet.com/hc/en-us/articles/35085663098516-Route-Plans)
ties route colour to task pins and exposes route state and task counts. Apply that
identity consistency, not the full operational feature set. This portfolio does
not have live drivers, tasks changing state or dispatch assignment.

[Routific's route workflow](https://help.routific.com/en/articles/46-draw-your-route)
allows selecting the same route from its map or timeline. The transferable idea
is keeping route geography and route detail together. Drag-to-reoptimise is not
appropriate here: it would require new interaction and planning semantics.

[IBM Carbon's data palettes](https://carbondesignsystem.com/data-visualization/color-palettes/)
separate categorical data from alerts. This implementation uses a Carbon-inspired
palette, not a claim to reproduce a competitor's branding. V02 uses a darker blue
than Carbon's default cyan to improve contrast for white stop numbers.

| Role | Colour |
|---|---|
| Chrome and primary action | Navy #16324F |
| Interface accent | Teal #0F766E |
| Canvas / surface | #F4F7FA / white |
| Text / secondary text | #172B3A / #526477 |
| V01 / V02 | #6929C4 / #0072C3 |
| V03 / V04 | #005D5D / #9F1853 |

Vehicle IDs, stop numbers, route sequences and status words carry meaning in
addition to colour. This is not a certification of WCAG conformance.

[Progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/)
informs advanced location settings and optional model details.
[GOV.UK button guidance](https://design-system.service.gov.uk/components/button/)
informs the single primary action. Native Streamlit controls are preferable to
fragile clickable HTML cards. No Figma file or external design artifact was edited;
design decisions were checked against the running application.

## What belongs on each page

- **Overview:** the delivery decision, CVRP constraints, method comparison,
  published Vienna proof, one next action. The SVG draws once and respects reduced
  motion; it explains closed routes and is not a simulation of solving.
- **Scenarios:** demand, homogeneous fleet capacity, three meaningful presets,
  editable custom orders, input checks, map, search limit and Run comparison.
  Check 3 is a lower bound, not a packing feasibility guarantee.
- **Plan:** both statuses, eligible objectives, eligible saving, coverage,
  routes, vehicle details, optional stop detail, exports and audit links.
  Incomplete nearest-neighbour distance remains partial, not a full objective.
- **Methodology:** assumptions, heuristic limitations, estimated distances and
  interpretation of no_solution_found. No solution found does not mean infeasible.
- **Model validation:** technical reconstruction and actual stored search metadata.
  LEARNING_6 remains outside the primary journey and normal scenario selector.

## Map layout choice

Desktop uses side-by-side baseline and OR-Tools maps with the same initial camera.
Below the 760 px CSS breakpoint a native plan selector and one visible map replace
the pair. The compact external legend avoids a tall Plotly legend strip.
Existing OpenStreetMap tiles remain; no new mapping service or token was added.
Connections are schematic, estimated-distance planning, not roads or navigation.

## Verification record

- Existing .venv used for API and Streamlit. Port 8000 was free when restarting;
  the old local Streamlit process was restarted for configuration changes.
- Browser journey: Overview, Standard 24, five-second comparison, Plan,
  prepare baseline exports, Methodology, Model validation, German switch.
- Live API result: 24/24, baseline 122.394 km, OR-Tools 97.193 km, 20.6%.
  This particular run matched the benchmark; future runs need not do so.
- API logs: baseline request about 68 ms; optimiser about 5.1 s; result reads
  followed immediately. Export requests appeared only after Prepare was clicked.
- German Plan at a narrow viewport: stacked KPIs, wrapped labels, native map
  selector functional, no document horizontal overflow; all outer stops visible.
- Regression suite: 88 existing tests passed, plus three new presentation tests
  for lazy export, camera/palette and numeric/vehicle table markup. Ruff passed.
- Published numbers and mathematical expectations were not changed.

## Remaining limits and next priorities

These are follow-up improvements, not hidden claims of completion:

1. Streamlit has no native viewport-aware Python rendering. CSS hides the unused
   map layout but its figures are still constructed. OSM tiles load asynchronously;
   a first render can briefly be blank. Cameras start equal but do not synchronise
   after manual panning. A future explicit map-layout selector could reduce this
   rendering cost, at the cost of losing automatic mobile presentation.
2. Native sidebar starts collapsed as requested. The breadcrumb preserves location,
   but language switching requires opening the sidebar. Active styling relies on
   stable test IDs and registered URL suffixes, not generated CSS class names.
3. Model validation is still a dense technical surface. Its native dataframes
   retain built-in English toolbar labels and lack the dispatch table's complete
   alignment control. Move more reconstruction tables into labelled expanders in
   a future pass; do not promote them into the recruiter journey.
4. Overview remains relatively long on smaller laptops. A later content-only pass
   could shorten the introduction and combine repeated scope notes. Do not remove
   the historical-result label or feasibility caveats to save space.
5. The checked-in published screenshot has the old palette and clipped right-edge
   legend content. It is a historical figure, not evidence of the current UI.
   Regenerate presentation screenshots separately without changing its recorded
   numbers. Capture fresh deployed UI screenshots before sending recruiters a URL.
6. Native wide tables scroll within their containers on phones. Custom data-editor
   keyboard and screen-reader testing remains less thorough than the main journey.
   Full assistive-technology and colour-vision testing is still outstanding.
7. No user study was performed. Validate comprehension with a recruiter: ask what
   is being optimised, what the capacity rule is, whether the result is proven
   optimal, and which action they would take next. Measure task completion before
   adding richer animations or more controls.

## Main files

Frontend entry, Overview, Scenarios and Plan; components.py, maps.py, display.py,
workflow_copy.py, api_client.py; .streamlit/config.toml; README; this audit and
tests/test_frontend_presentation.py. Earlier methodology, state, scenario builder
and backend changes are documented in ux_rewrite.md.
