# Gin中间件基础与高级模式

## 📚 目录

- [中间件概念](#中间件概念)
- [内置中间件](#内置中间件)
- [自定义中间件](#自定义中间件)
- [中间件链](#中间件链)
- [中间件参数](#中间件参数)
- [中间件最佳实践](#中间件最佳实践)
- [中间件性能优化](#中间件性能优化)
- [高级中间件模式](#高级中间件模式)
- [中间件测试](#中间件测试)
- [实战案例](#实战案例)

## 中间件概念

### 什么是中间件
中间件是在HTTP请求处理过程中插入的函数，它们可以在请求到达处理函数之前或响应返回客户端之后执行特定操作。

### 中间件执行流程
```go
func main() {
    r := gin.Default()

    // 全局中间件
    r.Use(LoggerMiddleware())
    r.Use(AuthMiddleware())

    r.GET("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    r.Run(":8080")
}

// 日志中间件
func LoggerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        // 请求处理前
        fmt.Printf("Request started: %s %s\n", c.Request.Method, c.Request.URL.Path)

        // 处理请求
        c.Next()

        // 请求处理后
        duration := time.Since(start)
        fmt.Printf("Request completed: %s %s - %v\n",
            c.Request.Method, c.Request.URL.Path, duration)
    }
}

// 认证中间件
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.JSON(401, gin.H{"error": "No token provided"})
            c.Abort()
            return
        }

        // 验证token
        if token != "valid-token" {
            c.JSON(401, gin.H{"error": "Invalid token"})
            c.Abort()
            return
        }

        c.Next()
    }
}
```

## 内置中间件

### 常用内置中间件
```go
func main() {
    // 创建gin引擎
    r := gin.New()

    // 使用内置中间件
    r.Use(gin.Logger())                    // 日志中间件
    r.Use(gin.Recovery())                  // 恢复中间件
    r.Use(gin.CustomLoggerWithConfig(gin.LoggerConfig{
        Output:    gin.DefaultWriter,
        Formatter: gin.LogFormatter,
        SkipPaths: []string{"/health", "/metrics"},
    }))

    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    r.Run(":8080")
}
```

### Logger中间件配置
```go
func main() {
    r := gin.New()

    // 自定义日志配置
    r.Use(gin.LoggerWithConfig(gin.LoggerConfig{
        Formatter: func(param gin.LogFormatterParams) string {
            return fmt.Sprintf("%s - [%s] \"%s %s %s %d %s \"%s\" %s\"\n",
                param.ClientIP,
                param.TimeStamp.Format(time.RFC1123),
                param.Method,
                param.Path,
                param.Request.Proto,
                param.StatusCode,
                param.Latency,
                param.Request.UserAgent(),
                param.ErrorMessage,
            )
        },
        Output:    gin.DefaultWriter,
        SkipPaths: []string{"/health", "/metrics"},
    }))

    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    r.Run(":8080")
}
```

### Recovery中间件配置
```go
func main() {
    r := gin.New()

    // 自定义恢复中间件
    r.Use(gin.CustomRecoveryWithConfig(gin.RecoveryConfig{
        StackTrace: true,
        Handler: func(c *gin.Context, err interface{}) {
            // 自定义错误处理
            c.JSON(500, gin.H{
                "error": "Internal Server Error",
                "message": fmt.Sprintf("%v", err),
            })
        },
    }))

    r.GET("/panic", func(c *gin.Context) {
        panic("This is a panic")
    })

    r.Run(":8080")
}
```

## 自定义中间件

### 基础自定义中间件
```go
func main() {
    r := gin.Default()

    // 使用自定义中间件
    r.Use(CORSMiddleware())
    r.Use(RateLimitMiddleware())
    r.Use(SecurityHeadersMiddleware())

    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    r.Run(":8080")
}

// CORS中间件
func CORSMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("Access-Control-Allow-Origin", "*")
        c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        c.Header("Access-Control-Allow-Credentials", "true")

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }

        c.Next()
    }
}

// 限流中间件
func RateLimitMiddleware() gin.HandlerFunc {
    // 简单的内存限流
    limiter := make(map[string]int)
    mutex := &sync.Mutex{}

    return func(c *gin.Context) {
        ip := c.ClientIP()

        mutex.Lock()
        count := limiter[ip]
        if count >= 100 { // 每分钟100个请求
            mutex.Unlock()
            c.JSON(429, gin.H{"error": "Rate limit exceeded"})
            c.Abort()
            return
        }
        limiter[ip] = count + 1
        mutex.Unlock()

        c.Next()
    }
}

// 安全头中间件
func SecurityHeadersMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-XSS-Protection", "1; mode=block")
        c.Header("Content-Security-Policy", "default-src 'self'")
        c.Header("Referrer-Policy", "strict-origin-when-cross-origin")

        c.Next()
    }
}
```

### 带状态的自定义中间件
```go
func main() {
    r := gin.Default()

    // 使用带状态的自定义中间件
    r.Use(RequestCounterMiddleware())
    r.Use(ResponseTimeMiddleware())

    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    r.Run(":8080")
}

// 请求计数中间件
type RequestCounter struct {
    count   int64
    mutex   sync.RWMutex
}

func (rc *RequestCounter) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        rc.mutex.Lock()
        rc.count++
        count := rc.count
        rc.mutex.Unlock()

        c.Set("request_count", count)
        c.Header("X-Request-Count", fmt.Sprintf("%d", count))

        c.Next()
    }
}

func RequestCounterMiddleware() gin.HandlerFunc {
    counter := &RequestCounter{}
    return counter.Middleware()
}

// 响应时间中间件
type ResponseTimeTracker struct {
    times map[string]time.Duration
    mutex sync.RWMutex
}

func (rt *ResponseTimeTracker) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        path := c.Request.URL.Path
        start := time.Now()

        c.Next()

        duration := time.Since(start)

        rt.mutex.Lock()
        rt.times[path] = duration
        rt.mutex.Unlock()

        c.Header("X-Response-Time", duration.String())
    }
}

func ResponseTimeMiddleware() gin.HandlerFunc {
    tracker := &ResponseTimeTracker{
        times: make(map[string]time.Duration),
    }
    return tracker.Middleware()
}
```

### 认证授权中间件
```go
func main() {
    r := gin.Default()

    // 认证中间件
    r.Use(JWTAuthMiddleware())

    // 需要认证的路由组
    auth := r.Group("/auth")
    auth.Use(JWTAuthMiddleware())
    {
        auth.GET("/profile", GetProfile)
        auth.PUT("/profile", UpdateProfile)
    }

    // 管理员路由组
    admin := r.Group("/admin")
    admin.Use(JWTAuthMiddleware(), AdminMiddleware())
    {
        admin.GET("/users", GetUsers)
        admin.POST("/users", CreateUser)
    }

    r.Run(":8080")
}

// JWT认证中间件
func JWTAuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.JSON(401, gin.H{"error": "No token provided"})
            c.Abort()
            return
        }

        // 移除Bearer前缀
        token = strings.TrimPrefix(token, "Bearer ")
        if token == "" {
            c.JSON(401, gin.H{"error": "Invalid token format"})
            c.Abort()
            return
        }

        // 验证JWT token
        claims, err := ValidateJWTToken(token)
        if err != nil {
            c.JSON(401, gin.H{"error": "Invalid token"})
            c.Abort()
            return
        }

        // 将用户信息存储在上下文中
        c.Set("user_id", claims.UserID)
        c.Set("user_role", claims.Role)

        c.Next()
    }
}

// 管理员权限中间件
func AdminMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        role, exists := c.Get("user_role")
        if !exists {
            c.JSON(401, gin.H{"error": "User not authenticated"})
            c.Abort()
            return
        }

        if role != "admin" {
            c.JSON(403, gin.H{"error": "Insufficient permissions"})
            c.Abort()
            return
        }

        c.Next()
    }
}

// JWT Claims
type JWTClaims struct {
    UserID string `json:"user_id"`
    Role   string `json:"role"`
    Exp    int64  `json:"exp"`
}

// 验证JWT token（简化版）
func ValidateJWTToken(token string) (*JWTClaims, error) {
    // 这里应该使用实际的JWT库进行验证
    // 例如：github.com/golang-jwt/jwt

    // 简化的验证逻辑
    if token == "valid-admin-token" {
        return &JWTClaims{
            UserID: "admin-id",
            Role:   "admin",
            Exp:    time.Now().Add(time.Hour).Unix(),
        }, nil
    }

    return nil, fmt.Errorf("invalid token")
}
```

## 中间件链

### 中间件链执行顺序
```go
func main() {
    r := gin.New()

    // 中间件链
    r.Use(Middleware1())
    r.Use(Middleware2())
    r.Use(Middleware3())

    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    r.Run(":8080")
}

func Middleware1() gin.HandlerFunc {
    return func(c *gin.Context) {
        fmt.Println("Middleware 1 - Before")
        c.Next()
        fmt.Println("Middleware 1 - After")
    }
}

func Middleware2() gin.HandlerFunc {
    return func(c *gin.Context) {
        fmt.Println("Middleware 2 - Before")
        c.Next()
        fmt.Println("Middleware 2 - After")
    }
}

func Middleware3() gin.HandlerFunc {
    return func(c *gin.Context) {
        fmt.Println("Middleware 3 - Before")
        c.Next()
        fmt.Println("Middleware 3 - After")
    }
}
```

### 条件中间件链
```go
func main() {
    r := gin.New()

    // 条件中间件
    r.Use(func(c *gin.Context) {
        // 根据路径条件使用中间件
        if strings.HasPrefix(c.Request.URL.Path, "/api") {
            // API路径使用认证中间件
            JWTAuthMiddleware()(c)
        }
        c.Next()
    })

    r.Use(func(c *gin.Context) {
        // 根据环境条件使用中间件
        if os.Getenv("ENV") == "production" {
            SecurityHeadersMiddleware()(c)
        }
        c.Next()
    })

    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    r.GET("/api/users", func(c *gin.Context) {
        c.JSON(200, gin.H{"users": []string{"user1", "user2"}})
    })

    r.Run(":8080")
}
```

## 中间件参数

### 带参数的中间件
```go
func main() {
    r := gin.Default()

    // 带参数的中间件
    r.Use(RateLimitMiddleware(100, time.Minute))
    r.Use(LoggerMiddleware(true))

    // 路由组使用参数化中间件
    api := r.Group("/api")
    api.Use(CORSMiddleware([]string{"http://localhost:3000"}))
    {
        api.GET("/users", GetUsers)
        api.POST("/users", CreateUser)
    }

    r.Run(":8080")
}

// 带参数的限流中间件
func RateLimitMiddleware(maxRequests int, window time.Duration) gin.HandlerFunc {
    limiter := make(map[string]int)
    lastReset := make(map[string]time.Time)
    mutex := &sync.Mutex{}

    return func(c *gin.Context) {
        ip := c.ClientIP()

        mutex.Lock()
        defer mutex.Unlock()

        // 检查时间窗口
        if lastReset[ip].Add(window).Before(time.Now()) {
            limiter[ip] = 0
            lastReset[ip] = time.Now()
        }

        // 检查限流
        if limiter[ip] >= maxRequests {
            c.JSON(429, gin.H{
                "error": "Rate limit exceeded",
                "reset_in": lastReset[ip].Add(window).Sub(time.Now()),
            })
            c.Abort()
            return
        }

        limiter[ip]++
        c.Next()
    }
}

// 带参数的日志中间件
func LoggerMiddleware(enableColors bool) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        method := c.Request.Method

        c.Next()

        duration := time.Since(start)
        status := c.Writer.Status()

        if enableColors {
            // 带颜色的日志输出
            switch {
            case status >= 500:
                fmt.Printf("\033[31m%s %s %d %v\033[0m\n", method, path, status, duration)
            case status >= 400:
                fmt.Printf("\033[33m%s %s %d %v\033[0m\n", method, path, status, duration)
            default:
                fmt.Printf("\033[32m%s %s %d %v\033[0m\n", method, path, status, duration)
            }
        } else {
            fmt.Printf("%s %s %d %v\n", method, path, status, duration)
        }
    }
}

// 带参数的CORS中间件
func CORSMiddleware(allowedOrigins []string) gin.HandlerFunc {
    return func(c *gin.Context) {
        origin := c.Request.Header.Get("Origin")

        // 检查是否允许该源
        allowed := false
        for _, allowedOrigin := range allowedOrigins {
            if origin == allowedOrigin {
                allowed = true
                break
            }
        }

        if allowed {
            c.Header("Access-Control-Allow-Origin", origin)
            c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            c.Header("Access-Control-Allow-Credentials", "true")
        }

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }

        c.Next()
    }
}
```

## 中间件最佳实践

### 中间件设计原则
```go
func main() {
    r := gin.Default()

    // 1. 早期验证和拒绝
    r.Use(ValidationMiddleware())

    // 2. 日志和监控
    r.Use(MonitoringMiddleware())

    // 3. 认证和授权
    r.Use(AuthenticationMiddleware())

    // 4. 业务相关中间件
    r.Use(BusinessMiddleware())

    // 5. 错误处理
    r.Use(ErrorHandlingMiddleware())

    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    r.Run(":8080")
}

// 验证中间件 - 早期验证
func ValidationMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 验证必需的头部
        if c.GetHeader("Content-Type") == "" {
            c.JSON(400, gin.H{"error": "Content-Type header is required"})
            c.Abort()
            return
        }

        // 验证请求大小
        if c.Request.ContentLength > 10*1024*1024 { // 10MB
            c.JSON(413, gin.H{"error": "Request too large"})
            c.Abort()
            return
        }

        c.Next()
    }
}

// 监控中间件
func MonitoringMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        c.Next()

        duration := time.Since(start)
        status := c.Writer.Status()

        // 记录监控指标
        RecordMetrics(c.Request.Method, c.Request.URL.Path, status, duration)
    }
}

// 认证中间件
func AuthenticationMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查认证信息
        token := c.GetHeader("Authorization")
        if token == "" {
            c.JSON(401, gin.H{"error": "Authentication required"})
            c.Abort()
            return
        }

        // 验证token
        if !ValidateToken(token) {
            c.JSON(401, gin.H{"error": "Invalid token"})
            c.Abort()
            return
        }

        c.Next()
    }
}

// 业务中间件
func BusinessMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 设置业务相关的上下文
        c.Set("request_id", GenerateRequestID())
        c.Set("timestamp", time.Now())

        c.Next()
    }
}

// 错误处理中间件
func ErrorHandlingMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        defer func() {
            if err := recover(); err != nil {
                HandleError(c, err)
            }
        }()
        c.Next()
    }
}
```

### 中间件错误处理
```go
func main() {
    r := gin.New()

    // 错误处理中间件
    r.Use(ErrorHandlingMiddleware())

    // 恢复中间件
    r.Use(gin.Recovery())

    r.GET("/error", func(c *gin.Context) {
        // 模拟错误
        panic("Something went wrong")
    })

    r.Run(":8080")
}

// 全局错误处理中间件
func ErrorHandlingMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        defer func() {
            if err := recover(); err != nil {
                // 记录错误
                log.Printf("Error occurred: %v", err)

                // 根据错误类型返回不同的响应
                switch e := err.(type) {
                case *APIError:
                    c.JSON(e.StatusCode, gin.H{
                        "error": e.Message,
                        "code":  e.Code,
                    })
                case ValidationError:
                    c.JSON(400, gin.H{
                        "error": "Validation failed",
                        "details": e.Details,
                    })
                default:
                    c.JSON(500, gin.H{
                        "error": "Internal server error",
                    })
                }

                c.Abort()
            }
        }()
        c.Next()
    }
}

// 自定义错误类型
type APIError struct {
    StatusCode int
    Code       string
    Message    string
}

func (e *APIError) Error() string {
    return e.Message
}

type ValidationError struct {
    Details map[string]string
}

func (e *ValidationError) Error() string {
    return "Validation failed"
}
```

## 中间件性能优化

### 性能优化策略
```go
func main() {
    r := gin.New()

    // 1. 路由级别的中间件
    r.Use(GlobalOptimizedMiddleware())

    // 2. 组级别的中间件
    api := r.Group("/api")
    api.Use(APIOptimizedMiddleware())
    {
        api.GET("/users", GetUsers)
        api.POST("/users", CreateUser)
    }

    // 3. 路由级别的中间件
    r.GET("/health", HealthCheckMiddleware(), HealthCheck)

    r.Run(":8080")
}

// 全局优化中间件
func GlobalOptimizedMiddleware() gin.HandlerFunc {
    // 使用sync.Pool优化内存分配
    var pool = sync.Pool{
        New: func() interface{} {
            return make(map[string]interface{})
        },
    }

    return func(c *gin.Context) {
        // 从池中获取map
        data := pool.Get().(map[string]interface{})
        defer pool.Put(data)

        // 重置map
        for k := range data {
            delete(data, k)
        }

        // 设置上下文数据
        data["start_time"] = time.Now()
        c.Set("data", data)

        c.Next()
    }
}

// API优化中间件
func APIOptimizedMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 缓存常用的验证结果
        if cached, ok := c.Get("validation_cache"); ok {
            if valid, ok := cached.(bool); ok && valid {
                c.Next()
                return
            }
        }

        // 执行验证
        valid := ValidateAPIRequest(c)
        c.Set("validation_cache", valid)

        if !valid {
            c.JSON(400, gin.H{"error": "Invalid request"})
            c.Abort()
            return
        }

        c.Next()
    }
}

// 健康检查中间件
func HealthCheckMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 轻量级健康检查
        if err := CheckDatabaseHealth(); err != nil {
            c.JSON(503, gin.H{"status": "unhealthy"})
            c.Abort()
            return
        }

        c.Next()
    }
}
```

### 中间件基准测试
```go
package main

import (
    "net/http"
    "net/http/httptest"
    "testing"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

// 中间件性能测试
func BenchmarkMiddleware(b *testing.B) {
    r := setupBenchmarkRouter()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        req, _ := http.NewRequest("GET", "/api/users", nil)
        w := httptest.NewRecorder()
        r.ServeHTTP(w, req)
    }
}

// 设置基准测试路由
func setupBenchmarkRouter() *gin.Engine {
    r := gin.New()

    // 使用优化的中间件
    r.Use(OptimizedLoggerMiddleware())
    r.Use(OptimizedAuthMiddleware())

    api := r.Group("/api")
    api.Use(OptimizedCORSMiddleware())
    {
        api.GET("/users", func(c *gin.Context) {
            c.JSON(200, gin.H{"users": []string{"user1", "user2"}})
        })
    }

    return r
}

// 优化的日志中间件
func OptimizedLoggerMiddleware() gin.HandlerFunc {
    // 预分配缓冲区
    buffer := make([]byte, 0, 256)

    return func(c *gin.Context) {
        start := time.Now()

        c.Next()

        // 使用缓冲区减少内存分配
        buffer = buffer[:0]
        buffer = append(buffer, []byte(c.Request.Method)...)
        buffer = append(buffer, ' ')
        buffer = append(buffer, []byte(c.Request.URL.Path)...)
        buffer = append(buffer, ' ')
        buffer = append(buffer, []byte(c.Writer.Status())...)

        // 写入日志
        fmt.Println(string(buffer))
    }
}

// 优化的认证中间件
func OptimizedAuthMiddleware() gin.HandlerFunc {
    // 缓存有效的token
    validTokens := make(map[string]bool)
    mutex := &sync.RWMutex{}

    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.AbortWithStatus(401)
            return
        }

        // 从缓存中检查
        mutex.RLock()
        valid := validTokens[token]
        mutex.RUnlock()

        if !valid {
            // 验证token
            valid = ValidateToken(token)
            if valid {
                mutex.Lock()
                validTokens[token] = true
                mutex.Unlock()
            }
        }

        if !valid {
            c.AbortWithStatus(401)
            return
        }

        c.Next()
    }
}

// 优化的CORS中间件
func OptimizedCORSMiddleware() gin.HandlerFunc {
    // 预构建CORS头部
    headers := map[string]string{
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Credentials": "true",
    }

    return func(c *gin.Context) {
        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }

        // 批量设置头部
        for key, value := range headers {
            c.Header(key, value)
        }

        c.Next()
    }
}
```

## 🚀 高级中间件模式

### 1. 中间件工厂模式

```go
// 中间件工厂 - 创建不同类型的中间件
type MiddlewareFactory struct {
    config *MiddlewareConfig
}

type MiddlewareConfig struct {
    EnableLogging     bool
    EnableAuth        bool
    EnableRateLimit   bool
    EnableCORS       bool
    LogFormat        string
    RateLimitCount   int
    RateLimitWindow  time.Duration
    AllowedOrigins   []string
}

func NewMiddlewareFactory(config *MiddlewareConfig) *MiddlewareFactory {
    return &MiddlewareFactory{config: config}
}

// 创建日志中间件
func (mf *MiddlewareFactory) CreateLogger() gin.HandlerFunc {
    if !mf.config.EnableLogging {
        return func(c *gin.Context) { c.Next() }
    }

    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        method := c.Request.Method

        c.Next()

        duration := time.Since(start)
        status := c.Writer.Status()

        // 自定义日志格式
        logEntry := fmt.Sprintf(mf.config.LogFormat,
            method, path, status, duration,
            c.ClientIP(), c.Request.UserAgent(),
        )

        fmt.Println(logEntry)
    }
}

// 创建认证中间件
func (mf *MiddlewareFactory) CreateAuth() gin.HandlerFunc {
    if !mf.config.EnableAuth {
        return func(c *gin.Context) { c.Next() }
    }

    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.JSON(401, gin.H{"error": "No token provided"})
            c.Abort()
            return
        }

        // 验证token
        if !mf.validateToken(token) {
            c.JSON(401, gin.H{"error": "Invalid token"})
            c.Abort()
            return
        }

        c.Next()
    }
}

// 创建限流中间件
func (mf *MiddlewareFactory) CreateRateLimiter() gin.HandlerFunc {
    if !mf.config.EnableRateLimit {
        return func(c *gin.Context) { c.Next() }
    }

    limiter := rate.NewLimiter(rate.Limit(mf.config.RateLimitCount), mf.config.RateLimitCount)

    return func(c *gin.Context) {
        ip := c.ClientIP()

        if !limiter.Allow() {
            c.JSON(429, gin.H{"error": "Rate limit exceeded"})
            c.Abort()
            return
        }

        c.Next()
    }
}

// 创建CORS中间件
func (mf *MiddlewareFactory) CreateCORS() gin.HandlerFunc {
    if !mf.config.EnableCORS {
        return func(c *gin.Context) { c.Next() }
    }

    return func(c *gin.Context) {
        origin := c.Request.Header.Get("Origin")

        // 检查是否允许该源
        for _, allowedOrigin := range mf.config.AllowedOrigins {
            if origin == allowedOrigin {
                c.Header("Access-Control-Allow-Origin", origin)
                c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                c.Header("Access-Control-Allow-Credentials", "true")
                break
            }
        }

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }

        c.Next()
    }
}

func (mf *MiddlewareFactory) validateToken(token string) bool {
    // 实际实现中应该使用JWT或其他认证机制
    return token == "valid-token"
}
```

### 2. 中间件装饰器模式

```go
// 中间件装饰器 - 为现有中间件添加功能
type MiddlewareDecorator interface {
    Decorate(gin.HandlerFunc) gin.HandlerFunc
}

// 缓存装饰器
type CacheDecorator struct {
    cache *sync.Map
    ttl   time.Duration
}

func NewCacheDecorator(ttl time.Duration) *CacheDecorator {
    return &CacheDecorator{
        cache: &sync.Map{},
        ttl:   ttl,
    }
}

func (cd *CacheDecorator) Decorate(next gin.HandlerFunc) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 生成缓存键
        key := fmt.Sprintf("%s:%s", c.Request.Method, c.Request.URL.Path)

        // 检查缓存
        if cached, found := cd.cache.Load(key); found {
            c.JSON(200, cached)
            c.Abort()
            return
        }

        // 执行原始中间件
        next(c)

        // 缓存响应（简化版）
        if len(c.Errors) == 0 {
            cd.cache.Store(key, "cached_response")
        }
    }
}

// 监控装饰器
type MonitoringDecorator struct {
    metrics *MiddlewareMetrics
}

type MiddlewareMetrics struct {
    RequestCount   int64
    ErrorCount     int64
    TotalDuration  time.Duration
    mutex          sync.RWMutex
}

func NewMonitoringDecorator() *MonitoringDecorator {
    return &MonitoringDecorator{
        metrics: &MiddlewareMetrics{},
    }
}

func (md *MonitoringDecorator) Decorate(next gin.HandlerFunc) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        next(c)

        duration := time.Since(start)

        // 更新监控指标
        md.metrics.mutex.Lock()
        md.metrics.RequestCount++
        md.metrics.TotalDuration += duration
        if len(c.Errors) > 0 {
            md.metrics.ErrorCount++
        }
        md.metrics.mutex.Unlock()
    }
}

// 使用装饰器
func DecorateMiddleware(base gin.HandlerFunc, decorators ...MiddlewareDecorator) gin.HandlerFunc {
    result := base

    // 按顺序应用装饰器
    for _, decorator := range decorators {
        result = decorator.Decorate(result)
    }

    return result
}
```

### 3. 中间件链模式

```go
// 中间件链管理器
type MiddlewareChain struct {
    middlewares []gin.HandlerFunc
    mutex       sync.RWMutex
}

func NewMiddlewareChain() *MiddlewareChain {
    return &MiddlewareChain{
        middlewares: make([]gin.HandlerFunc, 0),
    }
}

// 添加中间件
func (mc *MiddlewareChain) Use(middleware gin.HandlerFunc) {
    mc.mutex.Lock()
    defer mc.mutex.Unlock()
    mc.middlewares = append(mc.middlewares, middleware)
}

// 插入中间件到指定位置
func (mc *MiddlewareChain) Insert(index int, middleware gin.HandlerFunc) {
    mc.mutex.Lock()
    defer mc.mutex.Unlock()

    if index < 0 || index > len(mc.middlewares) {
        return
    }

    mc.middlewares = append(mc.middlewares[:index],
        append([]gin.HandlerFunc{middleware}, mc.middlewares[index:]...)...)
}

// 移除中间件
func (mc *MiddlewareChain) Remove(index int) {
    mc.mutex.Lock()
    defer mc.mutex.Unlock()

    if index < 0 || index >= len(mc.middlewares) {
        return
    }

    mc.middlewares = append(mc.middlewares[:index], mc.middlewares[index+1:]...)
}

// 执行中间件链
func (mc *MiddlewareChain) Execute(c *gin.Context, handler gin.HandlerFunc) {
    mc.mutex.RLock()
    middlewares := make([]gin.HandlerFunc, len(mc.middlewares))
    copy(middlewares, mc.middlewares)
    mc.mutex.RUnlock()

    // 创建执行链
    chain := make([]gin.HandlerFunc, 0, len(middlewares)+1)
    chain = append(chain, middlewares...)
    chain = append(chain, handler)

    // 执行链
    for i, middleware := range chain {
        if i < len(chain)-1 {
            middleware(c)
            if c.IsAborted() {
                break
            }
        } else {
            // 最后一个中间件
            middleware(c)
        }
    }
}
```

### 4. 条件中间件

```go
// 条件中间件管理器
type ConditionalMiddleware struct {
    conditions map[string]func(*gin.Context) bool
    middlewares map[string]gin.HandlerFunc
    mutex      sync.RWMutex
}

func NewConditionalMiddleware() *ConditionalMiddleware {
    return &ConditionalMiddleware{
        conditions: make(map[string]func(*gin.Context) bool),
        middlewares: make(map[string]gin.HandlerFunc),
    }
}

// 注册条件中间件
func (cm *ConditionalMiddleware) Register(name string,
    condition func(*gin.Context) bool,
    middleware gin.HandlerFunc) {

    cm.mutex.Lock()
    defer cm.mutex.Unlock()

    cm.conditions[name] = condition
    cm.middlewares[name] = middleware
}

// 条件中间件执行器
func (cm *ConditionalMiddleware) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        cm.mutex.RLock()
        defer cm.mutex.RUnlock()

        // 执行所有满足条件的中间件
        for name, condition := range cm.conditions {
            if condition(c) {
                middleware := cm.middlewares[name]
                middleware(c)
                if c.IsAborted() {
                    return
                }
            }
        }

        c.Next()
    }
}

// 预定义条件
func PathPrefixCondition(prefix string) func(*gin.Context) bool {
    return func(c *gin.Context) bool {
        return strings.HasPrefix(c.Request.URL.Path, prefix)
    }
}

func MethodCondition(method string) func(*gin.Context) bool {
    return func(c *gin.Context) bool {
        return c.Request.Method == method
    }
}

func HeaderCondition(header, value string) func(*gin.Context) bool {
    return func(c *gin.Context) bool {
        return c.GetHeader(header) == value
    }
}

func UserAgentCondition(pattern string) func(*gin.Context) bool {
    regex, err := regexp.Compile(pattern)
    if err != nil {
        return func(*gin.Context) bool { return false }
    }

    return func(c *gin.Context) bool {
        return regex.MatchString(c.GetHeader("User-Agent"))
    }
}
```

## 🧪 中间件测试

### 1. 单元测试

```go
package middleware_test

import (
    "net/http"
    "net/http/httptest"
    "testing"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

// 测试认证中间件
func TestAuthMiddleware(t *testing.T) {
    // 设置Gin为测试模式
    gin.SetMode(gin.TestMode)

    tests := []struct {
        name         string
        token        string
        expectedCode int
        expectedBody map[string]interface{}
    }{
        {
            name:         "Valid token",
            token:        "valid-token",
            expectedCode: 200,
            expectedBody: map[string]interface{}{"message": "success"},
        },
        {
            name:         "No token",
            token:        "",
            expectedCode:  401,
            expectedBody: map[string]interface{}{"error": "No token provided"},
        },
        {
            name:         "Invalid token",
            token:        "invalid-token",
            expectedCode:  401,
            expectedBody: map[string]interface{}{"error": "Invalid token"},
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // 创建路由
            r := gin.New()
            r.Use(AuthMiddleware())
            r.GET("/test", func(c *gin.Context) {
                c.JSON(200, gin.H{"message": "success"})
            })

            // 创建请求
            req, _ := http.NewRequest("GET", "/test", nil)
            if tt.token != "" {
                req.Header.Set("Authorization", tt.token)
            }

            // 记录响应
            w := httptest.NewRecorder()
            r.ServeHTTP(w, req)

            // 验证响应
            assert.Equal(t, tt.expectedCode, w.Code)

            var response map[string]interface{}
            err := json.Unmarshal(w.Body.Bytes(), &response)
            assert.NoError(t, err)
            assert.Equal(t, tt.expectedBody, response)
        })
    }
}

// 测试限流中间件
func TestRateLimitMiddleware(t *testing.T) {
    gin.SetMode(gin.TestMode)

    // 创建带限流的路由
    r := gin.New()
    r.Use(RateLimitMiddleware(2, time.Second))
    r.GET("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "success"})
    })

    // 发送3个请求
    responses := make([]int, 3)
    for i := 0; i < 3; i++ {
        req, _ := http.NewRequest("GET", "/test", nil)
        w := httptest.NewRecorder()
        r.ServeHTTP(w, req)
        responses[i] = w.Code
    }

    // 前两个请求应该成功，第三个应该被限流
    assert.Equal(t, 200, responses[0])
    assert.Equal(t, 200, responses[1])
    assert.Equal(t, 429, responses[2])
}

// 基准测试
func BenchmarkAuthMiddleware(b *testing.B) {
    gin.SetMode(gin.TestMode)

    r := gin.New()
    r.Use(AuthMiddleware())
    r.GET("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "success"})
    })

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        req, _ := http.NewRequest("GET", "/test", nil)
        req.Header.Set("Authorization", "valid-token")
        w := httptest.NewRecorder()
        r.ServeHTTP(w, req)
    }
}
```

### 2. 集成测试

```go
// 中间件集成测试
func TestMiddlewareIntegration(t *testing.T) {
    gin.SetMode(gin.TestMode)

    // 创建测试服务器
    r := setupTestServer()

    tests := []struct {
        name           string
        path           string
        method         string
        headers        map[string]string
        expectedCode   int
        expectedHeader map[string]string
    }{
        {
            name:   "Public API without auth",
            path:   "/public/health",
            method: "GET",
            expectedCode: 200,
        },
        {
            name:   "Protected API without auth",
            path:   "/api/users",
            method: "GET",
            expectedCode: 401,
        },
        {
            name:   "Protected API with auth",
            path:   "/api/users",
            method: "GET",
            headers: map[string]string{"Authorization": "valid-token"},
            expectedCode: 200,
            expectedHeader: map[string]string{"X-Rate-Limit": "100"},
        },
        {
            name:   "CORS preflight",
            path:   "/api/users",
            method: "OPTIONS",
            expectedCode: 204,
            expectedHeader: map[string]string{
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // 创建请求
            req, _ := http.NewRequest(tt.method, tt.path, nil)

            // 设置头部
            for key, value := range tt.headers {
                req.Header.Set(key, value)
            }

            // 记录响应
            w := httptest.NewRecorder()
            r.ServeHTTP(w, req)

            // 验证响应码
            assert.Equal(t, tt.expectedCode, w.Code)

            // 验证头部
            for key, expectedValue := range tt.expectedHeader {
                assert.Equal(t, expectedValue, w.Header().Get(key))
            }
        })
    }
}

// 设置测试服务器
func setupTestServer() *gin.Engine {
    r := gin.New()

    // 全局中间件
    r.Use(gin.Logger())
    r.Use(gin.Recovery())
    r.Use(SecurityHeadersMiddleware())

    // 公共路由
    public := r.Group("/public")
    {
        public.GET("/health", func(c *gin.Context) {
            c.JSON(200, gin.H{"status": "healthy"})
        })
    }

    // API路由
    api := r.Group("/api")
    api.Use(CORSMiddleware([]string{"*"}))
    api.Use(RateLimitMiddleware(100, time.Minute))
    {
        api.Use(AuthMiddleware())
        api.GET("/users", func(c *gin.Context) {
            c.Header("X-Rate-Limit", "100")
            c.JSON(200, gin.H{"users": []string{}})
        })
    }

    return r
}
```

## 🎯 实战案例

### 1. 微服务中间件架构

```go
// 微服务中间件管理器
type MicroserviceMiddleware struct {
    factory      *MiddlewareFactory
    conditional  *ConditionalMiddleware
    monitoring   *MonitoringDecorator
    cache        *CacheDecorator
}

func NewMicroserviceMiddleware(config *MiddlewareConfig) *MicroserviceMiddleware {
    factory := NewMiddlewareFactory(config)
    conditional := NewConditionalMiddleware()
    monitoring := NewMonitoringDecorator()
    cache := NewCacheDecorator(5 * time.Minute)

    return &MicroserviceMiddleware{
        factory:     factory,
        conditional: conditional,
        monitoring:  monitoring,
        cache:       cache,
    }
}

// 设置服务中间件
func (mm *MicroserviceMiddleware) SetupService(r *gin.Engine) {
    // 全局中间件
    r.Use(mm.factory.CreateLogger())
    r.Use(mm.factory.CreateCORS())
    r.Use(SecurityHeadersMiddleware())
    r.Use(mm.monitoring.Decorate(func(c *gin.Context) { c.Next() }))

    // 健康检查 - 不需要认证
    health := r.Group("/health")
    {
        health.GET("", func(c *gin.Context) {
            c.JSON(200, gin.H{"status": "healthy"})
        })
        health.GET("/ready", func(c *gin.Context) {
            c.JSON(200, gin.H{"status": "ready"})
        })
    }

    // API路由
    api := r.Group("/api/v1")
    {
        // 公共API
        public := api.Group("/public")
        {
            public.GET("/info", func(c *gin.Context) {
                c.JSON(200, gin.H{"version": "1.0.0"})
            })
        }

        // 需要认证的API
        protected := api.Group("")
        protected.Use(mm.factory.CreateAuth())
        protected.Use(mm.factory.CreateRateLimiter())
        {
            // 用户服务
            users := protected.Group("/users")
            users.Use(mm.cache.Decorate(func(c *gin.Context) { c.Next() }))
            {
                users.GET("", GetUsers)
                users.GET("/:id", GetUser)
                users.POST("", CreateUser)
                users.PUT("/:id", UpdateUser)
                users.DELETE("/:id", DeleteUser)
            }

            // 订单服务
            orders := protected.Group("/orders")
            {
                orders.GET("", GetOrders)
                orders.POST("", CreateOrder)
                orders.GET("/:id", GetOrder)
                orders.PUT("/:id", UpdateOrder)
            }

            // 产品服务
            products := protected.Group("/products")
            {
                products.GET("", GetProducts)
                products.GET("/:id", GetProduct)
                products.POST("", CreateProduct)
                products.PUT("/:id", UpdateProduct)
            }
        }

        // 管理员API
        admin := api.Group("/admin")
        admin.Use(mm.factory.CreateAuth())
        admin.Use(AdminMiddleware())
        {
            admin.GET("/dashboard", GetAdminDashboard)
            admin.GET("/users", GetAllUsers)
            admin.GET("/orders", GetAllOrders)
        }
    }

    // 注册条件中间件
    mm.conditional.Register("api-monitoring",
        PathPrefixCondition("/api"),
        APIMonitoringMiddleware(),
    )

    mm.conditional.Register("mobile-optimization",
        UserAgentCondition(".*Mobile.*"),
        MobileOptimizationMiddleware(),
    )

    // 应用条件中间件
    r.Use(mm.conditional.Middleware())
}

// API监控中间件
func APIMonitoringMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        c.Next()

        duration := time.Since(start)
        status := c.Writer.Status()

        // 记录API指标
        RecordAPIMetrics(c.Request.Method, c.Request.URL.Path, status, duration)
    }
}

// 移动端优化中间件
func MobileOptimizationMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 添加移动端优化头部
        c.Header("X-Mobile-Optimized", "true")
        c.Header("Cache-Control", "max-age=300")

        // 压缩响应
        if strings.Contains(c.GetHeader("Accept-Encoding"), "gzip") {
            c.Header("Content-Encoding", "gzip")
        }

        c.Next()
    }
}
```

### 2. 高级认证与授权中间件

```go
// JWT认证中间件
type JWTAuthMiddleware struct {
    secretKey      []byte
    tokenBlacklist *sync.Map
    validator     TokenValidator
}

type TokenValidator interface {
    Validate(token string) (*Claims, error)
    Refresh(token string) (string, error)
}

type Claims struct {
    UserID    string   `json:"user_id"`
    Username  string   `json:"username"`
    Roles     []string `json:"roles"`
    ExpiresAt int64   `json:"exp"`
    IssuedAt  int64   `json:"iat"`
}

func NewJWTAuthMiddleware(secretKey string, validator TokenValidator) *JWTAuthMiddleware {
    return &JWTAuthMiddleware{
        secretKey:      []byte(secretKey),
        tokenBlacklist: &sync.Map{},
        validator:     validator,
    }
}

func (m *JWTAuthMiddleware) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := m.extractToken(c)
        if token == "" {
            c.JSON(401, gin.H{"error": "No token provided"})
            c.Abort()
            return
        }

        // 检查黑名单
        if m.isTokenBlacklisted(token) {
            c.JSON(401, gin.H{"error": "Token revoked"})
            c.Abort()
            return
        }

        // 验证token
        claims, err := m.validator.Validate(token)
        if err != nil {
            c.JSON(401, gin.H{"error": "Invalid token"})
            c.Abort()
            return
        }

        // 检查过期
        if time.Now().Unix() > claims.ExpiresAt {
            c.JSON(401, gin.H{"error": "Token expired"})
            c.Abort()
            return
        }

        // 设置用户信息到上下文
        c.Set("user_id", claims.UserID)
        c.Set("username", claims.Username)
        c.Set("roles", claims.Roles)
        c.Set("claims", claims)

        c.Next()
    }
}

func (m *JWTAuthMiddleware) extractToken(c *gin.Context) string {
    authHeader := c.GetHeader("Authorization")
    if authHeader == "" {
        return ""
    }

    // Bearer token格式
    parts := strings.Split(authHeader, " ")
    if len(parts) != 2 || parts[0] != "Bearer" {
        return ""
    }

    return parts[1]
}

func (m *JWTAuthMiddleware) isTokenBlacklisted(token string) bool {
    _, blacklisted := m.tokenBlacklist.Load(token)
    return blacklisted
}

func (m *JWTAuthMiddleware) BlacklistToken(token string) {
    m.tokenBlacklist.Store(token, true)
}

// RBAC权限中间件
type RBACMiddleware struct {
    rolePermissions map[string][]string
    enforcer       *Enforcer
}

type Enforcer struct {
    policies map[string]map[string]bool
    mutex    sync.RWMutex
}

func NewRBACMiddleware() *RBACMiddleware {
    return &RBACMiddleware{
        rolePermissions: make(map[string][]string),
        enforcer: &Enforcer{
            policies: make(map[string]map[string]bool),
        },
    }
}

func (m *RBACMiddleware) AddPermission(role, permission string) {
    m.rolePermissions[role] = append(m.rolePermissions[role], permission)
}

func (m *RBACMiddleware) AddPolicy(role, resource, action string) {
    m.enforcer.mutex.Lock()
    defer m.enforcer.mutex.Unlock()

    key := fmt.Sprintf("%s:%s", role, resource)
    if _, exists := m.enforcer.policies[key]; !exists {
        m.enforcer.policies[key] = make(map[string]bool)
    }
    m.enforcer.policies[key][action] = true
}

func (m *RBACMiddleware) Middleware(requiredPermissions ...string) gin.HandlerFunc {
    return func(c *gin.Context) {
        roles, exists := c.Get("roles")
        if !exists {
            c.JSON(401, gin.H{"error": "User not authenticated"})
            c.Abort()
            return
        }

        userRoles := roles.([]string)
        resource := c.Request.URL.Path
        action := c.Request.Method

        // 检查权限
        if !m.enforcer.Enforce(userRoles, resource, action) {
            c.JSON(403, gin.H{"error": "Insufficient permissions"})
            c.Abort()
            return
        }

        c.Next()
    }
}

func (e *Enforcer) Enforce(roles []string, resource, action string) bool {
    e.mutex.RLock()
    defer e.mutex.RUnlock()

    for _, role := range roles {
        key := fmt.Sprintf("%s:%s", role, resource)
        if policies, exists := e.policies[key]; exists {
            if policies[action] || policies["*"] {
                return true
            }
        }
    }

    return false
}
```

这个全面的Gin中间件基础与高级模式文档涵盖了：

1. **中间件基础**：概念、内置中间件、自定义中间件开发
2. **中间件链**：执行顺序、条件中间件链、中间件组合
3. **中间件参数**：参数化中间件、配置管理、工厂模式
4. **中间件最佳实践**：设计原则、错误处理、性能优化
5. **高级中间件模式**：工厂模式、装饰器模式、链模式、条件中间件
6. **中间件测试**：单元测试、集成测试、基准测试
7. **实战案例**：微服务架构、JWT认证、RBAC权限、监控中间件
8. **性能优化**：缓存、连接池、内存优化、并发处理

这个文档为Go开发者提供了Gin框架中间件系统的完整指南，从基础概念到高级架构模式，帮助开发者构建安全、高效、可维护的Web应用中间件系统。