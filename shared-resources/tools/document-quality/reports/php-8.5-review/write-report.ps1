param([Parameter(Mandatory = $true)][string]$Output)

$ErrorActionPreference = 'Stop'
$Output = (Resolve-Path -LiteralPath $Output).Path
$index = @(Get-Content -LiteralPath (Join-Path $Output 'index.json') -Raw | ConvertFrom-Json)
$log = Get-Content -LiteralPath (Join-Path $Output 'lint-8.5.log')
$completed = @($log | ForEach-Object {
    if ($_ -match '^(?:No syntax errors detected in|Errors parsing) /blocks/(b\d+\.php)\s*$') {
        $Matches[1]
    }
})
$expected = @($index | ForEach-Object { 'b' + $_.id + '.php' } | Sort-Object)
$actual = @($completed | Sort-Object)
if ($actual.Count -ne $expected.Count -or @(Compare-Object $expected $actual).Count -gt 0) {
    throw 'Lint log is incomplete or does not match index.json; missing checks must not count as PASS.'
}
$errors = Select-String -LiteralPath (Join-Path $Output 'lint-8.5.log') -Pattern 'Errors parsing /blocks/(b\d+\.php)' | ForEach-Object {
    $name = $_.Matches[0].Groups[1].Value; $item = $index | Where-Object { ('b' + $_.id + '.php') -eq $name }
    $diagnostic = $log[$_.LineNumber - 2].Trim()
    $category = if ($item.content -match '<\?php if \(\$ok\):') { '模板语法示意' }
        elseif ($item.content -match '\bpublic (static )?function') { '类成员节选' }
        elseif ($item.content -match "'payment'\s*=>") { '配置数组节选' }
        elseif ($item.content -match '(?m)^\s*(function |new |\$\w+->|[A-Za-z_][A-Za-z_\\]*\(|Reflection|mb_|str_|preg_|explode|implode|ltrim|DateTime|set_error|restore_|error_reporting|clone\(|\(clone|public const|public Type|interface )') { 'API/语法签名参考' }
        else { '待人工分类' }
    $reason = switch ($category) {
        '类成员节选' { '方法属于已有类；独立补 PHP 开标签后没有类体，故 lint 必然失败。' }
        '配置数组节选' { 'services.php 的一个键值项，缺少 return [ ... ]; 外层数组。' }
        '模板语法示意' { '示例中的 ?> 在 PHP 单行注释内仍会结束 PHP 模式；它表达模板文件中的替代语法。' }
        'API/语法签名参考' { '此块列出 API 签名、返回类型或省略号占位，不是可执行定义。' }
        default { '需要进一步审查。' }
    }
    [pscustomobject]@{ item=$item; diagnostic=$diagnostic; category=$category; reason=$reason }
}
$total = $index.Count; $passed = $total - @($errors).Count
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('# PHP 8.5 静态复核'); $lines.Add('')
$lines.Add("范围：最终源文件中的 ``07-php-mastery`` PHP 围栏（$total 项）；这不是全仓库所有 PHP 代码的统计。运行环境：``php:8.5-cli-alpine``，``php -l``，Docker ``--network none``。无开标签者只在临时副本补充开标签。"); $lines.Add('')
$lines.Add("结果：$passed 项可独立通过语法检查；$(@($errors).Count) 项不能独立 lint，均逐项记录，未作自动 PASS 或 hash 豁免。真实修复：``projects/04-production-laravel-app.md`` 的 ``create([...])`` 占位表达式，以及 ``reference/language-concepts/07-namespaces-autoloading.md`` 的重复短类名导入。所有 SHA-256 均由修复后的源文件重新提取。"); $lines.Add('')
$lines.Add('| ID | 路径与行 | 最终源 SHA-256 | lint 副本 SHA-256 | PHP 8.5 诊断 | 类别与理由 |'); $lines.Add('| --- | --- | --- | --- | --- | --- |')
foreach ($entry in $errors) { $i=$entry.item; $lines.Add("| $($i.id) | ``$($i.file):$($i.start)-$($i.end)`` | ``$($i.source_sha256)`` | ``$($i.lint_sha256)`` | $($entry.diagnostic.Replace('|','\\|')) | $($entry.category)：$($entry.reason) |") }
$lines.Add(''); $lines.Add('## 分类统计'); $lines.Add('')
foreach ($g in $errors | Group-Object category | Sort-Object Name) { $lines.Add("- $($g.Name)：$($g.Count) 项") }
$lines.Add(''); $lines.Add('可复现：依次运行 `extract-php-fences.ps1 -Repo <repo> -Output <output>`、`lint-php-8.5.ps1 -Output <output>`、`write-report.ps1 -Output <output>`。')
[IO.File]::WriteAllLines((Join-Path $Output 'PHP-8.5-STATIC-REVIEW.md'), $lines, [Text.UTF8Encoding]::new($false))
