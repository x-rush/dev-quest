# 项目实战 01：能逐步验收的 TODO REST API

## 分阶段练习与验收

**最小阶段**：先完成创建、查询与非法输入处理，再补更新删除。

**验收结果**：每个声明的接口都有实现与可执行验收，重启清空内存的限制明确。

**扩展顺序**：先运行单元和 HTTP 检查，再提取仓库接口和数据库实现。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> 前置：[Spring Boot 入门](../frameworks/01-spring-boot-basics.md)、Java record、集合与异常。适用：Java 21、Spring Boot 4.x 的 Spring Web MVC 与 Validation。项目层级：入门。

## 本次只做什么

做一个内存待办服务：创建、列表、详情、改标题、设完成状态与删除。进程重启后数据清空，不包含登录、数据库和部署。先证明 HTTP、校验、业务和存储能连起来，再在[下一项目](./02-library-management.md)替换存储。

旧版此处省略了仓库方法和若干接口，却声称可以完整运行。本版给出全部必要类、导入、文件位置与调用步骤。当前文档增强环境没有 JDK，本轮未执行本工程；下面的启动、编译与行为验收是读者和后续 CI 需要执行的检查，不冒充已通过结果。

## 1. 创建工程

使用 [Spring Initializr](https://start.spring.io) 创建 Maven / Java / Jar 工程，Java 选择 21，Spring Boot 选择与[模块基线](../README.md)相符的稳定 4.x，加入 Spring Web 与 Validation。Group 为 `example`，Artifact 为 `todo`，Package name 为 `example.todo`。保留生成的 Maven Wrapper 与 pom.xml，并记录具体版本。

解压到独立练习目录。在 `src/main/java/example/todo/TodoApplication.java` 放下方完整文件，替换模板同名类，不保留两个启动类。先使用一个文件中的嵌套类型降低文件跳转；职责已经分开，练习末尾再拆文件。

## 2. 完整实现

```java
package example.todo;

import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.UnaryOperator;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;

@SpringBootApplication
public class TodoApplication {
    public static void main(String[] args) {
        SpringApplication.run(TodoApplication.class, args);
    }

    public record Todo(long id, String title, boolean done, Instant createdAt) {}
    public record TitleRequest(@NotBlank @Size(max = 100) String title) {}
    public record DoneRequest(@NotNull Boolean done) {}

    public static final class NotFound extends RuntimeException {
        private final long id;
        public NotFound(long id) {
            super("Todo not found: " + id);
            this.id = id;
        }
        public long id() { return id; }
    }

    @Service
    public static class TodoService {
        private final ConcurrentHashMap<Long, Todo> rows = new ConcurrentHashMap<>();
        private final AtomicLong sequence = new AtomicLong();

        private String normalizedTitle(String title) {
            if (title == null || title.isBlank() || title.length() > 100) {
                throw new IllegalArgumentException("标题需为 1 到 100 字符的非空白文本");
            }
            return title.strip();
        }

        public Todo create(String title) {
            String normalized = normalizedTitle(title);
            long id = sequence.incrementAndGet();
            Todo todo = new Todo(id, normalized, false, Instant.now());
            rows.put(id, todo);
            return todo;
        }

        public List<Todo> list(Boolean done) {
            return rows.values().stream()
                    .filter(todo -> done == null || todo.done() == done)
                    .sorted(Comparator.comparingLong(Todo::id))
                    .toList();
        }

        public Todo get(long id) {
            Todo todo = rows.get(id);
            if (todo == null) throw new NotFound(id);
            return todo;
        }

        private Todo update(long id, UnaryOperator<Todo> operation) {
            return rows.compute(id, (key, old) -> {
                if (old == null) throw new NotFound(id);
                return operation.apply(old);
            });
        }

        public Todo rename(long id, String title) {
            String normalized = normalizedTitle(title);
            return update(id, old -> new Todo(id, normalized, old.done(), old.createdAt()));
        }

        public Todo setDone(long id, boolean done) {
            return update(id, old -> new Todo(id, old.title(), done, old.createdAt()));
        }

        public void delete(long id) {
            if (rows.remove(id) == null) throw new NotFound(id);
        }
    }

    @RestController
    @RequestMapping("/api/todos")
    public static class TodoController {
        private final TodoService service;
        public TodoController(TodoService service) { this.service = service; }

        @GetMapping
        public List<Todo> list(@RequestParam(name = "done", required = false) Boolean done) {
            return service.list(done);
        }

        @PostMapping
        @ResponseStatus(HttpStatus.CREATED)
        public Todo create(@RequestBody @Valid TitleRequest request) {
            return service.create(request.title());
        }

        @GetMapping("/{id}")
        public Todo get(@PathVariable("id") long id) { return service.get(id); }

        @PutMapping("/{id}/title")
        public Todo rename(@PathVariable("id") long id, @RequestBody @Valid TitleRequest request) {
            return service.rename(id, request.title());
        }

        @PutMapping("/{id}/done")
        public Todo setDone(@PathVariable("id") long id, @RequestBody @Valid DoneRequest request) {
            return service.setDone(id, request.done());
        }

        @DeleteMapping("/{id}")
        @ResponseStatus(HttpStatus.NO_CONTENT)
        public void delete(@PathVariable("id") long id) { service.delete(id); }
    }

    @RestControllerAdvice
    public static class ErrorHandler {
        @ExceptionHandler(NotFound.class)
        @ResponseStatus(HttpStatus.NOT_FOUND)
        public Map<String, Object> notFound(NotFound error) {
            return Map.of("error", "TODO_NOT_FOUND", "id", error.id());
        }

        @ExceptionHandler(IllegalArgumentException.class)
        @ResponseStatus(HttpStatus.BAD_REQUEST)
        public Map<String, String> invalid(IllegalArgumentException error) {
            return Map.of("error", "INVALID_TITLE", "message", error.getMessage());
        }
    }
}
```

## 3. 为什么这样分工

请求 JSON 先由框架转成请求 record，`@Valid` 执行输入约束；Controller 将有效输入交给 Service。Service 仍验证标题，因为它也可能被命令行或测试直接调用。业务对象不携带 HTTP 状态码，ErrorHandler 在 HTTP 边界把 NotFound 映射成 404。

ConcurrentHashMap 保护单次映射操作；“读取后修改再写回”并不会因为使用并发容器就自动成为原子操作，因此本例用 compute 处理同一 ID 的更新。列表是弱一致视图，不提供跨记录事务快照。

设置 done=true 使用明确目标状态，而不使用“每次反转”。同一设置重复两次仍是完成状态，较容易理解幂等；这不意味着 POST 创建也自动幂等。时间与 ID 会随执行变化，不用硬编码 createdAt 作为断言。

## 4. 启动与手工验收

在包含 pom.xml 的工程根目录运行。Windows PowerShell：

```powershell
.\mvnw.cmd test
.\mvnw.cmd spring-boot:run
```

macOS/Linux 使用 `./mvnw test` 与 `./mvnw spring-boot:run`。服务默认在 8080，另开终端请求。PowerShell 用下列完整流程，避免把 Bash 的反斜杠续行复制到 PowerShell：

```powershell
$todoBase = 'http://localhost:8080/api/todos'
$todoCreated = Invoke-RestMethod -Method Post -Uri $todoBase -ContentType 'application/json' -Body '{"title":"Read a chapter"}'
$todoId = $todoCreated.id
Invoke-RestMethod -Uri "$todoBase/$todoId"
Invoke-RestMethod -Method Put -Uri "$todoBase/$todoId/done" -ContentType 'application/json' -Body '{"done":true}'
Invoke-RestMethod -Uri "${todoBase}?done=true"
Invoke-WebRequest -Method Delete -Uri "$todoBase/$todoId"
```

| 验收动作 | 预期 | 未满足时先查 |
|---|---|---|
| 创建正常标题 | 201，返回 id/title/done=false/createdAt | 路由、请求 JSON 与 Content-Type |
| 空白或缺少标题 | 400，不新增记录 | Validation 依赖与 @Valid |
| 查询不存在 ID | 404，error=TODO_NOT_FOUND | 异常映射 |
| 两次设置 done=true | 两次都保持 true | 是否错误实现为 toggle |
| 按 done=true 查询 | 只返回已完成项，按 ID 排序 | 筛选条件 |
| 删除已存在项 | 204，无响应正文 | 状态码注解 |
| 删除后再查 | 404 | 是否真的移除 |
| 停服重启后查原 ID | 404 | 本例只有进程内存，没有数据库 |

PowerShell 默认对非成功 HTTP 状态抛出异常，这是客户端工具对 400/404 的表现。可用 try/catch 查看响应状态；不要因终端显示红字就判定服务崩溃。

## 5. 业务测试：正常路径和失败路径一起验证

放在 `src/test/java/example/todo/TodoServiceTest.java`。Initializr 生成的测试依赖提供 JUnit Jupiter；保留该依赖。执行 Maven test。

```java
package example.todo;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class TodoServiceTest {
    @Test
    void createCompleteAndDelete() {
        var service = new TodoApplication.TodoService();
        var todo = service.create("  Learn Java  ");
        assertEquals("Learn Java", todo.title());
        assertFalse(todo.done());
        assertTrue(service.setDone(todo.id(), true).done());
        assertTrue(service.setDone(todo.id(), true).done());
        assertEquals(1, service.list(true).size());
        service.delete(todo.id());
        assertThrows(TodoApplication.NotFound.class, () -> service.get(todo.id()));
    }

    @Test
    void rejectsInvalidInputWithoutCreatingData() {
        var service = new TodoApplication.TodoService();
        assertThrows(IllegalArgumentException.class, () -> service.create("   "));
        assertThrows(IllegalArgumentException.class, () -> service.create(null));
        assertTrue(service.list(null).isEmpty());
        assertThrows(TodoApplication.NotFound.class, () -> service.setDone(99, true));
    }
}
```

这些单元测试没有启动 HTTP，不能证明 JSON 绑定、Validation 或状态码配置正确；还需执行上一节 HTTP 验收，并可继续做[接口测试](../testing/03-api-testing.md)。

## 6. 适量扩展与参考思路

必做：给重命名增加测试，证明修改标题后 id、createdAt 和 done 不变。再测试同一 ID 重复删除；本项目约定第二次 404，而非 204，只要接口契约明确即可。

选做：把嵌套类型拆到同包多个文件，保留测试通过；然后提取存储接口，用数据库实现替换。替换前先决定事务、唯一性、排序与并发语义，不能仅凭“有接口”宣称上层永远零改动。

本例尚无认证与持久化，不用于真实多用户服务。业务异常的自定义 JSON 与框架校验错误的默认响应形状可能不同；统一错误协议可作为下一步练习。

参考：[Spring REST 入门](https://spring.io/guides/gs/rest-service/)解释 Controller 与自动配置，[输入校验指南](https://spring.io/guides/gs/validating-form-input/)解释 Validation 的接入。具体依赖以生成工程为准。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
