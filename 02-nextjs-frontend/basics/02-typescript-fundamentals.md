# TypeScript 基础 - 为现代 React 开发打基础

## 概述

TypeScript 是 JavaScript 的超集，为代码添加了静态类型系统。作为 PHP 开发者，你已经习惯了静态类型检查，这会让 TypeScript 的学习更加自然。本指南将帮助你快速掌握 TypeScript 核心概念，为 Next.js 和 React 19 开发打下坚实基础。

## 为什么选择 TypeScript

### 对比 PHP 的类型系统

| PHP 类型系统 | TypeScript 类型系统 |
|-------------|-------------------|
| 动态类型为主 | 静态类型优先 |
| 运行时类型检查 | 编译时类型检查 |
| 类型声明可选 | 类型声明推荐 |
| 弱类型 | 强类型 + 类型推断 |
| 简单类型系统 | 丰富的类型系统 |

### TypeScript 的优势
- **类型安全**: 在编译时捕获类型错误
- **IDE 支持**: 更好的代码补全和重构
- **代码文档**: 类型即文档
- **重构支持**: 安全的大规模重构
- **团队协作**: 统一的类型契约

## 基础类型

### 1. 基本类型

```typescript
// 字符串类型
let name: string = "张三";
let greeting: string = `Hello, ${name}!`;

// 数字类型 (PHP 对比: int, float)
let age: number = 25;
let price: number = 99.99;
let hex: number = 0xff; // 255

// 布尔类型
let isActive: boolean = true;
let hasPermission: boolean = false;

// null 和 undefined
let nullable: null = null;
let undefinedVar: undefined = undefined;

// any 类型 (慎用，相当于 PHP 的 mixed)
let anything: any = "可以是任何类型";
anything = 42;
anything = true;

// void 类型 (PHP 对比: 函数无返回值)
function logMessage(message: string): void {
  console.log(message);
}

// never 类型 (表示永不返回)
function throwError(message: string): never {
  throw new Error(message);
}
```

### 2. 字面量类型

```typescript
// 字符串字面量
type Direction = "up" | "down" | "left" | "right";
let moveDirection: Direction = "up";

// 数字字面量
type Dice = 1 | 2 | 3 | 4 | 5 | 6;
let diceRoll: Dice = 6;

// 布尔字面量
type Status = "success" | "error" | "loading";
let apiStatus: Status = "loading";
```

## 复杂类型

### 1. 数组和元组

```typescript
// 数组类型 (PHP 对比: array)
let numbers: number[] = [1, 2, 3, 4, 5];
let fruits: Array<string> = ["apple", "banana", "orange"];

// 多维数组
let matrix: number[][] = [
  [1, 2, 3],
  [4, 5, 6],
  [7, 8, 9]
];

// 元组类型 (固定长度和类型的数组)
let person: [string, number, boolean] = ["张三", 25, true];
let coordinates: [number, number] = [116.4074, 39.9042]; // 经纬度

// 元组解构
let [name, age, isActive] = person;
```

### 2. 对象类型

```typescript
// 基本对象类型
let user: {
  name: string;
  age: number;
  isActive: boolean;
} = {
  name: "张三",
  age: 25,
  isActive: true
};

// 可选属性 (PHP 对比: ? 属性)
let product: {
  id: number;
  name: string;
  price?: number; // 可选属性
  description?: string;
} = {
  id: 1,
  name: "商品",
  price: 99.99
};

// 只读属性
let config: {
  readonly apiUrl: string;
  readonly timeout: number;
} = {
  apiUrl: "https://api.example.com",
  timeout: 5000
};

// 索引签名 (PHP 对比: 动态属性)
let dictionary: {
  [key: string]: string;
} = {
  "hello": "你好",
  "world": "世界"
};
```

### 3. 函数类型

```typescript
// 函数声明
function add(a: number, b: number): number {
  return a + b;
}

// 函数表达式
const multiply: (a: number, b: number) => number = (a, b) => a * b;

// 可选参数
function greet(name: string, greeting?: string): string {
  return greeting ? `${greeting}, ${name}!` : `Hello, ${name}!`;
}

// 默认参数
function createEmail(
  to: string,
  subject: string = "无主题",
  body: string = ""
): string {
  return `To: ${to}\nSubject: ${subject}\n\n${body}`;
}

// 剩余参数
function sum(...numbers: number[]): number {
  return numbers.reduce((acc, curr) => acc + curr, 0);
}

// 函数重载 (PHP 对比: 方法重载)
function processInput(input: string): string;
function processInput(input: number): number;
function processInput(input: string | number): string | number {
  if (typeof input === "string") {
    return input.toUpperCase();
  } else {
    return input * 2;
  }
}
```

## 接口和类型别名

### 1. 接口 (Interface)

```typescript
// 基本接口定义
interface User {
  id: number;
  name: string;
  email: string;
  age?: number; // 可选属性
}

// 使用接口
const user: User = {
  id: 1,
  name: "张三",
  email: "zhangsan@example.com"
};

// 只读接口
interface Config {
  readonly apiUrl: string;
  readonly timeout: number;
}

// 函数接口
interface SearchFunction {
  (query: string, page: number): Promise<User[]>;
}

// 接口继承
interface Admin extends User {
  permissions: string[];
  role: "admin" | "super_admin";
}

const admin: Admin = {
  id: 1,
  name: "管理员",
  email: "admin@example.com",
  permissions: ["read", "write", "delete"],
  role: "admin"
};
```

### 2. 类型别名 (Type Alias)

```typescript
// 基本类型别名
type Age = number;
type Name = string;
type ID = string | number;

// 对象类型别名
type Point = {
  x: number;
  y: number;
};

// 联合类型
type Status = "pending" | "success" | "error" | "loading";
type Result = Success | Error;

type Success = {
  type: "success";
  data: any;
};

type Error = {
  type: "error";
  message: string;
};

// 交叉类型
type Person = {
  name: string;
  age: number;
};

type Employee = {
  employeeId: number;
  department: string;
};

type Staff = Person & Employee;

const staff: Staff = {
  name: "张三",
  age: 25,
  employeeId: 1001,
  department: "技术部"
};
```

## 高级类型

### 1. 泛型 (Generics)

```typescript
// 基本泛型
function identity<T>(arg: T): T {
  return arg;
}

let output = identity<string>("Hello TypeScript");
let output2 = identity(42); // 类型推断为 number

// 数组泛型
function getFirst<T>(arr: T[]): T | undefined {
  return arr[0];
}

let firstNumber = getFirst([1, 2, 3]); // number | undefined
let firstString = getFirst(["a", "b", "c"]); // string | undefined

// 接口泛型
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

interface User {
  id: number;
  name: string;
}

const userResponse: ApiResponse<User> = {
  success: true,
  data: {
    id: 1,
    name: "张三"
  }
};

// 泛型约束
interface HasLength {
  length: number;
}

function logLength<T extends HasLength>(arg: T): T {
  console.log(`Length: ${arg.length}`);
  return arg;
}

logLength("Hello"); // OK
logLength([1, 2, 3]); // OK
logLength(42); // Error: number 没有 length 属性
```

### 2. 类型守卫

```typescript
// typeof 类型守卫
function processValue(value: string | number) {
  if (typeof value === "string") {
    // 在这个分支中，value 的类型是 string
    return value.toUpperCase();
  } else {
    // 在这个分支中，value 的类型是 number
    return value * 2;
  }
}

// in 操作符类型守卫
interface Dog {
  bark: () => void;
}

interface Cat {
  meow: () => void;
}

function makeSound(animal: Dog | Cat) {
  if ("bark" in animal) {
    animal.bark(); // animal 是 Dog
  } else {
    animal.meow(); // animal 是 Cat
  }
}

// 自定义类型守卫
function isString(value: any): value is string {
  return typeof value === "string";
}

function processInput(input: string | number) {
  if (isString(input)) {
    return input.toUpperCase(); // input 是 string
  } else {
    return input.toFixed(2); // input 是 number
  }
}
```

### 3. 工具类型

```typescript
// Partial - 所有属性可选
interface Todo {
  title: string;
  description: string;
  completed: boolean;
}

type PartialTodo = Partial<Todo>;
// 等价于:
// type PartialTodo = {
//   title?: string;
//   description?: string;
//   completed?: boolean;
// }

// Required - 所有属性必需
type RequiredTodo = Required<Todo>;

// Pick - 选择特定属性
type TodoPreview = Pick<Todo, "title" | "completed">;

// Omit - 排除特定属性
type TodoWithoutDescription = Omit<Todo, "description">;

// Record - 创建对象类型
type UserRoles = Record<string, "admin" | "user" | "guest">;

// Exclude - 排除类型
type AllRoles = "admin" | "user" | "guest" | "bot";
type HumanRoles = Exclude<AllRoles, "bot">;

// Extract - 提取类型
type AdminRoles = Extract<AllRoles, "admin" | "guest">;
```

## 实用模式

### 1. 枚举 (Enum)

```typescript
// 数字枚举
enum Direction {
  Up = 1,
  Down = 2,
  Left = 3,
  Right = 4
}

// 字符串枚举
enum HttpStatus {
  OK = "200",
  Created = "201",
  BadRequest = "400",
  Unauthorized = "401",
  NotFound = "404"
}

// 使用枚举
function handleResponse(status: HttpStatus) {
  switch (status) {
    case HttpStatus.OK:
      return "请求成功";
    case HttpStatus.NotFound:
      return "资源不存在";
    default:
      return "未知状态";
  }
}
```

### 2. 命名空间 (Namespace)

```typescript
namespace App.Utils {
  export function formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  export function validateEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
}

// 使用命名空间
const formattedDate = App.Utils.formatDate(new Date());
const isValid = App.Utils.validateEmail("test@example.com");
```

### 3. 装饰器 (Decorator)

```typescript
// 类装饰器
function logClass(target: Function) {
  console.log(`Class ${target.name} is defined`);
}

@logClass
class UserService {
  // ...
}

// 方法装饰器
function logMethod(target: any, key: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = function(...args: any[]) {
    console.log(`Method ${key} called with args:`, args);
    const result = originalMethod.apply(this, args);
    console.log(`Method ${key} returned:`, result);
    return result;
  };
}

class Calculator {
  @logMethod
  add(a: number, b: number): number {
    return a + b;
  }
}
```

## 配置文件

### tsconfig.json 配置

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "incremental": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

## 与 PHP 开发的对比

### 类型系统对比

| PHP | TypeScript |
|-----|------------|
| `string $name = "张三";` | `let name: string = "张三";` |
| `int $age = 25;` | `let age: number = 25;` |
| `array $numbers = [1, 2, 3];` | `let numbers: number[] = [1, 2, 3];` |
| `function add(int $a, int $b): int` | `function add(a: number, b: number): number` |
| `?string $name = null;` | `name: string | null = null;` |
| `array|stdClass $data;` | `data: object | Array<any>;` |

### 开发体验对比

1. **类型检查时机**
   - PHP: 运行时类型检查
   - TypeScript: 编译时类型检查

2. **IDE 支持**
   - PHP: 基本代码补全
   - TypeScript: 强大的类型推断和重构支持

3. **错误发现**
   - PHP: 运行时才能发现类型错误
   - TypeScript: 编译时就能发现类型错误

4. **类型系统**
   - PHP: 相对简单的类型系统
   - TypeScript: 丰富的类型系统（泛型、联合类型、工具类型等）

## 最佳实践

### 1. 类型定义原则
- **优先使用类型推断**: 让 TypeScript 自动推断类型
- **明确接口边界**: 公共 API 明确指定类型
- **避免 any 类型**: 使用 unknown 或具体类型
- **合理使用泛型**: 提高代码复用性

### 2. 代码组织
- **按功能模块组织**: 相关类型定义放在一起
- **统一命名规范**: 接口使用 PascalCase，类型别名使用 PascalCase
- **分层类型定义**: 基础类型 → 业务类型 → API 类型

### 3. 性能考虑
- **避免过度类型化**: 保持类型系统的简洁性
- **合理使用工具类型**: 提高类型定义的复用性
- **避免循环引用**: 防止类型定义的循环依赖

## 练习项目

### 1. 类型安全的用户管理系统
```typescript
// 定义用户类型
interface User {
  id: string;
  name: string;
  email: string;
  age: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// 定义 API 响应类型
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 实现用户管理类
class UserManager {
  private users: Map<string, User> = new Map();

  createUser(userData: Omit<User, "id" | "createdAt" | "updatedAt">): User {
    const user: User = {
      id: Math.random().toString(36).substr(2, 9),
      ...userData,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.users.set(user.id, user);
    return user;
  }

  getUser(id: string): User | undefined {
    return this.users.get(id);
  }

  updateUser(id: string, updates: Partial<User>): User | undefined {
    const user = this.users.get(id);
    if (!user) return undefined;

    const updatedUser = {
      ...user,
      ...updates,
      updatedAt: new Date()
    };

    this.users.set(id, updatedUser);
    return updatedUser;
  }

  deleteUser(id: string): boolean {
    return this.users.delete(id);
  }

  listUsers(): User[] {
    return Array.from(this.users.values());
  }
}
```

### 2. 类型安全的表单验证
```typescript
// 定义表单验证规则
interface ValidationRule<T> {
  required?: boolean;
  min?: number;
  max?: number;
  pattern?: RegExp;
  custom?: (value: T) => string | null;
}

// 定义表单字段
interface FormField<T> {
  value: T;
  error?: string;
  rules: ValidationRule<T>;
}

// 定义表单状态
interface FormState<T> {
  [key: string]: FormField<any>;
}

// 表单验证器类
class FormValidator<T extends FormState<any>> {
  private formState: T;

  constructor(initialState: T) {
    this.formState = { ...initialState };
  }

  validateField<K extends keyof T>(fieldName: K): boolean {
    const field = this.formState[fieldName];
    const { value, rules } = field;

    // 清除之前的错误
    field.error = undefined;

    // 必填验证
    if (rules.required && (value === null || value === undefined || value === "")) {
      field.error = "此字段为必填项";
      return false;
    }

    // 最小长度验证
    if (rules.min !== undefined && typeof value === "string" && value.length < rules.min) {
      field.error = `最小长度为 ${rules.min}`;
      return false;
    }

    // 最大长度验证
    if (rules.max !== undefined && typeof value === "string" && value.length > rules.max) {
      field.error = `最大长度为 ${rules.max}`;
      return false;
    }

    // 正则验证
    if (rules.pattern && typeof value === "string" && !rules.pattern.test(value)) {
      field.error = "格式不正确";
      return false;
    }

    // 自定义验证
    if (rules.custom) {
      const customError = rules.custom(value);
      if (customError) {
        field.error = customError;
        return false;
      }
    }

    return true;
  }

  validateForm(): boolean {
    let isValid = true;

    for (const fieldName in this.formState) {
      if (!this.validateField(fieldName)) {
        isValid = false;
      }
    }

    return isValid;
  }

  getField<K extends keyof T>(fieldName: K): FormField<T[K]> {
    return this.formState[fieldName];
  }

  setFieldValue<K extends keyof T>(fieldName: K, value: T[K]): void {
    this.formState[fieldName].value = value;
    this.validateField(fieldName);
  }

  getFormData(): T {
    const result: any = {};

    for (const fieldName in this.formState) {
      result[fieldName] = this.formState[fieldName].value;
    }

    return result;
  }
}

// 使用示例
interface LoginForm {
  email: string;
  password: string;
  rememberMe: boolean;
}

const loginForm = new FormValidator<LoginForm>({
  email: {
    value: "",
    rules: {
      required: true,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    }
  },
  password: {
    value: "",
    rules: {
      required: true,
      min: 6
    }
  },
  rememberMe: {
    value: false,
    rules: {
      required: false
    }
  }
});

// 验证表单
if (loginForm.validateForm()) {
  const formData = loginForm.getFormData();
  // 提交表单数据
}
```

## 下一步

掌握 TypeScript 基础后，你可以继续学习：

1. **React 基础** - 使用 TypeScript 开发 React 组件
2. **Next.js 路由** - 理解 App Router 和页面路由
3. **状态管理** - 使用 Zustand、Jotai 等现代状态管理库
4. **样式解决方案** - 掌握 Tailwind CSS 和样式组件

---

*TypeScript 为现代前端开发提供了强大的类型安全保障，掌握 TypeScript 是成为专业前端开发者的必备技能。*