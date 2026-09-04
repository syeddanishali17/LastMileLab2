# Frontend UI/UX review brief

## Product context

LastMile Lab is a recruiter-facing portfolio application for a static capacitated
vehicle routing problem (CVRP). It compares a deterministic nearest-neighbour
baseline with a time-limited Google OR-Tools solution.

The interface should feel like professional operations decision-support software.
It should remain understandable to a non-specialist without becoming conversational
or imprecise.

## Files to review

- `frontend/components.py`: design tokens, CSS, shared layout, header, navigation,
  status indicators, language control, and vehicle cards
- `frontend/i18n.py`: all English and German interface copy
- `frontend/Home.py`: landing-page information architecture
- `frontend/pages/1_Dispatch_Setup.py`: scenario selection, feasibility pre-checks,
  and solution controls
- `frontend/pages/2_Route_Plan.py`: route and vehicle review
- `frontend/pages/3_Baseline_vs_Optimised.py`: solution comparison
- `frontend/pages/4_Model_Inspector.py`: route reconstruction and model validation
- `frontend/pages/5_Learning_Lab.py`: six-customer worked example
- `.streamlit/config.toml`: native Streamlit colour configuration

## Current design direction

- Cool neutral canvas: `#F4F7FA`
- White, lightly translucent surfaces
- Primary navy: `#16324F`
- Accent teal: `#0F766E`
- Primary text: `#172B3A`
- Muted text: `#526477`
- Borders: `#D7E0E8`
- Inter typeface with a restrained enterprise hierarchy
- Compact globe menu for English and German
- No em dashes in user-facing text
- Sentence-case labels and headings

## Terminology

- Use **scenario** for the selected input data and operating assumptions.
- Use **planning service** for the FastAPI backend.
- Use **nearest-neighbour baseline** for the transparent greedy method.
- Use **optimised solution** or **OR-Tools solution** for the search result.
- Use **feasible solution** when all customers are served and capacity is respected.
- Use **vehicle** in general CVRP language; use **van** only when referring to the
  fictional operating fleet.
- Define **tote** as a standard reusable delivery container.
- Do not imply that a time-limited OR-Tools result is globally optimal.

## Constraints that must remain unchanged

- The Streamlit frontend displays FastAPI results and must not recompute solutions.
- LEARNING_6 nearest neighbour is incomplete: C4 is unserved and 27.000 km is only
  a partial constructed distance.
- The named reference packing is 34.000 km.
- The independently verified shortest LEARNING_6 solution is 31.000 km.
- A timeout or missing complete assignment is `no_solution_found`, not `infeasible`.
- Schematic connections are not road geometry or live navigation.

## Suggested external-review prompt

Review this Streamlit interface as an enterprise product designer with familiarity
in logistics and vehicle routing. Evaluate information architecture, typography,
spacing, interaction hierarchy, terminology, accessibility, bilingual behaviour,
and recruiter comprehension. Recommend specific changes that preserve the technical
constraints above. Flag wording that is too informal, too academic, misleading, or
inconsistent. Do not alter solver behaviour, API contracts, or KPI definitions.
