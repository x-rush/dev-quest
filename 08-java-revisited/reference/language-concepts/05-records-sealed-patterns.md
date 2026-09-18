# Record / Sealed / 模式匹配速查

> **文档简介**: Java 16-21 三大现代语言特性（Record、Sealed、模式匹配）的完整语义、组合用法与陷阱的条目式参考
>
> **目标读者**: 需要查阅这三项特性精确规则的开发者
>
> **前置知识**: 类与接口基础（教程见 [类、接口与 Record](../../basics/04-classes-records.md)、[控制流程](../../basics/05-control-flow.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#Record` `#Sealed` `#模式匹配` `#现代特性` |
| **更新日期** | `2026年9月` |

</details>

## 📦 Record

### 定义与自动成员

**定义**: `record` 声明"透明携带不可变数据"的 final 类，自动获得：规范构造器、访问器 `组件名()`、基于全组件的 `equals`/`hashCode`/`toString`。

```java
public record Point(int x, int y) {}
new Point(1, 2).x();      // 访问器无 get 前缀
```

### 构造器变体

```java
public record Range(int low, int high) {
    public Range {                          // 紧凑构造器：赋值前运行，可改参数
        if (low > high) throw new IllegalArgumentException("low>high");
        low = Math.max(low, 0);             // 直接改参数即影响最终字段
    }

    public Range(int high) {                // 自定义构造器：必须委托规范构造器
        this(0, high);
    }
}
```

### 能力与限制

- ✅ 实现接口、声明静态成员/静态工厂、泛型 record、嵌套 record
- ✅ 组件可加注解；`instanceof Point(int x, int y)` 可解构
- ❌ 不能继承类、不能再被继承、不能声明实例字段
- ❌ 组件为可变对象时是**浅不可变**——用 `List.copyOf` 防御性拷贝

```java
public record Team(String name, List<String> members) {
    public Team { members = List.copyOf(members); }   // 防御性拷贝惯用法
}
```

## 🔒 Sealed

### 定义与规则

**定义**: `sealed` 限定继承树封闭，编译器据此做穷举检查；`permits` 列出许可子类型。

```java
public sealed interface Shape permits Circle, Square, Weird {}
public record Circle(double r) implements Shape {}          // record 隐式 final
public record Square(double side) implements Shape {}
public non-sealed class Weird implements Shape {}           // 重新开放
```

**规则清单**:
1. 许可子类型必须与密封类型同模块；未命名模块中必须同包
2. 每个许可子类必须选一个收口：`final` / `sealed` / `non-sealed`
3. `permits` 子句与子类同文件时可省略
4. 密封接口同样可密封其父接口（`sealed interface X extends Y permits A`）

### 与 switch 的组合价值

```java
double area(Shape s) {
    return switch (s) {              // 无 default：穷举由编译器保证
        case Circle c -> Math.PI * c.r() * c.r();
        case Square q -> q.side() * q.side();
        case Weird w  -> 0;          // 漏掉任何分支 → 编译错误
    };
}
```

## 🧩 模式匹配

### instanceof 模式（Java 16）

```java
if (obj instanceof String s && s.length() > 3) { use(s); }
```

作用域规则：模式变量仅在**必然匹配成功**的作用域可用（if 体内、`&&` 右侧、否定分支 `!(obj instanceof String s)` 的 else）。

### switch 类型模式（Java 21）

```java
String label = switch (obj) {
    case null            -> "空";          // 显式 null 分支
    case String s        -> "字符串: " + s;
    case Integer i when i > 0 -> "正整数"; // 守卫 when
    case Integer i       -> "其他整数";
    default              -> "未知";
};
```

- 分支按序匹配；**子类型必须排在父类型前**，否则支配错误（dominance）编译失败
- `case null` 与 default 可共存：有 `case null` 时 null 走该分支，无则 null 落入 default
- Java 25 预览：基本类型模式（`case long l`），生产慎用

### record 模式（Java 21）与嵌套解构

```java
// 单层解构
if (obj instanceof Point(int x, int y)) {
    use(x + y);
}

// 嵌套解构 + 未命名组件 _（Java 22+）
record Order(String id, Customer customer, List<Item> items) {}
record Customer(String name, Address address) {}
record Address(String city, String street) {}

String cityOf(Order order) {
    return switch (order) {
        case Order(_, Customer(_, Address(var city, _)), _) -> city;
        default -> "unknown";
    };
}
```

- 解构即调用 record 的访问器，无反射
- 泛型 record 解构支持类型推断：`case Box<String>(var s)`
- 解构模式中已声明过的变量名会编译报错（同名冲突）

## ✅ 最佳实践 / ❌ 陷阱清单

sealed 适合已知且受控的类型集合，例如一组领域事件；新增成员时，穷尽处理能提醒相关分支更新。开放类型层级也可以使用模式匹配，但需要相应兜底，不能因无法穷尽就认定语法无用。

record 适合数据载体，自动生成相等比较不等于内部成员深度不可变。若可变集合影响 hashCode，把 record 用作 Map key 后再修改成员可能破坏查找；采用不可变成员或复制，并测试这一边界。

## 🔗 相关文档

- 📄 **[Java 关键字详解](./01-java-keywords.md)** - record/sealed/yield/when 关键字条目
- 📄 **[集合框架与泛型](./02-collections-generics.md)** - 泛型 record 与边界
- 📄 **[控制流程](../../basics/05-control-flow.md)** - 模式匹配教程
- 📄 **[现代 Java 特性](../../basics/07-modern-features.md)** - Sealed 教程


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
