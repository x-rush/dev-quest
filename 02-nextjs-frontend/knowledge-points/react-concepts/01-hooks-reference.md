# React Hooks 参考手册

## 📚 概述

React Hooks 是 React 16.8 引入的革命性特性，让函数组件能够使用状态和其他 React 特性。本手册涵盖 React 19 的所有 Hooks，包括最新的 Hooks 特性和最佳实践。

## 🔥 核心基础 Hooks

### useState
**用途**: 在函数组件中添加状态管理

```typescript
// 基础用法
const [count, setCount] = useState(0);

// 带初始化函数
const [state, setState] = useState(() => {
  const initialState = someExpensiveComputation(props);
  return initialState;
});

// 函数式更新
const increment = () => {
  setCount(prevCount => prevCount + 1);
};

// 对象状态更新
const [user, setUser] = useState({ name: '', age: 0 });
const updateUserName = (name: string) => {
  setUser(prev => ({ ...prev, name }));
};
```

### useEffect
**用途**: 处理副作用操作（数据获取、订阅、DOM操作）

```typescript
// 基础用法 - 模拟 componentDidMount
useEffect(() => {
  document.title = `You clicked ${count} times`;
}, []);

// 依赖数组 - 模拟 componentDidUpdate
useEffect(() => {
  document.title = `You clicked ${count} times`;
}, [count]);

// 清理函数 - 模拟 componentWillUnmount
useEffect(() => {
  const timer = setInterval(() => {
    setCount(prev => prev + 1);
  }, 1000);

  return () => clearInterval(timer);
}, []);

// 异步操作
useEffect(() => {
  const fetchData = async () => {
    try {
      const response = await fetch('/api/data');
      const data = await response.json();
      setData(data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  fetchData();
}, [dependency]);
```

### useContext
**用途**: 订阅 React Context 的变化

```typescript
// 创建 Context
const ThemeContext = createContext<'light' | 'dark'>('light');

// 在组件中使用
const theme = useContext(ThemeContext);

// 结合 useState 提供者
function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  return (
    <ThemeContext.Provider value={theme}>
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        Toggle Theme
      </button>
      {children}
    </ThemeContext.Provider>
  );
}
```

## 🎯 额外 Hooks

### useReducer
**用途**: 复杂状态管理的替代方案

```typescript
// 定义状态和操作类型
type State = {
  count: number;
  loading: boolean;
  error: string | null;
};

type Action =
  | { type: 'INCREMENT' }
  | { type: 'DECREMENT' }
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: number }
  | { type: 'FETCH_ERROR'; payload: string };

// Reducer 函数
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'INCREMENT':
      return { ...state, count: state.count + 1 };
    case 'DECREMENT':
      return { ...state, count: state.count - 1 };
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, count: action.payload };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };
    default:
      return state;
  }
}

// 在组件中使用
const [state, dispatch] = useReducer(reducer, {
  count: 0,
  loading: false,
  error: null,
});
```

### useCallback
**用途**: 缓存函数引用，优化性能

```typescript
// 基础用法
const memoizedCallback = useCallback(() => {
  doSomething(a, b);
}, [a, b]);

// 事件处理器
const handleClick = useCallback((id: number) => {
  setSelectedId(id);
  onItemSelect?.(id);
}, [onItemSelect]);

// 与依赖数组配合
const fetchData = useCallback(async () => {
  setLoading(true);
  try {
    const response = await fetch(`/api/items/${id}`);
    const data = await response.json();
    setData(data);
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
}, [id]);
```

### useMemo
**用途**: 缓存计算结果，优化性能

```typescript
// 基础用法
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);

// 复杂计算缓存
const filteredItems = useMemo(() => {
  return items.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
}, [items, searchTerm]);

// 对象和数组缓存
const memoizedStyle = useMemo(() => ({
  color: theme === 'dark' ? 'white' : 'black',
  backgroundColor: theme === 'dark' ? 'black' : 'white',
  padding: '1rem',
}), [theme]);
```

### useRef
**用途**: 创建可变的引用对象

```typescript
// DOM 元素引用
const inputRef = useRef<HTMLInputElement>(null);

const focusInput = () => {
  inputRef.current?.focus();
};

// 保存可变值
const timerRef = useRef<NodeJS.Timeout | null>(null);

const startTimer = () => {
  timerRef.current = setInterval(() => {
    setCount(prev => prev + 1);
  }, 1000);
};

const stopTimer = () => {
  if (timerRef.current) {
    clearInterval(timerRef.current);
    timerRef.current = null;
  }
};

// 清理
useEffect(() => {
  return () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  };
}, []);
```

### useImperativeHandle
**用途**: 自定义暴露给父组件的实例值

```typescript
// 子组件
const FancyInput = forwardRef<HTMLInputElement, { value: string }>(
  (props, ref) => {
    const inputRef = useRef<HTMLInputElement>(null);

    useImperativeHandle(ref, () => ({
      focus: () => inputRef.current?.focus(),
      getValue: () => inputRef.current?.value || '',
      clear: () => {
        if (inputRef.current) {
          inputRef.current.value = '';
        }
      }
    }));

    return <input ref={inputRef} {...props} />;
  }
);

// 父组件使用
const fancyInputRef = useRef<{ focus: () => void; getValue: () => string }>(null);

const handleFocus = () => {
  fancyInputRef.current?.focus();
};
```

## 🚀 React 19 新 Hooks

### useOptimistic
**用途**: 乐观更新 UI，提升用户体验

```typescript
function Messages({ messages, sendMessage }) {
  const [optimisticMessages, addOptimisticMessage] = useOptimistic(
    messages,
    (state, newMessage) => [...state, { message: newMessage, sending: true }]
  );

  const formAction = async (formData) => {
    const message = formData.get('message');
    addOptimisticMessage(message);
    await sendMessage(message);
  };

  return (
    <div>
      {optimisticMessages.map((msg, index) => (
        <div key={index}>
          {msg.message}
          {msg.sending && <small> (Sending...)</small>}
        </div>
      ))}
      <form action={formAction}>
        <input type="text" name="message" placeholder="Hello!" />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

### useFormStatus
**用途**: 获取表单提交状态

```typescript
function SubmitButton({ children }) {
  const { pending } = useFormStatus();

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : children}
    </button>
  );
}

function ContactForm() {
  return (
    <form action={submitForm}>
      <input type="text" name="name" required />
      <input type="email" name="email" required />
      <SubmitButton>Send Message</SubmitButton>
    </form>
  );
}
```

### useActionState
**用途**: 管理表单操作的状态

```typescript
async function createPost(previousState, formData) {
  const title = formData.get('title');
  const content = formData.get('content');

  try {
    const response = await fetch('/api/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });

    if (!response.ok) {
      throw new Error('Failed to create post');
    }

    return { success: true, error: null };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

function PostForm() {
  const [state, formAction] = useActionState(createPost, {
    success: false,
    error: null,
  });

  return (
    <form action={formAction}>
      <input type="text" name="title" required />
      <textarea name="content" required />
      <button type="submit">Create Post</button>
      {state.error && <p className="error">{state.error}</p>}
      {state.success && <p className="success">Post created successfully!</p>}
    </form>
  );
}
```

## 🎨 自定义 Hooks

### useLocalStorage
```typescript
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      if (typeof window !== 'undefined') {
        const item = window.localStorage.getItem(key);
        return item ? JSON.parse(item) : initialValue;
      }
      return initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue] as const;
}

// 使用
const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('theme', 'light');
```

### useDebounce
```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// 使用
const [searchTerm, setSearchTerm] = useState('');
const debouncedSearchTerm = useDebounce(searchTerm, 500);

useEffect(() => {
  if (debouncedSearchTerm) {
    // 执行搜索
    searchItems(debouncedSearchTerm);
  }
}, [debouncedSearchTerm]);
```

### useAsync
```typescript
function useAsync<T, E = string>(
  asyncFunction: () => Promise<T>,
  immediate = true
) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<E | null>(null);
  const [loading, setLoading] = useState(false);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await asyncFunction();
      setData(result);
    } catch (err) {
      setError(err as E);
    } finally {
      setLoading(false);
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { data, error, loading, execute };
}

// 使用
const { data, error, loading, execute } = useAsync(() =>
  fetch('/api/users').then(res => res.json())
);
```

## ⚠️ Hooks 规则和最佳实践

### 基本规则
1. **只在顶层调用 Hooks**: 不要在循环、条件或嵌套函数中调用
2. **只在 React 函数中调用 Hooks**: 在 React 函数组件或自定义 Hooks 中调用

### 性能优化
```typescript
// ✅ 正确: 使用 useCallback 和 useMemo
const handleEvent = useCallback(() => {
  // 处理事件
}, [dependency]);

const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);

// ❌ 避免: 过度优化
const handleClick = useCallback(() => {
  console.log('clicked');
}, []); // 简单函数不需要优化
```

### 错误处理
```typescript
// ✅ 正确: 处理错误
useEffect(() => {
  const fetchData = async () => {
    try {
      const response = await fetch('/api/data');
      const data = await response.json();
      setData(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  fetchData();
}, [url]);

// ❌ 避免: 忽略错误
useEffect(() => {
  fetch('/api/data')
    .then(res => res.json())
    .then(setData); // 错误未处理
}, [url]);
```

### 清理副作用
```typescript
// ✅ 正确: 清理副作用
useEffect(() => {
  const subscription = subscribeToUpdates();
  return () => subscription.unsubscribe();
}, []);

useEffect(() => {
  const timer = setInterval(() => {
    // 定时任务
  }, 1000);

  return () => clearInterval(timer);
}, []);
```

## 📖 总结

React Hooks 提供了强大的工具来构建现代化的 React 应用。掌握这些 Hooks 的使用方法和最佳实践，将帮助你构建更加高效、可维护的 React 应用程序。

React 19 引入的新 Hooks 进一步增强了开发体验，特别是在表单处理和乐观更新方面。结合自定义 Hooks，你可以构建出更加模块化和可复用的代码。

记住遵循 Hooks 的规则，合理使用性能优化技巧，并正确处理错误和清理副作用，这将确保你的 React 应用保持高性能和稳定性。