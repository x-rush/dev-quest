# Gin缓存策略设计指南

本文档详细介绍Gin框架中的缓存策略设计，涵盖多级缓存、缓存模式、缓存优化等高级应用。

## 1. 缓存概述

### 1.1 缓存的重要性
- **性能提升**：减少数据库查询和计算开销
- **响应速度**：快速响应用户请求
- **资源节约**：降低后端服务负载
- **用户体验**：提供更流畅的用户交互
- **系统稳定性**：缓存机制提高系统抗压能力

### 1.2 缓存层次结构
```
客户端缓存 → CDN缓存 → 网关缓存 → 应用缓存 → 数据库缓存
    ↓            ↓           ↓           ↓           ↓
浏览器缓存    边缘缓存     内存缓存     分布式缓存   查询缓存
```

### 1.3 缓存策略类型
- **按位置**：客户端缓存、网关缓存、应用缓存、数据库缓存
- **按技术**：内存缓存、Redis缓存、Memcached缓存
- **按策略**：时间过期、容量淘汰、版本控制、事件通知

## 2. 多级缓存架构

### 2.1 三级缓存设计
```go
// 多级缓存接口
type MultiLevelCache struct {
    l1Cache *MemoryCache    // L1: 内存缓存 (本地缓存)
    l2Cache *RedisCache     // L2: 分布式缓存 (Redis)
    l3Cache *DatabaseCache  // L3: 数据库缓存
    stats   *CacheStats     // 缓存统计
    config  *CacheConfig    // 缓存配置
}

// 缓存配置
type CacheConfig struct {
    L1 struct {
        Enabled      bool          `yaml:"enabled"`
        Size         int           `yaml:"size"`
        TTL          time.Duration `yaml:"ttl"`
        CleanupFreq  time.Duration `yaml:"cleanup_freq"`
    } `yaml:"l1"`

    L2 struct {
        Enabled      bool          `yaml:"enabled"`
        Addresses    []string      `yaml:"addresses"`
        Password     string        `yaml:"password"`
        DB           int           `yaml:"db"`
        TTL          time.Duration `yaml:"ttl"`
        PoolSize     int           `yaml:"pool_size"`
    } `yaml:"l2"`

    L3 struct {
        Enabled      bool          `yaml:"enabled"`
        QueryCache   bool          `yaml:"query_cache"`
        TTL          time.Duration `yaml:"ttl"`
    } `yaml:"l3"`

    Strategy struct {
        ReadThrough  bool `yaml:"read_through"`
        WriteThrough bool `yaml:"write_through"`
        WriteBehind  bool `yaml:"write_behind"`
        RefreshAhead bool `yaml:"refresh_ahead"`
    } `yaml:"strategy"`
}

// 缓存统计
type CacheStats struct {
    Hits   int64 `json:"hits"`
    Misses int64 `json:"misses"`
    Errors int64 `json:"errors"`
    mu     sync.RWMutex
}

func (s *CacheStats) Hit() {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.Hits++
}

func (s *CacheStats) Miss() {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.Misses++
}

func (s *CacheStats) Error() {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.Errors++
}

func (s *CacheStats) HitRate() float64 {
    s.mu.RLock()
    defer s.mu.RUnlock()

    total := s.Hits + s.Misses
    if total == 0 {
        return 0
    }
    return float64(s.Hits) / float64(total) * 100
}
```

### 2.2 L1内存缓存实现
```go
// 内存缓存
type MemoryCache struct {
    items      map[string]*cacheItem
    mu         sync.RWMutex
    maxSize    int
    defaultTTL time.Duration
    cleanup    *time.Ticker
    done       chan struct{}
}

type cacheItem struct {
    value      interface{}
    expiration time.Time
    accessTime time.Time
    accessCount int64
}

func NewMemoryCache(maxSize int, defaultTTL time.Duration) *MemoryCache {
    cache := &MemoryCache{
        items:      make(map[string]*cacheItem),
        maxSize:    maxSize,
        defaultTTL: defaultTTL,
        cleanup:    time.NewTicker(time.Minute),
        done:       make(chan struct{}),
    }

    go cache.cleanupExpired()
    return cache
}

func (m *MemoryCache) Set(key string, value interface{}, ttl time.Duration) {
    if ttl == 0 {
        ttl = m.defaultTTL
    }

    m.mu.Lock()
    defer m.mu.Unlock()

    // 检查是否需要清理空间
    if len(m.items) >= m.maxSize {
        m.evictLRU()
    }

    m.items[key] = &cacheItem{
        value:      value,
        expiration: time.Now().Add(ttl),
        accessTime: time.Now(),
        accessCount: 1,
    }
}

func (m *MemoryCache) Get(key string) (interface{}, bool) {
    m.mu.RLock()
    defer m.mu.RUnlock()

    item, exists := m.items[key]
    if !exists {
        return nil, false
    }

    // 检查是否过期
    if time.Now().After(item.expiration) {
        return nil, false
    }

    // 更新访问信息
    item.accessTime = time.Now()
    item.accessCount++

    return item.value, true
}

func (m *MemoryCache) Delete(key string) {
    m.mu.Lock()
    defer m.mu.Unlock()

    delete(m.items, key)
}

func (m *MemoryCache) Clear() {
    m.mu.Lock()
    defer m.mu.Unlock()

    m.items = make(map[string]*cacheItem)
}

// LRU淘汰策略
func (m *MemoryCache) evictLRU() {
    var oldestKey string
    var oldestTime time.Time

    for key, item := range m.items {
        if oldestKey == "" || item.accessTime.Before(oldestTime) {
            oldestKey = key
            oldestTime = item.accessTime
        }
    }

    if oldestKey != "" {
        delete(m.items, oldestKey)
    }
}

// LFU淘汰策略
func (m *MemoryCache) evictLFU() {
    var leastUsedKey string
    var leastUsedCount int64

    for key, item := range m.items {
        if leastUsedKey == "" || item.accessCount < leastUsedCount {
            leastUsedKey = key
            leastUsedCount = item.accessCount
        }
    }

    if leastUsedKey != "" {
        delete(m.items, leastUsedKey)
    }
}

// 清理过期项目
func (m *MemoryCache) cleanupExpired() {
    for {
        select {
        case <-m.cleanup.C:
            m.mu.Lock()
            now := time.Now()
            for key, item := range m.items {
                if now.After(item.expiration) {
                    delete(m.items, key)
                }
            }
            m.mu.Unlock()
        case <-m.done:
            return
        }
    }
}

func (m *MemoryCache) Close() {
    m.cleanup.Stop()
    close(m.done)
}
```

### 2.3 L2 Redis缓存实现
```go
// Redis缓存
type RedisCache struct {
    client *redis.Client
    pool   *redis.Pool
    config *RedisConfig
}

type RedisConfig struct {
    Addresses    []string `yaml:"addresses"`
    Password     string   `yaml:"password"`
    DB           int      `yaml:"db"`
    PoolSize     int      `yaml:"pool_size"`
    MinIdleConns int      `yaml:"min_idle_conns"`
    MaxRetries   int      `yaml:"max_retries"`
}

func NewRedisCache(config *RedisConfig) *RedisCache {
    client := redis.NewClient(&redis.Options{
        Addr:         config.Addresses[0],
        Password:     config.Password,
        DB:           config.DB,
        PoolSize:     config.PoolSize,
        MinIdleConns: config.MinIdleConns,
        MaxRetries:   config.MaxRetries,
    })

    return &RedisCache{
        client: client,
        config: config,
    }
}

func (r *RedisCache) Set(key string, value interface{}, ttl time.Duration) error {
    serialized, err := serialize(value)
    if err != nil {
        return err
    }

    return r.client.Set(key, serialized, ttl).Err()
}

func (r *RedisCache) Get(key string) (interface{}, error) {
    val, err := r.client.Get(key).Result()
    if err == redis.Nil {
        return nil, nil
    }
    if err != nil {
        return nil, err
    }

    return deserialize(val)
}

func (r *RedisCache) Delete(key string) error {
    return r.client.Del(key).Err()
}

func (r *RedisCache) Exists(key string) (bool, error) {
    count, err := r.client.Exists(key).Result()
    return count > 0, err
}

func (r *RedisCache) TTL(key string) (time.Duration, error) {
    return r.client.TTL(key).Result()
}

// 批量操作
func (r *RedisCache) MGet(keys []string) ([]interface{}, error) {
    return r.client.MGet(keys...).Result()
}

func (r *RedisCache) MSet(kv map[string]interface{}, ttl time.Duration) error {
    pipe := r.client.Pipeline()

    for key, value := range kv {
        serialized, err := serialize(value)
        if err != nil {
            return err
        }
        pipe.Set(key, serialized, ttl)
    }

    _, err := pipe.Exec()
    return err
}

// 分布式锁
func (r *RedisCache) Lock(key string, ttl time.Duration) (bool, error) {
    return r.client.SetNX(key, "locked", ttl).Result()
}

func (r *RedisCache) Unlock(key string) error {
    return r.client.Del(key).Err()
}

// 序列化和反序列化
func serialize(value interface{}) (string, error) {
    data, err := json.Marshal(value)
    if err != nil {
        return "", err
    }
    return string(data), nil
}

func deserialize(data string) (interface{}, error) {
    var result interface{}
    err := json.Unmarshal([]byte(data), &result)
    return result, err
}
```

### 2.4 多级缓存核心实现
```go
// 多级缓存实现
func NewMultiLevelCache(config *CacheConfig) *MultiLevelCache {
    cache := &MultiLevelCache{
        stats:  &CacheStats{},
        config: config,
    }

    // 初始化各级缓存
    if config.L1.Enabled {
        cache.l1Cache = NewMemoryCache(config.L1.Size, config.L1.TTL)
    }

    if config.L2.Enabled {
        redisConfig := &RedisConfig{
            Addresses:    config.L2.Addresses,
            Password:     config.L2.Password,
            DB:           config.L2.DB,
            PoolSize:     config.L2.PoolSize,
            MinIdleConns: 10,
            MaxRetries:   3,
        }
        cache.l2Cache = NewRedisCache(redisConfig)
    }

    if config.L3.Enabled {
        cache.l3Cache = NewDatabaseCache(config.L3.TTL)
    }

    return cache
}

func (m *MultiLevelCache) Get(key string) (interface{}, error) {
    // L1缓存查找
    if m.config.L1.Enabled {
        if value, found := m.l1Cache.Get(key); found {
            m.stats.Hit()
            return value, nil
        }
    }

    // L2缓存查找
    if m.config.L2.Enabled {
        value, err := m.l2Cache.Get(key)
        if err == nil && value != nil {
            m.stats.Hit()
            // 回填L1缓存
            if m.config.L1.Enabled {
                m.l1Cache.Set(key, value, m.config.L1.TTL)
            }
            return value, nil
        }
        if err != nil {
            m.stats.Error()
            return nil, err
        }
    }

    // L3缓存查找
    if m.config.L3.Enabled {
        value, err := m.l3Cache.Get(key)
        if err == nil && value != nil {
            m.stats.Miss()
            // 回填L2和L1缓存
            if m.config.L2.Enabled {
                m.l2Cache.Set(key, value, m.config.L2.TTL)
            }
            if m.config.L1.Enabled {
                m.l1Cache.Set(key, value, m.config.L1.TTL)
            }
            return value, nil
        }
        if err != nil {
            m.stats.Error()
            return nil, err
        }
    }

    m.stats.Miss()
    return nil, nil
}

func (m *MultiLevelCache) Set(key string, value interface{}, ttl time.Duration) error {
    // 设置L1缓存
    if m.config.L1.Enabled {
        m.l1Cache.Set(key, value, m.config.L1.TTL)
    }

    // 设置L2缓存
    if m.config.L2.Enabled {
        if err := m.l2Cache.Set(key, value, m.config.L2.TTL); err != nil {
            return err
        }
    }

    // 设置L3缓存
    if m.config.L3.Enabled {
        if err := m.l3Cache.Set(key, value, ttl); err != nil {
            return err
        }
    }

    return nil
}

func (m *MultiLevelCache) Delete(key string) error {
    // 删除所有级别的缓存
    if m.config.L1.Enabled {
        m.l1Cache.Delete(key)
    }

    if m.config.L2.Enabled {
        if err := m.l2Cache.Delete(key); err != nil {
            return err
        }
    }

    if m.config.L3.Enabled {
        if err := m.l3Cache.Delete(key); err != nil {
            return err
        }
    }

    return nil
}

func (m *MultiLevelCache) GetStats() *CacheStats {
    return m.stats
}

func (m *MultiLevelCache) Clear() error {
    if m.config.L1.Enabled {
        m.l1Cache.Clear()
    }

    if m.config.L2.Enabled {
        // 清空Redis数据库
        if err := m.l2Cache.client.FlushDB().Err(); err != nil {
            return err
        }
    }

    if m.config.L3.Enabled {
        m.l3Cache.Clear()
    }

    return nil
}
```

## 3. 缓存模式

### 3.1 Cache-Aside模式
```go
// Cache-Aside模式实现
type CacheAside struct {
    cache    Cache
    database Database
}

func NewCacheAside(cache Cache, database Database) *CacheAside {
    return &CacheAside{
        cache:    cache,
        database: database,
    }
}

func (c *CacheAside) Get(key string) (interface{}, error) {
    // 先查缓存
    value, err := c.cache.Get(key)
    if err == nil && value != nil {
        return value, nil
    }

    // 缓存未命中，查询数据库
    value, err = c.database.Get(key)
    if err != nil {
        return nil, err
    }

    // 写入缓存
    if value != nil {
        c.cache.Set(key, value, time.Hour)
    }

    return value, nil
}

func (c *CacheAside) Set(key string, value interface{}) error {
    // 先写数据库
    if err := c.database.Set(key, value); err != nil {
        return err
    }

    // 再写缓存
    return c.cache.Set(key, value, time.Hour)
}

func (c *CacheAside) Delete(key string) error {
    // 先删数据库
    if err := c.database.Delete(key); err != nil {
        return err
    }

    // 再删缓存
    return c.cache.Delete(key)
}
```

### 3.2 Read-Through模式
```go
// Read-Through模式实现
type ReadThrough struct {
    cache    Cache
    database Database
}

func NewReadThrough(cache Cache, database Database) *ReadThrough {
    return &ReadThrough{
        cache:    cache,
        database: database,
    }
}

func (r *ReadThrough) Get(key string) (interface{}, error) {
    // 先查缓存
    value, err := r.cache.Get(key)
    if err == nil && value != nil {
        return value, nil
    }

    // 缓存未命中，查询数据库并缓存
    value, err = r.database.Get(key)
    if err != nil {
        return nil, err
    }

    // 自动写入缓存
    if value != nil {
        r.cache.Set(key, value, time.Hour)
    }

    return value, nil
}

func (r *ReadThrough) Set(key string, value interface{}) error {
    // 只更新数据库
    return r.database.Set(key, value)
}

func (r *ReadThrough) Delete(key string) error {
    // 只删除数据库
    return r.database.Delete(key)
}
```

### 3.3 Write-Through模式
```go
// Write-Through模式实现
type WriteThrough struct {
    cache    Cache
    database Database
}

func NewWriteThrough(cache Cache, database Database) *WriteThrough {
    return &WriteThrough{
        cache:    cache,
        database: database,
    }
}

func (w *WriteThrough) Get(key string) (interface{}, error) {
    // 只查缓存
    return w.cache.Get(key)
}

func (w *WriteThrough) Set(key string, value interface{}) error {
    // 先写缓存
    if err := w.cache.Set(key, value, time.Hour); err != nil {
        return err
    }

    // 同步写数据库
    return w.database.Set(key, value)
}

func (w *WriteThrough) Delete(key string) error {
    // 先删缓存
    if err := w.cache.Delete(key); err != nil {
        return err
    }

    // 同步删数据库
    return w.database.Delete(key)
}
```

### 3.4 Write-Behind模式
```go
// Write-Behind模式实现
type WriteBehind struct {
    cache      Cache
    database   Database
    writeQueue chan *WriteTask
    workers    []*WriteWorker
    config     *WriteBehindConfig
}

type WriteTask struct {
    Operation string      `json:"operation"`
    Key       string      `json:"key"`
    Value     interface{} `json:"value"`
    Timestamp time.Time   `json:"timestamp"`
}

type WriteBehindConfig struct {
    QueueSize    int           `yaml:"queue_size"`
    WorkerCount  int           `yaml:"worker_count"`
    BatchSize    int           `yaml:"batch_size"`
    FlushTimeout time.Duration `yaml:"flush_timeout"`
}

type WriteWorker struct {
    id         int
    database   Database
    writeQueue <-chan *WriteTask
    quit       chan struct{}
    config     *WriteBehindConfig
}

func NewWriteBehind(cache Cache, database Database, config *WriteBehindConfig) *WriteBehind {
    wb := &WriteBehind{
        cache:      cache,
        database:   database,
        writeQueue: make(chan *WriteTask, config.QueueSize),
        config:     config,
        workers:    make([]*WriteWorker, config.WorkerCount),
    }

    // 启动工作协程
    for i := 0; i < config.WorkerCount; i++ {
        worker := &WriteWorker{
            id:         i,
            database:   database,
            writeQueue: wb.writeQueue,
            quit:       make(chan struct{}),
            config:     config,
        }
        wb.workers = append(wb.workers, worker)
        go worker.Start()
    }

    return wb
}

func (w *WriteWorker) Start() {
    batch := make([]*WriteTask, 0, w.config.BatchSize)
    ticker := time.NewTicker(w.config.FlushTimeout)
    defer ticker.Stop()

    for {
        select {
        case task := <-w.writeQueue:
            batch = append(batch, task)
            if len(batch) >= w.config.BatchSize {
                w.flushBatch(batch)
                batch = batch[:0]
            }
        case <-ticker.C:
            if len(batch) > 0 {
                w.flushBatch(batch)
                batch = batch[:0]
            }
        case <-w.quit:
            if len(batch) > 0 {
                w.flushBatch(batch)
            }
            return
        }
    }
}

func (w *WriteWorker) flushBatch(batch []*WriteTask) {
    for _, task := range batch {
        switch task.Operation {
        case "set":
            w.database.Set(task.Key, task.Value)
        case "delete":
            w.database.Delete(task.Key)
        }
    }
}

func (w *WriteBehind) Get(key string) (interface{}, error) {
    return w.cache.Get(key)
}

func (w *WriteBehind) Set(key string, value interface{}) error {
    // 先写缓存
    if err := w.cache.Set(key, value, time.Hour); err != nil {
        return err
    }

    // 异步写入队列
    task := &WriteTask{
        Operation: "set",
        Key:       key,
        Value:     value,
        Timestamp: time.Now(),
    }

    select {
    case w.writeQueue <- task:
        return nil
    default:
        // 队列满，直接写入数据库
        return w.database.Set(key, value)
    }
}

func (w *WriteBehind) Delete(key string) error {
    // 先删缓存
    if err := w.cache.Delete(key); err != nil {
        return err
    }

    // 异步写入队列
    task := &WriteTask{
        Operation: "delete",
        Key:       key,
        Timestamp: time.Now(),
    }

    select {
    case w.writeQueue <- task:
        return nil
    default:
        // 队列满，直接删除数据库
        return w.database.Delete(key)
    }
}

func (w *WriteBehind) Close() {
    for _, worker := range w.workers {
        close(worker.quit)
    }
}
```

### 3.5 Refresh-Ahead模式
```go
// Refresh-Ahead模式实现
type RefreshAhead struct {
    cache         Cache
    database      Database
    refreshQueue  chan *RefreshTask
    workers       []*RefreshWorker
    config        *RefreshAheadConfig
    ttlCalculator func(key string) time.Duration
}

type RefreshTask struct {
    Key       string    `json:"key"`
    TTL       time.Duration `json:"ttl"`
    Timestamp time.Time `json:"timestamp"`
}

type RefreshAheadConfig struct {
    QueueSize       int           `yaml:"queue_size"`
    WorkerCount     int           `yaml:"worker_count"`
    RefreshInterval time.Duration `yaml:"refresh_interval"`
    EarlyRefresh    float64       `yaml:"early_refresh"` // 0.8 means refresh at 80% of TTL
}

type RefreshWorker struct {
    id            int
    cache         Cache
    database      Database
    refreshQueue  <-chan *RefreshTask
    quit          chan struct{}
    config        *RefreshAheadConfig
    ttlCalculator func(key string) time.Duration
}

func NewRefreshAhead(cache Cache, database Database, config *RefreshAheadConfig) *RefreshAhead {
    ra := &RefreshAhead{
        cache:         cache,
        database:      database,
        refreshQueue:  make(chan *RefreshTask, config.QueueSize),
        config:        config,
        ttlCalculator: func(key string) time.Duration { return time.Hour },
        workers:       make([]*RefreshWorker, config.WorkerCount),
    }

    // 启动工作协程
    for i := 0; i < config.WorkerCount; i++ {
        worker := &RefreshWorker{
            id:            i,
            cache:         cache,
            database:      database,
            refreshQueue:  ra.refreshQueue,
            quit:          make(chan struct{}),
            config:        config,
            ttlCalculator: ra.ttlCalculator,
        }
        ra.workers = append(ra.workers, worker)
        go worker.Start()
    }

    return ra
}

func (r *RefreshWorker) Start() {
    ticker := time.NewTicker(r.config.RefreshInterval)
    defer ticker.Stop()

    for {
        select {
        case task := <-r.refreshQueue:
            r.refreshKey(task.Key, task.TTL)
        case <-ticker.C:
            // 定期检查需要刷新的key
            r.checkAndRefresh()
        case <-r.quit:
            return
        }
    }
}

func (r *RefreshWorker) refreshKey(key string, ttl time.Duration) {
    // 从数据库获取最新数据
    value, err := r.database.Get(key)
    if err != nil {
        return
    }

    // 更新缓存
    if value != nil {
        r.cache.Set(key, value, ttl)
    }
}

func (r *RefreshWorker) checkAndRefresh() {
    // 这里需要实现检查即将过期的key的逻辑
    // 由于Gin缓存的限制，可能需要额外的过期时间跟踪
}

func (r *RefreshAhead) SetTTLCalculator(calculator func(key string) time.Duration) {
    r.ttlCalculator = calculator
}

func (r *RefreshAhead) Get(key string) (interface{}, error) {
    // 先查缓存
    value, err := r.cache.Get(key)
    if err == nil && value != nil {
        // 检查是否需要预刷新
        r.checkAndScheduleRefresh(key)
        return value, nil
    }

    // 缓存未命中，查询数据库
    value, err = r.database.Get(key)
    if err != nil {
        return nil, err
    }

    // 写入缓存
    if value != nil {
        ttl := r.ttlCalculator(key)
        r.cache.Set(key, value, ttl)
    }

    return value, nil
}

func (r *RefreshAhead) checkAndScheduleRefresh(key string) {
    // 检查是否需要预刷新
    ttl, err := r.cache.TTL(key)
    if err != nil {
        return
    }

    // 如果剩余时间小于总TTL的20%，则安排刷新
    totalTTL := r.ttlCalculator(key)
    refreshThreshold := time.Duration(float64(totalTTL) * (1.0 - r.config.EarlyRefresh))

    if ttl < refreshThreshold {
        task := &RefreshTask{
            Key:       key,
            TTL:       totalTTL,
            Timestamp: time.Now(),
        }

        select {
        case r.refreshQueue <- task:
        default:
            // 队列满，跳过刷新
        }
    }
}

func (r *RefreshAhead) Set(key string, value interface{}) error {
    ttl := r.ttlCalculator(key)
    return r.cache.Set(key, value, ttl)
}

func (r *RefreshAhead) Delete(key string) error {
    return r.cache.Delete(key)
}

func (r *RefreshAhead) Close() {
    for _, worker := range r.workers {
        close(worker.quit)
    }
}
```

## 4. Gin缓存中间件

### 4.1 基础缓存中间件
```go
// 缓存中间件
func CacheMiddleware(cache Cache, ttl time.Duration) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 只缓存GET请求
        if c.Request.Method != "GET" {
            c.Next()
            return
        }

        // 生成缓存key
        cacheKey := generateCacheKey(c)

        // 尝试从缓存获取
        if cached, found := cache.Get(cacheKey); found {
            // 解析缓存数据
            cachedData, ok := cached.(CachedResponse)
            if ok {
                c.Data(cachedData.Status, cachedData.ContentType, cachedData.Data)
                c.Abort()
                return
            }
        }

        // 记录响应
        writer := &cachedWriter{ResponseWriter: c.Writer}
        c.Writer = writer

        c.Next()

        // 缓存响应
        if c.Writer.Status() == 200 {
            cachedData := CachedResponse{
                Status:      c.Writer.Status(),
                ContentType: c.Writer.Header().Get("Content-Type"),
                Data:        writer.data,
            }

            cache.Set(cacheKey, cachedData, ttl)
        }
    }
}

// 缓存响应结构
type CachedResponse struct {
    Status      int         `json:"status"`
    ContentType string      `json:"content_type"`
    Data        []byte      `json:"data"`
}

// 缓存写入器
type cachedWriter struct {
    gin.ResponseWriter
    data []byte
}

func (w *cachedWriter) Write(data []byte) (int, error) {
    w.data = append(w.data, data...)
    return w.ResponseWriter.Write(data)
}

// 生成缓存key
func generateCacheKey(c *gin.Context) string {
    // 基础key：方法 + 路径
    key := fmt.Sprintf("%s:%s", c.Request.Method, c.Request.URL.Path)

    // 添加查询参数
    if c.Request.URL.RawQuery != "" {
        key += ":" + c.Request.URL.RawQuery
    }

    // 添加用户标识（如果需要）
    if userID := c.GetHeader("X-User-ID"); userID != "" {
        key += ":" + userID
    }

    // 添加语言标识（如果需要）
    if lang := c.GetHeader("Accept-Language"); lang != "" {
        key += ":" + lang
    }

    return key
}
```

### 4.2 高级缓存中间件
```go
// 高级缓存中间件
func AdvancedCacheMiddleware(cache Cache, config *CacheConfig) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查是否应该缓存
        if !shouldCache(c) {
            c.Next()
            return
        }

        // 生成缓存key
        cacheKey := generateAdvancedCacheKey(c)

        // 尝试从缓存获取
        if cached, found := cache.Get(cacheKey); found {
            handleCachedResponse(c, cached)
            return
        }

        // 缓存未命中，处理请求
        processRequest(c, cache, cacheKey, config)
    }
}

// 检查是否应该缓存
func shouldCache(c *gin.Context) bool {
    // 只缓存GET请求
    if c.Request.Method != "GET" {
        return false
    }

    // 检查不缓存的路由
    noCacheRoutes := []string{
        "/api/auth/",
        "/api/upload/",
        "/api/stream/",
    }

    for _, route := range noCacheRoutes {
        if strings.HasPrefix(c.Request.URL.Path, route) {
            return false
        }
    }

    // 检查请求头
    if c.GetHeader("Cache-Control") == "no-cache" {
        return false
    }

    if c.GetHeader("Authorization") != "" && isAuthRequired(c.Request.URL.Path) {
        return false
    }

    return true
}

// 生成高级缓存key
func generateAdvancedCacheKey(c *gin.Context) string {
    var builder strings.Builder

    // 基础信息
    builder.WriteString(c.Request.Method)
    builder.WriteString(":")
    builder.WriteString(c.Request.URL.Path)

    // 查询参数（排序后确保一致性）
    if len(c.Request.URL.Query()) > 0 {
        builder.WriteString(":")
        keys := make([]string, 0, len(c.Request.URL.Query()))
        for k := range c.Request.URL.Query() {
            keys = append(keys, k)
        }
        sort.Strings(keys)

        for _, k := range keys {
            builder.WriteString(k)
            builder.WriteString("=")
            builder.WriteString(c.Request.URL.Query().Get(k))
            builder.WriteString("&")
        }
    }

    // 用户上下文
    if userID := getUserID(c); userID != "" {
        builder.WriteString(":user:")
        builder.WriteString(userID)
    }

    // 租户信息
    if tenantID := getTenantID(c); tenantID != "" {
        builder.WriteString(":tenant:")
        builder.WriteString(tenantID)
    }

    // 版本信息
    if version := c.GetHeader("API-Version"); version != "" {
        builder.WriteString(":v:")
        builder.WriteString(version)
    }

    return builder.String()
}

// 处理缓存响应
func handleCachedResponse(c *gin.Context, cached interface{}) {
    cachedData, ok := cached.(*CachedResponseData)
    if !ok {
        c.Next()
        return
    }

    // 设置响应头
    for key, values := range cachedData.Headers {
        for _, value := range values {
            c.Header(key, value)
        }
    }

    // 设置缓存控制头
    c.Header("X-Cache", "HIT")
    c.Header("X-Cache-TTL", fmt.Sprintf("%.0f", cachedData.TTL.Seconds()))

    // 发送响应
    c.Data(cachedData.Status, cachedData.ContentType, cachedData.Data)
    c.Abort()
}

// 处理请求
func processRequest(c *gin.Context, cache Cache, cacheKey string, config *CacheConfig) {
    writer := &advancedResponseWriter{
        ResponseWriter: c.Writer,
        headers:       make(http.Header),
    }
    c.Writer = writer

    c.Next()

    // 检查是否应该缓存响应
    if shouldCacheResponse(c, writer) {
        cachedData := &CachedResponseData{
            Status:      writer.Status(),
            ContentType: writer.Header().Get("Content-Type"),
            Headers:     writer.headers,
            Data:        writer.data,
            TTL:         calculateTTL(c, config),
            CachedAt:    time.Now(),
        }

        // 异步写入缓存
        go func() {
            cache.Set(cacheKey, cachedData, cachedData.TTL)
        }()
    }

    // 设置缓存控制头
    c.Header("X-Cache", "MISS")
}

// 缓存响应数据结构
type CachedResponseData struct {
    Status      int           `json:"status"`
    ContentType string        `json:"content_type"`
    Headers     http.Header   `json:"headers"`
    Data        []byte        `json:"data"`
    TTL         time.Duration `json:"ttl"`
    CachedAt    time.Time     `json:"cached_at"`
}

// 高级响应写入器
type advancedResponseWriter struct {
    gin.ResponseWriter
    headers http.Header
    data    []byte
}

func (w *advancedResponseWriter) WriteHeader(code int) {
    w.ResponseWriter.WriteHeader(code)
}

func (w *advancedResponseWriter) Write(data []byte) (int, error) {
    w.data = append(w.data, data...)
    return w.ResponseWriter.Write(data)
}

func (w *advancedResponseWriter) Header() http.Header {
    return w.headers
}

// 检查是否应该缓存响应
func shouldCacheResponse(c *gin.Context, writer *advancedResponseWriter) bool {
    // 只缓存成功的响应
    if writer.Status() != 200 {
        return false
    }

    // 检查内容类型
    contentType := writer.Header().Get("Content-Type")
    cacheableTypes := []string{
        "application/json",
        "application/xml",
        "text/html",
        "text/plain",
    }

    for _, cacheableType := range cacheableTypes {
        if strings.Contains(contentType, cacheableType) {
            return true
        }
    }

    return false
}

// 计算TTL
func calculateTTL(c *gin.Context, config *CacheConfig) time.Duration {
    // 基于路径的TTL配置
    pathTTLs := map[string]time.Duration{
        "/api/public/":  time.Hour,
        "/api/products/": 30 * time.Minute,
        "/api/users/":    15 * time.Minute,
    }

    for path, ttl := range pathTTLs {
        if strings.HasPrefix(c.Request.URL.Path, path) {
            return ttl
        }
    }

    // 默认TTL
    return config.L2.TTL
}

// 辅助函数
func getUserID(c *gin.Context) string {
    if userID, exists := c.Get("user_id"); exists {
        return userID.(string)
    }
    return ""
}

func getTenantID(c *gin.Context) string {
    if tenantID, exists := c.Get("tenant_id"); exists {
        return tenantID.(string)
    }
    return ""
}

func isAuthRequired(path string) bool {
    authPaths := []string{
        "/api/users/profile",
        "/api/orders/",
        "/api/payments/",
    }

    for _, authPath := range authPaths {
        if strings.HasPrefix(path, authPath) {
            return true
        }
    }

    return false
}
```

### 4.3 缓存标签和批量失效
```go
// 缓存标签系统
type CacheTagManager struct {
    cache     Cache
    tagPrefix string
}

type CacheTag struct {
    Name      string   `json:"name"`
    Keys      []string `json:"keys"`
    Version   int64    `json:"version"`
    Timestamp time.Time `json:"timestamp"`
}

func NewCacheTagManager(cache Cache, tagPrefix string) *CacheTagManager {
    return &CacheTagManager{
        cache:     cache,
        tagPrefix: tagPrefix,
    }
}

func (m *CacheTagManager) SetWithTags(key string, value interface{}, ttl time.Duration, tags []string) error {
    // 设置缓存值
    if err := m.cache.Set(key, value, ttl); err != nil {
        return err
    }

    // 更新标签
    for _, tagName := range tags {
        if err := m.addKeyToTag(tagName, key); err != nil {
            return err
        }
    }

    return nil
}

func (m *CacheTagManager) InvalidateTag(tagName string) error {
    tagKey := m.getTagKey(tagName)

    // 获取标签
    tagData, err := m.cache.Get(tagKey)
    if err != nil {
        return err
    }

    if tagData == nil {
        return nil
    }

    tag, ok := tagData.(*CacheTag)
    if !ok {
        return nil
    }

    // 删除所有关联的缓存
    for _, key := range tag.Keys {
        m.cache.Delete(key)
    }

    // 更新标签版本
    tag.Version++
    tag.Timestamp = time.Now()
    return m.cache.Set(tagKey, tag, 24*time.Hour)
}

func (m *CacheTagManager) addKeyToTag(tagName, key string) error {
    tagKey := m.getTagKey(tagName)

    // 获取现有标签
    var tag *CacheTag
    if tagData, err := m.cache.Get(tagKey); err == nil && tagData != nil {
        tag = tagData.(*CacheTag)
    } else {
        tag = &CacheTag{
            Name:    tagName,
            Keys:    []string{},
            Version: 1,
        }
    }

    // 添加key到标签
    tag.Keys = append(tag.Keys, key)
    tag.Timestamp = time.Now()

    return m.cache.Set(tagKey, tag, 24*time.Hour)
}

func (m *CacheTagManager) getTagKey(tagName string) string {
    return fmt.Sprintf("%s:tag:%s", m.tagPrefix, tagName)
}

// 带标签的缓存中间件
func CacheWithTagMiddleware(cache Cache, tagManager *CacheTagManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        if !shouldCache(c) {
            c.Next()
            return
        }

        cacheKey := generateAdvancedCacheKey(c)

        // 检查缓存
        if cached, found := cache.Get(cacheKey); found {
            handleCachedResponse(c, cached)
            return
        }

        // 处理请求
        writer := &taggedResponseWriter{
            ResponseWriter: c.Writer,
            tags:           []string{},
        }
        c.Writer = writer

        c.Next()

        // 缓存响应
        if shouldCacheResponse(c, writer) && len(writer.tags) > 0 {
            cachedData := &CachedResponseData{
                Status:      writer.Status(),
                ContentType: writer.Header().Get("Content-Type"),
                Data:        writer.data,
                TTL:         time.Hour,
            }

            // 设置带标签的缓存
            tagManager.SetWithTags(cacheKey, cachedData, cachedData.TTL, writer.tags)
        }
    }
}

// 带标签的响应写入器
type taggedResponseWriter struct {
    gin.ResponseWriter
    tags []string
    data []byte
}

func (w *taggedResponseWriter) Write(data []byte) (int, error) {
    w.data = append(w.data, data...)
    return w.ResponseWriter.Write(data)
}

func (w *taggedResponseWriter) AddCacheTag(tags ...string) {
    w.tags = append(w.tags, tags...)
}

// 在控制器中使用
func GetProductHandler(c *gin.Context) {
    writer := c.Writer.(*taggedResponseWriter)

    // 添加缓存标签
    writer.AddCacheTag("products", "product:" + c.Param("id"))

    // 正常的业务逻辑
    product := getProductFromDB(c.Param("id"))
    c.JSON(200, product)
}

// 批量失效函数
func InvalidateProductTags(cache Cache, tagManager *CacheTagManager, productID string) {
    // 失效产品相关缓存
    tagManager.InvalidateTag("product:" + productID)
    tagManager.InvalidateTag("products")

    // 失效分类相关缓存
    tagManager.InvalidateTag("categories")
}
```

## 5. 缓存监控和统计

### 5.1 缓存监控中间件
```go
// 缓存监控中间件
func CacheMonitorMiddleware(cache Cache) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        cacheKey := generateAdvancedCacheKey(c)

        // 检查缓存
        cached, found := cache.Get(cacheKey)

        if found {
            // 缓存命中
            c.Header("X-Cache", "HIT")
            c.Header("X-Cache-Key", cacheKey)

            // 记录缓存命中统计
            recordCacheHit(c.Request.URL.Path)
        } else {
            // 缓存未命中
            c.Header("X-Cache", "MISS")

            // 记录缓存未命中统计
            recordCacheMiss(c.Request.URL.Path)
        }

        c.Next()

        // 记录请求处理时间
        duration := time.Since(start)
        recordRequestDuration(c.Request.URL.Path, duration)
    }
}

// 缓存统计管理器
type CacheStatsManager struct {
    hits         map[string]int64
    misses       map[string]int64
    errors       map[string]int64
    responseTime map[string][]time.Duration
    mu           sync.RWMutex
}

func NewCacheStatsManager() *CacheStatsManager {
    return &CacheStatsManager{
        hits:         make(map[string]int64),
        misses:       make(map[string]int64),
        errors:       make(map[string]int64),
        responseTime: make(map[string][]time.Duration),
    }
}

func (m *CacheStatsManager) RecordHit(path string) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.hits[path]++
}

func (m *CacheStatsManager) RecordMiss(path string) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.misses[path]++
}

func (m *CacheStatsManager) RecordError(path string) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.errors[path]++
}

func (m *CacheStatsManager) RecordResponseTime(path string, duration time.Duration) {
    m.mu.Lock()
    defer m.mu.Unlock()

    m.responseTime[path] = append(m.responseTime[path], duration)

    // 保持最近1000个记录
    if len(m.responseTime[path]) > 1000 {
        m.responseTime[path] = m.responseTime[path][1:]
    }
}

func (m *CacheStatsManager) GetStats(path string) CachePathStats {
    m.mu.RLock()
    defer m.mu.RUnlock()

    stats := CachePathStats{
        Path:  path,
        Hits:  m.hits[path],
        Misses: m.misses[path],
        Errors: m.errors[path],
    }

    total := stats.Hits + stats.Misses
    if total > 0 {
        stats.HitRate = float64(stats.Hits) / float64(total) * 100
    }

    // 计算平均响应时间
    if len(m.responseTime[path]) > 0 {
        var total time.Duration
        for _, duration := range m.responseTime[path] {
            total += duration
        }
        stats.AvgResponseTime = total / time.Duration(len(m.responseTime[path]))
    }

    return stats
}

func (m *CacheStatsManager) GetAllStats() []CachePathStats {
    m.mu.RLock()
    defer m.mu.RUnlock()

    allPaths := make(map[string]bool)
    for path := range m.hits {
        allPaths[path] = true
    }
    for path := range m.misses {
        allPaths[path] = true
    }
    for path := range m.errors {
        allPaths[path] = true
    }

    stats := make([]CachePathStats, 0, len(allPaths))
    for path := range allPaths {
        stats = append(stats, m.GetStats(path))
    }

    return stats
}

type CachePathStats struct {
    Path            string        `json:"path"`
    Hits            int64         `json:"hits"`
    Misses          int64         `json:"misses"`
    Errors          int64         `json:"errors"`
    HitRate         float64       `json:"hit_rate"`
    AvgResponseTime time.Duration `json:"avg_response_time"`
}

// 全局实例
var (
    cacheStatsManager = NewCacheStatsManager()
)

func recordCacheHit(path string) {
    cacheStatsManager.RecordHit(path)
}

func recordCacheMiss(path string) {
    cacheStatsManager.RecordMiss(path)
}

func recordRequestDuration(path string, duration time.Duration) {
    cacheStatsManager.RecordResponseTime(path, duration)
}

// 监控端点
func CacheStatsHandler(c *gin.Context) {
    path := c.Query("path")
    if path != "" {
        stats := cacheStatsManager.GetStats(path)
        c.JSON(200, stats)
        return
    }

    allStats := cacheStatsManager.GetAllStats()
    c.JSON(200, gin.H{
        "stats": allStats,
        "summary": gin.H{
            "total_hits":   getTotalHits(),
            "total_misses": getTotalMisses(),
            "overall_hit_rate": getOverallHitRate(),
        },
    })
}

func getTotalHits() int64 {
    var total int64
    for _, hits := range cacheStatsManager.hits {
        total += hits
    }
    return total
}

func getTotalMisses() int64 {
    var total int64
    for _, misses := range cacheStatsManager.misses {
        total += misses
    }
    return total
}

func getOverallHitRate() float64 {
    hits := getTotalHits()
    misses := getTotalMisses()
    total := hits + misses
    if total == 0 {
        return 0
    }
    return float64(hits) / float64(total) * 100
}
```

### 5.2 Prometheus监控
```go
// Prometheus缓存指标
type CacheMetrics struct {
    cacheHits       *prometheus.CounterVec
    cacheMisses     *prometheus.CounterVec
    cacheErrors     *prometheus.CounterVec
    cacheSize       *prometheus.GaugeVec
    cacheOperations *prometheus.CounterVec
    cacheDuration   *prometheus.HistogramVec
}

func NewCacheMetrics(namespace string) *CacheMetrics {
    return &CacheMetrics{
        cacheHits: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Namespace: namespace,
                Name:      "cache_hits_total",
                Help:      "Total number of cache hits",
            },
            []string{"path", "cache_level"},
        ),
        cacheMisses: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Namespace: namespace,
                Name:      "cache_misses_total",
                Help:      "Total number of cache misses",
            },
            []string{"path", "cache_level"},
        ),
        cacheErrors: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Namespace: namespace,
                Name:      "cache_errors_total",
                Help:      "Total number of cache errors",
            },
            []string{"path", "cache_level", "error_type"},
        ),
        cacheSize: prometheus.NewGaugeVec(
            prometheus.GaugeOpts{
                Namespace: namespace,
                Name:      "cache_size_bytes",
                Help:      "Current cache size in bytes",
            },
            []string{"cache_level"},
        ),
        cacheOperations: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Namespace: namespace,
                Name:      "cache_operations_total",
                Help:      "Total number of cache operations",
            },
            []string{"operation", "cache_level"},
        ),
        cacheDuration: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Namespace: namespace,
                Name:      "cache_operation_duration_seconds",
                Help:      "Cache operation duration in seconds",
                Buckets:   []float64{0.001, 0.01, 0.1, 1, 10},
            },
            []string{"operation", "cache_level"},
        ),
    }
}

func (m *CacheMetrics) Register() {
    prometheus.MustRegister(m.cacheHits)
    prometheus.MustRegister(m.cacheMisses)
    prometheus.MustRegister(m.cacheErrors)
    prometheus.MustRegister(m.cacheSize)
    prometheus.MustRegister(m.cacheOperations)
    prometheus.MustRegister(m.cacheDuration)
}

func (m *CacheMetrics) RecordHit(path, cacheLevel string) {
    m.cacheHits.WithLabelValues(path, cacheLevel).Inc()
}

func (m *CacheMetrics) RecordMiss(path, cacheLevel string) {
    m.cacheMisses.WithLabelValues(path, cacheLevel).Inc()
}

func (m *CacheMetrics) RecordError(path, cacheLevel, errorType string) {
    m.cacheErrors.WithLabelValues(path, cacheLevel, errorType).Inc()
}

func (m *CacheMetrics) RecordSize(cacheLevel string, size int64) {
    m.cacheSize.WithLabelValues(cacheLevel).Set(float64(size))
}

func (m *CacheMetrics) RecordOperation(operation, cacheLevel string) {
    m.cacheOperations.WithLabelValues(operation, cacheLevel).Inc()
}

func (m *CacheMetrics) RecordDuration(operation, cacheLevel string, duration time.Duration) {
    m.cacheDuration.WithLabelValues(operation, cacheLevel).Observe(duration.Seconds())
}

// 带监控的缓存包装器
type MonitoredCache struct {
    cache   Cache
    metrics *CacheMetrics
    level   string
}

func NewMonitoredCache(cache Cache, metrics *CacheMetrics, level string) *MonitoredCache {
    return &MonitoredCache{
        cache:   cache,
        metrics: metrics,
        level:   level,
    }
}

func (m *MonitoredCache) Get(key string) (interface{}, error) {
    start := time.Now()

    value, err := m.cache.Get(key)

    m.metrics.RecordDuration("get", m.level, time.Since(start))
    m.metrics.RecordOperation("get", m.level)

    if err != nil {
        m.metrics.RecordError("", m.level, "get_error")
        return nil, err
    }

    if value != nil {
        m.metrics.RecordHit("", m.level)
    } else {
        m.metrics.RecordMiss("", m.level)
    }

    return value, nil
}

func (m *MonitoredCache) Set(key string, value interface{}, ttl time.Duration) error {
    start := time.Now()

    err := m.cache.Set(key, value, ttl)

    m.metrics.RecordDuration("set", m.level, time.Since(start))
    m.metrics.RecordOperation("set", m.level)

    if err != nil {
        m.metrics.RecordError("", m.level, "set_error")
    }

    return err
}

func (m *MonitoredCache) Delete(key string) error {
    start := time.Now()

    err := m.cache.Delete(key)

    m.metrics.RecordDuration("delete", m.level, time.Since(start))
    m.metrics.RecordOperation("delete", m.level)

    if err != nil {
        m.metrics.RecordError("", m.level, "delete_error")
    }

    return err
}

func (m *MonitoredCache) Exists(key string) (bool, error) {
    start := time.Now()

    exists, err := m.cache.Exists(key)

    m.metrics.RecordDuration("exists", m.level, time.Since(start))
    m.metrics.RecordOperation("exists", m.level)

    if err != nil {
        m.metrics.RecordError("", m.level, "exists_error")
    }

    return exists, err
}

func (m *MonitoredCache) TTL(key string) (time.Duration, error) {
    start := time.Now()

    ttl, err := m.cache.TTL(key)

    m.metrics.RecordDuration("ttl", m.level, time.Since(start))
    m.metrics.RecordOperation("ttl", m.level)

    if err != nil {
        m.metrics.RecordError("", m.level, "ttl_error")
    }

    return ttl, err
}
```

## 6. 缓存优化策略

### 6.1 缓存预热
```go
// 缓存预热器
type CacheWarmer struct {
    cache        Cache
    database     Database
    warmupTasks  []WarmupTask
    concurrency int
    done         chan struct{}
}

type WarmupTask struct {
    Key     string        `json:"key"`
    Loader  func() (interface{}, error) `json:"-"`
    TTL     time.Duration `json:"ttl"`
    Tags    []string      `json:"tags"`
    Priority int          `json:"priority"`
}

func NewCacheWarmer(cache Cache, database Database, concurrency int) *CacheWarmer {
    return &CacheWarmer{
        cache:        cache,
        database:     database,
        concurrency: concurrency,
        done:         make(chan struct{}),
    }
}

func (w *CacheWarmer) AddTask(key string, loader func() (interface{}, error), ttl time.Duration, tags []string, priority int) {
    task := WarmupTask{
        Key:      key,
        Loader:   loader,
        TTL:      ttl,
        Tags:     tags,
        Priority: priority,
    }

    w.warmupTasks = append(w.warmupTasks, task)
}

func (w *CacheWarmer) Start() {
    // 按优先级排序
    sort.Slice(w.warmupTasks, func(i, j int) bool {
        return w.warmupTasks[i].Priority > w.warmupTasks[j].Priority
    })

    // 启动预热协程
    go w.warmup()
}

func (w *CacheWarmer) warmup() {
    semaphore := make(chan struct{}, w.concurrency)

    for _, task := range w.warmupTasks {
        select {
        case semaphore <- struct{}{}:
            go func(t WarmupTask) {
                defer func() { <-semaphore }()

                // 执行预热
                value, err := t.Loader()
                if err != nil {
                    log.Printf("Cache warmup failed for key %s: %v", t.Key, err)
                    return
                }

                // 设置缓存
                if err := w.cache.Set(t.Key, value, t.TTL); err != nil {
                    log.Printf("Cache set failed for key %s: %v", t.Key, err)
                }

                log.Printf("Cache warmup completed for key %s", t.Key)
            }(task)
        case <-w.done:
            return
        }
    }

    // 等待所有任务完成
    for i := 0; i < w.concurrency; i++ {
        semaphore <- struct{}{}
    }
}

func (w *CacheWarmer) Stop() {
    close(w.done)
}

// 预热示例
func setupCacheWarmup(cache Cache, database Database) {
    warmer := NewCacheWarmer(cache, database, 5)

    // 预热热门产品
    warmer.AddTask("products:popular", func() (interface{}, error) {
        return getPopularProducts(database)
    }, time.Hour, []string{"products", "popular"}, 10)

    // 预热分类数据
    warmer.AddTask("categories:all", func() (interface{}, error) {
        return getAllCategories(database)
    }, 2*time.Hour, []string{"categories"}, 8)

    // 预热用户设置
    warmer.AddTask("settings:global", func() (interface{}, error) {
        return getGlobalSettings(database)
    }, 24*time.Hour, []string{"settings"}, 5)

    warmer.Start()
}
```

### 6.2 缓存压缩
```go
// 缓存压缩器
type CacheCompressor struct {
    cache      Cache
    compressor CompressionInterface
    threshold  int64
}

type CompressionInterface interface {
    Compress(data []byte) ([]byte, error)
    Decompress(data []byte) ([]byte, error)
}

// Gzip压缩器
type GzipCompressor struct {
    level int
}

func NewGzipCompressor(level int) *GzipCompressor {
    return &GzipCompressor{level: level}
}

func (g *GzipCompressor) Compress(data []byte) ([]byte, error) {
    var buf bytes.Buffer
    writer := gzip.NewWriterLevel(&buf, g.level)
    if _, err := writer.Write(data); err != nil {
        return nil, err
    }
    if err := writer.Close(); err != nil {
        return nil, err
    }
    return buf.Bytes(), nil
}

func (g *GzipCompressor) Decompress(data []byte) ([]byte, error) {
    reader, err := gzip.NewReader(bytes.NewReader(data))
    if err != nil {
        return nil, err
    }
    defer reader.Close()

    return io.ReadAll(reader)
}

func NewCacheCompressor(cache Cache, compressor CompressionInterface, threshold int64) *CacheCompressor {
    return &CacheCompressor{
        cache:      cache,
        compressor: compressor,
        threshold:  threshold,
    }
}

func (c *CacheCompressor) Get(key string) (interface{}, error) {
    compressed, err := c.cache.Get(key)
    if err != nil {
        return nil, err
    }

    if compressed == nil {
        return nil, nil
    }

    compressedData, ok := compressed.([]byte)
    if !ok {
        return compressed, nil
    }

    return c.compressor.Decompress(compressedData)
}

func (c *CacheCompressor) Set(key string, value interface{}, ttl time.Duration) error {
    var data []byte

    switch v := value.(type) {
    case []byte:
        data = v
    case string:
        data = []byte(v)
    default:
        jsonData, err := json.Marshal(value)
        if err != nil {
            return err
        }
        data = jsonData
    }

    // 只有超过阈值的数据才压缩
    if int64(len(data)) > c.threshold {
        compressed, err := c.compressor.Compress(data)
        if err != nil {
            return err
        }
        data = compressed
    }

    return c.cache.Set(key, data, ttl)
}

func (c *CacheCompressor) Delete(key string) error {
    return c.cache.Delete(key)
}
```

### 6.3 缓存分片
```go
// 缓存分片器
type ShardedCache struct {
    shards    []*Shard
    hashFunc  func(string) uint32
    shardSize int
}

type Shard struct {
    cache  Cache
    locker sync.RWMutex
}

func NewShardedCache(shardSize int, cacheFactory func() Cache, hashFunc func(string) uint32) *ShardedCache {
    shards := make([]*Shard, shardSize)
    for i := 0; i < shardSize; i++ {
        shards[i] = &Shard{
            cache: cacheFactory(),
        }
    }

    return &ShardedCache{
        shards:    shards,
        hashFunc:  hashFunc,
        shardSize: shardSize,
    }
}

func (s *ShardedCache) getShard(key string) *Shard {
    hash := s.hashFunc(key)
    return s.shards[hash%uint32(s.shardSize)]
}

func (s *ShardedCache) Get(key string) (interface{}, error) {
    shard := s.getShard(key)
    shard.locker.RLock()
    defer shard.locker.RUnlock()

    return shard.cache.Get(key)
}

func (s *ShardedCache) Set(key string, value interface{}, ttl time.Duration) error {
    shard := s.getShard(key)
    shard.locker.Lock()
    defer shard.locker.Unlock()

    return shard.cache.Set(key, value, ttl)
}

func (s *ShardedCache) Delete(key string) error {
    shard := s.getShard(key)
    shard.locker.Lock()
    defer shard.locker.Unlock()

    return shard.cache.Delete(key)
}

// 默认哈希函数
func defaultHashFunc(key string) uint32 {
    hash := fnv.New32a()
    hash.Write([]byte(key))
    return hash.Sum32()
}

// 一致性哈希分片
type ConsistentHashShardedCache struct {
    shards    map[string]Cache
    ring      *consistenthash.Map
    replicas  int
}

func NewConsistentHashShardedCache(replicas int) *ConsistentHashShardedCache {
    return &ConsistentHashShardedCache{
        shards:   make(map[string]Cache),
        ring:     consistenthash.New(replicas, nil),
        replicas: replicas,
    }
}

func (c *ConsistentHashShardedCache) AddShard(shardID string, cache Cache) {
    c.shards[shardID] = cache
    c.ring.Add(shardID)
}

func (c *ConsistentHashShardedCache) GetShard(key string) Cache {
    shardID := c.ring.Get(key)
    return c.shards[shardID]
}

func (c *ConsistentHashShardedCache) Get(key string) (interface{}, error) {
    shard := c.GetShard(key)
    return shard.Get(key)
}

func (c *ConsistentHashShardedCache) Set(key string, value interface{}, ttl time.Duration) error {
    shard := c.GetShard(key)
    return shard.Set(key, value, ttl)
}

func (c *ConsistentHashShardedCache) Delete(key string) error {
    shard := c.GetShard(key)
    return shard.Delete(key)
}
```

## 7. 缓存配置管理

### 7.1 动态配置
```go
// 缓存配置管理器
type CacheConfigManager struct {
    config     *CacheConfig
    configPath string
    watchers   []chan *CacheConfig
    mu         sync.RWMutex
}

func NewCacheConfigManager(configPath string) *CacheConfigManager {
    return &CacheConfigManager{
        configPath: configPath,
        watchers:   make([]chan *CacheConfig, 0),
    }
}

func (m *CacheConfigManager) Load() error {
    m.mu.Lock()
    defer m.mu.Unlock()

    data, err := os.ReadFile(m.configPath)
    if err != nil {
        return err
    }

    config := &CacheConfig{}
    if err := yaml.Unmarshal(data, config); err != nil {
        return err
    }

    m.config = config
    return nil
}

func (m *CacheConfigManager) GetConfig() *CacheConfig {
    m.mu.RLock()
    defer m.mu.RUnlock()

    return m.config
}

func (m *CacheConfigManager) WatchConfig() (<-chan *CacheConfig, error) {
    m.mu.Lock()
    defer m.mu.Unlock()

    watcher := fsnotify.NewWatcher()
    if err := watcher.Add(m.configPath); err != nil {
        return nil, err
    }

    configChan := make(chan *CacheConfig, 1)
    m.watchers = append(m.watchers, configChan)

    go func() {
        for {
            select {
            case event, ok := <-watcher.Events:
                if !ok {
                    return
                }

                if event.Op&fsnotify.Write == fsnotify.Write {
                    if err := m.Load(); err == nil {
                        m.notifyWatchers()
                    }
                }

            case err, ok := <-watcher.Errors:
                if !ok {
                    return
                }
                log.Printf("Config watcher error: %v", err)
            }
        }
    }()

    return configChan, nil
}

func (m *CacheConfigManager) notifyWatchers() {
    m.mu.RLock()
    config := m.config
    watchers := make([]chan *CacheConfig, len(m.watchers))
    copy(watchers, m.watchers)
    m.mu.RUnlock()

    for _, watcher := range watchers {
        select {
        case watcher <- config:
        default:
            // 通道满，跳过通知
        }
    }
}

// 配置热更新
type HotReloadableCache struct {
    cache          Cache
    configManager  *CacheConfigManager
    configWatcher  <-chan *CacheConfig
    reloadFunc     func(*CacheConfig) error
}

func NewHotReloadableCache(cache Cache, configManager *CacheConfigManager, reloadFunc func(*CacheConfig) error) *HotReloadableCache {
    configWatcher, err := configManager.WatchConfig()
    if err != nil {
        panic(err)
    }

    return &HotReloadableCache{
        cache:         cache,
        configManager: configManager,
        configWatcher: configWatcher,
        reloadFunc:    reloadFunc,
    }
}

func (h *HotReloadableCache) Start() {
    go h.watchConfig()
}

func (h *HotReloadableCache) watchConfig() {
    for config := range h.configWatcher {
        if err := h.reloadFunc(config); err != nil {
            log.Printf("Failed to reload cache config: %v", err)
        } else {
            log.Printf("Cache config reloaded successfully")
        }
    }
}

func (h *HotReloadableCache) Get(key string) (interface{}, error) {
    return h.cache.Get(key)
}

func (h *HotReloadableCache) Set(key string, value interface{}, ttl time.Duration) error {
    return h.cache.Set(key, value, ttl)
}

func (h *HotReloadableCache) Delete(key string) error {
    return h.cache.Delete(key)
}
```

### 7.2 环境配置
```yaml
# cache-config.yaml
cache:
  # L1内存缓存配置
  l1:
    enabled: true
    size: 10000
    ttl: 5m
    cleanup_freq: 1m
    eviction_policy: "lru"  # lru, lfu, random

  # L2 Redis缓存配置
  l2:
    enabled: true
    addresses:
      - "redis://localhost:6379"
      - "redis://localhost:6380"
    password: ""
    db: 0
    pool_size: 100
    min_idle_conns: 10
    ttl: 30m
    compression:
      enabled: true
      threshold: 1024  # 1KB
      algorithm: "gzip"

  # L3数据库缓存配置
  l3:
    enabled: true
    query_cache: true
    ttl: 1h

  # 缓存策略配置
  strategy:
    read_through: true
    write_through: false
    write_behind:
      enabled: true
      queue_size: 10000
      worker_count: 5
      batch_size: 100
      flush_timeout: 5s
    refresh_ahead:
      enabled: true
      refresh_interval: 1m
      early_refresh: 0.8

  # 监控配置
  monitoring:
    enabled: true
    prometheus:
      namespace: "gin_cache"
    stats_interval: 10s

  # 预热配置
  warmup:
    enabled: true
    concurrency: 10
    tasks:
      - key: "config:global"
        ttl: 24h
        priority: 10
      - key: "products:featured"
        ttl: 1h
        priority: 8
```

## 8. 完整示例

### 8.1 缓存服务初始化
```go
package cache

import (
    "context"
    "log"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/gin-gonic/gin"
)

type CacheService struct {
    multiCache   *MultiLevelCache
    tagManager   *CacheTagManager
    config       *CacheConfig
    configMgr    *CacheConfigManager
    metrics      *CacheMetrics
    warmer       *CacheWarmer
}

func NewCacheService(configPath string) *CacheService {
    // 加载配置
    configMgr := NewCacheConfigManager(configPath)
    if err := configMgr.Load(); err != nil {
        log.Fatalf("Failed to load cache config: %v", err)
    }

    config := configMgr.GetConfig()

    // 初始化多级缓存
    multiCache := NewMultiLevelCache(config)

    // 初始化标签管理器
    tagManager := NewCacheTagManager(multiCache, "gin")

    // 初始化指标
    metrics := NewCacheMetrics("gin_cache")
    metrics.Register()

    // 初始化预热器
    warmer := NewCacheWarmer(multiCache, nil, 5)

    return &CacheService{
        multiCache: multiCache,
        tagManager: tagManager,
        config:     config,
        configMgr:  configMgr,
        metrics:    metrics,
        warmer:     warmer,
    }
}

func (s *CacheService) Start() error {
    // 启动配置监听
    configWatcher, err := s.configMgr.WatchConfig()
    if err != nil {
        return err
    }

    go func() {
        for newConfig := range configWatcher {
            s.reloadConfig(newConfig)
        }
    }()

    // 启动预热
    if s.config.Warmup.Enabled {
        s.setupWarmup()
        s.warmer.Start()
    }

    return nil
}

func (s *CacheService) reloadConfig(newConfig *CacheConfig) {
    s.config = newConfig
    log.Println("Cache configuration reloaded")
}

func (s *CacheService) setupWarmup() {
    // 添加预热任务
    s.warmer.AddTask("config:global", s.loadGlobalConfig, 24*time.Hour, []string{"config"}, 10)
    s.warmer.AddTask("products:featured", s.loadFeaturedProducts, time.Hour, []string{"products"}, 8)
    s.warmer.AddTask("categories:all", s.loadAllCategories, 2*time.Hour, []string{"categories"}, 6)
}

func (s *CacheService) loadGlobalConfig() (interface{}, error) {
    // 从数据库加载全局配置
    return map[string]interface{}{
        "site_name": "My App",
        "version":   "1.0.0",
        "maintenance": false,
    }, nil
}

func (s *CacheService) loadFeaturedProducts() (interface{}, error) {
    // 从数据库加载热门产品
    return []map[string]interface{}{
        {"id": 1, "name": "Product 1", "price": 100},
        {"id": 2, "name": "Product 2", "price": 200},
    }, nil
}

func (s *CacheService) loadAllCategories() (interface{}, error) {
    // 从数据库加载所有分类
    return []map[string]interface{}{
        {"id": 1, "name": "Category 1"},
        {"id": 2, "name": "Category 2"},
    }, nil
}

func (s *CacheService) Stop() {
    if s.warmer != nil {
        s.warmer.Stop()
    }
}

// Gin中间件
func (s *CacheService) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查是否启用缓存
        if !s.config.L1.Enabled && !s.config.L2.Enabled {
            c.Next()
            return
        }

        // 生成缓存key
        cacheKey := generateAdvancedCacheKey(c)

        // 尝试从缓存获取
        if cached, found := s.multiCache.Get(cacheKey); found {
            handleCachedResponse(c, cached)
            return
        }

        // 处理请求
        writer := &taggedResponseWriter{
            ResponseWriter: c.Writer,
            tags:           []string{},
        }
        c.Writer = writer

        c.Next()

        // 缓存响应
        if shouldCacheResponse(c, writer) && len(writer.tags) > 0 {
            cachedData := &CachedResponseData{
                Status:      writer.Status(),
                ContentType: writer.Header().Get("Content-Type"),
                Data:        writer.data,
                TTL:         calculateTTL(c, s.config),
            }

            // 异步设置缓存
            go func() {
                if err := s.tagManager.SetWithTags(cacheKey, cachedData, cachedData.TTL, writer.tags); err != nil {
                    log.Printf("Failed to cache response: %v", err)
                }
            }()
        }

        // 记录指标
        s.metrics.RecordOperation("request", "multi")
    }
}

// 标签辅助函数
func (s *CacheService) AddCacheTags(c *gin.Context, tags ...string) {
    if writer, ok := c.Writer.(*taggedResponseWriter); ok {
        writer.AddCacheTag(tags...)
    }
}

func (s *CacheService) InvalidateTags(tags ...string) {
    for _, tag := range tags {
        if err := s.tagManager.InvalidateTag(tag); err != nil {
            log.Printf("Failed to invalidate tag %s: %v", tag, err)
        }
    }
}

// 缓存操作接口
func (s *CacheService) Get(key string) (interface{}, error) {
    return s.multiCache.Get(key)
}

func (s *CacheService) Set(key string, value interface{}, ttl time.Duration) error {
    return s.multiCache.Set(key, value, ttl)
}

func (s *CacheService) Delete(key string) error {
    return s.multiCache.Delete(key)
}

func (s *CacheService) SetWithTags(key string, value interface{}, ttl time.Duration, tags []string) error {
    return s.tagManager.SetWithTags(key, value, ttl, tags)
}

func (s *CacheService) GetStats() []CachePathStats {
    return cacheStatsManager.GetAllStats()
}
```

### 8.2 在Gin应用中使用
```go
package main

import (
    "log"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "./cache"
)

var cacheService *cache.CacheService

func main() {
    // 初始化缓存服务
    cacheService = cache.NewCacheService("config/cache.yaml")
    if err := cacheService.Start(); err != nil {
        log.Fatalf("Failed to start cache service: %v", err)
    }
    defer cacheService.Stop()

    // 创建Gin引擎
    r := gin.New()

    // 中间件
    r.Use(gin.Logger())
    r.Use(gin.Recovery())
    r.Use(cacheService.Middleware())

    // 路由
    api := r.Group("/api")
    {
        products := api.Group("/products")
        {
            products.GET("", GetProducts)
            products.GET("/:id", GetProduct)
            products.POST("", CreateProduct)
            products.PUT("/:id", UpdateProduct)
            products.DELETE("/:id", DeleteProduct)
        }

        categories := api.Group("/categories")
        {
            categories.GET("", GetCategories)
            categories.GET("/:id", GetCategory)
        }
    }

    // 监控端点
    r.GET("/cache/stats", func(c *gin.Context) {
        stats := cacheService.GetStats()
        c.JSON(200, stats)
    })

    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "status": "healthy",
            "timestamp": time.Now().Unix(),
        })
    })

    // 启动服务器
    log.Println("Server starting on :8080")
    if err := r.Run(":8080"); err != nil {
        log.Fatalf("Failed to start server: %v", err)
    }
}

// 产品控制器
func GetProducts(c *gin.Context) {
    // 添加缓存标签
    cacheService.AddCacheTags(c, "products")

    // 模拟数据
    products := []map[string]interface{}{
        {"id": 1, "name": "Product 1", "price": 100},
        {"id": 2, "name": "Product 2", "price": 200},
    }

    c.JSON(200, products)
}

func GetProduct(c *gin.Context) {
    id := c.Param("id")

    // 添加缓存标签
    cacheService.AddCacheTags(c, "products", "product:"+id)

    // 模拟数据
    product := map[string]interface{}{
        "id":    id,
        "name":  "Product " + id,
        "price": 100,
    }

    c.JSON(200, product)
}

func CreateProduct(c *gin.Context) {
    var product struct {
        Name  string  `json:"name"`
        Price float64 `json:"price"`
    }

    if err := c.ShouldBindJSON(&product); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    // 失效相关缓存
    cacheService.InvalidateTags("products")

    c.JSON(201, gin.H{
        "id":      "3",
        "name":    product.Name,
        "price":   product.Price,
        "created": time.Now(),
    })
}

func UpdateProduct(c *gin.Context) {
    id := c.Param("id")

    var product struct {
        Name  string  `json:"name"`
        Price float64 `json:"price"`
    }

    if err := c.ShouldBindJSON(&product); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    // 失效相关缓存
    cacheService.InvalidateTags("products", "product:"+id)

    c.JSON(200, gin.H{
        "id":      id,
        "name":    product.Name,
        "price":   product.Price,
        "updated": time.Now(),
    })
}

func DeleteProduct(c *gin.Context) {
    id := c.Param("id")

    // 失效相关缓存
    cacheService.InvalidateTags("products", "product:"+id)

    c.JSON(200, gin.H{
        "message": "Product deleted",
        "id":      id,
    })
}

// 分类控制器
func GetCategories(c *gin.Context) {
    // 添加缓存标签
    cacheService.AddCacheTags(c, "categories")

    // 模拟数据
    categories := []map[string]interface{}{
        {"id": 1, "name": "Category 1"},
        {"id": 2, "name": "Category 2"},
    }

    c.JSON(200, categories)
}

func GetCategory(c *gin.Context) {
    id := c.Param("id")

    // 添加缓存标签
    cacheService.AddCacheTags(c, "categories", "category:"+id)

    // 模拟数据
    category := map[string]interface{}{
        "id":   id,
        "name": "Category " + id,
    }

    c.JSON(200, category)
}
```

## 9. 最佳实践

### 9.1 缓存设计原则
- **缓存分层**：合理设计多级缓存架构
- **TTL策略**：根据数据更新频率设置合适的TTL
- **缓存失效**：选择合适的失效策略和时间
- **监控指标**：建立完整的缓存监控体系
- **容量规划**：合理规划缓存容量和淘汰策略

### 9.2 性能优化建议
- **热点数据**：优先缓存热点数据
- **缓存预热**：系统启动时预热重要数据
- **压缩存储**：对大缓存值进行压缩
- **连接池**：合理使用连接池减少开销
- **异步处理**：异步处理缓存写入和刷新

### 9.3 运维建议
- **监控告警**：建立缓存命中率、容量等监控
- **日志分析**：记录缓存操作日志用于分析
- **配置管理**：支持动态配置调整
- **故障处理**：建立缓存故障的降级策略
- **定期维护**：定期清理过期数据和优化配置

---

这个Gin缓存策略设计指南提供了完整的缓存解决方案，涵盖多级缓存、缓存模式、缓存优化、监控统计等各个方面。通过这个指南，你可以构建一个高性能、高可用的缓存系统。