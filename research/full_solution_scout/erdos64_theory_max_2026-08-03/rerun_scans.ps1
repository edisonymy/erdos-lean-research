$ErrorActionPreference = 'Stop'

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$python = Join-Path $repo '.venv\Scripts\python.exe'
$source = Join-Path $repo 'research\full_solution_scout\erdos64_nonhamiltonian_cubic_max_2026-08-03'
$scanner = Join-Path $PSScriptRoot 'three_pole_scan.py'
$insertionScanner = Join-Path $PSScriptRoot 'pair_insertion_vertex_poles.py'

$n22 = Get-ChildItem -LiteralPath $source -Filter 'cubic_n22_part*_dyadic_pair_structure.json' |
    Sort-Object Name |
    ForEach-Object FullName

& $python $scanner @n22 `
    --scope 'order-22 exact hard-core (no edge-disjoint dyadic pair) records' `
    --output (Join-Path $PSScriptRoot 'three_pole_scan.json')
if ($LASTEXITCODE -ne 0) { throw "order-22 scan exited $LASTEXITCODE" }

$through22 = @()
foreach ($n in 4,6,8,10,12,14,16,18,20) {
    $name = 'cubic_n{0}_dyadic_pair_structure.json' -f $n.ToString('00')
    $through22 += (Resolve-Path (Join-Path $source $name)).Path
}
$through22 += $n22

& $python $scanner @through22 `
    --scope 'orders 4 through 22 exact hard-core (no edge-disjoint dyadic pair) records' `
    --output (Join-Path $PSScriptRoot 'three_pole_scan_through22.json')
if ($LASTEXITCODE -ne 0) { throw "through-order-22 scan exited $LASTEXITCODE" }

& $python $insertionScanner @n22 `
    --output (Join-Path $PSScriptRoot 'pair_insertion_vertex_poles.json')
if ($LASTEXITCODE -ne 0) { throw "pair-insertion scan exited $LASTEXITCODE" }

Write-Output 'PASS: all scan outputs regenerated.'
