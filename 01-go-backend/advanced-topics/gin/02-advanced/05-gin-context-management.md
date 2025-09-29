# Gin上下文管理与数据流控制

## 📚 目录

- [Context基础概念](#context基础概念)
- [Context生命周期](#context生命周期)
- [数据存储与传递](#数据存储与传递)
- [请求上下文管理](#请求上下文管理)
- [响应控制](#响应控制)
- [错误处理](#错误处理)
- [并发安全](#并发安全)
- [性能优化](#性能优化)
- [最佳实践](#最佳实践)
- [实战案例](#实战案例)

## 🚀 Context基础概念

### Gin Context概述

Gin Context是Gin框架中最重要的组件之一，它在整个HTTP请求处理过程中充当核心角色。每个请求都会创建一个独立的Context实例，负责管理请求生命周期中的所有数据和操作。

### Context基本结构

```go
// gin.Context的核心结构
type Context struct {
    writermem responseWriterMem
    Request   *http.Request
    Writer    ResponseWriter

    // 请求参数
    Params   Params
    handlers HandlersChain
    index    int8
    fullPath string

    // 引擎实例
    engine *Engine
    params *Params

    // 数据存储
    Keys map[string]interface{}

    // 错误管理
    Errors errorMsgs

    // 元数据
    Accepted []string
}
```

### Context基本用法

```go
package main

import (
    "github.com/gin-gonic/gin"
    "net/http"
)

func main() {
    r := gin.Default()

    // 基本Context使用
    r.GET("/basic", func(c *gin.Context) {
        // 获取请求信息
        method := c.Request.Method
        path := c.FullPath()
        userAgent := c.GetHeader("User-Agent")

        // 设置响应
        c.JSON(http.StatusOK, gin.H{
            "method": method,
            "path":   path,
            "ua":     userAgent,
        })
    })

    // 参数获取
    r.GET("/user/:id", func(c *gin.Context) {
        // 路径参数
        userID := c.Param("id")

        // 查询参数
        name := c.Query("name")
        age := c.DefaultQuery("age", "18")

        // 表单参数
        email := c.PostForm("email")

        c.JSON(http.StatusOK, gin.H{
            "user_id": userID,
            "name":    name,
            "age":     age,
            "email":   email,
        })
    })

    r.Run(":8080")
}
```

## 🔄 Context生命周期

### 请求生命周期管理

```go
// Context生命周期管理器
type ContextLifecycleManager struct {
    pool sync.Pool
    stats *LifecycleStats
}

type LifecycleStats struct {
    TotalContexts    int64
    ActiveContexts  int64
    RecycledContexts int64
    mutex           sync.RWMutex
}

func NewContextLifecycleManager() *ContextLifecycleManager {
    return &ContextLifecycleManager{
        pool: sync.Pool{
            New: func() interface{} {
                return &gin.Context{}
            },
        },
        stats: &LifecycleStats{},
    }
}

func (m *ContextLifecycleManager) Acquire() *gin.Context {
    m.stats.mutex.Lock()
    m.stats.TotalContexts++
    m.stats.ActiveContexts++
    m.stats.mutex.Unlock()

    return m.pool.Get().(*gin.Context)
}

func (m *ContextLifecycleManager) Release(c *gin.Context) {
    m.stats.mutex.Lock()
    m.stats.ActiveContexts--
    m.stats.RecycledContexts++
    m.stats.mutex.Unlock()

    // 重置Context状态
    m.resetContext(c)
    m.pool.Put(c)
}

func (m *ContextLifecycleManager) resetContext(c *gin.Context) {
    // 重置Context状态
    c.index = -1
    c.handlers = nil
    c.Keys = nil
    c.Errors = nil
    c.Accepted = nil
    c.Params = c.Params[:0]
}

func (m *ContextLifecycleManager) GetStats() LifecycleStats {
    m.stats.mutex.RLock()
    defer m.stats.mutex.RUnlock()
    return *m.stats
}
```

### 请求生命周期钩子

```go
// 生命周期钩子管理器
type LifecycleHooks struct {
    beforeHooks []LifecycleHook
    afterHooks  []LifecycleHook
    errorHooks  []ErrorHook
}

type LifecycleHook func(*gin.Context)
type ErrorHook func(*gin.Context, error)

func NewLifecycleHooks() *LifecycleHooks {
    return &LifecycleHooks{
        beforeHooks: make([]LifecycleHook, 0),
        afterHooks:  make([]LifecycleHook, 0),
        errorHooks:  make([]ErrorHook, 0),
    }
}

func (h *LifecycleHooks) BeforeRequest(hook LifecycleHook) {
    h.beforeHooks = append(h.beforeHooks, hook)
}

func (h *LifecycleHooks) AfterRequest(hook LifecycleHook) {
    h.afterHooks = append(h.afterHooks, hook)
}

func (h *LifecycleHooks) OnError(hook ErrorHook) {
    h.errorHooks = append(h.errorHooks, hook)
}

func (h *LifecycleHooks) ExecuteBefore(c *gin.Context) {
    for _, hook := range h.beforeHooks {
        hook(c)
        if c.IsAborted() {
            break
        }
    }
}

func (h *LifecycleHooks) ExecuteAfter(c *gin.Context) {
    for _, hook := range h.afterHooks {
        hook(c)
    }
}

func (h *LifecycleHooks) ExecuteError(c *gin.Context, err error) {
    for _, hook := range h.errorHooks {
        hook(c, err)
    }
}

// 使用生命周期钩子的中间件
func LifecycleMiddleware(hooks *LifecycleHooks) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 请求前钩子
        hooks.ExecuteBefore(c)

        // 执行请求处理
        c.Next()

        // 请求后钩子
        hooks.ExecuteAfter(c)

        // 错误处理
        if len(c.Errors) > 0 {
            for _, err := range c.Errors {
                hooks.ExecuteError(c, err)
            }
        }
    }
}
```

## 💾 数据存储与传递

### Context数据管理

```go
// Context数据管理器
type ContextDataManager struct {
    validators map[string]DataValidator
    converters map[string]DataConverter
}

type DataValidator interface {
    Validate(interface{}) error
}

type DataConverter interface {
    Convert(interface{}) (interface{}, error)
}

func NewContextDataManager() *ContextDataManager {
    return &ContextDataManager{
        validators: make(map[string]DataValidator),
        converters: make(map[string]DataConverter),
    }
}

func (m *ContextDataManager) SetValidator(key string, validator DataValidator) {
    m.validators[key] = validator
}

func (m *ContextDataManager) SetConverter(key string, converter DataConverter) {
    m.converters[key] = converter
}

func (m *ContextDataManager) SetValidatedData(c *gin.Context, key string, value interface{}) error {
    if validator, exists := m.validators[key]; exists {
        if err := validator.Validate(value); err != nil {
            return err
        }
    }

    if converter, exists := m.converters[key]; exists {
        converted, err := converter.Convert(value)
        if err != nil {
            return err
        }
        c.Set(key, converted)
    } else {
        c.Set(key, value)
    }

    return nil
}

func (m *ContextDataManager) GetValidatedData(c *gin.Context, key string) (interface{}, error) {
    value, exists := c.Get(key)
    if !exists {
        return nil, fmt.Errorf("key '%s' not found in context", key)
    }

    if validator, exists := m.validators[key]; exists {
        if err := validator.Validate(value); err != nil {
            return nil, err
        }
    }

    return value, nil
}

// 数据验证器示例
type StringValidator struct {
    MinLength int
    MaxLength int
    Required  bool
}

func (v *StringValidator) Validate(value interface{}) error {
    str, ok := value.(string)
    if !ok {
        return fmt.Errorf("value must be a string")
    }

    if v.Required && str == "" {
        return fmt.Errorf("value is required")
    }

    if v.MinLength > 0 && len(str) < v.MinLength {
        return fmt.Errorf("value must be at least %d characters", v.MinLength)
    }

    if v.MaxLength > 0 && len(str) > v.MaxLength {
        return fmt.Errorf("value must be at most %d characters", v.MaxLength)
    }

    return nil
}

// 数据转换器示例
type StringToIntConverter struct{}

func (c *StringToIntConverter) Convert(value interface{}) (interface{}, error) {
    switch v := value.(type) {
    case string:
        return strconv.Atoi(v)
    case int:
        return v, nil
    default:
        return nil, fmt.Errorf("cannot convert %T to int", value)
    }
}
```

### 高级数据传递模式

```go
// 请求数据传递器
type RequestContextCarrier struct {
    data map[string]interface{}
    metadata map[string]interface{}
    mutex sync.RWMutex
}

func NewRequestContextCarrier() *RequestContextCarrier {
    return &RequestContextCarrier{
        data:     make(map[string]interface{}),
        metadata: make(map[string]interface{}),
    }
}

func (c *RequestContextCarrier) Set(key string, value interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.data[key] = value
}

func (c *RequestContextCarrier) Get(key string) (interface{}, bool) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    value, exists := c.data[key]
    return value, exists
}

func (c *RequestContextCarrier) SetMetadata(key string, value interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.metadata[key] = value
}

func (c *RequestContextCarrier) GetMetadata(key string) (interface{}, bool) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    value, exists := c.metadata[key]
    return value, exists
}

func (c *RequestContextCarrier) Copy() *RequestContextCarrier {
    c.mutex.RLock()
    defer c.mutex.RUnlock()

    copy := NewRequestContextCarrier()
    for k, v := range c.data {
        copy.data[k] = v
    }
    for k, v := range c.metadata {
        copy.metadata[k] = v
    }
    return copy
}

// 上下文链管理
type ContextChain struct {
    contexts []*gin.Context
    current  int
    mutex    sync.RWMutex
}

func NewContextChain() *ContextChain {
    return &ContextChain{
        contexts: make([]*gin.Context, 0),
        current:  -1,
    }
}

func (c *ContextChain) Push(ctx *gin.Context) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.contexts = append(c.contexts, ctx)
    c.current = len(c.contexts) - 1
}

func (c *ContextChain) Pop() *gin.Context {
    c.mutex.Lock()
    defer c.mutex.Unlock()

    if c.current < 0 {
        return nil
    }

    ctx := c.contexts[c.current]
    c.contexts = c.contexts[:c.current]
    c.current--
    return ctx
}

func (c *ContextChain) Current() *gin.Context {
    c.mutex.RLock()
    defer c.mutex.RUnlock()

    if c.current < 0 || c.current >= len(c.contexts) {
        return nil
    }
    return c.contexts[c.current]
}

func (c *ContextChain) GetParent() *gin.Context {
    c.mutex.RLock()
    defer c.mutex.RUnlock()

    if c.current <= 0 {
        return nil
    }
    return c.contexts[c.current-1]
}

// 上下文数据传播
type ContextPropagator struct {
    keysToPropagate []string
    metadataKeys   []string
}

func NewContextPropagator(keys, metadataKeys []string) *ContextPropagator {
    return &ContextPropagator{
        keysToPropagate: keys,
        metadataKeys:   metadataKeys,
    }
}

func (p *ContextPropagator) Propagate(from *gin.Context, to *gin.Context) {
    // 传播指定键的数据
    for _, key := range p.keysToPropagate {
        if value, exists := from.Get(key); exists {
            to.Set(key, value)
        }
    }

    // 传播元数据
    for _, key := range p.metadataKeys {
        if value, exists := from.Get("meta_" + key); exists {
            to.Set("meta_" + key, value)
        }
    }
}
```

## 🌐 请求上下文管理

### 请求上下文构建器

```go
// 请求上下文构建器
type RequestContextBuilder struct {
    context *gin.Context
    data    map[string]interface{}
    metadata map[string]interface{}
    validators map[string]DataValidator
}

func NewRequestContextBuilder(c *gin.Context) *RequestContextBuilder {
    return &RequestContextBuilder{
        context: c,
        data:    make(map[string]interface{}),
        metadata: make(map[string]interface{}),
        validators: make(map[string]DataValidator),
    }
}

func (b *RequestContextBuilder) Set(key string, value interface{}) *RequestContextBuilder {
    b.data[key] = value
    return b
}

func (b *RequestContextBuilder) SetMetadata(key string, value interface{}) *RequestContextBuilder {
    b.metadata[key] = value
    return b
}

func (b *RequestContextBuilder) AddValidator(key string, validator DataValidator) *RequestContextBuilder {
    b.validators[key] = validator
    return b
}

func (b *RequestContextBuilder) Validate() error {
    for key, validator := range b.validators {
        if value, exists := b.data[key]; exists {
            if err := validator.Validate(value); err != nil {
                return fmt.Errorf("validation failed for key '%s': %v", key, err)
            }
        }
    }
    return nil
}

func (b *RequestContextBuilder) Build() error {
    if err := b.Validate(); err != nil {
        return err
    }

    // 设置数据到Context
    for key, value := range b.data {
        b.context.Set(key, value)
    }

    // 设置元数据
    for key, value := range b.metadata {
        b.context.Set("meta_"+key, value)
    }

    return nil
}

// 请求上下文解析器
type RequestContextParser struct {
    parsers map[string]DataParser
}

type DataParser interface {
    Parse(*gin.Context) (interface{}, error)
}

func NewRequestContextParser() *RequestContextParser {
    return &RequestContextParser{
        parsers: make(map[string]DataParser),
    }
}

func (p *RequestContextParser) AddParser(key string, parser DataParser) {
    p.parsers[key] = parser
}

func (p *RequestContextParser) ParseContext(c *gin.Context) error {
    for key, parser := range p.parsers {
        value, err := parser.Parse(c)
        if err != nil {
            return fmt.Errorf("failed to parse '%s': %v", key, err)
        }
        c.Set(key, value)
    }
    return nil
}

// 数据解析器示例
type JSONBodyParser struct {
    Target interface{}
}

func (p *JSONBodyParser) Parse(c *gin.Context) (interface{}, error) {
    if err := c.ShouldBindJSON(p.Target); err != nil {
        return nil, err
    }
    return p.Target, nil
}

type HeaderParser struct {
    HeaderName string
    Required   bool
}

func (p *HeaderParser) Parse(c *gin.Context) (interface{}, error) {
    value := c.GetHeader(p.HeaderName)
    if p.Required && value == "" {
        return nil, fmt.Errorf("header '%s' is required", p.HeaderName)
    }
    return value, nil
}
```

### 会话管理

```go
// 会话管理器
type SessionManager struct {
    store      SessionStore
    cookieName string
    options    *SessionOptions
}

type SessionStore interface {
    Get(sessionID string) (map[string]interface{}, error)
    Set(sessionID string, data map[string]interface{}) error
    Delete(sessionID string) error
}

type SessionOptions struct {
    Path     string
    Domain   string
    MaxAge   int
    Secure   bool
    HttpOnly bool
    SameSite http.SameSite
}

func NewSessionManager(store SessionStore, cookieName string, options *SessionOptions) *SessionManager {
    return &SessionManager{
        store:      store,
        cookieName: cookieName,
        options:    options,
    }
}

func (m *SessionManager) StartSession(c *gin.Context) (map[string]interface{}, error) {
    // 获取或创建会话ID
    sessionID := m.getSessionID(c)
    if sessionID == "" {
        sessionID = m.generateSessionID()
        m.setSessionID(c, sessionID)
    }

    // 获取会话数据
    data, err := m.store.Get(sessionID)
    if err != nil {
        return nil, err
    }

    if data == nil {
        data = make(map[string]interface{})
    }

    // 将会话数据存储到Context
    c.Set("session", data)
    c.Set("session_id", sessionID)

    return data, nil
}

func (m *SessionManager) GetSession(c *gin.Context) (map[string]interface{}, bool) {
    session, exists := c.Get("session")
    if !exists {
        return nil, false
    }
    return session.(map[string]interface{}), true
}

func (m *SessionManager) SaveSession(c *gin.Context) error {
    sessionID, exists := c.Get("session_id")
    if !exists {
        return fmt.Errorf("no active session")
    }

    session, exists := c.Get("session")
    if !exists {
        return fmt.Errorf("no session data")
    }

    return m.store.Set(sessionID.(string), session.(map[string]interface{}))
}

func (m *SessionManager) DestroySession(c *gin.Context) error {
    sessionID, exists := c.Get("session_id")
    if !exists {
        return nil
    }

    if err := m.store.Delete(sessionID.(string)); err != nil {
        return err
    }

    m.clearSessionCookie(c)
    c.Set("session", nil)
    c.Set("session_id", nil)

    return nil
}

func (m *SessionManager) getSessionID(c *gin.Context) string {
    cookie, err := c.Cookie(m.cookieName)
    if err != nil {
        return ""
    }
    return cookie
}

func (m *SessionManager) setSessionID(c *gin.Context, sessionID string) {
    c.SetCookie(m.cookieName, sessionID, m.options.MaxAge, m.options.Path,
        m.options.Domain, m.options.Secure, m.options.HttpOnly)
}

func (m *SessionManager) clearSessionCookie(c *gin.Context) {
    c.SetCookie(m.cookieName, "", -1, m.options.Path,
        m.options.Domain, m.options.Secure, m.options.HttpOnly)
}

func (m *SessionManager) generateSessionID() string {
    bytes := make([]byte, 32)
    rand.Read(bytes)
    return hex.EncodeToString(bytes)
}

// 会话中间件
func SessionMiddleware(manager *SessionManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 启动会话
        session, err := manager.StartSession(c)
        if err != nil {
            c.AbortWithStatusJSON(500, gin.H{"error": "Failed to start session"})
            return
        }

        // 执行请求处理
        c.Next()

        // 保存会话
        if err := manager.SaveSession(c); err != nil {
            c.Error(fmt.Errorf("Failed to save session: %v", err))
        }
    }
}
```

## 📤 响应控制

### 响应管理器

```go
// 响应管理器
type ResponseManager struct {
    formatters map[string]ResponseFormatter
    encoders   map[string]ResponseEncoder
}

type ResponseFormatter interface {
    Format(*gin.Context, interface{}) (interface{}, error)
}

type ResponseEncoder interface {
    Encode(*gin.Context, interface{}) error
}

func NewResponseManager() *ResponseManager {
    return &ResponseManager{
        formatters: make(map[string]ResponseFormatter),
        encoders:   make(map[string]ResponseEncoder),
    }
}

func (m *ResponseManager) AddFormatter(contentType string, formatter ResponseFormatter) {
    m.formatters[contentType] = formatter
}

func (m *ResponseManager) AddEncoder(contentType string, encoder ResponseEncoder) {
    m.encoders[contentType] = encoder
}

func (m *ResponseManager) Respond(c *gin.Context, data interface{}, statusCode int) error {
    // 确定内容类型
    contentType := c.NegotiateFormat(m.getSupportedContentTypes())
    if contentType == "" {
        contentType = "application/json"
    }

    // 格式化数据
    var formattedData interface{}
    if formatter, exists := m.formatters[contentType]; exists {
        var err error
        formattedData, err = formatter.Format(c, data)
        if err != nil {
            return err
        }
    } else {
        formattedData = data
    }

    // 编码响应
    if encoder, exists := m.encoders[contentType]; exists {
        if err := encoder.Encode(c, formattedData); err != nil {
            return err
        }
    } else {
        c.JSON(statusCode, formattedData)
    }

    return nil
}

func (m *ResponseManager) getSupportedContentTypes() []string {
    types := make([]string, 0, len(m.encoders))
    for contentType := range m.encoders {
        types = append(types, contentType)
    }
    return types
}

// 响应格式化器示例
type APIResponseFormatter struct{}

func (f *APIResponseFormatter) Format(c *gin.Context, data interface{}) (interface{}, error) {
    return gin.H{
        "success": true,
        "data":    data,
        "meta": gin.H{
            "timestamp": time.Now().Unix(),
            "request_id": c.GetString("request_id"),
        },
    }, nil
}

// 响应编码器示例
type JSONEncoder struct{}

func (e *JSONEncoder) Encode(c *gin.Context, data interface{}) error {
    c.JSON(http.StatusOK, data)
    return nil
}

type XMLEncoder struct{}

func (e *XMLEncoder) Encode(c *gin.Context, data interface{}) error {
    c.XML(http.StatusOK, data)
    return nil
}
```

### 流式响应

```go
// 流式响应管理器
type StreamResponseManager struct {
    bufferSize int
    timeout    time.Duration
}

func NewStreamResponseManager(bufferSize int, timeout time.Duration) *StreamResponseManager {
    return &StreamResponseManager{
        bufferSize: bufferSize,
        timeout:    timeout,
    }
}

func (m *StreamResponseManager) StreamJSON(c *gin.Context, dataChan <-chan interface{}) error {
    // 设置响应头
    c.Header("Content-Type", "application/json")
    c.Header("Transfer-Encoding", "chunked")

    // 创建流式写入器
    writer := c.Writer
    flusher, ok := writer.(http.Flusher)
    if !ok {
        return fmt.Errorf("streaming not supported")
    }

    // 写入JSON数组开始
    fmt.Fprint(writer, "[")

    first := true
    timeout := time.After(m.timeout)

    for {
        select {
        case data, ok := <-dataChan:
            if !ok {
                // 数据通道关闭，写入JSON数组结束
                fmt.Fprint(writer, "]")
                return nil
            }

            // 编码数据
            jsonData, err := json.Marshal(data)
            if err != nil {
                return err
            }

            // 写入逗号分隔符
            if !first {
                fmt.Fprint(writer, ",")
            }
            first = false

            // 写入数据
            if _, err := writer.Write(jsonData); err != nil {
                return err
            }

            // 刷新缓冲区
            flusher.Flush()

        case <-timeout:
            return fmt.Errorf("stream timeout")
        case <-c.Request.Context().Done():
            return fmt.Errorf("client disconnected")
        }
    }
}

func (m *StreamResponseManager) StreamSSE(c *gin.Context, eventChan <-chan SSEEvent) error {
    // 设置响应头
    c.Header("Content-Type", "text/event-stream")
    c.Header("Cache-Control", "no-cache")
    c.Header("Connection", "keep-alive")

    // 创建流式写入器
    writer := c.Writer
    flusher, ok := writer.(http.Flusher)
    if !ok {
        return fmt.Errorf("streaming not supported")
    }

    timeout := time.After(m.timeout)

    for {
        select {
        case event, ok := <-eventChan:
            if !ok {
                return nil
            }

            // 写入SSE事件
            if err := m.writeSSEEvent(writer, event); err != nil {
                return err
            }

            // 刷新缓冲区
            flusher.Flush()

        case <-timeout:
            return fmt.Errorf("stream timeout")
        case <-c.Request.Context().Done():
            return fmt.Errorf("client disconnected")
        }
    }
}

type SSEEvent struct {
    ID    string
    Event string
    Data  string
    Retry *int
}

func (m *StreamResponseManager) writeSSEEvent(writer io.Writer, event SSEEvent) error {
    // 写入事件ID
    if event.ID != "" {
        if _, err := fmt.Fprintf(writer, "id: %s\n", event.ID); err != nil {
            return err
        }
    }

    // 写入事件类型
    if event.Event != "" {
        if _, err := fmt.Fprintf(writer, "event: %s\n", event.Event); err != nil {
            return err
        }
    }

    // 写入数据
    if _, err := fmt.Fprintf(writer, "data: %s\n", event.Data); err != nil {
        return err
    }

    // 写入重试时间
    if event.Retry != nil {
        if _, err := fmt.Fprintf(writer, "retry: %d\n", *event.Retry); err != nil {
            return err
        }
    }

    // 写入空行表示事件结束
    if _, err := fmt.Fprint(writer, "\n"); err != nil {
        return err
    }

    return nil
}
```

## ⚠️ 错误处理

### 错误管理系统

```go
// 错误管理系统
type ErrorManager struct {
    handlers map[string]ErrorHandler
    logger   ErrorLogger
}

type ErrorHandler func(*gin.Context, error)
type ErrorLogger func(*gin.Context, error, map[string]interface{})

func NewErrorManager() *ErrorManager {
    return &ErrorManager{
        handlers: make(map[string]ErrorHandler),
        logger:   defaultErrorLogger,
    }
}

func (m *ErrorManager) RegisterHandler(errorType string, handler ErrorHandler) {
    m.handlers[errorType] = handler
}

func (m *ErrorManager) SetLogger(logger ErrorLogger) {
    m.logger = logger
}

func (m *ErrorManager) HandleError(c *gin.Context, err error) {
    // 获取错误类型
    errorType := getErrorType(err)

    // 记录错误
    m.logger(c, err, map[string]interface{}{
        "error_type": errorType,
        "request_id": c.GetString("request_id"),
        "path":       c.Request.URL.Path,
        "method":     c.Request.Method,
        "user_agent": c.Request.UserAgent(),
        "client_ip":  c.ClientIP(),
    })

    // 获取错误处理器
    handler, exists := m.handlers[errorType]
    if !exists {
        handler = m.defaultErrorHandler
    }

    // 处理错误
    handler(c, err)
}

func (m *ErrorManager) defaultErrorHandler(c *gin.Context, err error) {
    c.JSON(http.StatusInternalServerError, gin.H{
        "success": false,
        "error":   err.Error(),
        "request_id": c.GetString("request_id"),
    })
}

// 错误类型定义
type APIError struct {
    Type    string `json:"type"`
    Message string `json:"message"`
    Code    int    `json:"code"`
    Details map[string]interface{} `json:"details,omitempty"`
}

func (e *APIError) Error() string {
    return e.Message
}

type ValidationError struct {
    Field   string `json:"field"`
    Message string `json:"message"`
    Value   interface{} `json:"value"`
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on field '%s': %s", e.Field, e.Message)
}

type NotFoundError struct {
    Resource string `json:"resource"`
    ID       string `json:"id"`
}

func (e *NotFoundError) Error() string {
    return fmt.Sprintf("resource '%s' with id '%s' not found", e.Resource, e.ID)
}

type UnauthorizedError struct {
    Message string `json:"message"`
}

func (e *UnauthorizedError) Error() string {
    return e.Message
}

// 错误类型检测
func getErrorType(err error) string {
    switch err.(type) {
    case *APIError:
        return "api_error"
    case *ValidationError:
        return "validation_error"
    case *NotFoundError:
        return "not_found_error"
    case *UnauthorizedError:
        return "unauthorized_error"
    default:
        return "internal_error"
    }
}

// 默认错误记录器
func defaultErrorLogger(c *gin.Context, err error, metadata map[string]interface{}) {
    log.Printf("Error: %v, Metadata: %+v", err, metadata)
}

// 错误中间件
func ErrorMiddleware(manager *ErrorManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        defer func() {
            if err := recover(); err != nil {
                // 处理panic错误
                manager.HandleError(c, fmt.Errorf("panic: %v", err))
                c.Abort()
            }
        }()

        c.Next()

        // 处理请求过程中的错误
        if len(c.Errors) > 0 {
            for _, err := range c.Errors {
                manager.HandleError(c, err)
            }
            c.Abort()
        }
    }
}
```

### 错误响应格式化

```go
// 错误响应格式化器
type ErrorResponseFormatter struct {
    includeStackTrace bool
    includeDebugInfo  bool
}

func NewErrorResponseFormatter(includeStackTrace, includeDebugInfo bool) *ErrorResponseFormatter {
    return &ErrorResponseFormatter{
        includeStackTrace: includeStackTrace,
        includeDebugInfo:  includeDebugInfo,
    }
}

func (f *ErrorResponseFormatter) FormatError(c *gin.Context, err error) interface{} {
    response := gin.H{
        "success": false,
        "error": gin.H{
            "message": err.Error(),
            "type":    getErrorType(err),
            "request_id": c.GetString("request_id"),
        },
    }

    // 添加调试信息
    if f.includeDebugInfo {
        response["debug"] = gin.H{
            "path":       c.Request.URL.Path,
            "method":     c.Request.Method,
            "timestamp": time.Now().Unix(),
        }
    }

    // 添加堆栈跟踪
    if f.includeStackTrace {
        if stackTrace := getStackTrace(err); stackTrace != "" {
            response["error"].(gin.H)["stack_trace"] = stackTrace
        }
    }

    // 根据错误类型添加特定字段
    switch e := err.(type) {
    case *APIError:
        response["error"].(gin.H)["code"] = e.Code
        if e.Details != nil {
            response["error"].(gin.H)["details"] = e.Details
        }
    case *ValidationError:
        response["error"].(gin.H)["field"] = e.Field
        response["error"].(gin.H)["value"] = e.Value
    case *NotFoundError:
        response["error"].(gin.H)["resource"] = e.Resource
        response["error"].(gin.H)["id"] = e.ID
    }

    return response
}

func getStackTrace(err error) string {
    // 这里可以实现堆栈跟踪逻辑
    return ""
}

// 错误响应中间件
func ErrorResponseMiddleware(formatter *ErrorResponseFormatter) gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()

        if len(c.Errors) > 0 {
            // 只处理第一个错误
            err := c.Errors[0]
            response := formatter.FormatError(c, err)

            // 根据错误类型设置状态码
            var statusCode int
            switch err.Err.(type) {
            case *ValidationError:
                statusCode = http.StatusBadRequest
            case *NotFoundError:
                statusCode = http.StatusNotFound
            case *UnauthorizedError:
                statusCode = http.StatusUnauthorized
            default:
                statusCode = http.StatusInternalServerError
            }

            c.JSON(statusCode, response)
            c.Abort()
        }
    }
}
```

## 🔒 并发安全

### 并发安全Context管理

```go
// 并发安全Context包装器
type ConcurrentSafeContext struct {
    ctx     *gin.Context
    mutex   sync.RWMutex
    counters map[string]*AtomicCounter
}

type AtomicCounter struct {
    value int64
    mutex sync.Mutex
}

func NewAtomicCounter(initial int64) *AtomicCounter {
    return &AtomicCounter{
        value: initial,
    }
}

func (c *AtomicCounter) Increment() int64 {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.value++
    return c.value
}

func (c *AtomicCounter) Decrement() int64 {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.value--
    return c.value
}

func (c *AtomicCounter) Get() int64 {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    return c.value
}

func NewConcurrentSafeContext(ctx *gin.Context) *ConcurrentSafeContext {
    return &ConcurrentSafeContext{
        ctx:      ctx,
        counters: make(map[string]*AtomicCounter),
    }
}

func (c *ConcurrentSafeContext) Get(key string) (interface{}, bool) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    return c.ctx.Get(key)
}

func (c *ConcurrentSafeContext) Set(key string, value interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.ctx.Set(key, value)
}

func (c *ConcurrentSafeContext) IncrementCounter(key string) int64 {
    c.mutex.Lock()
    defer c.mutex.Unlock()

    if counter, exists := c.counters[key]; exists {
        return counter.Increment()
    }

    counter := NewAtomicCounter(0)
    c.counters[key] = counter
    return counter.Increment()
}

func (c *ConcurrentSafeContext) GetCounter(key string) int64 {
    c.mutex.RLock()
    defer c.mutex.RUnlock()

    if counter, exists := c.counters[key]; exists {
        return counter.Get()
    }
    return 0
}

// 并发安全的数据管理器
type ConcurrentDataManager struct {
    data     map[string]interface{}
    mutex    sync.RWMutex
    watchers map[string][]chan interface{}
}

func NewConcurrentDataManager() *ConcurrentDataManager {
    return &ConcurrentDataManager{
        data:     make(map[string]interface{}),
        watchers: make(map[string][]chan interface{}),
    }
}

func (m *ConcurrentDataManager) Set(key string, value interface{}) {
    m.mutex.Lock()
    defer m.mutex.Unlock()

    m.data[key] = value

    // 通知观察者
    if watchers, exists := m.watchers[key]; exists {
        for _, watcher := range watchers {
            select {
            case watcher <- value:
            default:
                // 如果通道已满，跳过
            }
        }
    }
}

func (m *ConcurrentDataManager) Get(key string) (interface{}, bool) {
    m.mutex.RLock()
    defer m.mutex.RUnlock()

    value, exists := m.data[key]
    return value, exists
}

func (m *ConcurrentDataManager) Watch(key string) chan interface{} {
    m.mutex.Lock()
    defer m.mutex.Unlock()

    watcher := make(chan interface{}, 1)
    m.watchers[key] = append(m.watchers[key], watcher)
    return watcher
}

func (m *ConcurrentDataManager) Unwatch(key string, watcher chan interface{}) {
    m.mutex.Lock()
    defer m.mutex.Unlock()

    if watchers, exists := m.watchers[key]; exists {
        for i, w := range watchers {
            if w == watcher {
                m.watchers[key] = append(watchers[:i], watchers[i+1:]...)
                break
            }
        }
    }
}
```

### 请求限制器

```go
// 请求限制器
type RequestLimiter struct {
    limiters map[string]*RateLimiter
    mutex    sync.RWMutex
}

type RateLimiter struct {
    tokens    int64
    capacity  int64
    rate      float64
    lastRefill time.Time
    mutex     sync.Mutex
}

func NewRequestLimiter() *RequestLimiter {
    return &RequestLimiter{
        limiters: make(map[string]*RateLimiter),
    }
}

func (l *RequestLimiter) GetLimiter(key string, capacity int64, rate float64) *RateLimiter {
    l.mutex.RLock()
    if limiter, exists := l.limiters[key]; exists {
        l.mutex.RUnlock()
        return limiter
    }
    l.mutex.RUnlock()

    l.mutex.Lock()
    defer l.mutex.Unlock()

    // 双重检查
    if limiter, exists := l.limiters[key]; exists {
        return limiter
    }

    limiter := &RateLimiter{
        tokens:    capacity,
        capacity:  capacity,
        rate:      rate,
        lastRefill: time.Now(),
    }
    l.limiters[key] = limiter
    return limiter
}

func (l *RateLimiter) Allow() bool {
    l.mutex.Lock()
    defer l.mutex.Unlock()

    // 补充令牌
    now := time.Now()
    elapsed := now.Sub(l.lastRefill).Seconds()
    tokensToAdd := int64(elapsed * l.rate)
    if tokensToAdd > 0 {
        l.tokens = min(l.tokens+tokensToAdd, l.capacity)
        l.lastRefill = now
    }

    // 检查是否有足够的令牌
    if l.tokens > 0 {
        l.tokens--
        return true
    }

    return false
}

func min(a, b int64) int64 {
    if a < b {
        return a
    }
    return b
}

// 请求限制中间件
func RateLimitMiddleware(limiter *RequestLimiter) gin.HandlerFunc {
    return func(c *gin.Context) {
        key := c.ClientIP()
        rateLimiter := limiter.GetLimiter(key, 100, 10) // 100个令牌，每秒补充10个

        if !rateLimiter.Allow() {
            c.AbortWithStatusJSON(429, gin.H{
                "error": "Rate limit exceeded",
                "retry_after": "1s",
            })
            return
        }

        c.Next()
    }
}
```

## ⚡ 性能优化

### Context池化优化

```go
// Context池化管理器
type ContextPool struct {
    pool    sync.Pool
    stats   *PoolStats
    maxIdle int
}

type PoolStats struct {
    Created    int64
    Acquired   int64
    Released   int64
    Active     int64
    mutex      sync.RWMutex
}

func NewContextPool(maxIdle int) *ContextPool {
    return &ContextPool{
        pool: sync.Pool{
            New: func() interface{} {
                ctx := &gin.Context{}
                return ctx
            },
        },
        stats: &PoolStats{},
        maxIdle: maxIdle,
    }
}

func (p *ContextPool) Acquire() *gin.Context {
    p.stats.mutex.Lock()
    p.stats.Acquired++
    p.stats.Active++
    p.stats.mutex.Unlock()

    ctx := p.pool.Get().(*gin.Context)
    p.stats.mutex.Lock()
    p.stats.Created++
    p.stats.mutex.Unlock()
    return ctx
}

func (p *ContextPool) Release(ctx *gin.Context) {
    p.stats.mutex.Lock()
    p.stats.Released++
    p.stats.Active--
    p.stats.mutex.Unlock()

    // 重置Context状态
    p.resetContext(ctx)
    p.pool.Put(ctx)
}

func (p *ContextPool) resetContext(ctx *gin.Context) {
    ctx.index = -1
    ctx.handlers = nil
    ctx.Keys = nil
    ctx.Errors = nil
    ctx.Accepted = nil
    ctx.Params = ctx.Params[:0]
}

func (p *ContextPool) GetStats() PoolStats {
    p.stats.mutex.RLock()
    defer p.stats.mutex.RUnlock()
    return *p.stats
}

// 内存优化Context
type OptimizedContext struct {
    *gin.Context
    bufferPool *BufferPool
    stringPool *StringPool
}

type BufferPool struct {
    pool sync.Pool
}

type StringPool struct {
    pool sync.Pool
}

func NewOptimizedContext(ctx *gin.Context) *OptimizedContext {
    return &OptimizedContext{
        Context:    ctx,
        bufferPool: &BufferPool{
            pool: sync.Pool{
                New: func() interface{} {
                    return make([]byte, 0, 1024)
                },
            },
        },
        stringPool: &StringPool{
            pool: sync.Pool{
                New: func() interface{} {
                    return make([]byte, 0, 256)
                },
            },
        },
    }
}

func (c *OptimizedContext) GetBuffer() []byte {
    return c.bufferPool.pool.Get().([]byte)
}

func (c *OptimizedContext) ReleaseBuffer(buf []byte) {
    c.bufferPool.pool.Put(buf[:0])
}

func (c *OptimizedContext) GetStringBuffer() []byte {
    return c.stringPool.pool.Get().([]byte)
}

func (c *OptimizedContext) ReleaseStringBuffer(buf []byte) {
    c.stringPool.pool.Put(buf[:0])
}
```

### 缓存优化

```go
// 上下文缓存管理器
type ContextCache struct {
    data     map[string]*CacheEntry
    mutex    sync.RWMutex
    ttl      time.Duration
    maxSize  int
}

type CacheEntry struct {
    value     interface{}
    expiresAt time.Time
    size      int
}

func NewContextCache(ttl time.Duration, maxSize int) *ContextCache {
    return &ContextCache{
        data:    make(map[string]*CacheEntry),
        ttl:     ttl,
        maxSize: maxSize,
    }
}

func (c *ContextCache) Set(key string, value interface{}, size int) {
    c.mutex.Lock()
    defer c.mutex.Unlock()

    // 清理过期条目
    c.cleanupExpired()

    // 检查大小限制
    if len(c.data) >= c.maxSize {
        c.evictLRU()
    }

    c.data[key] = &CacheEntry{
        value:     value,
        expiresAt: time.Now().Add(c.ttl),
        size:      size,
    }
}

func (c *ContextCache) Get(key string) (interface{}, bool) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()

    entry, exists := c.data[key]
    if !exists {
        return nil, false
    }

    if time.Now().After(entry.expiresAt) {
        return nil, false
    }

    return entry.value, true
}

func (c *ContextCache) Delete(key string) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    delete(c.data, key)
}

func (c *ContextCache) cleanupExpired() {
    now := time.Now()
    for key, entry := range c.data {
        if now.After(entry.expiresAt) {
            delete(c.data, key)
        }
    }
}

func (c *ContextCache) evictLRU() {
    // 简单的LRU淘汰策略
    // 实际实现中可以使用更复杂的数据结构
    if len(c.data) > 0 {
        for key := range c.data {
            delete(c.data, key)
            break
        }
    }
}

// 缓存中间件
func ContextCacheMiddleware(cache *ContextCache) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 将缓存管理器存储到Context中
        c.Set("context_cache", cache)

        c.Next()
    }
}
```

## 💡 最佳实践

### Context使用最佳实践

```go
// Context使用最佳实践示例
func setupBestPracticeRoutes(r *gin.Engine) {
    // 1. 请求ID跟踪
    r.Use(RequestIDMiddleware())

    // 2. 性能监控
    r.Use(PerformanceMiddleware())

    // 3. 错误处理
    r.Use(ErrorMiddleware())

    // 4. 请求日志
    r.Use(RequestLoggingMiddleware())

    // 5. 安全中间件
    r.Use(SecurityMiddleware())

    api := r.Group("/api")
    {
        // 6. API版本控制
        v1 := api.Group("/v1")
        {
            // 7. 认证中间件
            auth := v1.Group("")
            auth.Use(AuthenticationMiddleware())

            // 8. 限流中间件
            auth.Use(RateLimitMiddleware())

            // 9. 用户路由
            users := auth.Group("/users")
            {
                users.GET("", GetUsers)
                users.POST("", CreateUser)
                users.GET("/:id", GetUser)
                users.PUT("/:id", UpdateUser)
                users.DELETE("/:id", DeleteUser)
            }

            // 10. 产品路由
            products := auth.Group("/products")
            {
                products.GET("", GetProducts)
                products.POST("", CreateProduct)
                products.GET("/:id", GetProduct)
                products.PUT("/:id", UpdateProduct)
            }
        }
    }
}

// 最佳实践中间件实现
func RequestIDMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        requestID := generateRequestID()
        c.Set("request_id", requestID)
        c.Header("X-Request-ID", requestID)
        c.Next()
    }
}

func PerformanceMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        c.Set("start_time", start)

        c.Next()

        duration := time.Since(start)
        c.Set("response_time", duration)

        // 记录性能指标
        if duration > 500*time.Millisecond {
            log.Printf("Slow request: %s %s took %v", c.Request.Method, c.Request.URL.Path, duration)
        }
    }
}

func RequestLoggingMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path

        c.Next()

        duration := time.Since(start)
        status := c.Writer.Status()

        log.Printf("%s %s %d %v", c.Request.Method, path, status, duration)
    }
}

func SecurityMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 安全头
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-XSS-Protection", "1; mode=block")
        c.Header("Content-Security-Policy", "default-src 'self'")

        // 防止路径遍历
        if strings.Contains(c.Request.URL.Path, "..") {
            c.AbortWithStatusJSON(400, gin.H{"error": "Invalid path"})
            return
        }

        c.Next()
    }
}

func generateRequestID() string {
    bytes := make([]byte, 16)
    rand.Read(bytes)
    return hex.EncodeToString(bytes)
}
```

### 请求处理最佳实践

```go
// 请求处理最佳实践示例
func GetUser(c *gin.Context) {
    // 1. 参数验证
    userID := c.Param("id")
    if userID == "" {
        c.JSON(400, gin.H{"error": "User ID is required"})
        return
    }

    // 2. 数据获取
    user, err := getUserByID(userID)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            c.JSON(404, gin.H{"error": "User not found"})
            return
        }
        c.JSON(500, gin.H{"error": "Failed to get user"})
        return
    }

    // 3. 权限检查
    if !hasPermission(c, "user.read") {
        c.JSON(403, gin.H{"error": "Insufficient permissions"})
        return
    }

    // 4. 响应格式化
    response := gin.H{
        "success": true,
        "data":    user,
        "meta": gin.H{
            "request_id": c.GetString("request_id"),
            "response_time": c.GetString("response_time"),
        },
    }

    c.JSON(200, response)
}

func CreateUser(c *gin.Context) {
    // 1. 请求体解析
    var user CreateUserRequest
    if err := c.ShouldBindJSON(&user); err != nil {
        c.JSON(400, gin.H{"error": "Invalid request body"})
        return
    }

    // 2. 数据验证
    if err := validateUser(&user); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    // 3. 业务逻辑
    createdUser, err := createUser(&user)
    if err != nil {
        c.JSON(500, gin.H{"error": "Failed to create user"})
        return
    }

    // 4. 响应
    response := gin.H{
        "success": true,
        "data":    createdUser,
        "meta": gin.H{
            "request_id": c.GetString("request_id"),
            "response_time": c.GetString("response_time"),
        },
    }

    c.JSON(201, response)
}

// 数据验证函数
func validateUser(user *CreateUserRequest) error {
    if user.Name == "" {
        return fmt.Errorf("name is required")
    }
    if user.Email == "" {
        return fmt.Errorf("email is required")
    }
    if !isValidEmail(user.Email) {
        return fmt.Errorf("invalid email format")
    }
    if user.Age < 0 || user.Age > 150 {
        return fmt.Errorf("age must be between 0 and 150")
    }
    return nil
}

// 权限检查函数
func hasPermission(c *gin.Context, permission string) bool {
    // 从Context中获取用户权限
    permissions, exists := c.Get("permissions")
    if !exists {
        return false
    }

    userPermissions := permissions.([]string)
    for _, p := range userPermissions {
        if p == permission {
            return true
        }
    }
    return false
}

// 邮箱验证函数
func isValidEmail(email string) bool {
    emailRegex := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    return emailRegex.MatchString(email)
}
```

## 🎯 实战案例

### 完整的API服务器示例

```go
// 完整的API服务器Context管理
type APIServer struct {
    engine             *gin.Engine
    contextPool        *ContextPool
    lifecycleManager   *ContextLifecycleManager
    errorManager       *ErrorManager
    responseManager    *ResponseManager
    sessionManager     *SessionManager
    requestLimiter     *RequestLimiter
    contextCache       *ContextCache
    lifecycleHooks     *LifecycleHooks
    dataManager        *ContextDataManager
    streamManager      *StreamResponseManager
}

func NewAPIServer() *APIServer {
    // 创建Gin引擎
    engine := gin.New()

    // 初始化各个组件
    contextPool := NewContextPool(100)
    lifecycleManager := NewContextLifecycleManager()
    errorManager := NewErrorManager()
    responseManager := NewResponseManager()
    sessionManager := NewSessionManager(NewMemorySessionStore(), "session_id", &SessionOptions{
        Path:     "/",
        MaxAge:   3600,
        Secure:   true,
        HttpOnly: true,
    })
    requestLimiter := NewRequestLimiter()
    contextCache := NewContextCache(5*time.Minute, 1000)
    lifecycleHooks := NewLifecycleHooks()
    dataManager := NewContextDataManager()
    streamManager := NewStreamResponseManager(1024, 30*time.Second)

    server := &APIServer{
        engine:           engine,
        contextPool:      contextPool,
        lifecycleManager:  lifecycleManager,
        errorManager:     errorManager,
        responseManager:  responseManager,
        sessionManager:   sessionManager,
        requestLimiter:   requestLimiter,
        contextCache:     contextCache,
        lifecycleHooks:   lifecycleHooks,
        dataManager:      dataManager,
        streamManager:    streamManager,
    }

    // 配置服务器
    server.setupServer()

    return server
}

func (s *APIServer) setupServer() {
    // 注册响应编码器
    s.responseManager.AddEncoder("application/json", &JSONEncoder{})
    s.responseManager.AddEncoder("application/xml", &XMLEncoder{})

    // 注册响应格式化器
    s.responseManager.AddFormatter("application/json", &APIResponseFormatter{})

    // 注册错误处理器
    s.errorManager.RegisterHandler("validation_error", s.handleValidationError)
    s.errorManager.RegisterHandler("not_found_error", s.handleNotFoundError)
    s.errorManager.RegisterHandler("unauthorized_error", s.handleUnauthorizedError)

    // 注册数据验证器
    s.dataManager.SetValidator("email", &StringValidator{
        Required:  true,
        MinLength: 5,
        MaxLength: 100,
    })

    // 注册数据转换器
    s.dataManager.SetConverter("age", &StringToIntConverter{})

    // 注册生命周期钩子
    s.lifecycleHooks.BeforeRequest(s.beforeRequestHook)
    s.lifecycleHooks.AfterRequest(s.afterRequestHook)
    s.lifecycleHooks.OnError(s.errorHook)

    // 设置中间件
    s.setupMiddleware()

    // 设置路由
    s.setupRoutes()
}

func (s *APIServer) setupMiddleware() {
    s.engine.Use(gin.Logger())
    s.engine.Use(gin.Recovery())

    // 生命周期中间件
    s.engine.Use(LifecycleMiddleware(s.lifecycleHooks))

    // 请求ID中间件
    s.engine.Use(RequestIDMiddleware())

    // 性能监控中间件
    s.engine.Use(PerformanceMiddleware())

    // 限流中间件
    s.engine.Use(RateLimitMiddleware(s.requestLimiter))

    // 会话中间件
    s.engine.Use(SessionMiddleware(s.sessionManager))

    // 上下文缓存中间件
    s.engine.Use(ContextCacheMiddleware(s.contextCache))

    // 错误处理中间件
    s.engine.Use(ErrorMiddleware(s.errorManager))

    // 安全中间件
    s.engine.Use(SecurityMiddleware())

    // 认证中间件
    s.engine.Use(AuthenticationMiddleware())
}

func (s *APIServer) setupRoutes() {
    // 健康检查
    s.engine.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{"status": "healthy"})
    })

    // API路由
    api := s.engine.Group("/api/v1")
    {
        // 公共路由
        api.POST("/auth/login", s.login)
        api.POST("/auth/register", s.register)
        api.POST("/auth/logout", s.logout)

        // 需要认证的路由
        auth := api.Group("")
        auth.Use(AuthorizationMiddleware())
        {
            // 用户管理
            users := auth.Group("/users")
            {
                users.GET("", s.getUsers)
                users.POST("", s.createUser)
                users.GET("/:id", s.getUser)
                users.PUT("/:id", s.updateUser)
                users.DELETE("/:id", s.deleteUser)
            }

            // 产品管理
            products := auth.Group("/products")
            {
                products.GET("", s.getProducts)
                products.POST("", s.createProduct)
                products.GET("/:id", s.getProduct)
                products.PUT("/:id", s.updateProduct)
                products.DELETE("/:id", s.deleteProduct)
            }

            // 流式响应
            sse := auth.Group("/sse")
            {
                sse.GET("/events", s.handleSSE)
                sse.GET("/data", s.handleStreamData)
            }
        }
    }
}

// 错误处理器
func (s *APIServer) handleValidationError(c *gin.Context, err error) {
    c.JSON(400, gin.H{
        "success": false,
        "error": gin.H{
            "type":    "validation_error",
            "message": err.Error(),
        },
    })
}

func (s *APIServer) handleNotFoundError(c *gin.Context, err error) {
    c.JSON(404, gin.H{
        "success": false,
        "error": gin.H{
            "type":    "not_found_error",
            "message": err.Error(),
        },
    })
}

func (s *APIServer) handleUnauthorizedError(c *gin.Context, err error) {
    c.JSON(401, gin.H{
        "success": false,
        "error": gin.H{
            "type":    "unauthorized_error",
            "message": err.Error(),
        },
    })
}

// 生命周期钩子
func (s *APIServer) beforeRequestHook(c *gin.Context) {
    // 记录请求开始时间
    c.Set("start_time", time.Now())

    // 生成请求ID
    requestID := generateRequestID()
    c.Set("request_id", requestID)
    c.Header("X-Request-ID", requestID)

    // 设置上下文缓存
    c.Set("context_cache", s.contextCache)
}

func (s *APIServer) afterRequestHook(c *gin.Context) {
    // 记录响应时间
    if startTime, exists := c.Get("start_time"); exists {
        duration := time.Since(startTime.(time.Time))
        c.Set("response_time", duration.String())
    }

    // 清理Context
    if ctx, ok := c.Get("optimized_context"); ok {
        if optimizedCtx, ok := ctx.(*OptimizedContext); ok {
            // 释放缓冲区
            s.contextPool.Release(optimizedCtx.Context)
        }
    }
}

func (s *APIServer) errorHook(c *gin.Context, err error) {
    // 记录错误
    log.Printf("Error in request %s: %v", c.GetString("request_id"), err)
}

// 流式响应处理器
func (s *APIServer) handleSSE(c *gin.Context) {
    eventChan := make(chan SSEEvent, 10)

    // 启动事件生成器
    go s.generateEvents(eventChan)

    // 流式传输SSE
    if err := s.streamManager.StreamSSE(c, eventChan); err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
    }
}

func (s *APIServer) handleStreamData(c *gin.Context) {
    dataChan := make(chan interface{}, 10)

    // 启动数据生成器
    go s.generateData(dataChan)

    // 流式传输JSON
    if err := s.streamManager.StreamJSON(c, dataChan); err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
    }
}

func (s *APIServer) generateEvents(eventChan chan<- SSEEvent) {
    defer close(eventChan)

    for i := 0; i < 10; i++ {
        event := SSEEvent{
            ID:    fmt.Sprintf("event-%d", i),
            Event: "update",
            Data:  fmt.Sprintf("Event data %d", i),
        }
        eventChan <- event
        time.Sleep(1 * time.Second)
    }
}

func (s *APIServer) generateData(dataChan chan<- interface{}) {
    defer close(dataChan)

    for i := 0; i < 10; i++ {
        data := gin.H{
            "id":        i,
            "timestamp": time.Now().Unix(),
            "data":      fmt.Sprintf("Sample data %d", i),
        }
        dataChan <- data
        time.Sleep(500 * time.Millisecond)
    }
}

func (s *APIServer) Run(addr string) error {
    return s.engine.Run(addr)
}
```

这个全面的Gin上下文管理与数据流控制文档涵盖了：

1. **Context基础概念**：基本结构、基本用法、生命周期
2. **Context生命周期**：生命周期管理、钩子函数、请求流程
3. **数据存储与传递**：数据管理、验证转换、并发安全
4. **请求上下文管理**：构建器、解析器、会话管理
5. **响应控制**：响应管理、流式响应、格式化
6. **错误处理**：错误管理系统、错误格式化、错误中间件
7. **并发安全**：并发包装器、原子计数器、请求限制
8. **性能优化**：Context池化、缓存优化、内存管理
9. **最佳实践**：中间件设计、请求处理、安全考虑
10. **实战案例**：完整API服务器、流式响应、错误处理

这个文档为Go开发者提供了Gin框架Context管理的完整指南，从基础概念到高级优化，帮助开发者构建高效、安全、可维护的Web应用。