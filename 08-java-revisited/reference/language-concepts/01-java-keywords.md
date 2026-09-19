# Java 关键字：完整分类、语义边界与运行实验

本篇用于查阅语法，不要求先学 Spring。先掌握变量、方法、类，再按“流程 → 对象 → 异常 → 现代语法 → 并发”阅读。示例全部是独立的 `Main.java`，运行 `javac --release 21 -encoding UTF-8 Main.java`，再运行 `java Main`；不需要 Maven 或外部依赖。

词表依据 Java SE 25 语言规范核对；可运行示例采用本模块默认的 Java 21，未启用预览特性。Java 22/25 扩展单独说明，不能直接复制到 Java 21 工程。

## 1. 先分清关键词、字面量和库类型

`class` 决定程序语法；`String` 是 `java.lang` 中的类；`List` 是集合接口；`true`、`false`、`null` 是字面量。Java 没有 Python 那样一组全局内置函数：输出 `System.out.println`、排序 `Arrays.sort` 都是库方法，见[标准库参考](../library-guides/01-standard-library.md)。

### 51 个保留关键字

以下分组互不重复，合计 51 个。`const` 和 `goto` 没有可用语法；单独的 `_` 也是保留关键字，不是普通变量名。

| 分类 | 关键字 | 阅读时要回答的问题 |
|---|---|---|
| 原始类型 | `boolean byte short int long char float double` | 值的范围、精度和表示方式是什么？`char` 是 UTF-16 代码单元，不是任意完整 Unicode 字符 |
| 类型声明 | `class interface enum extends implements` | 声明类、接口或枚举；继承实现关系是什么？ |
| 访问权限 | `public protected private` | 谁可以使用成员？没有修饰符是包访问，不等于 `public` |
| 对象与成员 | `new this super static final abstract` | 创建实例、引用实例/父类、类级成员、禁止重赋值/继承、留待子类实现 |
| 分支循环 | `if else switch case default for while do break continue` | 哪条路径执行？终止整个循环还是跳过本轮？ |
| 方法与类型判断 | `return void instanceof` | 是否返回值？对象是否匹配类型？ |
| 异常与断言 | `try catch finally throw throws assert` | 谁抛出、谁处理、谁负责清理？ |
| 包与导入 | `package import` | 类型属于哪个命名空间？短名称如何解析？ |
| 并发 | `synchronized volatile` | 哪个锁保护哪些读写？是否有复合操作？ |
| 特殊修饰符 | `transient native strictfp` | 默认对象序列化、本地方法、历史浮点语义 |
| 保留或特殊声明 | `const goto _` | 前两者不能使用；`_` 的未命名变量/模式用法在 Java 22 成为正式特性 |

### 17 个上下文关键字

| 分组 | 词 | 语义 |
|---|---|---|
| 模块 | `module open requires transitive exports opens to uses provides with` | 声明模块依赖、API 导出、反射开放和服务发现 |
| 类型与模式 | `record sealed permits non-sealed when` | 数据载体、限定继承集合、模式守卫 |
| 局部语法 | `var yield` | 局部类型推断、`switch` 表达式分支结果 |

“上下文”不代表任何位置都能当名字：`var`、`record`、`sealed`、`permits`、`yield` 不能作类型名；名为 `yield` 的方法不能无接收者调用。`open` 与 `opens` 不同，前者开放整个模块，后者开放指定包的反射访问。Java 25 还允许 `import module`；不要把所有这些词的用途永久限定为 `module-info.java`。分类与限制见 [JLS §3.8–3.9](https://docs.oracle.com/javase/specs/jls/se25/html/jls-3.html#jls-3.9)。

## 2. 分支、循环和返回：先跟踪执行顺序

`continue` 跳过本轮后续语句，`break` 退出循环或 `switch`，`return` 离开整个方法。`do` 至少执行一次循环体；`while` 可能一次也不执行。传统冒号形式的 `switch` 可以穿透，箭头形式不会穿透。

下面先过滤负数，再在遇到 10 时停止。`switch` 是表达式，分支代码块用 `yield` 产生值；此处用 `return` 会尝试离开方法，不能代替 `yield`。

<!-- reference-case: {"id":"java-flow","stdout":"5\nmedium\n"} -->
```java
public class Main {
    public static void main(String[] args) {
        int total = 0;
        for (int value : new int[]{2, -1, 3, 10, 4}) {
            if (value < 0) continue;
            if (value == 10) break;
            total += value;
        }
        String label = switch (total) {
            case 0 -> "empty";
            case 5 -> {
                String size = "medium";
                yield size;
            }
            default -> "other";
        };
        System.out.println(total);
        System.out.println(label);
    }
}
```

输出依次为 `5`、`medium`。练习：删除 `break` 那行，结果应为 `19`、`other`；解释为什么负数没有相加。不要仅背诵三个跳转词的中文名称。

## 3. final、static、record：引用不变与对象不变

`final` 变量只能赋值一次，不能阻止引用对象内部改变；`final` 方法禁止重写，`final` 类禁止继承。`static` 成员属于类，不依赖某个实例；静态方法没有 `this`，但可通过一个明确的对象引用访问其实例成员。静态可变字段也不会自动线程安全。

`record` 自动提供组件访问器、规范构造器、`equals`、`hashCode` 和 `toString`，组件对应的字段是 `private final`。它保证组件引用不能重新绑定，不会递归冻结对象。对外部可变集合建立快照是构造器的责任。

预期输出两行：`[Ada, Lin]`、`[Ada]`。

<!-- reference-case: {"id":"java-record","stdout":"[Ada, Lin]\n[Ada]\n"} -->
```java
import java.util.ArrayList;
import java.util.List;

public class Main {
    record Team(List<String> names) {
        Team {
            names = List.copyOf(names);
        }
    }

    public static void main(String[] args) {
        final var source = new ArrayList<>(List.of("Ada"));
        Team team = new Team(source);
        source.add("Lin");
        System.out.println(source);
        System.out.println(team.names());
    }
}
```

`source.add` 合法，重新给 `source` 赋值不合法。`List.copyOf` 不复制元素对象；此例元素为不可变的 `String`，若元素是可变 `Person`，仍需设计其修改边界。删除构造器中的复制，第二行也会变为 `[Ada, Lin]`。

`var` 推断的是静态类型，此例为 `ArrayList<String>`；它不是动态类型。不能写 `var value = null`、不能声明 `var` 字段或方法返回类型。Lambda 参数允许统一使用 `var`（Java 11 起），但它们的类型由目标函数式接口确定，而非初始化表达式。

`transient` 影响普通类字段的默认 Java 对象序列化；**record 组件不能声明为 transient**，也不能据此保证 JSON 字段被忽略。JSON 序列化是所选库的另一个契约。参见 [JLS record 定义](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.10)。

## 4. 类型、继承和模式：把可能性写进接口

普通类只能 `extends` 一个类，可以 `implements` 多个接口。`abstract` 类不能直接实例化，可提供部分实现；接口描述可实现的契约，`default` 方法可以携带默认实现。`sealed` 限定直接子类型，使编译器能检查某些模式分支是否穷尽。

预期输出三行：`positive:3`、`non-positive`、`missing`。

<!-- reference-case: {"id":"java-patterns","stdout":"positive:3\nnon-positive\nmissing\n"} -->
```java
public class Main {
    sealed interface Result permits Found, Missing {}
    record Found(int value) implements Result {}
    record Missing() implements Result {}

    static String describe(Result result) {
        return switch (result) {
            case Found f when f.value() > 0 -> "positive:" + f.value();
            case Found f -> "non-positive";
            case Missing m -> "missing";
        };
    }

    public static void main(String[] args) {
        System.out.println(describe(new Found(3)));
        System.out.println(describe(new Found(0)));
        System.out.println(describe(new Missing()));
    }
}
```

具体守卫要放在通用 `Found` 分支前；`when` 只判断已匹配的模式，不单独声明类型。传入 `null` 仍会抛 `NullPointerException`：穷尽非空子类型并不等于处理了空引用，需要时显式加 `case null`。

许可子类型必须与父类型同属一个具名模块；处于未命名模块时必须同包。直接子类选择 `final`、`sealed` 或 `non-sealed`；record 隐式为 final。`non-sealed` 意味着重新开放这一支的继承，并不是“取消父类限制”。

`instanceof` 对 `null` 返回 false；使用模式变量时，变量只在编译器能证明匹配成功的区域可用，例如 `obj instanceof String text && !text.isBlank()` 的右侧。详细学习见 [Record、Sealed 与模式匹配](./05-records-sealed-patterns.md)。

## 5. 异常与资源：throw、throws 和 finally 不可互换

`throw` 真正抛出异常对象，`throws` 声明方法可能传播的受检异常，`catch` 决定如何处理。没有恢复策略时应传播或补充上下文，不能空 catch 后继续当作成功。`finally` 用于离开 try/catch 时的清理；JVM 被终止等情况不能保证执行，且在 finally 中 return 会覆盖原返回值或异常。

预期输出三行：`work`、`closed`、`failed`。

<!-- reference-case: {"id":"java-resource","stdout":"work\nclosed\nfailed\n"} -->
```java
public class Main {
    static class Resource implements AutoCloseable {
        @Override public void close() {
            System.out.println("closed");
        }
    }

    static void work() throws java.io.IOException {
        try (Resource resource = new Resource()) {
            System.out.println("work");
            throw new java.io.IOException("failed");
        }
    }

    public static void main(String[] args) {
        try {
            work();
        } catch (java.io.IOException exception) {
            System.out.println(exception.getMessage());
        }
    }
}
```

资源会先关闭，再进入调用方的 catch。若工作和 close 同时抛异常，关闭异常通常作为 suppressed exception 附在主要异常上。练习：将资源声明两个，观察它们按声明的反序关闭。

`assert` 默认不启用；`java -ea Main` 才打开普通应用断言。用户输入校验必须使用明确条件和异常，不能依赖运行参数是否启用断言。

## 6. 并发词：承诺必须对应具体读写

`synchronized` 对**同一个监视器**互斥，并提供锁释放到后续获取之间的可见性。实例同步方法锁住 `this`，静态同步方法锁住对应 `Class` 对象，二者不是同一把锁。

`volatile` 的单次读写具有内存可见性与相应的排序保证；“禁止所有指令重排”并不准确。`count++` 包含读取、计算、写入，即使 count 是 volatile，多线程仍可能丢失更新。对计数使用合适的原子类；多字段业务不变式使用同一锁或其他整体协调机制。进一步见[并发 API](./04-concurrency-api.md)。

## 7. 低频词与版本扩展

| 词/用法 | 应掌握的边界 |
|---|---|
| `this` / `super` | `this` 是当前对象；`super` 选择父类构造器或成员。Java 21 显式构造器调用须在构造器体首条；Java 25 的灵活构造器体允许受限制的前置语句，不是任意访问未初始化的 this |
| `native` | 声明由本地实现的方法，不能把普通 Java 方法体一起写上；本地调用还有独立资源与线程边界 |
| `strictfp` | Java 17 起浮点运算恢复始终严格的语义，新代码无需添加此历史修饰符 |
| `_` | Java 9 起是关键字。Java 22 的未命名声明用于“有值但不引用它”，不是可以读取的变量；Java 21 本篇不使用其预览语法 |
| `package` / `import` | import 只简化名称解析，不复制代码、不自动下载依赖；`java.lang` 类型通常自动可见，其子包不会随之导入 |

## 8. 验收与下一步

四个完整程序应输出上方标记中对应的结果。学习验收还包括：能区分 final 引用与不可变元素；能解释 null 为什么不被密封子类型穷尽自动覆盖；能指出哪个 catch 处理异常，以及资源何时关闭；能说出 volatile 为什么不足以保护自增。

接着读[集合与泛型](./02-collections-generics.md)、[标准库](../library-guides/01-standard-library.md)，最后回到[第一个项目](../../basics/08-first-project.md)使用这些规则。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
