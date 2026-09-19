# PHP 与 Java 核心边界运行验证

本报告绑定三篇正文中的 8 个标记完整程序。运行器原样抽取代码，不补 import、不生成应用类、不把局部片段拼装为程序；退出码必须为 0，标准错误必须为空，标准输出必须与标记逐字一致。

| 正文 | 案例 | 结果 |
|---|---|---:|
| [PHP 枚举、属性与 Fiber](../../../../07-php-mastery/basics/07-advanced-features.md) | 提升属性 target、Fiber 返回通道与生命周期 | 3 / 3 |
| [Java 集合与泛型](../../../../08-java-revisited/reference/language-concepts/02-collections-generics.md) | 视图与浅快照、Map 的 null 契约、PECS 复制 | 3 / 3 |
| [Java 异常与资源](../../../../08-java-revisited/reference/language-concepts/06-exceptions-resources.md) | 主体/关闭失败、初始化失败/逆序关闭 | 2 / 2 |

本次环境是 PHP 8.3.6、OpenJDK Temurin 21.0.12；Java 使用 `--release 21` 编译。结果 **8 / 8 通过**，机器记录见 [版本、命令、源码哈希与实际输出](php-java-core-boundaries.json)。哈希覆盖报告生成时的文档字节及抽取程序；文件换行变更后应复跑生成报告。

## 复现方法

在具备 Python 3、PHP CLI 与 JDK 21 的环境，从仓库根目录执行：

```bash
python3 shared-resources/tools/document-quality/verify_php_java_core_boundaries.py --report /tmp/php-java-core-boundaries.json
```

运行器复用 [基础验证器](../verify_php_java_foundations.py) 的数量守卫、临时目录和严格输出比较；预期案例数量固定为 3、3、2。`--language php` 或 `--language java` 只运行对应子集，不能把子集通过报告解释为全部通过。

本次使用现有本地 `dev-quest-validation:local` 镜像，源码只读挂载，容器无网络、根文件系统只读、移除 capabilities，临时编译目录位于 256 MiB tmpfs，并限制 512 MiB 内存、2 CPU 和 128 进程。镜像并非公共交付依赖，使用上述语言工具链即可复现。

## 范围边界

这些案例验证有限的语言行为，包含主动失败后的处理输出；并不覆盖三篇文档的所有片段。PHP 属性钩子、管道与 URI 段落需要对应 PHP 8.4/8.5 环境，未计入这 3 个 PHP 8.3 基线案例。Fiber 案例不证明任何异步 I/O 框架可用；Java 的纯语言资源案例不证明 Spring 事务配置、文件系统故障或数据库行为。

本轮正文修复包括：PHP `match` 未覆盖分支在运行时抛异常而非语言编译期穷尽检查、提升参数按声明 target 选择反射入口、一等 callable 不提供部分实参绑定；Java 集合只读结构与可变元素的区分、`getOrDefault` 与 `putIfAbsent` 的 null 行为、PECS 不等于只读视图，以及资源初始化失败后的关闭语义。官方契约链接分别保留在源文档中。
