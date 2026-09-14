# 枚举详解

> **文档简介**: 枚举的完整语义——values/valueOf/ordinal/name 内置成员、抽象方法与常量体、私有构造器与字段、EnumMap/EnumSet、枚举单例、传统与 Java 21 模式匹配 switch 对枚举的支持、Enum 与 record 的组合
>
> **目标读者**: 需要把枚举从"一组常量"升级为"有行为的类型"来用的开发者
>
> **前置知识**: 基本语法；switch 演进见 [控制流程](../../basics/05-control-flow.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#枚举` `#Enum` `#语言概念` |
| **更新日期** | `2026年9月` |

## 📌 定义

`enum` 声明的是一个**隐式 final、隐式继承 `java.lang.Enum` 的类**；每个枚举常量是该类的**唯一实例**（构造器隐式 private，JVM 保证实例化唯一）。枚举因此天然适合做"有限集合 + 附属数据 + 附属行为"的类型建模。

> 💡 本文行为断言均在本机 JDK 21（javac 21.0.12.1）下编译运行验证。

## 📖 语法 / 签名

### 内置成员速查（继承自 java.lang.Enum）

| 成员 | 语义 | 实测要点 |
|------|------|---------|
| `values()` | 按声明顺序返回所有常量 | **每次调用返回新数组**（防外部改动，循环内注意） |
| `valueOf(String)` | 按名字反查常量 | 大小写敏感 → `IllegalArgumentException`；`null` → `NullPointerException` |
| `ordinal()` | 声明序号（从 0 起） | 只反映声明顺序，别当业务 ID |
| `name()` | 常量名（final，不可重写） | 反序列化/持久化用它 |
| `toString()` | 默认返回 `name()` | **可重写**（展示文案放这里） |
| `compareTo()` | 按 `ordinal` 比较 | 枚举已实现 `Comparable` |
| `equals()` / `==` | 等价（实例唯一） | 枚举是少数可安全用 `==` 的对象 |

### 完整声明形态

```java
public enum Planet {
    // 常量列表（必须最前）—— 传参给构造器
    MERCURY(1), EARTH(3), MARS(4);

    private final int orderNo;                 // 附属字段

    private Planet(int orderNo) {              // 构造器隐式 private，显式写 private 合法
        this.orderNo = orderNo;
    }

    int orderNo() { return orderNo; }

    @Override public String toString() { return name().toLowerCase(); }
}
```

**抽象方法 + 常量体**——每个常量提供自己的实现：

```java
enum Op {
    PLUS  { @Override int apply(int a, int b) { return a + b; } },
    MINUS { @Override int apply(int a, int b) { return a - b; } };

    abstract int apply(int a, int b);          // 每个常量必须实现
}
// Op.PLUS.apply(2, 3) == 5、Op.MINUS.apply(2, 3) == -1（实测）
```

## 💡 示例

```java
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.Map;

public class EnumDemo {
    enum Color { RED, GREEN, BLUE }

    public static void main(String[] args) {
        // 基本成员
        System.out.println(Color.valueOf("GREEN") == Color.GREEN);   // true
        System.out.println(Color.values().length);                   // 3，顺序 = 声明顺序
        Color.RED.ordinal();                                         // 0（合法表达式语句）

        // EnumSet / EnumMap：内部位向量/数组实现，迭代按声明顺序
        var primary = EnumSet.of(Color.RED, Color.BLUE);        // 常用集合首选
        EnumSet.allOf(Color.class);
        Map<Color, String> cn = new EnumMap<>(Color.class);     // Map 键为枚举时的首选
        cn.put(Color.RED, "红");

        // 传统 switch：枚举常量不加类型前缀
        String label = switch (Color.GREEN) {
            case RED -> "warm";
            case GREEN -> "go";
            case BLUE -> "cool";
        };

        // Java 21：对超类型 switch，case 标签可用限定枚举常量 + 类型模式
        Object o = Color.BLUE;
        String kind = switch (o) {
            case Color.RED -> "primary";
            case Color c -> "also-color: " + c.name();
            case null, default -> "not-a-color";
        };                                              // kind == "also-color: BLUE"
    }
}
```

**枚举单例**——JVM 从三个方向堵死"造第二个实例"：

```java
// 1. 构造器隐式 private，编译期禁止 new / super 调用
// 2. 反射：Constructor.newInstance 对枚举直接抛出（实测）
//    java.lang.IllegalArgumentException: Cannot reflectively create enum objects
//    注意：字节码中构造器隐式前置 (String name, int ordinal)，
//    反射查找签名要写 getDeclaredConstructor(String.class, int.class, <原参数...>)
// 3. 克隆：Enum.clone 被 final 化并抛 CloneNotSupportedException；序列化由 Enum 特殊处理
```

**与 record 组合**——枚举做类型标签，record 做不可变载荷：

```java
record Weighted(Op op, int weight) {}   // 枚举做标签、record 做不可变载荷
// sealed 界定子类型的路线见 Record / Sealed / 模式匹配条目
```

## ⚠️ 常见陷阱

- ❌ **`valueOf("green")` 想做大小写无关反查**：直接抛 `IllegalArgumentException`（实测）。
  ✅ `Arrays.stream(Color.values()).filter(c -> c.name().equalsIgnoreCase(input)).findFirst()`，或 `valueOf(input.toUpperCase(Locale.ROOT))` 并捕获异常。
- ❌ **把 `ordinal()` 存进数据库当 ID**：插入新常量或调整声明顺序后，历史数据全部错位。
  ✅ 显式加 `private final int code` 字段持久化。
- ❌ **循环里反复调 `values()`**：每次都克隆新数组（实测 `values() != values()`），热路径白白分配。
  ✅ 提取到局部变量或用 `EnumSet.allOf(...)` 缓存。
- ❌ **switch 选择器就是该枚举类型时写 `case Color.RED`**：编译错误——枚举 switch 的 case 不带类型前缀。
  ✅ 直接 `case RED ->`；限定名仅用于 Java 21 超类型 switch 场景。
- ❌ **重写了 `toString()` 后仍拿它做持久化键**：`toString` 可被重写。
  ✅ 持久化/协议传输用 `name()`。

## 🔗 相关条目

- 📄 **[Record / Sealed / 模式匹配](./05-records-sealed-patterns.md)** — 密封类型与 switch 模式匹配全貌
- 📄 **[接口语义](./10-interface-semantics.md)** — 枚举实现接口与函数式接口判定
- 📄 **[集合框架与泛型](./02-collections-generics.md)** — EnumMap/EnumSet 在集合体系中的位置
- 📄 **[注解详解](./09-annotations.md)** — 注解属性可引用枚举常量
- 🌐 **[Enum (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Enum.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
