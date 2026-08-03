#!/usr/bin/env python3
"""Rank-two EDM screening for q=5 colour patterns from the companion CSP.

For each edge colouring, let s_c be the squared length of colour c and form
the complete squared-distance matrix D(s).  The centred Gram matrix

    B(s) = -1/2 J D(s) J

must be positive semidefinite of rank two.  We normalize the shortest colour
to squared length one and parameterize the remaining known strict orders.
Differential evolution plus least-squares is only a candidate screen; an
apparent zero must be reconstructed and checked exactly.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, least_squares


N = 10
EDGES = tuple(itertools.combinations(range(N), 2))
J = np.eye(N) - np.ones((N, N)) / N


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def squared_lengths(parameters: np.ndarray, record: dict) -> np.ndarray:
    """Respect the two cap endpoint orders and the global extrema.

    We construct one positive value for each colour by assigning unconstrained
    positive increments to the total order selected outside this function.
    The chosen order is stored temporarily in record['_length_order'].
    """
    order = record["_length_order"]
    values = np.empty(5)
    values[order[0]] = 1.0
    current = 1.0
    for colour, log_gap in zip(order[1:], parameters):
        current += math.exp(float(log_gap))
        values[colour] = current
    return values


def compatible_length_orders(record: dict) -> list[tuple[int, ...]]:
    shortest = int(record["shortest_colour"])
    longest = int(record["longest_colour"])
    order0 = tuple(int(c) for c in record["cap_order_at_0"])
    order4 = tuple(int(c) for c in record["cap_order_at_4"])
    answer = []
    for order in itertools.permutations(range(5)):
        if order[0] != shortest or order[-1] != longest:
            continue
        rank = {c: i for i, c in enumerate(order)}
        if all(rank[a] < rank[b] for a, b in zip(order0, order0[1:])) and all(
            rank[a] < rank[b] for a, b in zip(order4, order4[1:])
        ):
            answer.append(order)
    return answer


def gram(parameters: np.ndarray, record: dict) -> np.ndarray:
    lengths = squared_lengths(parameters, record)
    D = np.zeros((N, N))
    for e, colour in zip(EDGES, record["edge_colours"]):
        i, j = e
        D[i, j] = D[j, i] = lengths[int(colour)]
    return -0.5 * J @ D @ J


def tail_eigenvalues(parameters: np.ndarray, record: dict) -> np.ndarray:
    values = np.linalg.eigvalsh(gram(parameters, record))
    scale = max(float(np.linalg.norm(values)), 1e-30)
    # For a PSD rank-two Gram matrix, the eight smallest eigenvalues vanish.
    # One zero is automatic from centering, but retaining it is harmless.
    return values[:-2] / scale


def objective(parameters: np.ndarray, record: dict) -> float:
    residual = tail_eigenvalues(parameters, record)
    return float(np.dot(residual, residual))


def screen_record(record: dict, seeds: int, maxiter: int) -> dict:
    trials = []
    for order_index, order in enumerate(compatible_length_orders(record)):
        working = dict(record)
        working["_length_order"] = order
        for seed in range(seeds):
            result = differential_evolution(
                objective,
                [(-8.0, 8.0)] * 4,
                args=(working,),
                seed=982_500_000 + 1000 * order_index + seed,
                maxiter=maxiter,
                popsize=12,
                tol=1e-11,
                atol=1e-14,
                polish=False,
                updating="immediate",
                workers=1,
            )
            refined = least_squares(
                tail_eigenvalues,
                result.x,
                bounds=(-12.0, 12.0),
                args=(working,),
                max_nfev=5000,
                ftol=1e-14,
                xtol=1e-14,
                gtol=1e-14,
            )
            parameters = refined.x if objective(refined.x, working) <= objective(result.x, working) else result.x
            B = gram(parameters, working)
            eigenvalues = np.linalg.eigvalsh(B)
            lengths = squared_lengths(parameters, working)
            trials.append({
                "length_order": list(order),
                "seed": seed,
                "normalized_rank2_residual": objective(parameters, working),
                "parameters": parameters.tolist(),
                "squared_lengths": lengths.tolist(),
                "gram_eigenvalues": eigenvalues.tolist(),
                "positive_semidefinite_tolerance_1e_8": bool(eigenvalues[0] >= -1e-8 * max(1.0, eigenvalues[-1])),
                "numerical_rank_tolerance_1e_8": int(np.sum(eigenvalues > 1e-8 * max(1.0, eigenvalues[-1]))),
            })
    trials.sort(key=lambda item: item["normalized_rank2_residual"])
    return {
        "edge_colours": record["edge_colours"],
        "canonical_dihedral": record["canonical_dihedral"],
        "compatible_total_length_orders": len(compatible_length_orders(record)),
        "trials": trials,
        "best": trials[0] if trials else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("patterns", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--maxiter", type=int, default=500)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("q5_edm_screen.json"))
    args = parser.parse_args()

    source = json.loads(args.patterns.read_text(encoding="utf-8"))
    records = source["retained"][: args.limit]
    screened = []
    for index, record in enumerate(records):
        result = screen_record(record, args.seeds, args.maxiter)
        result["index"] = index
        screened.append(result)
        best = result["best"]
        residual_text = "NO_COMPATIBLE_TOTAL_ORDER" if best is None else f"{best['normalized_rank2_residual']:.12g}"
        print(
            f"pattern={index} orders={result['compatible_total_length_orders']} "
            f"residual={residual_text}",
            flush=True,
        )
    screened.sort(key=lambda item: float("inf") if item["best"] is None else item["best"]["normalized_rank2_residual"])
    payload = {
        "status": "NUMERICAL_EDM_SCREEN_ONLY",
        "source": str(args.patterns),
        "source_sha256": hashlib.sha256(args.patterns.read_bytes()).hexdigest(),
        "patterns_screened": len(screened),
        "seeds_per_length_order": args.seeds,
        "maxiter": args.maxiter,
        "patterns": screened,
    }
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("sha256", hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
