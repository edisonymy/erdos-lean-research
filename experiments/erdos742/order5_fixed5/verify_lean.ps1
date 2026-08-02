param(
    [string]$PythonExecutable = "",
    [string]$ZstdExecutable = "",
    [string]$LakeExecutable = ""
)

$ErrorActionPreference = "Stop"
$packageDirectory = $PSScriptRoot
$workspace = (Resolve-Path (Join-Path $packageDirectory "../../..")).Path
$outputDirectory = Join-Path $workspace ".tmp/erdos742-order5-fixed5-lean"
$generator = Join-Path $packageDirectory "generate_cases.py"
$baseManifest = Get-Content -LiteralPath (Join-Path $packageDirectory "MANIFEST.json") -Raw | ConvertFrom-Json
$leanManifest = Get-Content -LiteralPath (Join-Path $packageDirectory "LEAN_MANIFEST.json") -Raw | ConvertFrom-Json
$leanProject = Join-Path $packageDirectory "LeanCNF"

function Get-LowerHash([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

if ((Get-LowerHash $generator) -ne $baseManifest.generator.sha256) {
    throw "generator hash mismatch"
}

if ([string]::IsNullOrWhiteSpace($PythonExecutable)) {
    $workspacePython = Join-Path $workspace ".venv/Scripts/python.exe"
    if (Test-Path -LiteralPath $workspacePython) {
        $PythonExecutable = $workspacePython
    } else {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCommand) { throw "Python with python-sat is required" }
        $PythonExecutable = $pythonCommand.Source
    }
}
$PythonExecutable = (Resolve-Path -LiteralPath $PythonExecutable).Path
& $PythonExecutable -c "import pysat"
if ($LASTEXITCODE -ne 0) { throw "selected Python does not provide python-sat" }

if ([string]::IsNullOrWhiteSpace($ZstdExecutable)) {
    $zstdCommand = Get-Command zstd -ErrorAction SilentlyContinue
    if ($zstdCommand) {
        $ZstdExecutable = $zstdCommand.Source
    } elseif (Test-Path -LiteralPath "C:\ProgramData\miniconda3\Library\bin\zstd.exe") {
        $ZstdExecutable = "C:\ProgramData\miniconda3\Library\bin\zstd.exe"
    } else {
        throw "zstd is required; pass -ZstdExecutable"
    }
}
$ZstdExecutable = (Resolve-Path -LiteralPath $ZstdExecutable).Path

if ([string]::IsNullOrWhiteSpace($LakeExecutable)) {
    $lakeCommand = Get-Command lake -ErrorAction SilentlyContinue
    if ($lakeCommand) {
        $LakeExecutable = $lakeCommand.Source
    } else {
        $elanLake = Join-Path $env:USERPROFILE ".elan/bin/lake.exe"
        if (-not (Test-Path -LiteralPath $elanLake)) {
            throw "lake/elan is required; pass -LakeExecutable"
        }
        $LakeExecutable = $elanLake
    }
}
$LakeExecutable = (Resolve-Path -LiteralPath $LakeExecutable).Path

New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null

$baseCases = @{}
foreach ($case in $baseManifest.cases) { $baseCases[$case.name] = $case }

foreach ($case in $leanManifest.cases) {
    if (-not $baseCases.ContainsKey($case.name)) {
        throw "Lean manifest names unknown base case $($case.name)"
    }
    $caseDirectory = Join-Path $outputDirectory $case.name
    New-Item -ItemType Directory -Force -Path $caseDirectory | Out-Null
    $cnf = Join-Path $caseDirectory "case.cnf"
    $metadata = Join-Path $caseDirectory "build.json"
    $lrat = Join-Path $caseDirectory "case.direct.lrat"
    $compressed = Join-Path $packageDirectory $case.compressed_lrat

    if ((Get-Item -LiteralPath $compressed).Length -ne $case.compressed_bytes -or
        (Get-LowerHash $compressed) -ne $case.compressed_sha256) {
        throw "compressed direct LRAT mismatch for $($case.name)"
    }

    $generatorOutput = & $PythonExecutable $generator `
        --fixed 5 `
        --quotient `
        --fixed-graph-type $case.name `
        --max-degree 17 `
        --no-dominating-edge `
        --unique-witness-markers `
        --normalizer-lex `
        --cnf $cnf `
        --metadata $metadata
    if ($LASTEXITCODE -ne 0 -or
        (Get-LowerHash $cnf) -ne $case.cnf_sha256 -or
        (Get-LowerHash $cnf) -ne $baseCases[$case.name].cnf_sha256) {
        throw "CNF regeneration mismatch for $($case.name)"
    }

    & $ZstdExecutable -d -f $compressed -o $lrat | Out-Null
    if ($LASTEXITCODE -ne 0 -or
        (Get-Item -LiteralPath $lrat).Length -ne $case.direct_lrat_bytes -or
        (Get-LowerHash $lrat) -ne $case.direct_lrat_sha256) {
        throw "direct LRAT decompression mismatch for $($case.name)"
    }
}

Push-Location $leanProject
try {
    & $LakeExecutable build LRATCatcher
    if ($LASTEXITCODE -ne 0) { throw "building pinned LRAT-Catcher failed" }
    & $LakeExecutable env lean Main.lean
    if ($LASTEXITCODE -ne 0) { throw "Lean LRAT replay failed" }
} finally {
    Pop-Location
}

Write-Output "VERIFIED: six Erdős #742 fixed-five DIMACS formulas are Lean-certified UNSAT"
