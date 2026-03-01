# 🔮 Traceify — DSA Visualizer

A high-end, dark-themed, glassmorphic **Data Structures & Algorithms visualizer** built with **Python + Streamlit**.  
Watch Dijkstra's pathfinding and sorting algorithms come to life with real-time animated step-by-step breakdowns.

---
## 📸 App Preview

| Pathfinding Module | Sorting Module | Real-World Maps |
| :---: | :---: | :---: |
| ![Pathfinding](screenshots/Screenshot(1).png) | ![Sorting](screenshots/Screenshot(2).png) | ![Maps](screenshots/Screenshot(3).png) |

---

## 🚀 Setup & Installation

### Prerequisites
- Python **3.10+**
- pip

### 1. Clone / download the project
```bash
# If using git
git clone https://github.com/amandeepintl/Traceify
cd Traceify
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**

---

## 🗂️ Project Structure

```
Traceify/
├── app.py            # Main Streamlit application (UI & Navigation)
├── pathfinding.py    # Dijkstra's algorithm engine (15×30 grid logic)
├── sorting.py        # Bubble Sort & Quick Sort step generators
├── maps.py           # Real-world routing (OSMnx + OSRM Integration)
├── requirements.txt  # Python dependencies
└── README.md         # Documentation
```

---

## 🗺️ Pathfinding Module

### Features
- **15 × 30 interactive grid**
- **Start node** fixed at `(row 2, col 2)` · **End node** at `(row 12, col 27)`
- **Draw walls** by typing `row, col` in the wall editor (e.g. `5, 14`)
- **Preset maze patterns**: Vertical Wall, Zigzag Maze, Random Walls
- **Animated traversal**: watched nodes light up progressively in indigo
- **Path highlight**: shortest path glows amber after traversal

### Algorithm: Dijkstra's
| Metric | Value |
|---|---|
| Time Complexity | **O((V + E) log V)** |
| Space Complexity | **O(V)** |
| Shortest Path? | ✅ Yes (non-negative weights) |
| Data Structure | Min-heap priority queue |

> On a uniform-weight grid, Dijkstra behaves identically to BFS.

---

## 📊 Sorting Module

### Features
- **Bubble Sort** and **Quick Sort** (Lomuto partition)
- **Full animation** — press ▶ Run Sort, watch bars race to their places
- **Step-by-step mode** — ⏭ Step → / ⏮ ← Step for manual frame control
- **Array size** slider (8–80 elements), configurable **random seed**
- **Real-time metrics**: Comparisons, Swaps, Step index, % Progress
- **Color coding**: 🔴 Comparing, 🟡 Pivot, 🟢 Sorted, 🔵 Unsorted

### Big O Complexity

| Algorithm | Best | Average | Worst | Space | Stable |
|---|---|---|---|---|---|
| **Bubble Sort** | Ω(n) | Θ(n²) | O(n²) | O(1) | ✅ Yes |
| **Quick Sort** | Ω(n log n) | Θ(n log n) | O(n²) | O(log n) | ❌ No |

#### Bubble Sort
- **Best case** Ω(n): array already sorted, single pass with no swaps.
- **Worst case** O(n²): reverse-sorted array, every pair must be swapped.
- **Stable**: equal elements preserve original relative order.

#### Quick Sort (Lomuto)
- **Best / Average** Ω/Θ(n log n): well-balanced pivot splits.
- **Worst case** O(n²): consistently bad pivot (already sorted / all same).
- **Not stable**: swaps can change relative order of equal elements.
- **In-place** (O(log n) implicit stack space for recursion).

#### Traceify Maps (Real-World)
- **100% Free / No API Key** Uses Nominatim for geocoding and OSRM for public routing.
- **Real-World Graph Theory** Downloads road networks via OSMnx to run Dijkstra on real intersections.
- **Comparison Engine: Compare** "Fastest Route" (API) vs "Shortest Path" (Raw Dijkstra) side-by-side.
- **Interactive Mapping** Folium-based maps with custom markers and glowing path polylines.

---

## ⚙️ Configuration

| Control | Range | Default | Effect |
|---|---|---|---|
| Speed slider | 10–500 ms | 60 ms | Delay between animation frames |
| Array size | 8–80 | 42 | Number of bars to sort |
| Seed | 0–9999 | 7 | Reproducible random array |
| Map Source | OSRM / OSM | N/A | Fetching live road network data |
---

## 🛠️ Tech Stack

| Library | Version | Use |
|---|---|---|
| `streamlit` | ≥ 1.32 | UI framework & reactivity |
| `numpy` | ≥ 1.26 | Grid state arrays |
| `pandas` | ≥ 2.0 | Big-O reference tables |
| `osmnx` | ≥ 1.9 | Street network retrieval & Graph logic |
| `networkx` | ≥ 3.3 | Mathematical graph structures |
---

## 📄 License
MIT — free to use, modify, and distribute.



