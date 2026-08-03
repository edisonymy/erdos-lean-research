# Pinned CaDiCaL 1.9.5 proof generator

This container builds the official CaDiCaL source at immutable commit
`146207318796f094dcded87349a64f0c6927309e` (tag `rel-1.9.5`) on the pinned
Ubuntu 24.04 base digest shown in `Dockerfile`.  It also builds `drat-trim` at
immutable commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`, so binary traces can be
checked inside Linux without Windows text-mode translation.

Build from the repository root:

```powershell
docker build -t erdos-cadical:1.9.5 tools/proof_generators/cadical_1_9_5_docker
```

On Windows, mount an artifact directory at `/work` and pass container paths
for the DIMACS input and proof output.  CaDiCaL accepts the proof path as its
second positional argument:

```powershell
docker run --rm -v "${PWD}/artifacts:/work" erdos-cadical:1.9.5 \
  /work/input.cnf /work/output.drat
```

The SAT result alone is not a certificate.  Check every emitted trace using
the independently built `drat-trim` binary, and preferably convert it to LRAT
for a second replay.

```powershell
docker run --rm --entrypoint /opt/drat-trim/drat-trim \
  -v "${PWD}/artifacts:/work" erdos-cadical:1.9.5 \
  /work/input.cnf /work/output.drat
```
