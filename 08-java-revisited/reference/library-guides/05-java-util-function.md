# java.util.function 导览

> **文档简介**: JDK 内置函数式接口库——Function/Consumer/Supplier/Predicate 四大核心与二元变体、andThen/compose/identity 组合子、基本类型特化、方法引用四种形态
>
> **目标读者**: 需要选对函数式接口签名、读懂 Stream 参数类型的开发者
>
> **前置知识**: lambda 基础；消费场景见 [Stream / Optional / Collector](../language-concepts/03-streams-optional.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#函数式接口` `#lambda` `#方法引用` `#标准库` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

`java.util.function` 是 JDK 自带的函数式接口库（数十个接口），Stream/Optional/Map 的许多行为参数使用这里的接口，另有 Comparator 等类型。选型口诀：**看"进什么、出什么"**——有进有出 `Function`、只进不出 `Consumer`、无进有出 `Supplier`、返回布尔结果 `Predicate`。

> 示例给出预期行为与规范依据。本轮环境未提供 Java 编译器，未复现历史运行记录；请在项目约定 JDK 上编译验证。

## 📖 语法 / 签名

### 四大核心 + 常用变体

| 接口 | 抽象方法 | 语义 | 预期示例 |
|------|---------|------|---------|
| `Function<T,R>` | `R apply(T)` | 有进有出 | `x -> x * 2` |
| `Consumer<T>` | `void accept(T)` | 只进不出（副作用） | `sb::append` |
| `Supplier<T>` | `T get()` | 无进有出 | `() -> "made"` |
| `Predicate<T>` | `boolean test(T)` | 判定 | `s -> !s.isEmpty()` |
| `BiFunction<T,U,R>` | `R apply(T,U)` | 双参进 | `Integer::sum` |
| `BinaryOperator<T>` | 继承 BiFunction，两参同型一结果 | 归约 | `BinaryOperator.maxBy(Integer::compare)` |
| `UnaryOperator<T>` | 继承 Function，进出同型 | 变换 | `String::toUpperCase` |
| `BiConsumer<T,U>` / `BiPredicate<T,U>` | 双参版 | Map.forEach 等 | — |

### 组合方法

```java
Function<Integer, Integer> twice = x -> x * 2;
Function<Integer, Integer> inc   = x -> x + 1;

twice.andThen(inc).apply(5);   // 11：先自身后参数（预期）
twice.compose(inc).apply(5);   // 12：先参数后自身（预期）
Function.identity();           // 原样返回（预期）

Predicate<String> nonEmpty  = s -> !s.isEmpty();
nonEmpty.and(shortStr)         // 且
        .or(other)             // 或
        .negate();             // 非（预期行为）

Consumer<String> chained = appender.andThen(next);  // 顺序执行（预期）
BinaryOperator.maxBy / minBy                  // 按比较器取极值（预期）
```

### 基本类型特化（避免装箱）

| 泛型版 | 特化版 |
|--------|--------|
| `Predicate<Integer>` | `IntPredicate` / `LongPredicate` / `DoublePredicate` |
| `Function<Integer,Integer>` | `IntUnaryOperator`、`IntFunction<R>`、`ToIntFunction<T>` |
| `Supplier<Integer>` | `IntSupplier` |

```java
IntPredicate even = n -> n % 2 == 0;          // 直接收 int，无装箱（预期）
ToIntFunction<String> h = String::hashCode;   // 出参特化（预期）
```

### 方法引用四种形态

| 形态 | 写法 | 等价 lambda |
|------|------|------------|
| 静态方法 | `Integer::parseInt` | `s -> Integer.parseInt(s)`（预期） |
| 绑定实例（特定对象） | `base::concat` | `s -> base.concat(s)`（预期） |
| 无界实例（首个参数作接收者） | `String::length` | `s -> s.length()`（预期） |
| 构造器 | `ArrayList::new`、`int[]::new` | `() -> new ArrayList<>()`、`n -> new int[n]`（预期） |

## 💡 示例

```java
import java.util.ArrayList;
import java.util.function.*;

public class FunctionDemo {
    public static void main(String[] args) {
        var sb = new StringBuilder();
        Consumer<String> appender = sb::append;
        Consumer<String> chained  = appender.andThen(s -> sb.append('!'));
        chained.accept("go");
        System.out.println(sb);                       // go!（andThen 顺序执行）

        BiFunction<Integer, Integer, Integer> add = Integer::sum;
        System.out.println(add.apply(2, 3));          // 5

        Supplier<ArrayList<String>> make = ArrayList::new;
        System.out.println(make.get().isEmpty());     // true
    }
}
```

### 正文提取验证：组合顺序与短路

这个完整围栏只使用 `java.util.function`。它验证 `andThen`/`compose` 的顺序，也验证 `Predicate.and` 在左侧为 `false` 时不会调用右侧谓词。

```java
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Function;
import java.util.function.Predicate;

public class FunctionVerification {
    public static void main(String[] args) {
        Function<Integer, Integer> twice = n -> n * 2;
        Function<Integer, Integer> increment = n -> n + 1;
        AtomicInteger rightCalls = new AtomicInteger();
        Predicate<Integer> never = n -> false;
        Predicate<Integer> right = n -> {
            rightCalls.incrementAndGet();
            return true;
        };

        System.out.println(twice.andThen(increment).apply(5));
        System.out.println(twice.compose(increment).apply(5));
        System.out.println(never.and(right).test(1) + "|" + rightCalls.get());
    }
}
```

## ⚠️ 常见陷阱

- ❌ **`andThen` 与 `compose` 顺序记反**：`f.andThen(g)` = f 先 g 后；`f.compose(g)` = g 先 f 后（预期：`twice.andThen(inc)` 11 vs `twice.compose(inc)` 12）。
  ✅ 记忆锚点：`andThen` 是"然后"，`compose` 是"先经过 g"。
- ❌ **用 `Function<Integer,Integer>` 处理大量基本类型**：自动装箱开销。
  ✅ 流里 `mapToInt/mapToLong/...`，独立接口选 `IntPredicate` 等特化版。
- ❌ **lambda 写入共享可变状态还指望并行安全**：并行流会并发调用 Consumer；共享的 `ArrayList`、计数器等若没有同步就会产生竞态。副作用本身不必然不安全，关键在于状态是否共享及其同步契约。
  ✅ 中间操作保持无状态；并行终止操作同样需要线程安全或正确的归约，不能共享无保护的可变容器。
- ❌ **方法引用歧义时硬读**：重载方法的方法引用可能匹配多个函数式接口。
  ✅ 显式声明目标类型变量，或退回写 lambda。

<!-- full-library-explanation -->
## 函数对象不等于已经执行的结果

Supplier<T> 表示每次调用 get 时如何取得 T，不保证缓存，也不保证每次创建新对象。Function<T,R> 变换输入，Predicate<T> 给出布尔判断，Consumer<T> 执行副作用。理解签名后，Stream 的 map、filter、forEach 就分别对应这三种职责。

andThen 按先自己后参数的顺序组合；前一个函数抛异常时，后一个不会执行。Predicate.and 与 or 会短路，因此 `s -> s != null` 与后续长度检查可以安全组合，但顺序写反仍会空指针。标准 Function 的方法签名不声明受检异常，调用会抛 IOException 的函数时必须明确处理或选择自定义契约。

**练习**：用计数器观察 Optional.orElse(expensive()) 和 orElseGet(() -> expensive())：Optional 有值时，前者参数仍先求值，后者供应函数不执行。再组合一个必定为 false 的 Predicate 与会抛错的 Predicate，验证 and 会跳过后者。把操作放到并行流终止阶段并不自动使共享 ArrayList.add 安全，优先用满足归约契约的 collect。

## 🔗 相关条目

- 📄 **[Stream / Optional / Collector](../language-concepts/03-streams-optional.md)** — 函数式接口的主消费场景
- 📄 **[接口语义](../language-concepts/10-interface-semantics.md)** — SAM 判定与 @FunctionalInterface
- 📄 **[集合框架与泛型](../language-concepts/02-collections-generics.md)** — `Map.computeIfAbsent` 等消费点
- 🌐 **[java.util.function (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/function/package-summary.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
