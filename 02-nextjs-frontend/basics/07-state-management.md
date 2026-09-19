# Next.js 16 状态管理基础完整指南

## 先理解，再动手

## 本轮先交付一个状态归属练习

前置：已有能启动的 Next.js App Router + TypeScript 项目，知道客户端组件与事件处理器。本文包含多个独立片段，Context、Zustand、查询库与表单部分不是一套可直接拼接的应用；先只接入下文 Counter，暂不安装其他状态库。

产物：一个 `/state-lab` 页面、Counter 组件和一张操作记录。页面作为客户端组件，渲染 `<Counter initialValue={1} min={0} max={2} onChange={setLast} />`，在父组件用 `useState<number | null>(null)` 保存 `last` 并显示它。这能观察“子组件拥有 count、父组件收到通知”的边界。若父组件也必须控制 count，则改为 `value/onChange` 受控接口，只保留一个拥有者，参见 [共享状态](https://react.dev/learn/sharing-state-between-components)。

| 输入操作 | 预期界面输出 | 失败时回查 |
|---|---|---|
| 初次进入 | count 为 1，last 为 null | 是否在挂载或渲染期间错误调用回调 |
| 点击加号一次 | count 与 last 都为 2，加号禁用 | 是否把 onChange 留在 updater 中 |
| 连点减号直到下限 | 停在 0，减号禁用 | 边界是否同时作用于按钮与计算 |
| 点击重置 | 两处显示 1 | reset 是否使用同一个初始值 |
| 浏览器刷新 | count 回到 1，last 回到 null | 本地内存状态本就不保证持久化 |

这些是待执行的验收预期。本轮未启动 Next.js、未执行浏览器交互或生产构建，不能据此宣称框架项目通过。执行时记录 Node/Next/React 版本、锁文件与浏览器结果；项目使用 npm 时先运行既有的 `npm run dev`，再运行 `npm run build`，分别记录开发交互与构建结果。

下一步：把“已提交搜索词”迁入 URL，再用刷新和浏览器后退检查恢复；保留输入草稿在组件内。先写出草稿、URL 和远端结果各由谁拥有，再决定是否引入 Context 或查询库。

状态按拥有者分层：输入框文本在本地，分享筛选在 URL，服务器记录以远端为准。复制一份远端数据到全局 store 会增加同步责任。

**本节自测**：给搜索页列出输入草稿、已提交关键词、查询结果的归属。

<details>
<summary>预期结果与参考思路（先尝试再展开）</summary>

草稿可用组件状态；可分享的关键词进入 URL；结果由查询层保存并根据关键词区分。

</details>

> **文档简介**: Next.js 16 现代状态管理完整教程，涵盖React状态、Context API、Zustand、服务器状态、表单状态等企业级状态管理解决方案

> **目标读者**: 具备React基础的开发者，需要掌握现代状态管理模式的前端工程师

> **前置知识**: React组件基础、JavaScript ES6+、TypeScript基础、异步编程概念

> **预计时长**: 4-5小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `basics` |
| **难度** | ⭐⭐ |
| **标签** | `#state-management` `#zustand` `#context-api` `#react-query` `#form-state` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### 🗄️ 状态管理核心概念
- 理解不同类型的状态：本地状态、全局状态、服务器状态、表单状态
- 掌握React 19的状态管理最佳实践
- 学会选择合适的状态管理解决方案
- 理解状态持久化和同步机制

### 🚀 实际应用能力
- 构建可扩展的状态架构
- 实现状态的性能优化和调试
- 掌握复杂业务逻辑的状态处理
- 学会状态测试和验证

## 📖 概述

Next.js 16应用中的状态管理需要考虑服务器端和客户端的不同特点。本教程将帮助你掌握现代React状态管理的核心概念，学会选择和实现适合不同场景的状态管理解决方案。

## 🏗️ 状态管理架构概览

### 状态分类体系

```typescript
// src/types/state-architecture.ts
export interface StateArchitecture {
  // 本地状态
  localState: {
    componentState: '组件内部状态'
    formState: '表单状态'
    uiState: 'UI交互状态'
  }

  // 全局状态
  globalState: {
    userState: '用户认证状态'
    appConfig: '应用配置状态'
    themeState: '主题和偏好设置'
  }

  // 服务器状态
  serverState: {
    apiData: 'API获取的数据'
    cacheData: '缓存的数据'
    realtimeData: '实时数据'
  }

  // URL状态
  urlState: {
    queryParams: '查询参数状态'
    routeParams: '路由参数状态'
    hashState: 'Hash状态'
  }
}
```

## 🔧 本地状态管理

### 组件状态基础

```tsx
// src/components/Counter.tsx
'use client'

import { useState, useCallback } from 'react'

interface CounterProps {
  initialValue?: number
  max?: number
  min?: number
  onChange?: (value: number) => void
}

export function Counter({
  initialValue = 0,
  max = 100,
  min = 0,
  onChange
}: CounterProps) {
  const [count, setCount] = useState(initialValue)

  const increment = useCallback(() => {
    const next = Math.min(count + 1, max)
    setCount(next)
    onChange?.(next)
  }, [count, max, onChange])

  const decrement = useCallback(() => {
    const next = Math.max(count - 1, min)
    setCount(next)
    onChange?.(next)
  }, [count, min, onChange])

  const reset = useCallback(() => {
    setCount(initialValue)
    onChange?.(initialValue)
  }, [initialValue, onChange])

  return (
    <div className="flex items-center space-x-4">
      <button
        onClick={decrement}
        disabled={count <= min}
        className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        -
      </button>

      <span className="text-xl font-semibold w-12 text-center">
        {count}
      </span>

      <button
        onClick={increment}
        disabled={count >= max}
        className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        +
      </button>

      <button
        onClick={reset}
        className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        重置
      </button>
    </div>
  )
}
```

### 复杂组件状态

上面的按钮每次用户事件只执行一次状态转换，回调放在事件处理器里。不要把通知父组件、写存储或发请求放进 updater：updater 必须纯净，开发环境 Strict Mode 可能重复调用它。若同一事件要连续累加三次，应使用三个纯 updater，或者一次计算最终值；不要把本例的 `increment()` 连调三次当作 `+3`。`initialValue` 只初始化首次挂载，后续 props 改变不会自动重置 count。参见 [React useState](https://react.dev/reference/react/useState)。

```tsx
// src/components/TodoList.tsx
'use client'

import { useState, useCallback, useMemo } from 'react'
import { v4 as uuidv4 } from 'uuid'

interface Todo {
  id: string
  text: string
  completed: boolean
  createdAt: Date
  completedAt?: Date
}

interface TodoListProps {
  initialTodos?: Todo[]
}

export function TodoList({ initialTodos = [] }: TodoListProps) {
  const [todos, setTodos] = useState<Todo[]>(initialTodos)
  const [newTodoText, setNewTodoText] = useState('')
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all')

  // 添加新任务
  const addTodo = useCallback(() => {
    if (!newTodoText.trim()) return

    const newTodo: Todo = {
      id: uuidv4(),
      text: newTodoText.trim(),
      completed: false,
      createdAt: new Date()
    }

    setTodos(prev => [...prev, newTodo])
    setNewTodoText('')
  }, [newTodoText])

  // 切换任务状态
  const toggleTodo = useCallback((id: string) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id
        ? {
            ...todo,
            completed: !todo.completed,
            completedAt: !todo.completed ? new Date() : undefined
          }
        : todo
    ))
  }, [])

  // 删除任务
  const deleteTodo = useCallback((id: string) => {
    setTodos(prev => prev.filter(todo => todo.id !== id))
  }, [])

  // 编辑任务
  const editTodo = useCallback((id: string, newText: string) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id ? { ...todo, text: newText } : todo
    ))
  }, [])

  // 过滤后的任务
  const filteredTodos = useMemo(() => {
    switch (filter) {
      case 'active':
        return todos.filter(todo => !todo.completed)
      case 'completed':
        return todos.filter(todo => todo.completed)
      default:
        return todos
    }
  }, [todos, filter])

  // 统计信息
  const stats = useMemo(() => ({
    total: todos.length,
    active: todos.filter(todo => !todo.completed).length,
    completed: todos.filter(todo => todo.completed).length
  }), [todos])

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">待办事项</h1>

      {/* 添加新任务 */}
      <div className="flex space-x-2 mb-6">
        <input
          type="text"
          value={newTodoText}
          onChange={(e) => setNewTodoText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
          placeholder="添加新任务..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          onClick={addTodo}
          disabled={!newTodoText.trim()}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          添加
        </button>
      </div>

      {/* 过滤器 */}
      <div className="flex space-x-2 mb-6">
        {(['all', 'active', 'completed'] as const).map(filterType => (
          <button
            key={filterType}
            onClick={() => setFilter(filterType)}
            className={`px-4 py-2 rounded-lg ${
              filter === filterType
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {filterType === 'all' && `全部 (${stats.total})`}
            {filterType === 'active' && `进行中 (${stats.active})`}
            {filterType === 'completed' && `已完成 (${stats.completed})`}
          </button>
        ))}
      </div>

      {/* 任务列表 */}
      <div className="space-y-2">
        {filteredTodos.map(todo => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={toggleTodo}
            onDelete={deleteTodo}
            onEdit={editTodo}
          />
        ))}
      </div>

      {filteredTodos.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          {filter === 'all' && '暂无任务'}
          {filter === 'active' && '暂无进行中的任务'}
          {filter === 'completed' && '暂无已完成的任务'}
        </div>
      )}
    </div>
  )
}

// 任务项组件
interface TodoItemProps {
  todo: Todo
  onToggle: (id: string) => void
  onDelete: (id: string) => void
  onEdit: (id: string, text: string) => void
}

function TodoItem({ todo, onToggle, onDelete, onEdit }: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editText, setEditText] = useState(todo.text)

  const saveEdit = () => {
    if (editText.trim() && editText !== todo.text) {
      onEdit(todo.id, editText.trim())
    }
    setIsEditing(false)
  }

  const cancelEdit = () => {
    setEditText(todo.text)
    setIsEditing(false)
  }

  return (
    <div className="flex items-center space-x-3 p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50">
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
        className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
      />

      <div className="flex-1">
        {isEditing ? (
          <input
            type="text"
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') saveEdit()
              if (e.key === 'Escape') cancelEdit()
            }}
            onBlur={saveEdit}
            className="w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            autoFocus
          />
        ) : (
          <span
            className={`
              cursor-text
              ${todo.completed ? 'line-through text-gray-500' : 'text-gray-900'}
            `}
            onClick={() => setIsEditing(true)}
          >
            {todo.text}
          </span>
        )}
      </div>

      <div className="text-sm text-gray-500">
        {todo.completed && todo.completedAt && (
          <span>完成于 {todo.completedAt.toLocaleDateString()}</span>
        )}
      </div>

      <button
        onClick={() => onDelete(todo.id)}
        className="px-2 py-1 text-red-600 hover:bg-red-50 rounded"
      >
        删除
      </button>
    </div>
  )
}
```

## 🌐 全局状态管理

### Context API基础

```tsx
// src/contexts/AuthContext.tsx
'use client'

import React, { createContext, useContext, useReducer, useEffect } from 'react'

// 用户类型
interface User {
  id: string
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'user'
}

// 认证状态
interface AuthState {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

// 认证动作
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: User }
  | { type: 'AUTH_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }

// 初始状态
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null
}

// Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        loading: true,
        error: null
      }
    case 'AUTH_SUCCESS':
      return {
        ...state,
        loading: false,
        user: action.payload,
        isAuthenticated: true,
        error: null
      }
    case 'AUTH_ERROR':
      return {
        ...state,
        loading: false,
        user: null,
        isAuthenticated: false,
        error: action.payload
      }
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        loading: false,
        error: null
      }
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null
      }
    default:
      return state
  }
}

// Context
const AuthContext = createContext<{
  state: AuthState
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  clearError: () => void
} | null>(null)

// Provider组件
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // 登录函数
  const login = async (email: string, password: string) => {
    dispatch({ type: 'AUTH_START' })

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '登录失败')
      }

      dispatch({ type: 'AUTH_SUCCESS', payload: data.user })
    } catch (error) {
      dispatch({
        type: 'AUTH_ERROR',
        payload: error instanceof Error ? error.message : '未知错误'
      })
    }
  }

  // 登出函数
  const logout = () => {
    dispatch({ type: 'LOGOUT' })
  }

  // 清除错误
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  // 检查本地存储的认证状态
  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        const user = JSON.parse(savedUser)
        dispatch({ type: 'AUTH_SUCCESS', payload: user })
      } catch {
        localStorage.removeItem('user')
      }
    }
  }, [])

  // 保存用户信息到本地存储
  useEffect(() => {
    if (state.user) {
      localStorage.setItem('user', JSON.stringify(state.user))
    } else {
      localStorage.removeItem('user')
    }
  }, [state.user])

  return (
    <AuthContext.Provider value={{ state, login, logout, clearError }}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
```

### Zustand状态管理

```tsx
// src/stores/useUserStore.ts
import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// 用户类型
interface User {
  id: string
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'user'
  preferences: {
    theme: 'light' | 'dark' | 'system'
    language: string
    notifications: boolean
  }
}

// 用户状态接口
interface UserState {
  // 状态
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null

  // 动作
  setUser: (user: User) => void
  updateUser: (updates: Partial<User>) => void
  updatePreferences: (preferences: Partial<User['preferences']>) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
  logout: () => void

  // 异步动作
  login: (email: string, password: string) => Promise<void>
  fetchUser: () => Promise<void>
  updateProfile: (updates: Partial<User>) => Promise<void>
}

// 创建store
export const useUserStore = create<UserState>()(
  devtools(
    subscribeWithSelector(
      persist(
        immer((set, get) => ({
          // 初始状态
          user: null,
          isAuthenticated: false,
          loading: false,
          error: null,

          // 设置用户
          setUser: (user) => {
            set((state) => {
              state.user = user
              state.isAuthenticated = true
              state.error = null
            })
          },

          // 更新用户信息
          updateUser: (updates) => {
            set((state) => {
              if (state.user) {
                Object.assign(state.user, updates)
              }
            })
          },

          // 更新用户偏好
          updatePreferences: (preferences) => {
            set((state) => {
              if (state.user) {
                Object.assign(state.user.preferences, preferences)
              }
            })
          },

          // 设置加载状态
          setLoading: (loading) => {
            set((state) => {
              state.loading = loading
            })
          },

          // 设置错误
          setError: (error) => {
            set((state) => {
              state.error = error
              state.loading = false
            })
          },

          // 清除错误
          clearError: () => {
            set((state) => {
              state.error = null
            })
          },

          // 登出
          logout: () => {
            set((state) => {
              state.user = null
              state.isAuthenticated = false
              state.error = null
              state.loading = false
            })
          },

          // 登录
          login: async (email, password) => {
            const { setLoading, setError, setUser } = get()

            setLoading(true)
            setError(null)

            try {
              const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
              })

              const data = await response.json()

              if (!response.ok) {
                throw new Error(data.error || '登录失败')
              }

              setUser(data.user)
            } catch (error) {
              setError(error instanceof Error ? error.message : '登录失败')
            } finally {
              setLoading(false)
            }
          },

          // 获取用户信息
          fetchUser: async () => {
            const { setLoading, setError, setUser } = get()

            setLoading(true)

            try {
              const response = await fetch('/api/user/profile')

              if (!response.ok) {
                throw new Error('获取用户信息失败')
              }

              const data = await response.json()
              setUser(data.user)
            } catch (error) {
              setError(error instanceof Error ? error.message : '获取用户信息失败')
            } finally {
              setLoading(false)
            }
          },

          // 更新个人资料
          updateProfile: async (updates) => {
            const { setLoading, setError, updateUser } = get()

            setLoading(true)

            try {
              const response = await fetch('/api/user/profile', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
              })

              const data = await response.json()

              if (!response.ok) {
                throw new Error(data.error || '更新失败')
              }

              updateUser(data.user)
            } catch (error) {
              setError(error instanceof Error ? error.message : '更新失败')
            } finally {
              setLoading(false)
            }
          }
        })),
        {
          name: 'user-store',
          partialize: (state) => ({
            user: state.user,
            isAuthenticated: state.isAuthenticated
          })
        }
      )
    ),
    {
      name: 'user-store'
    }
  )
)

// 选择器hooks
export const useUser = () => useUserStore((state) => state.user)
export const useIsAuthenticated = () => useUserStore((state) => state.isAuthenticated)
export const useUserLoading = () => useUserStore((state) => state.loading)
export const useUserError = () => useUserStore((state) => state.error)
export const useUserPreferences = () => useUserStore((state) => state.user?.preferences)
```

## 📊 服务器状态管理

### React Query集成

```tsx
// src/hooks/useApiQuery.ts
'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useUserStore } from '@/stores/useUserStore'

// API查询配置
const defaultQueryConfig = {
  staleTime: 5 * 60 * 1000, // 5分钟
  cacheTime: 10 * 60 * 1000, // 10分钟
  retry: 3,
  retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000)
}

// 通用查询Hook
export function useApiQuery<T>(
  queryKey: string[],
  queryFn: () => Promise<T>,
  config = {}
) {
  const user = useUserStore(state => state.user)

  return useQuery({
    queryKey,
    queryFn,
    ...defaultQueryConfig,
    ...config,
    enabled: !!user // 只有用户登录后才执行查询
  })
}

// 文章查询Hook
export function usePosts(params: { page?: number; category?: string } = {}) {
  return useApiQuery(
    ['posts', params],
    () => fetchPosts(params),
    {
      staleTime: 2 * 60 * 1000 // 2分钟
    }
  )
}

async function fetchPosts(params: { page?: number; category?: string }) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set('page', params.page.toString())
  if (params.category) searchParams.set('category', params.category)

  const response = await fetch(`/api/posts?${searchParams}`)
  if (!response.ok) throw new Error('Failed to fetch posts')
  return response.json()
}

// 单篇文章查询Hook
export function usePost(id: string) {
  return useApiQuery(
    ['post', id],
    () => fetchPost(id),
    {
      staleTime: 10 * 60 * 1000 // 10分钟
    }
  )
}

async function fetchPost(id: string) {
  const response = await fetch(`/api/posts/${id}`)
  if (!response.ok) throw new Error('Failed to fetch post')
  return response.json()
}

// 创建文章Mutation Hook
export function useCreatePost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (postData: {
      title: string
      content: string
      category?: string
    }) => {
      const response = await fetch('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postData)
      })

      if (!response.ok) throw new Error('Failed to create post')
      return response.json()
    },
    onSuccess: (newPost) => {
      // 使文章列表缓存失效
      queryClient.invalidateQueries({ queryKey: ['posts'] })

      // 将新文章添加到缓存
      queryClient.setQueryData(['post', newPost.id], newPost)
    },
    onError: (error) => {
      console.error('Error creating post:', error)
    }
  })
}

// 更新文章Mutation Hook
export function useUpdatePost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, ...updates }: {
      id: string
      title?: string
      content?: string
      category?: string
    }) => {
      const response = await fetch(`/api/posts/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })

      if (!response.ok) throw new Error('Failed to update post')
      return response.json()
    },
    onSuccess: (updatedPost) => {
      // 更新缓存中的文章
      queryClient.setQueryData(['post', updatedPost.id], updatedPost)

      // 使文章列表缓存失效
      queryClient.invalidateQueries({ queryKey: ['posts'] })
    },
    onError: (error) => {
      console.error('Error updating post:', error)
    }
  })
}
```

## 📝 表单状态管理

### React Hook Form集成

```tsx
// src/hooks/useFormState.ts
'use client'

import { useForm, UseFormReturn } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useState } from 'react'

// 通用表单状态Hook
export function useFormState<T extends z.ZodSchema>(
  schema: T,
  defaultValues?: Partial<z.infer<T>>
) {
  const form = useForm<z.infer<T>>({
    resolver: zodResolver(schema),
    defaultValues,
    mode: 'onChange'
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const handleSubmit = async (onSubmit: (data: z.infer<T>) => Promise<void>) => {
    const isValid = await form.trigger()

    if (!isValid) {
      return
    }

    setIsSubmitting(true)
    setSubmitError(null)

    try {
      const data = form.getValues()
      await onSubmit(data)
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : '提交失败')
    } finally {
      setIsSubmitting(false)
    }
  }

  return {
    form,
    isSubmitting,
    submitError,
    handleSubmit,
    clearError: () => setSubmitError(null)
  }
}

// 登录表单Hook
const loginSchema = z.object({
  email: z.string().email('请输入有效的邮箱地址'),
  password: z.string().min(6, '密码至少需要6个字符'),
  remember: z.boolean().default(false)
})

export function useLoginForm() {
  const { form, isSubmitting, submitError, handleSubmit } = useFormState(
    loginSchema,
    {
      email: '',
      password: '',
      remember: false
    }
  )

  return {
    form,
    isSubmitting,
    submitError,
    handleSubmit
  }
}

// 文章编辑表单Hook
const postSchema = z.object({
  title: z.string().min(1, '标题不能为空').max(200, '标题不能超过200个字符'),
  content: z.string().min(10, '内容至少需要10个字符'),
  excerpt: z.string().max(500, '摘要不能超过500个字符').optional(),
  category: z.string().min(1, '请选择分类'),
  tags: z.array(z.string()).default([]),
  published: z.boolean().default(false)
})

export function usePostForm(initialData?: Partial<z.infer<typeof postSchema>>) {
  const { form, isSubmitting, submitError, handleSubmit } = useFormState(
    postSchema,
    initialData
  )

  return {
    form,
    isSubmitting,
    submitError,
    handleSubmit
  }
}
```

## 🔀 状态持久化

### 本地存储同步

```tsx
// src/hooks/useLocalStorage.ts
'use client'

import { useState, useEffect } from 'react'

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  // 获取初始值
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue
    }

    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error)
      return initialValue
    }
  })

  // 设置值的函数
  const setValue = (value: T | ((prev: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)

      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore))
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error)
    }
  }

  // 监听其他标签页的变化
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        setStoredValue(JSON.parse(e.newValue))
      }
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('storage', handleStorageChange)
      return () => window.removeEventListener('storage', handleStorageChange)
    }
  }, [key])

  return [storedValue, setValue]
}

// 使用示例
export function useTheme() {
  const [theme, setTheme] = useLocalStorage<'light' | 'dark'>(
    'theme',
    'light'
  )

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  return { theme, toggleTheme, setTheme }
}

export function useCart() {
  const [items, setItems] = useLocalStorage<CartItem[]>(
    'cart',
    []
  )

  const addItem = (item: CartItem) => {
    setItems(prev => {
      const existingItem = prev.find(i => i.id === item.id)
      if (existingItem) {
        return prev.map(i =>
          i.id === item.id
            ? { ...i, quantity: i.quantity + item.quantity }
            : i
        )
      }
      return [...prev, item]
    })
  }

  const removeItem = (id: string) => {
    setItems(prev => prev.filter(item => item.id !== id))
  }

  const updateQuantity = (id: string, quantity: number) => {
    if (quantity <= 0) {
      removeItem(id)
    } else {
      setItems(prev =>
        prev.map(item =>
          item.id === id ? { ...item, quantity } : item
        )
      )
    }
  }

  const clearCart = () => {
    setItems([])
  }

  const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0)

  return {
    items,
    total,
    addItem,
    removeItem,
    updateQuantity,
    clearCart
  }
}

interface CartItem {
  id: string
  name: string
  price: number
  quantity: number
  image?: string
}
```

## ✅ 总结

通过本教程，你已经掌握了：

1. **本地状态**: 组件级状态管理和复杂状态处理
2. **全局状态**: Context API和Zustand的现代状态管理
3. **服务器状态**: React Query的数据获取和缓存管理
4. **表单状态**: React Hook Form和Zod的表单验证
5. **状态持久化**: 本地存储和状态同步机制
6. **性能优化**: 状态管理的最佳实践和优化策略

## 📚 下一步学习

- 深入学习高级状态管理模式(Redux Toolkit, Jotai)
- 掌握状态管理和调试工具
- 学习状态测试和验证策略
- 探索微前端状态管理
- 了解状态安全性和权限控制

现代React应用的状态管理需要根据具体场景选择合适的解决方案。继续探索更多高级特性，构建更强大的应用吧！

## 🔄 文档交叉引用

### 相关文档
- 📄 **[前一个basics文档](./06-data-fetching-basics.md)**: 学习数据获取基础，理解服务器状态管理
- 📄 **[后一个basics文档](./08-first-project.md)**: 学习完整项目实战，综合应用状态管理知识
- 📄 **[相关的reference文档](../reference/framework-patterns/05-state-management-patterns.md)**: 深入了解状态管理模式和最佳实践
- 📄 **[相关的reference文档](../reference/language-concepts/01-react-syntax-cheatsheet.md)**: 快速参考React Hook和状态管理语法

### 参考章节
- 📖 **[本模块其他章节]**: [数据获取基础](./06-data-fetching-basics.md#-client-components-数据获取) | [完整项目实战](./08-first-project.md#主题提供者)
- 📖 **[Knowledge Points快速参考]**: [状态管理模式](../reference/framework-patterns/05-state-management-patterns.md) | [React语法速查](../reference/language-concepts/01-react-syntax-cheatsheet.md)

## 📝 总结

### 状态选择回顾

先按数据的所有者和失效方式分类，再选工具；不要因为一个库流行就把所有值放进全局 store。

1. **组件本地状态**：只被一个组件树消费的展开、输入和临时 UI 状态，使用 `useState`；多个状态转移需要统一描述时使用 `useReducer`，并让 reducer 对相同输入返回可预测结果。
2. **跨组件客户端状态**：主题、当前草稿或未提交的界面偏好可用 Context 或轻量 store。Context 的 value 每次变化会通知消费者，频繁变化的大对象应拆分或选择带 selector 的 store。
3. **服务器状态**：来自 API、会过期且可被其他请求改变的数据，保留请求状态、缓存键、失效条件和重新获取逻辑。不要把一次请求结果复制到全局 store 后就失去刷新与错误语义。
4. **表单状态**：字段值、校验错误和提交状态属于同一次交互。模式校验在提交前给出可读错误，服务端仍必须重新校验；类型推导不能替代运行时输入检查。
5. **持久化状态**：只持久化可以安全恢复且版本兼容的数据。读取 `localStorage` 只能在客户端发生；为旧数据准备迁移或丢弃策略，绝不保存会话密钥或敏感身份信息。

### 学习成果验收

- [ ] 为一个筛选面板标出每个值是本地、跨组件、服务器、表单还是持久化状态，并说明它何时失效。
- [ ] 用 reducer 实现至少两个状态转移；对非法 action 保持状态不变或显式报错，并用测试或控制台输出验证。
- [ ] 为一条查询设置稳定缓存键，完成一次编辑后失效并重新获取，确认界面没有继续显示旧列表。
- [ ] 提交包含错误字段的表单，确认错误贴近字段、请求没有发出；再模拟服务端拒绝并显示可恢复的提交状态。
- [ ] 刷新页面验证允许持久化的偏好能恢复；删除或损坏存储项后，应用回到安全默认值且不崩溃。

## 🤝 贡献与反馈

### 内容改进
如果你发现本文档有改进空间，欢迎：
- 🐛 **报告问题**: 在Issues中提出具体问题
- 💡 **建议改进**: 提出修改建议和补充内容
- 📝 **参与贡献**: 提交PR完善文档内容

### 学习反馈
分享你的学习体验：
- ✅ **有用内容**: 哪些部分对你最有帮助
- ❓ **疑问点**: 哪些内容需要进一步澄清
- 🎯 **建议**: 希望增加什么内容

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
