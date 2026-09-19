# 异常体系与资源管理

> **文档简介**: Java 异常类型的条目式速查：受检/非受检的取舍准则、try-with-resources 资源管理语义、异常包装与因果链、快速失败工具
>
> **目标读者**: 需要系统性梳理异常处理习惯的开发者；入门教程见 [异常处理](../../basics/06-exceptions.md)
>
> **前置知识**: [类与 Record](../../basics/04-classes-records.md)、[Java 关键字详解](./01-java-keywords.md) 中 `throw`/`throws`/`finally` 条目

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#异常` `#try-with-resources` `#快速失败` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

| 层级 | 类型 | 是否受检 | 典型代表 | 处理准则 |
|------|------|---------|---------|---------|
| `Throwable` | Error | 否 | `OutOfMemoryError`、`StackOverflowError` | 通常不由普通业务逻辑捕获恢复；也包含链接等严重问题 |
| `Exception` | 受检异常 | 是 | `IOException`、`SQLException` | 编译器强制 catch/throws；调用方"可合理恢复"时使用 |
| `Exception` | 非受检 | 否 | `RuntimeException` 及子类：`NullPointerException`、`IllegalStateException`、`IllegalArgumentException` | 编程错误/状态非法；现代 Java（含 Spring 生态）的默认选择 |

- **资源管理**：资源实现 `AutoCloseable`，用 try-with-resources 管理；关闭异常不会吞掉主体异常，而是**追加到 `getSuppressed()`**。
- **快速失败**：入口处校验参数，尽早抛 `IllegalArgumentException`/`IllegalStateException`，避免坏状态扩散到深层。

## 📖 语法 / 签名

```java
// 自定义非受检异常：携带业务键，不暴露实现细节
public class BookNotFoundException extends RuntimeException {
    public BookNotFoundException(String isbn) {
        super("图书不存在: " + isbn);
    }
}

// multi-catch：同一处理逻辑的多种异常合并（catch 变量隐式 final）
try {
    load(isbn);
} catch (IOException | TimeoutException e) {
    throw new BookLoadException(isbn, e);      // 包装时必须传 cause
}

// try-with-resources：多资源按声明逆序自动关闭
try (var reader = Files.newBufferedReader(path);
     var writer = Files.newBufferedWriter(target)) {
    // ...
}
```

| 方法 | 用途 |
|------|------|
| `e.getMessage()` | 异常消息 |
| `e.getCause()` | 因果链上游（包装时传入的原始异常）|
| `e.getSuppressed()` | try-with-resources 中被主体异常"压制"的关闭异常 |
| `e.addSuppressed(other)` | 手动追加压制异常 |
| `Objects.requireNonNull(x, "msg")` | 参数判空快速失败，返回原值可直接赋值 |

## 💡 示例

```java
// 业务层：包装底层异常，保留因果链
public Book borrow(String isbn) {
    try {
        return externalCatalogClient.fetch(isbn);
    } catch (IOException e) {
        throw new CatalogUnavailableException(isbn, e);   // e 作为 cause 传入
    }
}

// 快速失败 + 规整（record 紧凑构造器）
public record Loan(String isbn, LocalDate dueDate) {
    public Loan {
        Objects.requireNonNull(isbn, "isbn 不能为空");
        Objects.requireNonNull(dueDate, "dueDate 不能为空");
    }
}
```

## ⚠️ 常见陷阱

- **吞异常**：`catch (Exception e) {}` 或只打日志不处理——调用方无从感知失败
- **包装丢因**：`new XException(e.getMessage())` 丢失堆栈与 cause，排查断链
- **finally 里 return**：覆盖 try/catch 的返回值与异常，静默吞掉异常
- **捕获 `Throwable`/`Error`**：连 `OutOfMemoryError` 都吞掉，掩盖 JVM 故障
- **受检异常层层 throws**：接口被 `throws Exception` 污染——避免宽泛 throws Exception，按调用方恢复责任选择具体异常并保留 cause
- **异常当流程控制**：用异常驱动正常分支，性能差且可读性崩坏
- **异常类型与事务回滚**：Spring 声明式事务的常见默认规则对 `RuntimeException`/`Error` 回滚；这不是 Java 语言规则，配置、调用是否经过代理和异常是否被吞掉都会影响实际行为（见[事务速查](../framework-essentials/05-transaction-essentials.md)）

<!-- full-library-explanation -->
## 主体失败和关闭失败是两条信息

try-with-resources 按资源声明的逆序关闭。若主体先失败，关闭时又失败，主体异常继续向外传播，关闭异常附加到 suppressed 列表；若主体正常而关闭失败，关闭异常本身成为传播的异常。第二个资源初始化失败时，第一个已经成功创建的资源仍会关闭。

完整实验保存为 `Main.java`，使用 JDK 21 运行 `javac --release 21 Main.java`、`java Main`：

<!-- reference-case: {"id":"java-resource-body-and-close","stdout":"body\nclose\n"} -->
```java
public class Main {
    static class Resource implements AutoCloseable {
        public void close() { throw new IllegalStateException("close"); }
    }
    public static void main(String[] args) {
        try (var resource = new Resource()) {
            throw new IllegalArgumentException("body");
        } catch (Exception e) {
            System.out.println(e.getMessage());
            System.out.println(e.getSuppressed()[0].getMessage());
        }
    }
}
```

预期依次输出 body、close。删掉主体的 throw 再观察：这次没有 suppressed 元素，直接访问下标会出错，应先查看数组长度。练习的目标是保留两个失败的因果信息，而不是把所有异常改成同一种类型。受检与非受检是接口契约的选择；无法恢复时向有上下文的边界传播，能恢复时才在当地处理。

再独立运行第二个 `Main.java`，观察“后创建先关闭”和“创建第二个资源失败”的路径。构造器抛异常的资源没有成功进入 try-with-resources 管理，构造器自己取得但尚未交付的资源必须自己清理。

<!-- reference-case: {"id":"java-resource-initialization-order","stdout":"close:b\nclose:a\nprimary:close:b\nsuppressed:close:a\nclose:a\nprimary:init:b\nsuppressed:close:a\n"} -->
```java
public class Main {
    static final class Resource implements AutoCloseable {
        private final String name;
        Resource(String name, boolean fail) {
            this.name = name;
            if (fail) throw new IllegalArgumentException("init:" + name);
        }
        @Override public void close() {
            System.out.println("close:" + name);
            throw new IllegalStateException("close:" + name);
        }
    }
    static void show(Exception error) {
        System.out.println("primary:" + error.getMessage());
        for (Throwable suppressed : error.getSuppressed()) {
            System.out.println("suppressed:" + suppressed.getMessage());
        }
    }
    public static void main(String[] args) {
        try (var a = new Resource("a", false); var b = new Resource("b", false)) {
            // 主体正常结束，b 的关闭异常成为主异常，a 的关闭异常被附加。
        } catch (Exception error) {
            show(error);
        }
        try (var a = new Resource("a", false); var b = new Resource("b", true)) {
            throw new AssertionError("b 初始化失败，不能进入主体");
        } catch (Exception error) {
            show(error);
        }
    }
}
```

预期第一段先关闭 b 再关闭 a，主异常是 `close:b`；第二段只关闭 a，主异常是 `init:b`。两段都把 `close:a` 保留在 suppressed 中。这里没有真实文件和数据库，验证范围仅是 Java 资源关闭与异常传播契约，见 [两个完整程序的运行证据](../../../shared-resources/tools/document-quality/reports/php-java-core-boundaries.md)。

实际读取文件时可按调用者责任划分：缺失的可选配置允许使用默认值；配置格式损坏应拒绝启动；保存失败必须返回失败，不能日志记录后仍返回成功。包装成业务异常时传入原异常作为 cause，日志只在负责诊断的边界记录一次，避免每一层重复输出同一条堆栈。

## 🔗 相关条目

- [JLS 21：try-with-resources 的初始化、关闭与异常传播](https://docs.oracle.com/javase/specs/jls/se21/html/jls-14.html#jls-14.20.3)
- 📄 **[Java 关键字详解](./01-java-keywords.md)** — `throw`/`throws`/`try`/`finally` 条目
- 📄 **[异常处理教程](../../basics/06-exceptions.md)** - 入门版讲解
- 📄 **[事务传播与隔离速查](../framework-essentials/05-transaction-essentials.md)** — 异常类型决定回滚
- 📄 **[故障排除速查](../quick-references/02-troubleshooting.md)** - 常见异常对照表
- 📄 **[标准库核心](../library-guides/01-standard-library.md)** — 相关工具类


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
