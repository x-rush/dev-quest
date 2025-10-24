# Go 应用监控与可观测性

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `deployment/devops` |
| **难度** | ⭐⭐⭐⭐ |
| **标签** | `#monitoring` `#observability` `#logging` `#metrics` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 📚 概述

监控和可观测性是现代Go应用运维的核心要素。Go语言的并发特性和丰富的标准库使其在监控方面具有天然优势。本指南将详细介绍Go应用的监控、日志、追踪和告警体系。

### 🎯 学习目标
- 掌握Go应用监控指标收集
- 学会分布式追踪实现
- 理解日志收集和分析
- 掌握性能分析和调优
- 学会故障诊断和预测

## 🔄 可观测性三大支柱

### 1. 指标监控
- **Metrics**: 数值型指标，如CPU使用率、内存占用、请求计数等
- **Prometheus**: 开源监控和告警系统
- **OpenTelemetry**: 云原生可观测性框架

### 2. 日志管理
- **Structured Logging**: 结构化日志记录
- **Log Aggregation**: 日志聚合和分析
- **Log Correlation**: 日志关联和追踪

### 3. 分布式追踪
- **Tracing**: 请求链路追踪
- **Spans**: 追踪单元
- **Context Propagation**: 上下文传播

## 📝 指标监控

### 1. Prometheus 集成

#### 基础指标收集
```go
// metrics/prometheus.go
package metrics

import (
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    // HTTP请求指标
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )

    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration in seconds",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint"},
    )

    // 数据库指标
    dbQueriesTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "db_queries_total",
            Help: "Total number of database queries",
        },
        []string{"operation", "table", "status"},
    )

    dbQueryDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "db_query_duration_seconds",
            Help:    "Database query duration in seconds",
            Buckets: []float64{0.001, 0.01, 0.1, 1, 10},
        },
        []string{"operation", "table"},
    )

    // 业务指标
    activeUsers = promauto.NewGauge(
        prometheus.GaugeOpts{
            Name: "active_users",
            Help: "Number of active users",
        },
    )

    orderProcessingTime = promauto.NewHistogram(
        prometheus.HistogramOpts{
            Name:    "order_processing_duration_seconds",
            Help:    "Order processing duration in seconds",
            Buckets: []float64{0.1, 0.5, 1, 2.5, 5, 10},
        },
    )
)

// 记录HTTP请求
func RecordHTTPRequest(method, endpoint string, status int, duration time.Duration) {
    httpRequestsTotal.WithLabelValues(method, endpoint, getStatusRange(status)).Inc()
    httpRequestDuration.WithLabelValues(method, endpoint).Observe(duration.Seconds())
}

// 记录数据库查询
func RecordDBQuery(operation, table string, status string, duration time.Duration) {
    dbQueriesTotal.WithLabelValues(operation, table, status).Inc()
    dbQueryDuration.WithLabelValues(operation, table).Observe(duration.Seconds())
}

// 更新活跃用户数
func UpdateActiveUsers(count int) {
    activeUsers.Set(float64(count))
}

// 记录订单处理时间
func RecordOrderProcessing(duration time.Duration) {
    orderProcessingTime.Observe(duration.Seconds())
}

func getStatusRange(status int) string {
    switch {
    case status >= 200 && status < 300:
        return "2xx"
    case status >= 300 && status < 400:
        return "3xx"
    case status >= 400 && status < 500:
        return "4xx"
    case status >= 500:
        return "5xx"
    default:
        return "unknown"
    }
}
```

#### 中间件集成
```go
// middleware/metrics.go
package middleware

import (
    "strconv"
    "time"

    "github.com/gin-gonic/gin"
    "your-project/metrics"
)

func PrometheusMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        // 处理请求
        c.Next()

        // 记录指标
        duration := time.Since(start)
        method := c.Request.Method
        endpoint := c.FullPath()
        status := c.Writer.Status()

        metrics.RecordHTTPRequest(method, endpoint, status, duration)
    }
}

func DatabaseMetricsMiddleware(operation, table string) func(next func() error) error {
    return func(next func() error) error {
        start := time.Now()
        err := next()
        duration := time.Since(start)

        status := "success"
        if err != nil {
            status = "error"
        }

        metrics.RecordDBQuery(operation, table, status, duration)
        return err
    }
}
```

#### 自定义业务指标
```go
// metrics/business.go
package metrics

import (
    "sync"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    // 用户相关指标
    userRegistrations = promauto.NewCounter(
        prometheus.CounterOpts{
            Name: "user_registrations_total",
            Help: "Total number of user registrations",
        },
    )

    userLogins = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "user_logins_total",
            Help: "Total number of user logins",
        },
        []string{"status"}, // success, failed
    )

    // 订单相关指标
    ordersCreated = promauto.NewCounter(
        prometheus.CounterOpts{
            Name: "orders_created_total",
            Help: "Total number of orders created",
        },
    )

    ordersAmount = promauto.NewHistogram(
        prometheus.HistogramOpts{
            Name:    "orders_amount_dollars",
            Help:    "Order amounts in dollars",
            Buckets: []float64{10, 50, 100, 500, 1000, 5000},
        },
    )

    // 缓存指标
    cacheHits = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "cache_hits_total",
            Help: "Total number of cache hits",
        },
        []string{"cache_type"},
    )

    cacheMisses = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "cache_misses_total",
            Help: "Total number of cache misses",
        },
        []string{"cache_type"},
    )
)

// 用户指标记录
func RecordUserRegistration() {
    userRegistrations.Inc()
}

func RecordUserLogin(status string) {
    userLogins.WithLabelValues(status).Inc()
}

// 订单指标记录
func RecordOrderCreated(amount float64) {
    ordersCreated.Inc()
    ordersAmount.Observe(amount)
}

// 缓存指标记录
func RecordCacheHit(cacheType string) {
    cacheHits.WithLabelValues(cacheType).Inc()
}

func RecordCacheMiss(cacheType string) {
    cacheMisses.WithLabelValues(cacheType).Inc()
}

// 实时统计指标
type realtimeStats struct {
    mu                sync.RWMutex
    activeConnections int
    lastMinuteRequests int
    requestTimes       []time.Time
}

var RealtimeStats = &realtimeStats{
    requestTimes: make([]time.Time, 0),
}

func (rs *realtimeStats) AddRequest() {
    rs.mu.Lock()
    defer rs.mu.Unlock()

    now := time.Now()
    rs.requestTimes = append(rs.requestTimes, now)

    // 清理1分钟前的请求
    cutoff := now.Add(-time.Minute)
    var validRequests []time.Time
    for _, t := range rs.requestTimes {
        if t.After(cutoff) {
            validRequests = append(validRequests, t)
        }
    }
    rs.requestTimes = validRequests
    rs.lastMinuteRequests = len(validRequests)
}

func (rs *realtimeStats) GetRequestsPerMinute() int {
    rs.mu.RLock()
    defer rs.mu.RUnlock()
    return rs.lastMinuteRequests
}

func (rs *realtimeStats) AddConnection() {
    rs.mu.Lock()
    defer rs.mu.Unlock()
    rs.activeConnections++
}

func (rs *realtimeStats) RemoveConnection() {
    rs.mu.Lock()
    defer rs.mu.Unlock()
    rs.activeConnections--
}

func (rs *realtimeStats) GetActiveConnections() int {
    rs.mu.RLock()
    defer rs.mu.RUnlock()
    return rs.activeConnections
}
```

### 2. OpenTelemetry 集成

#### 初始化配置
```go
// telemetry/otel.go
package telemetry

import (
    "context"
    "time"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/jaeger"
    "go.opentelemetry.io/otel/exporters/prometheus"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/metric"
    "go.opentelemetry.io/otel/sdk/resource"
    "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.4.0"
)

func InitProvider(serviceName, jaegerURL string) (func(), error) {
    // 设置资源属性
    res, err := resource.New(context.Background(),
        resource.WithAttributes(
            semconv.ServiceNameKey.String(serviceName),
            semconv.ServiceVersionKey.String("1.0.0"),
            semconv.ServiceInstanceIDKey.String("instance-1"),
        ),
    )
    if err != nil {
        return nil, err
    }

    // Jaeger导出器
    jaegerExporter, err := jaeger.New(jaeger.WithCollectorEndpoint(jaeger.WithEndpoint(jaegerURL)))
    if err != nil {
        return nil, err
    }

    // Prometheus导出器
    prometheusExporter, err := prometheus.New()
    if err != nil {
        return nil, err
    }

    // 创建TracerProvider
    tracerProvider := trace.NewTracerProvider(
        trace.WithBatcher(jaegerExporter),
        trace.WithResource(res),
        trace.WithSampler(trace.AlwaysSample()),
    )

    // 创建MeterProvider
    meterProvider := metric.NewMeterProvider(
        metric.WithResource(res),
        metric.WithReader(prometheusExporter),
    )

    // 设置全局Provider
    otel.SetTracerProvider(tracerProvider)
    otel.SetMeterProvider(meterProvider)
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))

    // 返回清理函数
    return func() {
        ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        defer cancel()

        if err := tracerProvider.Shutdown(ctx); err != nil {
            // 处理错误
        }

        if err := meterProvider.Shutdown(ctx); err != nil {
            // 处理错误
        }
    }, nil
}
```

#### 追踪使用示例
```go
// services/user_service.go
package services

import (
    "context"
    "time"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/trace"
)

type UserService struct {
    tracer trace.Tracer
}

func NewUserService() *UserService {
    return &UserService{
        tracer: otel.Tracer("user-service"),
    }
}

func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    ctx, span := s.tracer.Start(ctx, "GetUser",
        trace.WithAttributes(
            attribute.String("user.id", id),
        ),
    )
    defer span.End()

    // 模拟数据库查询
    time.Sleep(10 * time.Millisecond)

    user := &User{
        ID:   id,
        Name: "John Doe",
        Email: "john@example.com",
    }

    span.SetAttributes(
        attribute.String("user.name", user.Name),
        attribute.String("user.email", user.Email),
    )

    return user, nil
}

func (s *UserService) CreateUser(ctx context.Context, req *CreateUserRequest) (*User, error) {
    ctx, span := s.tracer.Start(ctx, "CreateUser")
    defer span.End()

    // 验证输入
    if err := validateUser(req); err != nil {
        span.RecordError(err)
        span.SetStatus(trace.StatusError, err.Error())
        return nil, err
    }

    // 创建用户
    user := &User{
        ID:   generateUserID(),
        Name: req.Name,
        Email: req.Email,
    }

    span.SetAttributes(
        attribute.String("user.id", user.ID),
        attribute.String("user.name", user.Name),
    )

    return user, nil
}
```

## 📝 日志管理

### 1. 结构化日志

#### Zap 日志配置
```go
// logging/logger.go
package logging

import (
    "os"
    "time"

    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

var Logger *zap.Logger

func InitLogger(level string) error {
    zapLevel := zapcore.InfoLevel
    switch level {
    case "debug":
        zapLevel = zapcore.DebugLevel
    case "info":
        zapLevel = zapcore.InfoLevel
    case "warn":
        zapLevel = zapcore.WarnLevel
    case "error":
        zapLevel = zapcore.ErrorLevel
    }

    config := zap.Config{
        Level:    zap.NewAtomicLevelAt(zapLevel),
        Development: false,
        Encoding: "json",
        EncoderConfig: zapcore.EncoderConfig{
            TimeKey:        "timestamp",
            LevelKey:       "level",
            NameKey:        "logger",
            CallerKey:      "caller",
            FunctionKey:    zapcore.OmitKey,
            MessageKey:     "message",
            StacktraceKey:  "stacktrace",
            LineEnding:     zapcore.DefaultLineEnding,
            EncodeLevel:    zapcore.LowercaseLevelEncoder,
            EncodeTime:     zapcore.ISO8601TimeEncoder,
            EncodeDuration: zapcore.SecondsDurationEncoder,
            EncodeCaller:   zapcore.ShortCallerEncoder,
        },
        OutputPaths:      []string{"stdout"},
        ErrorOutputPaths: []string{"stderr"},
    }

    // 生产环境配置
    if os.Getenv("APP_ENV") == "production" {
        config.OutputPaths = []string{"stdout", "/var/log/app.log"}
        config.ErrorOutputPaths = []string{"stderr", "/var/log/app-error.log"}
    }

    var err error
    Logger, err = config.Build()
    if err != nil {
        return err
    }

    return nil
}

// 添加上下文信息的日志记录器
type ContextLogger struct {
    logger *zap.Logger
    fields []zap.Field
}

func WithFields(fields ...zap.Field) *ContextLogger {
    return &ContextLogger{
        logger: Logger,
        fields: fields,
    }
}

func (cl *ContextLogger) WithFields(fields ...zap.Field) *ContextLogger {
    return &ContextLogger{
        logger: cl.logger,
        fields: append(cl.fields, fields...),
    }
}

func (cl *ContextLogger) Debug(msg string, fields ...zap.Field) {
    cl.logger.Debug(msg, append(cl.fields, fields...)...)
}

func (cl *ContextLogger) Info(msg string, fields ...zap.Field) {
    cl.logger.Info(msg, append(cl.fields, fields...)...)
}

func (cl *ContextLogger) Warn(msg string, fields ...zap.Field) {
    cl.logger.Warn(msg, append(cl.fields, fields...)...)
}

func (cl *ContextLogger) Error(msg string, fields ...zap.Field) {
    cl.logger.Error(msg, append(cl.fields, fields...)...)
}

func (cl *ContextLogger) Fatal(msg string, fields ...zap.Field) {
    cl.logger.Fatal(msg, append(cl.fields, fields...)...)
}

// HTTP请求日志中间件
func HTTPLoggingMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        raw := c.Request.URL.RawQuery

        // 处理请求
        c.Next()

        // 记录日志
        end := time.Now()
        latency := end.Sub(start)

        if raw != "" {
            path = path + "?" + raw
        }

        logger := WithFields(
            zap.String("method", c.Request.Method),
            zap.String("path", path),
            zap.String("ip", c.ClientIP()),
            zap.String("user_agent", c.Request.UserAgent()),
            zap.Int("status", c.Writer.Status()),
            zap.Duration("latency", latency),
            zap.String("request_id", c.GetHeader("X-Request-ID")),
        )

        switch {
        case c.Writer.Status() >= 500:
            logger.Error("HTTP request error")
        case c.Writer.Status() >= 400:
            logger.Warn("HTTP request warning")
        default:
            logger.Info("HTTP request")
        }
    }
}
```

#### 业务日志记录
```go
// services/order_service.go
package services

import (
    "context"
    "time"

    "your-project/logging"
)

type OrderService struct {
    logger *logging.ContextLogger
}

func NewOrderService() *OrderService {
    return &OrderService{
        logger: logging.WithFields(zap.String("service", "order-service")),
    }
}

func (s *OrderService) CreateOrder(ctx context.Context, req *CreateOrderRequest) (*Order, error) {
    // 记录订单创建开始
    s.logger.Info("Creating order",
        zap.String("user_id", req.UserID),
        zap.Float64("amount", req.Amount),
        zap.Strings("product_ids", req.ProductIDs),
    )

    // 验证库存
    if err := s.validateInventory(req.ProductIDs); err != nil {
        s.logger.Error("Inventory validation failed",
            zap.String("user_id", req.UserID),
            zap.Error(err),
        )
        return nil, err
    }

    // 创建订单
    order := &Order{
        ID:         generateOrderID(),
        UserID:     req.UserID,
        ProductIDs: req.ProductIDs,
        Amount:     req.Amount,
        Status:     "pending",
        CreatedAt:  time.Now(),
    }

    // 处理支付
    if err := s.processPayment(order); err != nil {
        s.logger.Error("Payment processing failed",
            zap.String("order_id", order.ID),
            zap.String("user_id", req.UserID),
            zap.Error(err),
        )
        return nil, err
    }

    order.Status = "confirmed"

    s.logger.Info("Order created successfully",
        zap.String("order_id", order.ID),
        zap.String("user_id", req.UserID),
        zap.String("status", order.Status),
    )

    return order, nil
}

func (s *OrderService) validateInventory(productIDs []string) error {
    s.logger.Debug("Validating inventory",
        zap.Strings("product_ids", productIDs),
    )

    // 库存验证逻辑
    time.Sleep(10 * time.Millisecond)

    return nil
}

func (s *OrderService) processPayment(order *Order) error {
    s.logger.Debug("Processing payment",
        zap.String("order_id", order.ID),
        zap.Float64("amount", order.Amount),
    )

    // 支付处理逻辑
    time.Sleep(50 * time.Millisecond)

    return nil
}
```

### 2. 日志聚合和分析

#### ELK Stack 集成
```go
// logging/elk.go
package logging

import (
    "context"
    "encoding/json"
    "fmt"
    "net/http"
    "sync"
    "time"

    "go.uber.org/zap"
)

type ELKSender struct {
    elasticsearchURL string
    indexPrefix     string
    httpClient      *http.Client
    buffer          chan *LogEntry
    wg              sync.WaitGroup
}

type LogEntry struct {
    Timestamp   time.Time              `json:"timestamp"`
    Level       string                 `json:"level"`
    Message     string                 `json:"message"`
    Service     string                 `json:"service"`
    Host        string                 `json:"host"`
    Fields      map[string]interface{} `json:"fields,omitempty"`
    TraceID     string                 `json:"trace_id,omitempty"`
    SpanID      string                 `json:"span_id,omitempty"`
}

func NewELKSender(elasticsearchURL, indexPrefix string, bufferSize int) *ELKSender {
    sender := &ELKSender{
        elasticsearchURL: elasticsearchURL,
        indexPrefix:     indexPrefix,
        httpClient:      &http.Client{Timeout: 30 * time.Second},
        buffer:          make(chan *LogEntry, bufferSize),
    }

    sender.wg.Add(1)
    go sender.sendBatch()

    return sender
}

func (s *ELKSender) Send(entry *LogEntry) {
    select {
    case s.buffer <- entry:
    default:
        // 缓冲区满，丢弃日志
        Logger.Warn("ELK buffer full, dropping log entry")
    }
}

func (s *ELKSender) sendBatch() {
    defer s.wg.Done()

    ticker := time.NewTicker(5 * time.Second)
    defer ticker.Stop()

    batch := make([]*LogEntry, 0, 100)

    for {
        select {
        case entry := <-s.buffer:
            batch = append(batch, entry)
            if len(batch) >= 100 {
                s.flushBatch(batch)
                batch = batch[:0]
            }
        case <-ticker.C:
            if len(batch) > 0 {
                s.flushBatch(batch)
                batch = batch[:0]
            }
        }
    }
}

func (s *ELKSender) flushBatch(batch []*LogEntry) {
    if len(batch) == 0 {
        return
    }

    // 构建批量请求体
    var body []byte
    index := fmt.Sprintf("%s-%s", s.indexPrefix, time.Now().Format("2006.01.02"))

    for _, entry := range batch {
        action := map[string]interface{}{
            "index": map[string]interface{}{
                "_index": index,
                "_type":  "_doc",
            },
        }
        actionBytes, _ := json.Marshal(action)
        entryBytes, _ := json.Marshal(entry)

        body = append(body, actionBytes...)
        body = append(body, '\n')
        body = append(body, entryBytes...)
        body = append(body, '\n')
    }

    // 发送到Elasticsearch
    req, err := http.NewRequest("POST", s.elasticsearchURL+"/_bulk", bytes.NewReader(body))
    if err != nil {
        Logger.Error("Failed to create ELK request", zap.Error(err))
        return
    }

    req.Header.Set("Content-Type", "application/x-ndjson")

    resp, err := s.httpClient.Do(req)
    if err != nil {
        Logger.Error("Failed to send logs to ELK", zap.Error(err))
        return
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 400 {
        Logger.Error("ELK returned error status", zap.Int("status", resp.StatusCode))
    }
}

func (s *ELKSender) Close() {
    close(s.buffer)
    s.wg.Wait()
}
```

## 📝 性能分析

### 1. pprof 性能分析

#### pprof 集成
```go
// pprof/pprof.go
package pprof

import (
    "net/http"
    "net/http/pprof"

    "github.com/gin-gonic/gin"
)

func Register(router *gin.Engine) {
    // 注册pprof路由
    router.GET("/debug/pprof/", gin.WrapH(http.HandlerFunc(pprof.Index)))
    router.GET("/debug/pprof/cmdline", gin.WrapH(http.HandlerFunc(pprof.Cmdline)))
    router.GET("/debug/pprof/profile", gin.WrapH(http.HandlerFunc(pprof.Profile)))
    router.GET("/debug/pprof/symbol", gin.WrapH(http.HandlerFunc(pprof.Symbol)))
    router.GET("/debug/pprof/trace", gin.WrapH(http.HandlerFunc(pprof.Trace)))

    // 添加自定义性能指标路由
    router.GET("/debug/metrics", metricsHandler)
    router.GET("/debug/health", healthHandler)
}

func metricsHandler(c *gin.Context) {
    // 返回应用性能指标
    metrics := map[string]interface{}{
        "goroutines": runtime.NumGoroutine(),
        "memory":     getMemoryStats(),
        "gc_stats":   getGCStats(),
        "cpu_usage":  getCPUUsage(),
    }

    c.JSON(http.StatusOK, metrics)
}

func healthHandler(c *gin.Context) {
    // 健康检查
    health := map[string]string{
        "status": "healthy",
        "uptime": getUptime(),
    }

    c.JSON(http.StatusOK, health)
}

func getMemoryStats() map[string]interface{} {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

    return map[string]interface{}{
        "alloc":      m.Alloc,
        "total_alloc": m.TotalAlloc,
        "sys":        m.Sys,
        "num_gc":     m.NumGC,
        "pause_total_ns": m.PauseTotalNs,
    }
}

func getGCStats() map[string]interface{} {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

    return map[string]interface{}{
        "last_gc":       m.LastGC,
        "next_gc":       m.NextGC,
        "num_gc":        m.NumGC,
        "gc_cpu_fraction": m.GCCPUFraction,
    }
}

func getCPUUsage() float64 {
    // 简化的CPU使用率计算
    return 0.0
}

func getUptime() string {
    // 返回应用运行时间
    return "0s"
}
```

#### 性能分析工具
```go
// profiling/profiler.go
package profiling

import (
    "context"
    "os"
    "runtime/pprof"
    "time"

    "go.uber.org/zap"
)

type Profiler struct {
    logger *zap.Logger
}

func NewProfiler(logger *zap.Logger) *Profiler {
    return &Profiler{logger: logger}
}

func (p *Profiler) StartCPUProfile(filename string) (*os.File, error) {
    f, err := os.Create(filename)
    if err != nil {
        return nil, err
    }

    if err := pprof.StartCPUProfile(f); err != nil {
        f.Close()
        return nil, err
    }

    p.logger.Info("CPU profiling started", zap.String("filename", filename))
    return f, nil
}

func (p *Profiler) StopCPUProfile(f *os.File) {
    pprof.StopCPUProfile()
    f.Close()
    p.logger.Info("CPU profiling stopped")
}

func (p *Profiler) ProfileMemory(filename string) error {
    f, err := os.Create(filename)
    if err != nil {
        return err
    }
    defer f.Close()

    if err := pprof.WriteHeapProfile(f); err != nil {
        return err
    }

    p.logger.Info("Memory profile written", zap.String("filename", filename))
    return nil
}

func (p *Profiler) ProfileGoroutines(filename string) error {
    f, err := os.Create(filename)
    if err != nil {
        return err
    }
    defer f.Close()

    if err := pprof.Lookup("goroutine").WriteTo(f, 0); err != nil {
        return err
    }

    p.logger.Info("Goroutine profile written", zap.String("filename", filename))
    return nil
}

// 自动化性能分析
func (p *Profiler) AutoProfile(ctx context.Context, duration time.Duration) {
    ticker := time.NewTicker(duration)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            // CPU性能分析
            cpuFile, err := p.StartCPUProfile(fmt.Sprintf("cpu-%s.prof", time.Now().Format("20060102-150405")))
            if err != nil {
                p.logger.Error("Failed to start CPU profile", zap.Error(err))
                continue
            }

            // 运行30秒
            time.Sleep(30 * time.Second)

            p.StopCPUProfile(cpuFile)

            // 内存性能分析
            if err := p.ProfileMemory(fmt.Sprintf("mem-%s.prof", time.Now().Format("20060102-150405"))); err != nil {
                p.logger.Error("Failed to profile memory", zap.Error(err))
            }

        case <-ctx.Done():
            return
        }
    }
}
```

### 2. 业务性能监控

#### 响应时间监控
```go
// monitoring/response_time.go
package monitoring

import (
    "sync"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

type ResponseTimeMonitor struct {
    responseTimes map[string][]time.Duration
    mu           sync.RWMutex

    // Prometheus指标
    responseTimeHistogram *prometheus.HistogramVec
    responseTimeSummary   *prometheus.SummaryVec
}

func NewResponseTimeMonitor() *ResponseTimeMonitor {
    return &ResponseTimeMonitor{
        responseTimes: make(map[string][]time.Duration),
        responseTimeHistogram: promauto.NewHistogramVec(
            prometheus.HistogramOpts{
                Name:    "response_time_seconds",
                Help:    "Response time in seconds",
                Buckets: []float64{0.001, 0.01, 0.1, 0.5, 1, 2.5, 5, 10},
            },
            []string{"endpoint", "method"},
        ),
        responseTimeSummary: promauto.NewSummaryVec(
            prometheus.SummaryOpts{
                Name:       "response_time_summary_seconds",
                Help:       "Response time summary in seconds",
                Objectives: map[float64]float64{0.5: 0.05, 0.9: 0.01, 0.99: 0.001},
            },
            []string{"endpoint", "method"},
        ),
    }
}

func (m *ResponseTimeMonitor) RecordResponseTime(endpoint, method string, duration time.Duration) {
    key := fmt.Sprintf("%s-%s", method, endpoint)

    // 记录到内存中
    m.mu.Lock()
    m.responseTimes[key] = append(m.responseTimes[key], duration)

    // 保持最近1000个记录
    if len(m.responseTimes[key]) > 1000 {
        m.responseTimes[key] = m.responseTimes[key][1:]
    }
    m.mu.Unlock()

    // 记录到Prometheus
    m.responseTimeHistogram.WithLabelValues(endpoint, method).Observe(duration.Seconds())
    m.responseTimeSummary.WithLabelValues(endpoint, method).Observe(duration.Seconds())
}

func (m *ResponseTimeMonitor) GetAverageResponseTime(endpoint, method string) time.Duration {
    key := fmt.Sprintf("%s-%s", method, endpoint)

    m.mu.RLock()
    defer m.mu.RUnlock()

    times := m.responseTimes[key]
    if len(times) == 0 {
        return 0
    }

    var total time.Duration
    for _, t := range times {
        total += t
    }

    return total / time.Duration(len(times))
}

func (m *ResponseTimeMonitor) GetPercentileResponseTime(endpoint, method string, percentile float64) time.Duration {
    key := fmt.Sprintf("%s-%s", method, endpoint)

    m.mu.RLock()
    defer m.mu.RUnlock()

    times := m.responseTimes[key]
    if len(times) == 0 {
        return 0
    }

    // 复制并排序
    sorted := make([]time.Duration, len(times))
    copy(sorted, times)
    sort.Slice(sorted, func(i, j int) bool {
        return sorted[i] < sorted[j]
    })

    index := int(float64(len(sorted)) * percentile)
    if index >= len(sorted) {
        index = len(sorted) - 1
    }

    return sorted[index]
}
```

## 📝 告警和通知

### 1. 告警规则配置

#### Prometheus 告警规则
```yaml
# alerts/rules.yml
groups:
- name: go-app-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} requests per second"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected"
      description: "95th percentile latency is {{ $value }} seconds"

  - alert: HighMemoryUsage
    expr: go_memstats_alloc_bytes / go_memstats_sys_bytes > 0.8
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High memory usage detected"
      description: "Memory usage is {{ $value | humanizePercentage }}"

  - alert: DatabaseConnectionsHigh
    expr: go_sql_stats_max_open_connections / go_sql_stats_max_open_connections > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Database connections high"
      description: "Database connection usage is {{ $value | humanizePercentage }}"

  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
      description: "Service {{ $labels.instance }} has been down for more than 1 minute"
```

#### 自定义告警处理器
```go
// alerting/handler.go
package alerting

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "sync"
    "time"

    "github.com/prometheus/alertmanager/template"
    "go.uber.org/zap"
)

type AlertHandler struct {
    logger     *zap.Logger
    notifiers  []Notifier
    alertStore *AlertStore
}

type Notifier interface {
    Send(alert *Alert) error
    Name() string
}

type Alert struct {
    Status      string                 `json:"status"`
    Labels      map[string]string      `json:"labels"`
    Annotations map[string]string      `json:"annotations"`
    StartsAt    time.Time              `json:"startsAt"`
    EndsAt      time.Time              `json:"endsAt"`
    GeneratorURL string               `json:"generatorURL"`
}

func NewAlertHandler(logger *zap.Logger) *AlertHandler {
    return &AlertHandler{
        logger:     logger,
        alertStore: NewAlertStore(),
    }
}

func (h *AlertHandler) AddNotifier(notifier Notifier) {
    h.notifiers = append(h.notifiers, notifier)
}

func (h *AlertHandler) HandleWebhook(w http.ResponseWriter, r *http.Request) {
    var data template.Data
    if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
        h.logger.Error("Failed to decode alert", zap.Error(err))
        http.Error(w, "Bad Request", http.StatusBadRequest)
        return
    }

    // 处理每个告警
    for _, alert := range data.Alerts {
        h.processAlert(alert)
    }

    w.WriteHeader(http.StatusOK)
}

func (h *AlertHandler) processAlert(alert template.Alert) {
    // 转换为内部Alert结构
    internalAlert := &Alert{
        Status:      alert.Status,
        Labels:      alert.Labels,
        Annotations: alert.Annotations,
        StartsAt:    alert.StartsAt,
        EndsAt:      alert.EndsAt,
        GeneratorURL: alert.GeneratorURL,
    }

    // 存储告警
    h.alertStore.Store(internalAlert)

    // 发送通知
    for _, notifier := range h.notifiers {
        if err := notifier.Send(internalAlert); err != nil {
            h.logger.Error("Failed to send alert notification",
                zap.String("notifier", notifier.Name()),
                zap.Error(err),
            )
        }
    }
}

// Slack通知器
type SlackNotifier struct {
    webhookURL string
    httpClient *http.Client
}

func NewSlackNotifier(webhookURL string) *SlackNotifier {
    return &SlackNotifier{
        webhookURL: webhookURL,
        httpClient: &http.Client{Timeout: 30 * time.Second},
    }
}

func (n *SlackNotifier) Send(alert *Alert) error {
    // 生成Slack消息
    message := n.formatSlackMessage(alert)

    // 发送到Slack
    return n.sendToSlack(message)
}

func (n *SlackNotifier) formatSlackMessage(alert *Alert) SlackMessage {
    color := "#36a64f" // green
    if alert.Status == "firing" {
        color = "#ff0000" // red
    }

    return SlackMessage{
        Text: fmt.Sprintf("Alert: %s", alert.Labels["alertname"]),
        Attachments: []SlackAttachment{
            {
                Color:      color,
                Title:      alert.Annotations["summary"],
                Text:       alert.Annotations["description"],
                Fields:     n.formatFields(alert),
                Footer:     "Prometheus AlertManager",
                Ts:         alert.StartsAt.Unix(),
            },
        },
    }
}

func (n *SlackNotifier) sendToSlack(message SlackMessage) error {
    payload, err := json.Marshal(message)
    if err != nil {
        return err
    }

    req, err := http.NewRequest("POST", n.webhookURL, bytes.NewReader(payload))
    if err != nil {
        return err
    }

    req.Header.Set("Content-Type", "application/json")

    resp, err := n.httpClient.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("slack returned status %d", resp.StatusCode)
    }

    return nil
}

func (n *SlackNotifier) Name() string {
    return "slack"
}

// 告警存储
type AlertStore struct {
    alerts map[string]*Alert
    mu     sync.RWMutex
}

func NewAlertStore() *AlertStore {
    return &AlertStore{
        alerts: make(map[string]*Alert),
    }
}

func (s *AlertStore) Store(alert *Alert) {
    key := fmt.Sprintf("%s-%s", alert.Labels["alertname"], alert.Labels["instance"])

    s.mu.Lock()
    defer s.mu.Unlock()

    s.alerts[key] = alert
}

func (s *AlertStore) Get(alertname, instance string) (*Alert, bool) {
    key := fmt.Sprintf("%s-%s", alertname, instance)

    s.mu.RLock()
    defer s.mu.RUnlock()

    alert, exists := s.alerts[key]
    return alert, exists
}

func (s *AlertStore) GetAll() []*Alert {
    s.mu.RLock()
    defer s.mu.RUnlock()

    alerts := make([]*Alert, 0, len(s.alerts))
    for _, alert := range s.alerts {
        alerts = append(alerts, alert)
    }

    return alerts
}
```

## 🧪 实践练习

### 练习1: 完整的监控系统
```go
// main.go
package main

import (
    "context"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "go.uber.org/zap"

    "your-project/logging"
    "your-project/metrics"
    "your-project/pprof"
    "your-project/telemetry"
)

func main() {
    // 初始化日志
    if err := logging.InitLogger("info"); err != nil {
        panic(err)
    }
    defer logging.Logger.Sync()

    // 初始化OpenTelemetry
    cleanup, err := telemetry.InitProvider("go-app", "http://jaeger:14268/api/traces")
    if err != nil {
        logging.Logger.Fatal("Failed to initialize telemetry", zap.Error(err))
    }
    defer cleanup()

    // 创建Gin引擎
    r := gin.Default()

    // 注册中间件
    r.Use(logging.HTTPLoggingMiddleware())
    r.Use(middleware.PrometheusMiddleware())

    // 注册路由
    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello, World!"})
    })

    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "healthy"})
    })

    // 注册监控端点
    r.GET("/metrics", gin.WrapH(promhttp.Handler()))
    pprof.Register(r)

    // 启动服务器
    logging.Logger.Info("Starting server on :8080")
    if err := r.Run(":8080"); err != nil {
        logging.Logger.Fatal("Failed to start server", zap.Error(err))
    }
}
```

### 练习2: 自定义业务监控
```go
// services/business_monitor.go
package services

import (
    "context"
    "sync"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
    "go.uber.org/zap"
)

type BusinessMonitor struct {
    logger *zap.Logger

    // 业务指标
    orderCount       *prometheus.CounterVec
    orderAmount      *prometheus.HistogramVec
    userActivity     *prometheus.GaugeVec
    conversionRate   *prometheus.GaugeVec

    // 实时统计
    realtimeStats    *RealtimeBusinessStats
}

type RealtimeBusinessStats struct {
    mu              sync.RWMutex
    ordersPerHour   map[string]int
    revenuePerHour  map[string]float64
    activeUsers     int
    conversions     map[string]int
}

func NewBusinessMonitor(logger *zap.Logger) *BusinessMonitor {
    return &BusinessMonitor{
        logger: logger,
        orderCount: promauto.NewCounterVec(
            prometheus.CounterOpts{
                Name: "business_orders_total",
                Help: "Total number of orders",
            },
            []string{"category", "status"},
        ),
        orderAmount: promauto.NewHistogramVec(
            prometheus.HistogramOpts{
                Name:    "business_order_amount_dollars",
                Help:    "Order amounts in dollars",
                Buckets: []float64{10, 50, 100, 500, 1000, 5000},
            },
            []string{"category"},
        ),
        userActivity: promauto.NewGaugeVec(
            prometheus.GaugeOpts{
                Name: "business_active_users",
                Help: "Number of active users",
            },
            []string{"segment"},
        ),
        conversionRate: promauto.NewGaugeVec(
            prometheus.GaugeOpts{
                Name: "business_conversion_rate",
                Help: "Conversion rate by segment",
            },
            []string{"segment"},
        ),
        realtimeStats: &RealtimeBusinessStats{
            ordersPerHour:  make(map[string]int),
            revenuePerHour: make(map[string]float64),
            conversions:    make(map[string]int),
        },
    }
}

func (m *BusinessMonitor) RecordOrder(order *Order) {
    // 记录订单指标
    m.orderCount.WithLabelValues(order.Category, order.Status).Inc()
    m.orderAmount.WithLabelValues(order.Category).Observe(order.Amount)

    // 更新实时统计
    m.updateRealtimeStats(order)

    m.logger.Info("Order recorded",
        zap.String("order_id", order.ID),
        zap.String("category", order.Category),
        zap.Float64("amount", order.Amount),
        zap.String("status", order.Status),
    )
}

func (m *BusinessMonitor) UpdateUserActivity(segment string, count int) {
    m.userActivity.WithLabelValues(segment).Set(float64(count))

    m.realtimeStats.mu.Lock()
    m.realtimeStats.activeUsers = count
    m.realtimeStats.mu.Unlock()
}

func (m *BusinessMonitor) RecordConversion(segment string) {
    m.realtimeStats.mu.Lock()
    m.realtimeStats.conversions[segment]++
    m.realtimeStats.mu.Unlock()

    // 计算转化率
    m.calculateConversionRate(segment)
}

func (m *BusinessMonitor) updateRealtimeStats(order *Order) {
    hour := time.Now().Format("2006-01-02-15")

    m.realtimeStats.mu.Lock()
    defer m.realtimeStats.mu.Unlock()

    m.realtimeStats.ordersPerHour[hour]++
    m.realtimeStats.revenuePerHour[hour] += order.Amount
}

func (m *BusinessMonitor) calculateConversionRate(segment string) {
    m.realtimeStats.mu.RLock()
    defer m.realtimeStats.mu.RUnlock()

    visits := m.getVisitCount(segment)
    conversions := m.realtimeStats.conversions[segment]

    if visits > 0 {
        rate := float64(conversions) / float64(visits)
        m.conversionRate.WithLabelValues(segment).Set(rate)
    }
}

func (m *BusinessMonitor) getVisitCount(segment string) int {
    // 从数据库或缓存获取访问次数
    return 1000 // 示例值
}

func (m *BusinessMonitor) GetHourlyStats() map[string]interface{} {
    m.realtimeStats.mu.RLock()
    defer m.realtimeStats.mu.RUnlock()

    currentHour := time.Now().Format("2006-01-02-15")

    return map[string]interface{}{
        "current_hour_orders":    m.realtimeStats.ordersPerHour[currentHour],
        "current_hour_revenue":   m.realtimeStats.revenuePerHour[currentHour],
        "active_users":           m.realtimeStats.activeUsers,
        "conversions":            m.realtimeStats.conversions,
    }
}
```

## 📋 检查清单

- [ ] 掌握Prometheus指标收集
- [ ] 学会OpenTelemetry集成
- [ ] 理解结构化日志记录
- [ ] 掌握分布式追踪
- [ ] 学会性能分析工具
- [ ] 理解告警和通知
- [ ] 掌握业务监控
- [ ] 学会故障诊断

## 🚀 下一步

掌握监控和可观测性后，你可以继续学习：
- **AIOps**: 智能运维和自动化
- **混沌工程**: 系统韧性测试
- **服务网格**: 高级可观测性
- **时序数据库**: 高性能监控数据存储

---

**学习提示**: Go应用的监控体系是其性能和稳定性的重要保障。完善的监控可以帮助你快速发现问题、优化性能、提升用户体验。

*最后更新: 2025年9月*