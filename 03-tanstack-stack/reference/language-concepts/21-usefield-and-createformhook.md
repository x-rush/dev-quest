# useField 与 createFormHook：字段复用与表单工厂

> **模块**: `03-tanstack-stack` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

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
| `formHook.withForm` | 声明式渲染切片；使用一致的表单选项获得类型，可提取共享 formOptions 复用 |
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
  return <form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting] as const}>
    {([canSubmit, isSubmitting]) => <button type="submit" disabled={!canSubmit || isSubmitting}>{label}</button>}
  </form.Subscribe>
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

// —— withForm：把渲染切片拆成独立"组件"，通过 form prop 传入有类型的表单实例 ——
const SubmitSection = formHook.withForm({
  defaultValues: { username: '', age: 0 },  // 重复声明以获得类型
  onSubmit: ({ value }) => console.log(value.username),
  props: { note: '' },
  render: ({ form, note }) => (
    <div>
      <span>{note}</span>
      <form.SubmitButton label="保存" />
      <form.Subscribe selector={(state) => state.values.username}>
        {(username) => <span>{username}</span>}
      </form.Subscribe>
    </div>
  ),
})

function WithFormParent() {
  const form = formHook.useAppForm({
    defaultValues: { username: '', age: 0 },
    onSubmit: ({ value }) => console.log(value),
  })
  return <form onSubmit={(event) => { event.preventDefault(); void form.handleSubmit(); }}>
    <form.AppForm><SubmitSection form={form} note="请检查输入后保存" /></form.AppForm>
  </form>
}
```

## ⚠️ 常见陷阱

- ❌ 找 `form.useField(...)` 绑定方法：不存在——独立 Hook 是 `useField({ form, name })`
- ❌ 混用不匹配的 Context：字段和工厂必须使用同一组 createFormHookContexts；简单组件通过 props 传 form 也可以是合理选择
- 类型复用：用一致的表单选项（可提取共享 formOptions）帮助 withForm 推断；不要为每个渲染切片重复实现提交逻辑，具体泛型以所用版本为准。
- ❌ `useFieldContext()` 不写泛型：值类型推断为未知——`useFieldContext<string>()` 显式标注
- ❌ 在普通 `useForm` 的树里用 `<field.TextField>`：扩展属性只在 `useAppForm` + `AppField` 组合下存在
- ❌ 渲染 `meta.errors` 不做 key/序列化：错误项可能是对象（validator 返回值），直接当 ReactNode 用会告警
- ✅ 表单组件通过 form.Subscribe 订阅 canSubmit/isSubmitting 后控制按钮禁用

<!-- full-library-explanation -->
## 复用边界：字段 UI、表单上下文和提交入口

先修：Form Field、React Context、Subscribe。createFormHook 注册通用字段组件，AppField 提供对应字段上下文；AppForm 提供表单上下文，但不会自动生成 HTML form，也不会自动绑定提交事件。

useFieldContext<string> 表达该输入组件期待字符串，不能运行时验证任意字段都真是字符串。数字组件应有独立的转换与空值规则，不要用同一个 TextField 强制吞掉不同值类型。

withForm 是让拆分组件保留表单类型的工具，父组件仍通过 form prop 传入实例。共享 formOptions 可减少重复声明；不能为了类型提示在子片段重复实现一套提交业务。

**练习：** 两个表单复用同一用户名字段与提交按钮，各自输入不同值。验收：上下文不串表单，按钮会响应提交状态，按 Enter 与点击按钮触发同一提交路径。参考[表单组合](https://tanstack.com/form/latest/docs/framework/react/guides/form-composition)。

## 🔗 相关条目

- 📄 **[Form 核心 API](./04-form-core-api.md)** - useForm/Field/validator 与 form.Subscribe
- 📄 **[Form 基础教程](../../basics/06-form-fundamentals.md)** - 表单入门与状态机
- 📄 **[TypeScript 模式](./05-typescript-patterns.md)** - 泛型标注与类型收窄
- 📄 **[协同看板项目](../../projects/03-collaborative-kanban.md)** - 复杂表单的工程化拆分
- 📄 **[语法速查](../quick-references/01-syntax-cheatsheet.md)** - 一行式签名

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
