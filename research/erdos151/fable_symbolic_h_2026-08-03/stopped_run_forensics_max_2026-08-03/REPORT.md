# Independent forensics: simultaneous n=50 CEGAR stop

Date: 2026-08-03 (BST). Existing run artifacts were inspected read-only. No
research worker was started, resumed, stopped, or modified.

## Bottom line

The strongest explanation is a **Codex host/container teardown**, not a solver
outcome and probably not memory pressure. At `16:26:29.005 BST`, Windows logged
destruction of the active OpenAI Codex Desktop AppX container. A new Codex
container was created `10.272 s` later. The three last CEGAR writes precede the
destruction by only `5.098 s`, `3.119 s`, and `31.542 s`. Their next progress
messages were not due at identical times, so this spread is compatible with one
simultaneous kill between progress prints.

The launch records explain the vulnerability. This shell currently belongs to
a Windows Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` and
`JOB_OBJECT_LIMIT_BREAKAWAY_OK` (`LimitFlags=0x00002800`). The matching-only
launcher requested `DETACHED_PROCESS`, `CREATE_NEW_PROCESS_GROUP`, and
`CREATE_NO_WINDOW`, but not `CREATE_BREAKAWAY_FROM_JOB`; the combined launcher
requested no breakaway. Microsoft documents that detaching from a console and
creating a process group do not leave a Job Object, while children remain in
their parent's job by default. Closing a kill-on-close job terminates its
associated processes.

This is **high-confidence causal attribution, not proof of the precise exit
instruction**: process-termination audit events were unavailable, and the
inherited run's original launch call was not found. The exact statement proved
by the evidence is that all three were vulnerable to a common job/container
teardown, and their disappearance aligns tightly with a recorded Codex
container destruction.

Microsoft references:

- [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
- [Process Creation Flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)
- [Tasks performed by Task Scheduler](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasks)

## Exact run observations

| lane | last round | last write (BST) | before container destruction | stderr | result |
|---|---:|---|---:|---:|---|
| inherited degree-9 | 22,360 | 16:26:23.907553 | 5.098 s | 0 B | absent |
| matching-3 | 6,480 | 16:26:25.886325 | 3.119 s | 0 B | absent |
| matching-3 + TCG-3 | 1,100 | 16:25:57.463872 | 31.542 s | 0 B | absent |

The final elapsed-time fields agree with the recorded process start times, so
there is no evidence of stale buffered output. None of the scripts reached its
normal SAT-candidate, UNSAT, or round-cap write path. No mathematical inference
is licensed by the stop.

The log hashes and complete Windows event identifiers/XML hashes are in
`EVIDENCE.json`. The three stdout SHA-256 values are, in table order:

```text
35018b195fecc7fd6aa610af073639335695e1aa8d9518f1fff38c6e8d52ebdc
d124e1a37118fc0439f393a3f28eddb5f0015b55e1a70cf67a333ef4b7707895
ea29a15964ea01354169c80c482a096e73f485774722f5153346c8f2b4f9c63a
```

## Host timeline

Windows log `Microsoft-Windows-AppModel-Runtime/Admin` records:

1. `16:25:07.270888`: process 59556 added to Codex container
   `68d6bfef-...` (record 78898).
2. `16:26:29.005472`: that Codex container destroyed (record 78902).
3. `16:26:39.277484`: new Codex container `0d3fbb92-...` created (record
   78904), followed by new Codex process 54360.

The System and Application logs contain no resource-exhaustion event 2004,
power/reboot event 41/1074/6006/6008, Application Error/WER event
1000/1001/1002, or WER archive report in the surrounding 15-minute window.
No Codex tool transcript contains a process-kill command in the five-minute
window. These are negative observations, not impossibility proofs.

## Launcher reconstruction

The hash-pinned Codex transcript shows:

- Matching-3 was launched through `subprocess.Popen` with
  `CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`. Those flags
  separate console behavior but do not request Job Object breakaway.
- The combined lane was launched by `ProcessStartInfo` through `cmd.exe`, with
  no creation flag that requests breakaway.
- The inherited lane was observed as `.venv` redirector PID 58260 -> actual
  Python PID 60196. Its original launch invocation was not recovered, so its
  job membership at death is inferred from the shared host and stop evidence,
  not asserted from a launch record.

A bounded diagnostic made no persistent process:

- ordinary short child: associated job flags `0x2800`, including kill-on-close;
- short child created with `CREATE_BREAKAWAY_FROM_JOB`: associated job flags
  `0x0000`, but `IsProcessInJob` remained true, demonstrating a nested/outer
  job. Thus explicit breakaway is better than the old launcher but is not by
  itself a certificate of surviving destruction of the outer AppX container.

## Persistent-worker design

For a genuinely durable research worker, **launch through Windows Task
Scheduler**, not `Start-Process` and not a detached child of the Codex tool
process. The Task Scheduler service is currently `Running` with automatic
startup and acts as an OS broker outside the transient Codex job lifecycle.

The production design should be:

1. Put the exact absolute command and working directory in a small supervisor
   script. It must create an atomic lock, write PID/start time/command/script
   hashes, redirect stdout/stderr, and always write exit code and terminal time.
2. Register a uniquely named user task with `ExecutionTimeLimit = PT0S`,
   `MultipleInstances = IgnoreNew`, explicit battery policy, and a bounded
   restart-on-failure rule. Trigger it explicitly with `Start-ScheduledTask`.
3. Verify the task through `Get-ScheduledTaskInfo`, the supervisor's metadata,
   and a child Job Object probe. Do not treat scheduler status alone as worker
   liveness.
4. Delete or disable the task only after a terminal result is frozen and
   checked.

An explicitly breakaway child can be a short-term fallback because the current
inner job allows breakaway, but the nested-job probe means it should not be
called "persistent" until it survives a deliberate Codex-app restart control.

Finally, OS persistence does not repair the CEGAR state-loss defect. Before a
production relaunch, serialize learned cuts (or periodic final-formula
snapshots) plus a restart cursor. Otherwise a machine reboot, solver crash, or
planned task restart still replays all prior rounds.

## Confidence-ranked attribution

1. **Codex AppX/job teardown: high confidence.** Exact host event, matching
   timing, common vulnerability, and all three disappear together.
2. **Manual broad process kill: low confidence.** No matching Codex tool call;
   external tools were not exhaustively auditable.
3. **Resource exhaustion/OOM: low confidence.** No Windows detector/WER event
   and a container teardown gives a simpler common cause, but absence of an
   event is not proof.
4. **Independent script/solver exits: effectively excluded as a common normal
   explanation.** No stderr, result, or terminal print in any lane.

No SAT, UNSAT, timeout, convergence, or proximity claim follows from this
forensic result.
