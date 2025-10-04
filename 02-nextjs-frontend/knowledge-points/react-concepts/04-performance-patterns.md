# React 性能模式

## 📚 概述

性能优化是 React 应用开发的关键环节。本指南涵盖了 React 19 的最新性能优化技术，包括并发特性、渲染优化、内存管理和最佳实践，帮助构建高性能的 React 应用。

## 🚀 React 19 并发特性

### startTransition
**标记非紧急更新，避免阻塞用户交互**

```typescript
import { startTransition, useState } from 'react';

function SearchApp() {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<string[]>([]);
  const [isPending, setIsPending] = useState(false);

  const handleSearch = (value: string) => {
    // 立即更新输入框
    setSearchTerm(value);

    // 标记搜索为非紧急更新
    startTransition(() => {
      setIsPending(true);
      const searchResults = performSearch(value);
      setResults(searchResults);
      setIsPending(false);
    });
  };

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search..."
      />
      {isPending && (
        <div className="search-indicator">Searching...</div>
      )}
      <SearchResults results={results} />
    </div>
  );
}

// 复杂的搜索逻辑
function performSearch(query: string): string[] {
  // 模拟耗时的搜索操作
  const allItems = Array.from({ length: 10000 }, (_, i) => `Item ${i}`);
  return allItems.filter(item =>
    item.toLowerCase().includes(query.toLowerCase())
  );
}
```

### useDeferredValue
**延迟更新非关键值**

```typescript
import { useDeferredValue, useMemo } from 'react';

function ProductList({ products }: { products: Product[] }) {
  const [searchTerm, setSearchTerm] = useState('');

  // 延迟搜索词，避免输入阻塞
  const deferredSearchTerm = useDeferredValue(searchTerm);

  // 基于延迟的搜索词进行过滤
  const filteredProducts = useMemo(() => {
    if (!deferredSearchTerm) return products;

    return products.filter(product =>
      product.name.toLowerCase().includes(deferredSearchTerm.toLowerCase())
    );
  }, [products, deferredSearchTerm]);

  const isStale = searchTerm !== deferredSearchTerm;

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search products..."
        className={isStale ? 'stale' : ''}
      />

      <div className={`product-list ${isStale ? 'stale' : ''}`}>
        {filteredProducts.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}
```

### useTransition Hook
**获取过渡状态，提供更好的用户反馈**

```typescript
function DataFilter() {
  const [filter, setFilter] = useState('all');
  const [data, setData] = useState<DataType[]>([]);
  const [isPending, startTransition] = useTransition();

  const handleFilterChange = (newFilter: string) => {
    startTransition(() => {
      setFilter(newFilter);
      // 模拟数据处理
      const filteredData = processData(newFilter);
      setData(filteredData);
    });
  };

  return (
    <div>
      <FilterButtons
        currentFilter={filter}
        onFilterChange={handleFilterChange}
        disabled={isPending}
      />

      {isPending && (
        <div className="loading-overlay">
          <Spinner />
          <p>Filtering data...</p>
        </div>
      )}

      <DataTable data={data} isTransitioning={isPending} />
    </div>
  );
}
```

## 🎯 渲染优化

### React.memo
**组件记忆化，避免不必要的重新渲染**

```typescript
// 基础用法
const TodoItem = React.memo(function TodoItem({
  todo,
  onToggle,
  onDelete
}: {
  todo: Todo;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  console.log(`Rendering TodoItem: ${todo.id}`);

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

// 自定义比较函数
const ExpensiveComponent = React.memo(function ExpensiveComponent({
  data,
  settings
}: {
  data: DataItem[];
  settings: Settings;
}) {
  // 复杂的渲染逻辑
  return <div>{/* 渲染内容 */}</div>;
}, (prevProps, nextProps) => {
  // 自定义比较逻辑
  return (
    prevProps.data.length === nextProps.data.length &&
    prevProps.settings.theme === nextProps.settings.theme &&
    JSON.stringify(prevProps.settings.filters) === JSON.stringify(nextProps.settings.filters)
  );
});
```

### useMemo
**缓存计算密集型操作的结果**

```typescript
function ExpensiveCalculation({ items, filter }: {
  items: ComplexItem[];
  filter: FilterOptions;
}) {
  // 缓存昂贵的计算
  const processedItems = useMemo(() => {
    console.log('Performing expensive calculation...');
    return items
      .filter(item => matchesFilter(item, filter))
      .map(item => ({
        ...item,
        computed: heavyComputation(item),
        formatted: formatData(item)
      }));
  }, [items, filter]);

  // 缓存排序结果
  const sortedItems = useMemo(() => {
    return [...processedItems].sort((a, b) =>
      compareItems(a, b, filter.sortBy)
    );
  }, [processedItems, filter.sortBy]);

  // 缓存聚合数据
  const statistics = useMemo(() => {
    return {
      total: sortedItems.length,
      average: calculateAverage(sortedItems),
      distribution: calculateDistribution(sortedItems)
    };
  }, [sortedItems]);

  return (
    <div>
      <Statistics stats={statistics} />
      <ItemList items={sortedItems} />
    </div>
  );
}

// 复杂的计算函数
function heavyComputation(item: ComplexItem): ComputedResult {
  // 模拟复杂的计算
  let result = item.data;
  for (let i = 0; i < 1000; i++) {
    result = process(result);
  }
  return result;
}
```

### useCallback
**缓存函数引用，避免子组件不必要的重新渲染**

```typescript
function TodoList({ todos, onToggle, onDelete }: {
  todos: Todo[];
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  const [filter, setFilter] = useState('all');

  // 缓存事件处理器
  const handleToggle = useCallback((id: string) => {
    onToggle(id);
  }, [onToggle]);

  const handleDelete = useCallback((id: string) => {
    onDelete(id);
  }, [onDelete]);

  const handleFilterChange = useCallback((newFilter: string) => {
    setFilter(newFilter);
  }, []);

  // 缓存过滤逻辑
  const filteredTodos = useMemo(() => {
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
  }, [todos, filter]);

  return (
    <div>
      <FilterControls
        currentFilter={filter}
        onFilterChange={handleFilterChange}
      />
      <ul>
        {filteredTodos.map(todo => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={handleToggle}
            onDelete={handleDelete}
          />
        ))}
      </ul>
    </div>
  );
}

// 父组件中使用
function TodoApp() {
  const [todos, setTodos] = useState<Todo[]>([]);

  const handleToggle = useCallback((id: string) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  }, []);

  const handleDelete = useCallback((id: string) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  }, []);

  return <TodoList todos={todos} onToggle={handleToggle} onDelete={handleDelete} />;
}
```

## 🏗️ 组件架构优化

### 组件拆分模式
**将大组件拆分为更小的、可复用的组件**

```typescript
// ❌ 避免大型组件
function BadUserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [followers, setFollowers] = useState([]);
  const [loading, setLoading] = useState(true);

  // 大量逻辑混合在一起...
  useEffect(() => {
    // 获取用户数据
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(setUser);

    // 获取用户帖子
    fetch(`/api/users/${userId}/posts`)
      .then(res => res.json())
      .then(setPosts);

    // 获取关注者
    fetch(`/api/users/${userId}/followers`)
      .then(res => res.json())
      .then(setFollowers);
  }, [userId]);

  return (
    <div>
      {/* 复杂的渲染逻辑 */}
    </div>
  );
}

// ✅ 良好的组件拆分
function UserProfile({ userId }: { userId: string }) {
  return (
    <div className="user-profile">
      <UserInfo userId={userId} />
      <UserPosts userId={userId} />
      <UserFollowers userId={userId} />
    </div>
  );
}

function UserInfo({ userId }: { userId: string }) {
  const { data: user, loading } = useUser(userId);

  if (loading) return <UserInfoSkeleton />;
  if (!user) return <div>User not found</div>;

  return (
    <div className="user-info">
      <Avatar src={user.avatar} alt={user.name} />
      <div>
        <h2>{user.name}</h2>
        <p>{user.bio}</p>
        <UserStats stats={user.stats} />
      </div>
    </div>
  );
}

function UserPosts({ userId }: { userId: string }) {
  const { data: posts, loading, error } = useUserPosts(userId);

  if (loading) return <PostsSkeleton />;
  if (error) return <div>Failed to load posts</div>;

  return (
    <div className="user-posts">
      <h3>Posts</h3>
      <PostList posts={posts} />
    </div>
  );
}
```

### 虚拟化长列表
**使用 react-window 或 react-virtualized**

```typescript
import { FixedSizeList as List } from 'react-window';

interface VirtualizedListProps {
  items: any[];
  itemHeight: number;
  height: number;
}

function VirtualizedList({ items, itemHeight, height }: VirtualizedListProps) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <ListItem item={items[index]} />
    </div>
  );

  return (
    <List
      height={height}
      itemCount={items.length}
      itemSize={itemHeight}
      width="100%"
    >
      {Row}
    </List>
  );
}

// 更复杂的虚拟化示例
import { VariableSizeList as List } from 'react-window';

function VariableHeightList({ items }: { items: ComplexItem[] }) {
  const listRef = useRef<List>(null);

  const getItemSize = useCallback((index: number) => {
    return items[index].estimatedHeight || 100;
  }, [items]);

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <ComplexListItem item={items[index]} />
    </div>
  );

  // 当项目大小更新时重新计算
  const handleItemResize = useCallback((index: number, newSize: number) => {
    items[index].estimatedHeight = newSize;
    listRef.current?.resetAfterIndex(index);
  }, [items]);

  return (
    <List
      ref={listRef}
      height={600}
      itemCount={items.length}
      itemSize={getItemSize}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

## 🔄 数据获取优化

### 智能数据获取
**避免重复请求和过度获取**

```typescript
// 使用 SWR 或 TanStack Query 进行数据获取
function useUserProfile(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const response = await fetch(`/api/users/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user');
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5分钟内不重新获取
    cacheTime: 10 * 60 * 1000, // 10分钟缓存时间
    refetchOnWindowFocus: false, // 窗口聚焦时不重新获取
    enabled: !!userId, // 只有当 userId 存在时才获取
  });
}

// 预加载数据
function usePrefetchUsers() {
  const queryClient = useQueryClient();

  return useCallback((userIds: string[]) => {
    userIds.forEach(userId => {
      queryClient.prefetchQuery({
        queryKey: ['user', userId],
        queryFn: () => fetch(`/api/users/${userId}`).then(res => res.json()),
        staleTime: 5 * 60 * 1000,
      });
    });
  }, [queryClient]);
}

// 分页数据获取
function usePaginatedData(page: number, pageSize: number) {
  return useQuery({
    queryKey: ['data', page, pageSize],
    queryFn: async () => {
      const response = await fetch(`/api/data?page=${page}&size=${pageSize}`);
      if (!response.ok) throw new Error('Failed to fetch data');
      return response.json();
    },
    keepPreviousData: true, // 保持上一页数据直到新数据加载完成
  });
}

// 无限滚动
function useInfiniteScroll() {
  return useInfiniteQuery({
    queryKey: ['infinite-data'],
    queryFn: async ({ pageParam = 0 }) => {
      const response = await fetch(`/api/data?page=${pageParam}`);
      if (!response.ok) throw new Error('Failed to fetch data');
      return response.json();
    },
    getNextPageParam: (lastPage, allPages) => {
      if (lastPage.hasMore) {
        return allPages.length;
      }
      return undefined;
    },
  });
}
```

### 乐观更新
**提供即时的用户反馈**

```typescript
function useOptimisticTodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Omit<Todo, 'id'>) => [
      ...state,
      { ...newTodo, id: `temp-${Date.now()}`, optimistic: true }
    ]
  );

  const addTodo = async (text: string) => {
    // 乐观添加
    addOptimisticTodo({ text, completed: false });

    try {
      // 实际添加
      const response = await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to add todo');
      }

      const newTodo = await response.json();
      setTodos(prev => [...prev, newTodo]);
    } catch (error) {
      // 移除乐观更新
      setTodos(prev => prev.filter(todo => !todo.optimistic));
      console.error('Add todo error:', error);
    }
  };

  return {
    todos: optimisticTodos,
    addTodo,
  };
}
```

## 🎨 样式和布局优化

### CSS-in-JS 优化
**减少样式计算开销**

```typescript
// 使用 styled-components 的样式缓存
import styled, { css } from 'styled-components';

// 缓存复杂样式
const expensiveStyle = css`
  ${() => {
    // 复杂的计算逻辑
    const theme = useTheme();
    const colors = generateColorPalette(theme);

    return css`
      background: linear-gradient(${colors.primary}, ${colors.secondary});
      box-shadow: 0 4px 6px ${colors.shadow};
      transition: all 0.3s ease;
    `;
  }}
`;

const StyledCard = styled.div`
  padding: 1rem;
  border-radius: 8px;
  ${expensiveStyle}
`;

// 使用 CSS 变量实现主题切换
const ThemeProvider = ({ children, theme }) => {
  const themeCSS = useMemo(() => {
    return Object.entries(theme)
      .map(([key, value]) => `--${key}: ${value};`)
      .join('\n');
  }, [theme]);

  return (
    <div style={{ css: themeCSS }}>
      {children}
    </div>
  );
};
```

### 布局优化
**减少重排和重绘**

```typescript
// 使用 CSS Grid 和 Flexbox 优化布局
function OptimizedGrid({ items }: { items: GridItem[] }) {
  return (
    <div className="grid-container">
      {items.map(item => (
        <GridItem key={item.id} item={item} />
      ))}
    </div>
  );
}

// CSS
/*
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  will-change: transform; // 提示浏览器优化
  contain: layout style paint; // 隔离样式和布局计算
}

.grid-item {
  contain: layout style paint;
  backface-visibility: hidden; // 优化动画性能
}
*/

// 使用 Intersection Observer 进行懒加载
function LazyImage({ src, alt, ...props }) {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={imgRef} className="lazy-image-container">
      {isIntersecting && (
        <img
          src={src}
          alt={alt}
          onLoad={() => setHasLoaded(true)}
          style={{ opacity: hasLoaded ? 1 : 0 }}
          {...props}
        />
      )}
      {!hasLoaded && <ImageSkeleton />}
    </div>
  );
}
```

## 🧠 内存优化

### 避免内存泄漏
**正确清理副作用**

```typescript
function DataComponent({ userId }: { userId: string }) {
  const [data, setData] = useState(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    // 创建新的 AbortController
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    const fetchData = async () => {
      try {
        const response = await fetch(`/api/users/${userId}`, {
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }

        const result = await response.json();
        setData(result);
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('Fetch error:', error);
        }
      }
    };

    fetchData();

    // 清理函数
    return () => {
      abortController.abort();
    };
  }, [userId]);

  // 组件卸载时的清理
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return <div>{/* 渲染数据 */}</div>;
}

// 定时器清理
function TimerComponent() {
  const [count, setCount] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setCount(prev => prev + 1);
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return <div>Count: {count}</div>;
}

// 事件监听器清理
function ResizeComponent() {
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div>
      Width: {dimensions.width}, Height: {dimensions.height}
    </div>
  );
}
```

### 大对象优化
**避免在组件状态中存储大对象**

```typescript
// ❌ 避免：在状态中存储大对象
function BadComponent() {
  const [largeData, setLargeData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch('/api/large-data');
      const data = await response.json(); // 可能是几MB的数据
      setLargeData(data);
    };

    fetchData();
  }, []);

  return <div>{/* 渲染大对象 */}</div>;
}

// ✅ 推荐：使用分页或虚拟化
function GoodComponent() {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 50;

  const { data: pageData, loading } = useQuery({
    queryKey: ['data', currentPage, pageSize],
    queryFn: async () => {
      const response = await fetch(
        `/api/data?page=${currentPage}&size=${pageSize}`
      );
      return response.json();
    },
  });

  return (
    <div>
      <DataList data={pageData} loading={loading} />
      <Pagination
        current={currentPage}
        onChange={setCurrentPage}
        pageSize={pageSize}
      />
    </div>
  );
}

// 使用 Web Workers 处理大数据
function useDataProcessor(data: any[]) {
  const [processedData, setProcessedData] = useState(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (!data) return;

    setProcessing(true);

    // 创建 Web Worker
    const worker = new Worker('/data-processor.js');

    worker.postMessage(data);

    worker.onmessage = (event) => {
      setProcessedData(event.data);
      setProcessing(false);
      worker.terminate();
    };

    worker.onerror = (error) => {
      console.error('Worker error:', error);
      setProcessing(false);
      worker.terminate();
    };

    return () => {
      worker.terminate();
    };
  }, [data]);

  return { processedData, processing };
}
```

## 📊 性能监控

### React DevTools Profiler
**识别性能瓶颈**

```typescript
// 使用 Profiler API 进行性能监控
import { Profiler } from 'react';

interface ProfileProps {
  id: string;
  onRender: (id: string, phase: string, actualDuration: number) => void;
  children: React.ReactNode;
}

function Profile({ id, onRender, children }: ProfileProps) {
  return (
    <Profiler
      id={id}
      onRender={(
        id,
        phase,
        actualDuration,
        baseDuration,
        startTime,
        commitTime
      ) => {
        onRender(id, phase, actualDuration);

        // 发送性能数据到分析服务
        if (actualDuration > 100) { // 超过100ms的渲染
          console.warn(`Slow render detected: ${id} took ${actualDuration}ms`);
        }
      }}
    >
      {children}
    </Profiler>
  );
}

// 使用示例
function App() {
  const handleRender = useCallback((id: string, phase: string, duration: number) => {
    // 记录性能数据
    analytics.track('component-render', {
      componentId: id,
      phase,
      duration,
    });
  }, []);

  return (
    <div>
      <Profile id="user-profile" onRender={handleRender}>
        <UserProfile />
      </Profile>

      <Profile id="todo-list" onRender={handleRender}>
        <TodoList />
      </Profile>
    </div>
  );
}
```

### 自定义性能 Hook
**监控组件性能**

```typescript
function useRenderTime(componentName: string) {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(Date.now());

  useEffect(() => {
    renderCount.current += 1;
    const now = Date.now();
    const renderTime = now - lastRenderTime.current;
    lastRenderTime.current = now;

    if (renderCount.current > 1) {
      console.log(
        `${componentName} rendered ${renderCount.current} times. ` +
        `Last render took ${renderTime}ms`
      );
    }

    // 如果渲染时间过长，发出警告
    if (renderTime > 50) {
      console.warn(
        `${componentName} slow render detected: ${renderTime}ms`
      );
    }
  });

  return {
    renderCount: renderCount.current,
    lastRenderTime: lastRenderTime.current,
  };
}

// 使用监控 Hook
function ExpensiveComponent({ data }: { data: any[] }) {
  useRenderTime('ExpensiveComponent');

  // 组件逻辑...
  return <div>{/* 渲染内容 */}</div>;
}
```

## 📋 最佳实践总结

### 渲染优化清单
- [ ] 使用 `React.memo` 包装纯组件
- [ ] 使用 `useMemo` 缓存昂贵计算
- [ ] 使用 `useCallback` 缓存事件处理器
- [ ] 合理拆分组件，避免过度渲染
- [ ] 使用虚拟化处理长列表
- [ ] 优化状态结构，避免深层嵌套

### 并发特性使用
- [ ] 使用 `startTransition` 标记非紧急更新
- [ ] 使用 `useDeferredValue` 延迟非关键值更新
- [ ] 使用 `useTransition` 提供加载状态
- [ ] 合理使用 Suspense 处理异步组件

### 内存管理
- [ ] 正确清理副作用（定时器、事件监听器）
- [ ] 取消组件卸载时的异步请求
- [ ] 避免在状态中存储大对象
- [ ] 使用分页或虚拟化处理大量数据

### 性能监控
- [ ] 使用 React DevTools Profiler 分析性能
- [ ] 监控组件渲染次数和耗时
- [ ] 设置性能预算和警告阈值
- [ ] 定期进行性能审查和优化

## 📖 总结

React 性能优化是一个持续的过程，需要结合应用的具体场景来选择合适的优化策略。React 19 的并发特性为我们提供了更强大的工具来构建高性能的应用。

记住优化的黄金法则：**先测量，再优化**。不要过早优化，但要在性能问题出现时及时识别和解决。

通过合理使用这些模式和最佳实践，你可以构建出响应迅速、用户体验优秀的 React 应用。