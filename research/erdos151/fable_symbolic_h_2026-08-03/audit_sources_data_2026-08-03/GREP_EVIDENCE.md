# Grep and artifact evidence

Run from `research/erdos151/fable_symbolic_h_2026-08-03` on 2026-08-03.

## Claim locations

```text
PROGRAM_ALPHA.md:182:COMPUTATIONALLY CHECKED, two families, greedy upper bounds on chi_tf:
PROGRAM_ALPHA.md:194:Readings: (i) the empirical class constant is < 1/2 everywhere measured
PROGRAM_ALPHA.md:207:... the honest bracket is chi_tf in [6, 10] (the lower
PROGRAM_ALPHA.md:218:empirical class constant is now < 1/2 with margin on EVERY family
PROGRAM_ALPHA.md:294:(glauber_tf.jsonl): stationary densities 0.36 ...
PROGRAM_ALPHA.md:295:... implied C_f = 0.09 / 0.11 / 0.30,
RESEARCH_LOG.md:200:Caveat recorded: tf_found is a heuristic lower
RESEARCH_LOG.md:202:DEAD verdict used only the sound direction tf >= tf_found >= h.
```

The complete line extraction, including source hashes, is in
`audit_data_semantics.result.json` under `claim_grep` and `script_grep`.

## Stored data contradicting “below 1/2 everywhere”

```text
chitf_landscape.jsonl n=200 seed=1 C_emp=0.562
chitf_landscape.jsonl n=200 seed=2 C_emp=0.562
chitf_landscape.jsonl n=400 seed=1 C_emp=0.542
chitf_landscape.jsonl n=400 seed=2 C_emp=0.542
```

Four other stored rows (`n=800,1600`, two seeds each) are below `1/2`.
All eight stored arithmetic fields recompute exactly.

## Anchor artifact gap

The matching file search returns:

```text
anchor_pin.py
anchor_pin.json
anchor_pin.log
anchor_pin2.json
anchor_pin2.log
anchor_pin2_launch.log
```

There is no `anchor_pin2.py` and neither JSON file stores a colour assignment.
The deterministic checker replay of the available `anchor_pin.py` is recorded
in `audit_data_semantics.result.json`: its ten classes have triangle counts

```text
[299, 261, 370, 373, 304, 338, 264, 231, 410, 377]
```

for a total of 3,227 monochromatic triangles.

## Direction-bearing source lines

```text
anchor_pin.py:142: "tf_lower": tf_lb,
anchor_pin.py:143: "chi_tf_lower": math.ceil(n / tf_lb),
glauber_tf.py:4: Measures the stationary density ...
glauber_tf.py:113: "implied_frac_cover": round(1 / max(dens, 1e-9), 2),
glauber_tf.py:114: "implied_C": round(log(Delta)/Delta/dens, 3),
mt_threshold.py:86: break  # smaller c will also fail; move to next instance
```

The first conversion needs an **upper** bound on the maximum triangle-free
set, not the stored lower bound.  The Glauber conversion needs a certified
lower bound on every vertex marginal, not an uncertified mean.  The
Moser--Tardos early-break comment is not a valid statement about independent
stochastic runs.
