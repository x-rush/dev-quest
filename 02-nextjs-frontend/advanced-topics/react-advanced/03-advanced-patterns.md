# React 19 高级模式与实践

## 📋 概述

React 19 引入了许多高级模式和最佳实践，这些模式可以帮助开发者构建更加健壮、可维护和高性能的应用程序。本文将深入探讨这些高级模式，并提供实际应用示例。

## 🎯 高级组件模式

### 1. Compound Components (复合组件)

复合组件模式允许你创建一组相互协作的组件，提供更加灵活和直观的API。

```typescript
// Tab组件示例
interface TabContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabContext = createContext<TabContextType | null>(null);

function TabGroup({ children, defaultTab }: {
  children: React.ReactNode;
  defaultTab: string;
}) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <TabContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tab-group">{children}</div>
    </TabContext.Provider>
  );
}

function TabList({ children }: { children: React.ReactNode }) {
  return <div className="tab-list">{children}</div>;
}

function Tab({ children, value }: {
  children: React.ReactNode;
  value: string;
}) {
  const context = useContext(TabContext);
  if (!context) throw new Error('Tab must be used within TabGroup');

  const { activeTab, setActiveTab } = context;
  const isActive = activeTab === value;

  return (
    <button
      className={`tab ${isActive ? 'active' : ''}`}
      onClick={() => setActiveTab(value)}
    >
      {children}
    </button>
  );
}

function TabPanel({ children, value }: {
  children: React.ReactNode;
  value: string;
}) {
  const context = useContext(TabContext);
  if (!context) throw new Error('TabPanel must be used within TabGroup');

  const { activeTab } = context;
  if (activeTab !== value) return null;

  return <div className="tab-panel">{children}</div>;
}

// 使用方式
function App() {
  return (
    <TabGroup defaultTab="profile">
      <TabList>
        <Tab value="profile">Profile</Tab>
        <Tab value="settings">Settings</Tab>
        <Tab value="security">Security</Tab>
      </TabList>
      <TabPanel value="profile">
        <ProfileContent />
      </TabPanel>
      <TabPanel value="settings">
        <SettingsContent />
      </TabPanel>
      <TabPanel value="security">
        <SecurityContent />
      </TabPanel>
    </TabGroup>
  );
}
```

### 2. Render Props 模式进化

```typescript
// 传统Render Props
class DataFetcher extends React.Component {
  state = { data: null, loading: false, error: null };

  async componentDidMount() {
    await this.fetchData();
  }

  fetchData = async () => {
    this.setState({ loading: true });
    try {
      const data = await this.props.fetchFunction();
      this.setState({ data, loading: false });
    } catch (error) {
      this.setState({ error, loading: false });
    }
  };

  render() {
    return this.props.children(this.state);
  }
}

// 现代化Render Props with Hooks
function useDataFetcher<T>(fetchFunction: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchFunction();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [fetchFunction]);

  return { data, loading, error, refetch: fetchData };
}

// 使用自定义Hook的Render Props组件
function DataFetcher<T>({
  fetchFunction,
  children
}: {
  fetchFunction: () => Promise<T>;
  children: (state: ReturnType<typeof useDataFetcher<T>>) => React.ReactNode;
}) {
  const state = useDataFetcher(fetchFunction);
  return <>{children(state)}</>;
}

// 使用方式
function UserProfile({ userId }: { userId: string }) {
  return (
    <DataFetcher
      fetchFunction={() => fetchUser(userId)}
    >
      {({ data, loading, error, refetch }) => {
        if (loading) return <div>Loading...</div>;
        if (error) return <div>Error: {error.message}</div>;
        if (!data) return null;

        return (
          <div>
            <h2>{data.name}</h2>
            <p>{data.email}</p>
            <button onClick={refetch}>Refresh</button>
          </div>
        );
      }}
    </DataFetcher>
  );
}
```

### 3. Controlled & Uncontrolled 模式

```typescript
// 双模式组件实现
interface InputProps {
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
}

function Input({ value, defaultValue, onChange, placeholder }: InputProps) {
  const [internalValue, setInternalValue] = useState(defaultValue || '');

  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    if (!isControlled) {
      setInternalValue(newValue);
    }
    onChange?.(newValue);
  };

  return (
    <input
      value={currentValue}
      onChange={handleChange}
      placeholder={placeholder}
    />
  );
}

// 使用示例
function ControlledExample() {
  const [value, setValue] = useState('');

  return (
    <div>
      <Input
        value={value}
        onChange={setValue}
        placeholder="Controlled input"
      />
      <p>Value: {value}</p>
    </div>
  );
}

function UncontrolledExample() {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    console.log(inputRef.current?.value);
  };

  return (
    <div>
      <Input
        defaultValue="Default value"
        placeholder="Uncontrolled input"
        ref={inputRef}
      />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}
```

## 🚀 状态管理高级模式

### 1. 自定义状态管理Hook

```typescript
// 轻量级状态管理
function createStore<T>(initialState: T) {
  let state = initialState;
  const listeners = new Set<() => void>();

  const setState = (updater: T | ((prev: T) => T)) => {
    state = typeof updater === 'function'
      ? (updater as (prev: T) => T)(state)
      : updater;
    listeners.forEach(listener => listener());
  };

  const useStore = () => {
    const [forceUpdate] = useState({});
    useEffect(() => {
      const listener = () => forceUpdate({});
      listeners.add(listener);
      return () => listeners.delete(listener);
    }, []);

    return [state, setState] as const;
  };

  return { useStore, getState: () => state };
}

// 使用示例
const { useStore } = createStore({
  user: null,
  theme: 'light',
  notifications: []
});

function useUserStore() {
  const [state, setState] = useStore();

  return {
    user: state.user,
    setUser: (user: any) => setState({ ...state, user }),
    clearUser: () => setState({ ...state, user: null })
  };
}
```

### 2. Context优化模式

```typescript
// 分离Context避免不必要的重渲染
interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  notifications: Notification[];
}

interface AppActions {
  setUser: (user: User | null) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  addNotification: (notification: Notification) => void;
}

// 状态Context
const AppContext = createContext<AppState | null>(null);

// 动作Context
const AppActionsContext = createContext<AppActions | null>(null);

// Provider组件
function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AppState>({
    user: null,
    theme: 'light',
    notifications: []
  });

  const actions: AppActions = {
    setUser: (user) => setState(prev => ({ ...prev, user })),
    setTheme: (theme) => setState(prev => ({ ...prev, theme })),
    addNotification: (notification) =>
      setState(prev => ({
        ...prev,
        notifications: [...prev.notifications, notification]
      }))
  };

  return (
    <AppContext.Provider value={state}>
      <AppActionsContext.Provider value={actions}>
        {children}
      </AppActionsContext.Provider>
    </AppContext.Provider>
  );
}

// 自定义Hook
function useAppState() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useAppState must be used within AppProvider');
  return context;
}

function useAppActions() {
  const context = useContext(AppActionsContext);
  if (!context) throw new Error('useAppActions must be used within AppProvider');
  return context;
}

// 组件使用
function UserProfile() {
  const { user } = useAppState(); // 只订阅状态变化
  return <div>{user?.name}</div>;
}

function ThemeSwitcher() {
  const { setTheme } = useAppActions(); // 只订阅动作
  return (
    <button onClick={() => setTheme('dark')}>
      Switch to Dark Mode
    </button>
  );
}
```

### 3. 状态机模式

```typescript
// 简单状态机实现
interface StateMachineConfig<TState, TEvent> {
  initial: TState;
  states: Record<TState, {
    on?: Record<TEvent, TState>;
    effects?: () => void;
  }>;
}

function useStateMachine<TState extends string, TEvent extends string>(
  config: StateMachineConfig<TState, TEvent>
) {
  const [currentState, setCurrentState] = useState<TState>(config.initial);

  const transition = (event: TEvent) => {
    const stateConfig = config.states[currentState];
    const nextState = stateConfig.on?.[event];

    if (nextState) {
      setCurrentState(nextState);
      config.states[nextState].effects?.();
    }
  };

  return { currentState, transition };
}

// 使用示例
type FormState = 'idle' | 'submitting' | 'success' | 'error';
type FormEvent = 'SUBMIT' | 'SUCCESS' | 'ERROR' | 'RESET';

function useFormState() {
  const { currentState, transition } = useStateMachine({
    initial: 'idle' as FormState,
    states: {
      idle: {
        on: {
          SUBMIT: 'submitting'
        }
      },
      submitting: {
        on: {
          SUCCESS: 'success',
          ERROR: 'error'
        }
      },
      success: {
        effects: () => {
          setTimeout(() => transition('RESET'), 3000);
        },
        on: {
          RESET: 'idle'
        }
      },
      error: {
        on: {
          RESET: 'idle'
        }
      }
    }
  });

  return { currentState, transition };
}
```

## 🎨 渲染优化模式

### 1. 虚拟列表实现

```typescript
interface VirtualListProps {
  items: any[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: any, index: number) => React.ReactNode;
}

function VirtualList({
  items,
  itemHeight,
  containerHeight,
  renderItem
}: VirtualListProps) {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length - 1
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  return (
    <div
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        {visibleItems.map((item, index) => (
          <div
            key={item.id}
            style={{
              position: 'absolute',
              top: (startIndex + index) * itemHeight,
              height: itemHeight,
              width: '100%'
            }}
          >
            {renderItem(item, startIndex + index)}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 2. 渐进式加载

```typescript
function ProgressiveImage({
  src,
  placeholder,
  alt
}: {
  src: string;
  placeholder: string;
  alt: string;
}) {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const img = new Image();
    img.src = src;
    img.onload = () => {
      setImageSrc(src);
      setLoading(false);
    };
  }, [src]);

  return (
    <div className="progressive-image-container">
      <img
        src={imageSrc}
        alt={alt}
        className={`progressive-image ${loading ? 'loading' : 'loaded'}`}
      />
    </div>
  );
}
```

### 3. 懒加载组件

```typescript
interface LazyComponentProps {
  component: React.LazyExoticComponent<React.ComponentType<any>>;
  fallback?: React.ReactNode;
  [key: string]: any;
}

function LazyComponent({
  component: Component,
  fallback = <div>Loading...</div>,
  ...props
}: LazyComponentProps) {
  return (
    <Suspense fallback={fallback}>
      <Component {...props} />
    </Suspense>
  );
}

// 使用方式
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <div>
      <h1>My App</h1>
      <LazyComponent component={HeavyComponent} />
    </div>
  );
}
```

## 🔄 异步模式

### 1. 并发数据获取

```typescript
function useParallelQueries<T extends any[]>(
  queries: { (): Promise<any> }[]
) {
  const [data, setData] = useState<{ [K in keyof T]?: T[K] }>({});
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<Error[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setErrors([]);

      try {
        const results = await Promise.allSettled(
          queries.map(query => query())
        );

        const newData: { [K in keyof T]?: T[K] } = {};
        const newErrors: Error[] = [];

        results.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            newData[index as keyof T] = result.value;
          } else {
            newErrors.push(result.reason);
          }
        });

        setData(newData);
        setErrors(newErrors);
      } catch (error) {
        setErrors([error as Error]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [queries]);

  return { data, loading, errors };
}

// 使用示例
function Dashboard() {
  const { data, loading, errors } = useParallelQueries([
    () => fetch('/api/users'),
    () => fetch('/api/posts'),
    () => fetch('/api/stats')
  ]);

  if (loading) return <div>Loading dashboard...</div>;
  if (errors.length > 0) return <div>Errors occurred</div>;

  return (
    <div>
      <UserList users={data[0]} />
      <PostList posts={data[1]} />
      <StatsPanel stats={data[2]} />
    </div>
  );
}
```

### 2. 取消机制

```typescript
function useCancellableFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const abortController = new AbortController();

    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(url, {
          signal: abortController.signal
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError(err as Error);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    return () => {
      abortController.abort();
    };
  }, [url]);

  return { data, loading, error };
}
```

## 🎯 测试模式

### 1. 自定义测试Hook

```typescript
import { renderHook, act } from '@testing-library/react';

// 测试自定义Hook
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);

  const increment = () => setCount(c => c + 1);
  const decrement = () => setCount(c => c - 1);
  const reset = () => setCount(initialValue);

  return { count, increment, decrement, reset };
}

// 测试用例
test('useCounter should increment and decrement', () => {
  const { result } = renderHook(() => useCounter());

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });
  expect(result.current.count).toBe(1);

  act(() => {
    result.current.decrement();
  });
  expect(result.current.count).toBe(0);

  act(() => {
    result.current.reset();
  });
  expect(result.current.count).toBe(0);
});
```

### 2. 测试异步组件

```typescript
// 异步组件测试
function AsyncComponent({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(userData => {
      setUser(userData);
      setLoading(false);
    });
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return <div>{user.name}</div>;
}

// 测试用例
test('AsyncComponent should display user data', async () => {
  const mockUser = { id: '1', name: 'John Doe' };
  jest.spyOn(api, 'fetchUser').mockResolvedValue(mockUser);

  const { findByText } = render(<AsyncComponent userId="1" />);

  expect(await findByText('Loading...')).toBeInTheDocument();
  expect(await findByText('John Doe')).toBeInTheDocument();
});
```

## 🚀 总结

React 19 的高级模式为构建复杂应用提供了强大的工具和模式。通过合理使用这些模式，开发者可以创建出更加健壮、可维护和高性能的应用程序。

### 关键要点：

1. **组件设计**：复合组件、Render Props、双模式组件等提供灵活的API设计
2. **状态管理**：自定义状态管理、Context优化、状态机等模式
3. **性能优化**：虚拟列表、渐进式加载、懒加载等技术
4. **异步处理**：并发数据获取、取消机制等模式
5. **测试策略**：Hook测试、异步组件测试等方法

这些模式不仅适用于React 19，也体现了现代前端开发的最佳实践。对于从PHP转向React的开发者来说，理解这些模式将帮助你更好地构建现代化的Web应用。