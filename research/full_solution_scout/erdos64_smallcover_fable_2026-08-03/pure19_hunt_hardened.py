#!/usr/bin/env python3
"""Crash-resumable, audited sigma=19 C16/C32 hunt.

The base CNF is still built by sat_search.py.  This wrapper differs from the
handover runner in four operational ways:

* it resolves every path relative to this packet;
* it independently audits all persisted cycle blocks before loading them;
* it keeps one incremental CaDiCaL instance alive across CEGAR rounds;
* on incremental UNSAT it freezes the exact final CNF and stops at the
  explicit `SOLVER_UNSAT` evidence class.  Proof generation is a separate
  supervised step so a detached writer cannot silently outlive this process.

A SAT survivor is frozen immediately.  Public claims remain out of scope for
this script; a candidate still requires the campaign's external priority and
recognition protocol.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from collections import deque
from pathlib import Path

from pysat.solvers import Cadical195

import audit_pure19_blocks
import sat_search


SIGMA = 19
CAP = 512
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BLOCKS_PATH = HERE / "blocks_pure19.jsonl"
AUDIT_PATH = HERE / "audit_pure19_blocks.json"
STATUS_PATH = HERE / "pure19_hardened_status.json"
LOCK_PATH = HERE / "pure19_hardened.lock"
VERIFY_A = HERE / "checker_a.py"
VERIFY_B = ROOT / "experiments" / "erdos64" / "verify_graph.py"
CADICAL_WIN = ROOT / "third_party" / "cadical" / "cadical-linux"
DRAT_TRIM_WIN = ROOT / "third_party" / "drat-trim" / "drat-trim"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def atomic_json(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def write_dimacs(path: Path, top: int, clauses: list[list[int]]) -> None:
    with path.open("w", encoding="ascii", newline="\n") as stream:
        stream.write(f"p cnf {top} {len(clauses)}\n")
        for clause in clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    rest = resolved.as_posix().split(":", 1)[1].lstrip("/")
    return f"/mnt/host/{drive}/{rest}"


def bfs_dist(adjacency: list[list[int]], source: int) -> list[int]:
    distance = [-1] * len(adjacency)
    distance[source] = 0
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbor in adjacency[vertex]:
            if distance[neighbor] < 0:
                distance[neighbor] = distance[vertex] + 1
                queue.append(neighbor)
    return distance


def find_cycles(adjacency: list[list[int]], length: int, cap: int) -> list[list[int]]:
    """Enumerate up to cap exact simple cycles, deduplicated by edge set."""

    n = len(adjacency)
    adjacency_sets = [set(row) for row in adjacency]
    found: list[list[int]] = []
    seen_edges: set[frozenset[tuple[int, int]]] = set()

    for root in range(n):
        if len(found) >= cap:
            break
        distance = bfs_dist(adjacency, root)
        used = [False] * n
        used[root] = True
        path = [root]

        def visit(vertex: int, edges_used: int) -> None:
            if len(found) >= cap:
                return
            if edges_used == length - 1:
                if root in adjacency_sets[vertex]:
                    edge_key = frozenset(
                        (min(a, b), max(a, b))
                        for a, b in zip(path, path[1:] + path[:1])
                    )
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        found.append(list(path))
                return
            for neighbor in adjacency[vertex]:
                if neighbor <= root or used[neighbor]:
                    continue
                remaining = length - (edges_used + 1)
                if distance[neighbor] < 0 or distance[neighbor] > remaining:
                    continue
                used[neighbor] = True
                path.append(neighbor)
                visit(neighbor, edges_used + 1)
                path.pop()
                used[neighbor] = False

        visit(root, 0)
    return found


def clause_for_cycle(cycle: list[int], xvars: dict[tuple[int, int], int]) -> list[int]:
    audit_pure19_blocks.expected_clause(cycle)  # structural check, independent mapping
    clause = []
    for a, b in zip(cycle, cycle[1:] + cycle[:1]):
        point, line_vertex = (a, b) if a < SIGMA else (b, a)
        clause.append(-xvars[(point, line_vertex - SIGMA)])
    return clause


def certify(cnf_path: Path, drat_path: Path, prefix: str) -> dict:
    solve_log = HERE / f"{prefix}.cadical.log"
    check_log = HERE / f"{prefix}.drat-trim.log"
    command = [
        "wsl.exe", "-e", wsl_path(CADICAL_WIN), "-q",
        wsl_path(cnf_path), wsl_path(drat_path),
    ]
    solved = subprocess.run(command, capture_output=True, text=True)
    solve_text = (solved.stdout or "") + (solved.stderr or "")
    solve_log.write_text(solve_text, encoding="utf-8", errors="replace")
    if solved.returncode != 20:
        return {
            "status": "CERT_SOLVER_FAILED",
            "returncode": solved.returncode,
            "solve_log": solve_log.name,
        }
    checked = subprocess.run(
        ["wsl.exe", "-e", wsl_path(DRAT_TRIM_WIN), wsl_path(cnf_path), wsl_path(drat_path)],
        capture_output=True,
        text=True,
    )
    check_text = (checked.stdout or "") + (checked.stderr or "")
    check_log.write_text(check_text, encoding="utf-8", errors="replace")
    verified = checked.returncode == 0 and "s VERIFIED" in check_text
    return {
        "status": "CERTIFIED_UNSAT" if verified else "CERT_CHECK_FAILED",
        "cadical_returncode": solved.returncode,
        "drat_trim_returncode": checked.returncode,
        "verified": verified,
        "cnf": cnf_path.name,
        "cnf_sha256": sha256(cnf_path),
        "drat": drat_path.name,
        "drat_sha256": sha256(drat_path) if drat_path.exists() else None,
        "solve_log": solve_log.name,
        "check_log": check_log.name,
    }


def verify_candidate(candidate: Path) -> dict:
    result = {"candidate": candidate.name, "candidate_sha256": sha256(candidate)}
    for label, checker in (("checker_a", VERIFY_A), ("verify_graph", VERIFY_B)):
        completed = subprocess.run([sys.executable, str(checker), str(candidate)], capture_output=True, text=True)
        log = candidate.with_suffix(candidate.suffix + f".{label}.log")
        log.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8")
        result[label] = {"returncode": completed.returncode, "log": log.name}
    result["dual_verified"] = all(result[label]["returncode"] == 0 for label in ("checker_a", "verify_graph"))
    return result


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def acquire_lock() -> None:
    try:
        descriptor = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        try:
            old_pid = int(LOCK_PATH.read_text(encoding="ascii").strip())
        except (OSError, ValueError):
            old_pid = -1
        if pid_alive(old_pid):
            raise SystemExit(f"refusing concurrent run; live lock PID {old_pid}") from exc
        LOCK_PATH.unlink()
        descriptor = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(descriptor, "w", encoding="ascii") as stream:
        stream.write(f"{os.getpid()}\n")


def run(time_budget: float, cap: int = CAP) -> str:
    acquire_lock()
    started = time.time()
    try:
        audit = audit_pure19_blocks.audit(BLOCKS_PATH)
        atomic_json(AUDIT_PATH, audit)
        if audit["status"] != "PASS":
            raise RuntimeError(f"persisted block audit failed: {audit['errors'][:3]}")

        records = [json.loads(line) for line in BLOCKS_PATH.read_text(encoding="utf-8").splitlines()]
        block_clauses = [record["clause"] for record in records]
        known_clauses = {tuple(sorted(clause)) for clause in block_clauses}

        pool, xvars, used_vars, max_lines, base_clauses = sat_search.build(
            SIGMA, verbose=False, symmetry=True
        )
        if max_lines != audit_pure19_blocks.M:
            raise AssertionError((max_lines, audit_pure19_blocks.M))
        for point in range(SIGMA):
            for line in range(max_lines):
                if xvars[(point, line)] != audit_pure19_blocks.xvar(point, line):
                    raise AssertionError(f"X mapping drift at {(point, line)}")

        all_clauses = list(base_clauses) + block_clauses
        solver = Cadical195(bootstrap_with=all_clauses)
        rounds = 0
        start_payload = {
            "status": "RUNNING",
            "event": "START",
            "pid": os.getpid(),
            "base_clauses": len(base_clauses),
            "resumed_blocks": len(records),
            "blocks": len(records),
            "block_sha256": sha256(BLOCKS_PATH),
            "vars": pool.top,
            "seconds": round(time.time() - started, 1),
        }
        atomic_json(STATUS_PATH, start_payload)
        print(json.dumps(start_payload), flush=True)

        while True:
            elapsed = time.time() - started
            if elapsed >= time_budget:
                payload = {
                    "status": "TIMEOUT",
                    "rounds_this_run": rounds,
                    "blocks": len(records),
                    "seconds": round(elapsed, 1),
                    "block_sha256": sha256(BLOCKS_PATH),
                }
                atomic_json(STATUS_PATH, payload)
                print(json.dumps(payload), flush=True)
                return "TIMEOUT"

            rounds += 1
            sat = solver.solve()
            if not sat:
                stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
                prefix = f"pure19_final_{stamp}"
                cnf_path = HERE / f"{prefix}.cnf"
                drat_path = HERE / f"{prefix}.drat"
                write_dimacs(cnf_path, pool.top, all_clauses)
                payload = {
                    "status": "SOLVER_UNSAT",
                    "rounds_this_run": rounds,
                    "blocks": len(records),
                    "seconds": round(time.time() - started, 1),
                    "cnf": cnf_path.name,
                    "cnf_sha256": sha256(cnf_path),
                }
                atomic_json(STATUS_PATH, payload)
                print(json.dumps(payload), flush=True)
                payload["certification"] = {
                    "status": "PENDING_SUPERVISED_REPLAY",
                    "suggested_drat": drat_path.name,
                }
                atomic_json(STATUS_PATH, payload)
                return "SOLVER_UNSAT"

            model = solver.get_model()
            lines = sat_search.decode(model, xvars, used_vars, SIGMA, max_lines)
            if any(original_index != i for i, (original_index, _) in enumerate(lines)):
                raise AssertionError("used lines are not the required prefix")
            n, adjacency, edges = sat_search.incidence_graph(SIGMA, lines)

            bad_length = None
            bad_cycles: list[list[int]] = []
            for length in (4, 8, 16, 32):
                cycles = find_cycles(adjacency, length, cap)
                if cycles:
                    bad_length, bad_cycles = length, cycles
                    break

            if bad_length is None:
                stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
                candidate = HERE / f"CANDIDATE_pure19_{stamp}.json"
                payload = {
                    "status": "CANDIDATE",
                    "sigma": SIGMA,
                    "n": n,
                    "m_lines": len(lines),
                    "lines": [sorted(line) for _, line in lines],
                    "edges": edges,
                    "blocks": len(records),
                    "seconds": round(time.time() - started, 1),
                }
                atomic_json(candidate, payload)
                verification = verify_candidate(candidate)
                status = {
                    "status": "CANDIDATE_DUAL_VERIFIED" if verification["dual_verified"] else "CANDIDATE_CHECK_FAILED",
                    "candidate": candidate.name,
                    "verification": verification,
                }
                atomic_json(STATUS_PATH, status)
                print(json.dumps(status), flush=True)
                return status["status"]

            if bad_length in (4, 8):
                payload = {
                    "status": "STATIC_LEAK",
                    "length": bad_length,
                    "cycle": bad_cycles[0],
                    "round": rounds,
                }
                atomic_json(STATUS_PATH, payload)
                print(json.dumps(payload), flush=True)
                return "STATIC_LEAK"

            appended = []
            with BLOCKS_PATH.open("a", encoding="utf-8", newline="\n") as stream:
                for cycle in bad_cycles:
                    clause = clause_for_cycle(cycle, xvars)
                    key = tuple(sorted(clause))
                    if key in known_clauses:
                        raise AssertionError("solver model violates an already-loaded cycle block")
                    record = {"cycle": cycle, "clause": clause}
                    stream.write(json.dumps(record, separators=(",", ":")) + "\n")
                    records.append(record)
                    appended.append(clause)
                    known_clauses.add(key)
                stream.flush()
                os.fsync(stream.fileno())

            for clause in appended:
                solver.add_clause(clause)
                all_clauses.append(clause)

            payload = {
                "status": "RUNNING",
                "rounds_this_run": rounds,
                "last_bad_length": bad_length,
                "added": len(appended),
                "blocks": len(records),
                "model_order": n,
                "model_lines": len(lines),
                "seconds": round(time.time() - started, 1),
                "block_sha256": sha256(BLOCKS_PATH),
            }
            atomic_json(STATUS_PATH, payload)
            print(json.dumps(payload), flush=True)
    finally:
        try:
            LOCK_PATH.unlink()
        except FileNotFoundError:
            pass


def main(argv: list[str]) -> int:
    budget = float(argv[1]) if len(argv) > 1 else 14_400.0
    cap = int(argv[2]) if len(argv) > 2 else CAP
    outcome = run(budget, cap)
    return 0 if outcome in {"TIMEOUT", "SOLVER_UNSAT", "CERTIFIED_UNSAT", "CANDIDATE_DUAL_VERIFIED"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
