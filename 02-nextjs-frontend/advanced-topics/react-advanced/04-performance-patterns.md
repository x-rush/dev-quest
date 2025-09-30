# React 19 性能模式与优化策略

## 📋 概述

React 19 引入了强大的性能优化机制，但要让应用达到最佳性能，开发者需要理解并正确应用各种性能模式。本文将深入探讨React 19的性能模式，帮助开发者构建高性能的现代Web应用。

## 🎯 性能基础概念

### 1. 渲染性能原理

```typescript
// React渲染过程示例
function Component() {
  // 1. 状态和props确定
  const [count, setCount] = useState(0);

  // 2. 计算渲染
  const doubled = count * 2;

  // 3. 生成虚拟DOM
  return (
    <div>
      <p>Count: {count}</p>
      <p>Doubled: {doubled}</p>
    </div>
  );
}

// 渲染生命周期
const renderPipeline = {
  // 状态更新触发重新渲染
  stateUpdate: () => {
    // 计算新状态
    // 执行副作用
    // 重新渲染组件
  },

  // 虚拟DOM比对
  reconciliation: () => {
    // 比对新旧虚拟DOM
    // 生成更新操作
    // 应用到真实DOM
  }
};
```

### 2. 性能监控工具

```typescript
// React Profiler使用
function PerformanceProfiler({ children }: { children: React.ReactNode }) {
  const [metrics, setMetrics] = useState<Record<string, any>>({});

  const handleRender = (
    id: string,
    phase: string,
    actualDuration: number,
    baseDuration: number,
    startTime: number,
    commitTime: number,
    interactions: any[]
  ) => {
    setMetrics(prev => ({
      ...prev,
      [id]: {
        ...prev[id],
        [phase]: {
          actualDuration,
          baseDuration,
          renderTime: actualDuration - baseDuration
        }
      }
    }));
  };

  return (
    <React.Profiler id="app" onRender={handleRender}>
      {children}
    </React.Profiler>
  );
}

// 自定义性能Hook
function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState({
    renderCount: 0,
    totalTime: 0,
    lastRenderTime: 0
  });

  const trackRender = useCallback(() => {
    const startTime = performance.now();

    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      setMetrics(prev => ({
        renderCount: prev.renderCount + 1,
        totalTime: prev.totalTime + renderTime,
        lastRenderTime: renderTime
      }));
    };
  }, []);

  return { ...metrics, trackRender };
}
```

## 🚀 组件优化模式

### 1. React.memo 优化

```typescript
// 基础memo使用
const ExpensiveComponent = React.memo(function ExpensiveComponent({ data }: {
  data: any;
}) {
  // 昂贵的计算
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      processed: true,
      timestamp: Date.now()
    }));
  }, [data]);

  return (
    <div>
      {processedData.map(item => (
        <Item key={item.id} item={item} />
      ))}
    </div>
  );
});

// 自定义比较函数
const areEqual = (prevProps: any, nextProps: any) => {
  return (
    prevProps.id === nextProps.id &&
    prevProps.data.length === nextProps.data.length &&
    prevProps.data.every((item: any, index: number) =>
      item.id === nextProps.data[index]?.id
    )
  );
};

const OptimizedComponent = React.memo(Component, areEqual);
```

### 2. 组件分割策略

```typescript
// 大型组件分割
function LargeComponent({ data }: { data: any[] }) {
  return (
    <div className="large-component">
      <HeaderSection />
      <ContentSection data={data} />
      <FooterSection />
    </div>
  );
}

// 分割后的子组件
const HeaderSection = React.memo(function HeaderSection() {
  return (
    <header>
      <Logo />
      <Navigation />
    </header>
  );
});

const ContentSection = React.memo(function ContentSection({ data }: { data: any[] }) {
  return (
    <main>
      {data.map(item => (
        <ContentItem key={item.id} item={item} />
      ))}
    </main>
  );
});

const FooterSection = React.memo(function FooterSection() {
  return (
    <footer>
      <Copyright />
      <Links />
    </footer>
  );
});
```

### 3. 条件渲染优化

```typescript
// 避免在render中创建新函数
function Component() {
  const [isVisible, setIsVisible] = useState(false);

  // ❌ 每次渲染都创建新函数
  const handleClick = () => {
    setIsVisible(!isVisible);
  };

  // ✅ 使用useCallback
  const optimizedHandleClick = useCallback(() => {
    setIsVisible(prev => !prev);
  }, []);

  return (
    <div>
      <button onClick={optimizedHandleClick}>
        Toggle
      </button>
      {isVisible && <ExpensiveComponent />}
    </div>
  );
}

// 使用React.lazy进行代码分割
const LazyComponent = React.lazy(() => import('./LazyComponent'));

function App() {
  const [showComponent, setShowComponent] = useState(false);

  return (
    <div>
      <button onClick={() => setShowComponent(true)}>
        Load Component
      </button>
      {showComponent && (
        <Suspense fallback={<div>Loading...</div>}>
          <LazyComponent />
        </Suspense>
      )}
    </div>
  );
}
```

## 🎨 状态优化模式

### 1. 状态管理优化

```typescript
// 避免不必要的状态提升
function ParentComponent() {
  // ❌ 将子组件的状态提升到父组件
  const [childState, setChildState] = useState('');

  return (
    <div>
      <ChildComponent state={childState} onChange={setChildState} />
      <OtherComponent />
    </div>
  );
}

// ✅ 让子组件管理自己的状态
function OptimizedParentComponent() {
  return (
    <div>
      <SelfManagedChildComponent />
      <OtherComponent />
    </div>
  );
}

function SelfManagedChildComponent() {
  const [state, setState] = useState('');

  return (
    <input
      value={state}
      onChange={(e) => setState(e.target.value)}
    />
  );
}
```

### 2. 状态归一化

```typescript
// 归一化状态结构
interface NormalizedState {
  entities: {
    users: Record<string, User>;
    posts: Record<string, Post>;
  };
  ids: {
    users: string[];
    posts: string[];
  };
}

function useNormalizedState() {
  const [state, setState] = useState<NormalizedState>({
    entities: { users: {}, posts: {} },
    ids: { users: [], posts: [] }
  });

  const addUser = (user: User) => {
    setState(prev => ({
      entities: {
        ...prev.entities,
        users: { ...prev.entities.users, [user.id]: user }
      },
      ids: {
        ...prev.ids,
        users: [...prev.ids.users, user.id]
      }
    }));
  };

  const updateUser = (id: string, updates: Partial<User>) => {
    setState(prev => ({
      ...prev,
      entities: {
        ...prev.entities,
        users: {
          ...prev.entities.users,
          [id]: { ...prev.entities.users[id], ...updates }
        }
      }
    }));
  };

  return { state, addUser, updateUser };
}
```

### 3. 状态派生优化

```typescript
// 使用useMemo优化派生状态
function OptimizedComponent({ items }: { items: any[] }) {
  const [filter, setFilter] = useState('');
  const [sortBy, setSortBy] = useState('name');

  // 优化过滤和排序
  const filteredAndSortedItems = useMemo(() => {
    let filtered = items.filter(item =>
      item.name.toLowerCase().includes(filter.toLowerCase())
    );

    return filtered.sort((a, b) => {
      if (sortBy === 'name') {
        return a.name.localeCompare(b.name);
      }
      return a.id - b.id;
    });
  }, [items, filter, sortBy]);

  return (
    <div>
      <input
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter items..."
      />
      <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
        <option value="name">Sort by Name</option>
        <option value="id">Sort by ID</option>
      </select>
      <ItemList items={filteredAndSortedItems} />
    </div>
  );
}
```

## 🔄 数据获取优化

### 1. 并发数据获取

```typescript
// 使用Promise.all并行获取数据
function useParallelData(urls: string[]) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Error[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setErrors([]);

      try {
        const results = await Promise.allSettled(
          urls.map(url => fetch(url).then(res => res.json()))
        );

        const successfulData = results
          .filter((result): result is PromiseFulfilledResult<any> =>
            result.status === 'fulfilled'
          )
          .map(result => result.value);

        const failedResults = results
          .filter((result): result is PromiseRejectedResult =>
            result.status === 'rejected'
          )
          .map(result => result.reason);

        setData(successfulData);
        setErrors(failedResults);
      } catch (error) {
        setErrors([error as Error]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [urls]);

  return { data, loading, errors };
}
```

### 2. 数据缓存策略

```typescript
// 简单缓存实现
class DataCache {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private maxAge = 5 * 60 * 1000; // 5分钟

  async get<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
    const cached = this.cache.get(key);

    if (cached && Date.now() - cached.timestamp < this.maxAge) {
      return cached.data;
    }

    const data = await fetcher();
    this.cache.set(key, { data, timestamp: Date.now() });

    return data;
  }

  invalidate(key: string) {
    this.cache.delete(key);
  }

  clear() {
    this.cache.clear();
  }
}

const dataCache = new DataCache();

// 使用缓存Hook
function useCachedData<T>(key: string, fetcher: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await dataCache.get(key, fetcher);
        setData(result);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [key, fetcher]);

  return { data, loading, error };
}
```

### 3. 数据预取

```typescript
// 预取Hook
function usePrefetch(url: string) {
  const prefetch = useCallback(() => {
    // 使用低优先级获取数据
    if ('requestIdleCallback' in window) {
      window.requestIdleCallback(() => {
        fetch(url);
      });
    } else {
      // 回退方案
      setTimeout(() => {
        fetch(url);
      }, 1000);
    }
  }, [url]);

  return prefetch;
}

// 在组件中使用
function LinkWithPrefetch({ href, children }: {
  href: string;
  children: React.ReactNode;
}) {
  const prefetch = usePrefetch(href);

  return (
    <a
      href={href}
      onMouseEnter={prefetch}
      onFocus={prefetch}
    >
      {children}
    </a>
  );
}
```

## 🎨 渲染优化策略

### 1. 虚拟化长列表

```typescript
// 虚拟列表实现
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
  const containerRef = useRef<HTMLDivElement>(null);

  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length - 1
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
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

### 2. 窗口化渲染

```typescript
// 窗口化组件
function WindowedComponent({ items, windowHeight }: {
  items: any[];
  windowHeight: number;
}) {
  const [windowStart, setWindowStart] = useState(0);

  const visibleItems = items.slice(windowStart, windowStart + windowHeight);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const newWindowStart = Math.floor(scrollPosition / 100) * 10; // 每100px切换窗口
      setWindowStart(newWindowStart);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div>
      {visibleItems.map((item, index) => (
        <Item key={item.id} item={item} index={windowStart + index} />
      ))}
    </div>
  );
}
```

### 3. 渐进式渲染

```typescript
// 渐进式内容加载
function ProgressiveContent({ content }: { content: string[] }) {
  const [visibleCount, setVisibleCount] = useState(10);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setVisibleCount(prev => Math.min(prev + 10, content.length));
          }
        });
      },
      { threshold: 0.1 }
    );

    const sentinel = document.getElementById('sentinel');
    if (sentinel) {
      observer.observe(sentinel);
    }

    return () => observer.disconnect();
  }, [content.length]);

  return (
    <div>
      {content.slice(0, visibleCount).map((item, index) => (
        <p key={index}>{item}</p>
      ))}
      {visibleCount < content.length && (
        <div id="sentinel" style={{ height: '20px' }}>
          Loading more...
        </div>
      )}
    </div>
  );
}
```

## 🚨 性能监控与调试

### 1. 自定义性能监控

```typescript
// 性能监控Hook
function usePerformanceMonitoring(componentName: string) {
  useEffect(() => {
    const startTime = performance.now();

    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // 发送到分析服务
      console.log(`${componentName} render time: ${renderTime}ms`);

      // 如果渲染时间过长，发出警告
      if (renderTime > 100) {
        console.warn(`${componentName} took ${renderTime}ms to render`);
      }
    };
  }, [componentName]);
}

// 使用示例
function MonitoredComponent() {
  usePerformanceMonitoring('MonitoredComponent');

  return <div>Component content</div>;
}
```

### 2. 渲染计数器

```typescript
// 渲染计数器Hook
function useRenderCount(componentName: string) {
  const count = useRef(0);

  useEffect(() => {
    count.current += 1;
    console.log(`${componentName} rendered ${count.current} times`);
  });

  return count.current;
}

// 使用示例
function ComponentWithRenderCount() {
  const renderCount = useRenderCount('ComponentWithRenderCount');

  return (
    <div>
      <p>Rendered {renderCount} times</p>
    </div>
  );
}
```

## 🎯 总结

React 19 提供了强大的性能优化工具和模式，但关键在于理解何时以及如何使用它们。通过合理应用这些模式，可以显著提升应用的性能表现。

### 关键优化策略：

1. **组件优化**：使用React.memo、组件分割、条件渲染优化
2. **状态管理**：避免不必要的状态提升、状态归一化、派生状态优化
3. **数据获取**：并发获取、缓存策略、预取机制
4. **渲染优化**：虚拟化、窗口化、渐进式渲染
5. **监控调试**：性能监控、渲染计数、性能分析

### 最佳实践：

- **测量优先**：在优化前先测量性能瓶颈
- **渐进优化**：不要过度优化，关注真正影响用户体验的部分
- **保持可读性**：优化代码时保持代码的可维护性
- **测试验证**：确保优化不会引入新的bug

通过掌握这些性能模式，开发者可以构建出既高效又可维护的现代React应用。