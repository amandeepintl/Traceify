"""
pathfinding.py — Dijkstra's algorithm engine for Traceify.
Grid: 15 rows × 30 cols
Start: (2, 2)   End: (12, 27)
"""

import heapq
import numpy as np

ROWS = 15
COLS = 30
START = (2, 2)
END = (12, 27)

# Cell state constants
EMPTY   = 0
WALL    = 1
START_C = 2
END_C   = 3
VISITED = 4
PATH    = 5


class DijkstraGrid:
    def __init__(self):
        self.rows = ROWS
        self.cols = COLS
        self.start = START
        self.end = END
        self.walls: set[tuple[int, int]] = set()
        self.visited_steps: list[list[tuple[int, int]]] = []
        self.path: list[tuple[int, int]] = []
        self.nodes_visited: int = 0

    # ------------------------------------------------------------------ #
    #  Wall management                                                     #
    # ------------------------------------------------------------------ #
    def toggle_wall(self, r: int, c: int):
        """Toggle a wall cell (cannot be placed on start or end)."""
        if (r, c) in (self.start, self.end):
            return
        if (r, c) in self.walls:
            self.walls.discard((r, c))
        else:
            self.walls.add((r, c))

    def add_wall(self, r: int, c: int):
        if (r, c) not in (self.start, self.end):
            self.walls.add((r, c))

    def remove_wall(self, r: int, c: int):
        self.walls.discard((r, c))

    def clear_walls(self):
        self.walls.clear()

    # ------------------------------------------------------------------ #
    #  Grid state as numpy array                                           #
    # ------------------------------------------------------------------ #
    def get_grid_state(
        self,
        visited: list[tuple[int, int]] | None = None,
        path: list[tuple[int, int]] | None = None,
    ) -> np.ndarray:
        grid = np.zeros((self.rows, self.cols), dtype=np.int8)
        for (r, c) in self.walls:
            grid[r][c] = WALL
        if visited:
            for (r, c) in visited:
                if (r, c) not in (self.start, self.end):
                    grid[r][c] = VISITED
        if path:
            for (r, c) in path:
                if (r, c) not in (self.start, self.end):
                    grid[r][c] = PATH
        sr, sc = self.start
        er, ec = self.end
        grid[sr][sc] = START_C
        grid[er][ec] = END_C
        return grid

    # ------------------------------------------------------------------ #
    #  Dijkstra                                                            #
    # ------------------------------------------------------------------ #
    def dijkstra(self):
        """
        Run Dijkstra's algorithm.
        Returns:
            visited_order : list of (r, c) in visit order
            path          : list of (r, c) from start to end (empty if unreachable)
            nodes_visited : int
        """
        dist = {(r, c): float('inf') for r in range(self.rows) for c in range(self.cols)}
        prev: dict[tuple[int, int], tuple[int, int] | None] = {}
        dist[self.start] = 0
        heap: list[tuple[float, tuple[int, int]]] = [(0, self.start)]
        visited_set: set[tuple[int, int]] = set()
        visited_order: list[tuple[int, int]] = []

        while heap:
            d, u = heapq.heappop(heap)
            if u in visited_set:
                continue
            visited_set.add(u)
            visited_order.append(u)

            if u == self.end:
                break

            r, c = u
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) not in visited_set and (nr, nc) not in self.walls:
                        nd = d + 1
                        if nd < dist[(nr, nc)]:
                            dist[(nr, nc)] = nd
                            prev[(nr, nc)] = u
                            heapq.heappush(heap, (nd, (nr, nc)))

        # Reconstruct path
        path: list[tuple[int, int]] = []
        if self.end in visited_set:
            node: tuple[int, int] | None = self.end
            while node is not None:
                path.append(node)
                node = prev.get(node)
            path.reverse()

        self.visited_steps = visited_order
        self.path = path
        self.nodes_visited = len(visited_order)
        return visited_order, path, len(visited_order)

    def reset(self):
        """Reset algorithm results (keeps walls)."""
        self.visited_steps = []
        self.path = []
        self.nodes_visited = 0
