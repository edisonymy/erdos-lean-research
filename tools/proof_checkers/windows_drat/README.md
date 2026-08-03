# Windows DRAT/LRAT checker wrapper

This directory contains only the MSVC portability shim and build assets for
the pinned sources in `third_party/drat-trim/`; it does not copy or modify
those sources. `build.ps1` builds x64 `drat-trim.exe` and `lrat-check.exe`
under the existing Visual Studio 2022 Build Tools environment and records
source, shim, script, and executable SHA-256 hashes in `build-manifest.json`.

Run `validate_examples.ps1` after building. It performs the upstream
`example-5-vars.cnf` plus `example-5-vars.drat` DRAT-to-LRAT conversion,
checks that generated LRAT, and independently checks the shipped LRAT example.
It records commands, hashes, logs, and exact pass boundaries in
`validation-manifest.json`.

Validation is separate from building: DRAT-trim must report `s VERIFIED` on
the exact DIMACS and normalized ASCII DRAT input; the resulting LRAT must then
be accepted by `lrat-check.exe`. A successful checker run certifies only the
specified DIMACS input and proof file, not a higher-level mathematical mapping.
