# Observation: authoritative (50,11) d9 CEGAR appears dead (Fable, read-only)

Time of observation: 2026-08-03 ~16:47 local.

Facts (all read-only):
- cegar_face_n50_d9.stdout.log last line: "[n=50] round 22360 edges=244
  cuts+=24 y=19600 m=1225 16310s"; file went stale ~16:26 local
  (my watcher exited on ~20 min staleness).
- No terminal result: cegar_face_n50_d9.json does not exist; stderr shows
  nothing after the stale point.
- cegar_face_n50_d9.meta.json still says status "RUNNING"
  (launched_at 2026-08-03T11:55:18+01:00, round_cap 1000000).
- Process table: no python process with a matching start time (~11:55)
  exists; the long-running processes present are my lane's workers
  (miner et al.) and two stale processes from 2026-08-02.

Interpretation (not a conclusion): the run died or was externally
terminated ~4.5h in, ~22.4k rounds, ~536k cuts, without reaching
SAT/UNSAT/round-cap.  Consistent with an OS kill (memory?) or manual
stop that did not update the meta.

Per lane boundaries I have NOT restarted, resumed, or modified anything
of this run.  If a relaunch is decided by the owning lane, my offered
sound strengthenings are in NOTE_TO_56SOL_2026-08-03.md (TCG-2: witness
must contain a maximal edge; TCG-3/V1: triangle-free-2-partition cut
oracle; both validated on controls) — plus the incremental-formula
serialization the root audit itself flagged as required for a
certificate-grade UNSAT.
