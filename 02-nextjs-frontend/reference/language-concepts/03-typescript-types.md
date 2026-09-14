# TypeScript 类型速查手册

> **文档简介**: TypeScript 5核心类型和实用类型快速参考，涵盖基础类型、高级类型、工具类型等
>
> **目标读者**: TypeScript开发者，需要快速查阅类型语法的开发者
>
> **前置知识**: JavaScript基础、编程基础概念
>
> **预计时长**: 25-45分钟

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `reference` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#typescript5` `#type-system` `#generics` `#utility-types` `#cheatsheet` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

---

## 🔤 基础类型

### 原始类型
```typescript
// 基础原始类型
let name: string = "John"
let age: number = 30
let isActive: boolean = true
let data: null = null
let value: undefined = undefined

// 特殊类型
let anyValue: any = "anything" // 任意类型（避免使用）
let unknownValue: unknown = "unknown" // 未知类型（类型安全）
let voidValue: void = undefined // 无返回值
let neverValue: never = // 永不返回的值

// 字面量类型
let direction: "up" | "down" | "left" | "right" = "up"
let status: "pending" | "success" | "error" = "pending"
let luckyNumber: 7 | 13 | 21 = 7
```

### 数组和元组
```typescript
// 数组类型
let numbers: number[] = [1, 2, 3]
let strings: Array<string> = ["a", "b", "c"]
let mixed: (string | number)[] = [1, "hello", 2]

// 只读数组
let readonlyNumbers: readonly number[] = [1, 2, 3]
// readonlyNumbers[0] = 4 // 错误：只读数组

// 元组类型
let tuple: [string, number] = ["hello", 42]
let threeTuple: [string, number, boolean] = ["hello", 42, true]

// 可选元组元素
let optionalTuple: [string, number?, boolean?] = ["hello"]
optionalTuple = ["hello", 42]
optionalTuple = ["hello", 42, true]

// 剩余元组元素
let restTuple: [string, ...number[]] = ["hello", 1, 2, 3]
```

### 对象类型
```typescript
// 基础对象类型
interface User {
  id: number
  name: string
  email?: string // 可选属性
  readonly createdAt: Date // 只读属性
}

// 对象字面量类型
let person: {
  name: string
  age: number
  address?: {
    street: string
    city: string
  }
} = {
  name: "John",
  age: 30
}

// 计算属性名
const propName = "age"
type UserKeys = {
  [propName]: number
  [key: string]: string | number
}

// 索引签名
interface Dictionary {
  [key: string]: any
}
```

---

## ⚛️ React + TypeScript 类型

### 组件类型
```typescript
import React, { useState, useEffect, ReactNode } from 'react'

// 函数组件类型
interface ButtonProps {
  children: ReactNode
  onClick: () => void
  variant?: 'primary' | 'secondary'
  disabled?: boolean
}

function Button({ children, onClick, variant = 'primary', disabled = false }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`btn btn-${variant}`}
      disabled={disabled}
    >
      {children}
    </button>
  )
}

// 使用泛型的组件
interface ListProps<T> {
  items: T[]
  renderItem: (item: T, index: number) => ReactNode
  keyExtractor: (item: T) => string
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  )
}
```

### Hook 类型
```typescript
// useState 类型
const [count, setCount] = useState<number>(0)
const [user, setUser] = useState<User | null>(null)

// 带泛型的useState
interface ApiResponse<T> {
  data: T
  loading: boolean
  error: string | null
}

const [apiResponse, setApiResponse] = useState<ApiResponse<User>>({
  data: {} as User,
  loading: false,
  error: null
})

// useEffect 类型
useEffect(() => {
  const timer = setTimeout(() => {
    console.log('Timer executed')
  }, 1000)

  return () => clearTimeout(timer)
}, [])

// 带依赖的useEffect
useEffect(() => {
  console.log('Component mounted or count changed')
}, [count])

// useCallback 类型
const handleClick = useCallback((id: number) => {
  onItemClick(id)
}, [onItemClick])

// useMemo 类型
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b)
}, [a, b])

// useRef 类型
const inputRef = useRef<HTMLInputElement>(null)
const timerRef = useRef<NodeJS.Timeout | null>(null)
```

### 事件类型
```typescript
// 表单事件
function FormComponent() {
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    console.log('Form submitted')
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log(event.target.value)
  }

  const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    console.log(event.target.value)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleInputChange} />
      <select onChange={handleSelectChange}>
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
      </select>
    </form>
  )
}

// 鼠标事件
function MouseEventComponent() {
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    console.log('Button clicked', event.clientX, event.clientY)
  }

  const handleMouseOver = (event: React.MouseEvent<HTMLDivElement>) => {
    console.log('Mouse over', event.currentTarget)
  }

  return (
    <div onMouseOver={handleMouseOver}>
      <button onClick={handleClick}>Click me</button>
    </div>
  )
}

// 键盘事件
function KeyboardEventComponent() {
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      console.log('Enter key pressed')
    }
  }

  return <input onKeyDown={handleKeyDown} />
}
```

---

## 🛠️ 高级类型

### 联合类型和交叉类型
```typescript
// 联合类型 (Union Types)
type Status = "pending" | "success" | "error"
type ID = string | number

interface LoadingState {
  status: "loading"
}

interface SuccessState {
  status: "success"
  data: any
}

interface ErrorState {
  status: "error"
  error: string
}

type AsyncState = LoadingState | SuccessState | ErrorState

// 交叉类型 (Intersection Types)
interface Person {
  name: string
  age: number
}

interface Employee {
  id: number
  department: string
}

type EmployeePerson = Person & Employee

const employee: EmployeePerson = {
  name: "John",
  age: 30,
  id: 123,
  department: "Engineering"
}

// 联合类型区分
function processState(state: AsyncState) {
  switch (state.status) {
    case "loading":
      console.log("Loading...")
      break
    case "success":
      console.log("Data:", state.data)
      break
    case "error":
      console.log("Error:", state.error)
      break
  }
}
```

### 条件类型
```typescript
// 基础条件类型
type IsString<T> = T extends string ? true : false
type Test1 = IsString<string> // true
type Test2 = IsString<number> // false

// 条件类型与泛型
type ArrayType<T> = T extends (infer U)[] ? U : never
type StringArray = ArrayType<string[]> // string
type NumberArray = ArrayType<number[]> // number

// 嵌套条件类型
type NonNullable<T> = T extends null | undefined ? never : T
type Test3 = NonNullable<string | null> // string

// 条件类型在函数中的应用
function processValue<T>(value: T): T extends string
  ? string
  : T extends number
    ? number
    : any {
  if (typeof value === "string") {
    return value.toUpperCase() as any
  }
  if (typeof value === "number") {
    return value * 2 as any
  }
  return value
}
```

### 映射类型
```typescript
// 基础映射类型
type ReadonlyType<T> = {
  readonly [K in keyof T]: T[K]
}

type PartialType<T> = {
  [K in keyof T]?: T[K]
}

// 应用映射类型
interface User {
  name: string
  age: number
  email: string
}

type ReadonlyUser = ReadonlyType<User>
type PartialUser = PartialType<User>

// 高级映射类型
type StringifyProperties<T> = {
  [K in keyof T]: T[K] extends string ? T[K] : string
}

type StringifiedUser = StringifyProperties<User>
// 结果: { name: string; age: string; email: string; }

// 条件映射类型
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]
}

type UserGetters = Getters<User>
// 结果: { getName: () => string; getAge: () => number; getEmail: () => string; }
```

---

## 🧰 工具类型 (Utility Types)

### 常用工具类型
```typescript
interface User {
  id: number
  name: string
  email: string
  age: number
}

// Partial<T> - 所有属性变为可选
type PartialUser = Partial<User>
// 结果: { id?: number; name?: string; email?: string; age?: number; }

// Required<T> - 所有属性变为必需
type OptionalUser = {
  id?: number
  name?: string
}
type RequiredUser = Required<OptionalUser>

// Pick<T, K> - 选择特定属性
type UserBasicInfo = Pick<User, 'id' | 'name'>
// 结果: { id: number; name: string; }

// Omit<T, K> - 排除特定属性
type UserWithoutEmail = Omit<User, 'email'>
// 结果: { id: number; name: string; age: number; }

// Record<K, T> - 创建对象类型
type UserRoles = Record<string, 'admin' | 'user' | 'guest'>
const roles: UserRoles = {
  john: 'admin',
  jane: 'user'
}

// Readonly<T> - 所有属性变为只读
type ReadonlyUser = Readonly<User>
const readonlyUser: ReadonlyUser = { id: 1, name: 'John', email: 'j@ex.com', age: 30 }
// readonlyUser.id = 2 // 错误：Cannot assign to 'id' because it is a read-only property
```

### 转换工具类型
```typescript
// Exclude<T, U> - 排除联合类型中的某些类型
type Status = "pending" | "success" | "error" | "loading"
type FinalStatus = Exclude<Status, "pending" | "loading">
// 结果: "success" | "error"

// Extract<T, U> - 提取联合类型中的某些类型
type StringOrNumber = string | number | boolean
type OnlyString = Extract<StringOrNumber, string>
// 结果: string

// NonNullable<T> - 排除 null 和 undefined
type NotNull = NonNullable<string | null | undefined>
// 结果: string

// ReturnType<T> - 获取函数返回类型
function getUser(): User {
  return {} as User
}
type GetUserReturn = ReturnType<typeof getUser> // User

// Parameters<T> - 获取函数参数类型
type GetUserParams = Parameters<typeof getUser> // []

function createUser(name: string, age: number): User {
  return {} as User
}
type CreateUserParams = Parameters<typeof createUser> // [string, number]
```

### 构造器与异步工具类型
```typescript
// InstanceType<T> - 获取类的实例类型
class UserRepo {
  findById(id: number) { return { id } }
}
type Repo = InstanceType<typeof UserRepo>
const repo: Repo = new UserRepo()
repo.findById(1)

// ConstructorParameters<T> - 获取构造函数参数元组类型
class Box {
  constructor(public value: string, public limit?: number) {}
}
type BoxArgs = ConstructorParameters<typeof Box>
// 结果: [value: string, limit?: number | undefined]
const args: BoxArgs = ['hello', 10]

// 常见组合：反射一个依赖类（构造参数 + 实例类型一起拿到）
type RepoCtor = new (...args: ConstructorParameters<typeof UserRepo>) => InstanceType<typeof UserRepo>

// Awaited<T> - 解开 Promise 嵌套，取最终 resolve 的类型（TS 4.5+）
type A1 = Awaited<Promise<number>>           // number
type A2 = Awaited<Promise<Promise<string>>>  // string
async function fetchUser(): Promise<User> { return {} as User }
type FetchedUser = Awaited<ReturnType<typeof fetchUser>>  // User —— async 函数返回值的标准取法
```

### 推断控制工具类型
```typescript
// ThisType<T> - 指定对象字面量内 this 的上下文类型（需 noImplicitThis，strict 默认开启）
type CounterState = { count: number }
type CounterApi = {
  inc(): void
  reset(): void
} & ThisType<CounterState & CounterApi>

function createCounter(): CounterState & CounterApi {
  return {
    count: 0,
    inc() { this.count += 1 },   // this 被推断为 CounterState & CounterApi
    reset() { this.count = 0 },
  }
}

// NoInfer<T> - 阻止该位置的类型参与推断，只能由其他参数"喂"进来（TS 5.4+）
function createPair<T>(first: T, second: NoInfer<T>): [T, T] {
  return [first, second]
}
const pair1 = createPair('a', 'b')   // T 由 first 推断为 string，second 必须同为 string
// const pair2 = createPair('a', 42) // 错误：42 不能赋给 string（second 不再反向影响 T）
```

### 高级工具类型
```typescript
// Uppercase/Lowercase - 字符串大小写转换
type EventName = "click" | "hover"
type UpperEventName = Uppercase<EventName> // "CLICK" | "HOVER"

// Capitalize - 首字母大写
type PropertyName = "name" | "age"
type GetterName = Capitalize<PropertyName> // "Name" | "Age"

// Uncapitalize - 首字母小写
type LowerGetterName = Uncapitalize<GetterName> // "name" | "age"

// 自定义工具类型
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K]
}

type DeepUser = DeepPartial<User>
// 结果: { id?: number; name?: string; email?: string; age?: number; }

type OptionalKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? K : never
}[keyof T]

type RequiredKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? never : K
}[keyof T]

type UserOptionalKeys = OptionalKeys<User> // 检查哪些属性是可选的
type UserRequiredKeys = RequiredKeys<User> // 检查哪些属性是必需的
```

---

## 🎯 泛型 (Generics)

### 基础泛型
```typescript
// 泛型函数
function identity<T>(arg: T): T {
  return arg
}

const stringResult = identity<string>("hello") // string
const numberResult = identity<number>(42) // number

// 泛型约束
interface Lengthwise {
  length: number
}

function logLength<T extends Lengthwise>(arg: T): void {
  console.log(arg.length)
}

logLength("hello") // 5
logLength([1, 2, 3]) // 3
// logLength(42) // 错误：number 没有 length 属性

// 多个泛型参数
function pair<T, U>(first: T, second: U): [T, U] {
  return [first, second]
}

const stringNumberPair = pair("hello", 42) // [string, number]
```

### 泛型接口
```typescript
// 基础泛型接口
interface Box<T> {
  value: T
  getValue(): T
  setValue(value: T): void
}

class StringBox implements Box<string> {
  constructor(private value: string) {}

  getValue(): string {
    return this.value
  }

  setValue(value: string): void {
    this.value = value
  }
}

// 复杂泛型接口
interface Repository<T, ID = number> {
  findById(id: ID): Promise<T | null>
  save(entity: T): Promise<T>
  delete(id: ID): Promise<void>
  findAll(): Promise<T[]>
}

interface User {
  id: number
  name: string
}

class UserRepository implements Repository<User> {
  async findById(id: number): Promise<User | null> {
    // 实现逻辑
    return null
  }

  async save(user: User): Promise<User> {
    // 实现逻辑
    return user
  }

  async delete(id: number): Promise<void> {
    // 实现逻辑
  }

  async findAll(): Promise<User[]> {
    // 实现逻辑
    return []
  }
}
```

### 泛型工具类型
```typescript
// 创建泛型工具类型
type Optionalify<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

interface Product {
  id: number
  name: string
  price: number
  description: string
}

type CreateProduct = Optionalify<Product, 'id' | 'description'>
// 结果: { name: string; price: number; id?: number; description?: string; }

// 条件泛型类型
type ApiResponse<T> = {
  data: T
  success: boolean
  message?: string
}

type ErrorApiResponse = ApiResponse<null> & { error: string }

// 使用泛型的工厂函数
function createApiResponse<T>(
  data: T,
  success: boolean = true,
  message?: string
): ApiResponse<T> {
  return { data, success, message }
}

const successResponse = createApiResponse({ id: 1, name: "Product" })
const errorResponse = createApiResponse(null, false, "Not found")
```

---

## 🔧 TypeScript 5 新特性

### const 断言
```typescript
// const 断言创建不可变类型
const colors = ["red", "green", "blue"] as const
// 类型: readonly ["red", "green", "blue"]

const config = {
  apiUrl: "https://api.example.com",
  timeout: 5000,
  retries: 3
} as const
// 类型: { readonly apiUrl: "https://api.example.com"; readonly timeout: 5000; readonly retries: 3; }

// 在函数中使用
function getApiConfig(): typeof config {
  return config
}
```

### Template Literal 类型
```typescript
// 模板字面量类型
type EventName = `on${Capitalize<string>}`
type ClickEvent = EventName & `on${string}`

// 动态属性名
interface ThemeConfig {
  [K in `color${Capitalize<string>}`]: string
}

const theme: ThemeConfig = {
  colorPrimary: "#007bff",
  colorSecondary: "#6c757d",
  colorSuccess: "#28a745"
}

// 路径构建
type ApiPath = `/api/${string}`
type UserPath = `${ApiPath}/users/${number}`

const userPath: UserPath = "/api/users/123"
```

### satisfies 操作符 (TypeScript 4.9+)
```typescript
// satisfies 操作符 - 验证类型但不改变类型
const palette = {
  red: "#ff0000",
  green: "#00ff00",
  blue: "#0000ff"
} satisfies Record<string, string>

// palette 仍然是具体对象类型，而不是 Record<string, string>

// 在 React 组件中使用
const buttonVariants = {
  primary: "bg-blue-500 text-white",
  secondary: "bg-gray-500 text-white"
} satisfies Record<string, string>

function Button({ variant }: { variant: keyof typeof buttonVariants }) {
  return <button className={buttonVariants[variant]}>Click</button>
}
```

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[React 语法速查](./01-react-syntax-cheatsheet.md)**: React核心语法和组件类型定义
- 📄 **[Next.js API 参考](./02-nextjs-api-reference.md)**: Next.js 框架的TypeScript类型定义
- 📄 **[现代 JavaScript 语法速查](./04-javascript-modern.md)**: ES6+语法特性，TypeScript的基础
- 📄 **[CSS 模式速查](./05-css-patterns.md)**: CSS-in-JS的TypeScript类型定义

### 参考章节
- 📖 **[客户端组件模式](../framework-patterns/03-client-components-patterns.md)**: React组件TypeScript最佳实践
- 📖 **[状态管理模式](../framework-patterns/05-state-management-patterns.md)**: 状态管理的TypeScript类型设计
- 📖 **[表单验证模式](../framework-patterns/06-form-validation-patterns.md)**: 表单数据的类型安全验证
- 📖 **[TypeScript 集成基础](../../basics/03-typescript-integration.md)**: Next.js项目中TypeScript配置和使用
- 📖 **[Tailwind CSS 样式](../../basics/05-styling-with-tailwind.md)**: 样式类的TypeScript类型定义

## 📝 总结

### 核心要点回顾
1. **基础类型系统**: 掌握了TypeScript的原始类型、数组、元组和对象类型的定义和使用方法
2. **React + TypeScript**: 学会了为React组件、Hooks和事件定义准确的类型，提升开发体验
3. **高级类型特性**: 理解了联合类型、交叉类型、条件类型和映射类型的概念和应用场景
4. **工具类型应用**: 熟练使用内置工具类型进行类型转换和操作，提高代码复用性
5. **泛型编程**: 掌握了泛型函数、泛型接口的设计，编写类型安全且灵活的代码

### 学习成果检查
- [ ] 是否理解了TypeScript类型系统的核心概念？
- [ ] 是否能够为React组件定义准确的Props和State类型？
- [ ] 是否能够熟练使用工具类型进行类型操作？
- [ ] 是否能够设计泛型函数和泛型接口？
- [ ] 是否具备了处理复杂类型场景的能力？

## 🤝 贡献与反馈

### 内容改进
如果你发现本文档有改进空间，欢迎：
- 🐛 **报告问题**: 在Issues中提出具体问题
- 💡 **建议改进**: 提出修改建议和补充内容
- 📝 **参与贡献**: 提交PR完善文档内容

### 学习反馈
分享你的学习体验：
- ✅ **有用内容**: 哪些部分对你最有帮助
- ❓ **疑问点**: 哪些内容需要进一步澄清
- 🎯 **建议**: 希望增加什么内容

## 🔗 外部资源

### 官方文档
- 📖 **[TypeScript 5 官方文档](https://www.typescriptlang.org/docs/)**: 完整TypeScript文档和类型系统说明
- 📖 **[React + TypeScript 手册](https://react-typescript-cheatsheet.netlify.app/)**: React TypeScript完整指南
- 📖 **[TypeScript 深入理解](https://basarat.gitbook.io/typescript/)**: TypeScript深度学习资料

### 快速参考

### 基础类型
- `string`、`number`、`boolean` - 原始类型
- `array[]` 或 `Array<T>` - 数组类型
- `[T, U]` - 元组类型
- `{ key: T }` - 对象类型
- `T | U` - 联合类型
- `T & U` - 交叉类型

### React 类型
- `ReactNode` - 可渲染内容
- `React.FC<Props>` - 函数组件类型
- `React.ChangeEvent<T>` - 表单变更事件
- `React.MouseEvent<T>` - 鼠标事件
- `React.FormEvent<T>` - 表单事件

### 工具类型
- `Partial<T>` - 所有属性可选
- `Required<T>` - 所有属性必需
- `Readonly<T>` - 所有属性只读
- `Pick<T, K>` - 选择特定属性
- `Omit<T, K>` - 排除特定属性
- `Record<K, T>` - 创建对象类型

### TypeScript 5 新特性
- `const` 断言 - 创建不可变类型
- `satisfies` 操作符 - 类型验证但不改变类型
- Template Literal 类型 - 动态字符串类型

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0