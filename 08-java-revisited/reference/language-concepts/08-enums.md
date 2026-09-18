# 枚举详解

> **文档简介**: 枚举的完整语义——values/valueOf/ordinal/name 内置成员、抽象方法与常量体、私有构造器与字段、EnumMap/EnumSet、枚举单例、传统与 Java 21 模式匹配 switch 对枚举的支持、Enum 与 record 的组合
>
> **目标读者**: 需要把枚举从"一组常量"升级为"有行为的类型"来用的开发者
>
> **前置知识**: 基本语法；switch 演进见 [控制流程](../../basics/05-control-flow.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#枚举` `#Enum` `#语言概念` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

`enum` 声明的是一个**隐式继承 java.lang.Enum 的类**；无常量专属类体时隐式 final，有常量专属类体时隐式 sealed；每个枚举常量对应一个唯一的实例（构造器隐式 private，JVM 保证实例化唯一）。枚举因此天然适合做"有限集合 + 附属数据 + 附属行为"的类型建模。

> 示例给出预期行为与规范依据。本轮环境未提供 Java 编译器，未复现历史运行记录；请在项目约定 JDK 上编译验证。

## 📖 语法 / 签名

### 内置成员速查（values/valueOf(String) 由具体枚举声明隐式提供，其余主要来自 Enum）

| 成员 | 语义 | 语义要点 |
|------|------|---------|
| `values()` | 按声明顺序返回所有常量 | **每次调用返回新数组**（防外部改动，循环内注意） |
| `valueOf(String)` | 按名字反查常量 | 大小写敏感 → `IllegalArgumentException`；`null` → `NullPointerException` |
| `ordinal()` | 声明序号（从 0 起） | 只反映声明顺序，别当业务 ID |
| `name()` | 常量名（final，不可重写） | 可用于按名字映射；重命名会影响兼容，长期协议宜定义独立 code |
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
// Op.PLUS.apply(2, 3) == 5、Op.MINUS.apply(2, 3) == -1（预期）
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
// 2. 反射：Constructor.newInstance 对枚举直接抛出（预期）
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

- ❌ **`valueOf("green")` 想做大小写无关反查**：直接抛 `IllegalArgumentException`（预期）。
  ✅ `Arrays.stream(Color.values()).filter(c -> c.name().equalsIgnoreCase(input)).findFirst()`，或 `valueOf(input.toUpperCase(Locale.ROOT))` 并捕获异常。
- ❌ **把 `ordinal()` 存进数据库当 ID**：插入新常量或调整声明顺序后，历史数据全部错位。
  ✅ 显式加 `private final int code` 字段持久化。
- ❌ **循环里反复调 `values()`**：每次都克隆新数组（预期 `values() != values()`），热路径白白分配。
  ✅ 提取到局部变量或用 `EnumSet.allOf(...)` 缓存。
- **case 标签与版本**：Java 21 允许限定枚举常量，例如 case Color.RED；也可继续使用传统 case RED。旧版本语法限制不同，不要套用到 Java 21。
- ❌ **重写了 `toString()` 后仍拿它做持久化键**：`toString` 可被重写。
  ✅ 持久化/协议传输用 `name()`。

<!-- full-library-explanation -->
## 枚举负责封闭集合，协议编码负责兼容

枚举适合程序已知且有限的状态，例如 DRAFT、PUBLISHED、ARCHIVED。ordinal 是声明位置，调整顺序就会变化；name 比位置稳定，但重命名常量也会改变它。长期保存或跨服务传输时，可定义独立 code，并为未知 code 设计失败或降级策略。

枚举常量可以有方法和字段，但可变字段会被所有使用该常量的调用者共享。因此“枚举单例”只解决实例唯一，不自动保证内部状态线程安全。EnumSet 和 EnumMap 表达受限的键集合，比散落的字符串更容易让编译器帮助发现拼写错误。

**练习**：给订单状态定义独立 code，把 JSON 中的 code 转成枚举；未知值应返回明确的验证错误。改变常量声明顺序后，已有 code 的解析结果应保持不变。再增加一个状态，观察穷尽 switch 表达式如何提示遗漏分支；不要为了消除提示立即加一个吞掉所有情况的 default。

Java 21 允许限定枚举常量作 case 标签，适用条件以 [Java 21 语言更新](https://docs.oracle.com/en/java/javase/21/language/java-language-changes-release.html) 为准。

## 🔗 相关条目

- 📄 **[Record / Sealed / 模式匹配](./05-records-sealed-patterns.md)** — 密封类型与 switch 模式匹配全貌
- 📄 **[接口语义](./10-interface-semantics.md)** — 枚举实现接口与函数式接口判定
- 📄 **[集合框架与泛型](./02-collections-generics.md)** — EnumMap/EnumSet 在集合体系中的位置
- 📄 **[注解详解](./09-annotations.md)** — 注解属性可引用枚举常量
- 🌐 **[Enum (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Enum.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
