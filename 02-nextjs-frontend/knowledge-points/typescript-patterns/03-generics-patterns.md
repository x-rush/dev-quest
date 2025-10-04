# TypeScript 泛型模式速查手册

## 📚 概述

泛型是 TypeScript 的核心特性之一，提供了编写可重用、类型安全代码的能力。本指南涵盖了泛型的高级模式、约束技巧以及在 React 和 Next.js 开发中的实际应用。

## 🏗️ 基础泛型概念

### 泛型函数
**创建可重用的类型安全函数**

```typescript
// 基础泛型函数
function identity<T>(arg: T): T {
  return arg;
}

// 使用示例
const num = identity<number>(42); // 42
const str = identity('hello');    // 'hello' (类型推断)
const bool = identity(true);      // true

// 实际应用：API 响应处理
async function fetchData<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

// 使用示例
interface User {
  id: number;
  name: string;
  email: string;
}

interface Product {
  id: number;
  name: string;
  price: number;
}

const users = await fetchData<User[]>('/api/users');
const product = await fetchData<Product>('/api/products/1');

// 泛型数组函数
function getLastElement<T>(array: T[]): T | undefined {
  return array[array.length - 1];
}

const lastNumber = getLastElement([1, 2, 3]);      // number | undefined
const lastString = getLastElement(['a', 'b', 'c']);  // string | undefined
```

### 泛型接口
**定义灵活的对象类型**

```typescript
// 基础泛型接口
interface Box<T> {
  value: T;
  description: string;
}

// 使用示例
const numberBox: Box<number> = {
  value: 42,
  description: 'The answer to life',
};

const stringBox: Box<string> = {
  value: 'hello',
  description: 'A greeting',
};

// 实际应用：API 响应包装
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

// 使用示例
interface User {
  id: number;
  name: string;
}

const userResponse: ApiResponse<User> = {
  success: true,
  data: { id: 1, name: 'John' },
  timestamp: new Date().toISOString(),
};

// 实际应用：分页数据
interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

const usersPage: PaginatedResponse<User> = {
  items: [
    { id: 1, name: 'John' },
    { id: 2, name: 'Jane' },
  ],
  pagination: {
    page: 1,
    pageSize: 10,
    total: 2,
    totalPages: 1,
  },
};
```

### 泛型类
**创建可重用的类组件**

```typescript
// 基础泛型类
class Container<T> {
  private value: T;

  constructor(value: T) {
    this.value = value;
  }

  getValue(): T {
    return this.value;
  }

  setValue(value: T): void {
    this.value = value;
  }
}

// 使用示例
const numberContainer = new Container<number>(42);
const stringContainer = new Container('hello');

// 实际应用：状态管理
class StateManager<T> {
  private state: T;
  private listeners: ((state: T) => void)[] = [];

  constructor(initialState: T) {
    this.state = initialState;
  }

  getState(): T {
    return this.state;
  }

  setState(newState: Partial<T>): void {
    this.state = { ...this.state, ...newState };
    this.notifyListeners();
  }

  subscribe(listener: (state: T) => void): () => void {
    this.listeners.push(listener);

    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.state));
  }
}

// 使用示例
interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  isLoading: boolean;
}

const appState = new StateManager<AppState>({
  user: null,
  theme: 'light',
  isLoading: false,
});
```

## 🎯 泛型约束

### 基础约束
**限制泛型类型的范围**

```typescript
// 基础约束
interface Lengthwise {
  length: number;
}

function logLength<T extends Lengthwise>(arg: T): void {
  console.log(arg.length);
}

logLength('hello');     // 5
logLength([1, 2, 3]);   // 3
logLength({ length: 10 }); // 10
// logLength(42);         // 错误：number 没有 length 属性

// 实际应用：对象键操作
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

interface User {
  id: number;
  name: string;
  email: string;
}

const user: User = { id: 1, name: 'John', email: 'john@example.com' };
const userName = getProperty(user, 'name');     // string
const userId = getProperty(user, 'id');         // number
// const userAge = getProperty(user, 'age');     // 错误：'age' 不是 User 的键

// 实际应用：表单验证
interface Validatable {
  validate(): boolean;
}

function validateAndSubmit<T extends Validatable>(item: T): Promise<void> {
  if (item.validate()) {
    return submit(item);
  }
  throw new Error('Validation failed');
}

interface UserForm extends Validatable {
  name: string;
  email: string;
  validate(): boolean;
}

const userForm: UserForm = {
  name: 'John',
  email: 'john@example.com',
  validate() {
    return this.name.length > 0 && this.email.includes('@');
  },
};

validateAndSubmit(userForm);
```

### 条件约束
**基于条件的类型约束**

```typescript
// 条件类型约束
interface IdProvider {
  id: string;
}

function logId<T extends IdProvider>(item: T): void {
  console.log(item.id);
}

interface User extends IdProvider {
  name: string;
}

interface Product extends IdProvider {
  name: string;
  price: number;
}

logId({ id: '1', name: 'John' }); // 正确
// logId({ name: 'John' });       // 错误：缺少 id 属性

// 实际应用：数据库操作
interface Entity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

interface Repository<T extends Entity> {
  find(id: string): Promise<T | null>;
  save(entity: Omit<T, 'id' | 'createdAt' | 'updatedAt'>): Promise<T>;
  update(id: string, updates: Partial<T>): Promise<T>;
  delete(id: string): Promise<void>;
}

class UserRepository implements Repository<User> {
  async find(id: string): Promise<User | null> {
    // 实现查找逻辑
    return null;
  }

  async save(userData: Omit<User, keyof Entity>): Promise<User> {
    // 实现保存逻辑
    return {} as User;
  }

  async update(id: string, updates: Partial<User>): Promise<User> {
    // 实现更新逻辑
    return {} as User;
  }

  async delete(id: string): Promise<void> {
    // 实现删除逻辑
  }
}
```

### 键值约束
**使用键值对进行类型约束**

```typescript
// 键值对约束
interface KeyValuePair<K extends string | number, V> {
  key: K;
  value: V;
}

function createKeyValuePair<K extends string | number, V>(
  key: K,
  value: V
): KeyValuePair<K, V> {
  return { key, value };
}

// 使用示例
const stringKeyPair = createKeyValuePair('name', 'John');
const numberKeyPair = createKeyValuePair(42, 'answer');

// 实际应用：国际化字典
interface TranslationDict {
  [key: string]: string;
}

class I18n<T extends TranslationDict> {
  private translations: T;

  constructor(translations: T) {
    this.translations = translations;
  }

  translate<K extends keyof T>(key: K): T[K] {
    return this.translations[key];
  }

  addTranslations<K extends string, V extends string>(
    key: K,
    value: V
  ): I18n<T & Record<K, V>> {
    return new I18n({ ...this.translations, [key]: value });
  }
}

// 使用示例
type EnglishTranslations = {
  welcome: string;
  login: string;
  logout: string;
};

const i18n = new I18n<EnglishTranslations>({
  welcome: 'Welcome',
  login: 'Login',
  logout: 'Logout',
});

const welcomeMessage = i18n.translate('welcome'); // string
```

## 🔄 高级泛型模式

### 泛型工厂模式
**创建泛型对象的工厂函数**

```typescript
// 泛型工厂接口
interface Factory<T> {
  create(...args: any[]): T;
}

// 用户工厂
class UserFactory implements Factory<User> {
  create(id: number, name: string, email: string): User {
    return {
      id,
      name,
      email,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }
}

// 产品工厂
class ProductFactory implements Factory<Product> {
  create(id: number, name: string, price: number): Product {
    return {
      id,
      name,
      price,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }
}

// 实际应用：组件工厂
interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
}

class ButtonFactory implements Factory<React.ComponentType<ComponentProps & { onClick: () => void }>> {
  create(variant: 'primary' | 'secondary'): React.ComponentType<ComponentProps & { onClick: () => void }> {
    const Button = ({ onClick, className, children, ...props }: ComponentProps & { onClick: () => void }) => (
      <button
        onClick={onClick}
        className={`btn btn-${variant} ${className || ''}`}
        {...props}
      >
        {children}
      </button>
    );
    return Button;
  }
}

// 使用示例
const buttonFactory = new ButtonFactory();
const PrimaryButton = buttonFactory.create('primary');
const SecondaryButton = buttonFactory.create('secondary');
```

### 泛型装饰器模式
**使用泛型增强对象功能**

```typescript
// 缓存装饰器
function memoize<T extends (...args: any[]) => any>(fn: T): T {
  const cache = new Map<string, ReturnType<T>>();

  return ((...args: Parameters<T>) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }

    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
}

// 使用示例
const expensiveCalculation = memoize((n: number): number => {
  console.log('Calculating...');
  return n * n * n;
});

console.log(expensiveCalculation(5)); // Calculating... 125
console.log(expensiveCalculation(5)); // 125 (from cache)

// 实际应用：API 请求缓存
class ApiClient {
  @memoize
  async fetchUser(id: string): Promise<User> {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
  }
}

// 装饰器实现
function memoize<T extends Record<string, any>, K extends keyof T>(
  target: T,
  propertyKey: K,
  descriptor: TypedPropertyDescriptor<T[K]>
): void {
  const originalMethod = descriptor.value!;
  const cache = new Map<string, any>();

  descriptor.value = function (...args: any[]) {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }

    const result = originalMethod.apply(this, args);
    cache.set(key, result);
    return result;
  };
}
```

### 泛型组合模式
**组合多个泛型类型**

```typescript
// 基础组件类型
interface BaseComponent {
  id: string;
  type: string;
}

interface Draggable {
  canDrag: boolean;
  onDragStart: (event: DragEvent) => void;
  onDragEnd: (event: DragEvent) => void;
}

interface Resizable {
  canResize: boolean;
  onResize: (dimensions: { width: number; height: number }) => void;
}

interface Positionable {
  x: number;
  y: number;
  setPosition: (x: number, y: number) => void;
}

// 组合类型
type UIComponent<T extends BaseComponent = BaseComponent> = T & Draggable & Resizable & Positionable;

// 创建组件工厂
function createComponent<T extends BaseComponent>(
  baseProps: T
): UIComponent<T> {
  return {
    ...baseProps,
    canDrag: true,
    canResize: true,
    x: 0,
    y: 0,
    onDragStart: () => {},
    onDragEnd: () => {},
    onResize: () => {},
    setPosition: (x, y) => {},
  };
}

// 使用示例
interface Button extends BaseComponent {
  type: 'button';
  label: string;
  onClick: () => void;
}

const button = createComponent<Button>({
  id: 'btn1',
  type: 'button',
  label: 'Click me',
  onClick: () => console.log('Button clicked'),
});

// 实际应用：中间件系统
type Middleware<T, R> = (input: T, next: () => R) => R;

class Pipeline<T> {
  private middlewares: Middleware<T, any>[] = [];

  use<R>(middleware: Middleware<T, R>): Pipeline<R> {
    const newPipeline = new Pipeline<R>();
    newPipeline.middlewares = [...this.middlewares, middleware];
    return newPipeline;
  }

  async execute(input: T): Promise<any> {
    let result = input;

    for (const middleware of this.middlewares) {
      result = await middleware(result, () => result);
    }

    return result;
  }
}

// 使用示例
type Context = {
  user?: User;
  request: Request;
  response: Response;
};

const pipeline = new Pipeline<Context>()
  .use(async (ctx, next) => {
    console.log('Request received');
    return next();
  })
  .use(async (ctx, next) => {
    ctx.user = await getUserFromRequest(ctx.request);
    return next();
  })
  .use(async (ctx, next) => {
    console.log('Processing request');
    return next();
  });
```

## 🎨 React 中的泛型模式

### 泛型组件
**创建可重用的 React 组件**

```typescript
// 泛型函数组件
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string;
  onItemClick?: (item: T) => void;
  emptyMessage?: string;
}

function List<T>({ items, renderItem, keyExtractor, onItemClick, emptyMessage }: ListProps<T>) {
  if (items.length === 0) {
    return <div>{emptyMessage || 'No items to display'}</div>;
  }

  return (
    <ul>
      {items.map((item, index) => (
        <li
          key={keyExtractor(item)}
          onClick={() => onItemClick?.(item)}
          style={{ cursor: onItemClick ? 'pointer' : 'default' }}
        >
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
      renderItem={(user) => (
        <div>
          <strong>{user.name}</strong>
          <br />
          <small>{user.email}</small>
        </div>
      )}
      keyExtractor={(user) => user.id}
      onItemClick={(user) => console.log('Selected:', user.name)}
      emptyMessage="No users found"
    />
  );
}
```

### 泛型 Hook
**创建可重用的自定义 Hook**

```typescript
// 泛型数据获取 Hook
interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

function useApi<T>(
  url: string,
  options?: {
    immediate?: boolean;
    dependencies?: React.DependencyList;
  }
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json() as T;
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    if (options?.immediate !== false) {
      fetchData();
    }
  }, [fetchData, ...(options?.dependencies || [])]);

  return { data, loading, error, refetch: fetchData };
}

// 使用示例
function UserProfile({ userId }: { userId: string }) {
  const { data: user, loading, error } = useApi<User>(`/api/users/${userId}`);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}

// 泛型状态管理 Hook
interface StateManager<T> {
  state: T;
  updateState: (updates: Partial<T>) => void;
  resetState: () => void;
}

function useStateManager<T>(initialState: T): StateManager<T> {
  const [state, setState] = useState(initialState);

  const updateState = useCallback((updates: Partial<T>) => {
    setState(prevState => ({ ...prevState, ...updates }));
  }, []);

  const resetState = useCallback(() => {
    setState(initialState);
  }, [initialState]);

  return { state, updateState, resetState };
}

// 使用示例
interface FormData {
  name: string;
  email: string;
  age: number;
}

function UserForm() {
  const { state, updateState, resetState } = useStateManager<FormData>({
    name: '',
    email: '',
    age: 0,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form data:', state);
    resetState();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Name"
        value={state.name}
        onChange={(e) => updateState({ name: e.target.value })}
      />
      <input
        type="email"
        placeholder="Email"
        value={state.email}
        onChange={(e) => updateState({ email: e.target.value })}
      />
      <input
        type="number"
        placeholder="Age"
        value={state.age}
        onChange={(e) => updateState({ age: parseInt(e.target.value) || 0 })}
      />
      <button type="submit">Submit</button>
    </form>
  );
}
```

### 泛型表单处理
**类型安全的表单处理**

```typescript
// 泛型表单接口
interface FormField<T = any> {
  name: string;
  label: string;
  type: string;
  value: T;
  required?: boolean;
  validation?: (value: T) => string | null;
}

interface FormState<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
}

// 泛型表单 Hook
function useForm<T extends Record<string, any>>(
  initialValues: T,
  validations?: Partial<Record<keyof T, (value: any) => string | null>>
) {
  const [formState, setFormState] = useState<FormState<T>>({
    values: initialValues,
    errors: {},
    touched: {},
    isValid: true,
  });

  const setValue = useCallback((name: keyof T, value: any) => {
    setFormState(prev => {
      const newValues = { ...prev.values, [name]: value };
      const error = validations?.[name]?.(value);
      const newErrors = { ...prev.errors, [name]: error };

      return {
        ...prev,
        values: newValues,
        errors: newErrors,
        isValid: Object.values(newErrors).every(err => !err),
      };
    });
  }, [validations]);

  const setTouched = useCallback((name: keyof T) => {
    setFormState(prev => ({
      ...prev,
      touched: { ...prev.touched, [name]: true },
    }));
  }, []);

  const validate = useCallback(() => {
    let isValid = true;
    const errors: Partial<Record<keyof T, string>> = {};

    Object.entries(validations || {}).forEach(([key, validation]) => {
      const error = validation(formState.values[key as keyof T]);
      if (error) {
        errors[key as keyof T] = error;
        isValid = false;
      }
    });

    setFormState(prev => ({
      ...prev,
      errors,
      isValid,
    }));

    return isValid;
  }, [formState.values, validations]);

  const reset = useCallback(() => {
    setFormState({
      values: initialValues,
      errors: {},
      touched: {},
      isValid: true,
    });
  }, [initialValues]);

  return {
    formState,
    setValue,
    setTouched,
    validate,
    reset,
  };
}

// 使用示例
interface UserRegistration {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

function RegistrationForm() {
  const { formState, setValue, setTouched, validate, reset } = useForm<UserRegistration>(
    {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
    {
      name: (value) => (value.length < 2 ? 'Name must be at least 2 characters' : null),
      email: (value) => (!value.includes('@') ? 'Invalid email address' : null),
      password: (value) => (value.length < 8 ? 'Password must be at least 8 characters' : null),
      confirmPassword: (value) => (value !== formState.values.password ? 'Passwords do not match' : null),
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      console.log('Form submitted:', formState.values);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Name</label>
        <input
          type="text"
          value={formState.values.name}
          onChange={(e) => setValue('name', e.target.value)}
          onBlur={() => setTouched('name')}
        />
        {formState.touched.name && formState.errors.name && (
          <span style={{ color: 'red' }}>{formState.errors.name}</span>
        )}
      </div>

      <div>
        <label>Email</label>
        <input
          type="email"
          value={formState.values.email}
          onChange={(e) => setValue('email', e.target.value)}
          onBlur={() => setTouched('email')}
        />
        {formState.touched.email && formState.errors.email && (
          <span style={{ color: 'red' }}>{formState.errors.email}</span>
        )}
      </div>

      <div>
        <label>Password</label>
        <input
          type="password"
          value={formState.values.password}
          onChange={(e) => setValue('password', e.target.value)}
          onBlur={() => setTouched('password')}
        />
        {formState.touched.password && formState.errors.password && (
          <span style={{ color: 'red' }}>{formState.errors.password}</span>
        )}
      </div>

      <div>
        <label>Confirm Password</label>
        <input
          type="password"
          value={formState.values.confirmPassword}
          onChange={(e) => setValue('confirmPassword', e.target.value)}
          onBlur={() => setTouched('confirmPassword')}
        />
        {formState.touched.confirmPassword && formState.errors.confirmPassword && (
          <span style={{ color: 'red' }}>{formState.errors.confirmPassword}</span>
        )}
      </div>

      <button type="submit" disabled={!formState.isValid}>
        Register
      </button>
    </form>
  );
}
```

## 📋 最佳实践

### 泛型命名约定
```typescript
// 常用泛型参数名称
// T - Type (最常见的泛型参数)
// K - Key
// V - Value
// E - Element
// R - Return type
// P - Properties
// S - State
// D - Data

// 好的命名
interface Repository<T> { ... }
interface KeyValuePair<K, V> { ... }
class Component<P, S> { ... }

// 避免
interface Repository<TypeParameter> { ... }
interface KeyValuePair<KeyType, ValueType> { ... }
```

### 避免过度泛型化
```typescript
// ❌ 过度泛型化
function processData<T, U, V, W>(data: T, processor: (item: T) => U, validator: (item: U) => V, formatter: (item: V) => W): W {
  // 复杂的实现
}

// ✅ 简化设计
interface DataProcessor<T, R> {
  process(data: T): R;
}

function processData<T, R>(data: T, processor: DataProcessor<T, R>): R {
  return processor.process(data);
}
```

### 提供合理的默认值
```typescript
// 好的默认类型
interface Response<T = any> {
  data: T;
  status: number;
}

class Cache<K = string, V = any> {
  private data = new Map<K, V>();
  // ...
}

// 泛型约束提供更好的类型安全
interface Identifiable {
  id: string;
}

interface Repository<T extends Identifiable> {
  find(id: string): Promise<T>;
}
```

## 📖 总结

TypeScript 泛型提供了强大的类型抽象能力：

### 核心概念：
1. **泛型函数**: 创建类型可重用的函数
2. **泛型接口**: 定义灵活的对象类型
3. **泛型类**: 创建类型安全的类组件
4. **泛型约束**: 限制泛型类型的范围

### 高级模式：
1. **泛型工厂模式**: 创建泛型对象的工厂
2. **泛型装饰器模式**: 增强对象功能
3. **泛型组合模式**: 组合多个泛型类型

### React 应用：
1. **泛型组件**: 创建可重用的 React 组件
2. **泛型 Hook**: 创建类型安全的自定义 Hook
3. **泛型表单处理**: 类型安全的表单管理

### 最佳实践：
1. **合理的命名约定**: 使用标准泛型参数名称
2. **避免过度泛型化**: 保持设计的简洁性
3. **提供默认值**: 为泛型参数提供合理的默认类型
4. **适当的约束**: 使用约束提供更好的类型安全

掌握这些泛型模式将帮助你在 Next.js 开发中编写更加类型安全、可重用和可维护的代码。