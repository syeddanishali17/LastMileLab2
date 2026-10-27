"""Design layer: typography, motion, loading states and the newer visual components.

Appended after the base theme in `components.THEME_CSS`, so these rules win ties.
Everything animated here honours `prefers-reduced-motion` at the end of the sheet.
"""

DESIGN_LAYER_CSS = r"""
/* ---------- Typography ---------- */
.lm-hero h1, .lm-inner h1, .lm-section h2, .lm-cvrp-heading, .lm-about-title,
.lm-plan-heading :is(h2, h3), .lm-concept h3, .lm-card h3, .lm-result-title,
.lm-console-title, .lm-insight h3, .stApp:has(.lm-scenarios-flag) .lm-section h2 {
  font-family: var(--lm-display) !important;
  letter-spacing: -0.02em;
}
.lm-kpi .lm-kpi-value, .lm-plan-distance, .lm-preview-stats dd, .lm-result-num,
.lm-result-km, .lm-console-clock, .lm-stat-value {
  font-family: var(--lm-mono) !important;
  font-feature-settings: "tnum" 1, "zero" 1;
  letter-spacing: -0.03em;
}

/* ---------- Canvas: a faint map grid behind every page ---------- */
[data-testid="stAppViewContainer"], .stApp {
  background:
    radial-gradient(circle at 1px 1px, rgba(12, 20, 36, 0.055) 1px, transparent 0) 0 0 / 24px 24px,
    var(--lm-canvas);
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background:
    radial-gradient(120% 40% at 0% 0%, rgba(99, 102, 241, 0.22), transparent 60%),
    radial-gradient(90% 30% at 100% 100%, rgba(190, 242, 100, 0.06), transparent 70%),
    var(--lm-sidebar);
}
[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebarNav"] a[aria-current="page"],
.stApp:has(.lm-overview-flag) [data-testid="stSidebarNavLink"][href$="/"],
.stApp:has(.lm-scenarios-flag) [data-testid="stSidebarNavLink"][href*="/scenarios"],
.stApp:has(.lm-plan-flag) [data-testid="stSidebarNavLink"][href*="/plan"],
.stApp:has(.lm-method-flag) [data-testid="stSidebarNavLink"][href*="/methodology"],
.stApp:has(.lm-inspect-flag) [data-testid="stSidebarNavLink"][href*="/validation"] {
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.34), rgba(99, 102, 241, 0.08)) !important;
}
/* Collapse control: Streamlit only reveals it on hover, so keep it visible and obvious. */
[data-testid="stSidebarCollapseButton"] {
  display: flex !important;
  align-items: center;
  visibility: visible !important;
  opacity: 1 !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button {
  width: 30px !important;
  height: 30px !important;
  border-radius: 9px !important;
  color: #C7D2FE !important;
  background: rgba(255, 255, 255, 0.06) !important;
  border: 1px solid rgba(165, 180, 252, 0.22) !important;
  transition: background 0.15s ease, color 0.15s ease !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {
  color: #FFFFFF !important;
  background: rgba(99, 102, 241, 0.45) !important;
}
[data-testid="stSidebarCollapseButton"] button:focus-visible,
[data-testid="stSidebarCollapsedControl"] button:focus-visible {
  outline: 3px solid var(--lm-focus) !important;
  outline-offset: 2px !important;
}
/* Reopen control while collapsed: a floating dark pill with the brand mark. */
[data-testid="stSidebarCollapsedControl"] {
  z-index: 1000050 !important;
  align-items: center;
  gap: 8px;
  padding: 6px 8px 6px 10px !important;
  border-radius: 14px;
  background: var(--lm-sidebar);
  border: 1px solid rgba(165, 180, 252, 0.22);
  box-shadow: 0 12px 28px -14px rgba(10, 16, 32, 0.7);
}
[data-testid="stSidebarCollapsedControl"] img { width: 24px !important; height: 24px !important; }
.stApp:has(section[data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stSidebarCollapsedControl"] {
  display: none !important;
}
.lm-api-status-up .lm-api-dot {
  background: #4ADE80;
  box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.6);
  animation: lm-ping 2.4s ease-out infinite;
}
@keyframes lm-ping {
  0% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.55); }
  70%, 100% { box-shadow: 0 0 0 7px rgba(74, 222, 128, 0); }
}

/* ---------- Loading: a route line runs along the top while Streamlit works ---------- */
.stApp::before {
  content: "";
  position: fixed;
  inset: 0 0 auto 0;
  height: 3px;
  z-index: 1000100;
  pointer-events: none;
  opacity: 0;
  background: linear-gradient(90deg, transparent 0%, #6366F1 30%, #BEF264 50%, #6366F1 70%, transparent 100%);
  background-size: 50% 100%;
  background-repeat: no-repeat;
  transition: opacity 0.2s ease;
}
.stApp:has([data-testid="stStatusWidget"] svg, [data-testid="stStatusWidget"] img,
  .lm-console.is-running)::before {
  opacity: 1;
  animation: lm-topbar 1.15s cubic-bezier(0.45, 0, 0.25, 1) infinite;
}
@keyframes lm-topbar {
  from { background-position: -60% 0; }
  to { background-position: 160% 0; }
}
/* Re-running content stays legible: a soft fade, never a grey-out. */
[data-testid="stElementContainer"][data-stale="true"] {
  opacity: 0.6 !important;
  filter: saturate(0.6);
  transition: opacity 0.3s ease 0.45s, filter 0.3s ease 0.45s !important;
}
/* Skeleton shimmer while a Plotly map or chart is still mounting. */
.stPlotlyChart, [data-testid="stPlotlyChart"] {
  border-radius: 12px;
  background:
    linear-gradient(100deg, transparent 30%, rgba(255, 255, 255, 0.7) 50%, transparent 70%) 0 0 / 200% 100%,
    var(--lm-surface-soft);
  animation: lm-shimmer 1.4s linear infinite;
  min-height: 120px;
}
.stPlotlyChart:has(.main-svg), [data-testid="stPlotlyChart"]:has(.main-svg) {
  animation: none;
  background: transparent;
}
@keyframes lm-shimmer {
  from { background-position: 150% 0, 0 0; }
  to { background-position: -50% 0, 0 0; }
}
[data-testid="stSpinner"] i, .stSpinner i {
  border-color: rgba(99, 102, 241, 0.2) !important;
  border-top-color: var(--lm-primary) !important;
}

/* ---------- Page entrance ---------- */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :is(
  [data-testid="stElementContainer"], [data-testid="stVerticalBlockBorderWrapper"],
  [data-testid="stHorizontalBlock"], .stElementContainer, div[class*="st-key-"]) {
  animation: lm-rise 0.55s cubic-bezier(0.2, 0.7, 0.2, 1) both;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(2) { animation-delay: 40ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(3) { animation-delay: 80ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(4) { animation-delay: 120ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(5) { animation-delay: 160ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > :nth-child(n+6) { animation-delay: 200ms; }
@keyframes lm-rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: none; }
}

/* ---------- Hero ---------- */
.lm-hero {
  background: var(--lm-glow), linear-gradient(160deg, #0B1226 0%, #101B3B 55%, #1E1B4B 100%);
  border: 1px solid rgba(165, 180, 252, 0.18);
  border-radius: 20px;
  padding: 40px 44px 34px;
  box-shadow: 0 30px 60px -30px rgba(30, 27, 75, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.06);
  isolation: isolate;
}
.lm-hero-grid {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  opacity: 0.9;
  pointer-events: none;
  -webkit-mask-image: linear-gradient(90deg, transparent 0%, transparent 48%, #000 72%, #000 100%);
  mask-image: linear-gradient(90deg, transparent 0%, transparent 48%, #000 72%, #000 100%);
}
.lm-hero-grid .lm-hg-street { stroke: rgba(148, 163, 214, 0.10); stroke-width: 1; fill: none; }
.lm-hero-grid .lm-hg-route {
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 6 10;
  animation: lm-flow 2.8s linear infinite;
  opacity: 0.75;
}
.lm-hero-grid .lm-hg-route.r2 { animation-duration: 3.4s; }
.lm-hero-grid .lm-hg-route.r3 { animation-duration: 3.1s; }
.lm-hero-grid .lm-hg-stop { fill: #0B1226; stroke-width: 2; }
.lm-hero-grid .lm-hg-depot { fill: #BEF264; }
.lm-hero-grid .lm-hg-depot-ring {
  fill: none; stroke: #BEF264; stroke-width: 1.5;
  transform-box: fill-box; transform-origin: center;
  animation: lm-ring 2.6s ease-out infinite;
}
@keyframes lm-flow { to { stroke-dashoffset: -64; } }
@keyframes lm-ring {
  from { transform: scale(0.6); opacity: 0.9; }
  to { transform: scale(2.6); opacity: 0; }
}
.lm-hero-heading, .lm-hero-copy { z-index: 2; }
/* The animated street grid replaces the small corner mark on wide screens. */
.lm-hero { grid-template-columns: minmax(0, 1fr); }
.lm-hero .lm-route-motif { display: none; }
.lm-hero h1 {
  font-size: clamp(34px, 3.4vw, 50px);
  line-height: 1.04;
  letter-spacing: -0.035em;
  max-width: 17ch;
  background: linear-gradient(180deg, #FFFFFF 30%, #C7D2FE 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.lm-hero .lm-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px 5px 10px;
  border-radius: 999px;
  background: rgba(190, 242, 100, 0.08);
  border: 1px solid rgba(190, 242, 100, 0.28);
  color: #D9F99D;
  margin-bottom: 18px;
}
.lm-hero .lm-kicker::before {
  content: "";
  width: 7px; height: 7px; border-radius: 50%;
  background: #BEF264;
  box-shadow: 0 0 10px #BEF264;
}
.lm-hero p { color: #C9D2EC; max-width: min(62ch, 62%) !important; }
@media (max-width: 900px) {
  .lm-hero p { max-width: none !important; }
  .lm-hero-grid { opacity: 0.35; }
}
.lm-hero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 20px 0 0 !important;
  padding: 0;
  list-style: none;
}
.lm-hero-chips li {
  margin: 0;
  padding: 4px 11px;
  border-radius: 8px;
  font-family: var(--lm-mono);
  font-size: 12px;
  font-weight: 500;
  color: #C7D2FE;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(165, 180, 252, 0.2);
}

/* ---------- Inner page header + workflow stepper ---------- */
.lm-inner h1 { color: var(--lm-ink); letter-spacing: -0.03em; }
.lm-stepper {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin: 0 0 14px;
  padding: 0;
  list-style: none;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--lm-muted);
}
.lm-stepper li { display: inline-flex; align-items: center; gap: 7px; margin: 0; }
.lm-stepper li + li::before {
  content: "";
  width: 22px; height: 2px; margin-right: 6px; border-radius: 2px;
  background: repeating-linear-gradient(90deg, var(--lm-border-strong) 0 4px, transparent 4px 7px);
}
.lm-stepper .lm-step-num {
  display: inline-grid; place-items: center;
  width: 20px; height: 20px; border-radius: 50%;
  font-family: var(--lm-mono); font-size: 11px;
  border: 1.5px solid var(--lm-border-strong);
  background: var(--lm-surface);
}
.lm-stepper .is-done .lm-step-num {
  background: var(--lm-primary-soft); border-color: var(--lm-primary); color: var(--lm-primary);
}
.lm-stepper .is-current { color: var(--lm-ink); }
.lm-stepper .is-current .lm-step-num {
  background: var(--lm-primary); border-color: var(--lm-primary); color: #FFFFFF;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.16);
}

/* ---------- Surfaces ---------- */
.lm-card, .lm-kpi, .lm-feas-card, .lm-empty {
  border-radius: 14px;
  box-shadow: var(--lm-shadow);
}
.lm-kpi {
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.lm-kpi::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 3px;
  background: linear-gradient(90deg, var(--lm-primary), #A5B4FC);
  opacity: 0.85;
}
.lm-kpi:hover { transform: translateY(-2px); box-shadow: 0 14px 30px -18px rgba(30, 27, 75, 0.35); }
.st-key-scenario_presets [data-baseweb="radio"] {
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}
.st-key-scenario_presets [data-baseweb="radio"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px -16px rgba(30, 27, 75, 0.4);
}
.st-key-scenario_presets [data-baseweb="radio"]:has(input:checked) {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.14), 0 10px 24px -16px rgba(30, 27, 75, 0.45);
}

/* ---------- Buttons ---------- */
.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"],
.stApp:has(.lm-overview-flag) .st-key-overview-cta button {
  background: linear-gradient(180deg, #6366F1 0%, #4F46E5 100%) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.18), 0 6px 16px -8px rgba(79, 70, 229, 0.7) !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease !important;
}
.stButton > button[kind="primary"]:not(:disabled):hover,
[data-testid="stBaseButton-primary"]:not(:disabled):hover,
.stApp:has(.lm-overview-flag) .st-key-overview-cta button:hover {
  filter: brightness(1.06);
  transform: translateY(-1px) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 12px 24px -10px rgba(79, 70, 229, 0.75) !important;
}
.stApp:has(.lm-overview-flag) .st-key-overview-cta button p::after { content: "  \2192"; }

/* ---------- Dispatch console (run progress) ---------- */
@property --lm-tick { syntax: "<integer>"; inherits: false; initial-value: 0; }
.lm-console {
  position: relative;
  overflow: hidden;
  margin: 8px 0 20px;
  padding: 22px 24px 20px;
  border-radius: 18px;
  color: #E2E8F8;
  background: var(--lm-glow), linear-gradient(160deg, #0B1226 0%, #121C3D 100%);
  border: 1px solid rgba(165, 180, 252, 0.2);
  box-shadow: 0 24px 50px -28px rgba(30, 27, 75, 0.6);
  animation: lm-console-in 0.45s cubic-bezier(0.2, 0.8, 0.2, 1) both;
}
.lm-console::after {
  /* A slow scan line sweeping across the panel while work is in progress. */
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(100deg, transparent 40%, rgba(165, 180, 252, 0.07) 50%, transparent 60%);
  background-size: 250% 100%;
  opacity: 0;
}
.lm-console.is-running::after { opacity: 1; animation: lm-scan 2.8s linear infinite; }
@keyframes lm-scan { from { background-position: 150% 0; } to { background-position: -50% 0; } }
@keyframes lm-console-in { from { opacity: 0; transform: translateY(8px) scale(0.99); } to { opacity: 1; transform: none; } }
.lm-console-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.lm-console-heading { display: flex; align-items: center; gap: 12px; }
.lm-console-title { margin: 0 !important; font-size: 18px; font-weight: 600; color: #FFFFFF; }
.lm-console-sub { margin: 2px 0 0 !important; font-size: 13.5px; color: #98A3C2; max-width: none !important; }
.lm-console.is-done .lm-console-sub { color: #D9F99D; font-family: var(--lm-mono); font-size: 13px; }
.lm-console-clock {
  font-family: var(--lm-mono);
  font-size: 13px; color: #D9F99D; padding: 5px 11px; border-radius: 9px;
  border: 1px solid rgba(190, 242, 100, 0.3); background: rgba(190, 242, 100, 0.06);
  white-space: nowrap;
}
.lm-console-clock.is-live { box-shadow: 0 0 0 0 rgba(190, 242, 100, 0.4); animation: lm-glowpulse 1.6s ease-out infinite; }
@keyframes lm-glowpulse { 70%, 100% { box-shadow: 0 0 0 8px rgba(190, 242, 100, 0); } }
/* The registered property does not inherit, so the counter is set on the element. */
.lm-console-elapsed { font-weight: 600; color: #FFFFFF; counter-reset: lm-elapsed var(--lm-tick); }
.lm-console-elapsed::after { content: counter(lm-elapsed); }
.lm-tick-1 .lm-console-elapsed { animation: lm-tick-1 1s linear forwards; }
.lm-tick-5 .lm-console-elapsed { animation: lm-tick-5 5s linear forwards; }
.lm-tick-10 .lm-console-elapsed { animation: lm-tick-10 10s linear forwards; }
@keyframes lm-tick-1 { to { --lm-tick: 1; } }
@keyframes lm-tick-5 { to { --lm-tick: 5; } }
@keyframes lm-tick-10 { to { --lm-tick: 10; } }
.lm-console-check {
  position: relative;
  flex: 0 0 34px; width: 34px; height: 34px; border-radius: 50%;
  background: #BEF264;
  box-shadow: 0 0 0 0 rgba(190, 242, 100, 0.6);
  animation: lm-pop 0.5s cubic-bezier(0.2, 0.9, 0.3, 1.4) both, lm-glowpulse 1.4s ease-out 0.4s 2;
}
.lm-console-check::after {
  content: ""; position: absolute; left: 12px; top: 8px; width: 8px; height: 14px;
  border: solid #0B1226; border-width: 0 3px 3px 0; transform: rotate(45deg);
}
.lm-console-road { position: relative; height: 46px; margin: 18px 6px 12px; }
.lm-road-track, .lm-road-done {
  position: absolute; top: 30px; left: 2%; height: 2px; border-radius: 2px;
}
.lm-road-track {
  right: 2%;
  background: repeating-linear-gradient(90deg, rgba(148, 163, 214, 0.45) 0 5px, transparent 5px 12px);
}
.lm-console.is-running .lm-road-track { animation: lm-road 0.9s linear infinite; }
@keyframes lm-road { to { background-position: -12px 0; } }
.lm-road-done {
  height: 3px; top: 29.5px;
  background: linear-gradient(90deg, #818CF8, #BEF264);
  box-shadow: 0 0 10px rgba(190, 242, 100, 0.45);
  animation: 0.8s cubic-bezier(0.3, 0.7, 0.2, 1) both;
}
.lm-road-depot {
  position: absolute; left: 2%; top: 25px; width: 12px; height: 12px; margin-left: -6px;
  border-radius: 3px; background: #BEF264; box-shadow: 0 0 12px rgba(190, 242, 100, 0.6);
}
.lm-road-stop {
  position: absolute; top: 25px; width: 12px; height: 12px; margin-left: -6px;
  border-radius: 50%; background: #0B1226; border: 2px solid rgba(165, 180, 252, 0.5);
  transition: background 0.3s ease, border-color 0.3s ease;
}
.lm-road-stop.is-reached { border-color: #A5B4FC; background: #1E1B4B; }
.lm-road-stop.is-new { animation: lm-stop-pop 0.6s cubic-bezier(0.2, 0.9, 0.3, 1.5) 0.55s both; }
@keyframes lm-stop-pop {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(190, 242, 100, 0.7); }
  45% { transform: scale(1.5); border-color: #BEF264; }
  100% { transform: scale(1); box-shadow: 0 0 0 10px rgba(190, 242, 100, 0); }
}
.lm-console-van {
  position: absolute; top: 9px; width: 34px; height: 22px;
  transform: translateX(-50%);
  animation: 0.8s cubic-bezier(0.3, 0.7, 0.2, 1) both;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.45));
}
.lm-console.is-running .lm-console-van svg { animation: lm-bob 0.45s ease-in-out infinite alternate; }
.lm-console.is-done .lm-console-van svg { animation: lm-van-park 0.6s ease 0.8s both; }
@keyframes lm-van-park { 50% { transform: translateY(-5px); } }
@keyframes lm-bob { to { transform: translateY(-1.5px); } }
.lm-console-steps {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.lm-console-steps li {
  margin: 0;
  font-size: 12.5px;
  line-height: 1.35;
  color: #7E8AAB;
  padding-top: 10px;
  border-top: 2px solid rgba(148, 163, 214, 0.18);
  transition: color 0.3s ease, border-color 0.3s ease;
}
.lm-console-steps li.is-done { color: #C7D2FE; border-top-color: #818CF8; }
.lm-console-steps li.is-active { color: #FFFFFF; border-top-color: #BEF264; }
.lm-console-steps li.is-active::after {
  content: "";
  display: inline-block;
  width: 10px; height: 10px; margin-left: 6px; vertical-align: -1px;
  border-radius: 50%;
  border: 2px solid rgba(190, 242, 100, 0.3);
  border-top-color: #BEF264;
  animation: lm-spin 0.8s linear infinite;
}
.lm-console-steps li.is-done::before { content: "\2713  "; color: #BEF264; font-weight: 700; }
.lm-console-steps li.is-error { color: #FCA5A5; border-top-color: #F87171; }
.lm-step-time {
  display: block; margin-top: 3px;
  font-family: var(--lm-mono); font-size: 11px; color: #8B97B8;
}
@keyframes lm-spin { to { transform: rotate(360deg); } }
.lm-console-moves {
  display: flex; align-items: center; gap: 12px;
  margin-top: 14px; padding: 10px 12px; border-radius: 12px;
  background: rgba(255, 255, 255, 0.035); border: 1px solid rgba(165, 180, 252, 0.14);
}
.lm-console-moves p { margin: 0 !important; font-size: 12.5px !important; color: #98A3C2 !important; max-width: none !important; }
.lm-move-list span {
  display: inline-block; margin: 0 2px; padding: 1px 7px; border-radius: 6px;
  font-family: var(--lm-mono); font-size: 11.5px; color: #8B97B8;
  animation: lm-move-hi 6s linear infinite;
}
.lm-move-list span:nth-child(2) { animation-delay: 1.2s; }
.lm-move-list span:nth-child(3) { animation-delay: 2.4s; }
.lm-move-list span:nth-child(4) { animation-delay: 3.6s; }
.lm-move-list span:nth-child(5) { animation-delay: 4.8s; }
@keyframes lm-move-hi {
  0%, 20% { color: #0B1226; background: #BEF264; }
  21%, 100% { color: #8B97B8; background: transparent; }
}
.lm-two-opt { flex: 0 0 44px; width: 44px; height: 28px; }
.lm-two-opt circle { fill: #A5B4FC; }
.lm-two-opt path { fill: none; stroke-width: 2; stroke-linecap: round; }
.lm-2opt-a { stroke: #F87171; animation: lm-2opt-a 2.4s ease-in-out infinite; }
.lm-2opt-b { stroke: #BEF264; animation: lm-2opt-b 2.4s ease-in-out infinite; }
@keyframes lm-2opt-a { 0%, 35% { opacity: 1; } 50%, 90% { opacity: 0; } 100% { opacity: 1; } }
@keyframes lm-2opt-b { 0%, 40% { opacity: 0; } 55%, 88% { opacity: 1; } 100% { opacity: 0; } }
.lm-console-budget {
  height: 4px;
  margin-top: 14px;
  border-radius: 4px;
  background: rgba(148, 163, 214, 0.18);
  overflow: hidden;
}
.lm-console-budget span {
  display: block;
  height: 100%;
  width: 100%;
  transform-origin: left;
  background: linear-gradient(90deg, #6366F1, #BEF264);
  animation: lm-budget 5s linear both;
}
@keyframes lm-budget { from { transform: scaleX(0); } to { transform: scaleX(1); } }
.lm-console.is-error { border-color: rgba(248, 113, 113, 0.5); }
.lm-console.is-done { border-color: rgba(190, 242, 100, 0.35); }
@media (max-width: 760px) {
  .lm-console { padding: 18px 16px; }
  .lm-console-head { flex-direction: column; align-items: flex-start; gap: 10px; }
  .lm-console-steps { grid-template-columns: 1fr; gap: 6px; }
  .lm-console-steps li { border-top: 0; border-left: 2px solid rgba(148, 163, 214, 0.18); padding: 2px 0 2px 10px; }
  .lm-console-steps li.is-done { border-left-color: #818CF8; }
  .lm-console-steps li.is-active { border-left-color: #BEF264; }
  .lm-step-time { display: inline; margin-left: 6px; }
  .lm-console-moves { flex-wrap: wrap; }
}

/* ---------- Plan: result banner ---------- */
.lm-result {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
  gap: 28px 40px;
  align-items: center;
  margin: 6px 0 22px;
  padding: 28px 32px;
  border-radius: 20px;
  color: #E2E8F8;
  background: var(--lm-glow), linear-gradient(160deg, #0B1226 0%, #121C3D 60%, #1E1B4B 100%);
  border: 1px solid rgba(165, 180, 252, 0.2);
  box-shadow: 0 30px 60px -32px rgba(30, 27, 75, 0.6);
}
.lm-result-kicker {
  margin: 0 0 6px !important;
  font-size: 11.5px !important; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
  color: #D9F99D !important;
}
.lm-result-num {
  margin: 0 !important;
  font-size: clamp(48px, 6vw, 76px) !important;
  font-weight: 600;
  line-height: 1 !important;
  color: #FFFFFF !important;
  animation: lm-pop 0.7s cubic-bezier(0.2, 0.9, 0.3, 1.3) both 0.15s;
}
.lm-result-num small {
  font-family: var(--lm-display); font-size: 0.36em; font-weight: 500;
  color: #A5B4FC; margin-left: 12px; letter-spacing: 0;
}
@keyframes lm-pop { from { opacity: 0; transform: translateY(12px) scale(0.96); } to { opacity: 1; transform: none; } }
.lm-result-title {
  margin: 10px 0 0 !important; font-size: 17px !important; font-weight: 500; line-height: 1.45 !important;
  color: #C9D2EC !important; max-width: 46ch;
}
.lm-result-bars { display: grid; gap: 14px; margin: 0; }
.lm-result-bar-label {
  max-width: none !important;
  display: flex; justify-content: space-between; gap: 12px;
  margin: 0 0 6px !important; font-size: 13px !important; color: #AEB8D6 !important;
}
.lm-result-km { color: #FFFFFF; font-size: 14px; }
.lm-result-track { height: 12px; border-radius: 6px; background: rgba(148, 163, 214, 0.14); overflow: hidden; }
.lm-result-track span {
  display: block; height: 100%; border-radius: 6px;
  transform-origin: left;
  animation: lm-grow 1.1s cubic-bezier(0.2, 0.8, 0.2, 1) both 0.25s;
}
.lm-result-track .is-baseline { background: linear-gradient(90deg, #64748B, #94A3B8); }
.lm-result-track .is-optimised { background: linear-gradient(90deg, #6366F1, #BEF264); animation-delay: 0.5s; }
@keyframes lm-grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
.lm-result-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 6px 0 0 !important;
}
.lm-result-stats div {
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(165, 180, 252, 0.14);
}
.lm-result-stats dt { margin: 0; font-size: 11.5px; color: #98A3C2; }
.lm-stat-value {
  display: block; margin: 2px 0 0; font-size: 16px; font-weight: 600; color: #FFFFFF; white-space: nowrap;
}
@media (max-width: 1000px) {
  .lm-result { grid-template-columns: 1fr; padding: 24px; }
}
@media (max-width: 520px) {
  .lm-result-stats { grid-template-columns: 1fr; }
}

/* ---------- Plan: insight panels (convergence, shift timeline) ---------- */
.lm-insight {
  margin: 2px 0 8px;
}
.lm-insight h3 { margin: 0 0 4px !important; font-size: 20px; font-weight: 600; color: var(--lm-ink); }
.lm-insight p { margin: 0 !important; color: var(--lm-muted); font-size: 14.5px; line-height: 1.55; max-width: 75ch; }
.lm-insight-chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 2px !important; padding: 0; list-style: none; }
.lm-insight-chips li {
  margin: 0; padding: 4px 10px; border-radius: 8px; font-size: 12.5px; font-weight: 600;
  color: var(--lm-ink); background: var(--lm-surface); border: 1px solid var(--lm-border);
}
.lm-insight-chips li b { font-family: var(--lm-mono); font-weight: 600; color: var(--lm-primary); }
.st-key-plan-insights [data-testid="stHorizontalBlock"] { gap: 28px; }
.st-key-plan-insights [data-testid="stColumn"] {
  background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  border-radius: 16px;
  padding: 18px 18px 6px;
  box-shadow: var(--lm-shadow);
}

/* ---------- Continuum approximation: Scenarios card and Plan check ---------- */
.lm-ca {
  margin: 14px 0 12px;
  padding: 16px 18px;
  border-radius: 14px;
  background: linear-gradient(180deg, #FFFFFF, var(--lm-well));
  border: 1px solid var(--lm-border);
  box-shadow: var(--lm-shadow);
}
.lm-ca-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; }
.lm-ca-kicker {
  margin: 0 !important; font-size: 11px !important; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--lm-primary) !important;
}
.lm-ca-title { margin: 2px 0 0 !important; font-family: var(--lm-display); font-size: 17px !important; font-weight: 600; color: var(--lm-ink) !important; }
.lm-ca-total {
  margin: 0 !important; font-family: var(--lm-mono); font-size: 26px !important; font-weight: 600;
  color: var(--lm-ink) !important; white-space: nowrap; letter-spacing: -0.03em;
}
.lm-ca-body { margin: 8px 0 12px !important; font-size: 13.5px !important; line-height: 1.5 !important; color: var(--lm-muted) !important; }
.lm-ca-split { display: flex; gap: 3px; height: 10px; }
.lm-ca-split span { display: block; border-radius: 4px; transform-origin: left; animation: lm-grow 0.9s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
.lm-ca-split .is-linehaul { background: #A5B4FC; }
.lm-ca-split .is-local { background: var(--lm-primary); animation-delay: 0.15s; }
.lm-ca-legend { max-width: none !important; display: flex; flex-wrap: wrap; gap: 6px 18px; margin: 8px 0 10px !important; font-size: 12.5px !important; color: var(--lm-muted) !important; }
.lm-ca-legend span::before { content: ""; display: inline-block; width: 9px; height: 9px; border-radius: 3px; margin-right: 6px; vertical-align: 0; }
.lm-ca-legend .is-linehaul::before { background: #A5B4FC; }
.lm-ca-legend .is-local::before { background: var(--lm-primary); }
.lm-ca-legend b, .lm-ca-facts dd { font-family: var(--lm-mono); font-weight: 600; color: var(--lm-ink); }
.lm-ca-facts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin: 0 !important; }
.lm-ca-facts div { padding: 8px 10px; border-radius: 10px; background: var(--lm-surface-soft); }
.lm-ca-facts dt { font-size: 11.5px; color: var(--lm-muted); }
.lm-ca-facts dd { margin: 2px 0 0; font-size: 14px; }
.lm-cac {
  margin: 18px 0 6px;
  padding: 18px 20px 16px;
  border-radius: 16px;
  background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  box-shadow: var(--lm-shadow);
}
.lm-cac-estimate { max-width: none !important; display: flex; align-items: center; gap: 8px; margin: 12px 0 10px !important; font-size: 13px !important; color: var(--lm-muted) !important; }
.lm-cac-estimate b { font-family: var(--lm-mono); color: var(--lm-ink); }
.lm-cac-estimate i, .lm-cac-track i {
  display: inline-block; width: 2px; height: 14px; background: var(--lm-ink);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.9);
}
.lm-cac-row + .lm-cac-row { margin-top: 10px; }
.lm-cac-label { max-width: none !important; display: flex; justify-content: space-between; gap: 12px; margin: 0 0 5px !important; font-size: 13px !important; color: var(--lm-muted) !important; }
.lm-cac-label b { font-family: var(--lm-mono); color: var(--lm-ink); }
.lm-cac-track { position: relative; height: 12px; border-radius: 6px; background: var(--lm-surface-soft); }
.lm-cac-track span { display: block; height: 100%; border-radius: 6px; transform-origin: left; animation: lm-grow 1s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
.lm-cac-track .is-baseline { background: linear-gradient(90deg, #64748B, #94A3B8); }
.lm-cac-track .is-optimised { background: linear-gradient(90deg, #4F46E5, #818CF8); }
.lm-cac-track i { position: absolute; top: -4px; height: 20px; transform: translateX(-1px); }

/* ---------- Plan: dispatcher-acceptance panel ---------- */
.lm-rq {
  margin: 18px 0 6px;
  padding: 18px 20px 14px;
  border-radius: 16px;
  background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  box-shadow: var(--lm-shadow);
}
.lm-rq-table { width: 100%; margin-top: 12px; border-collapse: separate; border-spacing: 0; font-size: 14px; }
.lm-rq-table th, .lm-rq-table td { padding: 11px 12px; text-align: left; border-bottom: 1px solid var(--lm-border); vertical-align: middle; }
.lm-rq-table thead th { font-size: 12px; font-weight: 600; color: var(--lm-muted); background: var(--lm-well); }
.lm-rq-table thead th:first-child { border-radius: 10px 0 0 0; }
.lm-rq-table thead th:last-child { border-radius: 0 10px 0 0; }
.lm-rq-table tbody th { width: 38%; font-weight: 600; color: var(--lm-ink); }
.lm-rq-table tbody th small { display: block; margin-top: 2px; font-weight: 400; font-size: 12.5px; color: var(--lm-muted); }
.lm-rq-table tbody tr:last-child :is(th, td) { border-bottom: 0; }
.lm-rq-val { display: inline-block; min-width: 92px; font-family: var(--lm-mono); font-weight: 600; color: var(--lm-ink); }
.lm-rq-table td.is-better .lm-rq-val { color: var(--lm-success); }
.lm-rq-table td.is-better .lm-rq-val::after { content: " \2713"; font-family: var(--lm-font); }
.lm-rq-bar { display: inline-block; vertical-align: middle; width: calc(100% - 104px); max-width: 160px; height: 8px; border-radius: 4px; background: var(--lm-surface-soft); overflow: hidden; }
.lm-rq-bar i { display: block; height: 100%; border-radius: 4px; transform-origin: left; animation: lm-grow 0.9s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
.lm-rq-bar.is-baseline i { background: #94A3B8; }
.lm-rq-bar.is-optimised i { background: var(--lm-primary); }
.lm-rq-note { margin: 10px 0 0 !important; font-size: 12.5px !important; color: var(--lm-muted) !important; }
.st-key-plan-pair [data-testid="stCheckbox"], .st-key-plan-pair .stCheckbox { margin-bottom: 4px; }
@media (max-width: 760px) {
  .lm-rq { padding: 16px 14px 12px; }
  .lm-rq-table { font-size: 13px; }
  .lm-rq-table th, .lm-rq-table td { padding: 9px 8px; }
  .lm-rq-table tbody th { width: auto; }
  .lm-rq-table tbody th small, .lm-rq-bar { display: none; }
  .lm-rq-val { min-width: 0; }
}

/* ---------- Methodology: walkthrough (assign -> sequence -> 2-opt) ---------- */
.lm-walk-panel { max-width: 860px !important; padding: 18px 20px 12px; border-radius: 18px; background: var(--lm-surface); border: 1px solid var(--lm-border); box-shadow: var(--lm-shadow); }
.lm-walk-steps { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 6px; padding: 0; list-style: none; }
.lm-walk-step {
  display: inline-flex; align-items: center; gap: 8px; margin: 0;
  padding: 5px 12px 5px 6px; border-radius: 999px; font-size: 13px; font-weight: 600;
  color: var(--lm-muted); background: var(--lm-well); border: 1px solid var(--lm-border);
  flex: 0 0 auto; max-width: none !important; white-space: nowrap; line-height: 1.3;
  animation: 12s linear infinite;
}
/* Streamlit's markdown list-item padding outranks a single class. */
.lm-walk-steps .lm-walk-step { margin: 0 !important; padding: 5px 14px 5px 6px !important; }
.lm-walk-step span {
  display: inline-grid; place-items: center; width: 22px; height: 22px; border-radius: 50%;
  font-family: var(--lm-mono); font-size: 11.5px; background: var(--lm-surface); border: 1px solid var(--lm-border-strong);
  color: var(--lm-primary);
}
.lm-walk-step.s1 { animation-name: lm-walk-s1; }
.lm-walk-step.s2 { animation-name: lm-walk-s2; }
.lm-walk-step.s3 { animation-name: lm-walk-s3; }
@keyframes lm-walk-s1 { 6%, 30% { color: #FFFFFF; background: var(--lm-primary); border-color: var(--lm-primary); } 0%, 5%, 31%, 100% { color: var(--lm-muted); background: var(--lm-well); } }
@keyframes lm-walk-s2 { 32%, 50% { color: #FFFFFF; background: var(--lm-primary); border-color: var(--lm-primary); } 0%, 31%, 51%, 100% { color: var(--lm-muted); background: var(--lm-well); } }
@keyframes lm-walk-s3 { 52%, 92% { color: #FFFFFF; background: var(--lm-primary); border-color: var(--lm-primary); } 0%, 51%, 93%, 100% { color: var(--lm-muted); background: var(--lm-well); } }
.lm-walk { display: block; width: 100%; height: auto; }
.lm-walk-map { fill: var(--lm-well); stroke: var(--lm-border); }
/* Van colours live here: Streamlit strips custom properties from inline styles. */
.lm-walk-node.v1 { --van: #2A78D6; }
.lm-walk-node.v2 { --van: #EB6834; }
.lm-walk-node.v3 { --van: #1BAF7A; }
.lm-walk-node circle { fill: #FFFFFF; stroke: #94A3B8; stroke-width: 2; animation: lm-walk-node 12s linear infinite; }
.lm-walk-node text { font: 600 12px var(--lm-mono); fill: var(--lm-ink); animation: lm-walk-node-text 12s linear infinite; }
.lm-walk-node.v2 circle, .lm-walk-node.v2 text { animation-delay: 0.35s; }
.lm-walk-node.v3 circle, .lm-walk-node.v3 text { animation-delay: 0.7s; }
@keyframes lm-walk-node { 0%, 7% { fill: #FFFFFF; stroke: #94A3B8; } 11%, 94% { fill: var(--van); stroke: #FFFFFF; } 98%, 100% { fill: #FFFFFF; stroke: #94A3B8; } }
@keyframes lm-walk-node-text { 0%, 7% { fill: var(--lm-ink); } 11%, 94% { fill: #FFFFFF; } 98%, 100% { fill: var(--lm-ink); } }
.lm-walk-track { fill: var(--lm-well); stroke: var(--lm-border-strong); }
.lm-walk-tote { opacity: 0; animation: lm-walk-tote 12s linear infinite; }
@keyframes lm-walk-tote { 0%, 10% { opacity: 0; transform: translateY(-6px); } 13%, 94% { opacity: 1; transform: none; } 98%, 100% { opacity: 0; } }
.lm-walk-cap { font: 600 12px var(--lm-font); fill: var(--lm-muted); }
.lm-walk-van { font: 700 12px var(--lm-mono); fill: var(--lm-ink); }
.lm-walk-load { font: 600 12px var(--lm-mono); fill: var(--lm-muted); animation: lm-walk-fade 12s linear infinite; }
@keyframes lm-walk-fade { 0%, 22% { opacity: 0; } 26%, 94% { opacity: 1; } 98%, 100% { opacity: 0; } }
.lm-walk-route { stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 1; stroke-dashoffset: 1; animation: lm-walk-draw 12s linear infinite; }
.lm-walk-route.r2 { animation-delay: 0.4s; }
.lm-walk-route.r3 { animation-delay: 0.8s; }
@keyframes lm-walk-draw { 0%, 32% { stroke-dashoffset: 1; opacity: 1; } 42%, 94% { stroke-dashoffset: 0; opacity: 1; } 98%, 100% { stroke-dashoffset: 0; opacity: 0; } }
.lm-walk-route.is-bad { animation-name: lm-walk-bad; }
@keyframes lm-walk-bad { 0%, 32% { stroke-dashoffset: 1; opacity: 1; } 42%, 64% { stroke-dashoffset: 0; opacity: 1; } 70%, 100% { stroke-dashoffset: 0; opacity: 0; } }
.lm-walk-route.is-good { animation-name: lm-walk-good; stroke-width: 3.5; }
@keyframes lm-walk-good { 0%, 68% { stroke-dashoffset: 1; opacity: 0; } 69% { opacity: 1; stroke-dashoffset: 1; } 80%, 94% { stroke-dashoffset: 0; opacity: 1; } 98%, 100% { opacity: 0; } }
.lm-walk-cross { fill: rgba(220, 38, 38, 0.12); stroke: #DC2626; stroke-width: 2; opacity: 0; transform-box: fill-box; transform-origin: center; animation: lm-walk-cross 12s linear infinite; }
@keyframes lm-walk-cross { 0%, 52% { opacity: 0; transform: scale(0.6); } 55% { opacity: 1; transform: scale(1.15); } 58%, 64% { opacity: 1; transform: scale(1); } 60% { transform: scale(1.12); } 68%, 100% { opacity: 0; transform: scale(0.6); } }
.lm-walk-km { font: 600 13px var(--lm-mono); opacity: 0; }
.lm-walk-km.is-bad { fill: #DC2626; animation: lm-walk-km-bad 12s linear infinite; }
.lm-walk-km.is-good { fill: var(--lm-success); animation: lm-walk-km-good 12s linear infinite; }
@keyframes lm-walk-km-bad { 0%, 44% { opacity: 0; } 47%, 66% { opacity: 1; } 70%, 100% { opacity: 0; } }
@keyframes lm-walk-km-good { 0%, 76% { opacity: 0; } 80%, 94% { opacity: 1; } 98%, 100% { opacity: 0; } }
.stApp:has(.lm-motion-pause input:checked) .lm-walk-panel * { animation-play-state: paused !important; }

/* ---------- Methodology: on-this-page and further reading ---------- */
.lm-toc {
  display: flex; flex-wrap: wrap; gap: 8px;
  margin: 4px 0 8px; padding: 0; list-style: none;
}
.lm-toc li { margin: 0; }
.lm-toc a {
  display: inline-block; padding: 6px 12px; border-radius: 999px;
  font-size: 13px; font-weight: 600; text-decoration: none;
  color: var(--lm-ink) !important; background: var(--lm-surface);
  border: 1px solid var(--lm-border);
  transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
}
.lm-toc a:hover { border-color: var(--lm-primary); color: var(--lm-primary) !important; background: var(--lm-primary-soft); }
.lm-reading { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 6px 0 4px; }
.lm-reading a {
  display: block; padding: 14px 16px; border-radius: 14px; text-decoration: none;
  background: var(--lm-surface); border: 1px solid var(--lm-border); box-shadow: var(--lm-shadow);
  transition: transform 0.18s ease, border-color 0.18s ease;
}
.lm-reading a:hover { transform: translateY(-2px); border-color: var(--lm-primary); }
.lm-reading .lm-reading-src {
  margin: 0 0 4px !important; font-size: 11.5px !important; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--lm-primary) !important;
}
.lm-reading .lm-reading-title { margin: 0 0 4px !important; font-weight: 650; color: var(--lm-ink) !important; font-size: 15px !important; }
.lm-reading .lm-reading-why { margin: 0 !important; font-size: 13.5px !important; color: var(--lm-muted) !important; line-height: 1.5 !important; }
@media (max-width: 760px) { .lm-reading { grid-template-columns: 1fr; } }
.lm-section[id] { scroll-margin-top: 16px; }

/* ---------- Empty states and verification verdict ---------- */
.lm-empty {
  padding: 28px 20px 24px;
  border: 1.5px dashed var(--lm-border-strong);
  background: linear-gradient(180deg, var(--lm-surface), var(--lm-well));
}
.lm-empty strong { font-family: var(--lm-display); font-size: 18px; color: var(--lm-ink); }
.lm-empty-art { display: block; width: 120px; height: 56px; margin: 0 auto 10px; overflow: visible; }
.lm-empty-path {
  fill: none; stroke: var(--lm-primary); stroke-width: 2.5; stroke-linecap: round;
  stroke-dasharray: 5 7; animation: lm-flow 2.6s linear infinite;
}
.lm-empty-stop { fill: var(--lm-surface); stroke: var(--lm-primary); stroke-width: 2.5; }
.lm-empty-depot { fill: #BEF264; stroke: var(--lm-ink); stroke-width: 2; }
.lm-inspect-verdict {
  display: inline-flex;
  align-items: center;
  padding: 10px 16px;
  border-radius: 12px;
  border: 1px solid currentColor;
  font-family: var(--lm-display);
}
.lm-inspect-verdict.is-pass { background: #ECFDF5; border-color: #A7F3D0; }
.lm-inspect-verdict.is-fail { background: #FEF2F2; border-color: #FECACA; }
.lm-inspect-verdict-icon {
  display: inline-grid; place-items: center; width: 22px; height: 22px; border-radius: 50%;
  color: #FFFFFF; background: currentColor; font-size: 13px;
}
.lm-inspect-verdict.is-pass .lm-inspect-verdict-icon { background: var(--lm-success); }
.lm-inspect-verdict.is-fail .lm-inspect-verdict-icon { background: var(--lm-danger); }

/* ---------- Footer ---------- */
.lm-footer { border-top-style: dashed; }

/* ---------- Motion preferences ---------- */
@media (prefers-reduced-motion: reduce) {
  .lm-hero-grid *, .lm-console *, .lm-result *, .lm-ca *, .lm-cac *, .lm-rq *, .lm-kpi, .lm-api-dot, .lm-empty-path,
  [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *,
  .stPlotlyChart, [data-testid="stPlotlyChart"], .stApp::before {
    animation: none !important;
    transition: none !important;
  }
}
"""
