# Gin异步处理模式指南

本文档详细介绍Gin框架中的异步处理模式，涵盖消息队列、任务队列、事件驱动等异步处理技术。

## 1. 异步处理概述

### 1.1 异步处理的优势
- **提高响应速度**：快速响应用户请求，耗时任务异步处理
- **提升吞吐量**：处理更多并发请求
- **资源优化**：合理利用系统资源，避免阻塞
- **可靠性提升**：任务失败重试，保证数据一致性
- **系统解耦**：服务间通过消息队列解耦

### 1.2 异步处理场景
- **耗时操作**：文件处理、图片压缩、数据导入导出
- **外部调用**：第三方API调用、邮件发送、短信通知
- **批量处理**：数据统计、报表生成、批量更新
- **事件处理**：用户行为追踪、状态变更通知
- **定时任务**：数据清理、缓存预热、健康检查

### 1.3 异步处理架构
```
HTTP请求 → Gin应用 → 消息队列 → 工作进程 → 结果存储
    ↓            ↓          ↓         ↓         ↓
   路由处理    任务分发    消息持久化   任务执行   结果通知
```

## 2. 基础异步处理

### 2.1 Goroutine异步处理
```go
// 基础Goroutine异步处理
package main

import (
    "fmt"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
)

// 异步任务结构
type AsyncTask struct {
    ID        string
    TaskType  string
    Payload   interface{}
    Status    string
    CreatedAt time.Time
    StartedAt *time.Time
    CompletedAt *time.Time
    Result    interface{}
    Error     error
}

// 任务管理器
type TaskManager struct {
    tasks    map[string]*AsyncTask
    mu       sync.RWMutex
}

func NewTaskManager() *TaskManager {
    return &TaskManager{
        tasks: make(map[string]*AsyncTask),
    }
}

func (m *TaskManager) CreateTask(taskType string, payload interface{}) *AsyncTask {
    task := &AsyncTask{
        ID:        generateUUID(),
        TaskType:  taskType,
        Payload:   payload,
        Status:    "pending",
        CreatedAt: time.Now(),
    }

    m.mu.Lock()
    m.tasks[task.ID] = task
    m.mu.Unlock()

    return task
}

func (m *TaskManager) GetTask(id string) (*AsyncTask, bool) {
    m.mu.RLock()
    defer m.mu.RUnlock()

    task, exists := m.tasks[id]
    return task, exists
}

func (m *TaskManager) UpdateTask(id string, status string, result interface{}, err error) {
    m.mu.Lock()
    defer m.mu.Unlock()

    if task, exists := m.tasks[id]; exists {
        task.Status = status
        task.Result = result
        task.Error = err

        now := time.Now()
        if status == "running" {
            task.StartedAt = &now
        } else if status == "completed" || status == "failed" {
            task.CompletedAt = &now
        }
    }
}

// 异步处理中间件
func AsyncMiddleware(taskManager *TaskManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查是否是异步请求
        if c.GetHeader("X-Async") != "true" {
            c.Next()
            return
        }

        // 创建异步任务
        task := taskManager.CreateTask("http_request", map[string]interface{}{
            "method": c.Request.Method,
            "path":   c.Request.URL.Path,
            "headers": c.Request.Header,
            "body":    c.Request.Body,
        })

        // 立即返回任务ID
        c.JSON(202, gin.H{
            "task_id": task.ID,
            "status":  "accepted",
            "message": "Task is being processed",
        })

        // 异步处理请求
        go func() {
            taskManager.UpdateTask(task.ID, "running", nil, nil)

            // 模拟处理时间
            time.Sleep(2 * time.Second)

            // 创建新的上下文来处理请求
            req := c.Request.Clone(c.Request.Context())
            w := &responseRecorder{headers: make(http.Header)}

            // 执行后续中间件和处理函数
            c.Request = req
            c.Writer = w
            c.Next()

            // 记录结果
            taskManager.UpdateTask(task.ID, "completed", gin.H{
                "status": w.status,
                "headers": w.headers,
                "body": w.body.String(),
            }, nil)
        }()

        c.Abort()
    }
}

// 响应记录器
type responseRecorder struct {
    status  int
    headers http.Header
    body    bytes.Buffer
    gin.ResponseWriter
}

func (r *responseRecorder) WriteHeader(code int) {
    r.status = code
    r.ResponseWriter.WriteHeader(code)
}

func (r *responseRecorder) Write(data []byte) (int, error) {
    r.body.Write(data)
    return r.ResponseWriter.Write(data)
}

func (r *responseRecorder) Header() http.Header {
    return r.headers
}

// 任务查询端点
func GetTaskHandler(taskManager *TaskManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        taskID := c.Param("id")
        task, exists := taskManager.GetTask(taskID)

        if !exists {
            c.JSON(404, gin.H{"error": "Task not found"})
            return
        }

        c.JSON(200, task)
    }
}

func main() {
    // 创建任务管理器
    taskManager := NewTaskManager()

    // 创建Gin引擎
    r := gin.Default()

    // 中间件
    r.Use(AsyncMiddleware(taskManager))

    // 路由
    r.GET("/async-test", func(c *gin.Context) {
        time.Sleep(2 * time.Second) // 模拟耗时操作
        c.JSON(200, gin.H{
            "message": "Task completed",
            "time":    time.Now(),
        })
    })

    r.GET("/tasks/:id", GetTaskHandler(taskManager))

    // 启动服务器
    r.Run(":8080")
}
```

### 2.2 Channel异步处理
```go
// Channel异步处理
type ChannelProcessor struct {
    taskChan    chan Task
    workers     []*Worker
    resultChan  chan TaskResult
    config      *ProcessorConfig
}

type Task struct {
    ID      string
    Type    string
    Payload interface{}
}

type TaskResult struct {
    TaskID  string
    Result  interface{}
    Error   error
    Timing  time.Duration
}

type ProcessorConfig struct {
    WorkerCount    int
    QueueSize      int
    Timeout        time.Duration
    RetryCount     int
}

type Worker struct {
    id         int
    taskChan   <-chan Task
    resultChan chan<- TaskResult
    quit       chan struct{}
}

func NewChannelProcessor(config *ProcessorConfig) *ChannelProcessor {
    processor := &ChannelProcessor{
        taskChan:   make(chan Task, config.QueueSize),
        resultChan: make(chan TaskResult, config.QueueSize),
        config:     config,
    }

    // 创建工作协程
    for i := 0; i < config.WorkerCount; i++ {
        worker := &Worker{
            id:         i,
            taskChan:   processor.taskChan,
            resultChan: processor.resultChan,
            quit:       make(chan struct{}),
        }
        processor.workers = append(processor.workers, worker)
        go worker.Start()
    }

    return processor
}

func (w *Worker) Start() {
    for {
        select {
        case task := <-w.taskChan:
            start := time.Now()
            result, err := w.processTask(task)
            duration := time.Since(start)

            w.resultChan <- TaskResult{
                TaskID: task.ID,
                Result: result,
                Error:  err,
                Timing: duration,
            }
        case <-w.quit:
            return
        }
    }
}

func (w *Worker) processTask(task Task) (interface{}, error) {
    switch task.Type {
    case "email":
        return w.sendEmail(task.Payload)
    case "image_process":
        return w.processImage(task.Payload)
    case "data_export":
        return w.exportData(task.Payload)
    default:
        return nil, fmt.Errorf("unknown task type: %s", task.Type)
    }
}

func (w *Worker) sendEmail(payload interface{}) (interface{}, error) {
    // 模拟邮件发送
    time.Sleep(1 * time.Second)
    return map[string]interface{}{
        "message": "Email sent successfully",
        "to":      payload,
    }, nil
}

func (w *Worker) processImage(payload interface{}) (interface{}, error) {
    // 模拟图片处理
    time.Sleep(3 * time.Second)
    return map[string]interface{}{
        "message": "Image processed successfully",
        "file":    payload,
    }, nil
}

func (w *Worker) exportData(payload interface{}) (interface{}, error) {
    // 模拟数据导出
    time.Sleep(5 * time.Second)
    return map[string]interface{}{
        "message": "Data exported successfully",
        "records": 1000,
    }, nil
}

func (p *ChannelProcessor) SubmitTask(taskType string, payload interface{}) (string, error) {
    task := Task{
        ID:      generateUUID(),
        Type:    taskType,
        Payload: payload,
    }

    select {
    case p.taskChan <- task:
        return task.ID, nil
    case <-time.After(p.config.Timeout):
        return "", fmt.Errorf("task submission timeout")
    }
}

func (p *ChannelProcessor) GetResult(taskID string, timeout time.Duration) (*TaskResult, error) {
    timeoutChan := time.After(timeout)

    for {
        select {
        case result := <-p.resultChan:
            if result.TaskID == taskID {
                return &result, nil
            }
        case <-timeoutChan:
            return nil, fmt.Errorf("result timeout")
        }
    }
}

func (p *ChannelProcessor) Stop() {
    for _, worker := range p.workers {
        close(worker.quit)
    }
    close(p.taskChan)
    close(p.resultChan)
}

// Gin中间件
func ChannelProcessorMiddleware(processor *ChannelProcessor) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查是否需要异步处理
        taskType := c.GetHeader("X-Task-Type")
        if taskType == "" {
            c.Next()
            return
        }

        // 提交任务
        payload := map[string]interface{}{
            "method":  c.Request.Method,
            "path":    c.Request.URL.Path,
            "headers": c.Request.Header,
            "query":   c.Request.URL.Query(),
        }

        taskID, err := processor.SubmitTask(taskType, payload)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        // 返回任务ID
        c.JSON(202, gin.H{
            "task_id": taskID,
            "status":  "queued",
            "message": "Task has been queued for processing",
        })

        c.Abort()
    }
}
```

## 3. 消息队列集成

### 3.1 Go标准库消息队列

```go
// 标准库实现的内存队列
type MemoryQueue struct {
    tasks   chan Task
    workers []*Worker
    wg      sync.WaitGroup
    config  *QueueConfig
}

type QueueConfig struct {
    WorkerCount int
    QueueSize   int
    Timeout     time.Duration
}

func NewMemoryQueue(config *QueueConfig) *MemoryQueue {
    return &MemoryQueue{
        tasks:  make(chan Task, config.QueueSize),
        config: config,
    }
}

func (q *MemoryQueue) Start() {
    for i := 0; i < q.config.WorkerCount; i++ {
        worker := &Worker{
            id:     i,
            tasks:  q.tasks,
            wg:     &q.wg,
            quit:   make(chan struct{}),
            config: q.config,
        }
        q.workers = append(q.workers, worker)
        q.wg.Add(1)
        go worker.Start()
    }
}

func (q *MemoryQueue) Stop() {
    for _, worker := range q.workers {
        close(worker.quit)
    }
    q.wg.Wait()
}

func (q *MemoryQueue) Enqueue(task Task) error {
    select {
    case q.tasks <- task:
        return nil
    case <-time.After(q.config.Timeout):
        return fmt.Errorf("queue timeout")
    }
}

func (q *MemoryQueue) EnqueueBatch(tasks []Task) error {
    for _, task := range tasks {
        if err := q.Enqueue(task); err != nil {
            return err
        }
    }
    return nil
}

// 优先级队列实现
type PriorityQueue struct {
    queues map[int]chan Task  // 优先级 -> 任务队列
    workers []*PriorityWorker
    wg      sync.WaitGroup
    config  *PriorityQueueConfig
}

type PriorityQueueConfig struct {
    WorkerCount int
    QueueSize   int
    Priorities  []int  // 支持的优先级
}

type PriorityTask struct {
    Task
    Priority int
}

func NewPriorityQueue(config *PriorityQueueConfig) *PriorityQueue {
    queues := make(map[int]chan Task)
    for _, priority := range config.Priorities {
        queues[priority] = make(chan Task, config.QueueSize)
    }

    return &PriorityQueue{
        queues: queues,
        config: config,
    }
}

func (q *PriorityQueue) Enqueue(task Task, priority int) error {
    if _, exists := q.queues[priority]; !exists {
        return fmt.Errorf("invalid priority: %d", priority)
    }

    select {
    case q.queues[priority] <- task:
        return nil
    case <-time.After(5 * time.Second):
        return fmt.Errorf("queue timeout")
    }
}

func (q *PriorityQueue) Start() {
    for i := 0; i < q.config.WorkerCount; i++ {
        worker := &PriorityWorker{
            id:      i,
            queues:  q.queues,
            wg:      &q.wg,
            quit:    make(chan struct{}),
            config:  q.config,
        }
        q.workers = append(q.workers, worker)
        q.wg.Add(1)
        go worker.Start()
    }
}

type PriorityWorker struct {
    id      int
    queues  map[int]chan Task
    wg      *sync.WaitGroup
    quit    chan struct{}
    config  *PriorityQueueConfig
}

func (w *PriorityWorker) Start() {
    defer w.wg.Done()

    for {
        select {
        case <-w.quit:
            return
        default:
            // 按优先级从高到低检查队列
            for _, priority := range w.config.Priorities {
                select {
                case task := <-w.queues[priority]:
                    w.processTask(task)
                    continue
                default:
                }
            }
            // 如果没有任务，稍微等待
            time.Sleep(10 * time.Millisecond)
        }
    }
}

// 有界队列（防止内存溢出）
type BoundedQueue struct {
    tasks   chan Task
    reject  chan Task
    workers []*Worker
    wg      sync.WaitGroup
    config  *BoundedQueueConfig
    metrics *QueueMetrics
}

type BoundedQueueConfig struct {
    WorkerCount    int
    QueueSize      int
    RejectHandler  func(Task) error
}

type QueueMetrics struct {
    Enqueued       int64
    Dequeued       int64
    Rejected       int64
    Processed      int64
    Failed         int64
}

func NewBoundedQueue(config *BoundedQueueConfig) *BoundedQueue {
    return &BoundedQueue{
        tasks:   make(chan Task, config.QueueSize),
        reject:  make(chan Task, config.QueueSize*2),
        workers: make([]*Worker, 0, config.WorkerCount),
        wg:      sync.WaitGroup{},
        config:  config,
        metrics: &QueueMetrics{},
    }
}

func (q *BoundedQueue) Start() {
    // 启动工作协程
    for i := 0; i < q.config.WorkerCount; i++ {
        worker := &Worker{
            id:     i,
            tasks:  q.tasks,
            wg:     &q.wg,
            quit:   make(chan struct{}),
            config: &QueueConfig{
                WorkerCount: 1,
                QueueSize:   q.config.QueueSize,
                Timeout:     30 * time.Second,
            },
        }
        q.workers = append(q.workers, worker)
        q.wg.Add(1)
        go worker.Start()
    }

    // 启动拒绝任务处理器
    go q.processRejectedTasks()
}

func (q *BoundedQueue) Enqueue(task Task) error {
    select {
    case q.tasks <- task:
        atomic.AddInt64(&q.metrics.Enqueued, 1)
        return nil
    default:
        // 队列满，尝试放入拒绝队列
        select {
        case q.reject <- task:
            atomic.AddInt64(&q.metrics.Rejected, 1)
            return fmt.Errorf("queue full, task rejected")
        default:
            // 拒绝队列也满，调用拒绝处理器
            if q.config.RejectHandler != nil {
                return q.config.RejectHandler(task)
            }
            return fmt.Errorf("queue full and reject queue full")
        }
    }
}

func (q *BoundedQueue) processRejectedTasks() {
    for task := range q.reject {
        if q.config.RejectHandler != nil {
            if err := q.config.RejectHandler(task); err != nil {
                log.Printf("Reject handler error: %v", err)
            }
        }
        // 重试入队
        if err := q.Enqueue(task); err != nil {
            log.Printf("Failed to requeue rejected task: %v", err)
        }
    }
}
```

### 3.2 Redis消息队列

```go
// Redis列表实现的基础队列
type RedisListQueue struct {
    client      *redis.Client
    queueName   string
    workerCount int
    workers     []*RedisWorker
    handlers    map[string]TaskHandler
    mu          sync.RWMutex
    config      *RedisQueueConfig
}

type RedisQueueConfig struct {
    BlockingTimeout time.Duration
    MaxRetries      int
    RetryDelay      time.Duration
    DeadLetterQueue string
}

func NewRedisListQueue(client *redis.Client, queueName string, workerCount int, config *RedisQueueConfig) *RedisListQueue {
    if config == nil {
        config = &RedisQueueConfig{
            BlockingTimeout: 30 * time.Second,
            MaxRetries:      3,
            RetryDelay:      5 * time.Second,
        }
    }

    return &RedisListQueue{
        client:      client,
        queueName:   queueName,
        workerCount: workerCount,
        handlers:    make(map[string]TaskHandler),
        config:      config,
    }
}

func (q *RedisListQueue) RegisterHandler(taskType string, handler TaskHandler) {
    q.mu.Lock()
    defer q.mu.Unlock()
    q.handlers[taskType] = handler
}

func (q *RedisListQueue) Start() {
    for i := 0; i < q.workerCount; i++ {
        worker := &RedisWorker{
            id:        i,
            client:    q.client,
            queueName: q.queueName,
            handlers:  q.handlers,
            config:    q.config,
            quit:      make(chan struct{}),
        }
        q.workers = append(q.workers, worker)
        go worker.Start()
    }
}

func (q *RedisListQueue) Enqueue(taskType string, payload interface{}) (string, error) {
    task := Task{
        ID:      generateUUID(),
        Type:    taskType,
        Payload: payload,
    }

    taskData, err := json.Marshal(task)
    if err != nil {
        return "", err
    }

    err = q.client.LPush(q.ctx, q.queueName, taskData).Err()
    if err != nil {
        return "", err
    }

    return task.ID, nil
}

func (q *RedisListQueue) EnqueueBatch(tasks []Task) error {
    pipe := q.client.Pipeline()

    for _, task := range tasks {
        taskData, err := json.Marshal(task)
        if err != nil {
            return err
        }
        pipe.LPush(q.ctx, q.queueName, taskData)
    }

    _, err := pipe.Exec(q.ctx)
    return err
}

// Redis Stream实现（推荐用于生产环境）
type RedisStreamQueue struct {
    client      *redis.Client
    streamName  string
    groupName   string
    consumer    string
    workerCount int
    workers     []*RedisStreamWorker
    handlers    map[string]TaskHandler
    mu          sync.RWMutex
    config      *RedisStreamConfig
}

type RedisStreamConfig struct {
    MaxLen           int64
    Approx           bool
    BlockTime        time.Duration
    ConsumerTimeout time.Duration
}

func NewRedisStreamQueue(client *redis.Client, streamName, groupName string, workerCount int, config *RedisStreamConfig) *RedisStreamQueue {
    if config == nil {
        config = &RedisStreamConfig{
            MaxLen:     10000,
            Approx:     true,
            BlockTime:  5 * time.Second,
        }
    }

    consumer := fmt.Sprintf("consumer-%d", time.Now().UnixNano())

    return &RedisStreamQueue{
        client:      client,
        streamName:  streamName,
        groupName:   groupName,
        consumer:    consumer,
        workerCount: workerCount,
        handlers:    make(map[string]TaskHandler),
        config:      config,
    }
}

func (q *RedisStreamQueue) Initialize() error {
    // 创建消费者组
    err := q.client.XGroupCreateMkStream(
        q.ctx, q.streamName, q.groupName, "0",
    ).Err()

    if err != nil && !strings.Contains(err.Error(), "BUSYGROUP") {
        return err
    }

    return nil
}

func (q *RedisStreamQueue) Start() error {
    if err := q.Initialize(); err != nil {
        return err
    }

    for i := 0; i < q.workerCount; i++ {
        worker := &RedisStreamWorker{
            id:          i,
            client:      q.client,
            streamName:  q.streamName,
            groupName:   q.groupName,
            consumer:    fmt.Sprintf("%s-%d", q.consumer, i),
            handlers:    q.handlers,
            config:      q.config,
            quit:        make(chan struct{}),
        }
        q.workers = append(q.workers, worker)
        go worker.Start()
    }

    return nil
}

func (q *RedisStreamQueue) Enqueue(taskType string, payload interface{}) (string, error) {
    task := Task{
        ID:      generateUUID(),
        Type:    taskType,
        Payload: payload,
    }

    values := map[string]interface{}{
        "task_id": task.ID,
        "type":    task.Type,
        "payload": task.Payload,
        "created": time.Now().Unix(),
    }

    // 使用XADD添加到流
    result, err := q.client.XAdd(q.ctx, &redis.XAddArgs{
        Stream: q.streamName,
        Values: values,
        MaxLen: q.config.MaxLen,
        Approx: q.config.Approx,
    }).Result()

    if err != nil {
        return "", err
    }

    return task.ID, nil
}

// Redis PubSub实现（实时消息）
type RedisPubSubQueue struct {
    client    *redis.Client
    channel   string
    subscriber *redis.PubSub
    handlers  map[string]TaskHandler
    mu        sync.RWMutex
    running   bool
}

func NewRedisPubSubQueue(client *redis.Client, channel string) *RedisPubSubQueue {
    return &RedisPubSubQueue{
        client:   client,
        channel:  channel,
        handlers: make(map[string]TaskHandler),
    }
}

func (q *RedisPubSubQueue) Start() error {
    q.subscriber = q.client.Subscribe(q.ctx, q.channel)
    q.running = true

    go q.listen()

    return nil
}

func (q *RedisPubSubQueue) Publish(taskType string, payload interface{}) error {
    task := Task{
        ID:      generateUUID(),
        Type:    taskType,
        Payload: payload,
    }

    taskData, err := json.Marshal(task)
    if err != nil {
        return err
    }

    return q.client.Publish(q.ctx, q.channel, taskData).Err()
}

func (q *RedisPubSubQueue) Subscribe(taskType string, handler TaskHandler) {
    q.mu.Lock()
    defer q.mu.Unlock()
    q.handlers[taskType] = handler
}

func (q *RedisPubSubQueue) listen() {
    for q.running {
        msg, err := q.subscriber.ReceiveMessage(q.ctx)
        if err != nil {
            if err == context.Canceled {
                return
            }
            log.Printf("PubSub receive error: %v", err)
            continue
        }

        var task Task
        if err := json.Unmarshal([]byte(msg.Payload), &task); err != nil {
            log.Printf("Failed to unmarshal task: %v", err)
            continue
        }

        q.mu.RLock()
        handler, exists := q.handlers[task.Type]
        q.mu.RUnlock()

        if exists {
            go func(t Task) {
                defer func() {
                    if r := recover(); r != nil {
                        log.Printf("Handler panic: %v", r)
                    }
                }()
                handler(t.Payload)
            }(task)
        }
    }
}

// Redis延迟队列
type RedisDelayedQueue struct {
    client      *redis.Client
    queueName   string
    scheduleSet string
    workers     []*RedisDelayedWorker
    handlers    map[string]TaskHandler
    mu          sync.RWMutex
}

func NewRedisDelayedQueue(client *redis.Client, queueName string) *RedisDelayedQueue {
    return &RedisDelayedQueue{
        client:      client,
        queueName:   queueName,
        scheduleSet: queueName + ":schedule",
        handlers:    make(map[string]TaskHandler),
    }
}

func (q *RedisDelayedQueue) EnqueueDelayed(taskType string, payload interface{}, delay time.Duration) (string, error) {
    task := Task{
        ID:      generateUUID(),
        Type:    taskType,
        Payload: payload,
    }

    taskData, err := json.Marshal(task)
    if err != nil {
        return "", err
    }

    // 计算执行时间
    executeAt := time.Now().Add(delay)
    score := float64(executeAt.Unix())

    // 添加到有序集合
    err = q.client.ZAdd(q.ctx, q.scheduleSet, &redis.Z{
        Score:  score,
        Member: taskData,
    }).Err()

    if err != nil {
        return "", err
    }

    return task.ID, nil
}

func (q *RedisDelayedQueue) StartWorker(workerCount int) {
    for i := 0; i < workerCount; i++ {
        worker := &RedisDelayedWorker{
            id:          i,
            client:      q.client,
            queueName:   q.queueName,
            scheduleSet: q.scheduleSet,
            handlers:    q.handlers,
            quit:        make(chan struct{}),
        }
        q.workers = append(q.workers, worker)
        go worker.Start()
    }
}

type RedisDelayedWorker struct {
    id          int
    client      *redis.Client
    queueName   string
    scheduleSet string
    handlers    map[string]TaskHandler
    quit        chan struct{}
}

func (w *RedisDelayedWorker) Start() {
    ticker := time.NewTicker(1 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            w.checkScheduledTasks()
        case <-w.quit:
            return
        }
    }
}

func (w *RedisDelayedWorker) checkScheduledTasks() {
    now := time.Now().Unix()

    // 使用Lua脚本原子性地获取到期的任务
    script := `
        local tasks = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1], 'LIMIT', 0, 10)
        local removed = {}

        for i, task in ipairs(tasks) do
            if redis.call('ZREM', KEYS[1], task) == 1 then
                table.insert(removed, task)
            end
        end

        return removed
    `

    result, err := w.client.Eval(w.ctx, script, []string{w.scheduleSet}, now).Result()
    if err != nil {
        log.Printf("Worker %d: Failed to get scheduled tasks: %v", w.id, err)
        return
    }

    tasks, ok := result.([]interface{})
    if !ok {
        return
    }

    // 处理到期的任务
    for _, taskData := range tasks {
        var task Task
        if err := json.Unmarshal([]byte(taskData.(string)), &task); err != nil {
            log.Printf("Worker %d: Failed to unmarshal task: %v", w.id, err)
            continue
        }

        w.processTask(task)
    }
}

// Redis可靠队列（确认机制）
type RedisReliableQueue struct {
    client      *redis.Client
    queueName   string
    processing  string
    workerCount int
    workers     []*RedisReliableWorker
    handlers    map[string]TaskHandler
    mu          sync.RWMutex
}

func NewRedisReliableQueue(client *redis.Client, queueName string, workerCount int) *RedisReliableQueue {
    return &RedisReliableQueue{
        client:     client,
        queueName:  queueName,
        processing: queueName + ":processing",
        workerCount: workerCount,
        handlers:   make(map[string]TaskHandler),
    }
}

func (q *RedisReliableQueue) Enqueue(taskType string, payload interface{}) (string, error) {
    task := Task{
        ID:      generateUUID(),
        Type:    taskType,
        Payload: payload,
    }

    taskData, err := json.Marshal(task)
    if err != nil {
        return "", err
    }

    err = q.client.LPush(q.ctx, q.queueName, taskData).Err()
    if err != nil {
        return "", err
    }

    return task.ID, nil
}

func (q *RedisReliableQueue) Start() {
    for i := 0; i < q.workerCount; i++ {
        worker := &RedisReliableWorker{
            id:         i,
            client:     q.client,
            queueName:  q.queueName,
            processing: q.processing,
            handlers:   q.handlers,
            quit:       make(chan struct{}),
        }
        q.workers = append(q.workers, worker)
        go worker.Start()
    }
}

type RedisReliableWorker struct {
    id         int
    client     *redis.Client
    queueName  string
    processing string
    handlers   map[string]TaskHandler
    quit       chan struct{}
}

func (w *RedisReliableWorker) Start() {
    for {
        select {
        case <-w.quit:
            return
        default:
            w.processNextTask()
        }
    }
}

func (w *RedisReliableWorker) processNextTask() {
    // 从主队列移动到处理队列
    result, err := w.client.BRPopLPush(
        w.ctx, w.queueName, w.processing, 30*time.Second,
    ).Result()

    if err != nil {
        if err != redis.Nil {
            log.Printf("Worker %d: BRPOPLPUSH error: %v", w.id, err)
        }
        return
    }

    // 处理任务
    var task Task
    if err := json.Unmarshal([]byte(result), &task); err != nil {
        log.Printf("Worker %d: Failed to unmarshal task: %v", w.id, err)
        return
    }

    // 处理任务
    err = w.executeTask(task)
    if err != nil {
        log.Printf("Worker %d: Task failed: %v", w.id, err)
        // 处理失败，移回主队列
        w.client.LPush(w.ctx, w.queueName, result)
        return
    }

    // 处理成功，从处理队列删除
    w.client.LRem(w.ctx, w.processing, 1, result)
}

// Gin集成
func RedisQueueMiddleware(queue *RedisListQueue) gin.HandlerFunc {
    return func(c *gin.Context) {
        taskType := c.GetHeader("X-Queue-Task")
        if taskType == "" {
            c.Next()
            return
        }

        // 构建任务载荷
        payload := map[string]interface{}{
            "method":  c.Request.Method,
            "path":    c.Request.URL.Path,
            "headers": c.Request.Header,
            "query":   c.Request.URL.Query(),
        }

        // 读取请求体
        if c.Request.Body != nil {
            body, err := io.ReadAll(c.Request.Body)
            if err == nil {
                payload["body"] = string(body)
                // 恢复请求体
                c.Request.Body = io.NopCloser(bytes.NewBuffer(body))
            }
        }

        // 入队任务
        taskID, err := queue.Enqueue(taskType, payload)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        // 返回任务信息
        c.JSON(202, gin.H{
            "task_id":    taskID,
            "queue":      queue.queueName,
            "status":     "queued",
            "check_url":  fmt.Sprintf("/queue/results/%s", taskID),
            "message":    "Task has been queued",
        })

        c.Abort()
    }
}
```

### 3.2 RabbitMQ消息队列
```go
// RabbitMQ消息队列
type RabbitMQQueue struct {
    connection  *amqp.Connection
    channel     *amqp.Channel
    queueName   string
    exchange    string
    routingKey  string
    workers     []*RabbitMQWorker
    handlers    map[string]TaskHandler
    mu          sync.RWMutex
}

type RabbitMQWorker struct {
    id         int
    channel    *amqp.Channel
    queue      amqp.Queue
    handlers   map[string]TaskHandler
    quit       chan struct{}
}

func NewRabbitMQQueue(url, queueName, exchange, routingKey string) (*RabbitMQQueue, error) {
    // 建立连接
    conn, err := amqp.Dial(url)
    if err != nil {
        return nil, err
    }

    // 创建通道
    ch, err := conn.Channel()
    if err != nil {
        return nil, err
    }

    // 声明交换机
    err = ch.ExchangeDeclare(
        exchange,
        "direct", // 交换机类型
        true,     // 持久化
        false,    // 自动删除
        false,    // 内部使用
        false,    // 等待确认
        nil,      // 参数
    )
    if err != nil {
        return nil, err
    }

    // 声明队列
    q, err := ch.QueueDeclare(
        queueName,
        true,  // 持久化
        false, // 自动删除
        false, // 排他性
        false, // 等待确认
        nil,   // 参数
    )
    if err != nil {
        return nil, err
    }

    // 绑定队列到交换机
    err = ch.QueueBind(
        q.Name,
        routingKey,
        exchange,
        false,
        nil,
    )
    if err != nil {
        return nil, err
    }

    return &RabbitMQQueue{
        connection:  conn,
        channel:     ch,
        queueName:   queueName,
        exchange:    exchange,
        routingKey:  routingKey,
        handlers:    make(map[string]TaskHandler),
    }, nil
}

func (q *RabbitMQQueue) RegisterHandler(taskType string, handler TaskHandler) {
    q.mu.Lock()
    defer q.mu.Unlock()
    q.handlers[taskType] = handler
}

func (q *RabbitMQQueue) StartWorker(workerCount int) error {
    for i := 0; i < workerCount; i++ {
        worker := &RabbitMQWorker{
            id:       i,
            channel:  q.channel,
            queue:    q.queue,
            handlers: q.handlers,
            quit:     make(chan struct{}),
        }
        q.workers = append(q.workers, worker)
        go worker.Start()
    }
    return nil
}

func (w *RabbitMQWorker) Start() {
    // 设置QoS
    err := w.channel.Qos(
        1,     // 预取计数
        0,     // 预取大小
        false, // 全局设置
    )
    if err != nil {
        log.Printf("Worker %d: Failed to set QoS: %v", w.id, err)
        return
    }

    // 消费消息
    msgs, err := w.channel.Consume(
        w.queue.Name,
        "",    // 消费者标签
        false, // 自动确认
        false, // 排他性
        false, // 不等待
        false, // 额外参数
        nil,   // 参数
    )
    if err != nil {
        log.Printf("Worker %d: Failed to register consumer: %v", w.id, err)
        return
    }

    for {
        select {
        case msg, ok := <-msgs:
            if !ok {
                return
            }

            w.processMessage(msg)

        case <-w.quit:
            return
        }
    }
}

func (w *RabbitMQWorker) processMessage(msg amqp.Delivery) {
    log.Printf("Worker %d: Processing message", w.id)

    // 解析任务
    var task struct {
        ID      string      `json:"id"`
        Type    string      `json:"type"`
        Payload interface{} `json:"payload"`
    }

    if err := json.Unmarshal(msg.Body, &task); err != nil {
        log.Printf("Worker %d: Failed to unmarshal task: %v", w.id, err)
        msg.Nack(false, false) // 拒绝消息，不重新入队
        return
    }

    // 处理任务
    result, err := w.processTask(task)
    if err != nil {
        log.Printf("Worker %d: Task failed: %v", w.id, err)
        msg.Nack(false, true) // 拒绝消息，重新入队
        return
    }

    log.Printf("Worker %d: Task completed successfully", w.id)
    msg.Ack(false) // 确认消息
}

func (w *RabbitMQWorker) processTask(task struct {
    ID      string      `json:"id"`
    Type    string      `json:"type"`
    Payload interface{} `json:"payload"`
}) (interface{}, error) {
    // 查找处理器
    handler, exists := w.handlers[task.Type]
    if !exists {
        return nil, fmt.Errorf("no handler for task type: %s", task.Type)
    }

    return handler(task.Payload)
}

func (q *RabbitMQQueue) Publish(taskType string, payload interface{}) error {
    task := map[string]interface{}{
        "id":      generateUUID(),
        "type":    taskType,
        "payload": payload,
        "queued":  time.Now(),
    }

    data, err := json.Marshal(task)
    if err != nil {
        return err
    }

    // 发布消息
    err = q.channel.Publish(
        q.exchange,
        q.routingKey,
        false, // 强制发布
        false, // 立即发布
        amqp.Publishing{
            ContentType:  "application/json",
            Body:         data,
            DeliveryMode: amqp.Persistent, // 持久化消息
        },
    )
    return err
}

func (q *RabbitMQQueue) Close() error {
    // 停止工作协程
    for _, worker := range q.workers {
        close(worker.quit)
    }

    // 关闭通道和连接
    if q.channel != nil {
        q.channel.Close()
    }
    if q.connection != nil {
        q.connection.Close()
    }

    return nil
}
```

### 3.3 Kafka消息队列
```go
// Kafka消息队列
type KafkaQueue struct {
    producer   sarama.SyncProducer
    consumer   sarama.ConsumerGroup
    topic      string
    groupID    string
    handlers   map[string]TaskHandler
    mu         sync.RWMutex
}

type KafkaConsumer struct {
    ready    chan bool
    handlers map[string]TaskHandler
}

func NewKafkaQueue(brokers []string, topic, groupID string) (*KafkaQueue, error) {
    // 生产者配置
    producerConfig := sarama.NewConfig()
    producerConfig.Producer.Return.Successes = true
    producerConfig.Producer.RequiredAcks = sarama.WaitForAll
    producerConfig.Producer.Retry.Max = 5
    producerConfig.Producer.Retry.Backoff = 1 * time.Second

    // 创建生产者
    producer, err := sarama.NewSyncProducer(brokers, producerConfig)
    if err != nil {
        return nil, err
    }

    // 消费者配置
    consumerConfig := sarama.NewConfig()
    consumerConfig.Consumer.Group.Rebalance.Strategy = sarama.BalanceStrategyRoundRobin
    consumerConfig.Consumer.Offsets.Initial = sarama.OffsetNewest

    // 创建消费者
    consumer, err := sarama.NewConsumerGroup(brokers, groupID, consumerConfig)
    if err != nil {
        producer.Close()
        return nil, err
    }

    return &KafkaQueue{
        producer: producer,
        consumer: consumer,
        topic:    topic,
        groupID:  groupID,
        handlers: make(map[string]TaskHandler),
    }, nil
}

func (q *KafkaQueue) RegisterHandler(taskType string, handler TaskHandler) {
    q.mu.Lock()
    defer q.mu.Unlock()
    q.handlers[taskType] = handler
}

func (q *KafkaQueue) StartConsumer() error {
    consumer := &KafkaConsumer{
        ready:    make(chan bool),
        handlers: q.handlers,
    }

    go func() {
        for {
            if err := q.consumer.Consume(context.Background(), []string{q.topic}, consumer); err != nil {
                log.Printf("Consumer error: %v", err)
            }
            // 等待重试
            time.Sleep(5 * time.Second)
        }
    }()

    // 等待消费者就绪
    <-consumer.ready
    return nil
}

func (c *KafkaConsumer) Setup(sarama.ConsumerGroupSession) error {
    // 标记消费者就绪
    close(c.ready)
    return nil
}

func (c *KafkaConsumer) Cleanup(sarama.ConsumerGroupSession) error {
    return nil
}

func (c *KafkaConsumer) ConsumeClaim(session sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
    for message := range claim.Messages() {
        c.processMessage(message, session)
    }
    return nil
}

func (c *KafkaConsumer) processMessage(message *sarama.ConsumerMessage, session sarama.ConsumerGroupSession) {
    log.Printf("Processing message from topic %s partition %d offset %d",
        message.Topic, message.Partition, message.Offset)

    // 解析任务
    var task struct {
        ID      string      `json:"id"`
        Type    string      `json:"type"`
        Payload interface{} `json:"payload"`
    }

    if err := json.Unmarshal(message.Value, &task); err != nil {
        log.Printf("Failed to unmarshal task: %v", err)
        return
    }

    // 处理任务
    result, err := c.processTask(task)
    if err != nil {
        log.Printf("Task failed: %v", err)
        return
    }

    log.Printf("Task completed successfully")
    session.MarkMessage(message, "")
}

func (c *KafkaConsumer) processTask(task struct {
    ID      string      `json:"id"`
    Type    string      `json:"type"`
    Payload interface{} `json:"payload"`
}) (interface{}, error) {
    // 查找处理器
    handler, exists := c.handlers[task.Type]
    if !exists {
        return nil, fmt.Errorf("no handler for task type: %s", task.Type)
    }

    return handler(task.Payload)
}

func (q *KafkaQueue) Publish(taskType string, payload interface{}) error {
    task := map[string]interface{}{
        "id":      generateUUID(),
        "type":    taskType,
        "payload": payload,
        "queued":  time.Now(),
    }

    data, err := json.Marshal(task)
    if err != nil {
        return err
    }

    // 发送消息
    message := &sarama.ProducerMessage{
        Topic: q.topic,
        Key:   sarama.StringEncoder(taskType),
        Value: sarama.ByteEncoder(data),
    }

    _, _, err = q.producer.SendMessage(message)
    return err
}

func (q *KafkaQueue) Close() error {
    if q.producer != nil {
        q.producer.Close()
    }
    if q.consumer != nil {
        q.consumer.Close()
    }
    return nil
}
```

## 4. 任务队列系统

### 4.1 任务调度器
```go
// 任务调度器
type TaskScheduler struct {
    queue      chan *ScheduledTask
    workers    []*ScheduledWorker
    ticker     *time.Ticker
    tasks      map[string]*ScheduledTask
    mu         sync.RWMutex
    config     *SchedulerConfig
}

type ScheduledTask struct {
    ID         string
    Type       string
    Payload    interface{}
    Schedule   time.Time
    Interval   time.Duration
    Repeat     int
    Executed   int
    Status     string
    CreatedAt  time.Time
    NextRun    time.Time
    LastRun    *time.Time
    Handler    TaskHandler
}

type SchedulerConfig struct {
    WorkerCount int
    QueueSize   int
    TickInterval time.Duration
}

type ScheduledWorker struct {
    id    int
    queue <-chan *ScheduledTask
    quit  chan struct{}
}

func NewTaskScheduler(config *SchedulerConfig) *TaskScheduler {
    return &TaskScheduler{
        queue:  make(chan *ScheduledTask, config.QueueSize),
        tasks:  make(map[string]*ScheduledTask),
        ticker: time.NewTicker(config.TickInterval),
        config: config,
    }
}

func (s *TaskScheduler) Start() {
    // 启动工作协程
    for i := 0; i < s.config.WorkerCount; i++ {
        worker := &ScheduledWorker{
            id:    i,
            queue: s.queue,
            quit:  make(chan struct{}),
        }
        s.workers = append(s.workers, worker)
        go worker.Start()
    }

    // 启动调度器
    go s.scheduleTasks()
}

func (s *TaskScheduler) ScheduleTask(taskType string, payload interface{}, schedule time.Time, handler TaskHandler) string {
    task := &ScheduledTask{
        ID:        generateUUID(),
        Type:      taskType,
        Payload:   payload,
        Schedule:  schedule,
        Status:    "scheduled",
        CreatedAt: time.Now(),
        NextRun:   schedule,
        Handler:   handler,
    }

    s.mu.Lock()
    s.tasks[task.ID] = task
    s.mu.Unlock()

    return task.ID
}

func (s *TaskScheduler) ScheduleRecurringTask(taskType string, payload interface{}, interval time.Duration, repeat int, handler TaskHandler) string {
    task := &ScheduledTask{
        ID:        generateUUID(),
        Type:      taskType,
        Payload:   payload,
        Schedule:  time.Now().Add(interval),
        Interval:  interval,
        Repeat:    repeat,
        Status:    "scheduled",
        CreatedAt: time.Now(),
        NextRun:    time.Now().Add(interval),
        Handler:   handler,
    }

    s.mu.Lock()
    s.tasks[task.ID] = task
    s.mu.Unlock()

    return task.ID
}

func (s *TaskScheduler) scheduleTasks() {
    for {
        select {
        case <-s.ticker.C:
            s.checkAndScheduleTasks()
        case <-s.quit:
            return
        }
    }
}

func (s *TaskScheduler) checkAndScheduleTasks() {
    s.mu.RLock()
    now := time.Now()
    tasksToRun := make([]*ScheduledTask, 0)

    for _, task := range s.tasks {
        if task.Status == "scheduled" && !task.NextRun.After(now) {
            tasksToRun = append(tasksToRun, task)
        }
    }
    s.mu.RUnlock()

    // 调度任务
    for _, task := range tasksToRun {
        s.queue <- task
    }
}

func (w *ScheduledWorker) Start() {
    for {
        select {
        case task := <-w.queue:
            w.executeTask(task)
        case <-w.quit:
            return
        }
    }
}

func (w *ScheduledWorker) executeTask(task *ScheduledTask) {
    log.Printf("Worker %d: Executing scheduled task %s", w.id, task.ID)

    // 更新任务状态
    task.Status = "running"
    now := time.Now()
    task.LastRun = &now
    task.Executed++

    // 执行任务
    result, err := task.Handler(task.Payload)
    if err != nil {
        log.Printf("Worker %d: Task %s failed: %v", w.id, task.ID, err)
        task.Status = "failed"
        return
    }

    log.Printf("Worker %d: Task %s completed successfully", w.id, task.ID)

    // 处理重复任务
    if task.Interval > 0 && (task.Repeat == 0 || task.Executed < task.Repeat) {
        task.Status = "scheduled"
        task.NextRun = time.Now().Add(task.Interval)
    } else {
        task.Status = "completed"
    }
}

func (s *TaskScheduler) GetTask(id string) (*ScheduledTask, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    task, exists := s.tasks[id]
    return task, exists
}

func (s *TaskScheduler) CancelTask(id string) error {
    s.mu.Lock()
    defer s.mu.Unlock()

    if task, exists := s.tasks[id]; exists {
        task.Status = "cancelled"
        return nil
    }

    return fmt.Errorf("task not found")
}

func (s *TaskScheduler) Stop() {
    close(s.quit)
    s.ticker.Stop()
    for _, worker := range s.workers {
        close(worker.quit)
    }
}
```

### 4.2 任务状态管理
```go
// 任务状态管理器
type TaskStatusManager struct {
    storage    TaskStorage
    metrics    *TaskMetrics
    listeners  map[string][]TaskStatusListener
    mu         sync.RWMutex
}

type TaskStorage interface {
    Save(task *TaskStatus) error
    Get(id string) (*TaskStatus, error)
    List(filter TaskFilter) ([]*TaskStatus, error)
    Update(id string, updater func(*TaskStatus) error) error
    Delete(id string) error
}

type TaskStatus struct {
    ID           string                 `json:"id"`
    Type         string                 `json:"type"`
    Status       string                 `json:"status"`
    Payload      interface{}            `json:"payload"`
    Result       interface{}            `json:"result"`
    Error        string                 `json:"error"`
    Progress     float64                `json:"progress"`
    CreatedAt    time.Time              `json:"created_at"`
    StartedAt    *time.Time             `json:"started_at,omitempty"`
    CompletedAt  *time.Time             `json:"completed_at,omitempty"`
    UpdatedAt    time.Time              `json:"updated_at"`
    Metadata     map[string]interface{} `json:"metadata"`
    Retries      int                    `json:"retries"`
    MaxRetries   int                    `json:"max_retries"`
    Priority     int                    `json:"priority"`
}

type TaskFilter struct {
    Status    []string
    Type      string
    CreatedAt time.Time
    Limit     int
    Offset    int
}

type TaskStatusListener func(task *TaskStatus)

type TaskMetrics struct {
    tasksCreated   *prometheus.CounterVec
    tasksCompleted *prometheus.CounterVec
    tasksFailed    *prometheus.CounterVec
    taskDuration   *prometheus.HistogramVec
}

func NewTaskStatusManager(storage TaskStorage) *TaskStatusManager {
    metrics := &TaskMetrics{
        tasksCreated: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "async_tasks_created_total",
                Help: "Total number of async tasks created",
            },
            []string{"type"},
        ),
        tasksCompleted: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "async_tasks_completed_total",
                Help: "Total number of async tasks completed",
            },
            []string{"type"},
        ),
        tasksFailed: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "async_tasks_failed_total",
                Help: "Total number of async tasks failed",
            },
            []string{"type", "error"},
        ),
        taskDuration: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name:    "async_task_duration_seconds",
                Help:    "Async task duration in seconds",
                Buckets: []float64{1, 10, 60, 300, 600, 1800},
            },
            []string{"type"},
        ),
    }

    // 注册指标
    prometheus.MustRegister(metrics.tasksCreated)
    prometheus.MustRegister(metrics.tasksCompleted)
    prometheus.MustRegister(metrics.tasksFailed)
    prometheus.MustRegister(metrics.taskDuration)

    return &TaskStatusManager{
        storage:   storage,
        metrics:   metrics,
        listeners: make(map[string][]TaskStatusListener),
    }
}

func (m *TaskStatusManager) CreateTask(taskType string, payload interface{}, options ...TaskOption) (*TaskStatus, error) {
    task := &TaskStatus{
        ID:          generateUUID(),
        Type:        taskType,
        Status:      "pending",
        Payload:     payload,
        Progress:    0,
        CreatedAt:   time.Now(),
        UpdatedAt:   time.Now(),
        Metadata:    make(map[string]interface{}),
        MaxRetries:  3,
        Priority:    0,
    }

    // 应用选项
    for _, option := range options {
        option(task)
    }

    // 保存任务
    if err := m.storage.Save(task); err != nil {
        return nil, err
    }

    // 记录指标
    m.metrics.tasksCreated.WithLabelValues(taskType).Inc()

    // 通知监听器
    m.notifyListeners(task)

    return task, nil
}

func (m *TaskStatusManager) UpdateTaskStatus(id string, status string, result interface{}, err error) error {
    now := time.Now()
    updater := func(task *TaskStatus) error {
        task.Status = status
        task.UpdatedAt = now
        task.Result = result

        if err != nil {
            task.Error = err.Error()
        }

        // 更新时间戳
        switch status {
        case "running":
            task.StartedAt = &now
        case "completed", "failed":
            task.CompletedAt = &now
        }

        return nil
    }

    if err := m.storage.Update(id, updater); err != nil {
        return err
    }

    // 获取更新后的任务
    task, err := m.storage.Get(id)
    if err != nil {
        return err
    }

    // 记录指标
    if status == "completed" {
        m.metrics.tasksCompleted.WithLabelValues(task.Type).Inc()
        if task.StartedAt != nil {
            duration := task.CompletedAt.Sub(*task.StartedAt)
            m.metrics.taskDuration.WithLabelValues(task.Type).Observe(duration.Seconds())
        }
    } else if status == "failed" {
        m.metrics.tasksFailed.WithLabelValues(task.Type, err.Error()).Inc()
    }

    // 通知监听器
    m.notifyListeners(task)

    return nil
}

func (m *TaskStatusManager) UpdateTaskProgress(id string, progress float64) error {
    return m.storage.Update(id, func(task *TaskStatus) error {
        task.Progress = progress
        task.UpdatedAt = time.Now()
        return nil
    })
}

func (m *TaskStatusManager) GetTask(id string) (*TaskStatus, error) {
    return m.storage.Get(id)
}

func (m *TaskStatusManager) ListTasks(filter TaskFilter) ([]*TaskStatus, error) {
    return m.storage.List(filter)
}

func (m *TaskStatusManager) AddListener(taskID string, listener TaskStatusListener) {
    m.mu.Lock()
    defer m.mu.Unlock()

    m.listeners[taskID] = append(m.listeners[taskID], listener)
}

func (m *TaskStatusManager) RemoveListener(taskID string, listener TaskStatusListener) {
    m.mu.Lock()
    defer m.mu.Unlock()

    if listeners, exists := m.listeners[taskID]; exists {
        for i, l := range listeners {
            if l == listener {
                m.listeners[taskID] = append(listeners[:i], listeners[i+1:]...)
                break
            }
        }
    }
}

func (m *TaskStatusManager) notifyListeners(task *TaskStatus) {
    m.mu.RLock()
    listeners := make([]TaskStatusListener, len(m.listeners[task.ID]))
    copy(listeners, m.listeners[task.ID])
    m.mu.RUnlock()

    for _, listener := range listeners {
        go listener(task)
    }
}

// 任务选项
type TaskOption func(*TaskStatus)

func WithPriority(priority int) TaskOption {
    return func(task *TaskStatus) {
        task.Priority = priority
    }
}

func WithMaxRetries(retries int) TaskOption {
    return func(task *TaskStatus) {
        task.MaxRetries = retries
    }
}

func WithMetadata(key string, value interface{}) TaskOption {
    return func(task *TaskStatus) {
        task.Metadata[key] = value
    }
}

func WithTimeout(timeout time.Duration) TaskOption {
    return func(task *TaskStatus) {
        task.Metadata["timeout"] = timeout
    }
}
```

### 4.3 任务重试机制
```go
// 任务重试管理器
type TaskRetryManager struct {
    queue      chan *RetryTask
    workers    []*RetryWorker
    storage    TaskStorage
    config     *RetryConfig
    metrics    *RetryMetrics
}

type RetryTask struct {
    TaskID     string
    RetryCount int
    NextRetry  time.Time
    MaxRetries int
    Strategy   RetryStrategy
    Backoff    BackoffStrategy
}

type RetryConfig struct {
    WorkerCount  int
    QueueSize    int
    MaxRetries   int
    DefaultDelay time.Duration
}

type RetryStrategy string

const (
    RetryStrategyFixed   RetryStrategy = "fixed"
    RetryStrategyLinear  RetryStrategy = "linear"
    RetryStrategyExponential RetryStrategy = "exponential"
)

type BackoffStrategy interface {
    NextDelay(retryCount int) time.Duration
}

type FixedBackoff struct {
    Delay time.Duration
}

func (f *FixedBackoff) NextDelay(retryCount int) time.Duration {
    return f.Delay
}

type LinearBackoff struct {
    BaseDelay time.Duration
    Increment time.Duration
}

func (l *LinearBackoff) NextDelay(retryCount int) time.Duration {
    return l.BaseDelay + time.Duration(retryCount)*l.Increment
}

type ExponentialBackoff struct {
    BaseDelay time.Duration
    Multiplier float64
    MaxDelay   time.Duration
}

func (e *ExponentialBackoff) NextDelay(retryCount int) time.Duration {
    delay := time.Duration(float64(e.BaseDelay) * math.Pow(e.Multiplier, float64(retryCount)))
    if delay > e.MaxDelay {
        return e.MaxDelay
    }
    return delay
}

type RetryMetrics struct {
    retriesTotal    *prometheus.CounterVec
    retryExhausted  *prometheus.CounterVec
    retryDelay      *prometheus.HistogramVec
}

func NewTaskRetryManager(storage TaskStorage, config *RetryConfig) *TaskRetryManager {
    metrics := &RetryMetrics{
        retriesTotal: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "async_task_retries_total",
                Help: "Total number of async task retries",
            },
            []string{"task_type"},
        ),
        retryExhausted: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "async_task_retry_exhausted_total",
                Help: "Total number of async tasks that exhausted retries",
            },
            []string{"task_type"},
        ),
        retryDelay: prometheus.NewHistogramVec(
            prometheus.CounterOpts{
                Name: "async_task_retry_delay_seconds",
                Help: "Async task retry delay in seconds",
            },
            []string{"task_type"},
        ),
    }

    prometheus.MustRegister(metrics.retriesTotal)
    prometheus.MustRegister(metrics.retryExhausted)
    prometheus.MustRegister(metrics.retryDelay)

    return &TaskRetryManager{
        queue:   make(chan *RetryTask, config.QueueSize),
        storage: storage,
        config:  config,
        metrics: metrics,
    }
}

func (m *TaskRetryManager) Start() {
    for i := 0; i < m.config.WorkerCount; i++ {
        worker := &RetryWorker{
            id:      i,
            queue:   m.queue,
            storage: m.storage,
            metrics: m.metrics,
        }
        m.workers = append(m.workers, worker)
        go worker.Start()
    }
}

func (m *TaskRetryManager) ScheduleRetry(taskID string, maxRetries int, strategy RetryStrategy, backoff BackoffStrategy) error {
    retryTask := &RetryTask{
        TaskID:     taskID,
        RetryCount: 0,
        NextRetry:  time.Now().Add(backoff.NextDelay(0)),
        MaxRetries: maxRetries,
        Strategy:   strategy,
        Backoff:    backoff,
    }

    select {
    case m.queue <- retryTask:
        return nil
    default:
        return fmt.Errorf("retry queue is full")
    }
}

type RetryWorker struct {
      id      int
      queue   <-chan *RetryTask
      storage TaskStorage
      metrics *RetryMetrics
}

func (w *RetryWorker) Start() {
    for {
        select {
        case retryTask := <-w.queue:
            w.processRetry(retryTask)
        }
    }
}

func (w *RetryWorker) processRetry(retryTask *RetryTask) {
    // 等待重试时间
    select {
    case <-time.After(time.Until(retryTask.NextRetry)):
    case <-time.After(5 * time.Minute):
        // 如果时间过长，跳过这次重试
        return
    }

    // 获取任务状态
    task, err := w.storage.Get(retryTask.TaskID)
    if err != nil {
        log.Printf("RetryWorker %d: Failed to get task %s: %v", w.id, retryTask.TaskID, err)
        return
    }

    // 检查任务状态
    if task.Status != "failed" {
        return // 任务已经不在失败状态
    }

    // 更新重试次数
    retryTask.RetryCount++

    // 检查是否超过最大重试次数
    if retryTask.RetryCount >= retryTask.MaxRetries {
        log.Printf("RetryWorker %d: Task %s exhausted retries", w.id, retryTask.TaskID)
        w.metrics.retryExhausted.WithLabelValues(task.Type).Inc()
        return
    }

    // 记录重试指标
    w.metrics.retriesTotal.WithLabelValues(task.Type).Inc()
    delay := time.Until(retryTask.NextRetry)
    w.metrics.retryDelay.WithLabelValues(task.Type).Observe(delay.Seconds())

    // 重新排队任务
    task.Status = "pending"
    task.Retries = retryTask.RetryCount
    task.UpdatedAt = time.Now()

    if err := w.storage.Save(task); err != nil {
        log.Printf("RetryWorker %d: Failed to save task %s: %v", w.id, retryTask.TaskID, err)
        return
    }

    log.Printf("RetryWorker %d: Retried task %s (attempt %d)", w.id, retryTask.TaskID, retryTask.RetryCount)

    // 安排下次重试
    retryTask.NextRetry = time.Now().Add(retryTask.Backoff.NextDelay(retryTask.RetryCount))
    go func() {
        select {
        case w.queue <- retryTask:
        case <-time.After(time.Minute):
            // 如果队列满，放弃重试
        }
    }()
}
```

## 5. 事件驱动架构

### 5.1 事件总线
```go
// 事件总线
type EventBus struct {
    subscribers map[string][]EventHandler
    middleware  []EventMiddleware
    mu         sync.RWMutex
}

type Event struct {
    ID        string                 `json:"id"`
    Type      string                 `json:"type"`
    Data      interface{}            `json:"data"`
    Timestamp time.Time              `json:"timestamp"`
    Metadata  map[string]interface{} `json:"metadata"`
}

type EventHandler func(event *Event) error

type EventMiddleware func(next EventHandler) EventHandler

func NewEventBus() *EventBus {
    return &EventBus{
        subscribers: make(map[string][]EventHandler),
        middleware:  make([]EventMiddleware, 0),
    }
}

func (b *EventBus) Subscribe(eventType string, handler EventHandler) {
    b.mu.Lock()
    defer b.mu.Unlock()

    b.subscribers[eventType] = append(b.subscribers[eventType], handler)
}

func (b *EventBus) Unsubscribe(eventType string, handler EventHandler) {
    b.mu.Lock()
    defer b.mu.Unlock()

    if handlers, exists := b.subscribers[eventType]; exists {
        for i, h := range handlers {
            if h == handler {
                b.subscribers[eventType] = append(handlers[:i], handlers[i+1:]...)
                break
            }
        }
    }
}

func (b *EventBus) Publish(eventType string, data interface{}, metadata map[string]interface{}) error {
    event := &Event{
        ID:        generateUUID(),
        Type:      eventType,
        Data:      data,
        Timestamp: time.Now(),
        Metadata:  metadata,
    }

    return b.publishEvent(event)
}

func (b *EventBus) publishEvent(event *Event) error {
    b.mu.RLock()
    handlers := make([]EventHandler, len(b.subscribers[event.Type]))
    copy(handlers, b.subscribers[event.Type])
    b.mu.RUnlock()

    // 创建处理链
    var handler EventHandler = func(e *Event) error {
        var wg sync.WaitGroup
        errChan := make(chan error, len(handlers))

        for _, h := range handlers {
            wg.Add(1)
            go func(eventHandler EventHandler) {
                defer wg.Done()
                if err := eventHandler(e); err != nil {
                    errChan <- err
                }
            }(h)
        }

        wg.Wait()
        close(errChan)

        // 返回第一个错误
        for err := range errChan {
            return err
        }

        return nil
    }

    // 应用中间件
    for i := len(b.middleware) - 1; i >= 0; i-- {
        handler = b.middleware[i](handler)
    }

    return handler(event)
}

func (b *EventBus) Use(middleware EventMiddleware) {
    b.middleware = append(b.middleware, middleware)
}

// 中间件
func LoggingMiddleware(logger Logger) EventMiddleware {
    return func(next EventHandler) EventHandler {
        return func(event *Event) error {
            start := time.Now()
            logger.Info("Event received",
                zap.String("event_type", event.Type),
                zap.String("event_id", event.ID),
            )

            err := next(event)

            duration := time.Since(start)
            logger.Info("Event processed",
                zap.String("event_type", event.Type),
                zap.String("event_id", event.ID),
                zap.Duration("duration", duration),
                zap.Error(err),
            )

            return err
        }
    }
}

func RecoveryMiddleware(logger Logger) EventMiddleware {
    return func(next EventHandler) EventHandler {
        return func(event *Event) error {
            defer func() {
                if r := recover(); r != nil {
                    logger.Error("Event handler panic",
                        zap.String("event_type", event.Type),
                        zap.String("event_id", event.ID),
                        zap.Any("panic", r),
                    )
                }
            }()

            return next(event)
        }
    }
}

func MetricsMiddleware(metrics *EventMetrics) EventMiddleware {
    return func(next EventHandler) EventHandler {
        return func(event *Event) error {
            start := time.Now()
            err := next(event)
            duration := time.Since(start)

            metrics.RecordEvent(event.Type, duration, err != nil)

            return err
        }
    }
}

type EventMetrics struct {
    eventsTotal    *prometheus.CounterVec
    eventDuration  *prometheus.HistogramVec
    eventErrors    *prometheus.CounterVec
}

func NewEventMetrics() *EventMetrics {
    metrics := &EventMetrics{
        eventsTotal: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "events_total",
                Help: "Total number of events processed",
            },
            []string{"event_type"},
        ),
        eventDuration: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name:    "event_duration_seconds",
                Help:    "Event processing duration in seconds",
                Buckets: []float64{0.001, 0.01, 0.1, 1, 10},
            },
            []string{"event_type"},
        ),
        eventErrors: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "events_errors_total",
                Help: "Total number of event processing errors",
            },
            []string{"event_type"},
        ),
    }

    prometheus.MustRegister(metrics.eventsTotal)
    prometheus.MustRegister(metrics.eventDuration)
    prometheus.MustRegister(metrics.eventErrors)

    return metrics
}

func (m *EventMetrics) RecordEvent(eventType string, duration time.Duration, hasError bool) {
    m.eventsTotal.WithLabelValues(eventType).Inc()
    m.eventDuration.WithLabelValues(eventType).Observe(duration.Seconds())
    if hasError {
        m.eventErrors.WithLabelValues(eventType).Inc()
    }
}
```

### 5.2 事件溯源
```go
// 事件溯源存储
type EventStore interface {
    SaveEvents(aggregateID string, events []*Event, version int) error
    GetEvents(aggregateID string) ([]*Event, error)
    GetEventsByType(eventType string) ([]*Event, error)
    GetEventsByTimeRange(start, end time.Time) ([]*Event, error)
}

// 内存事件存储
type MemoryEventStore struct {
    events map[string][]*Event
    mu     sync.RWMutex
}

func NewMemoryEventStore() *MemoryEventStore {
    return &MemoryEventStore{
        events: make(map[string][]*Event),
    }
}

func (s *MemoryEventStore) SaveEvents(aggregateID string, events []*Event, version int) error {
    s.mu.Lock()
    defer s.mu.Unlock()

    // 检查版本冲突
    if existingEvents, exists := s.events[aggregateID]; exists {
        if len(existingEvents) != version {
            return fmt.Errorf("version conflict: expected %d, got %d", version, len(existingEvents))
        }
    }

    // 添加事件
    s.events[aggregateID] = append(s.events[aggregateID], events...)
    return nil
}

func (s *MemoryEventStore) GetEvents(aggregateID string) ([]*Event, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    events := make([]*Event, len(s.events[aggregateID]))
    copy(events, s.events[aggregateID])
    return events, nil
}

func (s *MemoryEventStore) GetEventsByType(eventType string) ([]*Event, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    var events []*Event
    for _, aggregateEvents := range s.events {
        for _, event := range aggregateEvents {
            if event.Type == eventType {
                events = append(events, event)
            }
        }
    }

    return events, nil
}

func (s *MemoryEventStore) GetEventsByTimeRange(start, end time.Time) ([]*Event, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    var events []*Event
    for _, aggregateEvents := range s.events {
        for _, event := range aggregateEvents {
            if event.Timestamp.After(start) && event.Timestamp.Before(end) {
                events = append(events, event)
            }
        }
    }

    return events, nil
}

// 聚合根
type AggregateRoot struct {
    ID      string
    Version int
    Events  []*Event
}

func (a *AggregateRoot) ApplyEvent(eventType string, data interface{}) {
    event := &Event{
        ID:        generateUUID(),
        Type:      eventType,
        Data:      data,
        Timestamp: time.Now(),
    }

    a.Events = append(a.Events, event)
    a.Version++
}

// 用户聚合根示例
type UserAggregate struct {
    *AggregateRoot
    Name  string
    Email string
    Active bool
}

func NewUserAggregate(id, name, email string) *UserAggregate {
    aggregate := &UserAggregate{
        AggregateRoot: &AggregateRoot{ID: id},
    }

    aggregate.ApplyEvent("UserCreated", map[string]interface{}{
        "name":  name,
        "email": email,
    })

    return aggregate
}

func (u *UserAggregate) UpdateName(newName string) {
    u.ApplyEvent("UserNameUpdated", map[string]interface{}{
        "old_name": u.Name,
        "new_name": newName,
    })
    u.Name = newName
}

func (u *UserAggregate) Activate() {
    u.ApplyEvent("UserActivated", map[string]interface{}{
        "previous_state": !u.Active,
        "new_state":      true,
    })
    u.Active = true
}

func (u *UserAggregate) Deactivate() {
    u.ApplyEvent("UserDeactivated", map[string]interface{}{
        "previous_state": !u.Active,
        "new_state":      false,
    })
    u.Active = false
}

// 事件处理器
type UserEventHandler struct {
    store EventStore
}

func (h *UserEventHandler) HandleUserCreated(event *Event) error {
    // 处理用户创建事件
    data := event.Data.(map[string]interface{})
    log.Printf("User created: %s (%s)", data["name"], data["email"])

    // 发送欢迎邮件
    go h.sendWelcomeEmail(data["email"].(string))

    return nil
}

func (h *UserEventHandler) HandleUserNameUpdated(event *Event) error {
    // 处理用户名更新事件
    data := event.Data.(map[string]interface{})
    log.Printf("User name updated: %s -> %s", data["old_name"], data["new_name"])
    return nil
}

func (h *UserEventHandler) HandleUserActivated(event *Event) error {
    // 处理用户激活事件
    log.Printf("User activated")
    return nil
}

func (h *UserEventHandler) HandleUserDeactivated(event *Event) error {
    // 处理用户停用事件
    log.Printf("User deactivated")
    return nil
}

func (h *UserEventHandler) sendWelcomeEmail(email string) {
    // 模拟发送邮件
    time.Sleep(1 * time.Second)
    log.Printf("Welcome email sent to: %s", email)
}

// 事件溯源服务
type EventSourcingService struct {
    store    EventStore
    bus      *EventBus
    handlers map[string]EventHandler
}

func NewEventSourcingService(store EventStore, bus *EventBus) *EventSourcingService {
    return &EventSourcingService{
        store:    store,
        bus:      bus,
        handlers: make(map[string]EventHandler),
    }
}

func (s *EventSourcingService) RegisterHandler(eventType string, handler EventHandler) {
    s.handlers[eventType] = handler
    s.bus.Subscribe(eventType, handler)
}

func (s *EventSourcingService) SaveAggregate(aggregate *AggregateRoot) error {
    if len(aggregate.Events) == 0 {
        return nil
    }

    // 保存事件
    if err := s.store.SaveEvents(aggregate.ID, aggregate.Events, aggregate.Version-len(aggregate.Events)); err != nil {
        return err
    }

    // 发布事件
    for _, event := range aggregate.Events {
        if err := s.bus.Publish(event.Type, event.Data, event.Metadata); err != nil {
            log.Printf("Failed to publish event %s: %v", event.ID, err)
        }
    }

    // 清空事件
    aggregate.Events = make([]*Event, 0)

    return nil
}

func (s *EventSourcingService) LoadAggregate(aggregateID string, factory func(id string) *AggregateRoot) (*AggregateRoot, error) {
    events, err := s.store.GetEvents(aggregateID)
    if err != nil {
        return nil, err
    }

    aggregate := factory(aggregateID)

    // 重放事件
    for _, event := range events {
        aggregate.Version++
        // 这里需要根据事件类型更新聚合状态
        // 实际实现中需要更复杂的事件处理逻辑
    }

    return aggregate, nil
}
```

## 6. 完整示例

### 6.1 异步任务服务
```go
// 异步任务服务
type AsyncTaskService struct {
    queue          *RedisQueue
    statusManager  *TaskStatusManager
    retryManager   *TaskRetryManager
    eventBus       *EventBus
    scheduler      *TaskScheduler
    config         *AsyncConfig
}

type AsyncConfig struct {
    RedisAddr      string
    QueueName      string
    WorkerCount    int
    EnableRetries  bool
    EnableEvents   bool
    EnableSchedule bool
}

func NewAsyncTaskService(config *AsyncConfig) (*AsyncTaskService, error) {
    // 初始化Redis队列
    queue := NewRedisQueue(config.RedisAddr, config.QueueName, config.WorkerCount)

    // 初始化任务状态管理器
    storage := NewRedisTaskStorage(config.RedisAddr)
    statusManager := NewTaskStatusManager(storage)

    service := &AsyncTaskService{
        queue:         queue,
        statusManager: statusManager,
        eventBus:      NewEventBus(),
        config:        config,
    }

    // 初始化重试管理器
    if config.EnableRetries {
        retryConfig := &RetryConfig{
            WorkerCount: 3,
            QueueSize:   1000,
            MaxRetries:  3,
            DefaultDelay: 5 * time.Second,
        }
        service.retryManager = NewTaskRetryManager(storage, retryConfig)
    }

    // 初始化事件系统
    if config.EnableEvents {
        metrics := NewEventMetrics()
        service.eventBus.Use(MetricsMiddleware(metrics))
        service.eventBus.Use(LoggingMiddleware(NewZapLogger()))
        service.eventBus.Use(RecoveryMiddleware(NewZapLogger()))
    }

    // 初始化任务调度器
    if config.EnableSchedule {
        schedulerConfig := &SchedulerConfig{
            WorkerCount:  2,
            QueueSize:    100,
            TickInterval: 1 * time.Second,
        }
        service.scheduler = NewTaskScheduler(schedulerConfig)
    }

    // 注册任务处理器
    service.registerHandlers()

    return service, nil
}

func (s *AsyncTaskService) Start() error {
    // 启动队列工作协程
    s.queue.Start()

    // 启动重试管理器
    if s.retryManager != nil {
        s.retryManager.Start()
    }

    // 启动任务调度器
    if s.scheduler != nil {
        s.scheduler.Start()
    }

    return nil
}

func (s *AsyncTaskService) registerHandlers() {
    // 注册邮件发送处理器
    s.queue.RegisterHandler("email", s.handleEmailTask)

    // 注册图片处理处理器
    s.queue.RegisterHandler("image_process", s.handleImageProcessTask)

    // 注册数据导出处理器
    s.queue.RegisterHandler("data_export", s.handleDataExportTask)
}

func (s *AsyncTaskService) handleEmailTask(payload interface{}) (interface{}, error) {
    data := payload.(map[string]interface{})
    to := data["to"].(string)
    subject := data["subject"].(string)
    body := data["body"].(string)

    // 模拟邮件发送
    time.Sleep(1 * time.Second)

    log.Printf("Email sent to %s: %s", to, subject)

    return map[string]interface{}{
        "message":  "Email sent successfully",
        "to":       to,
        "subject":  subject,
        "sent_at":  time.Now(),
    }, nil
}

func (s *AsyncTaskService) handleImageProcessTask(payload interface{}) (interface{}, error) {
    data := payload.(map[string]interface{})
    imagePath := data["image_path"].(string)
    operation := data["operation"].(string)

    // 模拟图片处理
    time.Sleep(3 * time.Second)

    log.Printf("Image processed: %s (%s)", imagePath, operation)

    return map[string]interface{}{
        "message":     "Image processed successfully",
        "image_path":  imagePath,
        "operation":   operation,
        "processed":   time.Now(),
        "size":        fmt.Sprintf("%dx%d", rand.Intn(1000)+500, rand.Intn(1000)+500),
    }, nil
}

func (s *AsyncTaskService) handleDataExportTask(payload interface{}) (interface{}, error) {
    data := payload.(map[string]interface{})
    exportType := data["export_type"].(string)
    filters := data["filters"].(map[string]interface{})

    // 模拟数据导出
    time.Sleep(5 * time.Second)

    recordCount := rand.Intn(10000) + 1000
    filePath := fmt.Sprintf("/exports/%s_%d.csv", exportType, time.Now().Unix())

    log.Printf("Data exported: %s (%d records)", filePath, recordCount)

    return map[string]interface{}{
        "message":      "Data exported successfully",
        "export_type":  exportType,
        "file_path":    filePath,
        "record_count": recordCount,
        "filters":      filters,
        "exported_at":  time.Now(),
    }, nil
}

// 公共接口
func (s *AsyncTaskService) SubmitEmailTask(to, subject, body string) (string, error) {
    payload := map[string]interface{}{
        "to":      to,
        "subject": subject,
        "body":    body,
    }

    taskID, err := s.queue.Enqueue("email", payload)
    if err != nil {
        return "", err
    }

    // 创建任务状态
    _, err = s.statusManager.CreateTask("email", payload)
    if err != nil {
        return "", err
    }

    return taskID, nil
}

func (s *AsyncTaskService) SubmitImageProcessTask(imagePath, operation string) (string, error) {
    payload := map[string]interface{}{
        "image_path": imagePath,
        "operation":  operation,
    }

    taskID, err := s.queue.Enqueue("image_process", payload)
    if err != nil {
        return "", err
    }

    return taskID, nil
}

func (s *AsyncTaskService) SubmitDataExportTask(exportType string, filters map[string]interface{}) (string, error) {
    payload := map[string]interface{}{
        "export_type": exportType,
        "filters":    filters,
    }

    taskID, err := s.queue.Enqueue("data_export", payload)
    if err != nil {
        return "", err
    }

    return taskID, nil
}

func (s *AsyncTaskService) GetTaskStatus(taskID string) (*TaskStatus, error) {
    return s.statusManager.GetTask(taskID)
}

func (s *AsyncTaskService) ListTasks(filter TaskFilter) ([]*TaskStatus, error) {
    return s.statusManager.ListTasks(filter)
}

func (s *AsyncTaskService) ScheduleTask(taskType string, payload interface{}, schedule time.Time) (string, error) {
    handler := func(payload interface{}) (interface{}, error) {
        return s.handleTask(taskType, payload)
    }

    return s.scheduler.ScheduleTask(taskType, payload, schedule, handler), nil
}

func (s *AsyncTaskService) handleTask(taskType string, payload interface{}) (interface{}, error) {
    switch taskType {
    case "email":
        return s.handleEmailTask(payload)
    case "image_process":
        return s.handleImageProcessTask(payload)
    case "data_export":
        return s.handleDataExportTask(payload)
    default:
        return nil, fmt.Errorf("unknown task type: %s", taskType)
    }
}
```

### 6.2 Gin集成示例
```go
// Gin中间件和处理器
func AsyncServiceMiddleware(service *AsyncTaskService) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查是否是异步请求
        if c.GetHeader("X-Async-Request") != "true" {
            c.Next()
            return
        }

        // 解析任务类型
        taskType := c.GetHeader("X-Task-Type")
        if taskType == "" {
            c.JSON(400, gin.H{"error": "task type required"})
            return
        }

        // 读取载荷
        var payload map[string]interface{}
        if err := c.ShouldBindJSON(&payload); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }

        // 添加请求信息
        payload["request_info"] = map[string]interface{}{
            "method":  c.Request.Method,
            "path":    c.Request.URL.Path,
            "query":   c.Request.URL.Query(),
            "headers": c.Request.Header,
        }

        // 提交任务
        var taskID string
        var err error

        switch taskType {
        case "email":
            to := payload["to"].(string)
            subject := payload["subject"].(string)
            body := payload["body"].(string)
            taskID, err = service.SubmitEmailTask(to, subject, body)
        case "image_process":
            imagePath := payload["image_path"].(string)
            operation := payload["operation"].(string)
            taskID, err = service.SubmitImageProcessTask(imagePath, operation)
        case "data_export":
            exportType := payload["export_type"].(string)
            filters := payload["filters"].(map[string]interface{})
            taskID, err = service.SubmitDataExportTask(exportType, filters)
        default:
            c.JSON(400, gin.H{"error": "invalid task type"})
            return
        }

        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        // 返回任务信息
        c.JSON(202, gin.H{
            "task_id":    taskID,
            "task_type":  taskType,
            "status":     "queued",
            "check_url":  fmt.Sprintf("/async/tasks/%s", taskID),
            "message":    "Task has been queued for processing",
        })

        c.Abort()
    }
}

// 任务状态查询处理器
func GetTaskStatusHandler(service *AsyncTaskService) gin.HandlerFunc {
    return func(c *gin.Context) {
        taskID := c.Param("id")
        task, err := service.GetTaskStatus(taskID)
        if err != nil {
            c.JSON(404, gin.H{"error": "task not found"})
            return
        }

        c.JSON(200, task)
    }
}

// 任务列表查询处理器
func ListTasksHandler(service *AsyncTaskService) gin.HandlerFunc {
    return func(c *gin.Context) {
        filter := TaskFilter{
            Limit: 50,
        }

        if status := c.Query("status"); status != "" {
            filter.Status = []string{status}
        }

        if taskType := c.Query("type"); taskType != "" {
            filter.Type = taskType
        }

        if offsetStr := c.Query("offset"); offsetStr != "" {
            if offset, err := strconv.Atoi(offsetStr); err == nil {
                filter.Offset = offset
            }
        }

        if limitStr := c.Query("limit"); limitStr != "" {
            if limit, err := strconv.Atoi(limitStr); err == nil {
                filter.Limit = limit
            }
        }

        tasks, err := service.ListTasks(filter)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, gin.H{
            "tasks": tasks,
            "total": len(tasks),
        })
    }
}

// 邮件发送处理器
func SendEmailHandler(service *AsyncTaskService) gin.HandlerFunc {
    return func(c *gin.Context) {
        var request struct {
            To      string `json:"to" binding:"required,email"`
            Subject string `json:"subject" binding:"required"`
            Body    string `json:"body" binding:"required"`
        }

        if err := c.ShouldBindJSON(&request); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }

        taskID, err := service.SubmitEmailTask(request.To, request.Subject, request.Body)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(202, gin.H{
            "task_id":    taskID,
            "status":     "queued",
            "check_url":  fmt.Sprintf("/async/tasks/%s", taskID),
            "message":    "Email task has been queued",
        })
    }
}

// 图片处理处理器
func ProcessImageHandler(service *AsyncTaskService) gin.HandlerFunc {
    return func(c *gin.Context) {
        var request struct {
            ImagePath string `json:"image_path" binding:"required"`
            Operation string `json:"operation" binding:"required"`
        }

        if err := c.ShouldBindJSON(&request); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }

        taskID, err := service.SubmitImageProcessTask(request.ImagePath, request.Operation)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(202, gin.H{
            "task_id":    taskID,
            "status":     "queued",
            "check_url":  fmt.Sprintf("/async/tasks/%s", taskID),
            "message":    "Image processing task has been queued",
        })
    }
}

// 数据导出处理器
func ExportDataHandler(service *AsyncTaskService) gin.HandlerFunc {
    return func(c *gin.Context) {
        var request struct {
            ExportType string                 `json:"export_type" binding:"required"`
            Filters    map[string]interface{} `json:"filters"`
        }

        if err := c.ShouldBindJSON(&request); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }

        taskID, err := service.SubmitDataExportTask(request.ExportType, request.Filters)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(202, gin.H{
            "task_id":    taskID,
            "status":     "queued",
            "check_url":  fmt.Sprintf("/async/tasks/%s", taskID),
            "message":    "Data export task has been queued",
        })
    }
}

// 主程序示例
func main() {
    // 初始化异步服务
    config := &AsyncConfig{
        RedisAddr:      "localhost:6379",
        QueueName:      "async_tasks",
        WorkerCount:    5,
        EnableRetries:  true,
        EnableEvents:   true,
        EnableSchedule: true,
    }

    asyncService, err := NewAsyncTaskService(config)
    if err != nil {
        log.Fatalf("Failed to create async service: %v", err)
    }

    if err := asyncService.Start(); err != nil {
        log.Fatalf("Failed to start async service: %v", err)
    }

    // 创建Gin引擎
    r := gin.New()

    // 中间件
    r.Use(gin.Logger())
    r.Use(gin.Recovery())
    r.Use(AsyncServiceMiddleware(asyncService))

    // 路由
    api := r.Group("/api")
    {
        // 异步任务端点
        async := api.Group("/async")
        {
            async.POST("/email", SendEmailHandler(asyncService))
            async.POST("/image", ProcessImageHandler(asyncService))
            async.POST("/export", ExportDataHandler(asyncService))
            async.GET("/tasks/:id", GetTaskStatusHandler(asyncService))
            async.GET("/tasks", ListTasksHandler(asyncService))
        }

        // 同步端点（用于对比）
        sync := api.Group("/sync")
        {
            sync.POST("/email", func(c *gin.Context) {
                var request struct {
                    To      string `json:"to" binding:"required,email"`
                    Subject string `json:"subject" binding:"required"`
                    Body    string `json:"body" binding:"required"`
                }

                if err := c.ShouldBindJSON(&request); err != nil {
                    c.JSON(400, gin.H{"error": err.Error()})
                    return
                }

                // 模拟同步邮件发送
                time.Sleep(1 * time.Second)

                c.JSON(200, gin.H{
                    "message":  "Email sent successfully",
                    "to":       request.To,
                    "subject":  request.Subject,
                    "sent_at":  time.Now(),
                })
            })
        }
    }

    // 启动服务器
    log.Println("Server starting on :8080")
    if err := r.Run(":8080"); err != nil {
        log.Fatalf("Failed to start server: %v", err)
    }
}
```

## 7. 最佳实践

### 7.1 性能优化
- **协程池**：使用协程池复用goroutine
- **批处理**：合并小任务批量处理
- **异步I/O**：使用非阻塞I/O操作
- **资源管理**：合理管理连接池和内存
- **监控指标**：建立完整的性能监控体系

### 7.2 可靠性保证
- **重试机制**：实现智能重试和退避策略
- **错误处理**：完善的错误处理和恢复机制
- **数据持久化**：任务状态持久化存储
- **幂等性**：确保任务重复执行不会产生副作用
- **超时控制**：设置合理的超时时间

### 7.3 运维建议
- **日志记录**：详细记录任务执行过程
- **监控告警**：建立任务执行监控和告警
- **容量规划**：根据负载情况调整资源
- **故障处理**：建立故障诊断和处理流程
- **定期维护**：清理过期任务和优化配置

---

这个Gin异步处理模式指南提供了完整的异步处理解决方案，涵盖基础异步、消息队列、任务队列、事件驱动等各种模式。通过这个指南，你可以构建一个高性能、高可用的异步处理系统。