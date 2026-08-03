$ErrorActionPreference = 'Stop'

$expected = [ordered]@{
    'three_pole_scan.py' = 'ABE5AD941D852710A879F4D7F62621A799A58C63A158563FA1D25CE5721E1DF2'
    'three_pole_scan.json' = 'EB66AF5F78D1A8942FB7E1299CA4E3E8F61C173FC3803E4123BCCE25C085335E'
    'three_pole_scan_through22.json' = 'B6A2364F23A169DAD720EFB7D0526AF4B378DD5D37CA106DABC7C10A78EBC4CB'
    'pair_insertion_vertex_poles.py' = '751EA1CF18FCC71C6AB6EABEC79A6AEECCE63F2216A0691FD5807854A1C1C1FB'
    'pair_insertion_vertex_poles.json' = 'C55CEDD9D0096EB81FFFC69940AA9EADA1C763742F91A8F552F5731644363F5A'
}

foreach ($name in $expected.Keys) {
    $path = Join-Path $PSScriptRoot $name
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash
    if ($actual -ne $expected[$name]) {
        throw "SHA-256 mismatch for $name`: expected $($expected[$name]), got $actual"
    }
}

foreach ($name in 'three_pole_scan.json','three_pole_scan_through22.json','pair_insertion_vertex_poles.json') {
    $payload = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot $name) | ConvertFrom-Json
    if (-not $payload.complete) { throw "$name is not marked complete" }
    if ($null -ne $payload.candidate) { throw "$name unexpectedly contains a candidate" }
    foreach ($property in $payload.input_sha256.PSObject.Properties) {
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $property.Name).Hash.ToLowerInvariant()
        if ($actual -ne $property.Value) {
            throw "upstream SHA-256 mismatch for $($property.Name)"
        }
    }
}

$n22 = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'three_pole_scan.json') | ConvertFrom-Json
if ($n22.stats.source_graphs -ne 645 -or $n22.poles.Count -ne 0) {
    throw 'unexpected order-22 scan counts'
}

$all = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'three_pole_scan_through22.json') | ConvertFrom-Json
if ($all.stats.source_graphs -ne 1389 -or $all.stats.safe_poles -ne 9 -or
    $all.stats.signature_pair_bijections -ne 60) {
    throw 'unexpected through-order-22 scan counts'
}

$insertions = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'pair_insertion_vertex_poles.json') | ConvertFrom-Json
if ($insertions.stats.operation_instances -ne 340560 -or $insertions.poles.Count -ne 0) {
    throw 'unexpected pair-insertion scan counts'
}

Write-Output 'PASS: frozen scan artifacts, upstream inputs, counts, and null candidates verified.'
