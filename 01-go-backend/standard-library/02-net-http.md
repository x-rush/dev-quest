# Go 标准库：net/http 包 - 从PHP视角理解

## 📚 概述

Go的`net/http`包是构建Web应用的核心库，提供了完整的HTTP客户端和服务器功能。与PHP的Web开发方式不同，Go将Web服务器直接内建在标准库中，使得开发者可以构建高性能的Web应用而无需依赖外部服务器。

### 🎯 学习目标
- 掌握Go的HTTP服务器开发
- 理解HTTP客户端请求处理
- 学会中间件和路由设计
- 熟悉Go Web开发与PHP的差异

## 🔄 Go vs PHP Web开发对比

### PHP Web开发
```php
<?php
// PHP通常需要Web服务器(Apache/Nginx)
// 文件: index.php
<?php
// 获取请求信息
$method = $_SERVER['REQUEST_METHOD'];
$path = $_SERVER['REQUEST_URI'];
$headers = getallheaders();
$body = file_get_contents('php://input');

// 处理路由
if ($method === 'GET' && $path === '/') {
    echo "Hello, World!";
} elseif ($method === 'POST' && $path === '/api/users') {
    $data = json_decode($body, true);
    echo json_encode(['status' => 'success', 'data' => $data]);
} else {
    http_response_code(404);
    echo "Not Found";
}

// 或者使用框架
$app = new Slim\App();
$app->get('/', function($request, $response) {
    return $response->write("Hello, World!");
});
$app->post('/api/users', function($request, $response) {
    $data = $request->getParsedBody();
    return $response->withJson(['status' => 'success', 'data' => $data]);
});
$app->run();
```

### Go Web开发
```go
// Go内置HTTP服务器
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
)

// 请求处理函数
func helloHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, World!")
}

func usersHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    var user User
    if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
        http.Error(w, "Invalid request body", http.StatusBadRequest)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]interface{}{
        "status": "success",
        "data":   user,
    })
}

func main() {
    // 注册路由
    http.HandleFunc("/", helloHandler)
    http.HandleFunc("/api/users", usersHandler)

    // 启动服务器
    fmt.Println("服务器启动，监听端口 8080...")
    if err := http.ListenAndServe(":8080", nil); err != nil {
        log.Fatal(err)
    }
}
```

## 📝 HTTP 服务器开发

### 1. 基础HTTP服务器

#### 简单服务器
```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    // 处理根路径
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "欢迎使用Go HTTP服务器!")
    })

    // 处理关于页面
    http.HandleFunc("/about", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "关于我们页面")
    })

    // 处理健康检查
    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        fmt.Fprintf(w, "OK")
    })

    // 启动服务器
    fmt.Println("服务器启动，监听端口 8080...")
    if err := http.ListenAndServe(":8080", nil); err != nil {
        panic(err)
    }
}
```

#### 自定义服务器配置
```go
func customServer() {
    // 创建自定义服务器
    server := &http.Server{
        Addr:         ":8080",
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    // 注册路由
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "自定义服务器配置")
    })

    // 启动服务器
    if err := server.ListenAndServe(); err != nil {
        log.Fatal(err)
    }
}
```

### 2. 请求处理

#### 请求信息获取
```go
func requestInfoHandler(w http.ResponseWriter, r *http.Request) {
    // 获取HTTP方法
    method := r.Method

    // 获取URL路径
    path := r.URL.Path

    // 获取查询参数
    query := r.URL.Query()
    name := query.Get("name")
    page := query.Get("page")

    // 获取请求头
    userAgent := r.Header.Get("User-Agent")
    contentType := r.Header.Get("Content-Type")

    // 获取所有请求头
    headers := r.Header

    // 读取请求体
    body, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "读取请求体失败", http.StatusInternalServerError)
        return
    }
    defer r.Body.Close()

    // 返回请求信息
    response := map[string]interface{}{
        "method":      method,
        "path":        path,
        "query":       map[string]string{"name": name, "page": page},
        "userAgent":   userAgent,
        "contentType": contentType,
        "headers":     headers,
        "body":        string(body),
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}
```

#### 请求体解析
```go
type User struct {
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age"`
}

func parseRequestBodyHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    // 解析JSON请求体
    var user User
    if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
        http.Error(w, "Invalid JSON", http.StatusBadRequest)
        return
    }

    // 处理用户数据
    response := map[string]interface{}{
        "message": "用户创建成功",
        "user":    user,
    }

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(response)
}
```

### 3. 响应处理

#### 基础响应
```go
func responseHandler(w http.ResponseWriter, r *http.Request) {
    // 设置响应头
    w.Header().Set("Content-Type", "text/plain; charset=utf-8")
    w.Header().Set("X-Custom-Header", "CustomValue")

    // 设置状态码
    w.WriteHeader(http.StatusOK)

    // 写入响应体
    fmt.Fprintf(w, "这是一个简单的响应")
}
```

#### JSON响应
```go
func jsonResponseHandler(w http.ResponseWriter, r *http.Request) {
    data := struct {
        Status  string      `json:"status"`
        Message string      `json:"message"`
        Data    interface{} `json:"data,omitempty"`
    }{
        Status:  "success",
        Message: "操作成功",
        Data: map[string]interface{}{
            "id":    1,
            "name":  "张三",
            "email": "zhangsan@example.com",
        },
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(data)
}
```

#### 文件响应
```go
func fileResponseHandler(w http.ResponseWriter, r *http.Request) {
    // 读取文件
    filePath := "./static/example.txt"
    content, err := os.ReadFile(filePath)
    if err != nil {
        http.Error(w, "文件未找到", http.StatusNotFound)
        return
    }

    // 设置响应头
    w.Header().Set("Content-Type", "text/plain")
    w.Header().Set("Content-Disposition", "attachment; filename=example.txt")

    // 写入文件内容
    w.Write(content)
}
```

## 📝 HTTP 客户端开发

### 1. 基础GET请求
```go
func simpleGetRequest() {
    // 发送GET请求
    resp, err := http.Get("https://api.example.com/users")
    if err != nil {
        log.Fatal(err)
    }
    defer resp.Body.Close()

    // 读取响应体
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("状态码: %d\n", resp.StatusCode)
    fmt.Printf("响应头: %v\n", resp.Header)
    fmt.Printf("响应体: %s\n", string(body))
}
```

### 2. 带参数的请求
```go
func getRequestWithParams() {
    // 创建请求URL
    baseURL := "https://api.example.com/search"
    params := url.Values{}
    params.Add("q", "golang")
    params.Add("page", "1")
    params.Add("per_page", "10")

    // 构建完整URL
    fullURL := fmt.Sprintf("%s?%s", baseURL, params.Encode())

    // 发送请求
    resp, err := http.Get(fullURL)
    if err != nil {
        log.Fatal(err)
    }
    defer resp.Body.Close()

    // 处理响应
    if resp.StatusCode == http.StatusOK {
        body, _ := io.ReadAll(resp.Body)
        fmt.Printf("搜索结果: %s\n", string(body))
    }
}
```

### 3. POST请求
```go
func postRequest() {
    // 准备请求数据
    data := map[string]interface{}{
        "name":  "John Doe",
        "email": "john@example.com",
        "age":   30,
    }
    jsonData, _ := json.Marshal(data)

    // 发送POST请求
    resp, err := http.Post(
        "https://api.example.com/users",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    if err != nil {
        log.Fatal(err)
    }
    defer resp.Body.Close()

    // 处理响应
    body, _ := io.ReadAll(resp.Body)
    fmt.Printf("创建用户结果: %s\n", string(body))
}
```

### 4. 自定义客户端
```go
func customClient() {
    // 创建自定义客户端
    client := &http.Client{
        Timeout: 30 * time.Second,
        Transport: &http.Transport{
            MaxIdleConns:        10,
            IdleConnTimeout:     30 * time.Second,
            DisableCompression:  false,
            MaxIdleConnsPerHost: 10,
        },
    }

    // 创建请求
    req, err := http.NewRequest("GET", "https://api.example.com/users", nil)
    if err != nil {
        log.Fatal(err)
    }

    // 设置请求头
    req.Header.Set("Authorization", "Bearer your-token-here")
    req.Header.Set("Accept", "application/json")

    // 发送请求
    resp, err := client.Do(req)
    if err != nil {
        log.Fatal(err)
    }
    defer resp.Body.Close()

    // 处理响应
    if resp.StatusCode == http.StatusOK {
        body, _ := io.ReadAll(resp.Body)
        fmt.Printf("用户列表: %s\n", string(body))
    }
}
```

## 📝 中间件开发

### 1. 日志中间件
```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        // 记录请求信息
        log.Printf("开始 %s %s", r.Method, r.URL.Path)

        // 调用下一个处理器
        next.ServeHTTP(w, r)

        // 记录处理时间
        log.Printf("完成 %s %s - %v", r.Method, r.URL.Path, time.Since(start))
    })
}
```

### 2. 认证中间件
```go
func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 获取Authorization头
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "未提供认证令牌", http.StatusUnauthorized)
            return
        }

        // 验证令牌（这里简化处理）
        if token != "Bearer valid-token" {
            http.Error(w, "无效的认证令牌", http.StatusUnauthorized)
            return
        }

        // 将用户信息添加到上下文
        ctx := context.WithValue(r.Context(), "user", "authenticated-user")
        r = r.WithContext(ctx)

        // 调用下一个处理器
        next.ServeHTTP(w, r)
    })
}
```

### 3. CORS中间件
```go
func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 设置CORS头
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

        // 处理预检请求
        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }

        // 调用下一个处理器
        next.ServeHTTP(w, r)
    })
}
```

### 4. 使用中间件
```go
func main() {
    // 创建路由器
    mux := http.NewServeMux()

    // 注册路由
    mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello, World!")
    })

    mux.HandleFunc("/protected", func(w http.ResponseWriter, r *http.Request) {
        user := r.Context().Value("user")
        fmt.Fprintf(w, "欢迎，%s!", user)
    })

    // 包装中间件
    handler := loggingMiddleware(corsMiddleware(authMiddleware(mux)))

    // 启动服务器
    fmt.Println("服务器启动，监听端口 8080...")
    if err := http.ListenAndServe(":8080", handler); err != nil {
        log.Fatal(err)
    }
}
```

## 📝 路由设计

### 1. 简单路由器
```go
type Router struct {
    routes map[string]map[string]http.HandlerFunc
}

func NewRouter() *Router {
    return &Router{
        routes: make(map[string]map[string]http.HandlerFunc),
    }
}

func (r *Router) HandleFunc(method, path string, handler http.HandlerFunc) {
    if _, ok := r.routes[path]; !ok {
        r.routes[path] = make(map[string]http.HandlerFunc)
    }
    r.routes[path][method] = handler
}

func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    // 查找路由
    if handlers, ok := r.routes[req.URL.Path]; ok {
        if handler, ok := handlers[req.Method]; ok {
            handler(w, req)
            return
        }
    }

    // 未找到路由
    http.NotFound(w, req)
}

func main() {
    router := NewRouter()

    // 注册路由
    router.HandleFunc("GET", "/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "首页")
    })

    router.HandleFunc("GET", "/users", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "用户列表")
    })

    router.HandleFunc("POST", "/users", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "创建用户")
    })

    fmt.Println("服务器启动，监听端口 8080...")
    if err := http.ListenAndServe(":8080", router); err != nil {
        log.Fatal(err)
    }
}
```

### 2. 带参数的路由
```go
type ParamRouter struct {
    routes map[string]map[string]http.HandlerFunc
    params map[string]string
}

func NewParamRouter() *ParamRouter {
    return &ParamRouter{
        routes: make(map[string]map[string]http.HandlerFunc),
        params: make(map[string]string),
    }
}

func (r *ParamRouter) HandleFunc(method, path string, handler http.HandlerFunc) {
    // 简化版参数路由
    cleanPath := path
    if strings.Contains(path, ":") {
        parts := strings.Split(path, "/")
        for i, part := range parts {
            if strings.HasPrefix(part, ":") {
                paramName := part[1:]
                cleanPath = strings.Replace(cleanPath, part, "*", 1)
            }
        }
    }

    if _, ok := r.routes[cleanPath]; !ok {
        r.routes[cleanPath] = make(map[string]http.HandlerFunc)
    }
    r.routes[cleanPath][method] = handler
}

func (r *ParamRouter) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    path := req.URL.Path

    // 查找匹配的路由
    for routePath, handlers := range r.routes {
        if routePath == path {
            if handler, ok := handlers[req.Method]; ok {
                handler(w, req)
                return
            }
        }
    }

    http.NotFound(w, req)
}
```

## 📝 实际应用示例

### 1. RESTful API 服务器
```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "sync"
    "time"
)

type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    Age       int       `json:"age"`
    CreatedAt time.Time `json:"created_at"`
}

type UserHandler struct {
    users map[int]*User
    mu    sync.RWMutex
    nextID int
}

func NewUserHandler() *UserHandler {
    return &UserHandler{
        users: make(map[int]*User),
        nextID: 1,
    }
}

func (h *UserHandler) GetUsers(w http.ResponseWriter, r *http.Request) {
    h.mu.RLock()
    defer h.mu.RUnlock()

    users := make([]*User, 0, len(h.users))
    for _, user := range h.users {
        users = append(users, user)
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(users)
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    id := parseIDFromPath(r.URL.Path)
    if id == 0 {
        http.Error(w, "无效的用户ID", http.StatusBadRequest)
        return
    }

    h.mu.RLock()
    defer h.mu.RUnlock()

    user, exists := h.users[id]
    if !exists {
        http.Error(w, "用户未找到", http.StatusNotFound)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var user User
    if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
        http.Error(w, "无效的请求数据", http.StatusBadRequest)
        return
    }

    user.ID = h.nextID
    user.CreatedAt = time.Now()

    h.mu.Lock()
    h.users[user.ID] = &user
    h.nextID++
    h.mu.Unlock()

    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(user)
}

func (h *UserHandler) UpdateUser(w http.ResponseWriter, r *http.Request) {
    id := parseIDFromPath(r.URL.Path)
    if id == 0 {
        http.Error(w, "无效的用户ID", http.StatusBadRequest)
        return
    }

    var updateUser User
    if err := json.NewDecoder(r.Body).Decode(&updateUser); err != nil {
        http.Error(w, "无效的请求数据", http.StatusBadRequest)
        return
    }

    h.mu.Lock()
    defer h.mu.Unlock()

    user, exists := h.users[id]
    if !exists {
        http.Error(w, "用户未找到", http.StatusNotFound)
        return
    }

    // 更新用户信息
    if updateUser.Name != "" {
        user.Name = updateUser.Name
    }
    if updateUser.Email != "" {
        user.Email = updateUser.Email
    }
    if updateUser.Age > 0 {
        user.Age = updateUser.Age
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

func (h *UserHandler) DeleteUser(w http.ResponseWriter, r *http.Request) {
    id := parseIDFromPath(r.URL.Path)
    if id == 0 {
        http.Error(w, "无效的用户ID", http.StatusBadRequest)
        return
    }

    h.mu.Lock()
    defer h.mu.Unlock()

    if _, exists := h.users[id]; !exists {
        http.Error(w, "用户未找到", http.StatusNotFound)
        return
    }

    delete(h.users, id)
    w.WriteHeader(http.StatusNoContent)
}

func parseIDFromPath(path string) int {
    // 简化版路径解析
    parts := strings.Split(path, "/")
    if len(parts) < 3 {
        return 0
    }

    var id int
    _, err := fmt.Sscanf(parts[2], "%d", &id)
    if err != nil {
        return 0
    }

    return id
}

func main() {
    userHandler := NewUserHandler()

    // 设置路由
    http.HandleFunc("/users", func(w http.ResponseWriter, r *http.Request) {
        switch r.Method {
        case http.MethodGet:
            userHandler.GetUsers(w, r)
        case http.MethodPost:
            userHandler.CreateUser(w, r)
        default:
            http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        }
    })

    http.HandleFunc("/users/", func(w http.ResponseWriter, r *http.Request) {
        switch r.Method {
        case http.MethodGet:
            userHandler.GetUser(w, r)
        case http.MethodPut:
            userHandler.UpdateUser(w, r)
        case http.MethodDelete:
            userHandler.DeleteUser(w, r)
        default:
            http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        }
    })

    fmt.Println("REST API 服务器启动，监听端口 8080...")
    if err := http.ListenAndServe(":8080", nil); err != nil {
        log.Fatal(err)
    }
}
```

### 2. 静态文件服务器
```go
func staticFileServer() {
    // 创建文件服务器
    fs := http.FileServer(http.Dir("./static"))

    // 处理静态文件请求
    http.Handle("/static/", http.StripPrefix("/static/", fs))

    // 处理根路径
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        http.ServeFile(w, r, "./static/index.html")
    })

    fmt.Println("静态文件服务器启动，监听端口 8080...")
    if err := http.ListenAndServe(":8080", nil); err != nil {
        log.Fatal(err)
    }
}
```

## 🧪 实践练习

### 练习1: 创建简单的Web服务器
```go
package main

import (
    "fmt"
    "net/http"
    "time"
)

func main() {
    // 首页
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "<h1>欢迎来到我的网站</h1>")
        fmt.Fprintf(w, "<p>当前时间: %s</p>", time.Now().Format("2006-01-02 15:04:05"))
    })

    // 关于页面
    http.HandleFunc("/about", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "<h1>关于我们</h1>")
        fmt.Fprintf(w, "<p>这是一个简单的Go Web服务器示例</p>")
    })

    // 健康检查
    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        fmt.Fprintf(w, `{"status": "healthy", "timestamp": "%s"}`, time.Now().Format(time.RFC3339))
    })

    fmt.Println("Web服务器启动，监听端口 8080...")
    fmt.Println("访问:")
    fmt.Println("  - http://localhost:8080/")
    fmt.Println("  - http://localhost:8080/about")
    fmt.Println("  - http://localhost:8080/health")

    if err := http.ListenAndServe(":8080", nil); err != nil {
        fmt.Printf("服务器启动失败: %v\n", err)
    }
}
```

### 练习2: 创建API客户端
```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
)

type Post struct {
    ID     int    `json:"id"`
    Title  string `json:"title"`
    Body   string `json:"body"`
    UserID int    `json:"userId"`
}

func main() {
    // 使用JSONPlaceholder API进行测试
    baseURL := "https://jsonplaceholder.typicode.com"

    // 1. 获取所有帖子
    fmt.Println("=== 获取所有帖子 ===")
    posts, err := getPosts(baseURL + "/posts")
    if err != nil {
        fmt.Printf("获取帖子失败: %v\n", err)
        return
    }
    fmt.Printf("共获取到 %d 个帖子\n", len(posts))
    if len(posts) > 0 {
        fmt.Printf("第一个帖子: %s\n", posts[0].Title)
    }

    // 2. 获取单个帖子
    fmt.Println("\n=== 获取单个帖子 ===")
    post, err := getPost(baseURL + "/posts/1")
    if err != nil {
        fmt.Printf("获取帖子失败: %v\n", err)
        return
    }
    fmt.Printf("帖子标题: %s\n", post.Title)
    fmt.Printf("帖子内容: %s\n", post.Body[:50]+"...")

    // 3. 搜索帖子
    fmt.Println("\n=== 搜索帖子 ===")
    searchResults, err := searchPosts(baseURL, "sunt")
    if err != nil {
        fmt.Printf("搜索失败: %v\n", err)
        return
    }
    fmt.Printf("搜索到 %d 个相关帖子\n", len(searchResults))
    for i, result := range searchResults {
        if i >= 3 { // 只显示前3个结果
            break
        }
        fmt.Printf("  %d. %s\n", i+1, result.Title)
    }
}

func getPosts(url string) ([]Post, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("HTTP错误: %d", resp.StatusCode)
    }

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

    var posts []Post
    if err := json.Unmarshal(body, &posts); err != nil {
        return nil, err
    }

    return posts, nil
}

func getPost(url string) (*Post, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("HTTP错误: %d", resp.StatusCode)
    }

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

    var post Post
    if err := json.Unmarshal(body, &post); err != nil {
        return nil, err
    }

    return &post, nil
}

func searchPosts(baseURL, keyword string) ([]Post, error) {
    // 获取所有帖子
    posts, err := getPosts(baseURL + "/posts")
    if err != nil {
        return nil, err
    }

    // 简单的关键词搜索
    var results []Post
    for _, post := range posts {
        if contains(post.Title, keyword) || contains(post.Body, keyword) {
            results = append(results, post)
        }
    }

    return results, nil
}

func contains(s, substr string) bool {
    return len(s) >= len(substr) && (s == substr ||
        len(s) > len(substr) &&
        (s[:len(substr)] == substr ||
         s[len(s)-len(substr):] == substr ||
         findSubstring(s, substr)))
}

func findSubstring(s, substr string) bool {
    for i := 0; i <= len(s)-len(substr); i++ {
        if s[i:i+len(substr)] == substr {
            return true
        }
    }
    return false
}
```

## 📋 最佳实践

### 1. 服务器配置最佳实践
- 设置适当的超时时间防止连接泄漏
- 使用`http.Server`结构体进行细粒度配置
- 实现优雅关闭机制
- 配置适当的并发限制

### 2. 路由设计最佳实践
- 使用一致的URL命名规范
- 实现RESTful API设计原则
- 添加适当的中间件处理通用逻辑
- 处理404和其他错误情况

### 3. 请求处理最佳实践
- 验证所有输入数据
- 使用适当的HTTP状态码
- 添加适当的请求头信息
- 处理所有可能的错误情况

### 4. 安全最佳实践
- 实现输入验证和清理
- 使用HTTPS和安全的Cookie设置
- 防止CSRF和XSS攻击
- 实现适当的认证和授权机制

### 5. 性能优化建议
- 使用连接池减少连接开销
- 实现缓存机制提高响应速度
- 使用压缩减少传输数据量
- 监控和分析性能指标

## 📋 检查清单

- [ ] 掌握HTTP服务器的基本创建
- [ ] 理解请求和响应的处理
- [ ] 学会使用中间件
- [ ] 掌握路由设计原理
- [ ] 能够创建RESTful API
- [ ] 理解HTTP客户端的使用
- [ ] 学会静态文件服务
- [ ] 掌握错误处理机制
- [ ] 了解安全最佳实践
- [ ] 能够构建完整的Web应用

## 🚀 下一步

掌握net/http包后，你可以继续学习：
- **encoding/json包**: JSON数据处理
- **database/sql包**: 数据库操作
- **Gin框架**: 高性能Web框架
- **Web应用安全**: 安全开发实践

---

**学习提示**: Go的net/http包提供了强大的Web开发能力，无需依赖外部服务器。相比PHP的Web开发模式，Go提供了更高的性能和更好的控制力。通过掌握net/http包，你可以构建高性能的Web应用和API服务。

*最后更新: 2025年9月*