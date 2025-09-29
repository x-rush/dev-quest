# Go高并发处理最佳实践

本文档详细介绍Go语言在高并发场景下的最佳实践，包括Goroutine管理、Channel使用、并发模式、性能优化、错误处理等方面的内容。

## 1. Goroutine管理

### 1.1 Goroutine基础

```go
package goroutine

import (
    "context"
    "runtime"
    "sync"
    "time"
)

// 基础Goroutine使用
func BasicGoroutineExample() {
    // 启动一个Goroutine
    go func() {
        // 在这里执行并发任务
        time.Sleep(1 * time.Second)
        println("Goroutine completed")
    }()

    // 使用WaitGroup等待Goroutine完成
    var wg sync.WaitGroup
    wg.Add(1)

    go func() {
        defer wg.Done()
        // 执行任务
        println("Task completed")
    }()

    wg.Wait()
}

// 带超时的Goroutine
func GoroutineWithTimeout(timeout time.Duration) error {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()

    done := make(chan error, 1)

    go func() {
        // 模拟耗时任务
        time.Sleep(2 * time.Second)
        done <- nil
    }()

    select {
    case err := <-done:
        return err
    case <-ctx.Done():
        return ctx.Err()
    }
}
```

### 1.2 Goroutine池

```go
package pool

import (
    "context"
    "sync"
    "time"
)

type Task struct {
    ID     int
    Data   interface{}
    Result chan interface{}
    Error  chan error
}

type GoroutinePool struct {
    workerCount int
    taskQueue   chan Task
    ctx         context.Context
    cancel      context.CancelFunc
    wg          sync.WaitGroup
}

func NewGoroutinePool(workerCount int) *GoroutinePool {
    ctx, cancel := context.WithCancel(context.Background())

    pool := &GoroutinePool{
        workerCount: workerCount,
        taskQueue:   make(chan Task, workerCount*2),
        ctx:         ctx,
        cancel:      cancel,
        wg:          sync.WaitGroup{},
    }

    pool.start()
    return pool
}

func (p *GoroutinePool) start() {
    for i := 0; i < p.workerCount; i++ {
        p.wg.Add(1)
        go p.worker(i)
    }
}

func (p *GoroutinePool) worker(id int) {
    defer p.wg.Done()

    for {
        select {
        case task := <-p.taskQueue:
            p.processTask(task, id)
        case <-p.ctx.Done():
            return
        }
    }
}

func (p *GoroutinePool) processTask(task Task, workerID int) {
    defer func() {
        if r := recover(); r != nil {
            if task.Error != nil {
                task.Error <- fmt.Errorf("worker %d panic: %v", workerID, r)
            }
        }
    }()

    // 处理任务
    result, err := p.handleTask(task)

    if err != nil && task.Error != nil {
        task.Error <- err
    }

    if result != nil && task.Result != nil {
        task.Result <- result
    }
}

func (p *GoroutinePool) handleTask(task Task) (interface{}, error) {
    // 这里实现具体的任务处理逻辑
    time.Sleep(100 * time.Millisecond) // 模拟处理时间
    return fmt.Sprintf("Task %d processed", task.ID), nil
}

func (p *GoroutinePool) Submit(task Task) error {
    select {
    case p.taskQueue <- task:
        return nil
    case <-p.ctx.Done():
        return fmt.Errorf("pool is closed")
    }
}

func (p *GoroutinePool) Close() {
    p.cancel()
    p.wg.Wait()
}

// 使用示例
func PoolExample() {
    pool := NewGoroutinePool(10)
    defer pool.Close()

    var tasks []Task
    for i := 0; i < 100; i++ {
        task := Task{
            ID:     i,
            Result: make(chan interface{}, 1),
            Error:  make(chan error, 1),
        }
        tasks = append(tasks, task)

        go func(t Task) {
            if err := pool.Submit(t); err != nil {
                t.Error <- err
            }
        }(task)
    }

    // 收集结果
    for _, task := range tasks {
        select {
        case result := <-task.Result:
            println(result.(string))
        case err := <-task.Error:
            println("Error:", err.Error())
        case <-time.After(5 * time.Second):
            println("Timeout")
        }
    }
}
```

### 1.3 Goroutine优雅关闭

```go
package graceful

import (
    "context"
    "os"
    "os/signal"
    "sync"
    "syscall"
    "time"
)

type GracefulManager struct {
    servers     []Server
    tasks       []*Task
    wg          sync.WaitGroup
    ctx         context.Context
    cancel      context.CancelFunc
    timeout     time.Duration
}

type Server interface {
    Shutdown(ctx context.Context) error
}

type Task struct {
    name string
    stop func()
}

func NewGracefulManager(timeout time.Duration) *GracefulManager {
    ctx, cancel := context.WithCancel(context.Background())

    return &GracefulManager{
        ctx:     ctx,
        cancel:  cancel,
        timeout: timeout,
    }
}

func (m *GracefulManager) AddServer(server Server) {
    m.servers = append(m.servers, server)
}

func (m *GracefulManager) AddTask(name string, stop func()) {
    m.tasks = append(m.tasks, &Task{
        name: name,
        stop: stop,
    })
}

func (m *GracefulManager) Start() {
    // 启动信号监听
    go m.signalHandler()
}

func (m *GracefulManager) signalHandler() {
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

    <-sigChan
    m.Shutdown()
}

func (m *GracefulManager) Shutdown() {
    println("Starting graceful shutdown...")

    // 创建带超时的上下文
    ctx, cancel := context.WithTimeout(m.ctx, m.timeout)
    defer cancel()

    // 停止所有任务
    m.stopTasks(ctx)

    // 关闭所有服务器
    m.shutdownServers(ctx)

    // 取消上下文
    m.cancel()

    println("Graceful shutdown completed")
}

func (m *GracefulManager) stopTasks(ctx context.Context) {
    var wg sync.WaitGroup

    for _, task := range m.tasks {
        wg.Add(1)
        go func(t *Task) {
            defer wg.Done()

            println("Stopping task:", t.name)
            t.stop()
            println("Task stopped:", t.name)
        }(task)
    }

    done := make(chan struct{})
    go func() {
        wg.Wait()
        close(done)
    }()

    select {
    case <-done:
        println("All tasks stopped")
    case <-ctx.Done():
        println("Timeout stopping tasks")
    }
}

func (m *GracefulManager) shutdownServers(ctx context.Context) {
    var wg sync.WaitGroup

    for _, server := range m.servers {
        wg.Add(1)
        go func(s Server) {
            defer wg.Done()

            if err := s.Shutdown(ctx); err != nil {
                println("Server shutdown error:", err)
            }
        }(server)
    }

    done := make(chan struct{})
    go func() {
        wg.Wait()
        close(done)
    }()

    select {
    case <-done:
        println("All servers stopped")
    case <-ctx.Done():
        println("Timeout stopping servers")
    }
}

// 使用示例
func GracefulExample() {
    manager := NewGracefulManager(30 * time.Second)

    // 添加需要优雅关闭的服务器
    // manager.AddServer(httpServer)

    // 添加后台任务
    manager.AddTask("background-worker", func() {
        println("Stopping background worker")
    })

    manager.Start()
}
```

## 2. Channel模式

### 2.1 基础Channel模式

```go
package channel

import (
    "context"
    "fmt"
    "time"
)

// Fan-out模式：一个输入，多个输出
func FanOut(ctx context.Context, in <-chan int, workers int) []<-chan int {
    outs := make([]<-chan int, workers)

    for i := 0; i < workers; i++ {
        outs[i] = worker(ctx, in, i)
    }

    return outs
}

func worker(ctx context.Context, in <-chan int, id int) <-chan int {
    out := make(chan int)

    go func() {
        defer close(out)

        for {
            select {
            case <-ctx.Done():
                return
            case v, ok := <-in:
                if !ok {
                    return
                }
                // 处理数据
                result := v * 2
                out <- result
            }
        }
    }()

    return out
}

// Fan-in模式：多个输入，一个输出
func FanIn(ctx context.Context, chans ...<-chan int) <-chan int {
    out := make(chan int)

    var wg sync.WaitGroup
    wg.Add(len(chans))

    for _, ch := range chans {
        go func(c <-chan int) {
            defer wg.Done()

            for v := range c {
                select {
                case out <- v:
                case <-ctx.Done():
                    return
                }
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}

// Pipeline模式
func PipelineExample() {
    // 第一阶段：生成数据
    generator := func(ctx context.Context) <-chan int {
        out := make(chan int)

        go func() {
            defer close(out)

            for i := 1; i <= 10; i++ {
                select {
                case out <- i:
                case <-ctx.Done():
                    return
                }
            }
        }()

        return out
    }

    // 第二阶段：处理数据
    processor := func(ctx context.Context, in <-chan int) <-chan int {
        out := make(chan int)

        go func() {
            defer close(out)

            for v := range in {
                result := v * v
                select {
                case out <- result:
                case <-ctx.Done():
                    return
                }
            }
        }()

        return out
    }

    // 第三阶段：输出结果
    consumer := func(ctx context.Context, in <-chan int) {
        for v := range in {
            println("Result:", v)
        }
    }

    ctx := context.Background()
    stage1 := generator(ctx)
    stage2 := processor(ctx, stage1)
    consumer(ctx, stage2)
}

// 带缓存的Channel
func BufferedChannelExample() {
    // 创建带缓存的Channel
    ch := make(chan int, 100)

    // 生产者
    go func() {
        for i := 0; i < 1000; i++ {
            ch <- i
        }
        close(ch)
    }()

    // 消费者
    for v := range ch {
        println("Received:", v)
    }
}
```

### 2.2 高级Channel模式

```go
package advanced

import (
    "context"
    "sync"
    "time"
)

// 带超时的Channel操作
func ChannelWithTimeout(ctx context.Context, ch <-chan int, timeout time.Duration) (int, error) {
    select {
    case v := <-ch:
        return v, nil
    case <-ctx.Done():
        return 0, ctx.Err()
    case <-time.After(timeout):
        return 0, fmt.Errorf("timeout")
    }
}

// Channel池
type ChannelPool struct {
    pools    map[string]chan interface{}
    mu       sync.Mutex
    ctx      context.Context
    maxSize  int
}

func NewChannelPool(ctx context.Context, maxSize int) *ChannelPool {
    return &ChannelPool{
        pools:   make(map[string]chan interface{}),
        ctx:     ctx,
        maxSize: maxSize,
    }
}

func (p *ChannelPool) GetChannel(name string) chan interface{} {
    p.mu.Lock()
    defer p.mu.Unlock()

    if ch, exists := p.pools[name]; exists {
        return ch
    }

    ch := make(chan interface{}, p.maxSize)
    p.pools[name] = ch

    return ch
}

func (p *ChannelPool) Close() {
    p.mu.Lock()
    defer p.mu.Unlock()

    for name, ch := range p.pools {
        close(ch)
        delete(p.pools, name)
    }
}

// 广播Channel
type Broadcaster struct {
    subscribers map[chan interface{}]struct{}
    mu          sync.RWMutex
    ctx         context.Context
}

func NewBroadcaster(ctx context.Context) *Broadcaster {
    return &Broadcaster{
        subscribers: make(map[chan interface{}]struct{}),
        ctx:         ctx,
    }
}

func (b *Broadcaster) Subscribe() chan interface{} {
    ch := make(chan interface{}, 100)

    b.mu.Lock()
    b.subscribers[ch] = struct{}{}
    b.mu.Unlock()

    return ch
}

func (b *Broadcaster) Unsubscribe(ch chan interface{}) {
    b.mu.Lock()
    defer b.mu.Unlock()

    delete(b.subscribers, ch)
    close(ch)
}

func (b *Broadcaster) Broadcast(message interface{}) {
    b.mu.RLock()
    defer b.mu.RUnlock()

    for sub := range b.subscribers {
        select {
        case sub <- message:
        case <-b.ctx.Done():
            return
        default:
            // Channel满，丢弃消息
        }
    }
}

// 使用示例
func BroadcasterExample() {
    ctx := context.Background()
    broadcaster := NewBroadcaster(ctx)

    // 订阅者1
    sub1 := broadcaster.Subscribe()
    go func() {
        for msg := range sub1 {
            println("Subscriber 1:", msg)
        }
    }()

    // 订阅者2
    sub2 := broadcaster.Subscribe()
    go func() {
        for msg := range sub2 {
            println("Subscriber 2:", msg)
        }
    }()

    // 广播消息
    for i := 0; i < 10; i++ {
        broadcaster.Broadcast(fmt.Sprintf("Message %d", i))
        time.Sleep(1 * time.Second)
    }
}
```

## 3. 并发模式

### 3.1 Worker Pool模式

```go
package workerpool

import (
    "context"
    "sync"
    "time"
)

type Job struct {
    ID     int
    Data   interface{}
    Result chan interface{}
    Error  chan error
}

type WorkerPool struct {
    workers    []*Worker
    jobQueue   chan Job
    ctx        context.Context
    cancel     context.CancelFunc
    wg         sync.WaitGroup
    workerSize int
    queueSize  int
}

type Worker struct {
    id     int
    pool   *WorkerPool
    active bool
}

func NewWorkerPool(workerSize, queueSize int) *WorkerPool {
    ctx, cancel := context.WithCancel(context.Background())

    pool := &WorkerPool{
        workerSize: workerSize,
        queueSize:  queueSize,
        jobQueue:   make(chan Job, queueSize),
        ctx:        ctx,
        cancel:     cancel,
    }

    pool.workers = make([]*Worker, workerSize)
    for i := 0; i < workerSize; i++ {
        pool.workers[i] = &Worker{
            id:   i,
            pool: pool,
        }
    }

    return pool
}

func (p *WorkerPool) Start() {
    for _, worker := range p.workers {
        p.wg.Add(1)
        go worker.start()
    }
}

func (p *WorkerPool) Stop() {
    p.cancel()
    p.wg.Wait()
}

func (p *WorkerPool) Submit(job Job) error {
    select {
    case p.jobQueue <- job:
        return nil
    case <-p.ctx.Done():
        return fmt.Errorf("pool is closed")
    }
}

func (w *Worker) start() {
    defer w.pool.wg.Done()
    w.active = true

    for {
        select {
        case job := <-w.pool.jobQueue:
            w.processJob(job)
        case <-w.pool.ctx.Done():
            w.active = false
            return
        }
    }
}

func (w *Worker) processJob(job Job) {
    defer func() {
        if r := recover(); r != nil {
            if job.Error != nil {
                job.Error <- fmt.Errorf("worker %d panic: %v", w.id, r)
            }
        }
    }()

    start := time.Now()
    result, err := w.executeJob(job)
    duration := time.Since(start)

    // 记录处理时间
    log.Printf("Worker %d processed job %d in %v", w.id, job.ID, duration)

    if err != nil && job.Error != nil {
        job.Error <- err
    }

    if result != nil && job.Result != nil {
        job.Result <- result
    }
}

func (w *Worker) executeJob(job Job) (interface{}, error) {
    // 这里实现具体的作业处理逻辑
    time.Sleep(time.Duration(100+job.ID%50) * time.Millisecond)

    return fmt.Sprintf("Job %d completed by worker %d", job.ID, w.id), nil
}

// 使用示例
func WorkerPoolExample() {
    pool := NewWorkerPool(10, 100)
    pool.Start()
    defer pool.Stop()

    // 提交作业
    var wg sync.WaitGroup
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func(jobID int) {
            defer wg.Done()

            job := Job{
                ID:     jobID,
                Result: make(chan interface{}, 1),
                Error:  make(chan error, 1),
            }

            if err := pool.Submit(job); err != nil {
                println("Submit error:", err.Error())
                return
            }

            select {
            case result := <-job.Result:
                println(result.(string))
            case err := <-job.Error:
                println("Job error:", err.Error())
            case <-time.After(5 * time.Second):
                println("Job timeout")
            }
        }(i)
    }

    wg.Wait()
}
```

### 3.2 Futures/Promises模式

```go
package futures

import (
    "context"
    "sync"
    "time"
)

type Future struct {
    result interface{}
    err    error
    done   chan struct{}
    once   sync.Once
    mu     sync.Mutex
}

func NewFuture() *Future {
    return &Future{
        done: make(chan struct{}),
    }
}

func (f *Future) Set(result interface{}, err error) {
    f.once.Do(func() {
        f.mu.Lock()
        defer f.mu.Unlock()

        f.result = result
        f.err = err
        close(f.done)
    })
}

func (f *Future) Get() (interface{}, error) {
    <-f.done
    f.mu.Lock()
    defer f.mu.Unlock()

    return f.result, f.err
}

func (f *Future) GetWithTimeout(timeout time.Duration) (interface{}, error) {
    select {
    case <-f.done:
        f.mu.Lock()
        defer f.mu.Unlock()
        return f.result, f.err
    case <-time.After(timeout):
        return nil, fmt.Errorf("timeout")
    }
}

func (f *Future) GetWithContext(ctx context.Context) (interface{}, error) {
    select {
    case <-f.done:
        f.mu.Lock()
        defer f.mu.Unlock()
        return f.result, f.err
    case <-ctx.Done():
        return nil, ctx.Err()
    }
}

func (f *Future) IsDone() bool {
    select {
    case <-f.done:
        return true
    default:
        return false
    }
}

// 异步执行函数
func Async(fn func() (interface{}, error)) *Future {
    future := NewFuture()

    go func() {
        defer func() {
            if r := recover(); r != nil {
                future.Set(nil, fmt.Errorf("panic: %v", r))
            }
        }()

        result, err := fn()
        future.Set(result, err)
    }()

    return future
}

// 并发执行多个任务
func AsyncAll(futures ...*Future) *Future {
    future := NewFuture()

    go func() {
        results := make([]interface{}, len(futures))
        errors := make([]error, len(futures))

        for i, f := range futures {
            result, err := f.Get()
            results[i] = result
            errors[i] = err
        }

        // 检查是否有错误
        for _, err := range errors {
            if err != nil {
                future.Set(nil, fmt.Errorf("one or more futures failed"))
                return
            }
        }

        future.Set(results, nil)
    }()

    return future
}

// 并发执行，只等待第一个完成
func AsyncRace(futures ...*Future) *Future {
    future := NewFuture()

    go func() {
        done := make(chan struct{})
        var result interface{}
        var err error

        for _, f := range futures {
            go func(fut *Future) {
                res, e := fut.Get()
                select {
                case <-done:
                    return
                default:
                    result = res
                    err = e
                    close(done)
                }
            }(f)
        }

        <-done
        future.Set(result, err)
    }()

    return future
}

// 使用示例
func FuturesExample() {
    // 异步执行任务
    future1 := Async(func() (interface{}, error) {
        time.Sleep(1 * time.Second)
        return "Task 1 completed", nil
    })

    future2 := Async(func() (interface{}, error) {
        time.Sleep(2 * time.Second)
        return "Task 2 completed", nil
    })

    // 等待所有任务完成
    allFuture := AsyncAll(future1, future2)
    result, err := allFuture.Get()
    if err != nil {
        println("Error:", err.Error())
        return
    }

    println("All tasks completed:", result)

    // 竞争模式
    raceFuture := AsyncRace(future1, future2)
    raceResult, err := raceFuture.Get()
    if err != nil {
        println("Race error:", err.Error())
        return
    }

    println("Race winner:", raceResult)
}
```

## 4. 性能优化

### 4.1 并发控制

```go
package concurrency

import (
    "context"
    "golang.org/x/time/rate"
    "sync"
    "time"
)

// 信号量模式
type Semaphore struct {
    permits chan struct{}
    ctx      context.Context
}

func NewSemaphore(ctx context.Context, maxConcurrent int) *Semaphore {
    permits := make(chan struct{}, maxConcurrent)
    for i := 0; i < maxConcurrent; i++ {
        permits <- struct{}{}
    }

    return &Semaphore{
        permits: permits,
        ctx:     ctx,
    }
}

func (s *Semaphore) Acquire() error {
    select {
    case <-s.permits:
        return nil
    case <-s.ctx.Done():
        return s.ctx.Err()
    }
}

func (s *Semaphore) Release() {
    select {
    case s.permits <- struct{}{}:
    default:
        // 已经有足够的许可
    }
}

func (s *Semaphore) AcquireWithTimeout(timeout time.Duration) error {
    select {
    case <-s.permits:
        return nil
    case <-time.After(timeout):
        return fmt.Errorf("timeout acquiring semaphore")
    case <-s.ctx.Done():
        return s.ctx.Err()
    }
}

// 使用示例
func SemaphoreExample() {
    ctx := context.Background()
    sem := NewSemaphore(ctx, 10) // 最多10个并发

    var wg sync.WaitGroup
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            // 获取许可
            if err := sem.Acquire(); err != nil {
                println("Error:", err.Error())
                return
            }
            defer sem.Release()

            // 执行任务
            time.Sleep(100 * time.Millisecond)
            println("Task", id, "completed")
        }(i)
    }

    wg.Wait()
}

// 限流器模式
type RateLimiter struct {
    limiter *rate.Limiter
    ctx     context.Context
}

func NewRateLimiter(ctx context.Context, r rate.Limit, b int) *RateLimiter {
    return &RateLimiter{
        limiter: rate.NewLimiter(r, b),
        ctx:     ctx,
    }
}

func (r *RateLimiter) Wait() error {
    return r.limiter.Wait(r.ctx)
}

func (r *RateLimiter) Allow() bool {
    return r.liter.Allow()
}

func (r *RateLimiter) Reserve() *rate.Reservation {
    return r.limiter.Reserve()
}

// 使用示例
func RateLimiterExample() {
    ctx := context.Background()
    limiter := NewRateLimiter(ctx, rate.Limit(10), 1) // 每秒10个请求

    for i := 0; i < 20; i++ {
        if err := limiter.Wait(); err != nil {
            println("Rate limit error:", err.Error())
            continue
        }

        println("Request", i, "processed")
    }
}

// 断路器模式
type CircuitBreaker struct {
    state        State
    failureCount int
    threshold    int
    timeout      time.Duration
    lastFailure  time.Time
    mu           sync.Mutex
}

type State int

const (
    StateClosed State = iota
    StateOpen
    StateHalfOpen
)

func NewCircuitBreaker(threshold int, timeout time.Duration) *CircuitBreaker {
    return &CircuitBreaker{
        state:     StateClosed,
        threshold: threshold,
        timeout:   timeout,
    }
}

func (cb *CircuitBreaker) Execute(fn func() error) error {
    cb.mu.Lock()
    defer cb.mu.Unlock()

    now := time.Now()

    // 检查断路器状态
    if cb.state == StateOpen {
        if now.Sub(cb.lastFailure) > cb.timeout {
            cb.state = StateHalfOpen
            cb.failureCount = 0
        } else {
            return fmt.Errorf("circuit breaker is open")
        }
    }

    // 执行函数
    err := fn()

    if err != nil {
        cb.failureCount++
        cb.lastFailure = now

        if cb.failureCount >= cb.threshold {
            cb.state = StateOpen
        }

        return err
    }

    // 成功，重置状态
    cb.failureCount = 0
    cb.state = StateClosed

    return nil
}

// 使用示例
func CircuitBreakerExample() {
    cb := NewCircuitBreaker(5, 30*time.Second)

    for i := 0; i < 10; i++ {
        err := cb.Execute(func() error {
            // 模拟可能失败的操作
            if i%3 == 0 {
                return fmt.Errorf("operation failed")
            }
            println("Operation", i, "succeeded")
            return nil
        })

        if err != nil {
            println("Operation", i, "failed:", err.Error())
        }
    }
}
```

### 4.2 内存优化

```go
package memory

import (
    "runtime"
    "sync"
    "time"
)

// 对象池模式
type ObjectPool struct {
    pool   chan interface{}
    create func() interface{}
    reset  func(interface{})
    mu     sync.Mutex
}

func NewObjectPool(size int, create func() interface{}, reset func(interface{})) *ObjectPool {
    pool := &ObjectPool{
        pool:   make(chan interface{}, size),
        create: create,
        reset:  reset,
    }

    // 预填充池
    for i := 0; i < size; i++ {
        pool.pool <- create()
    }

    return pool
}

func (p *ObjectPool) Get() interface{} {
    select {
    case obj := <-p.pool:
        return obj
    default:
        return p.create()
    }
}

func (p *ObjectPool) Put(obj interface{}) {
    p.reset(obj)

    select {
    case p.pool <- obj:
    default:
        // 池已满，丢弃对象
    }
}

// 使用示例
func ObjectPoolExample() {
    // 创建缓冲区池
    bufferPool := NewObjectPool(
        100, // 池大小
        func() interface{} {
            return make([]byte, 1024)
        },
        func(obj interface{}) {
            buf := obj.([]byte)
            for i := range buf {
                buf[i] = 0
            }
        },
    )

    // 使用池中的对象
    buf := bufferPool.Get().([]byte)
    defer bufferPool.Put(buf)

    // 使用缓冲区
    copy(buf, []byte("Hello, World!"))
    println(string(buf))
}

// 内存监控
type MemoryMonitor struct {
    interval time.Duration
    stopChan chan struct{}
}

func NewMemoryMonitor(interval time.Duration) *MemoryMonitor {
    return &MemoryMonitor{
        interval: interval,
        stopChan: make(chan struct{}),
    }
}

func (m *MemoryMonitor) Start() {
    ticker := time.NewTicker(m.interval)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            m.printMemStats()
        case <-m.stopChan:
            return
        }
    }
}

func (m *MemoryMonitor) Stop() {
    close(m.stopChan)
}

func (m *MemoryMonitor) printMemStats() {
    var memStats runtime.MemStats
    runtime.ReadMemStats(&memStats)

    println("Memory Stats:")
    println("  Alloc:", memStats.Alloc)
    println("  TotalAlloc:", memStats.TotalAlloc)
    println("  Sys:", memStats.Sys)
    println("  NumGC:", memStats.NumGC)
    println("  Goroutines:", runtime.NumGoroutine())
}

// 使用示例
func MemoryMonitorExample() {
    monitor := NewMemoryMonitor(10 * time.Second)
    go monitor.Start()
    defer monitor.Stop()

    // 模拟内存使用
    for i := 0; i < 1000; i++ {
        data := make([]byte, 1024*1024) // 1MB
        time.Sleep(100 * time.Millisecond)
        _ = data // 避免被优化掉
    }
}
```

## 5. 错误处理

### 5.1 并发错误处理

```go
package errors

import (
    "context"
    "errors"
    "sync"
    "time"
)

// 错误聚合器
type ErrorAggregator struct {
    errors []error
    mu     sync.Mutex
}

func NewErrorAggregator() *ErrorAggregator {
    return &ErrorAggregator{
        errors: make([]error, 0),
    }
}

func (e *ErrorAggregator) Add(err error) {
    e.mu.Lock()
    defer e.mu.Unlock()

    if err != nil {
        e.errors = append(e.errors, err)
    }
}

func (e *ErrorAggregator) Error() error {
    e.mu.Lock()
    defer e.mu.Unlock()

    if len(e.errors) == 0 {
        return nil
    }

    if len(e.errors) == 1 {
        return e.errors[0]
    }

    var msgs []string
    for _, err := range e.errors {
        msgs = append(msgs, err.Error())
    }

    return fmt.Errorf("multiple errors occurred: %v", msgs)
}

func (e *ErrorAggregator) HasErrors() bool {
    e.mu.Lock()
    defer e.mu.Unlock()
    return len(e.errors) > 0
}

// 重试机制
type RetryConfig struct {
    MaxAttempts int
    InitialDelay time.Duration
    MaxDelay     time.Duration
    Backoff      float64
}

func Retry(ctx context.Context, config RetryConfig, fn func() error) error {
    var err error
    delay := config.InitialDelay

    for attempt := 1; attempt <= config.MaxAttempts; attempt++ {
        err = fn()
        if err == nil {
            return nil
        }

        if attempt == config.MaxAttempts {
            return fmt.Errorf("after %d attempts: %w", attempt, err)
        }

        select {
        case <-time.After(delay):
            delay = time.Duration(float64(delay) * config.Backoff)
            if delay > config.MaxDelay {
                delay = config.MaxDelay
            }
        case <-ctx.Done():
            return ctx.Err()
        }
    }

    return err
}

// 使用示例
func RetryExample() {
    config := RetryConfig{
        MaxAttempts: 3,
        InitialDelay: 1 * time.Second,
        MaxDelay:     10 * time.Second,
        Backoff:      2.0,
    }

    err := Retry(context.Background(), config, func() error {
        // 模拟可能失败的操作
        if time.Now().Unix()%2 == 0 {
            return errors.New("operation failed")
        }
        return nil
    })

    if err != nil {
        println("Retry failed:", err.Error())
    } else {
        println("Operation succeeded")
    }
}

// 并发错误处理
func ConcurrentErrorExample() {
    var wg sync.WaitGroup
    errorAggregator := NewErrorAggregator()

    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            // 模拟可能失败的操作
            if id%3 == 0 {
                errorAggregator.Add(fmt.Errorf("task %d failed", id))
            }
        }(i)
    }

    wg.Wait()

    if errorAggregator.HasErrors() {
        println("Some tasks failed:", errorAggregator.Error().Error())
    } else {
        println("All tasks succeeded")
    }
}
```

### 5.2 恢复处理

```go
package recovery

import (
    "context"
    "fmt"
    "runtime/debug"
    "sync"
    "time"
)

// 恢复处理中间件
type RecoveryHandler struct {
    mu       sync.Mutex
    panics   []PanicInfo
    maxSize  int
    callback func(PanicInfo)
}

type PanicInfo struct {
    Time       time.Time
    StackTrace string
    Goroutine  int
    Message    string
}

func NewRecoveryHandler(maxSize int, callback func(PanicInfo)) *RecoveryHandler {
    return &RecoveryHandler{
        panics:   make([]PanicInfo, 0, maxSize),
        maxSize:  maxSize,
        callback: callback,
    }
}

func (r *RecoveryHandler) Handle() {
    if rec := recover(); rec != nil {
        info := PanicInfo{
            Time:       time.Now(),
            StackTrace: string(debug.Stack()),
            Goroutine:  runtime.NumGoroutine(),
            Message:    fmt.Sprintf("%v", rec),
        }

        r.mu.Lock()
        defer r.mu.Unlock()

        // 添加到记录
        r.panics = append(r.panics, info)

        // 保持最大大小限制
        if len(r.panics) > r.maxSize {
            r.panics = r.panics[1:]
        }

        // 调用回调函数
        if r.callback != nil {
            go r.callback(info)
        }
    }
}

func (r *RecoveryHandler) GetPanics() []PanicInfo {
    r.mu.Lock()
    defer r.mu.Unlock()

    result := make([]PanicInfo, len(r.panics))
    copy(result, r.panics)

    return result
}

// 安全执行函数
func SafeExecute(fn func()) (err error) {
    defer func() {
        if rec := recover(); rec != nil {
            err = fmt.Errorf("panic recovered: %v", rec)
        }
    }()

    fn()
    return nil
}

// 安全执行并返回结果
func SafeExecuteResult[T any](fn func() T) (result T, err error) {
    defer func() {
        if rec := recover(); rec != nil {
            err = fmt.Errorf("panic recovered: %v", rec)
        }
    }()

    result = fn()
    return result, nil
}

// 使用示例
func RecoveryExample() {
    // 创建恢复处理器
    recovery := NewRecoveryHandler(100, func(info PanicInfo) {
        println("Panic occurred:", info.Message)
        println("Stack trace:", info.StackTrace)
    })

    // 在Goroutine中使用
    go func() {
        defer recovery.Handle()

        // 模拟panic
        panic("something went wrong")
    }()

    // 安全执行
    err := SafeExecute(func() {
        // 模拟可能panic的代码
        if time.Now().Unix()%2 == 0 {
            panic("random panic")
        }
        println("Safe execution completed")
    })

    if err != nil {
        println("Safe execution failed:", err.Error())
    }

    // 安全执行返回结果
    result, err := SafeExecuteResult(func() string {
        if time.Now().Unix()%2 == 0 {
            panic("panic in result function")
        }
        return "success"
    })

    if err != nil {
        println("Safe execution result failed:", err.Error())
    } else {
        println("Result:", result)
    }

    // 等待一下让panic有时间被记录
    time.Sleep(1 * time.Second)

    // 获取所有panic记录
    panics := recovery.GetPanics()
    println("Total panics recorded:", len(panics))
}
```

## 6. 监控和指标

### 6.1 并发监控

```go
package monitoring

import (
    "context"
    "runtime"
    "sync"
    "time"
)

// 并发监控器
type ConcurrencyMonitor struct {
    metrics map[string]*Metric
    mu      sync.RWMutex
}

type Metric struct {
    Name      string
    Value     int64
    MaxValue  int64
    MinValue  int64
    Timestamp time.Time
}

func NewConcurrencyMonitor() *ConcurrencyMonitor {
    return &ConcurrencyMonitor{
        metrics: make(map[string]*Metric),
    }
}

func (m *ConcurrencyMonitor) Record(name string, value int64) {
    m.mu.Lock()
    defer m.mu.Unlock()

    metric, exists := m.metrics[name]
    if !exists {
        metric = &Metric{
            Name:      name,
            MaxValue:  value,
            MinValue:  value,
            Timestamp: time.Now(),
        }
        m.metrics[name] = metric
    }

    metric.Value = value
    if value > metric.MaxValue {
        metric.MaxValue = value
    }
    if value < metric.MinValue {
        metric.MinValue = value
    }
    metric.Timestamp = time.Now()
}

func (m *ConcurrencyMonitor) GetMetric(name string) (*Metric, bool) {
    m.mu.RLock()
    defer m.mu.RUnlock()

    metric, exists := m.metrics[name]
    if !exists {
        return nil, false
    }

    // 返回副本
    result := *metric
    return &result, true
}

func (m *ConcurrencyMonitor) GetAllMetrics() map[string]Metric {
    m.mu.RLock()
    defer m.mu.RUnlock()

    result := make(map[string]Metric)
    for name, metric := range m.metrics {
        result[name] = *metric
    }

    return result
}

// 系统监控器
type SystemMonitor struct {
    interval time.Duration
    stopChan chan struct{}
    monitor  *ConcurrencyMonitor
}

func NewSystemMonitor(interval time.Duration) *SystemMonitor {
    return &SystemMonitor{
        interval: interval,
        stopChan: make(chan struct{}),
        monitor:  NewConcurrencyMonitor(),
    }
}

func (s *SystemMonitor) Start() {
    ticker := time.NewTicker(s.interval)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            s.collectMetrics()
        case <-s.stopChan:
            return
        }
    }
}

func (s *SystemMonitor) Stop() {
    close(s.stopChan)
}

func (s *SystemMonitor) collectMetrics() {
    // 收集Goroutine数量
    s.monitor.Record("goroutines", int64(runtime.NumGoroutine()))

    // 收集内存统计
    var memStats runtime.MemStats
    runtime.ReadMemStats(&memStats)

    s.monitor.Record("memory_alloc", int64(memStats.Alloc))
    s.monitor.Record("memory_sys", int64(memStats.Sys))
    s.monitor.Record("memory_num_gc", int64(memStats.NumGC))

    // 可以添加更多系统指标
}

func (s *SystemMonitor) GetMetrics() map[string]Metric {
    return s.monitor.GetAllMetrics()
}

// 使用示例
func MonitoringExample() {
    // 创建系统监控器
    monitor := NewSystemMonitor(5 * time.Second)
    go monitor.Start()
    defer monitor.Stop()

    // 模拟工作负载
    var wg sync.WaitGroup
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            // 模拟工作
            time.Sleep(time.Duration(id%100) * time.Millisecond)

            // 记录自定义指标
            monitor.monitor.Record("task_completed", int64(id))
        }(i)
    }

    wg.Wait()

    // 获取监控指标
    metrics := monitor.GetMetrics()
    println("Collected metrics:")
    for name, metric := range metrics {
        printf("  %s: %d (max: %d, min: %d)\n",
            name, metric.Value, metric.MaxValue, metric.MinValue)
    }
}
```

### 6.2 性能分析

```go
package profiling

import (
    "context"
    "fmt"
    "runtime/pprof"
    "sync"
    "time"
)

// 性能分析器
type Profiler struct {
    cpuProfile   string
    memProfile   string
    goroutineProfile string
    enabled      bool
    mu           sync.Mutex
}

func NewProfiler() *Profiler {
    return &Profiler{
        enabled: false,
    }
}

func (p *Profiler) StartCPUProfile(filename string) error {
    p.mu.Lock()
    defer p.mu.Unlock()

    if p.enabled {
        return fmt.Errorf("profiler already running")
    }

    p.cpuProfile = filename
    p.enabled = true

    go func() {
        f, err := os.Create(filename)
        if err != nil {
            log.Printf("Failed to create CPU profile: %v", err)
            return
        }
        defer f.Close()

        if err := pprof.StartCPUProfile(f); err != nil {
            log.Printf("Failed to start CPU profile: %v", err)
            return
        }

        // 运行一段时间
        time.Sleep(30 * time.Second)
        pprof.StopCPUProfile()

        p.mu.Lock()
        p.enabled = false
        p.mu.Unlock()
    }()

    return nil
}

func (p *Profiler) WriteMemoryProfile(filename string) error {
    f, err := os.Create(filename)
    if err != nil {
        return fmt.Errorf("failed to create memory profile: %v", err)
    }
    defer f.Close()

    if err := pprof.WriteHeapProfile(f); err != nil {
        return fmt.Errorf("failed to write memory profile: %v", err)
    }

    return nil
}

func (p *Profiler) WriteGoroutineProfile(filename string) error {
    f, err := os.Create(filename)
    if err != nil {
        return fmt.Errorf("failed to create goroutine profile: %v", err)
    }
    defer f.Close()

    if err := pprof.Lookup("goroutine").WriteTo(f, 0); err != nil {
        return fmt.Errorf("failed to write goroutine profile: %v", err)
    }

    return nil
}

// 使用示例
func ProfilingExample() {
    profiler := NewProfiler()

    // 开始CPU分析
    err := profiler.StartCPUProfile("cpu.prof")
    if err != nil {
        println("Failed to start CPU profile:", err.Error())
        return
    }

    // 运行一些工作负载
    var wg sync.WaitGroup
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            // 模拟CPU密集型工作
            for j := 0; j < 1000000; j++ {
                _ = j * j
            }
        }(i)
    }

    wg.Wait()

    // 写入内存分析
    err = profiler.WriteMemoryProfile("mem.prof")
    if err != nil {
        println("Failed to write memory profile:", err.Error())
    }

    // 写入Goroutine分析
    err = profiler.WriteGoroutineProfile("goroutine.prof")
    if err != nil {
        println("Failed to write goroutine profile:", err.Error())
    }

    println("Profiling completed")
}
```

## 7. 最佳实践总结

### 7.1 Goroutine最佳实践

1. **Goroutine管理**
   - 避免创建过多的Goroutine
   - 使用Worker Pool模式控制并发数量
   - 实现优雅关闭机制
   - 处理panic和异常

2. **资源控制**
   - 使用信号量控制并发数量
   - 实现限流机制
   - 监控Goroutine数量
   - 避免资源泄露

3. **错误处理**
   - 在每个Goroutine中处理panic
   - 使用错误聚合器收集错误
   - 实现重试机制
   - 记录错误日志

### 7.2 Channel最佳实践

1. **Channel使用**
   - 优先使用带缓冲的Channel
   - 正确处理Channel关闭
   - 避免死锁
   - 使用select实现超时

2. **并发模式**
   - 使用Fan-out/Fan-in模式
   - 实现Pipeline模式
   - 使用广播Channel
   - 实现竞争模式

3. **性能优化**
   - 减少Channel操作
   - 使用批量操作
   - 避免在循环中创建Channel
   - 合理设置缓冲区大小

### 7.3 性能优化最佳实践

1. **内存管理**
   - 使用对象池减少GC压力
   - 避免频繁的内存分配
   - 监控内存使用
   - 优化数据结构

2. **并发控制**
   - 合理设置并发数量
   - 使用断路器模式
   - 实现负载均衡
   - 监控系统资源

3. **监控和调优**
   - 收集性能指标
   - 分析瓶颈
   - 优化热点代码
   - 定期性能测试

### 7.4 安全最佳实践

1. **输入验证**
   - 验证所有输入数据
   - 防止注入攻击
   - 限制输入大小
   - 清理敏感数据

2. **并发安全**
   - 使用同步机制保护共享资源
   - 避免竞态条件
   - 实现原子操作
   - 使用线程安全的数据结构

3. **资源安全**
   - 限制资源使用
   - 实现超时机制
   - 防止资源泄露
   - 监控资源使用

通过遵循这些最佳实践，你可以构建高性能、高并发、高可靠的Go应用程序。