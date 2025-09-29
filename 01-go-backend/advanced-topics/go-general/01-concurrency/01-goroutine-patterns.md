# Go Goroutine模式与最佳实践

## 概述

Goroutine是Go语言并发编程的核心特性，它提供了一种轻量级的线程实现方式。本文档将深入探讨Goroutine的各种模式、最佳实践以及在实际开发中的应用。

## 目录

- [Goroutine基础](#goroutine基础)
- [工作池模式](#工作池模式)
- [扇出扇入模式](#扇出扇入模式)
- [生产者消费者模式](#生产者消费者模式)
- [管道模式](#管道模式)
- [超时和取消模式](#超时和取消模式)
- [错误处理模式](#错误处理模式)
- [资源池模式](#资源池模式)
- [限流模式](#限流模式)
- [性能优化技巧](#性能优化技巧)
- [监控和调试](#监控和调试)
- [最佳实践总结](#最佳实践总结)

## Goroutine基础

### Goroutine生命周期管理

```go
// Goroutine生命周期管理器
type GoroutineManager struct {
    wg         sync.WaitGroup
    ctx        context.Context
    cancel     context.CancelFunc
    maxWorkers int
    semaphore  chan struct{}
}

// 创建Goroutine管理器
func NewGoroutineManager(maxWorkers int) *GoroutineManager {
    ctx, cancel := context.WithCancel(context.Background())
    return &GoroutineManager{
        ctx:        ctx,
        cancel:     cancel,
        maxWorkers: maxWorkers,
        semaphore:  make(chan struct{}, maxWorkers),
    }
}

// 启动Goroutine
func (gm *GoroutineManager) Go(task func(ctx context.Context) error) error {
    select {
    case gm.semaphore <- struct{}{}:
        gm.wg.Add(1)
        go func() {
            defer gm.wg.Done()
            defer func() { <-gm.semaphore }()

            if err := task(gm.ctx); err != nil {
                log.Printf("Goroutine error: %v", err)
            }
        }()
        return nil
    case <-gm.ctx.Done():
        return gm.ctx.Err()
    }
}

// 等待所有Goroutine完成
func (gm *GoroutineManager) Wait() {
    gm.wg.Wait()
}

// 停止所有Goroutine
func (gm *GoroutineManager) Stop() {
    gm.cancel()
    gm.Wait()
}
```

### Goroutine安全模式

```go
// 安全的Goroutine启动器
type SafeGoroutine struct {
    panicHandler func(interface{})
    logger       *log.Logger
}

// 创建安全的Goroutine启动器
func NewSafeGoroutine() *SafeGoroutine {
    return &SafeGoroutine{
        panicHandler: func(recoverObj interface{}) {
            log.Printf("Goroutine panic recovered: %v", recoverObj)
        },
        logger: log.Default(),
    }
}

// 安全启动Goroutine
func (sg *SafeGoroutine) Go(task func()) {
    go func() {
        defer sg.panicHandler(recover())
        task()
    }()
}

// 带超时的Goroutine
func (sg *SafeGoroutine) GoWithTimeout(task func(), timeout time.Duration) error {
    done := make(chan struct{})

    sg.Go(func() {
        defer close(done)
        task()
    })

    select {
    case <-done:
        return nil
    case <-time.After(timeout):
        return fmt.Errorf("goroutine timeout after %v", timeout)
    }
}
```

## 工作池模式

### 固定大小工作池

```go
// 工作池配置
type WorkerPoolConfig struct {
    WorkerCount    int
    QueueSize      int
    RetryCount     int
    RetryDelay     time.Duration
    Timeout        time.Duration
}

// 工作任务
type Task struct {
    ID        string
    Data      interface{}
    Handler   func(ctx context.Context, data interface{}) error
    Retry     int
    CreatedAt time.Time
}

// 工作池
type WorkerPool struct {
    config     *WorkerPoolConfig
    tasks      chan *Task
    workers    []*Worker
    ctx        context.Context
    cancel     context.CancelFunc
    wg         sync.WaitGroup
    stats      *PoolStats
}

// 创建工作池
func NewWorkerPool(config *WorkerPoolConfig) *WorkerPool {
    ctx, cancel := context.WithCancel(context.Background())

    pool := &WorkerPool{
        config: config,
        tasks:  make(chan *Task, config.QueueSize),
        ctx:    ctx,
        cancel: cancel,
        stats:  &PoolStats{},
    }

    // 创建工作器
    pool.workers = make([]*Worker, config.WorkerCount)
    for i := 0; i < config.WorkerCount; i++ {
        pool.workers[i] = NewWorker(i, pool)
    }

    return pool
}

// 启动工作池
func (wp *WorkerPool) Start() {
    wp.wg.Add(wp.config.WorkerCount)
    for _, worker := range wp.workers {
        go worker.Start()
    }
}

// 提交任务
func (wp *WorkerPool) Submit(task *Task) error {
    select {
    case wp.tasks <- task:
        wp.stats.IncrementSubmitted()
        return nil
    case <-wp.ctx.Done():
        return wp.ctx.Err()
    }
}

// 工作器
type Worker struct {
    id   int
    pool *WorkerPool
}

func NewWorker(id int, pool *WorkerPool) *Worker {
    return &Worker{
        id:   id,
        pool: pool,
    }
}

func (w *Worker) Start() {
    defer w.pool.wg.Done()

    for {
        select {
        case task := <-w.pool.tasks:
            w.processTask(task)
        case <-w.pool.ctx.Done():
            return
        }
    }
}

func (w *Worker) processTask(task *Task) {
    var err error
    defer func() {
        w.pool.stats.IncrementProcessed()
        if err != nil {
            w.pool.stats.IncrementFailed()
        }
    }()

    // 重试逻辑
    for i := 0; i <= task.Retry; i++ {
        ctx, cancel := context.WithTimeout(w.pool.ctx, w.pool.config.Timeout)
        err = task.Handler(ctx, task.Data)
        cancel()

        if err == nil {
            break
        }

        if i < task.Retry {
            time.Sleep(w.pool.config.RetryDelay)
        }
    }
}

// 工作池统计
type PoolStats struct {
    submitted int64
    processed int64
    failed    int64
    mutex     sync.RWMutex
}

func (ps *PoolStats) IncrementSubmitted() {
    ps.mutex.Lock()
    defer ps.mutex.Unlock()
    ps.submitted++
}

func (ps *PoolStats) IncrementProcessed() {
    ps.mutex.Lock()
    defer ps.mutex.Unlock()
    ps.processed++
}

func (ps *PoolStats) IncrementFailed() {
    ps.mutex.Lock()
    defer ps.mutex.Unlock()
    ps.failed++
}

func (ps *PoolStats) GetStats() (int64, int64, int64) {
    ps.mutex.RLock()
    defer ps.mutex.RUnlock()
    return ps.submitted, ps.processed, ps.failed
}
```

### 动态大小工作池

```go
// 动态工作池
type DynamicWorkerPool struct {
    config      *WorkerPoolConfig
    minWorkers  int
    maxWorkers  int
    currentSize int
    tasks       chan *Task
    workers     map[int]*Worker
    ctx         context.Context
    cancel      context.CancelFunc
    wg          sync.WaitGroup
    stats       *PoolStats
    loadMonitor *LoadMonitor
}

// 创建动态工作池
func NewDynamicWorkerPool(config *WorkerPoolConfig, minWorkers, maxWorkers int) *DynamicWorkerPool {
    ctx, cancel := context.WithCancel(context.Background())

    pool := &DynamicWorkerPool{
        config:      config,
        minWorkers:  minWorkers,
        maxWorkers:  maxWorkers,
        currentSize: minWorkers,
        tasks:       make(chan *Task, config.QueueSize),
        workers:     make(map[int]*Worker),
        ctx:         ctx,
        cancel:      cancel,
        stats:       &PoolStats{},
        loadMonitor: NewLoadMonitor(),
    }

    // 初始化工作器
    for i := 0; i < minWorkers; i++ {
        pool.addWorker()
    }

    // 启动负载监控
    go pool.monitorLoad()

    return pool
}

// 添加工作器
func (dwp *DynamicWorkerPool) addWorker() {
    worker := NewWorker(dwp.currentSize, dwp)
    dwp.workers[dwp.currentSize] = worker
    dwp.currentSize++

    dwp.wg.Add(1)
    go worker.Start()
}

// 移除工作器
func (dwp *DynamicWorkerPool) removeWorker() {
    if len(dwp.workers) > dwp.minWorkers {
        // 选择一个工作器进行移除
        // 这里简化处理，实际应该基于负载和状态
        for id, worker := range dwp.workers {
            worker.Stop()
            delete(dwp.workers, id)
            dwp.currentSize--
            break
        }
    }
}

// 监控负载
func (dwp *DynamicWorkerPool) monitorLoad() {
    ticker := time.NewTicker(5 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            load := dwp.loadMonitor.GetLoad()

            // 根据负载调整工作器数量
            if load > 0.8 && len(dwp.workers) < dwp.maxWorkers {
                dwp.addWorker()
            } else if load < 0.3 && len(dwp.workers) > dwp.minWorkers {
                dwp.removeWorker()
            }
        case <-dwp.ctx.Done():
            return
        }
    }
}

// 负载监控器
type LoadMonitor struct {
    taskCount    int64
    windowSize   int
    measurements []float64
    mutex        sync.RWMutex
}

func NewLoadMonitor() *LoadMonitor {
    return &LoadMonitor{
        windowSize:   10,
        measurements: make([]float64, 0),
    }
}

func (lm *LoadMonitor) RecordTask() {
    atomic.AddInt64(&lm.taskCount, 1)
}

func (lm *LoadMonitor) GetLoad() float64 {
    currentLoad := float64(atomic.LoadInt64(&lm.taskCount)) / float64(cap(lm.measurements))

    lm.mutex.Lock()
    defer lm.mutex.Unlock()

    lm.measurements = append(lm.measurements, currentLoad)
    if len(lm.measurements) > lm.windowSize {
        lm.measurements = lm.measurements[1:]
    }

    // 计算平均负载
    var sum float64
    for _, m := range lm.measurements {
        sum += m
    }

    return sum / float64(len(lm.measurements))
}
```

## 扇出扇入模式

### 扇出模式

```go
// 扇出模式实现
type FanOut struct {
    workers   int
    input     chan interface{}
    outputs   []chan interface{}
    ctx       context.Context
    cancel    context.CancelFunc
    wg        sync.WaitGroup
}

// 创建扇出
func NewFanOut(workers int) *FanOut {
    ctx, cancel := context.WithCancel(context.Background())

    fo := &FanOut{
        workers: workers,
        input:   make(chan interface{}),
        outputs: make([]chan interface{}, workers),
        ctx:     ctx,
        cancel:  cancel,
    }

    // 创建输出通道
    for i := 0; i < workers; i++ {
        fo.outputs[i] = make(chan interface{})
    }

    return fo
}

// 启动扇出
func (fo *FanOut) Start() {
    fo.wg.Add(fo.workers)
    for i := 0; i < fo.workers; i++ {
        go fo.worker(i)
    }
}

// 工作器
func (fo *FanOut) worker(id int) {
    defer fo.wg.Done()

    for {
        select {
        case data := <-fo.input:
            // 处理数据并发送到对应的输出通道
            processed := fo.processData(id, data)
            select {
            case fo.outputs[id] <- processed:
            case <-fo.ctx.Done():
                return
            }
        case <-fo.ctx.Done():
            return
        }
    }
}

// 处理数据
func (fo *FanOut) processData(id int, data interface{}) interface{} {
    // 这里可以根据工作器ID进行不同的处理
    result := fmt.Sprintf("Worker %d processed: %v", id, data)
    return result
}

// 输入数据
func (fo *FanOut) Input(data interface{}) {
    select {
    case fo.input <- data:
    case <-fo.ctx.Done():
    }
}

// 获取输出通道
func (fo *FanOut) Outputs() []chan interface{} {
    return fo.outputs
}

// 停止扇出
func (fo *FanOut) Stop() {
    fo.cancel()
    fo.wg.Wait()
}
```

### 扇入模式

```go
// 扇入模式实现
type FanIn struct {
    inputs    []chan interface{}
    output    chan interface{}
    ctx       context.Context
    cancel    context.CancelFunc
    wg        sync.WaitGroup
    merger    func([]interface{}) interface{}
}

// 创建扇入
func NewFanIn(inputs []chan interface{}, merger func([]interface{}) interface{}) *FanIn {
    ctx, cancel := context.WithCancel(context.Background())

    fi := &FanIn{
        inputs: inputs,
        output: make(chan interface{}),
        ctx:    ctx,
        cancel: cancel,
        merger: merger,
    }

    return fi
}

// 启动扇入
func (fi *FanIn) Start() {
    fi.wg.Add(len(fi.inputs))
    for i, input := range fi.inputs {
        go fi.collector(i, input)
    }
}

// 数据收集器
func (fi *FanIn) collector(id int, input chan interface{}) {
    defer fi.wg.Done()

    buffer := make([]interface{}, 0)

    for {
        select {
        case data := <-input:
            buffer = append(buffer, data)

            // 当缓冲区达到一定大小时进行合并
            if len(buffer) >= 10 {
                result := fi.merger(buffer)
                select {
                case fi.output <- result:
                    buffer = buffer[:0] // 清空缓冲区
                case <-fi.ctx.Done():
                    return
                }
            }
        case <-fi.ctx.Done():
            // 处理剩余数据
            if len(buffer) > 0 {
                result := fi.merger(buffer)
                select {
                case fi.output <- result:
                default:
                }
            }
            return
        }
    }
}

// 获取输出通道
func (fi *FanIn) Output() chan interface{} {
    return fi.output
}

// 停止扇入
func (fi *FanIn) Stop() {
    fi.cancel()
    fi.wg.Wait()
}
```

## 生产者消费者模式

### 基本生产者消费者

```go
// 消息队列
type MessageQueue struct {
    messages chan interface{}
    capacity int
    ctx      context.Context
    cancel   context.CancelFunc
}

// 创建消息队列
func NewMessageQueue(capacity int) *MessageQueue {
    ctx, cancel := context.WithCancel(context.Background())
    return &MessageQueue{
        messages: make(chan interface{}, capacity),
        capacity: capacity,
        ctx:      ctx,
        cancel:   cancel,
    }
}

// 生产者
type Producer struct {
    id      int
    queue   *MessageQueue
    counter int
}

// 创建生产者
func NewProducer(id int, queue *MessageQueue) *Producer {
    return &Producer{
        id:    id,
        queue: queue,
    }
}

// 启动生产者
func (p *Producer) Start() {
    ticker := time.NewTicker(100 * time.Millisecond)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            p.produce()
        case <-p.queue.ctx.Done():
            return
        }
    }
}

// 生产消息
func (p *Producer) produce() {
    message := fmt.Sprintf("Producer %d - Message %d", p.id, p.counter)
    p.counter++

    select {
    case p.queue.messages <- message:
        log.Printf("Produced: %s", message)
    case <-p.queue.ctx.Done():
        return
    }
}

// 消费者
type Consumer struct {
    id    int
    queue *MessageQueue
}

// 创建消费者
func NewConsumer(id int, queue *MessageQueue) *Consumer {
    return &Consumer{
        id:    id,
        queue: queue,
    }
}

// 启动消费者
func (c *Consumer) Start() {
    for {
        select {
        case message := <-c.queue.messages:
            c.consume(message)
        case <-c.queue.ctx.Done():
            return
        }
    }
}

// 消费消息
func (c *Consumer) consume(message interface{}) {
    log.Printf("Consumer %d consumed: %v", c.id, message)

    // 模拟处理时间
    time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
}
```

### 多级生产者消费者

```go
// 多级生产者消费者系统
type MultiStageProducerConsumer struct {
    stages    []*Stage
    ctx       context.Context
    cancel    context.CancelFunc
    wg        sync.WaitGroup
}

// 处理阶段
type Stage struct {
    name      string
    input     chan interface{}
    output    chan interface{}
    workers   int
    processor func(interface{}) interface{}
}

// 创建多级系统
func NewMultiStageProducerConsumer() *MultiStageProducerConsumer {
    ctx, cancel := context.WithCancel(context.Background())
    return &MultiStageProducerConsumer{
        ctx:    ctx,
        cancel: cancel,
        stages: make([]*Stage, 0),
    }
}

// 添加阶段
func (mspc *MultiStageProducerConsumer) AddStage(name string, workers int, processor func(interface{}) interface{}) {
    bufferSize := workers * 2
    stage := &Stage{
        name:      name,
        input:     make(chan interface{}, bufferSize),
        output:    make(chan interface{}, bufferSize),
        workers:   workers,
        processor: processor,
    }
    mspc.stages = append(mspc.stages, stage)
}

// 启动系统
func (mspc *MultiStageProducerConsumer) Start() {
    // 连接各阶段的输入输出
    for i := 0; i < len(mspc.stages); i++ {
        stage := mspc.stages[i]

        // 启动工作器
        for j := 0; j < stage.workers; j++ {
            mspc.wg.Add(1)
            go mspc.stageWorker(stage, j)
        }
    }
}

// 阶段工作器
func (mspc *MultiStageProducerConsumer) stageWorker(stage *Stage, id int) {
    defer mspc.wg.Done()

    for {
        select {
        case data := <-stage.input:
            // 处理数据
            result := stage.processor(data)

            // 发送到下一阶段
            select {
            case stage.output <- result:
            case <-mspc.ctx.Done():
                return
            }
        case <-mspc.ctx.Done():
            return
        }
    }
}

// 输入数据
func (mspc *MultiStageProducerConsumer) Input(data interface{}) {
    if len(mspc.stages) > 0 {
        select {
        case mspc.stages[0].input <- data:
        case <-mspc.ctx.Done():
        }
    }
}

// 获取最终输出
func (mspc *MultiStageProducerConsumer) Output() <-chan interface{} {
    if len(mspc.stages) > 0 {
        return mspc.stages[len(mspc.stages)-1].output
    }
    return nil
}

// 停止系统
func (mspc *MultiStageProducerConsumer) Stop() {
    mspc.cancel()
    mspc.wg.Wait()
}
```

## 管道模式

### 基本管道模式

```go
// 管道阶段
type PipelineStage struct {
    name      string
    input     chan interface{}
    output    chan interface{}
    processor func(interface{}) (interface{}, error)
    errorChan chan error
}

// 创建管道阶段
func NewPipelineStage(name string, bufferSize int, processor func(interface{}) (interface{}, error)) *PipelineStage {
    return &PipelineStage{
        name:      name,
        input:     make(chan interface{}, bufferSize),
        output:    make(chan interface{}, bufferSize),
        processor: processor,
        errorChan: make(chan error, bufferSize),
    }
}

// 启动阶段
func (ps *PipelineStage) Start() {
    go func() {
        defer close(ps.output)
        defer close(ps.errorChan)

        for data := range ps.input {
            result, err := ps.processor(data)
            if err != nil {
                ps.errorChan <- err
                continue
            }
            ps.output <- result
        }
    }()
}

// 管道
type Pipeline struct {
    stages    []*PipelineStage
    ctx       context.Context
    cancel    context.CancelFunc
    wg        sync.WaitGroup
}

// 创建管道
func NewPipeline() *Pipeline {
    ctx, cancel := context.WithCancel(context.Background())
    return &Pipeline{
        ctx:    ctx,
        cancel: cancel,
        stages: make([]*PipelineStage, 0),
    }
}

// 添加阶段
func (p *Pipeline) AddStage(name string, bufferSize int, processor func(interface{}) (interface{}, error)) {
    stage := NewPipelineStage(name, bufferSize, processor)
    p.stages = append(p.stages, stage)
}

// 启动管道
func (p *Pipeline) Start() {
    // 启动所有阶段
    for _, stage := range p.stages {
        stage.Start()
    }
}

// 输入数据
func (p *Pipeline) Input(data interface{}) {
    if len(p.stages) > 0 {
        p.stages[0].input <- data
    }
}

// 获取输出
func (p *Pipeline) Output() <-chan interface{} {
    if len(p.stages) > 0 {
        return p.stages[len(p.stages)-1].output
    }
    return nil
}

// 获取错误通道
func (p *Pipeline) Errors() <-chan error {
    if len(p.stages) > 0 {
        return p.stages[len(p.stages)-1].errorChan
    }
    return nil
}

// 连接阶段
func (p *Pipeline) Connect() {
    for i := 0; i < len(p.stages)-1; i++ {
        current := p.stages[i]
        next := p.stages[i+1]

        go func() {
            for data := range current.output {
                next.input <- data
            }
            close(next.input)
        }()
    }
}

// 停止管道
func (p *Pipeline) Stop() {
    p.cancel()
    for _, stage := range p.stages {
        close(stage.input)
    }
}
```

### 分支管道模式

```go
// 分支管道
type BranchingPipeline struct {
    mainPipeline  *Pipeline
    branches     map[string]*Pipeline
    router        func(interface{}) string
    ctx           context.Context
    cancel        context.CancelFunc
}

// 创建分支管道
func NewBranchingPipeline(router func(interface{}) string) *BranchingPipeline {
    ctx, cancel := context.WithCancel(context.Background())
    return &BranchingPipeline{
        mainPipeline: NewPipeline(),
        branches:    make(map[string]*Pipeline),
        router:       router,
        ctx:          ctx,
        cancel:       cancel,
    }
}

// 添加分支
func (bp *BranchingPipeline) AddBranch(name string, pipeline *Pipeline) {
    bp.branches[name] = pipeline
}

// 启动分支管道
func (bp *BranchingPipeline) Start() {
    // 启动主管道
    bp.mainPipeline.Start()

    // 启动所有分支
    for _, branch := range bp.branches {
        branch.Start()
    }

    // 启动路由器
    go bp.routerWorker()
}

// 路由工作器
func (bp *BranchingPipeline) routerWorker() {
    for data := range bp.mainPipeline.Output() {
        branchName := bp.router(data)

        if branch, exists := bp.branches[branchName]; exists {
            branch.Input(data)
        } else {
            log.Printf("No branch found for: %s", branchName)
        }
    }
}

// 输入数据
func (bp *BranchingPipeline) Input(data interface{}) {
    bp.mainPipeline.Input(data)
}

// 获取分支输出
func (bp *BranchingPipeline) BranchOutput(name string) <-chan interface{} {
    if branch, exists := bp.branches[name]; exists {
        return branch.Output()
    }
    return nil
}

// 停止分支管道
func (bp *BranchingPipeline) Stop() {
    bp.cancel()
    bp.mainPipeline.Stop()
    for _, branch := range bp.branches {
        branch.Stop()
    }
}
```

## 超时和取消模式

### 超时控制模式

```go
// 超时控制器
type TimeoutController struct {
    timeout   time.Duration
    ctx       context.Context
    cancel    context.CancelFunc
}

// 创建超时控制器
func NewTimeoutController(timeout time.Duration) *TimeoutController {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    return &TimeoutController{
        timeout: timeout,
        ctx:     ctx,
        cancel:  cancel,
    }
}

// 执行带超时的操作
func (tc *TimeoutController) Execute(task func() (interface{}, error)) (interface{}, error) {
    resultChan := make(chan interface{})
    errorChan := make(chan error)

    go func() {
        defer close(resultChan)
        defer close(errorChan)

        result, err := task()
        if err != nil {
            errorChan <- err
            return
        }
        resultChan <- result
    }()

    select {
    case result := <-resultChan:
        return result, nil
    case err := <-errorChan:
        return nil, err
    case <-tc.ctx.Done():
        return nil, tc.ctx.Err()
    }
}

// 取消超时
func (tc *TimeoutController) Cancel() {
    tc.cancel()
}
```

### 层级取消模式

```go
// 层级取消管理器
type HierarchicalCancelManager struct {
    parent    context.Context
    children  map[string]*HierarchicalCancelManager
    mutex     sync.RWMutex
}

// 创建层级取消管理器
func NewHierarchicalCancelManager(parent context.Context) *HierarchicalCancelManager {
    return &HierarchicalCancelManager{
        parent:   parent,
        children: make(map[string]*HierarchicalCancelManager),
    }
}

// 创建子管理器
func (hcm *HierarchicalCancelManager) CreateChild(name string) *HierarchicalCancelManager {
    hcm.mutex.Lock()
    defer hcm.mutex.Unlock()

    if child, exists := hcm.children[name]; exists {
        return child
    }

    child := NewHierarchicalCancelManager(hcm.parent)
    hcm.children[name] = child
    return child
}

// 取消特定分支
func (hcm *HierarchicalCancelManager) CancelBranch(name string) {
    hcm.mutex.RLock()
    defer hcm.mutex.RUnlock()

    if child, exists := hcm.children[name]; exists {
        child.CancelAll()
    }
}

// 取消所有
func (hcm *HierarchicalCancelManager) CancelAll() {
    hcm.mutex.RLock()
    defer hcm.mutex.RUnlock()

    for _, child := range hcm.children {
        child.CancelAll()
    }
}
```

## 错误处理模式

### 错误收集模式

```go
// 错误收集器
type ErrorCollector struct {
    errors   chan error
    collected []error
    ctx      context.Context
    cancel   context.CancelFunc
    wg       sync.WaitGroup
}

// 创建错误收集器
func NewErrorCollector(bufferSize int) *ErrorCollector {
    ctx, cancel := context.WithCancel(context.Background())
    return &ErrorCollector{
        errors:   make(chan error, bufferSize),
        collected: make([]error, 0),
        ctx:      ctx,
        cancel:   cancel,
    }
}

// 启动错误收集
func (ec *ErrorCollector) Start() {
    ec.wg.Add(1)
    go ec.collectErrors()
}

// 收集错误
func (ec *ErrorCollector) collectErrors() {
    defer ec.wg.Done()

    for {
        select {
        case err := <-ec.errors:
            ec.collected = append(ec.collected, err)
        case <-ec.ctx.Done():
            return
        }
    }
}

// 提交错误
func (ec *ErrorCollector) SubmitError(err error) {
    select {
    case ec.errors <- err:
    case <-ec.ctx.Done():
    }
}

// 获取所有错误
func (ec *ErrorCollector) GetErrors() []error {
    ec.mutex.RLock()
    defer ec.mutex.RUnlock()
    return ec.collected
}

// 停止收集
func (ec *ErrorCollector) Stop() {
    ec.cancel()
    ec.wg.Wait()
}
```

### 错误恢复模式

```go
// 错误恢复管理器
type ErrorRecoveryManager struct {
    recoveries map[string]RecoveryHandler
    logger     *log.Logger
}

// 恢复处理器类型
type RecoveryHandler func(error) error

// 创建错误恢复管理器
func NewErrorRecoveryManager() *ErrorRecoveryManager {
    return &ErrorRecoveryManager{
        recoveries: make(map[string]RecoveryHandler),
        logger:     log.Default(),
    }
}

// 注册恢复处理器
func (erm *ErrorRecoveryManager) RegisterRecovery(errorType string, handler RecoveryHandler) {
    erm.recoveries[errorType] = handler
}

// 处理错误
func (erm *ErrorRecoveryManager) HandleError(err error) error {
    errorType := erm.getErrorType(err)

    if handler, exists := erm.recoveries[errorType]; exists {
        recovered := handler(err)
        if recovered == nil {
            return nil
        }
        return recovered
    }

    return err
}

// 获取错误类型
func (erm *ErrorRecoveryManager) getErrorType(err error) string {
    switch err.(type) {
    case *net.Error:
        return "network"
    case *json.SyntaxError:
        return "json"
    case *sql.Error:
        return "database"
    default:
        return "general"
    }
}
```

## 资源池模式

### 连接池模式

```go
// 连接池配置
type ConnectionPoolConfig struct {
    InitialSize   int
    MaxSize       int
    MaxIdle       int
    MaxLifetime   time.Duration
    IdleTimeout   time.Duration
    Factory       func() (interface{}, error)
    Close         func(interface{}) error
    Ping          func(interface{}) error
}

// 连接池
type ConnectionPool struct {
    config      *ConnectionPoolConfig
    connections chan interface{}
    mutex       sync.Mutex
    created     int
}

// 创建连接池
func NewConnectionPool(config *ConnectionPoolConfig) (*ConnectionPool, error) {
    pool := &ConnectionPool{
        config:      config,
        connections: make(chan interface{}, config.MaxSize),
    }

    // 初始化连接
    for i := 0; i < config.InitialSize; i++ {
        conn, err := config.Factory()
        if err != nil {
            return nil, err
        }
        pool.connections <- conn
        pool.created++
    }

    return pool, nil
}

// 获取连接
func (cp *ConnectionPool) Get() (interface{}, error) {
    select {
    case conn := <-cp.connections:
        // 检查连接是否有效
        if cp.config.Ping != nil {
            if err := cp.config.Ping(conn); err != nil {
                cp.Close(conn)
                return cp.Get()
            }
        }
        return conn, nil
    default:
        // 池中没有可用连接，创建新连接
        cp.mutex.Lock()
        if cp.created < cp.config.MaxSize {
            conn, err := cp.config.Factory()
            if err != nil {
                cp.mutex.Unlock()
                return nil, err
            }
            cp.created++
            cp.mutex.Unlock()
            return conn, nil
        }
        cp.mutex.Unlock()

        // 等待连接释放
        select {
        case conn := <-cp.connections:
            return conn, nil
        case <-time.After(5 * time.Second):
            return nil, fmt.Errorf("connection pool timeout")
        }
    }
}

// 释放连接
func (cp *ConnectionPool) Put(conn interface{}) error {
    select {
    case cp.connections <- conn:
        return nil
    default:
        // 池已满，关闭连接
        return cp.Close(conn)
    }
}

// 关闭连接
func (cp *ConnectionPool) Close(conn interface{}) error {
    if cp.config.Close != nil {
        return cp.config.Close(conn)
    }
    return nil
}

// 关闭连接池
func (cp *ConnectionPool) CloseAll() error {
    cp.mutex.Lock()
    defer cp.mutex.Unlock()

    var err error
    for i := 0; i < cp.created; i++ {
        conn := <-cp.connections
        if closeErr := cp.Close(conn); closeErr != nil {
            err = closeErr
        }
    }

    return err
}
```

## 限流模式

### 令牌桶限流

```go
// 令牌桶限流器
type TokenBucket struct {
    capacity    int64
    tokens      int64
    refillRate  int64
    lastRefill  int64
    mutex       sync.Mutex
}

// 创建令牌桶
func NewTokenBucket(capacity, refillRate int64) *TokenBucket {
    return &TokenBucket{
        capacity:   capacity,
        tokens:     capacity,
        refillRate: refillRate,
        lastRefill: time.Now().UnixNano(),
    }
}

// 获取令牌
func (tb *TokenBucket) Acquire(count int64) bool {
    tb.mutex.Lock()
    defer tb.mutex.Unlock()

    now := time.Now().UnixNano()
    elapsed := now - tb.lastRefill

    // 补充令牌
    if elapsed > 0 {
        refill := (elapsed * tb.refillRate) / 1e9
        if refill > 0 {
            tb.tokens = min(tb.capacity, tb.tokens+refill)
            tb.lastRefill = now
        }
    }

    // 检查是否有足够的令牌
    if tb.tokens >= count {
        tb.tokens -= count
        return true
    }

    return false
}

// 等待获取令牌
func (tb *TokenBucket) AcquireWithWait(count int64, timeout time.Duration) bool {
    deadline := time.Now().Add(timeout)

    for time.Now().Before(deadline) {
        if tb.Acquire(count) {
            return true
        }
        time.Sleep(10 * time.Millisecond)
    }

    return false
}

func min(a, b int64) int64 {
    if a < b {
        return a
    }
    return b
}
```

### 滑动窗口限流

```go
// 滑动窗口限流器
type SlidingWindow struct {
    windowSize time.Duration
    maxCount   int64
    timestamps []int64
    mutex      sync.Mutex
}

// 创建滑动窗口限流器
func NewSlidingWindow(windowSize time.Duration, maxCount int64) *SlidingWindow {
    return &SlidingWindow{
        windowSize: windowSize,
        maxCount:   maxCount,
        timestamps: make([]int64, 0),
    }
}

// 检查是否允许通过
func (sw *SlidingWindow) Allow() bool {
    sw.mutex.Lock()
    defer sw.mutex.Unlock()

    now := time.Now().UnixNano()
    windowStart := now - sw.windowSize.Nanoseconds()

    // 清理过期的记录
    valid := make([]int64, 0)
    for _, ts := range sw.timestamps {
        if ts > windowStart {
            valid = append(valid, ts)
        }
    }
    sw.timestamps = valid

    // 检查是否超过限制
    if int64(len(sw.timestamps)) < sw.maxCount {
        sw.timestamps = append(sw.timestamps, now)
        return true
    }

    return false
}

// 获取当前计数
func (sw *SlidingWindow) Count() int64 {
    sw.mutex.Lock()
    defer sw.mutex.Unlock()

    now := time.Now().UnixNano()
    windowStart := now - sw.windowSize.Nanoseconds()

    count := int64(0)
    for _, ts := range sw.timestamps {
        if ts > windowStart {
            count++
        }
    }

    return count
}
```

## 性能优化技巧

### Goroutine池优化

```go
// 高性能Goroutine池
type HighPerformancePool struct {
    workers    []*Worker
    taskQueue  chan *Task
    workerPool chan *Worker
    maxWorkers int
    minWorkers int
    ctx        context.Context
    cancel     context.CancelFunc
    wg         sync.WaitGroup
    stats      *PoolStats
}

// 创建高性能池
func NewHighPerformancePool(minWorkers, maxWorkers int) *HighPerformancePool {
    ctx, cancel := context.WithCancel(context.Background())

    pool := &HighPerformancePool{
        taskQueue:  make(chan *Task, 1000),
        workerPool: make(chan *Worker, maxWorkers),
        maxWorkers: maxWorkers,
        minWorkers: minWorkers,
        ctx:        ctx,
        cancel:     cancel,
        stats:      &PoolStats{},
    }

    // 初始化工作器
    for i := 0; i < minWorkers; i++ {
        worker := pool.createWorker(i)
        pool.workers = append(pool.workers, worker)
        pool.workerPool <- worker
    }

    // 启动调度器
    go pool.scheduler()

    return pool
}

// 创建工作器
func (hpp *HighPerformancePool) createWorker(id int) *Worker {
    worker := &Worker{
        id:   id,
        pool: hpp,
    }

    hpp.wg.Add(1)
    go worker.run()

    return worker
}

// 调度器
func (hpp *HighPerformancePool) scheduler() {
    for {
        select {
        case task := <-hpp.taskQueue:
            // 获取空闲工作器
            select {
            case worker := <-hpp.workerPool:
                worker.task <- task
            default:
                // 没有空闲工作器，创建新的
                if len(hpp.workers) < hpp.maxWorkers {
                    worker := hpp.createWorker(len(hpp.workers))
                    hpp.workers = append(hpp.workers, worker)
                    worker.task <- task
                } else {
                    // 等待工作器空闲
                    worker := <-hpp.workerPool
                    worker.task <- task
                }
            }
        case <-hpp.ctx.Done():
            return
        }
    }
}

// 提交任务
func (hpp *HighPerformancePool) Submit(task *Task) error {
    select {
    case hpp.taskQueue <- task:
        return nil
    case <-hpp.ctx.Done():
        return hpp.ctx.Err()
    }
}
```

### 内存优化技巧

```go
// 内存优化的Goroutine通信
type OptimizedCommunication struct {
    bufferPool *sync.Pool
    messagePool *sync.Pool
}

// 创建优化通信器
func NewOptimizedCommunication() *OptimizedCommunication {
    return &OptimizedCommunication{
        bufferPool: &sync.Pool{
            New: func() interface{} {
                return make([]byte, 1024)
            },
        },
        messagePool: &sync.Pool{
            New: func() interface{} {
                return &Message{}
            },
        },
    }
}

// 获取缓冲区
func (oc *OptimizedCommunication) GetBuffer() []byte {
    return oc.bufferPool.Get().([]byte)
}

// 释放缓冲区
func (oc *OptimizedCommunication) PutBuffer(buf []byte) {
    oc.bufferPool.Put(buf[:0])
}

// 获取消息
func (oc *OptimizedCommunication) GetMessage() *Message {
    return oc.messagePool.Get().(*Message)
}

// 释放消息
func (oc *OptimizedCommunication) PutMessage(msg *Message) {
    msg.Reset()
    oc.messagePool.Put(msg)
}
```

## 监控和调试

### Goroutine监控

```go
// Goroutine监控器
type GoroutineMonitor struct {
    stats      *GoroutineStats
    ticker     *time.Ticker
    threshold  int
    logger     *log.Logger
}

// Goroutine统计
type GoroutineStats struct {
    Count       int64
    MaxCount    int64
    MinCount    int64
    AvgCount    float64
    Samples     []int64
    mutex       sync.RWMutex
}

// 创建监控器
func NewGoroutineMonitor(threshold int) *GoroutineMonitor {
    return &GoroutineMonitor{
        stats:     &GoroutineStats{Samples: make([]int64, 0)},
        ticker:    time.NewTicker(5 * time.Second),
        threshold: threshold,
        logger:    log.Default(),
    }
}

// 启动监控
func (gm *GoroutineMonitor) Start() {
    go gm.monitor()
}

// 监控Goroutine数量
func (gm *GoroutineMonitor) monitor() {
    for range gm.ticker.C {
        count := runtime.NumGoroutine()
        gm.stats.Update(count)

        if count > gm.threshold {
            gm.logger.Printf("Warning: Goroutine count %d exceeds threshold %d", count, gm.threshold)
        }
    }
}

// 更新统计
func (gs *GoroutineStats) Update(count int64) {
    gs.mutex.Lock()
    defer gs.mutex.Unlock()

    gs.Count = count
    gs.Samples = append(gs.Samples, count)

    if len(gs.Samples) > 100 {
        gs.Samples = gs.Samples[1:]
    }

    gs.MaxCount = max(gs.MaxCount, count)
    gs.MinCount = min(gs.MinCount, count)

    var sum int64
    for _, sample := range gs.Samples {
        sum += sample
    }
    gs.AvgCount = float64(sum) / float64(len(gs.Samples))
}
```

### 性能分析

```go
// 性能分析器
type PerformanceProfiler struct {
    profiles   map[string]*Profile
    mutex      sync.RWMutex
    enabled    bool
}

// 性能配置文件
type Profile struct {
    Name       string
    StartTime  time.Time
    EndTime    time.Time
    Duration   time.Duration
    Calls      int64
    TotalTime  time.Duration
    AvgTime    time.Duration
    MinTime    time.Duration
    MaxTime    time.Duration
    Samples    []time.Duration
}

// 创建性能分析器
func NewPerformanceProfiler() *PerformanceProfiler {
    return &PerformanceProfiler{
        profiles: make(map[string]*Profile),
        enabled:  true,
    }
}

// 开始分析
func (pp *PerformanceProfiler) StartProfile(name string) func() {
    if !pp.enabled {
        return func() {}
    }

    start := time.Now()

    pp.mutex.Lock()
    if _, exists := pp.profiles[name]; !exists {
        pp.profiles[name] = &Profile{
            Name:      name,
            MinTime:   time.Hour,
            Samples:   make([]time.Duration, 0),
        }
    }
    pp.mutex.Unlock()

    return func() {
        duration := time.Since(start)

        pp.mutex.Lock()
        defer pp.mutex.Unlock()

        profile := pp.profiles[name]
        profile.Calls++
        profile.TotalTime += duration
        profile.AvgTime = time.Duration(int64(profile.TotalTime) / profile.Calls)
        profile.MinTime = min(profile.MinTime, duration)
        profile.MaxTime = max(profile.MaxTime, duration)
        profile.Samples = append(profile.Samples, duration)

        if len(profile.Samples) > 1000 {
            profile.Samples = profile.Samples[1:]
        }
    }
}

// 获取性能报告
func (pp *PerformanceProfiler) GetReport() map[string]*Profile {
    pp.mutex.RLock()
    defer pp.mutex.RUnlock()

    report := make(map[string]*Profile)
    for name, profile := range pp.profiles {
        report[name] = profile
    }

    return report
}
```

## 最佳实践总结

### Goroutine使用最佳实践

1. **控制并发数量**：使用工作池模式限制Goroutine数量
2. **正确处理错误**：使用专门的错误收集和处理机制
3. **优雅关闭**：使用Context实现优雅的Goroutine关闭
4. **资源管理**：避免资源泄漏，确保资源正确释放
5. **监控和调试**：建立完善的监控体系

### 性能优化建议

1. **减少Goroutine创建开销**：使用对象池和复用机制
2. **优化Channel使用**：合理设置缓冲区大小，避免阻塞
3. **使用sync.Pool**：减少内存分配和GC压力
4. **批处理**：对于大量小任务，考虑批处理
5. **避免锁竞争**：使用无锁数据结构或减少锁粒度

### 错误处理策略

1. **集中错误处理**：使用错误收集器统一管理错误
2. **错误恢复机制**：实现错误自动恢复策略
3. **超时控制**：为长时间运行的任务设置超时
4. **重试机制**：对于临时性错误实现自动重试
5. **监控和告警**：建立错误监控和告警机制

通过实施这些模式和最佳实践，可以构建高效、可靠、可维护的Go并发系统。关键是要根据具体的业务场景选择合适的模式，并进行充分的测试和优化。