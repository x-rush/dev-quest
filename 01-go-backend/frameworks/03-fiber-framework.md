# Fiber框架详解

## 概述
Fiber是受Express.js启发构建的Go语言Web框架，它基于fasthttp（基于C语言的高性能HTTP库）构建，旨在提供极致的性能和开发体验。Fiber的设计理念是保持简单易用的同时，提供出色的性能表现。

## 核心特性
- **极致性能**: 基于fasthttp，性能远超基于net/http的框架
- **Express.js风格**: 熟悉的API设计，便于Node.js开发者迁移
- **低内存占用**: 高效的内存管理
- **路由系统**: 灵活的路由匹配和参数解析
- **中间件支持**: 类似Express的中间件系统
- **模板引擎**: 支持多种模板引擎

## 快速开始

### 安装
```bash
go get -u github.com/gofiber/fiber/v2
```

### 基本示例
```go
package main

import (
    "github.com/gofiber/fiber/v2"
)

func main() {
    app := fiber.New()

    app.Get("/", func(c *fiber.Ctx) error {
        return c.SendString("Hello, World!")
    })

    app.Listen(":8080")
}
```

## 核心组件

### 1. 路由系统
Fiber提供了灵活的路由系统，支持参数路由和通配符路由。

```go
// 基本路由
app.Get("/users", getUsers)
app.Post("/users", createUser)
app.Put("/users/:id", updateUser)
app.Delete("/users/:id", deleteUser)

// 参数路由
app.Get("/users/:id", getUser)
app.Get("/users/:id/posts/:postId", getUserPost)

// 通配符路由
app.Get("/files/*", serveFiles)

// 路由组
api := app.Group("/api", func(c *fiber.Ctx) error {
    c.Set("API-Version", "1.0.0")
    return c.Next()
})

v1 := api.Group("/v1")
v1.Get("/users", getUsers)
v1.Post("/users", createUser)
```

### 2. 中间件
Fiber的中间件系统类似于Express.js，使用链式调用。

```go
// 全局中间件
app.Use(func(c *fiber.Ctx) error {
    // 在所有请求之前执行
    c.Set("X-Custom-Header", "Hello")
    return c.Next()
})

// 路由组中间件
api := app.Group("/api")
api.Use(AuthMiddleware())

// 单个路由中间件
app.Get("/protected", AuthMiddleware(), protectedHandler)

// 内置中间件
app.Use(fiber.Logger())
app.Use(fiber.Recover())
app.Use(fiber.Cors())
```

### 3. 请求处理
Fiber提供了强大的请求处理功能。

```go
func handler(c *fiber.Ctx) error {
    // 获取路由参数
    id := c.Params("id")

    // 获取查询参数
    name := c.Query("name")
    page := c.Query("page", "1")

    // 获取请求体
    body := c.Body()

    // 获取JSON数据
    var user User
    if err := c.BodyParser(&user); err != nil {
        return err
    }

    // 获取请求头
    userAgent := c.Get("User-Agent")

    // 获取Cookie
    session := c.Cookies("session")

    return c.SendString("Hello World")
}
```

### 4. 响应处理
Fiber支持多种响应格式。

```go
func handler(c *fiber.Ctx) error {
    // JSON响应
    return c.JSON(fiber.Map{
        "message": "Hello, World!",
        "data":    user,
    })

    // JSONP响应
    return c.JSONP(fiber.Map{
        "message": "Hello, World!",
    }, "callback")

    // XML响应
    return c.XML(fiber.Map{
        "message": "Hello, World!",
    })

    // 字符串响应
    return c.SendString("Hello, World!")

    // 文件响应
    return c.SendFile("path/to/file.txt")

    // 流响应
    return c.SendStream(bytes.NewReader(data))

    // HTML响应
    return c.SendString("<h1>Hello, World!</h1>")
}
```

## 高级特性

### 1. 静态文件服务
```go
// 静态文件服务
app.Static("/static", "./public")

// 带前缀的静态文件服务
app.Static("/static", "./public", fiber.Static{
    Compress:      true,
    Browse:        true,
    Index:         "index.html",
    CacheDuration: 10 * time.Second,
})

// 单个文件服务
app.Get("/favicon.ico", func(c *fiber.Ctx) error {
    return c.SendFile("./favicon.ico")
})
```

### 2. 模板引擎
```go
// 配置模板引擎
app := fiber.New(fiber.Config{
    Views: engine.New("./views", ".html"),
})

// 使用模板
app.Get("/", func(c *fiber.Ctx) error {
    return c.Render("index", fiber.Map{
        "Title": "Hello, World!",
    })
})

// HTML模板示例
<!-- views/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{.Title}}</title>
</head>
<body>
    <h1>{{.Title}}</h1>
</body>
</html>
```

### 3. WebSocket支持
```go
// WebSocket处理器
app.Get("/ws", websocket.New(func(c *websocket.Conn) {
    for {
        // 读取消息
        mt, msg, err := c.ReadMessage()
        if err != nil {
            log.Println("read:", err)
            break
        }
        log.Printf("recv: %s", msg)

        // 发送消息
        if err := c.WriteMessage(mt, msg); err != nil {
            log.Println("write:", err)
            break
        }
    }
}))

// 广播消息
app.Get("/broadcast", func(c *fiber.Ctx) error {
    message := c.Query("message")
    for _, conn := range connections {
        if err := conn.WriteMessage(websocket.TextMessage, []byte(message)); err != nil {
            log.Println("write:", err)
        }
    }
    return c.SendString("Message broadcasted")
})
```

### 4. 错误处理
```go
// 全局错误处理
app.Use(func(c *fiber.Ctx) error {
    // 捕获panic
    defer func() {
        if r := recover(); r != nil {
            log.Printf("Recovered: %v", r)
            c.Status(500).SendString("Internal Server Error")
        }
    }()
    return c.Next()
})

// 自定义错误响应
app.Get("/error", func(c *fiber.Ctx) error {
    return fiber.NewError(404, "Not Found")
})

// 404处理
app.Use(func(c *fiber.Ctx) error {
    return c.Status(404).SendFile("./public/404.html")
})
```

## 内置中间件详解

### 1. Logger中间件
```go
// 配置日志中间件
app.Use(fiber.New(fiber.Config{
    AppName: "My App",
}))

// 自定义日志配置
app.Use(fiber.New(fiber.Config{
    Logger: fiber.Logger{
        Format: "${pid} ${locals:requestid} ${status} - ${method} ${path}\n",
        Output: os.Stdout,
    },
}))
```

### 2. CORS中间件
```go
// 配置CORS
app.Use(fiber.New(fiber.Config{
    EnablePreflight: true,
}))

// 自定义CORS配置
app.Use(cors.New(cors.Config{
    AllowOrigins:     "*",
    AllowMethods:     "GET,POST,PUT,DELETE",
    AllowHeaders:     "Origin,Content-Type,Accept",
    ExposeHeaders:    "Content-Length",
    AllowCredentials: true,
    MaxAge:           86400,
}))
```

### 3. 限流中间件
```go
// 限流配置
app.Use(limiter.New(limiter.Config{
    Max:        100,
    Expiration: 30 * time.Second,
    KeyGenerator: func(c *fiber.Ctx) string {
        return c.IP()
    },
    LimitReached: func(c *fiber.Ctx) error {
        return c.Status(429).JSON(fiber.Map{
            "error": "Too many requests",
        })
    },
}))
```

### 4. JWT中间件
```go
// JWT配置
app.Use(jwtware.New(jwtware.Config{
    SigningKey: []byte("secret"),
    ContextKey: "jwt",
}))

// 获取JWT claims
func handler(c *fiber.Ctx) error {
    user := c.Locals("jwt").(*jwt.Token)
    claims := user.Claims.(jwt.MapClaims)
    name := claims["name"].(string)
    return c.JSON(fiber.Map{
        "name": name,
    })
}
```

## 性能优化技巧

### 1. 内存优化
```go
// 使用对象池
var userPool = sync.Pool{
    New: func() interface{} {
        return &User{}
    },
}

func handler(c *fiber.Ctx) error {
    user := userPool.Get().(*User)
    defer userPool.Put(user)

    // 使用user对象
    return c.JSON(user)
}
```

### 2. 连接池优化
```go
// 数据库连接池
db, err := sql.Open("postgres", connStr)
if err != nil {
    log.Fatal(err)
}

// 配置连接池
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(25)
db.SetConnMaxLifetime(5 * time.Minute)
```

### 3. 缓存优化
```go
// Redis缓存
redisClient := redis.NewClient(&redis.Options{
    Addr:     "localhost:6379",
    Password: "",
    DB:       0,
})

// 使用缓存
func getUser(c *fiber.Ctx) error {
    id := c.Params("id")

    // 尝试从缓存获取
    cached, err := redisClient.Get(context.Background(), "user:"+id).Result()
    if err == nil {
        return c.JSON(cached)
    }

    // 从数据库获取
    user, err := getUserFromDB(id)
    if err != nil {
        return err
    }

    // 设置缓存
    redisClient.Set(context.Background(), "user:"+id, user, 10*time.Minute)

    return c.JSON(user)
}
```

## 项目结构最佳实践

```
my-fiber-app/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   │   └── config.go
│   ├── handlers/
│   │   ├── user.go
│   │   └── auth.go
│   ├── models/
│   │   └── user.go
│   ├── services/
│   │   └── user.go
│   ├── middleware/
│   │   ├── auth.go
│   │   └── cors.go
│   └── database/
│       └── database.go
├── pkg/
│   └── utils/
│       └── utils.go
├── web/
│   └── templates/
├── migrations/
├── tests/
└── go.mod
```

## 与其他框架对比

| 特性 | Fiber | Gin | Echo |
|------|-------|-----|------|
| 基础库 | fasthttp | net/http | net/http |
| 性能 | 极高 | 高 | 高 |
| 内存占用 | 低 | 中 | 中 |
| API设计 | Express.js风格 | Martini风格 | 自定义 |
| 学习曲线 | 低 | 中 | 中 |
| 社区支持 | 良好 | 优秀 | 良好 |
| 兼容性 | 有限 | 完全 | 完全 |

## 实战项目示例

### 1. REST API服务
```go
package main

import (
    "github.com/gofiber/fiber/v2"
    "github.com/gofiber/fiber/v2/middleware/cors"
    "github.com/gofiber/fiber/v2/middleware/logger"
    "github.com/gofiber/fiber/v2/middleware/recover"
)

type User struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

var users = []User{
    {ID: "1", Name: "John Doe", Email: "john@example.com"},
    {ID: "2", Name: "Jane Smith", Email: "jane@example.com"},
}

func main() {
    app := fiber.New()

    // 中间件
    app.Use(cors.New())
    app.Use(logger.New())
    app.Use(recover.New())

    // 路由
    api := app.Group("/api/v1")

    // 用户路由
    userRoutes := api.Group("/users")
    userRoutes.Get("/", getUsers)
    userRoutes.Get("/:id", getUser)
    userRoutes.Post("/", createUser)
    userRoutes.Put("/:id", updateUser)
    userRoutes.Delete("/:id", deleteUser)

    // 启动服务器
    app.Listen(":8080")
}

func getUsers(c *fiber.Ctx) error {
    return c.JSON(users)
}

func getUser(c *fiber.Ctx) error {
    id := c.Params("id")
    for _, user := range users {
        if user.ID == id {
            return c.JSON(user)
        }
    }
    return c.Status(404).JSON(fiber.Map{"error": "User not found"})
}

func createUser(c *fiber.Ctx) error {
    var user User
    if err := c.BodyParser(&user); err != nil {
        return c.Status(400).JSON(fiber.Map{"error": err.Error()})
    }
    users = append(users, user)
    return c.Status(201).JSON(user)
}

func updateUser(c *fiber.Ctx) error {
    id := c.Params("id")
    var updatedUser User
    if err := c.BodyParser(&updatedUser); err != nil {
        return c.Status(400).JSON(fiber.Map{"error": err.Error()})
    }

    for i, user := range users {
        if user.ID == id {
            users[i] = updatedUser
            return c.JSON(updatedUser)
        }
    }
    return c.Status(404).JSON(fiber.Map{"error": "User not found"})
}

func deleteUser(c *fiber.Ctx) error {
    id := c.Params("id")
    for i, user := range users {
        if user.ID == id {
            users = append(users[:i], users[i+1:]...)
            return c.SendStatus(204)
        }
    }
    return c.Status(404).JSON(fiber.Map{"error": "User not found"})
}
```

## 总结
Fiber框架凭借其基于fasthttp的极致性能和Express.js风格的API设计，成为Go语言Web开发的高性能选择。它特别适合那些需要处理大量并发请求、对性能要求极高的项目。通过合理使用Fiber的各种特性，可以构建出既高性能又易于维护的Web应用。

## 学习资源
- [Fiber官方文档](https://docs.gofiber.io/)
- [Fiber源码分析](https://github.com/gofiber/fiber)
- [Fiber食谱](https://docs.gofiber.io/recipe)
- [Fiber示例](https://github.com/gofiber/fiber/tree/master/examples)

*最后更新: 2025年9月*