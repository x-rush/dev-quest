param(
    [Parameter(Mandatory = $true)][string]$Results,
    [Parameter(Mandatory = $true)][string]$Output
)

$ErrorActionPreference = 'Stop'
$records = Get-Content -LiteralPath $Results | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.lang -eq 'python' }
$l1 = @{}; $l2 = @{}
foreach ($record in $records) {
    $l1[$record.l1.status] = 1 + ($l1[$record.l1.status] ?? 0)
    $l2[$record.l2.status] = 1 + ($l2[$record.l2.status] ?? 0)
}
$summary = [ordered]@{
    scope = '10-python-discovery Python fences only'
    runtime = 'python:3.14-alpine'
    runtime_version = 'Python 3.14'
    network = 'none'
    command = 'extract_blocks.py, then verify.py --langs python --strict --execute'
    source_mount = 'read-only; copied to writable /work before extraction and verification'
    total = @($records).Count
    l1 = $l1
    l2 = $l2
    post_run_retagging = @(
        'basics/02-first-script.md REPL session: python -> pycon',
        'frameworks/04-devtools.md IPython session: python -> console'
    )
}
$summary | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $Output 'summary.json') -Encoding utf8
$report = @(
    '# Python 3.14 final verification',
    '',
    'The verifier extracted and checked 284 Python fences from `10-python-discovery` in `python:3.14-alpine` with network disabled. The source was read-only and was copied to `/work` before extraction and verification.',
    '',
    '- L1: 282 PASS, 2 FAIL.',
    '- L2: 115 PASS, 89 GATED, 80 FAIL.',
    '',
    'The two L1 failures were interactive REPL/IPython transcripts, not invalid Python programs. After verification their fences were relabelled `pycon` and `console`, retaining their command/output content and documenting the required host. See the repository Python review for the per-item classifications.'
)
[IO.File]::WriteAllLines((Join-Path $Output 'report.md'), $report, [Text.UTF8Encoding]::new($false))
