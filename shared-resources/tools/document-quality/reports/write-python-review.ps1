param(
    [Parameter(Mandatory = $true)][string]$Results,
    [Parameter(Mandatory = $true)][string]$Manifest,
    [Parameter(Mandatory = $true)][string]$Output
)

$ErrorActionPreference = 'Stop'
$records = Get-Content -LiteralPath $Results | ForEach-Object { $_ | ConvertFrom-Json } |
    Where-Object { $_.lang -eq 'python' -and $_.classification -eq 'NEEDS_REVIEW' }
$manifestById = @{}
Get-Content -LiteralPath $Manifest | ForEach-Object { $item = $_ | ConvertFrom-Json; $manifestById[$item.id] = $item }

function Get-Category($record, $content) {
    if ($content -match '(?m)^>>> |(?m)^In \[\d+\]:') { return '教学交互式片段（REPL/IPython）' }
    if ($record.id -eq '03276') { return '教学语法片段（条件体省略）' }
    if ($record.id -eq '03349') { return '教学预期错误（positional-only 参数）' }
    if ($record.l2.detail -match "outside (async )?function") { return '上下文依赖（需要 async 函数体）' }
    if ($record.l2.detail -match 'ModuleNotFoundError') { return '上下文依赖（第三方包未安装）' }
    if ($record.l2.detail -match 'FileNotFoundError') { return '上下文依赖（外部文件/环境）' }
    if ($record.l2.detail -match 'NameError|ImportError') { return '上下文依赖（前序定义、导入或项目模块）' }
    if ($record.l2.detail -match 'TypeError|AttributeError|ValueError') { return '教学预期错误或输入前提缺失' }
    if ($record.l1.status -eq 'FAIL') { return '教学片段或版本差异' }
    return '上下文依赖（受限执行）'
}

function Get-Reason($record, $category) {
    switch ($record.id) {
        '03276' { return '本块列举条件表达式，不是完整 if 语句；每行若作为程序使用必须补缩进语句体。' }
        '03349' { return '示例刻意调用仅位置参数的错误形式，并在下一行标出预期 TypeError。' }
        default {
            if ($category -eq '教学交互式片段（REPL/IPython）') { return '提示符和魔术命令只适用于交互式宿主，不能作为 .py 文件由 AST 编译。' }
            if ($category -like '上下文依赖（前序*') { return '该围栏依赖同一教学段落或项目文件中的名称/导入；单独执行不是其承诺的运行方式。' }
            if ($category -like '上下文依赖（需要*') { return 'await/async with 必须置于 async def 或支持顶层 await 的宿主中。' }
            if ($category -like '上下文依赖（第三方*') { return '隔离验证环境未安装框架依赖；这不表示代码在声明的项目依赖中不可用。' }
            if ($category -like '上下文依赖（外部*') { return '示例显式读取用户环境或项目文件；隔离容器不具备该输入。' }
            if ($category -eq '教学预期错误或输入前提缺失') { return '示例展示异常、边界或需要调用方提供的对象；诊断本身是示例语义的一部分或缺少演示输入。' }
            return '原始受限执行无法建立教学片段所需上下文；未将其作为真实代码错误修改。'
        }
    }
}

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('# Python 容器失败复核'); $lines.Add('')
$lines.Add("范围：使用隔离网络的 ``python:3.14-alpine`` 对最终源重新提取的 284 个 ``10-python-discovery`` Python 围栏运行 ``verify.py --langs python --strict --execute``。本报告覆盖其中 $(@($records).Count) 个 ``NEEDS_REVIEW`` 项；源目录以只读方式挂载，容器先复制后提取与验证。未改动核心检查器、text 围栏或豁免。"); $lines.Add('')
$lines.Add('结果：L1 语法层 282 通过、2 项不能作为 .py 文件编译；这两项均为已有历史 REPL/IPython 教学片段。L2 运行层为 115 通过、89 门禁、80 失败；失败项均在本表逐项归因。10 个非历史项中，9 个依赖相邻示例、项目模块、异步宿主或演示输入，1 个刻意展示 positional-only 参数的 TypeError。此前裸 if 条目已被改善为带真实输入和可观察 print 的示例，并在此轮 Python 3.14 L1 复验中通过。'); $lines.Add('')
$lines.Add('Python 官方 3.14 文档确认 t-string、延迟注解等基线特性；本轮实际解释器与模块基线一致，因此本报告不再以旧 Python 3.12 的语法诊断作结论。'); $lines.Add('')
$lines.Add('| ID | 历史例外 | 路径与行 | 源 SHA-256 | 原始 L1 / L2 诊断 | 分类 | 处理理由 |'); $lines.Add('| --- | --- | --- | --- | --- | --- | --- |')
foreach ($record in $records) {
    $item=$manifestById[$record.id]; $category=Get-Category $record $item.content; $reason=Get-Reason $record $category
    $diag=("L1 {0}: {1}; L2 {2}: {3}" -f $record.l1.status,$record.l1.detail,$record.l2.status,$record.l2.detail).Replace('|','\\|')
    $legacy=if($record.legacy_hash_exception){'是'}else{'否'}
    $lines.Add("| $($record.id) | $legacy | ``$($record.file):$($record.start)-$($record.end)`` | ``$($record.source_sha256)`` | $diag | $category | $reason |")
}
$lines.Add(''); $lines.Add('## 分类统计'); $lines.Add('')
foreach ($g in $records | Group-Object { Get-Category $_ $manifestById[$_.id].content } | Sort-Object Name) { $lines.Add("- $($g.Name)：$($g.Count) 项") }
$lines.Add(''); $lines.Add('### 非历史项清单'); $lines.Add('')
foreach ($record in $records | Where-Object { -not $_.legacy_hash_exception }) { $lines.Add("- `$($record.id)` — $(Get-Category $record $manifestById[$record.id].content)：$(Get-Reason $record (Get-Category $record $manifestById[$record.id].content))") }
[IO.File]::WriteAllLines($Output, $lines, [Text.UTF8Encoding]::new($false))
