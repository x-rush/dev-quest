# 注解详解

> **文档简介**: 注解机制全景——内置注解、元注解（@Retention/@Target/@Inherited/@Repeatable）、自定义注解定义、注解的两种处理时机（编译期处理器 vs 运行时反射），以及与 Spring 等框架注解的关系
>
> **目标读者**: 需要读懂并自定义注解、理解框架注解背后发生了什么的开发者
>
> **前置知识**: 反射基础见 [java.lang 导览](../library-guides/03-java-lang.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#注解` `#Annotation` `#反射` `#语言概念` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

注解（`@interface`）是挂在包/类/方法/字段等声明上的**元数据标记**，本身不执行任何行为——它的价值完全来自**读取它的工具**：编译器检查（`@Override`）、编译期注解处理器（Lombok/MapStruct）、运行时反射（JUnit/Spring）。

> 示例给出预期行为与规范依据。本轮环境未提供 Java 编译器，未复现历史运行记录；请在项目约定 JDK 上编译验证。

## 📖 语法 / 签名

### 内置注解

| 注解 | 用途 | 要点 |
|------|------|------|
| `@Override` | 声明重写父方法 | 编译器强制校验签名；SOURCE 保留（反射读不到，预期） |
| `@Deprecated(since, forRemoval)` | 标记废弃 | `forRemoval=true` 表示未来会删，IDE/静态工具分级告警 |
| `@FunctionalInterface` | 声明函数式接口 | 强制编译器校验"只有一个抽象方法"，非必需但强烈推荐 |
| `@SuppressWarnings("...")` | 压制告警 | 值如 `"unchecked"` `"deprecation"`，范围尽量小 |
| `@SafeVarargs` | 断言泛型可变参数安全 | 仅可用于 static/private/final 方法与构造器 |

### 元注解（贴在注解定义上的注解）

| 元注解 | 作用 | 语义要点 |
|--------|------|---------|
| `@Retention` | 保留策略：`SOURCE`（仅源码）/ `CLASS`（默认，到 class 文件）/ `RUNTIME`（反射可见） | 未标注时**默认 CLASS**——运行时反射读不到（预期） |
| `@Target` | 可标注位置：`TYPE`/`METHOD`/`FIELD`/`PARAMETER`/`PACKAGE`/`TYPE_PARAMETER` 等 | 贴错位置编译报错 |
| `@Inherited` | 子类反射读取父类的**类级**注解 | 只对类有效；接口方法/字段注解不继承（预期） |
| `@Repeatable` | 允许同一位置重复标注 | 需指定容器注解；读取用 `getAnnotationsByType` |
| `@Documented` | 进入 javadoc | 文档类注解标配 |

### 自定义注解定义

```java
import java.lang.annotation.*;

@Retention(RetentionPolicy.RUNTIME)      // 运行时反射要读 → 必须 RUNTIME
@Target(ElementType.METHOD)
@Repeatable(Tags.class)                  // 允许重复
public @interface Tag {
    String value();                      // 属性名 value，使用时可省略 "value ="
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Tags {                 // 容器注解，持有 Tag 数组
    Tag[] value();
}
```

属性类型只能是：基本类型、`String`、`Class`、枚举、注解类型，以及它们的一维数组（JLS 9.6.1）。属性可用 `default` 给默认值。

## 💡 示例

```java
import java.lang.annotation.*;
import java.lang.reflect.Method;

public class AnnotationDemo {
    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.TYPE)
    @Inherited
    @interface Marker { String value() default ""; }

    @Marker("base-marker")
    static class Base {}
    static class Child extends Base {}          // 未自己标注

    @Tag("fast") @Tag("cache")                  // 同一位置重复标注
    void run() {}

    public static void main(String[] args) throws Exception {
        // @Inherited：子类反射可读到父类注解（预期）
        Marker m = Child.class.getAnnotation(Marker.class);
        System.out.println(m.value());           // base-marker
        // Child.class.getDeclaredAnnotation(Marker.class) 则为 null（只查自身）

        // 可重复注解：必须用 getAnnotationsByType（预期）
        Method run = AnnotationDemo.class.getDeclaredMethod("run");
        for (Tag tag : run.getAnnotationsByType(Tag.class)) {
            System.out.println(tag.value());     // fast / cache
        }
        // run.getAnnotation(Tag.class) 在多个重复注解存在时返回 null（预期行为）
    }
}
```

### 两种处理时机

| 时机 | 机制 | 代表 |
|------|------|------|
| **编译期** | 注解处理器（`javax.annotation.processing`，javac 钩子），按标准处理器 API 生成新源码或资源；Lombok 修改编译器内部树属于额外机制 | Lombok、MapStruct |
| **运行时** | 反射读取 RUNTIME 保留的注解，据此驱动逻辑 | JUnit `@Test`、Spring `@Component`/`@Autowired` |

框架可以通过类路径元数据扫描、反射或 AOT 生成结果读取注解（如 Spring 的 @Component）——你定义的注解与框架注解在机制上完全同级。

## ⚠️ 常见陷阱

- ❌ **自定义注解忘了写 `@Retention(RUNTIME)`**：默认 CLASS 保留，运行时反射永远读不到（预期：未标注时 `getAnnotation(Retention.class)` 为 null，标注过的类运行时不可见）。
  ✅ 需要反射读取的注解一律显式 `@Retention(RetentionPolicy.RUNTIME)`。
- ❌ **用 `getAnnotation(Tag.class)` 读可重复注解**：多个存在时返回 null（预期）。
  ✅ 统一用 `getAnnotationsByType(Tag.class)`。
- ❌ **指望 `@Inherited` 继承方法/接口上的注解**：它只作用于类继承链的类级注解。
  ✅ 方法注解需自己沿父类/接口向上查找（Spring 的 `AnnotatedElementUtils` 已封装）。
- ❌ **删掉 `@Override` 让编译器"闭嘴"**：失去重写签名校验，拼错方法名变成新增方法。
  ✅ 所有重写都保留 `@Override`。
- ❌ **注解里放"任意类型"属性**：类型受限（见上），放不了任意对象。
  ✅ 复杂数据用 `Class` 引用 + `String`/数组组合。

<!-- full-library-explanation -->
## 注解要有读取者才会产生效果

给方法贴上自定义 @Retry 不会自动重试。需要先决定谁读取它：编译期处理器生成代码，还是运行时框架检查并包装调用。Retention 决定信息保留到哪个阶段；Target 决定可以贴在哪里。二者不决定业务语义。

本页 Tag 与 Tags 是两个 public 顶层注解，保存时分别放进 Tag.java、Tags.java，再与 AnnotationDemo.java 一起编译。将 Tag 的保留策略改成 CLASS 后，运行时 getAnnotationsByType 无法读到该标记；这不表示 class 文件中完全没有注解信息。

**练习**：保留上文 Base 和 Child，同时比较 getAnnotation 与 getDeclaredAnnotation 的结果。预期前者可沿受 @Inherited 支持的类继承关系查找，后者只看本类。再把标记放到接口上，解释为什么 @Inherited 不会自动把接口标记传给实现类。框架可能提供更广的合并查找，这是框架规则，不能当作 Java 反射的默认行为。

## 🔗 相关条目

- 📄 **[接口语义](./10-interface-semantics.md)** — `@FunctionalInterface` 与 SAM 判定
- 📄 **[java.lang 导览](../library-guides/03-java-lang.md)** — Class/Method 反射 API 基础
- 📄 **[IoC/DI 要点](../framework-essentials/03-ioc-di-essentials.md)** — Spring 注解驱动的容器机制
- 🌐 **[java.lang.annotation (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/annotation/package-summary.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
