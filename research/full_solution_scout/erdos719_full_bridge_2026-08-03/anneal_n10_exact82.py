#!/usr/bin/env python3
"""Bounded 38-missing-edge local search for a full #719 counterexample."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import time
from pathlib import Path

V = tuple(range(10))
TRIPLES = tuple(itertools.combinations(V, 3))
BLOCKS = tuple(itertools.combinations(V, 4))
REQ = tuple(frozenset(itertools.combinations(b, 3)) for b in BLOCKS)


def evaluate(missing: set[tuple[int, int, int]]) -> tuple[int, int, list[int]]:
    clean = [i for i, req in enumerate(REQ) if req.isdisjoint(missing)]
    bad = 0
    for i, j, k in itertools.combinations(clean, 3):
        if (
            len(set(BLOCKS[i]) & set(BLOCKS[j])) <= 2
            and len(set(BLOCKS[i]) & set(BLOCKS[k])) <= 2
            and len(set(BLOCKS[j]) & set(BLOCKS[k])) <= 2
        ):
            bad += 1
    return bad, len(clean), clean


def run(seed: int, steps: int, seconds: float, outdir: Path) -> None:
    rng = random.Random(seed)
    missing = set(rng.sample(TRIPLES, 38))
    bad, q, clean = evaluate(missing)
    best = (bad, q, sorted(missing), clean)
    started = time.time()
    accepted = 0
    for step in range(1, steps + 1):
        elapsed = time.time() - started
        if elapsed >= seconds:
            break
        old = rng.choice(tuple(missing))
        new = rng.choice(tuple(e for e in TRIPLES if e not in missing))
        trial = set(missing)
        trial.remove(old)
        trial.add(new)
        nb, nq, nc = evaluate(trial)
        # Number of forbidden three-packings is primary.  The clean count is a
        # gentle secondary guide toward the necessary q<=14 design regime.
        score = bad + 0.02 * q
        nscore = nb + 0.02 * nq
        temperature = max(0.05, 8.0 * (1.0 - step / steps))
        if nscore <= score or rng.random() < math.exp((score - nscore) / temperature):
            missing, bad, q, clean = trial, nb, nq, nc
            accepted += 1
        if (bad, q) < best[:2]:
            best = (bad, q, sorted(missing), clean)
            if bad == 0:
                break
        if step % 50000 == 0:
            # Reheat by restarting from the best configuration with a few
            # random swaps; this avoids a single frozen basin.
            missing = set(best[2])
            for _ in range(3):
                old = rng.choice(tuple(missing))
                missing.remove(old)
                missing.add(rng.choice(tuple(e for e in TRIPLES if e not in missing)))
            bad, q, clean = evaluate(missing)

    outdir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "CANDIDATE" if best[0] == 0 else "BOUNDED_NO_COUNTEREXAMPLE",
        "seed": seed,
        "steps_requested": steps,
        "elapsed_seconds": time.time() - started,
        "accepted_moves": accepted,
        "best_forbidden_three_packings": best[0],
        "best_clean_tetrahedra": best[1],
        "missing_triples": [list(e) for e in best[2]],
        "clean_tetrahedra": [list(BLOCKS[i]) for i in best[3]],
    }
    (outdir / f"seed_{seed}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--steps", type=int, default=2000000)
    p.add_argument("--seconds", type=float, default=300)
    p.add_argument("--outdir", type=Path, required=True)
    a = p.parse_args()
    run(a.seed, a.steps, a.seconds, a.outdir)
