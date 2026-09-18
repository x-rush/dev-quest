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
> **目标读者**: 有旧版 Java 经验、写过大量 getter/setter 样板代码的开发者
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
- 用 record 一行替代传统手写 DTO 的全部样板
- 使用紧凑构造器完成参数校验与规整
- 正确运用接口的 default/static/private 方法
- 判断 record 与传统类、Lombok 的适用边界

## 🔄 旧回顾：一个"标准 DTO"要写多少代码？

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
        return Objects.hash(x, y);
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

一行完成，自动获得：全参构造器、访问器 `x()`/`y()`、基于所有组件的 `equals`/`hashCode`/`toString`、final 类不可继承。

## 🏛️ 类的现代语法要点

### 灵活构造器（Java 25+）

Java 25 之前，`super(...)`/`this(...)` 必须是构造器第一条语句；现在允许在其**之前**先校验参数或初始化字段：

```java
public class SafeList extends ArrayList<String> {
    public SafeList(int capacity) {
        if (capacity < 0) {
            throw new IllegalArgumentException("容量不能为负: " + capacity); // Java 25 前不允许
        }
        super(capacity);
    }
}
```

Java 21 及以下请沿用"先 super、后校验"的写法。

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

    private BigDecimal normalize(BigDecimal price) {          // private 方法（Java 9）
        return price == null ? BigDecimal.ZERO : price;
    }
}
```

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

紧凑构造器在字段赋值**之前**运行，直接修改参数即可影响最终字段值。自定义构造器必须委托给规范构造器（`this(...)`）。

### record 还可以

- 实现接口：`record Circle(double r) implements Shape {}`
- 声明静态成员与静态工厂：`public static Point origin() { return new Point(0, 0); }`
- 使用泛型：`record Box<T>(T value) {}`
- 与 switch 的 record 模式配合解构（见[Record/Sealed/模式匹配](../reference/language-concepts/05-records-sealed-patterns.md)）

### record 的陷阱

- **浅不可变**：组件是 `List` 等可变对象时，内部仍可被修改——构造时用 `List.copyOf` 做防御性拷贝
- **访问器命名**：是 `x()` 而非 `getX()`；Jackson 2.12+/3.x 已原生支持 record，老序列化框架可能不识别
- **可选字段多**时，record 的全参构造器不友好，builder 模式仍更合适

## 🆚 如何选择

| 场景 | 推荐 |
|------|------|
| DTO、值对象、多返回值、配置载体 | `record` |
| 需要继承扩展、可变状态 | `class` |
| 固定实例集合（状态机、常量表） | `enum` |
| 需要跨类型共享行为契约 | `interface` |

关于 Lombok：`@Data`/`@Value` 解决的是 record 出现之前的同一个问题。**新代码优先 record**（语言原生、无编译器插件依赖）；存量 Lombok 代码不必强行迁移。

## 🎯 练习与实践

### 练习一：DTO 迁移
1. 挑一个手写 DTO，改写为 record + 紧凑构造器校验
2. 验证自动生成的 equals/hashCode/toString 行为

### 练习二：泛型 record
1. 定义 `record Pair<K, V>(K key, V value)` 并让它实现 `Comparable<Pair<K,V>>`

### 练习三：防御性拷贝
1. 写一个组件为 `List<String>` 的 record，保证外部无法修改其内部列表

## 🔗 相关文档

- 📄 **[控制流程](./05-control-flow.md)** - 下一站：switch 表达式与模式匹配
- 📄 **[Record/Sealed/模式匹配](../reference/language-concepts/05-records-sealed-patterns.md)** - 现代特性完整参考
- 📄 **[Java 关键字详解](../reference/language-concepts/01-java-keywords.md)** - record 关键字条目


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
