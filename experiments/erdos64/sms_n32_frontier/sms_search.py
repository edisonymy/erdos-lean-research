"""Reproduce the bounded SMS/Glasgow searches recorded in results.json."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import time
from pathlib import Path

from pysms.graph_builder import GraphEncodingBuilder


def write_cycles(path: Path) -> None:
    with path.open("w") as fh:
        for k in (4, 8, 16, 32):
            edges = []
            for i in range(k):
                edges.extend((i, (i + 1) % k))
            fh.write(f"{k} " + " ".join(map(str, edges)) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--high", type=int, choices=(4, 6, 8, 10, 12))
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    n, h = 32, args.high
    args.output.mkdir(parents=True, exist_ok=True)
    cnf = args.output / "encoding.cnf"
    cycles = args.output / "cycles.txt"
    stdout = args.output / "stdout.txt"
    stderr = args.output / "stderr.txt"

    b = GraphEncodingBuilder(n, directed=False)
    cmd = ["smsg", "--vertices", str(n)]
    if h is None:
        b.minDegree(3, countertype="sequential")
    else:
        high, cubic = list(range(h)), list(range(h, n))
        b.degreeBounds(high, 4, 4, encoding="sequential")
        b.degreeBounds(cubic, 3, 3, encoding="sequential")
        for u in high:
            for v in high:
                if u < v:
                    b.append([-b.var_edge(u, v)])
        for u in cubic:
            b.append([b.var_edge(u, v) for v in cubic if u != v])
        cmd += ["--connected", "--initial-partition", str(h), str(n-h)]
    with cnf.open("w") as fh:
        b.print_dimacs(fh)
    write_cycles(cycles)
    cmd += ["--forbidden-subgraph-file", str(cycles), "--dimacs", str(cnf),
            "--timeout", str(args.timeout)]
    started = time.monotonic()
    with stdout.open("w") as out, stderr.open("w") as err:
        process = subprocess.run(cmd, stdout=out, stderr=err)
    elapsed = time.monotonic() - started
    text = stdout.read_text()
    result_code = next((int(line.split(":", 1)[1]) for line in text.splitlines()
                        if line.startswith("Result:")), process.returncode)
    status = {0: "TIMEOUT", 10: "SAT", 20: "UNSAT"}.get(result_code, "ERROR")
    record = {"n": n, "high": h, "status": status, "result": result_code,
              "elapsed": elapsed, "timeout": args.timeout, "command": cmd}
    if status == "SAT":
        first = next(line for line in text.splitlines() if line.startswith("["))
        edges = ast.literal_eval(first)
        candidate = {"n": n, "edges": [list(edge) for edge in edges]}
        (args.output / "candidate.json").write_text(json.dumps(candidate, indent=2)+"\n")
        record["candidate"] = "candidate.json"
    (args.output / "result.json").write_text(json.dumps(record, indent=2)+"\n")
    print(json.dumps(record), flush=True)
    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
