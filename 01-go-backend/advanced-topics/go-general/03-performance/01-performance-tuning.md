# Go性能优化专项

## 目录
- [性能优化概述](#性能优化概述)
- [CPU性能优化](#cpu性能优化)
- [内存优化](#内存优化)
- [并发优化](#并发优化)
- [I/O优化](#io优化)
- [网络优化](#网络优化)
- [数据库优化](#数据库优化)
- [编译优化](#编译优化)
- [性能分析工具](#性能分析工具)
- [性能优化最佳实践](#性能优化最佳实践)

## 性能优化概述

### 优化原则
1. **数据驱动优化**：基于实际性能数据进行优化
2. **80/20原则**：优化最耗时的20%代码
3. **权衡取舍**：在性能、可读性、维护性之间找到平衡
4. **渐进式优化**：避免过早优化，但也不忽略关键路径

### 优化流程
```
性能分析 → 瓶颈识别 → 优化实施 → 效果验证 → 持续监控
```

## CPU性能优化

### 1. 算法复杂度优化

#### 时间复杂度选择
```go
// 优化前：O(n²)
func findDuplicatesOld(slice []int) []int {
    var duplicates []int
    for i := 0; i < len(slice); i++ {
        for j := i + 1; j < len(slice); j++ {
            if slice[i] == slice[j] {
                duplicates = append(duplicates, slice[i])
            }
        }
    }
    return duplicates
}

// 优化后：O(n)
func findDuplicatesNew(slice []int) []int {
    seen := make(map[int]bool)
    var duplicates []int

    for _, num := range slice {
        if seen[num] {
            duplicates = append(duplicates, num)
        } else {
            seen[num] = true
        }
    }
    return duplicates
}
```

#### 空间复杂度优化
```go
// 优化前：额外空间O(n)
func reverseSliceOld(slice []int) []int {
    reversed := make([]int, len(slice))
    for i, v := range slice {
        reversed[len(slice)-1-i] = v
    }
    return reversed
}

// 优化后：原地操作，空间O(1)
func reverseSliceNew(slice []int) {
    for i, j := 0, len(slice)-1; i < j; i, j = i+1, j-1 {
        slice[i], slice[j] = slice[j], slice[i]
    }
}
```

### 2. 循环优化

#### 减少循环内计算
```go
// 优化前
func processSliceOld(slice []int) {
    for i := 0; i < len(slice); i++ {
        result := expensiveFunction(slice[i], len(slice)) // len(slice)每次都计算
        // 处理结果
    }
}

// 优化后
func processSliceNew(slice []int) {
    length := len(slice) // 提前计算长度
    for i := 0; i < length; i++ {
        result := expensiveFunction(slice[i], length)
        // 处理结果
    }
}
```

#### 循环展开
```go
// 优化前
func sumSliceOld(slice []int) int {
    sum := 0
    for i := 0; i < len(slice); i++ {
        sum += slice[i]
    }
    return sum
}

// 优化后：循环展开
func sumSliceNew(slice []int) int {
    sum := 0
    length := len(slice)

    // 处理4个一组的元素
    i := 0
    for i <= length-4 {
        sum += slice[i] + slice[i+1] + slice[i+2] + slice[i+3]
        i += 4
    }

    // 处理剩余元素
    for i < length {
        sum += slice[i]
        i++
    }

    return sum
}
```

### 3. 分支预测优化

#### 热路径优先
```go
// 优化前
func processRequestOld(req *Request) {
    if req.IsValid() { // 较少执行
        // 处理无效请求
        return
    }

    // 处理有效请求
    // ... 大量代码
}

// 优化后
func processRequestNew(req *Request) {
    if !req.IsValid() { // 热路径优先
        // 处理有效请求
        // ... 大量代码
        return
    }

    // 处理无效请求
}
```

#### 位运算替代乘除
```go
// 优化前
func multiplyBy16Old(x int) int {
    return x * 16
}

func divideBy8Old(x int) int {
    return x / 8
}

// 优化后
func multiplyBy16New(x int) int {
    return x << 4 // 左移4位
}

func divideBy8New(x int) int {
    return x >> 3 // 右移3位
}
```

## 内存优化

### 1. 内存分配优化

#### 对象池模式
```go
import "sync"

// 对象池
type ObjectPool struct {
    pool sync.Pool
}

func NewObjectPool() *ObjectPool {
    return &ObjectPool{
        pool: sync.Pool{
            New: func() interface{} {
                return &ExpensiveObject{
                    data: make([]byte, 1024),
                }
            },
        },
    }
}

func (p *ObjectPool) Get() *ExpensiveObject {
    return p.pool.Get().(*ExpensiveObject)
}

func (p *ObjectPool) Put(obj *ExpensiveObject) {
    // 重置对象状态
    obj.Reset()
    p.pool.Put(obj)
}

type ExpensiveObject struct {
    data []byte
}

func (obj *ExpensiveObject) Reset() {
    for i := range obj.data {
        obj.data[i] = 0
    }
}
```

#### 预分配切片容量
```go
// 优化前：频繁扩容
func collectDataOld(items []string) []string {
    var result []string
    for _, item := range items {
        if len(item) > 5 {
            result = append(result, item) // 可能触发多次扩容
        }
    }
    return result
}

// 优化后：预分配容量
func collectDataNew(items []string) []string {
    // 预估容量
    capacity := 0
    for _, item := range items {
        if len(item) > 5 {
            capacity++
        }
    }

    result := make([]string, 0, capacity)
    for _, item := range items {
        if len(item) > 5 {
            result = append(result, item)
        }
    }
    return result
}
```

### 2. 内存布局优化

#### 结构体字段重排
```go
// 优化前：内存对齐不佳
type BadStruct struct {
    a bool    // 1字节 + 7字节填充
    b int64   // 8字节
    c int32   // 4字节 + 4字节填充
    d bool    // 1字节 + 7字节填充
} // 总共32字节

// 优化后：优化内存对齐
type GoodStruct struct {
    b int64   // 8字节
    c int32   // 4字节
    a bool    // 1字节
    d bool    // 1字节 + 2字节填充
} // 总共16字节
```

#### 使用指针减少拷贝
```go
// 优化前：大结构体拷贝
type LargeStruct struct {
    data [1024]byte
    more [4096]byte
}

func processStructOld(s LargeStruct) {
    // 处理结构体，但会拷贝整个结构体
}

// 优化后：使用指针
func processStructNew(s *LargeStruct) {
    // 处理结构体，只拷贝指针
}
```

### 3. 垃圾回收优化

#### 减少临时对象创建
```go
// 优化前：创建大量临时字符串
func concatenateStringsOld(parts []string) string {
    result := ""
    for _, part := range parts {
        result += part // 每次都创建新字符串
    }
    return result
}

// 优化后：使用strings.Builder
func concatenateStringsNew(parts []string) string {
    var builder strings.Builder
    for _, part := range parts {
        builder.WriteString(part)
    }
    return builder.String()
}
```

#### 内存复用
```go
import "sync"

// 内存缓冲区池
var bufferPool = sync.Pool{
    New: func() interface{} {
        return make([]byte, 1024)
    },
}

func processData(data []byte) {
    buf := bufferPool.Get().([]byte)
    defer bufferPool.Put(buf)

    // 复用缓冲区
    if len(data) > len(buf) {
        buf = make([]byte, len(data))
    }

    copy(buf, data)
    // 处理数据
}
```

## 并发优化

### 1. 协程池管理

#### 固定大小协程池
```go
type WorkerPool struct {
    tasks   chan Task
    workers int
    wg      sync.WaitGroup
}

type Task struct {
    ID      int
    Payload interface{}
    Process func(interface{}) error
}

func NewWorkerPool(workers int) *WorkerPool {
    pool := &WorkerPool{
        tasks:   make(chan Task, workers*2),
        workers: workers,
    }

    // 启动工作协程
    pool.wg.Add(workers)
    for i := 0; i < workers; i++ {
        go pool.worker()
    }

    return pool
}

func (p *WorkerPool) worker() {
    defer p.wg.Done()

    for task := range p.tasks {
        task.Process(task.Payload)
    }
}

func (p *WorkerPool) Submit(task Task) {
    p.tasks <- task
}

func (p *WorkerPool) Shutdown() {
    close(p.tasks)
    p.wg.Wait()
}
```

#### 动态协程池
```go
type DynamicWorkerPool struct {
    tasks        chan Task
    minWorkers   int
    maxWorkers   int
    currentWorkers int
    taskTimeout  time.Duration
    wg           sync.WaitGroup
    mu           sync.Mutex
}

func NewDynamicWorkerPool(min, max int) *DynamicWorkerPool {
    pool := &DynamicWorkerPool{
        tasks:        make(chan Task, 100),
        minWorkers:   min,
        maxWorkers:   max,
        currentWorkers: min,
        taskTimeout:  5 * time.Second,
    }

    pool.start()
    return pool
}

func (p *DynamicWorkerPool) start() {
    p.wg.Add(p.minWorkers)
    for i := 0; i < p.minWorkers; i++ {
        go p.dynamicWorker()
    }
}

func (p *DynamicWorkerPool) dynamicWorker() {
    defer p.wg.Done()

    for {
        select {
        case task := <-p.tasks:
            // 处理任务
            task.Process(task.Payload)

            // 检查是否需要缩减工作协程
            p.mu.Lock()
            if p.currentWorkers > p.minWorkers && len(p.tasks) < p.currentWorkers/2 {
                p.currentWorkers--
                p.mu.Unlock()
                return
            }
            p.mu.Unlock()

        case <-time.After(p.taskTimeout):
            // 超时后检查是否需要缩减工作协程
            p.mu.Lock()
            if p.currentWorkers > p.minWorkers {
                p.currentWorkers--
                p.mu.Unlock()
                return
            }
            p.mu.Unlock()
        }
    }
}

func (p *DynamicWorkerPool) Submit(task Task) {
    p.mu.Lock()

    // 检查是否需要增加工作协程
    if len(p.tasks) > p.currentWorkers && p.currentWorkers < p.maxWorkers {
        p.currentWorkers++
        p.wg.Add(1)
        go p.dynamicWorker()
    }

    p.mu.Unlock()
    p.tasks <- task
}
```

### 2. 锁优化

#### 读写分离锁
```go
import "sync"

type DataStore struct {
    mu     sync.RWMutex
    data   map[string]interface{}
    cache  map[string]interface{}
}

func (ds *DataStore) Get(key string) (interface{}, bool) {
    // 读锁
    ds.mu.RLock()
    defer ds.mu.RUnlock()

    // 先检查缓存
    if value, ok := ds.cache[key]; ok {
        return value, true
    }

    // 再检查主数据
    value, ok := ds.data[key]
    if ok {
        // 更新缓存
        ds.cache[key] = value
    }

    return value, ok
}

func (ds *DataStore) Set(key string, value interface{}) {
    // 写锁
    ds.mu.Lock()
    defer ds.mu.Unlock()

    ds.data[key] = value
    // 更新缓存
    ds.cache[key] = value
}

func (ds *DataStore) BatchUpdate(updates map[string]interface{}) {
    // 批量更新使用单个写锁
    ds.mu.Lock()
    defer ds.mu.Unlock()

    for key, value := range updates {
        ds.data[key] = value
        ds.cache[key] = value
    }
}
```

#### 无锁数据结构
```go
import (
    "sync/atomic"
    "unsafe"
)

// 无锁栈
type LockFreeStack struct {
    head unsafe.Pointer
}

type Node struct {
    value interface{}
    next  unsafe.Pointer
}

func NewLockFreeStack() *LockFreeStack {
    return &LockFreeStack{}
}

func (s *LockFreeStack) Push(value interface{}) {
    newNode := &Node{value: value}

    for {
        oldHead := atomic.LoadPointer(&s.head)
        newNode.next = oldHead

        if atomic.CompareAndSwapPointer(&s.head, oldHead, unsafe.Pointer(newNode)) {
            return
        }
    }
}

func (s *LockFreeStack) Pop() (interface{}, bool) {
    for {
        oldHead := atomic.LoadPointer(&s.head)
        if oldHead == nil {
            return nil, false
        }

        newHead := (*Node)(oldHead).next

        if atomic.CompareAndSwapPointer(&s.head, oldHead, newHead) {
            return (*Node)(oldHead).value, true
        }
    }
}
```

### 3. 通道优化

#### 缓冲通道使用
```go
// 优化前：无缓冲通道阻塞
func processChannelOld(data []int) {
    ch := make(chan int)

    // 生产者
    go func() {
        for _, v := range data {
            ch <- v // 可能阻塞
        }
        close(ch)
    }()

    // 消费者
    for v := range ch {
        process(v)
    }
}

// 优化后：缓冲通道
func processChannelNew(data []int) {
    ch := make(chan int, len(data)) // 缓冲大小等于数据量

    // 生产者
    go func() {
        for _, v := range data {
            ch <- v // 不会阻塞
        }
        close(ch)
    }()

    // 消费者
    for v := range ch {
        process(v)
    }
}
```

#### 批量通道操作
```go
// 批量处理通道数据
func batchProcessChannel(ch <-chan int, batchSize int) {
    batch := make([]int, 0, batchSize)

    for {
        select {
        case value, ok := <-ch:
            if !ok {
                // 处理剩余数据
                if len(batch) > 0 {
                    processBatch(batch)
                }
                return
            }

            batch = append(batch, value)

            if len(batch) >= batchSize {
                processBatch(batch)
                batch = batch[:0] // 重置batch
            }

        case <-time.After(100 * time.Millisecond):
            // 超时后处理当前批次
            if len(batch) > 0 {
                processBatch(batch)
                batch = batch[:0]
            }
        }
    }
}

func processBatch(batch []int) {
    // 批量处理逻辑
    fmt.Printf("Processing batch: %v\n", batch)
}
```

## I/O优化

### 1. 文件I/O优化

#### 缓冲读写
```go
// 优化前：频繁的小I/O操作
func copyFileOld(src, dst string) error {
    data, err := ioutil.ReadFile(src)
    if err != nil {
        return err
    }
    return ioutil.WriteFile(dst, data, 0644)
}

// 优化后：缓冲读写
func copyFileNew(src, dst string) error {
    srcFile, err := os.Open(src)
    if err != nil {
        return err
    }
    defer srcFile.Close()

    dstFile, err := os.Create(dst)
    if err != nil {
        return err
    }
    defer dstFile.Close()

    // 使用缓冲
    buf := make([]byte, 32*1024) // 32KB缓冲
    _, err = io.CopyBuffer(dstFile, srcFile, buf)
    return err
}
```

#### 内存映射文件
```go
import (
    "os"
    "syscall"
    "unsafe"
)

// 内存映射文件处理
func processLargeFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close()

    fileInfo, err := file.Stat()
    if err != nil {
        return err
    }

    size := fileInfo.Size()
    if size == 0 {
        return nil
    }

    // 内存映射
    data, err := syscall.Mmap(int(file.Fd()), 0, int(size), syscall.PROT_READ, syscall.MAP_SHARED)
    if err != nil {
        return err
    }
    defer syscall.Munmap(data)

    // 处理映射的内存
    processMemoryMapped(data)
    return nil
}

func processMemoryMapped(data []byte) {
    // 处理内存映射数据
    fmt.Printf("Processing %d bytes of mapped memory\n", len(data))
}
```

### 2. 网络I/O优化

#### 连接池
```go
import "net"

type ConnectionPool struct {
    connections chan net.Conn
    factory     func() (net.Conn, error)
    maxConn     int
}

func NewConnectionPool(factory func() (net.Conn, error), maxConn int) *ConnectionPool {
    pool := &ConnectionPool{
        connections: make(chan net.Conn, maxConn),
        factory:     factory,
        maxConn:     maxConn,
    }

    // 预创建连接
    for i := 0; i < maxConn/2; i++ {
        conn, err := factory()
        if err == nil {
            pool.connections <- conn
        }
    }

    return pool
}

func (p *ConnectionPool) Get() (net.Conn, error) {
    select {
    case conn := <-p.connections:
        return conn, nil
    default:
        return p.factory()
    }
}

func (p *ConnectionPool) Put(conn net.Conn) {
    select {
    case p.connections <- conn:
        // 连接放回池中
    default:
        // 池已满，关闭连接
        conn.Close()
    }
}
```

#### 零拷贝传输
```go
import "io"

// 零拷贝文件传输
func sendFile(w io.Writer, file *os.File) error {
    // 获取文件信息
    fileInfo, err := file.Stat()
    if err != nil {
        return err
    }

    // 使用sendfile系统调用（零拷贝）
    if fileWriter, ok := w.(interface {
        ReadFrom(r io.Reader) (int64, error)
    }); ok {
        _, err = fileWriter.ReadFrom(file)
        return err
    }

    // 回退到普通拷贝
    _, err = io.Copy(w, file)
    return err
}
```

## 网络优化

### 1. HTTP优化

#### 连接复用
```go
import "net/http"

// 优化前：每次请求创建新连接
func makeRequestsOld(urls []string) {
    client := &http.Client{}

    for _, url := range urls {
        resp, err := client.Get(url)
        if err != nil {
            continue
        }
        resp.Body.Close()
    }
}

// 优化后：连接复用
func makeRequestsNew(urls []string) {
    // 配置连接池
    transport := &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     30 * time.Second,
    }

    client := &http.Client{
        Transport: transport,
        Timeout:   10 * time.Second,
    }

    for _, url := range urls {
        resp, err := client.Get(url)
        if err != nil {
            continue
        }
        resp.Body.Close()
    }
}
```

#### HTTP/2优化
```go
// HTTP/2客户端优化
func createHTTP2Client() *http.Client {
    transport := &http.Transport{
        ForceAttemptHTTP2: true,

        // HTTP/2特定优化
        WriteBufferSize:    32 * 1024,
        ReadBufferSize:     32 * 1024,

        // 连接池配置
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    }

    return &http.Client{
        Transport: transport,
        Timeout:   30 * time.Second,
    }
}

// 并发HTTP请求
func concurrentRequests(client *http.Client, urls []string) {
    var wg sync.WaitGroup
    sem := make(chan struct{}, 10) // 限制并发数

    for _, url := range urls {
        wg.Add(1)
        sem <- struct{}{}

        go func(url string) {
            defer func() {
                <-sem
                wg.Done()
            }()

            resp, err := client.Get(url)
            if err != nil {
                return
            }
            resp.Body.Close()
        }(url)
    }

    wg.Wait()
}
```

### 2. 网络协议优化

#### TCP优化
```go
import (
    "net"
    "syscall"
)

// 优化TCP连接参数
func optimizeTCPConn(conn net.Conn) error {
    tcpConn, ok := conn.(*net.TCPConn)
    if !ok {
        return nil
    }

    // 设置socket选项
    file, err := tcpConn.File()
    if err != nil {
        return err
    }
    defer file.Close()

    // TCP_NODELAY - 禁用Nagle算法
    err = syscall.SetsockoptInt(int(file.Fd()), syscall.IPPROTO_TCP, syscall.TCP_NODELAY, 1)
    if err != nil {
        return err
    }

    // SO_KEEPALIVE - 启用keepalive
    err = syscall.SetsockoptInt(int(file.Fd()), syscall.SOL_SOCKET, syscall.SO_KEEPALIVE, 1)
    if err != nil {
        return err
    }

    // SO_REUSEADDR - 地址重用
    err = syscall.SetsockoptInt(int(file.Fd()), syscall.SOL_SOCKET, syscall.SO_REUSEADDR, 1)
    if err != nil {
        return err
    }

    return nil
}

// TCP服务器优化
func startTCPServer(address string) error {
    listener, err := net.Listen("tcp", address)
    if err != nil {
        return err
    }

    for {
        conn, err := listener.Accept()
        if err != nil {
            continue
        }

        // 优化连接参数
        optimizeTCPConn(conn)

        go handleConnection(conn)
    }
}

func handleConnection(conn net.Conn) {
    defer conn.Close()

    // 设置读写超时
    conn.SetDeadline(time.Now().Add(30 * time.Second))

    // 处理连接
    // ...
}
```

#### UDP优化
```go
// UDP服务器优化
func startUDPServer(address string) error {
    addr, err := net.ResolveUDPAddr("udp", address)
    if err != nil {
        return err
    }

    conn, err := net.ListenUDP("udp", addr)
    if err != nil {
        return err
    }

    // 设置读取缓冲区大小
    err = conn.SetReadBuffer(1024 * 1024) // 1MB
    if err != nil {
        return err
    }

    // 设置写入缓冲区大小
    err = conn.SetWriteBuffer(1024 * 1024) // 1MB
    if err != nil {
        return err
    }

    buffer := make([]byte, 64*1024) // 64KB缓冲

    for {
        n, clientAddr, err := conn.ReadFromUDP(buffer)
        if err != nil {
            continue
        }

        go func(data []byte, addr *net.UDPAddr) {
            processUDPData(data)
            conn.WriteToUDP(data, addr)
        }(buffer[:n], clientAddr)
    }
}

func processUDPData(data []byte) {
    // 处理UDP数据
}
```

## 数据库优化

### 1. 连接池优化

#### GORM连接池配置
```go
import (
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "time"
)

func setupDatabase(dsn string) (*gorm.DB, error) {
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        return nil, err
    }

    // 获取底层sql.DB
    sqlDB, err := db.DB()
    if err != nil {
        return nil, err
    }

    // 优化连接池配置
    sqlDB.SetMaxIdleConns(10)           // 最大空闲连接数
    sqlDB.SetMaxOpenConns(100)          // 最大打开连接数
    sqlDB.SetConnMaxLifetime(time.Hour) // 连接最大生命周期
    sqlDB.SetConnMaxIdleTime(30 * time.Minute) // 空闲连接最大存活时间

    return db, nil
}
```

#### 连接池监控
```go
type ConnectionPoolMonitor struct {
    db *gorm.DB
}

func NewConnectionPoolMonitor(db *gorm.DB) *ConnectionPoolMonitor {
    return &ConnectionPoolMonitor{db: db}
}

func (m *ConnectionPoolMonitor) GetStats() map[string]interface{} {
    sqlDB, err := m.db.DB()
    if err != nil {
        return nil
    }

    stats := sqlDB.Stats()

    return map[string]interface{}{
        "open_connections":     stats.OpenConnections,
        "in_use":             stats.InUse,
        "idle":               stats.Idle,
        "wait_count":         stats.WaitCount,
        "wait_duration":      stats.WaitDuration,
        "max_idle_closed":    stats.MaxIdleClosed,
        "max_lifetime_closed": stats.MaxLifetimeClosed,
    }
}

func (m *ConnectionPoolMonitor) StartMonitoring(interval time.Duration) {
    ticker := time.NewTicker(interval)
    defer ticker.Stop()

    for range ticker.C {
        stats := m.GetStats()
        log.Printf("Connection Pool Stats: %+v", stats)

        // 检查连接池健康状态
        if stats["wait_count"].(int64) > 100 {
            log.Println("Warning: High wait count detected")
        }
    }
}
```

### 2. 查询优化

#### 批量操作
```go
// 优化前：逐条插入
func batchInsertOld(db *gorm.DB, users []User) error {
    for _, user := range users {
        if err := db.Create(&user).Error; err != nil {
            return err
        }
    }
    return nil
}

// 优化后：批量插入
func batchInsertNew(db *gorm.DB, users []User) error {
    // 使用Create批量插入
    return db.Create(&users).Error
}

// 更大的批量操作
func batchInsertInChunks(db *gorm.DB, users []User, chunkSize int) error {
    for i := 0; i < len(users); i += chunkSize {
        end := i + chunkSize
        if end > len(users) {
            end = len(users)
        }

        chunk := users[i:end]
        if err := db.Create(&chunk).Error; err != nil {
            return err
        }
    }
    return nil
}
```

#### 预编译语句
```go
// 预编译语句优化
func prepareStatements(db *gorm.DB) error {
    // 预编译常用查询
    insertStmt, err := db.DB().Prepare(`
        INSERT INTO users (name, email, created_at)
        VALUES ($1, $2, $3)
    `)
    if err != nil {
        return err
    }
    defer insertStmt.Close()

    updateStmt, err := db.DB().Prepare(`
        UPDATE users SET name = $1, email = $2
        WHERE id = $3
    `)
    if err != nil {
        return err
    }
    defer updateStmt.Close()

    // 使用预编译语句
    _, err = insertStmt.Exec("John Doe", "john@example.com", time.Now())
    if err != nil {
        return err
    }

    _, err = updateStmt.Exec("John Smith", "john.smith@example.com", 1)
    return err
}
```

#### 索引优化
```go
// 创建优化索引
func createOptimizedIndexes(db *gorm.DB) error {
    // 复合索引
    if err := db.Exec(`
        CREATE INDEX IF NOT EXISTS idx_users_name_email
        ON users(name, email)
    `).Error; err != nil {
        return err
    }

    // 部分索引
    if err := db.Exec(`
        CREATE INDEX IF NOT EXISTS idx_active_users
        ON users(id) WHERE active = true
    `).Error; err != nil {
        return err
    }

    // 函数索引
    if err := db.Exec(`
        CREATE INDEX IF NOT EXISTS idx_users_lower_email
        ON users(LOWER(email))
    `).Error; err != nil {
        return err
    }

    return nil
}
```

## 编译优化

### 1. 编译优化标志

#### 构建优化
```bash
# 生产环境编译优化
go build -ldflags="-s -w" -o app main.go

# 去除调试信息和符号表
-s: 去除符号表
-w: 去除DWARF调试信息

# 更激进的优化
go build -ldflags="-s -w -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" \
    -buildmode=pie \
    -trimpath \
    -o app main.go
```

#### 编译时优化
```go
// 编译时优化：内联函数
//go:noinline
func noInlineFunction() {
    // 防止编译器内联优化
}

// 编译时优化：分支预测优化
func likelyOptimized(condition bool) {
    if likely(condition) { // 提示编译器condition很可能为true
        // 热路径
    } else {
        // 冷路径
    }
}

// 编译时优化：函数内联
//go:inline
func inlineFunction(x, y int) int {
    return x + y
}
```

### 2. 链接时优化

#### 链接时优化
```go
package main

/*
#cgo LDFLAGS: -flto
#cgo CFLAGS: -O3
import "C"
*/
import "fmt"

func main() {
    fmt.Println("Link Time Optimization")
}
```

#### 内存布局优化
```go
// 内存对齐优化
type AlignedStruct struct {
    // 8字节对齐
    Value1 int64
    // 4字节对齐
    Value2 int32
    // 2字节对齐
    Value3 int16
    // 1字节对齐
    Value4 bool
}

// 使用内存池优化
var arenaPool = sync.Pool{
    New: func() interface{} {
        return make([]byte, 1024*1024) // 1MB arena
    },
}

func allocateFromArena(size int) []byte {
    arena := arenaPool.Get().([]byte)
    if size > len(arena) {
        arena = make([]byte, size)
    }
    return arena[:size]
}

func releaseArena(arena []byte) {
    arenaPool.Put(arena)
}
```

## 性能分析工具

### 1. CPU性能分析

#### 使用pprof
```go
import (
    "net/http"
    _ "net/http/pprof"
    "runtime/pprof"
    "os"
)

func startProfiling() {
    // 启动pprof HTTP服务器
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()

    // CPU性能分析
    cpuProfile, err := os.Create("cpu.prof")
    if err != nil {
        log.Fatal(err)
    }
    defer cpuProfile.Close()

    err = pprof.StartCPUProfile(cpuProfile)
    if err != nil {
        log.Fatal(err)
    }
    defer pprof.StopCPUProfile()

    // 内存性能分析
    memProfile, err := os.Create("mem.prof")
    if err != nil {
        log.Fatal(err)
    }
    defer memProfile.Close()

    runtime.GC() // GC后获取内存快照
    err = pprof.WriteHeapProfile(memProfile)
    if err != nil {
        log.Fatal(err)
    }
}
```

#### 基准测试
```go
func BenchmarkStringConcat(b *testing.B) {
    strings := make([]string, b.N)
    for i := range strings {
        strings[i] = "test"
    }

    b.ResetTimer()
    result := ""
    for _, s := range strings {
        result += s
    }
    b.StopTimer()
}

func BenchmarkStringBuilder(b *testing.B) {
    strings := make([]string, b.N)
    for i := range strings {
        strings[i] = "test"
    }

    b.ResetTimer()
    var builder strings.Builder
    for _, s := range strings {
        builder.WriteString(s)
    }
    b.StopTimer()
}
```

### 2. 内存分析

#### 内存泄漏检测
```go
import "runtime"

func detectMemoryLeaks() {
    var m1, m2 runtime.MemStats

    // 获取内存统计
    runtime.GC()
    runtime.ReadMemStats(&m1)

    // 执行操作
    performOperation()

    // 再次获取内存统计
    runtime.GC()
    runtime.ReadMemStats(&m2)

    // 分析内存增长
    allocated := m2.TotalAlloc - m1.TotalAlloc
    inUse := m2.Alloc - m1.Alloc

    fmt.Printf("Allocated: %d bytes\n", allocated)
    fmt.Printf("In use: %d bytes\n", inUse)

    // 如果内存使用持续增长，可能存在泄漏
    if inUse > 1024*1024 { // 1MB阈值
        fmt.Println("Warning: Potential memory leak detected")
    }
}
```

#### 对象分配分析
```go
func trackAllocations() {
    var m runtime.MemStats

    runtime.ReadMemStats(&m)

    fmt.Printf("Memory Stats:\n")
    fmt.Printf("  Alloc: %d bytes\n", m.Alloc)
    fmt.Printf("  TotalAlloc: %d bytes\n", m.TotalAlloc)
    fmt.Printf("  Sys: %d bytes\n", m.Sys)
    fmt.Printf("  NumGC: %d\n", m.NumGC)
    fmt.Printf("  Goroutines: %d\n", runtime.NumGoroutine())
}
```

## 性能优化最佳实践

### 1. 性能优化清单

#### 开发阶段
- [ ] 使用合适的数据结构和算法
- [ ] 避免不必要的内存分配
- [ ] 减少锁的粒度和持有时间
- [ ] 使用缓冲I/O操作
- [ ] 实现连接池和对象池
- [ ] 优化数据库查询和索引

#### 编译阶段
- [ ] 使用适当的编译优化标志
- [ ] 启用链接时优化
- [ ] 优化内存布局和对齐
- [ ] 去除不必要的调试信息

#### 运行阶段
- [ ] 监控关键性能指标
- [ ] 定期进行性能分析
- [ ] 优化GC参数和内存配置
- [ ] 使用缓存和CDN加速
- [ ] 实现负载均衡和故障转移

### 2. 性能优化模式

#### 缓存模式
```go
// 多级缓存实现
type MultiLevelCache struct {
    l1Cache *sync.Map    // 内存缓存
    l2Cache *redis.Client // Redis缓存
    l3Cache *gorm.DB     // 数据库
}

func (c *MultiLevelCache) Get(key string) (interface{}, error) {
    // L1缓存
    if value, ok := c.l1Cache.Load(key); ok {
        return value, nil
    }

    // L2缓存
    value, err := c.l2Cache.Get(key).Result()
    if err == nil {
        c.l1Cache.Store(key, value)
        return value, nil
    }

    // L3缓存
    // 从数据库获取并更新缓存
    // ...

    return nil, fmt.Errorf("key not found")
}
```

#### 延迟加载模式
```go
// 延迟加载实现
type LazyLoader struct {
    once    sync.Once
    value   interface{}
    loadFn  func() (interface{}, error)
    err     error
}

func NewLazyLoader(loadFn func() (interface{}, error)) *LazyLoader {
    return &LazyLoader{loadFn: loadFn}
}

func (l *LazyLoader) Get() (interface{}, error) {
    l.once.Do(func() {
        l.value, l.err = l.loadFn()
    })
    return l.value, l.err
}
```

### 3. 性能监控

#### 实时监控
```go
import "time"

type PerformanceMonitor struct {
    metrics map[string]float64
    mu      sync.RWMutex
}

func NewPerformanceMonitor() *PerformanceMonitor {
    return &PerformanceMonitor{
        metrics: make(map[string]float64),
    }
}

func (m *PerformanceMonitor) RecordMetric(name string, value float64) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.metrics[name] = value
}

func (m *PerformanceMonitor) GetMetric(name string) float64 {
    m.mu.RLock()
    defer m.mu.RUnlock()
    return m.metrics[name]
}

func (m *PerformanceMonitor) StartMonitoring() {
    ticker := time.NewTicker(5 * time.Second)
    defer ticker.Stop()

    for range ticker.C {
        m.collectMetrics()
    }
}

func (m *PerformanceMonitor) collectMetrics() {
    // 收集系统指标
    var m1, m2 runtime.MemStats

    runtime.ReadMemStats(&m1)
    time.Sleep(time.Second)
    runtime.ReadMemStats(&m2)

    // 计算内存分配速率
    allocationRate := float64(m2.TotalAlloc-m1.TotalAlloc) / 1024 / 1024 // MB/s

    m.RecordMetric("memory_allocation_rate", allocationRate)
    m.RecordMetric("goroutine_count", float64(runtime.NumGoroutine()))
    m.RecordMetric("gc_count", float64(m2.NumGC))
}
```

这个Go性能优化专项文档涵盖了CPU、内存、并发、I/O、网络、数据库、编译等各个方面的优化技术，提供了实际可用的代码示例和最佳实践。通过这些优化技术，可以显著提升Go应用的性能表现。