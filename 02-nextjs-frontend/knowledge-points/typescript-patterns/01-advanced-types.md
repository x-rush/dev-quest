# TypeScript 高级类型模式

## 📚 概述

TypeScript 提供了强大的类型系统，支持复杂的类型操作和约束。本指南涵盖了在 Next.js 和 React 开发中最常用的高级类型模式，帮助你编写类型安全且表达力强的代码。

## 🏗️ 条件类型

### 基础条件类型
**基于条件进行类型选择**

```typescript
// 基础条件类型语法
type IsString<T> = T extends string ? true : false;

type Test1 = IsString<string>; // true
type Test2 = IsString<number>; // false

// 实际应用：API 响应类型
type ApiResponse<T> = T extends 'success'
  ? { status: 'success'; data: any }
  : { status: 'error'; message: string };

type SuccessResponse = ApiResponse<'success'>; // { status: 'success'; data: any }
type ErrorResponse = ApiResponse<'error'>;   // { status: 'error'; message: string }

// 组件 Props 类型
type ComponentProps<T> = T extends 'button'
  ? { type: 'button'; onClick: () => void }
  : T extends 'input'
  ? { type: 'input'; value: string; onChange: (value: string) => void }
  : never;

type ButtonProps = ComponentProps<'button'>;
type InputProps = ComponentProps<'input'>;
```

### 分布式条件类型
**处理联合类型的条件推断**

```typescript
// 分布式条件类型
type ToArray<T> = T extends any ? T[] : never;

type StringOrNumberArray = ToArray<string | number>; // string[] | number[]

// 过滤联合类型
type NonNullable<T> = T extends null | undefined ? never : T;

type FilteredTypes = NonNullable<string | number | null | undefined>; // string | number

// 实际应用：过滤函数类型
type FunctionProperties<T> = {
  [K in keyof T]: T[K] extends Function ? T[K] : never;
}[keyof T];

interface User {
  id: number;
  name: string;
  updateProfile: () => void;
  delete: () => void;
}

type UserMethods = FunctionProperties<User>; // updateProfile | delete
```

### 条件类型推断
**使用 infer 关键字推断类型**

```typescript
// 获取函数返回类型
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

type ExampleFunction = (x: number) => string;
type FunctionReturn = ReturnType<ExampleFunction>; // string

// 获取数组元素类型
type ArrayElement<T> = T extends (infer U)[] ? U : never;

type StringArray = string[];
type ArrayElementType = ArrayElement<StringArray>; // string

// 获取 Promise 解析类型
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;

type AsyncData = Promise<string>;
type DataType = UnwrapPromise<AsyncData>; // string

// 实际应用：API Hook 类型
type UseApiResult<T> = T extends (...args: any[]) => Promise<infer R>
  ? {
      data: R | null;
      loading: boolean;
      error: string | null;
      refetch: T;
    }
  : never;

type UseUsers = UseApiResult<() => Promise<User[]>>;
// 结果：{ data: User[] | null; loading: boolean; error: string | null; refetch: () => Promise<User[]> }
```

## 🔧 映射类型

### 基础映射类型
**创建对象类型的变换版本**

```typescript
// 基础映射类型
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

type Partial<T> = {
  [P in keyof T]?: T[P];
};

type Required<T> = {
  [P in keyof T]-?: T[P];
};

// 实际应用：表单数据类型
interface UserData {
  name: string;
  email: string;
  age: number;
  avatar: string;
}

type UserFormData = Partial<UserData>; // 所有属性可选
type UserDisplayData = Readonly<UserData>; // 所有属性只读

// 深度只读
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

interface Config {
  database: {
    host: string;
    port: number;
  };
  api: {
    version: string;
    endpoint: string;
  };
}

type ReadonlyConfig = DeepReadonly<Config>;
```

### 键重映射
**重新映射对象的键**

```typescript
// 键重映射语法
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface User {
  name: string;
  email: string;
  age: number;
}

type UserGetters = Getters<User>;
// 结果：
// {
//   getName: () => string;
//   getEmail: () => string;
//   getAge: () => number;
// }

// 实际应用：事件处理器类型
type EventHandlers<T> = {
  [K in keyof T as `on${Capitalize<string & K>}Change`]: (value: T[K]) => void;
};

type FormEvents = EventHandlers<{
  username: string;
  email: string;
  age: number;
}>;
// 结果：
// {
//   onUsernameChange: (value: string) => void;
//   onEmailChange: (value: string) => void;
//   onAgeChange: (value: number) => void;
// }

// 选择性映射
type StringKeys<T> = {
  [K in keyof T as T[K] extends string ? K : never]: T[K];
};

type UserStrings = StringKeys<User>;
// 结果：{ name: string; email: string; }
```

### 高级映射模式
**复杂的类型变换**

```typescript
// 条件映射类型
type OptionalProperties<T> = {
  [K in keyof T as undefined extends T[K] ? K : never]?: T[K];
};

type RequiredProperties<T> = {
  [K in keyof T as undefined extends T[K] ? never : K]: T[K];
};

interface PartialUser {
  id: number;
  name: string;
  email?: string;
  avatar?: string;
}

type OptionalUser = OptionalProperties<PartialUser>; // { email?: string; avatar?: string; }
type RequiredUser = RequiredProperties<PartialUser>; // { id: number; name: string; }

// 函数类型变换
type AsyncFunction<T> = T extends (...args: infer A) => infer R
  ? (...args: A) => Promise<R>
  : never;

type SyncFunction = (id: number) => User;
type AsyncFunctionType = AsyncFunction<SyncFunction>; // (id: number) => Promise<User>

// 数组类型变换
type ArrayToUnion<T> = T extends readonly (infer U)[] ? U : never;

type UserArray = User[];
type UserUnion = ArrayToUnion<UserArray>; // User
```

## 🎯 模板字面量类型

### 基础模板字面量
**使用字符串模板创建类型**

```typescript
// 基础模板字面量
type Greeting = `Hello, ${string}!`;

type Example = Greeting; // "Hello, world!" | "Hello, TypeScript!" | etc.

// 联合类型与模板字面量
type Color = 'red' | 'green' | 'blue';
type Size = 'small' | 'medium' | 'large';
type Variant = `${Color}-${Size}`;

type ButtonVariant = Variant; // "red-small" | "red-medium" | "red-large" | "green-small" | etc.

// 实际应用：CSS 类名
type CSSClass = {
  [K in keyof ComponentProps as `component-${string & K}`]?: boolean;
};

type ComponentProps = {
  primary: boolean;
  large: boolean;
  disabled: boolean;
};

type CSSClasses = CSSClass; // { 'component-primary'?: boolean; 'component-large'?: boolean; 'component-disabled'?: boolean; }

// API 端点类型
type Endpoint = `/api/${'users' | 'posts' | 'comments'}/${string}`;

type UserEndpoint = `/api/users/${string}`; // "/api/users/123" | "/api/users/me" | etc.
```

### 高级模板操作
**复杂的字符串类型操作**

```typescript
// 字符串操作类型
type Capitalize<S extends string> = S extends `${infer F}${infer R}`
  ? `${Uppercase<F>}${R}`
  : S;

type Uncapitalize<S extends string> = S extends `${infer F}${infer R}`
  ? `${Lowercase<F>}${R}`
  : S;

// 实际应用：对象键转换
type ToCamelCase<S extends string> = S extends `${infer P1}_${infer P2}`
  ? `${P1}${Capitalize<ToCamelCase<P2>>}`
  : S;

type ToPascalCase<S extends string> = S extends `${infer P1}_${infer P2}`
  ? `${Capitalize<P1>}${Capitalize<ToPascalCase<P2>>}`
  : Capitalize<S>;

type SnakeCaseToCamelCase = ToCamelCase<'user_name'>; // "userName"
type SnakeCaseToPascalCase = ToPascalCase<'user_name'>; // "UserName"

// 对象键转换
type ConvertKeysToCamelCase<T> = {
  [K in keyof T as ToCamelCase<string & K>]: T[K];
};

interface ApiUser {
  user_name: string;
  created_at: string;
  last_login: string;
}

type UserModel = ConvertKeysToCamelCase<ApiUser>;
// 结果：{ userName: string; createdAt: string; lastLogin: string; }
```

### 路径类型
**类型安全的路由系统**

```typescript
// 路径参数类型
type RouteParams<Path extends string> = Path extends `${string}:${infer Param}/${infer Rest}`
  ? { [K in Param | keyof RouteParams<`/${Rest}`>]: string }
  : Path extends `${string}:${infer Param}`
  ? { [K in Param]: string }
  : {};

type UserRouteParams = RouteParams<'/users/:id/posts/:postId'>;
// 结果：{ id: string; postId: string; }

// 路由构建器类型
type RouteBuilder<Path extends string> = (params: RouteParams<Path>) => string;

const buildUserRoute: RouteBuilder<'/users/:id'> = (params) => `/users/${params.id}`;

// 类型安全的路由链接组件
interface LinkProps<Path extends string> {
  to: Path;
  params: RouteParams<Path>;
  children: React.ReactNode;
}

function TypedLink<Path extends string>({ to, params, children }: LinkProps<Path>) {
  // 构建路径逻辑
  let path = to;
  Object.entries(params).forEach(([key, value]) => {
    path = path.replace(`:${key}`, value);
  });

  return <a href={path}>{children}</a>;
}

// 使用示例
<TypedLink to="/users/:id/posts/:postId" params={{ id: "123", postId: "456" }}>
  View Post
</TypedLink>
```

## 🔍 类型守卫和判别

### 自定义类型守卫
**运行时类型检查**

```typescript
// 基础类型守卫
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number' && !isNaN(value);
}

// 对象类型守卫
interface Cat {
  type: 'cat';
  meow(): void;
}

interface Dog {
  type: 'dog';
  bark(): void;
}

function isCat(animal: Cat | Dog): animal is Cat {
  return animal.type === 'cat';
}

function makeSound(animal: Cat | Dog) {
  if (isCat(animal)) {
    animal.meow(); // TypeScript 知道这是 Cat
  } else {
    animal.bark(); // TypeScript 知道这是 Dog
  }
}

// 实际应用：API 响应处理
interface SuccessResponse<T> {
  success: true;
  data: T;
}

interface ErrorResponse {
  success: false;
  error: string;
  code: string;
}

function isSuccess<T>(response: SuccessResponse<T> | ErrorResponse): response is SuccessResponse<T> {
  return response.success;
}

async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  const data: SuccessResponse<User> | ErrorResponse = await response.json();

  if (isSuccess(data)) {
    return data.data;
  } else {
    throw new Error(data.error);
  }
}
```

### 判别联合类型
**使用公共属性区分类型**

```typescript
// 判别联合类型
interface LoadingState {
  status: 'loading';
}

interface SuccessState<T> {
  status: 'success';
  data: T;
}

interface ErrorState {
  status: 'error';
  error: string;
}

type DataState<T> = LoadingState | SuccessState<T> | ErrorState;

// 在组件中使用
function DataComponent<T>({ state }: { state: DataState<T> }) {
  switch (state.status) {
    case 'loading':
      return <div>Loading...</div>;
    case 'success':
      return <div>Data: {JSON.stringify(state.data)}</div>;
    case 'error':
      return <div>Error: {state.error}</div>;
  }
}

// 实际应用：表单状态
type FormState<T> =
  | { status: 'idle' }
  | { status: 'submitting' }
  | { status: 'success'; data: T }
  | { status: 'error'; errors: Record<string, string> };

function useFormState<T>() {
  const [state, setState] = useState<FormState<T>>({ status: 'idle' });

  const submit = async (data: T) => {
    setState({ status: 'submitting' });
    try {
      const result = await submitForm(data);
      setState({ status: 'success', data: result });
    } catch (errors) {
      setState({ status: 'error', errors });
    }
  };

  return { state, submit };
}
```

## 🏗️ 工具类型组合

### 高级工具类型
**组合多种类型操作**

```typescript
// 深度可选
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// 深度必选
type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

// 选择性深度操作
type DeepPartialSome<T, K extends keyof T> = {
  [P in keyof T]: P extends K ? DeepPartial<T[P]> : T[P];
};

// 实际应用：配置对象
interface AppConfig {
  database: {
    host: string;
    port: number;
    credentials: {
      username: string;
      password: string;
    };
  };
  api: {
    version: string;
    timeout: number;
  };
}

type PartialConfig = DeepPartial<AppConfig>;
type PartialDatabaseConfig = DeepPartialSome<AppConfig, 'database'>;

// 递归条件类型
type Flatten<T> = T extends readonly (infer U)[]
  ? U extends readonly (infer V)[]
    ? Flatten<V>
    : U
  : T;

type NestedArray = string[][][];
type Flattened = Flatten<NestedArray>; // string

// 实际应用：深度合并
type DeepMerge<T, U> = {
  [K in keyof T | keyof U]: K extends keyof U
    ? U[K] extends object
      ? K extends keyof T
        ? T[K] extends object
          ? DeepMerge<T[K], U[K]>
          : U[K]
        : U[K]
      : U[K]
    : K extends keyof T
    ? T[K]
    : never;
};

// 使用示例
type MergedConfig = DeepMerge<PartialConfig, AppConfig>;
```

### 类型级别的编程
**在类型系统中进行复杂计算**

```typescript
// 数字运算类型
type Add<A extends number, B extends number> =
  [...Tuple<A>, ...Tuple<B>]['length'] extends number
    ? [...Tuple<A>, ...Tuple<B>]['length']
    : never;

type Tuple<T extends number, R extends readonly unknown[] = []> =
  R['length'] extends T ? R : Tuple<T, readonly [...R, unknown]>;

// 类型级别的数组操作
type Length<T extends readonly unknown[]> = T['length'];
type First<T extends readonly unknown[]> = T extends readonly [infer F, ...readonly any[]] ? F : never;
type Last<T extends readonly unknown[]> = T extends readonly [...readonly any[], infer L] ? L : never;

// 实际应用：固定长度数组
type FixedLengthArray<T, N extends number> = readonly [T, ...T[]] & { length: N };

type ThreeStrings = FixedLengthArray<string, 3>; // [string, string, string]

// 类型安全的对象路径
type Path<T> = T extends object
  ? {
      [K in keyof T]: K extends string
        ? T[K] extends object
          ? `${K}` | `${K}.${Path<T[K]>}`
          : `${K}`
        : never;
    }[keyof T]
  : never;

type UserPaths = Path<{
  id: number;
  profile: {
    name: string;
    settings: {
      theme: string;
    };
  };
}>;
// 结果："id" | "profile" | "profile.name" | "profile.settings" | "profile.settings.theme"
```

## 📋 实际应用模式

### React 组件类型模式
**类型安全的 React 开发**

```typescript
// 泛型组件 Props
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string;
  onItemClick?: (item: T) => void;
}

function List<T>({ items, renderItem, keyExtractor, onItemClick }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)} onClick={() => onItemClick?.(item)}>
          {renderItem(item, index)}
        </li>
      ))}
    </ul>
  );
}

// 使用示例
interface User {
  id: string;
  name: string;
  email: string;
}

function UserList() {
  const users: User[] = [
    { id: '1', name: 'John', email: 'john@example.com' },
    { id: '2', name: 'Jane', email: 'jane@example.com' },
  ];

  return (
    <List<User>
      items={users}
      renderItem={(user) => <div>{user.name} - {user.email}</div>}
      keyExtractor={(user) => user.id}
      onItemClick={(user) => console.log('Clicked:', user.name)}
    />
  );
}

// Hook 返回类型模式
interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

function useApi<T>(url: string): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(url);
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch };
}
```

### API 类型模式
**类型安全的 API 开发**

```typescript
// API 响应包装类型
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

// 分页类型
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// API 端点类型定义
type ApiEndpoints = {
  '/api/users': {
    GET: () => Promise<ApiResponse<User[]>>;
    POST: (data: CreateUserRequest) => Promise<ApiResponse<User>>;
  };
  '/api/users/:id': {
    GET: (params: { id: string }) => Promise<ApiResponse<User>>;
    PUT: (params: { id: string }, data: UpdateUserRequest) => Promise<ApiResponse<User>>;
    DELETE: (params: { id: string }) => Promise<ApiResponse<void>>;
  };
};

// 类型安全的 API 客户端
class ApiClient {
  async request<
    Endpoint extends keyof ApiEndpoints,
    Method extends keyof ApiEndpoints[Endpoint],
    Response extends ApiEndpoints[Endpoint][Method] extends (...args: any[]) => Promise<infer R>
      ? R
      : never
  >(
    endpoint: Endpoint,
    method: Method,
    ...args: ApiEndpoints[Endpoint][Method] extends (...args: any[]) => any
      ? Parameters<ApiEndpoints[Endpoint][Method]>
      : never
  ): Promise<Response> {
    // 实现请求逻辑
    const url = endpoint.toString().replace(/:(\w+)/g, (match, key) => {
      const params = args[0] as any;
      return params[key] || match;
    });

    const response = await fetch(url, {
      method: method as string,
      body: args[1] ? JSON.stringify(args[1]) : undefined,
    });

    return response.json();
  }
}

// 使用示例
const api = new ApiClient();

// 类型安全的 API 调用
const users = await api.request('/api/users', 'GET');
const user = await api.request('/api/users/:id', 'GET', { id: '123' });
const updatedUser = await api.request('/api/users/:id', 'PUT', { id: '123' }, { name: 'New Name' });
```

## 📖 总结

TypeScript 高级类型提供了强大的类型系统功能：

### 核心概念：
1. **条件类型**: 基于条件进行类型选择和推断
2. **映射类型**: 创建对象类型的变换版本
3. **模板字面量类型**: 字符串模板类型操作
4. **类型守卫**: 运行时类型检查
5. **工具类型组合**: 组合多种类型操作

### 实际应用：
- 类型安全的 React 组件开发
- API 客户端类型定义
- 表单状态管理
- 路由系统类型安全
- 配置对象类型转换

掌握这些高级类型模式将帮助你构建更加类型安全、可维护的 TypeScript 应用。在 Next.js 开发中，合理使用这些模式可以大大提升开发效率和代码质量。