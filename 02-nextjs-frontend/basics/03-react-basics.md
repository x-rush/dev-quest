# React 19 基础 - 现代组件化开发

## 概述

React 19 是当前最流行的前端框架之一，它引入了许多新特性，如 Server Components、Actions、并发特性等。作为 PHP 开发者，你需要从传统的模板渲染思维转向组件化开发思维。本指南将帮助你掌握 React 19 的核心概念和最佳实践。

## 从 PHP 到 React 的思维转变

### 开发模式对比

| PHP 开发 | React 开发 |
|---------|-----------|
| 服务端渲染模板 | 客户端组件渲染 |
| 请求-响应循环 | 组件状态管理 |
| 页面刷新跳转 | 单页应用路由 |
| 服务器端状态 | 客户端状态管理 |
| 混合 HTML/PHP 代码 | JSX 语法 |
| 表单提交处理 | 组件事件处理 |

### 核心概念对比

```php
<?php
// PHP 模板示例
foreach ($users as $user) {
    echo "<div class='user-card'>";
    echo "<h3>" . htmlspecialchars($user['name']) . "</h3>";
    echo "<p>" . htmlspecialchars($user['email']) . "</p>";
    echo "</div>";
}
?>
```

```jsx
// React 组件示例
function UserList({ users }) {
  return (
    <div className="user-list">
      {users.map(user => (
        <div key={user.id} className="user-card">
          <h3>{user.name}</h3>
          <p>{user.email}</p>
        </div>
      ))}
    </div>
  );
}
```

## React 19 新特性

### 1. Server Components
```jsx
// Server Component (服务端组件)
async function UserProfile({ userId }) {
  const user = await db.user.findUnique({
    where: { id: userId }
  });

  return (
    <div className="profile">
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}

// Client Component (客户端组件)
"use client";

function InteractiveProfile({ userId }) {
  const [isFollowing, setIsFollowing] = useState(false);

  return (
    <div>
      <UserProfile userId={userId} />
      <button onClick={() => setIsFollowing(!isFollowing)}>
        {isFollowing ? '取消关注' : '关注'}
      </button>
    </div>
  );
}
```

### 2. React Actions
```jsx
"use client";

function TodoList() {
  const [todos, setTodos] = useState([]);
  const [isPending, startTransition] = useTransition();

  async function addTodo(formData) {
    const title = formData.get("title");

    // 使用 React Actions
    const newTodo = await createTodo(title);

    startTransition(() => {
      setTodos(prev => [...prev, newTodo]);
    });
  }

  return (
    <div>
      <form action={addTodo}>
        <input name="title" />
        <button type="submit" disabled={isPending}>
          {isPending ? "添加中..." : "添加 Todo"}
        </button>
      </form>

      <ul>
        {todos.map(todo => (
          <li key={todo.id}>{todo.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

### 3. 并发特性
```jsx
import { useDeferredValue, useMemo } from 'react';

function SearchResults({ query }) {
  // 延迟搜索输入，避免频繁渲染
  const deferredQuery = useDeferredValue(query);

  const filteredResults = useMemo(() => {
    return searchResults.filter(item =>
      item.title.toLowerCase().includes(deferredQuery.toLowerCase())
    );
  }, [deferredQuery]);

  return (
    <div>
      {filteredResults.map(item => (
        <div key={item.id}>{item.title}</div>
      ))}
    </div>
  );
}
```

## 核心概念

### 1. JSX 语法

```jsx
// 基本 JSX 语法
const element = <h1>Hello, React!</h1>;

// 使用表达式
const name = "张三";
const greeting = <h1>Hello, {name}!</h1>;

// 属性设置
const element = <div className="container" id="main">内容</div>;

// 条件渲染
function Greeting({ isLoggedIn }) {
  return isLoggedIn ? <h1>欢迎回来!</h1> : <h1>请登录</h1>;
}

// 列表渲染
function NumberList({ numbers }) {
  return (
    <ul>
      {numbers.map(number => (
        <li key={number.toString()}>
          {number}
        </li>
      ))}
    </ul>
  );
}
```

### 2. 组件基础

```jsx
// 函数组件
function Welcome(props) {
  return <h1>Hello, {props.name}!</h1>;
}

// 箭头函数组件
const Welcome = ({ name }) => <h1>Hello, {name}!</h1>;

// 使用组件
function App() {
  return <Welcome name="张三" />;
}

// 组件解构 props
function UserProfile({ name, email, age }) {
  return (
    <div className="profile">
      <h2>{name}</h2>
      <p>邮箱: {email}</p>
      <p>年龄: {age}</p>
    </div>
  );
}
```

### 3. 状态管理

```jsx
import { useState } from 'react';

// 计数器组件
function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        增加
      </button>
      <button onClick={() => setCount(count - 1)}>
        减少
      </button>
    </div>
  );
}

// 复杂状态管理
function Form() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    age: 0
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <form>
      <input
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="姓名"
      />
      <input
        name="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="邮箱"
      />
      <input
        name="age"
        type="number"
        value={formData.age}
        onChange={handleChange}
        placeholder="年龄"
      />
    </form>
  );
}
```

### 4. 事件处理

```jsx
// 基本事件处理
function Button() {
  const handleClick = (e) => {
    e.preventDefault();
    console.log('按钮被点击');
  };

  return (
    <button onClick={handleClick}>
      点击我
    </button>
  );
}

// 传递参数
function TodoItem({ todo, onDelete }) {
  return (
    <li>
      {todo.text}
      <button onClick={() => onDelete(todo.id)}>
        删除
      </button>
    </li>
  );
}

// 表单处理
function SearchForm() {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('搜索:', query);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="搜索..."
      />
      <button type="submit">搜索</button>
    </form>
  );
}
```

## Hooks 深入

### 1. useState

```jsx
// 状态更新函数
function Counter() {
  const [count, setCount] = useState(0);

  // 使用函数更新确保获取最新状态
  const increment = () => {
    setCount(prevCount => prevCount + 1);
  };

  const decrement = () => {
    setCount(prevCount => prevCount - 1);
  };

  return (
    <div>
      <p>计数: {count}</p>
      <button onClick={increment}>+1</button>
      <button onClick={decrement}>-1</button>
    </div>
  );
}

// 对象状态
function UserProfile() {
  const [user, setUser] = useState({
    name: '',
    email: '',
    age: 0
  });

  const updateName = (newName) => {
    setUser(prev => ({
      ...prev,
      name: newName
    }));
  };

  const updateEmail = (newEmail) => {
    setUser(prev => ({
      ...prev,
      email: newEmail
    }));
  };

  return (
    <div>
      <input
        value={user.name}
        onChange={(e) => updateName(e.target.value)}
        placeholder="姓名"
      />
      <input
        value={user.email}
        onChange={(e) => updateEmail(e.target.value)}
        placeholder="邮箱"
      />
    </div>
  );
}
```

### 2. useEffect

```jsx
import { useState, useEffect } from 'react';

// 数据获取
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        setUser(userData);
      } catch (error) {
        console.error('获取用户数据失败:', error);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchUser();
    }
  }, [userId]); // 依赖数组

  if (loading) return <div>加载中...</div>;
  if (!user) return <div>用户不存在</div>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}

// 清理副作用
function Timer() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCount(c => c + 1);
    }, 1000);

    // 清理函数
    return () => {
      clearInterval(timer);
    };
  }, []); // 空依赖数组，只在组件挂载和卸载时执行

  return <div>计时器: {count}s</div>;
}
```

### 3. useContext

```jsx
import { createContext, useContext, useState } from 'react';

// 创建主题上下文
const ThemeContext = createContext();

// 主题提供者组件
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// 使用主题
function ThemedButton() {
  const { theme, toggleTheme } = useContext(ThemeContext);

  return (
    <button
      onClick={toggleTheme}
      style={{
        backgroundColor: theme === 'light' ? '#fff' : '#333',
        color: theme === 'light' ? '#333' : '#fff'
      }}
    >
      切换主题 ({theme})
    </button>
  );
}

// 应用组件
function App() {
  return (
    <ThemeProvider>
      <div>
        <ThemedButton />
        <ThemedButton />
      </div>
    </ThemeProvider>
  );
}
```

### 4. useReducer

```jsx
import { useReducer } from 'react';

// 定义 action 类型
const ACTIONS = {
  ADD_TODO: 'ADD_TODO',
  TOGGLE_TODO: 'TOGGLE_TODO',
  DELETE_TODO: 'DELETE_TODO'
};

// 定义 reducer
function todoReducer(state, action) {
  switch (action.type) {
    case ACTIONS.ADD_TODO:
      return [
        ...state,
        {
          id: Date.now(),
          text: action.payload.text,
          completed: false
        }
      ];

    case ACTIONS.TOGGLE_TODO:
      return state.map(todo =>
        todo.id === action.payload.id
          ? { ...todo, completed: !todo.completed }
          : todo
      );

    case ACTIONS.DELETE_TODO:
      return state.filter(todo => todo.id !== action.payload.id);

    default:
      return state;
  }
}

// 使用 useReducer
function TodoApp() {
  const [todos, dispatch] = useReducer(todoReducer, []);
  const [inputValue, setInputValue] = useState('');

  const addTodo = (text) => {
    dispatch({ type: ACTIONS.ADD_TODO, payload: { text } });
  };

  const toggleTodo = (id) => {
    dispatch({ type: ACTIONS.TOGGLE_TODO, payload: { id } });
  };

  const deleteTodo = (id) => {
    dispatch({ type: ACTIONS.DELETE_TODO, payload: { id } });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      addTodo(inputValue);
      setInputValue('');
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="添加 Todo"
        />
        <button type="submit">添加</button>
      </form>

      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(todo.id)}
            />
            <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>
              {todo.text}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>
              删除
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 组件模式

### 1. 容器组件与展示组件

```jsx
// 展示组件 (只负责渲染)
const UserList = ({ users, onUserClick }) => (
  <ul>
    {users.map(user => (
      <li key={user.id} onClick={() => onUserClick(user.id)}>
        {user.name}
      </li>
    ))}
  </ul>
);

// 容器组件 (负责数据和逻辑)
function UserListContainer() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);

  useEffect(() => {
    // 获取用户数据
    fetchUsers().then(data => setUsers(data));
  }, []);

  const handleUserClick = (userId) => {
    setSelectedUser(userId);
  };

  return (
    <div>
      <UserList users={users} onUserClick={handleUserClick} />
      {selectedUser && <UserDetail userId={selectedUser} />}
    </div>
  );
}
```

### 2. 高阶组件 (HOC)

```jsx
// 高阶组件：为组件添加加载状态
function withLoading(WrappedComponent) {
  return function WithLoadingComponent({ isLoading, ...props }) {
    if (isLoading) {
      return <div>加载中...</div>;
    }
    return <WrappedComponent {...props} />;
  };
}

// 使用高阶组件
const UserProfileWithLoading = withLoading(UserProfile);

function App() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchUser().then(data => {
      setUser(data);
      setIsLoading(false);
    });
  }, []);

  return (
    <UserProfileWithLoading
      user={user}
      isLoading={isLoading}
    />
  );
}
```

### 3. 自定义 Hooks

```jsx
// 自定义 Hook：数据获取
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(url);
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (url) {
      fetchData();
    }
  }, [url]);

  return { data, loading, error };
}

// 使用自定义 Hook
function UserProfile({ userId }) {
  const { data: user, loading, error } = useFetch(`/api/users/${userId}`);

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  if (!user) return <div>用户不存在</div>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}

// 自定义 Hook：本地存储
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('读取本地存储失败:', error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('写入本地存储失败:', error);
    }
  };

  return [storedValue, setValue];
}

// 使用本地存储 Hook
function ThemeSwitcher() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <button onClick={toggleTheme}>
      当前主题: {theme}
    </button>
  );
}
```

## 性能优化

### 1. React.memo

```jsx
import React, { memo } from 'react';

// 使用 memo 优化组件渲染
const TodoItem = memo(({ todo, onToggle, onDelete }) => {
  console.log('渲染 TodoItem:', todo.id);

  return (
    <li>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
      />
      <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>
        {todo.text}
      </span>
      <button onClick={() => onDelete(todo.id)}>
        删除
      </button>
    </li>
  );
});

function TodoList() {
  const [todos, setTodos] = useState([
    { id: 1, text: '学习 React', completed: false },
    { id: 2, text: '学习 TypeScript', completed: false }
  ]);

  const toggleTodo = (id) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const deleteTodo = (id) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  };

  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={toggleTodo}
          onDelete={deleteTodo}
        />
      ))}
    </ul>
  );
}
```

### 2. useMemo

```jsx
import { useMemo } from 'react';

function ExpensiveComponent({ data, filter }) {
  // 使用 useMemo 缓存计算结果
  const filteredData = useMemo(() => {
    console.log('执行过滤操作...');
    return data.filter(item => item.category === filter);
  }, [data, filter]);

  // 使用 useMemo 缓存复杂计算
  const processedData = useMemo(() => {
    return filteredData.map(item => ({
      ...item,
      processedValue: complexCalculation(item.value)
    }));
  }, [filteredData]);

  return (
    <div>
      {processedData.map(item => (
        <div key={item.id}>
          {item.name}: {item.processedValue}
        </div>
      ))}
    </div>
  );
}
```

### 3. useCallback

```jsx
import { useState, useCallback } from 'react';

function ParentComponent() {
  const [count, setCount] = useState(0);

  // 使用 useCallback 缓存函数
  const handleClick = useCallback(() => {
    console.log('按钮被点击');
  }, []); // 空依赖数组，函数不会重新创建

  const handleIncrement = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);

  return (
    <div>
      <p>计数: {count}</p>
      <ChildComponent onClick={handleClick} />
      <button onClick={handleIncrement}>增加</button>
    </div>
  );
}

// 子组件使用 memo 优化
const ChildComponent = memo(({ onClick }) => {
  console.log('ChildComponent 渲染');
  return <button onClick={onClick}>点击我</button>;
});
```

## TypeScript 集成

### 1. 类型化组件

```tsx
import { useState, ReactNode } from 'react';

// 定义 Props 类型
interface ButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: () => void;
}

// 类型化函数组件
const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  onClick
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

// 使用组件
function App() {
  return (
    <div>
      <Button variant="primary" size="large">
        主要按钮
      </Button>
      <Button variant="secondary" onClick={() => console.log('点击')}>
        次要按钮
      </Button>
    </div>
  );
}
```

### 2. 类型化 Hooks

```tsx
import { useState, useEffect } from 'react';

// 类型化 useState
interface User {
  id: string;
  name: string;
  email: string;
}

function UserProfile() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchUser = async (): Promise<void> => {
      try {
        const response = await fetch<User>('/api/user');
        const userData = await response.json();
        setUser(userData);
      } catch (error) {
        console.error('获取用户失败:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  if (loading) return <div>加载中...</div>;
  if (!user) return <div>用户不存在</div>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

### 3. 泛型组件

```tsx
import { useState } from 'react';

// 泛型组件 Props
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

// 泛型组件
function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map(item => (
        <li key={keyExtractor(item)}>
          {renderItem(item)}
        </li>
      ))}
    </ul>
  );
}

// 使用泛型组件
interface User {
  id: string;
  name: string;
  email: string;
}

function UserList() {
  const users: User[] = [
    { id: '1', name: '张三', email: 'zhangsan@example.com' },
    { id: '2', name: '李四', email: 'lisi@example.com' }
  ];

  return (
    <List<User>
      items={users}
      renderItem={(user) => (
        <div>
          <h3>{user.name}</h3>
          <p>{user.email}</p>
        </div>
      )}
      keyExtractor={(user) => user.id}
    />
  );
}
```

## 实战示例

### 1. 完整的 Todo 应用

```tsx
import { useState, useEffect, useCallback } from 'react';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: Date;
}

function TodoApp() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  // 从本地存储加载 todos
  useEffect(() => {
    const savedTodos = localStorage.getItem('todos');
    if (savedTodos) {
      try {
        const parsedTodos = JSON.parse(savedTodos);
        setTodos(parsedTodos.map((todo: any) => ({
          ...todo,
          createdAt: new Date(todo.createdAt)
        })));
      } catch (error) {
        console.error('解析本地存储失败:', error);
      }
    }
  }, []);

  // 保存 todos 到本地存储
  useEffect(() => {
    localStorage.setItem('todos', JSON.stringify(todos));
  }, [todos]);

  // 添加 todo
  const addTodo = useCallback((text: string) => {
    if (text.trim()) {
      const newTodo: Todo = {
        id: Date.now().toString(),
        text: text.trim(),
        completed: false,
        createdAt: new Date()
      };
      setTodos(prev => [newTodo, ...prev]);
    }
  }, []);

  // 切换 todo 状态
  const toggleTodo = useCallback((id: string) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  }, []);

  // 删除 todo
  const deleteTodo = useCallback((id: string) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  }, []);

  // 过滤 todos
  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed;
    if (filter === 'completed') return todo.completed;
    return true;
  });

  // 统计信息
  const activeCount = todos.filter(todo => !todo.completed).length;
  const completedCount = todos.filter(todo => todo.completed).length;

  return (
    <div className="todo-app">
      <h1>Todo 应用</h1>

      <div className="todo-input">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="添加新的 todo..."
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              addTodo(inputValue);
              setInputValue('');
            }
          }}
        />
        <button onClick={() => {
          addTodo(inputValue);
          setInputValue('');
        }}>
          添加
        </button>
      </div>

      <div className="todo-filters">
        <button
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          全部 ({todos.length})
        </button>
        <button
          className={filter === 'active' ? 'active' : ''}
          onClick={() => setFilter('active')}
        >
          进行中 ({activeCount})
        </button>
        <button
          className={filter === 'completed' ? 'active' : ''}
          onClick={() => setFilter('completed')}
        >
          已完成 ({completedCount})
        </button>
      </div>

      <ul className="todo-list">
        {filteredTodos.map(todo => (
          <li key={todo.id} className={todo.completed ? 'completed' : ''}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(todo.id)}
            />
            <span>{todo.text}</span>
            <span className="todo-date">
              {todo.createdAt.toLocaleDateString()}
            </span>
            <button onClick={() => deleteTodo(todo.id)}>
              删除
            </button>
          </li>
        ))}
      </ul>

      {todos.length > 0 && (
        <div className="todo-stats">
          <p>
            总计: {todos.length} |
            进行中: {activeCount} |
            已完成: {completedCount}
          </p>
        </div>
      )}
    </div>
  );
}

export default TodoApp;
```

### 2. 用户管理系统

```tsx
import { useState, useEffect, useCallback } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  isActive: boolean;
  lastLogin: Date | null;
}

function UserManager() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // 模拟 API 获取用户数据
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        // 模拟 API 调用
        await new Promise(resolve => setTimeout(resolve, 1000));

        const mockUsers: User[] = [
          {
            id: '1',
            name: '张三',
            email: 'zhangsan@example.com',
            role: 'admin',
            isActive: true,
            lastLogin: new Date('2024-01-15')
          },
          {
            id: '2',
            name: '李四',
            email: 'lisi@example.com',
            role: 'user',
            isActive: true,
            lastLogin: new Date('2024-01-14')
          },
          {
            id: '3',
            name: '王五',
            email: 'wangwu@example.com',
            role: 'guest',
            isActive: false,
            lastLogin: null
          }
        ];

        setUsers(mockUsers);
      } catch (error) {
        console.error('获取用户失败:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  // 更新用户状态
  const toggleUserStatus = useCallback((userId: string) => {
    setUsers(prev => prev.map(user =>
      user.id === userId
        ? { ...user, isActive: !user.isActive }
        : user
    ));
  }, []);

  // 选择用户
  const selectUser = useCallback((user: User) => {
    setSelectedUser(user);
    setIsEditing(false);
  }, []);

  // 保存用户编辑
  const saveUser = useCallback((updatedUser: User) => {
    setUsers(prev => prev.map(user =>
      user.id === updatedUser.id ? updatedUser : user
    ));
    setSelectedUser(updatedUser);
    setIsEditing(false);
  }, []);

  if (loading) return <div className="loading">加载用户数据中...</div>;

  return (
    <div className="user-manager">
      <div className="user-list">
        <h2>用户列表</h2>
        <table>
          <thead>
            <tr>
              <th>姓名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>状态</th>
              <th>最后登录</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr
                key={user.id}
                className={selectedUser?.id === user.id ? 'selected' : ''}
              >
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>
                  <span className={`status ${user.isActive ? 'active' : 'inactive'}`}>
                    {user.isActive ? '活跃' : '禁用'}
                  </span>
                </td>
                <td>
                  {user.lastLogin
                    ? user.lastLogin.toLocaleDateString()
                    : '从未登录'
                  }
                </td>
                <td>
                  <button onClick={() => selectUser(user)}>
                    详情
                  </button>
                  <button onClick={() => toggleUserStatus(user.id)}>
                    {user.isActive ? '禁用' : '启用'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedUser && (
        <div className="user-detail">
          <h2>用户详情</h2>
          {isEditing ? (
            <UserForm
              user={selectedUser}
              onSave={saveUser}
              onCancel={() => setIsEditing(false)}
            />
          ) : (
            <UserDetails
              user={selectedUser}
              onEdit={() => setIsEditing(true)}
            />
          )}
        </div>
      )}
    </div>
  );
}

// 用户详情组件
interface UserDetailsProps {
  user: User;
  onEdit: () => void;
}

function UserDetails({ user, onEdit }: UserDetailsProps) {
  return (
    <div className="user-details">
      <div className="detail-row">
        <label>ID:</label>
        <span>{user.id}</span>
      </div>
      <div className="detail-row">
        <label>姓名:</label>
        <span>{user.name}</span>
      </div>
      <div className="detail-row">
        <label>邮箱:</label>
        <span>{user.email}</span>
      </div>
      <div className="detail-row">
        <label>角色:</label>
        <span>{user.role}</span>
      </div>
      <div className="detail-row">
        <label>状态:</label>
        <span className={user.isActive ? 'active' : 'inactive'}>
          {user.isActive ? '活跃' : '禁用'}
        </span>
      </div>
      <div className="detail-row">
        <label>最后登录:</label>
        <span>
          {user.lastLogin
            ? user.lastLogin.toLocaleString()
            : '从未登录'
          }
        </span>
      </div>
      <button onClick={onEdit}>编辑</button>
    </div>
  );
}

// 用户表单组件
interface UserFormProps {
  user: User;
  onSave: (user: User) => void;
  onCancel: () => void;
}

function UserForm({ user, onSave, onCancel }: UserFormProps) {
  const [formData, setFormData] = useState<User>(user);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'isActive' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="user-form">
      <div className="form-row">
        <label>姓名:</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      <div className="form-row">
        <label>邮箱:</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      <div className="form-row">
        <label>角色:</label>
        <select
          name="role"
          value={formData.role}
          onChange={handleChange}
        >
          <option value="admin">管理员</option>
          <option value="user">用户</option>
          <option value="guest">访客</option>
        </select>
      </div>
      <div className="form-row">
        <label>
          <input
            type="checkbox"
            name="isActive"
            checked={formData.isActive}
            onChange={handleChange}
          />
          活跃状态
        </label>
      </div>
      <div className="form-actions">
        <button type="submit">保存</button>
        <button type="button" onClick={onCancel}>取消</button>
      </div>
    </form>
  );
}

export default UserManager;
```

## 下一步

掌握 React 19 基础后，你可以继续学习：

1. **Next.js 路由系统** - 理解 App Router 和页面路由
2. **状态管理进阶** - 学习 Zustand、Jotai 等现代状态管理库
3. **样式解决方案** - 掌握 Tailwind CSS 和样式组件
4. **测试策略** - 学习 Vitest 和 Testing Library

---

*React 19 引入了许多新特性，掌握这些基础概念将为你开发现代化 Web 应用奠定坚实基础。*