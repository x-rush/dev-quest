# React 组件模式

## 📚 概述

React 组件是构建用户界面的基本单元。本文档涵盖了 React 19 的现代组件模式，包括函数组件、复合组件、高阶组件、自定义 Hooks 等设计模式，以及最佳实践。

## 🏗️ 基础组件模式

### 函数组件
**最简单和推荐的组件形式**

```typescript
// 基础函数组件
interface GreetingProps {
  name: string;
  age?: number;
}

function Greeting({ name, age = 0 }: GreetingProps) {
  return (
    <div>
      <h1>Hello, {name}!</h1>
      {age > 0 && <p>You are {age} years old.</p>}
    </div>
  );
}

// 箭头函数组件
const Button = ({
  onClick,
  children,
  variant = 'primary'
}: {
  onClick: () => void;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}) => {
  return (
    <button
      onClick={onClick}
      className={`btn btn-${variant}`}
    >
      {children}
    </button>
  );
};
```

### 受控组件
**表单元素由 React 状态控制**

```typescript
function ControlledInput() {
  const [value, setValue] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Submitted value:', value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder="Enter text..."
      />
      <button type="submit">Submit</button>
    </form>
  );
}

// 多个表单字段
interface FormData {
  name: string;
  email: string;
  age: number;
}

function ComplexForm() {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    age: 0,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseInt(value) || 0 : value,
    }));
  };

  return (
    <form>
      <input
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Name"
      />
      <input
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="Email"
      />
      <input
        name="age"
        type="number"
        value={formData.age}
        onChange={handleChange}
        placeholder="Age"
      />
    </form>
  );
}
```

## 🎯 高级组件模式

### 复合组件 (Compound Components)
**组件组合在一起工作**

```typescript
// Accordion 复合组件
interface AccordionContextType {
  openItem: string | null;
  toggleItem: (id: string) => void;
}

const AccordionContext = createContext<AccordionordionContextType>({
  openItem: null,
  toggleItem: () => {},
});

function Accordion({ children }: { children: React.ReactNode }) {
  const [openItem, setOpenItem] = useState<string | null>(null);

  const toggleItem = (id: string) => {
    setOpenItem(prev => (prev === id ? null : id));
  };

  return (
    <AccordionContext.Provider value={{ openItem, toggleItem }}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  );
}

function AccordionItem({
  id,
  children
}: {
  id: string;
  children: React.ReactNode;
}) {
  const { openItem, toggleItem } = useContext(AccordionContext);
  const isOpen = openItem === id;

  return (
    <div className={`accordion-item ${isOpen ? 'open' : ''}`}>
      {children}
    </div>
  );
}

function AccordionHeader({ children, id }: {
  children: React.ReactNode;
  id: string;
}) {
  const { toggleItem } = useContext(AccordionContext);

  return (
    <button
      className="accordion-header"
      onClick={() => toggleItem(id)}
    >
      {children}
    </button>
  );
}

function AccordionPanel({ children, id }: {
  children: React.ReactNode;
  id: string;
}) {
  const { openItem } = useContext(AccordionContext);
  const isOpen = openItem === id;

  return (
    <div
      className={`accordion-panel ${isOpen ? 'open' : ''}`}
      hidden={!isOpen}
    >
      {children}
    </div>
  );
}

// 使用
function App() {
  return (
    <Accordion>
      <AccordionItem id="section1">
        <AccordionHeader id="section1">Section 1</AccordionHeader>
        <AccordionPanel id="section1">
          Content for section 1...
        </AccordionPanel>
      </AccordionItem>

      <AccordionItem id="section2">
        <AccordionHeader id="section2">Section 2</AccordionHeader>
        <AccordionPanel id="section2">
          Content for section 2...
        </AccordionPanel>
      </AccordionItem>
    </Accordion>
  );
}
```

### Render Props 模式
**通过函数 prop 传递渲染逻辑**

```typescript
interface MousePosition {
  x: number;
  y: number;
}

interface MouseTrackerProps {
  render: (position: MousePosition) => React.ReactNode;
}

function MouseTracker({ render }: MouseTrackerProps) {
  const [position, setPosition] = useState<MousePosition>({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return <>{render(position)}</>;
}

// 使用
function App() {
  return (
    <MouseTracker
      render={({ x, y }) => (
        <div>
          Mouse position: {x}, {y}
        </div>
      )}
    />
  );
}

// 现代 React 更倾向于使用自定义 Hooks
function useMousePosition() {
  const [position, setPosition] = useState<MousePosition>({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return position;
}

function ModernApp() {
  const { x, y } = useMousePosition();

  return <div>Mouse position: {x}, {y}</div>;
}
```

### 高阶组件 (HOC)
**组件装饰器模式**

```typescript
// 基础 HOC
function withLoading<P extends object>(
  Component: React.ComponentType<P>
) {
  return function WithLoadingComponent(props: P & { loading?: boolean }) {
    const { loading, ...rest } = props;

    if (loading) {
      return <div>Loading...</div>;
    }

    return <Component {...(rest as P)} />;
  };
}

// 使用 HOC
interface UserProps {
  user: { name: string; email: string };
}

function UserProfile({ user }: UserProps) {
  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}

const UserProfileWithLoading = withLoading(UserProfile);

// 更复杂的 HOC - 错误边界
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

interface ErrorBoundaryProps {
  fallback?: React.ReactNode;
  onError?: (error: Error) => void;
}

function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>
) {
  return function WithErrorBoundaryComponent(props: P & ErrorBoundaryProps) {
    const { fallback, onError, ...rest } = props;
    const [hasError, setError] = useState(false);
    const [error, setErrorState] = useState<Error | undefined>();

    useEffect(() => {
      if (hasError && onError && error) {
        onError(error);
      }
    }, [hasError, error, onError]);

    const handleError = (error: Error) => {
      setError(true);
      setErrorState(error);
    };

    if (hasError) {
      return (
        fallback || (
          <div>
            <h2>Something went wrong.</h2>
            <details>
              <summary>Error details</summary>
              <pre>{error?.message}</pre>
            </details>
          </div>
        )
      );
    }

    return (
      <ErrorBoundaryProvider onError={handleError}>
        <Component {...(rest as P)} />
      </ErrorBoundaryProvider>
    );
  };
}
```

## 🎨 现代 React 19 模式

### Server Components
**在服务器上渲染的组件**

```typescript
// ✅ 服务器组件
async function BlogPost({ id }: { id: string }) {
  const post = await fetch(`https://api.example.com/posts/${id}`);
  const data = await post.json();

  return (
    <article>
      <h1>{data.title}</h1>
      <p>{data.content}</p>
    </article>
  );
}

// ❌ 不能在服务器组件中使用状态或事件
function ClientComponent() {
  const [count, setCount] = useState(0); // ❌ 错误：不能在服务器组件中

  return <button onClick={() => setCount(count + 1)}>Click me</button>; // ❌ 错误
}

// ✅ 服务器组件可以导入客户端组件
'use client';

function InteractiveCounter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}

// 在服务器组件中使用客户端组件
async function BlogPostWithCounter({ id }: { id: string }) {
  const post = await fetch(`https://api.example.com/posts/${id}`);
  const data = await post.json();

  return (
    <article>
      <h1>{data.title}</h1>
      <p>{data.content}</p>
      <InteractiveCounter />
    </article>
  );
}
```

### 并发模式 (Concurrent Mode)
**React 19 的并发特性**

```typescript
// 使用 startTransition 标记非紧急更新
import { startTransition, useState } from 'react';

function SearchableList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<string[]>([]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);

    // 标记为非紧急更新
    startTransition(() => {
      setResults(searchDatabase(value));
    });
  };

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={handleSearch}
        placeholder="Search..."
      />
      <ul>
        {results.map((result, index) => (
          <li key={index}>{result}</li>
        ))}
      </ul>
    </div>
  );
}

// 使用 useDeferredValue 优化输入
function DeferredSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const deferredSearchTerm = useDeferredValue(searchTerm);

  const results = useMemo(() => {
    return searchDatabase(deferredSearchTerm);
  }, [deferredSearchTerm]);

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search..."
      />
      <List results={results} />
    </div>
  );
}
```

### Suspense 模式
**处理异步组件加载**

```typescript
// 数据获取的 Suspense
async function fetchUser(id: string) {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
}

function UserProfile({ id }: { id: string }) {
  const user = fetchUser(id); // React 19 支持直接在组件中 await

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}

function App() {
  return (
    <Suspense fallback={<div>Loading profile...</div>}>
      <UserProfile id="123" />
    </Suspense>
  );
}

// 代码分割的 Suspense
const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <div>
      <h1>My App</h1>
      <Suspense fallback={<div>Loading component...</div>}>
        <LazyComponent />
      </Suspense>
    </div>
  );
}
```

## 🏢 容器/展示组件模式

### 容器组件
**处理数据获取和状态管理**

```typescript
// 容器组件
function UserListContainer() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/users');
        const data = await response.json();
        setUsers(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleDeleteUser = async (userId: string) => {
    try {
      await fetch(`/api/users/${userId}`, { method: 'DELETE' });
      setUsers(prev => prev.filter(user => user.id !== userId));
    } catch (err) {
      setError('Failed to delete user');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <UserList
      users={users}
      onDeleteUser={handleDeleteUser}
    />
  );
}

// 展示组件
interface UserListProps {
  users: User[];
  onDeleteUser: (userId: string) => void;
}

function UserList({ users, onDeleteUser }: UserListProps) {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          <span>{user.name} - {user.email}</span>
          <button
            onClick={() => onDeleteUser(user.id)}
            aria-label={`Delete ${user.name}`}
          >
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
```

## 🎯 自定义 Hook 模式

### 逻辑复用模式
**将组件逻辑提取到自定义 Hooks**

```typescript
// 数据获取 Hook
function useData<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
}

// 表单管理 Hook
function useForm<T extends Record<string, any>>(initialValues: T) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const setValue = useCallback((name: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    // 清除该字段的错误
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  }, [errors]);

  const setError = useCallback((name: keyof T, error: string) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  }, []);

  const setSubmitting = useCallback((submitting: boolean) => {
    setIsSubmitting(submitting);
  }, []);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setIsSubmitting(false);
  }, [initialValues]);

  return {
    values,
    errors,
    isSubmitting,
    setValue,
    setError,
    setSubmitting,
    reset,
  };
}

// 使用自定义 Hook
function UserForm() {
  const { values, errors, setValue, setError, isSubmitting, reset } = useForm({
    name: '',
    email: '',
    age: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // 验证逻辑
    if (!values.name) {
      setError('name', 'Name is required');
      setIsSubmitting(false);
      return;
    }

    try {
      // 提交逻辑
      await submitUser(values);
      reset();
    } catch (error) {
      console.error('Submit error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={values.name}
        onChange={(e) => setValue('name', e.target.value)}
        placeholder="Name"
      />
      {errors.name && <span className="error">{errors.name}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

## 🔧 状态管理模式

### 状态提升 (Lifting State Up)
**将共享状态提升到最近的共同祖先组件**

```typescript
// 状态提升示例
function TemperatureCalculator() {
  const [temperature, setTemperature] = useState('');
  const [scale, setScale] = useState<'celsius' | 'fahrenheit'>('celsius');

  const handleCelsiusChange = (value: string) => {
    setTemperature(value);
    setScale('celsius');
  };

  const handleFahrenheitChange = (value: string) => {
    setTemperature(value);
    setScale('fahrenheit');
  };

  const celsius = scale === 'fahrenheit'
    ? tryConvert(temperature, toCelsius)
    : temperature;

  const fahrenheit = scale === 'celsius'
    ? tryConvert(temperature, toFahrenheit)
    : temperature;

  return (
    <div>
      <TemperatureInput
        scale="celsius"
        temperature={celsius}
        onTemperatureChange={handleCelsiusChange}
      />
      <TemperatureInput
        scale="fahrenheit"
        temperature={fahrenheit}
        onTemperatureChange={handleFahrenheitChange}
      />
      <BoilingVerdict
        celsius={parseFloat(celsius)}
      />
    </div>
  );
}
```

## 📋 最佳实践

### 组件设计原则
1. **单一职责**: 每个组件只负责一个功能
2. **组合优于继承**: 使用组件组合而不是继承
3. **Props 验证**: 使用 TypeScript 或 PropTypes 验证 props
4. **性能优化**: 合理使用 memo, useMemo, useCallback

### 错误处理
```typescript
// 错误边界组件
class ErrorBoundary extends Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div>
          <h2>Something went wrong.</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 可访问性 (Accessibility)
```typescript
function Button({
  children,
  onClick,
  disabled = false
}: {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-disabled={disabled}
      role="button"
    >
      {children}
    </button>
  );
}

// 表单标签
function FormField({
  label,
  error,
  children
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  const id = useId();

  return (
    <div>
      <label htmlFor={id}>{label}</label>
      {React.cloneElement(children as React.ReactElement, { id })}
      {error && (
        <span id={`${id}-error`} role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
```

## 📖 总结

React 组件模式提供了丰富的工具来构建可维护、可复用的用户界面。掌握这些模式将帮助你：

1. **组织代码结构**: 使用合适的组件模式组织你的代码
2. **逻辑复用**: 通过自定义 Hooks 和高阶组件复用逻辑
3. **性能优化**: 使用并发模式和最佳实践优化性能
4. **用户体验**: 构建响应式、可访问的用户界面

React 19 的新特性进一步增强了这些模式，特别是 Server Components 和并发特性，为构建现代 Web 应用提供了更强大的工具。