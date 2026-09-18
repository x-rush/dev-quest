# 入门项目：TODO REST API

## 分阶段练习与验收

**最小阶段**：先完成待办创建和详情，再补列表与修改。

**验收结果**：无效标题不入库，不存在 ID 返回 404，JSON 结构一致。

**扩展顺序**：认证、分页和发布是后续步骤，不要省略本阶段必要迁移与路由。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

> **文档简介**: 用 Laravel 13 从零构建一个符合 REST 风格的 TODO API，覆盖模型、验证、资源响应与路由设计的最小闭环
>
> **目标读者**: 学完 frameworks 入门篇、第一次用 Laravel 写完整接口的开发者
>
> **前置知识**: [Laravel 入门](../frameworks/01-laravel-basics.md)、[CLI 任务管理工具](../basics/08-first-project.md)；枚举前置：[高级特性 · 枚举](../basics/07-advanced-features.md)（第 1 节即可——项目直接使用 Backed Enum 与 `enum:` 校验规则）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `07-php-mastery` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#Laravel` `#REST` `#实战项目` `#TODO` `#API` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 项目目标

- ✅ 设计并实现 5 个 REST 端点（列表/详情/创建/更新/删除）
- ✅ 用 FormRequest 集中验证输入
- ✅ 用 API Resource 控制响应结构
- ✅ 用枚举表达任务状态，杜绝魔法字符串

## 1. 需求与接口设计

| 方法 | URI | 说明 |
|------|-----|------|
| GET | `/api/todos` | 任务列表（支持 `?status=` 过滤） |
| POST | `/api/todos` | 创建任务 |
| GET | `/api/todos/{todo}` | 任务详情 |
| PATCH | `/api/todos/{todo}` | 更新任务 |
| DELETE | `/api/todos/{todo}` | 删除任务 |

任务字段：`id`、`title`（必填，≤120 字）、`status`（`pending|doing|done`）、`due_date`（可空日期）。

```bash
composer create-project laravel/laravel:^13.0 todo-api
cd todo-api && php artisan install:api
php artisan make:model Todo -mfs   # 模型 + 迁移 + 工厂 + Seeder
```

## 2. 迁移与模型

```php
// database/migrations/xxxx_create_todos_table.php
Schema::create('todos', function (Blueprint $table): void {
    $table->id();
    $table->string('title', 120);
    $table->string('status', 16)->default('pending')->index(); // 过滤列建索引
    $table->date('due_date')->nullable();
    $table->timestamps();
});
```

```php
// app/Models/Todo.php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

final class Todo extends Model
{
    protected $fillable = ['title', 'status', 'due_date'];

    protected $casts = [
        'status'   => TodoStatus::class,   // 枚举自动互转
        'due_date' => 'date:Y-m-d',
    ];
}
```

```php
// app/Enums/TodoStatus.php —— 状态只此一处定义
namespace App\Enums;

enum TodoStatus: string
{
    case Pending = 'pending';
    case Doing   = 'doing';
    case Done    = 'done';
}
```

## 3. 验证：FormRequest

```bash
php artisan make:request StoreTodoRequest
```

```php
// app/Http/Requests/StoreTodoRequest.php
namespace App\Http\Requests;

use App\Enums\TodoStatus;
use Illuminate\Foundation\Http\FormRequest;

final class StoreTodoRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;   // 开放接口；有用户体系时在此做权限判断
    }

    /** @return array<string, array<int, string>> */
    public function rules(): array
    {
        return [
            'title'    => ['required', 'string', 'max:120'],
            'status'   => ['sometimes', 'enum:'.TodoStatus::class],
            'due_date' => ['nullable', 'date', 'after_or_equal:today'],
        ];
    }
}
```

验证失败 Laravel 自动返回 422 与错误 JSON，控制器无需手写判断。

## 4. 控制器与 API Resource

```php
// app/Http/Controllers/TodoController.php
namespace App\Http\Controllers;

use App\Enums\TodoStatus;
use App\Http\Requests\StoreTodoRequest;
use App\Http\Resources\TodoResource;
use App\Models\Todo;
use Illuminate\Contracts\Database\Eloquent\Builder;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;

final class TodoController extends Controller
{
    public function index(Request $request): AnonymousResourceCollection
    {
        // 非法 status 用 tryFrom 兜底返回 null：from() 会抛 ValueError，
        // 未捕获直接 500；需要把非法值挡成 422 时，改为 $request->validate 校验
        $status = TodoStatus::tryFrom($request->string('status'));

        return TodoResource::collection(
            Todo::query()
                ->when($status !== null, fn (Builder $q) => $q->where('status', $status))
                ->orderBy('due_date')
                ->paginate(20),
        );
    }

    public function store(StoreTodoRequest $request): JsonResponse
    {
        $todo = Todo::create($request->validated());

        return (new TodoResource($todo))->response()->setStatusCode(201);
    }

    public function update(Request $request, Todo $todo): TodoResource
    {
        // 简单场景可内联 validate()，422 行为与 FormRequest 一致；
        // 白名单字段 + $fillable 双保险，杜绝越权改 id 等字段
        $data = $request->validate([
            'title'    => ['sometimes', 'string', 'max:120'],
            'status'   => ['sometimes', 'enum:'.TodoStatus::class],
            'due_date' => ['nullable', 'date', 'after_or_equal:today'],
        ]);

        $todo->update($data);

        return new TodoResource($todo);
    }

    public function destroy(Todo $todo): JsonResponse
    {
        $todo->delete();   // 路由模型绑定：找不到自动 404

        return response()->json(status: 204);
    }
}
```

```php
// app/Http/Resources/TodoResource.php —— 响应结构收敛到一层
namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/** @mixin \App\Models\Todo */
final class TodoResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'     => $this->id,
            'title'  => $this->title,
            'status' => $this->status->value,
            'due'    => $this->due_date?->format('Y-m-d'),
        ];
    }
}
```

```php
// routes/api.php
use App\Http\Controllers\TodoController;
use Illuminate\Support\Facades\Route;

Route::apiResource('todos', TodoController::class); // 自动排除 create/edit
```

## 5. 自测清单

```bash
php artisan migrate --seed
php artisan serve
curl -s localhost:8000/api/todos | php -r 'echo json_encode(json_decode(stream_get_contents(STDIN)), JSON_PRETTY_PRINT);'
```

- [ ] 创建/更新接口传无效 `status` 返回 422 且带字段级错误
- [ ] 列表过滤 `?status=非法值` 不报 500（被忽略，返回未过滤列表）
- [ ] 不存在的 id 返回 404 而非 500
- [ ] `PATCH /api/todos/1` 只允许修改白名单字段

完成本项目的自然延伸：为其补测试（见[单元测试](../testing/01-unit-testing.md)）。

## 🔗 相关文档

- 📄 [Laravel 核心速查](../reference/framework-essentials/01-laravel-essentials.md) — 路由与 Eloquent 细节回查
- 📄 [类型系统与现代 OOP](../reference/language-concepts/03-types-oop-modern.md) — 枚举语法详解
- 📄 [博客平台实战](./02-blog-platform.md) — 加认证与关系的进阶项目
- 📄 [PHP 故障排除](../reference/quick-references/02-troubleshooting.md) — 报错时先查这里


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
