param(
    [Parameter(Mandatory = $true)] [string] $Geng,
    [Parameter(Mandatory = $true)] [string] $Labelg,
    [string] $WorkDirectory = (Join-Path $PSScriptRoot "work")
)

$ErrorActionPreference = "Stop"
$expectedRecords = 2174357
$expectedDigest = "5997409f26372eea577b7a6bec6b94e3f26282ba7ba5473ae9f54ab69ad98889"
$gengPath = (Resolve-Path -LiteralPath $Geng).Path
$labelgPath = (Resolve-Path -LiteralPath $Labelg).Path
$workPath = [System.IO.Path]::GetFullPath($WorkDirectory)
New-Item -ItemType Directory -Force -Path $workPath | Out-Null

function Invoke-Native([scriptblock] $Command) {
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "native command failed with exit code $LASTEXITCODE" }
}

Invoke-Native { dotnet build (Join-Path $PSScriptRoot "ResidualTools.csproj") -c Release }
Invoke-Native { dotnet build (Join-Path $PSScriptRoot "DenseScreen.csproj") -c Release }
Invoke-Native { dotnet build (Join-Path $PSScriptRoot "IndependentVerify.csproj") -c Release }

$tools = Join-Path $PSScriptRoot "bin\ResidualTools\Release\net8.0\ResidualTools.dll"
$screen = Join-Path $PSScriptRoot "bin\DenseScreen\Release\net8.0\DenseScreen.dll"
$verify = Join-Path $PSScriptRoot "bin\IndependentVerify\Release\net8.0\IndependentVerify.dll"
$rawA = Join-Path $workPath "family_a_raw.g6"
$familyA = Join-Path $workPath "family_a.g6"
$base10 = Join-Path $workPath "base10.g6"
$base9 = Join-Path $workPath "base9.g6"
$rawB = Join-Path $workPath "family_b_raw.g6"
$rawC = Join-Path $workPath "family_c_raw.g6"
$rawD = Join-Path $workPath "family_d_raw.g6"
$familyB = Join-Path $workPath "family_b.g6"
$familyC = Join-Path $workPath "family_c.g6"
$familyD = Join-Path $workPath "family_d.g6"
$residual = Join-Path $workPath "residual.g6"
$residualSummary = Join-Path $workPath "residual_summary.json"
$unresolved = Join-Path $workPath "unresolved.g6"
$primarySummary = Join-Path $workPath "primary_summary.json"
$independentSummary = Join-Path $workPath "independent_summary.json"

Invoke-Native { & $gengPath -q 11 0:16 $rawA }
Invoke-Native { & $gengPath -q 10 0:10 $base10 }
Invoke-Native { & $gengPath -q 9 0:4 $base9 }
Invoke-Native { dotnet $tools expand-file delete-one $base10 $rawB }
Invoke-Native { dotnet $tools expand-file delete-two $base9 $rawC }
Invoke-Native { dotnet $tools expand-file cover-three - $rawD }
Invoke-Native { & $labelgPath -q $rawA $familyA }
Invoke-Native { & $labelgPath -q $rawB $familyB }
Invoke-Native { & $labelgPath -q $rawC $familyC }
Invoke-Native { & $labelgPath -q $rawD $familyD }
Invoke-Native { dotnet $tools union $residual $residualSummary $familyA $familyB $familyC $familyD }
Invoke-Native { dotnet $screen $unresolved $primarySummary $residual }
Invoke-Native { dotnet $verify $residual $independentSummary }

$residualResult = Get-Content -LiteralPath $residualSummary -Raw | ConvertFrom-Json
$primaryResult = Get-Content -LiteralPath $primarySummary -Raw | ConvertFrom-Json
$independentResult = Get-Content -LiteralPath $independentSummary -Raw | ConvertFrom-Json
if ($residualResult.union_records -ne $expectedRecords -or $residualResult.union_sha256 -ne $expectedDigest) {
    throw "residual count or digest mismatch"
}
if ($primaryResult.records -ne $expectedRecords -or $primaryResult.residual_sha256 -ne $expectedDigest -or $primaryResult.unresolved -ne 0) {
    throw "primary witness screen mismatch"
}
if ($independentResult.records -ne $expectedRecords -or $independentResult.residual_sha256 -ne $expectedDigest -or
    $independentResult.outside_puleo_residual -ne 0 -or $independentResult.unresolved -ne 0) {
    throw "independent verification mismatch"
}

$manifest = [ordered]@{
    schema = "tuza-order-11-reproduction-manifest-v1"
    generated_utc = [DateTime]::UtcNow.ToString("o")
    dotnet_version = (& dotnet --version).Trim()
    geng_version = ((& $gengPath -version 2>&1) -join " ").Trim()
    geng_sha256 = (Get-FileHash -LiteralPath $gengPath -Algorithm SHA256).Hash.ToLowerInvariant()
    labelg_version = ((& $labelgPath -version 2>&1) -join " ").Trim()
    labelg_sha256 = (Get-FileHash -LiteralPath $labelgPath -Algorithm SHA256).Hash.ToLowerInvariant()
    residual_records = $residualResult.union_records
    residual_sha256 = $residualResult.union_sha256
    primary_unresolved = $primaryResult.unresolved
    independent_unresolved = $independentResult.unresolved
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $workPath "manifest.json") -Encoding UTF8
$manifest | ConvertTo-Json -Depth 4
