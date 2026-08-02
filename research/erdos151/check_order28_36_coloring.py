"""Exhaustive checks for the two finite coloring lemmas in order28_36.md.

Uses only the Python standard library.  This is an independent finite sanity
check; the note also includes direct analytic proofs of both lemmas.
"""

from __future__ import annotations

from itertools import combinations, product


RED = 0
BLUE = 1


def edges(n: int) -> list[tuple[int, int]]:
    return list(combinations(range(n), 2))


def triangles(n: int) -> list[tuple[tuple[int, int], ...]]:
    return [tuple(combinations(t, 2)) for t in combinations(range(n), 3)]


def edge_key(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def has_mono_triangle(n: int, coloring: dict[tuple[int, int], int]) -> bool:
    for tri in triangles(n):
        if all(e in coloring for e in tri):
            colors = {coloring[e] for e in tri}
            if len(colors) == 1:
                return True
    return False


def cone_assignment_exists(
    n: int, coloring: dict[tuple[int, int], int]
) -> bool:
    for spokes in product((RED, BLUE), repeat=n):
        good = True
        for (u, v), color in coloring.items():
            if spokes[u] == color and spokes[v] == color:
                good = False
                break
        if good:
            return True
    return False


def check_cone_lemma() -> int:
    cases = 0
    for n in range(5):
        all_edges = edges(n)
        for present_bits in product((0, 1), repeat=len(all_edges)):
            present = [e for e, bit in zip(all_edges, present_bits) if bit]
            if n == 4 and len(present) == 6:
                continue  # The explicitly excluded K4 link.
            for colors in product((RED, BLUE), repeat=len(present)):
                coloring = dict(zip(present, colors))
                if has_mono_triangle(n, coloring):
                    continue
                cases += 1
                assert cone_assignment_exists(n, coloring), (n, coloring)
    return cases


def good_k4_extension_exists(
    prescriptions: dict[tuple[int, int], int]
) -> bool:
    all_edges = edges(4)
    for colors in product((RED, BLUE), repeat=6):
        coloring = dict(zip(all_edges, colors))
        if any(coloring[e] != c for e, c in prescriptions.items()):
            continue
        if not has_mono_triangle(4, coloring):
            return True
    return False


def check_matching_prescriptions() -> int:
    all_edges = edges(4)
    matchings: list[tuple[tuple[int, int], ...]] = [()]
    matchings.extend((e,) for e in all_edges)
    matchings.extend(
        (e, f)
        for e, f in combinations(all_edges, 2)
        if set(e).isdisjoint(f)
    )
    cases = 0
    for matching in matchings:
        for colors in product((RED, BLUE), repeat=len(matching)):
            prescriptions = dict(zip(matching, colors))
            cases += 1
            assert good_k4_extension_exists(prescriptions), prescriptions
    return cases


def main() -> None:
    cone_cases = check_cone_lemma()
    prescription_cases = check_matching_prescriptions()
    print(f"cone lemma: VERIFIED ({cone_cases} colored-link cases)")
    print(
        "matching prescriptions: VERIFIED "
        f"({prescription_cases} prescription cases)"
    )


if __name__ == "__main__":
    main()
