param(
    [Parameter(Mandatory = $true)][string]$Repo,
    [Parameter(Mandatory = $true)][string]$Output
)

$ErrorActionPreference = 'Stop'
$Repo = (Resolve-Path -LiteralPath $Repo).Path
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$blocks = Join-Path $Output 'blocks'
New-Item -ItemType Directory -Force -Path $blocks | Out-Null
Get-ChildItem -LiteralPath $blocks -File -Filter 'b?????.php' | ForEach-Object {
    Remove-Item -LiteralPath $_.FullName -Force
}

$root = Join-Path $Repo '07-php-mastery'
$pattern = [regex]'(?ms)^```php\s*\r?\n(?<content>.*?)(?:\r?\n)?^```\s*$'
$index = [System.Collections.Generic.List[object]]::new()
$number = 0

Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.md' | Sort-Object FullName | ForEach-Object {
    $file = $_
    $text = [System.IO.File]::ReadAllText($file.FullName)
    foreach ($match in $pattern.Matches($text)) {
        $number++
        $content = $match.Groups['content'].Value
        $before = $text.Substring(0, $match.Index)
        $start = ([regex]::Matches($before, "`n").Count + 2)
        $end = $start + ([regex]::Matches($content, "`n").Count)
        $lintContent = $content
        if ($lintContent -notmatch '(?ms)^(?:#![^\r\n]*\r?\n)?\s*<\?php') { $lintContent = "<?php`n$lintContent" }
        $name = ('b{0:d5}.php' -f $number)
        $target = Join-Path $blocks $name
        [System.IO.File]::WriteAllText($target, $lintContent, [System.Text.UTF8Encoding]::new($false))
        $index.Add([pscustomobject]@{
            id = ('{0:d5}' -f $number); file = $file.FullName.Substring($Repo.Length + 1).Replace('\', '/'); start = $start; end = $end
            source_sha256 = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($content))).ToLowerInvariant()
            lint_sha256 = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant(); content = $content
        })
    }
}
$index | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $Output 'index.json') -Encoding utf8
Write-Output "Extracted $number PHP fences from 07-php-mastery."
