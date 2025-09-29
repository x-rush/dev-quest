# Go流行常用库详解

Go生态系统拥有丰富的第三方库，这些库极大地扩展了Go语言的功能。本文档详细介绍Go开发中最流行和实用的第三方库，包括JSON解析、网络请求、数据库操作等性能优先的库。

## 1. JSON处理库

### 1.1 json-iterator/go - 高性能JSON库

**功能**：比标准库更快的JSON解析和生成

**安装**：
```bash
go get github.com/json-iterator/go
```

**示例**：
```go
package main

import (
    "fmt"
    "github.com/json-iterator/go"
)

type User struct {
    Name    string   `json:"name"`
    Age     int      `json:"age"`
    Email   string   `json:"email,omitempty"`
    Hobbies []string `json:"hobbies"`
}

var jsoniter = jsoniter.ConfigCompatibleWithStandardLibrary

func main() {
    // 编码
    user := User{
        Name:    "Alice",
        Age:     25,
        Hobbies: []string{"reading", "gaming"},
    }

    data, err := jsoniter.Marshal(user)
    if err != nil {
        panic(err)
    }
    fmt.Println("JSON编码:", string(data))

    // 解码
    var decoded User
    err = jsoniter.Unmarshal(data, &decoded)
    if err != nil {
        panic(err)
    }
    fmt.Printf("解码结果: %+v\n", decoded)

    // 流式编码
    stream := jsoniter.NewStream(jsoniter.ConfigDefault, nil, 0)
    stream.WriteVal(user)
    fmt.Println("流式编码:", stream.Buffer())

    // 流式解码
    decoder := jsoniter.NewDecoder(strings.NewReader(string(data)))
    var streamUser User
    decoder.Decode(&streamUser)
    fmt.Printf("流式解码: %+v\n", streamUser)
}
```

### 1.2 segmentio/encoding - 高性能编码库

**功能**：提供高性能的JSON、CBOR等编码支持

**安装**：
```bash
go get github.com/segmentio/encoding
```

**示例**：
```go
package main

import (
    "fmt"
    "github.com/segmentio/encoding/json"
)

type Product struct {
    ID    int     `json:"id"`
    Name  string  `json:"name"`
    Price float64 `json:"price"`
}

func main() {
    product := Product{
        ID:    1,
        Name:  "Laptop",
        Price: 999.99,
    }

    // 编码
    data, err := json.Marshal(product)
    if err != nil {
        panic(err)
    }
    fmt.Println("Segmentio JSON:", string(data))

    // 解码
    var decoded Product
    err = json.Unmarshal(data, &decoded)
    if err != nil {
        panic(err)
    }
    fmt.Printf("解码: %+v\n", decoded)

    // 自定义配置
    config := json.EncoderConfig{
        EscapeHTML: true,
        SortMapKeys: true,
    }
    encoder := json.NewEncoder(config)

    customData, err := encoder.Encode(product)
    if err != nil {
        panic(err)
    }
    fmt.Println("自定义编码:", string(customData))
}
```

## 2. 网络请求库

### 2.1 resty - 简洁的HTTP客户端

**功能**：简化和增强HTTP请求

**安装**：
```bash
go get github.com/go-resty/resty/v2
```

**示例**：
```go
package main

import (
    "fmt"
    "github.com/go-resty/resty/v2"
    "time"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

func main() {
    // 创建客户端
    client := resty.New()

    // 基本配置
    client.SetTimeout(10 * time.Second)
    client.SetRetryCount(3)
    client.SetRetryWaitTime(2 * time.Second)

    // 设置请求头
    client.SetHeader("Accept", "application/json")
    client.SetHeader("User-Agent", "MyApp/1.0")

    // GET请求
    resp, err := client.R().
        SetResult(&User{}).
        Get("https://jsonplaceholder.typicode.com/users/1")

    if err != nil {
        fmt.Printf("请求失败: %v\n", err)
        return
    }

    if resp.StatusCode() == 200 {
        user := resp.Result().(*User)
        fmt.Printf("用户信息: %+v\n", user)
    }

    // POST请求
    newUser := User{
        Name:  "John Doe",
        Email: "john@example.com",
    }

    createResp, err := client.R().
        SetBody(newUser).
        SetResult(&User{}).
        Post("https://jsonplaceholder.typicode.com/users")

    if err == nil && createResp.StatusCode() == 201 {
        createdUser := createResp.Result().(*User)
        fmt.Printf("创建用户: %+v\n", createdUser)
    }

    // 查询参数
    queryResp, err := client.R().
        SetQueryParams(map[string]string{
            "userId": "1",
            "limit":  "5",
        }).
        Get("https://jsonplaceholder.typicode.com/posts")

    if err == nil {
        fmt.Printf("查询响应: %s\n", queryResp.String())
    }

    // 文件上传
    uploadResp, err := client.R().
        SetFile("file", "test.txt").
        Post("https://httpbin.org/post")

    if err == nil {
        fmt.Printf("上传响应: %s\n", uploadResp.String())
    }

    // 基础认证
    authClient := resty.New()
    authClient.SetBasicAuth("username", "password")

    // Bearer Token
    tokenClient := resty.New()
    tokenClient.SetAuthToken("your-token-here")

    // 中间件
    client.OnBeforeRequest(func(c *resty.Client, r *resty.Request) error {
        fmt.Printf("请求前: %s %s\n", r.Method, r.URL)
        return nil
    })

    client.OnAfterResponse(func(c *resty.Client, r *resty.Response) error {
        fmt.Printf("响应后: %d\n", r.StatusCode())
        return nil
    })
}
```

### 2.2 fasthttp - 高性能HTTP客户端/服务器

**功能**：高性能的HTTP实现，比标准库快10倍

**安装**：
```bash
go get github.com/valyala/fasthttp
```

**示例**：
```go
package main

import (
    "fmt"
    "github.com/valyala/fasthttp"
)

func main() {
    // HTTP客户端
    args := fasthttp.Args{}
    args.Add("name", "Alice")
    args.Add("age", "25")

    statusCode, body, err := fasthttp.Post(nil, "https://httpbin.org/post", &args)
    if err != nil {
        fmt.Printf("请求失败: %v\n", err)
        return
    }

    if statusCode == fasthttp.StatusOK {
        fmt.Printf("响应: %s\n", body)
    }

    // 自定义请求
    req := fasthttp.AcquireRequest()
    defer fasthttp.ReleaseRequest(req)

    req.SetRequestURI("https://jsonplaceholder.typicode.com/users/1")
    req.Header.SetMethod("GET")
    req.Header.Set("User-Agent", "MyApp/1.0")

    resp := fasthttp.AcquireResponse()
    defer fasthttp.ReleaseResponse(resp)

    if err := fasthttp.Do(req, resp); err != nil {
        fmt.Printf("请求失败: %v\n", err)
        return
    }

    if resp.StatusCode() == fasthttp.StatusOK {
        fmt.Printf("响应体: %s\n", resp.Body())
    }

    // 并发请求
    urls := []string{
        "https://jsonplaceholder.typicode.com/users/1",
        "https://jsonplaceholder.typicode.com/users/2",
        "https://jsonplaceholder.typicode.com/users/3",
    }

    ch := make(chan string, len(urls))

    for _, url := range urls {
        go func(u string) {
            _, body, err := fasthttp.Get(nil, u)
            if err == nil {
                ch <- string(body)
            } else {
                ch <- fmt.Sprintf("Error: %v", err)
            }
        }(url)
    }

    for i := 0; i < len(urls); i++ {
        result := <-ch
        fmt.Printf("结果 %d: %s\n", i+1, result[:100])
    }

    // HTTP服务器
    requestHandler := func(ctx *fasthttp.RequestCtx) {
        switch string(ctx.Path()) {
        case "/":
            fmt.Fprintf(ctx, "Hello, World!")
        case "/user":
            user := `{"id": 1, "name": "Alice"}`
            ctx.SetContentType("application/json")
            ctx.SetBody([]byte(user))
        default:
            ctx.Error("Not found", fasthttp.StatusNotFound)
        }
    }

    fmt.Println("启动服务器在 :8080")
    // fasthttp.ListenAndServe(":8080", requestHandler)
}
```

## 3. 数据库库

### 3.1 sqlx - 数据库扩展库

**功能**：标准库database/sql的扩展，提供更多便利功能

**安装**：
```bash
go get github.com/jmoiron/sqlx
```

**示例**：
```go
package main

import (
    "database/sql"
    "fmt"
    "log"
    "time"

    _ "github.com/lib/pq"
    "github.com/jmoiron/sqlx"
)

type User struct {
    ID        int       `db:"id"`
    Name      string    `db:"name"`
    Email     string    `db:"email"`
    Age       int       `db:"age"`
    CreatedAt time.Time `db:"created_at"`
}

func main() {
    // 连接数据库
    db, err := sqlx.Connect("postgres", "host=localhost port=5432 user=postgres password=password dbname=testdb sslmode=disable")
    if err != nil {
        log.Fatal("连接数据库失败:", err)
    }
    defer db.Close()

    // 创建表
    schema := `
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        age INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )`

    _, err = db.Exec(schema)
    if err != nil {
        log.Fatal("创建表失败:", err)
    }

    // 插入数据
    insertSQL := `INSERT INTO users (name, email, age) VALUES ($1, $2, $3) RETURNING id`
    var id int
    err = db.QueryRow(insertSQL, "Alice", "alice@example.com", 25).Scan(&id)
    if err != nil {
        log.Fatal("插入失败:", err)
    }
    fmt.Printf("插入成功，ID: %d\n", id)

    // 查询单条记录到结构体
    var user User
    err = db.Get(&user, "SELECT * FROM users WHERE id = $1", id)
    if err != nil {
        log.Fatal("查询失败:", err)
    }
    fmt.Printf("查询结果: %+v\n", user)

    // 查询多条记录到切片
    var users []User
    err = db.Select(&users, "SELECT * FROM users ORDER BY created_at DESC LIMIT 10")
    if err != nil {
        log.Fatal("查询失败:", err)
    }
    fmt.Printf("用户列表: %+v\n", users)

    // 命名参数查询
    var usersByAge []User
    err = db.Select(&usersByAge, "SELECT * FROM users WHERE age > :age", map[string]interface{}{
        "age": 20,
    })
    if err != nil {
        log.Fatal("查询失败:", err)
    }
    fmt.Printf("年龄大于20的用户: %+v\n", usersByAge)

    // 事务处理
    tx, err := db.Beginx()
    if err != nil {
        log.Fatal("开始事务失败:", err)
    }

    // 在事务中执行多个操作
    _, err = tx.Exec("INSERT INTO users (name, email, age) VALUES ($1, $2, $3)", "Bob", "bob@example.com", 30)
    if err != nil {
        tx.Rollback()
        log.Fatal("事务插入失败:", err)
    }

    _, err = tx.Exec("INSERT INTO users (name, email, age) VALUES ($1, $2, $3)", "Charlie", "charlie@example.com", 35)
    if err != nil {
        tx.Rollback()
        log.Fatal("事务插入失败:", err)
    }

    err = tx.Commit()
    if err != nil {
        log.Fatal("提交事务失败:", err)
    }

    fmt.Println("事务提交成功")

    // 预编译语句
    stmt, err := db.Preparex("UPDATE users SET name = $1 WHERE id = $2")
    if err != nil {
        log.Fatal("准备语句失败:", err)
    }
    defer stmt.Close()

    result, err := stmt.Exec("Alice Smith", id)
    if err != nil {
        log.Fatal("执行更新失败:", err)
    }

    rowsAffected, err := result.RowsAffected()
    if err != nil {
        log.Fatal("获取影响行数失败:", err)
    }
    fmt.Printf("更新了 %d 行\n", rowsAffected)

    // 批量操作
    batchStmt, err := db.Preparex("INSERT INTO users (name, email, age) VALUES ($1, $2, $3)")
    if err != nil {
        log.Fatal("准备批量语句失败:", err)
    }
    defer batchStmt.Close()

    names := []string{"David", "Eve", "Frank"}
    emails := []string{"david@example.com", "eve@example.com", "frank@example.com"}
    ages := []int{28, 32, 29}

    for i := 0; i < len(names); i++ {
        _, err = batchStmt.Exec(names[i], emails[i], ages[i])
        if err != nil {
            log.Printf("批量插入失败: %v\n", err)
        }
    }

    fmt.Println("批量插入完成")

    // 连接池配置
    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(25)
    db.SetConnMaxLifetime(5 * time.Minute)

    fmt.Printf("连接池状态: Open=%d, Idle=%d\n", db.Stats().OpenConnections, db.Stats().Idle)
}
```

### 3.2 pgx - PostgreSQL高性能驱动

**功能**：PostgreSQL的高性能驱动和工具包

**安装**：
```bash
go get github.com/jackc/pgx/v5
```

**示例**：
```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    Age       int       `json:"age"`
    CreatedAt time.Time `json:"created_at"`
}

func main() {
    // 使用连接池
    config, err := pgxpool.ParseConfig("host=localhost port=5432 user=postgres password=password dbname=testdb sslmode=disable")
    if err != nil {
        log.Fatal("解析配置失败:", err)
    }

    // 配置连接池
    config.MaxConns = 10
    config.MinConns = 2
    config.HealthCheckPeriod = 1 * time.Minute
    config.MaxConnLifetime = 2 * time.Hour

    pool, err := pgxpool.NewWithConfig(context.Background(), config)
    if err != nil {
        log.Fatal("创建连接池失败:", err)
    }
    defer pool.Close()

    // 测试连接
    if err := pool.Ping(context.Background()); err != nil {
        log.Fatal("数据库连接测试失败:", err)
    }

    fmt.Println("数据库连接成功")

    // 创建表
    createTable := `
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        age INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )`

    _, err = pool.Exec(context.Background(), createTable)
    if err != nil {
        log.Fatal("创建表失败:", err)
    }

    // 插入数据
    insertSQL := `INSERT INTO users (name, email, age) VALUES ($1, $2, $3) RETURNING id`
    var id int
    err = pool.QueryRow(context.Background(), insertSQL, "Alice", "alice@example.com", 25).Scan(&id)
    if err != nil {
        log.Fatal("插入失败:", err)
    }
    fmt.Printf("插入成功，ID: %d\n", id)

    // 查询单条记录
    var user User
    err = pool.QueryRow(context.Background(), "SELECT id, name, email, age, created_at FROM users WHERE id = $1", id).Scan(&user.ID, &user.Name, &user.Email, &user.Age, &user.CreatedAt)
    if err != nil {
        log.Fatal("查询失败:", err)
    }
    fmt.Printf("查询结果: %+v\n", user)

    // 查询多条记录
    rows, err := pool.Query(context.Background(), "SELECT id, name, email, age, created_at FROM users ORDER BY created_at DESC")
    if err != nil {
        log.Fatal("查询失败:", err)
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var u User
        err := rows.Scan(&u.ID, &u.Name, &u.Email, &u.Age, &u.CreatedAt)
        if err != nil {
            log.Fatal("扫描行失败:", err)
        }
        users = append(users, u)
    }

    fmt.Printf("用户列表: %+v\n", users)

    // 批量插入
    batch := &pgx.Batch{}
    names := []string{"Bob", "Charlie", "David"}
    emails := []string{"bob@example.com", "charlie@example.com", "david@example.com"}
    ages := []int{30, 35, 28}

    for i := 0; i < len(names); i++ {
        batch.Queue("INSERT INTO users (name, email, age) VALUES ($1, $2, $3)", names[i], emails[i], ages[i])
    }

    br := pool.SendBatch(context.Background(), batch)
    defer br.Close()

    for i := 0; i < len(names); i++ {
        _, err := br.Exec()
        if err != nil {
            log.Printf("批量插入第%d条失败: %v\n", i+1, err)
        }
    }

    fmt.Println("批量插入完成")

    // 事务处理
    tx, err := pool.Begin(context.Background())
    if err != nil {
        log.Fatal("开始事务失败:", err)
    }

    defer func() {
        if err != nil {
            tx.Rollback(context.Background())
        }
    }()

    // 在事务中执行
    _, err = tx.Exec(context.Background(), "INSERT INTO users (name, email, age) VALUES ($1, $2, $3)", "Eve", "eve@example.com", 32)
    if err != nil {
        log.Fatal("事务插入失败:", err)
    }

    err = tx.Commit(context.Background())
    if err != nil {
        log.Fatal("提交事务失败:", err)
    }

    fmt.Println("事务提交成功")

    // 使用pgx直接连接（无连接池）
    conn, err := pgx.Connect(context.Background(), "host=localhost port=5432 user=postgres password=password dbname=testdb sslmode=disable")
    if err != nil {
        log.Fatal("直接连接失败:", err)
    }
    defer conn.Close(context.Background())

    // 使用连接执行简单查询
    var count int
    err = conn.QueryRow(context.Background(), "SELECT COUNT(*) FROM users").Scan(&count)
    if err != nil {
        log.Fatal("计数查询失败:", err)
    }
    fmt.Printf("总用户数: %d\n", count)
}
```

## 4. 日志库

### 4.1 zap - Uber高性能日志库

**功能**：高性能、结构化的日志库

**安装**：
```bash
go get go.uber.org/zap
```

**示例**：
```go
package main

import (
    "time"
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func main() {
    // 创建logger
    logger, err := zap.NewProduction()
    if err != nil {
        panic(err)
    }
    defer logger.Sync()

    // 基本日志
    logger.Info("用户登录",
        zap.String("username", "alice"),
        zap.Int("user_id", 123),
        zap.Time("login_time", time.Now()),
    )

    logger.Error("数据库连接失败",
        zap.String("error", "connection timeout"),
        zap.Duration("timeout", 5*time.Second),
    )

    logger.Debug("调试信息",
        zap.String("operation", "cache_update"),
        zap.Bool("success", true),
    )

    // 开发环境logger
    devLogger, err := zap.NewDevelopment()
    if err != nil {
        panic(err)
    }
    defer devLogger.Sync()

    devLogger.Info("这是一条开发环境日志")
    devLogger.Warn("这是一条警告日志")

    // 自定义配置
    config := zap.NewProductionConfig()
    config.Level = zap.NewAtomicLevelAt(zapcore.DebugLevel)
    config.Encoding = "console"
    config.EncoderConfig.TimeKey = "timestamp"
    config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

    customLogger, err := config.Build()
    if err != nil {
        panic(err)
    }
    defer customLogger.Sync()

    customLogger.Info("自定义配置日志",
        zap.String("service", "api"),
        zap.String("version", "1.0.0"),
    )

    // SugaredLogger (更易用但性能稍低)
    sugar := logger.Sugar()
    sugar.Infow("用户操作",
        "action", "create",
        "resource", "user",
        "user_id", 456,
    )

    sugar.Infof("用户 %s 创建了资源 %s", "bob", "document")

    // 命名logger
    apiLogger := logger.Named("api")
    apiLogger.Info("API请求",
        zap.String("method", "GET"),
        zap.String("path", "/api/users"),
    )

    // 带上下文的日志
    ctx := zap.NewExample().With(
        zap.String("request_id", "abc123"),
        zap.String("session_id", "def456"),
    )

    ctx.Info("带上下文的日志")

    // 异步日志
    asyncLogger, err := zap.NewProduction()
    if err != nil {
        panic(err)
    }
    defer asyncLogger.Sync()

    for i := 0; i < 10; i++ {
        asyncLogger.Info("异步日志消息",
            zap.Int("iteration", i),
        )
    }
}
```

### 4.2 logrus - 结构化日志库

**功能**：结构化、可插拔的日志库

**安装**：
```bash
go get github.com/sirupsen/logrus
```

**示例**：
```go
package main

import (
    "os"
    "github.com/sirupsen/logrus"
)

func main() {
    // 创建logger
    logger := logrus.New()

    // 设置日志级别
    logger.SetLevel(logrus.DebugLevel)

    // 设置格式
    logger.SetFormatter(&logrus.JSONFormatter{
        TimestampFormat: "2006-01-02 15:04:05",
    })

    // 设置输出
    logger.SetOutput(os.Stdout)

    // 基本日志
    logger.Info("这是一条信息日志")
    logger.Warn("这是一条警告日志")
    logger.Error("这是一条错误日志")
    logger.Debug("这是一条调试日志")
    logger.Fatal("这是一条致命错误日志") // 会调用os.Exit(1)
    logger.Panic("这是一条恐慌日志")   // 会panic

    // 带字段的日志
    logger.WithFields(logrus.Fields{
        "event": "user_login",
        "user_id": 123,
        "ip": "192.168.1.1",
    }).Info("用户登录")

    // 带上下文的日志
    contextLogger := logger.WithFields(logrus.Fields{
        "request_id": "abc123",
        "session_id": "def456",
    })

    contextLogger.Info("处理请求")
    contextLogger.Warn("请求处理时间过长")

    // 自定义Hook
    logger.AddHook(&MyHook{})

    logger.Info("带Hook的日志")

    // 不同格式
    logger.SetFormatter(&logrus.TextFormatter{
        FullTimestamp: true,
        ForceColors: true,
    })

    logger.Info("文本格式日志")

    // 文件输出
    file, err := os.OpenFile("app.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
    if err == nil {
        logger.SetOutput(file)
        defer file.Close()
    }

    logger.Info("写入文件的日志")

    // 多输出
    logger.SetOutput(os.Stdout) // 恢复控制台输出
}

// 自定义Hook
type MyHook struct{}

func (hook *MyHook) Fire(entry *logrus.Entry) error {
    entry.Data["hook"] = "MyHook"
    return nil
}

func (hook *MyHook) Levels() []logrus.Level {
    return logrus.AllLevels
}
```

## 5. 配置管理库

### 5.1 viper - 配置管理库

**功能**：支持多种配置格式的配置管理

**安装**：
```bash
go get github.com/spf13/viper
```

**示例**：
```go
package main

import (
    "fmt"
    "github.com/spf13/viper"
)

type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    Logging  LoggingConfig  `mapstructure:"logging"`
}

type ServerConfig struct {
    Host string `mapstructure:"host"`
    Port int    `mapstructure:"port"`
}

type DatabaseConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    Username string `mapstructure:"username"`
    Password string `mapstructure:"password"`
    Database string `mapstructure:"database"`
}

type LoggingConfig struct {
    Level  string `mapstructure:"level"`
    Format string `mapstructure:"format"`
}

func main() {
    // 创建viper实例
    v := viper.New()

    // 设置默认值
    v.SetDefault("server.host", "localhost")
    v.SetDefault("server.port", 8080)
    v.SetDefault("database.port", 5432)

    // 配置文件名
    v.SetConfigName("config")
    v.SetConfigType("yaml")

    // 配置文件路径
    v.AddConfigPath(".")
    v.AddConfigPath("./config")
    v.AddConfigPath("/etc/myapp")

    // 读取配置文件
    if err := v.ReadInConfig(); err != nil {
        fmt.Printf("读取配置文件失败: %v\n", err)
    } else {
        fmt.Printf("使用配置文件: %s\n", v.ConfigFileUsed())
    }

    // 环境变量
    v.AutomaticEnv()
    v.SetEnvPrefix("MYAPP")
    v.BindEnv("server.host", "MYAPP_SERVER_HOST")
    v.BindEnv("server.port", "MYAPP_SERVER_PORT")

    // 命令行标志
    pflag.String("host", "", "服务器主机")
    pflag.Int("port", 0, "服务器端口")
    pflag.Parse()

    v.BindPFlags(pflag.CommandLine)

    // 读取配置值
    host := v.GetString("server.host")
    port := v.GetInt("server.port")
    dbHost := v.GetString("database.host")
    dbPort := v.GetInt("database.port")

    fmt.Printf("配置: host=%s, port=%d, db_host=%s, db_port=%d\n", host, port, dbHost, dbPort)

    // 监听配置变化
    v.WatchConfig()
    v.OnConfigChange(func(e fsnotify.Event) {
        fmt.Printf("配置文件变化: %s\n", e.Name)
        // 重新加载配置
    })

    // 解析到结构体
    var config Config
    if err := v.Unmarshal(&config); err != nil {
        fmt.Printf("解析配置失败: %v\n", err)
    } else {
        fmt.Printf("结构体配置: %+v\n", config)
    }

    // 设置配置值
    v.Set("server.host", "newhost")
    v.Set("logging.level", "debug")

    // 写入配置文件
    if err := v.WriteConfigAs("config_new.yaml"); err != nil {
        fmt.Printf("写入配置文件失败: %v\n", err)
    }

    // 子配置
    serverConfig := v.Sub("server")
    if serverConfig != nil {
        fmt.Printf("服务器配置: host=%s, port=%d\n",
            serverConfig.GetString("host"),
            serverConfig.GetInt("port"))
    }

    // 检查配置是否存在
    if v.IsSet("server.host") {
        fmt.Println("server.host 已设置")
    }

    // 获取所有键
    allKeys := v.AllKeys()
    fmt.Printf("所有配置键: %v\n", allKeys)
}
```

## 6. 命令行库

### 6.1 cobra - 强大的命令行应用框架

**功能**：创建强大的命令行应用

**安装**：
```bash
go get github.com/spf13/cobra
```

**示例**：
```go
package main

import (
    "fmt"
    "github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "My application does amazing things",
    Long:  `My application is a powerful tool that can do amazing things.`,
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("Welcome to My App!")
    },
}

var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "Print the version number",
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("My App v1.0.0")
    },
}

var greetCmd = &cobra.Command{
    Use:   "greet [name]",
    Short: "Greet someone",
    Args:  cobra.ExactArgs(1),
    Run: func(cmd *cobra.Command, args []string) {
        name := args[0]
        formal, _ := cmd.Flags().GetBool("formal")

        if formal {
            fmt.Printf("Good day, %s!\n", name)
        } else {
            fmt.Printf("Hello, %s!\n", name)
        }
    },
}

var serveCmd = &cobra.Command{
    Use:   "serve",
    Short: "Start the server",
    Run: func(cmd *cobra.Command, args []string) {
        port, _ := cmd.Flags().GetInt("port")
        host, _ := cmd.Flags().GetString("host")

        fmt.Printf("Starting server on %s:%d\n", host, port)
        // 启动服务器逻辑
    },
}

func init() {
    // 为greet命令添加标志
    greetCmd.Flags().BoolP("formal", "f", false, "Use formal greeting")

    // 为serve命令添加标志
    serveCmd.Flags().IntP("port", "p", 8080, "Port to run server on")
    serveCmd.Flags().StringP("host", "H", "localhost", "Host to bind to")

    // 添加子命令
    rootCmd.AddCommand(versionCmd)
    rootCmd.AddCommand(greetCmd)
    rootCmd.AddCommand(serveCmd)

    // 添加全局标志
    rootCmd.PersistentFlags().BoolP("verbose", "v", false, "Verbose output")
    rootCmd.PersistentFlags().StringP("config", "c", "", "Config file path")
}

func main() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}
```

## 7. 缓存库

### 7.1 redis-go - Redis客户端

**功能**：Redis的Go客户端

**安装**：
```bash
go get github.com/redis/go-redis/v9
```

**示例**：
```go
package main

import (
    "context"
    "fmt"
    "time"

    "github.com/redis/go-redis/v9"
)

type User struct {
    ID    int    `redis:"id"`
    Name  string `redis:"name"`
    Email string `redis:"email"`
}

func main() {
    // 创建Redis客户端
    rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
        Password: "", // 无密码
        DB:       0,  // 默认数据库
    })

    // 测试连接
    ctx := context.Background()
    if err := rdb.Ping(ctx).Err(); err != nil {
        panic(err)
    }

    fmt.Println("Redis连接成功")

    // 字符串操作
    err := rdb.Set(ctx, "key1", "value1", time.Hour).Err()
    if err != nil {
        panic(err)
    }

    val, err := rdb.Get(ctx, "key1").Result()
    if err != nil {
        panic(err)
    }
    fmt.Printf("key1 = %s\n", val)

    // 设置过期时间
    err = rdb.SetEX(ctx, "temp_key", "temp_value", 10*time.Second).Err()
    if err != nil {
        panic(err)
    }

    // 检查键是否存在
    exists, err := rdb.Exists(ctx, "key1").Result()
    if err != nil {
        panic(err)
    }
    fmt.Printf("key1 exists: %d\n", exists)

    // 删除键
    deleted, err := rdb.Del(ctx, "temp_key").Result()
    if err != nil {
        panic(err)
    }
    fmt.Printf("Deleted keys: %d\n", deleted)

    // 哈希操作
    user := User{
        ID:    1,
        Name:  "Alice",
        Email: "alice@example.com",
    }

    err = rdb.HSet(ctx, "user:1", map[string]interface{}{
        "id":    user.ID,
        "name":  user.Name,
        "email": user.Email,
    }).Err()
    if err != nil {
        panic(err)
    }

    var user2 User
    err = rdb.HGetAll(ctx, "user:1").Scan(&user2)
    if err != nil {
        panic(err)
    }
    fmt.Printf("User from hash: %+v\n", user2)

    // 列表操作
    err = rdb.LPush(ctx, "mylist", "item1", "item2", "item3").Err()
    if err != nil {
        panic(err)
    }

    listItems, err := rdb.LRange(ctx, "mylist", 0, -1).Result()
    if err != nil {
        panic(err)
    }
    fmt.Printf("List items: %v\n", listItems)

    // 集合操作
    err = rdb.SAdd(ctx, "myset", "member1", "member2", "member3").Err()
    if err != nil {
        panic(err)
    }

    setMembers, err := rdb.SMembers(ctx, "myset").Result()
    if err != nil {
        panic(err)
    }
    fmt.Printf("Set members: %v\n", setMembers)

    // 有序集合操作
    err = rdb.ZAdd(ctx, "leaderboard", redis.Z{
        Score:  100,
        Member: "player1",
    }, redis.Z{
        Score:  200,
        Member: "player2",
    }).Err()
    if err != nil {
        panic(err)
    }

    topPlayers, err := rdb.ZRevRangeWithScores(ctx, "leaderboard", 0, 2).Result()
    if err != nil {
        panic(err)
    }
    fmt.Printf("Top players: %v\n", topPlayers)

    // 事务
    tx := rdb.TxPipeline()

    tx.Set(ctx, "key2", "value2", time.Hour)
    tx.Incr(ctx, "counter")
    tx.HSet(ctx, "user:2", "name", "Bob")

    _, err = tx.Exec(ctx)
    if err != nil {
        panic(err)
    }

    // 发布订阅
    pubsub := rdb.Subscribe(ctx, "channel1")
    defer pubsub.Close()

    go func() {
        for msg := range pubsub.Channel() {
            fmt.Printf("Received message: %s\n", msg.Payload)
        }
    }()

    err = rdb.Publish(ctx, "channel1", "Hello, Redis!").Err()
    if err != nil {
        panic(err)
    }

    time.Sleep(1 * time.Second)

    // 连接池配置
    rdb = redis.NewClient(&redis.Options{
        Addr:         "localhost:6379",
        Password:     "",
        DB:           0,
        PoolSize:     10,
        MinIdleConns: 2,
        MaxRetries:   3,
        DialTimeout:  5 * time.Second,
        ReadTimeout:  3 * time.Second,
        WriteTimeout: 3 * time.Second,
        PoolTimeout:  4 * time.Second,
    })

    // Lua脚本
    script := redis.NewScript(`
        local current = redis.call('GET', KEYS[1])
        if current then
            return tonumber(current) + tonumber(ARGV[1])
        else
            return tonumber(ARGV[1])
        end
    `)

    result, err := script.Run(ctx, rdb, []string{"counter"}, 5).Result()
    if err != nil {
        panic(err)
    }
    fmt.Printf("Lua script result: %v\n", result)
}
```

## 8. 验证库

### 8.1 validator - 结构体验证库

**功能**：强大的结构体验证库

**安装**：
```bash
go get github.com/go-playground/validator/v10
```

**示例**：
```go
package main

import (
    "fmt"
    "github.com/go-playground/validator/v10"
)

type User struct {
    Name     string `validate:"required,min=3,max=50"`
    Email    string `validate:"required,email"`
    Age      int    `validate:"gte=18,lte=120"`
    Password string `validate:"required,min=8"`
    Phone    string `validate:"e164"`
}

type Product struct {
    Name        string  `validate:"required"`
    Price       float64 `validate:"required,gte=0"`
    SKU         string  `validate:"required,len=10"`
    Description string  `validate:"max=500"`
}

func main() {
    validate := validator.New()

    // 验证用户
    user := User{
        Name:     "Jo", // 太短
        Email:    "invalid-email",
        Age:      15,  // 太小
        Password: "short",
        Phone:    "123",
    }

    err := validate.Struct(user)
    if err != nil {
        // 获取验证错误
        for _, err := range err.(validator.ValidationErrors) {
            fmt.Printf("字段 %s 验证失败: %s\n", err.Field(), err.Tag())
        }
    }

    // 有效用户
    validUser := User{
        Name:     "Alice Smith",
        Email:    "alice@example.com",
        Age:      25,
        Password: "securepassword123",
        Phone:    "+1234567890",
    }

    err = validate.Struct(validUser)
    if err == nil {
        fmt.Println("用户验证通过")
    }

    // 验证产品
    product := Product{
        Name:  "Laptop",
        Price: -100, // 负价格
        SKU:   "123",  // 长度错误
    }

    err = validate.Struct(product)
    if err != nil {
        for _, err := range err.(validator.ValidationErrors) {
            fmt.Printf("产品字段 %s 验证失败: %s\n", err.Field(), err.Tag())
        }
    }

    // 自定义验证函数
    validate.RegisterValidation("custom_date", func(fl validator.FieldLevel) bool {
        dateStr := fl.Field().String()
        // 自定义日期验证逻辑
        return len(dateStr) == 10 && dateStr[4] == '-' && dateStr[7] == '-'
    })

    type Event struct {
        Name string `validate:"required"`
        Date string `validate:"required,custom_date"`
    }

    event := Event{
        Name: "Conference",
        Date: "2024-01-01",
    }

    err = validate.Struct(event)
    if err == nil {
        fmt.Println("事件验证通过")
    }

    // 翻译错误消息
    en := en.New()
    uni := ut.New(en, en)
    trans, _ := uni.GetTranslator("en")

    _ = en_trans.RegisterDefaultTranslations(validate, trans)

    err = validate.Struct(user)
    if err != nil {
        errs := err.(validator.ValidationErrors)
        for _, e := range errs {
            fmt.Println(e.Translate(trans))
        }
    }

    // 变量验证
    email := "invalid-email"
    err = validate.Var(email, "required,email")
    if err != nil {
        fmt.Println("邮箱验证失败:", err)
    }

    // 跨字段验证
    type ChangePassword struct {
        OldPassword     string `validate:"required"`
        NewPassword     string `validate:"required,min=8"`
        ConfirmPassword string `validate:"required,eqfield=NewPassword"`
    }

    changePwd := ChangePassword{
        OldPassword:     "oldpass",
        NewPassword:     "newpassword",
        ConfirmPassword: "different", // 不匹配
    }

    err = validate.Struct(changePwd)
    if err != nil {
        for _, err := range err.(validator.ValidationErrors) {
            fmt.Printf("密码变更字段 %s 验证失败: %s\n", err.Field(), err.Tag())
        }
    }
}
```

## 9. 测试库

### 9.1 testify - 测试工具包

**功能**：提供断言、mock和suite功能

**安装**：
```bash
go get github.com/stretchr/testify
```

**示例**：
```go
package main

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/suite"
)

// 基本断言示例
func TestBasicAssertions(t *testing.T) {
    // 相等断言
    assert.Equal(t, 42, 42, "它们应该相等")
    assert.NotEqual(t, 42, 43, "它们不应该相等")

    // 布尔断言
    assert.True(t, true, "应该是true")
    assert.False(t, false, "应该是false")

    // nil断言
    assert.Nil(t, nil, "应该是nil")
    assert.NotNil(t, "not nil", "不应该为nil")

    // 包含断言
    assert.Contains(t, "Hello World", "World", "应该包含World")
    assert.NotContains(t, "Hello World", "Bye", "不应该包含Bye")

    // 错误断言
    err := someFunction()
    assert.Error(t, err, "应该返回错误")
    assert.NoError(t, nil, "不应该有错误")

    // 类型断言
    var value interface{} = "string"
    assert.IsType(t, "", value, "应该是字符串类型")

    // 数值比较断言
    assert.Greater(t, 10, 5, "10应该大于5")
    assert.Less(t, 5, 10, "5应该小于10")
    assert.InDelta(t, 3.14159, 3.14, 0.01, "应该在误差范围内")
}

// Mock示例
type Database interface {
    GetUser(id int) (*User, error)
    SaveUser(user *User) error
}

type MockDatabase struct {
    mock.Mock
}

func (m *MockDatabase) GetUser(id int) (*User, error) {
    args := m.Called(id)
    return args.Get(0).(*User), args.Error(1)
}

func (m *MockDatabase) SaveUser(user *User) error {
    args := m.Called(user)
    return args.Error(0)
}

func TestUserService(t *testing.T) {
    mockDB := new(MockDatabase)

    // 设置mock期望
    expectedUser := &User{ID: 1, Name: "Alice"}
    mockDB.On("GetUser", 1).Return(expectedUser, nil)
    mockDB.On("SaveUser", expectedUser).Return(nil)

    // 测试
    service := NewUserService(mockDB)
    user, err := service.GetUser(1)

    // 断言
    assert.NoError(t, err)
    assert.Equal(t, expectedUser, user)

    // 验证mock调用
    mockDB.AssertExpectations(t)
}

// Suite示例
type UserServiceTestSuite struct {
    suite.Suite
    service   *UserService
    mockDB    *MockDatabase
    testUser  *User
}

func (suite *UserServiceTestSuite) SetupTest() {
    suite.mockDB = new(MockDatabase)
    suite.service = NewUserService(suite.mockDB)
    suite.testUser = &User{ID: 1, Name: "Alice", Email: "alice@example.com"}
}

func (suite *UserServiceTestSuite) TestGetUser() {
    // 设置mock
    suite.mockDB.On("GetUser", 1).Return(suite.testUser, nil)

    // 测试
    user, err := suite.service.GetUser(1)

    // 断言
    suite.NoError(err)
    suite.Equal(suite.testUser, user)
    suite.mockDB.AssertExpectations(suite.T())
}

func (suite *UserServiceTestSuite) TestCreateUser() {
    suite.mockDB.On("SaveUser", suite.testUser).Return(nil)

    err := suite.service.CreateUser(suite.testUser)

    suite.NoError(err)
    suite.mockDB.AssertExpectations(suite.T())
}

func TestUserServiceSuite(t *testing.T) {
    suite.Run(t, new(UserServiceTestSuite))
}

// HTTP测试示例
func TestHTTPHandler(t *testing.T) {
    router := setupRouter()

    // 测试GET请求
    w := httptest.NewRecorder()
    req, _ := http.NewRequest("GET", "/users/1", nil)
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)
    assert.Contains(t, w.Body.String(), "Alice")

    // 测试POST请求
    w = httptest.NewRecorder()
    req, _ = http.NewRequest("POST", "/users", strings.NewReader(`{"name":"Bob","email":"bob@example.com"}`))
    req.Header.Set("Content-Type", "application/json")
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusCreated, w.Code)
    assert.Contains(t, w.Body.String(), "Bob")
}

// 性能测试示例
func BenchmarkStringConcatenation(b *testing.B) {
    str1 := "Hello"
    str2 := "World"

    for i := 0; i < b.N; i++ {
        result := str1 + str2
        _ = result
    }
}

func BenchmarkStringBuilder(b *testing.B) {
    str1 := "Hello"
    str2 := "World"
    var builder strings.Builder

    for i := 0; i < b.N; i++ {
        builder.Reset()
        builder.WriteString(str1)
        builder.WriteString(str2)
        _ = builder.String()
    }
}
```

## 10. 工具库

### 10.1 uuid - UUID生成库

**功能**：生成UUID

**安装**：
```bash
go get github.com/google/uuid
```

**示例**：
```go
package main

import (
    "fmt"
    "github.com/google/uuid"
)

func main() {
    // 生成UUID v4
    id := uuid.New()
    fmt.Printf("UUID v4: %s\n", id.String())

    // 解析UUID
    parsed, err := uuid.Parse("123e4567-e89b-12d3-a456-426614174000")
    if err != nil {
        panic(err)
    }
    fmt.Printf("解析的UUID: %s\n", parsed.String())

    // 生成UUID v1
    v1 := uuid.NewUUID()
    fmt.Printf("UUID v1: %s\n", v1.String())

    // 生成UUID v3 (基于MD5哈希)
    namespace := uuid.MustParse("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
    v3 := uuid.NewMD5(namespace, []byte("example.com"))
    fmt.Printf("UUID v3: %s\n", v3.String())

    // 生成UUID v5 (基于SHA-1哈希)
    v5 := uuid.NewSHA1(namespace, []byte("example.com"))
    fmt.Printf("UUID v5: %s\n", v5.String())

    // 检查UUID版本
    fmt.Printf("UUID版本: %d\n", id.Version())

    // 检查UUID变体
    fmt.Printf("UUID变体: %d\n", id.Variant())

    // 零值UUID
    nilUUID := uuid.Nil
    fmt.Printf("零值UUID: %s\n", nilUUID.String())

    // UUID比较
    id1 := uuid.New()
    id2 := uuid.New()
    fmt.Printf("UUID相等: %t\n", id1 == id2)
    fmt.Printf("UUID比较: %d\n", id1.Compare(id2))

    // 从字符串创建UUID
    fromString, err := uuid.Parse("123e4567-e89b-12d3-a456-426614174000")
    if err != nil {
        panic(err)
    }
    fmt.Printf("从字符串创建: %s\n", fromString.String())

    // 从字节数组创建UUID
    var bytes [16]byte
    copy(bytes[:], []byte("1234567890123456"))
    fromBytes := uuid.FromBytesOrNil(bytes[:])
    fmt.Printf("从字节数组创建: %s\n", fromBytes.String())
}
```

### 10.2 bcrypt - 密码哈希库

**功能**：密码哈希和验证

**安装**：
```bash
go get golang.org/x/crypto/bcrypt
```

**示例**：
```go
package main

import (
    "fmt"
    "golang.org/x/crypto/bcrypt"
)

func main() {
    password := "mySecurePassword123"

    // 生成哈希
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    if err != nil {
        panic(err)
    }

    fmt.Printf("哈希密码: %s\n", hashedPassword)

    // 验证密码
    err = bcrypt.CompareHashAndPassword(hashedPassword, []byte(password))
    if err == nil {
        fmt.Println("密码验证成功")
    }

    // 验证错误密码
    err = bcrypt.CompareHashAndPassword(hashedPassword, []byte("wrongPassword"))
    if err != nil {
        fmt.Println("密码验证失败:", err)
    }

    // 使用不同的cost
    hashedPasswordHighCost, err := bcrypt.GenerateFromPassword([]byte(password), 12)
    if err != nil {
        panic(err)
    }

    fmt.Printf("高cost哈希: %s\n", hashedPasswordHighCost)

    // 验证高cost哈希
    err = bcrypt.CompareHashAndPassword(hashedPasswordHighCost, []byte(password))
    if err == nil {
        fmt.Println("高cost密码验证成功")
    }

    // 检查哈希是否有效
    cost, err := bcrypt.Cost(hashedPassword)
    if err != nil {
        panic(err)
    }
    fmt.Printf("哈希cost: %d\n", cost)

    // 密码哈希函数
    func hashPassword(password string) (string, error) {
        bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
        return string(bytes), err
    }

    func checkPasswordHash(password, hash string) bool {
        err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
        return err == nil
    }

    // 使用函数
    hash, err := hashPassword("anotherPassword")
    if err != nil {
        panic(err)
    }

    isValid := checkPasswordHash("anotherPassword", hash)
    fmt.Printf("密码验证: %t\n", isValid)
}
```

## 流行库选择建议

### 1. JSON处理
- **标准库encoding/json**: 简单使用场景
- **json-iterator/go**: 需要更高性能时
- **segmentio/encoding**: 需要极致性能时

### 2. HTTP客户端
- **标准库net/http**: 简单请求
- **resty**: 需要便捷的API和重试功能
- **fasthttp**: 需要极致性能时

### 3. 数据库
- **标准库database/sql**: 基础使用
- **sqlx**: 需要更多便利功能
- **pgx**: PostgreSQL专用，高性能

### 4. 日志
- **标准库log**: 简单日志
- **zap**: 高性能、结构化日志
- **logrus**: 功能丰富的结构化日志

### 5. 配置管理
- **viper**: 支持多种格式，功能全面

### 6. 命令行
- **cobra**: 功能强大的命令行框架

### 7. 缓存
- **redis-go**: Redis客户端

### 8. 验证
- **validator**: 强大的结构体验证

### 9. 测试
- **testify**: 提供断言、mock和suite功能

### 10. 工具
- **uuid**: UUID生成
- **bcrypt**: 密码哈希

这些库都是Go生态系统中经过验证的流行库，选择合适的库可以大大提高开发效率和代码质量。