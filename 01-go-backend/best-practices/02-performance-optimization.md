# Go 性能优化最佳实践

## 📚 概述

Go语言以其出色的性能特性著称，但要充分发挥其性能优势，需要深入理解Go的运行机制和优化技巧。本指南将从PHP开发者的角度，详细介绍Go应用的性能优化策略。

### 🎯 学习目标
- 掌握Go内存管理和优化
- 学会并发性能优化
- 理解I/O和网络性能优化
- 掌握数据库查询优化
- 学会使用性能分析工具
- 理解Go与PHP性能差异的根本原因

## 🔄 Go vs PHP 性能对比

### 基础性能差异
```go
// Go: 编译型语言，直接运行机器码
func fibonacci(n int) int {
    if n <= 1 {
        return n
    }
    return fibonacci(n-1) + fibonacci(n-2)
}

// 编译后直接运行，无解释器开销
// 编译时优化，静态类型检查
```

```php
// PHP: 解释型语言，需要运行时解析
function fibonacci($n) {
    if ($n <= 1) {
        return $n;
    }
    return fibonacci($n - 1) + fibonacci($n - 2);
}

// 每次请求都需要解释执行
// 动态类型检查，运行时开销较大
```

### 内存管理差异
```go
// Go: 自动垃圾回收，编译时内存分配优化
func processData(data []byte) {
    // 栈分配（小对象）
    var buffer [1024]byte

    // 堆分配（大对象或逃逸分析）
    largeData := make([]byte, 1024*1024)

    // defer延迟释放
    defer func() {
        // 清理资源
    }()
}
```

```php
// PHP: 引用计数垃圾回收，运行时内存管理
function processData($data) {
    // 所有变量都是引用类型
    $buffer = str_repeat("x", 1024);
    $largeData = str_repeat("x", 1024 * 1024);

    // 依赖GC自动回收
}
```

## 📝 内存优化

### 1. 内存分配优化

#### 减少堆分配
```go
// 优化前：频繁的内存分配
func concatenateStrings(strings []string) string {
    result := ""
    for _, s := range strings {
        result += s // 每次都分配新内存
    }
    return result
}

// 优化后：预分配内存
func concatenateStringsOptimized(strings []string) string {
    // 计算总长度
    totalLen := 0
    for _, s := range strings {
        totalLen += len(s)
    }

    // 预分配足够空间
    builder := strings.Builder{}
    builder.Grow(totalLen)

    for _, s := range strings {
        builder.WriteString(s)
    }

    return builder.String()
}
```

#### 对象池模式
```go
package pool

import "sync"

type Object struct {
    Data []byte
}

type ObjectPool struct {
    pool sync.Pool
}

func NewObjectPool() *ObjectPool {
    return &ObjectPool{
        pool: sync.Pool{
            New: func() interface{} {
                return &Object{
                    Data: make([]byte, 1024),
                }
            },
        },
    }
}

func (p *ObjectPool) Get() *Object {
    return p.pool.Get().(*Object)
}

func (p *ObjectPool) Put(obj *Object) {
    // 重置对象状态
    obj.Data = obj.Data[:0]
    p.pool.Put(obj)
}

// 使用示例
func processWithPool() {
    pool := NewObjectPool()

    for i := 0; i < 1000; i++ {
        obj := pool.Get()

        // 处理数据
        obj.Data = append(obj.Data, []byte("data")...)

        // 处理完成后放回池中
        pool.Put(obj)
    }
}
```

#### 内存复用
```go
// 优化前：每次创建新切片
func processChunks(chunks [][]byte) [][]byte {
    var result [][]byte
    for _, chunk := range chunks {
        processed := make([]byte, len(chunk))
        // 处理数据...
        result = append(result, processed)
    }
    return result
}

// 优化后：复用切片
func processChunksOptimized(chunks [][]byte) [][]byte {
    // 预分配切片容量
    result := make([][]byte, 0, len(chunks))

    // 复用缓冲区
    buffer := make([]byte, 0, 1024)

    for _, chunk := range chunks {
        // 重置缓冲区
        buffer = buffer[:0]
        buffer = append(buffer, chunk...)

        // 处理数据...

        // 复制结果
        processed := make([]byte, len(buffer))
        copy(processed, buffer)
        result = append(result, processed)
    }

    return result
}
```

### 2. 垃圾回收优化

#### GC压力测试
```go
package gc

import (
    "runtime"
    "time"
)

type GCStats struct {
    NumGC        uint32
    PauseTotalNs uint64
    PauseNs      [256]uint64
}

func GetGCStats() GCStats {
    var stats GCStats
    runtime.ReadMemStats(&runtime.MemStats{
        NumGC:        &stats.NumGC,
        PauseTotalNs: &stats.PauseTotalNs,
        PauseNs:      stats.PauseNs,
    })
    return stats
}

// 监控GC性能
func MonitorGCPrint() {
    ticker := time.NewTicker(5 * time.Second)
    defer ticker.Stop()

    for range ticker.C {
        stats := GetGCStats()
        println("GC Stats:")
        println("  NumGC:", stats.NumGC)
        println("  PauseTotalNs:", stats.PauseTotalNs)
        println("  AvgPauseNs:", stats.PauseTotalNs/uint64(stats.NumGC))
    }
}

// 优化GC调优
func OptimizeGCSettings() {
    // 设置GC目标百分比
    debug.SetGCPercent(20) // 默认100，减小更激进回收

    // 设置最大内存限制
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

    // 根据应用特点调整
    if m.Sys > 1024*1024*1024 { // 1GB
        debug.SetMaxMemory(2 * 1024 * 1024 * 1024) // 2GB限制
    }
}
```

#### 内存泄漏检测
```go
package memleak

import (
    "runtime"
    "time"
)

type MemoryLeakDetector struct {
    threshold   uint64
    lastCheck   uint64
    checkTicker *time.Ticker
    stopChan    chan struct{}
}

func NewMemoryLeakDetector(thresholdMB uint64) *MemoryLeakDetector {
    return &MemoryLeakDetector{
        threshold: thresholdMB * 1024 * 1024,
        stopChan:  make(chan struct{}),
    }
}

func (d *MemoryLeakDetector) Start() {
    d.lastCheck = d.getCurrentMemory()

    d.checkTicker = time.NewTicker(30 * time.Second)
    go func() {
        for {
            select {
            case <-d.checkTicker.C:
                d.checkMemory()
            case <-d.stopChan:
                return
            }
        }
    }()
}

func (d *MemoryLeakDetector) Stop() {
    if d.checkTicker != nil {
        d.checkTicker.Stop()
    }
    close(d.stopChan)
}

func (d *MemoryLeakDetector) getCurrentMemory() uint64 {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    return m.Alloc
}

func (d *MemoryLeakDetector) checkMemory() {
    current := d.getCurrentMemory()

    if current > d.lastCheck+d.threshold {
        println("Potential memory leak detected!")
        println("Previous:", d.lastCheck)
        println("Current:", current)
        println("Difference:", current-d.lastCheck)

        // 打印堆栈信息
        d.printStacks()
    }

    d.lastCheck = current
}

func (d *MemoryLeakDetector) printStacks() {
    buf := make([]byte, 1024*1024)
    n := runtime.Stack(buf, true)
    println(string(buf[:n]))
}
```

## 📝 并发优化

### 1. Goroutine 优化

#### 控制Goroutine数量
```go
// 优化前：无限制创建goroutine
func processUnlimited(items []string) {
    for _, item := range items {
        go func(i string) {
            // 处理每个item
            processItem(i)
        }(item)
    }
}

// 优化后：使用worker pool
func processWithWorkerPool(items []string, workers int) {
    // 创建任务通道
    taskChan := make(chan string, len(items))
    resultChan := make(chan string, len(items))

    // 创建worker pool
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for task := range taskChan {
                result := processItem(task)
                resultChan <- result
            }
        }(i)
    }

    // 发送任务
    go func() {
        for _, item := range items {
            taskChan <- item
        }
        close(taskChan)
    }()

    // 等待所有worker完成
    go func() {
        wg.Wait()
        close(resultChan)
    }()

    // 收集结果
    for result := range resultChan {
        // 处理结果
        _ = result
    }
}

func processItem(item string) string {
    // 模拟处理
    time.Sleep(10 * time.Millisecond)
    return "processed:" + item
}
```

#### 使用sync.Pool减少GC压力
```go
package worker

import (
    "sync"
    "time"
)

type Task struct {
    ID    string
    Data  []byte
    Result chan<- *Result
}

type Result struct {
    ID   string
    Data []byte
}

type WorkerPool struct {
    workers   int
    taskQueue chan *Task
    workerPool sync.Pool
    wg        sync.WaitGroup
    quit      chan struct{}
}

func NewWorkerPool(workers, queueSize int) *WorkerPool {
    return &WorkerPool{
        workers:   workers,
        taskQueue: make(chan *Task, queueSize),
        workerPool: sync.Pool{
            New: func() interface{} {
                return &worker{
                    id:         time.Now().UnixNano(),
                    taskQueue:  make(chan *Task, 100),
                }
            },
        },
        quit: make(chan struct{}),
    }
}

func (p *WorkerPool) Start() {
    for i := 0; i < p.workers; i++ {
        p.wg.Add(1)
        go p.worker()
    }
}

func (p *WorkerPool) Stop() {
    close(p.quit)
    p.wg.Wait()
}

func (p *WorkerPool) Submit(task *Task) {
    select {
    case p.taskQueue <- task:
    default:
        // 队列满，拒绝或等待
        task.Result <- &Result{ID: task.ID, Data: []byte("queue full")}
    }
}

func (p *WorkerPool) worker() {
    defer p.wg.Done()

    // 从pool获取worker
    w := p.workerPool.Get().(*worker)
    defer p.workerPool.Put(w)

    for {
        select {
        case task := <-p.taskQueue:
            w.process(task)
        case <-p.quit:
            return
        }
    }
}

type worker struct {
    id        int64
    taskQueue chan *Task
}

func (w *worker) process(task *Task) {
    // 处理任务
    result := &Result{
        ID:   task.ID,
        Data: []byte("processed:" + task.ID),
    }

    // 返回结果
    task.Result <- result
}
```

### 2. 并发模式优化

#### 使用Context进行超时控制
```go
package context

import (
    "context"
    "net/http"
    "time"
)

func fetchWithTimeout(ctx context.Context, url string) (*http.Response, error) {
    // 创建带超时的context
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    // 创建请求
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }

    // 发送请求
    client := &http.Client{}
    return client.Do(req)
}

// 并发请求优化
func fetchMultiple(urls []string) map[string]*http.Response {
    ctx := context.Background()
    results := make(map[string]*http.Response)
    resultChan := make(chan struct {
        url    string
        resp   *http.Response
        err    error
    }, len(urls))

    var wg sync.WaitGroup
    for _, url := range urls {
        wg.Add(1)
        go func(u string) {
            defer wg.Done()

            resp, err := fetchWithTimeout(ctx, u)
            resultChan <- struct {
                url    string
                resp   *http.Response
                err    error
            }{u, resp, err}
        }(url)
    }

    // 等待所有请求完成
    go func() {
        wg.Wait()
        close(resultChan)
    }()

    // 收集结果
    for result := range resultChan {
        if result.err == nil {
            results[result.url] = result.resp
        }
    }

    return results
}
```

#### 使用errgroup进行错误处理
```go
package errgroup

import (
    "context"
    "errors"
    "fmt"
    "sync"
)

type Group struct {
    cancel func()
    wg     sync.WaitGroup
    err    error
}

func WithContext(ctx context.Context) (*Group, context.Context) {
    ctx, cancel := context.WithCancel(ctx)
    return &Group{cancel: cancel}, ctx
}

func (g *Group) Go(f func() error) {
    g.wg.Add(1)
    go func() {
        defer g.wg.Done()

        if err := f(); err != nil {
            g.err = err
            if g.cancel != nil {
                g.cancel()
            }
        }
    }()
}

func (g *Group) Wait() error {
    g.wg.Wait()
    return g.err
}

// 使用示例
func processMultipleOperations() error {
    g, ctx := WithContext(context.Background())

    // 并发执行多个操作
    g.Go(func() error {
        return fetchUserData(ctx)
    })

    g.Go(func() error {
        return fetchOrderData(ctx)
    })

    g.Go(func() error {
        return fetchProductData(ctx)
    })

    // 等待所有操作完成
    return g.Wait()
}

func fetchUserData(ctx context.Context) error {
    // 模拟用户数据获取
    select {
    case <-time.After(100 * time.Millisecond):
        return nil
    case <-ctx.Done():
        return ctx.Err()
    }
}

func fetchOrderData(ctx context.Context) error {
    // 模拟订单数据获取
    select {
    case <-time.After(150 * time.Millisecond):
        return errors.New("failed to fetch orders")
    case <-ctx.Done():
        return ctx.Err()
    }
}

func fetchProductData(ctx context.Context) error {
    // 模拟产品数据获取
    select {
    case <-time.After(200 * time.Millisecond):
        return nil
    case <-ctx.Done():
        return ctx.Err()
    }
}
```

## 📝 I/O和网络优化

### 1. 网络优化

#### 连接池复用
```go
package http

import (
    "net/http"
    "sync"
    "time"
)

type HTTPClientPool struct {
    clients map[string]*http.Client
    mu      sync.RWMutex
}

func NewHTTPClientPool() *HTTPClientPool {
    return &HTTPClientPool{
        clients: make(map[string]*http.Client),
    }
}

func (p *HTTPClientPool) GetClient(timeout time.Duration) *http.Client {
    key := timeout.String()

    p.mu.RLock()
    if client, exists := p.clients[key]; exists {
        p.mu.RUnlock()
        return client
    }
    p.mu.RUnlock()

    p.mu.Lock()
    defer p.mu.Unlock()

    // 双重检查
    if client, exists := p.clients[key]; exists {
        return client
    }

    // 创建新client
    client := &http.Client{
        Timeout: timeout,
        Transport: &http.Transport{
            MaxIdleConns:        100,
            MaxIdleConnsPerHost: 10,
            IdleConnTimeout:     30 * time.Second,
        },
    }

    p.clients[key] = client
    return client
}

// 使用示例
var httpClientPool = NewHTTPClientPool()

func makeRequest(url string) (*http.Response, error) {
    client := httpClientPool.GetClient(10 * time.Second)
    return client.Get(url)
}
```

#### 批量请求处理
```go
package batch

import (
    "context"
    "sync"
    "time"
)

type BatchProcessor struct {
    batchSize int
    timeout   time.Duration
    buffer    []interface{}
    processor func([]interface{}) error
    mu        sync.Mutex
    ticker    *time.Ticker
    quit      chan struct{}
}

func NewBatchProcessor(batchSize int, timeout time.Duration, processor func([]interface{}) error) *BatchProcessor {
    return &BatchProcessor{
        batchSize: batchSize,
        timeout:   timeout,
        buffer:    make([]interface{}, 0, batchSize),
        processor: processor,
        quit:      make(chan struct{}),
    }
}

func (p *BatchProcessor) Start() {
    p.ticker = time.NewTicker(p.timeout)
    go func() {
        for {
            select {
            case <-p.ticker.C:
                p.flush()
            case <-p.quit:
                p.flush()
                return
            }
        }
    }()
}

func (p *BatchProcessor) Stop() {
    close(p.quit)
    if p.ticker != nil {
        p.ticker.Stop()
    }
}

func (p *BatchProcessor) Add(item interface{}) error {
    p.mu.Lock()
    defer p.mu.Unlock()

    p.buffer = append(p.buffer, item)

    if len(p.buffer) >= p.batchSize {
        return p.flush()
    }

    return nil
}

func (p *BatchProcessor) flush() error {
    p.mu.Lock()
    defer p.mu.Unlock()

    if len(p.buffer) == 0 {
        return nil
    }

    batch := make([]interface{}, len(p.buffer))
    copy(batch, p.buffer)
    p.buffer = p.buffer[:0]

    return p.processor(batch)
}

// 使用示例
func processBatchItems() {
    processor := NewBatchProcessor(100, 5*time.Second, func(items []interface{}) error {
        println("Processing batch of", len(items), "items")
        // 批量处理逻辑
        return nil
    })

    processor.Start()
    defer processor.Stop()

    // 添加项目
    for i := 0; i < 250; i++ {
        processor.Add(i)
    }
}
```

### 2. 文件I/O优化

#### 缓冲I/O
```go
package io

import (
    "bufio"
    "os"
)

// 优化前：直接文件操作
func readFileDirect(filename string) ([]string, error) {
    file, err := os.Open(filename)
    if err != nil {
        return nil, err
    }
    defer file.Close()

    var lines []string
    buffer := make([]byte, 1024)

    for {
        n, err := file.Read(buffer)
        if err != nil {
            break
        }

        // 处理数据
        lines = append(lines, string(buffer[:n]))
    }

    return lines, nil
}

// 优化后：缓冲读取
func readBuffered(filename string) ([]string, error) {
    file, err := os.Open(filename)
    if err != nil {
        return nil, err
    }
    defer file.Close()

    scanner := bufio.NewScanner(file)
    var lines []string

    for scanner.Scan() {
        lines = append(lines, scanner.Text())
    }

    if err := scanner.Err(); err != nil {
        return nil, err
    }

    return lines, nil
}

// 并发文件处理
func processFilesConcurrently(filenames []string) error {
    const workers = 5
    jobs := make(chan string, len(filenames))
    results := make(chan error, len(filenames))

    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for filename := range jobs {
                err := processFile(filename)
                results <- err
            }
        }()
    }

    // 发送任务
    go func() {
        for _, filename := range filenames {
            jobs <- filename
        }
        close(jobs)
    }()

    // 等待完成
    go func() {
        wg.Wait()
        close(results)
    }()

    // 收集结果
    for err := range results {
        if err != nil {
            return err
        }
    }

    return nil
}

func processFile(filename string) error {
    // 文件处理逻辑
    _, err := readBuffered(filename)
    return err
}
```

## 📝 数据库优化

### 1. 连接池优化

#### 数据库连接池配置
```go
package database

import (
    "time"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

type DBConfig struct {
    Host            string
    Port            int
    User            string
    Password        string
    DBName          string
    MaxIdleConns    int
    MaxOpenConns    int
    ConnMaxLifetime time.Duration
    ConnMaxIdleTime time.Duration
}

func InitDB(config DBConfig) (*gorm.DB, error) {
    dsn := buildDSN(config)

    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
        Logger: logger.Default.LogMode(logger.Info),
    })
    if err != nil {
        return nil, err
    }

    // 获取底层sql.DB
    sqlDB, err := db.DB()
    if err != nil {
        return nil, err
    }

    // 配置连接池
    sqlDB.SetMaxIdleConns(config.MaxIdleConns)
    sqlDB.SetMaxOpenConns(config.MaxOpenConns)
    sqlDB.SetConnMaxLifetime(config.ConnMaxLifetime)
    sqlDB.SetConnMaxIdleTime(config.ConnMaxIdleTime)

    return db, nil
}

func buildDSN(config DBConfig) string {
    return fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%d sslmode=disable TimeZone=Asia/Shanghai",
        config.Host, config.User, config.Password, config.DBName, config.Port)
}

// 连接池监控
type ConnectionPoolMonitor struct {
    db *gorm.DB
}

func NewConnectionPoolMonitor(db *gorm.DB) *ConnectionPoolMonitor {
    return &ConnectionPoolMonitor{db: db}
}

func (m *ConnectionPoolMonitor) GetStats() map[string]interface{} {
    sqlDB, _ := m.db.DB()
    stats := sqlDB.Stats()

    return map[string]interface{}{
        "open_connections":     stats.OpenConnections,
        "in_use":              stats.InUse,
        "idle":                stats.Idle,
        "wait_count":          stats.WaitCount,
        "wait_duration":       stats.WaitDuration,
        "max_idle_closed":     stats.MaxIdleClosed,
        "max_lifetime_closed":  stats.MaxLifetimeClosed,
    }
}

func (m *ConnectionPoolMonitor) PrintStats() {
    stats := m.GetStats()
    println("Database Connection Pool Stats:")
    for key, value := range stats {
        printf("  %s: %v\n", key, value)
    }
}
```

### 2. 查询优化

#### 批量查询优化
```go
package repository

import (
    "context"
    "gorm.io/gorm"
)

type UserRepository struct {
    db *gorm.DB
}

// 优化前：N+1查询问题
func (r *UserRepository) GetUsersWithPostsBad() ([]User, error) {
    var users []User
    if err := r.db.Find(&users).Error; err != nil {
        return nil, err
    }

    // 对每个用户都发起一次查询
    for i := range users {
        var posts []Post
        if err := r.db.Where("user_id = ?", users[i].ID).Find(&posts).Error; err != nil {
            return nil, err
        }
        users[i].Posts = posts
    }

    return users, nil
}

// 优化后：预加载关联
func (r *UserRepository) GetUsersWithPostsGood() ([]User, error) {
    var users []User
    // 使用Preload一次性加载关联数据
    if err := r.db.Preload("Posts").Find(&users).Error; err != nil {
        return nil, err
    }
    return users, nil
}

// 批量插入优化
func (r *UserRepository) BatchInsertUsers(users []User) error {
    // 优化前：逐条插入
    // for _, user := range users {
    //     if err := r.db.Create(&user).Error; err != nil {
    //         return err
    //     }
    // }

    // 优化后：批量插入
    if len(users) == 0 {
        return nil
    }

    // 分批处理，避免单次插入数据量过大
    batchSize := 1000
    for i := 0; i < len(users); i += batchSize {
        end := i + batchSize
        if end > len(users) {
            end = len(users)
        }

        batch := users[i:end]
        if err := r.db.CreateInBatches(batch, batchSize).Error; err != nil {
            return err
        }
    }

    return nil
}

// 事务优化
func (r *UserRepository) TransferFunds(ctx context.Context, fromID, toID uint, amount float64) error {
    return r.db.Transaction(func(tx *gorm.DB) error {
        // 扣除发送方余额
        if err := tx.Model(&User{}).Where("id = ?", fromID).
            Update("balance", gorm.Expr("balance - ?", amount)).Error; err != nil {
            return err
        }

        // 增加接收方余额
        if err := tx.Model(&User{}).Where("id = ?", toID).
            Update("balance", gorm.Expr("balance + ?", amount)).Error; err != nil {
            return err
        }

        return nil
    })
}
```

## 📝 性能分析工具

### 1. pprof 使用

#### CPU性能分析
```go
package pprof

import (
    "os"
    "runtime/pprof"
    "time"
)

type Profiler struct {
    cpuProfile *os.File
    memProfile *os.File
}

func NewProfiler() *Profiler {
    return &Profiler{}
}

func (p *Profiler) StartCPUProfile(filename string) error {
    var err error
    p.cpuProfile, err = os.Create(filename)
    if err != nil {
        return err
    }

    return pprof.StartCPUProfile(p.cpuProfile)
}

func (p *Profiler) StopCPUProfile() {
    if p.cpuProfile != nil {
        pprof.StopCPUProfile()
        p.cpuProfile.Close()
        p.cpuProfile = nil
    }
}

func (p *Profiler) WriteMemProfile(filename string) error {
    var err error
    p.memProfile, err = os.Create(filename)
    if err != nil {
        return err
    }

    // 获取当前堆内存信息
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

    // 写入内存分析数据
    return pprof.WriteHeapProfile(p.memProfile)
}

func (p *Profiler) Close() {
    p.StopCPUProfile()
    if p.memProfile != nil {
        p.memProfile.Close()
        p.memProfile = nil
    }
}

// 使用示例
func profileApplication() {
    profiler := NewProfiler()

    // 开始CPU分析
    if err := profiler.StartCPUProfile("cpu.prof"); err != nil {
        panic(err)
    }

    // 运行应用程序
    runApplication()

    // 停止CPU分析
    profiler.StopCPUProfile()

    // 写入内存分析
    if err := profiler.WriteMemProfile("mem.prof"); err != nil {
        panic(err)
    }

    profiler.Close()
}

func runApplication() {
    // 模拟应用程序运行
    for i := 0; i < 1000000; i++ {
        fibonacci(30)
    }
}

func fibonacci(n int) int {
    if n <= 1 {
        return n
    }
    return fibonacci(n-1) + fibonacci(n-2)
}
```

### 2. 自定义性能监控

#### 性能指标收集
```go
package metrics

import (
    "runtime"
    "sync"
    "time"
)

type PerformanceMetrics struct {
    mu           sync.RWMutex
    goroutines   int
    memoryUsage  uint64
    gcStats      GCStats
    responseTime map[string]time.Duration
}

type GCStats struct {
    NumGC        uint32
    PauseTotalNs uint64
    PauseNs      [256]uint64
}

type MetricsCollector struct {
    metrics      *PerformanceMetrics
    interval     time.Duration
    stopChan     chan struct{}
}

func NewMetricsCollector(interval time.Duration) *MetricsCollector {
    return &MetricsCollector{
        metrics: &PerformanceMetrics{
            responseTime: make(map[string]time.Duration),
        },
        interval: interval,
        stopChan: make(chan struct{}),
    }
}

func (c *MetricsCollector) Start() {
    ticker := time.NewTicker(c.interval)
    go func() {
        for {
            select {
            case <-ticker.C:
                c.collectMetrics()
            case <-c.stopChan:
                return
            }
        }
    }()
}

func (c *MetricsCollector) Stop() {
    close(c.stopChan)
}

func (c *MetricsCollector) collectMetrics() {
    c.metrics.mu.Lock()
    defer c.metrics.mu.Unlock()

    // 收集goroutine数量
    c.metrics.goroutines = runtime.NumGoroutine()

    // 收集内存使用
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    c.metrics.memoryUsage = m.Alloc

    // 收集GC统计
    c.metrics.gcStats = GCStats{
        NumGC:        m.NumGC,
        PauseTotalNs: m.PauseTotalNs,
    }
    copy(c.metrics.gcStats.PauseNs[:], m.PauseNs[:])
}

func (c *MetricsCollector) RecordResponseTime(endpoint string, duration time.Duration) {
    c.metrics.mu.Lock()
    defer c.metrics.mu.Unlock()

    c.metrics.responseTime[endpoint] = duration
}

func (c *MetricsCollector) GetMetrics() PerformanceMetrics {
    c.metrics.mu.RLock()
    defer c.metrics.mu.RUnlock()

    return *c.metrics
}

// 性能分析器
type PerformanceAnalyzer struct {
    collector *MetricsCollector
    threshold time.Duration
}

func NewPerformanceAnalyzer(collector *MetricsCollector, threshold time.Duration) *PerformanceAnalyzer {
    return &PerformanceAnalyzer{
        collector: collector,
        threshold: threshold,
    }
}

func (a *PerformanceAnalyzer) Analyze() []string {
    metrics := a.collector.GetMetrics()
    var issues []string

    // 检查goroutine数量
    if metrics.goroutines > 1000 {
        issues = append(issues, fmt.Sprintf("High goroutine count: %d", metrics.goroutines))
    }

    // 检查内存使用
    if metrics.memoryUsage > 100*1024*1024 { // 100MB
        issues = append(issues, fmt.Sprintf("High memory usage: %d MB", metrics.memoryUsage/1024/1024))
    }

    // 检查GC频率
    if metrics.gcStats.NumGC > 100 {
        issues = append(issues, fmt.Sprintf("High GC frequency: %d", metrics.gcStats.NumGC))
    }

    // 检查响应时间
    for endpoint, duration := range metrics.responseTime {
        if duration > a.threshold {
            issues = append(issues, fmt.Sprintf("Slow endpoint %s: %v", endpoint, duration))
        }
    }

    return issues
}
```

## 🧪 实践练习

### 练习1: 完整的性能优化示例
```go
// main.go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

type PerformanceOptimizedServer struct {
    requestCounter  prometheus.Counter
    requestDuration prometheus.Histogram
    workerPool     *WorkerPool
    cache         *Cache
}

func NewPerformanceOptimizedServer() *PerformanceOptimizedServer {
    return &PerformanceOptimizedServer{
        requestCounter: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "requests_total",
            Help: "Total number of requests",
        }),
        requestDuration: prometheus.NewHistogram(prometheus.HistogramOpts{
            Name:    "request_duration_seconds",
            Help:    "Request duration in seconds",
            Buckets: []float64{0.1, 0.5, 1, 2.5, 5},
        }),
        workerPool: NewWorkerPool(10, 100),
        cache:      NewCache(1000),
    }
}

func (s *PerformanceOptimizedServer) HandleRequest(ctx context.Context, req *Request) (*Response, error) {
    start := time.Now()
    defer func() {
        s.requestCounter.Inc()
        s.requestDuration.Observe(time.Since(start).Seconds())
    }()

    // 检查缓存
    if cached, found := s.cache.Get(req.ID); found {
        return cached.(*Response), nil
    }

    // 使用worker pool处理
    resultChan := make(chan *Response, 1)
    errChan := make(chan error, 1)

    task := &Task{
        ID:     req.ID,
        Data:   req.Data,
        Result: resultChan,
        Error:  errChan,
    }

    if err := s.workerPool.Submit(task); err != nil {
        return nil, err
    }

    select {
    case result := <-resultChan:
        // 缓存结果
        s.cache.Set(req.ID, result, 5*time.Minute)
        return result, nil
    case err := <-errChan:
        return nil, err
    case <-ctx.Done():
        return nil, ctx.Err()
    }
}

// 缓存实现
type Cache struct {
    items map[string]interface{}
    mu    sync.RWMutex
    size  int
}

func NewCache(size int) *Cache {
    return &Cache{
        items: make(map[string]interface{}),
        size:  size,
    }
}

func (c *Cache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()

    item, exists := c.items[key]
    return item, exists
}

func (c *Cache) Set(key string, value interface{}, ttl time.Duration) {
    c.mu.Lock()
    defer c.mu.Unlock()

    // 如果缓存已满，删除最旧的项
    if len(c.items) >= c.size {
        // 简单的LRU实现
        for k := range c.items {
            delete(c.items, k)
            break
        }
    }

    c.items[key] = value
}

func main() {
    server := NewPerformanceOptimizedServer()

    // 启动监控
    http.Handle("/metrics", promhttp.Handler())
    go http.ListenAndServe(":9090", nil)

    // 处理请求
    for i := 0; i < 10000; i++ {
        req := &Request{
            ID:   fmt.Sprintf("req-%d", i),
            Data: fmt.Sprintf("data-%d", i),
        }

        resp, err := server.HandleRequest(context.Background(), req)
        if err != nil {
            fmt.Printf("Error: %v\n", err)
            continue
        }

        fmt.Printf("Processed: %s\n", resp.Data)
    }
}
```

## 📋 检查清单

- [ ] 理解内存管理优化
- [ ] 掌握并发编程优化
- [ ] 学会I/O和网络优化
- [ ] 理解数据库优化策略
- [ ] 掌握性能分析工具
- [ ] 学会使用缓存
- [ ] 理解Go性能特性
- [ ] 掌握最佳实践

## 🚀 下一步

掌握性能优化后，你可以继续学习：
- **高级并发模式**: 复杂并发场景处理
- **分布式系统**: 分布式性能优化
- **容器化优化**: Docker和K8s性能调优
- **AIOps**: 智能性能监控和优化

---

**学习提示**: Go的性能优化需要深入理解其运行机制。与PHP不同，Go是编译型语言，可以通过编译时优化和运行时调优来获得更好的性能。合理使用并发和内存管理是Go性能优化的关键。

*最后更新: 2025年9月*