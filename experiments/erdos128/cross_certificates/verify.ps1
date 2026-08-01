param(
    [string]$OutputDirectory = ".tmp/erdos128-cross-certificate-verify",
    [string]$ZstdExecutable = "",
    [string]$PythonExecutable = ""
)

$ErrorActionPreference = "Stop"
$certificateDirectory = $PSScriptRoot
$workspace = (Resolve-Path (Join-Path $certificateDirectory "../../..")).Path
$generator = Join-Path $workspace "experiments/erdos128/cross_proof_cnf.py"
$checker = Join-Path $workspace "third_party/drat-trim/lrat-check"
$expectedCheckerHash = "8a5c1bde335526ac3778cc25ab6174ca2374659adb5df4a5cd5ddabce5b0f5d9"
$expected = @{
    1 = @{ Cnf = "1c7318ff62724cbc69eeec406a27f79572e3854702af69c1370c8743983fedf5"; Lrat = "6d5d7639a19f864f9db49526726a1343e1596dab7e847dd997c02b723df36d97"; Compressed = "ecb20dc728f28fd3cd1a496bba89537cefd468aecd8abe31cd018e499132b8a8" }
    2 = @{ Cnf = "74a6d906a39f8f7b845eb5478c9ba33b285369d044770181a14f1701b9e1109d"; Lrat = "7fb7a857212817cd7722371a0218d7210194535a36cadd528548140e216250da"; Compressed = "cf008fddee23429dc35692e59945112f189c98d46e8df2a5e71c1c3c01390c02" }
    3 = @{ Cnf = "f0da7d0f65d2da43e68a75a468b313e6ca242979084d4b7c1febd128322c1e09"; Lrat = "d6249fa72a2fe2fef350edbe1d91fd1251df5e358596cde05b96153041bfbd0a"; Compressed = "77e4da03b445abe2cd32eda97eefc4b5e32c7c60bf0c0fd53a0d20bb2cedf887" }
}

function Get-LowerHash([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Convert-ToWslHostPath([string]$Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    if ($full -notmatch '^[A-Za-z]:\\') { throw "unsupported path $full" }
    return "/mnt/host/" + $full.Substring(0, 1).ToLowerInvariant() + "/" + `
        $full.Substring(3).Replace("\", "/")
}

function Convert-ToBase64([string]$Value) {
    return [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Value))
}

if (-not (Test-Path -LiteralPath $checker)) { throw "missing pinned lrat-check" }
if ((Get-LowerHash $checker) -ne $expectedCheckerHash) { throw "lrat-check hash mismatch" }
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
if ([string]::IsNullOrWhiteSpace($PythonExecutable)) {
    $workspacePython = Join-Path $workspace ".venv/Scripts/python.exe"
    if (Test-Path -LiteralPath $workspacePython) {
        $PythonExecutable = $workspacePython
    } elseif (Test-Path -LiteralPath "C:\ProgramData\miniconda3\python.exe") {
        $PythonExecutable = "C:\ProgramData\miniconda3\python.exe"
    } else {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCommand) { throw "Python with python-sat is required" }
        $PythonExecutable = $pythonCommand.Source
    }
}
$PythonExecutable = (Resolve-Path -LiteralPath $PythonExecutable).Path
& $PythonExecutable -c "import pysat"
if ($LASTEXITCODE -ne 0) { throw "selected Python does not provide python-sat" }

$outputFull = if ([IO.Path]::IsPathRooted($OutputDirectory)) {
    [IO.Path]::GetFullPath($OutputDirectory)
} else {
    [IO.Path]::GetFullPath((Join-Path $workspace $OutputDirectory))
}
New-Item -ItemType Directory -Force -Path $outputFull | Out-Null
if (Get-ChildItem -LiteralPath $outputFull -Force | Select-Object -First 1) {
    throw "output directory is not empty"
}

$records = @()
foreach ($d in 1, 2, 3) {
    $caseDirectory = Join-Path $outputFull "d$d"
    New-Item -ItemType Directory -Path $caseDirectory | Out-Null
    $cnf = Join-Path $caseDirectory "case.cnf"
    $lrat = Join-Path $caseDirectory "case.lrat"
    $log = Join-Path $caseDirectory "lrat-check.log"
    $compressed = Join-Path $certificateDirectory "erdos128_n16_d$d.lrat.zst"
    if ((Get-LowerHash $compressed) -ne $expected[$d].Compressed) {
        throw "compressed certificate hash mismatch for d=$d"
    }
    & $PythonExecutable $generator $d --dimacs $cnf
    if ($LASTEXITCODE -ne 0 -or (Get-LowerHash $cnf) -ne $expected[$d].Cnf) {
        throw "CNF generation or hash check failed for d=$d"
    }
    & $ZstdExecutable -d -f $compressed -o $lrat
    if ($LASTEXITCODE -ne 0 -or (Get-LowerHash $lrat) -ne $expected[$d].Lrat) {
        throw "LRAT decompression or hash check failed for d=$d"
    }
    $script = @'
set -eu
exe=$(printf '%s' "$1" | base64 -d)
cnf=$(printf '%s' "$2" | base64 -d)
lrat=$(printf '%s' "$3" | base64 -d)
log=$(printf '%s' "$4" | base64 -d)
"$exe" "$cnf" "$lrat" >"$log" 2>&1
# end-of-script sentinel absorbs PowerShell's final CRLF
'@
    $script | & wsl -e sh -s -- `
        (Convert-ToBase64 (Convert-ToWslHostPath $checker)) `
        (Convert-ToBase64 (Convert-ToWslHostPath $cnf)) `
        (Convert-ToBase64 (Convert-ToWslHostPath $lrat)) `
        (Convert-ToBase64 (Convert-ToWslHostPath $log))
    $text = if (Test-Path -LiteralPath $log) { Get-Content -LiteralPath $log -Raw } else { "" }
    if ($LASTEXITCODE -ne 0 -or $text -notmatch "(?m)^c VERIFIED\s*$") {
        throw "LRAT verification failed for d=$d"
    }
    $records += [ordered]@{
        cross_degree = $d
        cnf_sha256 = Get-LowerHash $cnf
        lrat_sha256 = Get-LowerHash $lrat
        status = "VERIFIED"
    }
}
$records | ConvertTo-Json -Depth 4
