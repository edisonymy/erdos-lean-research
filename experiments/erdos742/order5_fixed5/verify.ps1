param(
    [string]$OutputDirectory = ".tmp/erdos742-order5-fixed5-verify",
    [string]$PythonExecutable = "",
    [string]$ZstdExecutable = ""
)

$ErrorActionPreference = "Stop"
$certificateDirectory = $PSScriptRoot
$workspace = (Resolve-Path (Join-Path $certificateDirectory "../../..")).Path
$generator = Join-Path $certificateDirectory "generate_cases.py"
$audit = Join-Path $certificateDirectory "audit_reduction.py"
$smallQuotientAudit = Join-Path $certificateDirectory "audit_small_quotient.py"
$manifestPath = Join-Path $certificateDirectory "MANIFEST.json"
$checker = Join-Path $workspace "third_party/drat-trim/lrat-check"
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

function Get-LowerHash([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

if ((Get-LowerHash $generator) -ne $manifest.generator.sha256) {
    throw "generator hash mismatch"
}
if ((Get-LowerHash $audit) -ne $manifest.reduction_audit.sha256) {
    throw "reduction-audit hash mismatch"
}
if ((Get-LowerHash $smallQuotientAudit) -ne $manifest.small_quotient_audit.sha256) {
    throw "small-quotient-audit hash mismatch"
}
if ((Get-LowerHash $checker) -ne $manifest.proof_tools.lrat_check_sha256) {
    throw "pinned lrat-check hash mismatch"
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

$outputFull = if ([IO.Path]::IsPathRooted($OutputDirectory)) {
    [IO.Path]::GetFullPath($OutputDirectory)
} else {
    [IO.Path]::GetFullPath((Join-Path $workspace $OutputDirectory))
}
New-Item -ItemType Directory -Force -Path $outputFull | Out-Null
if (Get-ChildItem -LiteralPath $outputFull -Force | Select-Object -First 1) {
    throw "output directory is not empty"
}

$auditOutput = & $PythonExecutable $audit 2>&1
if ($LASTEXITCODE -ne 0 -or ($auditOutput -join "`n") -notmatch '"status": "PASS"') {
    throw "finite reduction audit failed"
}
$auditOutput | Set-Content -LiteralPath (Join-Path $outputFull "audit_reduction.json") -Encoding utf8

$smallAuditOutput = & $PythonExecutable $smallQuotientAudit 2>&1
if ($LASTEXITCODE -ne 0 -or
    ($smallAuditOutput -join "`n") -notmatch '"status": "PASS"' -or
    ($smallAuditOutput -join "`n") -notmatch '"mismatches": 0') {
    throw "small quotient-vs-definition audit failed"
}
$smallAuditOutput | Set-Content `
    -LiteralPath (Join-Path $outputFull "audit_small_quotient.json") -Encoding utf8

$records = @()
foreach ($case in $manifest.cases) {
    $caseDirectory = Join-Path $outputFull $case.name
    New-Item -ItemType Directory -Path $caseDirectory | Out-Null
    $cnf = Join-Path $caseDirectory "case.cnf"
    $metadata = Join-Path $caseDirectory "build.json"
    $generatorLog = Join-Path $caseDirectory "generator.log"
    $lrat = Join-Path $caseDirectory "case.lrat"
    $lratLog = Join-Path $caseDirectory "lrat-check.log"
    $compressed = Join-Path $certificateDirectory $case.compressed_lrat

    if ((Get-Item -LiteralPath $compressed).Length -ne $case.compressed_bytes -or
        (Get-LowerHash $compressed) -ne $case.compressed_sha256) {
        throw "compressed certificate mismatch for $($case.name)"
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
        --metadata $metadata 2>&1
    $generatorOutput | Set-Content -LiteralPath $generatorLog -Encoding utf8
    if ($LASTEXITCODE -ne 0 -or
        (Get-Item -LiteralPath $cnf).Length -ne $case.cnf_bytes -or
        (Get-LowerHash $cnf) -ne $case.cnf_sha256) {
        throw "CNF regeneration mismatch for $($case.name)"
    }

    & $ZstdExecutable -d -f $compressed -o $lrat | Out-Null
    if ($LASTEXITCODE -ne 0 -or
        (Get-Item -LiteralPath $lrat).Length -ne $case.lrat_bytes -or
        (Get-LowerHash $lrat) -ne $case.lrat_sha256) {
        throw "LRAT decompression mismatch for $($case.name)"
    }

    $checkerLinux = "/mnt/host/" + $checker.Substring(0, 1).ToLowerInvariant() + "/" + `
        $checker.Substring(3).Replace("\", "/")
    $cnfLinux = "/mnt/host/" + $cnf.Substring(0, 1).ToLowerInvariant() + "/" + `
        $cnf.Substring(3).Replace("\", "/")
    $lratLinux = "/mnt/host/" + $lrat.Substring(0, 1).ToLowerInvariant() + "/" + `
        $lrat.Substring(3).Replace("\", "/")
    $checkerOutput = & wsl -e $checkerLinux $cnfLinux $lratLinux 2>&1
    $checkerCode = $LASTEXITCODE
    $checkerOutput | Set-Content -LiteralPath $lratLog -Encoding utf8
    if ($checkerCode -ne 0 -or ($checkerOutput -join "`n") -notmatch "(?m)^c VERIFIED\s*$") {
        throw "LRAT verification failed for $($case.name)"
    }
    $records += [ordered]@{
        case = $case.name
        cnf_sha256 = Get-LowerHash $cnf
        lrat_sha256 = Get-LowerHash $lrat
        status = "VERIFIED"
    }
}

$records | ConvertTo-Json -Depth 4
