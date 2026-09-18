# Form 核心 API

## 概述

TanStack Form v1 的三层 API：`useForm`（表单实例）、`form.Field` / `form.Subscribe`（订阅渲染）、校验器（同步/异步/Standard Schema）。教程见 [Form 基础](../../basics/06-form-fundamentals.md)。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#useForm` `#Field` `#validators` `#API字典` |
| **更新日期** | `2026年9月` |

</details>

---

## 1. useForm

### 定义

创建并持有表单状态机。返回的 `form` 对象是稳定的（不随渲染变化），所有状态通过订阅机制读取。

### 语法

```ts
const form = useForm({
  defaultValues: { username: '', age: 0 }, // 必填，决定 value 类型
  onSubmit: async ({ value }) => api.submit(value), // 提交回调
  validators: {                            // 表单级校验
    onChange: schemaOrFn,
    onBlur: schemaOrFn,
    onSubmit: z.object({ /* ... */ }),     // Standard Schema 直接可用
    onChangeDebounceMs: 300,               // 异步校验防抖
  },
})
```

### form 实例成员

| 成员 | 作用 |
|------|------|
| `form.Field` | 字段渲染组件（name + children 渲染属性） |
| `form.Subscribe` | 选择性订阅表单级状态 |
| `form.handleSubmit()` | 触发校验与 onSubmit |
| `form.reset()` | 恢复 defaultValues |
| `form.setFieldValue(name, value)` | 编程式写单个字段 |
| `form.state` | 完整状态（渲染外读取） |

### form.state 关键字段

| 字段 | 含义 |
|------|------|
| `values` | 全部字段值 |
| `canSubmit` | 无阻塞错误且不在提交中 |
| `isSubmitting` / `isSubmitted` | 提交状态 |
| `isDirty` | 字段曾被编辑的脏状态；与当前值是否等于默认值应分别判断 |
| `errorMap` | 按校验时机分布的表单级错误 |
| `fieldMeta` | 所有字段的 meta 汇总 |

### 陷阱

- `form.state.values` 的引用在每次按键都变化——组件里直读会失去订阅优化
- `defaultValues` 若来自异步数据，用 `key` 重挂表单或重设 `defaultValues`，不要 setState 手工灌入

## 2. form.Field 与 field 对象

### 定义

`<form.Field name="xxx">` 把某个字段的读写与元信息以渲染属性暴露给输入控件。

### 语法与示例

```tsx
<form.Field
  name="age"
  validators={{
    onChange: ({ value }) => (value < 0 ? '不能为负数' : undefined),
    onBlurAsync: async ({ value }) =>
      (await api.checkAge(value)) ? undefined : '年龄校验失败',
  }}
  defaultValue={18} // 可覆盖表单级初始值
>
  {(field) => (
    <input
      name={field.name}                 // 字段名（含嵌套路径）
      value={field.state.value}         // 当前值（类型精确）
      onBlur={field.handleBlur}         // 标记 touched + 触发 onBlur 校验
      onChange={(e) => field.handleChange(Number(e.target.value))}
    />
  )}
</form.Field>
```

### field 对象成员

| 成员 | 作用 |
|------|------|
| `field.name` | 字段路径（支持 `a.b` / `list[0].name` 嵌套） |
| `field.state.value` | 字段值 |
| `field.state.meta.errors` | 错误数组 |
| `field.state.meta.isTouched` / `isBlurred` | 触碰状态 |
| `field.state.meta.isValidating` | 异步校验进行中 |
| `field.state.meta.isValid` | 无错误的便捷标志 |
| `field.handleChange(v)` | 写值（自动触发 onChange 校验） |
| `field.handleBlur()` | 失焦处理 |
| `field.pushValue(v)` / `field.removeValue(i)` | 数组字段操作 |

### 陷阱

- `meta.errors` 是数组：函数校验器的错误是 string，Standard Schema 的错误是含 `message` 的对象，渲染时按实际错误类型提取 message；直接 String(对象) 可能只显示 [object Object]
- `onChange` 里写重量级异步校验会阻塞输入，应使用 `onChangeAsync` + `onChangeDebounceMs`

## 3. 校验器层级与时机

### 定义

校验器可挂在**字段级**（只校验该字段）与**表单级**（跨字段/整表校验），错误自动归位：表单级 schema 校验失败时，Zod 的 issues 会按路径分发到对应字段。

### 时机选项

| 键名 | 触发时机 |
|------|---------|
| `onChange` / `onChangeAsync` | 值变化 |
| `onBlur` / `onBlurAsync` | 失焦 |
| `onSubmit` / `onSubmitAsync` | 提交时 |
| 上述 + `DebounceMs` | 异步变体可配防抖 |

```tsx
// 表单级：Standard Schema 提交把关（错误按 path 分发到字段）
const form = useForm({
  defaultValues: { password: '', confirm: '' },
  validators: {
    onSubmit: z.object({ password: z.string().min(8), confirm: z.string() })
      .refine((v) => v.password === v.confirm, {
        message: '两次密码不一致', path: ['confirm'],
      }),
  },
  onSubmit: ({ value }) => api.register(value),
})
```

### 陷阱

- 通常用 undefined 表示无错误；官方表单级示例也支持 null，不应笼统禁止
- 同一字段同一时机的字段级错误可能覆盖表单级分配的错误；需要通过用例确认最终 errorMap

## 4. form.Subscribe

### 定义

以 selector 粒度订阅表单状态，返回值变化才重渲染，适合提交按钮、错误横幅等派生 UI。

### 示例

```tsx
<form.Subscribe selector={(s) => [s.canSubmit, s.isSubmitting] as const}>
  {([canSubmit, isSubmitting]) => (
    <button type="submit" disabled={!canSubmit}>
      {isSubmitting ? '提交中...' : '提交'}
    </button>
  )}
</form.Subscribe>
```

### 陷阱

- selector 返回新对象时需保证内容比较稳定，否则退化为全量重渲染（尽量返回原始值或拆分订阅）

## 相关文档

- 📄 **[Form 基础](../../basics/06-form-fundamentals.md)** - 教程入口
- 📄 **[TypeScript 模式](./05-typescript-patterns.md)** - 表单类型的推断
- 📄 **[相关库：Zod](../library-guides/02-related-libs.md)** - Schema 生态搭配


<!-- full-library-explanation -->
## 表单实例与响应式订阅分别负责什么

先修：受控输入、事件、异步函数。form 实例是操作入口；直接在 React 渲染中读 form.state，不会自动为所有字段建立响应式订阅。字段用 Field/useField，表单派生 UI 用 Subscribe 或 store 订阅。

数字输入的空字符串不是数字 0 的同义词；Number('') 会得到 0，可能把“未填写”误作合法年龄。先定义空值业务语义，再决定字段存字符串、number 或 number|undefined，转换时检查 NaN 与范围。

客户端校验帮助用户修正输入，服务端仍须重验。异步校验应考虑防抖与过期结果，但把函数标成 async 并不会使其中同步重计算不阻塞主线程。

**练习：** 创建年龄与用户名两字段，验证空值、负数、正常值；提交时显示 isSubmitting，并在失败时保留用户输入。验收：按钮状态随订阅变化，服务端错误能够显示，异步初始数据不会覆盖用户已经编辑的字段。

官方依据：[校验规则](https://tanstack.com/form/latest/docs/framework/react/guides/validation)与[响应式订阅](https://tanstack.com/form/latest/docs/framework/react/guides/reactivity)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
