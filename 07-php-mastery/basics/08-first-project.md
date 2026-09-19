# 综合练习 - CLI 任务管理工具

## 先理解，再动手

CLI 工具也需要稳定的输入、输出和失败约定。保存文件时应把“读失败”和“第一次没有文件”区分开。

**本节自测**：新增两条任务、完成一条、重启读取，再模拟 JSON 损坏。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

正常记录保留，损坏数据明确报错；不能静默覆盖用户已有文件。

</details>

> **文档简介**: 综合运用前七篇知识，用 Composer PSR-4 项目结构从零实现一个命令行任务管理工具（增删改查 + JSON 持久化）
>
> **目标读者**: 已完成 basics 全部教程、准备第一次独立交付完整项目的学习者
>
> **前置知识**: [环境搭建](./01-environment-setup.md) 至 [高级特性](./07-advanced-features.md) 全部内容

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#实战项目` `#Composer` `#PSR-4` `#CLI` `#JSON存储` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本项目后，你将能够：

- ✅ 从零初始化 Composer 项目并配置 PSR-4 自动加载
- ✅ 按分层结构组织代码：模型 / 存储 / 服务 / 命令
- ✅ 使用枚举与构造器属性提升构建领域模型
- ✅ 用 `php bin/task` 执行命令，并通过退出码判断成功与失败

## 0. 项目需求

本项目基线为 PHP 8.3+、Composer 2、本地普通文件系统。先完成 basics 01–06；枚举可结合第 07 篇边做边学。下面 shell 命令使用 Bash；Windows 可在 WSL 中创建目录，也可手动按文件名创建，再用 `php bin/task` 运行。

命令 `task` 支持以下子命令（开发目录中实际使用 `php bin/task`）：

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

编辑生成的 `composer.json`，加入 PSR-4 映射与 bin 声明。`bin` 声明供 Composer 安装包时识别可执行文件，它不会把当前项目自动加入系统 PATH。

<!-- project-file: composer.json -->
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

<!-- project-file: src/Model/Priority.php -->
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

<!-- project-file: src/Model/Status.php -->
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

<!-- project-file: src/Model/Task.php -->
```php
<?php

declare(strict_types=1);

namespace DevQuest\TaskCli\Model;

use InvalidArgumentException;

final readonly class Task
{
    public function __construct(
        public string $id,
        public string $title,
        public Priority $priority,
        public Status $status = Status::Pending,
        public string $createdAt = '',
    ) {
        if (!preg_match('/\A[0-9a-f]{8}\z/', $id)) {
            throw new InvalidArgumentException('id 必须是 8 位十六进制字符串');
        }
        if (trim($title) === '' || strlen($title) > 240
            || !preg_match('//u', $title) || preg_match('/[\x00-\x1f\x7f]/', $title)) {
            throw new InvalidArgumentException('标题须为 1–240 字节 UTF-8 文本，不能包含控制字符');
        }
        $date = \DateTimeImmutable::createFromFormat(DATE_ATOM, $createdAt);
        if ($date === false || $date->format(DATE_ATOM) !== $createdAt) {
            throw new InvalidArgumentException('created_at 必须是有效的 ISO 8601 时间');
        }
    }

    /** 反序列化入口：数组 -> 对象，非法值统一在此暴露 */
    public static function fromArray(array $row): self
    {
        foreach (['id', 'title', 'priority', 'status', 'created_at'] as $key) {
            if (!isset($row[$key]) || !is_string($row[$key])) {
                throw new InvalidArgumentException("字段必须是字符串: {$key}");
            }
        }
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
        return new self($this->id, $this->title, $this->priority, Status::Done, $this->createdAt);
    }
}
```

## 3. 存储层：JSON 读写

`src/Storage/TaskRepository.php`：

<!-- project-file: src/Storage/TaskRepository.php -->
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
        if (!file_exists($this->file) && !is_link($this->file)) {
            return [];
        }
        if (!is_file($this->file) || is_link($this->file)) {
            throw new RuntimeException('存储路径必须是普通文件，不能是目录或符号链接');
        }

        $raw = @file_get_contents($this->file);
        if ($raw === false) {
            throw new RuntimeException("无法读取: {$this->file}");
        }

        $rows = json_decode($raw, flags: JSON_THROW_ON_ERROR);
        if (!is_array($rows)) {
            throw new RuntimeException('存储根节点必须是 JSON 数组');
        }
        $tasks = [];
        $ids = [];
        foreach ($rows as $row) {
            if (!$row instanceof \stdClass) {
                throw new RuntimeException('任务记录必须是 JSON 对象');
            }
            $task = Task::fromArray((array) $row);
            if (isset($ids[$task->id])) {
                throw new RuntimeException("存储包含重复 id: {$task->id}");
            }
            $ids[$task->id] = true;
            $tasks[] = $task;
        }
        return $tasks;
    }

    /** @param list<Task> $tasks */
    public function save(array $tasks): void
    {
        $rows = array_map(fn(Task $t) => $t->toArray(), $tasks);
        $json = json_encode(
            array_values($rows),
            JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR
        );

        // 同目录临时文件：成功写完后再替换，避免截断原文件。
        $temp = @tempnam(dirname($this->file), '.tasks-');
        if ($temp === false || realpath(dirname($temp)) !== realpath(dirname($this->file))) {
            if ($temp !== false) { @unlink($temp); }
            throw new RuntimeException('无法在数据目录创建临时文件');
        }
        try {
            if (@file_put_contents($temp, $json) !== strlen($json)) {
                throw new RuntimeException('数据未完整写入');
            }
            if (!@rename($temp, $this->file)) {
                throw new RuntimeException("无法替换: {$this->file}");
            }
        } finally {
            if (is_file($temp)) { @unlink($temp); }
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

<!-- project-file: src/Service/TaskService.php -->
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

        $level = Priority::tryFrom($priority)
            ?? throw new InvalidArgumentException('priority 只能是 low、normal 或 high');
        $tasks = $this->repo->all();
        $ids = array_map(fn(Task $t) => $t->id, $tasks);
        do { $id = $this->repo->nextId(); } while (in_array($id, $ids, true));
        $task = new Task(
            id: $id,
            title: $trimmed,
            priority: $level,
            createdAt: (new \DateTimeImmutable('now', new \DateTimeZone('UTC')))->format(DATE_ATOM),
        );

        $this->repo->save([...$tasks, $task]);
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

        if (count($kept) === count($tasks)) {
            throw new RuntimeException("任务不存在: {$id}");
        }
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

`bin/task`（无 `.php` 后缀；使用 `php bin/task` 无需执行权限）：

<!-- project-file: bin/task -->
```php
#!/usr/bin/env php
<?php

declare(strict_types=1);

require __DIR__ . '/../vendor/autoload.php';

use DevQuest\TaskCli\Service\TaskService;
use DevQuest\TaskCli\Storage\TaskRepository;
$command = $argv[1] ?? 'list';
$options = array_slice($argv, 2);
$file = getenv('TASK_FILE') ?: __DIR__ . '/../tasks.json';
$lock = null;
$exit = 1;

try {
    // 固定锁文件不随数据文件 rename 改变。整个读→改→写操作持有同一把锁。
    $lock = @fopen($file . '.lock', 'c');
    if ($lock === false || !flock($lock, LOCK_EX)) {
        throw new RuntimeException('无法取得数据文件锁');
    }
    $svc = new TaskService(new TaskRepository($file));
    $exit = match ($command) {
        'add' => (function () use ($svc, $options): int {
            if (count($options) !== 1 && !(count($options) === 3 && $options[1] === '--priority')) {
                throw new InvalidArgumentException('用法: task add "标题" [--priority high]');
            }
            $task = $svc->add($options[0], $options[2] ?? 'normal');
            printf("已添加 [%s] %s%s", $task->id, $task->title, PHP_EOL);
            return 0;
        })(),
        'list' => (function () use ($svc, $options): int {
            if ($options !== [] && $options !== ['--all']) {
                throw new InvalidArgumentException('用法: task list [--all]');
            }
            foreach ($svc->list($options === ['--all']) as $t) {
                printf("[%s] %-6s %-8s %s%s", $t->id, $t->priority->value, $t->status->value, $t->title, PHP_EOL);
            }
            return 0;
        })(),
        'done' => (function () use ($svc, $options): int {
            $id = taskId($options);
            $svc->done($id);
            echo "已完成", PHP_EOL;
            return 0;
        })(),
        'remove' => (function () use ($svc, $options): int {
            $id = taskId($options);
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
} finally {
    if (is_resource($lock)) {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}

exit($exit);

function taskId(array $options): string
{
    if (count($options) !== 1 || !preg_match('/\A[0-9a-f]{8}\z/', $options[0])) {
        throw new InvalidArgumentException('需要一个 8 位十六进制任务 ID');
    }
    return $options[0];
}
```

这里按 `$argv` 的每个元素解析参数。先 `implode()` 再正则匹配会丢失 shell 已解析好的参数边界，并把拼错的选项静默忽略。未知优先级现在明确报错；`done` 重复执行是幂等的，`remove` 删除未知 ID 则失败。

固定 `.lock` 文件保护所有 CLI 实例的完整读改写周期；**不要在运行中删除锁文件**。`TaskRepository` 本身没有线程/进程事务能力，直接调用服务的其他程序也必须遵循同一锁协议。锁语义见 [PHP flock 手册](https://www.php.net/manual/en/function.flock.php)。

临时文件替换减少了半写 JSON 的风险，但不能保证断电时数据已经落盘；网络文件系统、不同平台的替换语义需要单独验收。这个练习只面向受控的本地数据目录，多用户服务应采用具有事务和唯一约束的数据库。

## 6. 运行验证

```bash
php bin/task add "完成PHP模块第一篇" --priority high
php bin/task add "阅读Go关键字文档"
php bin/task list
# 将列表中实际的任务 ID 填入 TASK_ID
TASK_ID=""
php bin/task done "${TASK_ID:?请先填写任务ID}"
php bin/task list --all
php bin/task remove "${TASK_ID:?请先填写任务ID}"
```

每条命令启动新进程，所以后一次 `list` 已经验证了重启读取。完成以下失败路径才能验收：

| 操作 | 可观察结果 |
|---|---|
| `add "   "`、`add "任务" --priority urgent`、`list --unknown` | 退出码 1；标准错误说明原因；原 JSON 字节保持不变 |
| 对现存 ID 执行 `remove` | 退出码 0；再次列出时该记录消失 |
| 再次删除同一 ID | 退出码 1；其余记录不变 |
| 将测试文件改成 `{`、`{}` 或含重复 ID 的数组，再执行新增 | 拒绝损坏存储；不覆盖原文件 |
| 让 `TASK_FILE` 指向目录或不可写目录 | 明确失败；不能报告已添加 |
| 多个进程向同一个本地文件新增 | 所有成功返回的记录保留，ID 不重复 |

先复制测试目录再做损坏/权限实验；用 `TASK_FILE=/tmp/task-test.json php bin/task list` 可隔离数据。PowerShell 对应 `$env:TASK_FILE = "$PWD/tasks-test.json"`。

仓库的 [首项目验证器](../../shared-resources/tools/document-quality/verify_php_java_projects.py) 从本篇逐字提取文件，再用 Composer 生成自动加载并执行上述场景；结果见 [验证报告](../../shared-resources/tools/document-quality/reports/php-java-projects.md)。

## ✅ 最佳实践

CLI 入口负责读参数、组装依赖和映射退出码，业务规则放在可直接测试的函数或服务中。存储格式转换集中在明确边界，放模型还是独立映射器取决于复用需求，不必宣布一个方法是系统唯一数据入口。

运行数据与示例夹具分开：真实 tasks.json 通常不提交，合成测试数据可以入库。验证无效参数、损坏文件与写入失败时的退出码和数据完整性，再检查成功后重启仍能读取。

## ❓ 常见问题

### Q1: 报 `Class "DevQuest\TaskCli\..." not found`？
**A**: 检查命名空间与目录是否严格符合 PSR-4，然后重新 `composer dump-autoload`。

### Q2: `bin/task` 提示权限不足？
**A**: `chmod +x bin/task`；Windows 下用 `php bin/task` 调用即可。

### Q3: JSON 文件损坏后如何兜底？
**A**: 本文已经使用 `JSON_THROW_ON_ERROR` 和逐字段校验。读取失败时停止修改，先手工备份原文件，再修复或恢复备份；不要把损坏当作“空列表”继续保存。临时文件替换只能降低新的写入损坏风险，不能恢复已有损坏。

## 🎯 练习与实践

### 基础练习（必做）
- [ ] 跑通第 6 节全部命令并检查 `tasks.json`
- [ ] 给 `task list` 增加按标题过滤参数：`task list --filter=周报`
- [ ] 为 `TaskService` 的每个方法补全参数校验与对应异常

### 进阶挑战
- [ ] 引入 `symfony/console` 重写入口，获得彩色输出与帮助信息（参照 [`../reference/framework-essentials/02-symfony-essentials.md`](../reference/framework-essentials/02-symfony-essentials.md)）
- [ ] 先提取 `TaskStore` 接口，再让文件仓库与内存仓库实现它，并用 Pest 测试服务；当前 `final TaskRepository` 不能靠继承替换（参照 [`../reference/library-guides/02-composer-ecosystem.md`](../reference/library-guides/02-composer-ecosystem.md)）。

---

## 🔗 相关文档

- 📄 **[环境搭建](./01-environment-setup.md)** — 本项目使用其 Composer 配置
- 📄 **[Composer 生态精选](../reference/library-guides/02-composer-ecosystem.md)** — PSR-4 与测试工具深入
- 📄 **[Symfony 核心](../reference/framework-essentials/02-symfony-essentials.md)** — Console 组件进阶改造


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
