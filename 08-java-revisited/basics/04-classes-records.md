# 类、接口与 Record

## 先理解，再动手

接口表达能力，类提供实现，record 方便表达数据载体。record 的成员引用不可变不意味着其引用的集合不可修改。

**本节自测**：给 record 放一个可变 List，再修改列表；尝试改用不可变副本。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

能观察浅不可变的边界；要保持快照应在构造边界复制或选择不可变集合。

</details>

> **文档简介**: 复习类与接口的现代语法要点，掌握用 Record 一行替代手写 DTO 样板代码，学会紧凑构造器校验与 record 适用边界判断
>
> **目标读者**: 会基本编程、正在学习 Java 类与接口的学习者
>
> **前置知识**: 已掌握[变量与类型](./03-variables-types.md)基础

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#面向对象` `#Record` `#接口` `#DTO` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：
- 用 record 表达固定组件的数据载体，并识别不能直接迁移的 DTO 行为
- 使用紧凑构造器完成参数校验与规整
- 正确运用接口的 default/static/private 方法
- 判断 record 与传统类、Lombok 的适用边界

## 🔄 旧回顾：一个"标准 DTO"要写多少代码？

本页先用类声明和方法片段解释语法；带 `public` 的顶层类型应分别放在同名文件。完整 `Main.java` 实验在后文，包含 import、入口及边界检查。

**旧写法**（Java 8 时代典型 DTO）：

```java
public class Point {
    private final int x;
    private final int y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public int getX() { return x; }
    public int getY() { return y; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Point)) return false;
        Point p = (Point) o;
        return x == p.x && y == p.y;
    }

    @Override
    public int hashCode() {
        return java.util.Objects.hash(x, y);
    }

    @Override
    public String toString() {
        return "Point{x=" + x + ", y=" + y + "}";
    }
}
```

约 40 行，只为表达"一个有 x 和 y 的点"。

**现代写法**（Java 16+ 正式特性）：

```java
public record Point(int x, int y) {}
```

record 自动提供规范构造器、访问器 `x()`/`y()`，以及按组件生成的 `equals`/`hashCode`/`toString`；类隐式 final。它不是原 DTO 的无条件替换：访问器名称变了，不能保留可变 setter 或继承结构，默认字符串形式也不同。数组组件按数组对象自身的相等语义比较，不自动做深度内容比较。

## 🏛️ 类的现代语法要点

### 灵活构造器（Java 25+）

Java 25 将灵活构造器正式发布；Java 22–24 曾提供相应预览特性。下面是 Java 25 片段，允许在 `super(...)` 前做受限制的初始化工作；不能由此推断该阶段可任意调用实例方法或泄露 `this`：

```java
public class SafeList extends java.util.ArrayList<String> {
    public SafeList(int capacity) {
        if (capacity < 0) {
            throw new IllegalArgumentException("容量不能为负: " + capacity); // Java 25 前不允许
        }
        super(capacity);
    }
}
```

本教程基础示例使用 Java 21。该版本可通过 `super(checkedCapacity(capacity))` 调用静态辅助方法先验证实参，不能在显式 `super(...)` 前添加独立语句。上述 Java 25 片段不属于本文 Java 21 运行证据。版本与限制见 [JEP 513](https://openjdk.org/jeps/513)。

## 🔌 接口：不再是纯抽象

```java
public interface DiscountPolicy {
    BigDecimal apply(BigDecimal price);                       // 抽象方法

    default BigDecimal applyWithFloor(BigDecimal price) {     // default 方法（Java 8）
        return apply(price).max(BigDecimal.ZERO);             // 可复用抽象方法
    }

    static DiscountPolicy none() {                            // static 工厂（Java 8）
        return price -> price;
    }

}
```

片段需要 `import java.math.BigDecimal;`；调用者应传非 null 价格。接口还可用 private 方法复用内部实现，但 private 方法不属于调用者可见契约。不要为了展示语法，把“缺失价格”默默转换成零。default 方法冲突时，实现类可能需要显式选择实现；接口也不能代替对象状态的设计。

**旧对照**：Java 8 之前接口只能有抽象方法与常量，公共实现只能放抽象类。default 方法改变了这个取舍——"为接口添加能力"不再必须付出"单继承"的代价。

## 📦 Record：不可变数据载体

### 基本用法

```java
var p = new Point(1, 2);
p.x();   // 访问器直接用组件名，没有 get 前缀
p.y();
System.out.println(p);  // Point[x=1, y=2]
```

### 紧凑构造器：校验与规整

```java
public record Range(int low, int high) {
    public Range {                        // 不写参数列表 = 紧凑构造器
        if (low > high) {
            throw new IllegalArgumentException("low 不能大于 high");
        }
    }
}
```

紧凑构造器体执行后，编译器才将参数赋给对应字段；修改参数会影响字段值。非规范构造器必须委托给其他构造器，最终到达规范构造器；规范构造器本身不通过 `this(...)` 委托。

### record 还可以

- 实现接口：`record Circle(double r) implements Shape {}`
- 声明静态成员与静态工厂：`public static Point origin() { return new Point(0, 0); }`
- 使用泛型：`record Box<T>(T value) {}`
- 与 switch 的 record 模式配合解构（见[Record/Sealed/模式匹配](../reference/language-concepts/05-records-sealed-patterns.md)）

### record 的陷阱

- **浅不可变**：组件引用不能重绑，引用的对象仍可能改变。`List.copyOf` 提供不可修改的列表快照，但不复制元素，还拒绝 null 列表与 null 元素。含可变元素时需另定深拷贝或不可变元素契约
- **访问器命名**：是 `x()` 而非 `getX()`；Jackson 2.12+/3.x 已原生支持 record，老序列化框架可能不识别
- **可选字段多**时，record 的全参构造器不友好，builder 模式仍更合适

## 🆚 如何选择

| 场景 | 推荐 |
|------|------|
| DTO、值对象、多返回值、配置载体 | `record` |
| 需要继承扩展、可变状态 | `class` |
| 固定实例集合（状态机、常量表） | `enum` |
| 需要跨类型共享行为契约 | `interface` |

record 适合固定组件的数据载体。Lombok `@Data` 常用于可变 bean，`@Value` 用于生成另一种不可变类样板；其访问器、继承与构造契约并不都等同 record。先看调用者是否依赖 setter、无参构造器或 bean 命名规则，再决定是否迁移。

## 完整实验：建立列表快照与输入不变量

将本节保存为 `Main.java`，用 Java 21 执行 `javac --release 21 Main.java` 和 `java Main`。预期输出 `record boundaries: ok`。构造器拒绝损坏输入，外部修改原始列表不会改变 `Tags`；但对可变元素做浅复制仍不能隔离修改。运行范围见 [基础类型验证记录](../../shared-resources/tools/document-quality/reports/php-java-types-validation.md)。

<!-- reference-case: {"id":"java-record-boundaries","stdout":"record boundaries: ok\n"} -->
```java
import java.util.ArrayList;
import java.util.List;

public class Main {
    record Tags(List<String> values) {
        Tags { values = List.copyOf(values); }
    }
    record Range(int low, int high) {
        Range {
            if (low > high) throw new IllegalArgumentException("low > high");
        }
        Range(int point) { this(point, point); }
    }
    static void check(boolean condition) {
        if (!condition) throw new AssertionError("检查失败");
    }
    static void expect(Class<? extends Throwable> type, Runnable action) {
        try { action.run(); }
        catch (Throwable error) {
            if (type.isInstance(error)) return;
            throw new AssertionError("异常类型错误", error);
        }
        throw new AssertionError("应拒绝操作");
    }
    public static void main(String[] args) {
        var original = new ArrayList<>(List.of("java"));
        var tags = new Tags(original);
        original.add("changed");
        check(tags.values().equals(List.of("java")));
        expect(UnsupportedOperationException.class, () -> tags.values().add("x"));
        expect(NullPointerException.class, () -> new Tags(null));
        var withNull = new ArrayList<String>();
        withNull.add(null);
        expect(NullPointerException.class, () -> new Tags(withNull));
        check(new Tags(List.of("java")).equals(tags));
        check(new Range(2).equals(new Range(2, 2)));
        expect(IllegalArgumentException.class, () -> new Range(3, 2));

        var mutableElement = new StringBuilder("a");
        var shallow = List.copyOf(List.of(mutableElement));
        mutableElement.append("b");
        check(shallow.get(0).toString().equals("ab"));
        System.out.println("record boundaries: ok");
    }
}
```

选择 `List<String>` 是因为 String 元素本身不可变。若换成可变的订单对象，需要在边界复制对象，或把订单也设计为具有不可变组件的值对象；只复制列表并不完成这项设计。相关官方契约：[Record 类](https://docs.oracle.com/en/java/javase/21/language/records.html) 与 [List.copyOf](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html#copyOf(java.util.Collection))。

## 🎯 练习与实践

### 练习一：DTO 迁移
1. 挑一个手写 DTO，改写为 record + 紧凑构造器校验
2. 验证自动生成的 equals/hashCode/toString 行为

### 练习二：泛型 record
1. 定义 `record Pair<K, V>(K key, V value)`，再用外部 `Comparator<Pair<String, Integer>>` 按 key、value 排序。任意 K/V 不保证可比较；若把排序放进 `Comparable`，必须设计泛型边界和 null 策略。

### 练习三：防御性拷贝
1. 写一个组件为 `List<String>` 的 record，保证外部无法修改其内部列表

## 🔗 相关文档

- 📄 **[控制流程](./05-control-flow.md)** - 下一站：switch 表达式与模式匹配
- 📄 **[Record/Sealed/模式匹配](../reference/language-concepts/05-records-sealed-patterns.md)** - 现代特性完整参考
- 📄 **[Java 关键字详解](../reference/language-concepts/01-java-keywords.md)** - record 关键字条目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
