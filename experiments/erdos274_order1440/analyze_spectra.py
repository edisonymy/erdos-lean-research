from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from math import gcd
from pathlib import Path


ORDER = 1440
ROOT = Path(__file__).resolve().parent


def has_forbidden_triple(indices: tuple[int, ...]) -> bool:
    even = [d // 2 for d in indices if d % 2 == 0]
    return any(
        gcd(a, b) == gcd(a, c) == gcd(b, c) == 1
        for a, b, c in combinations(even, 3)
    )


@lru_cache(maxsize=None)
def analyze_spectrum(spectrum: tuple[int, ...]):
    values = tuple(d for d in spectrum if d > 2)
    weights = tuple(ORDER // d for d in values)
    suffix = [0] * (len(values) + 1)
    for i in range(len(values) - 1, -1, -1):
        suffix[i] = suffix[i + 1] + weights[i]

    total = 0
    unblocked: list[tuple[int, ...]] = []
    intersection: set[int] | None = None

    def visit(pos: int, remaining: int, chosen: tuple[int, ...]) -> None:
        nonlocal total, intersection
        if remaining == 0:
            total += 1
            chosen_set = set(chosen)
            intersection = chosen_set if intersection is None else intersection & chosen_set
            if not has_forbidden_triple(chosen):
                unblocked.append(chosen)
            return
        if pos == len(values) or remaining < 0 or suffix[pos] < remaining:
            return
        d = values[pos]
        w = weights[pos]
        if w <= remaining and all(gcd(d, old) > 1 for old in chosen):
            visit(pos + 1, remaining - w, chosen + (d,))
        visit(pos + 1, remaining, chosen)

    visit(0, ORDER, ())
    return total, tuple(unblocked), tuple(sorted(intersection or ()))


def main() -> None:
    rows = []
    source = ROOT / "solvable_subgroup_stats.tsv"
    for raw in source.read_text().splitlines():
        fields = raw.split("\t")
        group_id = int(fields[0])
        total_cosets = int(fields[3])
        spectrum = tuple(int(x) for x in fields[4].split(",") if x)
        rows.append((group_id, total_cosets, spectrum))

    no_sum = []
    all_forbidden = []
    survivors = []
    for group_id, total_cosets, spectrum in rows:
        total, unblocked, common = analyze_spectrum(spectrum)
        record = (group_id, total_cosets, total, len(unblocked), common, spectrum)
        if total == 0:
            no_sum.append(record)
        elif not unblocked:
            all_forbidden.append(record)
        else:
            survivors.append(record)

    print(f"groups={len(rows)} unique_spectra={analyze_spectrum.cache_info().misses}")
    print(f"no_sum={len(no_sum)} all_forbidden={len(all_forbidden)} survivors={len(survivors)}")
    print("smallest survivors:")
    for r in sorted(survivors, key=lambda x: (x[1], x[3], x[0]))[:30]:
        group_id, cosets, total, unblocked, common, spectrum = r
        print(
            f"{group_id}\tcosets={cosets}\tsums={total}\tunblocked={unblocked}"
            f"\tcommon={','.join(map(str, common))}\tspectrum={','.join(map(str, spectrum))}"
        )


if __name__ == "__main__":
    main()
