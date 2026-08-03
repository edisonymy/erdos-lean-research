[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$root = (Resolve-Path (Join-Path $here '..\..\..')).Path
$source = Join-Path $root 'third_party\drat-trim'
$out = Join-Path $here 'bin'
$vsdev = 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat'
if (!(Test-Path -LiteralPath $vsdev)) { throw "VsDevCmd.bat not found: $vsdev" }
New-Item -ItemType Directory -Force -Path $out | Out-Null

$include = Join-Path $here 'compat_include'
$drat = Join-Path $source 'drat-trim.c'
$lrat = Join-Path $source 'lrat-check.c'
$dratExe = Join-Path $out 'drat-trim.exe'
$lratExe = Join-Path $out 'lrat-check.exe'
$flags = '/nologo /O2 /W4 /TC /D_CRT_SECURE_NO_WARNINGS'

# Run MSVC inside its supplied environment; the source files are only inputs.
$commands = @(
    "call `"$vsdev`" -arch=x64 -host_arch=x64 && cl.exe $flags /I `"$include`" /Fo:`"$out\drat-trim.obj`" /Fe:`"$dratExe`" `"$drat`"",
    "call `"$vsdev`" -arch=x64 -host_arch=x64 && cl.exe $flags /I `"$include`" /Fo:`"$out\lrat-check.obj`" /Fe:`"$lratExe`" `"$lrat`""
)
foreach ($command in $commands) {
    & cmd.exe /d /s /c $command
    if ($LASTEXITCODE -ne 0) { throw "MSVC compilation failed with exit code $LASTEXITCODE" }
}

$compiler_lines = & cmd.exe /d /s /c "call `"$vsdev`" -arch=x64 -host_arch=x64 >nul && cl.exe 2>&1"
$version = ($compiler_lines | Where-Object { $_ -match '^Microsoft .*Compiler Version' } | Select-Object -First 1)
$sourceRevision = (& git.exe -C $source rev-parse HEAD).Trim()
$manifest = [ordered]@{
    artifact = 'windows_drat_trim_build'
    status = 'BUILT_NOT_YET_VALIDATED'
    architecture = 'x64'
    compiler_banner = [string]$version
    pinned_source_git_revision = $sourceRevision
    commands = $commands
    sources = [ordered]@{
        'third_party/drat-trim/drat-trim.c' = (Get-FileHash -Algorithm SHA256 $drat).Hash.ToLowerInvariant()
        'third_party/drat-trim/lrat-check.c' = (Get-FileHash -Algorithm SHA256 $lrat).Hash.ToLowerInvariant()
        'compat_include/sys/time.h' = (Get-FileHash -Algorithm SHA256 (Join-Path $include 'sys\time.h')).Hash.ToLowerInvariant()
        'build.ps1' = (Get-FileHash -Algorithm SHA256 $PSCommandPath).Hash.ToLowerInvariant()
    }
    binaries = [ordered]@{
        'bin/drat-trim.exe' = (Get-FileHash -Algorithm SHA256 $dratExe).Hash.ToLowerInvariant()
        'bin/lrat-check.exe' = (Get-FileHash -Algorithm SHA256 $lratExe).Hash.ToLowerInvariant()
    }
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $here 'build-manifest.json') -Encoding utf8
Write-Output (Join-Path $here 'build-manifest.json')
