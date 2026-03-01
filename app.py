"""
app.py — Traceify: DSA Visualizer
Dark glassmorphic Streamlit app with Pathfinding + Sorting + Maps modules.
"""

import time
import random

import numpy as np
import pandas as pd
import streamlit as st

from pathfinding import (
    DijkstraGrid, ROWS, COLS,
    EMPTY, WALL, START_C, END_C, VISITED, PATH,
)
from sorting import bubble_sort_steps, quick_sort_steps, generate_array, SortStep

# Maps module — graceful import
try:
    from maps import (
        geocode, get_routes, build_osm_graph,
        dijkstra_on_graph, build_folium_map, fmt_distance, fmt_duration,
        MAX_GRAPH_DIST_KM, _haversine_m,
    )
    from streamlit_folium import st_folium
    MAPS_AVAILABLE = True
except ImportError:
    MAPS_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────── #
#  Page Config                                                                 #
# ─────────────────────────────────────────────────────────────────────────── #
st.set_page_config(
    page_title="Traceify — DSA Visualizer",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────── #
#  Global CSS — Dark Glassmorphic Theme                                        #
# ─────────────────────────────────────────────────────────────────────────── #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    color: #e2e8f0;
}

.stApp {
    background: radial-gradient(ellipse at 15% 40%, rgba(99,102,241,0.14) 0%, transparent 55%),
                radial-gradient(ellipse at 85% 15%, rgba(139,92,246,0.12) 0%, transparent 55%),
                radial-gradient(ellipse at 50% 85%, rgba(16,185,129,0.09) 0%, transparent 50%),
                #080b14;
    min-height: 100vh;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(10,12,22,0.90) !important;
    backdrop-filter: blur(28px) !important;
    border-right: 1px solid rgba(99,102,241,0.22) !important;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Cards */
.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 1rem;
}
.metric-card {
    background: rgba(99,102,241,0.10);
    border: 1px solid rgba(99,102,241,0.28);
    border-radius: 12px;
    padding: 1rem 1.2rem 0.8rem;
    text-align: center;
    margin-bottom: 0.75rem;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.1;
}
.metric-label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 0.3rem;
}

/* Typography */
.logo-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8 0%, #a78bfa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}
.logo-sub {
    color: #475569;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}
.page-header {
    font-size: 1.6rem;
    font-weight: 600;
    background: linear-gradient(90deg, #818cf8, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.15rem;
}
.section-label {
    color: #475569;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-bottom: 0.9rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 0.45rem 1.3rem !important;
    letter-spacing: 0.03em !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px rgba(99,102,241,0.55) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* Form controls */
.stSlider > label, .stSelectbox > label,
.stRadio > label, .stNumberInput > label {
    color: #94a3b8 !important;
    font-size: 0.80rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
div[data-baseweb="select"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 8px !important;
}
.stTextInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Progress bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg,#6366f1,#a78bfa) !important;
    border-radius: 99px !important;
}

/* Dataframe */
.stDataFrame { border-radius: 12px !important; overflow: hidden; }

/* Divider / alerts */
hr { border-color: rgba(99,102,241,0.18) !important; }
.stAlert { border-radius: 10px !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────── #
#  Session State Init                                                          #
# ─────────────────────────────────────────────────────────────────────────── #
def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init("grid",         DijkstraGrid())
_init("pf_visited",   [])
_init("pf_path",      [])
_init("pf_nodes",     0)
_init("pf_ran",       False)

_init("sort_algo",    "Bubble Sort")
_init("sort_size",    42)
_init("sort_seed",    7)
_init("sort_steps",   [])
_init("sort_step_idx", 0)
_init("sort_ran",     False)

# Maps state
_init("maps_origin",   "New York, NY")
_init("maps_dest",     "Boston, MA")
_init("maps_routes",   None)
_init("maps_dijkstra", None)
_init("maps_folium",   None)
_init("maps_ran",      False)

# ─────────────────────────────────────────────────────────────────────────── #
#  Sidebar                                                                     #
# ─────────────────────────────────────────────────────────────────────────── #
with st.sidebar:
    st.markdown('<div class="logo-title">🔮 Traceify</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">DSA Visualizer</div>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigate",
        options=["🗺️  Pathfinding", "📊  Sorting", "🌍  Maps"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    speed = st.slider(
        "Speed (ms / frame)",
        min_value=10, max_value=500, value=60, step=10,
    )
    delay = speed / 1000.0

    st.markdown("---")
    st.markdown(
        '<div style="color:#334155;font-size:0.72rem;line-height:1.6;">'
        'Algorithms run entirely in Python.<br>No data leaves your machine.'
        '</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────── #
#  Grid helpers                                                                #
# ─────────────────────────────────────────────────────────────────────────── #
CELL_COLOR = {
    EMPTY:   ("#1e293b", "#2d3f55"),
    WALL:    ("#0a0f1a", "#1e293b"),
    START_C: ("#064e3b", "#10b981"),
    END_C:   ("#4c0519", "#f43f5e"),
    VISITED: ("#1e1b4b", "#6366f1"),
    PATH:    ("#451a03", "#fbbf24"),
}

def _grid_html(grid: np.ndarray) -> str:
    cw, ch = 27, 22
    rows_html = ""
    for r in range(grid.shape[0]):
        cells = ""
        for c in range(grid.shape[1]):
            v = int(grid[r, c])
            bg, bd = CELL_COLOR.get(v, ("#1e293b", "#2d3f55"))
            lbl = "S" if v == START_C else ("E" if v == END_C else "")
            fs = "9px"
            glow = "box-shadow:0 0 6px rgba(251,191,36,0.6);" if v == PATH else ""
            cells += (
                f'<td style="width:{cw}px;height:{ch}px;'
                f'background:{bg};border:1px solid {bd};'
                f'border-radius:3px;text-align:center;vertical-align:middle;'
                f'font-size:{fs};font-weight:800;color:#f8fafc;'
                f'font-family:JetBrains Mono,monospace;{glow}">{lbl}</td>'
            )
        rows_html += f"<tr>{cells}</tr>"

    return (
        '<div style="overflow-x:auto;padding:6px 0;">'
        '<table style="border-collapse:collapse;margin:auto;">'
        f'{rows_html}'
        '</table></div>'
    )

# ─────────────────────────────────────────────────────────────────────────── #
#  Bar chart helper                                                            #
# ─────────────────────────────────────────────────────────────────────────── #
def _bars_html(step: SortStep) -> str:
    arr  = step.array
    n    = len(arr)
    if n == 0:
        return ""
    maxv = max(arr)
    bw   = max(4, min(20, 700 // n))
    gap  = max(1, bw // 5)
    H    = 250

    bars = ""
    for i, v in enumerate(arr):
        bh = max(2, int(v / maxv * (H - 24)))
        if i in step.highlighted:
            col, glow = "#f43f5e", "box-shadow:0 0 10px rgba(244,63,94,0.65);"
        elif step.pivot_idx is not None and i == step.pivot_idx:
            col, glow = "#fbbf24", "box-shadow:0 0 10px rgba(251,191,36,0.65);"
        elif i in step.sorted_indices:
            col, glow = "#10b981", ""
        else:
            col, glow = "#6366f1", ""

        bars += (
            f'<div style="display:inline-block;width:{bw}px;height:{bh}px;'
            f'background:{col};border-radius:3px 3px 0 0;margin-right:{gap}px;'
            f'vertical-align:bottom;transition:height 0.05s,background 0.07s;{glow}"></div>'
        )

    return (
        f'<div style="background:rgba(8,11,20,0.85);border:1px solid rgba(99,102,241,0.22);'
        f'border-radius:14px;padding:1rem 1.2rem 0.6rem;overflow-x:auto;">'
        f'<div style="display:flex;align-items:flex-end;height:{H}px;min-width:{n*(bw+gap)}px;">'
        f'{bars}</div></div>'
    )

# ═════════════════════════════════════════════════════════════════════════════
#  PAGE: PATHFINDING
# ═════════════════════════════════════════════════════════════════════════════
if "Pathfinding" in page:
    st.markdown('<div class="page-header">🗺️ Pathfinding — Dijkstra\'s Algorithm</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">15 × 30 interactive grid · Start (row 2, col 2) → End (row 12, col 27)</div>', unsafe_allow_html=True)

    g: DijkstraGrid = st.session_state.grid

    # ── Button row ──────────────────────────────────────────────────────── #
    bc1, bc2, bc3 = st.columns([1, 1, 1])
    with bc1:
        run_pf      = st.button("▶  Run Dijkstra",  use_container_width=True, key="btn_run_pf")
    with bc2:
        clear_walls = st.button("🧹  Clear Walls",  use_container_width=True, key="btn_clr")
    with bc3:
        reset_all   = st.button("↺  Reset All",    use_container_width=True, key="btn_rst")

    if clear_walls:
        g.clear_walls()
        st.session_state.pf_visited = []
        st.session_state.pf_path    = []
        st.session_state.pf_ran     = False
        st.rerun()

    if reset_all:
        st.session_state.grid       = DijkstraGrid()
        g = st.session_state.grid
        st.session_state.pf_visited = []
        st.session_state.pf_path    = []
        st.session_state.pf_nodes   = 0
        st.session_state.pf_ran     = False
        st.rerun()

    # ── Wall editor ─────────────────────────────────────────────────────── #
    st.markdown('<div class="section-label" style="margin-top:0.6rem;">Click a cell to toggle wall — enter row,col below</div>', unsafe_allow_html=True)

    wc1, wc2 = st.columns([2, 1])
    with wc1:
        wall_in = st.text_input(
            "Wall cell",
            value="",
            placeholder="e.g.  7, 14",
            label_visibility="collapsed",
            key="wall_input",
        )
    with wc2:
        add_wall_btn = st.button("Add / Remove Wall", use_container_width=True, key="btn_wall")

    if add_wall_btn and wall_in.strip():
        try:
            parts = wall_in.strip().split(",")
            wr, wc = int(parts[0]), int(parts[1])
            if 0 <= wr < ROWS and 0 <= wc < COLS:
                g.toggle_wall(wr, wc)
                st.session_state.pf_ran = False
            else:
                st.warning(f"Row 0–{ROWS-1}, Col 0–{COLS-1}")
        except Exception:
            st.warning("Use format: row, col   (e.g. 7, 14)")

    # ── Preset patterns ─────────────────────────────────────────────────── #
    p1, p2, p3 = st.columns(3)
    with p1:
        if st.button("🏗️ Vertical Wall", use_container_width=True):
            g.clear_walls()
            for r in range(1, 14):
                g.add_wall(r, 15)
            st.session_state.pf_ran = False
            st.rerun()
    with p2:
        if st.button("🌀 Zigzag Maze", use_container_width=True):
            g.clear_walls()
            for r in range(0, 9):   g.add_wall(r, 10)
            for r in range(5, 15):  g.add_wall(r, 20)
            st.session_state.pf_ran = False
            st.rerun()
    with p3:
        if st.button("🗑️ Clear All Walls", use_container_width=True):
            g.clear_walls()
            st.session_state.pf_ran = False
            st.rerun()

    # ── Difficulty presets ───────────────────────────────────────────────── #
    st.markdown('<div class="section-label" style="margin-top:0.4rem;">Random Wall Difficulty</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)

    def _random_walls(n_walls: int, seed: int | None = None):
        """Place n_walls random walls using a fresh RNG seed."""
        g.clear_walls()
        rng = random.Random(seed if seed is not None else int(time.time() * 1000) % 99999)
        placed = 0
        attempts = 0
        while placed < n_walls and attempts < n_walls * 10:
            r2 = rng.randint(0, ROWS - 1)
            c2 = rng.randint(0, COLS - 1)
            if (r2, c2) not in (g.start, g.end):
                g.add_wall(r2, c2)
                placed += 1
            attempts += 1
        st.session_state.pf_ran = False

    with d1:
        if st.button("🟢 Easy  (25 walls)", use_container_width=True, key="diff_easy"):
            _random_walls(25)
            st.rerun()
    with d2:
        if st.button("🟡 Medium (65 walls)", use_container_width=True, key="diff_med"):
            _random_walls(65)
            st.rerun()
    with d3:
        if st.button("🔴 Hard  (120 walls)", use_container_width=True, key="diff_hard"):
            _random_walls(120)
            st.rerun()

    # ── Metrics ─────────────────────────────────────────────────────────── #
    m1, m2, m3 = st.columns(3)
    path_len = max(0, len(st.session_state.pf_path) - 1)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.pf_nodes}</div><div class="metric-label">Nodes Visited</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{path_len}</div><div class="metric-label">Path Length</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(g.walls)}</div><div class="metric-label">Walls</div></div>', unsafe_allow_html=True)

    # ── Grid placeholder ─────────────────────────────────────────────────── #
    grid_ph = st.empty()

    def _show_grid(vis=None, path=None):
        state = g.get_grid_state(visited=vis, path=path)
        grid_ph.markdown(_grid_html(state), unsafe_allow_html=True)

    if not st.session_state.pf_ran:
        _show_grid()
    else:
        _show_grid(st.session_state.pf_visited, st.session_state.pf_path)

    # ── Legend ───────────────────────────────────────────────────────────── #
    st.markdown(
        '<div style="display:flex;gap:1.4rem;flex-wrap:wrap;margin-top:0.4rem;font-size:0.77rem;color:#94a3b8;">'
        '<span>🟩 Start</span>'
        '<span>🟥 End</span>'
        '<span style="color:#818cf8;">■ Visited</span>'
        '<span style="color:#fbbf24;">■ Path</span>'
        '<span style="color:#475569;">▪ Wall</span>'
        '<span style="color:#334155;">□ Empty</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Run Algorithm ────────────────────────────────────────────────────── #
    if run_pf:
        g.reset()
        visited_order, path, nodes_visited = g.dijkstra()
        st.session_state.pf_nodes = nodes_visited

        cum_vis: list = []
        for node in visited_order:
            cum_vis.append(node)
            _show_grid(cum_vis, None)
            time.sleep(delay)

        if path:
            cum_path: list = []
            for node in path:
                cum_path.append(node)
                _show_grid(cum_vis, cum_path)
                time.sleep(delay * 2)
            st.success(f"✅ Path found!  Length: **{len(path)-1}** steps · Nodes visited: **{nodes_visited}**")
        else:
            _show_grid(cum_vis, [])
            st.error("❌ No path found — the destination is completely blocked.")

        st.session_state.pf_visited = cum_vis
        st.session_state.pf_path    = path
        st.session_state.pf_ran     = True

    # Big-O for Dijkstra
    st.markdown("---")
    st.markdown('<div class="section-label">Dijkstra Complexity</div>', unsafe_allow_html=True)
    st.markdown("""
    | Metric | Value |  
    |---|---|  
    | Time | **O((V + E) log V)** |  
    | Space | **O(V)** |  
    | Shortest path? | **Yes** (non-negative weights) |
    """)

# ═════════════════════════════════════════════════════════════════════════════
#  PAGE: SORTING
# ═════════════════════════════════════════════════════════════════════════════
elif "Sorting" in page:
    st.markdown('<div class="page-header">📊 Sorting — Bar Chart Visualizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Bubble Sort · Quick Sort · Full animation &amp; Step-by-step mode</div>', unsafe_allow_html=True)

    # ── Controls ─────────────────────────────────────────────────────────── #
    sc1, sc2, sc3 = st.columns([1.6, 1.2, 1])
    with sc1:
        algo = st.selectbox(
            "Algorithm",
            options=["Bubble Sort", "Quick Sort"],
            index=0 if st.session_state.sort_algo == "Bubble Sort" else 1,
            label_visibility="collapsed",
        )
        if algo != st.session_state.sort_algo:
            st.session_state.sort_algo    = algo
            st.session_state.sort_steps   = []
            st.session_state.sort_step_idx = 0
            st.session_state.sort_ran     = False

    with sc2:
        arr_size = st.slider("Array Size", 8, 80, st.session_state.sort_size, step=2, label_visibility="collapsed")
        if arr_size != st.session_state.sort_size:
            st.session_state.sort_size    = arr_size
            st.session_state.sort_steps   = []
            st.session_state.sort_step_idx = 0
            st.session_state.sort_ran     = False

    with sc3:
        seed_v = st.number_input("Seed", 0, 9999, st.session_state.sort_seed, 1, label_visibility="collapsed")
        if int(seed_v) != st.session_state.sort_seed:
            st.session_state.sort_seed    = int(seed_v)
            st.session_state.sort_steps   = []
            st.session_state.sort_step_idx = 0
            st.session_state.sort_ran     = False

    # ── Action buttons ───────────────────────────────────────────────────── #
    ab1, ab2, ab3, ab4 = st.columns(4)
    with ab1: run_sort   = st.button("▶  Run Sort",    use_container_width=True, key="btn_sort")
    with ab2: step_fwd   = st.button("⏭  Step →",     use_container_width=True, key="btn_fwd")
    with ab3: step_back  = st.button("⏮  ← Step",    use_container_width=True, key="btn_bck")
    with ab4: new_arr    = st.button("🎲  New Array",  use_container_width=True, key="btn_new")

    if new_arr:
        st.session_state.sort_seed    = random.randint(0, 9999)
        st.session_state.sort_steps   = []
        st.session_state.sort_step_idx = 0
        st.session_state.sort_ran     = False
        st.rerun()

    def _ensure_steps():
        arr = generate_array(st.session_state.sort_size, st.session_state.sort_seed)
        if st.session_state.sort_algo == "Bubble Sort":
            st.session_state.sort_steps = bubble_sort_steps(arr)
        else:
            st.session_state.sort_steps = quick_sort_steps(arr)
        st.session_state.sort_step_idx = 0

    # ── Metrics row ──────────────────────────────────────────────────────── #
    steps = st.session_state.sort_steps
    idx   = st.session_state.sort_step_idx
    total = len(steps)

    if steps:
        cur: SortStep = steps[idx]
        pct = int(100 * idx / max(1, total - 1))
        m_vals = [str(cur.comparisons), str(cur.swaps), f"{idx+1}/{total}", f"{pct}%"]
    else:
        m_vals = ["—", "—", "—", "—"]

    for label, val in zip(["Comparisons","Swaps","Step","Progress"], m_vals):
        pass  # rendered below in columns

    mc1, mc2, mc3, mc4 = st.columns(4)
    for col, lbl, val in zip(
        [mc1, mc2, mc3, mc4],
        ["Comparisons", "Swaps", "Step", "Progress"],
        m_vals,
    ):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{val}</div>'
                f'<div class="metric-label">{lbl}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Bar chart ────────────────────────────────────────────────────────── #
    bar_ph = st.empty()

    def _show_bars(i: int):
        if st.session_state.sort_steps:
            bar_ph.markdown(_bars_html(st.session_state.sort_steps[i]), unsafe_allow_html=True)

    if not steps:
        arr0 = generate_array(st.session_state.sort_size, st.session_state.sort_seed)
        bar_ph.markdown(_bars_html(SortStep(array=arr0, comparisons=0, swaps=0)), unsafe_allow_html=True)
    else:
        _show_bars(idx)

    # ── Step-by-step buttons ─────────────────────────────────────────────── #
    if step_fwd:
        if not steps:
            _ensure_steps()
        cur_i = st.session_state.sort_step_idx
        if cur_i < len(st.session_state.sort_steps) - 1:
            st.session_state.sort_step_idx = cur_i + 1
        st.rerun()

    if step_back:
        if not steps:
            _ensure_steps()
        cur_i = st.session_state.sort_step_idx
        if cur_i > 0:
            st.session_state.sort_step_idx = cur_i - 1
        st.rerun()

    # ── Full animation run ───────────────────────────────────────────────── #
    if run_sort:
        _ensure_steps()
        all_steps = st.session_state.sort_steps
        prog = st.progress(0)
        n_steps = len(all_steps)

        for i, s in enumerate(all_steps):
            bar_ph.markdown(_bars_html(s), unsafe_allow_html=True)
            prog.progress((i + 1) / n_steps)
            time.sleep(delay)

        st.session_state.sort_step_idx = n_steps - 1
        st.session_state.sort_ran      = True
        prog.empty()

        final = all_steps[-1]
        st.success(
            f"✅ **{st.session_state.sort_algo}** complete! "
            f"Comparisons: **{final.comparisons}** · "
            f"Swaps: **{final.swaps}** · "
            f"Total steps: **{n_steps}**"
        )

    # ── Big-O Table ──────────────────────────────────────────────────────── #
    st.markdown("---")
    st.markdown('<div class="section-label">Big O Complexity Reference</div>', unsafe_allow_html=True)
    df = pd.DataFrame({
        "Algorithm":  ["Bubble Sort", "Quick Sort"],
        "Best":       ["Ω(n)",        "Ω(n log n)"],
        "Average":    ["Θ(n²)",       "Θ(n log n)"],
        "Worst":      ["O(n²)",       "O(n²)"],
        "Space":      ["O(1)",        "O(log n)"],
        "Stable":     ["✅ Yes",      "❌ No"],
        "In-place":   ["✅ Yes",      "✅ Yes"],
    })
    st.dataframe(df, hide_index=True, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
#  PAGE: MAPS
# ═════════════════════════════════════════════════════════════════════════════
elif "Maps" in page:
    st.markdown('<div class="page-header">🌍 Traceify Maps — Real-World Routing</div>', unsafe_allow_html=True)

    if not MAPS_AVAILABLE:
        st.error(
            "📦 Maps dependencies not installed. Run:\n\n"
            "```bash\npip install streamlit-folium folium geopy osmnx networkx requests\n```"
        )
        st.stop()

    # ── OSM badge ──────────────────────────────────────────────────────── #
    st.markdown(
        '<div style="display:inline-block;background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.35);'
        'border-radius:8px;padding:0.3rem 0.8rem;font-size:0.76rem;color:#818cf8;margin-bottom:0.8rem;">'
        '🗺️ Powered by OpenStreetMap · Nominatim · OSRM · osmnx — 100% free, no API key</div>',
        unsafe_allow_html=True,
    )

    # ── Origin / Destination inputs ───────────────────────────────────────── #
    ic1, ic2 = st.columns(2)
    with ic1:
        origin_input = st.text_input(
            "🟢 Origin",
            value=st.session_state.maps_origin,
            placeholder="e.g. New York, NY",
        )
    with ic2:
        dest_input = st.text_input(
            "🔴 Destination",
            value=st.session_state.maps_dest,
            placeholder="e.g. Boston, MA",
        )

    # Dijkstra toggle
    show_dijkstra = st.checkbox(
        "Show Dijkstra simulation overlay on map (only for routes ≤ 50 km)",
        value=True,
    )

    find_btn = st.button("▶  Find Routes", use_container_width=False, key="btn_find_routes")

    # ── Run routing ───────────────────────────────────────────────────────── #
    if find_btn:
        if not origin_input.strip() or not dest_input.strip():
            st.warning("Please enter both an origin and a destination.")
        else:
            st.session_state.maps_origin  = origin_input.strip()
            st.session_state.maps_dest    = dest_input.strip()
            st.session_state.maps_ran     = False
            st.session_state.maps_routes  = None
            st.session_state.maps_dijkstra = None

            with st.spinner("📍 Geocoding locations..."):
                origin_ll = geocode(origin_input.strip())
                dest_ll   = geocode(dest_input.strip())

            if not origin_ll:
                st.error(f"❌ Could not geocode: **{origin_input}**")
                st.stop()
            if not dest_ll:
                st.error(f"❌ Could not geocode: **{dest_input}**")
                st.stop()

            with st.spinner("🛣️ Fetching routes..."):
                routes = get_routes(origin_ll, dest_ll)

            if not routes:
                st.error("❌ No routes found between these locations.")
                st.stop()

            st.session_state.maps_routes = routes

            # Dijkstra on OSM graph (only short routes)
            dijkstra_result = None
            if show_dijkstra:
                dist_km = _haversine_m(origin_ll, dest_ll) / 1000
                if dist_km <= MAX_GRAPH_DIST_KM:
                    with st.spinner(f"🔬 Building OSM road graph ({dist_km:.1f} km area)..."):
                        graph_data = build_osm_graph(origin_ll, dest_ll)
                    if graph_data:
                        G, orig_node, dest_node = graph_data
                        with st.spinner("⚙️ Running Dijkstra on real road nodes..."):
                            dijkstra_result = dijkstra_on_graph(G, orig_node, dest_node)
                else:
                    st.info(f"ℹ️ Route is {dist_km:.0f} km — Dijkstra overlay skipped (limit: {MAX_GRAPH_DIST_KM} km).")

            st.session_state.maps_dijkstra = dijkstra_result

            # Build folium map
            with st.spinner("🗺️ Rendering map..."):
                folium_map = build_folium_map(
                    origin_ll, dest_ll, routes,
                    dijkstra=dijkstra_result,
                    show_dijkstra=show_dijkstra,
                )
            st.session_state.maps_folium = folium_map
            st.session_state.maps_ran    = True

    # ── Map display ───────────────────────────────────────────────────────── #
    if st.session_state.maps_ran and st.session_state.maps_folium:
        routes    = st.session_state.maps_routes or []
        dijkstra  = st.session_state.maps_dijkstra

        # Metrics panel
        if routes:
            num_cols = min(4, len(routes) * 2)
            metric_cols = st.columns(4)
            labels = []
            for r in routes[:2]:
                labels.append((f"ETA — {r.label}", fmt_duration(r.total_duration_s)))
                labels.append((f"Distance — {r.label}", fmt_distance(r.total_distance_m)))

            for col, (lbl, val) in zip(metric_cols, labels):
                with col:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-value" style="font-size:1.4rem;">{val}</div>'
                        f'<div class="metric-label">{lbl}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        # Route legend
        legend_html = (
            '<div style="display:flex;gap:1.2rem;flex-wrap:wrap;font-size:0.77rem;'
            'color:#94a3b8;margin-bottom:0.5rem;">'
            '<span style="color:#60a5fa;">━━ Fastest Route</span>'
            '<span style="color:#34d399;">━━ Shortest Route</span>'
        )
        if dijkstra and dijkstra.available:
            legend_html += (
                '<span style="color:#818cf8;">● Dijkstra Visited</span>'
                '<span style="color:#fbbf24;">╌╌ Dijkstra Path</span>'
            )
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)

        # Folium map embed
        st_folium(
            st.session_state.maps_folium,
            width="100%",
            height=520,
            returned_objects=[],
        )

        # ── Step-by-step directions panel ────────────────────────────────── #
        for route in routes:
            if route.steps:
                with st.expander(f"📋 Turn-by-Turn Directions — {route.label} ({fmt_distance(route.total_distance_m)}, {fmt_duration(route.total_duration_s)})"):
                    for i, step in enumerate(route.steps, 1):
                        d = fmt_distance(step.distance_m)
                        dur = fmt_duration(step.duration_s)
                        st.markdown(
                            f'<div style="padding:0.4rem 0;border-bottom:1px solid rgba(99,102,241,0.12);'
                            f'font-size:0.85rem;">'
                            f'<span style="color:#6366f1;font-weight:700;margin-right:0.6rem;">{i}.</span>'
                            f'{step.instruction} '
                            f'<span style="color:#64748b;float:right;">{d} · {dur}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

        # ── Algorithm comparison table ────────────────────────────────────── #
        if dijkstra and dijkstra.available and routes:
            st.markdown("---")
            st.markdown('<div class="section-label">Algorithm Comparison</div>', unsafe_allow_html=True)
            api_route = routes[0]
            comparison_data = {
                "Metric": ["Distance", "Duration", "Nodes Explored", "Source"],
                f"{api_route.label} (API)": [
                    fmt_distance(api_route.total_distance_m),
                    fmt_duration(api_route.total_duration_s),
                    "N/A",
                    api_route.source.upper(),
                ],
                "Raw Dijkstra (OSM)": [
                    fmt_distance(dijkstra.path_length_m),
                    "N/A (edge weights only)",
                    str(dijkstra.nodes_explored),
                    "osmnx + networkx",
                ],
            }
            st.dataframe(pd.DataFrame(comparison_data), hide_index=True, use_container_width=True)

    elif not st.session_state.maps_ran:
        # ── Empty state ───────────────────────────────────────────────────── #
        st.markdown(
            '<div style="text-align:center;padding:3rem 0;color:#334155;">'
            '<div style="font-size:3rem;margin-bottom:0.5rem;">🌍</div>'
            '<div style="font-size:1rem;">Enter an origin and destination above, then click <b>▶ Find Routes</b></div>'
            '<div style="font-size:0.8rem;margin-top:0.5rem;">'
            'Example: <code>New York, NY</code> → <code>Boston, MA</code>'
            '</div></div>',
            unsafe_allow_html=True,
        )
