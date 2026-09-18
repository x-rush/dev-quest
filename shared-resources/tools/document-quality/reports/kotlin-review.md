# Kotlin 编译扫描与定点修补

使用 Kotlin 2.4.20、JDK 21 的隔离容器扫描全部 304 个 Kotlin 围栏。首轮 44 项通过，260 项失败；逐块包装编译无法提供 Android/Compose 工程上下文，失败不能直接认定为语言错误。

复核新增诊断及历史语法诊断后，已实际修复并定点编译通过 4 个围栏：

- 关键字示例把非法省略号分支改为实际输出，并修正 `"text"` 长度应为 4 的错误断言。
- 基础速查改为具有明确数据和 main 入口的例子，消除重复 name 声明与缺失示例输入。
- 自定义委托与 observable/vetoable 示例补齐真实标准库导入。

| 文件 | 当前块 SHA-256 | 定点编译 |
|---|---|---|
| `05-kotlin-compose/reference/language-concepts/01-kotlin-keywords.md:376` | `db9537c132ba8f10ea9e5cdf8c5374ace0d23ffd2b1add1ea06ff47bdc8804d9` | PASS |
| `05-kotlin-compose/reference/language-concepts/05-generics-delegates.md:131` | `1f50819dcde2b0de6acc8afd073806ec57bbd4311c375dbe2b19302760cb0d81` | PASS |
| `05-kotlin-compose/reference/language-concepts/05-generics-delegates.md:171` | `6ebd56168a50518b384fa4a69a50a61011006157e35692b1aa25af584891f4f4` | PASS |
| `05-kotlin-compose/reference/quick-references/01-kotlin-compose-cheatsheet.md:19` | `0472f00dd106f0721cd6c659b230bfd8f9145e4fdcff32b1873e24a6b5c11168` | PASS |

合并原有不变内容的证据后，当前为 **48 项编译通过，256 项保留编译诊断**。剩余范围含局部语法参考和依赖 AndroidX、Compose、Navigation、Room、Retrofit、Ktor、Hilt、Gradle/KSP 的片段；本轮没有安装完整 Android SDK/Gradle 工程，也没有把缺少依赖判为通过。语法或上下文疑点仍可从完整诊断追溯，不以历史豁免作为正确性证明。

参见[最终验证报告](./verification-2026-09-18/README.md)；首轮为 `container-final`，定点复验为 `kotlin-recheck`。没有重新执行全部 304 项来重复消耗编译时间。
