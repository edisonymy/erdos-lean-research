param(
  [Parameter(Mandatory = $true)]
  [string]$AssetDirectory,
  [string]$OutputDirectory = ".tmp/erdos742-fixed10-verify",
  [switch]$Regenerate
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../../..")).Path
$assetRoot = (Resolve-Path $AssetDirectory).Path
$assetCnf = Join-Path $assetRoot "case.cnf"
$assetLratZst = Join-Path $assetRoot "case.lrat.zst"
$outputRoot = Join-Path $repoRoot $OutputDirectory
$outputCnf = Join-Path $outputRoot "case.cnf"
$outputLrat = Join-Path $outputRoot "case.lrat"

function Assert-Sha256([string]$Path, [string]$Expected) {
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required file: $Path"
  }
  $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -ne $Expected) {
    throw "SHA-256 mismatch for ${Path}: expected $Expected, got $actual"
  }
}

New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null
Assert-Sha256 $assetCnf "d76aa6ff29e65423b3bb72a8f11451d7d4d8b6fb80943e2929b85bd9e179658f"
Assert-Sha256 $assetLratZst "c8d97f2d10add1c96c38a03b442d20e6fd1150143fbf20ed17dcd41475e35e0c"
Copy-Item -LiteralPath $assetCnf -Destination $outputCnf -Force

$python = Join-Path $repoRoot ".venv/Scripts/python.exe"
if (-not (Test-Path -LiteralPath $python)) {
  $python = "python"
}

Push-Location $repoRoot
try {
  & $python experiments/erdos742/order5_other_fixed/audit_search.py
  if ($LASTEXITCODE -ne 0) { throw "Independent implementation audit failed" }

  if ($Regenerate) {
    $regenCnf = Join-Path $outputRoot "regenerated.cnf"
    $regenMetadata = Join-Path $outputRoot "regenerated-build.json"
    $regenCandidate = Join-Path $outputRoot "unexpected-candidate.json"
    & $python experiments/erdos742/order5_other_fixed/search.py `
      --fixed 10 --cnf $regenCnf --metadata $regenMetadata `
      --candidate $regenCandidate
    if ($LASTEXITCODE -ne 0) { throw "CNF regeneration/search failed" }
    Assert-Sha256 $regenCnf "d76aa6ff29e65423b3bb72a8f11451d7d4d8b6fb80943e2929b85bd9e179658f"
  }

  & zstd -d -f $assetLratZst -o $outputLrat
  if ($LASTEXITCODE -ne 0) { throw "LRAT decompression failed" }
  Assert-Sha256 $outputLrat "86e35dcfd075be8a9a1ac5d6248f3074817c28b255d8d3cea59585a30b2f255e"

  $relativeCnf = $outputCnf.Substring($repoRoot.Length).TrimStart([char[]]"\/").Replace("\", "/")
  $relativeLrat = $outputLrat.Substring($repoRoot.Length).TrimStart([char[]]"\/").Replace("\", "/")
  & wsl -e ./third_party/drat-trim/lrat-check $relativeCnf $relativeLrat
  if ($LASTEXITCODE -ne 0) { throw "Native LRAT replay failed" }
} finally {
  Pop-Location
}

Write-Host "VERIFIED: Erdős #742 cycle type 1^10 5^3"
