# 控制流程 - 条件、循环与模式匹配

> **文档简介**: 复习条件与循环语法，掌握 switch 表达式的箭头语法与 yield，学会用 instanceof 与 switch 模式匹配替代冗长的类型判断
>
> **目标读者**: 写过旧版 switch/if-else 链、想升级到模式匹配写法的 Java 开发者
>
> **前置知识**: 已掌握[类、接口与 Record](./04-classes-records.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#控制流` `#switch表达式` `#模式匹配` `#instanceof` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：
- 用 switch 表达式（箭头语法、yield）替代旧 switch 语句
- 用 instanceof 模式匹配消除显式强转
- 用 switch 模式匹配 + 守卫条件处理多类型分发
- 理解 sealed 类带来的穷举检查价值

## 🔄 旧回顾：switch 语句的历史包袱

**旧写法**：

```java
switch (status) {
    case STATUS_NEW:
        System.out.println("新建");
        break;              // 忘写就穿透
    case STATUS_ACTIVE:
        System.out.println("有效");
        break;
    default:
        System.out.println("其他");
        break;
}
```

问题清单：fall-through 穿透事故、case 只能是常量、不能作为表达式赋值、编译器不检查穷举。

现代 Java 中 switch 从"语句"升级为"表达式"，以上问题逐一解决。

## 🔀 if 与 instanceof 模式匹配（Java 16+）

```java
// 旧写法：判断 + 强转分两步
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.length());
}

// 现代写法：模式变量直接可用
if (obj instanceof String s && s.length() > 0) {
    System.out.println(s.length());
}
```

模式变量作用域：只在**确认匹配成功**的范围内有效（如 `&&` 右侧、if 体内），编译器静态保证安全。

## 🎯 switch 表达式（Java 14+）

```java
enum Month { JAN, FEB, MAR, APR /* ... */ }

int days = switch (month) {
    case JAN, MAR, MAY, JUL, AUG, OCT, DEC -> 31;   // 多标签共用一个分支
    case APR, JUN, SEP, NOV -> 30;
    case FEB -> {
        int y = year();
        yield (y % 4 == 0 && y % 100 != 0) || y % 400 == 0 ? 29 : 28; // 复杂逻辑用 yield
    }
};
```

要点：

1. **箭头语法**：无穿透，一个分支要么是表达式、要么是 `yield` 块
2. **它是表达式**：整个 switch 可以直接赋值或返回
3. **必须穷举**：枚举与密封类型若未覆盖所有取值，编译报错
4. 穷举的枚举 switch **可以省略 default**——将来给枚举加新值时，所有 switch 会自动编译报错提醒你处理

## 🧩 switch 模式匹配（Java 21+）

```java
static String describe(Object obj) {
    return switch (obj) {
        case null                     -> "空值";            // 显式处理 null
        case Integer i when i > 0     -> "正整数: " + i;    // 类型模式 + 守卫 when
        case Integer i                -> "非正整数: " + i;
        case String s                 -> "字符串(" + s.length() + ")";
        case int[] arr                -> "int 数组，长度 " + arr.length;
        default                       -> "其他类型";
    };
}
```

- `case null` 可与类型模式合并：`case null, String s -> ...`
- 守卫条件用 `when`，只做布尔判断，别塞业务逻辑
- 分支按书写顺序匹配，**子类型要写在父类型前面**，否则编译器报"支配错误"（dominance）
- Java 25 中基本类型模式仍处于预览阶段（JEP 507），生产慎用

### 与 sealed 类配合：编译器保证穷举

```java
public sealed interface Shape permits Circle, Rectangle {}
public record Circle(double radius) implements Shape {}
public record Rectangle(double w, double h) implements Shape {}

static double area(Shape shape) {
    return switch (shape) {          // 无 default！
        case Circle c    -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.w() * r.h();
    };  // 少写一个子类型，这里直接编译错误
}
```

将来新增 `Triangle` 子类时，所有遗漏它的 switch 都会在编译期报错——这是旧版"default 兜底"永远给不了的安全感。

## 🔁 循环要点复习

```java
for (var entry : map.entrySet()) { ... }   // 增强 for 可用 var

for (var _ : data) { count++; }            // Java 22+：未命名变量 _，明确"不用这个元素"
```

- `while`/`do-while` 语义未变；标签 break/continue 少用，复杂跳转优先提取方法
- 集合遍历+过滤/变换优先考虑 Stream（见[现代特性](./07-modern-features.md)），普通迭代保留增强 for 即可

## ✅ 最佳实践

- ✅ 多分支值映射优先 switch 表达式，而非 if-else 链
- ✅ 枚举/密封类型 switch 省略 default，让编译器检查穷举
- ✅ null 值显式 `case null`，不要依赖 default 隐式吞掉
- ❌ 避免 `when` 守卫中写副作用与复杂业务逻辑
- ❌ 避免用 switch 模式匹配替代多态——先考虑虚方法

## 🎯 练习与实践

### 练习一：旧代码升级
1. 找一段旧 switch 语句，改写为 switch 表达式
2. 给一个枚举新增取值，观察省略 default 的 switch 如何报错

### 练习二：类型分发
1. 构造 `List<Object>`，用 switch 模式匹配统计各类型数量

### 练习三：穷举实验
1. 实现 sealed Shape 三兄弟（加 Triangle），故意漏掉一个子类看编译错误

## 🔗 相关文档

- 📄 **[异常处理](./06-exceptions.md)** - 下一站：现代异常设计
- 📄 **[Record/Sealed/模式匹配](../reference/language-concepts/05-records-sealed-patterns.md)** - 模式匹配完整语法
- 📄 **[Java 关键字详解](../reference/language-concepts/01-java-keywords.md)** - switch/yield/when 条目
