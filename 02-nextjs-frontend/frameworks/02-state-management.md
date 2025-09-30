# 现代状态管理 - Zustand、Jotai 和 TanStack Query

## 概述

状态管理是 React 应用开发中的重要组成部分。与 PHP 中使用 Session 和数据库来管理状态不同，React 应用需要在客户端管理复杂的状态。本指南将介绍 Zustand、Jotai 和 TanStack Query 等现代状态管理解决方案。

## 从 PHP 状态管理到 React 状态管理

### PHP 状态管理方式
```php
// PHP Session 状态管理
session_start();
$_SESSION['user_id'] = $user->id;
$_SESSION['cart_items'] = $cart->getItems();

// 数据库状态
$pdo->query("UPDATE users SET status = 'active' WHERE id = ?");
```

### React 状态管理方式
```jsx
// React 本地状态
const [count, setCount] = useState(0);
const [user, setUser] = useState(null);

// 全局状态管理
const useUserStore = create((set) => ({
  user: null,
  login: (userData) => set({ user: userData }),
  logout: () => set({ user: null }),
}));
```

## Zustand - 轻量级状态管理

### 1. 安装和基础用法

```bash
npm install zustand
```

```tsx
// stores/user.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  login: (userData: User) => void;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,

      login: (userData) => {
        set({ user: userData, isAuthenticated: true });
      },

      logout: () => {
        set({ user: null, isAuthenticated: false });
      },

      updateUser: (userData) => {
        const currentUser = get().user;
        if (currentUser) {
          set({ user: { ...currentUser, ...userData } });
        }
      },
    }),
    {
      name: 'user-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

### 2. 复杂状态管理

```tsx
// stores/cart.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
}

interface CartState {
  items: CartItem[];
  total: number;
  itemCount: number;
  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clearCart: () => void;
  getTotalPrice: () => number;
}

export const useCartStore = create<CartState>()(
  devtools(
    persist(
      (set, get) => ({
        items: [],
        total: 0,
        itemCount: 0,

        addItem: (item) => {
          const items = get().items;
          const existingItem = items.find(i => i.id === item.id);

          if (existingItem) {
            set({
              items: items.map(i =>
                i.id === item.id
                  ? { ...i, quantity: i.quantity + 1 }
                  : i
              ),
            });
          } else {
            set({
              items: [...items, { ...item, quantity: 1 }],
            });
          }

          // 更新总计
          get().updateTotals();
        },

        removeItem: (id) => {
          set({
            items: get().items.filter(item => item.id !== id),
          });
          get().updateTotals();
        },

        updateQuantity: (id, quantity) => {
          if (quantity <= 0) {
            get().removeItem(id);
            return;
          }

          set({
            items: get().items.map(item =>
              item.id === id ? { ...item, quantity } : item
            ),
          });
          get().updateTotals();
        },

        clearCart: () => {
          set({ items: [], total: 0, itemCount: 0 });
        },

        updateTotals: () => {
          const items = get().items;
          const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
          const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

          set({ total, itemCount });
        },

        getTotalPrice: () => {
          return get().total;
        },
      }),
      {
        name: 'cart-storage',
      }
    ),
    { name: 'cart' }
  )
);
```

### 3. 异步操作

```tsx
// stores/api.ts
import { create } from 'zustand';

interface ApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  fetchData: () => Promise<void>;
}

interface User {
  id: string;
  name: string;
  email: string;
}

export const useUserApiStore = create<ApiResponse<User>>((set) => ({
  data: null,
  loading: false,
  error: null,

  fetchData: async () => {
    set({ loading: true, error: null });

    try {
      const response = await fetch('/api/user/profile');
      if (!response.ok) {
        throw new Error('Failed to fetch user data');
      }
      const userData = await response.json();
      set({ data: userData, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
}));
```

## Jotai - 原子化状态管理

### 1. 基础用法

```bash
npm install jotai
```

```tsx
// atoms/user.ts
import { atom } from 'jotai';

export const userAtom = atom<User | null>(null);
export const isAuthenticatedAtom = atom((get) => get(userAtom) !== null);

export const userPreferencesAtom = atom({
  theme: 'light',
  language: 'zh-CN',
  notifications: true,
});
```

### 2. 派生原子

```tsx
// atoms/cart.ts
import { atom } from 'jotai';
import { atomWithStorage } from 'jotai/utils';

export const cartItemsAtom = atomWithStorage<CartItem[]>('cart-items', []);

export const cartTotalAtom = atom((get) => {
  return get(cartItemsAtom).reduce((total, item) => total + item.price * item.quantity, 0);
});

export const cartItemCountAtom = atom((get) => {
  return get(cartItemsAtom).reduce((count, item) => count + item.quantity, 0);
});

export const isInCartAtom = atom(
  (get) => (productId: string) => {
    return get(cartItemsAtom).some(item => item.id === productId);
  }
);
```

### 3. 异步原子

```tsx
// atoms/async.ts
import { atom } from 'jotai';
import { atomWithQuery } from 'jotai/query';

interface Post {
  id: string;
  title: string;
  content: string;
  author: string;
}

export const postsAtom = atomWithQuery<Post[]>(() => ({
  queryKey: ['posts'],
  queryFn: async () => {
    const response = await fetch('/api/posts');
    return response.json();
  },
}));

export const postAtom = atom((get) => (id: string) => {
  const posts = get(postsAtom);
  return posts.find(post => post.id === id);
});
```

### 4. 动作原子

```tsx
// atoms/actions.ts
import { atom } from 'jotai';
import { userAtom } from './user';
import { cartItemsAtom } from './cart';

export const updateUserAction = atom(
  null,
  (get, set, update: Partial<User>) => {
    const currentUser = get(userAtom);
    if (currentUser) {
      set(userAtom, { ...currentUser, ...update });
    }
  }
);

export const addToCartAction = atom(
  null,
  (get, set, item: Omit<CartItem, 'quantity'>) => {
    const currentItems = get(cartItemsAtom);
    const existingItem = currentItems.find(i => i.id === item.id);

    if (existingItem) {
      set(cartItemsAtom,
        currentItems.map(i =>
          i.id === item.id
            ? { ...i, quantity: i.quantity + 1 }
            : i
        )
      );
    } else {
      set(cartItemsAtom, [...currentItems, { ...item, quantity: 1 }]);
    }
  }
);
```

## TanStack Query - 服务端状态管理

### 1. 基础用法

```bash
npm install @tanstack/react-query
```

```tsx
// providers/QueryProvider.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 分钟
      cacheTime: 10 * 60 * 1000, // 10 分钟
      retry: 1,
    },
  },
});

export function QueryProvider({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### 2. 数据查询

```tsx
// hooks/useUsers.ts
import { useQuery } from '@tanstack/react-query';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

const fetchUsers = async (): Promise<User[]> => {
  const response = await fetch('/api/users');
  if (!response.ok) {
    throw new Error('Failed to fetch users');
  }
  return response.json();
};

export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
    staleTime: 5 * 60 * 1000, // 5 分钟
  });
};

export const useUser = (id: string) => {
  return useQuery({
    queryKey: ['users', id],
    queryFn: async () => {
      const response = await fetch(`/api/users/${id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }
      return response.json();
    },
    enabled: !!id, // 只有在 id 存在时才查询
  });
};
```

### 3. 数据变更

```tsx
// hooks/useCreateUser.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';

interface CreateUserDto {
  name: string;
  email: string;
  role: string;
}

export const useCreateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (userData: CreateUserDto) => {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        throw new Error('Failed to create user');
      }

      return response.json();
    },

    onMutate: async (newUser) => {
      // 取消正在进行的查询
      await queryClient.cancelQueries({ queryKey: ['users'] });

      // 获取当前数据快照
      const previousUsers = queryClient.getQueryData(['users']);

      // 乐观更新
      queryClient.setQueryData(['users'], (old: any) => [
        ...(old || []),
        { ...newUser, id: 'temp-id', status: 'pending' },
      ]);

      return { previousUsers };
    },

    onError: (err, newUser, context) => {
      // 发生错误时回滚
      queryClient.setQueryData(['users'], context?.previousUsers);
    },

    onSettled: () => {
      // 无论成功失败都重新获取数据
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
};
```

### 4. 复杂查询

```tsx
// hooks/usePaginatedUsers.ts
import { useQuery } from '@tanstack/react-query';

interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

interface UsePaginatedUsersOptions {
  page: number;
  limit: number;
  search?: string;
}

export const usePaginatedUsers = ({ page, limit, search }: UsePaginatedUsersOptions) => {
  return useQuery({
    queryKey: ['users', { page, limit, search }],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
      });

      if (search) {
        params.append('search', search);
      }

      const response = await fetch(`/api/users?${params}`);
      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }
      return response.json();
    },
    keepPreviousData: true, // 保持之前的数据
  });
};
```

## 综合应用

### 1. 完整的电商应用状态管理

```tsx
// stores/index.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// 用户状态
interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        isAuthenticated: false,

        login: async (credentials) => {
          const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials),
          });

          if (!response.ok) {
            throw new Error('Login failed');
          }

          const userData = await response.json();
          set({ user: userData, isAuthenticated: true });
        },

        logout: () => {
          set({ user: null, isAuthenticated: false });
        },

        updateProfile: async (data) => {
          const response = await fetch('/api/user/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
          });

          if (!response.ok) {
            throw new Error('Profile update failed');
          }

          const updatedUser = await response.json();
          set({ user: updatedUser });
        },
      }),
      {
        name: 'user-storage',
      }
    )
  )
);

// 购物车状态
export const useCartStore = create<CartState>()(
  devtools(
    persist(
      (set, get) => ({
        items: [],
        total: 0,
        itemCount: 0,

        addItem: (item) => {
          const items = get().items;
          const existingItem = items.find(i => i.id === item.id);

          if (existingItem) {
            set({
              items: items.map(i =>
                i.id === item.id
                  ? { ...i, quantity: i.quantity + 1 }
                  : i
              ),
            });
          } else {
            set({
              items: [...items, { ...item, quantity: 1 }],
            });
          }

          get().updateTotals();
        },

        // ... 其他购物车方法
      }),
      {
        name: 'cart-storage',
      }
    )
  )
);

// API 状态
export const useProductsQuery = () => {
  return useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await fetch('/api/products');
      return response.json();
    },
  });
};

export const useCreateOrderMutation = () => {
  const queryClient = useQueryClient();
  const { items, clearCart } = useCartStore();

  return useMutation({
    mutationFn: async (orderData: CreateOrderDto) => {
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...orderData, items }),
      });

      if (!response.ok) {
        throw new Error('Order creation failed');
      }

      return response.json();
    },

    onSuccess: () => {
      clearCart();
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });
};
```

### 2. 使用状态管理的组件

```tsx
// components/ProductList.tsx
'use client';

import { useProductsQuery } from '../stores';
import { useCartStore } from '../stores';
import ProductCard from './ProductCard';

export default function ProductList() {
  const { data: products, isLoading, error } = useProductsQuery();
  const addItem = useCartStore((state) => state.addItem);

  if (isLoading) {
    return <div className="text-center py-8">加载中...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-600">加载失败: {error.message}</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {products?.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={() => addItem({
            id: product.id,
            name: product.name,
            price: product.price,
            image: product.image,
          })}
        />
      ))}
    </div>
  );
}
```

```tsx
// components/CartSummary.tsx
'use client';

import { useCartStore } from '../stores';
import Button from './Button';

export default function CartSummary() {
  const { items, total, itemCount, clearCart } = useCartStore();

  if (itemCount === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        购物车是空的
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold mb-4">购物车摘要</h2>

      <div className="space-y-2 mb-4">
        {items.map((item) => (
          <div key={item.id} className="flex justify-between items-center">
            <div>
              <span className="font-medium">{item.name}</span>
              <span className="text-gray-600 ml-2">x{item.quantity}</span>
            </div>
            <span className="font-medium">¥{(item.price * item.quantity).toFixed(2)}</span>
          </div>
        ))}
      </div>

      <div className="border-t pt-4">
        <div className="flex justify-between items-center mb-4">
          <span className="text-lg font-semibold">总计:</span>
          <span className="text-xl font-bold text-blue-600">¥{total.toFixed(2)}</span>
        </div>

        <div className="space-y-2">
          <Button variant="primary" className="w-full">
            结算
          </Button>
          <Button variant="outline" className="w-full" onClick={clearCart}>
            清空购物车
          </Button>
        </div>
      </div>
    </div>
  );
}
```

## 性能优化

### 1. 选择性订阅

```tsx
// Zustand 选择器
const userName = useUserStore((state) => state.user?.name);
const cartItemCount = useCartStore((state) => state.itemCount);

// Jotai 选择器
const userPreferences = useAtomValue(
  useMemo(
    () => atom(
      (get) => ({
        theme: get(userPreferencesAtom).theme,
        language: get(userPreferencesAtom).language,
      })
    ),
    []
  )
);
```

### 2. 查询优化

```tsx
// 使用 suspense 模式
const { data } = useQuery({
  queryKey: ['posts'],
  queryFn: fetchPosts,
  suspense: true,
});

// 预取数据
const prefetchPosts = async () => {
  await queryClient.prefetchQuery({
    queryKey: ['posts'],
    queryFn: fetchPosts,
    staleTime: 5 * 60 * 1000,
  });
};
```

### 3. 批量更新

```tsx
// Zustand 批量更新
const updateMultipleItems = (updates: Array<{ id: string; data: Partial<Item> }>) => {
  useCartStore.getState().items.forEach((item, index, array) => {
    const update = updates.find(u => u.id === item.id);
    if (update) {
      array[index] = { ...item, ...update.data };
    }
  });

  useCartStore.getState().updateTotals();
};
```

## 最佳实践

### 1. 状态架构原则

```tsx
// 1. 单一职责原则
const useUserStore = create<UserState>((set) => ({
  // 只处理用户相关的状态
}));

const useCartStore = create<CartState>((set) => ({
  // 只处理购物车相关的状态
}));

// 2. 最小化状态
const useThemeStore = create((set) => ({
  theme: 'light',
  setTheme: (theme) => set({ theme }),
}));

// 3. 分离客户端状态和服务端状态
// 客户端状态使用 Zustand/Jotai
// 服务端状态使用 TanStack Query
```

### 2. 错误处理

```tsx
// 全局错误边界
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>出现错误，请刷新页面重试</div>;
    }

    return this.props.children;
  }
}

// 查询错误处理
const { data, error, isLoading } = useQuery({
  queryKey: ['users'],
  queryFn: fetchUsers,
  retry: (failureCount, error) => {
    if (failureCount >= 3) return false;
    return error.message !== 'Unauthorized';
  },
});
```

### 3. 测试策略

```tsx
// Zustand store 测试
describe('useUserStore', () => {
  it('should login successfully', () => {
    const { result } = renderHook(() => useUserStore());

    act(() => {
      result.current.login({ id: '1', name: 'Test User', email: 'test@example.com' });
    });

    expect(result.current.user).toEqual({
      id: '1',
      name: 'Test User',
      email: 'test@example.com',
    });
    expect(result.current.isAuthenticated).toBe(true);
  });
});

// TanStack Query 测试
describe('useUsersQuery', () => {
  it('should fetch users successfully', async () => {
    const mockUsers = [
      { id: '1', name: 'User 1' },
      { id: '2', name: 'User 2' },
    ];

    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockUsers),
    });

    const { result, waitFor } = renderHook(() => useUsersQuery());

    await waitFor(() => result.current.isSuccess);

    expect(result.current.data).toEqual(mockUsers);
  });
});
```

## 下一步

掌握现代状态管理后，你可以继续学习：

1. **表单处理** - 学习 React Hook Form 和 Zod 验证
2. **数据获取** - 深入学习 TanStack Query 的高级特性
3. **测试策略** - 学习状态管理的测试方法
4. **项目实战** - 构建完整的状态管理应用

---

*现代状态管理是 React 应用的核心，掌握 Zustand、Jotai 和 TanStack Query 将帮助你构建高性能、可维护的前端应用。*