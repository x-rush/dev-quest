# 接口语义

> **文档简介**: 接口的现代语义——default/static/private 方法的版本演进、函数式接口判定（SAM 与 @FunctionalInterface）、多重实现 default 冲突的消解规则，以及接口 vs 抽象类的决策
>
> **目标读者**: 需要准确掌握接口方法规则与冲突消解语义的开发者
>
> **前置知识**: 教程式讲解见 [类、接口与 Record](../../basics/04-classes-records.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#接口` `#default方法` `#函数式接口` `#语言概念` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

接口是纯契约：Java 8 起可以携带**带实现的方法**（`default`/`static`），Java 9 起进一步允许 `private` 方法复用实现。当多个来源提供同一签名的 default 方法时，编译器按**类胜出**规则消解冲突，无规则可用时强制你重写。

> 示例给出预期行为与规范依据。本轮环境未提供 Java 编译器，未复现历史运行记录；请在项目约定 JDK 上编译验证。

## 📖 语法 / 签名

### 接口成员演进

| 版本 | 新增成员 | 语义 |
|------|---------|------|
| Java 1-7 | 抽象方法、常量（`public static final`） | 纯契约 |
| Java 8 | `default` 方法、`static` 方法 | 接口携带实现；静态方法**只属于接口本身** |
| Java 9+ | `private` / `private static` 方法 | 供 default/static 方法内部复用，对外不可见 |
| Java 17+（正式特性） | 配合 sealed 限定实现者 | 见 [Record / Sealed / 模式匹配](./05-records-sealed-patterns.md) |

```java
interface Greeter {
    String name();                                        // 抽象：实现方必须给

    default String greet() { return "hi, " + name(); }    // default：有默认实现

    default String tagged() { return tag() + greet(); }   // 复用 private 方法

    private String tag() { return "["; }                  // Java 9+，接口内部工具

    static Greeter of(String n) { return () -> n; }       // 接口静态工厂（Java 8+）
}
// Greeter.of("java").greet() == "hi, java"（预期）
```

### 多重实现 default 冲突消解（三条规则）

1. **类胜出**：父类（或祖父类……）的具体方法优先于任何接口 default 方法。
2. **接口间冲突必须重写**：两个不相关接口提供同名 default → 实现类**必须**重写，否则编译失败。
3. **重写时可显式分派**：`接口名.super.方法名()` 指定采用哪个接口的实现（限定形式用于合适的直接父接口；父类方法通常用 super.method()）。

```java
interface A { default String hi() { return "A"; } }
interface B { default String hi() { return "B"; } }

class C implements A, B {
    @Override public String hi() { return A.super.hi() + B.super.hi(); }  // "AB"（预期）
}
```

### 函数式接口判定（SAM）

- **SAM = Single Abstract Method**：恰好一个抽象方法（`default`/`static`/`private` 不计入；与 `Object` 公有方法同签名的 `toString/equals` 等也不计入）。
- 非 sealed 接口满足函数式接口约束后可用 lambda / 方法引用实现，`@FunctionalInterface` 不是前提，只是让编译器替你把关。

## 💡 示例

```java
@FunctionalInterface
interface F { int len(String s); }

public class InterfaceDemo {
    static class Sup { public String m() { return "super"; } }
    interface Def { default String m() { return "iface"; } }
    static class Wins extends Sup implements Def {}     // 不重写，合法

    public static void main(String[] args) {
        // 规则 1：类胜出（预期）
        System.out.println(new Wins().m());             // super

        // SAM 直接接方法引用（预期）
        F f = String::length;
        System.out.println(f.len("abcd"));              // 4

        // 接口 static 方法只能通过接口名调用（预期：实现类上不存在该方法）
        // I.s() ✅；new Impl().s() 编译错误
    }
}
```

## ⚠️ 常见陷阱

- ❌ **实现两个不相关接口的 default 却不重写**：编译失败（典型编译诊断，措辞随版本变化）：
  `class DiamondBad inherits unrelated defaults for hi() from types A and B`
  ✅ 重写并在内部用 `A.super.hi()` 显式分派。
- ❌ **通过实现类调用接口 `static` 方法**：静态方法**不**被实现类继承（预期 `getMethod` 找不到）。
  ✅ 一律 `接口名.方法()`——与父类静态方法的"可被继承"语义刻意不同。
- ❌ **给含两个抽象方法的接口标 `@FunctionalInterface`**：编译失败（典型编译诊断，措辞随版本变化）：
  `Unexpected @FunctionalInterface annotation — Bad is not a functional interface (multiple non-overriding abstract methods found)`
  ✅ 先数清抽象方法；合并入参用自定义 record/参数对象。
- ❌ **拿 default 方法当多继承 mixin 滥用**：状态（字段）依旧不存在，default 里无法持有实例数据。
  ✅ 需要"状态 + 模板"用抽象类；需要"多来源组合行为"才用接口 default。
- ❌ **接口与抽象类无脑二选一**：
  ✅ 决策线：**能"是什么"且共享状态/受保护方法 → 抽象类；纯能力契约、需多实现组合 → 接口**。Java 8 后"接口不能有实现"已不再是接口的短板。

<!-- full-library-explanation -->
## 接口抽象的是调用能力，不是对象存储

接口声明 name()，调用方只需知道能获得名字；对象如何保存名字由实现类决定。default 方法可以复用其他接口方法，却不能为每个实例新增字段。接口常量引用若指向可变集合，final 也不会冻结集合内容，不应把它作为全局可写状态。

default 冲突先看具体父类方法，再看接口继承关系：更具体的子接口可覆盖父接口默认方法；两个互不相关的默认实现才需要实现类明确选择。函数式接口的“一个方法”指一个可合并的函数契约，并非简单统计源码里 abstract 出现次数，而且 sealed 接口不能作为函数式接口。

**练习**：在上文 A、B、C 中删掉 C.hi()，观察冲突；再让 B extends A 并重写 hi，令 C 只 implements B，解释为什么无需再二选一。把 Greeter 改成拥有两个不相容的抽象方法，lambda 应编译失败。验收时同时保留成功案例与预期失败案例，失败诊断的逐字文案不应成为跨 JDK 测试条件。

## 🔗 相关条目

- 📄 **[类、接口与 Record](../../basics/04-classes-records.md)** — 接口语法的教程式讲解
- 📄 **[注解详解](./09-annotations.md)** — `@FunctionalInterface` 的校验机制
- 📄 **[Stream / Optional / Collector](./03-streams-optional.md)** — 函数式接口的主要消费场景
- 📄 **[Record / Sealed / 模式匹配](./05-records-sealed-patterns.md)** — sealed 接口限定实现者
- 🌐 **[JLS 9.8 函数式接口](https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html#jls-9.8)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
