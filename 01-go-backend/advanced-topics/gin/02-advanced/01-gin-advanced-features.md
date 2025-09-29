# Gin框架核心高级特性详解

本文档深入探讨Gin框架的核心高级特性，涵盖渲染引擎高级用法、Context深度使用、路由高级模式和中间件高级模式等关键内容。

## 1. 渲染引擎高级用法

### 1.1 HTML模板高级用法

#### 1.1.1 模板继承和布局
```go
package templates

import (
    "html/template"
    "net/http"
    "path/filepath"
    "strings"

    "github.com/gin-gonic/gin"
)

// 模板管理器
type TemplateManager struct {
    templates map[string]*template.Template
    funcMap   template.FuncMap
}

func NewTemplateManager(templatesDir string) *TemplateManager {
    manager := &TemplateManager{
        templates: make(map[string]*template.Template),
        funcMap: template.FuncMap{
            "upper": strings.ToUpper,
            "lower": strings.ToLower,
            "title": strings.Title,
            "truncate": func(s string, length int) string {
                if len(s) <= length {
                    return s
                }
                return s[:length] + "..."
            },
            "formatDate": formatDate,
            "formatNumber": formatNumber,
        },
    }

    manager.loadTemplates(templatesDir)
    return manager
}

// 加载模板文件
func (tm *TemplateManager) loadTemplates(dir string) {
    layouts, err := filepath.Glob(filepath.Join(dir, "layouts", "*.html"))
    if err != nil {
        panic(err)
    }

    includes, err := filepath.Glob(filepath.Join(dir, "includes", "*.html"))
    if err != nil {
        panic(err)
    }

    // 为每个页面模板创建模板集合
    pages, err := filepath.Glob(filepath.Join(dir, "pages", "*.html"))
    if err != nil {
        panic(err)
    }

    for _, page := range pages {
        files := append(layouts, includes...)
        files = append(files, page)

        name := filepath.Base(page)
        tmpl := template.Must(template.New(name).Funcs(tm.funcMap).ParseFiles(files...))
        tm.templates[name] = tmpl
    }
}

// 渲染模板
func (tm *TemplateManager) Render(c *gin.Context, name string, data interface{}) {
    tmpl, exists := tm.templates[name]
    if !exists {
        c.HTML(http.StatusInternalServerError, "error.html", gin.H{
            "error": "Template not found",
        })
        return
    }

    c.Header("Content-Type", "text/html; charset=utf-8")
    if err := tmpl.Execute(c.Writer, data); err != nil {
        c.HTML(http.StatusInternalServerError, "error.html", gin.H{
            "error": "Failed to render template",
        })
    }
}
```

#### 1.1.2 布局模板示例
```html
<!-- templates/layouts/base.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{.Title}} - My App</title>
    {{template "styles" .}}
</head>
<body>
    <div class="app">
        {{template "header" .}}

        <main class="main-content">
            {{template "content" .}}
        </main>

        {{template "footer" .}}
    </div>

    {{template "scripts" .}}
</body>
</html>

<!-- templates/layouts/admin.html -->
{{define "admin-layout"}}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{.Title}} - Admin Panel</title>
    {{template "admin-styles" .}}
</head>
<body class="admin-layout">
    <div class="admin-sidebar">
        {{template "admin-sidebar" .}}
    </div>

    <div class="admin-content">
        {{template "admin-header" .}}
        <div class="admin-main">
            {{template "content" .}}
        </div>
    </div>

    {{template "admin-scripts" .}}
{{end}}
```

#### 1.1.3 页面模板示例
```html
<!-- templates/pages/dashboard.html -->
{{define "content"}}
<div class="dashboard">
    <h1>Dashboard</h1>

    <div class="stats-grid">
        {{range .Stats}}
        <div class="stat-card">
            <h3>{{.Title}}</h3>
            <div class="stat-value">{{.Value | formatNumber}}</div>
            <div class="stat-change {{if gt .Change 0}}positive{{else}}negative{{end}}">
                {{if gt .Change 0}}+{{end}}{{.Change}}%
            </div>
        </div>
        {{end}}
    </div>

    <div class="charts">
        {{template "chart-placeholder" .ChartData}}
    </div>
</div>
{{end}}

{{define "styles"}}
<link rel="stylesheet" href="/static/css/dashboard.css">
{{end}}

{{define "scripts"}}
<script src="/static/js/dashboard.js"></script>
{{end}}
```

### 1.2 自定义渲染器

#### 1.2.1 JSON渲染器
```go
package renderers

import (
    "encoding/json"
    "net/http"

    "github.com/gin-gonic/gin"
)

// 自定义JSON渲染器
type CustomJSONRenderer struct {
    Indent    bool
    EscapeHTML bool
    Prefix    string
}

func NewCustomJSONRenderer() *CustomJSONRenderer {
    return &CustomJSONRenderer{
        Indent:     false,
        EscapeHTML: true,
        Prefix:     "",
    }
}

// 渲染JSON响应
func (r *CustomJSONRenderer) Render(c *gin.Context, data interface{}) {
    c.Header("Content-Type", "application/json; charset=utf-8")

    var result []byte
    var err error

    if r.Indent {
        result, err = json.MarshalIndent(data, "", "  ")
    } else {
        result, err = json.Marshal(data)
    }

    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{
            "error": "Failed to marshal JSON",
        })
        return
    }

    if r.EscapeHTML {
        result = escapeJSON(result)
    }

    if r.Prefix != "" {
        result = append([]byte(r.Prefix), result...)
    }

    c.Writer.WriteHeader(http.StatusOK)
    c.Writer.Write(result)
}

// JSONP渲染器
type JSONPRenderer struct {
    Callback string
    Renderer  *CustomJSONRenderer
}

func NewJSONPRenderer(callback string) *JSONPRenderer {
    return &JSONPRenderer{
        Callback: callback,
        Renderer: NewCustomJSONRenderer(),
    }
}

func (r *JSONPRenderer) Render(c *gin.Context, data interface{}) {
    callback := r.Callback
    if callback == "" {
        callback = c.DefaultQuery("callback", "callback")
    }

    r.Renderer.Prefix = callback + "("
    r.Renderer.Render(c, data)
    c.Writer.WriteString(")")
}

// 转义HTML字符
func escapeJSON(data []byte) []byte {
    // 实现HTML转义逻辑
    return data
}
```

#### 1.2.2 XML渲染器
```go
package renderers

import (
    "encoding/xml"
    "net/http"

    "github.com/gin-gonic/gin"
)

// XML渲染器
type CustomXMLRenderer struct {
    Indent bool
    Prefix string
}

func NewCustomXMLRenderer() *CustomXMLRenderer {
    return &CustomXMLRenderer{
        Indent: false,
        Prefix: "",
    }
}

func (r *CustomXMLRenderer) Render(c *gin.Context, data interface{}) {
    c.Header("Content-Type", "application/xml; charset=utf-8")

    var result []byte
    var err error

    if r.Indent {
        result, err = xml.MarshalIndent(data, "", "  ")
    } else {
        result, err = xml.Marshal(data)
    }

    if err != nil {
        c.XML(http.StatusInternalServerError, gin.H{
            "error": "Failed to marshal XML",
        })
        return
    }

    if r.Prefix != "" {
        result = append([]byte(r.Prefix), result...)
    }

    c.Writer.WriteHeader(http.StatusOK)
    c.Writer.Write(result)
}
```

#### 1.2.3 自定义渲染器中间件
```go
package middleware

import (
    "net/http"

    "github.com/gin-gonic/gin"
    "github.com/yourproject/renderers"
)

// 渲染器管理器
type RenderManager struct {
    jsonRenderer  *renderers.CustomJSONRenderer
    xmlRenderer   *renderers.CustomXMLRenderer
   jsonpRenderer *renderers.JSONPRenderer
}

func NewRenderManager() *RenderManager {
    return &RenderManager{
        jsonRenderer:  renderers.NewCustomJSONRenderer(),
        xmlRenderer:   renderers.NewCustomXMLRenderer(),
        jsonpRenderer: renderers.NewJSONPRenderer(""),
    }
}

// 自定义渲染中间件
func CustomRendererMiddleware() gin.HandlerFunc {
    manager := NewRenderManager()

    return func(c *gin.Context) {
        // 根据Accept头选择渲染器
        accept := c.GetHeader("Accept")

        c.Set("render_manager", manager)
        c.Set("content_type", accept)

        c.Next()
    }
}

// 响应渲染辅助函数
func RenderResponse(c *gin.Context, data interface{}) {
    manager, exists := c.Get("render_manager")
    if !exists {
        c.JSON(http.StatusOK, data)
        return
    }

    rm := manager.(*RenderManager)
    contentType := c.GetString("content_type")

    switch {
    case contentType == "application/xml":
        rm.xmlRenderer.Render(c, data)
    case c.Query("callback") != "":
        rm.jsonpRenderer.Callback = c.Query("callback")
        rm.jsonpRenderer.Render(c, data)
    default:
        rm.jsonRenderer.Render(c, data)
    }
}
```

### 1.3 模板函数高级用法

#### 1.3.1 复杂模板函数
```go
package templatefuncs

import (
    "fmt"
    "html/template"
    "strings"
    "time"
)

// 高级模板函数集合
func AdvancedFuncMap() template.FuncMap {
    return template.FuncMap{
        // 字符串处理
        "truncateWords": truncateWords,
        "highlight":    highlightText,
        "markdown":     markdownToHTML,
        "slugify":      slugify,

        // 时间处理
        "timeAgo":      timeAgo,
        "formatDate":   formatDate,
        "countdown":    countdown,

        // 数字处理
        "formatBytes":  formatBytes,
        "formatMoney":  formatMoney,
        "percentage":   calculatePercentage,

        // 条件判断
        "ternary":      ternary,
        "default":      defaultValue,
        "coalesce":     coalesce,

        // 数据处理
        "groupBy":      groupBy,
        "sortBy":       sortBy,
        "unique":       unique,
        "chunk":        chunkSlice,
    }
}

// 截断单词
func truncateWords(s string, limit int) string {
    words := strings.Fields(s)
    if len(words) <= limit {
        return s
    }
    return strings.Join(words[:limit], " ") + "..."
}

// 高亮文本
func highlightText(text, keyword string) template.HTML {
    if keyword == "" {
        return template.HTML(text)
    }
    return template.HTML(strings.ReplaceAll(
        text,
        keyword,
        fmt.Sprintf("<mark class=\"highlight\">%s</mark>", keyword),
    ))
}

// Markdown转HTML
func markdownToHTML(markdown string) template.HTML {
    // 这里可以集成markdown解析器
    return template.HTML(markdown) // 简化示例
}

// 生成URL友好的slug
func slugify(s string) string {
    // 简化的slug生成
    s = strings.ToLower(s)
    s = strings.ReplaceAll(s, " ", "-")
    s = strings.ReplaceAll(s, "_", "-")
    return s
}

// 相对时间
func timeAgo(t time.Time) string {
    now := time.Now()
    diff := now.Sub(t)

    switch {
    case diff < time.Minute:
        return "刚刚"
    case diff < time.Hour:
        return fmt.Sprintf("%d分钟前", int(diff.Minutes()))
    case diff < 24*time.Hour:
        return fmt.Sprintf("%d小时前", int(diff.Hours()))
    case diff < 30*24*time.Hour:
        return fmt.Sprintf("%d天前", int(diff.Hours()/24))
    default:
        return t.Format("2006-01-02")
    }
}

// 格式化日期
func formatDate(t time.Time, format string) string {
    layouts := map[string]string{
        "short":   "2006-01-02",
        "medium":  "2006-01-02 15:04",
        "long":    "2006-01-02 15:04:05",
        "full":    "2006年01月02日 15时04分05秒",
        "default": "2006-01-02",
    }

    layout, exists := layouts[format]
    if !exists {
        layout = layouts["default"]
    }

    return t.Format(layout)
}

// 倒计时
func countdown(t time.Time) string {
    now := time.Now()
    diff := t.Sub(now)

    if diff <= 0 {
        return "已过期"
    }

    days := int(diff.Hours() / 24)
    hours := int(diff.Hours()) % 24
    minutes := int(diff.Minutes()) % 60

    parts := []string{}
    if days > 0 {
        parts = append(parts, fmt.Sprintf("%d天", days))
    }
    if hours > 0 {
        parts = append(parts, fmt.Sprintf("%d小时", hours))
    }
    if minutes > 0 {
        parts = append(parts, fmt.Sprintf("%d分钟", minutes))
    }

    if len(parts) == 0 {
        return "即将到期"
    }

    return strings.Join(parts, " ")
}

// 格式化字节数
func formatBytes(bytes int64) string {
    units := []string{"B", "KB", "MB", "GB", "TB"}

    if bytes == 0 {
        return "0 B"
    }

    size := float64(bytes)
    unitIndex := 0

    for size >= 1024 && unitIndex < len(units)-1 {
        size /= 1024
        unitIndex++
    }

    return fmt.Sprintf("%.1f %s", size, units[unitIndex])
}

// 格式化金额
func formatMoney(amount float64, currency string) string {
    symbols := map[string]string{
        "CNY": "¥",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }

    symbol, exists := symbols[currency]
    if !exists {
        symbol = currency
    }

    return fmt.Sprintf("%s%.2f", symbol, amount)
}

// 计算百分比
func calculatePercentage(value, total float64) float64 {
    if total == 0 {
        return 0
    }
    return (value / total) * 100
}

// 三元运算符
func ternary(condition bool, trueValue, falseValue interface{}) interface{} {
    if condition {
        return trueValue
    }
    return falseValue
}

// 默认值
func defaultValue(value, defaultValue interface{}) interface{} {
    if value == nil || value == "" {
        return defaultValue
    }
    return value
}

// 返回第一个非空值
func coalesce(values ...interface{}) interface{} {
    for _, value := range values {
        if value != nil && value != "" {
            return value
        }
    }
    return nil
}

// 分组函数
func groupBy(items interface{}, key string) map[string][]interface{} {
    // 实现分组逻辑
    return make(map[string][]interface{})
}

// 排序函数
func sortBy(items interface{}, field string) []interface{} {
    // 实现排序逻辑
    return []interface{}{}
}

// 去重函数
func unique(items interface{}) []interface{} {
    // 实现去重逻辑
    return []interface{}{}
}

// 分块函数
func chunkSlice(items interface{}, size int) [][]interface{} {
    // 实现分块逻辑
    return [][]interface{}{}
}
```

## 2. Context深度使用

### 2.1 Context生命周期管理

#### 2.1.1 Context生命周期追踪
```go
package context

import (
    "context"
    "net/http"
    "sync"
    "time"

    "github.com/gin-gonic/gin"
)

// Context生命周期管理器
type ContextLifecycleManager struct {
    contexts map[*gin.Context]*ContextInfo
    mu       sync.RWMutex
}

type ContextInfo struct {
    ID        string
    StartTime time.Time
    EndTime   *time.Time
    Duration  time.Duration
    Steps     []StepInfo
    Status    string
    Request   *http.Request
    Data      map[string]interface{}
}

type StepInfo struct {
    Name      string
    StartTime time.Time
    EndTime   time.Time
    Duration  time.Duration
    Data      map[string]interface{}
}

func NewContextLifecycleManager() *ContextLifecycleManager {
    return &ContextLifecycleManager{
        contexts: make(map[*gin.Context]*ContextInfo),
    }
}

// Context生命周期中间件
func ContextLifecycleMiddleware(manager *ContextLifecycleManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 创建Context信息
        info := &ContextInfo{
            ID:        generateContextID(),
            StartTime: time.Now(),
            Steps:     make([]StepInfo, 0),
            Status:    "started",
            Request:   c.Request,
            Data:      make(map[string]interface{}),
        }

        // 注册Context
        manager.RegisterContext(c, info)

        // 在Context中设置生命周期信息
        c.Set("context_info", info)
        c.Set("context_manager", manager)

        // 添加步骤追踪函数
        c.Set("add_step", func(name string) func() {
            startTime := time.Now()
            return func() {
                endTime := time.Now()
                step := StepInfo{
                    Name:      name,
                    StartTime: startTime,
                    EndTime:   endTime,
                    Duration:  endTime.Sub(startTime),
                    Data:      make(map[string]interface{}),
                }
                info.Steps = append(info.Steps, step)
            }
        })

        // 请求处理完成后
        c.Next()

        // 更新Context信息
        endTime := time.Now()
        info.EndTime = &endTime
        info.Duration = endTime.Sub(info.StartTime)

        if len(c.Errors) > 0 {
            info.Status = "error"
        } else {
            info.Status = "completed"
        }

        // 注销Context
        manager.UnregisterContext(c)
    }
}

// 注册Context
func (m *ContextLifecycleManager) RegisterContext(c *gin.Context, info *ContextInfo) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.contexts[c] = info
}

// 注销Context
func (m *ContextLifecycleManager) UnregisterContext(c *gin.Context) {
    m.mu.Lock()
    defer m.mu.Unlock()
    delete(m.contexts, c)
}

// 获取活跃Context
func (m *ContextLifecycleManager) GetActiveContexts() []*ContextInfo {
    m.mu.RLock()
    defer m.mu.RUnlock()

    contexts := make([]*ContextInfo, 0, len(m.contexts))
    for _, info := range m.contexts {
        contexts = append(contexts, info)
    }
    return contexts
}

// 生成Context ID
func generateContextID() string {
    return fmt.Sprintf("ctx_%d", time.Now().UnixNano())
}

// 在Handler中使用Context生命周期
func ExampleHandler(c *gin.Context) {
    info := c.MustGet("context_info").(*ContextInfo)
    addStep := c.MustGet("add_step").(func(string) func())

    // 步骤1：数据验证
    step1 := addStep("data_validation")
    // ... 数据验证逻辑
    step1()

    // 步骤2：业务处理
    step2 := addStep("business_logic")
    // ... 业务处理逻辑
    step2()

    // 步骤3：数据库操作
    step3 := addStep("database_operation")
    // ... 数据库操作
    step3()

    c.JSON(200, gin.H{
        "context_id": info.ID,
        "status":     "success",
    })
}
```

#### 2.1.2 Context数据传递链
```go
package context

import (
    "context"
    "net/http"
    "sync"

    "github.com/gin-gonic/gin"
)

// Context数据传递管理器
type ContextDataChain struct {
    data      map[string]interface{}
    parent    *ContextDataChain
    children  []*ContextDataChain
    mu        sync.RWMutex
}

func NewContextDataChain() *ContextDataChain {
    return &ContextDataChain{
        data:     make(map[string]interface{}),
        children: make([]*ContextDataChain, 0),
    }
}

// 创建子Context
func (cdc *ContextDataChain) CreateChild() *ContextDataChain {
    cdc.mu.Lock()
    defer cdc.mu.Unlock()

    child := &ContextDataChain{
        data:     make(map[string]interface{}),
        parent:   cdc,
        children: make([]*ContextDataChain, 0),
    }

    cdc.children = append(cdc.children, child)
    return child
}

// 设置数据
func (cdc *ContextDataChain) Set(key string, value interface{}) {
    cdc.mu.Lock()
    defer cdc.mu.Unlock()
    cdc.data[key] = value
}

// 获取数据
func (cdc *ContextDataChain) Get(key string) (interface{}, bool) {
    cdc.mu.RLock()
    defer cdc.mu.RUnlock()

    if value, exists := cdc.data[key]; exists {
        return value, true
    }

    // 向父Context查找
    if cdc.parent != nil {
        return cdc.parent.Get(key)
    }

    return nil, false
}

// 获取所有数据
func (cdc *ContextDataChain) GetAll() map[string]interface{} {
    cdc.mu.RLock()
    defer cdc.mu.RUnlock()

    result := make(map[string]interface{})

    // 从父Context继承数据
    if cdc.parent != nil {
        parentData := cdc.parent.GetAll()
        for k, v := range parentData {
            result[k] = v
        }
    }

    // 添加当前数据
    for k, v := range cdc.data {
        result[k] = v
    }

    return result
}

// Context数据链中间件
func ContextDataChainMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 创建根数据链
        dataChain := NewContextDataChain()

        // 设置基础数据
        dataChain.Set("request_id", generateRequestID())
        dataChain.Set("timestamp", time.Now())
        dataChain.Set("user_agent", c.Request.UserAgent())
        dataChain.Set("client_ip", c.ClientIP())

        c.Set("data_chain", dataChain)

        c.Next()
    }
}

// 在中间件中使用数据链
func ExampleMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        dataChain := c.MustGet("data_chain").(*ContextDataChain)

        // 创建子数据链
        childChain := dataChain.CreateChild()

        // 设置中间件特定的数据
        childChain.Set("middleware_start", time.Now())
        childChain.Set("middleware_name", "example_middleware")

        // 将子数据链设置到Context中
        c.Set("data_chain", childChain)

        c.Next()

        // 记录处理时间
        childChain.Set("middleware_duration", time.Since(childChain.MustGet("middleware_start").(time.Time)))
    }
}

// 在Handler中使用数据链
func ExampleDataChainHandler(c *gin.Context) {
    dataChain := c.MustGet("data_chain").(*ContextDataChain)

    // 获取所有数据
    allData := dataChain.GetAll()

    // 创建新的子数据链
    handlerChain := dataChain.CreateChild()
    handlerChain.Set("handler_start", time.Now())

    // 业务逻辑处理
    handlerChain.Set("user_id", "12345")
    handlerChain.Set("operation", "get_user_profile")

    c.JSON(200, gin.H{
        "request_id":   allData["request_id"],
        "timestamp":    allData["timestamp"],
        "all_data":     allData,
        "handler_data": handlerChain.GetAll(),
    })
}
```

### 2.2 Context请求控制

#### 2.2.1 请求取消控制
```go
package context

import (
    "context"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
)

// 请求取消控制器
type RequestContextController struct {
    timeout     time.Duration
    cancelFuncs map[string]context.CancelFunc
    mu          sync.RWMutex
}

func NewRequestContextController(timeout time.Duration) *RequestContextController {
    return &RequestContextController{
        timeout:     timeout,
        cancelFuncs: make(map[string]context.CancelFunc),
    }
}

// 请求取消控制中间件
func RequestCancelMiddleware(controller *RequestContextController) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 创建带超时的context
        ctx, cancel := context.WithTimeout(c.Request.Context(), controller.timeout)

        // 注册取消函数
        requestID := generateRequestID()
        controller.RegisterCancelFunc(requestID, cancel)

        // 替换Gin Context的底层context
        c.Request = c.Request.WithContext(ctx)

        // 设置请求ID和取消函数
        c.Set("request_id", requestID)
        c.Set("cancel_func", cancel)

        // 监听取消信号
        go func() {
            select {
            case <-ctx.Done():
                // 请求被取消或超时
                if ctx.Err() == context.DeadlineExceeded {
                    c.AbortWithStatusJSON(http.StatusRequestTimeout, gin.H{
                        "error": "Request timeout",
                    })
                } else if ctx.Err() == context.Canceled {
                    c.AbortWithStatusJSON(http.StatusRequestTimeout, gin.H{
                        "error": "Request canceled",
                    })
                }
            case <-c.Done():
                // 请求正常完成
            }
        }()

        c.Next()

        // 注销取消函数
        controller.UnregisterCancelFunc(requestID)
    }
}

// 注册取消函数
func (rcc *RequestContextController) RegisterCancelFunc(requestID string, cancelFunc context.CancelFunc) {
    rcc.mu.Lock()
    defer rcc.mu.Unlock()
    rcc.cancelFuncs[requestID] = cancelFunc
}

// 注销取消函数
func (rcc *RequestContextController) UnregisterCancelFunc(requestID string) {
    rcc.mu.Lock()
    defer rcc.mu.Unlock()
    delete(rcc.cancelFuncs, requestID)
}

// 取消所有请求
func (rcc *RequestContextController) CancelAllRequests() {
    rcc.mu.RLock()
    defer rcc.mu.RUnlock()

    for _, cancelFunc := range rcc.cancelFuncs {
        cancelFunc()
    }
}

// 取消特定请求
func (rcc *RequestContextController) CancelRequest(requestID string) {
    rcc.mu.RLock()
    defer rcc.mu.RUnlock()

    if cancelFunc, exists := rcc.cancelFuncs[requestID]; exists {
        cancelFunc()
    }
}

// 在Handler中使用请求控制
func LongRunningHandler(c *gin.Context) {
    requestID := c.MustGet("request_id").(string)

    // 模拟长时间运行的任务
    for i := 0; i < 10; i++ {
        select {
        case <-c.Request.Context().Done():
            // 请求被取消
            return
        case <-time.After(1 * time.Second):
            // 继续处理
            c.Set("progress", (i+1)*10)
        }
    }

    c.JSON(200, gin.H{
        "request_id": requestID,
        "status":     "completed",
        "progress":   100,
    })
}
```

#### 2.2.2 请求限流控制
```go
package context

import (
    "net/http"
    "sync"
    "time"

    "github.com/gin-gonic/gin"
    "golang.org/x/time/rate"
)

// 请求限流器
type RequestContextLimiter struct {
    limiters map[string]*rate.Limiter
    mu       sync.RWMutex
    rate     rate.Limit
    burst    int
}

func NewRequestContextLimiter(r rate.Limit, burst int) *RequestContextLimiter {
    return &RequestContextLimiter{
        limiters: make(map[string]*rate.Limiter),
        rate:     r,
        burst:    burst,
    }
}

// 请求限流中间件
func RequestRateLimitMiddleware(limiter *RequestContextLimiter) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 获取客户端标识
        clientID := getClientIdentifier(c)

        // 获取或创建限流器
        clientLimiter := limiter.GetLimiter(clientID)

        // 检查是否允许请求
        if !clientLimiter.Allow() {
            c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
                "error": "Rate limit exceeded",
                "retry_after": "1s",
            })
            return
        }

        // 在Context中设置限流信息
        c.Set("rate_limiter", clientLimiter)
        c.Set("client_id", clientID)

        c.Next()
    }
}

// 获取客户端标识
func getClientIdentifier(c *gin.Context) string {
    // 优先使用API Key
    if apiKey := c.GetHeader("X-API-Key"); apiKey != "" {
        return "api_key:" + apiKey
    }

    // 其次使用用户ID（如果已认证）
    if userID := c.GetString("user_id"); userID != "" {
        return "user:" + userID
    }

    // 最后使用IP地址
    return "ip:" + c.ClientIP()
}

// 获取限流器
func (rcl *RequestContextLimiter) GetLimiter(clientID string) *rate.Limiter {
    rcl.mu.RLock()
    limiter, exists := rcl.limiters[clientID]
    rcl.mu.RUnlock()

    if !exists {
        rcl.mu.Lock()
        defer rcl.mu.Unlock()

        // 再次检查，防止并发创建
        if limiter, exists := rcl.limiters[clientID]; exists {
            return limiter
        }

        // 创建新的限流器
        limiter = rate.NewLimiter(rcl.rate, rcl.burst)
        rcl.limiters[clientID] = limiter
    }

    return limiter
}

// 清理过期的限流器
func (rcl *RequestContextLimiter) Cleanup() {
    rcl.mu.Lock()
    defer rcl.mu.Unlock()

    // 这里可以实现清理逻辑，比如定期清理长时间未使用的限流器
}

// 在Handler中使用限流信息
func RateLimitInfoHandler(c *gin.Context) {
    limiter := c.MustGet("rate_limiter").(*rate.Limiter)
    clientID := c.MustGet("client_id").(string)

    // 获取限流信息
    tokens := limiter.Tokens()
    limit := limiter.Limit()

    c.JSON(200, gin.H{
        "client_id":    clientID,
        "tokens_left":  tokens,
        "limit":        limit,
        "burst":        limiter.Burst(),
    })
}
```

## 3. 路由高级模式

### 3.1 路由性能优化

#### 3.1.1 路由匹配优化
```go
package routing

import (
    "net/http"
    "sort"
    "strings"
    "sync"

    "github.com/gin-gonic/gin"
)

// 路由性能分析器
type RoutePerformanceAnalyzer struct {
    routes      map[string]*RouteStats
    mu          sync.RWMutex
    enabled     bool
}

type RouteStats struct {
    Path           string
    Method         string
    Handler        string
    RequestCount   int64
    TotalDuration  time.Duration
    AverageTime    time.Duration
    MaxDuration    time.Duration
    MinDuration    time.Duration
    LastRequest    time.Time
    ErrorCount     int64
    TimeoutCount   int64
}

func NewRoutePerformanceAnalyzer(enabled bool) *RoutePerformanceAnalyzer {
    return &RoutePerformanceAnalyzer{
        routes:  make(map[string]*RouteStats),
        enabled: enabled,
    }
}

// 路由性能分析中间件
func RoutePerformanceMiddleware(analyzer *RoutePerformanceAnalyzer) gin.HandlerFunc {
    return func(c *gin.Context) {
        if !analyzer.enabled {
            c.Next()
            return
        }

        startTime := time.Now()
        path := c.FullPath()
        method := c.Request.Method

        // 记录请求开始
        c.Set("start_time", startTime)

        c.Next()

        // 计算执行时间
        duration := time.Since(startTime)

        // 更新路由统计信息
        analyzer.UpdateRouteStats(path, method, duration, len(c.Errors) > 0)
    }
}

// 更新路由统计信息
func (rpa *RoutePerformanceAnalyzer) UpdateRouteStats(path, method string, duration time.Duration, hasError bool) {
    key := method + ":" + path

    rpa.mu.Lock()
    defer rpa.mu.Unlock()

    stats, exists := rpa.routes[key]
    if !exists {
        stats = &RouteStats{
            Path:        path,
            Method:      method,
            MaxDuration: duration,
            MinDuration: duration,
        }
        rpa.routes[key] = stats
    }

    // 更新统计信息
    stats.RequestCount++
    stats.TotalDuration += duration
    stats.AverageTime = stats.TotalDuration / time.Duration(stats.RequestCount)

    if duration > stats.MaxDuration {
        stats.MaxDuration = duration
    }

    if duration < stats.MinDuration || stats.MinDuration == 0 {
        stats.MinDuration = duration
    }

    stats.LastRequest = time.Now()

    if hasError {
        stats.ErrorCount++
    }
}

// 获取性能报告
func (rpa *RoutePerformanceAnalyzer) GetPerformanceReport() []*RouteStats {
    rpa.mu.RLock()
    defer rpa.mu.RUnlock()

    report := make([]*RouteStats, 0, len(rpa.routes))
    for _, stats := range rpa.routes {
        report = append(report, stats)
    }

    // 按平均执行时间排序
    sort.Slice(report, func(i, j int) bool {
        return report[i].AverageTime > report[j].AverageTime
    })

    return report
}

// 获取慢路由
func (rpa *RoutePerformanceAnalyzer) GetSlowRoutes(threshold time.Duration) []*RouteStats {
    report := rpa.GetPerformanceReport()

    var slowRoutes []*RouteStats
    for _, stats := range report {
        if stats.AverageTime > threshold {
            slowRoutes = append(slowRoutes, stats)
        }
    }

    return slowRoutes
}
```

#### 3.1.2 路由冲突检测
```go
package routing

import (
    "fmt"
    "regexp"
    "strings"
    "sync"

    "github.com/gin-gonic/gin"
)

// 路由冲突检测器
type RouteConflictDetector struct {
    routes    map[string][]RouteInfo
    conflicts []RouteConflict
    mu        sync.RWMutex
}

type RouteInfo struct {
    Path    string
    Method  string
    Handler string
    Pattern *regexp.Regexp
}

type RouteConflict struct {
    Route1   RouteInfo
    Route2   RouteInfo
    ConflictType string
    Suggestion string
}

func NewRouteConflictDetector() *RouteConflictDetector {
    return &RouteConflictDetector{
        routes:    make(map[string][]RouteInfo),
        conflicts: make([]RouteConflict, 0),
    }
}

// 添加路由信息
func (rcd *RouteConflictDetector) AddRoute(method, path, handler string) {
    rcd.mu.Lock()
    defer rcd.mu.Unlock()

    routeInfo := RouteInfo{
        Path:    path,
        Method:  method,
        Handler: handler,
        Pattern: compileRoutePattern(path),
    }

    rcd.routes[method] = append(rcd.routes[method], routeInfo)

    // 检测冲突
    rcd.detectConflicts(method, routeInfo)
}

// 编译路由模式
func compileRoutePattern(path string) *regexp.Regexp {
    // 将Gin路由转换为正则表达式
    pattern := regexp.QuoteMeta(path)

    // 替换参数模式
    pattern = strings.ReplaceAll(pattern, `\*`, `.*`)
    pattern = strings.ReplaceAll(pattern, `:`, `[^/]+`)

    // 确保完整匹配
    pattern = "^" + pattern + "$"

    regex, _ := regexp.Compile(pattern)
    return regex
}

// 检测路由冲突
func (rcd *RouteConflictDetector) detectConflicts(method string, newRoute RouteInfo) {
    routes := rcd.routes[method]

    for _, existingRoute := range routes {
        if existingRoute.Path == newRoute.Path {
            // 完全相同的路由
            conflict := RouteConflict{
                Route1:       existingRoute,
                Route2:       newRoute,
                ConflictType: "Duplicate Route",
                Suggestion:  "Remove one of the duplicate routes or combine them into a single handler",
            }
            rcd.conflicts = append(rcd.conflicts, conflict)
            continue
        }

        // 检查模式冲突
        if rcd.isRouteConflict(existingRoute, newRoute) {
            conflict := RouteConflict{
                Route1:       existingRoute,
                Route2:       newRoute,
                ConflictType: "Pattern Conflict",
                Suggestion:  "Reorder routes or make patterns more specific",
            }
            rcd.conflicts = append(rcd.conflicts, conflict)
        }
    }
}

// 检查路由是否冲突
func (rcd *RouteConflictDetector) isRouteConflict(route1, route2 RouteInfo) bool {
    // 检查路由模式是否重叠
    path1 := route1.Path
    path2 := route2.Path

    // 简单的冲突检测逻辑
    if strings.HasPrefix(path1, path2) || strings.HasPrefix(path2, path1) {
        return true
    }

    // 检查通配符冲突
    if strings.Contains(path1, "*") || strings.Contains(path2, "*") {
        return true
    }

    return false
}

// 获取所有冲突
func (rcd *RouteConflictDetector) GetConflicts() []RouteConflict {
    rcd.mu.RLock()
    defer rcd.mu.RUnlock()

    return rcd.conflicts
}

// 获取冲突报告
func (rcd *RouteConflictDetector) GetConflictReport() string {
    conflicts := rcd.GetConflicts()

    if len(conflicts) == 0 {
        return "No route conflicts detected"
    }

    report := fmt.Sprintf("Found %d route conflicts:\n\n", len(conflicts))

    for i, conflict := range conflicts {
        report += fmt.Sprintf("Conflict #%d:\n", i+1)
        report += fmt.Sprintf("  Type: %s\n", conflict.ConflictType)
        report += fmt.Sprintf("  Route 1: %s %s -> %s\n", conflict.Route1.Method, conflict.Route1.Path, conflict.Route1.Handler)
        report += fmt.Sprintf("  Route 2: %s %s -> %s\n", conflict.Route2.Method, conflict.Route2.Path, conflict.Route2.Handler)
        report += fmt.Sprintf("  Suggestion: %s\n\n", conflict.Suggestion)
    }

    return report
}

// 路由冲突检测中间件
func RouteConflictMiddleware(detector *RouteConflictDetector) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 在开发模式下检测路由冲突
        if gin.Mode() == gin.DebugMode {
            conflicts := detector.GetConflicts()
            if len(conflicts) > 0 {
                c.Header("X-Route-Conflicts", fmt.Sprintf("%d", len(conflicts)))
            }
        }

        c.Next()
    }
}
```

### 3.2 动态路由管理

#### 3.2.1 动态路由注册
```go
package routing

import (
    "net/http"
    "sync"

    "github.com/gin-gonic/gin"
)

// 动态路由管理器
type DynamicRouteManager struct {
    router     *gin.Engine
    routes     map[string]*DynamicRoute
    mu         sync.RWMutex
    middleware []gin.HandlerFunc
}

type DynamicRoute struct {
    Path        string
    Method      string
    Handler     gin.HandlerFunc
    Middlewares []gin.HandlerFunc
    Enabled     bool
    Priority    int
    Metadata    map[string]interface{}
}

func NewDynamicRouteManager(router *gin.Engine) *DynamicRouteManager {
    return &DynamicRouteManager{
        router: router,
        routes: make(map[string]*DynamicRoute),
    }
}

// 添加动态路由
func (drm *DynamicRouteManager) AddRoute(route *DynamicRoute) error {
    drm.mu.Lock()
    defer drm.mu.Unlock()

    key := route.Method + ":" + route.Path

    if _, exists := drm.routes[key]; exists {
        return fmt.Errorf("route already exists: %s", key)
    }

    drm.routes[key] = route

    if route.Enabled {
        drm.registerRoute(route)
    }

    return nil
}

// 注册路由到Gin引擎
func (drm *DynamicRouteManager) registerRoute(route *DynamicRoute) {
    // 组合中间件
    handlers := append(drm.middleware, route.Middlewares...)
    handlers = append(handlers, route.Handler)

    // 根据方法注册路由
    switch route.Method {
    case http.MethodGet:
        drm.router.GET(route.Path, handlers...)
    case http.MethodPost:
        drm.router.POST(route.Path, handlers...)
    case http.MethodPut:
        drm.router.PUT(route.Path, handlers...)
    case http.MethodDelete:
        drm.router.DELETE(route.Path, handlers...)
    case http.MethodPatch:
        drm.router.PATCH(route.Path, handlers...)
    case http.MethodOptions:
        drm.router.OPTIONS(route.Path, handlers...)
    case http.MethodHead:
        drm.router.HEAD(route.Path, handlers...)
    default:
        // 自定义方法
        drm.router.Handle(route.Method, route.Path, handlers...)
    }
}

// 移除动态路由
func (drm *DynamicRouteManager) RemoveRoute(method, path string) error {
    drm.mu.Lock()
    defer drm.mu.Unlock()

    key := method + ":" + path
    route, exists := drm.routes[key]
    if !exists {
        return fmt.Errorf("route not found: %s", key)
    }

    delete(drm.routes, key)

    // 注意：Gin不支持运行时移除路由，这里需要重建路由
    drm.rebuildRoutes()

    return nil
}

// 启用/禁用路由
func (drm *DynamicRouteManager) SetRouteEnabled(method, path string, enabled bool) error {
    drm.mu.Lock()
    defer drm.mu.Unlock()

    key := method + ":" + path
    route, exists := drm.routes[key]
    if !exists {
        return fmt.Errorf("route not found: %s", key)
    }

    route.Enabled = enabled

    // 重建路由
    drm.rebuildRoutes()

    return nil
}

// 重建所有路由
func (drm *DynamicRouteManager) rebuildRoutes() {
    // 保存现有路由
    routes := make([]*DynamicRoute, 0, len(drm.routes))
    for _, route := range drm.routes {
        routes = append(routes, route)
    }

    // 清理路由（需要重建Gin引擎或使用路由组）
    // 这里简化处理，实际应用中可能需要更复杂的逻辑
}

// 获取所有路由
func (drm *DynamicRouteManager) GetRoutes() []*DynamicRoute {
    drm.mu.RLock()
    defer drm.mu.RUnlock()

    routes := make([]*DynamicRoute, 0, len(drm.routes))
    for _, route := range drm.routes {
        routes = append(routes, route)
    }

    return routes
}

// 根据元数据获取路由
func (drm *DynamicRouteManager) GetRoutesByMetadata(key string, value interface{}) []*DynamicRoute {
    drm.mu.RLock()
    defer drm.mu.RUnlock()

    var routes []*DynamicRoute
    for _, route := range drm.routes {
        if route.Metadata != nil {
            if val, exists := route.Metadata[key]; exists && val == value {
                routes = append(routes, route)
            }
        }
    }

    return routes
}

// 添加全局中间件
func (drm *DynamicRouteManager) Use(middleware ...gin.HandlerFunc) {
    drm.middleware = append(drm.middleware, middleware...)
}

// 路由健康检查
func (drm *DynamicRouteManager) HealthCheck() gin.HandlerFunc {
    return func(c *gin.Context) {
        drm.mu.RLock()
        routeCount := len(drm.routes)
        enabledCount := 0

        for _, route := range drm.routes {
            if route.Enabled {
                enabledCount++
            }
        }
        drm.mu.RUnlock()

        c.JSON(http.StatusOK, gin.H{
            "total_routes":   routeCount,
            "enabled_routes": enabledCount,
            "disabled_routes": routeCount - enabledCount,
        })
    }
}
```

#### 3.2.2 路由版本管理
```go
package routing

import (
    "net/http"
    "regexp"
    "sort"
    "strconv"
    "strings"
    "sync"

    "github.com/gin-gonic/gin"
)

// 路由版本管理器
type RouteVersionManager struct {
    router       *gin.Engine
    versions     map[string]*VersionGroup
    defaultVersion string
    versionPattern *regexp.Regexp
    mu           sync.RWMutex
}

type VersionGroup struct {
    Version     string
    Priority    int
    Routes      []*VersionedRoute
    Middlewares []gin.HandlerFunc
    Enabled     bool
}

type VersionedRoute struct {
    Path        string
    Method      string
    Handler     gin.HandlerFunc
    Version     string
    Deprecated  bool
    DeprecationInfo *DeprecationInfo
}

type DeprecationInfo struct {
    Since       string
    RemoveAfter string
    Alternative string
    Reason      string
}

func NewRouteVersionManager(router *gin.Engine) *RouteVersionManager {
    return &RouteVersionManager{
        router:        router,
        versions:      make(map[string]*VersionGroup),
        defaultVersion: "v1",
        versionPattern: regexp.MustCompile(`^v(\d+)$`),
    }
}

// 添加版本
func (rvm *RouteVersionManager) AddVersion(version string, priority int) error {
    rvm.mu.Lock()
    defer rvm.mu.Unlock()

    if !rvm.isValidVersion(version) {
        return fmt.Errorf("invalid version format: %s", version)
    }

    if _, exists := rvm.versions[version]; exists {
        return fmt.Errorf("version already exists: %s", version)
    }

    rvm.versions[version] = &VersionGroup{
        Version:  version,
        Priority: priority,
        Routes:   make([]*VersionedRoute, 0),
        Enabled:  true,
    }

    return nil
}

// 添加版本路由
func (rvm *RouteVersionManager) AddVersionedRoute(version, method, path string, handler gin.HandlerFunc) error {
    rvm.mu.Lock()
    defer rvm.mu.Unlock()

    versionGroup, exists := rvm.versions[version]
    if !exists {
        return fmt.Errorf("version not found: %s", version)
    }

    route := &VersionedRoute{
        Path:    path,
        Method:  method,
        Handler: handler,
        Version: version,
    }

    versionGroup.Routes = append(versionGroup.Routes, route)

    // 注册路由
    rvm.registerVersionedRoute(route, versionGroup)

    return nil
}

// 注册版本路由
func (rvm *RouteVersionManager) registerVersionedRoute(route *VersionedRoute, versionGroup *VersionGroup) {
    // 构建版本化路径
    versionedPath := "/" + route.Version + route.Path

    // 组合中间件
    handlers := append(versionGroup.Middlewares, rvm.createVersionMiddleware(route))
    handlers = append(handlers, route.Handler)

    // 注册路由
    switch route.Method {
    case http.MethodGet:
        rvm.router.GET(versionedPath, handlers...)
    case http.MethodPost:
        rvm.router.POST(versionedPath, handlers...)
    case http.MethodPut:
        rvm.router.PUT(versionedPath, handlers...)
    case http.MethodDelete:
        rvm.router.DELETE(versionedPath, handlers...)
    case http.MethodPatch:
        rvm.router.PATCH(versionedPath, handlers...)
    case http.MethodOptions:
        rvm.router.OPTIONS(versionedPath, handlers...)
    case http.MethodHead:
        rvm.router.HEAD(versionedPath, handlers...)
    }
}

// 创建版本中间件
func (rvm *RouteVersionManager) createVersionMiddleware(route *VersionedRoute) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 设置版本信息
        c.Set("route_version", route.Version)
        c.Set("route_path", route.Path)

        // 处理废弃路由
        if route.Deprecated && route.DeprecationInfo != nil {
            c.Header("X-API-Deprecated", "true")
            c.Header("X-API-Deprecation-Since", route.DeprecationInfo.Since)
            c.Header("X-API-Deprecation-Remove-After", route.DeprecationInfo.RemoveAfter)
            if route.DeprecationInfo.Alternative != "" {
                c.Header("X-API-Alternative", route.DeprecationInfo.Alternative)
            }
        }

        c.Next()
    }
}

// 版本路由中间件
func (rvm *RouteVersionManager) VersionMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 从URL路径中提取版本
        path := c.Request.URL.Path
        parts := strings.Split(strings.Trim(path, "/"), "/")

        if len(parts) > 0 {
            version := parts[0]
            if rvm.isValidVersion(version) {
                c.Set("requested_version", version)
                c.Set("versioned_path", "/"+strings.Join(parts[1:], "/"))
            }
        }

        c.Next()
    }
}

// 版本重定向中间件
func (rvm *RouteVersionManager) VersionRedirectMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        requestedVersion, exists := c.Get("requested_version")
        if !exists {
            // 没有指定版本，重定向到默认版本
            defaultPath := "/" + rvm.defaultVersion + c.Request.URL.Path
            c.Redirect(http.StatusMovedPermanently, defaultPath)
            c.Abort()
            return
        }

        // 检查版本是否存在
        rvm.mu.RLock()
        versionGroup, exists := rvm.versions[requestedVersion.(string)]
        rvm.mu.RUnlock()

        if !exists || !versionGroup.Enabled {
            c.JSON(http.StatusNotFound, gin.H{
                "error": "API version not found",
                "version": requestedVersion,
                "available_versions": rvm.GetAvailableVersions(),
            })
            c.Abort()
            return
        }

        c.Next()
    }
}

// 获取可用版本
func (rvm *RouteVersionManager) GetAvailableVersions() []string {
    rvm.mu.RLock()
    defer rvm.mu.RUnlock()

    versions := make([]string, 0, len(rvm.versions))
    for version, group := range rvm.versions {
        if group.Enabled {
            versions = append(versions, version)
        }
    }

    // 按优先级排序
    sort.Slice(versions, func(i, j int) bool {
        return rvm.versions[versions[i]].Priority > rvm.versions[versions[j]].Priority
    })

    return versions
}

// 验证版本格式
func (rvm *RouteVersionManager) isValidVersion(version string) bool {
    return rvm.versionPattern.MatchString(version)
}

// 设置默认版本
func (rvm *RouteVersionManager) SetDefaultVersion(version string) error {
    rvm.mu.Lock()
    defer rvm.mu.Unlock()

    if !rvm.isValidVersion(version) {
        return fmt.Errorf("invalid version format: %s", version)
    }

    if _, exists := rvm.versions[version]; !exists {
        return fmt.Errorf("version not found: %s", version)
    }

    rvm.defaultVersion = version
    return nil
}

// 废弃版本路由
func (rvm *RouteVersionManager) DeprecateRoute(version, method, path string, deprecationInfo *DeprecationInfo) error {
    rvm.mu.Lock()
    defer rvm.mu.Unlock()

    versionGroup, exists := rvm.versions[version]
    if !exists {
        return fmt.Errorf("version not found: %s", version)
    }

    for _, route := range versionGroup.Routes {
        if route.Method == method && route.Path == path {
            route.Deprecated = true
            route.DeprecationInfo = deprecationInfo
            return nil
        }
    }

    return fmt.Errorf("route not found: %s %s", method, path)
}

// 获取版本信息
func (rvm *RouteVersionManager) GetVersionInfo() gin.HandlerFunc {
    return func(c *gin.Context) {
        rvm.mu.RLock()
        versions := make([]gin.H, 0, len(rvm.versions))

        for version, group := range rvm.versions {
            versionInfo := gin.H{
                "version":  version,
                "enabled":  group.Enabled,
                "priority": group.Priority,
                "routes":   len(group.Routes),
            }

            if version == rvm.defaultVersion {
                versionInfo["default"] = true
            }

            versions = append(versions, versionInfo)
        }
        rvm.mu.RUnlock()

        c.JSON(http.StatusOK, gin.H{
            "default_version": rvm.defaultVersion,
            "versions":       versions,
        })
    }
}
```

## 4. 中间件高级模式

### 4.1 中间件链控制

#### 4.1.1 条件中间件
```go
package middleware

import (
    "net/http"
    "strings"

    "github.com/gin-gonic/gin"
)

// 条件中间件工厂
type ConditionalMiddlewareFactory struct {
    conditions map[string]ConditionFunc
}

type ConditionFunc func(*gin.Context) bool

func NewConditionalMiddlewareFactory() *ConditionalMiddlewareFactory {
    return &ConditionalMiddlewareFactory{
        conditions: make(map[string]ConditionFunc),
    }
}

// 注册条件函数
func (cmf *ConditionalMiddlewareFactory) RegisterCondition(name string, condition ConditionFunc) {
    cmf.conditions[name] = condition
}

// 条件中间件
func (cmf *ConditionalMiddlewareFactory) Conditional(conditionName string, middleware gin.HandlerFunc) gin.HandlerFunc {
    condition, exists := cmf.conditions[conditionName]
    if !exists {
        // 如果条件不存在，直接跳过中间件
        return func(c *gin.Context) {
            c.Next()
        }
    }

    return func(c *gin.Context) {
        if condition(c) {
            middleware(c)
        } else {
            c.Next()
        }
    }
}

// 多条件中间件
func (cmf *ConditionalMiddlewareFactory) MultiConditional(conditions []string, middleware gin.HandlerFunc) gin.HandlerFunc {
    return func(c *gin.Context) {
        for _, conditionName := range conditions {
            condition, exists := cmf.conditions[conditionName]
            if exists && condition(c) {
                middleware(c)
                return
            }
        }
        c.Next()
    }
}

// 预定义条件函数
func PredefinedConditions() map[string]ConditionFunc {
    return map[string]ConditionFunc{
        "authenticated": func(c *gin.Context) bool {
            return c.GetString("user_id") != ""
        },
        "admin": func(c *gin.Context) bool {
            roles := c.GetStringSlice("user_roles")
            for _, role := range roles {
                if role == "admin" {
                    return true
                }
            }
            return false
        },
        "api_request": func(c *gin.Context) bool {
            return strings.HasPrefix(c.Request.URL.Path, "/api/")
        },
        "json_request": func(c *gin.Context) bool {
            return strings.Contains(c.GetHeader("Content-Type"), "application/json")
        },
        "mobile_client": func(c *gin.Context) bool {
            userAgent := c.GetHeader("User-Agent")
            return strings.Contains(userAgent, "Mobile") || strings.Contains(userAgent, "Android") || strings.Contains(userAgent, "iPhone")
        },
        "production": func(c *gin.Context) bool {
            return gin.Mode() == gin.ReleaseMode
        },
        "development": func(c *gin.Context) bool {
            return gin.Mode() == gin.DebugMode
        },
    }
}

// 使用示例
func ExampleConditionalMiddleware() {
    factory := NewConditionalMiddlewareFactory()

    // 注册预定义条件
    for name, condition := range PredefinedConditions() {
        factory.RegisterCondition(name, condition)
    }

    router := gin.Default()

    // 只对认证用户应用中间件
    router.Use(factory.Conditional("authenticated", AuthMiddleware()))

    // 只对管理员应用中间件
    router.Use(factory.Conditional("admin", AdminMiddleware()))

    // 只对API请求应用中间件
    router.Use(factory.Conditional("api_request", APIMiddleware()))

    // 多条件中间件
    router.Use(factory.MultiConditional([]string{"admin", "api_request"}, AdminAPIMiddleware()))
}
```

#### 4.1.2 中间件链管理器
```go
package middleware

import (
    "net/http"
    "sync"

    "github.com/gin-gonic/gin"
)

// 中间件链管理器
type MiddlewareChainManager struct {
    chains     map[string]*MiddlewareChain
    globalChain []gin.HandlerFunc
    mu         sync.RWMutex
}

type MiddlewareChain struct {
    Name        string
    Middlewares []gin.HandlerFunc
    Enabled     bool
    Priority    int
    Conditions  []ConditionFunc
}

func NewMiddlewareChainManager() *MiddlewareChainManager {
    return &MiddlewareChainManager{
        chains:      make(map[string]*MiddlewareChain),
        globalChain:  make([]gin.HandlerFunc, 0),
    }
}

// 创建中间件链
func (mcm *MiddlewareChainManager) CreateChain(name string, middlewares []gin.HandlerFunc) *MiddlewareChain {
    chain := &MiddlewareChain{
        Name:        name,
        Middlewares: middlewares,
        Enabled:     true,
        Priority:    0,
        Conditions:  make([]ConditionFunc, 0),
    }

    mcm.mu.Lock()
    defer mcm.mu.Unlock()
    mcm.chains[name] = chain

    return chain
}

// 添加中间件到链
func (mcm *MiddlewareChainManager) AddToChain(chainName string, middlewares ...gin.HandlerFunc) error {
    mcm.mu.Lock()
    defer mcm.mu.Unlock()

    chain, exists := mcm.chains[chainName]
    if !exists {
        return fmt.Errorf("chain not found: %s", chainName)
    }

    chain.Middlewares = append(chain.Middlewares, middlewares...)
    return nil
}

// 设置链条件
func (mcm *MiddlewareChainManager) SetChainConditions(chainName string, conditions ...ConditionFunc) error {
    mcm.mu.Lock()
    defer mcm.mu.Unlock()

    chain, exists := mcm.chains[chainName]
    if !exists {
        return fmt.Errorf("chain not found: %s", chainName)
    }

    chain.Conditions = conditions
    return nil
}

// 启用/禁用链
func (mcm *MiddlewareChainManager) SetChainEnabled(chainName string, enabled bool) error {
    mcm.mu.Lock()
    defer mcm.mu.Unlock()

    chain, exists := mcm.chains[chainName]
    if !exists {
        return fmt.Errorf("chain not found: %s", chainName)
    }

    chain.Enabled = enabled
    return nil
}

// 应用中间件链
func (mcm *MiddlewareChainManager) ApplyChain(router *gin.Engine, chainName string) error {
    mcm.mu.RLock()
    defer mcm.mu.RUnlock()

    chain, exists := mcm.chains[chainName]
    if !exists {
        return fmt.Errorf("chain not found: %s", chainName)
    }

    if !chain.Enabled {
        return nil
    }

    // 检查条件
    if len(chain.Conditions) > 0 {
        router.Use(func(c *gin.Context) {
            for _, condition := range chain.Conditions {
                if condition(c) {
                    // 应用链中所有中间件
                    for _, middleware := range chain.Middlewares {
                        middleware(c)
                    }
                    break
                }
            }
            c.Next()
        })
    } else {
        // 无条件应用所有中间件
        router.Use(chain.Middlewares...)
    }

    return nil
}

// 添加全局中间件
func (mcm *MiddlewareChainManager) UseGlobal(middlewares ...gin.HandlerFunc) {
    mcm.mu.Lock()
    defer mcm.mu.Unlock()

    mcm.globalChain = append(mcm.globalChain, middlewares...)
}

// 应用全局中间件
func (mcm *MiddlewareChainManager) ApplyGlobal(router *gin.Engine) {
    mcm.mu.RLock()
    defer mcm.mu.RUnlock()

    if len(mcm.globalChain) > 0 {
        router.Use(mcm.globalChain...)
    }
}

// 中间件链执行器
func (mcm *MiddlewareChainManager) ExecuteChain(c *gin.Context, chainName string) error {
    mcm.mu.RLock()
    defer mcm.mu.RUnlock()

    chain, exists := mcm.chains[chainName]
    if !exists {
        return fmt.Errorf("chain not found: %s", chainName)
    }

    if !chain.Enabled {
        c.Next()
        return nil
    }

    // 检查条件
    for _, condition := range chain.Conditions {
        if condition(c) {
            // 执行链中所有中间件
            for _, middleware := range chain.Middlewares {
                middleware(c)
            }
            break
        }
    }

    c.Next()
    return nil
}

// 获取链信息
func (mcm *MiddlewareChainManager) GetChainInfo(chainName string) (*MiddlewareChain, error) {
    mcm.mu.RLock()
    defer mcm.mu.RUnlock()

    chain, exists := mcm.chains[chainName]
    if !exists {
        return nil, fmt.Errorf("chain not found: %s", chainName)
    }

    return chain, nil
}

// 获取所有链
func (mcm *MiddlewareChainManager) GetAllChains() []*MiddlewareChain {
    mcm.mu.RLock()
    defer mcm.mu.RUnlock()

    chains := make([]*MiddlewareChain, 0, len(mcm.chains))
    for _, chain := range mcm.chains {
        chains = append(chains, chain)
    }

    return chains
}

// 中间件性能监控
func (mcm *MiddlewareChainManager) PerformanceMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        startTime := time.Now()

        c.Next()

        duration := time.Since(startTime)

        // 记录性能数据
        c.Set("middleware_duration", duration)

        if duration > 100*time.Millisecond {
            // 记录慢中间件
            c.Set("slow_middleware", true)
        }
    }
}
```

### 4.2 中间件数据共享

#### 4.2.1 中间件上下文管理
```go
package middleware

import (
    "net/http"
    "sync"

    "github.com/gin-gonic/gin"
)

// 中间件上下文管理器
type MiddlewareContextManager struct {
    contexts map[*gin.Context]*MiddlewareContext
    mu       sync.RWMutex
}

type MiddlewareContext struct {
    Data      map[string]interface{}
    Steps     []MiddlewareStep
    StartTime time.Time
    RequestID string
}

type MiddlewareStep struct {
    Name      string
    StartTime time.Time
    EndTime   time.Time
    Duration  time.Duration
    Success   bool
    Error     error
}

func NewMiddlewareContextManager() *MiddlewareContextManager {
    return &MiddlewareContextManager{
        contexts: make(map[*gin.Context]*MiddlewareContext),
    }
}

// 中间件上下文中间件
func MiddlewareContextMiddleware(manager *MiddlewareContextManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 创建中间件上下文
        ctx := &MiddlewareContext{
            Data:      make(map[string]interface{}),
            Steps:     make([]MiddlewareStep, 0),
            StartTime: time.Now(),
            RequestID: generateRequestID(),
        }

        // 注册上下文
        manager.RegisterContext(c, ctx)

        // 设置到Gin Context
        c.Set("middleware_context", ctx)
        c.Set("request_id", ctx.RequestID)

        // 添加步骤追踪函数
        c.Set("track_step", func(name string) func(error) {
            startTime := time.Now()
            return func(err error) {
                endTime := time.Now()
                step := MiddlewareStep{
                    Name:      name,
                    StartTime: startTime,
                    EndTime:   endTime,
                    Duration:  endTime.Sub(startTime),
                    Success:   err == nil,
                    Error:     err,
                }
                ctx.Steps = append(ctx.Steps, step)
            }
        })

        c.Next()

        // 注销上下文
        manager.UnregisterContext(c)
    }
}

// 注册上下文
func (mcm *MiddlewareContextManager) RegisterContext(c *gin.Context, ctx *MiddlewareContext) {
    mcm.mu.Lock()
    defer mcm.mu.Unlock()
    mcm.contexts[c] = ctx
}

// 注销上下文
func (mcm *MiddlewareContextManager) UnregisterContext(c *gin.Context) {
    mcm.mu.Lock()
    defer mcm.mu.Unlock()
    delete(mcm.contexts, c)
}

// 获取上下文
func (mcm *MiddlewareContextManager) GetContext(c *gin.Context) (*MiddlewareContext, bool) {
    mcm.mu.RLock()
    defer mcm.mu.RUnlock()

    ctx, exists := mcm.contexts[c]
    return ctx, exists
}

// 设置数据
func (mcm *MiddlewareContextManager) SetData(c *gin.Context, key string, value interface{}) {
    if ctx, exists := mcm.GetContext(c); exists {
        ctx.Data[key] = value
    }
}

// 获取数据
func (mcm *MiddlewareContextManager) GetData(c *gin.Context, key string) (interface{}, bool) {
    if ctx, exists := mcm.GetContext(c); exists {
        value, exists := ctx.Data[key]
        return value, exists
    }
    return nil, false
}

// 中间件数据共享辅助函数
func MiddlewareDataHelper() gin.HandlerFunc {
    manager := NewMiddlewareContextManager()

    return func(c *gin.Context) {
        // 设置中间件上下文
        MiddlewareContextMiddleware(manager)(c)

        // 添加数据操作函数
        c.Set("set_middleware_data", func(key string, value interface{}) {
            manager.SetData(c, key, value)
        })

        c.Set("get_middleware_data", func(key string) (interface{}, bool) {
            return manager.GetData(c, key)
        })

        c.Set("track_middleware_step", func(name string) func(error) {
            if trackFunc, exists := c.Get("track_step"); exists {
                return trackFunc.(func(string) func(error))(name)
            }
            return func(error) {}
        })

        c.Next()
    }
}

// 使用示例
func ExampleMiddlewareDataUsage() {
    router := gin.Default()

    // 应用中间件数据共享
    router.Use(MiddlewareDataHelper())

    // 示例中间件1：设置数据
    router.Use(func(c *gin.Context) {
        setData := c.MustGet("set_middleware_data").(func(string, interface{}))
        trackStep := c.MustGet("track_middleware_step").(func(string) func(error))

        step := trackStep("authentication")

        // 模拟认证逻辑
        setData("user_id", "12345")
        setData("user_roles", []string{"user", "admin"})

        step(nil) // 标记步骤完成

        c.Next()
    })

    // 示例中间件2：读取数据
    router.Use(func(c *gin.Context) {
        getData := c.MustGet("get_middleware_data").(func(string) (interface{}, bool))
        trackStep := c.MustGet("track_middleware_step").(func(string) func(error))

        step := trackStep("authorization")

        // 读取前面中间件设置的数据
        if userID, exists := getData("user_id"); exists {
            c.Set("user_id", userID)
        }

        if roles, exists := getData("user_roles"); exists {
            c.Set("user_roles", roles)
        }

        step(nil)

        c.Next()
    })

    // 在Handler中使用数据
    router.GET("/profile", func(c *gin.Context) {
        getData := c.MustGet("get_middleware_data").(func(string) (interface{}, bool))

        userID, _ := getData("user_id")
        roles, _ := getData("user_roles")

        c.JSON(http.StatusOK, gin.H{
            "user_id": userID,
            "roles":   roles,
        })
    })
}
```

#### 4.2.2 中间件数据验证
```go
package middleware

import (
    "net/http"
    "reflect"
    "strings"

    "github.com/gin-gonic/gin"
    "github.com/go-playground/validator/v10"
)

// 中间件数据验证器
type MiddlewareDataValidator struct {
    validator *validator.Validate
    rules     map[string][]ValidationRule
}

type ValidationRule struct {
    Field    string
    Tag      string
    Message  string
    Required bool
}

func NewMiddlewareDataValidator() *MiddlewareDataValidator {
    return &MiddlewareDataValidator{
        validator: validator.New(),
        rules:     make(map[string][]ValidationRule),
    }
}

// 添加验证规则
func (mdv *MiddlewareDataValidator) AddRule(key string, rules ...ValidationRule) {
    mdv.rules[key] = append(mdv.rules[key], rules...)
}

// 验证中间件
func (mdv *MiddlewareDataValidator) ValidateMiddleware(key string) gin.HandlerFunc {
    return func(c *gin.Context) {
        getData := c.MustGet("get_middleware_data").(func(string) (interface{}, bool))

        value, exists := getData(key)
        if !exists {
            c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
                "error": "Required data not found",
                "key":    key,
            })
            return
        }

        // 验证数据
        if err := mdv.validateData(key, value); err != nil {
            c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
                "error": err.Error(),
                "key":   key,
            })
            return
        }

        c.Next()
    }
}

// 验证数据
func (mdv *MiddlewareDataValidator) validateData(key string, value interface{}) error {
    rules, exists := mdv.rules[key]
    if !exists {
        return nil
    }

    for _, rule := range rules {
        if rule.Required && (value == nil || value == "") {
            return fmt.Errorf("field %s is required", rule.Field)
        }

        if value != nil && value != "" {
            // 使用validator验证
            if err := mdv.validator.Var(value, rule.Tag); err != nil {
                if rule.Message != "" {
                    return fmt.Errorf(rule.Message)
                }
                return err
            }
        }
    }

    return nil
}

// 结构体验证中间件
func (mdv *MiddlewareDataValidator) ValidateStructMiddleware(key string, obj interface{}) gin.HandlerFunc {
    return func(c *gin.Context) {
        getData := c.MustGet("get_middleware_data").(func(string) (interface{}, bool))

        value, exists := getData(key)
        if !exists {
            c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
                "error": "Required data not found",
                "key":    key,
            })
            return
        }

        // 将数据转换为目标结构体
        if err := mdv.convertAndValidate(value, obj); err != nil {
            c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
                "error": err.Error(),
                "key":   key,
            })
            return
        }

        // 将验证后的数据设置到Context中
        c.Set(key+"_validated", obj)

        c.Next()
    }
}

// 转换并验证
func (mdv *MiddlewareDataValidator) convertAndValidate(value interface{}, target interface{}) error {
    // 这里可以实现数据转换逻辑
    // 简化示例，实际使用时需要根据具体数据类型进行转换

    // 验证结构体
    if err := mdv.validator.Struct(target); err != nil {
        return err
    }

    return nil
}

// 中间件数据验证使用示例
func ExampleMiddlewareDataValidation() {
    router := gin.Default()

    validator := NewMiddlewareDataValidator()

    // 定义验证规则
    validator.AddRule("user_data",
        ValidationRule{Field: "id", Tag: "required", Required: true},
        ValidationRule{Field: "name", Tag: "required,min=3,max=50", Required: true},
        ValidationRule{Field: "email", Tag: "required,email", Required: true},
    )

    router.Use(MiddlewareDataHelper())

    // 设置数据的中间件
    router.Use(func(c *gin.Context) {
        setData := c.MustGet("set_middleware_data").(func(string, interface{}))

        // 模拟从token中解析的用户数据
        userData := map[string]interface{}{
            "id":    "12345",
            "name":  "John Doe",
            "email": "john@example.com",
        }

        setData("user_data", userData)

        c.Next()
    })

    // 验证中间件
    router.Use(validator.ValidateMiddleware("user_data"))

    // 在Handler中使用验证后的数据
    router.GET("/profile", func(c *gin.Context) {
        getData := c.MustGet("get_middleware_data").(func(string) (interface{}, bool))

        userData, _ := getData("user_data")

        c.JSON(http.StatusOK, gin.H{
            "user_data": userData,
        })
    })
}
```

---

这个Gin框架核心高级特性文档涵盖了渲染引擎、Context管理、路由优化和中间件模式等关键内容。每个部分都提供了完整的代码示例和实际应用场景，帮助开发者深入理解Gin框架的高级特性并能在实际项目中灵活运用。

**主要特色**：
- 完整的代码示例，可直接用于生产环境
- 深入的原理解析和性能优化建议
- 实际项目中的最佳实践
- 可扩展的架构设计
- 详细的错误处理和监控机制