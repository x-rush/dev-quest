# Go、PHP、Java、Python P1 限定运行验证（第十一轮）

范围：Four named complete fenced programs extracted unchanged from current P1 core/standard-library pages: Go map semantics, PHP DateTimeImmutable, Java java.util.regex, and Python asyncio.

执行约束：Existing local Docker images; network disabled, read-only root filesystem, capabilities dropped, bounded CPU/memory/processes, a read-only extracted source mount, and disposable writable output/tmp mounts only for compiler/runtime artifacts.

结果：4/4 通过。

| 案例 | 原文位置 | 结果 | 可观察输出 |
|---|---|---|---|
| go-map-semantics | `01-go-backend/reference/language-concepts/11-map-semantics.md` | PASS | `no rust`、`alice 25`、`bob 28`、`carol 30`、`1` |
| php-datetime-immutable | `07-php-mastery/reference/language-concepts/10-datetime.md` | PASS | `09:00 ~ 10:00` |
| java-regex | `08-java-revisited/reference/library-guides/08-java-util-regex.md` | PASS | `0`、`2`、`2`、`$$b` |
| python-asyncio | `10-python-discovery/basics/07-advanced-features.md` | PASS | `['A 完成', 'B 完成', 'C 完成']` |

## 未覆盖边界

- Other fences or prose in these pages
- Go map concurrent-access/race behaviour
- PHP timezone/database/framework integration
- Java regex performance or project-specific JDK behaviour
- Python external I/O, type checking, or framework integration
