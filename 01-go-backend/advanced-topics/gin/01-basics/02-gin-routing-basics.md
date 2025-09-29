# Gin路由基础与高级用法

## 📚 目录

- [路由基础](#路由基础)
- [路由组](#路由组)
- [路由参数](#路由参数)
- [路由冲突处理](#路由冲突处理)
- [路由性能优化](#路由性能优化)
- [高级路由模式](#高级路由模式)
- [路由中间件集成](#路由中间件集成)
- [最佳实践](#最佳实践)
- [实战案例](#实战案例)

## 路由基础

### 基本路由定义
```go
package main

import (
    "github.com/gin-gonic/gin"
    "net/http"
)

func main() {
    r := gin.Default()

    // GET路由
    r.GET("/users", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"message": "Get all users"})
    })

    // POST路由
    r.POST("/users", func(c *gin.Context) {
        c.JSON(http.StatusCreated, gin.H{"message": "User created"})
    })

    // PUT路由
    r.PUT("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{"message": "User updated", "id": id})
    })

    // DELETE路由
    r.DELETE("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{"message": "User deleted", "id": id})
    })

    r.Run(":8080")
}
```

### Any方法 - 匹配所有HTTP方法
```go
func main() {
    r := gin.Default()

    // 匹配所有HTTP方法
    r.Any("/test", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "method": c.Request.Method,
            "path":   c.Request.URL.Path,
        })
    })

    r.Run(":8080")
}
```

## 路由参数

### 路径参数
```go
func main() {
    r := gin.Default()

    // 简单参数
    r.GET("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{"id": id})
    })

    // 带参数类型
    r.GET("/users/:id/posts/:postId", func(c *gin.Context) {
        userId := c.Param("id")
        postId := c.Param("postId")
        c.JSON(http.StatusOK, gin.H{
            "user_id":  userId,
            "post_id": postId,
        })
    })

    // 通配符参数
    r.GET("/files/*filepath", func(c *gin.Context) {
        filepath := c.Param("filepath")
        c.JSON(http.StatusOK, gin.H{"filepath": filepath})
    })

    r.Run(":8080")
}
```

### 查询参数
```go
func main() {
    r := gin.Default()

    r.GET("/search", func(c *gin.Context) {
        // 获取单个查询参数
        query := c.DefaultQuery("q", "default")
        page := c.DefaultQuery("page", "1")
        limit := c.Query("limit")

        // 获取多个同名查询参数
        tags := c.QueryArray("tags")

        // 获取查询参数映射
        filters := c.QueryMap("filters")

        c.JSON(http.StatusOK, gin.H{
            "query":   query,
            "page":    page,
            "limit":   limit,
            "tags":    tags,
            "filters": filters,
        })
    })

    r.Run(":8080")
}
```

### 表单参数
```go
func main() {
    r := gin.Default()

    r.POST("/form", func(c *gin.Context) {
        // 获取表单字段
        name := c.PostForm("name")
        email := c.PostForm("email")

        // 获取多个同名表单字段
        hobbies := c.PostFormArray("hobbies")

        // 获取表单映射
        metadata := c.PostFormMap("metadata")

        // 获取上传的文件
        file, _ := c.FormFile("avatar")

        c.JSON(http.StatusOK, gin.H{
            "name":     name,
            "email":    email,
            "hobbies":  hobbies,
            "metadata": metadata,
            "file":     file.Filename,
        })
    })

    r.Run(":8080")
}
```

## 路由组

### 基本路由组
```go
func main() {
    r := gin.Default()

    // 创建API路由组
    api := r.Group("/api")
    {
        // 用户相关路由
        userGroup := api.Group("/users")
        {
            userGroup.GET("", GetUsers)
            userGroup.POST("", CreateUser)
            userGroup.GET("/:id", GetUser)
            userGroup.PUT("/:id", UpdateUser)
            userGroup.DELETE("/:id", DeleteUser)
        }

        // 商品相关路由
        productGroup := api.Group("/products")
        {
            productGroup.GET("", GetProducts)
            productGroup.POST("", CreateProduct)
            productGroup.GET("/:id", GetProduct)
            productGroup.PUT("/:id", UpdateProduct)
        }
    }

    r.Run(":8080")
}

// 路由处理函数
func GetUsers(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{"message": "Get all users"})
}

func CreateUser(c *gin.Context) {
    c.JSON(http.StatusCreated, gin.H{"message": "User created"})
}

func GetUser(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{"message": "Get user", "id": id})
}

func UpdateUser(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{"message": "User updated", "id": id})
}

func DeleteUser(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{"message": "User deleted", "id": id})
}

func GetProducts(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{"message": "Get all products"})
}

func CreateProduct(c *gin.Context) {
    c.JSON(http.StatusCreated, gin.H{"message": "Product created"})
}

func GetProduct(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{"message": "Get product", "id": id})
}

func UpdateProduct(c *gin.Context) {
    id := c.Param("id")
    c.JSON(http.StatusOK, gin.H{"message": "Product updated", "id": id})
}
```

### 嵌套路由组
```go
func main() {
    r := gin.Default()

    // API版本控制
    v1 := r.Group("/api/v1")
    {
        v1.GET("/users", GetUsersV1)
        v1.POST("/users", CreateUserV1)

        // 带中间件的路由组
        auth := v1.Group("/auth")
        auth.Use(AuthMiddleware())
        {
            auth.GET("/profile", GetProfile)
            auth.PUT("/profile", UpdateProfile)
        }
    }

    v2 := r.Group("/api/v2")
    {
        v2.GET("/users", GetUsersV2)
        v2.POST("/users", CreateUserV2)
    }

    r.Run(":8080")
}

// 认证中间件
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "No token provided"})
            c.Abort()
            return
        }
        c.Next()
    }
}
```

## 路由方法

### 处理方法映射
```go
func main() {
    r := gin.Default()

    // 处理器函数类型
    type HandlerFunc func(*gin.Context)

    // 路由方法映射
    routes := map[string]map[string]HandlerFunc{
        "GET": {
            "/users":    GetUsers,
            "/users/:id": GetUser,
        },
        "POST": {
            "/users": CreateUser,
        },
        "PUT": {
            "/users/:id": UpdateUser,
        },
        "DELETE": {
            "/users/:id": DeleteUser,
        },
    }

    // 动态注册路由
    for method, paths := range routes {
        for path, handler := range paths {
            switch method {
            case "GET":
                r.GET(path, handler)
            case "POST":
                r.POST(path, handler)
            case "PUT":
                r.PUT(path, handler)
            case "DELETE":
                r.DELETE(path, handler)
            }
        }
    }

    r.Run(":8080")
}
```

### 路由信息获取
```go
func main() {
    r := gin.Default()

    // 添加一些路由
    r.GET("/users", GetUsers)
    r.POST("/users", CreateUser)
    r.GET("/users/:id", GetUser)

    // 获取路由信息
    routes := r.Routes()
    for _, route := range routes {
        fmt.Printf("Method: %s, Path: %s, Handler: %s\n",
            route.Method, route.Path, route.Handler)
    }

    r.Run(":8080)
}
```

## 路由优先级

### 路由匹配优先级
```go
func main() {
    r := gin.Default()

    // 静态路由优先级最高
    r.GET("/users/list", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"message": "Static route - users list"})
    })

    // 参数路由次之
    r.GET("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{"message": "Parameter route", "id": id})
    })

    // 通配符路由优先级最低
    r.GET("/users/*action", func(c *gin.Context) {
        action := c.Param("action")
        c.JSON(http.StatusOK, gin.H{"message": "Wildcard route", "action": action})
    })

    r.Run(":8080")
}
```

### 路由冲突检测
```go
func main() {
    r := gin.Default()

    // 检查路由冲突
    checkRouteConflict := func(method, path string) bool {
        for _, route := range r.Routes() {
            if route.Method == method && route.Path == path {
                return true
            }
        }
        return false
    }

    // 尝试添加路由
    addRoute := func(method, path string, handler gin.HandlerFunc) {
        if checkRouteConflict(method, path) {
            fmt.Printf("Route conflict detected: %s %s\n", method, path)
            return
        }

        switch method {
        case "GET":
            r.GET(path, handler)
        case "POST":
            r.POST(path, handler)
        case "PUT":
            r.PUT(path, handler)
        case "DELETE":
            r.DELETE(path, handler)
        }
        fmt.Printf("Route added: %s %s\n", method, path)
    }

    // 添加路由
    addRoute("GET", "/users", GetUsers)
    addRoute("POST", "/users", CreateUser)
    addRoute("GET", "/users/:id", GetUser)

    // 尝试添加冲突路由
    addRoute("GET", "/users", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"message": "This will conflict"})
    })

    r.Run(":8080")
}
```

## 路由冲突处理

### 路由冲突解决方案
```go
func main() {
    r := gin.Default()

    // 使用路由前缀避免冲突
    api := r.Group("/api")
    {
        api.GET("/users", GetUsers)
        api.POST("/users", CreateUser)
    }

    // 使用版本控制避免冲突
    v1 := r.Group("/v1")
    {
        v1.GET("/users", GetUsersV1)
    }

    v2 := r.Group("/v2")
    {
        v2.GET("/users", GetUsersV2)
    }

    // 使用不同的HTTP方法
    r.GET("/users/:id", GetUser)
    r.PUT("/users/:id", UpdateUser)
    r.DELETE("/users/:id", DeleteUser)

    r.Run(":8080")
}
```

### 路由规范化
```go
func main() {
    r := gin.Default()

    // 规范化路由路径
    normalizePath := func(path string) string {
        // 移除末尾的斜杠
        if len(path) > 1 && path[len(path)-1] == '/' {
            return path[:len(path)-1]
        }
        return path
    }

    // 路由注册器
    type Route struct {
        Method  string
        Path    string
        Handler gin.HandlerFunc
    }

    // 注册路由
    registerRoutes := func(routes []Route) {
        for _, route := range routes {
            normalizedPath := normalizePath(route.Path)

            switch route.Method {
            case "GET":
                r.GET(normalizedPath, route.Handler)
            case "POST":
                r.POST(normalizedPath, route.Handler)
            case "PUT":
                r.PUT(normalizedPath, route.Handler)
            case "DELETE":
                r.DELETE(normalizedPath, route.Handler)
            }
        }
    }

    // 定义路由
    routes := []Route{
        {Method: "GET", Path: "/users/", Handler: GetUsers},
        {Method: "POST", Path: "/users", Handler: CreateUser},
        {Method: "GET", Path: "/users/:id/", Handler: GetUser},
    }

    registerRoutes(routes)

    r.Run(":8080")
}
```

## ⚡ 路由性能优化

### 路由性能分析

```go
// 路由性能分析器
type RouteProfiler struct {
    routes      map[string]*RouteStats
    mutex       sync.RWMutex
    enabled     bool
}

type RouteStats struct {
    Path        string
    Method      string
    Count       int64
    TotalTime   time.Duration
    MaxTime     time.Duration
    MinTime     time.Duration
    AvgTime     time.Duration
    LastAccess  time.Time
}

func NewRouteProfiler() *RouteProfiler {
    return &RouteProfiler{
        routes:  make(map[string]*RouteStats),
        enabled: true,
    }
}

func (p *RouteProfiler) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        if !p.enabled {
            c.Next()
            return
        }

        start := time.Now()
        path := c.FullPath()
        method := c.Request.Method

        // 执行处理器
        c.Next()

        // 记录性能数据
        duration := time.Since(start)
        key := fmt.Sprintf("%s:%s", method, path)

        p.mutex.Lock()
        defer p.mutex.Unlock()

        if stats, exists := p.routes[key]; exists {
            stats.Count++
            stats.TotalTime += duration
            if duration > stats.MaxTime || stats.MaxTime == 0 {
                stats.MaxTime = duration
            }
            if duration < stats.MinTime || stats.MinTime == 0 {
                stats.MinTime = duration
            }
            stats.AvgTime = stats.TotalTime / time.Duration(stats.Count)
            stats.LastAccess = time.Now()
        } else {
            p.routes[key] = &RouteStats{
                Path:       path,
                Method:     method,
                Count:      1,
                TotalTime:  duration,
                MaxTime:    duration,
                MinTime:    duration,
                AvgTime:    duration,
                LastAccess: time.Now(),
            }
        }
    }
}

func (p *RouteProfiler) GetStats() map[string]*RouteStats {
    p.mutex.RLock()
    defer p.mutex.RUnlock()

    stats := make(map[string]*RouteStats)
    for k, v := range p.routes {
        stats[k] = v
    }
    return stats
}
```

### 路由缓存优化

```go
// 路由缓存优化器
type RouteCache struct {
    cache    *lru.Cache
    enabled  bool
}

func NewRouteCache(size int) *RouteCache {
    cache, _ := lru.New(size)
    return &RouteCache{
        cache:   cache,
        enabled: true,
    }
}

func (rc *RouteCache) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        if !rc.enabled {
            c.Next()
            return
        }

        // 生成缓存键
        key := c.Request.Method + ":" + c.FullPath()

        // 检查缓存
        if cached, found := rc.cache.Get(key); found {
            c.JSON(200, cached)
            c.Abort()
            return
        }

        // 执行处理器
        c.Next()

        // 缓存响应
        if len(c.Errors) == 0 {
            // 这里需要从响应中提取数据
            // 实际实现需要根据具体需求调整
        }
    }
}
```

## 🔧 高级路由模式

### RESTful API路由设计

```go
// RESTful路由设计
func SetupRESTfulRoutes(r *gin.Engine) {
    // 资源路由
    users := r.Group("/users")
    {
        // 获取用户列表
        users.GET("", getUsers)

        // 创建用户
        users.POST("", createUser)

        // 获取用户详情
        users.GET("/:id", getUser)

        // 更新用户
        users.PUT("/:id", updateUser)
        users.PATCH("/:id", patchUser)

        // 删除用户
        users.DELETE("/:id", deleteUser)

        // 用户子资源
        users.GET("/:id/posts", getUserPosts)
        users.POST("/:id/posts", createUserPost)

        // 用户统计
        users.GET("/:id/stats", getUserStats)
    }

    // 嵌套资源路由
    posts := r.Group("/posts")
    {
        posts.GET("", getPosts)
        posts.POST("", createPost)
        posts.GET("/:id", getPost)
        posts.PUT("/:id", updatePost)
        posts.DELETE("/:id", deletePost)

        // 评论子资源
        posts.GET("/:id/comments", getPostComments)
        posts.POST("/:id/comments", createPostComment)
    }
}
```

### 版本控制路由

```go
// 版本控制路由设计
func SetupVersionedRoutes(r *gin.Engine) {
    // URL路径版本控制
    v1 := r.Group("/v1")
    setupV1Routes(v1)

    v2 := r.Group("/v2")
    setupV2Routes(v2)

    // Header版本控制
    v1Header := r.Group("")
    v1Header.Use(versionMiddleware("v1"))
    setupV1Routes(v1Header)

    v2Header := r.Group("")
    v2Header.Use(versionMiddleware("v2"))
    setupV2Routes(v2Header)
}

// 版本中间件
func versionMiddleware(version string) gin.HandlerFunc {
    return func(c *gin.Context) {
        apiVersion := c.GetHeader("API-Version")
        if apiVersion != version {
            c.AbortWithStatusJSON(400, gin.H{
                "error": "Invalid API version",
                "expected": version,
                "received": apiVersion,
            })
            return
        }
        c.Next()
    }
}
```

## 🔗 路由中间件集成

### 路由级中间件

```go
// 路由级中间件使用
func setupRouteLevelMiddleware(r *gin.Engine) {
    // 全局中间件
    r.Use(gin.Logger())
    r.Use(gin.Recovery())

    // 路由组中间件
    api := r.Group("/api")
    api.Use(corsMiddleware())
    api.Use(rateLimitMiddleware())
    {
        // 路由级中间件
        api.GET("/public/data", publicDataHandler)

        // 需要认证的路由
        api.GET("/private/data", authMiddleware(), privateDataHandler)

        // 管理员路由
        api.GET("/admin/data", authMiddleware(), adminMiddleware(), adminDataHandler)

        // 多中间件链
        api.POST("/upload",
            authMiddleware(),
            fileUploadMiddleware(),
            rateLimitMiddleware(),
            uploadHandler,
        )
    }
}
```

### 条件路由中间件

```go
// 条件路由中间件
func conditionalRouteMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 根据请求条件应用不同的中间件
        userAgent := c.GetHeader("User-Agent")
        isMobile := strings.Contains(userAgent, "Mobile")

        if isMobile {
            // 移动端处理逻辑
            c.Set("device_type", "mobile")
        } else {
            // 桌面端处理逻辑
            c.Set("device_type", "desktop")
        }

        c.Next()
    }
}
```

## 💡 最佳实践

### 1. 路由组织原则

```go
// 路由组织示例
func setupRoutes(r *gin.Engine) {
    // 1. 健康检查路由
    r.GET("/health", healthCheck)
    r.GET("/ready", readinessCheck)

    // 2. API路由分组
    api := r.Group("/api")
    api.Use(loggingMiddleware(), metricsMiddleware())
    {
        // 公共路由
        public := api.Group("/public")
        public.Use(corsMiddleware())
        setupPublicRoutes(public)

        // 认证路由
        auth := api.Group("/auth")
        setupAuthRoutes(auth)

        // 受保护路由
        protected := api.Group("/v1")
        protected.Use(authMiddleware())
        setupProtectedRoutes(protected)
    }

    // 3. 静态文件路由
    r.Static("/static", "./static")
    r.StaticFile("/favicon.ico", "./static/favicon.ico")

    // 4. 404处理
    r.NoRoute(notFoundHandler)
}
```

### 2. 路由命名规范

```go
// 路由命名规范示例
func setupNamedRoutes(r *gin.Engine) {
    // 使用命名路由
    r.GET("/", indexHandler).Name("index")
    r.GET("/about", aboutHandler).Name("about")
    r.GET("/contact", contactHandler).Name("contact")

    // 路由组命名
    users := r.Group("/users").Name("users")
    {
        users.GET("", usersHandler).Name("users.index")
        users.GET("/create", createUserForm).Name("users.create")
        users.POST("", createUserHandler).Name("users.store")
        users.GET("/:id", showUserHandler).Name("users.show")
        users.GET("/:id/edit", editUserForm).Name("users.edit")
        users.PUT("/:id", updateUserHandler).Name("users.update")
        users.DELETE("/:id", deleteUserHandler).Name("users.destroy")
    }
}
```

### 3. 路由安全考虑

```go
// 路由安全中间件
func securityMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 1. 添加安全头
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-XSS-Protection", "1; mode=block")

        // 2. 防止路径遍历攻击
        path := c.Request.URL.Path
        if strings.Contains(path, "..") {
            c.AbortWithStatusJSON(400, gin.H{"error": "Invalid path"})
            return
        }

        // 3. 请求大小限制
        if c.Request.ContentLength > 10<<20 { // 10MB
            c.AbortWithStatusJSON(413, gin.H{"error": "Request too large"})
            return
        }

        c.Next()
    }
}
```

## 🎯 实战案例

### 完整的API路由设计

```go
// 完整的API路由设计示例
func setupCompleteAPI(r *gin.Engine) {
    // 1. 中间件配置
    r.Use(gin.Logger())
    r.Use(gin.Recovery())
    r.Use(corsMiddleware())
    r.Use(metricsMiddleware())

    // 2. 健康检查
    health := r.Group("/health")
    {
        health.GET("", healthCheck)
        health.GET("/ready", readinessCheck)
        health.GET("/metrics", prometheusHandler())
    }

    // 3. API v1
    apiV1 := r.Group("/api/v1")
    apiV1.Use(apiVersionMiddleware("v1"))
    {
        // 认证相关
        auth := apiV1.Group("/auth")
        {
            auth.POST("/login", loginHandler)
            auth.POST("/register", registerHandler)
            auth.POST("/refresh", refreshTokenHandler)
            auth.POST("/logout", authMiddleware(), logoutHandler)
        }

        // 用户管理
        users := apiV1.Group("/users")
        users.Use(authMiddleware())
        {
            users.GET("", listUsersHandler)
            users.POST("", createUserHandler)
            users.GET("/:id", getUserHandler)
            users.PUT("/:id", updateUserHandler)
            users.DELETE("/:id", deleteUserHandler)

            // 用户相关资源
            users.GET("/:id/posts", getUserPostsHandler)
            users.GET("/:id/orders", getUserOrdersHandler)
            users.GET("/:id/profile", getUserProfileHandler)
            users.PUT("/:id/profile", updateUserProfileHandler)
        }

        // 产品管理
        products := apiV1.Group("/products")
        {
            products.GET("", listProductsHandler)
            products.GET("/:id", getProductHandler)
            products.GET("/:slug", getProductBySlugHandler)
            products.GET("/search", searchProductsHandler)
            products.GET("/category/:category", getProductsByCategoryHandler)

            // 需要认证的产品操作
            productsAuth := products.Group("")
            productsAuth.Use(authMiddleware())
            {
                productsAuth.POST("", createProductHandler)
                productsAuth.PUT("/:id", updateProductHandler)
                productsAuth.DELETE("/:id", deleteProductHandler)
            }
        }

        // 订单管理
        orders := apiV1.Group("/orders")
        orders.Use(authMiddleware())
        {
            orders.GET("", listOrdersHandler)
            orders.POST("", createOrderHandler)
            orders.GET("/:id", getOrderHandler)
            orders.PUT("/:id", updateOrderHandler)
            orders.DELETE("/:id", deleteOrderHandler)
            orders.POST("/:id/cancel", cancelOrderHandler)
            orders.GET("/:id/status", getOrderStatusHandler)
        }

        // 管理员路由
        admin := apiV1.Group("/admin")
        admin.Use(authMiddleware(), adminMiddleware())
        {
            admin.GET("/dashboard", adminDashboardHandler)
            admin.GET("/users", adminListUsersHandler)
            admin.GET("/orders", adminListOrdersHandler)
            admin.GET("/products", adminListProductsHandler)
            admin.POST("/announcements", createAnnouncementHandler)
        }
    }

    // 4. 静态文件服务
    r.Static("/static", "./static")
    r.StaticFile("/favicon.ico", "./static/favicon.ico")

    // 5. 404处理
    r.NoRoute(func(c *gin.Context) {
        c.JSON(404, gin.H{
            "error": "Route not found",
            "path":  c.Request.URL.Path,
            "method": c.Request.Method,
        })
    })
}
```

### 路由性能测试

```go
package main

import (
    "fmt"
    "net/http"
    "net/http/httptest"
    "testing"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

// 路由性能测试
func BenchmarkRouter(b *testing.B) {
    r := setupTestRouter()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        req, _ := http.NewRequest("GET", "/users/123", nil)
        w := httptest.NewRecorder()
        r.ServeHTTP(w, req)
    }
}

// 路由响应时间测试
func TestRouterResponseTime(t *testing.T) {
    r := setupTestRouter()

    req, _ := http.NewRequest("GET", "/users/123", nil)
    w := httptest.NewRecorder()

    start := time.Now()
    r.ServeHTTP(w, req)
    duration := time.Since(start)

    assert.Less(t, duration, 10*time.Millisecond, "Response time should be less than 10ms")
    fmt.Printf("Response time: %v\n", duration)
}

// 设置测试路由
func setupTestRouter() *gin.Engine {
    r := gin.New()

    // 添加测试路由
    r.GET("/users", GetUsers)
    r.POST("/users", CreateUser)
    r.GET("/users/:id", GetUser)
    r.PUT("/users/:id", UpdateUser)
    r.DELETE("/users/:id", DeleteUser)

    return r
}
```

这个全面的Gin路由基础与高级用法文档涵盖了：

1. **路由基础**：基本路由定义、HTTP方法支持、Any方法使用
2. **路由组**：基本路由组、嵌套路由组、带中间件的路由组
3. **路由参数**：路径参数、查询参数、表单参数处理
4. **路由冲突处理**：冲突检测、路由优先级管理
5. **路由性能优化**：性能分析、缓存优化、路由优化
6. **高级路由模式**：RESTful设计、版本控制、动态路由
7. **路由中间件集成**：路由级中间件、条件中间件
8. **最佳实践**：组织原则、命名规范、安全考虑、文档生成
9. **实战案例**：完整API设计、动态路由管理系统
10. **性能测试**：路由性能基准测试和响应时间测试

这个文档为Go开发者提供了Gin框架路由系统的全面指南，从基础概念到高级应用，帮助开发者构建高性能、可维护的Web应用。