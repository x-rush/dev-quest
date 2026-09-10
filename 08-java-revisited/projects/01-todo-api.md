# 项目实战 01 - TODO REST API（入门）

> **文档简介**: 从零构建一个完整可运行的 TODO REST API：单表 CRUD + 参数校验 + 全局异常处理 + 单元测试，是本模块第一个"端到端能跑"的项目
>
> **目标读者**: 刚学完 Spring Boot 入门、需要综合演练的入门者
>
> **前置知识**: 已完成 [Spring Boot 入门](../frameworks/01-spring-boot-basics.md) 与 [第一个项目](../basics/08-first-project.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#REST` `#CRUD` `#参数校验` `#入门项目` |
| **更新日期** | `2026年9月` |

## 🎯 项目目标

- 功能：TODO 的增删改查、完成状态切换、按状态过滤
- 技术栈：Java 21 + Spring Boot 3.x + Spring Web + Validation（先用内存存储，专注分层）
- 产出：可 `curl` 全流程验证的 API + 一套单元测试

## 🏗️ 一、需求与接口设计

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/todos?done=` | 列表，可按完成状态过滤 |
| `POST` | `/api/todos` | 新建，校验标题非空 |
| `GET` | `/api/todos/{id}` | 详情，404 语义 |
| `PUT` | `/api/todos/{id}` | 更新标题 |
| `PATCH` | `/api/todos/{id}/toggle` | 切换完成状态 |
| `DELETE` | `/api/todos/{id}` | 删除，204 |

## 🛠️ 二、分层实现

### 2.1 领域模型（Record 表达不可变视图）

```java
// 领域对象：用 record 表达"创建请求"与"响应视图"
public record Todo(Long id, String title, boolean done,
                   Instant createdAt) {
    public Todo {
        Objects.requireNonNull(title); // 紧凑构造器兜底校验
    }

    public Todo toggle() {
        return new Todo(id, title, !done, createdAt); // 返回新实例
    }
}
```

> Record 的语义与模式匹配详见 [Record / Sealed / 模式匹配速查](../reference/language-concepts/05-records-sealed-patterns.md)。

### 2.2 存储层（内存版，接口先行）

```java
// 先定义接口：后续换 JPA 实现时上层零改动
public interface TodoRepository {
    Todo save(Todo todo);
    Optional<Todo> findById(Long id);
    List<Todo> findAll();
    void deleteById(Long id);
}

@Repository
public class InMemoryTodoRepository implements TodoRepository {

    private final Map<Long, Todo> store = new ConcurrentHashMap<>();
    private final AtomicLong seq = new AtomicLong();

    @Override
    public Todo save(Todo todo) {
        if (todo.id() == null) {
            var created = new Todo(seq.incrementAndGet(),
                    todo.title(), todo.done(), Instant.now());
            store.put(created.id(), created);
            return created;
        }
        store.put(todo.id(), todo);
        return todo;
    }
    // 其余方法省略
}
```

### 2.3 服务层（业务规则集中地）

```java
@Service
public class TodoService {

    private final TodoRepository repo;

    public TodoService(TodoRepository repo) { this.repo = repo; }

    public Todo create(String title) {
        return repo.save(new Todo(null, title.strip(), false, Instant.now()));
    }

    public Todo toggle(Long id) {
        return repo.findById(id)
                .map(Todo::toggle)
                .map(repo::save)
                .orElseThrow(() -> new TodoNotFoundException(id));
    }
}
```

### 2.4 Web 层与全局异常

```java
@RestController
@RequestMapping("/api/todos")
public class TodoController {

    private final TodoService service;
    public TodoController(TodoService service) { this.service = service; }

    public record CreateTodoRequest(
            @NotBlank(message = "标题不能为空") @Size(max = 100) String title) {}

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Todo create(@RequestBody @Valid CreateTodoRequest req) {
        return service.create(req.title());
    }

    @GetMapping("/{id}")
    public Todo get(@PathVariable Long id) { return service.get(id); }
}

@RestControllerAdvice
class TodoExceptionHandler {

    @ExceptionHandler(TodoNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)   // 404：资源不存在
    public Map<String, Object> notFound(TodoNotFoundException e) {
        return Map.of("error", "TODO_NOT_FOUND", "id", e.getId());
    }
}
```

## 🧪 三、验证

```bash
# 新建
curl -X POST localhost:8080/api/todos \
  -H 'Content-Type: application/json' -d '{"title": "学完 Java 21"}'

# 切换状态 → 详情 → 删除（期望 204）
curl -X PATCH localhost:8080/api/todos/1/toggle
curl localhost:8080/api/todos/1
curl -X DELETE -i localhost:8080/api/todos/1
```

再为 `TodoService` 写一组单元测试（方法见 [单元测试](../testing/01-unit-testing.md)），覆盖"找不到时抛 404"分支。

## 🎨 最佳实践

### ✅ 推荐
- Repository 定义成接口：本项目第二版换 JPA 时上层无感
- 状态码语义化：201 创建 / 204 删除 / 404 不存在
- 校验注解放在请求 DTO 上，服务层只做业务校验

### ❌ 陷阱
- Controller 里写业务规则（本项目所有规则都在 Service）
- 直接返回内部实现类，破坏封装
- 忘记处理 `id` 不存在场景，返回 500 而非 404

## 🚀 下一步

- 数据落到真实数据库 → [图书管理系统](./02-library-management.md)（JPA + 认证）
- 为本项目补充接口级测试 → [MockMvc 与 REST Assured](../testing/03-api-testing.md)

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — 注解与配置条目
- 📖 [Stream 与 Optional 速查](../reference/language-concepts/03-streams-optional.md) — `map`/`orElseThrow` 链式用法
- 📄 [Spring Boot 入门](../frameworks/01-spring-boot-basics.md) — 依赖注入与 Controller 基础
- 📄 [单元测试](../testing/01-unit-testing.md) — 给本项目补测试
- 📄 [图书管理系统](./02-library-management.md) — 下一篇：接入真实数据库
