#!/usr/bin/env python3
"""
Sorting algorithms experiment.

Reads input sizes from a text file, generates multiple dataset shapes, runs several
sorting algorithms, and writes timings to CSV.

Usage:
  python sorting_experiment.py --sizes-file sizes.txt --out results.csv
"""

from __future__ import annotations

import argparse
import csv
import gc
import math
import random
import string
import time
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Sequence, Tuple


# ----------------------------
# Sorting algorithms
# ----------------------------

def bubble_sort(arr: List):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def insertion_sort(arr: List):
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def selection_sort(arr: List):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a


def shell_sort(arr: List):
    a = arr.copy()
    n = len(a)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                j -= gap
            a[j] = temp
        gap //= 2
    return a


def merge_sort(arr: List):
    a = arr.copy()
    if len(a) <= 1:
        return a

    def merge(left: List, right: List) -> List:
        out = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out

    def sort(xs: List) -> List:
        if len(xs) <= 1:
            return xs
        mid = len(xs) // 2
        return merge(sort(xs[:mid]), sort(xs[mid:]))

    return sort(a)


def quick_sort(arr: List):
    a = arr.copy()

    def median_of_three(lo: int, mid: int, hi: int):
        x, y, z = a[lo], a[mid], a[hi]
        if x <= y <= z or z <= y <= x:
            return mid
        if y <= x <= z or z <= x <= y:
            return lo
        return hi

    def partition(lo: int, hi: int) -> int:
        mid = (lo + hi) // 2
        pivot_index = median_of_three(lo, mid, hi)
        a[pivot_index], a[hi] = a[hi], a[pivot_index]
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        return i

    def sort(lo: int, hi: int):
        while lo < hi:
            p = partition(lo, hi)
            # recurse on smaller partition first (limits recursion depth)
            if p - lo < hi - p:
                sort(lo, p - 1)
                lo = p + 1
            else:
                sort(p + 1, hi)
                hi = p - 1

    if len(a) > 1:
        sort(0, len(a) - 1)
    return a


def heap_sort(arr: List):
    a = arr.copy()
    n = len(a)

    def sift_down(start: int, end: int):
        root = start
        while True:
            child = 2 * root + 1
            if child > end:
                break
            if child + 1 <= end and a[child] < a[child + 1]:
                child += 1
            if a[root] < a[child]:
                a[root], a[child] = a[child], a[root]
                root = child
            else:
                break

    # build max heap
    for start in range((n - 2) // 2, -1, -1):
        sift_down(start, n - 1)

    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(0, end - 1)

    return a


def counting_sort(arr: List[int]):
    if not arr:
        return []
    if any(not isinstance(x, int) for x in arr):
        raise TypeError("counting_sort only supports integers")
    mn = min(arr)
    mx = max(arr)
    k = mx - mn + 1
    counts = [0] * k
    for x in arr:
        counts[x - mn] += 1
    out = []
    for idx, c in enumerate(counts):
        if c:
            out.extend([idx + mn] * c)
    return out


def radix_sort(arr: List[int]):
    if not arr:
        return []
    if any(not isinstance(x, int) for x in arr):
        raise TypeError("radix_sort only supports integers")
    if any(x < 0 for x in arr):
        raise ValueError("radix_sort only supports non-negative integers")
    a = arr.copy()
    exp = 1
    base = 10
    max_val = max(a)
    while max_val // exp > 0:
        buckets = [0] * base
        for x in a:
            buckets[(x // exp) % base] += 1
        for i in range(1, base):
            buckets[i] += buckets[i - 1]
        out = [0] * len(a)
        for x in reversed(a):
            digit = (x // exp) % base
            buckets[digit] -= 1
            out[buckets[digit]] = x
        a = out
        exp *= base
    return a


def timsort(arr: List):
    return sorted(arr)


ALGORITHMS: Dict[str, Callable[[List], List]] = {
    "bubble": bubble_sort,
    "insertion": insertion_sort,
    "selection": selection_sort,
    "shell": shell_sort,
    "merge": merge_sort,
    "quick": quick_sort,
    "heap": heap_sort,
    "counting": counting_sort,
    "radix": radix_sort,
    "timsort": timsort,
}

COMPARISON_SORTS = {"bubble", "insertion", "selection", "shell", "merge", "quick", "heap", "timsort"}
INTEGER_ONLY = {"counting", "radix"}


# ----------------------------
# Data generation
# ----------------------------

def random_string(rng: random.Random, length: int = 8) -> str:
    alphabet = string.ascii_lowercase
    return "".join(rng.choice(alphabet) for _ in range(length))


def make_dataset(n: int, case: str, dtype: str, rng: random.Random):
    if dtype == "int":
        if case == "random":
            return [rng.randint(0, n * 10 if n > 0 else 10) for _ in range(n)]
        if case == "sorted":
            return list(range(n))
        if case == "reversed":
            return list(range(n, 0, -1))
        if case == "nearly":
            a = list(range(n))
            swaps = max(1, int(0.02 * n))
            for _ in range(swaps):
                i = rng.randrange(n)
                j = rng.randrange(n)
                a[i], a[j] = a[j], a[i]
            return a
        if case == "half":
            a = list(range(n))
            for i in range(n // 2, n):
                a[i] = rng.randint(0, n * 10 if n > 0 else 10)
            return a
        if case == "flat":
            values = [rng.randint(0, 5) for _ in range(max(1, n // 10))]
            return [rng.choice(values) for _ in range(n)]
    elif dtype == "float":
        if case == "random":
            return [rng.random() * (n * 10 if n > 0 else 10) for _ in range(n)]
        if case == "sorted":
            return [float(i) for i in range(n)]
        if case == "reversed":
            return [float(i) for i in range(n, 0, -1)]
        if case == "nearly":
            a = [float(i) for i in range(n)]
            swaps = max(1, int(0.02 * n))
            for _ in range(swaps):
                i = rng.randrange(n)
                j = rng.randrange(n)
                a[i], a[j] = a[j], a[i]
            return a
        if case == "half":
            a = [float(i) for i in range(n)]
            for i in range(n // 2, n):
                a[i] = rng.random() * (n * 10 if n > 0 else 10)
            return a
        if case == "flat":
            values = [round(rng.random() * 5, 3) for _ in range(max(1, n // 10))]
            return [rng.choice(values) for _ in range(n)]
    elif dtype == "str":
        if case == "random":
            return [random_string(rng, 8) for _ in range(n)]
        if case == "sorted":
            return [f"{i:08d}" for i in range(n)]
        if case == "reversed":
            return [f"{i:08d}" for i in range(n, 0, -1)]
        if case == "nearly":
            a = [f"{i:08d}" for i in range(n)]
            swaps = max(1, int(0.02 * n))
            for _ in range(swaps):
                i = rng.randrange(n)
                j = rng.randrange(n)
                a[i], a[j] = a[j], a[i]
            return a
        if case == "half":
            a = [f"{i:08d}" for i in range(n)]
            for i in range(n // 2, n):
                a[i] = random_string(rng, 8)
            return a
        if case == "flat":
            values = [random_string(rng, 4) for _ in range(max(1, n // 10))]
            return [rng.choice(values) for _ in range(n)]
    raise ValueError(f"Unsupported combination: case={case!r}, dtype={dtype!r}")


# ----------------------------
# Benchmarking helpers
# ----------------------------

def read_sizes(path: str) -> List[int]:
    sizes: List[int] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for token in line.replace(",", " ").split():
                sizes.append(int(token))
    return sizes


def is_supported(algorithm: str, dtype: str) -> bool:
    if algorithm in INTEGER_ONLY:
        return dtype == "int"
    return True


def should_run(algorithm: str, n: int, quadratic_limit: int, counting_limit: int) -> bool:
    if algorithm in {"bubble", "insertion", "selection"}:
        return n <= quadratic_limit
    if algorithm == "shell":
        return n <= max(quadratic_limit * 10, 200_000)
    if algorithm == "merge":
        return n <= max(counting_limit, 5_000_000)
    if algorithm == "quick":
        return n <= max(counting_limit, 5_000_000)
    if algorithm == "heap":
        return n <= max(counting_limit, 5_000_000)
    if algorithm == "counting":
        return n <= counting_limit
    if algorithm == "radix":
        return n <= counting_limit
    if algorithm == "timsort":
        return True
    return True


def repeat_count(n: int, min_repeats: int, max_repeats: int) -> int:
    if n <= 0:
        return min_repeats
    repeats = max(min_repeats, min(max_repeats, 100_000 // n))
    return repeats


def verify_sorted(original, result) -> bool:
    return result == sorted(original)


@dataclass
class ResultRow:
    size: int
    case: str
    dtype: str
    algorithm: str
    repeats: int
    avg_seconds: float
    best_seconds: float
    status: str


def run_benchmark(
    sizes: Sequence[int],
    cases: Sequence[str],
    dtypes: Sequence[str],
    algorithms: Sequence[str],
    min_repeats: int,
    max_repeats: int,
    quadratic_limit: int,
    counting_limit: int,
    seed: int,
) -> List[ResultRow]:
    rows: List[ResultRow] = []
    rng = random.Random(seed)

    for n in sizes:
        for case in cases:
            for dtype in dtypes:
                master = make_dataset(n, case, dtype, rng)

                for algo in algorithms:
                    if not is_supported(algo, dtype):
                        rows.append(ResultRow(n, case, dtype, algo, 0, math.nan, math.nan, "unsupported"))
                        continue
                    if not should_run(algo, n, quadratic_limit, counting_limit):
                        rows.append(ResultRow(n, case, dtype, algo, 0, math.nan, math.nan, "skipped"))
                        continue

                    fn = ALGORITHMS[algo]
                    reps = repeat_count(n, min_repeats, max_repeats)

                    # For huge inputs, keep work bounded.
                    if n >= 200_000 and algo in {"bubble", "insertion", "selection", "shell"}:
                        reps = 1

                    times: List[float] = []
                    ok = True
                    gc_was_enabled = gc.isenabled()
                    gc.disable()
                    try:
                        # warm-up run
                        try:
                            _ = fn(master)
                        except Exception:
                            pass

                        for _ in range(reps):
                            data = master.copy()
                            t0 = time.perf_counter()
                            result = fn(data)
                            t1 = time.perf_counter()
                            times.append(t1 - t0)
                            if not verify_sorted(master, result):
                                ok = False
                                break
                    except MemoryError:
                        rows.append(ResultRow(n, case, dtype, algo, reps, math.nan, math.nan, "memory_error"))
                        continue
                    except Exception as exc:
                        rows.append(ResultRow(n, case, dtype, algo, reps, math.nan, math.nan, f"error:{type(exc).__name__}"))
                        continue
                    finally:
                        if gc_was_enabled:
                            gc.enable()

                    if not times:
                        rows.append(ResultRow(n, case, dtype, algo, reps, math.nan, math.nan, "failed"))
                    else:
                        status = "ok" if ok else "incorrect"
                        rows.append(
                            ResultRow(
                                size=n,
                                case=case,
                                dtype=dtype,
                                algorithm=algo,
                                repeats=reps,
                                avg_seconds=sum(times) / len(times),
                                best_seconds=min(times),
                                status=status,
                            )
                        )

    return rows


def write_csv(rows: Sequence[ResultRow], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["size", "case", "dtype", "algorithm", "repeats", "avg_seconds", "best_seconds", "status"])
        for r in rows:
            writer.writerow([r.size, r.case, r.dtype, r.algorithm, r.repeats, r.avg_seconds, r.best_seconds, r.status])


def parse_args():
    p = argparse.ArgumentParser(description="Sorting algorithms experiment")
    p.add_argument("--sizes-file", default="sizes.txt", help="Text file containing sizes, one per line or separated by spaces/commas")
    p.add_argument("--out", default="results.csv", help="Output CSV file")
    p.add_argument("--cases", default="random,sorted,reversed,nearly,half,flat", help="Comma-separated dataset cases")
    p.add_argument("--dtypes", default="int,float,str", help="Comma-separated data types")
    p.add_argument(
        "--algorithms",
        default="bubble,insertion,selection,shell,merge,quick,heap,counting,radix,timsort",
        help="Comma-separated algorithms",
    )
    p.add_argument("--min-repeats", type=int, default=3)
    p.add_argument("--max-repeats", type=int, default=5000)
    p.add_argument("--quadratic-limit", type=int, default=5000, help="Do not run O(n^2) sorts above this size")
    p.add_argument("--counting-limit", type=int, default=1_000_000, help="Do not run counting/radix above this size")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main():
    args = parse_args()
    sizes = read_sizes(args.sizes_file)
    cases = [c.strip() for c in args.cases.split(",") if c.strip()]
    dtypes = [d.strip() for d in args.dtypes.split(",") if d.strip()]
    algorithms = [a.strip() for a in args.algorithms.split(",") if a.strip()]

    unknown = [a for a in algorithms if a not in ALGORITHMS]
    if unknown:
        raise SystemExit(f"Unknown algorithm(s): {', '.join(unknown)}")

    rows = run_benchmark(
        sizes=sizes,
        cases=cases,
        dtypes=dtypes,
        algorithms=algorithms,
        min_repeats=args.min_repeats,
        max_repeats=args.max_repeats,
        quadratic_limit=args.quadratic_limit,
        counting_limit=args.counting_limit,
        seed=args.seed,
    )
    write_csv(rows, args.out)
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
