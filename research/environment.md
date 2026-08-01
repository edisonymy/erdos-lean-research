# Reproducible environment

## Formal Conjectures

```powershell
git clone https://github.com/google-deepmind/formal-conjectures.git third_party/formal-conjectures
git -C third_party/formal-conjectures checkout 735aee074327b8e78b0d92bb1ee8ea00937c3f51
```

Install the official Lean version manager (`elan`). From the Formal Conjectures checkout, the
pinned `lean-toolchain` selects Lean 4.27.0 automatically.

```powershell
$env:PATH = 'C:\Users\Edison Yi\.elan\bin;' + $env:PATH
Set-Location third_party/formal-conjectures
lake exe cache get
lake build FormalConjecturesUtil
```

Observed clean baseline:

- `Lean 4.27.0`, commit `db93fe1608548721853390a10cd40580fe7d22ae`
- `Lake 5.0.0`
- `lake build FormalConjecturesUtil`: **passed**, 8,041 jobs
- unchanged `FormalConjectures/ErdosProblems/273.lean`: **elaborated**, with only the expected
  upstream `sorry` warnings

## Rethlas

The Erdős-focused runner is pinned for workflow comparison and optional budgeted campaigns:

```powershell
git clone https://github.com/leon2k2k2k/Rethlas.git third_party/rethlas-runner
git -C third_party/rethlas-runner checkout 622bc663d4212333ade4c4802af1db3da92262c0
```

Its verifier and generation MCP dependencies were installed into separate `uv` virtual
environments. No model-consuming Rethlas pool run has been launched. The runner's Linux-only
network-egress interposer is unavailable on this native Windows host, so any future Windows run
must not be described as a cryptographically or OS-level blind/frozen-world run.

## Generated artifacts

Compiled binaries, `.obj` files, Python bytecode, Lean caches, cloned upstream repositories, and
virtual environments are ignored. Rebuild compiled search tools from their checked-in source.

