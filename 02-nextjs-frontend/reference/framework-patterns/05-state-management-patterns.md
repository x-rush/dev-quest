# 企业级状态管理模式详解

> **文档简介**: Next.js 16 + React 19 企业级状态管理完整指南，涵盖Zustand、React Query、全局状态、服务器状态、持久化状态管理等现代状态管理模式

> **目标读者**: 具备React基础的中高级开发者，需要构建复杂状态管理系统的前端架构师

> **前置知识**: Next.js 16基础、React 19状态概念、TypeScript、异步编程、RESTful API

> **预计时长**: 8-12小时

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `framework-patterns` |
| **难度** | ⭐⭐⭐ (精通)|
| **标签** | `#state-management` `#zustand` `#react-query` `#redux` `#performance` `#scalability` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 📚 概述

Next.js 16 与 React 19 结合提供了强大的状态管理生态系统。本指南深入探讨企业级状态管理模式，涵盖从基础的本地状态到复杂的分布式状态管理，结合 Zustand、Vercel KV、Redis 等现代工具，构建高性能、可维护的状态管理架构。

## 🏗️ 状态管理架构概览

### 状态分类体系
**全面的状态分类和管理策略**

```typescript
// 状态分类体系
interface StateArchitecture {
  // 本地状态
  localState: {
    componentState: '单个组件内部状态';
    formState: '表单状态';
    uiState: 'UI 交互状态';
  };

  // 共享状态
  sharedState: {
    globalState: '全局应用状态';
    userState: '用户相关状态';
    sessionState: '会话状态';
  };

  // 服务器状态
  serverState: {
    remoteData: '远程数据';
    cacheData: '缓存数据';
    realtimeData: '实时数据';
  };

  // 持久化状态
  persistedState: {
    localStorage: '本地存储';
    sessionStorage: '会话存储';
    persistentStorage: '持久化存储';
  };
}

// 状态管理策略选择器
export function createStateStrategy(config: {
  scope: 'local' | 'shared' | 'server' | 'persisted';
  persistence?: boolean;
  realtime?: boolean;
  complexity?: 'simple' | 'medium' | 'complex';
}) {
  const strategies = {
    local: {
      simple: () => useState,
      medium: () => useReducer,
      complex: () => useHookState,
    },
    shared: {
      simple: () => createContext + useContext,
      medium: () => useZustand,
      complex: () => useRedux,
    },
    server: {
      simple: () => useSWR,
      medium: () => useReactQuery,
      complex: () => useApolloClient,
    },
    persisted: {
      simple: () => useLocalStorage,
      medium: () => useIndexedDB,
      complex: () => useSQLite,
    },
  };

  return strategies[config.scope][config.complexity || 'simple']();
}
```

## 🎯 本地状态管理模式

### 1. 高级 useState 模式
**智能状态管理 hooks**

```tsx
// hooks/use-advanced-state.ts
import { useState, useCallback, useRef, useEffect } from 'react';

// 智能状态 Hook - 支持历史记录和撤销
export function useAdvancedState<T>(
  initialValue: T,
  options?: {
    maxHistory?: number;
    persist?: boolean;
    key?: string;
    onChange?: (value: T, prevValue: T) => void;
  }
) {
  const [state, setState] = useState<T>(() => {
    if (options?.persist && options.key) {
      const stored = localStorage.getItem(options.key);
      return stored ? JSON.parse(stored) : initialValue;
    }
    return initialValue;
  });

  const history = useRef<T[]>([initialValue]);
  const historyIndex = useRef(0);

  const setValue = useCallback((newValue: T | ((prev: T) => T)) => {
    setState(prevValue => {
      const resolvedValue = typeof newValue === 'function'
        ? (newValue as (prev: T) => T)(prevValue)
        : newValue;

      // 更新历史记录
      if (options?.maxHistory) {
        const newHistory = history.current.slice(0, historyIndex.current + 1);
        newHistory.push(resolvedValue);

        if (newHistory.length > options.maxHistory) {
          newHistory.shift();
        } else {
          historyIndex.current++;
        }

        history.current = newHistory;
      }

      // 持久化存储
      if (options?.persist && options.key) {
        localStorage.setItem(options.key, JSON.stringify(resolvedValue));
      }

      // 触发回调
      options?.onChange?.(resolvedValue, prevValue);

      return resolvedValue;
    });
  }, [options]);

  const undo = useCallback(() => {
    if (historyIndex.current > 0) {
      historyIndex.current--;
      setState(history.current[historyIndex.current]);
    }
  }, []);

  const redo = useCallback(() => {
    if (historyIndex.current < history.current.length - 1) {
      historyIndex.current++;
      setState(history.current[historyIndex.current]);
    }
  }, []);

  const reset = useCallback(() => {
    historyIndex.current = 0;
    setState(initialValue);
  }, [initialValue]);

  return {
    value: state,
    setValue,
    undo,
    redo,
    reset,
    canUndo: historyIndex.current > 0,
    canRedo: historyIndex.current < history.current.length - 1,
    history: history.current,
    currentIndex: historyIndex.current,
  };
}

// 使用示例
export function ExampleComponent() {
  const { value: count, setValue, undo, redo, canUndo, canRedo } =
    useAdvancedState(0, {
      maxHistory: 10,
      persist: true,
      key: 'counter-state',
      onChange: (newValue, prevValue) => {
        console.log(`State changed: ${prevValue} -> ${newValue}`);
      },
    });

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setValue(count + 1)}>Increment</button>
      <button onClick={undo} disabled={!canUndo}>Undo</button>
      <button onClick={redo} disabled={!canRedo}>Redo</button>
    </div>
  );
}
```

### 2. 智能 useReducer 模式
**复杂状态逻辑管理**

```typescript
// hooks/use-smart-reducer.ts
import { useReducer, useCallback, useEffect } from 'react';

// 智能 Reducer 配置
interface SmartReducerConfig<T, A> {
  initialState: T;
  reducer: (state: T, action: A) => T;
  middleware?: Array<(state: T, action: A, next: () => T) => T>;
  persist?: {
    key: string;
    storage?: 'localStorage' | 'sessionStorage';
  };
  logger?: boolean;
}

// 智能状态管理 Hook
export function useSmartReducer<T, A>(config: SmartReducerConfig<T, A>) {
  const { initialState, reducer, middleware, persist, logger } = config;

  // 应用中间件的增强 Reducer
  const enhancedReducer = useCallback((state: T, action: A): T => {
    let nextState = state;

    // 日志中间件
    if (logger) {
      console.group(`Action: ${JSON.stringify(action)}`);
      console.log('Previous State:', state);
    }

    // 应用自定义中间件
    if (middleware) {
      nextState = middleware.reduce((acc, middlewareFn) => {
        return middlewareFn(acc, action, () => reducer(acc, action));
      }, state);
    } else {
      nextState = reducer(state, action);
    }

    // 日志输出
    if (logger) {
      console.log('Next State:', nextState);
      console.groupEnd();
    }

    return nextState;
  }, [reducer, middleware, logger]);

  // 从持久化存储加载初始状态
  const loadPersistedState = useCallback((): T => {
    if (persist) {
      const storage = persist.storage === 'sessionStorage'
        ? sessionStorage
        : localStorage;

      try {
        const stored = storage.getItem(persist.key);
        return stored ? JSON.parse(stored) : initialState;
      } catch (error) {
        console.error('Failed to load persisted state:', error);
        return initialState;
      }
    }
    return initialState;
  }, [persist, initialState]);

  const [state, dispatch] = useReducer(enhancedReducer, loadPersistedState());

  // 持久化状态变化
  useEffect(() => {
    if (persist) {
      const storage = persist.storage === 'sessionStorage'
        ? sessionStorage
        : localStorage;

      try {
        storage.setItem(persist.key, JSON.stringify(state));
      } catch (error) {
        console.error('Failed to persist state:', error);
      }
    }
  }, [state, persist]);

  // 增强 dispatch 函数
  const enhancedDispatch = useCallback((action: A) => {
    dispatch(action);
  }, [dispatch]);

  return { state, dispatch: enhancedDispatch };
}

// 实际使用示例：购物车状态管理
interface CartState {
  items: Array<{
    id: string;
    name: string;
    price: number;
    quantity: number;
  }>;
  total: number;
  isCheckingOut: boolean;
}

type CartAction =
  | { type: 'ADD_ITEM'; payload: { id: string; name: string; price: number } }
  | { type: 'REMOVE_ITEM'; payload: { id: string } }
  | { type: 'UPDATE_QUANTITY'; payload: { id: string; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'CHECKOUT_START' }
  | { type: 'CHECKOUT_SUCCESS' }
  | { type: 'CHECKOUT_ERROR'; payload: { error: string } };

const cartReducer = (state: CartState, action: CartAction): CartState => {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingItem = state.items.find(item => item.id === action.payload.id);

      if (existingItem) {
        return {
          ...state,
          items: state.items.map(item =>
            item.id === action.payload.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          ),
          total: state.total + action.payload.price,
        };
      }

      return {
        ...state,
        items: [...state.items, { ...action.payload, quantity: 1 }],
        total: state.total + action.payload.price,
      };
    }

    case 'REMOVE_ITEM': {
      const item = state.items.find(item => item.id === action.payload.id);
      if (!item) return state;

      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload.id),
        total: state.total - (item.price * item.quantity),
      };
    }

    case 'UPDATE_QUANTITY': {
      const item = state.items.find(item => item.id === action.payload.id);
      if (!item) return state;

      const quantityDiff = action.payload.quantity - item.quantity;

      return {
        ...state,
        items: state.items.map(item =>
          item.id === action.payload.id
            ? { ...item, quantity: action.payload.quantity }
            : item
        ),
        total: state.total + (item.price * quantityDiff),
      };
    }

    case 'CLEAR_CART':
      return { items: [], total: 0, isCheckingOut: false };

    case 'CHECKOUT_START':
      return { ...state, isCheckingOut: true };

    case 'CHECKOUT_SUCCESS':
      return { items: [], total: 0, isCheckingOut: false };

    case 'CHECKOUT_ERROR':
      return { ...state, isCheckingOut: false };

    default:
      return state;
  }
};

// 购物车中间件：库存检查
const inventoryMiddleware: Array<(state: CartState, action: CartAction, next: () => CartState) => CartState> = [
  (state, action, next) => {
    if (action.type === 'ADD_ITEM') {
      // 检查库存（模拟）
      const hasInventory = Math.random() > 0.1; // 90% 有库存

      if (!hasInventory) {
        console.warn('Item out of stock:', action.payload);
        return state; // 阻止添加
      }
    }

    return next();
  }
];

export function useShoppingCart() {
  return useSmartReducer<CartState, CartAction>({
    initialState: { items: [], total: 0, isCheckingOut: false },
    reducer: cartReducer,
    middleware: inventoryMiddleware,
    persist: {
      key: 'shopping-cart',
      storage: 'localStorage',
    },
    logger: process.env.NODE_ENV === 'development',
  });
}
```

## 🌐 全局状态管理模式

### 1. Zustand 企业级配置
**轻量级但功能强大的状态管理**

```typescript
// stores/index.ts
import { create } from 'zustand';
import { devtools, subscribeWithSelector, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// 类型定义
interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'user' | 'admin' | 'moderator';
  preferences: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    notifications: boolean;
  };
}

interface AppState {
  // 用户状态
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // 应用状态
  theme: 'light' | 'dark' | 'auto';
  sidebarOpen: boolean;
  notifications: Array<{
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    title: string;
    message: string;
    timestamp: Date;
    read: boolean;
  }>;

  // 系统状态
  online: boolean;
  lastActivity: Date;

  // 操作方法
  setUser: (user: User | null) => void;
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  toggleSidebar: () => void;
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  setOnline: (online: boolean) => void;
  updateLastActivity: () => void;
  logout: () => void;
}

// 创建 Zustand Store
export const useAppStore = create<AppState>()(
  devtools(
    subscribeWithSelector(
      persist(
        immer((set, get) => ({
          // 初始状态
          user: null,
          isAuthenticated: false,
          isLoading: false,
          theme: 'auto',
          sidebarOpen: true,
          notifications: [],
          online: navigator.onLine,
          lastActivity: new Date(),

          // 用户操作
          setUser: (user) => set((state) => {
            state.user = user;
            state.isAuthenticated = !!user;
            state.isLoading = false;
          }),

          setTheme: (theme) => set((state) => {
            state.theme = theme;
            if (state.user) {
              state.user.preferences.theme = theme;
            }
          }),

          toggleSidebar: () => set((state) => {
            state.sidebarOpen = !state.sidebarOpen;
          }),

          // 通知操作
          addNotification: (notification) => set((state) => {
            const newNotification = {
              ...notification,
              id: crypto.randomUUID(),
              timestamp: new Date(),
              read: false,
            };
            state.notifications.unshift(newNotification);

            // 限制通知数量
            if (state.notifications.length > 50) {
              state.notifications = state.notifications.slice(0, 50);
            }
          }),

          markNotificationRead: (id) => set((state) => {
            const notification = state.notifications.find(n => n.id === id);
            if (notification) {
              notification.read = true;
            }
          }),

          clearNotifications: () => set((state) => {
            state.notifications = [];
          }),

          // 系统操作
          setOnline: (online) => set((state) => {
            state.online = online;
          }),

          updateLastActivity: () => set((state) => {
            state.lastActivity = new Date();
          }),

          logout: () => set((state) => {
            state.user = null;
            state.isAuthenticated = false;
            state.notifications = [];
          }),
        })),
        {
          name: 'app-store',
          partialize: (state) => ({
            user: state.user,
            theme: state.theme,
            sidebarOpen: state.sidebarOpen,
            notifications: state.notifications.filter(n => !n.read),
          }),
        }
      )
    ),
    {
      name: 'AppStore',
    }
  )
);

// 选择器 hooks - 优化性能
export const useUser = () => useAppStore((state) => state.user);
export const useIsAuthenticated = () => useAppStore((state) => state.isAuthenticated);
export const useTheme = () => useAppStore((state) => state.theme);
export const useSidebarOpen = () => useAppStore((state) => state.sidebarOpen);
export const useNotifications = () => useAppStore((state) => state.notifications);
export const useUnreadNotifications = () => useAppStore((state) =>
  state.notifications.filter(n => !n.read)
);
export const useOnlineStatus = () => useAppStore((state) => state.online);

// 监听器设置
if (typeof window !== 'undefined') {
  // 监听网络状态
  window.addEventListener('online', () => {
    useAppStore.getState().setOnline(true);
  });

  window.addEventListener('offline', () => {
    useAppStore.getState().setOnline(false);
  });

  // 监听用户活动
  const updateActivity = () => {
    useAppStore.getState().updateLastActivity();
  };

  window.addEventListener('click', updateActivity);
  window.addEventListener('keydown', updateActivity);
  window.addEventListener('scroll', updateActivity);

  // 自动登出检查
  setInterval(() => {
    const { lastActivity, isAuthenticated, logout } = useAppStore.getState();
    const now = new Date();
    const inactiveTime = now.getTime() - lastActivity.getTime();
    const maxInactiveTime = 30 * 60 * 1000; // 30分钟

    if (isAuthenticated && inactiveTime > maxInactiveTime) {
      logout();
      window.location.href = '/login?reason=timeout';
    }
  }, 60000); // 每分钟检查一次
}
```

### 2. 高级 Store 模式
**模块化和可扩展的 Store 架构**

```typescript
// stores/base-store.ts
import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// 基础 Store 类型
interface BaseStore<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;

  // 操作
  setData: (data: T) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearData: () => void;
  refresh: () => Promise<void>;
}

// 创建基础 Store
export function createBaseStore<T>(
  name: string,
  fetchFn: () => Promise<T>
) {
  return create<BaseStore<T>>()(
    devtools(
      subscribeWithSelector(
        immer((set, get) => ({
          data: null,
          loading: false,
          error: null,
          lastUpdated: null,

          setData: (data) => set((state) => {
            state.data = data;
            state.loading = false;
            state.error = null;
            state.lastUpdated = new Date();
          }),

          setLoading: (loading) => set((state) => {
            state.loading = loading;
            if (loading) {
              state.error = null;
            }
          }),

          setError: (error) => set((state) => {
            state.error = error;
            state.loading = false;
          }),

          clearData: () => set((state) => {
            state.data = null;
            state.error = null;
            state.lastUpdated = null;
          }),

          refresh: async () => {
            const { setLoading, setError, setData } = get();

            setLoading(true);
            try {
              const data = await fetchFn();
              setData(data);
            } catch (error) {
              setError(error instanceof Error ? error.message : 'Unknown error');
            }
          },
        }))
      ),
      { name }
    )
  );
}

// 缓存 Store
interface CacheStore<T> extends BaseStore<T> {
  cacheTime: number;
  maxAge: number;

  setCacheTime: (time: number) => void;
  isExpired: () => boolean;
  getCachedData: () => T | null;
}

export function createCacheStore<T>(
  name: string,
  fetchFn: () => Promise<T>,
  maxAge: number = 5 * 60 * 1000 // 5分钟
) {
  return create<CacheStore<T>>()(
    devtools(
      subscribeWithSelector(
        immer((set, get) => ({
          data: null,
          loading: false,
          error: null,
          lastUpdated: null,
          cacheTime: 0,
          maxAge,

          setData: (data) => set((state) => {
            state.data = data;
            state.loading = false;
            state.error = null;
            state.lastUpdated = new Date();
            state.cacheTime = Date.now();
          }),

          setLoading: (loading) => set((state) => {
            state.loading = loading;
          }),

          setError: (error) => set((state) => {
            state.error = error;
            state.loading = false;
          }),

          clearData: () => set((state) => {
            state.data = null;
            state.error = null;
            state.lastUpdated = null;
            state.cacheTime = 0;
          }),

          setCacheTime: (time) => set((state) => {
            state.cacheTime = time;
          }),

          isExpired: () => {
            const { cacheTime, maxAge } = get();
            return Date.now() - cacheTime > maxAge;
          },

          getCachedData: () => {
            const { data, isExpired } = get();
            return isExpired() ? null : data;
          },

          refresh: async () => {
            const { setLoading, setError, setData, isExpired, data } = get();

            if (!isExpired() && data) {
              return; // 使用缓存数据
            }

            setLoading(true);
            try {
              const freshData = await fetchFn();
              setData(freshData);
            } catch (error) {
              setError(error instanceof Error ? error.message : 'Unknown error');
            }
          },
        }))
      ),
      { name }
    )
  );
}

// 实际使用：用户数据 Store
const fetchUserData = async () => {
  const response = await fetch('/api/user/profile');
  if (!response.ok) throw new Error('Failed to fetch user data');
  return response.json();
};

export const useUserStore = createCacheStore(
  'user-store',
  fetchUserData,
  10 * 60 * 1000 // 10分钟缓存
);

// 文章数据 Store
const fetchArticles = async () => {
  const response = await fetch('/api/articles');
  if (!response.ok) throw new Error('Failed to fetch articles');
  return response.json();
};

export const useArticlesStore = createCacheStore(
  'articles-store',
  fetchArticles,
  5 * 60 * 1000 // 5分钟缓存
);
```

## 🔄 React Query 与服务器状态

### 1. TanStack Query 企业级配置
**强大的服务器状态管理**

```typescript
// lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';

// 创建 Query Client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // 重试配置
      retry: (failureCount, error: any) => {
        // 4xx 错误不重试
        if (error?.status >= 400 && error?.status < 500) {
          return false;
        }
        // 最多重试3次
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

      // 缓存配置
      staleTime: 5 * 60 * 1000, // 5分钟内数据视为新鲜
      gcTime: 10 * 60 * 1000, // 10分钟缓存时间
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,

      // 错误处理
      throwOnError: false,

      // 查询配置
      networkMode: 'online',
    },
    mutations: {
      retry: 1,
      networkMode: 'online',
    },
  },
});

// hooks/use-query-with-error-handling.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

// 增强的查询 Hook
export function useQueryWithError<T>(
  queryKey: any[],
  queryFn: () => Promise<T>,
  options?: {
    errorMessage?: string;
    successMessage?: string;
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
  }
) {
  return useQuery({
    queryKey,
    queryFn: async () => {
      try {
        const result = await queryFn();
        if (options?.successMessage) {
          toast.success(options.successMessage);
        }
        options?.onSuccess?.(result);
        return result;
      } catch (error) {
        const errorMessage = options?.errorMessage ||
          (error instanceof Error ? error.message : 'Query failed');
        toast.error(errorMessage);
        options?.onError?.(error instanceof Error ? error : new Error(String(error)));
        throw error;
      }
    },
  });
}

// 增强的变更 Hook
export function useMutationWithError<TData, TVariables, TContext>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options?: {
    successMessage?: string;
    errorMessage?: string;
    onSuccess?: (data: TData, variables: TVariables, context?: TContext) => void;
    onError?: (error: Error, variables: TVariables, context?: TContext) => void;
    invalidateQueries?: any[];
  }
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (variables) => {
      try {
        const result = await mutationFn(variables);
        if (options?.successMessage) {
          toast.success(options.successMessage);
        }
        options?.onSuccess?.(result, variables);

        // 失效相关查询
        if (options?.invalidateQueries) {
          options.invalidateQueries.forEach(queryKey => {
            queryClient.invalidateQueries({ queryKey });
          });
        }

        return result;
      } catch (error) {
        const errorMessage = options?.errorMessage ||
          (error instanceof Error ? error.message : 'Mutation failed');
        toast.error(errorMessage);
        options?.onError?.(error instanceof Error ? error : new Error(String(error)), variables);
        throw error;
      }
    },
  });
}

// 实际使用示例
interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: string;
}

// 获取用户资料
export function useUserProfile(userId: string) {
  return useQueryWithError(
    ['user-profile', userId],
    () => fetch(`/api/users/${userId}`).then(res => res.json()),
    {
      errorMessage: 'Failed to load user profile',
    }
  );
}

// 更新用户资料
export function useUpdateProfile(userId: string) {
  return useMutationWithError(
    (data: Partial<UserProfile>) =>
      fetch(`/api/users/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      }).then(res => res.json()),
    {
      successMessage: 'Profile updated successfully',
      errorMessage: 'Failed to update profile',
      invalidateQueries: [['user-profile', userId]],
    }
  );
}
```

### 2. 实时数据同步
**WebSocket 和实时状态管理**

```typescript
// hooks/use-realtime.ts
import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

interface RealtimeConfig {
  url: string;
  channels: string[];
  onConnect?: () => void;
  onDisconnect?: () => void;
  onMessage?: (message: any) => void;
  onError?: (error: Error) => void;
}

export function useRealtime(config: RealtimeConfig) {
  const wsRef = useRef<WebSocket | null>(null);
  const queryClient = useQueryClient();
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(config.url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        reconnectAttempts.current = 0;

        // 订阅频道
        config.channels.forEach(channel => {
          ws.send(JSON.stringify({
            type: 'subscribe',
            channel,
          }));
        });

        config.onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          // 处理不同类型的消息
          switch (message.type) {
            case 'data_update':
              // 更新相关查询缓存
              queryClient.invalidateQueries({
                queryKey: message.queryKey,
              });
              break;

            case 'data_patch':
              // 直接更新查询缓存数据
              queryClient.setQueryData(
                message.queryKey,
                (oldData: any) => ({
                  ...oldData,
                  ...message.data,
                })
              );
              break;

            default:
              config.onMessage?.(message);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        config.onDisconnect?.();

        // 自动重连
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 30000);

          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts})`);
            connect();
          }, delay);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        config.onError?.(new Error('WebSocket connection error'));
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      config.onError?.(error instanceof Error ? error : new Error('Connection failed'));
    }
  }, [config, queryClient]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();
    return disconnect;
  }, [connect, disconnect]);

  return {
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
    sendMessage,
    disconnect,
    connect,
  };
}

// 使用示例：实时通知
export function useRealtimeNotifications() {
  const { sendMessage } = useRealtime({
    url: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:3001',
    channels: ['notifications'],
    onMessage: (message) => {
      if (message.type === 'notification') {
        // 显示通知
        toast(message.data.title, {
          description: message.data.message,
        });
      }
    },
  });

  return { sendMessage };
}
```

## 💾 持久化状态管理

### 1. IndexedDB 状态管理
**客户端大数据存储**

```typescript
// lib/indexeddb.ts
import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface AppDB extends DBSchema {
  users: {
    key: string;
    value: {
      id: string;
      name: string;
      email: string;
      avatar?: string;
      updatedAt: string;
    };
    indexes: {
      by_email: string;
    };
  };

  posts: {
    key: string;
    value: {
      id: string;
      title: string;
      content: string;
      authorId: string;
      createdAt: string;
      updatedAt: string;
    };
    indexes: {
      by_author: string;
      by_created_at: string;
    };
  };

  cache: {
    key: string;
    value: {
      data: any;
      url: string;
      cachedAt: string;
      expiresAt: string;
    };
    indexes: {
      by_url: string;
      by_expires_at: string;
    };
  };
}

class IndexedDBManager {
  private db: IDBPDatabase<AppDB> | null = null;
  private dbPromise: Promise<IDBPDatabase<AppDB>> | null = null;

  async getDB(): Promise<IDBPDatabase<AppDB>> {
    if (this.db) return this.db;

    if (!this.dbPromise) {
      this.dbPromise = this.initDB();
    }

    this.db = await this.dbPromise;
    return this.db;
  }

  private async initDB(): Promise<IDBPDatabase<AppDB>> {
    const db = await openDB<AppDB>('AppDatabase', 1, {
      upgrade(db) {
        // Users store
        if (!db.objectStoreNames.contains('users')) {
          const userStore = db.createObjectStore('users', { keyPath: 'id' });
          userStore.createIndex('by_email', 'email', { unique: true });
        }

        // Posts store
        if (!db.objectStoreNames.contains('posts')) {
          const postStore = db.createObjectStore('posts', { keyPath: 'id' });
          postStore.createIndex('by_author', 'authorId');
          postStore.createIndex('by_created_at', 'createdAt');
        }

        // Cache store
        if (!db.objectStoreNames.contains('cache')) {
          const cacheStore = db.createObjectStore('cache', { keyPath: 'id', autoIncrement: true });
          cacheStore.createIndex('by_url', 'url', { unique: true });
          cacheStore.createIndex('by_expires_at', 'expiresAt');
        }
      },
    });

    return db;
  }

  // 用户相关操作
  async saveUser(user: AppDB['users']['value']) {
    const db = await this.getDB();
    return db.put('users', {
      ...user,
      updatedAt: new Date().toISOString(),
    });
  }

  async getUser(userId: string) {
    const db = await this.getDB();
    return db.get('users', userId);
  }

  async getUserByEmail(email: string) {
    const db = await this.getDB();
    return db.getFromIndex('users', 'by_email', email);
  }

  async getAllUsers() {
    const db = await this.getDB();
    return db.getAll('users');
  }

  async deleteUser(userId: string) {
    const db = await this.getDB();
    return db.delete('users', userId);
  }

  // 帖子相关操作
  async savePost(post: AppDB['posts']['value']) {
    const db = await this.getDB();
    return db.put('posts', {
      ...post,
      updatedAt: new Date().toISOString(),
    });
  }

  async getPost(postId: string) {
    const db = await this.getDB();
    return db.get('posts', postId);
  }

  async getPostsByAuthor(authorId: string) {
    const db = await this.getDB();
    return db.getAllFromIndex('posts', 'by_author', authorId);
  }

  async getRecentPosts(limit = 10) {
    const db = await this.getDB();
    const tx = db.transaction('posts', 'readonly');
    const index = tx.store.index('by_created_at');

    const recentPosts = [];
    let cursor = await index.openCursor(null, 'prev');

    while (cursor && recentPosts.length < limit) {
      recentPosts.push(cursor.value);
      cursor = await cursor.continue();
    }

    await tx.done;
    return recentPosts;
  }

  // 缓存相关操作
  async cacheResponse(url: string, data: any, expiresIn = 5 * 60 * 1000) {
    const db = await this.getDB();
    const now = new Date();
    const expiresAt = new Date(now.getTime() + expiresIn);

    const cacheEntry: AppDB['cache']['value'] = {
      id: crypto.randomUUID(),
      data,
      url,
      cachedAt: now.toISOString(),
      expiresAt: expiresAt.toISOString(),
    };

    return db.put('cache', cacheEntry);
  }

  async getCachedResponse(url: string) {
    const db = await this.getDB();
    const cached = await db.getFromIndex('cache', 'by_url', url);

    if (!cached) return null;

    const expiresAt = new Date(cached.expiresAt);
    if (expiresAt < new Date()) {
      // 过期，删除缓存
      await db.delete('cache', cached.id);
      return null;
    }

    return cached.data;
  }

  async clearExpiredCache() {
    const db = await this.getDB();
    const tx = db.transaction('cache', 'readwrite');
    const index = tx.store.index('by_expires_at');
    const now = new Date().toISOString();

    let cursor = await index.openCursor(IDBKeyRange.upperBound(now));
    while (cursor) {
      cursor.delete();
      cursor = await cursor.continue();
    }

    await tx.done;
  }

  // 清理操作
  async clearAll() {
    const db = await this.getDB();
    const tx = db.transaction(['users', 'posts', 'cache'], 'readwrite');

    await Promise.all([
      tx.objectStore('users').clear(),
      tx.objectStore('posts').clear(),
      tx.objectStore('cache').clear(),
    ]);

    await tx.done;
  }
}

export const indexedDBManager = new IndexedDBManager();

// hooks/use-indexeddb.ts
import { useState, useEffect, useCallback } from 'react';

export function useIndexedDB<T>(
  key: string,
  fetchFn?: () => Promise<T>,
  options?: {
    staleTime?: number;
    cacheTime?: number;
    enabled?: boolean;
  }
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!options?.enabled) return;

    setLoading(true);
    setError(null);

    try {
      // 尝试从 IndexedDB 获取数据
      const cached = await indexedDBManager.getCachedResponse(key);

      if (cached) {
        setData(cached);
        setLoading(false);
        return;
      }

      // 从网络获取数据
      if (fetchFn) {
        const freshData = await fetchFn();
        setData(freshData);

        // 缓存到 IndexedDB
        await indexedDBManager.cacheResponse(key, freshData, options?.cacheTime);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [key, fetchFn, options?.cacheTime, options?.enabled]);

  const refetch = useCallback(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return { data, loading, error, refetch };
}
```

### 2. 服务器状态持久化
**数据库状态管理**

```typescript
// lib/database-state.ts
import { create } from 'zustand';
import { subscribeWithSelector, devtools } from 'zustand/middleware';

// 数据库状态管理接口
interface DatabaseState<T> {
  data: T[];
  loading: boolean;
  error: string | null;

  // CRUD 操作
  create: (item: Omit<T, 'id'>) => Promise<void>;
  read: (id?: string) => Promise<void>;
  update: (id: string, updates: Partial<T>) => Promise<void>;
  delete: (id: string) => Promise<void>;

  // 批量操作
  createMany: (items: Omit<T, 'id'>[]) => Promise<void>;
  updateMany: (updates: Array<{ id: string; changes: Partial<T> }>) => Promise<void>;
  deleteMany: (ids: string[]) => Promise<void>;

  // 查询操作
  findBy: (criteria: Partial<T>) => Promise<T[]>;
  findOneBy: (criteria: Partial<T>) => Promise<T | null>;

  // 同步操作
  sync: () => Promise<void>;
  clearCache: () => void;
}

// 创建数据库状态管理
export function createDatabaseStore<T extends { id: string }>(
  name: string,
  apiUrl: string
) {
  return create<DatabaseState<T>>()(
    devtools(
      subscribeWithSelector((set, get) => ({
        data: [],
        loading: false,
        error: null,

        // 创建单个项目
        create: async (item) => {
          set({ loading: true, error: null });

          try {
            const response = await fetch(apiUrl, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(item),
            });

            if (!response.ok) throw new Error('Failed to create item');

            const newItem = await response.json();

            set(state => ({
              data: [...state.data, newItem],
              loading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Create failed',
              loading: false,
            });
            throw error;
          }
        },

        // 读取数据
        read: async (id) => {
          set({ loading: true, error: null });

          try {
            const url = id ? `${apiUrl}/${id}` : apiUrl;
            const response = await fetch(url);

            if (!response.ok) throw new Error('Failed to fetch data');

            const result = await response.json();

            set(state => ({
              data: Array.isArray(result) ? result : id ? [result] : [],
              loading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Fetch failed',
              loading: false,
            });
            throw error;
          }
        },

        // 更新项目
        update: async (id, updates) => {
          set({ loading: true, error: null });

          try {
            const response = await fetch(`${apiUrl}/${id}`, {
              method: 'PATCH',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(updates),
            });

            if (!response.ok) throw new Error('Failed to update item');

            const updatedItem = await response.json();

            set(state => ({
              data: state.data.map(item =>
                item.id === id ? { ...item, ...updatedItem } : item
              ),
              loading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Update failed',
              loading: false,
            });
            throw error;
          }
        },

        // 删除项目
        delete: async (id) => {
          set({ loading: true, error: null });

          try {
            const response = await fetch(`${apiUrl}/${id}`, {
              method: 'DELETE',
            });

            if (!response.ok) throw new Error('Failed to delete item');

            set(state => ({
              data: state.data.filter(item => item.id !== id),
              loading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Delete failed',
              loading: false,
            });
            throw error;
          }
        },

        // 批量创建
        createMany: async (items) => {
          set({ loading: true, error: null });

          try {
            const response = await fetch(`${apiUrl}/batch`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ items }),
            });

            if (!response.ok) throw new Error('Failed to create items');

            const newItems = await response.json();

            set(state => ({
              data: [...state.data, ...newItems],
              loading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Batch create failed',
              loading: false,
            });
            throw error;
          }
        },

        // 批量更新
        updateMany: async (updates) => {
          set({ loading: true, error: null });

          try {
            const response = await fetch(`${apiUrl}/batch`, {
              method: 'PATCH',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ updates }),
            });

            if (!response.ok) throw new Error('Failed to update items');

            const updatedItems = await response.json();

            set(state => ({
              data: state.data.map(item => {
                const update = updatedItems.find((u: any) => u.id === item.id);
                return update ? { ...item, ...update } : item;
              }),
              loading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Batch update failed',
              loading: false,
            });
            throw error;
          }
        },

        // 批量删除
        deleteMany: async (ids) => {
          set({ loading: true, error: null });

          try {
            const response = await fetch(`${apiUrl}/batch`, {
              method: 'DELETE',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ ids }),
            });

            if (!response.ok) throw new Error('Failed to delete items');

            set(state => ({
              data: state.data.filter(item => !ids.includes(item.id)),
              loading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Batch delete failed',
              loading: false,
            });
            throw error;
          }
        },

        // 查询操作
        findBy: async (criteria) => {
          set({ loading: true, error: null });

          try {
            const params = new URLSearchParams(criteria as any);
            const response = await fetch(`${apiUrl}/search?${params}`);

            if (!response.ok) throw new Error('Failed to search items');

            const results = await response.json();

            set({ data: results, loading: false });
            return results;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Search failed',
              loading: false,
            });
            throw error;
          }
        },

        findOneBy: async (criteria) => {
          set({ loading: true, error: null });

          try {
            const params = new URLSearchParams(criteria as any);
            const response = await fetch(`${apiUrl}/search/one?${params}`);

            if (!response.ok) throw new Error('Failed to find item');

            const result = await response.json();

            set({ loading: false });
            return result;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Find failed',
              loading: false,
            });
            throw error;
          }
        },

        // 同步数据
        sync: async () => {
          const { read } = get();
          await read();
        },

        // 清除缓存
        clearCache: () => {
          set({ data: [], error: null });
        },
      }))
    ),
    { name }
  );
}

// 使用示例：任务管理
interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
}

export const useTaskStore = createDatabaseStore<Task>('task-store', '/api/tasks');
```

## 🎭 状态管理模式最佳实践

### 1. 状态选择优化
**性能优化和选择器模式**

```typescript
// hooks/use-optimized-selectors.ts
import { useMemo } from 'react';
import { useShallow } from 'zustand/react/shallow';

// 记忆化选择器
export function useMemoizedSelector<T, R>(
  selector: (state: T) => R,
  deps: any[] = []
) {
  return useMemo(() => selector, deps);
}

// 浅比较选择器
export function useShallowSelector<T, R>(
  selector: (state: T) => R
) {
  // Zustand 内置的 shallow 比较函数
  return selector;
}

// 复合选择器示例
export function useComplexUserSelector() {
  const user = useAppStore(useMemoizedSelector(
    (state) => ({
      id: state.user?.id,
      name: state.user?.name,
      avatar: state.user?.avatar,
      preferences: state.user?.preferences,
      isAuthenticated: state.isAuthenticated,
    }),
    []
  ));

  return user;
}

// 计算属性选择器
export function useComputedNotifications() {
  const notifications = useAppStore(useShallow(state => state.notifications));

  return useMemo(() => ({
    total: notifications.length,
    unread: notifications.filter(n => !n.read).length,
    byType: notifications.reduce((acc, n) => {
      acc[n.type] = (acc[n.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    recent: notifications.filter(n =>
      new Date(n.timestamp).getTime() > Date.now() - 24 * 60 * 60 * 1000
    ),
  }), [notifications]);
}
```

### 2. 错误处理和恢复
**健壮的错误处理策略**

```typescript
// hooks/use-state-with-error-handling.ts
import { useState, useCallback, useEffect } from 'react';

interface StateWithRetry<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  retryCount: number;

  retry: () => void;
  reset: () => void;
}

export function useStateWithRetry<T>(
  fetchFn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    retryDelay?: number;
    exponentialBackoff?: boolean;
  }
): StateWithRetry<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const maxRetries = options?.maxRetries ?? 3;
  const baseRetryDelay = options?.retryDelay ?? 1000;
  const useExponentialBackoff = options?.exponentialBackoff ?? true;

  const execute = useCallback(async (attempt = 1) => {
    setLoading(true);
    setError(null);

    try {
      const result = await fetchFn();
      setData(result);
      setRetryCount(0);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));

      if (attempt < maxRetries) {
        const delay = useExponentialBackoff
          ? baseRetryDelay * Math.pow(2, attempt - 1)
          : baseRetryDelay;

        setTimeout(() => {
          execute(attempt + 1);
        }, delay);

        setRetryCount(attempt);
      } else {
        setError(error);
        setRetryCount(attempt);
      }
    } finally {
      setLoading(false);
    }
  }, [fetchFn, maxRetries, baseRetryDelay, useExponentialBackoff]);

  const retry = useCallback(() => {
    execute(1);
  }, [execute]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setRetryCount(0);
  }, []);

  useEffect(() => {
    execute();
  }, [execute]);

  return {
    data,
    loading,
    error,
    retryCount,
    retry,
    reset,
  };
}
```

## 📋 企业级状态管理清单

### 状态选择指南
- [ ] **本地状态**: 使用 useState/useReducer 管理组件内部状态
- [ ] **共享状态**: 使用 Zustand 管理跨组件状态
- [ ] **服务器状态**: 使用 React Query 管理远程数据
- [ ] **持久化状态**: 使用 IndexedDB/LocalStorage 管理持久化数据
- [ ] **实时状态**: 使用 WebSocket 管理实时同步数据

### 性能优化
- [ ] **选择器优化**: 使用记忆化选择器避免不必要的重渲染
- [ ] **状态规范化**: 使用规范化数据结构提高查找效率
- [ ] **缓存策略**: 合理设置缓存时间和失效策略
- [ ] **批量更新**: 合并多个状态更新减少重渲染
- [ ] **懒加载**: 按需加载状态数据和组件

### 错误处理
- [ ] **重试机制**: 实现指数退避重试策略
- [ ] **错误边界**: 使用 Error Boundary 防止状态错误崩溃应用
- [ ] **降级策略**: 在状态不可用时提供备用方案
- [ ] **错误监控**: 集成错误监控和上报系统
- [ ] **用户反馈**: 提供清晰的错误提示和恢复选项

### 安全考虑
- [ ] **数据验证**: 验证状态数据的完整性和合法性
- [ ] **权限控制**: 根据用户权限控制状态访问
- [ ] **敏感数据**: 避免在客户端存储敏感信息
- [ ] **XSS 防护**: 防止通过状态注入恶意脚本
- [ ] **CSRF 防护**: 使用 CSRF Token 保护状态修改操作

## 📖 总结

Next.js 16 的状态管理生态系统提供了全面的解决方案：

### 核心特性：
1. **多样化选择**: 从本地状态到全局状态的完整解决方案
2. **性能优化**: 内置缓存、选择器优化和批量更新
3. **类型安全**: 完整的 TypeScript 支持
4. **开发体验**: 优秀的 DevTools 和调试支持

### 最佳实践：
先找状态的所有者：控件内部开关留在局部，需要分享和返回恢复的筛选可放 URL，服务端结果由请求缓存管理，跨页面业务状态再考虑共享 store。不要因为装了状态库就把所有值复制进去。

派生值尽量从单一来源计算，更新时验证所有消费界面一致。只有测到无关更新造成成本时，再优化订阅和记忆化；失败恢复也要防止旧快照覆盖用户后续操作。

---

## 模式不变量

- **状态按作用域与来源分类、各归其主**：本地 UI 状态、跨组件共享状态、服务器状态、持久化状态是四类不同问题，机制不可混用；服务器状态永远以服务器为事实来源，客户端持有的只是缓存（对照"状态分类体系"与状态选择指南）。
- **状态变更是集中声明的转换，而非散落的赋值**：复杂状态以 action/reducer 表达，变更逻辑集中一处、可插入中间件与日志（对照"智能 useReducer 模式"购物车的库存校验中间件）。
- **订阅粒度决定重渲染范围**：组件订阅所需的最小状态切片（选择器配合浅比较），而非整个 store——粗粒度订阅会把无关变更放大成大范围重渲染（对照 Zustand 选择器 hooks 与 `useShallow`）。
- **持久化是显式圈定的子集**：写入持久层前先声明哪些字段值得持久化，可再生的派生数据与敏感信息不落盘（对照 Zustand `persist` 的 `partialize` 与安全考虑中"避免在客户端存储敏感信息"）。
- **缓存数据必须携带过期语义**：条目记录时间戳与存活期，读取时判定过期、过期即清理或回源（对照 `createCacheStore` 的 `isExpired` 与 IndexedDB cache 的 `expiresAt`）。

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[客户端组件模式](./03-client-components-patterns.md)**: 深入了解客户端组件和本地状态管理
- 📄 **[数据获取模式](./04-data-fetching-patterns.md)**: 学习服务器状态管理和缓存策略
- 📄 **[表单验证模式](./06-form-validation-patterns.md)**: 掌握表单状态管理和验证集成
- 📄 **[认证流程模式](./07-authentication-flows.md)**: 实现用户状态和认证管理

### 参考章节
- 📖 **[本模块其他章节]**: [客户端组件模式](./03-client-components-patterns.md#21-本地状态管理)中的组件状态部分
- 📖 **[其他模块相关内容]**: [React语法速查表](../language-concepts/01-react-syntax-cheatsheet.md)中的Hooks部分

---

## 📝 总结

### 核心要点回顾
1. **状态分类体系**: 本地状态、共享状态、服务器状态的分类管理
2. **Zustand企业级应用**: 状态持久化、中间件、TypeScript集成
3. **React Query优化**: 服务器状态缓存、后台更新、乐观更新
4. **高级模式**: 状态同步、性能优化、错误边界处理
5. **状态持久化**: IndexedDB、localStorage、云存储集成

### 学习成果检查
- [ ] 是否理解了不同状态类型的分类和管理？
- [ ] 是否能够构建Zustand企业级状态管理？
- [ ] 是否掌握了React Query的缓存和同步策略？
- [ ] 是否能够实现复杂的状态持久化方案？
- [ ] 是否具备了企业级状态管理架构设计能力？

---

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

**文档状态**: ✅ 已完成 | 🚧 进行中 | 📋 计划中
**最后更新**: 2026年9月
**版本**: v1.0.0

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
