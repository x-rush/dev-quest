# Java 关键字详解

> **文档简介**: Java 全部关键字与保留字的分类速查，重点详解 record、sealed、var、yield、when 等新旧关键字与上下文关键字的语义、语法与陷阱
>
> **目标读者**: 需要系统核对 Java 关键字知识、特别是新版上下文关键字的开发者
>
> **前置知识**: 基本语法阅读能力；系统学习请先走 [basics 路径](../../basics/03-variables-types.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#关键字` `#语法基础` `#语言概念` |
| **更新日期** | `2026年9月` |

## 📋 关键字总表（按用途分组）

| 分组 | 关键字 |
|------|--------|
| 类型与声明 | `class` `interface` `record` `enum` `extends` `implements` `sealed` `permits` `non-sealed` |
| 访问与修饰 | `public` `private` `protected` `abstract` `static` `final` `strictfp` `transient` `volatile` `synchronized` `native` |
| 流程控制 | `if` `else` `switch` `case` `default` `for` `while` `do` `break` `continue` `return` `yield` |
| 异常 | `try` `catch` `finally` `throw` `throws` `assert` |
| 对象与引用 | `new` `this` `super` `instanceof` `void` `var` |
| 包与模块 | `package` `import` `module` `exports` `requires` `opens` `provides` `uses` `to` `with` `transitive` |
| 字面量 | `null` `true` `false` |
| 保留未用 | `const` `goto` |
| 模式匹配 | `when`（Java 21 守卫）、`_`（Java 22 未命名变量，非关键字但保留） |

> 💡 `record`/`sealed`/`var`/`yield`/`when` 等是**上下文关键字**：在特定语法位置有特殊含义，仍可作普通标识符使用。

---

## 1. var - 局部变量类型推断（Java 10）

**定义**: 编译器依据右侧初始化表达式推断局部变量类型，字节码与显式声明完全一致。

```java
var list = new ArrayList<String>();              // 推断为 ArrayList<String>
try (var reader = Files.newBufferedReader(p)) {} // try-with-resources 可用
```

**陷阱**: 仅限有初始化器的局部变量；字段/参数/返回值不可用；`var y = null;` 无法编译。

## 2. record - 不可变数据载体（Java 16）

**定义**: 声明透明携带不可变数据的 final 类，自动生成构造器、访问器、equals/hashCode/toString。

```java
public record Point(int x, int y) {
    public Point {                               // 紧凑构造器
        if (x < 0) throw new IllegalArgumentException("x<0");
    }
}
```

**陷阱**: 不可继承；浅不可变（组件为集合时内容可变）；访问器是 `x()` 不是 `getX()`。

## 3. sealed / permits / non-sealed - 密封类型（Java 17）

**定义**: `sealed` 限定哪些类可以继承/实现；`permits` 显式列举许可者；`non-sealed` 在子级重新开放。

```java
public sealed interface Shape permits Circle, Rect {}
public record Circle(double r) implements Shape {}
public non-sealed class Rect implements Shape {} // 重新开放继承
```

**陷阱**: 许可子类必须与密封类型同模块（或同包）；每个子类必须加 `final`/`sealed`/`non-sealed` 之一。

## 4. yield - switch 表达式返回值（Java 14）

**定义**: 在 switch 表达式的语句块分支中返回结果值。

```java
int code = switch (level) {
    default -> {
        int base = 1;
        yield base + 1;      // 代码块分支用 yield 而非 return
    }
};
```

**陷阱**: `yield` 是上下文关键字；变量名 `yield` 仍合法但强烈不建议。

## 5. when - switch 模式守卫（Java 21）

**定义**: 为类型模式追加布尔守卫条件，"类型匹配且条件成立"才进入该分支。

```java
String s = switch (obj) {
    case Integer i when i > 0 -> "正数";
    case Integer i            -> "非正数";
    default -> "其他";
};
```

**陷阱**: 守卫仅做判断，别放副作用；两个 `case Integer` 的顺序影响匹配结果。

## 6. instanceof - 类型判断（Java 16 模式匹配）

**定义**: 判断对象类型；配合模式变量免去显式强转。

```java
if (obj instanceof String s && !s.isBlank()) {
    use(s);               // s 已完成类型转换
}
```

**陷阱**: 对 `null` 恒为 false；不能跨兄弟类型转换。

## 7. synchronized / volatile - 并发基础

**定义**: `synchronized` 保证互斥与可见性；`volatile` 仅保证可见性与禁止指令重排。

```java
private volatile boolean running = true;    // 状态标志用 volatile
public synchronized void inc() { count++; } // 复合操作需要互斥
```

**陷阱**: `volatile` 不保证 `count++` 原子性——计数用 `AtomicInteger`/`LongAdder`；虚拟线程在 synchronized 中阻塞会"钉住"载体线程（Java 24 已修复）。

## 8. 经典关键字要点速览

| 关键字 | 定义 | 要点/陷阱 |
|--------|------|----------|
| `final` | 类不可继承/方法不可重写/变量不可重指 | `final` 引用 ≠ 不可变对象，内容仍可能可变 |
| `static` | 成员属于类而非实例 | 静态可变状态是并发隐患；静态方法不能访问实例成员 |
| `this` / `super` | 当前实例 / 父类引用 | 匿名内部类中外部实例需 `Outer.this`；`super(...)` 须是首条语句（Java 25 放宽） |
| `transient` | 字段不参与默认序列化 | record 组件同样生效；现代替代：Jackson `@JsonIgnore` |
| `native` | 方法由本地代码实现 | 集中在独立的本地适配层（JNI/FFM） |
| `assert` | 开发期不变式检查 | 默认禁用（需 `-ea`），不能替代参数校验 |
| `strictfp` | 严格浮点语义 | 历史遗留，几乎不用 |
| `default` | 接口 default 方法 / switch 兜底 | 两个语义完全不同，注意上下文 |
| `const` / `goto` | 保留字，无功能 | 不能作标识符 |
| `module` 等模块关键字 | JPMS 上下文关键字 | 仅在 `module-info.java` 中是关键字 |
| `_` | 未命名变量（Java 22） | Java 9-21 中是非法标识符 |

模块声明示例：

```java
module com.example.app {
    requires java.net.http;
    exports com.example.api;
}
```

---

## 🔗 相关文档

- 📄 **[Record/Sealed/模式匹配](./05-records-sealed-patterns.md)** - record/sealed/when 的完整语义
- 📄 **[集合框架与泛型](./02-collections-generics.md)** - var 与泛型推断的配合
- 📄 **[变量与类型](../../basics/03-variables-types.md)** - var 的教程式讲解
- 📄 **[控制流程](../../basics/05-control-flow.md)** - switch/yield/when 的教程式讲解
