# useField 与 createFormHook：字段复用与表单工厂

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

Form 的字段消费有两条进阶路径：`useField`（独立 Hook 形式）直接从 form 实例订阅单个字段——内置的 `form.Field` 组件内部正是用它实现的；`createFormHook`（工厂形式）把"一组字段组件 + 一组表单组件 + 两个 Context"打包成私有 Hook 家族（`useAppForm`/`AppField`/`AppForm`/`withForm`），让可复用字段组件不再逐层透传 form。校验器（validator）用法见 [Form 核心 API](./04-form-core-api.md)，本篇只讲结构复用。

## 📖 语法 / 签名

```ts
// —— Hook 形式 ——
const field = useField({ form, name: 'age' })
// field: { name, state: { value, meta: { errors, ... } }, handleChange, handleBlur, ... }

// —— 工厂形式 ——
const { fieldContext, useFieldContext, formContext, useFormContext } = createFormHookContexts()
useFieldContext<string>()   // 字段组件内取 field（泛型标注值类型）
useFormContext()            // 表单组件内取 form

const formHook = createFormHook({
  fieldComponents: { TextField },   // 注册后经 field.<组件名> 调用
  formComponents: { SubmitButton }, // 注册后经 form.<组件名> 调用
  fieldContext,
  formContext,
})

formHook.useAppForm({ defaultValues, onSubmit, /* 同 useForm 选项 */ })
formHook.withForm({ defaultValues, onSubmit, props, render }) // 跨组件拆分渲染
```

| 成员 | 说明 |
|------|------|
| `form.AppField` | render prop 内的 `field` 对象携带已注册字段组件（`field.TextField`） |
| `form.AppForm` | 子树注入 formContext，表单组件经 `form.SubmitButton` 调用 |
| `formHook.withForm` | 声明式渲染切片；**必须在此重复声明** `defaultValues`/`onSubmit` 才有类型 |
| `useField` | 独立于工厂可用；`form.useField` 形式不存在（v1.33 时代） |

## 💡 示例

```tsx
import { useForm, useField, createFormHook, createFormHookContexts } from '@tanstack/react-form'

// —— Hook 形式：不套 Field 组件，直接订阅 ——
function HookForm() {
  const form = useForm({
    defaultValues: { username: '', age: 0 },
    onSubmit: ({ value }) => console.log(value),
  })
  const ageField = useField({ form, name: 'age' })
  const usernameField = useField({ form, name: 'username' })
  return (
    <form onSubmit={(e) => { e.preventDefault(); void form.handleSubmit() }}>
      <input
        name={ageField.name}
        value={ageField.state.value}
        onBlur={ageField.handleBlur}
        onChange={(e) => ageField.handleChange(Number(e.target.value))}
      />
      <input
        value={usernameField.state.value}
        onBlur={usernameField.handleBlur}
        onChange={(e) => usernameField.handleChange(e.target.value)}
      />
    </form>
  )
}

// —— 工厂形式：可复用字段组件只依赖 Context，不接收 form prop ——
const { fieldContext, useFieldContext, formContext, useFormContext } = createFormHookContexts()

function TextField({ label }: { label: string }) {
  const field = useFieldContext<string>()
  return (
    <label>
      {label}
      <input
        value={field.state.value}
        onBlur={field.handleBlur}
        onChange={(e) => field.handleChange(e.target.value)}
      />
      {field.state.meta.errors.map((err) => (
        <span key={String(err)}>{String(err)}</span>
      ))}
    </label>
  )
}

function SubmitButton({ label }: { label: string }) {
  const form = useFormContext()
  return <button type="submit" disabled={!form.state.canSubmit}>{label}</button>
}

const formHook = createFormHook({
  fieldComponents: { TextField },
  formComponents: { SubmitButton },
  fieldContext,
  formContext,
})

function FactoryForm() {
  const form = formHook.useAppForm({
    defaultValues: { username: '', age: 0 },
    onSubmit: ({ value }) => console.log(value),
  })
  return (
    <form onSubmit={(e) => { e.preventDefault(); void form.handleSubmit() }}>
      {/* AppField 注入 fieldContext；字段组件经 field 扩展属性调用 */}
      <form.AppField name="username">
        {(field) => <field.TextField label="用户名" />}
      </form.AppField>
      {/* AppForm 注入 formContext；表单组件经 form 扩展属性调用 */}
      <form.AppForm>
        <form.SubmitButton label="提交" />
      </form.AppForm>
    </form>
  )
}

// —— withForm：把渲染切片拆成独立"组件"，不经过 JSX prop 传 form ——
const SubmitSection = formHook.withForm({
  defaultValues: { username: '', age: 0 },  // 重复声明以获得类型
  onSubmit: ({ value }) => console.log(value.username),
  props: { note: '' },
  render: ({ form, note }) => (
    <div>
      <span>{note}</span>
      <form.SubmitButton label="保存" />
      <span>{form.state.values.username}</span>
    </div>
  ),
})

function WithFormParent() {
  const form = formHook.useAppForm({
    defaultValues: { username: '', age: 0 },
    onSubmit: ({ value }) => console.log(value),
  })
  return <SubmitSection form={form} note="保存后不可撤销" />
}
```

## ⚠️ 常见陷阱

- ❌ 找 `form.useField(...)` 绑定方法：不存在——独立 Hook 是 `useField({ form, name })`
- ❌ 字段组件仍用 props 传 `form`：工厂形式的意义就是 Context 注入；需要跨树传 form 时才用 `withForm`
- ❌ `withForm` 里不声明 `defaultValues`/`onSubmit`：类型推断失败，`form.state.values` 退化为 unknown——声明式重复是官方约定
- ❌ `useFieldContext()` 不写泛型：值类型推断为未知——`useFieldContext<string>()` 显式标注
- ❌ 在普通 `useForm` 的树里用 `<field.TextField>`：扩展属性只在 `useAppForm` + `AppField` 组合下存在
- ❌ 渲染 `meta.errors` 不做 key/序列化：错误项可能是对象（validator 返回值），直接当 ReactNode 用会告警
- ✅ 表单组件读 `form.state.canSubmit`/`isSubmitting` 控制按钮禁用

## 🔗 相关条目

- 📄 **[Form 核心 API](./04-form-core-api.md)** - useForm/Field/validator 与 form.Subscribe
- 📄 **[Form 基础教程](../../basics/06-form-fundamentals.md)** - 表单入门与状态机
- 📄 **[TypeScript 模式](./05-typescript-patterns.md)** - 泛型标注与类型收窄
- 📄 **[协同看板项目](../../projects/03-collaborative-kanban.md)** - 复杂表单的工程化拆分
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - 一行式签名

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
