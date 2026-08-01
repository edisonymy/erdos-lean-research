param(
    [ValidateSet(1, 2, 3)]
    [int[]]$CrossDegree = @(1, 2, 3),
    [string]$OutputDirectory = ".tmp/erdos128-cross-proof-build",
    [switch]$MeasureOnly,
    [switch]$RunProof,
    [switch]$AcknowledgeLargeRun,
    [switch]$OverwriteExisting,
    [ValidateRange(1, 1024)]
    [int]$MaximumArtifactGB = 8,
    [ValidateRange(1, 1024)]
    [int]$ReserveFreeGB = 10
)

$ErrorActionPreference = "Stop"
$workspace = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$generator = Join-Path $PSScriptRoot "cross_proof_cnf.py"
$encodingAudit = Join-Path $PSScriptRoot "audit_cross_proof_encoding.py"
$activePidFile = Join-Path $workspace ".tmp/erdos128_n16_maple.pid"
$cadicalDirectory = Join-Path $workspace "third_party/cadical"
$dratDirectory = Join-Path $workspace "third_party/drat-trim"
$cadicalBinary = Join-Path $cadicalDirectory "cadical-linux"
$dratBinary = Join-Path $dratDirectory "drat-trim"
$lratBinary = Join-Path $dratDirectory "lrat-check"
$toolManifest = Join-Path $workspace "third_party/erdos128-proof-tools.json"
$cadicalCommit = "146207318796f094dcded87349a64f0c6927309e"
$dratCommit = "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"
$expectedCadicalHash = "0ffcd0bb1265203c8744b677dcd8d37185d24cbe00f723d53f2431ade02d0750"
$expectedDratHash = "fe99e01a4990e34789c61a17966a5c13bcdea5eb4c6fbf94f06d55b4718d0b2d"
$expectedLratHash = "8a5c1bde335526ac3778cc25ab6174ca2374659adb5df4a5cd5ddabce5b0f5d9"

function Get-LowerHash([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Convert-ToWslHostPath([string]$Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    if ($full -notmatch '^[A-Za-z]:\\') {
        throw "only local drive-letter paths are supported by the WSL proof tools: $full"
    }
    $drive = $full.Substring(0, 1).ToLowerInvariant()
    $tail = $full.Substring(3).Replace("\", "/")
    return "/mnt/host/$drive/$tail"
}

function Convert-ToBase64([string]$Value) {
    return [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Value))
}

function Write-Record([object]$Record, [string]$Path) {
    $Record | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $Path -Encoding utf8
}

function Assert-PinnedProofTools {
    foreach ($binary in @($cadicalBinary, $dratBinary, $lratBinary)) {
        if (-not (Test-Path -LiteralPath $binary)) {
            throw "missing proof tool $binary; run build_proof_tools.ps1 first"
        }
    }
    if (-not (Test-Path -LiteralPath $toolManifest)) {
        throw "missing proof-tool build manifest; rerun build_proof_tools.ps1"
    }
    $manifest = Get-Content -LiteralPath $toolManifest -Raw | ConvertFrom-Json
    $cadicalHead = ((& git -C $cadicalDirectory rev-parse HEAD) -join "").Trim()
    $dratHead = ((& git -C $dratDirectory rev-parse HEAD) -join "").Trim()
    if ($cadicalHead -ne $cadicalCommit -or $dratHead -ne $dratCommit) {
        throw "proof-tool source checkout is not at the pinned commits"
    }
    & git -C $cadicalDirectory diff --quiet $cadicalCommit -- src
    if ($LASTEXITCODE -ne 0) { throw "tracked CaDiCaL src differs from the pinned commit" }
    & git -C $dratDirectory diff --quiet $dratCommit -- .
    if ($LASTEXITCODE -ne 0) { throw "tracked drat-trim sources differ from the pinned commit" }
    $untrackedCadical = & git -C $cadicalDirectory ls-files --others --exclude-standard -- "src/*.cpp" "src/*.hpp"
    if ($untrackedCadical) { throw "untracked CaDiCaL compilation inputs exist" }
    $untrackedDrat = & git -C $dratDirectory ls-files --others --exclude-standard -- `
        "*.c" "*.h" "*.cc" "*.cpp" "*.hpp" "Makefile" "makefile" "GNUmakefile" "*.mk"
    if ($untrackedDrat) { throw "untracked drat-trim build inputs exist" }

    $cadicalHash = Get-LowerHash $cadicalBinary
    $dratHash = Get-LowerHash $dratBinary
    $lratHash = Get-LowerHash $lratBinary
    if ($cadicalHash -ne $expectedCadicalHash -or $dratHash -ne $expectedDratHash -or
        $lratHash -ne $expectedLratHash) {
        throw "proof-tool binary hash mismatch; rerun and inspect build_proof_tools.ps1"
    }
    if ($manifest.cadical_commit -ne $cadicalCommit -or
        $manifest.drat_trim_commit -ne $dratCommit -or
        $manifest.cadical_sha256 -ne $cadicalHash -or
        $manifest.drat_trim_sha256 -ne $dratHash -or
        $manifest.lrat_check_sha256 -ne $lratHash) {
        throw "proof-tool manifest does not match the pinned sources and binaries"
    }
}

if ($MeasureOnly -and $RunProof) {
    throw "-MeasureOnly and -RunProof are mutually exclusive"
}
if ($RunProof -and -not $AcknowledgeLargeRun) {
    throw "-RunProof requires -AcknowledgeLargeRun after reviewing CROSS_PROOF_PIPELINE.md"
}
if ($RunProof -and (Test-Path -LiteralPath $activePidFile)) {
    $activePid = [int](Get-Content -LiteralPath $activePidFile)
    if (Get-Process -Id $activePid -ErrorAction SilentlyContinue) {
        throw "refusing to compete with active Erdos-128 solver PID $activePid"
    }
}

if ([System.IO.Path]::IsPathRooted($OutputDirectory)) {
    $outputFull = [System.IO.Path]::GetFullPath($OutputDirectory)
} else {
    $outputFull = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputDirectory))
}
New-Item -ItemType Directory -Force -Path $outputFull | Out-Null
if ((Get-ChildItem -LiteralPath $outputFull -Force | Select-Object -First 1) -and
    -not $OverwriteExisting) {
    throw "output directory is not empty; choose a fresh directory or pass -OverwriteExisting"
}

$auditLog = Join-Path $outputFull "encoding-audit.json"
$auditOutput = & python $encodingAudit 2>&1
if ($LASTEXITCODE -ne 0) { throw "cross-proof encoding audit failed" }
$auditRecord = ($auditOutput -join "`n") | ConvertFrom-Json
if ($auditRecord.status -ne "PASS") { throw "encoding audit did not report PASS" }
$auditOutput | Set-Content -LiteralPath $auditLog -Encoding utf8

if ($RunProof) {
    Assert-PinnedProofTools
}

foreach ($d in ($CrossDegree | Sort-Object -Unique)) {
    $caseDirectory = Join-Path $outputFull "d$d"
    New-Item -ItemType Directory -Force -Path $caseDirectory | Out-Null
    $encodingLog = Join-Path $caseDirectory "encoding.json"
    $summaryPath = Join-Path $caseDirectory "summary.json"
    $dimacs = Join-Path $caseDirectory "erdos128_n16_d$d.cnf"
    $generatorArguments = @($generator, $d)
    if ($MeasureOnly) {
        $generatorArguments += "--measure-only"
    } else {
        $generatorArguments += @("--dimacs", $dimacs)
        if ($OverwriteExisting) { $generatorArguments += "--overwrite" }
    }
    $encodingOutput = & python @generatorArguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "DIMACS encoding failed for d=$d" }
    $encodingRecord = ($encodingOutput -join "`n") | ConvertFrom-Json
    $encodingOutput | Set-Content -LiteralPath $encodingLog -Encoding utf8
    $record = [ordered]@{
        schema = "erdos128-cross-proof-pipeline-v1"
        cross_degree = $d
        encoding_stage = [ordered]@{
            status = if ($MeasureOnly) { "measured" } else { "dimacs_written" }
            generator_sha256 = Get-LowerHash $generator
            audit_source_sha256 = Get-LowerHash $encodingAudit
            semantic_audit_output_sha256 = Get-LowerHash $auditLog
            metadata = $encodingRecord
        }
        solver_stage = [ordered]@{ status = "not_run" }
        drat_verification_stage = [ordered]@{ status = "not_run" }
        lrat_verification_stage = [ordered]@{ status = "not_run" }
    }
    Write-Record $record $summaryPath

    if (-not $RunProof) { continue }

    # The CNF has already been measured and written.  Every subsequent named
    # output is subjected to a per-file ulimit.  Five files can coexist at the
    # end (DRAT, LRAT, and three logs), so this is a conservative bound on the
    # disk consumption attributable to the remaining pipeline stages.
    $artifactBytes = [int64]$MaximumArtifactGB * [int64]1GB
    $reserveBytes = [int64]$ReserveFreeGB * [int64]1GB
    $requiredFutureBytes = [int64]5 * $artifactBytes + $reserveBytes
    $root = [System.IO.Path]::GetPathRoot($caseDirectory).TrimEnd("\")
    $driveName = $root.Substring(0, 1)
    $freeBytes = [int64](Get-PSDrive $driveName).Free
    if ($freeBytes -lt $requiredFutureBytes) {
        throw ("d=$d proof stage requires {0:N2} GB free after DIMACS: " +
            "five hard-capped artifacts plus reserve; only {1:N2} GB is free") -f `
            ($requiredFutureBytes / 1GB), ($freeBytes / 1GB)
    }
    $limitBlocks = [int64][Math]::Floor($artifactBytes / 512)

    $drat = Join-Path $caseDirectory "erdos128_n16_d$d.drat"
    $lrat = Join-Path $caseDirectory "erdos128_n16_d$d.lrat"
    $solverLog = Join-Path $caseDirectory "cadical.log"
    $dratLog = Join-Path $caseDirectory "drat-trim.log"
    $lratLog = Join-Path $caseDirectory "lrat-check.log"
    $cadicalLinux = Convert-ToWslHostPath $cadicalBinary
    $dratCheckerLinux = Convert-ToWslHostPath $dratBinary
    $lratCheckerLinux = Convert-ToWslHostPath $lratBinary
    $cnfLinux = Convert-ToWslHostPath $dimacs
    $dratLinux = Convert-ToWslHostPath $drat
    $lratLinux = Convert-ToWslHostPath $lrat
    $solverLogLinux = Convert-ToWslHostPath $solverLog
    $dratLogLinux = Convert-ToWslHostPath $dratLog
    $lratLogLinux = Convert-ToWslHostPath $lratLog

    $pathTestScript = @'
set -eu
p=$(printf '%s' "$1" | base64 -d)
test -e "$p"
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
    foreach ($wslPath in @(
        $cadicalLinux, $dratCheckerLinux, $lratCheckerLinux, $cnfLinux,
        (Convert-ToWslHostPath $caseDirectory)
    )) {
        $encodedPath = Convert-ToBase64 $wslPath
        $pathTestScript | & wsl -e sh -s -- $encodedPath
        if ($LASTEXITCODE -ne 0) {
            throw "path is not visible in the default WSL distribution: $wslPath"
        }
    }

    $solverScript = @'
set -u
exe=$(printf '%s' "$1" | base64 -d)
cnf=$(printf '%s' "$2" | base64 -d)
proof=$(printf '%s' "$3" | base64 -d)
log=$(printf '%s' "$4" | base64 -d)
ulimit -f "$5"
"$exe" "$cnf" "$proof" >"$log" 2>&1
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
    $solverScript | & wsl -e sh -s -- `
        (Convert-ToBase64 $cadicalLinux) (Convert-ToBase64 $cnfLinux) `
        (Convert-ToBase64 $dratLinux) (Convert-ToBase64 $solverLogLinux) $limitBlocks
    $solverExit = $LASTEXITCODE
    if ($solverExit -eq 10) {
        $record.solver_stage = [ordered]@{ status = "sat"; exit_code = 10; log_sha256 = Get-LowerHash $solverLog }
        $record.drat_verification_stage.status = "not_applicable"
        $record.lrat_verification_stage.status = "not_applicable"
        Write-Record $record $summaryPath
        throw "CaDiCaL found SAT for d=$d; retain the log and independently extract/check the model"
    }
    if ($solverExit -ne 20) {
        $record.solver_stage = [ordered]@{ status = "failed_or_capped"; exit_code = $solverExit }
        Write-Record $record $summaryPath
        throw "CaDiCaL did not return UNSAT for d=$d (exit $solverExit)"
    }
    $record.solver_stage = [ordered]@{
        status = "unsat_claim"
        exit_code = 20
        drat_bytes = (Get-Item -LiteralPath $drat).Length
        drat_sha256 = Get-LowerHash $drat
        log_sha256 = Get-LowerHash $solverLog
    }
    Write-Record $record $summaryPath

    $dratScript = @'
set -u
exe=$(printf '%s' "$1" | base64 -d)
cnf=$(printf '%s' "$2" | base64 -d)
proof=$(printf '%s' "$3" | base64 -d)
lrat=$(printf '%s' "$4" | base64 -d)
log=$(printf '%s' "$5" | base64 -d)
ulimit -f "$6"
"$exe" "$cnf" "$proof" -L "$lrat" >"$log" 2>&1
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
    $dratScript | & wsl -e sh -s -- `
        (Convert-ToBase64 $dratCheckerLinux) (Convert-ToBase64 $cnfLinux) `
        (Convert-ToBase64 $dratLinux) (Convert-ToBase64 $lratLinux) `
        (Convert-ToBase64 $dratLogLinux) $limitBlocks
    $dratExit = $LASTEXITCODE
    $dratText = if (Test-Path -LiteralPath $dratLog) { Get-Content -LiteralPath $dratLog -Raw } else { "" }
    if ($dratExit -ne 0 -or $dratText -notmatch "s VERIFIED") {
        $record.drat_verification_stage = [ordered]@{ status = "failed_or_capped"; exit_code = $dratExit }
        Write-Record $record $summaryPath
        throw "DRAT verification failed for d=$d"
    }
    $record.drat_verification_stage = [ordered]@{
        status = "verified"
        exit_code = 0
        lrat_bytes = (Get-Item -LiteralPath $lrat).Length
        lrat_sha256 = Get-LowerHash $lrat
        log_sha256 = Get-LowerHash $dratLog
    }
    Write-Record $record $summaryPath

    $lratScript = @'
set -u
exe=$(printf '%s' "$1" | base64 -d)
cnf=$(printf '%s' "$2" | base64 -d)
lrat=$(printf '%s' "$3" | base64 -d)
log=$(printf '%s' "$4" | base64 -d)
ulimit -f "$5"
"$exe" "$cnf" "$lrat" >"$log" 2>&1
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
    $lratScript | & wsl -e sh -s -- `
        (Convert-ToBase64 $lratCheckerLinux) (Convert-ToBase64 $cnfLinux) `
        (Convert-ToBase64 $lratLinux) (Convert-ToBase64 $lratLogLinux) $limitBlocks
    $lratExit = $LASTEXITCODE
    $lratText = if (Test-Path -LiteralPath $lratLog) { Get-Content -LiteralPath $lratLog -Raw } else { "" }
    if ($lratExit -ne 0 -or $lratText -notmatch "(?m)^c VERIFIED\s*$") {
        $record.lrat_verification_stage = [ordered]@{ status = "failed_or_capped"; exit_code = $lratExit }
        Write-Record $record $summaryPath
        throw "LRAT verification failed for d=$d"
    }
    $record.lrat_verification_stage = [ordered]@{
        status = "verified"
        exit_code = 0
        log_sha256 = Get-LowerHash $lratLog
    }
    $record.proof_tools = [ordered]@{
        cadical_commit = $cadicalCommit
        cadical_sha256 = $expectedCadicalHash
        drat_trim_commit = $dratCommit
        drat_trim_sha256 = $expectedDratHash
        lrat_check_sha256 = $expectedLratHash
        maximum_named_artifact_bytes = $artifactBytes
        reserve_free_bytes = $reserveBytes
    }
    Write-Record $record $summaryPath
}

Get-ChildItem -LiteralPath $outputFull -Recurse -Filter summary.json |
    ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw }
