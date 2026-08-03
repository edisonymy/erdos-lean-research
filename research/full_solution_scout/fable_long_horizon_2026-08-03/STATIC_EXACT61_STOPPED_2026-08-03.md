# Exact-61 static solve stopped after certified `n=9` theorem

The static exact-61 CaDiCaL process was externally stopped on 3 August 2026
after the same `(m, nu) = (61, 2)` window was excluded by a separate
three-core-orbit CNF/DRAT proof package.  Continuing the static solve would
have duplicated a certified empty case.

At the stop:

- PID: `41180`
- command: `C:\ProgramData\miniconda3\python.exe -X utf8 attack719.py encode-solve static_solve.json static_solve.drup`
- accumulated CPU time: `6803.234375` seconds
- process start: `2026-08-03 00:46:52` Europe/London
- `attack719.py` SHA-256: `f0be3cb94e3cf5b6645232944f929094fbf8eb526588ea4e68c5c162aeaed3b8`
- `static_solve.json`: not created
- `static_solve.drup`: not created

The stopped process produced neither a SAT candidate nor an UNSAT result or
proof.  It contributes no mathematical evidence to the certified theorem.
