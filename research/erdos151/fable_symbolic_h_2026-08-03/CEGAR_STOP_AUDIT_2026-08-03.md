# n=50 CEGAR stop audit (2026-08-03)

At `2026-08-03T16:57:20.6464815+01:00`, none of the three recorded worker
PIDs or any matching command line was present.  All stderr files were empty,
all intended result JSON files were absent, and the logs had stopped within a
31-second interval near 16:26 BST:

| lane | last logged round | last log write | terminal result |
|---|---:|---|---|
| inherited degree-9 | 22,360 | 16:26:23 | none |
| matching-3 | 6,480 | 16:26:25 | none |
| matching-3 + TCG-3 | 1,100 | 16:25:57 | none |

The cause is unknown.  The scripts retained their lazy clauses only in
memory, so these exact processes cannot be resumed and a same-seed restart
would replay prior work.  The logs are liveness/telemetry records only: this
stop is not SAT, UNSAT, a timeout certificate, or evidence of proximity to a
terminal result.

Before another production run, add durable serialization of learned cuts (or
periodic final-formula snapshots) and a restart path.  This is an
infrastructure requirement, not a mathematical claim.
