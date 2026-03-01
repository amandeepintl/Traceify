"""
sorting.py — Sorting algorithm engines for Traceify.
Provides step-by-step snapshots for animation.
"""

import random
from dataclasses import dataclass, field


@dataclass
class SortStep:
    array: list[int]
    comparisons: int
    swaps: int
    highlighted: list[int] = field(default_factory=list)   # indices being compared/swapped
    pivot_idx: int | None = None                            # for Quick Sort
    sorted_indices: list[int] = field(default_factory=list) # finalized positions


# ------------------------------------------------------------------ #
#  Bubble Sort                                                         #
# ------------------------------------------------------------------ #

def bubble_sort_steps(arr: list[int]) -> list[SortStep]:
    """Return all animation steps for Bubble Sort."""
    a = arr[:]
    steps: list[SortStep] = []
    n = len(a)
    comparisons = 0
    swaps = 0
    sorted_indices: list[int] = []

    for i in range(n):
        for j in range(n - i - 1):
            comparisons += 1
            steps.append(SortStep(
                array=a[:],
                comparisons=comparisons,
                swaps=swaps,
                highlighted=[j, j + 1],
                sorted_indices=sorted_indices[:],
            ))
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                steps.append(SortStep(
                    array=a[:],
                    comparisons=comparisons,
                    swaps=swaps,
                    highlighted=[j, j + 1],
                    sorted_indices=sorted_indices[:],
                ))
        sorted_indices.append(n - i - 1)

    # Final state — all sorted
    steps.append(SortStep(
        array=a[:],
        comparisons=comparisons,
        swaps=swaps,
        highlighted=[],
        sorted_indices=list(range(n)),
    ))
    return steps


# ------------------------------------------------------------------ #
#  Quick Sort                                                          #
# ------------------------------------------------------------------ #

def quick_sort_steps(arr: list[int]) -> list[SortStep]:
    """Return all animation steps for Quick Sort (Lomuto partition)."""
    a = arr[:]
    steps: list[SortStep] = []
    comparisons = 0
    swaps = 0
    sorted_indices: list[int] = []

    def _partition(lo: int, hi: int) -> int:
        nonlocal comparisons, swaps
        pivot = a[hi]
        i = lo - 1
        for j in range(lo, hi):
            comparisons += 1
            steps.append(SortStep(
                array=a[:],
                comparisons=comparisons,
                swaps=swaps,
                highlighted=[j, hi],
                pivot_idx=hi,
                sorted_indices=sorted_indices[:],
            ))
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
                swaps += 1
                steps.append(SortStep(
                    array=a[:],
                    comparisons=comparisons,
                    swaps=swaps,
                    highlighted=[i, j],
                    pivot_idx=hi,
                    sorted_indices=sorted_indices[:],
                ))
        a[i + 1], a[hi] = a[hi], a[i + 1]
        swaps += 1
        steps.append(SortStep(
            array=a[:],
            comparisons=comparisons,
            swaps=swaps,
            highlighted=[i + 1, hi],
            pivot_idx=i + 1,
            sorted_indices=sorted_indices[:],
        ))
        return i + 1

    def _quick(lo: int, hi: int):
        if lo < hi:
            p = _partition(lo, hi)
            sorted_indices.append(p)
            _quick(lo, p - 1)
            _quick(p + 1, hi)

    _quick(0, len(a) - 1)

    steps.append(SortStep(
        array=a[:],
        comparisons=comparisons,
        swaps=swaps,
        highlighted=[],
        sorted_indices=list(range(len(a))),
    ))
    return steps


# ------------------------------------------------------------------ #
#  Helpers                                                             #
# ------------------------------------------------------------------ #

def generate_array(n: int = 40, seed: int = 42) -> list[int]:
    """Generate a reproducible random array of length n."""
    rng = random.Random(seed)
    return [rng.randint(5, 100) for _ in range(n)]
