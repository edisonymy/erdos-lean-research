[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$root = (Resolve-Path (Join-Path $here '..\..\..')).Path
$bin = Join-Path $here 'bin'
$examples = Join-Path $root 'third_party\drat-trim\examples'
$out = Join-Path $here 'test-output'
$drat = Join-Path $bin 'drat-trim.exe'
$lrat = Join-Path $bin 'lrat-check.exe'
foreach ($path in @($drat, $lrat)) { if (!(Test-Path -LiteralPath $path)) { throw "build checker first: $path" } }
New-Item -ItemType Directory -Force -Path $out | Out-Null

$cnf = Join-Path $examples 'example-5-vars.cnf'
$proof = Join-Path $examples 'example-5-vars.drat'
$upstreamLrat = Join-Path $examples 'example-5-vars.lrat'
$generatedLrat = Join-Path $out 'example-5-vars.generated.lrat'
$dratLog = Join-Path $out 'drat-trim.log'
$generatedLog = Join-Path $out 'lrat-check.generated.log'
$upstreamLog = Join-Path $out 'lrat-check.upstream.log'

$commands = @(
    "& `"$drat`" `"$cnf`" `"$proof`" -L `"$generatedLrat`"",
    "& `"$lrat`" `"$cnf`" `"$generatedLrat`"",
    "& `"$lrat`" `"$cnf`" `"$upstreamLrat`""
)
$dratText = (& $drat $cnf $proof '-L' $generatedLrat 2>&1 | Out-String)
$dratExit = $LASTEXITCODE
$dratText | Set-Content -LiteralPath $dratLog -Encoding utf8
if ($dratExit -ne 0 -or $dratText -notmatch '(?m)^s VERIFIED\s*$') { throw 'DRAT example was not verified' }

$generatedText = (& $lrat $cnf $generatedLrat 2>&1 | Out-String)
$generatedExit = $LASTEXITCODE
$generatedText | Set-Content -LiteralPath $generatedLog -Encoding utf8
if ($generatedExit -ne 0 -or $generatedText -notmatch '(?m)^c VERIFIED\s*$') { throw 'generated LRAT was not verified' }

$upstreamText = (& $lrat $cnf $upstreamLrat 2>&1 | Out-String)
$upstreamExit = $LASTEXITCODE
$upstreamText | Set-Content -LiteralPath $upstreamLog -Encoding utf8
if ($upstreamExit -ne 0 -or $upstreamText -notmatch '(?m)^c VERIFIED\s*$') { throw 'upstream LRAT was not verified' }

function Hash([string]$path) { return (Get-FileHash -Algorithm SHA256 $path).Hash.ToLowerInvariant() }
$manifest = [ordered]@{
    artifact = 'windows_drat_trim_example_validation'
    status = 'VALIDATED'
    commands = $commands
    success_boundary = [ordered]@{
        drat_trim = 'exit code 0 and output line s VERIFIED'
        generated_lrat_check = 'exit code 0 and output line c VERIFIED'
        upstream_lrat_check = 'exit code 0 and output line c VERIFIED'
        scope = 'certifies the checked DIMACS/proof pair only, not any high-level encoding claim'
    }
    inputs = [ordered]@{
        'third_party/drat-trim/examples/example-5-vars.cnf' = (Hash $cnf)
        'third_party/drat-trim/examples/example-5-vars.drat' = (Hash $proof)
        'third_party/drat-trim/examples/example-5-vars.lrat' = (Hash $upstreamLrat)
    }
    binaries = [ordered]@{
        'bin/drat-trim.exe' = (Hash $drat)
        'bin/lrat-check.exe' = (Hash $lrat)
    }
    outputs = [ordered]@{
        'test-output/example-5-vars.generated.lrat' = (Hash $generatedLrat)
        'test-output/drat-trim.log' = (Hash $dratLog)
        'test-output/lrat-check.generated.log' = (Hash $generatedLog)
        'test-output/lrat-check.upstream.log' = (Hash $upstreamLog)
    }
    build_manifest_sha256 = Hash (Join-Path $here 'build-manifest.json')
    validator_script_sha256 = Hash $PSCommandPath
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $here 'validation-manifest.json') -Encoding utf8
Write-Output (Join-Path $here 'validation-manifest.json')
