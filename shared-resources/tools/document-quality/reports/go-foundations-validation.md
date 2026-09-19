# Go 关键词与内置函数验证（2026-09-19）

本记录覆盖两篇有限基础集合参考：[25 个关键字与预声明标识符](../../../../01-go-backend/reference/language-concepts/01-go-keywords.md)与[18 个内置函数](../../../../01-go-backend/reference/language-concepts/02-go-built-in-functions.md)。集合来源为 [Go 1.27 语言规范](https://go.dev/ref/spec)：25 个关键字、44 个预声明标识符，以及其中 18 个预声明内置函数。类型转换和 `unsafe` 的特殊操作不计入 18 个内置函数；它们在正文中另行说明。

## 已验证范围

在 Go 1.27.1 的 Linux 容器中，验证脚本从当前两篇文档直接提取所有 `go` 围栏。它不为片段生成补充定义、不注入导入，也不执行未标记为示例的代码。每个完整示例写入独立临时模块并逐字比较标准输出和标准错误；每个编译反例必须以正文注明的原因失败。容器关闭网络、以只读方式挂载源代码，并限制 CPU、内存与进程数。

结果：**20/20 通过**，包括 18 个完整程序和 2 个编译反例。每条结果在运行时记录源内容 SHA-256、生成的 `main.go` / `go.mod`、构建命令、运行命令、实际输出和退出码；原始 JSON 是本次隔离运行产物，不把旧哈希当作当前证明。

验证覆盖 package/import、声明和类型、分支、循环/range、defer/return、goroutine/channel/select、map/goto、预声明标识符、append/copy、clear/delete、len/cap、make/new、close、复数、min/max、panic/recover、print/println。它还验证了两个故意错误：错误的 `goto` 作用域，以及把切片用 `...` 展开传给 `min`。

## 未由本记录证明的内容

- 两篇之外的 Go 文章、框架、数据库、网络服务、并发竞争与性能表现；
- 编译器所有实现的 `print` / `println` 文本格式。正文只将它们作为实现相关的调试能力说明，不以输出格式建立跨实现契约；
- 升级到未来 Go 语言版本后的 API 和语义。

## 复现

在仓库根目录执行以下命令；`/out` 应指向可写的临时目录。脚本会在该目录生成本轮 JSON 证据。

```powershell
$repo = (Get-Location).Path
$out = Join-Path (Split-Path $repo -Parent) 'verification-lab/go-foundations'
New-Item -ItemType Directory -Force -Path $out | Out-Null
docker run --rm --network none --read-only `
  --tmpfs /tmp:rw,noexec,nosuid,size=128m `
  --tmpfs /work:rw,exec,nosuid,size=768m `
  --cap-drop ALL --pids-limit 256 --memory 1g --cpus 2 `
  -e GOCACHE=/work/go-cache -e HOME=/work -e TMPDIR=/work `
  -v "${repo}:/source:ro" -v "${out}:/out:rw" -w /source `
  dev-quest-validation:local `
  python3 shared-resources/tools/document-quality/verify_go_foundations.py `
    --go /usr/local/go/bin/go --report /out/results.json
```

预期最后一行是 `20/20 passed`。正文、工具链或预期输出改变后必须重新运行；只更新报告日期不构成验证。
