param()

$ErrorActionPreference = "Stop"

$workspace = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$thirdParty = Join-Path $workspace "third_party"
$dratDirectory = Join-Path $thirdParty "drat-trim"
$cadicalDirectory = Join-Path $thirdParty "cadical"
$dratCommit = "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"
$cadicalCommit = "146207318796f094dcded87349a64f0c6927309e"
$cadicalSourceDateEpoch = "1709135951"
$manifestPath = Join-Path $thirdParty "erdos128-proof-tools.json"

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

if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    throw "WSL2 is required for the pinned Linux proof tools"
}

& wsl -u root -e sh -lc "test -d /mnt/host && command -v apk >/dev/null"
if ($LASTEXITCODE -ne 0) {
    throw "the default WSL distribution must expose Windows drives under /mnt/host and provide apk"
}

# The existing Docker Desktop WSL distribution is Alpine-based.  This starts
# neither Docker Desktop nor a container; it only installs the small compiler
# toolchain used to build the two pinned command-line programs.
& wsl -u root -e sh -lc "apk add --no-cache build-base"
if ($LASTEXITCODE -ne 0) { throw "failed to install the WSL build toolchain" }

New-Item -ItemType Directory -Force -Path $thirdParty | Out-Null
if (-not (Test-Path $dratDirectory)) {
    & git -c core.autocrlf=false clone https://github.com/marijnheule/drat-trim.git $dratDirectory
}
if (-not (Test-Path $cadicalDirectory)) {
    & git -c core.autocrlf=false clone https://github.com/arminbiere/cadical.git $cadicalDirectory
}

& git -C $dratDirectory cat-file -e "$dratCommit`^{commit}"
if ($LASTEXITCODE -ne 0) {
    & git -C $dratDirectory fetch --depth 1 origin $dratCommit
    if ($LASTEXITCODE -ne 0) { throw "failed to fetch pinned drat-trim commit" }
}
& git -C $dratDirectory checkout --detach $dratCommit
if ((& git -C $dratDirectory rev-parse HEAD) -ne $dratCommit) {
    throw "unexpected drat-trim source commit"
}
& git -C $dratDirectory diff --quiet $dratCommit -- .
if ($LASTEXITCODE -ne 0) {
    throw "tracked drat-trim sources differ from the pinned commit"
}
$untrackedDratInputs = & git -C $dratDirectory ls-files --others --exclude-standard -- `
    "*.c" "*.h" "*.cc" "*.cpp" "*.hpp" "Makefile" "makefile" "GNUmakefile" "*.mk"
if ($untrackedDratInputs) {
    throw "untracked drat-trim build inputs exist: $($untrackedDratInputs -join ', ')"
}

& git -C $cadicalDirectory cat-file -e "$cadicalCommit`^{commit}"
if ($LASTEXITCODE -ne 0) {
    & git -C $cadicalDirectory fetch --depth 1 origin $cadicalCommit
    if ($LASTEXITCODE -ne 0) { throw "failed to fetch pinned CaDiCaL commit" }
}
& git -C $cadicalDirectory checkout --detach $cadicalCommit
if ((& git -C $cadicalDirectory rev-parse HEAD) -ne $cadicalCommit) {
    throw "unexpected CaDiCaL source commit"
}
& git -C $cadicalDirectory diff --quiet $cadicalCommit -- src
if ($LASTEXITCODE -ne 0) {
    throw "tracked CaDiCaL src files differ from the pinned commit"
}
$untrackedCadicalSources = & git -C $cadicalDirectory ls-files --others --exclude-standard -- "src/*.cpp" "src/*.hpp"
if ($untrackedCadicalSources) {
    throw "untracked CaDiCaL compilation inputs exist: $($untrackedCadicalSources -join ', ')"
}

$dratLinux = Convert-ToWslHostPath $dratDirectory
$cadicalLinux = Convert-ToWslHostPath $cadicalDirectory
$dratEncoded = Convert-ToBase64 $dratLinux
$cadicalEncoded = Convert-ToBase64 $cadicalLinux

$dratBuildScript = @'
set -eu
p=$(printf '%s' "$1" | base64 -d)
cd "$p"
make drat-trim lrat-check
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
$dratBuildScript | & wsl -u root -e sh -s -- $dratEncoded
if ($LASTEXITCODE -ne 0) { throw "failed to build drat-trim/lrat-check" }

# This is the manual build documented in CaDiCaL's BUILD.md.  It avoids an
# upstream generated-header bug when the checkout path contains spaces.
$cadicalBuildScript = @'
set -eu
p=$(printf '%s' "$1" | base64 -d)
cd "$p/src"
export SOURCE_DATE_EPOCH="$2" TZ=UTC
find . -maxdepth 1 -name '*.cpp' ! -name 'mobical.cpp' -print0 |
  sort -z |
  xargs -0 g++ -O3 -DNDEBUG -DNBUILD -o ../cadical-linux
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
$cadicalBuildScript | & wsl -u root -e sh -s -- $cadicalEncoded $cadicalSourceDateEpoch
if ($LASTEXITCODE -ne 0) { throw "failed to build CaDiCaL" }

$cadicalBinary = Join-Path $cadicalDirectory "cadical-linux"
$dratBinary = Join-Path $dratDirectory "drat-trim"
$lratBinary = Join-Path $dratDirectory "lrat-check"

$record = [ordered]@{
    cadical_commit = $cadicalCommit
    cadical_sha256 = (Get-FileHash $cadicalBinary -Algorithm SHA256).Hash.ToLowerInvariant()
    drat_trim_commit = $dratCommit
    drat_trim_sha256 = (Get-FileHash $dratBinary -Algorithm SHA256).Hash.ToLowerInvariant()
    lrat_check_sha256 = (Get-FileHash $lratBinary -Algorithm SHA256).Hash.ToLowerInvariant()
    source_date_epoch = $cadicalSourceDateEpoch
}
$record | ConvertTo-Json | Set-Content -Encoding utf8 $manifestPath
$record | ConvertTo-Json
