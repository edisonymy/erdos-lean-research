param(
    [int]$N = 8,
    [int]$AlphaUpper = 3,
    [int]$FixIndependentSize = 3,
    [string]$OutputDirectory = ".tmp/erdos128-proof-smoke",
    [switch]$AcknowledgeLargeRun,
    [switch]$OverwriteExisting,
    [int]$MinimumFreeGBForLargeRun = 50
)

$ErrorActionPreference = "Stop"
$workspace = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$generator = Join-Path $PSScriptRoot "cnf_search.py"
$cadicalBinary = Join-Path $workspace "third_party/cadical/cadical-linux"
$dratBinary = Join-Path $workspace "third_party/drat-trim/drat-trim"
$lratBinary = Join-Path $workspace "third_party/drat-trim/lrat-check"
$dratDirectory = Join-Path $workspace "third_party/drat-trim"
$cadicalDirectory = Join-Path $workspace "third_party/cadical"
$toolManifest = Join-Path $workspace "third_party/erdos128-proof-tools.json"
$cardinalityAudit = Join-Path $PSScriptRoot "audit_cardinality_encoding.py"
$activePidFile = Join-Path $workspace ".tmp/erdos128_n16_maple.pid"
$cadicalCommit = "146207318796f094dcded87349a64f0c6927309e"
$dratCommit = "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"
$expectedCadicalHash = "0ffcd0bb1265203c8744b677dcd8d37185d24cbe00f723d53f2431ade02d0750"
$expectedDratHash = "fe99e01a4990e34789c61a17966a5c13bcdea5eb4c6fbf94f06d55b4718d0b2d"
$expectedLratHash = "8a5c1bde335526ac3778cc25ab6174ca2374659adb5df4a5cd5ddabce5b0f5d9"

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

function Get-LowerHash([string]$Path) {
    return (Get-FileHash $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

foreach ($binary in @($cadicalBinary, $dratBinary, $lratBinary)) {
    if (-not (Test-Path $binary)) {
        throw "missing proof tool $binary; run build_proof_tools.ps1 first"
    }
}

if ($N -lt 0 -or $AlphaUpper -lt 0 -or $AlphaUpper -gt $N -or
    $FixIndependentSize -lt 0 -or $FixIndependentSize -gt $N) {
    throw "require 0 <= alpha/fixed-independent-size <= N"
}
if ($FixIndependentSize -gt $AlphaUpper) {
    throw "FixIndependentSize cannot exceed AlphaUpper"
}
if ($N -ge 16 -and ($N -ne 16 -or $AlphaUpper -ne 6 -or $FixIndependentSize -ne 6)) {
    throw "the large-run contract is exactly N=16, AlphaUpper=6, FixIndependentSize=6"
}

if (-not (Test-Path $toolManifest)) {
    throw "missing proof-tool build manifest; rerun build_proof_tools.ps1"
}
$manifest = Get-Content $toolManifest -Raw | ConvertFrom-Json
$cadicalHead = ((& git -C $cadicalDirectory rev-parse HEAD) -join "").Trim()
$dratHead = ((& git -C $dratDirectory rev-parse HEAD) -join "").Trim()
if ($cadicalHead -ne $cadicalCommit -or $dratHead -ne $dratCommit) {
    throw "proof-tool source checkout is not at the pinned commits"
}
& git -C $cadicalDirectory diff --quiet $cadicalCommit -- src
if ($LASTEXITCODE -ne 0) { throw "tracked CaDiCaL src differs from the pinned commit" }
& git -C $dratDirectory diff --quiet $dratCommit -- .
if ($LASTEXITCODE -ne 0) { throw "tracked drat-trim sources differ from the pinned commit" }
$untrackedCadicalSources = & git -C $cadicalDirectory ls-files --others --exclude-standard -- "src/*.cpp" "src/*.hpp"
if ($untrackedCadicalSources) { throw "untracked CaDiCaL compilation inputs exist" }
$untrackedDratInputs = & git -C $dratDirectory ls-files --others --exclude-standard -- `
    "*.c" "*.h" "*.cc" "*.cpp" "*.hpp" "Makefile" "makefile" "GNUmakefile" "*.mk"
if ($untrackedDratInputs) { throw "untracked drat-trim build inputs exist" }

$cadicalHash = Get-LowerHash $cadicalBinary
$dratHash = Get-LowerHash $dratBinary
$lratHash = Get-LowerHash $lratBinary
if ($cadicalHash -ne $expectedCadicalHash -or $dratHash -ne $expectedDratHash -or
    $lratHash -ne $expectedLratHash) {
    throw "proof-tool binary hash mismatch; rerun and inspect build_proof_tools.ps1"
}
if ($manifest.cadical_commit -ne $cadicalCommit -or $manifest.drat_trim_commit -ne $dratCommit -or
    $manifest.cadical_sha256 -ne $cadicalHash -or $manifest.drat_trim_sha256 -ne $dratHash -or
    $manifest.lrat_check_sha256 -ne $lratHash) {
    throw "proof-tool build manifest does not match the pinned sources and binaries"
}

if ($N -ge 16) {
    if (-not $AcknowledgeLargeRun) {
        throw "N >= 16 requires -AcknowledgeLargeRun after reviewing PROOF_PIPELINE.md"
    }
    if (Test-Path $activePidFile) {
        $activePid = [int](Get-Content $activePidFile)
        if (Get-Process -Id $activePid -ErrorAction SilentlyContinue) {
            throw "refusing to compete with active Erdos-128 solver PID $activePid"
        }
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
if ($N -ge 16) {
    $root = [System.IO.Path]::GetPathRoot($outputFull).TrimEnd("\")
    $driveName = $root.Substring(0, 1)
    $freeBytes = (Get-PSDrive $driveName).Free
    $requiredBytes = [int64]$MinimumFreeGBForLargeRun * 1GB
    if ($freeBytes -lt $requiredBytes) {
        throw "large proof run requires at least $MinimumFreeGBForLargeRun GB free on $driveName"
    }
}

$cnf = Join-Path $outputFull "erdos128_n$N.cnf"
$drat = Join-Path $outputFull "erdos128_n$N.drat"
$lrat = Join-Path $outputFull "erdos128_n$N.lrat"
$buildLog = Join-Path $outputFull "build.log"
$solverLog = Join-Path $outputFull "cadical.log"
$dratLog = Join-Path $outputFull "drat-trim.log"
$lratLog = Join-Path $outputFull "lrat-check.log"
$cardinalityLog = Join-Path $outputFull "cardinality-audit.log"
$summary = Join-Path $outputFull "summary.json"

$cardinalityOutput = & python $cardinalityAudit 2>&1
$cardinalityExit = $LASTEXITCODE
$cardinalityOutput | Set-Content -Encoding utf8 $cardinalityLog
if ($cardinalityExit -ne 0) {
    throw "cardinality-encoding audit failed; see $cardinalityLog"
}
$cardinalityRecord = ($cardinalityOutput -join "`n") | ConvertFrom-Json
if ($cardinalityRecord.status -ne "PASS") {
    throw "cardinality-encoding audit did not report PASS"
}

$generatorArguments = @(
    $generator,
    $N,
    "--alpha-upper", $AlphaUpper,
    "--fix-independent-size", $FixIndependentSize,
    "--dimacs", $cnf,
    "--build-only"
)
$buildOutput = & python @generatorArguments 2>&1
$buildExit = $LASTEXITCODE
$buildOutput | Set-Content -Encoding utf8 $buildLog
if ($buildExit -ne 0) { throw "DIMACS generation failed; see $buildLog" }

$cnfLinux = Convert-ToWslHostPath $cnf
$dratLinux = Convert-ToWslHostPath $drat
$lratLinux = Convert-ToWslHostPath $lrat
$cadicalLinux = Convert-ToWslHostPath $cadicalBinary
$dratCheckerLinux = Convert-ToWslHostPath $dratBinary
$lratCheckerLinux = Convert-ToWslHostPath $lratBinary
$pathTestScript = @'
set -eu
p=$(printf '%s' "$1" | base64 -d)
test -e "$p"
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
foreach ($wslPath in @($cadicalLinux, $dratCheckerLinux, $lratCheckerLinux, (Convert-ToWslHostPath $outputFull))) {
    $encodedPath = Convert-ToBase64 $wslPath
    $pathTestScript | & wsl -e sh -s -- $encodedPath
    if ($LASTEXITCODE -ne 0) { throw "path is not visible in the default WSL distribution: $wslPath" }
}

$solverScript = @'
set -eu
exe=$(printf '%s' "$1" | base64 -d)
cnf=$(printf '%s' "$2" | base64 -d)
proof=$(printf '%s' "$3" | base64 -d)
exec "$exe" "$cnf" "$proof"
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
$solverOutput = $solverScript | & wsl -e sh -s -- `
    (Convert-ToBase64 $cadicalLinux) (Convert-ToBase64 $cnfLinux) `
    (Convert-ToBase64 $dratLinux) 2>&1
$solverExit = $LASTEXITCODE
$solverOutput | Set-Content -Encoding utf8 $solverLog
if ($solverExit -ne 20) {
    throw "CaDiCaL did not return UNSAT (exit $solverExit); see $solverLog"
}

$dratScript = @'
set -eu
exe=$(printf '%s' "$1" | base64 -d)
cnf=$(printf '%s' "$2" | base64 -d)
proof=$(printf '%s' "$3" | base64 -d)
lrat=$(printf '%s' "$4" | base64 -d)
exec "$exe" "$cnf" "$proof" -L "$lrat"
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
$dratOutput = $dratScript | & wsl -e sh -s -- `
    (Convert-ToBase64 $dratCheckerLinux) (Convert-ToBase64 $cnfLinux) `
    (Convert-ToBase64 $dratLinux) (Convert-ToBase64 $lratLinux) 2>&1
$dratExit = $LASTEXITCODE
$dratOutput | Set-Content -Encoding utf8 $dratLog
if ($dratExit -ne 0 -or ($dratOutput -join "`n") -notmatch "s VERIFIED") {
    throw "DRAT verification failed; see $dratLog"
}

$lratScript = @'
set -eu
exe=$(printf '%s' "$1" | base64 -d)
cnf=$(printf '%s' "$2" | base64 -d)
lrat=$(printf '%s' "$3" | base64 -d)
exec "$exe" "$cnf" "$lrat"
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
$lratOutput = $lratScript | & wsl -e sh -s -- `
    (Convert-ToBase64 $lratCheckerLinux) (Convert-ToBase64 $cnfLinux) `
    (Convert-ToBase64 $lratLinux) 2>&1
$lratExit = $LASTEXITCODE
$lratOutput | Set-Content -Encoding utf8 $lratLog
# The reference lrat-check writes `c VERIFIED`; drat-trim writes `s VERIFIED`.
if ($lratExit -ne 0 -or ($lratOutput -join "`n") -notmatch "(?m)^c VERIFIED\s*$") {
    throw "LRAT verification failed; see $lratLog"
}

$record = [ordered]@{
    n = $N
    alpha_upper = $AlphaUpper
    fixed_independent_size = $FixIndependentSize
    python_sat = $cardinalityRecord.python_sat
    cardinality_audit_sha256 = Get-LowerHash $cardinalityLog
    generator_sha256 = Get-LowerHash $generator
    cnf_bytes = (Get-Item $cnf).Length
    cnf_sha256 = Get-LowerHash $cnf
    drat_bytes = (Get-Item $drat).Length
    drat_sha256 = Get-LowerHash $drat
    lrat_bytes = (Get-Item $lrat).Length
    lrat_sha256 = Get-LowerHash $lrat
    proof_tool_manifest_sha256 = Get-LowerHash $toolManifest
    cadical_commit = $cadicalCommit
    cadical_sha256 = $cadicalHash
    drat_trim_commit = $dratCommit
    drat_trim_sha256 = $dratHash
    lrat_check_sha256 = $lratHash
    cadical_exit = $solverExit
    drat_trim_verified = $true
    lrat_check_verified = $true
}
$record | ConvertTo-Json | Set-Content -Encoding utf8 $summary
$record | ConvertTo-Json
