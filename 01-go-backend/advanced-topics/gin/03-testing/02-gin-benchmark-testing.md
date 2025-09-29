# Gin基准测试

## 目录
- [基准测试概述](#基准测试概述)
- [HTTP基准测试](#HTTP基准测试)
- [路由性能测试](#路由性能测试)
- [中间件性能测试](#中间件性能测试)
- [数据库性能测试](#数据库性能测试)
- [并发性能测试](#并发性能测试)
- [内存性能测试](#内存性能测试)
- [性能分析和优化](#性能分析和优化)

## 基准测试概述

### 基准测试基础
```go
package benchmark

import (
    "fmt"
    "runtime"
    "testing"
    "time"
)

// 基础基准测试
func BenchmarkBasicOperation(b *testing.B) {
    for i := 0; i < b.N; i++ {
        // 执行要测试的操作
        result := someOperation()
        if result != expected {
            b.Fatal("Unexpected result")
        }
    }
}

// 带内存统计的基准测试
func BenchmarkWithMemStats(b *testing.B) {
    var m runtime.MemStats
    runtime.GC()
    runtime.ReadMemStats(&m)

    startAllocs := m.Allocs
    startBytes := m.TotalAlloc

    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        someOperation()
    }

    b.StopTimer()

    runtime.ReadMemStats(&m)
    b.Logf("Allocs: %d, Total bytes: %d", m.Allocs-startAllocs, m.TotalAlloc-startBytes)
}

// 基准测试辅助函数
func someOperation() int {
    return 42
}

const expected = 42

// 并发基准测试
func BenchmarkConcurrentOperation(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            someOperation()
        }
    })
}

// 带子测试的基准测试
func BenchmarkDifferentOperations(b *testing.B) {
    tests := []struct {
        name string
        fn   func()
    }{
        {"Operation1", operation1},
        {"Operation2", operation2},
        {"Operation3", operation3},
    }

    for _, tt := range tests {
        b.Run(tt.name, func(b *testing.B) {
            for i := 0; i < b.N; i++ {
                tt.fn()
            }
        })
    }
}

func operation1() { /* 操作1实现 */ }
func operation2() { /* 操作2实现 */ }
func operation3() { /* 操作3实现 */ }
```

### 基准测试配置
```go
package benchmark

import (
    "flag"
    "fmt"
    "os"
    "testing"
)

// 基准测试配置
type BenchmarkConfig struct {
    Duration       time.Duration
    WarmupDuration time.Duration
    Concurrency    int
    ReportFile     string
    EnableProfile  bool
}

var config = BenchmarkConfig{
    Duration:       10 * time.Second,
    WarmupDuration: 2 * time.Second,
    Concurrency:    10,
    ReportFile:     "",
    EnableProfile:  false,
}

func init() {
    flag.DurationVar(&config.Duration, "duration", config.Duration, "Benchmark duration")
    flag.DurationVar(&config.WarmupDuration, "warmup", config.WarmupDuration, "Warmup duration")
    flag.IntVar(&config.Concurrency, "concurrency", config.Concurrency, "Concurrency level")
    flag.StringVar(&config.ReportFile, "report", config.ReportFile, "Report file path")
    flag.BoolVar(&config.EnableProfile, "profile", config.EnableProfile, "Enable profiling")
}

// 基准测试运行器
type BenchmarkRunner struct {
    config BenchmarkConfig
}

func NewBenchmarkRunner(config BenchmarkConfig) *BenchmarkRunner {
    return &BenchmarkRunner{config: config}
}

// 运行基准测试
func (br *BenchmarkRunner) Run(benchmarks map[string]func(*testing.B)) *BenchmarkReport {
    report := &BenchmarkReport{
        Results: make(map[string]*BenchmarkResult),
        Config:  br.config,
    }

    // 预热
    br.warmup()

    // 运行基准测试
    for name, fn := range benchmarks {
        result := br.runSingleBenchmark(name, fn)
        report.Results[name] = result
    }

    // 生成报告
    if br.config.ReportFile != "" {
        br.generateReport(report)
    }

    return report
}

// 预热
func (br *BenchmarkRunner) warmup() {
    fmt.Printf("Warming up for %v...\n", br.config.WarmupDuration)
    time.Sleep(br.config.WarmupDuration)
}

// 运行单个基准测试
func (br *BenchmarkRunner) runSingleBenchmark(name string, fn func(*testing.B)) *BenchmarkResult {
    fmt.Printf("Running benchmark: %s\n", name)

    result := &BenchmarkResult{
        Name: name,
    }

    // 启用CPU分析
    if br.config.EnableProfile {
        profileFile := fmt.Sprintf("cpu_%s.prof", name)
        f, err := os.Create(profileFile)
        if err != nil {
            fmt.Printf("Failed to create profile file: %v\n", err)
        } else {
            defer f.Close()
            if err := testing.StartCPUProfile(f); err != nil {
                fmt.Printf("Failed to start CPU profile: %v\n", err)
            } else {
                defer testing.StopCPUProfile()
            }
        }
    }

    // 创建测试
    b := &testing.B{}
    b.N = int(br.config.Duration / time.Microsecond) // 转换为微秒

    // 重置计时器
    b.ResetTimer()

    // 运行测试
    start := time.Now()
    fn(b)
    duration := time.Since(start)

    // 收集结果
    result.Duration = duration
    result.Operations = b.N
    result.OPS = float64(b.N) / duration.Seconds()

    // 收集内存统计
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    result.Allocs = m.Allocs
    result.TotalAlloc = m.TotalAlloc

    fmt.Printf("Result: %s - Ops: %d, Duration: %v, OPS: %.2f\n",
        name, result.Operations, result.Duration, result.OPS)

    return result
}

// 基准测试结果
type BenchmarkResult struct {
    Name        string
    Duration    time.Duration
    Operations  int
    OPS         float64
    Allocs      uint64
    TotalAlloc  uint64
}

// 基准测试报告
type BenchmarkReport struct {
    Results map[string]*BenchmarkResult
    Config  BenchmarkConfig
}

// 生成报告
func (br *BenchmarkRunner) generateReport(report *BenchmarkReport) {
    // 实现报告生成逻辑
    fmt.Printf("Generating benchmark report: %s\n", br.config.ReportFile)
    // 这里可以生成JSON、CSV或HTML格式的报告
}
```

## HTTP基准测试

### HTTP服务器基准测试
```go
package benchmark

import (
    "fmt"
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/gin-gonic/gin"
)

// HTTP服务器基准测试
func BenchmarkHTTPServer(b *testing.B) {
    // 创建Gin引擎
    r := gin.New()

    // 添加路由
    r.GET("/simple", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    r.GET("/complex", func(c *gin.Context) {
        time.Sleep(1 * time.Millisecond) // 模拟处理时间
        c.JSON(200, gin.H{
            "message": "Complex response",
            "data":    []string{"item1", "item2", "item3"},
            "timestamp": time.Now().Unix(),
        })
    })

    // 创建测试服务器
    server := httptest.NewServer(r)
    defer server.Close()

    // 测试简单请求
    b.Run("SimpleRequest", func(b *testing.B) {
        client := http.Client{}
        for i := 0; i < b.N; i++ {
            resp, err := client.Get(server.URL + "/simple")
            if err != nil {
                b.Fatal(err)
            }
            resp.Body.Close()
        }
    })

    // 测试复杂请求
    b.Run("ComplexRequest", func(b *testing.B) {
        client := http.Client{}
        for i := 0; i < b.N; i++ {
            resp, err := client.Get(server.URL + "/complex")
            if err != nil {
                b.Fatal(err)
            }
            resp.Body.Close()
        }
    })
}

// 并发HTTP基准测试
func BenchmarkConcurrentHTTP(b *testing.B) {
    r := gin.New()
    r.GET("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello World"})
    })

    server := httptest.NewServer(r)
    defer server.Close()

    b.RunParallel(func(pb *testing.PB) {
        client := http.Client{}
        for pb.Next() {
            resp, err := client.Get(server.URL + "/test")
            if err != nil {
                b.Fatal(err)
            }
            resp.Body.Close()
        }
    })
}

// 不同HTTP方法基准测试
func BenchmarkHTTPMethods(b *testing.B) {
    r := gin.New()

    r.GET("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"method": "GET"})
    })

    r.POST("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"method": "POST"})
    })

    r.PUT("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"method": "PUT"})
    })

    r.DELETE("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"method": "DELETE"})
    })

    server := httptest.NewServer(r)
    defer server.Close()

    methods := []string{"GET", "POST", "PUT", "DELETE"}
    client := http.Client{}

    for _, method := range methods {
        b.Run(method, func(b *testing.B) {
            for i := 0; i < b.N; i++ {
                req, err := http.NewRequest(method, server.URL+"/test", nil)
                if err != nil {
                    b.Fatal(err)
                }
                resp, err := client.Do(req)
                if err != nil {
                    b.Fatal(err)
                }
                resp.Body.Close()
            }
        })
    }
}

// HTTP负载测试
func BenchmarkHTTPLoad(b *testing.B) {
    // 配置负载测试参数
    configs := []struct {
        name        string
        concurrency int
        duration    time.Duration
    }{
        {"LowConcurrency", 10, 5 * time.Second},
        {"MediumConcurrency", 50, 5 * time.Second},
        {"HighConcurrency", 100, 5 * time.Second},
    }

    r := gin.New()
    r.GET("/load-test", func(c *gin.Context) {
        // 模拟一些处理时间
        time.Sleep(10 * time.Millisecond)
        c.JSON(200, gin.H{"message": "Load test response"})
    })

    server := httptest.NewServer(r)
    defer server.Close()

    for _, config := range configs {
        b.Run(config.name, func(b *testing.B) {
            runner := NewLoadTester(config.concurrency, config.duration)
            result := runner.Run(server.URL + "/load-test")

            b.Logf("Load test result - Concurrency: %d, Duration: %v, "+
                "TotalRequests: %d, SuccessRate: %.2f%%, AvgLatency: %v",
                config.concurrency, config.duration, result.TotalRequests,
                result.SuccessRate, result.AvgLatency)
        })
    }
}

// 负载测试器
type LoadTester struct {
    concurrency int
    duration    time.Duration
}

func NewLoadTester(concurrency int, duration time.Duration) *LoadTester {
    return &LoadTester{
        concurrency: concurrency,
        duration:    duration,
    }
}

func (lt *LoadTester) Run(url string) *LoadTestResult {
    result := &LoadTestResult{
        StartTime: time.Now(),
    }

    // 创建工作池
    workChan := make(chan struct{}, lt.concurrency)
    resultChan := make(chan *RequestResult, lt.concurrency*1000)

    // 启动工作器
    for i := 0; i < lt.concurrency; i++ {
        go lt.worker(url, workChan, resultChan)
    }

    // 开始测试
    go func() {
        for {
            select {
            case workChan <- struct{}{}:
            case <-time.After(lt.duration):
                close(workChan)
                return
            }
        }
    }()

    // 收集结果
    go func() {
        for reqResult := range resultChan {
            result.AddResult(reqResult)
        }
    }()

    // 等待测试完成
    time.Sleep(lt.duration)
    close(resultChan)

    result.EndTime = time.Now()
    result.CalculateStats()

    return result
}

func (lt *LoadTester) worker(url string, workChan <-chan struct{}, resultChan chan<- *RequestResult) {
    client := http.Client{}

    for range workChan {
        start := time.Now()

        resp, err := client.Get(url)
        duration := time.Since(start)

        reqResult := &RequestResult{
            Duration: duration,
            Success:  err == nil && resp.StatusCode == 200,
        }

        if resp != nil {
            resp.Body.Close()
        }

        resultChan <- reqResult
    }
}

// 负载测试结果
type LoadTestResult struct {
    StartTime    time.Time
    EndTime      time.Time
    TotalRequests int
    SuccessCount int
    ErrorCount   int
    AvgLatency   time.Duration
    MaxLatency   time.Duration
    MinLatency   time.Duration
    SuccessRate  float64
    results      []*RequestResult
}

type RequestResult struct {
    Duration time.Duration
    Success  bool
}

func (ltr *LoadTestResult) AddResult(result *RequestResult) {
    ltr.results = append(ltr.results, result)
    ltr.TotalRequests++

    if result.Success {
        ltr.SuccessCount++
    } else {
        ltr.ErrorCount++
    }
}

func (ltr *LoadTestResult) CalculateStats() {
    if len(ltr.results) == 0 {
        return
    }

    var totalDuration time.Duration
    minDuration := ltr.results[0].Duration
    maxDuration := ltr.results[0].Duration

    for _, result := range ltr.results {
        totalDuration += result.Duration

        if result.Duration < minDuration {
            minDuration = result.Duration
        }
        if result.Duration > maxDuration {
            maxDuration = result.Duration
        }
    }

    ltr.AvgLatency = totalDuration / time.Duration(len(ltr.results))
    ltr.MinLatency = minDuration
    ltr.MaxLatency = maxDuration

    if ltr.TotalRequests > 0 {
        ltr.SuccessRate = float64(ltr.SuccessCount) / float64(ltr.TotalRequests) * 100
    }
}
```

## 路由性能测试

### 路由匹配基准测试
```go
package benchmark

import (
    "testing"
    "time"

    "github.com/gin-gonic/gin"
)

// 路由匹配基准测试
func BenchmarkRouteMatching(b *testing.B) {
    // 测试不同类型的路由
    routeConfigs := []struct {
        name   string
        routes []string
        test   string
    }{
        {
            name: "StaticRoutes",
            routes: []string{"/users", "/products", "/orders", "/categories"},
            test:   "/users",
        },
        {
            name: "ParamRoutes",
            routes: []string{"/users/:id", "/products/:id", "/orders/:id"},
            test:   "/users/123",
        },
        {
            name: "WildcardRoutes",
            routes: []string{"/users/*action", "/products/*action", "/orders/*action"},
            test:   "/users/profile",
        },
        {
            name: "MixedRoutes",
            routes: []string{
                "/users", "/users/:id", "/users/:id/posts", "/users/:id/posts/:post_id",
                "/products", "/products/:id", "/products/category/:category",
            },
            test: "/users/123/posts/456",
        },
    }

    for _, config := range routeConfigs {
        b.Run(config.name, func(b *testing.B) {
            router := gin.New()

            // 添加路由
            for _, route := range config.routes {
                router.GET(route, func(c *gin.Context) {
                    c.JSON(200, gin.H{"message": "OK"})
                })
            }

            // 创建测试请求
            w := httptest.NewRecorder()
            req, _ := http.NewRequest("GET", config.test, nil)

            // 重置计时器
            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                router.ServeHTTP(w, req)
            }
        })
    }
}

// 路由数量性能影响测试
func BenchmarkRouteCountPerformance(b *testing.B) {
    routeCounts := []int{10, 100, 1000, 10000}
    testPath := "/users/123/posts/456"

    for _, count := range routeCounts {
        b.Run(fmt.Sprintf("RouteCount_%d", count), func(b *testing.B) {
            router := gin.New()

            // 生成大量路由
            for i := 0; i < count; i++ {
                router.GET(fmt.Sprintf("/route%d", i), func(c *gin.Context) {
                    c.JSON(200, gin.H{"message": "OK"})
                })
            }

            // 添加测试路由
            router.GET("/users/:id/posts/:post_id", func(c *gin.Context) {
                c.JSON(200, gin.H{"message": "OK"})
            })

            // 创建测试请求
            w := httptest.NewRecorder()
            req, _ := http.NewRequest("GET", testPath, nil)

            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                router.ServeHTTP(w, req)
            }
        })
    }
}

// 路由组性能测试
func BenchmarkRouteGroups(b *testing.B) {
    // 创建路由器
    router := gin.New()

    // 添加路由组
    api := router.Group("/api")
    {
        v1 := api.Group("/v1")
        {
            v1.GET("/users", func(c *gin.Context) { c.JSON(200, gin.H{"message": "OK"}) })
            v1.GET("/users/:id", func(c *gin.Context) { c.JSON(200, gin.H{"message": "OK"}) })
            v1.POST("/users", func(c *gin.Context) { c.JSON(200, gin.H{"message": "OK"}) })

            v1.GET("/products", func(c *gin.Context) { c.JSON(200, gin.H{"message": "OK"}) })
            v1.GET("/products/:id", func(c *gin.Context) { c.JSON(200, gin.H{"message": "OK"}) })
        }

        v2 := api.Group("/v2")
        {
            v2.GET("/users", func(c *gin.Context) { c.JSON(200, gin.H{"message": "OK"}) })
            v2.GET("/users/:id", func(c *gin.Context) { c.JSON(200, gin.H{"message": "OK"}) })
            v2.POST("/users", func(c *gin.Context) { c.JSON(200, gin.H{"message": "OK"}) })
        }
    }

    // 测试不同路径
    testPaths := []string{
        "/api/v1/users",
        "/api/v1/users/123",
        "/api/v2/users",
        "/api/v2/users/456",
    }

    for _, path := range testPaths {
        b.Run(path, func(b *testing.B) {
            w := httptest.NewRecorder()
            req, _ := http.NewRequest("GET", path, nil)

            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                router.ServeHTTP(w, req)
            }
        })
    }
}

// 路由参数提取性能测试
func BenchmarkRouteParameterExtraction(b *testing.B) {
    router := gin.New()

    // 添加带参数的路由
    router.GET("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(200, gin.H{"user_id": id})
    })

    router.GET("/products/:category/:id", func(c *gin.Context) {
        category := c.Param("category")
        id := c.Param("id")
        c.JSON(200, gin.H{"category": category, "product_id": id})
    })

    router.GET("/files/*filepath", func(c *gin.Context) {
        filepath := c.Param("filepath")
        c.JSON(200, gin.H{"filepath": filepath})
    })

    testCases := []struct {
        name string
        path string
    }{
        {"SingleParam", "/users/12345"},
        {"MultipleParams", "/products/electronics/67890"},
        {"Wildcard", "/files/path/to/document.pdf"},
    }

    for _, tc := range testCases {
        b.Run(tc.name, func(b *testing.B) {
            w := httptest.NewRecorder()
            req, _ := http.NewRequest("GET", tc.path, nil)

            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                router.ServeHTTP(w, req)
            }
        })
    }
}

// 路由冲突检测性能测试
func BenchmarkRouteConflictDetection(b *testing.B) {
    // 创建路由器
    router := gin.New()

    // 添加一些基础路由
    baseRoutes := []string{
        "/users", "/users/:id", "/users/profile",
        "/products", "/products/:id", "/products/search",
    }

    for _, route := range baseRoutes {
        router.GET(route, func(c *gin.Context) {
            c.JSON(200, gin.H{"message": "OK"})
        })
    }

    // 测试冲突检测性能
    conflictRoutes := []string{
        "/users",           // 与现有路由冲突
        "/users/new",       // 不冲突
        "/products/123",    // 参数路由
        "/orders",          // 全新路由
    }

    for _, route := range conflictRoutes {
        b.Run(route, func(b *testing.B) {
            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                // 创建新的路由器用于测试
                testRouter := gin.New()

                // 复制基础路由
                for _, baseRoute := range baseRoutes {
                    testRouter.GET(baseRoute, func(c *gin.Context) {
                        c.JSON(200, gin.H{"message": "OK"})
                    })
                }

                // 尝试添加测试路由
                testRouter.GET(route, func(c *gin.Context) {
                    c.JSON(200, gin.H{"message": "OK"})
                })
            }
        })
    }
}
```

## 中间件性能测试

### 中间件性能基准测试
```go
package benchmark

import (
    "net/http"
    "net/http/httptest"
    "testing"
    "time"

    "github.com/gin-gonic/gin"
)

// 中间件性能基准测试
func BenchmarkMiddlewarePerformance(b *testing.B) {
    // 创建基础路由器
    baseRouter := gin.New()
    baseRouter.GET("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "OK"})
    })

    // 创建带中间件的路由器
    middlewareRouter := gin.New()
    middlewareRouter.Use(LoggerMiddleware())
    middlewareRouter.Use(AuthMiddleware())
    middlewareRouter.Use(CORSMiddleware())
    middlewareRouter.GET("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "OK"})
    })

    // 创建测试服务器
    baseServer := httptest.NewServer(baseRouter)
    defer baseServer.Close()

    middlewareServer := httptest.NewServer(middlewareRouter)
    defer middlewareServer.Close()

    client := http.Client{}

    // 测试基础路由器
    b.Run("BaseRouter", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            resp, err := client.Get(baseServer.URL + "/test")
            if err != nil {
                b.Fatal(err)
            }
            resp.Body.Close()
        }
    })

    // 测试带中间件的路由器
    b.Run("MiddlewareRouter", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            resp, err := client.Get(middlewareServer.URL + "/test")
            if err != nil {
                b.Fatal(err)
            }
            resp.Body.Close()
        }
    })
}

// 单个中间件性能测试
func BenchmarkIndividualMiddleware(b *testing.B) {
    middlewares := []struct {
        name string
        mw   gin.HandlerFunc
    }{
        {"Logger", LoggerMiddleware()},
        {"Auth", AuthMiddleware()},
        {"CORS", CORSMiddleware()},
        {"RateLimit", RateLimitMiddleware()},
        {"Security", SecurityMiddleware()},
    }

    for _, mw := range middlewares {
        b.Run(mw.name, func(b *testing.B) {
            router := gin.New()
            router.Use(mw.mw)
            router.GET("/test", func(c *gin.Context) {
                c.JSON(200, gin.H{"message": "OK"})
            })

            server := httptest.NewServer(router)
            defer server.Close()

            client := http.Client{}

            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                resp, err := client.Get(server.URL + "/test")
                if err != nil {
                    b.Fatal(err)
                }
                resp.Body.Close()
            }
        })
    }
}

// 中间件链长度影响测试
func BenchmarkMiddlewareChainLength(b *testing.B) {
    chainLengths := []int{1, 5, 10, 20, 50}

    for _, length := range chainLengths {
        b.Run(fmt.Sprintf("ChainLength_%d", length), func(b *testing.B) {
            router := gin.New()

            // 添加指定数量的中间件
            for i := 0; i < length; i++ {
                router.Use(SimpleMiddleware(i))
            }

            router.GET("/test", func(c *gin.Context) {
                c.JSON(200, gin.H{"message": "OK"})
            })

            server := httptest.NewServer(router)
            defer server.Close()

            client := http.Client{}

            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                resp, err := client.Get(server.URL + "/test")
                if err != nil {
                    b.Fatal(err)
                }
                resp.Body.Close()
            }
        })
    }
}

// 中间件内存使用测试
func BenchmarkMiddlewareMemoryUsage(b *testing.B) {
    router := gin.New()
    router.Use(LoggerMiddleware())
    router.Use(AuthMiddleware())
    router.Use(CORSMiddleware())
    router.Use(RateLimitMiddleware())
    router.Use(SecurityMiddleware())

    router.GET("/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "OK"})
    })

    server := httptest.NewServer(router)
    defer server.Close()

    client := http.Client{}

    // 运行GC以清理内存
    runtime.GC()

    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    startAllocs := m.Allocs
    startBytes := m.TotalAlloc

    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        resp, err := client.Get(server.URL + "/test")
        if err != nil {
            b.Fatal(err)
        }
        resp.Body.Close()
    }

    runtime.ReadMemStats(&m)
    b.Logf("Memory - Allocs: %d, Total bytes: %d",
        m.Allocs-startAllocs, m.TotalAlloc-startBytes)
}

// 条件中间件性能测试
func BenchmarkConditionalMiddleware(b *testing.B) {
    router := gin.New()

    // 条件中间件
    router.Use(func(c *gin.Context) {
        if c.Request.URL.Path == "/protected" {
            AuthMiddleware()(c)
        } else {
            c.Next()
        }
    })

    router.GET("/public", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Public"})
    })

    router.GET("/protected", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Protected"})
    })

    server := httptest.NewServer(router)
    defer server.Close()

    client := http.Client{}

    // 测试公共路由
    b.Run("PublicRoute", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            resp, err := client.Get(server.URL + "/public")
            if err != nil {
                b.Fatal(err)
            }
            resp.Body.Close()
        }
    })

    // 测试受保护路由
    b.Run("ProtectedRoute", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            req, _ := http.NewRequest("GET", server.URL + "/protected", nil)
            req.Header.Set("Authorization", "valid-token")
            resp, err := client.Do(req)
            if err != nil {
                b.Fatal(err)
            }
            resp.Body.Close()
        }
    })
}

// 中间件示例实现
func LoggerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        c.Next()
        duration := time.Since(start)
        _ = duration // 简化实现
    }
}

func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "valid-token" {
            c.Next()
        } else {
            c.JSON(401, gin.H{"error": "Unauthorized"})
            c.Abort()
        }
    }
}

func CORSMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("Access-Control-Allow-Origin", "*")
        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }
        c.Next()
    }
}

func RateLimitMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 简化的限流实现
        c.Next()
    }
}

func SecurityMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-Frame-Options", "DENY")
        c.Next()
    }
}

func SimpleMiddleware(id int) gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Set(fmt.Sprintf("middleware_%d", id), true)
        c.Next()
    }
}
```

## 数据库性能测试

### 数据库操作基准测试
```go
package benchmark

import (
    "database/sql"
    "testing"
    "time"

    "github.com/jmoiron/sqlx"
    _ "github.com/lib/pq"
)

// 数据库操作基准测试
func BenchmarkDatabaseOperations(b *testing.B) {
    // 数据库连接配置
    db, err := sqlx.Connect("postgres", "user=test dbname=test sslmode=disable")
    if err != nil {
        b.Fatal(err)
    }
    defer db.Close()

    // 准备测试数据
    setupTestData(db)

    // 测试不同类型的数据库操作
    operations := []struct {
        name string
        fn   func(*testing.B, *sqlx.DB)
    }{
        {"SimpleQuery", benchmarkSimpleQuery},
        {"ParameterizedQuery", benchmarkParameterizedQuery},
        {"Insert", benchmarkInsert},
        {"Update", benchmarkUpdate},
        {"Delete", benchmarkDelete},
        {"BatchInsert", benchmarkBatchInsert},
        {"Transaction", benchmarkTransaction},
    }

    for _, op := range operations {
        b.Run(op.name, func(b *testing.B) {
            op.fn(b, db)
        })
    }
}

// 简单查询基准测试
func benchmarkSimpleQuery(b *testing.B, db *sqlx.DB) {
    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        var result int
        err := db.Get(&result, "SELECT COUNT(*) FROM users")
        if err != nil {
            b.Fatal(err)
        }
    }
}

// 参数化查询基准测试
func benchmarkParameterizedQuery(b *testing.B, db *sqlx.DB) {
    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        var user User
        err := db.Get(&user, "SELECT * FROM users WHERE id = $1", i%1000+1)
        if err != nil {
            b.Fatal(err)
        }
    }
}

// 插入操作基准测试
func benchmarkInsert(b *testing.B, db *sqlx.DB) {
    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        _, err := db.Exec("INSERT INTO users (name, email, created_at) VALUES ($1, $2, $3)",
            fmt.Sprintf("user%d", i), fmt.Sprintf("user%d@example.com", i), time.Now())
        if err != nil {
            b.Fatal(err)
        }
    }
}

// 更新操作基准测试
func benchmarkUpdate(b *testing.B, db *sqlx.DB) {
    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        _, err := db.Exec("UPDATE users SET name = $1 WHERE id = $2",
            fmt.Sprintf("updated_user%d", i), i%1000+1)
        if err != nil {
            b.Fatal(err)
        }
    }
}

// 删除操作基准测试
func benchmarkDelete(b *testing.B, db *sqlx.DB) {
    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        _, err := db.Exec("DELETE FROM users WHERE id = $1", i%1000+1)
        if err != nil {
            b.Fatal(err)
        }
    }
}

// 批量插入基准测试
func benchmarkBatchInsert(b *testing.B, db *sqlx.DB) {
    batchSize := 100
    b.ResetTimer()

    for i := 0; i < b.N; i += batchSize {
        // 准备批量数据
        values := make([]interface{}, 0, batchSize*3)
        query := "INSERT INTO users (name, email, created_at) VALUES "

        for j := 0; j < batchSize && i+j < b.N; j++ {
            if j > 0 {
                query += ", "
            }
            query += fmt.Sprintf("($%d, $%d, $%d)", j*3+1, j*3+2, j*3+3)

            values = append(values, fmt.Sprintf("batch_user%d", i+j),
                fmt.Sprintf("batch_user%d@example.com", i+j), time.Now())
        }

        // 执行批量插入
        _, err := db.Exec(query, values...)
        if err != nil {
            b.Fatal(err)
        }
    }
}

// 事务基准测试
func benchmarkTransaction(b *testing.B, db *sqlx.DB) {
    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        tx, err := db.Beginx()
        if err != nil {
            b.Fatal(err)
        }

        // 执行多个操作
        _, err = tx.Exec("INSERT INTO users (name, email, created_at) VALUES ($1, $2, $3)",
            fmt.Sprintf("tx_user%d", i), fmt.Sprintf("tx_user%d@example.com", i), time.Now())
        if err != nil {
            tx.Rollback()
            b.Fatal(err)
        }

        _, err = tx.Exec("UPDATE users SET name = $1 WHERE id = $2",
            fmt.Sprintf("updated_tx_user%d", i), i%1000+1)
        if err != nil {
            tx.Rollback()
            b.Fatal(err)
        }

        err = tx.Commit()
        if err != nil {
            b.Fatal(err)
        }
    }
}

// 连接池性能测试
func BenchmarkConnectionPool(b *testing.B) {
    poolSizes := []int{1, 5, 10, 25, 50, 100}

    for _, size := range poolSizes {
        b.Run(fmt.Sprintf("PoolSize_%d", size), func(b *testing.B) {
            // 创建带特定池大小的数据库连接
            db, err := sqlx.Connect("postgres",
                fmt.Sprintf("user=test dbname=test sslmode=disable pool_max_conns=%d", size))
            if err != nil {
                b.Fatal(err)
            }
            defer db.Close()

            b.ResetTimer()

            // 并发测试连接池性能
            b.RunParallel(func(pb *testing.PB) {
                for pb.Next() {
                    var result int
                    err := db.Get(&result, "SELECT COUNT(*) FROM users")
                    if err != nil {
                        b.Fatal(err)
                    }
                }
            })
        })
    }
}

// 预处理语句性能测试
func BenchmarkPreparedStatements(b *testing.B) {
    db, err := sqlx.Connect("postgres", "user=test dbname=test sslmode=disable")
    if err != nil {
        b.Fatal(err)
    }
    defer db.Close()

    // 准备预处理语句
    stmt, err := db.Preparex("SELECT * FROM users WHERE id = $1")
    if err != nil {
        b.Fatal(err)
    }
    defer stmt.Close()

    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        var user User
        err := stmt.Get(&user, i%1000+1)
        if err != nil {
            b.Fatal(err)
        }
    }
}

// 数据库查询缓存性能测试
func BenchmarkDatabaseCache(b *testing.B) {
    db, err := sqlx.Connect("postgres", "user=test dbname=test sslmode=disable")
    if err != nil {
        b.Fatal(err)
    }
    defer db.Close()

    // 创建缓存层
    cache := NewSimpleCache()

    b.Run("WithoutCache", func(b *testing.B) {
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            var user User
            err := db.Get(&user, "SELECT * FROM users WHERE id = $1", i%1000+1)
            if err != nil {
                b.Fatal(err)
            }
        }
    })

    b.Run("WithCache", func(b *testing.B) {
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            key := fmt.Sprintf("user:%d", i%1000+1)

            // 尝试从缓存获取
            if user, exists := cache.Get(key); exists {
                _ = user.(*User)
            } else {
                // 从数据库获取
                var user User
                err := db.Get(&user, "SELECT * FROM users WHERE id = $1", i%1000+1)
                if err != nil {
                    b.Fatal(err)
                }
                // 存入缓存
                cache.Set(key, &user)
            }
        }
    })
}

// 辅助函数和类型
type User struct {
    ID        int       `db:"id"`
    Name      string    `db:"name"`
    Email     string    `db:"email"`
    CreatedAt time.Time `db:"created_at"`
}

func setupTestData(db *sqlx.DB) {
    // 创建测试表
    db.MustExec(`
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP
        )
    `)

    // 清空测试数据
    db.MustExec("TRUNCATE TABLE users")

    // 插入测试数据
    for i := 1; i <= 1000; i++ {
        db.MustExec("INSERT INTO users (name, email, created_at) VALUES ($1, $2, $3)",
            fmt.Sprintf("user%d", i), fmt.Sprintf("user%d@example.com", i), time.Now())
    }
}

// 简单缓存实现
type SimpleCache struct {
    cache map[string]interface{}
    mutex sync.RWMutex
}

func NewSimpleCache() *SimpleCache {
    return &SimpleCache{
        cache: make(map[string]interface{}),
    }
}

func (c *SimpleCache) Get(key string) (interface{}, bool) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()
    val, exists := c.cache[key]
    return val, exists
}

func (c *SimpleCache) Set(key string, value interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    c.cache[key] = value
}
```

## 并发性能测试

### 并发处理基准测试
```go
package benchmark

import (
    "context"
    "fmt"
    "sync"
    "testing"
    "time"
)

// 并发处理基准测试
func BenchmarkConcurrentProcessing(b *testing.B) {
    // 测试不同的并发级别
    concurrencyLevels := []int{1, 10, 100, 1000}

    for _, level := range concurrencyLevels {
        b.Run(fmt.Sprintf("Concurrency_%d", level), func(b *testing.B) {
            processor := NewConcurrentProcessor(level)

            b.ResetTimer()

            // 使用RunParallel进行并发测试
            b.RunParallel(func(pb *testing.PB) {
                for pb.Next() {
                    processor.Process("test")
                }
            })
        })
    }
}

// 并发处理器
type ConcurrentProcessor struct {
    workers int
    queue   chan string
    wg      sync.WaitGroup
}

func NewConcurrentProcessor(workers int) *ConcurrentProcessor {
    processor := &ConcurrentProcessor{
        workers: workers,
        queue:   make(chan string, workers*100),
    }

    processor.startWorkers()
    return processor
}

func (cp *ConcurrentProcessor) startWorkers() {
    for i := 0; i < cp.workers; i++ {
        cp.wg.Add(1)
        go cp.worker()
    }
}

func (cp *ConcurrentProcessor) worker() {
    defer cp.wg.Done()

    for task := range cp.queue {
        cp.processTask(task)
    }
}

func (cp *ConcurrentProcessor) processTask(task string) {
    // 模拟处理任务
    time.Sleep(100 * time.Microsecond)
    _ = task
}

func (cp *ConcurrentProcessor) Process(task string) {
    cp.queue <- task
}

func (cp *ConcurrentProcessor) Stop() {
    close(cp.queue)
    cp.wg.Wait()
}

// Goroutine池性能测试
func BenchmarkGoroutinePool(b *testing.B) {
    poolSizes := []int{10, 50, 100, 500}

    for _, size := range poolSizes {
        b.Run(fmt.Sprintf("PoolSize_%d", size), func(b *testing.B) {
            pool := NewGoroutinePool(size, 1000)
            defer pool.Stop()

            b.ResetTimer()

            b.RunParallel(func(pb *testing.PB) {
                for pb.Next() {
                    pool.Submit(func() {
                        time.Sleep(10 * time.Microsecond)
                    })
                }
            })
        })
    }
}

// Goroutine池实现
type GoroutinePool struct {
    workers   int
    taskQueue chan Task
    workerPool chan struct{}
    wg        sync.WaitGroup
    ctx       context.Context
    cancel    context.CancelFunc
}

type Task func()

func NewGoroutinePool(workers, queueSize int) *GoroutinePool {
    ctx, cancel := context.WithCancel(context.Background())

    pool := &GoroutinePool{
        workers:    workers,
        taskQueue:  make(chan Task, queueSize),
        workerPool: make(chan struct{}, workers),
        ctx:        ctx,
        cancel:     cancel,
    }

    // 初始化工作器池
    for i := 0; i < workers; i++ {
        pool.workerPool <- struct{}{}
    }

    // 启动调度器
    go pool.scheduler()

    return pool
}

func (gp *GoroutinePool) scheduler() {
    for {
        select {
        case <-gp.ctx.Done():
            return
        case task := <-gp.taskQueue:
            // 获取工作器
            <-gp.workerPool

            // 启动工作器
            go gp.worker(task)
        }
    }
}

func (gp *GoroutinePool) worker(task Task) {
    defer func() {
        gp.workerPool <- struct{}{}
        gp.wg.Done()
    }()

    // 执行任务
    task()
}

func (gp *GoroutinePool) Submit(task Task) error {
    select {
    case gp.taskQueue <- task:
        gp.wg.Add(1)
        return nil
    case <-gp.ctx.Done():
        return gp.ctx.Err()
    }
}

func (gp *GoroutinePool) Stop() {
    gp.cancel()
    gp.wg.Wait()
}

// 通道性能测试
func BenchmarkChannelPerformance(b *testing.B) {
    channelTypes := []struct {
        name string
        fn   func(*testing.B)
    }{
        {"BufferedChannel", benchmarkBufferedChannel},
        {"UnbufferedChannel", benchmarkUnbufferedChannel},
        {"SelectChannel", benchmarkSelectChannel},
    }

    for _, ct := range channelTypes {
        b.Run(ct.name, ct.fn)
    }
}

func benchmarkBufferedChannel(b *testing.B) {
    ch := make(chan int, 100)
    done := make(chan bool)

    go func() {
        for i := 0; i < b.N; i++ {
            ch <- i
        }
        close(ch)
    }()

    go func() {
        for range ch {
        }
        done <- true
    }()

    b.ResetTimer()
    <-done
}

func benchmarkUnbufferedChannel(b *testing.B) {
    ch := make(chan int)
    done := make(chan bool)

    go func() {
        for i := 0; i < b.N; i++ {
            ch <- i
        }
        close(ch)
    }()

    go func() {
        for range ch {
        }
        done <- true
    }()

    b.ResetTimer()
    <-done
}

func benchmarkSelectChannel(b *testing.B) {
    ch1 := make(chan int, 100)
    ch2 := make(chan int, 100)
    done := make(chan bool)

    go func() {
        for i := 0; i < b.N; i++ {
            if i%2 == 0 {
                ch1 <- i
            } else {
                ch2 <- i
            }
        }
        close(ch1)
        close(ch2)
    }()

    go func() {
        count := 0
        for count < b.N {
            select {
            case <-ch1:
                count++
            case <-ch2:
                count++
            }
        }
        done <- true
    }()

    b.ResetTimer()
    <-done
}

// 并发安全数据结构性能测试
func BenchmarkConcurrentDataStructures(b *testing.B) {
    dataStructures := []struct {
        name string
        fn   func(*testing.B)
    }{
        {"Mutex", benchmarkMutex},
        {"RWMutex", benchmarkRWMutex},
        {"Atomic", benchmarkAtomic},
        {"Channel", benchmarkChannelCounter},
    }

    for _, ds := range dataStructures {
        b.Run(ds.name, ds.fn)
    }
}

func benchmarkMutex(b *testing.B) {
    var counter int64
    var mutex sync.Mutex

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            mutex.Lock()
            counter++
            mutex.Unlock()
        }
    })
}

func benchmarkRWMutex(b *testing.B) {
    var counter int64
    var rwMutex sync.RWMutex

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            if pb.N%2 == 0 {
                // 读操作
                rwMutex.RLock()
                _ = counter
                rwMutex.RUnlock()
            } else {
                // 写操作
                rwMutex.Lock()
                counter++
                rwMutex.Unlock()
            }
        }
    })
}

func benchmarkAtomic(b *testing.B) {
    var counter int64

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            atomic.AddInt64(&counter, 1)
        }
    })
}

func benchmarkChannelCounter(b *testing.B) {
    counter := make(chan int64, 100)
    done := make(chan bool)

    // 启动计数器Goroutine
    go func() {
        var total int64
        for delta := range counter {
            total += delta
        }
        done <- total
    }()

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            counter <- 1
        }
    })

    close(counter)
    <-done
}

// 并发模式性能测试
func BenchmarkConcurrencyPatterns(b *testing.B) {
    patterns := []struct {
        name string
        fn   func(*testing.B)
    }{
        {"WorkerPool", benchmarkWorkerPool},
        {"FanOutFanIn", benchmarkFanOutFanIn},
        {"Pipeline", benchmarkPipeline},
        {"PubSub", benchmarkPubSub},
    }

    for _, pattern := range patterns {
        b.Run(pattern.name, pattern.fn)
    }
}

func benchmarkWorkerPool(b *testing.B) {
    tasks := make(chan int, b.N)
    results := make(chan int, b.N)

    // 启动工作池
    numWorkers := 10
    for i := 0; i < numWorkers; i++ {
        go func() {
            for task := range tasks {
                results <- task * 2
            }
        }()
    }

    b.ResetTimer()

    // 发送任务
    go func() {
        for i := 0; i < b.N; i++ {
            tasks <- i
        }
        close(tasks)
    }()

    // 收集结果
    for i := 0; i < b.N; i++ {
        <-results
    }
}

func benchmarkFanOutFanIn(b *testing.B) {
    source := make(chan int, b.N)
    worker1 := make(chan int, b.N)
    worker2 := make(chan int, b.N)
    sink := make(chan int, b.N)

    // Fan-out阶段
    go func() {
        for i := 0; i < b.N; i++ {
            source <- i
        }
        close(source)
    }()

    go func() {
        for num := range source {
            worker1 <- num * 2
        }
        close(worker1)
    }()

    go func() {
        for num := range source {
            worker2 <- num * 3
        }
        close(worker2)
    }()

    // Fan-in阶段
    go func() {
        for {
            select {
            case num := <-worker1:
                sink <- num
            case num := <-worker2:
                sink <- num
            }
        }
    }()

    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        <-sink
    }
}

func benchmarkPipeline(b *testing.B) {
    stage1 := make(chan int, b.N)
    stage2 := make(chan int, b.N)
    stage3 := make(chan int, b.N)

    // Pipeline阶段
    go func() {
        for num := range stage1 {
            stage2 <- num * 2
        }
        close(stage2)
    }()

    go func() {
        for num := range stage2 {
            stage3 <- num + 10
        }
        close(stage3)
    }()

    b.ResetTimer()

    go func() {
        for i := 0; i < b.N; i++ {
            stage1 <- i
        }
        close(stage1)
    }()

    for i := 0; i < b.N; i++ {
        <-stage3
    }
}

func benchmarkPubSub(b *testing.B) {
    publisher := make(chan int, b.N)
    subscribers := make([]chan int, 10)

    // 创建订阅者
    for i := 0; i < 10; i++ {
        subscriber := make(chan int, b.N)
        subscribers[i] = subscriber

        go func(sub chan int) {
            for range sub {
                // 处理消息
            }
        }(subscriber)
    }

    b.ResetTimer()

    // 发布消息
    go func() {
        for i := 0; i < b.N; i++ {
            publisher <- i
        }
        close(publisher)
    }()

    // 分发消息给订阅者
    go func() {
        for msg := range publisher {
            for _, sub := range subscribers {
                sub <- msg
            }
        }
    }()

    // 等待处理完成
    time.Sleep(100 * time.Millisecond)
}
```

## 内存性能测试

### 内存使用基准测试
```go
package benchmark

import (
    "runtime"
    "sync"
    "testing"
)

// 内存分配基准测试
func BenchmarkMemoryAllocation(b *testing.B) {
    // 测试不同类型的内存分配
    allocationTypes := []struct {
        name string
        fn   func(*testing.B)
    }{
        {"SliceAllocation", benchmarkSliceAllocation},
        {"MapAllocation", benchmarkMapAllocation},
        {"StructAllocation", benchmarkStructAllocation},
        {"StringAllocation", benchmarkStringAllocation},
        {"InterfaceAllocation", benchmarkInterfaceAllocation},
    }

    for _, at := range allocationTypes {
        b.Run(at.name, at.fn)
    }
}

func benchmarkSliceAllocation(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            // 分配切片
            slice := make([]int, 1000)
            _ = slice
        }
    })
}

func benchmarkMapAllocation(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            // 分配map
            m := make(map[string]int)
            m["key"] = 42
            _ = m
        }
    })
}

func benchmarkStructAllocation(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            // 分配struct
            s := struct {
                ID   int
                Name string
            }{
                ID:   42,
                Name: "test",
            }
            _ = s
        }
    })
}

func benchmarkStringAllocation(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            // 字符串连接
            str := "Hello, " + "World!"
            _ = str
        }
    })
}

func benchmarkInterfaceAllocation(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            // 接口分配
            var i interface{} = 42
            _ = i
        }
    })
}

// 对象池性能测试
func BenchmarkObjectPool(b *testing.B) {
    // 创建对象池
    pool := sync.Pool{
        New: func() interface{} {
            return make([]byte, 1024)
        },
    }

    b.Run("WithoutPool", func(b *testing.B) {
        b.ResetTimer()
        b.RunParallel(func(pb *testing.PB) {
            for pb.Next() {
                // 每次都重新分配
                buf := make([]byte, 1024)
                _ = buf
            }
        })
    })

    b.Run("WithPool", func(b *testing.B) {
        b.ResetTimer()
        b.RunParallel(func(pb *testing.PB) {
            for pb.Next() {
                // 从池中获取
                buf := pool.Get().([]byte)
                // 使用后放回池中
                pool.Put(buf)
            }
        })
    })
}

// 垃圾回收性能测试
func BenchmarkGarbageCollection(b *testing.B) {
    b.Run("HeavyAllocation", func(b *testing.B) {
        b.ResetTimer()
        b.RunParallel(func(pb *testing.PB) {
            for pb.Next() {
                // 大量内存分配
                data := make([][]byte, 100)
                for i := range data {
                    data[i] = make([]byte, 1024)
                }
                _ = data
            }
        })
    })

    b.Run("OptimizedAllocation", func(b *testing.B) {
        var pool sync.Pool
        pool.New = func() interface{} {
            return make([]byte, 1024)
        }

        b.ResetTimer()
        b.RunParallel(func(pb *testing.PB) {
            for pb.Next() {
                // 使用对象池优化
                data := make([][]byte, 100)
                for i := range data {
                    data[i] = pool.Get().([]byte)
                    // 重置并放回池中
                    pool.Put(data[i][:0])
                }
                _ = data
            }
        })
    })
}

// 内存泄漏检测测试
func BenchmarkMemoryLeakDetection(b *testing.B) {
    // 模拟可能存在内存泄漏的场景
    var leakyMap sync.Map

    b.Run("LeakyOperation", func(b *testing.B) {
        b.ResetTimer()
        b.RunParallel(func(pb *testing.PB) {
            for pb.Next() {
                // 持续向map中添加数据而不清理
                key := fmt.Sprintf("key_%d", time.Now().UnixNano())
                value := make([]byte, 1024)
                leakyMap.Store(key, value)
            }
        })

        // 打印内存使用情况
        var m runtime.MemStats
        runtime.ReadMemStats(&m)
        b.Logf("Memory usage - Alloc: %d, TotalAlloc: %d", m.Alloc, m.TotalAlloc)
    })

    b.Run("NonLeakyOperation", func(b *testing.B) {
        b.ResetTimer()
        b.RunParallel(func(pb *testing.PB) {
            for pb.Next() {
                // 使用局部变量，会被GC回收
                key := fmt.Sprintf("key_%d", time.Now().UnixNano())
                value := make([]byte, 1024)
                _ = key + string(value)
            }
        })

        // 打印内存使用情况
        var m runtime.MemStats
        runtime.ReadMemStats(&m)
        b.Logf("Memory usage - Alloc: %d, TotalAlloc: %d", m.Alloc, m.TotalAlloc)
    })
}

// 内存压力测试
func BenchmarkMemoryPressure(b *testing.B) {
    // 测试不同内存压力下的性能
    pressureLevels := []struct {
        name      string
        chunkSize int
        chunks    int
    }{
        {"LowPressure", 1024, 100},
        {"MediumPressure", 1024, 1000},
        {"HighPressure", 1024, 10000},
        {"ExtremePressure", 1024, 100000},
    }

    for _, level := range pressureLevels {
        b.Run(level.name, func(b *testing.B) {
            b.ResetTimer()
            b.RunParallel(func(pb *testing.PB) {
                for pb.Next() {
                    // 分配大块内存
                    data := make([][]byte, level.chunks)
                    for i := range data {
                        data[i] = make([]byte, level.chunkSize)
                    }
                    _ = data
                }
            })

            // 强制GC
            runtime.GC()

            var m runtime.MemStats
            runtime.ReadMemStats(&m)
            b.Logf("Memory pressure - Alloc: %d, TotalAlloc: %d, NumGC: %d",
                m.Alloc, m.TotalAlloc, m.NumGC)
        })
    }
}

// 缓存性能测试
func BenchmarkCachePerformance(b *testing.B) {
    // 测试不同缓存实现的性能
    cacheTypes := []struct {
        name string
        fn   func(*testing.B)
    }{
        {"SyncMapCache", benchmarkSyncMapCache},
        {"RWMutexCache", benchmarkRWMutexCache},
        {"ShardedCache", benchmarkShardedCache},
    }

    for _, ct := range cacheTypes {
        b.Run(ct.name, ct.fn)
    }
}

func benchmarkSyncMapCache(b *testing.B) {
    var cache sync.Map

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            key := fmt.Sprintf("key_%d", time.Now().UnixNano())
            value := make([]byte, 1024)

            // 写操作
            cache.Store(key, value)

            // 读操作
            if val, ok := cache.Load(key); ok {
                _ = val.([]byte)
            }
        }
    })
}

func benchmarkRWMutexCache(b *testing.B) {
    type cacheItem struct {
        value []byte
    }

    cache := make(map[string]*cacheItem)
    var mutex sync.RWMutex

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            key := fmt.Sprintf("key_%d", time.Now().UnixNano())
            value := make([]byte, 1024)

            // 写操作
            mutex.Lock()
            cache[key] = &cacheItem{value: value}
            mutex.Unlock()

            // 读操作
            mutex.RLock()
            if item := cache[key]; item != nil {
                _ = item.value
            }
            mutex.RUnlock()
        }
    })
}

func benchmarkShardedCache(b *testing.B) {
    // 分片缓存实现
    const numShards = 16
    shards := make([]sync.Map, numShards)

    getShard := func(key string) *sync.Map {
        hash := fnv32a(key)
        return &shards[hash%numShards]
    }

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            key := fmt.Sprintf("key_%d", time.Now().UnixNano())
            value := make([]byte, 1024)

            shard := getShard(key)

            // 写操作
            shard.Store(key, value)

            // 读操作
            if val, ok := shard.Load(key); ok {
                _ = val.([]byte)
            }
        }
    })
}

// 简单的FNV哈希函数
func fnv32a(key string) uint32 {
    const prime32 = uint32(16777619)
    hash := uint32(2166136261)
    for i := 0; i < len(key); i++ {
        hash ^= uint32(key[i])
        hash *= prime32
    }
    return hash
}

// 内存分配器性能测试
func BenchmarkAllocatorPerformance(b *testing.B) {
    // 测试不同内存分配策略的性能
    allocators := []struct {
        name string
        fn   func(*testing.B)
    }{
        {"DefaultAllocator", benchmarkDefaultAllocator},
        {"PoolAllocator", benchmarkPoolAllocator},
        {"PreallocatedAllocator", benchmarkPreallocatedAllocator},
    }

    for _, alloc := range allocators {
        b.Run(alloc.name, alloc.fn)
    }
}

func benchmarkDefaultAllocator(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            // 每次都重新分配
            buf := make([]byte, 1024)
            _ = buf
        }
    })
}

func benchmarkPoolAllocator(b *testing.B) {
    var pool sync.Pool
    pool.New = func() interface{} {
        return make([]byte, 1024)
    }

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            buf := pool.Get().([]byte)
            // 使用后放回池中
            pool.Put(buf[:0])
        }
    })
}

func benchmarkPreallocatedAllocator(b *testing.B) {
    // 预分配大块内存
    buffer := make([]byte, 1024*1024) // 1MB
    offset := 0

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            // 从预分配的内存中获取
            if offset+1024 > len(buffer) {
                offset = 0
            }
            buf := buffer[offset : offset+1024]
            offset += 1024
            _ = buf
        }
    })
}
```

## 性能分析和优化

### 性能分析工具
```go
package benchmark

import (
    "fmt"
    "os"
    "runtime"
    "runtime/pprof"
    "testing"
    "time"
)

// 性能分析基准测试
func BenchmarkProfiling(b *testing.B) {
    // CPU分析
    if os.Getenv("CPU_PROFILE") != "" {
        f, err := os.Create("cpu.prof")
        if err != nil {
            b.Fatal(err)
        }
        defer f.Close()

        if err := pprof.StartCPUProfile(f); err != nil {
            b.Fatal(err)
        }
        defer pprof.StopCPUProfile()
    }

    // 内存分析
    if os.Getenv("MEM_PROFILE") != "" {
        defer func() {
            f, err := os.Create("mem.prof")
            if err != nil {
                b.Fatal(err)
            }
            defer f.Close()

            runtime.GC() // 获取GC后的内存信息
            if err := pprof.WriteHeapProfile(f); err != nil {
                b.Fatal(err)
            }
        }()
    }

    // 运行基准测试
    b.Run("ComplexOperation", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            complexOperation()
        }
    })
}

// 复杂操作函数
func complexOperation() {
    // 模拟复杂的计算操作
    data := make([]int, 1000)
    for i := range data {
        data[i] = i * i
    }

    result := 0
    for _, v := range data {
        result += v
    }

    _ = result
}

// 性能对比测试
func BenchmarkPerformanceComparison(b *testing.B) {
    implementations := []struct {
        name string
        fn   func() int
    }{
        {"NaiveImplementation", naiveImplementation},
        {"OptimizedImplementation", optimizedImplementation},
        {"ParallelImplementation", parallelImplementation},
    }

    for _, impl := range implementations {
        b.Run(impl.name, func(b *testing.B) {
            b.ResetTimer()
            for i := 0; i < b.N; i++ {
                _ = impl.fn()
            }
        })
    }
}

// 朴素实现
func naiveImplementation() int {
    result := 0
    for i := 0; i < 1000; i++ {
        result += i * i
    }
    return result
}

// 优化实现
func optimizedImplementation() int {
    // 使用数学公式优化
    n := 1000
    return n * (n + 1) * (2*n + 1) / 6
}

// 并行实现
func parallelImplementation() int {
    const numWorkers = 4
    chunkSize := 1000 / numWorkers

    results := make(chan int, numWorkers)

    for i := 0; i < numWorkers; i++ {
        start := i * chunkSize
        end := start + chunkSize
        if i == numWorkers-1 {
            end = 1000
        }

        go func(s, e int) {
            result := 0
            for j := s; j < e; j++ {
                result += j * j
            }
            results <- result
        }(start, end)
    }

    total := 0
    for i := 0; i < numWorkers; i++ {
        total += <-results
    }

    return total
}

// 内存使用分析
func BenchmarkMemoryAnalysis(b *testing.B) {
    operations := []struct {
        name string
        fn   func()
    }{
        {"SliceOperation", sliceOperation},
        {"MapOperation", mapOperation},
        {"StringOperation", stringOperation},
    }

    for _, op := range operations {
        b.Run(op.name, func(b *testing.B) {
            // 重置内存统计
            runtime.GC()
            var m1, m2 runtime.MemStats
            runtime.ReadMemStats(&m1)

            b.ResetTimer()
            for i := 0; i < b.N; i++ {
                op.fn()
            }

            runtime.ReadMemStats(&m2)
            b.Logf("Memory usage - Allocs: %d, TotalAlloc: %d",
                m2.Allocs-m1.Allocs, m2.TotalAlloc-m1.TotalAlloc)
        })
    }
}

func sliceOperation() {
    // 切片操作
    data := make([]int, 100)
    for i := range data {
        data[i] = i * 2
    }
    _ = data
}

func mapOperation() {
    // Map操作
    data := make(map[string]int)
    for i := 0; i < 100; i++ {
        data[fmt.Sprintf("key_%d", i)] = i * 2
    }
    _ = data
}

func stringOperation() {
    // 字符串操作
    var result string
    for i := 0; i < 100; i++ {
        result += fmt.Sprintf("item_%d", i)
    }
    _ = result
}

// 执行时间分析
func BenchmarkExecutionTime(b *testing.B) {
    b.Run("AlgorithmComparison", func(b *testing.B) {
        algorithms := []struct {
            name string
            fn   func([]int) int
        }{
            {"LinearSearch", linearSearch},
            {"BinarySearch", binarySearch},
            {"HashSearch", hashSearch},
        }

        // 准备测试数据
        data := make([]int, 1000)
        for i := range data {
            data[i] = i
        }

        for _, algo := range algorithms {
            b.Run(algo.name, func(b *testing.B) {
                b.ResetTimer()
                for i := 0; i < b.N; i++ {
                    _ = algo.fn(data)
                }
            })
        }
    })
}

func linearSearch(data []int) int {
    target := 999
    for i, v := range data {
        if v == target {
            return i
        }
    }
    return -1
}

func binarySearch(data []int) int {
    target := 999
    left, right := 0, len(data)-1

    for left <= right {
        mid := left + (right-left)/2
        if data[mid] == target {
            return mid
        }
        if data[mid] < target {
            left = mid + 1
        } else {
            right = mid - 1
        }
    }
    return -1
}

func hashSearch(data []int) int {
    target := 999
    hashSet := make(map[int]int)
    for i, v := range data {
        hashSet[v] = i
    }
    return hashSet[target]
}

// 并发性能分析
func BenchmarkConcurrencyAnalysis(b *testing.B) {
    concurrencyLevels := []int{1, 2, 4, 8, 16}

    for _, level := range concurrencyLevels {
        b.Run(fmt.Sprintf("Concurrency_%d", level), func(b *testing.B) {
            processor := NewConcurrentProcessor(level)

            b.ResetTimer()

            // 测试不同并发级别的性能
            start := time.Now()
            b.RunParallel(func(pb *testing.PB) {
                for pb.Next() {
                    processor.Process("test")
                }
            })
            duration := time.Since(start)

            b.Logf("Concurrency level: %d, Duration: %v, Ops/sec: %.2f",
                level, duration, float64(b.N)/duration.Seconds())
        })
    }
}

// 缓存性能分析
func BenchmarkCacheAnalysis(b *testing.B) {
    cacheSizes := []int{100, 1000, 10000, 100000}

    for _, size := range cacheSizes {
        b.Run(fmt.Sprintf("CacheSize_%d", size), func(b *testing.B) {
            cache := NewLRUCache(size)

            b.ResetTimer()
            b.RunParallel(func(pb *testing.PB) {
                for pb.Next() {
                    key := fmt.Sprintf("key_%d", time.Now().UnixNano()%size)

                    // 尝试获取缓存
                    if value, exists := cache.Get(key); exists {
                        _ = value
                    } else {
                        // 缓存未命中，设置缓存
                        cache.Set(key, "value")
                    }
                }
            })

            // 打印缓存统计
            stats := cache.GetStats()
            b.Logf("Cache size: %d, Hit rate: %.2f%%, Miss rate: %.2f%%",
                size, stats.HitRate(), stats.MissRate())
        })
    }
}

// LRU缓存实现
type LRUCache struct {
    capacity int
    cache    map[string]*Node
    head     *Node
    tail     *Node
    mutex    sync.RWMutex
}

type Node struct {
    key   string
    value interface{}
    prev  *Node
    next  *Node
}

type CacheStats struct {
    Hits   int
    Misses int
}

func NewLRUCache(capacity int) *LRUCache {
    cache := &LRUCache{
        capacity: capacity,
        cache:    make(map[string]*Node),
    }
    cache.head = &Node{}
    cache.tail = &Node{}
    cache.head.next = cache.tail
    cache.tail.prev = cache.head
    return cache
}

func (c *LRUCache) Get(key string) (interface{}, bool) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()

    if node, exists := c.cache[key]; exists {
        // 移动到头部
        c.moveToHead(node)
        return node.value, true
    }
    return nil, false
}

func (c *LRUCache) Set(key string, value interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()

    if node, exists := c.cache[key]; exists {
        node.value = value
        c.moveToHead(node)
        return
    }

    node := &Node{
        key:   key,
        value: value,
    }

    c.cache[key] = node
    c.addToHead(node)

    if len(c.cache) > c.capacity {
        // 移除尾部节点
        tail := c.tail.prev
        c.removeNode(tail)
        delete(c.cache, tail.key)
    }
}

func (c *LRUCache) moveToHead(node *Node) {
    c.removeNode(node)
    c.addToHead(node)
}

func (c *LRUCache) removeNode(node *Node) {
    node.prev.next = node.next
    node.next.prev = node.prev
}

func (c *LRUCache) addToHead(node *Node) {
    node.prev = c.head
    node.next = c.head.next
    c.head.next.prev = node
    c.head.next = node
}

func (c *LRUCache) GetStats() *CacheStats {
    // 这里应该实现统计逻辑
    return &CacheStats{}
}

func (s *CacheStats) HitRate() float64 {
    if s.Hits+s.Misses == 0 {
        return 0
    }
    return float64(s.Hits) / float64(s.Hits+s.Misses) * 100
}

func (s *CacheStats) MissRate() float64 {
    if s.Hits+s.Misses == 0 {
        return 0
    }
    return float64(s.Misses) / float64(s.Hits+s.Misses) * 100
}
```

这个Gin基准测试文档涵盖了各种性能测试场景，包括HTTP服务器测试、路由性能测试、中间件性能测试、数据库性能测试、并发性能测试、内存性能测试以及性能分析和优化等方面。通过这些基准测试，开发者可以全面了解Gin应用的性能特征，并找到优化方向。