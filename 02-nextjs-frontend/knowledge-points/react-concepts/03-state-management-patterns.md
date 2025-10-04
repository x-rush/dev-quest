# React 状态管理模式

## 📚 概述

状态管理是 React 应用开发的核心概念。本指南涵盖了从基础的组件状态到复杂的状态管理解决方案，包括 React 19 的新特性和现代状态管理最佳实践。

## 🏗️ 基础状态管理

### useState Hook
**组件本地状态管理**

```typescript
// 基础状态
function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}

// 对象状态
interface User {
  name: string;
  email: string;
  age: number;
}

function UserProfile() {
  const [user, setUser] = useState<User>({
    name: '',
    email: '',
    age: 0,
  });

  const updateUser = (updates: Partial<User>) => {
    setUser(prev => ({ ...prev, ...updates }));
  };

  return (
    <div>
      <input
        value={user.name}
        onChange={(e) => updateUser({ name: e.target.value })}
        placeholder="Name"
      />
      <input
        value={user.email}
        onChange={(e) => updateUser({ email: e.target.value })}
        placeholder="Email"
      />
      <input
        type="number"
        value={user.age}
        onChange={(e) => updateUser({ age: parseInt(e.target.value) || 0 })}
        placeholder="Age"
      />
    </div>
  );
}

// 函数式更新
function OptimizedCounter() {
  const [count, setCount] = useState(0);

  // 使用函数式更新确保基于最新状态
  const increment = () => {
    setCount(prev => prev + 1);
  };

  const incrementBy = (amount: number) => {
    setCount(prev => prev + amount);
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+1</button>
      <button onClick={() => incrementBy(5)}>+5</button>
    </div>
  );
}
```

### useReducer Hook
**复杂状态逻辑管理**

```typescript
// 定义状态类型
interface State {
  todos: Todo[];
  filter: 'all' | 'active' | 'completed';
  nextId: number;
}

interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

// 定义动作类型
type Action =
  | { type: 'ADD_TODO'; text: string }
  | { type: 'TOGGLE_TODO'; id: number }
  | { type: 'DELETE_TODO'; id: number }
  | { type: 'SET_FILTER'; filter: State['filter'] }
  | { type: 'CLEAR_COMPLETED' };

// Reducer 函数
function todoReducer(state: State, action: Action): State {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        ...state,
        todos: [
          ...state.todos,
          {
            id: state.nextId,
            text: action.text,
            completed: false,
          },
        ],
        nextId: state.nextId + 1,
      };

    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.id
            ? { ...todo, completed: !todo.completed }
            : todo
        ),
      };

    case 'DELETE_TODO':
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.id),
      };

    case 'SET_FILTER':
      return {
        ...state,
        filter: action.filter,
      };

    case 'CLEAR_COMPLETED':
      return {
        ...state,
        todos: state.todos.filter(todo => !todo.completed),
      };

    default:
      return state;
  }
}

// 在组件中使用
function TodoApp() {
  const [state, dispatch] = useReducer(todoReducer, {
    todos: [],
    filter: 'all',
    nextId: 1,
  });

  const addTodo = (text: string) => {
    dispatch({ type: 'ADD_TODO', text });
  };

  const toggleTodo = (id: number) => {
    dispatch({ type: 'TOGGLE_TODO', id });
  };

  const deleteTodo = (id: number) => {
    dispatch({ type: 'DELETE_TODO', id });
  };

  const setFilter = (filter: State['filter']) => {
    dispatch({ type: 'SET_FILTER', filter });
  };

  const clearCompleted = () => {
    dispatch({ type: 'CLEAR_COMPLETED' });
  };

  const filteredTodos = state.todos.filter(todo => {
    switch (state.filter) {
      case 'active':
        return !todo.completed;
      case 'completed':
        return todo.completed;
      default:
        return true;
    }
  });

  return (
    <div>
      <TodoInput onAdd={addTodo} />
      <TodoFilter currentFilter={state.filter} onFilterChange={setFilter} />
      <TodoList
        todos={filteredTodos}
        onToggle={toggleTodo}
        onDelete={deleteTodo}
      />
      <button onClick={clearCompleted}>Clear Completed</button>
    </div>
  );
}
```

## 🌐 全局状态管理

### Context API
**跨组件共享状态**

```typescript
// 创建 Context
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Context Provider
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  const value = {
    theme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// 自定义 Hook
export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// 使用 Context
function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className={`header header-${theme}`}>
      <h1>My App</h1>
      <button onClick={toggleTheme}>
        Toggle Theme ({theme})
      </button>
    </header>
  );
}

// 多个 Context
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const userData = await response.json();
      setUser(userData);
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    isLoading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
```

### 状态优化策略
**避免不必要的重新渲染**

```typescript
// 使用 memo 优化子组件
const TodoItem = memo(function TodoItem({
  todo,
  onToggle,
  onDelete
}: {
  todo: Todo;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}) {
  return (
    <li>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
      />
      <span className={todo.completed ? 'completed' : ''}>
        {todo.text}
      </span>
      <button onClick={() => onDelete(todo.id)}>Delete</button>
    </li>
  );
});

// 使用 useMemo 优化计算
function TodoStats({ todos }: { todos: Todo[] }) {
  const stats = useMemo(() => {
    const total = todos.length;
    const completed = todos.filter(todo => todo.completed).length;
    const active = total - completed;
    const completionRate = total > 0 ? (completed / total) * 100 : 0;

    return {
      total,
      completed,
      active,
      completionRate,
    };
  }, [todos]);

  return (
    <div>
      <p>Total: {stats.total}</p>
      <p>Completed: {stats.completed}</p>
      <p>Active: {stats.active}</p>
      <p>Completion Rate: {stats.completionRate.toFixed(1)}%</p>
    </div>
  );
}

// 使用 useCallback 优化事件处理器
function TodoList({
  todos,
  onToggle,
  onDelete
}: {
  todos: Todo[];
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}) {
  const handleToggle = useCallback((id: number) => {
    onToggle(id);
  }, [onToggle]);

  const handleDelete = useCallback((id: number) => {
    onDelete(id);
  }, [onDelete]);

  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={handleToggle}
          onDelete={handleDelete}
        />
      ))}
    </ul>
  );
}
```

## 🚀 现代 React 19 状态管理模式

### useOptimistic Hook
**乐观更新状态**

```typescript
interface Message {
  id: string;
  text: string;
  sending?: boolean;
  error?: string;
}

function MessageBoard() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [optimisticMessages, addOptimisticMessage] = useOptimistic(
    messages,
    (state, newMessage: Omit<Message, 'id'>) => [
      ...state,
      { ...newMessage, id: Date.now().toString(), sending: true }
    ]
  );

  const sendMessage = async (text: string) => {
    // 乐观添加消息
    addOptimisticMessage({ text });

    try {
      // 实际发送消息
      const response = await fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const newMessage = await response.json();
      setMessages(prev => [...prev, newMessage]);
    } catch (error) {
      // 处理错误，移除乐观消息
      setMessages(prev => prev.filter(msg => !msg.sending));
      console.error('Send message error:', error);
    }
  };

  return (
    <div>
      <MessageForm onSend={sendMessage} />
      <div>
        {optimisticMessages.map(message => (
          <div key={message.id} className={`message ${message.sending ? 'sending' : ''}`}>
            {message.text}
            {message.sending && <span className="sending-indicator">Sending...</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### useActionState Hook
**管理异步操作状态**

```typescript
interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

function useAsyncAction<T, P = void>(
  action: (params: P) => Promise<T>
) {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (params: P) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const result = await action(params);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      throw error;
    }
  }, [action]);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, execute, reset };
}

// 使用示例
function UserProfile({ userId }: { userId: string }) {
  const { data: user, loading, error, execute } = useAsyncAction(
    async (id: string) => {
      const response = await fetch(`/api/users/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }
      return response.json();
    }
  );

  useEffect(() => {
    execute(userId);
  }, [userId, execute]);

  if (loading) return <div>Loading user profile...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return null;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <button onClick={() => execute(userId)}>Refresh</button>
    </div>
  );
}
```

## 🏢 状态管理库集成

### Zustand
**轻量级状态管理**

```typescript
// store/todos.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

interface TodosStore {
  todos: Todo[];
  filter: 'all' | 'active' | 'completed';
  addTodo: (text: string) => void;
  toggleTodo: (id: string) => void;
  deleteTodo: (id: string) => void;
  setFilter: (filter: 'all' | 'active' | 'completed') => void;
  clearCompleted: () => void;
}

export const useTodosStore = create<TodosStore>()(
  devtools(
    (set, get) => ({
      todos: [],
      filter: 'all',

      addTodo: (text: string) => {
        const newTodo: Todo = {
          id: Date.now().toString(),
          text,
          completed: false,
        };
        set(state => ({ todos: [...state.todos, newTodo] }));
      },

      toggleTodo: (id: string) => {
        set(state => ({
          todos: state.todos.map(todo =>
            todo.id === id
              ? { ...todo, completed: !todo.completed }
              : todo
          ),
        }));
      },

      deleteTodo: (id: string) => {
        set(state => ({
          todos: state.todos.filter(todo => todo.id !== id),
        }));
      },

      setFilter: (filter: 'all' | 'active' | 'completed') => {
        set({ filter });
      },

      clearCompleted: () => {
        set(state => ({
          todos: state.todos.filter(todo => !todo.completed),
        }));
      },
    }),
    { name: 'todos-store' }
  )
);

// 在组件中使用
function TodoList() {
  const { todos, filter, addTodo, toggleTodo, deleteTodo, setFilter } = useTodosStore();

  const filteredTodos = todos.filter(todo => {
    switch (filter) {
      case 'active':
        return !todo.completed;
      case 'completed':
        return todo.completed;
      default:
        return true;
    }
  });

  return (
    <div>
      <TodoInput onAdd={addTodo} />
      <FilterButtons currentFilter={filter} onFilterChange={setFilter} />
      <ul>
        {filteredTodos.map(todo => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={toggleTodo}
            onDelete={deleteTodo}
          />
        ))}
      </ul>
    </div>
  );
}

// 选择器模式
function useFilteredTodos() {
  return useTodosStore(state => {
    const { todos, filter } = state;
    return todos.filter(todo => {
      switch (filter) {
        case 'active':
          return !todo.completed;
        case 'completed':
          return todo.completed;
        default:
          return true;
      }
    });
  });
}
```

### Jotai
**原子化状态管理**

```typescript
// atoms.ts
import { atom } from 'jotai';

// 原子定义
export const countAtom = atom(0);
export const textAtom = atom('Hello Jotai');
export const themeAtom = atom<'light' | 'dark'>('light');

// 派生原子
export const doubledCountAtom = atom(get => get(countAtom) * 2);

export const uppercaseTextAtom = atom(get => get(textAtom).toUpperCase());

// 异步原子
export const userAtom = atom(async (get) => {
  const userId = get(currentUserIdAtom);
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
});

// 可写派生原子
export const userInfoAtom = atom(
  get => get(userAtom),
  (get, set, update) => {
    const currentUser = get(userAtom);
    const updatedUser = { ...currentUser, ...update };

    // 更新后端
    fetch(`/api/users/${currentUser.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedUser),
    });

    // 更新本地状态
    set(userAtom, updatedUser);
  }
);

// 在组件中使用
function Counter() {
  const [count, setCount] = useAtom(countAtom);
  const [doubledCount] = useAtom(doubledCountAtom);

  return (
    <div>
      <p>Count: {count}</p>
      <p>Doubled: {doubledCount}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}

function UserProfile() {
  const [user, setUser] = useAtom(userInfoAtom);

  if (!user) return <div>Loading...</div>;

  return (
    <div>
      <h2>{user.name}</h2>
      <input
        value={user.email}
        onChange={(e) => setUser({ email: e.target.value })}
      />
    </div>
  );
}
```

### TanStack Query
**服务器状态管理**

```typescript
// hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface User {
  id: string;
  name: string;
  email: string;
}

// 查询 Hook
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await fetch('/api/users');
      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }
      return response.json() as Promise<User[]>;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: ['users', id],
    queryFn: async () => {
      const response = await fetch(`/api/users/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }
      return response.json() as Promise<User>;
    },
    enabled: !!id, // 只有当 id 存在时才执行查询
  });
}

// 变更 Hook
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (userData: Omit<User, 'id'>) => {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      if (!response.ok) {
        throw new Error('Failed to create user');
      }
      return response.json() as Promise<User>;
    },
    onSuccess: (newUser) => {
      // 更新缓存
      queryClient.setQueryData(['users'], (old: User[] | undefined) => {
        return old ? [...old, newUser] : [newUser];
      });

      // 使其他相关查询失效
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
    onError: (error) => {
      console.error('Create user error:', error);
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...userData }: Partial<User> & { id: string }) => {
      const response = await fetch(`/api/users/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      if (!response.ok) {
        throw new Error('Failed to update user');
      }
      return response.json() as Promise<User>;
    },
    onMutate: async ({ id, ...userData }) => {
      // 取消任何进行中的查询
      await queryClient.cancelQueries({ queryKey: ['users', id] });

      // 快照之前的值
      const previousUser = queryClient.getQueryData(['users', id]);

      // 乐观更新
      queryClient.setQueryData(['users', id], (old: User | undefined) => {
        return old ? { ...old, ...userData } : old;
      });

      // 返回上下文对象，带有快照值
      return { previousUser };
    },
    onError: (err, variables, context) => {
      // 如果错误，回滚到之前的值
      if (context?.previousUser) {
        queryClient.setQueryData(['users', variables.id], context.previousUser);
      }
    },
    onSettled: (data, error, variables) => {
      // 无论成功或失败，都重新获取数据
      queryClient.invalidateQueries({ queryKey: ['users', variables.id] });
    },
  });
}

// 在组件中使用
function UserList() {
  const { data: users, isLoading, error } = useUsers();
  const createUser = useCreateUser();

  const handleCreateUser = (userData: Omit<User, 'id'>) => {
    createUser.mutate(userData);
  };

  if (isLoading) return <div>Loading users...</div>;
  if (error) return <div>Error loading users</div>;

  return (
    <div>
      <UserForm onSubmit={handleCreateUser} />
      <ul>
        {users?.map(user => (
          <UserItem key={user.id} user={user} />
        ))}
      </ul>
    </div>
  );
}
```

## 🔧 高级状态模式

### 状态机模式
**使用 XState 管理复杂状态**

```typescript
// machine/fetchMachine.ts
import { createMachine, assign } from 'xstate';

interface FetchContext {
  data: any;
  error: string;
}

export const fetchMachine = createMachine({
  id: 'fetch',
  initial: 'idle',
  context: {
    data: null,
    error: '',
  },
  states: {
    idle: {
      on: {
        FETCH: 'loading',
      },
    },
    loading: {
      invoke: {
        src: 'fetchData',
        onDone: {
          target: 'success',
          actions: assign({ data: (context, event) => event.data }),
        },
        onError: {
          target: 'failure',
          actions: assign({ error: (context, event) => event.data }),
        },
      },
    },
    success: {
      on: {
        FETCH: 'loading',
        RESET: 'idle',
      },
    },
    failure: {
      on: {
        RETRY: 'loading',
        RESET: 'idle',
      },
    },
  },
});

// 在 React 组件中使用
function DataComponent() {
  const [state, send] = useMachine(fetchMachine, {
    services: {
      fetchData: async () => {
        const response = await fetch('/api/data');
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        return response.json();
      },
    },
  });

  useEffect(() => {
    send('FETCH');
  }, [send]);

  if (state.matches('loading')) {
    return <div>Loading...</div>;
  }

  if (state.matches('failure')) {
    return (
      <div>
        <p>Error: {state.context.error}</p>
        <button onClick={() => send('RETRY')}>Retry</button>
      </div>
    );
  }

  if (state.matches('success')) {
    return (
      <div>
        <pre>{JSON.stringify(state.context.data, null, 2)}</pre>
        <button onClick={() => send('RESET')}>Reset</button>
      </div>
    );
  }

  return <button onClick={() => send('FETCH')}>Fetch Data</button>;
}
```

### 表单状态管理
**React Hook Form 结合状态管理**

```typescript
// forms/userForm.tsx
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// 定义表单模式
const userSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
  age: z.number().min(18, 'Must be at least 18 years old'),
});

type UserFormData = z.infer<typeof userSchema>;

interface UserFormProps {
  initialData?: UserFormData;
  onSubmit: (data: UserFormData) => Promise<void>;
  onCancel: () => void;
}

function UserForm({ initialData, onSubmit, onCancel }: UserFormProps) {
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting, dirtyFields },
    reset,
    watch,
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: initialData || {
      name: '',
      email: '',
      age: 18,
    },
  });

  const watchedValues = watch();

  const handleFormSubmit = async (data: UserFormData) => {
    try {
      await onSubmit(data);
      reset(data);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  const handleReset = () => {
    reset(initialData);
  };

  const isDirty = Object.keys(dirtyFields).length > 0;

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <div>
        <label>Name</label>
        <Controller
          name="name"
          control={control}
          render={({ field }) => (
            <input {...field} placeholder="Enter your name" />
          )}
        />
        {errors.name && <span className="error">{errors.name.message}</span>}
      </div>

      <div>
        <label>Email</label>
        <Controller
          name="email"
          control={control}
          render={({ field }) => (
            <input {...field} type="email" placeholder="Enter your email" />
          )}
        />
        {errors.email && <span className="error">{errors.email.message}</span>}
      </div>

      <div>
        <label>Age</label>
        <Controller
          name="age"
          control={control}
          render={({ field }) => (
            <input
              {...field}
              type="number"
              onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
            />
          )}
        />
        {errors.age && <span className="error">{errors.age.message}</span>}
      </div>

      <div className="form-actions">
        <button type="button" onClick={handleReset}>
          Reset
        </button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" disabled={isSubmitting || !isDirty}>
          {isSubmitting ? 'Submitting...' : 'Submit'}
        </button>
      </div>

      {/* 调试信息 */}
      <div className="debug-info">
        <h4>Form State:</h4>
        <pre>{JSON.stringify(watchedValues, null, 2)}</pre>
        <h4>Dirty Fields:</h4>
        <pre>{JSON.stringify(dirtyFields, null, 2)}</pre>
      </div>
    </form>
  );
}
```

## 📋 最佳实践

### 状态管理原则
1. **最小化状态**: 只存储必要的状态
2. **单一数据源**: 每个数据有唯一的状态来源
3. **状态提升**: 将共享状态提升到最近的共同祖先
4. **不可变性**: 始终创建新的状态对象而不是修改现有状态

### 性能优化
```typescript
// 使用选择器避免不必要的渲染
const useTodosCount = () => {
  return useTodosStore(state => state.todos.length);
};

const useCompletedTodos = () => {
  return useTodosStore(state => state.todos.filter(todo => todo.completed));
};

// 懒加载状态
const useHeavyComputation = (data: any[]) => {
  return useMemo(() => {
    return expensiveComputation(data);
  }, [data]);
};

// 状态分离
const useUIState = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return {
    isModalOpen,
    sidebarOpen,
    openModal: () => setIsModalOpen(true),
    closeModal: () => setIsModalOpen(false),
    toggleSidebar: () => setSidebarOpen(prev => !prev),
  };
};

const useDataState = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  return {
    data,
    loading,
    error,
    setData,
    setLoading,
    setError,
  };
};
```

### 错误处理
```typescript
// 状态恢复模式
const useErrorRecovery = () => {
  const [state, setState] = useState(initialState);
  const [error, setError] = useState(null);
  const [isRecovering, setIsRecovering] = useState(false);

  const recoverFromError = async () => {
    setIsRecovering(true);
    try {
      await recoverState();
      setState(backupState);
      setError(null);
    } catch (recoveryError) {
      console.error('Recovery failed:', recoveryError);
    } finally {
      setIsRecovering(false);
    }
  };

  return {
    state,
    error,
    isRecovering,
    recoverFromError,
    setState: (newState) => {
      try {
        setState(newState);
        backupState = newState;
        setError(null);
      } catch (err) {
        setError(err);
      }
    },
  };
};
```

## 📖 总结

选择合适的状态管理方案取决于应用的复杂度和需求：

1. **简单状态**: 使用 `useState` 和 `useReducer`
2. **组件间共享**: 使用 Context API
3. **复杂应用**: 使用 Zustand 或 Jotai
4. **服务器状态**: 使用 TanStack Query
5. **复杂状态流**: 使用状态机

React 19 的新特性如 `useOptimistic` 和 `useActionState` 为状态管理提供了更强大的工具，特别是处理异步操作和用户交互时。

记住，最好的状态管理方案是能够平衡性能、可维护性和开发体验的方案。始终从简单的解决方案开始，根据需要逐步演进到更复杂的解决方案。