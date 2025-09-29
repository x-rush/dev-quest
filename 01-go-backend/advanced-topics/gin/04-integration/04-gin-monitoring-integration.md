# Gin监控集成最佳实践

## 目录
- [监控概述](#监控概述)
- [指标收集](#指标收集)
- [日志管理](#日志管理)
- [分布式追踪](#分布式追踪)
- [性能监控](#性能监控)
- [告警机制](#告警机制)
- [可视化监控](#可视化监控)
- [监控最佳实践](#监控最佳实践)
- [故障排查](#故障排查)

## 监控概述

### 监控的重要性
- **性能优化**：识别性能瓶颈和优化机会
- **故障预测**：提前发现潜在问题
- **故障排查**：快速定位和解决问题
- **容量规划**：为系统扩展提供数据支持
- **用户体验**：监控用户访问体验
- **业务指标**：监控关键业务指标

### 监控架构
```
应用层 → 监控代理 → 监控存储 → 可视化平台
   ↓          ↓          ↓          ↓
指标收集   数据聚合   数据存储   告警分析
```

### 监控类型
- **基础设施监控**：CPU、内存、磁盘、网络
- **应用性能监控**：响应时间、吞吐量、错误率
- **业务监控**：订单量、用户活跃度、转化率
- **日志监控**：错误日志、访问日志、业务日志
- **链路追踪**：请求链路、服务依赖、性能分析

## 指标收集

### Prometheus集成
```go
// 指标定义
var (
    // HTTP请求计数器
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )

    // HTTP请求持续时间
    httpRequestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration in seconds",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint"},
    )

    // 当前活跃连接数
    activeConnections = prometheus.NewGauge(
        prometheus.GaugeOpts{
            Name: "http_active_connections",
            Help: "Number of active HTTP connections",
        },
    )

    // 数据库连接池状态
    dbConnections = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "db_connections",
            Help: "Database connection pool status",
        },
        []string{"state"}, // idle, active, total
    )
)

// 注册指标
func init() {
    prometheus.MustRegister(httpRequestsTotal)
    prometheus.MustRegister(httpRequestDuration)
    prometheus.MustRegister(activeConnections)
    prometheus.MustRegister(dbConnections)
}

// 监控中间件
func PrometheusMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        method := c.Request.Method

        // 增加活跃连接数
        activeConnections.Inc()
        defer activeConnections.Dec()

        c.Next()

        // 记录请求指标
        duration := time.Since(start).Seconds()
        status := fmt.Sprintf("%d", c.Writer.Status())

        httpRequestsTotal.WithLabelValues(method, path, status).Inc()
        httpRequestDuration.WithLabelValues(method, path).Observe(duration)
    }
}
```

### 自定义指标
```go
// 业务指标收集器
type BusinessMetrics struct {
    orderCount    prometheus.Counter
    revenue       prometheus.Counter
    userCount     prometheus.Gauge
    productViews  prometheus.Counter
}

// 创建业务指标
func NewBusinessMetrics() *BusinessMetrics {
    return &BusinessMetrics{
        orderCount: prometheus.NewCounter(
            prometheus.CounterOpts{
                Name: "business_orders_total",
                Help: "Total number of orders",
            },
        ),
        revenue: prometheus.NewCounter(
            prometheus.CounterOpts{
                Name: "business_revenue_total",
                Help: "Total revenue",
            },
        ),
        userCount: prometheus.NewGauge(
            prometheus.GaugeOpts{
                Name: "business_active_users",
                Help: "Number of active users",
            },
        ),
        productViews: prometheus.NewCounter(
            prometheus.CounterOpts{
                Name: "business_product_views_total",
                Help: "Total number of product views",
            },
        ),
    }
}

// 注册业务指标
func (m *BusinessMetrics) Register() {
    prometheus.MustRegister(m.orderCount)
    prometheus.MustRegister(m.revenue)
    prometheus.MustRegister(m.userCount)
    prometheus.MustRegister(m.productViews)
}

// 记录订单
func (m *BusinessMetrics) RecordOrder(amount float64) {
    m.orderCount.Inc()
    m.revenue.Add(amount)
}

// 更新活跃用户数
func (m *BusinessMetrics) UpdateActiveUsers(count int) {
    m.userCount.Set(float64(count))
}

// 记录产品查看
func (m *BusinessMetrics) RecordProductView() {
    m.productViews.Inc()
}
```

### 数据库监控
```go
// 数据库监控包装器
type MonitoredDB struct {
    db *gorm.DB
    metrics *DatabaseMetrics
}

// 数据库指标
type DatabaseMetrics struct {
    queryCount     prometheus.CounterVec
    queryDuration  prometheus.HistogramVec
    queryErrors    prometheus.CounterVec
    connectionPool *prometheus.GaugeVec
}

// 创建监控数据库
func NewMonitoredDB(db *gorm.DB) *MonitoredDB {
    metrics := &DatabaseMetrics{
        queryCount: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "db_queries_total",
                Help: "Total number of database queries",
            },
            []string{"operation", "table"},
        ),
        queryDuration: *prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name:    "db_query_duration_seconds",
                Help:    "Database query duration in seconds",
                Buckets: []float64{0.001, 0.01, 0.1, 1, 10},
            },
            []string{"operation", "table"},
        ),
        queryErrors: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "db_query_errors_total",
                Help: "Total number of database query errors",
            },
            []string{"operation", "table"},
        ),
        connectionPool: prometheus.NewGaugeVec(
            prometheus.GaugeOpts{
                Name: "db_connection_pool",
                Help: "Database connection pool status",
            },
            []string{"state"},
        ),
    }

    // 注册指标
    prometheus.MustRegister(&metrics.queryCount)
    prometheus.MustRegister(&metrics.queryDuration)
    prometheus.MustRegister(&metrics.queryErrors)
    prometheus.MustRegister(metrics.connectionPool)

    return &MonitoredDB{db: db, metrics: metrics}
}

// 监控查询执行
func (m *MonitoredDB) WithMetrics(operation, table string, fn func(*gorm.DB) *gorm.DB) *gorm.DB {
    start := time.Now()

    // 记录查询开始
    m.metrics.queryCount.WithLabelValues(operation, table).Inc()

    // 执行查询
    result := fn(m.db)

    // 记录查询耗时
    duration := time.Since(start).Seconds()
    m.metrics.queryDuration.WithLabelValues(operation, table).Observe(duration)

    // 检查错误
    if result.Error != nil {
        m.metrics.queryErrors.WithLabelValues(operation, table).Inc()
    }

    return result
}

// 更新连接池指标
func (m *MonitoredDB) UpdateConnectionPoolMetrics() {
    sqlDB, err := m.db.DB()
    if err != nil {
        return
    }

    stats := sqlDB.Stats()
    m.metrics.connectionPool.WithLabelValues("idle").Set(float64(stats.Idle))
    m.metrics.connectionPool.WithLabelValues("active").Set(float64(stats.InUse))
    m.metrics.connectionPool.WithLabelValues("total").Set(float64(stats.OpenConnections))
}
```

## 日志管理

### 结构化日志
```go
// 日志级别
type LogLevel int

const (
    DebugLevel LogLevel = iota
    InfoLevel
    WarnLevel
    ErrorLevel
    FatalLevel
)

// 日志条目
type LogEntry struct {
    Timestamp time.Time                 `json:"timestamp"`
    Level     LogLevel                 `json:"level"`
    Message   string                    `json:"message"`
    Fields    map[string]interface{}    `json:"fields,omitempty"`
    TraceID   string                    `json:"trace_id,omitempty"`
    SpanID    string                    `json:"span_id,omitempty"`
    UserID    string                    `json:"user_id,omitempty"`
    RequestID string                    `json:"request_id,omitempty"`
}

// 日志记录器
type StructuredLogger struct {
    output   io.Writer
    level    LogLevel
    fields   map[string]interface{}
}

// 创建结构化日志记录器
func NewStructuredLogger(output io.Writer, level LogLevel) *StructuredLogger {
    return &StructuredLogger{
        output: output,
        level:  level,
        fields: make(map[string]interface{}),
    }
}

// 记录日志
func (l *StructuredLogger) log(level LogLevel, message string, fields map[string]interface{}) {
    if level < l.level {
        return
    }

    entry := LogEntry{
        Timestamp: time.Now(),
        Level:     level,
        Message:   message,
        Fields:    make(map[string]interface{}),
    }

    // 合并字段
    for k, v := range l.fields {
        entry.Fields[k] = v
    }
    for k, v := range fields {
        entry.Fields[k] = v
    }

    // 序列化并输出
    data, _ := json.Marshal(entry)
    fmt.Fprintln(l.output, string(data))
}

// 级别方法
func (l *StructuredLogger) Debug(message string, fields ...map[string]interface{}) {
    l.log(DebugLevel, message, mergeFields(fields...))
}

func (l *StructuredLogger) Info(message string, fields ...map[string]interface{}) {
    l.log(InfoLevel, message, mergeFields(fields...))
}

func (l *StructuredLogger) Warn(message string, fields ...map[string]interface{}) {
    l.log(WarnLevel, message, mergeFields(fields...))
}

func (l *StructuredLogger) Error(message string, fields ...map[string]interface{}) {
    l.log(ErrorLevel, message, mergeFields(fields...))
}

// 合并字段
func mergeFields(fields ...map[string]interface{}) map[string]interface{} {
    result := make(map[string]interface{})
    for _, field := range fields {
        for k, v := range field {
            result[k] = v
        }
    }
    return result
}

// 日志中间件
func LoggingMiddleware(logger *StructuredLogger) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        method := c.Request.Method

        // 生成请求ID
        requestID := generateID()
        c.Header("X-Request-ID", requestID)

        // 记录请求开始
        logger.Info("Request started", map[string]interface{}{
            "method":     method,
            "path":       path,
            "request_id": requestID,
            "client_ip":  c.ClientIP(),
            "user_agent": c.Request.UserAgent(),
        })

        c.Next()

        // 记录请求完成
        duration := time.Since(start)
        status := c.Writer.Status()
        size := c.Writer.Size()

        logger.Info("Request completed", map[string]interface{}{
            "method":      method,
            "path":        path,
            "status":      status,
            "duration":    duration,
            "size":        size,
            "request_id":  requestID,
            "user_id":     c.GetString("user_id"),
        })
    }
}
```

### 日志聚合
```go
// 日志聚合器
type LogAggregator struct {
    buffer    chan *LogEntry
    batchSize int
    flushInterval time.Duration
    processors []LogProcessor
}

// 日志处理器
type LogProcessor interface {
    Process(logs []*LogEntry) error
}

// 日志发送器
type LogSender struct {
    endpoint string
    client   *http.Client
}

// 创建日志聚合器
func NewLogAggregator(bufferSize, batchSize int, flushInterval time.Duration) *LogAggregator {
    aggregator := &LogAggregator{
        buffer:        make(chan *LogEntry, bufferSize),
        batchSize:     batchSize,
        flushInterval: flushInterval,
        processors:    make([]LogProcessor, 0),
    }

    // 启动聚合协程
    go aggregator.run()

    return aggregator
}

// 运行聚合器
func (a *LogAggregator) run() {
    ticker := time.NewTicker(a.flushInterval)
    defer ticker.Stop()

    batch := make([]*LogEntry, 0, a.batchSize)

    for {
        select {
        case log := <-a.buffer:
            batch = append(batch, log)
            if len(batch) >= a.batchSize {
                a.flush(batch)
                batch = batch[:0]
            }
        case <-ticker.C:
            if len(batch) > 0 {
                a.flush(batch)
                batch = batch[:0]
            }
        }
    }
}

// 刷新日志批次
func (a *LogAggregator) flush(batch []*LogEntry) {
    var wg sync.WaitGroup

    for _, processor := range a.processors {
        wg.Add(1)
        go func(p LogProcessor) {
            defer wg.Done()
            if err := p.Process(batch); err != nil {
                log.Printf("Log processor error: %v", err)
            }
        }(processor)
    }

    wg.Wait()
}

// 添加日志
func (a *LogAggregator) Add(log *LogEntry) {
    a.buffer <- log
}

// 添加处理器
func (a *LogAggregator) AddProcessor(processor LogProcessor) {
    a.processors = append(a.processors, processor)
}

// HTTP日志发送器
func (s *LogSender) Process(logs []*LogEntry) error {
    data, err := json.Marshal(logs)
    if err != nil {
        return err
    }

    resp, err := s.client.Post(s.endpoint, "application/json", bytes.NewBuffer(data))
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("log sender returned status %d", resp.StatusCode)
    }

    return nil
}
```

### 错误日志追踪
```go
// 错误追踪器
type ErrorTracker struct {
    projectName string
    environment string
    sender      ErrorSender
}

// 错误发送器
type ErrorSender interface {
    Send(error *ErrorReport) error
}

// 错误报告
type ErrorReport struct {
    Timestamp   time.Time                 `json:"timestamp"`
    Project     string                    `json:"project"`
    Environment string                    `json:"environment"`
    Type        string                    `json:"type"`
    Message     string                    `json:"message"`
    StackTrace  string                    `json:"stack_trace"`
    Context     map[string]interface{}    `json:"context"`
    Request     *RequestInfo              `json:"request,omitempty"`
    User        *UserInfo                 `json:"user,omitempty"`
}

// 请求信息
type RequestInfo struct {
    Method     string            `json:"method"`
    URL        string            `json:"url"`
    Headers    map[string]string `json:"headers"`
    Body       string            `json:"body,omitempty"`
    RemoteAddr string            `json:"remote_addr"`
}

// 用户信息
type UserInfo struct {
    ID       string `json:"id"`
    Email    string `json:"email,omitempty"`
    Username string `json:"username,omitempty"`
}

// 创建错误追踪器
func NewErrorTracker(projectName, environment string, sender ErrorSender) *ErrorTracker {
    return &ErrorTracker{
        projectName: projectName,
        environment: environment,
        sender:      sender,
    }
}

// 追踪错误
func (t *ErrorTracker) TrackError(err error, context map[string]interface{}, c *gin.Context) {
    // 获取调用栈
    stackTrace := getStackTrace()

    // 构建错误报告
    report := &ErrorReport{
        Timestamp:   time.Now(),
        Project:     t.projectName,
        Environment: t.environment,
        Type:        reflect.TypeOf(err).String(),
        Message:     err.Error(),
        StackTrace:  stackTrace,
        Context:     context,
    }

    // 添加请求信息
    if c != nil {
        report.Request = &RequestInfo{
            Method:     c.Request.Method,
            URL:        c.Request.URL.String(),
            Headers:    getHeaders(c.Request),
            RemoteAddr: c.Request.RemoteAddr,
        }
    }

    // 发送错误报告
    if err := t.sender.Send(report); err != nil {
        log.Printf("Failed to send error report: %v", err)
    }
}

// 获取调用栈
func getStackTrace() string {
    buf := make([]byte, 4096)
    n := runtime.Stack(buf, false)
    return string(buf[:n])
}

// 获取请求头
func getHeaders(req *http.Request) map[string]string {
    headers := make(map[string]string)
    for key, values := range req.Header {
        if len(values) > 0 {
            headers[key] = values[0]
        }
    }
    return headers
}
```

## 分布式追踪

### Jaeger集成
```go
// Jaeger追踪器
type JaegerTracer struct {
    tracer opentracing.Tracer
    closer io.Closer
}

// 创建Jaeger追踪器
func NewJaegerTracer(serviceName, agentHost string) (*JaegerTracer, error) {
    cfg := jaegercfg.Configuration{
        ServiceName: serviceName,
        Sampler: &jaegercfg.SamplerConfig{
            Type:  jaeger.SamplerTypeConst,
            Param: 1,
        },
        Reporter: &jaegercfg.ReporterConfig{
            LogSpans:           true,
            LocalAgentHostPort: agentHost,
        },
    }

    tracer, closer, err := cfg.NewTracer()
    if err != nil {
        return nil, err
    }

    return &JaegerTracer{
        tracer: tracer,
        closer: closer,
    }, nil
}

// 关闭追踪器
func (t *JaegerTracer) Close() error {
    return t.closer.Close()
}

// 追踪中间件
func JaegerMiddleware(tracer *JaegerTracer) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 从请求头获取追踪上下文
        wireContext, err := tracer.tracer.Extract(
            opentracing.HTTPHeaders,
            opentracing.HTTPHeadersCarrier(c.Request.Header),
        )

        var span opentracing.Span
        if err != nil {
            span = tracer.tracer.StartSpan(c.Request.URL.Path)
        } else {
            span = tracer.tracer.StartSpan(c.Request.URL.Path, opentracing.ChildOf(wireContext))
        }
        defer span.Finish()

        // 设置追踪上下文
        ctx := opentracing.ContextWithSpan(c.Request.Context(), span)
        c.Request = c.Request.WithContext(ctx)

        // 添加标签
        span.SetTag("http.method", c.Request.Method)
        span.SetTag("http.url", c.Request.URL.String())
        span.SetTag("component", "gin")

        c.Next()

        // 添加响应状态码标签
        span.SetTag("http.status_code", c.Writer.Status())
    }
}

// 开始子追踪
func (t *JaegerTracer) StartSpan(operationName string, parentCtx context.Context) (opentracing.Span, context.Context) {
    if parentCtx == nil {
        return t.tracer.StartSpan(operationName)
    }

    return opentracing.StartSpanFromContext(parentCtx, operationName)
}

// 为HTTP客户端添加追踪
func (t *JaegerTracer) InjectHTTPHeaders(span opentracing.Span, req *http.Request) {
    err := t.tracer.Inject(
        span.Context(),
        opentracing.HTTPHeaders,
        opentracing.HTTPHeadersCarrier(req.Header),
    )
    if err != nil {
        log.Printf("Failed to inject tracing headers: %v", err)
    }
}
```

### 自定义追踪器
```go
// 自定义追踪器
type CustomTracer struct {
    serviceName string
    reporter    TraceReporter
}

// 追踪报告器
type TraceReporter interface {
    Report(span *Span) error
}

// 追踪跨度
type Span struct {
    TraceID    string            `json:"trace_id"`
    SpanID     string            `json:"span_id"`
    ParentID   string            `json:"parent_id,omitempty"`
    Operation  string            `json:"operation"`
    StartTime  time.Time         `json:"start_time"`
    EndTime    time.Time         `json:"end_time"`
    Duration   time.Duration     `json:"duration"`
    Tags       map[string]string `json:"tags"`
    Logs       []LogEntry        `json:"logs"`
    References []SpanReference   `json:"references"`
}

// 跨度引用
type SpanReference struct {
    Type  string `json:"type"`
    TraceID string `json:"trace_id"`
    SpanID string `json:"span_id"`
}

// 创建自定义追踪器
func NewCustomTracer(serviceName string, reporter TraceReporter) *CustomTracer {
    return &CustomTracer{
        serviceName: serviceName,
        reporter:    reporter,
    }
}

// 开始跨度
func (t *CustomTracer) StartSpan(operation string, parentSpan *Span) *Span {
    span := &Span{
        TraceID:   generateTraceID(),
        SpanID:    generateSpanID(),
        Operation: operation,
        StartTime: time.Now(),
        Tags:      make(map[string]string),
        Logs:      make([]LogEntry, 0),
    }

    // 设置父跨度
    if parentSpan != nil {
        span.ParentID = parentSpan.SpanID
        span.TraceID = parentSpan.TraceID
    }

    // 添加服务名称标签
    span.Tags["service.name"] = t.serviceName

    return span
}

// 完成跨度
func (t *CustomTracer) FinishSpan(span *Span) {
    span.EndTime = time.Now()
    span.Duration = span.EndTime.Sub(span.StartTime)

    // 报告跨度
    if err := t.reporter.Report(span); err != nil {
        log.Printf("Failed to report span: %v", err)
    }
}

// 添加标签
func (span *Span) AddTag(key, value string) {
    span.Tags[key] = value
}

// 添加日志
func (span *Span) AddLog(message string, fields map[string]interface{}) {
    span.Logs = append(span.Logs, LogEntry{
        Timestamp: time.Now(),
        Message:   message,
        Fields:    fields,
    })
}

// 追踪中间件
func CustomTracingMiddleware(tracer *CustomTracer) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 从请求头获取追踪ID
        traceID := c.GetHeader("X-Trace-ID")
        parentSpanID := c.GetHeader("X-Parent-Span-ID")

        var parentSpan *Span
        if traceID != "" && parentSpanID != "" {
            parentSpan = &Span{
                TraceID: traceID,
                SpanID:  parentSpanID,
            }
        }

        // 开始新的跨度
        span := tracer.StartSpan(fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path), parentSpan)

        // 设置追踪上下文到响应头
        c.Header("X-Trace-ID", span.TraceID)
        c.Header("X-Span-ID", span.SpanID)

        // 添加标签
        span.AddTag("http.method", c.Request.Method)
        span.AddTag("http.url", c.Request.URL.String())
        span.AddTag("http.host", c.Request.Host)
        span.AddTag("component", "gin")

        c.Next()

        // 添加响应状态码标签
        span.AddTag("http.status_code", fmt.Sprintf("%d", c.Writer.Status()))

        // 完成跨度
        tracer.FinishSpan(span)
    }
}
```

### 上下文传播
```go
// 追踪上下文
type TraceContext struct {
    TraceID    string
    SpanID     string
    ParentID   string
    Sampling   bool
    Baggage    map[string]string
}

// 上下文管理器
type ContextManager struct {
    tracer *CustomTracer
}

// 创建上下文管理器
func NewContextManager(tracer *CustomTracer) *ContextManager {
    return &ContextManager{
        tracer: tracer,
    }
}

// 从HTTP请求提取上下文
func (m *ContextManager) ExtractFromRequest(req *http.Request) *TraceContext {
    ctx := &TraceContext{
        TraceID: req.Header.Get("X-Trace-ID"),
        SpanID:  req.Header.Get("X-Span-ID"),
        ParentID: req.Header.Get("X-Parent-Span-ID"),
        Baggage:  make(map[string]string),
    }

    // 解析采样标志
    if sampling := req.Header.Get("X-Sampling"); sampling != "" {
        ctx.Sampling = sampling == "1"
    }

    // 解析额外数据
    for key, values := range req.Header {
        if strings.HasPrefix(key, "X-Baggage-") {
            baggageKey := strings.TrimPrefix(key, "X-Baggage-")
            if len(values) > 0 {
                ctx.Baggage[baggageKey] = values[0]
            }
        }
    }

    return ctx
}

// 注入上下文到HTTP请求
func (m *ContextManager) InjectToRequest(ctx *TraceContext, req *http.Request) {
    if ctx == nil {
        return
    }

    req.Header.Set("X-Trace-ID", ctx.TraceID)
    req.Header.Set("X-Span-ID", ctx.SpanID)
    req.Header.Set("X-Parent-Span-ID", ctx.ParentID)

    if ctx.Sampling {
        req.Header.Set("X-Sampling", "1")
    }

    // 注入额外数据
    for key, value := range ctx.Baggage {
        req.Header.Set(fmt.Sprintf("X-Baggage-%s", key), value)
    }
}

// 创建当前上下文
func (m *ContextManager) CreateContext() *TraceContext {
    return &TraceContext{
        TraceID:  generateTraceID(),
        SpanID:   generateSpanID(),
        Sampling: true,
        Baggage:  make(map[string]string),
    }
}

// 创建子上下文
func (m *ContextManager) CreateChildContext(parent *TraceContext) *TraceContext {
    if parent == nil {
        return m.CreateContext()
    }

    return &TraceContext{
        TraceID:  parent.TraceID,
        ParentID: parent.SpanID,
        SpanID:   generateSpanID(),
        Sampling: parent.Sampling,
        Baggage:  make(map[string]string),
    }
}
```

## 性能监控

### 内存监控
```go
// 内存监控器
type MemoryMonitor struct {
    interval    time.Duration
    stopChan    chan struct{}
    metrics     *MemoryMetrics
    reporters   []MemoryReporter
}

// 内存指标
type MemoryMetrics struct {
    alloc       prometheus.Gauge
    totalAlloc  prometheus.Counter
    sys         prometheus.Gauge
    numGC       prometheus.Counter
    pauseTotal  prometheus.Gauge
    heapAlloc   prometheus.Gauge
    heapSys     prometheus.Gauge
    heapIdle    prometheus.Gauge
    heapInuse   prometheus.Gauge
    heapReleased prometheus.Gauge
    stackInuse  prometheus.Gauge
    stackSys    prometheus.Gauge
}

// 内存报告器
type MemoryReporter interface {
    Report(metrics *runtime.MemStats) error
}

// 创建内存监控器
func NewMemoryMonitor(interval time.Duration) *MemoryMonitor {
    metrics := &MemoryMetrics{
        alloc: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_alloc_bytes",
            Help: "Current memory allocation",
        }),
        totalAlloc: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "memory_total_alloc_bytes_total",
            Help: "Total memory allocated",
        }),
        sys: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_sys_bytes",
            Help: "Total memory obtained from system",
        }),
        numGC: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "memory_gc_cycles_total",
            Help: "Number of GC cycles",
        }),
        pauseTotal: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_gc_pause_total_seconds",
            Help: "Total GC pause time",
        }),
        heapAlloc: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_heap_alloc_bytes",
            Help: "Heap allocated bytes",
        }),
        heapSys: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_heap_sys_bytes",
            Help: "Heap system bytes",
        }),
        heapIdle: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_heap_idle_bytes",
            Help: "Heap idle bytes",
        }),
        heapInuse: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_heap_inuse_bytes",
            Help: "Heap inuse bytes",
        }),
        heapReleased: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_heap_released_bytes",
            Help: "Heap released bytes",
        }),
        stackInuse: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_stack_inuse_bytes",
            Help: "Stack inuse bytes",
        }),
        stackSys: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "memory_stack_sys_bytes",
            Help: "Stack system bytes",
        }),
    }

    // 注册指标
    prometheus.MustRegister(metrics.alloc)
    prometheus.MustRegister(metrics.totalAlloc)
    prometheus.MustRegister(metrics.sys)
    prometheus.MustRegister(metrics.numGC)
    prometheus.MustRegister(metrics.pauseTotal)
    prometheus.MustRegister(metrics.heapAlloc)
    prometheus.MustRegister(metrics.heapSys)
    prometheus.MustRegister(metrics.heapIdle)
    prometheus.MustRegister(metrics.heapInuse)
    prometheus.MustRegister(metrics.heapReleased)
    prometheus.MustRegister(metrics.stackInuse)
    prometheus.MustRegister(metrics.stackSys)

    return &MemoryMonitor{
        interval: interval,
        stopChan: make(chan struct{}),
        metrics:  metrics,
        reporters: make([]MemoryReporter, 0),
    }
}

// 启动监控
func (m *MemoryMonitor) Start() {
    ticker := time.NewTicker(m.interval)
    defer ticker.Stop()

    var memStats runtime.MemStats

    for {
        select {
        case <-ticker.C:
            runtime.ReadMemStats(&memStats)
            m.updateMetrics(&memStats)
            m.reportMetrics(&memStats)
        case <-m.stopChan:
            return
        }
    }
}

// 停止监控
func (m *MemoryMonitor) Stop() {
    close(m.stopChan)
}

// 更新指标
func (m *MemoryMonitor) updateMetrics(memStats *runtime.MemStats) {
    m.metrics.alloc.Set(float64(memStats.Alloc))
    m.metrics.totalAlloc.Add(float64(memStats.TotalAlloc - memStats.TotalAlloc))
    m.metrics.sys.Set(float64(memStats.Sys))
    m.metrics.numGC.Add(float64(memStats.NumGC))
    m.metrics.pauseTotal.Set(float64(memStats.PauseTotalNs) / 1e9)
    m.metrics.heapAlloc.Set(float64(memStats.HeapAlloc))
    m.metrics.heapSys.Set(float64(memStats.HeapSys))
    m.metrics.heapIdle.Set(float64(memStats.HeapIdle))
    m.metrics.heapInuse.Set(float64(memStats.HeapInuse))
    m.metrics.heapReleased.Set(float64(memStats.HeapReleased))
    m.metrics.stackInuse.Set(float64(memStats.StackInuse))
    m.metrics.stackSys.Set(float64(memStats.StackSys))
}

// 报告指标
func (m *MemoryMonitor) reportMetrics(memStats *runtime.MemStats) {
    for _, reporter := range m.reporters {
        if err := reporter.Report(memStats); err != nil {
            log.Printf("Memory reporter error: %v", err)
        }
    }
}

// 添加报告器
func (m *MemoryMonitor) AddReporter(reporter MemoryReporter) {
    m.reporters = append(m.reporters, reporter)
}
```

### CPU监控
```go
// CPU监控器
type CPUMonitor struct {
    interval    time.Duration
    stopChan    chan struct{}
    metrics     *CPUMetrics
    reporters   []CPUReporter
    lastCPUTime time.Time
    lastCPUStat *cpu.Stat
}

// CPU指标
type CPUMetrics struct {
    usage       prometheus.Gauge
    userTime    prometheus.Counter
    systemTime  prometheus.Counter
    idleTime    prometheus.Counter
    iowaitTime  prometheus.Counter
    irqTime     prometheus.Counter
    softirqTime prometheus.Counter
    stealTime   prometheus.Counter
    guestTime   prometheus.Counter
    niceTime    prometheus.Counter
}

// CPU报告器
type CPUReporter interface {
    Report(stats *cpu.Stat) error
}

// 创建CPU监控器
func NewCPUMonitor(interval time.Duration) *CPUMonitor {
    metrics := &CPUMetrics{
        usage: prometheus.NewGauge(prometheus.GaugeOpts{
            Name: "cpu_usage_percent",
            Help: "CPU usage percentage",
        }),
        userTime: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "cpu_user_time_seconds_total",
            Help: "CPU user time",
        }),
        systemTime: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "cpu_system_time_seconds_total",
            Help: "CPU system time",
        }),
        idleTime: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "cpu_idle_time_seconds_total",
            Help: "CPU idle time",
        }),
        iowaitTime: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "cpu_iowait_time_seconds_total",
            Help: "CPU iowait time",
        }),
        irqTime: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "cpu_irq_time_seconds_total",
            Help: "CPU irq time",
        }),
        softirqTime: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "cpu_softirq_time_seconds_total",
            Help: "CPU softirq time",
        }),
        stealTime: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "cpu_steal_time_seconds_total",
            Help: "CPU steal time",
        }),
        guestTime: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "cpu_guest_time_seconds_total",
            Help: "CPU guest time",
        }),
        niceTime: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "cpu_nice_time_seconds_total",
            Help: "CPU nice time",
        }),
    }

    // 注册指标
    prometheus.MustRegister(metrics.usage)
    prometheus.MustRegister(metrics.userTime)
    prometheus.MustRegister(metrics.systemTime)
    prometheus.MustRegister(metrics.idleTime)
    prometheus.MustRegister(metrics.iowaitTime)
    prometheus.MustRegister(metrics.irqTime)
    prometheus.MustRegister(metrics.softirqTime)
    prometheus.MustRegister(metrics.stealTime)
    prometheus.MustRegister(metrics.guestTime)
    prometheus.MustRegister(metrics.niceTime)

    return &CPUMonitor{
        interval:   interval,
        stopChan:   make(chan struct{}),
        metrics:    metrics,
        reporters:  make([]CPUReporter, 0),
    }
}

// 启动监控
func (m *CPUMonitor) Start() {
    ticker := time.NewTicker(m.interval)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            now := time.Now()
            stats, err := cpu.Stat()
            if err != nil {
                log.Printf("Failed to get CPU stats: %v", err)
                continue
            }

            m.updateMetrics(stats, now)
            m.reportMetrics(stats)

            m.lastCPUTime = now
            m.lastCPUStat = stats
        case <-m.stopChan:
            return
        }
    }
}

// 停止监控
func (m *CPUMonitor) Stop() {
    close(m.stopChan)
}

// 更新指标
func (m *CPUMonitor) updateMetrics(stats *cpu.Stat, now time.Time) {
    if m.lastCPUStat == nil {
        m.lastCPUStat = stats
        m.lastCPUTime = now
        return
    }

    // 计算CPU使用率
    timeDiff := now.Sub(m.lastCPUTime).Seconds()
    if timeDiff > 0 {
        totalDiff := stats.Total - m.lastCPUStat.Total
        idleDiff := stats.Idle - m.lastCPUStat.Idle
        usage := (1.0 - float64(idleDiff)/float64(totalDiff)) * 100.0
        m.metrics.usage.Set(usage)
    }

    // 更新各项指标
    m.metrics.userTime.Set(float64(stats.User))
    m.metrics.systemTime.Set(float64(stats.System))
    m.metrics.idleTime.Set(float64(stats.Idle))
    m.metrics.iowaitTime.Set(float64(stats.Iowait))
    m.metrics.irqTime.Set(float64(stats.Irq))
    m.metrics.softirqTime.Set(float64(stats.Softirq))
    m.metrics.stealTime.Set(float64(stats.Steal))
    m.metrics.guestTime.Set(float64(stats.Guest))
    m.metrics.niceTime.Set(float64(stats.Nice))
}

// 报告指标
func (m *CPUMonitor) reportMetrics(stats *cpu.Stat) {
    for _, reporter := range m.reporters {
        if err := reporter.Report(stats); err != nil {
            log.Printf("CPU reporter error: %v", err)
        }
    }
}

// 添加报告器
func (m *CPUMonitor) AddReporter(reporter CPUReporter) {
    m.reporters = append(m.reporters, reporter)
}
```

### 网络监控
```go
// 网络监控器
type NetworkMonitor struct {
    interval    time.Duration
    stopChan    chan struct{}
    metrics     *NetworkMetrics
    reporters   []NetworkReporter
    lastStats   map[string]*net.IOCountersStat
}

// 网络指标
type NetworkMetrics struct {
    bytesSent      prometheus.CounterVec
    bytesRecv      prometheus.CounterVec
    packetsSent    prometheus.CounterVec
    packetsRecv    prometheus.CounterVec
    errIn          prometheus.CounterVec
    errOut         prometheus.CounterVec
    dropIn         prometheus.CounterVec
    dropOut        prometheus.CounterVec
}

// 网络报告器
type NetworkReporter interface {
    Report(stats map[string]*net.IOCountersStat) error
}

// 创建网络监控器
func NewNetworkMonitor(interval time.Duration) *NetworkMonitor {
    metrics := &NetworkMetrics{
        bytesSent: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "network_bytes_sent_total",
                Help: "Total bytes sent",
            },
            []string{"interface"},
        ),
        bytesRecv: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "network_bytes_recv_total",
                Help: "Total bytes received",
            },
            []string{"interface"},
        ),
        packetsSent: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "network_packets_sent_total",
                Help: "Total packets sent",
            },
            []string{"interface"},
        ),
        packetsRecv: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "network_packets_recv_total",
                Help: "Total packets received",
            },
            []string{"interface"},
        ),
        errIn: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "network_errors_in_total",
                Help: "Total input errors",
            },
            []string{"interface"},
        ),
        errOut: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "network_errors_out_total",
                Help: "Total output errors",
            },
            []string{"interface"},
        ),
        dropIn: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "network_drops_in_total",
                Help: "Total input drops",
            },
            []string{"interface"},
        ),
        dropOut: *prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "network_drops_out_total",
                Help: "Total output drops",
            },
            []string{"interface"},
        ),
    }

    // 注册指标
    prometheus.MustRegister(&metrics.bytesSent)
    prometheus.MustRegister(&metrics.bytesRecv)
    prometheus.MustRegister(&metrics.packetsSent)
    prometheus.MustRegister(&metrics.packetsRecv)
    prometheus.MustRegister(&metrics.errIn)
    prometheus.MustRegister(&metrics.errOut)
    prometheus.MustRegister(&metrics.dropIn)
    prometheus.MustRegister(&metrics.dropOut)

    return &NetworkMonitor{
        interval:   interval,
        stopChan:   make(chan struct{}),
        metrics:    metrics,
        reporters:  make([]NetworkReporter, 0),
        lastStats:  make(map[string]*net.IOCountersStat),
    }
}

// 启动监控
func (m *NetworkMonitor) Start() {
    ticker := time.NewTicker(m.interval)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            stats, err := net.IOCounters(true)
            if err != nil {
                log.Printf("Failed to get network stats: %v", err)
                continue
            }

            m.updateMetrics(stats)
            m.reportMetrics(stats)
        case <-m.stopChan:
            return
        }
    }
}

// 停止监控
func (m *NetworkMonitor) Stop() {
    close(m.stopChan)
}

// 更新指标
func (m *NetworkMonitor) updateMetrics(stats []net.IOCountersStat) {
    for _, stat := range stats {
        m.metrics.bytesSent.WithLabelValues(stat.Name).Add(float64(stat.BytesSent))
        m.metrics.bytesRecv.WithLabelValues(stat.Name).Add(float64(stat.BytesRecv))
        m.metrics.packetsSent.WithLabelValues(stat.Name).Add(float64(stat.PacketsSent))
        m.metrics.packetsRecv.WithLabelValues(stat.Name).Add(float64(stat.PacketsRecv))
        m.metrics.errIn.WithLabelValues(stat.Name).Add(float64(stat.Errin))
        m.metrics.errOut.WithLabelValues(stat.Name).Add(float64(stat.Errout))
        m.metrics.dropIn.WithLabelValues(stat.Name).Add(float64(stat.Dropin))
        m.metrics.dropOut.WithLabelValues(stat.Name).Add(float64(stat.Dropout))
    }
}

// 报告指标
func (m *NetworkMonitor) reportMetrics(stats []net.IOCountersStat) {
    statsMap := make(map[string]*net.IOCountersStat)
    for i := range stats {
        statsMap[stats[i].Name] = &stats[i]
    }

    for _, reporter := range m.reporters {
        if err := reporter.Report(statsMap); err != nil {
            log.Printf("Network reporter error: %v", err)
        }
    }
}

// 添加报告器
func (m *NetworkMonitor) AddReporter(reporter NetworkReporter) {
    m.reporters = append(m.reporters, reporter)
}
```

## 告警机制

### 告警规则
```go
// 告警规则
type AlertRule struct {
    ID          string            `json:"id"`
    Name        string            `json:"name"`
    Description string            `json:"description"`
    Condition   AlertCondition   `json:"condition"`
    Threshold   float64           `json:"threshold"`
    Duration    time.Duration     `json:"duration"`
    Severity    AlertSeverity     `json:"severity"`
    Labels      map[string]string `json:"labels"`
    Annotations map[string]string `json:"annotations"`
    Enabled     bool              `json:"enabled"`
}

// 告警条件
type AlertCondition struct {
    Metric    string `json:"metric"`
    Operator string `json:"operator"`  // >, <, >=, <=, ==, !=
    Aggregation string `json:"aggregation"` // avg, sum, max, min, count
}

// 告警严重程度
type AlertSeverity int

const (
    SeverityInfo AlertSeverity = iota
    SeverityWarning
    SeverityError
    SeverityCritical
)

// 告警评估器
type AlertEvaluator struct {
    rules      []*AlertRule
    metrics    MetricsProvider
    notifiers  []AlertNotifier
    activeAlerts map[string]*Alert
}

// 指标提供者
type MetricsProvider interface {
    GetMetric(metric string, labels map[string]string) (float64, error)
}

// 告警通知器
type AlertNotifier interface {
    Notify(alert *Alert) error
}

// 创建告警评估器
func NewAlertEvaluator(metrics MetricsProvider) *AlertEvaluator {
    return &AlertEvaluator{
        rules:        make([]*AlertRule, 0),
        metrics:      metrics,
        notifiers:    make([]AlertNotifier, 0),
        activeAlerts: make(map[string]*Alert),
    }
}

// 添加规则
func (e *AlertEvaluator) AddRule(rule *AlertRule) {
    e.rules = append(e.rules, rule)
}

// 添加通知器
func (e *AlertEvaluator) AddNotifier(notifier AlertNotifier) {
    e.notifiers = append(e.notifiers, notifier)
}

// 评估规则
func (e *AlertEvaluator) Evaluate() {
    for _, rule := range e.rules {
        if !rule.Enabled {
            continue
        }

        value, err := e.metrics.GetMetric(rule.Condition.Metric, rule.Labels)
        if err != nil {
            log.Printf("Failed to get metric %s: %v", rule.Condition.Metric, err)
            continue
        }

        triggered := e.evaluateCondition(value, rule)

        if triggered {
            e.triggerAlert(rule, value)
        } else {
            e.resolveAlert(rule.ID)
        }
    }
}

// 评估条件
func (e *AlertEvaluator) evaluateCondition(value float64, rule *AlertRule) bool {
    switch rule.Condition.Operator {
    case ">":
        return value > rule.Threshold
    case "<":
        return value < rule.Threshold
    case ">=":
        return value >= rule.Threshold
    case "<=":
        return value <= rule.Threshold
    case "==":
        return value == rule.Threshold
    case "!=":
        return value != rule.Threshold
    default:
        return false
    }
}

// 触发告警
func (e *AlertEvaluator) triggerAlert(rule *AlertRule, value float64) {
    alertKey := rule.ID

    if alert, exists := e.activeAlerts[alertKey]; exists {
        // 更新现有告警
        alert.Value = value
        alert.LastActive = time.Now()
        return
    }

    // 创建新告警
    alert := &Alert{
        ID:          generateID(),
        RuleID:      rule.ID,
        Name:        rule.Name,
        Description: rule.Description,
        Value:       value,
        Threshold:   rule.Threshold,
        Severity:    rule.Severity,
        Labels:      rule.Labels,
        Annotations: rule.Annotations,
        StartsAt:    time.Now(),
        LastActive:  time.Now(),
        Status:      AlertStatusFiring,
    }

    e.activeAlerts[alertKey] = alert

    // 发送通知
    for _, notifier := range e.notifiers {
        if err := notifier.Notify(alert); err != nil {
            log.Printf("Failed to send alert notification: %v", err)
        }
    }
}

// 解决告警
func (e *AlertEvaluator) resolveAlert(ruleID string) {
    alertKey := ruleID

    if alert, exists := e.activeAlerts[alertKey]; exists {
        alert.Status = AlertStatusResolved
        alert.EndsAt = time.Now()

        // 发送解决通知
        for _, notifier := range e.notifiers {
            if err := notifier.Notify(alert); err != nil {
                log.Printf("Failed to send alert resolution notification: %v", err)
            }
        }

        delete(e.activeAlerts, alertKey)
    }
}
```

### 告警通知
```go
// 告警通知器
type AlertNotifier interface {
    Notify(alert *Alert) error
}

// 邮件通知器
type EmailNotifier struct {
    smtpHost     string
    smtpPort     int
    username     string
    password     string
    fromAddress  string
    toAddresses  []string
    tls          bool
}

// 创建邮件通知器
func NewEmailNotifier(smtpHost string, smtpPort int, username, password, from string, to []string, tls bool) *EmailNotifier {
    return &EmailNotifier{
        smtpHost:    smtpHost,
        smtpPort:    smtpPort,
        username:    username,
        password:    password,
        fromAddress: from,
        toAddresses: to,
        tls:         tls,
    }
}

// 发送邮件通知
func (n *EmailNotifier) Notify(alert *Alert) error {
    subject := fmt.Sprintf("[%s] %s", alert.Severity, alert.Name)
    body := n.formatEmailBody(alert)

    auth := smtp.PlainAuth("", n.username, n.password, n.smtpHost)
    addr := fmt.Sprintf("%s:%d", n.smtpHost, n.smtpPort)

    msg := n.formatMessage(subject, body)

    return smtp.SendMail(addr, auth, n.fromAddress, n.toAddresses, msg)
}

// 格式化邮件内容
func (n *EmailNotifier) formatEmailBody(alert *Alert) string {
    var body strings.Builder

    body.WriteString(fmt.Sprintf("Alert: %s\n\n", alert.Name))
    body.WriteString(fmt.Sprintf("Description: %s\n", alert.Description))
    body.WriteString(fmt.Sprintf("Severity: %s\n", alert.Severity))
    body.WriteString(fmt.Sprintf("Value: %.2f\n", alert.Value))
    body.WriteString(fmt.Sprintf("Threshold: %.2f\n", alert.Threshold))
    body.WriteString(fmt.Sprintf("Status: %s\n", alert.Status))
    body.WriteString(fmt.Sprintf("Starts At: %s\n", alert.StartsAt))

    if alert.Status == AlertStatusResolved {
        body.WriteString(fmt.Sprintf("Ends At: %s\n", alert.EndsAt))
    }

    return body.String()
}

// 格式化邮件消息
func (n *EmailNotifier) formatMessage(subject, body string) []byte {
    var msg strings.Builder

    msg.WriteString(fmt.Sprintf("From: %s\r\n", n.fromAddress))
    msg.WriteString(fmt.Sprintf("To: %s\r\n", strings.Join(n.toAddresses, ",")))
    msg.WriteString(fmt.Sprintf("Subject: %s\r\n", subject))
    msg.WriteString("MIME-Version: 1.0\r\n")
    msg.WriteString("Content-Type: text/plain; charset=utf-8\r\n")
    msg.WriteString("\r\n")
    msg.WriteString(body)

    return []byte(msg.String())
}

// Slack通知器
type SlackNotifier struct {
    webhookURL string
    channel    string
    username   string
}

// 创建Slack通知器
func NewSlackNotifier(webhookURL, channel, username string) *SlackNotifier {
    return &SlackNotifier{
        webhookURL: webhookURL,
        channel:    channel,
        username:   username,
    }
}

// 发送Slack通知
func (n *SlackNotifier) Notify(alert *Alert) error {
    message := n.formatSlackMessage(alert)

    payload, err := json.Marshal(message)
    if err != nil {
        return err
    }

    resp, err := http.Post(n.webhookURL, "application/json", bytes.NewBuffer(payload))
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("slack webhook returned status %d", resp.StatusCode)
    }

    return nil
}

// 格式化Slack消息
func (n *SlackNotifier) formatSlackMessage(alert *Alert) map[string]interface{} {
    color := "#36a64f" // 绿色
    if alert.Status == AlertStatusFiring {
        switch alert.Severity {
        case SeverityCritical:
            color = "#ff0000" // 红色
        case SeverityError:
            color = "#ff9900" // 橙色
        case SeverityWarning:
            color = "#ffcc00" // 黄色
        }
    }

    return map[string]interface{}{
        "channel":   n.channel,
        "username":  n.username,
        "text":      alert.Name,
        "attachments": []map[string]interface{}{
            {
                "color":     color,
                "title":     alert.Name,
                "text":      alert.Description,
                "fields": []map[string]interface{}{
                    {
                        "title": "Severity",
                        "value": alert.Severity,
                        "short": true,
                    },
                    {
                        "title": "Value",
                        "value": fmt.Sprintf("%.2f", alert.Value),
                        "short": true,
                    },
                    {
                        "title": "Threshold",
                        "value": fmt.Sprintf("%.2f", alert.Threshold),
                        "short": true,
                    },
                    {
                        "title": "Status",
                        "value": alert.Status,
                        "short": true,
                    },
                },
                "timestamp": alert.StartsAt.Unix(),
            },
        },
    }
}
```

### 告警聚合
```go
// 告警聚合器
type AlertAggregator struct {
    groups      map[string]*AlertGroup
    rules       []*AlertRule
    aggregators []AlertAggregatorFunc
}

// 告警组
type AlertGroup struct {
    Key        string            `json:"key"`
    Alerts     []*Alert          `json:"alerts"`
    Labels     map[string]string `json:"labels"`
    CreatedAt  time.Time         `json:"created_at"`
    UpdatedAt  time.Time         `json:"updated_at"`
}

// 告警聚合函数
type AlertAggregatorFunc func(alerts []*Alert) *AlertGroup

// 创建告警聚合器
func NewAlertAggregator() *AlertAggregator {
    return &AlertAggregator{
        groups:      make(map[string]*AlertGroup),
        aggregators: make([]AlertAggregatorFunc, 0),
    }
}

// 添加聚合函数
func (a *AlertAggregator) AddAggregator(aggregator AlertAggregatorFunc) {
    a.aggregators = append(a.aggregators, aggregator)
}

// 聚合告警
func (a *AlertAggregator) Aggregate(alerts []*Alert) []*AlertGroup {
    groups := make([]*AlertGroup, 0)

    for _, aggregator := range a.aggregators {
        group := aggregator(alerts)
        if group != nil {
            groups = append(groups, group)
        }
    }

    return groups
}

// 按标签聚合
func GroupByLabel(label string) AlertAggregatorFunc {
    return func(alerts []*Alert) *AlertGroup {
        groups := make(map[string][]*Alert)

        for _, alert := range alerts {
            if value, exists := alert.Labels[label]; exists {
                groups[value] = append(groups[value], alert)
            }
        }

        var result []*AlertGroup
        for key, groupAlerts := range groups {
            result = append(result, &AlertGroup{
                Key:       key,
                Alerts:    groupAlerts,
                Labels:    map[string]string{label: key},
                CreatedAt: time.Now(),
                UpdatedAt: time.Now(),
            })
        }

        return nil // 返回nil，因为这是聚合到组而不是单个组
    }
}

// 按严重程度聚合
func GroupBySeverity() AlertAggregatorFunc {
    return func(alerts []*Alert) *AlertGroup {
        groups := make(map[AlertSeverity][]*Alert)

        for _, alert := range alerts {
            groups[alert.Severity] = append(groups[alert.Severity], alert)
        }

        var result []*AlertGroup
        for severity, groupAlerts := range groups {
            result = append(result, &AlertGroup{
                Key:       severity.String(),
                Alerts:    groupAlerts,
                Labels:    map[string]string{"severity": severity.String()},
                CreatedAt: time.Now(),
                UpdatedAt: time.Now(),
            })
        }

        return nil
    }
}

// 按时间窗口聚合
func GroupByTimeWindow(window time.Duration) AlertAggregatorFunc {
    return func(alerts []*Alert) *AlertGroup {
        groups := make(map[int64][]*Alert)

        for _, alert := range alerts {
            windowStart := alert.StartsAt.Truncate(window)
            groups[windowStart.Unix()] = append(groups[windowStart.Unix()], alert)
        }

        var result []*AlertGroup
        for windowTime, groupAlerts := range groups {
            result = append(result, &AlertGroup{
                Key:       time.Unix(windowTime, 0).Format(time.RFC3339),
                Alerts:    groupAlerts,
                Labels:    map[string]string{"window": time.Unix(windowTime, 0).Format(time.RFC3339)},
                CreatedAt: time.Now(),
                UpdatedAt: time.Now(),
            })
        }

        return nil
    }
}
```

## 可视化监控

### Grafana集成
```go
// Grafana配置
type GrafanaConfig struct {
    URL       string `json:"url"`
    Token     string `json:"token"`
    Username  string `json:"username"`
    Password  string `json:"password"`
    Datasource string `json:"datasource"`
}

// Grafana客户端
type GrafanaClient struct {
    config    *GrafanaConfig
    client    *http.Client
}

// 创建Grafana客户端
func NewGrafanaClient(config *GrafanaConfig) *GrafanaClient {
    return &GrafanaClient{
        config: config,
        client: &http.Client{
            Timeout: 30 * time.Second,
        },
    }
}

// 创建仪表板
func (c *GrafanaClient) CreateDashboard(dashboard *GrafanaDashboard) error {
    payload := map[string]interface{}{
        "dashboard": dashboard,
        "overwrite": true,
    }

    data, err := json.Marshal(payload)
    if err != nil {
        return err
    }

    req, err := http.NewRequest("POST", c.config.URL+"/api/dashboards/db", bytes.NewBuffer(data))
    if err != nil {
        return err
    }

    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer "+c.config.Token)

    resp, err := c.client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("grafana returned status %d", resp.StatusCode)
    }

    return nil
}

// Grafana仪表板
type GrafanaDashboard struct {
    ID          int                    `json:"id,omitempty"`
    UID         string                 `json:"uid,omitempty"`
    Title       string                 `json:"title"`
    Description string                 `json:"description"`
    Tags        []string               `json:"tags"`
    Time        *DashboardTime         `json:"time"`
    Timezone    string                 `json:"timezone"`
    Panels      []Panel                `json:"panels"`
    Templating  *Templating            `json:"templating"`
    Annotations *Annotations           `json:"annotations"`
    Refresh     string                 `json:"refresh"`
    Version     int                    `json:"version"`
}

// 面板
type Panel struct {
    ID         int                    `json:"id"`
    Title      string                 `json:"title"`
    Type       string                 `json:"type"`
    GridPos    *GridPos               `json:"gridPos"`
    Targets    []Target               `json:"targets"`
    FieldConfig *FieldConfig           `json:"fieldConfig,omitempty"`
    Options    map[string]interface{} `json:"options,omitempty"`
}

// 目标
type Target struct {
    RefID      string                 `json:"refId"`
    Datasource string                 `json:"datasource"`
    Query      string                 `json:"query"`
    Format     string                 `json:"format"`
}

// 网格位置
type GridPos struct {
    H int `json:"h"`
    W int `json:"w"`
    X int `json:"x"`
    Y int `json:"y"`
}

// 创建应用监控仪表板
func CreateApplicationDashboard() *GrafanaDashboard {
    return &GrafanaDashboard{
        Title:       "Application Monitoring",
        Description: "Application Performance Monitoring Dashboard",
        Tags:        []string{"application", "monitoring"},
        Time: &DashboardTime{
            From: "now-1h",
            To:   "now",
        },
        Timezone: "browser",
        Refresh:  "10s",
        Panels: []Panel{
            {
                ID:    1,
                Title: "HTTP Requests",
                Type:  "graph",
                GridPos: &GridPos{H: 8, W: 12, X: 0, Y: 0},
                Targets: []Target{
                    {
                        RefID:      "A",
                        Datasource: "prometheus",
                        Query:      "rate(http_requests_total[5m])",
                        Format:     "time_series",
                    },
                },
            },
            {
                ID:    2,
                Title: "Response Time",
                Type:  "graph",
                GridPos: &GridPos{H: 8, W: 12, X: 12, Y: 0},
                Targets: []Target{
                    {
                        RefID:      "A",
                        Datasource: "prometheus",
                        Query:      "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                        Format:     "time_series",
                    },
                },
            },
            {
                ID:    3,
                Title: "Error Rate",
                Type:  "graph",
                GridPos: &GridPos{H: 8, W: 12, X: 0, Y: 8},
                Targets: []Target{
                    {
                        RefID:      "A",
                        Datasource: "prometheus",
                        Query:      "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])",
                        Format:     "time_series",
                    },
                },
            },
            {
                ID:    4,
                Title: "Active Connections",
                Type:  "graph",
                GridPos: &GridPos{H: 8, W: 12, X: 12, Y: 8},
                Targets: []Target{
                    {
                        RefID:      "A",
                        Datasource: "prometheus",
                        Query:      "http_active_connections",
                        Format:     "time_series",
                    },
                },
            },
        },
    }
}
```

### 自定义监控面板
```go
// 监控面板生成器
type DashboardGenerator struct {
    grafanaClient *GrafanaClient
    templates     map[string]*DashboardTemplate
}

// 仪表板模板
type DashboardTemplate struct {
    Name         string                 `json:"name"`
    Description  string                 `json:"description"`
    Variables    []TemplateVariable     `json:"variables"`
    Panels       []PanelTemplate        `json:"panels"`
}

// 模板变量
type TemplateVariable struct {
    Name        string `json:"name"`
    Type        string `json:"type"`
    Label       string `json:"label"`
    Query       string `json:"query"`
    Current     string `json:"current"`
    Options     []VariableOption `json:"options"`
}

// 变量选项
type VariableOption struct {
    Text  string `json:"text"`
    Value string `json:"value"`
}

// 面板模板
type PanelTemplate struct {
    Title       string                 `json:"title"`
    Type        string                 `json:"type"`
    Description string                 `json:"description"`
    Targets     []TargetTemplate       `json:"targets"`
    Options     map[string]interface{} `json:"options"`
}

// 目标模板
type TargetTemplate struct {
    RefID      string `json:"refId"`
    Query      string `json:"query"`
    Format     string `json:"format"`
    Legend     string `json:"legend"`
}

// 创建仪表板生成器
func NewDashboardGenerator(grafanaClient *GrafanaClient) *DashboardGenerator {
    return &DashboardGenerator{
        grafanaClient: grafanaClient,
        templates:     make(map[string]*DashboardTemplate),
    }
}

// 添加模板
func (g *DashboardGenerator) AddTemplate(template *DashboardTemplate) {
    g.templates[template.Name] = template
}

// 生成仪表板
func (g *DashboardGenerator) GenerateDashboard(templateName string, variables map[string]string) (*GrafanaDashboard, error) {
    template, exists := g.templates[templateName]
    if !exists {
        return nil, fmt.Errorf("template %s not found", templateName)
    }

    dashboard := &GrafanaDashboard{
        Title:       template.Name,
        Description: template.Description,
        Time: &DashboardTime{
            From: "now-1h",
            To:   "now",
        },
        Timezone: "browser",
        Refresh:  "10s",
        Panels:   make([]Panel, len(template.Panels)),
    }

    // 生成面板
    for i, panelTemplate := range template.Panels {
        panel := Panel{
            ID:    i + 1,
            Title: panelTemplate.Title,
            Type:  panelTemplate.Type,
            GridPos: &GridPos{
                H: 8,
                W: 12,
                X: (i % 2) * 12,
                Y: (i / 2) * 8,
            },
            Targets: make([]Target, len(panelTemplate.Targets)),
            Options: panelTemplate.Options,
        }

        // 生成目标
        for j, targetTemplate := range panelTemplate.Targets {
            query := targetTemplate.Query
            for key, value := range variables {
                query = strings.ReplaceAll(query, fmt.Sprintf("$%s", key), value)
            }

            panel.Targets[j] = Target{
                RefID:      string(rune('A' + j)),
                Datasource: "prometheus",
                Query:      query,
                Format:     targetTemplate.Format,
            }
        }

        dashboard.Panels[i] = panel
    }

    return dashboard, nil
}

// 创建应用性能监控模板
func CreateAPMTemplate() *DashboardTemplate {
    return &DashboardTemplate{
        Name:        "Application Performance",
        Description: "Application Performance Monitoring Dashboard",
        Variables: []TemplateVariable{
            {
                Name:  "service",
                Type:  "query",
                Label: "Service",
                Query: "label_values(http_requests_total, service)",
            },
            {
                Name:  "environment",
                Type:  "custom",
                Label: "Environment",
                Options: []VariableOption{
                    {Text: "Production", Value: "production"},
                    {Text: "Staging", Value: "staging"},
                    {Text: "Development", Value: "development"},
                },
                Current: "production",
            },
        },
        Panels: []PanelTemplate{
            {
                Title:       "Request Rate",
                Type:        "graph",
                Description: "HTTP request rate by status code",
                Targets: []TargetTemplate{
                    {
                        RefID:  "A",
                        Query:  "rate(http_requests_total{service=\"$service\", environment=\"$environment\"}[5m])",
                        Format: "time_series",
                        Legend: "{{status}}",
                    },
                },
            },
            {
                Title:       "Response Time",
                Type:        "graph",
                Description: "HTTP response time percentiles",
                Targets: []TargetTemplate{
                    {
                        RefID:  "A",
                        Query:  "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{service=\"$service\", environment=\"$environment\"}[5m]))",
                        Format: "time_series",
                        Legend: "p50",
                    },
                    {
                        RefID:  "B",
                        Query:  "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service=\"$service\", environment=\"$environment\"}[5m]))",
                        Format: "time_series",
                        Legend: "p95",
                    },
                    {
                        RefID:  "C",
                        Query:  "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{service=\"$service\", environment=\"$environment\"}[5m]))",
                        Format: "time_series",
                        Legend: "p99",
                    },
                },
            },
            {
                Title:       "Error Rate",
                Type:        "graph",
                Description: "HTTP error rate",
                Targets: []TargetTemplate{
                    {
                        RefID:  "A",
                        Query:  "rate(http_requests_total{service=\"$service\", environment=\"$environment\", status=~\"5..\"}[5m]) / rate(http_requests_total{service=\"$service\", environment=\"$environment\"}[5m])",
                        Format: "time_series",
                        Legend: "error rate",
                    },
                },
            },
        },
    }
}
```

## 监控最佳实践

### 监控策略
```go
// 监控策略配置
type MonitoringStrategy struct {
    // 采样率
    SampleRate float64 `json:"sample_rate"`

    // 指标收集间隔
    MetricInterval time.Duration `json:"metric_interval"`

    // 告警级别
    AlertLevels map[string]AlertLevel `json:"alert_levels"`

    // 性能基线
    PerformanceBaselines map[string]PerformanceBaseline `json:"performance_baselines"`

    // 自适应阈值
    AdaptiveThresholds map[string]AdaptiveThreshold `json:"adaptive_thresholds"`
}

// 告警级别
type AlertLevel struct {
    Name        string  `json:"name"`
    Threshold   float64 `json:"threshold"`
    Duration    time.Duration `json:"duration"`
    Severity    AlertSeverity `json:"severity"`
    Actions     []string `json:"actions"`
}

// 性能基线
type PerformanceBaseline struct {
    Metric      string  `json:"metric"`
    Baseline    float64 `json:"baseline"`
    Deviation   float64 `json:"deviation"`
    Period      time.Duration `json:"period"`
}

// 自适应阈值
type AdaptiveThreshold struct {
    Metric      string  `json:"metric"`
    Algorithm   string  `json:"algorithm"`
    Parameters  map[string]interface{} `json:"parameters"`
    WindowSize  time.Duration `json:"window_size"`
}

// 创建监控策略
func CreateMonitoringStrategy() *MonitoringStrategy {
    return &MonitoringStrategy{
        SampleRate:      1.0,
        MetricInterval:  15 * time.Second,
        AlertLevels: map[string]AlertLevel{
            "error_rate": {
                Name:      "Error Rate",
                Threshold: 0.01,
                Duration:  5 * time.Minute,
                Severity:  SeverityWarning,
                Actions:   []string{"email", "slack"},
            },
            "response_time": {
                Name:      "Response Time",
                Threshold: 1.0,
                Duration:  2 * time.Minute,
                Severity:  SeverityError,
                Actions:   []string{"email", "slack", "pagerduty"},
            },
            "availability": {
                Name:      "Availability",
                Threshold: 0.99,
                Duration:  5 * time.Minute,
                Severity:  SeverityCritical,
                Actions:   []string{"pagerduty", "phone"},
            },
        },
        PerformanceBaselines: map[string]PerformanceBaseline{
            "response_time_p50": {
                Metric:     "response_time_p50",
                Baseline:   0.1,
                Deviation:  0.05,
                Period:     time.Hour,
            },
            "error_rate": {
                Metric:     "error_rate",
                Baseline:   0.001,
                Deviation:  0.002,
                Period:     time.Hour,
            },
        },
        AdaptiveThresholds: map[string]AdaptiveThreshold{
            "response_time": {
                Metric:     "response_time",
                Algorithm:  "ewma",
                Parameters: map[string]interface{}{
                    "alpha": 0.3,
                    "beta":  2.0,
                },
                WindowSize: time.Hour,
            },
        },
    }
}
```

### 监控性能优化
```go
// 监控性能优化器
type MonitoringOptimizer struct {
    strategy   *MonitoringStrategy
    metrics    MetricsProvider
    notifiers  []AlertNotifier
    adaptive   map[string]*AdaptiveMonitor
}

// 自适应监控器
type AdaptiveMonitor struct {
    metric      string
    algorithm   string
    parameters  map[string]interface{}
    history     []float64
    threshold   float64
    lastUpdate  time.Time
}

// 创建监控优化器
func NewMonitoringOptimizer(strategy *MonitoringStrategy, metrics MetricsProvider) *MonitoringOptimizer {
    return &MonitoringOptimizer{
        strategy:  strategy,
        metrics:   metrics,
        notifiers: make([]AlertNotifier, 0),
        adaptive:  make(map[string]*AdaptiveMonitor),
    }
}

// 初始化自适应监控
func (o *MonitoringOptimizer) InitializeAdaptiveMonitors() {
    for name, config := range o.strategy.AdaptiveThresholds {
        monitor := &AdaptiveMonitor{
            metric:     name,
            algorithm:  config.Algorithm,
            parameters: config.Parameters,
            history:    make([]float64, 0),
            threshold:  0,
            lastUpdate: time.Now(),
        }
        o.adaptive[name] = monitor
    }
}

// 更新自适应阈值
func (o *MonitoringOptimizer) UpdateAdaptiveThresholds() {
    for name, monitor := range o.adaptive {
        value, err := o.metrics.GetMetric(name, nil)
        if err != nil {
            continue
        }

        // 添加到历史记录
        monitor.history = append(monitor.history, value)

        // 保持历史记录大小
        maxSize := int(monitor.parameters["max_size"].(float64))
        if len(monitor.history) > maxSize {
            monitor.history = monitor.history[len(monitor.history)-maxSize:]
        }

        // 更新阈值
        switch monitor.algorithm {
        case "ewma":
            o.updateEWMA(monitor)
        case "stddev":
            o.updateStdDev(monitor)
        case "percentile":
            o.updatePercentile(monitor)
        }

        monitor.lastUpdate = time.Now()
    }
}

// 更新EWMA阈值
func (o *MonitoringOptimizer) updateEWMA(monitor *AdaptiveMonitor) {
    if len(monitor.history) < 2 {
        return
    }

    alpha := monitor.parameters["alpha"].(float64)
    beta := monitor.parameters["beta"].(float64)

    // 计算EWMA
    ewma := monitor.history[0]
    for _, value := range monitor.history[1:] {
        ewma = alpha*value + (1-alpha)*ewma
    }

    // 设置阈值
    monitor.threshold = ewma * beta
}

// 更新标准差阈值
func (o *MonitoringOptimizer) updateStdDev(monitor *AdaptiveMonitor) {
    if len(monitor.history) < 2 {
        return
    }

    // 计算平均值
    sum := 0.0
    for _, value := range monitor.history {
        sum += value
    }
    mean := sum / float64(len(monitor.history))

    // 计算标准差
    variance := 0.0
    for _, value := range monitor.history {
        variance += math.Pow(value-mean, 2)
    }
    stdDev := math.Sqrt(variance / float64(len(monitor.history)))

    // 设置阈值
    multiplier := monitor.parameters["multiplier"].(float64)
    monitor.threshold = mean + multiplier*stdDev
}

// 更新百分位阈值
func (o *MonitoringOptimizer) updatePercentile(monitor *AdaptiveMonitor) {
    if len(monitor.history) < 10 {
        return
    }

    // 排序历史值
    sorted := make([]float64, len(monitor.history))
    copy(sorted, monitor.history)
    sort.Float64s(sorted)

    // 计算百分位
    percentile := monitor.parameters["percentile"].(float64)
    index := int(float64(len(sorted)) * percentile / 100.0)
    if index >= len(sorted) {
        index = len(sorted) - 1
    }

    monitor.threshold = sorted[index]
}
```

### 监控数据管理
```go
// 监控数据管理器
type MonitoringDataManager struct {
    storage    MonitoringStorage
    retention  time.Duration
    compression CompressionStrategy
}

// 监控存储
type MonitoringStorage interface {
    Store(metrics *MetricBatch) error
    Retrieve(query *MetricQuery) (*MetricBatch, error)
    Delete(query *MetricQuery) error
}

// 压缩策略
type CompressionStrategy interface {
    Compress(batch *MetricBatch) (*MetricBatch, error)
    Decompress(batch *MetricBatch) (*MetricBatch, error)
}

// 指标批次
type MetricBatch struct {
    Timestamp time.Time    `json:"timestamp"`
    Metrics   []Metric     `json:"metrics"`
    Labels    Labels       `json:"labels"`
}

// 指标
type Metric struct {
    Name   string  `json:"name"`
    Value  float64 `json:"value"`
    Type   MetricType `json:"type"`
}

// 指标类型
type MetricType string

const (
    MetricTypeGauge     MetricType = "gauge"
    MetricTypeCounter   MetricType = "counter"
    MetricTypeHistogram MetricType = "histogram"
    MetricTypeSummary   MetricType = "summary"
)

// 指标查询
type MetricQuery struct {
    Name      string            `json:"name"`
    Labels    Labels            `json:"labels,omitempty"`
    StartTime time.Time         `json:"start_time,omitempty"`
    EndTime   time.Time         `json:"end_time,omitempty"`
    Aggregation string          `json:"aggregation,omitempty"`
}

// 标签
type Labels map[string]string

// 创建监控数据管理器
func NewMonitoringDataManager(storage MonitoringStorage, retention time.Duration, compression CompressionStrategy) *MonitoringDataManager {
    return &MonitoringDataManager{
        storage:    storage,
        retention:  retention,
        compression: compression,
    }
}

// 存储指标
func (m *MonitoringDataManager) StoreMetrics(batch *MetricBatch) error {
    // 压缩数据
    compressed, err := m.compression.Compress(batch)
    if err != nil {
        return err
    }

    // 存储数据
    return m.storage.Store(compressed)
}

// 检索指标
func (m *MonitoringDataManager) RetrieveMetrics(query *MetricQuery) (*MetricBatch, error) {
    // 检索数据
    batch, err := m.storage.Retrieve(query)
    if err != nil {
        return nil, err
    }

    // 解压缩数据
    return m.compression.Decompress(batch)
}

// 清理过期数据
func (m *MonitoringDataManager) CleanupExpiredData() error {
    query := &MetricQuery{
        EndTime: time.Now().Add(-m.retention),
    }

    return m.storage.Delete(query)
}

// 聚合指标
func (m *MonitoringDataManager) AggregateMetrics(query *MetricQuery, aggregationFunc func([]float64) float64) (*MetricBatch, error) {
    // 检索原始数据
    batch, err := m.RetrieveMetrics(query)
    if err != nil {
        return nil, err
    }

    // 按时间窗口聚合
    windowSize := time.Hour // 可以配置
    aggregated := m.aggregateByWindow(batch, windowSize, aggregationFunc)

    return aggregated, nil
}

// 按时间窗口聚合
func (m *MonitoringDataManager) aggregateByWindow(batch *MetricBatch, windowSize time.Duration, aggregationFunc func([]float64) float64) *MetricBatch {
    windows := make(map[int64][]float64)

    for _, metric := range batch.Metrics {
        windowStart := batch.Timestamp.Truncate(windowSize).Unix()
        windows[windowStart] = append(windows[windowStart], metric.Value)
    }

    aggregated := &MetricBatch{
        Timestamp: batch.Timestamp,
        Labels:    batch.Labels,
        Metrics:   make([]Metric, 0),
    }

    for windowStart, values := range windows {
        if len(values) > 0 {
            aggregated.Metrics = append(aggregated.Metrics, Metric{
                Name:  batch.Metrics[0].Name,
                Value: aggregationFunc(values),
                Type:  batch.Metrics[0].Type,
            })
        }
    }

    return aggregated
}
```

## 故障排查

### 监控数据导出
```go
// 监控数据导出器
type MonitoringExporter struct {
    manager *MonitoringDataManager
    formats map[string]ExportFormat
}

// 导出格式
type ExportFormat interface {
    Export(batch *MetricBatch) ([]byte, error)
    Import(data []byte) (*MetricBatch, error)
}

// 创建监控数据导出器
func NewMonitoringExporter(manager *MonitoringDataManager) *MonitoringExporter {
    exporter := &MonitoringExporter{
        manager: manager,
        formats: make(map[string]ExportFormat),
    }

    // 注册默认格式
    exporter.RegisterFormat("json", &JSONExportFormat{})
    exporter.RegisterFormat("csv", &CSVExportFormat{})
    exporter.RegisterFormat("prometheus", &PrometheusExportFormat{})

    return exporter
}

// 注册导出格式
func (e *MonitoringExporter) RegisterFormat(name string, format ExportFormat) {
    e.formats[name] = format
}

// 导出数据
func (e *MonitoringExporter) ExportData(query *MetricQuery, formatName string) ([]byte, error) {
    format, exists := e.formats[formatName]
    if !exists {
        return nil, fmt.Errorf("format %s not supported", formatName)
    }

    // 检索数据
    batch, err := e.manager.RetrieveMetrics(query)
    if err != nil {
        return nil, err
    }

    // 导出数据
    return format.Export(batch)
}

// JSON导出格式
type JSONExportFormat struct{}

func (f *JSONExportFormat) Export(batch *MetricBatch) ([]byte, error) {
    return json.Marshal(batch)
}

func (f *JSONExportFormat) Import(data []byte) (*MetricBatch, error) {
    var batch MetricBatch
    err := json.Unmarshal(data, &batch)
    return &batch, err
}

// CSV导出格式
type CSVExportFormat struct{}

func (f *CSVExportFormat) Export(batch *MetricBatch) ([]byte, error) {
    var buf bytes.Buffer

    // 写入CSV头
    buf.WriteString("timestamp,metric_name,metric_value,metric_type\n")

    // 写入数据
    for _, metric := range batch.Metrics {
        buf.WriteString(fmt.Sprintf("%s,%s,%.2f,%s\n",
            batch.Timestamp.Format(time.RFC3339),
            metric.Name,
            metric.Value,
            metric.Type,
        ))
    }

    return buf.Bytes(), nil
}

func (f *CSVExportFormat) Import(data []byte) (*MetricBatch, error) {
    // 简化的CSV导入实现
    // 实际实现需要更复杂的解析逻辑
    return nil, fmt.Errorf("CSV import not implemented")
}

// Prometheus导出格式
type PrometheusExportFormat struct{}

func (f *PrometheusExportFormat) Export(batch *MetricBatch) ([]byte, error) {
    var buf bytes.Buffer

    for _, metric := range batch.Metrics {
        // 写入指标类型注释
        buf.WriteString(fmt.Sprintf("# TYPE %s %s\n", metric.Name, metric.Type))

        // 写入指标值
        buf.WriteString(fmt.Sprintf("%s %.2f\n", metric.Name, metric.Value))
    }

    return buf.Bytes(), nil
}

func (f *PrometheusExportFormat) Import(data []byte) (*MetricBatch, error) {
    // Prometheus格式导入通常不需要，因为这是导出格式
    return nil, fmt.Errorf("Prometheus import not implemented")
}
```

### 监控数据分析
```go
// 监控数据分析器
type MonitoringAnalyzer struct {
    manager *MonitoringDataManager
    rules   []AnalysisRule
}

// 分析规则
type AnalysisRule struct {
    Name        string                 `json:"name"`
    Description string                 `json:"description"`
    Condition   AnalysisCondition      `json:"condition"`
    Actions     []AnalysisAction       `json:"actions"`
}

// 分析条件
type AnalysisCondition struct {
    Metric     string                 `json:"metric"`
    Operator   string                 `json:"operator"`
    Threshold  float64                `json:"threshold"`
    Duration   time.Duration          `json:"duration"`
    Parameters map[string]interface{} `json:"parameters"`
}

// 分析动作
type AnalysisAction struct {
    Type       string                 `json:"type"`
    Parameters map[string]interface{} `json:"parameters"`
}

// 创建监控数据分析器
func NewMonitoringAnalyzer(manager *MonitoringDataManager) *MonitoringAnalyzer {
    return &MonitoringAnalyzer{
        manager: manager,
        rules:   make([]AnalysisRule, 0),
    }
}

// 添加分析规则
func (a *MonitoringAnalyzer) AddRule(rule *AnalysisRule) {
    a.rules = append(a.rules, *rule)
}

// 运行分析
func (a *MonitoringAnalyzer) RunAnalysis() ([]AnalysisResult, error) {
    results := make([]AnalysisResult, 0)

    for _, rule := range a.rules {
        result, err := a.analyzeRule(rule)
        if err != nil {
            log.Printf("Analysis rule %s failed: %v", rule.Name, err)
            continue
        }

        if result != nil {
            results = append(results, *result)
        }
    }

    return results, nil
}

// 分析规则
func (a *MonitoringAnalyzer) analyzeRule(rule AnalysisRule) (*AnalysisResult, error) {
    // 检索指标数据
    query := &MetricQuery{
        Name:      rule.Condition.Metric,
        StartTime: time.Now().Add(-rule.Condition.Duration),
        EndTime:   time.Now(),
    }

    batch, err := a.manager.RetrieveMetrics(query)
    if err != nil {
        return nil, err
    }

    // 分析数据
    triggered, value := a.evaluateCondition(batch, rule.Condition)
    if !triggered {
        return nil, nil
    }

    // 创建分析结果
    result := &AnalysisResult{
        ID:          generateID(),
        RuleName:    rule.Name,
        Description: rule.Description,
        Value:       value,
        Threshold:   rule.Condition.Threshold,
        Timestamp:   time.Now(),
        Actions:     rule.Actions,
    }

    // 执行动作
    for _, action := range rule.Actions {
        if err := a.executeAction(action, result); err != nil {
            log.Printf("Failed to execute action %s: %v", action.Type, err)
        }
    }

    return result, nil
}

// 评估条件
func (a *MonitoringAnalyzer) evaluateCondition(batch *MetricBatch, condition AnalysisCondition) (bool, float64) {
    if len(batch.Metrics) == 0 {
        return false, 0
    }

    // 计算指标值
    var value float64
    switch condition.Operator {
    case "avg":
        sum := 0.0
        for _, metric := range batch.Metrics {
            sum += metric.Value
        }
        value = sum / float64(len(batch.Metrics))
    case "max":
        value = batch.Metrics[0].Value
        for _, metric := range batch.Metrics {
            if metric.Value > value {
                value = metric.Value
            }
        }
    case "min":
        value = batch.Metrics[0].Value
        for _, metric := range batch.Metrics {
            if metric.Value < value {
                value = metric.Value
            }
        }
    case "sum":
        value = 0
        for _, metric := range batch.Metrics {
            value += metric.Value
        }
    default:
        value = batch.Metrics[len(batch.Metrics)-1].Value
    }

    // 比较阈值
    switch condition.Operator {
    case ">", ">=":
        return value > condition.Threshold, value
    case "<", "<=":
        return value < condition.Threshold, value
    case "==":
        return value == condition.Threshold, value
    default:
        return false, value
    }
}

// 执行动作
func (a *MonitoringAnalyzer) executeAction(action AnalysisAction, result *AnalysisResult) error {
    switch action.Type {
    case "log":
        log.Printf("Analysis result: %s - %s = %.2f (threshold: %.2f)",
            result.RuleName, result.Description, result.Value, result.Threshold)
    case "alert":
        // 创建告警
        alert := &Alert{
            ID:          generateID(),
            Name:        result.RuleName,
            Description: result.Description,
            Value:       result.Value,
            Threshold:   result.Threshold,
            Severity:    SeverityWarning,
            StartsAt:    result.Timestamp,
            Status:      AlertStatusFiring,
        }
        // 发送告警通知
        // 这里需要集成告警系统
    case "email":
        // 发送邮件通知
        // 这里需要集成邮件系统
    default:
        return fmt.Errorf("unknown action type: %s", action.Type)
    }

    return nil
}

// 分析结果
type AnalysisResult struct {
    ID          string            `json:"id"`
    RuleName    string            `json:"rule_name"`
    Description string            `json:"description"`
    Value       float64           `json:"value"`
    Threshold   float64           `json:"threshold"`
    Timestamp   time.Time         `json:"timestamp"`
    Actions     []AnalysisAction  `json:"actions"`
    Metadata    map[string]interface{} `json:"metadata"`
}
```

这个完整的Gin监控集成最佳实践文档涵盖了监控系统的各个方面，包括指标收集、日志管理、分布式追踪、性能监控、告警机制、可视化监控、监控最佳实践和故障排查等内容。每个部分都提供了详细的代码示例和实现方案，可以作为生产环境监控系统的参考实现。