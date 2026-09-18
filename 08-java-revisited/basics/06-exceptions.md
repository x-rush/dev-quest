# 异常处理 - 异常体系与现代设计

## 先理解，再动手

异常把失败沿调用链传播。checked 异常要求声明或捕获；unchecked 不免除处理责任，只改变编译期要求。

**本节自测**：用 try-with-resources 读取文件并模拟处理失败。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

资源仍得到关闭；记录原始 cause，别只保留一条没有来源的错误文本。

</details>

> **文档简介**: 复习异常类层次与受检/非受检的划分逻辑，掌握 try-with-resources 与多异常捕获，建立"异常表达意外、消息说明细节"的现代异常设计观
>
> **目标读者**: 习惯 finally 手动关闭资源、异常使用随意的老 Java 开发者
>
> **前置知识**: 已掌握[控制流程](./05-control-flow.md)基础

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#异常处理` `#try-with-resources` `#错误设计` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：
- 画出异常类层次并说清受检/非受检的设计取舍
- 用 try-with-resources 管理资源生命周期
- 使用多捕获与精确重抛，保留完整原因链
- 遵循现代异常设计原则，避免吞异常等经典错误

## 🌳 异常体系回顾

```
Throwable
├── Error                    # JVM 级严重错误，不应捕获（OutOfMemoryError、StackOverflowError）
└── Exception
    ├── RuntimeException     # 非受检：NPE、IndexOutOfBounds、IllegalArgument、IllegalState...
    └── 其他 Exception       # 受检：IOException、SQLException、TimeoutException...
```

受检/非受检的决策口诀：**调用方能合理恢复 → 受检；编程缺陷或无法恢复 → 非受检（RuntimeException）**。现代 Java 生态（Spring 等）总体偏向"少用受检异常 + 声明式兜底"。

## 🧰 try-with-resources（Java 7+）

**旧写法**：finally 中判空、逐个 close、还要提防 close 抛出的异常掩盖业务异常。

**现代写法**：

```java
try (var reader = Files.newBufferedReader(path);
     var writer = Files.newBufferedWriter(target)) {
    writer.write(reader.readLine());
}   // 自动按声明逆序关闭；close 抛的异常被"抑制"，不会覆盖业务异常
```

- 任何实现 `AutoCloseable` 的对象都能用
- 资源变量可以是 try 外的"事实最终变量"（Java 9+）：

```java
var conn = openConnection();
try (conn) {            // 直接引用已有资源
    conn.query(sql);
}
```

## 🎣 多捕获与精确重抛

```java
try {
    importUsers(input);
} catch (IOException | DateTimeParseException e) {   // 多类型捕获，e 隐式 final
    throw new ImportException("导入失败: " + input, e);   // 包装时必须保留原因链！
}
```

- 包装异常时**永远传入 cause**，否则堆栈断链，线上排查痛苦加倍
- `getCause()` / `getSuppressed()` 是两个常被忽略的排查入口
- 自定义异常建议提供 `(String message)` 与 `(String message, Throwable cause)` 双构造器

## 🏗️ 现代异常设计原则

1. **类型说"出了什么事"，消息说"具体是什么事"**
   `new IllegalArgumentException("age 不能为负: " + age)` 优于裸的 `new IllegalArgumentException("error")`
2. **不用异常做流程控制**——异常构造含堆栈快照，成本高且误导调用方
3. **预期缺失用 Optional，意外失败用异常**

   ```java
   // Optional 表达"可能没有"，让调用方显式决策
   User user = repo.findById(id)
           .orElseThrow(() -> new UserNotFoundException(id));
   ```

4. **自定义业务异常默认继承 RuntimeException**——Spring 声明式事务默认只回滚运行时异常（详见[JPA 核心](../reference/framework-essentials/02-jpa-essentials.md)）
5. **catch 块只做三件事之一**：恢复、记录、重新抛出（可包装）

```java
// ❌ 吞异常：出了问题世界静默
try { loadConfig(); } catch (IOException e) { }

// ✅ 记录或包装，二选一
try { loadConfig(); } catch (IOException e) {
    throw new UncheckedIOException("读取配置失败: " + configPath, e);
}
```

## 🧪 异常与 Stream/Optional 的配合

- Stream 里调到受检异常：抽一个小方法包装为非受检异常，保持管道整洁
- `orElseThrow(Supplier)` 是比 `get()` 更安全的取值方式：

```java
// Stream 场景：找不到即快速失败
Book book = books.stream()
        .filter(b -> b.isbn().equals(isbn))
        .findFirst()
        .orElseThrow(() -> new BookNotFoundException(isbn));
```

## ✅ 最佳实践 / ❌ 陷阱清单

捕获异常后要决定恢复、转换还是传播，并在一个合适边界记录原因。InterruptedException 如果继续向上抛出就不必再原地恢复；若无法传播且终止本次工作，通常恢复中断标记让上层知道取消请求。

使用 try-with-resources 关闭支持该协议的资源，finally 中不要返回新结果覆盖原异常。宽泛捕获可以用于服务边界兜底，但不能吞掉未知错误继续假装成功；底层日志与用户消息分开。

## 🎯 练习与实践

### 练习一：资源管理迁移
1. 写一段 finally-close 的旧代码，迁移为 try-with-resources
2. 在 close 中故意抛异常，观察"抑制异常"行为（`getSuppressed()`）

### 练习二：异常体系设计
1. 为图书管理场景设计 `BookNotFoundException`/`DuplicateIsbnException`
2. 保证两处都有完整原因链与有信息量的消息

### 练习三：Optional 快速失败
1. 用 Stream + `orElseThrow` 重写一段"判空 if + 手动 throw"的旧逻辑

## 🔗 相关文档

- 📄 **[现代 Java 特性](./07-modern-features.md)** - 下一站：Lambda/Stream/Optional 全家桶
- 📄 **[JPA 核心](../reference/framework-essentials/02-jpa-essentials.md)** - @Transactional 回滚与异常的关系
- 📄 **[常见错误排查](../reference/quick-references/02-troubleshooting.md)** - NPE 等运行时异常速查


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
