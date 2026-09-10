# 单元测试 - JUnit 5 与 Mockito

> **文档简介**: 用 JUnit 5 + Mockito 构建快速反馈的单元测试层：断言体系、参数化测试、Mock 与行为验证，让 Service 层业务逻辑被测试"锁"住
>
> **目标读者**: 需要为 Spring Boot 服务层编写单元测试的开发者
>
> **前置知识**: 已完成 [Spring Boot 入门](../frameworks/01-spring-boot-basics.md)；Lambda 基础见 [现代 Java 特性](../basics/07-modern-features.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#JUnit5` `#Mockito` `#TDD` `#单元测试` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：
- 用 JUnit 5 的 `@Test`/`@DisplayName`/断言体系写出可读的测试
- 用 `@ParameterizedTest` 消除重复用例
- 用 Mockito 隔离依赖、验证交互与打桩异常

## 🛠️ 一、JUnit 5 基础

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

@DisplayName("TodoService 业务规则")
class TodoServiceTest {

    @Test
    @DisplayName("标题去除首尾空白后创建")
    void shouldTrimTitleOnCreate() {
        // Arrange（准备）- Act（执行）- Assert（断言）
        TodoService service = new TodoService(new InMemoryTodoRepository());

        Todo todo = service.create("  学完 Java 21  ");

        assertEquals("学完 Java 21", todo.title(), "标题应被 strip");
        assertFalse(todo.done(), "新建 TODO 默认未完成");
    }

    @Test
    @DisplayName("操作不存在的 TODO 抛出业务异常")
    void shouldThrowWhenNotFound() {
        TodoService service = new TodoService(new InMemoryTodoRepository());

        var ex = assertThrows(TodoNotFoundException.class,
                () -> service.toggle(999L));

        assertEquals(999L, ex.getId());
    }
}
```

### 常用断言速查

| 断言 | 用途 |
|------|------|
| `assertEquals(expected, actual)` | 相等（浮点用 `assertEquals(0.3, a+b, 1e-9)` 容差） |
| `assertTrue` / `assertFalse` | 布尔条件 |
| `assertThrows(Class, Executable)` | 异常断言并返回异常对象 |
| `assertAll("组", () -> ..., () -> ...)` | 组合断言：全部执行，失败汇总 |
| `assertTimeout(Duration, Executable)` | 超时约束 |

## 🛠️ 二、参数化测试

```java
@ParameterizedTest
@CsvSource({
        "1, 1, 2",
        "0, 5, 5",
        "-1, 1, 0"
})
@DisplayName("加法表")
void addition(int a, int b, int expected) {
    assertEquals(expected, Calculator.add(a, b));
}

@ParameterizedTest
@ValueSource(strings = {"", "   ", "  \t "})
@DisplayName("空白标题全部拒绝")
void rejectBlankTitle(String title) {
    assertThrows(InvalidTitleException.class, () -> service.create(title));
}
```

## 🛠️ 三、Mockito 隔离依赖

### 打桩（Stub）

```java
@ExtendWith(MockitoExtension.class)   // 替代 MockitoAnnotations.openMocks
class CheckoutServiceTest {

    @Mock  InventoryRepository inventory;  // 生成 Mock 替身
    @Mock  OrderRepository orders;
    @InjectMocks CheckoutService service;  // 构造器自动注入 Mock

    @Test
    @DisplayName("库存不足时拒绝下单且不落库")
    void rejectWhenOutOfStock() {
        // given：让 findByIdForUpdate 返回无货商品
        Product outOfStock = new Product(42L, 0);
        given(inventory.findByIdForUpdate(42L)).willReturn(Optional.of(outOfStock));

        // when
        var ex = catchThrowableOfType(
                () -> service.checkout(1L, 42L, 1), IllegalStateException.class);

        // then
        assertThat(ex).isNotNull();
        then(orders).should(never()).save(any()); // 关键交互断言：绝不落库
    }
}
```

### 验证交互与参数捕获

```java
@Test
void verifyOrderSavedForCorrectUser() {
    given(inventory.findByIdForUpdate(1L))
            .willReturn(Optional.of(new Product(1L, 10)));

    service.checkout(7L, 1L, 2);

    var captor = ArgumentCaptor.forClass(Order.class);
    then(orders).should().save(captor.capture());   // 捕获真实传入对象

    assertEquals(7L, captor.getValue().getUserId()); // 断言关键属性
}
```

### 打桩异常路径

```java
given(payClient.call(any())).willThrow(new PaymentTimeoutException());
// 用于测试重试、降级与事务回滚分支
```

## 🎨 最佳实践

### ✅ 推荐
- 一测一意：方法名/`@DisplayName` 表达业务行为而非方法名
- 优先构造器手写依赖（简单对象），Mock 只用于"边界"（网络、时钟、随机）
- 用 `assertAll` 汇报全部失败，减少"改一个跑一次"

### ❌ 陷阱
- 测试断言 Mock 的调用次数却不断言结果：测试了实现而非行为
- Mock 具体实现类而非接口：脆弱且难维护
- 在 Spring 容器里跑纯逻辑单测：`@SpringBootTest` 拖慢反馈，仅限集成层

## 🚀 下一步

- 需要"真数据库/真中间件"时 → [集成测试](./02-integration-testing.md)
- 从 HTTP 进出验证整条链路 → [API 测试](./03-api-testing.md)

## 🔗 相关文档

### 本模块
- 📖 [Stream 与 Optional 速查](../reference/language-concepts/03-streams-optional.md) — 断言中的流式链
- 📖 [故障排除速查](../reference/quick-references/02-troubleshooting.md) — 测试常见报错
- 📄 [Spring Boot 入门](../frameworks/01-spring-boot-basics.md) — 被测代码的分层约定
- 📄 [TODO API 项目](../projects/01-todo-api.md) — 综合练习对象
- 📄 [集成测试](./02-integration-testing.md) — 下一篇：真实依赖验证
