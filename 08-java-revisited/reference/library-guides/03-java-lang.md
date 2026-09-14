# java.lang 导览

> **文档简介**: 隐式 import 的根包——Object 方法契约（equals/hashCode/toString/clone）、StringBuilder 与 StringBuffer、Math、System、Class 与反射入门、record 的自动成员语义
>
> **目标读者**: 需要核对 Object 契约细节与 java.lang 基础设施 API 的开发者
>
> **前置知识**: 基本语法；String 专项见 [字符串不可变语义](../language-concepts/07-string-immutability-pool.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#java.lang` `#Object契约` `#反射` `#标准库` |
| **更新日期** | `2026年9月` |

## 📌 定义

`java.lang` 承载语言级基础设施：`Object`（一切对象的契约源头）、包装类、`String`/`StringBuilder`、`Math`、`System`、`Runtime`、`Thread`、`Class` 与反射入口。该包**自动 import**，无需显式声明。

> 💡 本文行为断言均在本机 JDK 21（javac 21.0.12.1）下编译运行验证。

## 📖 语法 / 签名

### Object 方法契约

| 方法 | 契约 | 要点 |
|------|------|------|
| `equals(Object)` | 自反、对称、传递、一致；`x.equals(null) == false` | 重写必须带 `Object` 参数签名 |
| `hashCode()` | 相等对象必同哈希；哈希相等不要求相等 | **重写 equals 必须连着重写 hashCode**，否则 HashMap/HashSet 行为错乱 |
| `toString()` | 可读表示 | 模板里大量隐式调用 |
| `clone()` | 浅拷贝 | 争议 API，见下 |
| `getClass()` | 运行时类 | 反射入口，`"x".getClass() == String.class`（实测） |
| `finalize()` | 终结器 | 已废弃（Java 18 起标记 forRemoval，JEP 421），别用 |

**clone 的争议**：`clone()` 要求实现 `Cloneable` 标记接口（无方法、纯开关），未实现时 `super.clone()` 抛 `CloneNotSupportedException`（实测）；且浅拷贝对可变嵌套对象不安全。《Effective Java》的建议：**用拷贝构造器或拷贝工厂替代 clone**；数组是唯一推荐 `clone` 的场景。

### StringBuilder vs StringBuffer

| | `StringBuilder` | `StringBuffer` |
|--|-----------------|----------------|
| 线程安全 | 否（单线程首选） | 是（方法级 synchronized） |
| 性能 | 更快 | 锁开销 |
| API | `append`/`insert`/`reverse`/`delete`/`setLength(0)` 复用 | 同左 |

默认初始容量 16，扩容为 `2*旧容量 + 2`（实测）。

### Math 与 System 要点

```java
Math.floorDiv(-7, 2);      // -4（向下取整除法）
Math.floorMod(-7, 2);      // 1 ；而 -7 % 2 == -1（% 符号随被除数，实测）
Math.addExact(Integer.MAX_VALUE, 1);   // 溢出 → ArithmeticException（实测）
Math.abs(Integer.MIN_VALUE);           // 仍是 Integer.MIN_VALUE！int 溢出（实测）
Math.round(-2.5);          // -2（"加 0.5 向下取整"，向正无穷方向半入，实测）

System.arraycopy(src, 0, dst, 1, 4);   // 高效数组复制
System.nanoTime();                     // 纳秒计时器：只用于测耗时的相对时间，不是墙钟
System.currentTimeMillis();            // 墙钟毫秒，可被调钟影响
System.getenv("PATH");                 // 环境变量
```

### Class 与反射入门

```java
String name = "reflect-me";
Class<? extends String> c = name.getClass();
c.getSimpleName();                          // "String"
Method len = String.class.getMethod("length");
len.invoke("reflect-me");                   // 10（实测）
Point.class.getRecordComponents();          // record 组件数组（Java 15+）
```

`setAccessible(true)` 可绕过 private（受 JPMS `opens` 限制）；反射有安全与性能成本，框架代码才用。

### record 的自动成员语义

record 自动生成：全参构造器、组件访问器（`x()` 而非 `getX()`）、分量比较的 `equals`/`hashCode`、格式 `Point[x=1, y=2]` 的 `toString`（全部实测验证）。

## 💡 示例

```java
import java.util.Objects;

public class ContractDemo {
    record Point(int x, int y) {}

    static class Money {
        final int cents;
        Money(int cents) { this.cents = cents; }

        @Override public boolean equals(Object o) {
            return o instanceof Money m && m.cents == cents;
        }
        @Override public int hashCode() { return Objects.hash(cents); }   // 与 equals 配套
        @Override public String toString() { return "Money{cents=%d}".formatted(cents); }
    }

    public static void main(String[] args) {
        Money a = new Money(100), b = new Money(100);
        System.out.println(a.equals(b) && a.hashCode() == b.hashCode());  // true
        System.out.println(new Point(1, 2));                              // Point[x=1, y=2]
        System.out.println(new StringBuilder("abc").reverse());           // cba
        // 陷阱：StringBuilder 的 equals 是同一性语义（实测）
        System.out.println(new StringBuilder("a").equals(new StringBuilder("a"))); // false
    }
}
```

## ⚠️ 常见陷阱

- ❌ **只重写 `equals` 不重写 `hashCode`**：放进 HashMap/HashSet 后"相等"的对象找不到。
  ✅ 成对重写，用 `Objects.hash(...)` 组合。
- ❌ **比较 `StringBuilder` 内容用 `equals`**：继承自 Object 的同一性语义，同内容也返回 false（实测）。
  ✅ `sb1.toString().contentEquals(sb2)` 或先 `toString()`。
- ❌ **`Math.abs(Integer.MIN_VALUE)` 想拿到正数**：int 溢出，结果还是负数（实测）。
  ✅ 换 `long` 运算或 `Math.absExact`（溢出抛异常）。
- ❌ **用 `nanoTime()` 表示当前时刻**：它是相对计时器，取值语义不代表墙钟。
  ✅ 当前时刻用 `System.currentTimeMillis()` 或 `Instant.now()`。
- ❌ **业务类实现 `Cloneable` 手写 clone**：标记接口 + 浅拷贝双重坑。
  ✅ 拷贝构造器 / `copy()` 方法；不可变对象（record）无需拷贝。

## 🔗 相关条目

- 📄 **[字符串不可变语义](../language-concepts/07-string-immutability-pool.md)** — String 的 `==`/常量池专项
- 📄 **[注解详解](../language-concepts/09-annotations.md)** — 反射读取注解的完整流程
- 📄 **[异常体系与资源管理](../language-concepts/06-exceptions-resources.md)** — Throwable 体系与 try-with-resources
- 🌐 **[Object (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
