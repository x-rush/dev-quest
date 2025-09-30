# React 核心概念速查手册

## 组件 (Components)

### 函数组件

```typescript
// 基础函数组件
type GreetingProps = {
  name: string;
  age?: number;
};

const Greeting: React.FC<GreetingProps> = ({ name, age }) => {
  return <h1>Hello, {name}! {age && `You are ${age} years old.`}</h1>;
};

// 使用
<Greeting name="Alice" age={25} />
```

### 类组件

```typescript
import React, { Component } from 'react';

type CounterState = {
  count: number;
};

type CounterProps = {
  initialCount?: number;
};

class Counter extends Component<CounterProps, CounterState> {
  state: CounterState = {
    count: this.props.initialCount || 0,
  };

  increment = () => {
    this.setState(prevState => ({
      count: prevState.count + 1,
    }));
  };

  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={this.increment}>Increment</button>
      </div>
    );
  }
}
```

## Hooks

### useState

```typescript
// 基础用法
const [count, setCount] = useState<number>(0);
const [user, setUser] = useState<User | null>(null);

// 函数式更新
setCount(prevCount => prevCount + 1);

// 对象更新
setUser(prevUser => ({
  ...prevUser,
  name: 'New Name',
}));
```

### useEffect

```typescript
// 基础用法
useEffect(() => {
  // 组件挂载时执行
  console.log('Component mounted');

  // 清理函数
  return () => {
    console.log('Component will unmount');
  };
}, []);

// 依赖数组
useEffect(() => {
  // 当依赖项变化时执行
  fetchData(userId);
}, [userId]);

// 避免无限循环
useEffect(() => {
  const timer = setInterval(() => {
    setCount(prev => prev + 1);
  }, 1000);

  return () => clearInterval(timer);
}, []);
```

### useContext

```typescript
// 创建 Context
type Theme = 'light' | 'dark';

const ThemeContext = React.createContext<{
  theme: Theme;
  setTheme: (theme: Theme) => void;
}>({
  theme: 'light',
  setTheme: () => {},
});

// 提供者
const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>('light');

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// 消费者
const ThemedComponent: React.FC = () => {
  const { theme, setTheme } = useContext(ThemeContext);

  return (
    <div className={theme}>
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        Toggle Theme
      </button>
    </div>
  );
};
```

### useReducer

```typescript
type State = {
  count: number;
  loading: boolean;
};

type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'reset' }
  | { type: 'loading_start' }
  | { type: 'loading_end' };

const initialState: State = {
  count: 0,
  loading: false,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + 1 };
    case 'decrement':
      return { ...state, count: state.count - 1 };
    case 'reset':
      return { ...state, count: 0 };
    case 'loading_start':
      return { ...state, loading: true };
    case 'loading_end':
      return { ...state, loading: false };
    default:
      return state;
  }
}

const Counter: React.FC = () => {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <div>
      <p>Count: {state.count}</p>
      {state.loading && <p>Loading...</p>}
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  );
};
```

### useCallback

```typescript
// 基础用法
const memoizedCallback = useCallback(
  (a: number, b: number) => {
    return a + b;
  },
  [a, b] // 依赖项
);

// 实际应用
const Parent: React.FC = () => {
  const [count, setCount] = useState(0);

  const handleClick = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);

  return <Child onClick={handleClick} />;
};
```

### useMemo

```typescript
// 基础用法
const memoizedValue = useMemo(
  () => computeExpensiveValue(a, b),
  [a, b] // 依赖项
);

// 实际应用
const UserList: React.FC<{ users: User[] }> = ({ users }) => {
  const sortedUsers = useMemo(() => {
    return [...users].sort((a, b) => a.name.localeCompare(b.name));
  }, [users]);

  return (
    <ul>
      {sortedUsers.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
};
```

### useRef

```typescript
// DOM 引用
const inputRef = useRef<HTMLInputElement>(null);

const focusInput = () => {
  inputRef.current?.focus();
};

return <input ref={inputRef} />;

// 持久化值
const timerRef = useRef<NodeJS.Timeout | null>(null);

useEffect(() => {
  timerRef.current = setInterval(() => {
    console.log('Tick');
  }, 1000);

  return () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  };
}, []);
```

## 事件处理

### 基础事件处理

```typescript
// 点击事件
const Button: React.FC = () => {
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    console.log('Button clicked!');
  };

  return <button onClick={handleClick}>Click me</button>;
};

// 表单事件
const Form: React.FC = () => {
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // 处理表单提交
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* 表单内容 */}
    </form>
  );
};

// 输入事件
const Input: React.FC = () => {
  const [value, setValue] = useState('');

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValue(event.target.value);
  };

  return <input value={value} onChange={handleChange} />;
};
```

## 条件渲染

### 三元运算符

```typescript
const UserStatus: React.FC<{ isLoggedIn: boolean }> = ({ isLoggedIn }) => {
  return (
    <div>
      {isLoggedIn ? (
        <p>Welcome back!</p>
      ) : (
        <p>Please log in</p>
      )}
    </div>
  );
};
```

### 逻辑与运算符

```typescript
const UserProfile: React.FC<{ user?: User }> = ({ user }) => {
  return (
    <div>
      {user && <p>Hello, {user.name}</p>}
    </div>
  );
};
```

### switch 语句

```typescript
const StatusMessage: React.FC<{ status: 'loading' | 'success' | 'error' }> = ({ status }) => {
  const getMessage = () => {
    switch (status) {
      case 'loading':
        return 'Loading...';
      case 'success':
        return 'Success!';
      case 'error':
        return 'Error occurred';
      default:
        return 'Unknown status';
    }
  };

  return <p>{getMessage()}</p>;
};
```

## 列表渲染

### 基础列表渲染

```typescript
const UserList: React.FC<{ users: User[] }> = ({ users }) => {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          {user.name} - {user.email}
        </li>
      ))}
    </ul>
  );
};
```

### 带索引的列表

```typescript
const NumberedList: React.FC<{ items: string[] }> = ({ items }) => {
  return (
    <ol>
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ol>
  );
};
```

## 表单处理

### 受控组件

```typescript
const ControlledForm: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    console.log('Form submitted:', formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Name"
      />
      <input
        type="email"
        name="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="Email"
      />
      <textarea
        name="message"
        value={formData.message}
        onChange={handleChange}
        placeholder="Message"
      />
      <button type="submit">Submit</button>
    </form>
  );
};
```

### 非受控组件

```typescript
const UncontrolledForm: React.FC = () => {
  const nameRef = useRef<HTMLInputElement>(null);
  const emailRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const formData = {
      name: nameRef.current?.value || '',
      email: emailRef.current?.value || '',
    };
    console.log('Form submitted:', formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" ref={nameRef} placeholder="Name" />
      <input type="email" ref={emailRef} placeholder="Email" />
      <button type="submit">Submit</button>
    </form>
  );
};
```

## 样式处理

### 内联样式

```typescript
const StyledComponent: React.FC = () => {
  const style: React.CSSProperties = {
    color: 'red',
    fontSize: '16px',
    backgroundColor: '#f0f0f0',
    padding: '10px',
    borderRadius: '5px',
  };

  return <div style={style}>Styled div</div>;
};
```

### CSS Modules

```typescript
// Component.module.css
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
}

// Component.tsx
import styles from './Component.module.css';

const Component: React.FC = () => {
  return (
    <div className={styles.container}>
      <button className={styles.button}>Click me</button>
    </div>
  );
};
```

### CSS-in-JS (styled-components)

```typescript
import styled from 'styled-components';

const StyledButton = styled.button<{ variant: 'primary' | 'secondary' }>`
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;

  background-color: ${props =>
    props.variant === 'primary' ? '#007bff' : '#6c757d'
  };
  color: white;

  &:hover {
    opacity: 0.9;
  }
`;

const ButtonExample: React.FC = () => {
  return (
    <div>
      <StyledButton variant="primary">Primary Button</StyledButton>
      <StyledButton variant="secondary">Secondary Button</StyledButton>
    </div>
  );
};
```

## 生命周期方法

### 函数组件生命周期

```typescript
const ComponentLifecycle: React.FC = () => {
  // 组件创建时执行（只执行一次）
  useEffect(() => {
    console.log('Component mounted');

    return () => {
      console.log('Component will unmount');
    };
  }, []);

  // 组件更新时执行
  useEffect(() => {
    console.log('Component updated');
  });

  // 特定状态更新时执行
  useEffect(() => {
    console.log('Count changed');
  }, [count]);

  return <div>Component Lifecycle Example</div>;
};
```

### 类组件生命周期

```typescript
class ClassComponentLifecycle extends React.Component {
  constructor(props: any) {
    super(props);
    console.log('Constructor');
  }

  componentDidMount() {
    console.log('Component mounted');
  }

  componentDidUpdate(prevProps: any, prevState: any) {
    console.log('Component updated');
  }

  componentWillUnmount() {
    console.log('Component will unmount');
  }

  render() {
    return <div>Class Component Lifecycle</div>;
  }
}
```

## 错误边界

```typescript
class ErrorBoundary extends React.Component<
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
    console.error('Error caught by error boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div>
          <h2>Something went wrong.</h2>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

// 使用
const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <MyComponent />
    </ErrorBoundary>
  );
};
```

## 性能优化

### React.memo

```typescript
const ExpensiveComponent: React.FC<{ data: Data }> = React.memo(({ data }) => {
  console.log('ExpensiveComponent rendered');
  return <div>{data.name}</div>;
});

// 使用自定义比较函数
const CustomMemoComponent: React.FC<{ user: User }> = React.memo(
  ({ user }) => {
    console.log('CustomMemoComponent rendered');
    return <div>{user.name}</div>;
  },
  (prevProps, nextProps) => {
    return prevProps.user.id === nextProps.user.id;
  }
);
```

### useMemo 和 useCallback

```typescript
// useMemo 用于缓存计算结果
const ExpensiveCalculation: React.FC<{ items: Item[] }> = ({ items }) => {
  const sortedItems = useMemo(() => {
    console.log('Sorting items...');
    return [...items].sort((a, b) => a.value - b.value);
  }, [items]);

  return (
    <div>
      {sortedItems.map(item => (
        <div key={item.id}>{item.name}: {item.value}</div>
      ))}
    </div>
  );
};

// useCallback 用于缓存函数
const ParentComponent: React.FC = () => {
  const [count, setCount] = useState(0);

  const handleClick = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);

  return <ChildComponent onClick={handleClick} />;
};
```

## 高阶组件 (HOC)

```typescript
// 基础 HOC
function withLogger<P extends object>(WrappedComponent: React.ComponentType<P>) {
  return (props: P) => {
    console.log(`${WrappedComponent.name} rendered`);
    return <WrappedComponent {...props} />;
  };
}

// 带参数的 HOC
function withAuth<P extends { user?: User }>(
  WrappedComponent: React.ComponentType<P>,
  requiredRole: string
) {
  return (props: P) => {
    const { user, ...restProps } = props;

    if (!user || user.role !== requiredRole) {
      return <div>Access denied</div>;
    }

    return <WrappedComponent {...restProps as P} user={user} />;
  };
}

// 使用
const ProtectedComponent = withAuth(DashboardComponent, 'admin');
const LoggedComponent = withLogger(ProfileComponent);
```

## 渲染模式

### 服务端组件 (React 19)

```typescript
// 服务端组件 - 不能使用 hooks 和状态
async function ServerComponent({ id }: { id: string }) {
  const data = await fetchData(id);

  return (
    <div>
      <h1>{data.title}</h>
      <p>{data.content}</p>
    </div>
  );
}

// 在 Next.js 中使用
export default async function Page({ params }: { params: { id: string } }) {
  return <ServerComponent id={params.id} />;
}
```

### 客户端组件

```typescript
'use client';

import { useState, useEffect } from 'react';

function ClientComponent({ initialData }: { initialData: Data }) {
  const [data, setData] = useState(initialData);
  const [isLoading, setIsLoading] = useState(false);

  const handleRefresh = async () => {
    setIsLoading(true);
    const newData = await fetchData(data.id);
    setData(newData);
    setIsLoading(false);
  };

  return (
    <div>
      <h1>{data.title}</h1>
      <p>{data.content}</p>
      <button onClick={handleRefresh} disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Refresh'}
      </button>
    </div>
  );
}
```

## 常见模式

### 复合组件

```typescript
// Tab 组件
const Tabs: React.FC<{ children: React.ReactNode }> & {
  Tab: React.FC<{ title: string; children: React.ReactNode }>;
} = ({ children }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = React.Children.toArray(children).filter(
    (child): child is React.ReactElement =>
      React.isValidElement(child) && child.type === Tabs.Tab
  );

  return (
    <div>
      <div className="tab-headers">
        {tabs.map((tab, index) => (
          <button
            key={index}
            onClick={() => setActiveTab(index)}
            className={activeTab === index ? 'active' : ''}
          >
            {tab.props.title}
          </button>
        ))}
      </div>
      <div className="tab-content">
        {tabs[activeTab]}
      </div>
    </div>
  );
};

Tabs.Tab = ({ children }) => <div>{children}</div>;

// 使用
const App: React.FC = () => {
  return (
    <Tabs>
      <Tabs.Tab title="Tab 1">
        <div>Content 1</div>
      </Tabs.Tab>
      <Tabs.Tab title="Tab 2">
        <div>Content 2</div>
      </Tabs.Tab>
    </Tabs>
  );
};
```

### Provider 模式

```typescript
// 创建 Context
interface AppContextType {
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
  user: User | null;
  setUser: (user: User | null) => void;
}

const AppContext = React.createContext<AppContextType | undefined>(undefined);

// Provider 组件
const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [user, setUser] = useState<User | null>(null);

  const value: AppContextType = {
    theme,
    setTheme,
    user,
    setUser,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

// Hook 用于使用 Context
const useApp = () => {
  const context = React.useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

// 使用
const ThemeSwitcher: React.FC = () => {
  const { theme, setTheme } = useApp();

  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      Switch to {theme === 'light' ? 'dark' : 'light'} theme
    </button>
  );
};
```

## 最佳实践

### 组件设计原则

1. **单一职责原则**：每个组件只负责一个功能
2. **可复用性**：设计可复用的组件
3. **可测试性**：确保组件易于测试
4. **性能优化**：避免不必要的重渲染

### 代码组织

```typescript
// 推荐的组件结构
interface ComponentProps {
  // Props 定义
}

const Component: React.FC<ComponentProps> = ({ prop1, prop2 }) => {
  // Hooks
  const [state, setState] = useState('');

  // 事件处理函数
  const handleClick = () => {
    // 处理逻辑
  };

  // 副作用
  useEffect(() => {
    // 副作用逻辑
  }, []);

  // 渲染
  return (
    <div>
      {/* JSX */}
    </div>
  );
};

export default Component;
```

### 性能最佳实践

1. **使用 memo 避免不必要的重渲染**
2. **使用 useMemo 缓存计算结果**
3. **使用 useCallback 缓存函数**
4. **合理使用 useEffect 依赖项**
5. **避免在渲染函数中创建新对象**

### 错误处理

```typescript
// 错误边界
const ErrorBoundary: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      console.error('Global error:', event.error);
      setHasError(true);
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return <div>Something went wrong. Please refresh the page.</div>;
  }

  return <>{children}</>;
};

// Promise 错误处理
const AsyncComponent: React.FC = () => {
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetchData()
      .catch(err => setError(err));
  }, []);

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return <div>Loading...</div>;
};
```

这个速查手册涵盖了 React 开发中最常用的概念和模式，可以作为日常开发的参考指南。