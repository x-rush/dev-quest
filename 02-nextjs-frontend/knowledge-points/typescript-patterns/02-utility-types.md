# TypeScript 工具类型速查手册

## 📚 概述

TypeScript 提供了丰富的内置工具类型，帮助我们进行类型转换和操作。本手册涵盖了所有常用工具类型的使用方法、实际应用场景和自定义工具类型的创建技巧。

## 🔧 基础工具类型

### Partial<T>
**将类型 T 的所有属性变为可选**

```typescript
// 基础用法
interface User {
  id: number;
  name: string;
  email: string;
  age: number;
}

type PartialUser = Partial<User>;
// 等同于：
// {
//   id?: number;
//   name?: string;
//   email?: string;
//   age?: number;
// }

// 实际应用：表单更新
function updateUser(userId: number, updates: Partial<User>) {
  return fetch(`/api/users/${userId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
}

// 使用示例
updateUser(1, { name: 'John Doe' });
updateUser(2, { email: 'new@example.com', age: 30 });
```

### Required<T>
**将类型 T 的所有属性变为必选**

```typescript
// 基础用法
interface PartialUser {
  id: number;
  name?: string;
  email?: string;
  age?: number;
}

type CompleteUser = Required<PartialUser>;
// 等同于：
// {
//   id: number;
//   name: string;
//   email: string;
//   age: number;
// }

// 实际应用：数据验证
function validateUser(user: PartialUser): CompleteUser | null {
  if (!user.name || !user.email || !user.age) {
    return null;
  }

  return user as CompleteUser;
}

// 与 Partial 配合使用
interface Config {
  apiUrl: string;
  timeout?: number;
  retries?: number;
}

function createConfig(base: Config, overrides: Partial<Config>): Required<Config> {
  return {
    ...base,
    ...overrides,
    timeout: overrides.timeout ?? 30,
    retries: overrides.retries ?? 3,
  };
}
```

### Readonly<T>
**将类型 T 的所有属性变为只读**

```typescript
// 基础用法
interface Product {
  id: number;
  name: string;
  price: number;
}

type ReadonlyProduct = Readonly<Product>;
// 等同于：
// {
//   readonly id: number;
//   readonly name: string;
//   readonly price: number;
// }

// 实际应用：不可变数据
const product: ReadonlyProduct = {
  id: 1,
  name: 'Laptop',
  price: 999,
};

// product.price = 899; // 错误：无法分配到 "price"，因为它是只读属性

// React 中的使用
interface AppState {
  user: User;
  settings: Settings;
}

function useAppStore(): Readonly<AppState> {
  const state = useAppContext();
  return state; // 返回只读状态，防止外部修改
}
```

### Record<K, V>
**创建一个对象类型，其键为 K 类型，值为 V 类型**

```typescript
// 基础用法
type StringDictionary = Record<string, string>;
type NumberDictionary = Record<string, number>;

// 实际应用：配置对象
interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
}

type ThemeConfig = Record<string, ThemeColors>;

const themes: ThemeConfig = {
  light: {
    primary: '#007bff',
    secondary: '#6c757d',
    background: '#ffffff',
  },
  dark: {
    primary: '#0d6efd',
    secondary: '#6c757d',
    background: '#212529',
  },
};

// 实际应用：国际化字典
type I18nDictionary = Record<string, string>;

const messages: I18nDictionary = {
  welcome: 'Welcome',
  login: 'Login',
  logout: 'Logout',
  settings: 'Settings',
};

// 带索引签名的对象
type UserMap = Record<string, User>;
const userMap: UserMap = {
  '1': { id: 1, name: 'John', email: 'john@example.com' },
  '2': { id: 2, name: 'Jane', email: 'jane@example.com' },
};
```

## 🎯 映射工具类型

### Pick<T, K>
**从类型 T 中选择一组属性 K 来创建新类型**

```typescript
// 基础用法
interface User {
  id: number;
  name: string;
  email: string;
  age: number;
  address: string;
}

type UserProfile = Pick<User, 'name' | 'email'>;
// 等同于：
// {
//   name: string;
//   email: string;
// }

// 实际应用：组件 Props
function UserProfile({ name, email }: Pick<User, 'name' | 'email'>) {
  return (
    <div>
      <h3>{name}</h3>
      <p>{email}</p>
    </div>
  );
}

// 实际应用：API 响应过滤
interface FullUserResponse {
  id: number;
  name: string;
  email: string;
  passwordHash: string;
  ssn: string;
}

type PublicUserData = Pick<FullUserResponse, 'id' | 'name' | 'email'>;

function sanitizeUserResponse(user: FullUserResponse): PublicUserData {
  const { id, name, email } = user;
  return { id, name, email };
}
```

### Omit<T, K>
**从类型 T 中排除一组属性 K 来创建新类型**

```typescript
// 基础用法
interface User {
  id: number;
  name: string;
  email: string;
  password: string;
  createdAt: string;
}

type UserCreateRequest = Omit<User, 'id' | 'createdAt'>;
// 等同于：
// {
//   name: string;
//   email: string;
//   password: string;
// }

// 实际应用：数据库操作
interface DatabaseUser {
  id: number;
  name: string;
  email: string;
  password_hash: string;
  created_at: string;
  updated_at: string;
}

type CreateUserInput = Omit<DatabaseUser, 'id' | 'created_at' | 'updated_at'>;
type UpdateUserInput = Omit<DatabaseUser, 'id' | 'created_at' | 'password_hash'>;

// 实际应用：组件 Props
interface FullComponentProps {
  id: string;
  className: string;
  style: React.CSSProperties;
  onClick: () => void;
  children: React.ReactNode;
}

type BasicProps = Omit<FullComponentProps, 'id' | 'onClick'>;
```

### Exclude<T, U>
**从类型 T 中排除可以赋值给 U 的类型**

```typescript
// 基础用法
type T = string | number | boolean;
type U = string | number;
type Result = Exclude<T, U>; // boolean

// 实际应用：事件类型
type MouseEvents = 'click' | 'dblclick' | 'mousedown' | 'mouseup';
type KeyboardEvents = 'keydown' | 'keypress' | 'keyup';
type TouchEvents = 'touchstart' | 'touchmove' | 'touchend';

type NonMouseEvents = Exclude<MouseEvents | KeyboardEvents | TouchEvents, MouseEvents>;
// 等同于 KeyboardEvents | TouchEvents

// 实际应用：联合类型过滤
type Status = 'loading' | 'success' | 'error' | 'idle';
type LoadingStatus = Exclude<Status, 'idle'>; // 'loading' | 'success' | 'error'

function useApi<T>(url: string) {
  const [status, setStatus] = useState<LoadingStatus>('loading');
  // ...
}
```

### Extract<T, U>
**从类型 T 中提取可以赋值给 U 的类型**

```typescript
// 基础用法
type T = string | number | boolean;
type U = string | number;
type Result = Extract<T, U>; // string | number

// 实际应用：函数类型提取
type AnyFunction = (...args: any[]) => any;
type StringFunction = Extract<AnyFunction, (...args: any[]) => string>;

// 实际应用：对象属性提取
interface Product {
  id: number;
  name: string;
  price: number;
  inStock: boolean;
}

type StringProperties = Extract<keyof Product, string>;
type NumberProperties = Extract<keyof Product, number>;
```

## 🔄 函数工具类型

### ReturnType<T>
**获取函数类型 T 的返回类型**

```typescript
// 基础用法
function getUser(): User {
  return { id: 1, name: 'John', email: 'john@example.com' };
}

type UserReturnType = ReturnType<typeof getUser>; // User

// 异步函数
async function fetchUsers(): Promise<User[]> {
  const response = await fetch('/api/users');
  return response.json();
}

type FetchUsersReturn = ReturnType<typeof fetchUsers>; // Promise<User[]>

// 实际应用：Hook 类型定义
function useCustomHook<T>(fetcher: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  // ...
  return { data };
}

// 使用示例
const { data } = useCustomHook(() => fetch('/api/users').then(res => res.json()));
// data 类型为 User[] | null
```

### Parameters<T>
**获取函数类型 T 的参数类型**

```typescript
// 基础用法
function updateUser(id: number, updates: Partial<User>): Promise<User> {
  return fetch(`/api/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  }).then(res => res.json());
}

type UpdateUserParams = Parameters<typeof updateUser>;
// 等同于：[number, Partial<User>]

// 实际应用：事件处理器
type EventHandler = (event: React.MouseEvent<HTMLButtonElement>) => void;
type EventHandlerParams = Parameters<EventHandler>; // [React.MouseEvent<HTMLButtonElement>]

// 实际应用：API 客户端
const api = {
  get: <T>(url: string) => fetch(url).then(res => res.json() as Promise<T>),
  post: <T>(url: string, data: any) => fetch(url, {
    method: 'POST',
    body: JSON.stringify(data),
  }).then(res => res.json() as Promise<T>),
};

function useApi<T, F extends (...args: any[]) => Promise<T>>(
  fetcher: F,
  deps: Parameters<F>
) {
  // 使用 fetcher 和 deps
  // ...
}
```

### ConstructorParameters<T>
**获取构造函数类型 T 的参数类型**

```typescript
// 基础用法
class User {
  constructor(
    public id: number,
    public name: string,
    public email: string
  ) {}
}

type UserConstructorParams = ConstructorParameters<typeof User>;
// 等同于：[number, string, string]

// 实际应用：依赖注入
interface Injectable {
  new (...args: any[]): any;
}

function createInstance<T extends Injectable>(
  constructor: T,
  ...args: ConstructorParameters<T>
): InstanceType<T> {
  return new constructor(...args);
}

// 使用示例
const user = createInstance(User, 1, 'John', 'john@example.com');
```

### ThisParameterType<T>
**获取函数类型 T 的 this 参数类型**

```typescript
// 基础用法
interface User {
  name: string;
  greet(this: User): void;
}

const user: User = {
  name: 'John',
  greet(this: User) {
    console.log(`Hello, I'm ${this.name}`);
  },
};

type GreetThisType = ThisParameterType<typeof user.greet>; // User

// 实际应用：链式调用
class StringBuilder {
  private buffer: string = '';

  constructor(private value: string = '') {
    this.buffer = value;
  }

  append(this: StringBuilder, text: string): this {
    this.buffer += text;
    return this;
  }

  toString(this: StringBuilder): string {
    return this.buffer;
  }
}

type StringBuilderMethod = ThisParameterType<StringBuilder['append']>;
// StringBuilder
```

## 🎨 高级工具类型

### NonNullable<T>
**从类型 T 中排除 null 和 undefined**

```typescript
// 基础用法
type T = string | number | null | undefined;
type NonNullableT = NonNullable<T>; // string | number

// 实际应用：配置对象
interface Config {
  apiUrl: string;
  timeout?: number;
  retries?: number;
  callback?: () => void;
}

function createConfig(config: Config) {
  const nonNullableConfig: Required<Pick<Config, 'apiUrl'>> &
    Partial<Omit<Config, 'apiUrl'>> = {
      apiUrl: config.apiUrl,
      timeout: config.timeout ?? 30,
      retries: config.retries ?? 3,
    };

  return nonNullableConfig;
}

// 实际应用：数组过滤
function removeNullish<T>(array: (T | null | undefined)[]): T[] {
  return array.filter((item): item is T => item != null);
}

const items = [1, null, 2, undefined, 3];
const filtered = removeNullish(items); // [1, 2, 3]
```

### InstanceType<T>
**获取构造函数类型 T 的实例类型**

```typescript
// 基础用法
class User {
  constructor(public name: string, public email: string) {}
}

type UserInstance = InstanceType<typeof User>; // User

// 实际应用：工厂函数
interface Component {
  new (props: any): React.Component<any, any>;
}

function createComponent<T extends Component>(
  ComponentClass: T,
  props: ConstructorParameters<T>[0]
): InstanceType<T> {
  return new ComponentClass(props);
}

// 使用示例
class Button extends React.Component<{ label: string }> {
  render() {
    return <button>{this.props.label}</button>;
  }
}

const button = createComponent(Button, { label: 'Click me' });
```

### Uppercase<T>
**将字符串字面量类型 T 转换为大写**

```typescript
// 基础用法
type EventName = 'click' | 'hover' | 'focus';
type UppercaseEvents = Uppercase<EventName>; // 'CLICK' | 'HOVER' | 'FOCUS'

// 实际应用：常量定义
type LogLevel = 'debug' | 'info' | 'warn' | 'error';
type LogLevelConstant = `LOG_${Uppercase<LogLevel>}`;

// 'LOG_DEBUG' | 'LOG_INFO' | 'LOG_WARN' | 'LOG_ERROR'
const LOG_LEVELS: Record<LogLevel, LogLevelConstant> = {
  debug: 'LOG_DEBUG',
  info: 'LOG_INFO',
  warn: 'LOG_WARN',
  error: 'LOG_ERROR',
};
```

### Lowercase<T>
**将字符串字面量类型 T 转换为小写**

```typescript
// 基础用法
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type LowercaseMethods = Lowercase<HttpMethod>; // 'get' | 'post' | 'put' | 'delete'

// 实际应用：API 客户端
type ApiMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type ApiMethodLowercase = Lowercase<ApiMethod>;

interface ApiRequest<T = any> {
  method: ApiMethodLowercase;
  url: string;
  data?: T;
}

function makeRequest<T>({ method, url, data }: ApiRequest<T>): Promise<T> {
  return fetch(url, {
    method: method.toUpperCase(),
    body: data ? JSON.stringify(data) : undefined,
  }).then(res => res.json());
}
```

## 🛠️ 自定义工具类型

### 深度 Partial
**递归地将对象的所有属性变为可选**

```typescript
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// 使用示例
interface NestedConfig {
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

type PartialConfig = DeepPartial<NestedConfig>;

const partialConfig: PartialConfig = {
  database: {
    host: 'localhost',
    credentials: {
      username: 'admin',
    },
  },
};

// 更安全的实现
type DeepPartialSafe<T> = T extends object
  ? {
      [P in keyof T]?: DeepPartialSafe<T[P]>;
    }
  : T;
```

### 深度只读
**递归地将对象的所有属性变为只读**

```typescript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

// 使用示例
interface AppState {
  user: {
    id: number;
    name: string;
    preferences: {
      theme: string;
      language: string;
    };
  };
  settings: {
    notifications: boolean;
    darkMode: boolean;
  };
}

type ReadonlyState = DeepReadonly<AppState>;

const state: ReadonlyState = {
  user: {
    id: 1,
    name: 'John',
    preferences: {
      theme: 'light',
      language: 'en',
    },
  },
  settings: {
    notifications: true,
    darkMode: false,
  },
};

// state.user.name = 'Jane'; // 错误
// state.user.preferences.theme = 'dark'; // 错误
```

### 深度必选
**递归地将对象的所有属性变为必选**

```typescript
type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

// 使用示例
interface PartialUser {
  id: number;
  profile?: {
    name?: string;
    email?: string;
    address?: {
      street?: string;
      city?: string;
    };
  };
}

type CompleteUser = DeepRequired<PartialUser>;
```

### 获取类型路径
**获取对象类型的所有可能路径**

```typescript
type Path<T> = T extends object
  ? {
      [K in keyof T]: K extends string
        ? T[K] extends object
          ? `${K}` | `${K}.${Path<T[K]>}`
          : `${K}`
        : never;
    }[keyof T]
  : never;

interface User {
  id: number;
  name: string;
  profile: {
    email: string;
    settings: {
      theme: string;
      notifications: boolean;
    };
  };
}

type UserPaths = Path<User>;
// 结果：
// "id" | "name" | "profile" | "profile.email" | "profile.settings" | "profile.settings.theme" | "profile.settings.notifications"

// 实际应用：类型安全的路径选择器
function getValue<T, P extends Path<T>>(obj: T, path: P): PathValue<T, P> {
  return path.split('.').reduce((acc, key) => acc[key], obj);
}

type PathValue<T, P extends Path<T>> = P extends `${infer K}.${infer Rest}`
  ? K extends keyof T
    ? Rest extends Path<T[K]>
      ? PathValue<T[K], Rest>
      : never
    : never
  : P extends keyof T
  ? T[P]
  : never;

// 使用示例
const user: User = {
  id: 1,
  name: 'John',
  profile: {
    email: 'john@example.com',
    settings: {
      theme: 'dark',
      notifications: true,
    },
  },
};

const theme = getValue(user, 'profile.settings.theme'); // string
```

### 条件类型工具
**条件类型的高级应用**

```typescript
// 提取函数的参数和返回类型
type AsyncFunction<T> = T extends (...args: any[]) => Promise<infer U>
  ? (...args: Parameters<T>) => Promise<U>
  : T extends (...args: infer A) => infer R
  ? (...args: A) => Promise<R>
  : never;

// 同步函数转换为异步函数
function createAsyncFunction<T extends (...args: any[]) => any>(
  fn: T
): AsyncFunction<T> {
  return (...args: Parameters<T>) => Promise.resolve(fn(...args));
}

// 使用示例
const syncAdd = (a: number, b: number): number => a + b;
const asyncAdd = createAsyncFunction(syncAdd);
// asyncAdd 的类型为 (a: number, b: number) => Promise<number>

// 提取 Promise 的解析类型
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;

type AsyncData = Promise<User>;
type DataType = UnwrapPromise<AsyncData>; // User
```

## 📋 实际应用场景

### React 类型模式
**在 React 组件中使用工具类型**

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

// Hook 类型安全
function useCustomHook<T, F extends (...args: any[]) => Promise<T>>(
  fetcher: F,
  deps: Parameters<F>
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      setLoading(true);
      try {
        const result = await fetcher(...deps);
        if (isMounted) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [fetcher, ...deps]);

  return { data, loading, error };
}
```

### API 类型模式
**类型安全的 API 开发**

```typescript
// API 响应包装
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

// 分页响应
interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

// API 端点类型定义
type ApiEndpoint = {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  request?: any;
  response: any;
};

// 类型安全的 API 客户端
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async request<T>(
    method: string,
    path: string,
    data?: any
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: data ? JSON.stringify(data) : undefined,
    });

    const result = await response.json();
    return result as ApiResponse<T>;
  }

  async get<T>(path: string): Promise<ApiResponse<T>> {
    return this.request<T>('GET', path);
  }

  async post<T>(path: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>('POST', path, data);
  }

  async put<T>(path: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', path, data);
  }

  async delete<T>(path: string): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', path);
  }
}

// 使用示例
const api = new ApiClient('/api');

const userResponse = await api.get<User>('/users/1');
const createResponse = await api.post<User>('/users', {
  name: 'John',
  email: 'john@example.com',
});
```

## 📖 总结

TypeScript 工具类型提供了强大的类型转换能力：

### 基础工具类型：
1. **Partial<T>**: 属性可选化
2. **Required<T>**: 属性必选化
3. **Readonly<T>**: 属性只读化
4. **Record<K, V>**: 键值对对象类型

### 映射工具类型：
1. **Pick<T, K>**: 选择属性
2. **Omit<T, K>**: 排除属性
3. **Exclude<T, U>**: 排除类型
4. **Extract<T, U>**: 提取类型

### 函数工具类型：
1. **ReturnType<T>**: 获取返回类型
2. **Parameters<T>**: 获取参数类型
3. **ConstructorParameters<T>**: 获取构造函数参数
4. **ThisParameterType<T>**: 获取 this 参数类型

### 高级工具类型：
1. **NonNullable<T>**: 排除 null 和 undefined
2. **InstanceType<T>**: 获取实例类型
3. **Uppercase<T>**: 转换为大写
4. **Lowercase<T>**: 转换为小写

掌握这些工具类型将帮助你编写更加类型安全、可维护的 TypeScript 代码。在 Next.js 开发中，合理使用工具类型可以大大提升开发效率和代码质量。