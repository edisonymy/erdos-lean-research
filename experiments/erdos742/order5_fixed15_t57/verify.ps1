param(
  [Parameter(Mandatory = $true)]
  [string]$AssetDirectory,
  [string]$OutputDirectory = ".tmp/erdos742-fixed15-t57-verify",
  [string]$ZstdExecutable = "",
  [switch]$Regenerate
)

$ErrorActionPreference = "Stop"
$packageRoot = $PSScriptRoot
$repoRoot = (Resolve-Path (Join-Path $packageRoot "../../..")).Path
$assetRoot = (Resolve-Path -LiteralPath $AssetDirectory).Path
$manifest = Get-Content -LiteralPath (Join-Path $packageRoot "MANIFEST.json") -Raw | ConvertFrom-Json
$outputRoot = Join-Path $repoRoot $OutputDirectory

function Assert-File([string]$Path, [long]$Bytes, [string]$Sha256) {
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required file: $Path"
  }
  $item = Get-Item -LiteralPath $Path
  if ($item.Length -ne $Bytes) {
    throw "Byte-size mismatch for ${Path}: expected $Bytes, got $($item.Length)"
  }
  $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -ne $Sha256) {
    throw "SHA-256 mismatch for ${Path}: expected $Sha256, got $actual"
  }
}

foreach ($source in $manifest.sources.PSObject.Properties) {
  $sourcePath = Join-Path $repoRoot $source.Value.file
  Assert-File $sourcePath $source.Value.bytes $source.Value.sha256
}

$assetCnf = Join-Path $assetRoot $manifest.assets.cnf.file
$assetProofZst = Join-Path $assetRoot $manifest.assets.compressed_lrat.file
$assetResult = Join-Path $assetRoot $manifest.assets.result.file
$assetBuildMetadata = Join-Path $assetRoot $manifest.assets.build_metadata.file
$assetSolverLog = Join-Path $assetRoot $manifest.assets.solver_log.file
$assetCheckerLog = Join-Path $assetRoot $manifest.assets.checker_log.file
$assetCheckerBinary = Join-Path $assetRoot $manifest.assets.lrat_checker.file
Assert-File $assetCnf $manifest.assets.cnf.bytes $manifest.assets.cnf.sha256
Assert-File $assetProofZst $manifest.assets.compressed_lrat.bytes $manifest.assets.compressed_lrat.sha256
Assert-File $assetResult $manifest.assets.result.bytes $manifest.assets.result.sha256
Assert-File $assetBuildMetadata $manifest.assets.build_metadata.bytes $manifest.assets.build_metadata.sha256
Assert-File $assetSolverLog $manifest.assets.solver_log.bytes $manifest.assets.solver_log.sha256
Assert-File $assetCheckerLog $manifest.assets.checker_log.bytes $manifest.assets.checker_log.sha256
Assert-File $assetCheckerBinary $manifest.assets.lrat_checker.bytes $manifest.assets.lrat_checker.sha256

if ([string]::IsNullOrWhiteSpace($ZstdExecutable)) {
  $zstd = Get-Command zstd -ErrorAction SilentlyContinue
  if ($zstd) {
    $ZstdExecutable = $zstd.Source
  } elseif (Test-Path -LiteralPath "C:\ProgramData\miniconda3\Library\bin\zstd.exe") {
    $ZstdExecutable = "C:\ProgramData\miniconda3\Library\bin\zstd.exe"
  } else {
    throw "zstd is required; pass -ZstdExecutable"
  }
}

New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null
$outputCnf = Join-Path $outputRoot "case.cnf"
$outputProof = Join-Path $outputRoot "case.direct.lrat"
$outputChecker = Join-Path $outputRoot "lrat-check"
Copy-Item -LiteralPath $assetCnf -Destination $outputCnf -Force
Copy-Item -LiteralPath $assetCheckerBinary -Destination $outputChecker -Force

Push-Location $repoRoot
try {
  $python = Join-Path $repoRoot ".venv/Scripts/python.exe"
  if (-not (Test-Path -LiteralPath $python)) { $python = "python" }

  & $python experiments/erdos742/order5_other_fixed/audit_split_search.py
  if ($LASTEXITCODE -ne 0) { throw "Independent split implementation audit failed" }

  if ($Regenerate) {
    $regenerated = Join-Path $outputRoot "regenerated.cnf"
    $buildMetadata = Join-Path $outputRoot "regenerated-build.json"
    $unexpectedCandidate = Join-Path $outputRoot "unexpected-candidate.json"
    & $python experiments/erdos742/order5_other_fixed/search_split_case.py `
      --fixed 15 --fixed-edge-count 57 --build-only --solver cadical195 `
      --cnf $regenerated --metadata $buildMetadata --candidate $unexpectedCandidate
    if ($LASTEXITCODE -ne 0) { throw "CNF regeneration failed" }
    Assert-File $regenerated $manifest.assets.cnf.bytes $manifest.assets.cnf.sha256
  }

  & $ZstdExecutable -d -f $assetProofZst -o $outputProof
  if ($LASTEXITCODE -ne 0) { throw "LRAT decompression failed" }
  Assert-File $outputProof $manifest.proof.bytes $manifest.proof.sha256

  $relativeCnf = $outputCnf.Substring($repoRoot.Length).TrimStart([char[]]"\/").Replace("\", "/")
  $relativeProof = $outputProof.Substring($repoRoot.Length).TrimStart([char[]]"\/").Replace("\", "/")
  $relativeChecker = $outputChecker.Substring($repoRoot.Length).TrimStart([char[]]"\/").Replace("\", "/")
  & wsl.exe -e chmod +x "./$relativeChecker"
  if ($LASTEXITCODE -ne 0) { throw "Could not mark the pinned checker executable" }
  & wsl.exe -e "./$relativeChecker" "./$relativeCnf" "./$relativeProof"
  if ($LASTEXITCODE -ne 0) { throw "Native LRAT replay failed" }
} finally {
  Pop-Location
}

Write-Output "VERIFIED: Erdos #742 fixed-15 split t=57 hash-locked CNF is UNSAT"
