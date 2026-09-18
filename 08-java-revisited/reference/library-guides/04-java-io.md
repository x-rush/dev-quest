# java.io 导览

> **文档简介**: 经典流式 IO——字节流/字符流两大家族、缓冲与编码转换、File 与 java.nio.Files 的分工、Serializable 序列化与 serialVersionUID、try-with-resources
>
> **目标读者**: 需要理清 java.io 家族谱系与新旧 IO 分工的开发者
>
> **前置知识**: 现代文件操作（Path/Files）见 [标准库核心速查](./01-standard-library.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#java.io` `#IO流` `#序列化` `#标准库` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

`java.io` 是流式 IO 的经典 API：**字节流**（`InputStream`/`OutputStream`，任意二进制）与**字符流**（`Reader`/`Writer`，文本 + 字符集）两大家族，装饰器模式层层叠加。现代文件系统操作的首选是 `java.nio.file`，java.io 的流仍是两者的管道底座。

> 示例给出预期行为与规范依据。本轮环境未提供 Java 编译器，未复现历史运行记录；请在项目约定 JDK 上编译验证。

## 📖 语法 / 签名

### 家族谱系

| 抽象基类 | 常用实现 | 用途 |
|----------|---------|------|
| `InputStream` | `FileInputStream`、`ByteArrayInputStream`、`BufferedInputStream`、`ObjectInputStream` | 读字节 |
| `OutputStream` | `FileOutputStream`、`ByteArrayOutputStream`、`BufferedOutputStream`、`ObjectOutputStream` | 写字节 |
| `Reader` | `InputStreamReader`（转换流）、`FileReader`、`BufferedReader` | 读字符 |
| `Writer` | `OutputStreamWriter`（转换流）、`FileWriter`、`BufferedWriter`、`PrintWriter` | 写字符 |

### 缓冲与转换（读文本的标准姿势）

```java
// 字节 → 字符 的桥梁是转换流；BufferedReader 提供 readLine()
try (var reader = new BufferedReader(
        new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {
    String line;
    while ((line = reader.readLine()) != null) {   // 末尾返回 null
        process(line);
    }
}
```

### File 与 java.nio.Files 分工

| 场景 | 用谁 |
|------|------|
| 元数据查询（`exists`/`isFile`/`length`，预期可用） | `File` 或 `Files` 均可 |
| 读写字符串、按行流、遍历树、复制移动 | **`Files`**（见 [标准库核心](./01-standard-library.md)） |
| 老 API 边界 | `file.toPath()` / `Path.toFile()` 互转 |

### 序列化 Serializable

```java
class Book implements Serializable {
    private static final long serialVersionUID = 1L;   // 显式声明版本号
    String title;
    transient String cache;                            // 不参与序列化（预期：读回为 null）
}
```

- `ObjectOutputStream.writeObject` / `ObjectInputStream.readObject` 完成往返。
- **serialVersionUID 失配预期**：以 `svuid=1` 写出、改类为 `svuid=2` 后读入 →
  `java.io.InvalidClassException: Book; local class incompatible: stream classdesc serialVersionUID = 1, local class serialVersionUID = 2`
- 不写该字段时 JVM 按类结构自动计算——结构变更可能改变自动计算的 UID；并非每一种变更都会改变它，固定 UID 也不保证任意结构变化都兼容。

### try-with-resources

```java
try (Res r1 = ...; Res r2 = ...) {       // 按 r2 → r1 的逆序关闭（预期）
    work(r1, r2);                        // body 异常为主异常
}                                        // close() 的异常进入 getSuppressed()（预期）
```

完整语义见 [异常体系与资源管理](../language-concepts/06-exceptions-resources.md)。

## 💡 示例

```java
import java.io.*;
import java.nio.charset.StandardCharsets;

public class IoDemo {
    public static void main(String[] args) throws Exception {
        // 字节流往返
        var out = new ByteArrayOutputStream();
        out.write("hello".getBytes(StandardCharsets.UTF_8));
        try (var in = new ByteArrayInputStream(out.toByteArray())) {
            System.out.println((char) in.read());          // h
        }

        // 字符流 + 转换 + 缓冲（UTF-8 显式指定）
        var f = java.nio.file.Files.createTempFile("io-demo-", ".txt").toFile();
        f.deleteOnExit(); // 教学临时文件；服务程序应在明确的生命周期及时清理
        try (var w = new BufferedWriter(new OutputStreamWriter(
                new FileOutputStream(f), StandardCharsets.UTF_8))) {
            w.write("第一行\n第二行");
        }
        try (var r = new BufferedReader(new InputStreamReader(
                new FileInputStream(f), StandardCharsets.UTF_8))) {
            System.out.println(r.readLine());              // 第一行
            System.out.println(r.readLine());              // 第二行
            System.out.println(r.readLine());              // null
        }
    }
}
```

## ⚠️ 常见陷阱

- ❌ **不指定字符集创建 Reader/Writer**：`new FileReader(f)` 跟随平台默认字符集（JEP 400 后默认 UTF-8，但历史 JVM 与外部环境仍可能不一致）。
  ✅ 显式传 `StandardCharsets.UTF_8`，或走 `Files.readString/newBufferedReader`（默认 UTF-8）。
- ❌ **手写 finally 关流**：冗长且容易漏。
  ✅ try-with-resources；注意 close 顺序是声明逆序、存在先前主异常时，后续 close 异常才作为 suppressed 保留。
- ❌ **序列化类不声明 `serialVersionUID`**：某些结构变化会使旧流因 UID 不匹配而无法读入（预期 InvalidClassException）。
  ✅ 显式声明并在兼容演进时手动维护；新项目数据交换优先 JSON/Protobuf。
- ❌ **反序列化来路不明的数据**：Java 序列化是已知攻击面。
  ✅ 只处理可信数据；对外接口用 JSON 等无代码执行语义的格式。
- ❌ **拿 `read()` 的 int 当字节用没判 -1**：`-1` 是流结束信号而非数据。
  ✅ 循环条件 `while ((b = in.read()) != -1)` 或用 `readAllBytes`/`readLine`。

<!-- full-library-explanation -->
## 先区分字节、字符与资源所有权

InputStream.read 返回 int，是为了同时容纳 0–255 的字节值和 -1 这个结束标记；读取到一个字节不代表读到一个中文字符。Reader 负责按字符集解码，BufferedReader 再提供按行读取。readLine 去掉行分隔符，因此读出后简单拼接不能保持原始文件的换行格式。

读取数组时，返回值 n 才是本轮有效长度。不能每次都写出整个缓冲区，否则最后一块可能夹带上一轮的数据。readAllBytes 简单，但必须有可接受的输入大小上限；压缩文件还要限制解压后大小。包装流通常关闭其底层流，方法若接收调用方传来的流，应明确由谁关闭，避免顺手关闭 System.in 或共享连接。

**练习**：用包含中文、空行和末尾无换行的临时文件，分别做字节复制和按行重新写入；比较字节是否完全相同。再让输出流在第二次写入时失败，确认异常可见且资源被关闭。序列化的 serialVersionUID 是兼容检查的一部分，不会自动迁移字段、验证业务约束或使不可信对象流安全。

## 🔗 相关条目

- 📄 **[标准库核心速查](./01-standard-library.md)** — Files/Path 现代文件 API 主战场
- 📄 **[异常体系与资源管理](../language-concepts/06-exceptions-resources.md)** — try-with-resources 完整语义
- 📄 **[java.lang 导览](./03-java-lang.md)** — 装饰器模式涉及的 Object 契约
- 🌐 **[java.io (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/package-summary.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
