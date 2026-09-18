# Form 基础：useForm 与字段绑定

## 先理解，再动手

表单同时管理输入值、是否触碰、校验结果与提交状态。显示错误的时机与校验规则是两个决定。

**本节自测**：输入空标题、只含空格的标题和合法标题，尝试重复点击提交。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

空白被拒绝，合法输入可提交；等待中防止重复动作，服务端仍要独立校验。

</details>

> **文档简介**: 上手 TanStack Form v1——用 useForm 管理表单状态、用 Field 渲染属性绑定输入框、用校验器完成第一道数据把关
>
> **目标读者**: 写过受控表单、被 useEffect 同步表单状态折磨过的开发者
>
> **前置知识**: React 受控组件概念、[Headless 设计哲学](./02-headless-philosophy.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `03-tanstack-stack` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#TanStack-Form` `#useForm` `#Field` `#校验` |
| **更新日期** | `2026年9月` |

</details>

## 🎯 学习目标

完成本文档后，你将能够：

- ✅ 用 `useForm` 声明表单初始值与提交逻辑
- ✅ 用 `<form.Field>` 渲染属性绑定每个输入框
- ✅ 在字段级与表单级两个层级配置校验
- ✅ 用 `form.Subscribe` 读取跨字段的派生状态

---

## 🔍 为什么表单也需要 Headless

表单的难点从来不是 `<input>`，而是：脏检查、touched 状态、异步校验、提交中禁用、跨字段联动。TanStack Form 把这些状态机做成了 Headless API，输入框长什么样由你决定。

## 🛠️ 实践：注册表单

### 步骤一：useForm 声明表单

```tsx
import { useForm } from '@tanstack/react-form'

type SignupValues = {
  username: string
  email: string
  age: number
}

function SignupForm() {
  const form = useForm({
    defaultValues: {
      username: '',
      email: '',
      age: 0,
    } satisfies SignupValues,
    onSubmit: async ({ value }) => {
      // value 的类型精确为 SignupValues
      await api.signup(value)
      console.log('提交成功', value)
    },
  })

  return null // 下一步填充 JSX
}
```

### 步骤二：字段绑定与渲染

```tsx
<form
  onSubmit={(e) => {
    e.preventDefault()
    e.stopPropagation()
    form.handleSubmit()
  }}
>
  {/* name 必须是 defaultValues 中的键，写错直接编译报错 */}
  <form.Field
    name="username"
    validators={{
      // 函数校验器：返回错误字符串或 undefined
      onChange: ({ value }) =>
        value.length < 3 ? '用户名至少 3 个字符' : undefined,
    }}
  >
    {(field) => (
      <label>
        用户名
        <input
          name={field.name}
          value={field.state.value}
          onBlur={field.handleBlur}
          onChange={(e) => field.handleChange(e.target.value)}
        />
        {/* meta.errors 是数组；isValid 是现成的无错标志 */}
        {!field.state.meta.isValid && (
          <em>{field.state.meta.errors.map(String).join(', ')}</em>
        )}
      </label>
    )}
  </form.Field>

  <form.Field name="email">
    {(field) => (
      <label>
        邮箱
        <input
          name={field.name}
          type="email"
          value={field.state.value}
          onBlur={field.handleBlur}
          onChange={(e) => field.handleChange(e.target.value)}
        />
      </label>
    )}
  </form.Field>

  <button type="submit">注册</button>
</form>
```

**关键点解析**：

- `field.state.value` 读值、`field.handleChange` 写值，二者配合实现受控组件
- `field.handleBlur` 触发 touched 标记，让 `onBlur` 校验成为可能
- `field.state.meta.errors` 是**数组**；函数校验器返回字符串数组，Standard Schema 返回带 `message` 的对象数组

### 步骤三：表单级校验（Standard Schema）

TanStack Form v1 原生支持 Standard Schema，Zod/Valibot/ArkType 的 schema 可以直接传入：

```tsx
import { z } from 'zod'

const schema = z.object({
  username: z.string().min(3, '用户名至少 3 个字符'),
  email: z.string().email('邮箱格式不正确'),
  age: z.number().min(18, '需年满 18 岁'),
})

const form = useForm({
  defaultValues: { username: '', email: '', age: 0 },
  validators: {
    // 提交时整表校验，错误自动分发到对应字段
    onSubmit: schema,
  },
  onSubmit: async ({ value }) => {
    await api.signup(value)
  },
})
```

### 步骤四：Subscribe 读取派生状态

```tsx
<form.Subscribe selector={(state) => state.canSubmit}>
  {(canSubmit) => (
    <button type="submit" disabled={!canSubmit}>
      注册
    </button>
  )}
</form.Subscribe>
```

`selector` 精确订阅所需状态，避免整表重渲染。常用状态：`canSubmit`、`isSubmitting`、`isDirty`、`errors`。

## ✅ 最佳实践

字段校验适合及时提示“这个邮箱格式不对”，表单校验适合检查“结束时间早于开始时间”等字段关系；服务端仍须重新校验，客户端反馈不能成为信任边界。同步与异步的区别取决于是否要等待外部结果，而不是规则看起来复杂与否。

检查用户名是否占用时，应防抖并处理旧响应晚于新响应的情况：连续输入 A、B，即使 A 最后返回，也不能覆盖 B 的提示。输入组件通过库提供的订阅接口观察字段变化，避免只读取一个不会触发更新的状态快照。

---

## 🎯 练习与实践

### 练习一：最小表单

- [ ] 实现用户名/邮箱两个字段：字段级校验即时提示，提交时打印 value
- [ ] 给提交按钮加 `isSubmitting` 状态防重复提交

### 练习二：Schema 收编

- [ ] 把练习一的字段校验全部迁移到 Zod schema（`onSubmit` + `onChange` 两个时机）
- [ ] 用 `form.Subscribe` 实现"有任一错误时按钮禁用"（提示：订阅 `state.errors`）

---

## 🔗 相关文档

- 📄 **[高级特性](./07-advanced-features.md)** - 下一篇：Query 的乐观更新与无限查询
- 📄 **[Form 核心 API](../reference/language-concepts/04-form-core-api.md)** - useForm/useField 完整字典
- 📄 **[TypeScript 模式](../reference/language-concepts/05-typescript-patterns.md)** - 表单类型的推断与收窄

---

**最后更新**: 2026年9月 | Dev Quest · 03-tanstack-stack


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
