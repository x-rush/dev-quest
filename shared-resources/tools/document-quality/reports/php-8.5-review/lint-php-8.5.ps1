param(
    [Parameter(Mandatory = $true)][string]$Output,
    [string]$Docker = 'docker'
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$Output = (Resolve-Path -LiteralPath $Output).Path
$blocks = Join-Path $Output 'blocks'
& $Docker run --rm --network none --mount "type=bind,src=$blocks,dst=/blocks,readonly" php:8.5-cli-alpine sh -lc 'for f in /blocks/*.php; do php -l "$f" 2>&1 || true; done' |
    Set-Content -LiteralPath (Join-Path $Output 'lint-8.5.log') -Encoding utf8
if ($LASTEXITCODE -ne 0) {
    throw "Docker did not complete the lint scan (exit $LASTEXITCODE). Inspect lint-8.5.log."
}
Write-Output 'Wrote lint-8.5.log using php:8.5-cli-alpine with network disabled.'
