# Go 离线运行验证（2026-09-19）

## 已验证范围

使用 Go `1.27.1` 的离线 Linux 容器，实际构建并运行了 `01-go-backend/reference` 中 18 个可独立执行的标准库示例：13 个主要完整程序、`errors` / `io-bufio` / `slices-maps` 的 3 个第二完整程序、1 组表驱动测试与 fuzz seed，以及 1 组 `net/http` 路由测试。全部通过。

主要完整程序来自 `language-concepts/04-go-data-types.md`，以及 `library-guides/04-encoding-json.md`、`05-context.md`、`06-sync.md`、`07-database-sql.md`、`08-time.md`、`09-errors.md`、`10-io-bufio.md`、`11-os.md`、`13-slices-maps.md`、`14-strconv.md`、`15-log-slog.md`、`16-flag.md`。额外运行了 `09-errors.md`、`10-io-bufio.md`、`13-slices-maps.md` 的第二完整程序；还运行了 `12-testing.md` 的测试和 `03-net-http.md` 的路由断言（含 GET、HEAD、POST 405 与 404，以及响应 JSON 解码）。

容器执行时关闭网络、将仓库以只读方式挂载，并限制 CPU、内存和进程数。运行的完整结果（含每个源块的 SHA-256）保存在验证工作目录的 `go-reference-examples.json`；此报告只保留可审阅的范围和复现命令。

本次补正了验证器本身的三个陈旧断言：`errors`、`io-bufio` 与 `slices-maps` 的条目各有两个完整 `package main` 示例，旧验证器只运行第一个却断言第二个的输出。现在两个示例都会实际运行，不再把另一段内容静默漏检。

## 未纳入“已运行”结论的内容

- Gin、GORM、gqlgen、Redis、MongoDB、gRPC 及微服务示例：需要模块依赖、生成代码或外部服务，不能在无网络标准库容器中诚实验证。
- 速查签名、故意错误对照、HTTP/GraphQL 协议文本和多文件片段：它们不是独立 `.go` 程序；不应靠拼接成虚构程序来取得“通过”。
- race 检测、长时间 fuzz、真实数据库、部署与全篇多文件项目构建：本次未运行。

WSL 已安装，但 `wsl -d Ubuntu --exec /bin/sh ...` 在 10 秒内未返回，因此没有使用或重置其中的 asdf 环境；改用仓库已有的离线 Go 1.27.1 容器。该限制不影响本报告中的实际运行结果。

## 复现

在仓库根目录执行下列命令。该命令不访问网络；`/work` 必须是可执行的临时目录，因为 `go run` 会在其中执行刚构建的测试程序。

```powershell
$repo = (Get-Location).Path
$out = Join-Path (Split-Path $repo -Parent) 'verification-lab/go-current'
New-Item -ItemType Directory -Force -Path $out | Out-Null
docker run --rm --network none --read-only `
  --tmpfs /tmp:rw,noexec,nosuid,size=128m `
  --tmpfs /work:rw,exec,nosuid,size=768m `
  --cap-drop ALL --pids-limit 256 --memory 1g --cpus 2 `
  -e GOCACHE=/work/go-cache -e HOME=/work -e TMPDIR=/work `
  -v "${repo}:/repo:ro" -v "${out}:/out:rw" -w /repo `
  dev-quest-validation:local `
  python3 shared-resources/tools/document-quality/verify_go_reference_examples.py `
    --go /usr/local/go/bin/go --report /out/go-reference-examples.json
```

预期末行是 `18 passed; 0 blocked`。如果文档中被验证的代码围栏变更，SHA-256 与输出断言会随之重新计算；不得复用旧报告代替重新运行。
