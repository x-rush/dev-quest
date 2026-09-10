# 综合练习 - CLI 任务管理工具

> **文档简介**: 综合运用前七篇知识，用 Composer PSR-4 项目结构从零实现一个命令行任务管理工具（增删改查 + JSON 持久化）
>
> **目标读者**: 已完成 basics 全部教程、准备第一次独立交付完整项目的学习者
>
> **前置知识**: [环境搭建](./01-environment-setup.md) 至 [高级特性](./07-advanced-features.md) 全部内容

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#实战项目` `#Composer` `#PSR-4` `#CLI` `#JSON存储` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ 从零初始化 Composer 项目并配置 PSR-4 自动加载
- ✅ 按分层结构组织代码：模型 / 存储 / 服务 / 命令
- ✅ 使用枚举与构造器属性提升构建领域模型
- ✅ 让 `task` 命令可以直接全局执行（bin 脚本）

## 0. 项目需求

命令 `task` 支持以下子命令：

```text
task add "写周报" --priority high    # 新增任务
task list [--all]                    # 列出未完成任务（--all 含已完成）
task done <id>                       # 标记完成
task remove <id>                     # 删除任务
```

数据持久化为 JSON 文件 `tasks.json`，每条记录结构：

```json
{
  "id": "3f9c2e10",
  "title": "写周报",
  "priority": "high",
  "status": "pending",
  "created_at": "2026-09-10T08:30:00+00:00"
}
```

字段说明：`id` 为 8 位随机十六进制；`priority` 取 `low|normal|high`；`status` 取 `pending|done`；`created_at` 为 ISO 8601 格式字符串。

## 1. 初始化项目

```bash
mkdir task-cli && cd task-cli
composer init --name devquest/task-cli --type project --no-interaction
```

编辑生成的 `composer.json`，加入 PSR-4 映射与 bin 声明：

```json
{
  "name": "devquest/task-cli",
  "description": "CLI 任务管理工具：basics 综合练习",
  "type": "project",
  "require": {
    "php": ">=8.3"
  },
  "autoload": {
    "psr-4": {
      "DevQuest\\TaskCli\\": "src/"
    }
  },
  "bin": ["bin/task"]
}
```

```bash
mkdir -p src/{Model,Storage,Service} bin
composer dump-autoload
```

**PSR-4 规则**：命名空间前缀 `DevQuest\TaskCli\` 映射到 `src/` 目录，类名与文件路径一一对应——`DevQuest\TaskCli\Model\Task` 必须位于 `src/Model/Task.php`。

## 2. 领域模型：枚举 + 只读对象

`src/Model/Priority.php`：

```php
<?php

declare(strict_types=1);

namespace DevQuest\TaskCli\Model;

enum Priority: string
{
    case Low    = 'low';
    case Normal = 'normal';
    case High   = 'high';

    public function rank(): int
    {
        return match ($this) {
            self::High   => 3,
            self::Normal => 2,
            self::Low    => 1,
        };
    }
}
```

`src/Model/Status.php`：

```php
<?php

declare(strict_types=1);

namespace DevQuest\TaskCli\Model;

enum Status: string
{
    case Pending = 'pending';
    case Done    = 'done';
}
```

`src/Model/Task.php`：

```php
<?php

declare(strict_types=1);

namespace DevQuest\TaskCli\Model;

use InvalidArgumentException;

final class Task
{
    public function __construct(
        public readonly string $id,
        public readonly string $title,
        public readonly Priority $priority,
        public Status $status = Status::Pending,
        public readonly string $createdAt = '',
    ) {
        $createdAt !== '' || throw new InvalidArgumentException('createdAt 不能为空');
    }

    /** 反序列化入口：数组 -> 对象，非法值统一在此暴露 */
    public static function fromArray(array $row): self
    {
        return new self(
            id: $row['id'],
            title: $row['title'],
            priority: Priority::from($row['priority']),
            status: Status::from($row['status']),
            createdAt: $row['created_at'],
        );
    }

    /** 序列化出口：对象 -> 数组 */
    public function toArray(): array
    {
        return [
            'id'         => $this->id,
            'title'      => $this->title,
            'priority'   => $this->priority->value,
            'status'     => $this->status->value,
            'created_at' => $this->createdAt,
        ];
    }

    /** 完成操作返回新对象（不可变风格），原对象保持不动 */
    public function markDone(): self
    {
        $copy = clone $this;
        $copy->status = Status::Done;
        return $copy;
    }
}
```

## 3. 存储层：JSON 读写

`src/Storage/TaskRepository.php`：

```php
<?php

declare(strict_types=1);

namespace DevQuest\TaskCli\Storage;

use DevQuest\TaskCli\Model\Task;
use RuntimeException;

final class TaskRepository
{
    public function __construct(
        private readonly string $file,
    ) {
    }

    /** @return list<Task> */
    public function all(): array
    {
        if (!is_file($this->file)) {
            return [];
        }

        $raw = file_get_contents($this->file);
        if ($raw === false) {
            throw new RuntimeException("无法读取: {$this->file}");
        }

        $rows = json_decode($raw, true, flags: JSON_THROW_ON_ERROR);
        return array_map(Task::fromArray(...), $rows);
    }

    /** @param list<Task> $tasks */
    public function save(array $tasks): void
    {
        $rows = array_map(fn(Task $t) => $t->toArray(), $tasks);
        $json = json_encode(
            array_values($rows),
            JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR
        );

        if (file_put_contents($this->file, $json) === false) {
            throw new RuntimeException("无法写入: {$this->file}");
        }
    }

    public function nextId(): string
    {
        return bin2hex(random_bytes(4));   // 8 位随机 id
    }
}
```

## 4. 服务层：业务规则

`src/Service/TaskService.php`：

```php
<?php

declare(strict_types=1);

namespace DevQuest\TaskCli\Service;

use DevQuest\TaskCli\Model\Priority;
use DevQuest\TaskCli\Model\Status;
use DevQuest\TaskCli\Model\Task;
use DevQuest\TaskCli\Storage\TaskRepository;
use InvalidArgumentException;
use RuntimeException;

final class TaskService
{
    public function __construct(
        private readonly TaskRepository $repo,
    ) {
    }

    public function add(string $title, string $priority = 'normal'): Task
    {
        $trimmed = trim($title);
        if ($trimmed === '') {
            throw new InvalidArgumentException('任务标题不能为空');
        }

        $task = new Task(
            id: $this->repo->nextId(),
            title: $trimmed,
            priority: Priority::tryFrom($priority) ?? Priority::Normal,
            createdAt: date('c'),
        );

        $this->repo->save([...$this->repo->all(), $task]);
        return $task;
    }

    /** @return list<Task> 按 priority 降序、时间升序排列 */
    public function list(bool $includeDone = false): array
    {
        $tasks = array_values(array_filter(
            $this->repo->all(),
            fn(Task $t) => $includeDone || $t->status === Status::Pending,
        ));

        usort($tasks, fn(Task $a, Task $b) => $b->priority->rank() <=> $a->priority->rank()
            ?: strcmp($a->createdAt, $b->createdAt));
        return $tasks;
    }

    public function done(string $id): Task
    {
        return $this->mutate($id, fn(Task $t) => $t->markDone());
    }

    public function remove(string $id): void
    {
        $tasks = $this->repo->all();
        $kept  = array_values(array_filter($tasks, fn(Task $t) => $t->id !== $id));

        count($kept) === count($tasks) || throw new RuntimeException("任务不存在: {$id}");
        $this->repo->save($kept);
    }

    private function mutate(string $id, callable $fn): Task
    {
        $tasks = $this->repo->all();
        foreach ($tasks as $i => $task) {
            if ($task->id === $id) {
                $updated = $fn($task);
                $tasks[$i] = $updated;
                $this->repo->save($tasks);
                return $updated;
            }
        }
        throw new RuntimeException("任务不存在: {$id}");
    }
}
```

## 5. 入口：bin 脚本与参数解析

`bin/task`（无 `.php` 后缀，加上可执行权限 `chmod +x bin/task`）：

```php
#!/usr/bin/env php
<?php

declare(strict_types=1);

require __DIR__ . '/../vendor/autoload.php';

use DevQuest\TaskCli\Service\TaskService;
use DevQuest\TaskCli\Storage\TaskRepository;
use InvalidArgumentException;
use Throwable;

$repo = new TaskRepository(__DIR__ . '/../tasks.json');
$svc  = new TaskService($repo);

$command = $argv[1] ?? 'list';

try {
    $exit = match ($command) {
        'add' => (function () use ($svc, $argv): int {
            $title = $argv[2] ?? throw new InvalidArgumentException('用法: task add "标题" [--priority high]');
            preg_match('/--priority\s+(\w+)/', implode(' ', array_slice($argv, 3)), $m);
            $task = $svc->add($title, $m[1] ?? 'normal');
            printf("已添加 [%s] %s%s", $task->id, $task->title, PHP_EOL);
            return 0;
        })(),
        'list' => (function () use ($svc, $argv): int {
            foreach ($svc->list(in_array('--all', $argv, true)) as $t) {
                printf("[%s] %-6s %-8s %s%s", $t->id, $t->priority->value, $t->status->value, $t->title, PHP_EOL);
            }
            return 0;
        })(),
        'done' => (function () use ($svc, $argv): int {
            $id = $argv[2] ?? throw new InvalidArgumentException('用法: task done <id>');
            $svc->done($id);
            echo "已完成", PHP_EOL;
            return 0;
        })(),
        'remove' => (function () use ($svc, $argv): int {
            $id = $argv[2] ?? throw new InvalidArgumentException('用法: task remove <id>');
            $svc->remove($id);
            echo "已删除", PHP_EOL;
            return 0;
        })(),
        default => (function () use ($command): int {
            fwrite(STDERR, "未知命令: {$command}" . PHP_EOL . "可用: add | list | done | remove" . PHP_EOL);
            return 1;
        })(),
    };
} catch (Throwable $e) {
    fwrite(STDERR, "错误: {$e->getMessage()}" . PHP_EOL);
    exit(1);
}

exit($exit);
```

## 6. 运行验证

```bash
php bin/task add "完成PHP模块第一篇" --priority high
php bin/task add "阅读Go关键字文档"
php bin/task list
php bin/task done <上面输出的id>
php bin/task list --all
php bin/task remove <id>
```

每一步输出都符合预期、`tasks.json` 内容正确，即项目完成。

## ✅ 最佳实践

- ✅ **分层单向依赖**：`bin → Service → Repository/Model`，上层依赖下层抽象，方便替换存储引擎
- ✅ **序列化集中在 Model**：`fromArray/toArray` 是数据进出系统的唯一边界，格式变更只改一处
- ✅ **CLI 必须有退出码**：成功 0、失败非 0，Shell 脚本与 CI 才能判断成败
- ❌ **不要在 bin 脚本里堆业务逻辑**：入口只做参数解析与装配，逻辑下沉到 Service
- ❌ **不要把 `tasks.json` 提交进版本库**：加入 `.gitignore`，数据文件属于运行时产物

## ❓ 常见问题

### Q1: 报 `Class "DevQuest\TaskCli\..." not found`？
**A**: 检查命名空间与目录是否严格符合 PSR-4，然后重新 `composer dump-autoload`。

### Q2: `bin/task` 提示权限不足？
**A**: `chmod +x bin/task`；Windows 下用 `php bin/task` 调用即可。

### Q3: JSON 文件损坏后如何兜底？
**A**: `JSON_THROW_ON_ERROR` 会让 `json_decode` 抛出 `JsonException`。生产化做法是写入前先写临时文件再原子重命名（`rename`），并在读取失败时备份损坏文件。

## 🎯 练习与实践

### 基础练习（必做）
- [ ] 跑通第 6 节全部命令并检查 `tasks.json`
- [ ] 给 `task list` 增加按标题过滤参数：`task list --filter=周报`
- [ ] 为 `TaskService` 的每个方法补全参数校验与对应异常

### 进阶挑战
- [ ] 引入 `symfony/console` 重写入口，获得彩色输出与帮助信息（参照 [`../reference/framework-essentials/02-symfony-essentials.md`](../reference/framework-essentials/02-symfony-essentials.md)）
- [ ] 用 Pest 给 `TaskService` 写单元测试，用内存假仓库替代文件存储（参照 [`../reference/library-guides/02-composer-ecosystem.md`](../reference/library-guides/02-composer-ecosystem.md)）

---

## 🔗 相关文档

- 📄 **[环境搭建](./01-environment-setup.md)** — 本项目使用其 Composer 配置
- 📄 **[Composer 生态精选](../reference/library-guides/02-composer-ecosystem.md)** — PSR-4 与测试工具深入
- 📄 **[Symfony 核心](../reference/framework-essentials/02-symfony-essentials.md)** — Console 组件进阶改造
