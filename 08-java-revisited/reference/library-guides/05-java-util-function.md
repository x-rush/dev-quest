# java.util.function 导览

> **文档简介**: JDK 内置函数式接口库——Function/Consumer/Supplier/Predicate 四大核心与二元变体、andThen/compose/identity 组合子、基本类型特化、方法引用四种形态
>
> **目标读者**: 需要选对函数式接口签名、读懂 Stream 参数类型的开发者
>
> **前置知识**: lambda 基础；消费场景见 [Stream / Optional / Collector](../language-concepts/03-streams-optional.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#函数式接口` `#lambda` `#方法引用` `#标准库` |
| **更新日期** | `2026年9月` |

## 📌 定义

`java.util.function` 是 JDK 自带的函数式接口库（数十个接口），Stream/Optional/Map 的参数类型全部出自这里。选型口诀：**看"进什么、出什么"**——有进有出 `Function`、只进不出 `Consumer`、无进有出 `Supplier`、只判不出 `Predicate`。

> 💡 本文行为断言均在本机 JDK 21（javac 21.0.12.1）下编译运行验证。

## 📖 语法 / 签名

### 四大核心 + 常用变体

| 接口 | 抽象方法 | 语义 | 实测示例 |
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

twice.andThen(inc).apply(5);   // 11：先自身后参数（实测）
twice.compose(inc).apply(5);   // 12：先参数后自身（实测）
Function.identity();           // 原样返回（实测）

Predicate<String> nonEmpty  = s -> !s.isEmpty();
nonEmpty.and(shortStr)         // 且
        .or(other)             // 或
        .negate();             // 非（全部实测）

Consumer<String> chained = appender.andThen(next);  // 顺序执行（实测）
BinaryOperator.maxBy / minBy                  // 按比较器取极值（实测）
```

### 基本类型特化（避免装箱）

| 泛型版 | 特化版 |
|--------|--------|
| `Predicate<Integer>` | `IntPredicate` / `LongPredicate` / `DoublePredicate` |
| `Function<Integer,Integer>` | `IntUnaryOperator`、`IntFunction<R>`、`ToIntFunction<T>` |
| `Supplier<Integer>` | `IntSupplier` |

```java
IntPredicate even = n -> n % 2 == 0;          // 直接收 int，无装箱（实测）
ToIntFunction<String> h = String::hashCode;   // 出参特化（实测）
```

### 方法引用四种形态

| 形态 | 写法 | 等价 lambda |
|------|------|------------|
| 静态方法 | `Integer::parseInt` | `s -> Integer.parseInt(s)`（实测） |
| 绑定实例（特定对象） | `base::concat` | `s -> base.concat(s)`（实测） |
| 无界实例（首个参数作接收者） | `String::length` | `s -> s.length()`（实测） |
| 构造器 | `ArrayList::new`、`int[]::new` | `() -> new ArrayList<>()`（实测） |

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

## ⚠️ 常见陷阱

- ❌ **`andThen` 与 `compose` 顺序记反**：`f.andThen(g)` = f 先 g 后；`f.compose(g)` = g 先 f 后（实测：`twice.andThen(inc)` 11 vs `twice.compose(inc)` 12）。
  ✅ 记忆锚点：`andThen` 是"然后"，`compose` 是"先经过 g"。
- ❌ **用 `Function<Integer,Integer>` 处理大量基本类型**：自动装箱开销。
  ✅ 流里 `mapToInt/mapToLong/...`，独立接口选 `IntPredicate` 等特化版。
- ❌ **lambda 里修改外部可变状态还指望并行安全**：Consumer 的副作用在并行流下是竞态。
  ✅ 副作用只放终止操作 `forEach/collect`，中间操作保持无状态。
- ❌ **方法引用歧义时硬读**：重载方法的方法引用可能匹配多个函数式接口。
  ✅ 显式声明目标类型变量，或退回写 lambda。

## 🔗 相关条目

- 📄 **[Stream / Optional / Collector](../language-concepts/03-streams-optional.md)** — 函数式接口的主消费场景
- 📄 **[接口语义](../language-concepts/10-interface-semantics.md)** — SAM 判定与 @FunctionalInterface
- 📄 **[集合框架与泛型](../language-concepts/02-collections-generics.md)** — `Map.computeIfAbsent` 等消费点
- 🌐 **[java.util.function (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/function/package-summary.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
