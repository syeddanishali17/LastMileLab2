# Recruiter journey: research and implementation map

## Applied practices

- Dispatch workflow: keep demand, vehicle capacity, resulting routes and review together. [Onfleet's operating workflow](https://support.onfleet.com/hc/en-us/articles/360023910351-Route-Optimization-Operating) provides a real dispatch reference. This project intentionally models a smaller static morning wave, without traffic, time windows or driver assignment.
- One primary action at each stage: choose a scenario, generate a valid custom scenario when needed, then run comparison. [GOV.UK buttons](https://design-system.service.gov.uk/components/button/) recommends avoiding competing main actions.
- Put advanced settings and audit detail behind secondary controls. [Nielsen Norman Group on progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/) supports keeping the initial view focused.
- Explain VRP through the delivery task, then introduce capacity as the extra rule. Keep the unsplit-order packing caveat beside the live meters: aggregate capacity does not guarantee a feasible packing. [OR-Tools capacity constraints](https://developers.google.com/optimization/routing/cvrp) explains this distinction.
- Compare both maps using the same geographic camera, with outcome metrics above and route tables below. On narrow screens, offer a native plan toggle. This is a project design decision to retain geographic context without squeezing two maps into a phone width.
- Use real request stages and a stated 1/5/10-second search limit, without invented progress percentages. [Streamlit st.status](https://docs.streamlit.io/1.39.0/develop/api-reference/status/st.status) provides the running, completed and failed states.
- Keep English/Deutsch navigation visible and all new copy paired. Allow text to wrap, including longer German labels. [W3C internationalization quick tips](https://www.w3.org/International/quicktips/) recommends visible navigation in the target language.
- Stay within Streamlit 1.44: explicit st.navigation registry, native controls, st.status, Plotly, keyed containers and a small CSS breakpoint. No custom frontend runtime or heavy animation.

## File and page map

| Surface | File | Flow |
|---|---|---|
| Entry/router | frontend/Home.py | Register three primary pages and two secondary pages; collapsed sidebar |
| Overview | frontend/pages/0_Overview.py | Business context → VRP → capacity → comparison → published proof → Scenarios |
| Scenarios | frontend/pages/1_Dispatch_Setup.py | Exactly three curated presets or guided demand editor → capacity feedback → generate → run pair |
| Plan | frontend/pages/3_Baseline_vs_Optimised.py | API KPIs + paired maps + van tables + JSON/CSV exports; automatic arrival after the pair |
| Methodology | frontend/pages/6_Methodology.py | Brief assumptions, methods and validation link |
| Model validation | frontend/pages/4_Model_Inspector.py | Secondary inspection with stored run type and search limit |

Shared components, maps and translations retain the navy/teal design. The old standalone Route Plan and Learning Lab pages were removed from `frontend/pages/`. Teaching fixtures, mathematical documentation and regression tests remain available in the repository.

## Scenario and API changes

Vienna Standard 24 and its published snapshot are unchanged. Tight Capacity 24 holds demand and locations fixed while reducing each van from 30 to 28 totes. Wide Geography 24 holds demand and fleet fixed while distributing stops farther across Vienna.

Custom locations still use the existing seeded Vienna generator. Optional customer_demands supplies one positive integer per customer. Scenario identity hashes the seed, counts, capacity, detour factor, zone weights and ordered demand vector. Planning endpoints pass the stored dataset to the existing planners, which apply the same prechecks and algorithms. API run summaries expose the recorded run type and solver time limit.

Frontend live meters describe draft inputs only. Comparison eligibility, run KPI formulas, OR-Tools constraints and exported data formats are unchanged. Published Overview metrics are labelled as a historical example, separate from live Plan results.
