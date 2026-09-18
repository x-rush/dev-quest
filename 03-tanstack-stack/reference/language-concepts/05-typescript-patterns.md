# TypeScript 模式

## 概述

TanStack 生态的类型体验建立在泛型推断、字面量类型与判别联合之上。本篇收录在 Query/Table/Form 中反复出现的五类 TS 模式，减少不必要的类型断言，并明确运行时验证边界。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#泛型推断` `#类型安全` `#DiscriminatedUnion` `#satisfies` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. 泛型推断：让库替你算类型

### 定义

TanStack 各库的核心 API 都是泛型函数，类型从"数据源头"自动传播，无需手写泛型参数。

### 示例

```ts
// Query：data 类型 = queryFn 返回值类型
const { data } = useQuery({ queryKey: ['users'], queryFn: fetchUsers })
//    ^? User[] | undefined —— 自动推断

// Table：v9 ColumnDef 双泛型 <TFeatures, TData>，TData 决定 accessorKey 的候选字段
const features = tableFeatures({})
const columns: ColumnDef<typeof features, User>[] = [
  { accessorKey: 'name', header: '姓名' }, // 使用 User 字段名；具体 accessorKey 约束取决于 Table 版本，不能代替数据验证
  { accessorFn: (row) => row.age, header: '年龄' }, // row 自动是 User
]

// Form：defaultValues 决定 Field name 的候选与 value 类型
const form = useForm({ defaultValues: { email: '', age: 0 } })
// <form.Field name="age"> 的 value 自动是 number
```

### 陷阱

- 在 `queryFn` 里加 `: Promise<any>` 会击穿整个推断链，源头保持精确返回类型
- `fetch().then((r) => r.json())` 返回 `any`——先用类型守卫或 zod 解析再返回

## 2. 类型安全的 queryKey 工厂

### 定义

用 `as const` + 工厂函数把 queryKey 从"到处手写的魔法数组"升级为"受类型约束的枚举"。

### 语法与示例

```ts
// 工厂：所有 key 的构造集中一处
const todoKeys = {
  all: ['todos'] as const,
  lists: () => [...todoKeys.all, 'list'] as const,
  list: (filters: { page: number; status: 'open' | 'done' }) =>
    [...todoKeys.lists(), filters] as const,
  details: () => [...todoKeys.all, 'detail'] as const,
  detail: (id: number) => [...todoKeys.details(), id] as const,
}

// 读：key 只能从工厂产出，拼错字段名会报错
useQuery({ queryKey: todoKeys.list({ page: 1, status: 'open' }), queryFn })

// 失效：天然按层级命中
queryClient.invalidateQueries({ queryKey: todoKeys.lists() })  // 全部列表
queryClient.invalidateQueries({ queryKey: todoKeys.detail(3) }) // 单条详情
```

### 陷阱

- `as const` 不能省：没有它 `['todos']` 是 `string[]`，失去字面量收窄
- key 里的对象字段顺序不影响命中（结构化比较），但**类型**要一致

## 3. Discriminated Union（判别联合）

### 定义

用公共字面量字段（kind/status/type）区分联合成员，让 TS 在分支中自动收窄。Query 的渲染三分支就是典型应用。

### 示例

```ts
// API 响应建模
type ApiResult<T> =
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error }

function handle<T>(result: ApiResult<T>) {
  switch (result.status) {
    case 'success':
      return result.data // 收窄为 T，不需要 any
    case 'error':
      return result.error.message // 收窄为 Error
  }
}
```

```tsx
// Query 状态渲染：利用 status 判别联合而非逐个布尔判断
function TodoView({ query }: { query: UseQueryResult<Todo[]> }) {
  switch (query.status) {
    case 'pending':  return <Spinner />
    case 'error':    return <ErrorTip error={query.error} /> // error 非空已保证
    case 'success':  return <List data={query.data} />       // data 非空已保证
  }
}
```

### 陷阱

- 判别字段必须是**字面量类型**，写成 `string` 会失去收窄
- 联合成员加新分支后，`switch` 建议配 `default: never` 检查穷尽性

## 4. satisfies：声明约束但保留推断

### 定义

`satisfies` 校验"值符合某形状"，同时保留字面量的精确推断——比类型注解少丢信息，比 `as` 安全。

### 示例

```ts
const routes = {
  home: '/',
  posts: '/posts',
  postDetail: (id: string) => `/posts/${id}` as const,
} satisfies Record<string, string | ((...args: any[]) => string)>

routes.postDetail('3') // 推断保留，仍是函数
```

```tsx
// Form 的 defaultValues：既校验又保字段名精确
const defaults = { email: '', age: 0 } satisfies SignupValues
```

### 陷阱

- `satisfies` 只做检查不做类型拓宽/收窄转换，无法替代 `as` 做"强制改类型"
- 想让某字段**必须**是字面量，仍需在目标类型处用字面量联合约束

## 5. 从实例反推类型

### 定义

TanStack 常用 `typeof` 从"值"反推"类型"，避免双向维护。

### 示例

```ts
const queryClient = new QueryClient({ /* ... */ })
export type AppQueryClient = typeof queryClient

const defaultSort: SortingState = [{ id: 'name', desc: false }]
export type SortKey = (typeof defaultSort)[number]['id'] // string：显式 SortingState 注解已拓宽 id

// 从 queryFn 提取数据类型，供他处复用
type FetchUsers = typeof fetchUsers
type Users = Awaited<ReturnType<FetchUsers>>
```

### 陷阱

- `typeof` 推的是**值的静态类型**，运行时行为（如 zod schema 的输出类型）用 `z.infer<typeof schema>`
- 不要在模块间导出 `typeof` 组件实例类型——React 组件类型用 `React.ComponentProps<typeof Comp>` 提取 props

## 相关文档

- 📄 **[Query 核心 API](./01-query-core-api.md)** - 推断链的宿主 API
- 📄 **[Table 核心 API](./02-table-core-api.md)** - ColumnDef 泛型细节
- 📄 **[Form 核心 API](./04-form-core-api.md)** - 表单类型推断
- 📄 **[缓存键、staleTime 与失效策略](../framework-essentials/01-query-essentials.md)** - key 工厂的使用语境


<!-- full-library-explanation -->
## 类型推断与运行时验证是两条链

先修：泛型、unknown、联合类型。queryFn 的返回类型会影响 data 推断；但给 JSON 写 `as User[]` 并不会检查接口真实返回值。应在网络边界解析，再把已验证的类型交给 Query。

`as const` 保留字面量和 readonly 信息，`satisfies` 检查约束，二者都不会生成运行时校验代码。普通查询键不写 as const 仍可运行，只是部分类型工具无法保留同样精确的元组信息。

有显式 `SortingState` 注解时，元素 id 通常已拓宽成 string，不能再声称 typeof 会恢复为单个 'name'。如果确实需要固定字面量，可单独定义 `const sortId = 'name' as const`，再用它构造排序配置。

**练习：** 把接口返回值先设为 unknown，分别传合法用户数组与缺少 id 的对象；确认错误在解析边界被发现。再比较 `const a = {id: 'name'}`、`as const` 与显式类型注解的推断。验收：能说明哪一步只是编译检查，哪一步真正检查了数据。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
